from fastapi import APIRouter, HTTPException, status, Response, Query
from typing import List, Optional
from app.schemas.vod import VodCreate, VodResponse, VodUpdate
import app.crud.vod as crud_vod
from app.utils.cache import get_or_set_cache
from app.core.logging import get_logger
from app.db.indexes import create_indexes, get_indexes


router = APIRouter()
logger = get_logger(__name__)

@router.get("/vods", response_model=List[VodResponse])
async def read_vods(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên video"),
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(10, ge=1, le=50, description="Số item mỗi trang"),
    sort_by: str = Query("release_year", description="Sắp xếp theo field")
):
    try:
        # Tính skip từ page
        skip = (page - 1) * limit
        
        if search:
            logger.info(f"Searching VODs with query: '{search}' (page: {page}, limit: {limit})")
        else:
            logger.info(f"Fetching VODs (page: {page}, limit: {limit})")
            
        async def fetch(): 
            result = await crud_vod.list_vods(search=search, limit=limit, skip=skip, sort_by=sort_by)
            log_msg = f"Fetched {len(result)} VODs from database (page: {page})"
            if search:
                log_msg += f" for search: '{search}'"
            logger.debug(log_msg)
            return result
        
        # Cache key bao gồm pagination params
        cache_key = f"vods:search:{search}:page:{page}:limit:{limit}:sort:{sort_by}" if search else f"vods:all:page:{page}:limit:{limit}:sort:{sort_by}"
        
        # Cache TTL khác nhau: search ngắn hơn, list normal lâu hơn
        ttl = 300 if not search else 120  # 5 phút vs 2 phút
        result = await get_or_set_cache(cache_key, fetch, ttl=ttl)
        log_msg = f"Retrieved {len(result)} VODs"
        if search:
            log_msg += f" matching '{search}'"
        logger.info(log_msg)
        return result
    except Exception as e:
        logger.error(f"Failed to fetch VODs: {str(e)}", exc_info=True)
        raise 


@router.get("/vods/{vod_id}",response_model=VodResponse)
async def read_doc(vod_id:str):
    try:
        logger.info(f"Fetching VOD with ID: {vod_id}")
        vod = await crud_vod.get_vod(vod_id)
        if not vod:
            logger.warning(f"VOD not found: {vod_id}")
            raise HTTPException(status_code=404, detail="VOD not found")
        logger.info(f"Retrieved VOD: {vod_id}")
        return vod
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VOD {vod_id}: {str(e)}", exc_info=True)
        raise

        

@router.post("/vods", response_model=VodResponse, status_code=status.HTTP_201_CREATED)
async def create_vod(v: VodCreate):
    try:
        logger.info(f"Creating new VOD: '{v.title}'")
        result = await crud_vod.create_vod(v)
        logger.info(f"Created VOD with ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create VOD '{v.title}': {str(e)}", exc_info=True)
        raise

@router.put("/vods/{vod_id}", response_model=VodResponse,status_code=status.HTTP_202_ACCEPTED)
async def update_vod(vod_id: str, v: VodUpdate):
    try: 
        logger.info(f"Udating VOD: {vod_id}")
        upd = await crud_vod.update_vod(vod_id, v)
        if not upd:
            logger.warning(f"VOD not found for update: {vod_id}")
            raise HTTPException(status_code=404, detail="VOD not found")
        logger.info(f"Updated VOD: {vod_id}")
        return upd
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update VOD {vod_id}: {str(e)}", exc_info=True)
        raise



@router.delete("/vods/{vod_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vod(vod_id: str):
    try:
        logger.info(f"Deleteting VOD: {vod_id}")
        success = await crud_vod.delete_vod(vod_id)
        if not success:
            logger.warning(f"VOD not found for deletion: {vod_id}")
            raise HTTPException(status_code=404, detail="VOD not found")
        logger.info(f"Deleted VOD: {vod_id}")
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete VOD {vod_id}: {str(e)}", exc_info=True)
        raise

# Admin endpoints để quản lý indexes
@router.post("/admin/indexes", status_code=status.HTTP_201_CREATED)
async def create_database_indexes():
    """
    Tạo indexes cho database để tối ưu performance
    """
    try:
        logger.info("Creating database indexes")
        await create_indexes()
        logger.info("Database indexes created successfully")
        return {"message": "Indexes created successfully"}
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create indexes")

@router.get("/admin/indexes")
async def list_database_indexes():
    """
    Lấy danh sách indexes hiện tại
    """
    try:
        logger.info("Fetching database indexes")
        indexes = await get_indexes()
        return {"indexes": indexes}
    except Exception as e:
        logger.error(f"Failed to get indexes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get indexes")