from keras.api.preprocessing.sequence import pad_sequences
from src.main.config import db
from src.main.model.models import Review
from keras.src.saving.saving_api import load_model
from keras.src.legacy.preprocessing.text import tokenizer_from_json
import json
from datetime import datetime

from collections import Counter

import numpy as np
import pandas as pd

import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Configuración de MongoDB
reviews_collection = db["reviews"]

# Cargar modelo y tokenizer
#model_IA = load_model("service/toxic_model.keras")
load_model("/home/ec2-user/ReviewBack/src/main/service/toxic_model.keras")
# Cargar el tokenizador
#with open("service/tokenizer.json", "r") as f:

with open("/home/ec2-user/ReviewBack/src/main/service/tokenizer.json", "r") as f:

    tokenizer_json = json.load(f)
token = tokenizer_from_json(tokenizer_json)

def get_all_reviews():
    """
    Obtiene todas las reseñas desde MongoDB.
    """
    reviews = reviews_collection.find()
    return [Review(**review) for review in reviews]


def calculate_percentages(reviews):
    """
    Calcula los porcentajes de reseñas positivas y negativas.
    """
    counts = Counter('bueno' in review.score.lower() for review in reviews)
    count_goods = counts[True]
    count_bads = counts[False]

    total_reviews = count_goods + count_bads
    good_percentage = int((count_goods / total_reviews) * 100) if total_reviews else 0
    bad_percentage = int((count_bads / total_reviews) * 100) if total_reviews else 0

    return [total_reviews, good_percentage, bad_percentage]


def reviewToxic(text, max_len=40, model=model_IA, tokenizer=token, threshold=0.9):
    """
    Realiza una predicción sobre si un texto es tóxico o no.
    """

    # Preprocesamiento del texto
    text_sequence = tokenizer.texts_to_sequences([text])  # Convierte el texto a secuencia
    text_padded = pad_sequences(text_sequence, maxlen=max_len)  # Padding

    # Predicción
    prediction = model.predict(text_padded)
    predicted_class = prediction.argmax(axis=-1)[0]  # Índice de la clase
    predicted_prob = prediction[0, predicted_class]  # Probabilidad de la clase

    # Mapear el índice a las clases correspondientes
    class_labels = {0: 'Negativo', 1: 'Neutro', 2: 'Positivo'}

    # Asignamos la clase según la probabilidad y el umbral
    if predicted_prob >= threshold:
        return class_labels.get(predicted_class, 'Neutro')
    else:
        return 'Neutro'


def reviewToxicFromData(data, labels, max_len=40, model=model_IA, tokenizer=token, threshold=0.9):
    """
    Realiza una predicción sobre un conjunto de datos (DataFrame).
    """

    # Verificar que las columnas requeridas existan
    if not {labels['Text'], labels['Rating']}.issubset(data.columns):
        raise ValueError("El DataFrame debe contener las columnas especificadas en 'labels'.")

    # Extraer textos y ratings
    text_data = data[labels['Text']].astype(str).tolist()  # Convertir a lista de strings
    ratings = data[labels['Rating']].tolist()

    # Preprocesamiento del texto
    text_sequences = tokenizer.texts_to_sequences(text_data)  # Tokenizar los textos
    text_padded = pad_sequences(text_sequences, maxlen=max_len)  # Aplicar padding

    # Predicción
    predictions = model.predict(text_padded, batch_size=32)  # Predecir probabilidades para cada clase

    # Obtener la clase con la mayor probabilidad
    predicted_classes = predictions.argmax(axis=-1)  # Índices de las clases más probables
    predicted_probs = predictions.max(axis=-1)  # Probabilidades de las clases más probables

    # Mapear los índices a etiquetas de clases
    class_labels = {0: 'Negativo', 1: 'Neutro', 2: 'Positivo'}
    predicted_labels = [
        class_labels[idx] if prob >= threshold else 'Neutro'
        for prob, idx in zip(predicted_probs, predicted_classes)
    ]

    # Crear un DataFrame con los resultados
    results = pd.DataFrame({
        'Text': text_data,
        'Predicted Class': predicted_labels,
        'Rating': ratings
    })

    ## Guarda en MongoDB =D
    #save_predictions_to_db(results)

    return results


def save_predictions_to_db(results, collection=reviews_collection):
    """
    Guarda las predicciones en la base de datos MongoDB.
    """
    # Convertir cada fila del DataFrame en un documento de MongoDB
    documents = []
    for _, row in results.iterrows():
        document = {
            "text": row['Text'],
            "predicted_class": row['Predicted Class'],
            "probability": row['Probability'],
            "rating": row['Rating'],
            "processed_date": datetime.now(),
        }
        documents.append(document)

    # Insertar en MongoDB
    if documents:
        collection.insert_many(documents)
        print(f"{len(documents)} documentos insertados en la base de datos.")
    else:
        print("No hay datos para guardar.")