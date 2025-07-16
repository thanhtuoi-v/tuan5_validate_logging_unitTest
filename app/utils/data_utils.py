from datetime import datetime, date

def normalize_release_date(doc: dict) -> dict:
    rd = doc.get("release_date")
    if isinstance(rd, date):
        doc["release_date"] = datetime(rd.year, rd.month, rd.day)
    return doc

