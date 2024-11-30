class Review:
    def __init__(self, id,
                 text,
                 predicted_class, rating,
                 processed_date, probability) :
        self.id = id
        self.text = text
        self.predicted_class = predicted_class
        self.rating = rating
        self.processed_date = processed_date
        self.probability = probability

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "predicted_class": self.predicted_class,
            "rating": self.rating,
            "processed_date": self.processed_date,
            "probability": self.probability

        }


