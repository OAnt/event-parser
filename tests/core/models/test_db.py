import importlib

import pytest
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
