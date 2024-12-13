from flask import Flask, jsonify, request
from flask_cors import CORS
from src.main.service.services import *
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={
    r"/api/*": {  # Aplica CORS solo a rutas que comienzan con /api/
        "origins": ["http://ec2-23-22-31-145.compute-1.amazonaws.com:3000"],  # Orígenes permitidos
        "methods": ["GET", "POST", "PUT", "DELETE"],  # Métodos HTTP permitidos
        "allow_headers": ["Content-Type", "Authorization"],  # Encabezados permitidos
    }
})

@app.route('/api/v1/reviews/hola', methods=['GET'])
def say_hello():
    return jsonify({"message": "Hola"})


@app.route('/api/v1/reviews/porcentajes', methods=['GET'])
def get_percentages():
    try:
        reviews = get_all_reviews()
        percentages = calculate_percentages(reviews)
        return jsonify(percentages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/reviews/predict', methods=['POST'])
def predict_toxicity():
    try:
        # Capturar JSON enviado por el cliente
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "El campo 'text' es obligatorio"}), 400

        # Realizar la predicción
        prediction = reviewToxic(text)
        return jsonify({"text": text, "prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/reviews/uploadDataFrame', methods=['POST'])
def upload_csv():
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({"error": "Archivo CSV no enviado."}), 400

        file = request.files['file']
        print("Archivo recibido:", file.filename)
        labels = json.loads(request.form.get("labels"))

        # Acceder a las posiciones directamente
        review_column = labels[0]
        rating_column = labels[1]
        # Obtener 'labels' del formulario (se espera que sea una cadena JSON)
        labels = {"Text": review_column, "Rating": rating_column}
       # labels = {"Text": request.get_json().get("Text"), "Rating": request.get_json().get("Rating")}

        # Verificar que el archivo no esté vacío
        if file.filename == '':
            return jsonify({"error": "Nombre del archivo vacío."}), 400

        # Leer el archivo CSV como DataFrame
        data = pd.read_csv(file)
        print(data.shape)
        # Procesar los datos
        results = reviewToxicFromData(data, labels)
        # Responder al cliente con los resultados
        return jsonify(results.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000,debug=True, ssl_context='adhoc' )

