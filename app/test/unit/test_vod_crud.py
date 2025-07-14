import pytest
from bson import ObjectId
from app.crud.vod import create_vod, get_vod, list_vods, update_vod, delete_vod

from app.schemas.vod import VodCreate, VodUpdate

@pytest.fixture
def sample_vod():
    return VodCreate(
        title="Test VOD",
        description="Mô tả test",
        url="http://example.com",
        tags=["test", "vod"]
    )

@pytest.mark.asyncio
async def test_create_and_get_vod(sample_vod):
    created = await create_vod(sample_vod)
    print(f"Created VOD: {created}")               
    assert isinstance(created.id, str)                   
    fetched = await get_vod(created.id) 
    print(f"Fetched VOD: {fetched}")                
    assert fetched.title == sample_vod.title             


@pytest.mark.asyncio
async def test_list_vods(sample_vod):
    await create_vod(sample_vod)
    lst = await list_vods()
    assert isinstance(lst, list)
    assert any(v.title == sample_vod.title for v in lst)


@pytest.mark.asyncio
async def test_update_vod(sample_vod):
    created = await create_vod(sample_vod)
    upd_data = VodUpdate(title="Updated Title")
    updated = await update_vod(created.id, upd_data)
    assert updated.title == "Updated Title"


@pytest.mark.asyncio
async def test_delete_vod(sample_vod):
    created = await create_vod(sample_vod)
    result = await delete_vod(created.id)
    assert result is True
    assert await get_vod(created.id) is None

