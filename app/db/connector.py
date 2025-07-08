from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "reddit_stream")
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection
        db = client[db_name]
        return db
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        raise