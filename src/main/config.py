from pymongo import MongoClient

MONGO_URI = "mongodb+srv://juancamargo:J7MhkJyKJ1S1f6SO@cluster0.aa8jfqj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "ReviewsECI"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
