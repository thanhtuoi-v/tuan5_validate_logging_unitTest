from typing import List
from bson import ObjectId
from pymongo import ReturnDocument
from app.db.mongodb import vod_collection
from app.schemas.vod import VodCreate, VodUpdate, VodResponse
from app.utils.data_utils import normalize_release_date


async def list_vods() -> List[VodResponse]:
    cursor = vod_collection.find()
    results = []
    async for doc in cursor:
        results.append(VodResponse(**doc))
    return results

async def get_vod(vod_id: str) -> VodResponse | None:
    doc = await vod_collection.find_one({"_id": ObjectId(vod_id)})
    return VodResponse(**doc) if doc else None

async def create_vod(v: VodCreate) -> VodResponse:
    data = v.model_dump()
    data = normalize_release_date(data)
    res = await vod_collection.insert_one(data)
    new = await vod_collection.find_one({"_id": res.inserted_id})
    return VodResponse(**new)

async def update_vod(vod_id: str, v: VodUpdate) -> VodResponse | None:
    data = {k: x for k, x in v.model_dump().items() if x is not None}
    data = normalize_release_date(data)
    doc = await vod_collection.find_one_and_update(
        {"_id": ObjectId(vod_id)},
        {"$set": data},
        return_document=ReturnDocument.AFTER
    )
    return VodResponse(**doc) if doc else None

async def delete_vod(vod_id: str) -> bool:
    res = await vod_collection.delete_one({"_id": ObjectId(vod_id)})
    return res.deleted_count == 1
