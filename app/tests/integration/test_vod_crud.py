import pytest
from bson import ObjectId
from datetime import date
from app.crud.vod import create_vod, get_vod, list_vods, update_vod, delete_vod
from app.schemas.vod import VodCreate, VodUpdate
import unittest.mock as patch

# @pytest.mark.anyio
# async def test_list_vods_empty():
#     result = await list_vods()
#     print(f"list of data {result}")
#     assert result == []

# @pytest.mark.anyio
# async def test_create_and_get_vod():
#     payload = VodCreate(
#         title="Test VOD",
#         url="http://example.com/video.mp4",
#         description="Mô tả sample",
#         tags=["a", "b"]
#     )
#     created = await create_vod(payload)
#     # Kiểm tra id và dữ liệu
#     assert isinstance(created.id, str) and ObjectId.is_valid(created.id)
#     assert created.title == payload.title

#     fetched = await get_vod(created.id)
#     assert fetched is not None
#     assert fetched.id == created.id
#     assert fetched.title == payload.title

# @pytest.mark.anyio
# async def test_update_vod_partial():
#     payload = VodCreate(
#         title="Original",
#         url="http://orig.com",
#         description="Desc",
#         tags=["x"]
#     )
#     created = await create_vod(payload)
#     # Chỉ update title
#     upd = VodUpdate(title="Updated")
#     updated = await update_vod(created.id, upd)
#     assert updated is not None
#     assert updated.title == "Updated"
#     # Các field không thay đổi
#     assert updated.description == payload.description
#     assert updated.tags == payload.tags

# @pytest.mark.anyio
# async def test_update_vod_full():
#     payload = VodCreate(
#         title="FullOriginal",
#         url="http://full.com",
#         description="DescFull",
#         tags=["x"]
#     )
#     created = await create_vod(payload)
#     # Update tất cả field
#     upd = VodUpdate(
#         title="NewTitle",
#         url="https://new.com",
#         description="NewDesc",
#         tags=["x", "y"]
#     )
#     updated = await update_vod(created.id, upd)
#     assert updated.title == upd.title
#     assert updated.url == upd.url
#     assert updated.description == upd.description
#     assert updated.tags == upd.tags

# @pytest.mark.anyio
# async def test_update_nonexistent_vod():
#     fake_id = ObjectId().hex
#     result = await update_vod(fake_id, VodUpdate(title="Nope"))
#     assert result is None

# @pytest.mark.anyio
# async def test_delete_vod():
#     payload = VodCreate(
#         title="ToDelete",
#         url="http://del.com",
#         description="DescDel",
#         tags=["d"]
#     )
#     created = await create_vod(payload)
#     ok = await delete_vod(created.id)
#     assert ok is True
#     # Đã xoá
#     assert await get_vod(created.id) is None

# @pytest.mark.anyio
# async def test_delete_nonexistent_vod():
#     fake_id = ObjectId().hex
#     ok = await delete_vod(fake_id)
#     assert ok is False

# @pytest.mark.anyio
# async def test_list_vods_with_data(init_db):
#     # Chèn 2 bản ghi sample
#     doc1 = {"_id": ObjectId(), "title": "A", "url": "u1", "description": "d1", "tags": [], "release_date": None}
#     doc2 = {"_id": ObjectId(), "title": "B", "url": "u2", "description": "d2", "tags": [], "release_date": None}
#     mdb.vod_collection.insert_many([doc1, doc2])

#     result = await list_vods()
#     ids = {v.id for v in result}
#     assert ids == {str(doc1["_id"]), str(doc2["_id"])}

# @pytest.mark.anyio
# async def test_create_with_release_date(init_db):
#     payload = VodCreate(
#         title="WithDate", url="u", description="", tags=[], release_date=date(2025,5,5)
#     )
#     created = await create_vod(payload)
#     # release_date trong response phải là datetime tương ứng
#     assert created.release_date.date() == date(2025,5,5)