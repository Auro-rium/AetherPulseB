from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def get_mongo_collection(
    mongo_uri: str,
    db_name: str,
    collection_name: str,
    timeout_ms: int = 5000
):
    """
    Connects to MongoDB and returns the specified collection.
    Raises an exception if connection fails.
    """
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
        # Force connection on a request as the connect=True parameter of MongoClient seems to be useless here
        client.server_info()
        db = client[db_name]
        collection = db[collection_name]
        print(f"Connected to MongoDB: {mongo_uri}, DB: {db_name}, Collection: {collection_name}")
        return collection
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        raise