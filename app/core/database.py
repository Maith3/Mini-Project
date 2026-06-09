from pymongo import MongoClient
from app.core.config import MONGO_URL

client = MongoClient(
    MONGO_URL)

db = client["cvd_database"]
users_collection = db['users']
reports_collection = db['reports']