from pymongo import MongoClient
from app.core.config import MONGO_URL

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=3000
)

db = client["cvd_database"]
users_collection = db['users']
reports_collection = db['reports']