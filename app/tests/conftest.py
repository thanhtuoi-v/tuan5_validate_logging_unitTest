import pytest
from mongomock import MongoClient
import app.db.mongodb as mdb

@pytest.fixture(autouse=True)
def init_db(monkeypatch):
    mock_client = MongoClient()
    mock_db = mock_client.vod_db
    mock_collection = mock_db.get_collection("vods")
    # mock_collection.insert_one({"title": "Example VOD"})
    print(f"Mock DB initialized: {list(mock_collection.find())}")
    monkeypatch.setattr(mdb, 'client', mock_client)
    monkeypatch.setattr(mdb, 'db', mock_db)
    monkeypatch.setattr(mdb, 'vod_collection', mock_collection)
    yield

