import pytest
from mongomock import MongoClient
import app.db.mongodb as mdb

@pytest.fixture(autouse=True)
def init_db(monkeypatch):
    mock_client = MongoClient()
    mock_db = mock_db.get_database("vod_db")
    mock_collection = mock_collection.get_collection("vods")
    monkeypatch.setattr(mdb, 'client', mock_client)
    monkeypatch.setattr(mdb, 'db', mock_db)
    monkeypatch.setattr(mdb, 'vod_collection', mock_collection)
    yield

