import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "app")

# Create global client (connection pool handled internally)
client = MongoClient(MONGO_URI)

# Database reference
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