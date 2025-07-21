from datetime import datetime, date
from bson import ObjectId

def normalize_release_date(doc: dict) -> dict:
    rd = doc.get("release_date")
    if isinstance(rd, date):
        doc["release_date"] = datetime(rd.year, rd.month, rd.day)
    return doc

def objectid_str(v):
    if not isinstance(v, ObjectId):
        raise TypeError("ObjectId required")
    return str(v)
