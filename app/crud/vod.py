from typing import List
from bson import ObjectId
from pymongo import ReturnDocument
import app.db.mongodb as db
from app.schemas.vod import VodCreate, VodUpdate, VodResponse
from app.utils.data_utils import normalize_release_date
from app.core.logging import get_logger

logger = get_logger(__name__)

async def list_vods(search: str = None, limit: int = 10, skip: int = 0, sort_by: str = "release_year") -> List[VodResponse]:
    try:
        # Tạo filter query
        filter_query = {}
        if search:
            # Sử dụng text search thay vì regex để tối ưu hơn
            filter_query["$text"] = {"$search": search}
            logger.debug(f"Text searching VODs with query: {search}")
        
        # Tạo sort criteria
        sort_criteria = []
        if search:
            # Khi search, sort theo score trước
            sort_criteria.append(("score", {"$meta": "textScore"}))
        
        if sort_by == "release_year":
            sort_criteria.append(("release_year", -1))
        elif sort_by == "title":
            sort_criteria.append(("title", 1))
        
        # Execute query với pagination
        cursor = db.vod_collection.find(filter_query).sort(sort_criteria).skip(skip).limit(limit)
        
        results = []
        async for doc in cursor:
            results.append(VodResponse(**doc))
        
        log_msg = f"Database returned {len(results)} VODs (limit: {limit}, skip: {skip})"
        if search:
            log_msg += f" for search: '{search}'"
        logger.debug(log_msg)
        return results
    except Exception as e:
        logger.error(f"Database error in list_vods: {str(e)}", exc_info=True)
        raise

async def count_vods(search: str = None) -> int:
    """
    Đếm tổng số VODs cho pagination
    """
    try:
        filter_query = {}
        if search:
            filter_query["$text"] = {"$search": search}
            
        count = await db.vod_collection.count_documents(filter_query)
        logger.debug(f"Count VODs: {count}")
        return count
    except Exception as e:
        logger.error(f"Database error in count_vods: {str(e)}", exc_info=True)
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
