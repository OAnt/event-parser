import importlib
from types import SimpleNamespace

import pytest
from pydantic import BaseModel
from pymongo.errors import PyMongoError

from evp.core.models import db


@pytest.fixture
def fresh_db_module(monkeypatch):
    """Reload evp.core.models.db with a known environment and no cached client."""
    monkeypatch.setenv("MONGO_INITDB_ROOT_USERNAME", "root")
    monkeypatch.setenv("MONGO_INITDB_ROOT_PASSWORD", "s3cret")
    monkeypatch.setenv("MONGO_HOST", "mongo-host")
    monkeypatch.setenv("MONGO_PORT", "27018")
    monkeypatch.setenv("MONGO_DB", "events")
    module = importlib.reload(db)
    yield module
    monkeypatch.undo()
    importlib.reload(db)


def test_client_is_built_from_environment(fresh_db_module, monkeypatch):
    calls = []
    monkeypatch.setattr(
        fresh_db_module, "MongoClient", lambda uri: calls.append(uri) or object()
    )

    fresh_db_module.get_mongo_client()

    assert calls == ["mongodb://root:s3cret@mongo-host:27018"]


def test_client_is_created_only_once(fresh_db_module, monkeypatch):
    calls = []
    monkeypatch.setattr(
        fresh_db_module, "MongoClient", lambda uri: calls.append(uri) or object()
    )

    first = fresh_db_module.get_mongo_client()
    second = fresh_db_module.get_mongo_client()

    assert first is second
    assert len(calls) == 1


def test_get_mongo_db_uses_configured_database(fresh_db_module, monkeypatch):
    class FakeClient:
        def get_database(self, name):
            return f"db:{name}"

    monkeypatch.setattr(fresh_db_module, "MongoClient", lambda uri: FakeClient())

    assert fresh_db_module.get_mongo_db() == "db:events"


def test_mongo_server_responds_to_ping():
    """Integration test: needs a reachable MongoDB (e.g. `docker compose up mongo`)
    configured through the MONGO_* environment variables."""
    if not db.HOST:
        pytest.skip("MONGO_HOST is not set")

    client = db.get_mongo_client()
    try:
        client.admin.command("ping")
    except PyMongoError as exc:
        pytest.skip(f"MongoDB not reachable: {exc}")


def test_mongo_storage_uses_a_collection_named_after_the_model(monkeypatch):
    class FakeDb:
        def __getitem__(self, name):
            return f"collection:{name}"

    monkeypatch.setattr(db, "get_mongo_db", lambda: FakeDb())

    class Concert(BaseModel):
        title: str

    storage = db.MongoStorage(Concert)

    assert storage.collection == "collection:Concert"


class Post(BaseModel):
    post_id: str
    caption: str


class FakeCollection:
    def __init__(self, matched_count=0):
        self.matched_count = matched_count
        self.update_calls = []
        self.index_calls = []

    def update_one(self, query, update, upsert=False):
        self.update_calls.append((query, update, upsert))
        return SimpleNamespace(matched_count=self.matched_count)

    def create_index(self, field, **kwargs):
        self.index_calls.append((field, kwargs))


@pytest.fixture
def fake_collection(monkeypatch):
    collection = FakeCollection()

    class FakeDb:
        def __getitem__(self, name):
            return collection

    monkeypatch.setattr(db, "get_mongo_db", lambda: FakeDb())
    return collection


def test_pk_field_must_be_a_field_of_the_model():
    with pytest.raises(AssertionError):
        db.MongoStorage(Post, pk_field="nope")


def test_ensure_index_creates_a_unique_index_on_the_pk_field(fake_collection):
    db.MongoStorage(Post, pk_field="post_id").ensure_index()

    assert fake_collection.index_calls == [("post_id", {"unique": True})]


def test_ensure_index_does_nothing_without_a_pk_field(fake_collection):
    db.MongoStorage(Post).ensure_index()

    assert fake_collection.index_calls == []


def test_create_if_missing_returns_true_when_the_object_was_created(fake_collection):
    fake_collection.matched_count = 0
    storage = db.MongoStorage(Post, pk_field="post_id")

    assert storage.create_if_missing(Post(post_id="1", caption="hi")) is True


def test_create_if_missing_returns_false_when_the_object_already_exists(fake_collection):
    fake_collection.matched_count = 1
    storage = db.MongoStorage(Post, pk_field="post_id")

    assert storage.create_if_missing(Post(post_id="1", caption="hi")) is False


def test_create_if_missing_upserts_on_pk_with_set_on_insert(fake_collection):
    storage = db.MongoStorage(Post, pk_field="post_id")

    storage.create_if_missing(Post(post_id="1", caption="hi"))

    assert fake_collection.update_calls == [
        (
            {"post_id": "1"},
            {"$setOnInsert": {"post_id": "1", "caption": "hi"}},
            True,
        )
    ]


def test_validate_query_accepts_model_fields():
    db.MongoStorage(Post).validate_query(post_id="1", caption="hi")


def test_validate_query_rejects_unknown_fields():
    with pytest.raises(KeyError, match="nope"):
        db.MongoStorage(Post).validate_query(nope="x")
