from typing import List
from bson import ObjectId
from pymongo import ReturnDocument
import app.db.mongodb as db
from app.schemas.vod import VodCreate, VodUpdate, VodResponse
from app.utils.data_utils import normalize_release_date
from app.core.logging import get_logger

logger = get_logger(__name__)

async def list_vods() -> List[VodResponse]:
    try:
        cursor = db.vod_collection.find()
        results = []
        async for doc in cursor:
            results.append(VodResponse(**doc))
        logger.debug(f"Database returned {len(results)} VODs")
        return results
    except Exception as e:
        logger.error(f"Database error in list_vods: {str(e)}", exc_info=True)
        raise


async def get_vod(vod_id: str) -> VodResponse | None:
    try:
        doc = await db.vod_collection.find_one({"_id": ObjectId(vod_id)})
        if doc:
            logger.debug(f"Found VOD in database: {vod_id}")
            return VodResponse(**doc)
        else:
            logger.debug(f"VOD not found in database: {vod_id}")
            return None
    except Exception as e:
        logger.error(f"Database error in get_vod({vod_id}): {str(e)}", exc_info=True)
        raise

async def create_vod(v: VodCreate) -> VodResponse:
    try:
        data = v.model_dump()
        data = normalize_release_date(data)
        res = await db.vod_collection.insert_one(data)
        logger.debug(f"VOD inserted with ID: {res.inserted_id}")
        
        new = await db.vod_collection.find_one({"_id": res.inserted_id})
        return VodResponse(**new)
    except Exception as e:
        logger.error(f"Database error in create_vod({v.title}): {str(e)}", exc_info=True)
        raise

async def update_vod(vod_id: str, v: VodUpdate) -> VodResponse | None:
    try:
        data = {k: x for k, x in v.model_dump().items() if x is not None}
        data = normalize_release_date(data)

        doc = await db.vod_collection.find_one_and_update(
            {"_id": ObjectId(vod_id)},
            {"$set": data},
            return_document=ReturnDocument.AFTER
        )
        if doc:
            logger.debug(f"VOD updated: {vod_id}")
            return VodResponse(**doc)
        else:
            logger.debug(f"VOD not found for update: {vod_id}")
            return None
    except Exception as e:
        logger.error(f"Database error in update_vod({vod_id}): {str(e)}", exc_info=True)
        raise

async def delete_vod(vod_id: str) -> bool:
    try:
        res = await db.vod_collection.delete_one({"_id": ObjectId(vod_id)})
        success = res.deleted_count == 1
        if success:
            logger.debug(f"VOD deleted: {vod_id}")
        else:
            logger.debug(f"VOD not found for deletion: {vod_id}")
        return success
    except Exception as e:
        logger.error(f"Database error in delete_vod({vod_id}): {str(e)}", exc_info=True)
        raise
