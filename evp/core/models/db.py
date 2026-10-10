import os
import threading

from pymongo import MongoClient

USRNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
HOST = os.getenv("MONGO_HOST")
PORT = os.getenv("MONGO_PORT", 27017)
DB = os.getenv("MONGO_DB", "default")

_mongo_client = None

def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(f"mongodb://{USRNAME}:{PASSWORD}@{HOST}:{PORT}")
    return _mongo_client

def get_mongo_db():
    client = get_mongo_client()
    return client.get_database(DB)
