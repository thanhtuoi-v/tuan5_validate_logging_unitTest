from fastapi import APIRouter, HTTPException, status, Response
from typing import List
from app.schemas.vod import VodCreate, VodResponse, VodUpdate
import app.crud.vod as crud_vod
from app.utils.cache import get_or_set_cache
from app.core.logging import get_logger


router = APIRouter()
logger = get_logger(__name__)

@router.get("/vods", response_model=List[VodResponse])
async def read_vods():
    try:
        logger.info("Fetching all VODs")
        async def fetch(): 
            result = await crud_vod.list_vods()
            logger.debug(f"Fetched {len(result)} VODs from database")
            return result
        
        result = await get_or_set_cache("vods:all", fetch, ttl=120)
        logger.info(f"Retrieved {len(result)} VODs")
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