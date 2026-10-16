import os
from typing import Any, TypeVar, Type, Generic, Optional

from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection

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

T = TypeVar("T", bound="BaseModel")

class MongoStorage(Generic[T]):
    def __init__(self, model: Type[T], pk_field: Optional[str] = None): 
        self.model = model
        if pk_field:
            assert pk_field in model.model_fields
        self.pk_field = pk_field

    def ensure_index(self):
        if self.pk_field:
            self.collection.create_index(self.pk_field, unique=True)

    @property
    def collection(self) -> Collection[dict[str, Any]]:
        db = get_mongo_db()
        return db[self.model.__name__]

    def create_if_missing(self, obj: T) -> bool:
        """
        create obj if does not exist, returns if was indeed created
        """
        _obj = obj.model_dump(mode="json")
        result = self.collection.update_one(
            {self.pk_field: getattr(obj, self.pk_field)},
            {"$setOnInsert": _obj},
            upsert=True
        )
        return bool(not result.matched_count)

    def validate_query(self, **kwargs):
        fields = self.model.model_fields
        for key in kwargs:
            if not key in fields:
                raise KeyError(f"{key} if not a field of model {self.model}")

    def get(self, **kwargs):
        self.validate_query(**kwargs)
        data = self.collection.find_one(kwargs)
        return self.model(**data)
