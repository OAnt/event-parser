import importlib
import uuid

import pytest
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError, PyMongoError

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
    likes: int = 0


@pytest.fixture
def throwaway_db(monkeypatch):
    """A randomly named database, dropped after the test, so the configured one
    is never touched. Skips when MongoDB is not configured or not reachable."""
    if not db.HOST:
        pytest.skip("MONGO_HOST is not set")

    client = db.get_mongo_client()
    try:
        client.admin.command("ping")
    except PyMongoError as exc:
        pytest.skip(f"MongoDB not reachable: {exc}")

    name = f"evp_test_{uuid.uuid4().hex}"
    database = client.get_database(name)
    monkeypatch.setattr(db, "get_mongo_db", lambda: database)
    yield database
    client.drop_database(name)


@pytest.fixture
def storage(throwaway_db):
    storage = db.MongoStorage(Post, pk_field="post_id")
    storage.ensure_index()
    return storage


def stored(storage, post_id):
    return storage.collection.find_one({"post_id": post_id}, {"_id": 0})


def test_pk_field_must_be_a_field_of_the_model():
    with pytest.raises(AssertionError):
        db.MongoStorage(Post, pk_field="nope")


def test_ensure_index_creates_a_unique_index_on_the_pk_field(throwaway_db):
    storage = db.MongoStorage(Post, pk_field="post_id")

    storage.ensure_index()

    indexes = storage.collection.index_information()
    assert any(
        info["key"] == [("post_id", 1)] and info.get("unique") for info in indexes.values()
    )


def test_ensure_index_does_nothing_without_a_pk_field(throwaway_db):
    storage = db.MongoStorage(Post)

    storage.ensure_index()

    assert list(storage.collection.index_information()) in ([], ["_id_"])


def test_unique_index_rejects_duplicate_pks(storage):
    storage.collection.insert_one({"post_id": "1", "caption": "a"})

    with pytest.raises(DuplicateKeyError):
        storage.collection.insert_one({"post_id": "1", "caption": "b"})


def test_create_if_missing_returns_true_when_the_object_was_created(storage):
    assert storage.create_if_missing(Post(post_id="1", caption="hi")) is True


def test_create_if_missing_returns_false_when_the_object_already_exists(storage):
    storage.create_if_missing(Post(post_id="1", caption="hi"))

    assert storage.create_if_missing(Post(post_id="1", caption="hi")) is False


def test_create_if_missing_stores_the_whole_object(storage):
    storage.create_if_missing(Post(post_id="1", caption="hi", likes=3))

    assert stored(storage, "1") == {"post_id": "1", "caption": "hi", "likes": 3}


def test_create_if_missing_does_not_overwrite_an_existing_object(storage):
    storage.create_if_missing(Post(post_id="1", caption="first"))
    storage.create_if_missing(Post(post_id="1", caption="second"))

    assert storage.collection.count_documents({}) == 1
    assert stored(storage, "1")["caption"] == "first"


def test_validate_query_accepts_model_fields():
    db.MongoStorage(Post).validate_query(post_id="1", caption="hi")


def test_validate_query_rejects_unknown_fields():
    with pytest.raises(KeyError, match="nope"):
        db.MongoStorage(Post).validate_query(nope="x")


def test_compare_and_set_field_updates_the_requested_field(storage):
    storage.create_if_missing(Post(post_id="1", caption="old", likes=3))

    res = storage.compare_and_set_field(
        Post(post_id="1", caption="new", likes=99), ["caption"]
    )

    assert res
    
    assert stored(storage, "1") == {"post_id": "1", "caption": "new", "likes": 3}

def test_compare_and_set_field_reports_not_updating_at_field(storage):
    storage.create_if_missing(Post(post_id="1", caption="old", likes=3))

    res = storage.compare_and_set_field(
        Post(post_id="1", caption="old", likes=99), ["caption"]
    )

    assert not res
    
    assert stored(storage, "1") == {"post_id": "1", "caption": "old", "likes": 3}


def test_compare_and_set_field_can_set_several_fields(storage):
    storage.create_if_missing(Post(post_id="1", caption="old", likes=3))

    res = storage.compare_and_set_field(
        Post(post_id="1", caption="new", likes=99), ["caption", "likes"]
    )

    assert res

    assert stored(storage, "1") == {"post_id": "1", "caption": "new", "likes": 99}


def test_compare_and_set_field_does_not_create_a_missing_document(storage):
    res = storage.compare_and_set_field(
        Post(post_id="1", caption="hi", likes=5), ["caption"]
    )

    assert not res

    assert storage.collection.count_documents({}) == 0


def test_compare_and_set_field_does_not_touch_other_documents(storage):
    storage.create_if_missing(Post(post_id="1", caption="one"))
    storage.create_if_missing(Post(post_id="2", caption="two"))

    res = storage.compare_and_set_field(Post(post_id="1", caption="changed"), ["caption"])

    assert res

    assert stored(storage, "2") == {"post_id": "2", "caption": "two", "likes": 0}


def test_compare_and_set_field_rejects_unknown_fields_without_writing(storage):
    with pytest.raises(KeyError, match="nope"):
        storage.compare_and_set_field(Post(post_id="1", caption="hi"), ["nope"])

    assert storage.collection.count_documents({}) == 0


def test_compare_and_set_field_requires_a_pk_field(throwaway_db):
    storage = db.MongoStorage(Post)

    with pytest.raises(AssertionError):
        storage.compare_and_set_field(Post(post_id="1", caption="hi"), ["caption"])

    assert storage.collection.count_documents({}) == 0
