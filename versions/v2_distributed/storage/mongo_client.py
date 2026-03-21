import os
import time
from pymongo import MongoClient, errors

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "app")

MAX_RETRIES = 5
RETRY_DELAY = 20
# Create global client (connection pool handled internally)
client = MongoClient(MONGO_URI)

# Database reference
def create_mongo_client():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # trigger server selection to catch early errors
            client.admin.command('ping')
            return client
        except errors.PyMongoError as e:
            print(f"[Mongo] Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(20)

client = create_mongo_client()
db = client[MONGO_DB]

def get_collection(name: str):
    return db[name]


def insert_document(collection: str, data: dict):
    col = get_collection(collection)
    result = col.insert_one(data)
    return str(result.inserted_id)


def find_documents(collection: str, query: dict = {}):
    col = get_collection(collection)
    return list(col.find(query))


def find_one(collection: str, query: dict):
    col = get_collection(collection)
    return col.find_one(query)