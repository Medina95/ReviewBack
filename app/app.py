from flask import Flask, jsonify
from services import get_all_reviews, calculate_percentages

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
