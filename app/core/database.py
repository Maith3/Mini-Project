from pymongo import MongoClient
from app.core.config import MONGO_URL

client = MongoClient(MONGO_URL)
try: 
    client.admin.command('ping')
    print('MongoDB Connected Successfully!')
except Exception as e:
    print(e)

db = client["cvd_database"]
users_collection = db['users']
reports_collection = db['reports']