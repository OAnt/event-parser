import os
import logging
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Type, Generic, Optional, List, ClassVar

from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.results import UpdateResult

log = logging.getLogger(__name__)

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
            log.info(f"creating index on {self.pk_field} for {self.model.__name__}")
            self.collection.create_index(self.pk_field, unique=True)

    @property
    def collection(self) -> Collection[dict[str, Any]]:
        db = get_mongo_db()
        return db[self.model.__name__]

    def validate_query(self, **kwargs):
        fields = self.model.model_fields
        for key in kwargs:
            if not key in fields:
                raise AttributeError(f"{key} if not a field of model {self.model}")

    def _atomic_operation(self, operation: str, obj: T, update: dict[str, Any], upsert=False) -> UpdateResult:
        assert self.pk_field, f"{self.model.__name__}, does not have pk, cannot perform atomic operations"
        result = self.collection.update_one(
            {self.pk_field: getattr(obj, self.pk_field)},
            {operation: update},
            upsert=upsert
        )
        return result

    def compare_and_set_field(self, obj: T, fields: List[str]) -> bool:
        """
        Set a fields to match obj's, return if any modification where made
        """
        update = {}
        for field in fields:
            _obj = obj
            for subfield in field.split("."):
                try:
                    _obj = getattr(_obj, subfield)
                except AttributeError:
                    raise AttributeError(f"{subfield} is not a member of {_obj}")
            update[field] = _obj
        result = self._atomic_operation("$set", obj, update)
        return result.modified_count > 0

    def create_if_missing(self, obj: T) -> bool:
        """
        create obj if does not exist, returns if was indeed created
        """
        _obj = obj.model_dump(mode="json")
        result = self._atomic_operation("$setOnInsert", obj, _obj, upsert=True)
        return bool(not result.matched_count)

    def get(self, **kwargs):
        self.validate_query(**kwargs)
        data = self.collection.find_one(kwargs)
        return self.model(**data)


class StoredModelMixin(ABC):
    storage: ClassVar[MongoStorage[T]]

    @abstractmethod
    def model_dump(self, *args, **kwargs):...

    def create_if_missing(self):
        return self.storage.create_if_missing(self)

    def insert(self):
        self.storage.collection.insert_one(self.model_dump(mode="json"))


storages = {}


def register_model(model: Type[T], *args, **kwargs):
    if model.__name__ in storages:
        log.warn(f"{model.__name__} is already registered")
        return storages[model.__name__]
    else:
        storage = MongoStorage(model, *args, **kwargs)
        storages[model.__name__] = storage
        return storage


def ensure_indexes():
    for model_name, storage in storages.items():
        storage.ensure_index()
