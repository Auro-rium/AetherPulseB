from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import certifi

def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "reddit_stream")
    try:
        # For Atlas connections, use proper SSL/TLS
        if mongo_uri.startswith("mongodb+srv://") or "mongodb.net" in mongo_uri:
            # Atlas connection with proper SSL
            client = MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=10000,
                tls=True, 
                tlsCAFile=certifi.where(),
                tlsAllowInvalidCertificates=False,
                tlsAllowInvalidHostnames=False
            )
        else:
            # Local MongoDB connection
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        client.server_info()  # Force connection
        db = client[db_name]
        return db
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        print("💡 For Atlas: Check your IP is whitelisted and credentials are correct")
        print("💡 For local: Make sure MongoDB is running: mongod")
        raise