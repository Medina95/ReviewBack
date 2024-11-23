from config import db
from models import Review

reviews_collection = db["reviews"]


def get_all_reviews():
    reviews = reviews_collection.find()
    return [Review(**review) for review in reviews]


def calculate_percentages(reviews):
    count_goods = 1
    count_bads = 1

    for review in reviews:
        if "bueno" in review.score.lower():
            count_goods += 1
        else:
            count_bads += 1

    total_reviews = count_goods + count_bads
    good_percentage = int((count_goods / total_reviews) * 100) if total_reviews else 0
    bad_percentage = int((count_bads / total_reviews) * 100) if total_reviews else 0

    return [total_reviews, good_percentage, bad_percentage]
