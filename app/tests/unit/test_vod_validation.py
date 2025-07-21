import pytest
from pydantic import ValidationError
from bson import ObjectId
from datetime import date

from app.utils.data_utils import objectid_str, normalize_release_date
from app.schemas.vod import VodCreate, VodResponse, VodBase, VodUpdate

def test_objectid_str_accepts_objectid():
    oid = ObjectId()
    # BeforeValidator sẽ chuyển ObjectId → str
    assert objectid_str(oid) == str(oid)

def test_objectid_str_rejects_other_types():
    with pytest.raises(TypeError):
        objectid_str("not-an-objectid")

def test_vodcreate_with_valid_data():
    data = {
        "title": "My Movie",
        "description": "A valid description",
        "url": "https://vod.com",
        "tags": ["tag1", "tag2"],
        "release_date": "2023-12-31",
        "duration": 90,
        "genres": ["Action"]
    }
    m = VodCreate(**data)
    assert m.title == "My Movie"
    assert isinstance(m.release_date, date)
    assert m.tags == ["tag1", "tag2"]
    assert m.duration == 90
    assert m.genres == ["Action"]

def test_vodcreate_rejects_invalid():
    bad = {
        "title": "T", 
        "url": "ftp://nope", 
        "tags": ["valid", "  "],  
    }
   
    with pytest.raises(ValidationError) as exc:
        VodCreate(**bad)
    err = exc.value.errors()
    locs = [ e["loc"] for e in err ]
    assert ("title",) in locs
    assert ("url",) in locs
    assert ("tags",) in locs  
    

def test_vodcreate_rejects_duration():
    data = {
        "title": "Valid Title",
        "url": "http://vod.com",
        "duration": -10,  # < 0
    }
    with pytest.raises(ValidationError) as exc:
        VodCreate(**data)
    err = exc.value.errors()[0]
    assert err["loc"] == ("duration",)


def test_vodbase_title_length_constraints():
    too_short = {"title": "Hi", "url": "http://vod.com"}
    too_long = {"title": "X" * 101, "url": "http://vod.com"}
    for payload in (too_short, too_long):
        with pytest.raises(ValidationError):
            VodBase(**payload)

def test_vodresponse_serializes_id_and_date():
    oid = ObjectId()
    base = {
        "title": "Movie",
        "url": "http://example.com",
        "tags": [],
    }
    resp = VodResponse(_id=oid, **base)
    assert resp.id == str(oid)
    dumped = resp.model_dump(by_alias=True)
    assert dumped["_id"] == str(oid)
    assert dumped.get("release_date") is None

    # khi có release_date:
    resp2 = VodResponse(
        _id=oid,
        title="Movie",
        url="http://example.com",
        tags=[],
        release_date=date(2025, 7, 18),
    )
    d2 = resp2.model_dump(by_alias=True)
    assert d2["release_date"] == "18-07-2025"


def test_vodcreate_rejects_description_too_long():
    data = {"title": "Valid Title", 
            "url": "http://vod.com", 
            "description": "A" * 501}
    with pytest.raises(ValidationError) as exc:
        VodCreate(**data)
    err = exc.value.errors()[0]
    assert err["loc"] == ("description",)








