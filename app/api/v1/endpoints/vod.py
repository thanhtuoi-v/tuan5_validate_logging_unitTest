from fastapi import APIRouter, HTTPException, status, Response
from typing import List
from app.schemas.vod import VodCreate, VodResponse, VodUpdate
import app.crud.vod as crud_vod
from app.utils.cache import get_or_set_cache

router = APIRouter()

@router.get("/vods", response_model=List[VodResponse],response_model_by_alias=False)
async def read_vods():
    async def fetch(): return await crud_vod.list_vods()
    return await get_or_set_cache("vods:all", fetch, ttl=120)

@router.get("/vods/{vod_id}", response_model=VodResponse,response_model_by_alias=False)
async def read_vod(vod_id: str):
    vod = await crud_vod.get_vod(vod_id)
    if not vod:
        raise HTTPException(status_code=404, detail="VOD not found")
    return vod

@router.post("/vods", response_model=VodResponse, status_code=status.HTTP_201_CREATED)
async def create_vod(v: VodCreate):
    return await crud_vod.create_vod(v)

@router.put("/vods/{vod_id}", response_model=VodResponse)
async def update_vod(vod_id: str, v: VodUpdate):
    upd = await crud_vod.update_vod(vod_id, v)
    if not upd:
        raise HTTPException(status_code=404, detail="VOD not found")
    return upd

@router.delete("/vods/{vod_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vod(vod_id: str):
    success = await crud_vod.delete_vod(vod_id)
    if not success:
        raise HTTPException(status_code=404, detail="VOD not found")
    return 
