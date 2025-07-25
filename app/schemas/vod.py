from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, field_validator
from typing_extensions import Annotated
from app.utils.data_utils import objectid_str

ObjectIdStr = Annotated[str, BeforeValidator(objectid_str)]

class VodBase(BaseModel):
    title: str = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    url: Optional[str] = Field(None, pattern=r"^https?://")
    country: Optional[str] = None
    tags: Optional[List[str]] = None
    release_year: Optional[int] = None
    duration: Optional[int] = Field(None, ge=0)
    genre: Optional[List[str]] = Field(default_factory=list)
    access_type: Optional[str] = 'free'
    age_rating: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    video_quality: Optional[str] = None
    view_count: Optional[int] = Field(default=0, ge=0)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    actors: Optional[List[str]] = None
    director: Optional[str] = None
    episode_number: Optional[int] = Field(None, ge=1)
   

  # Validate từng item của tags không được rỗng (sau khi đã chuyển sang List[str])
    # @field_validator("tags", mode="after")
    # def tag_non_empty(cls, v: List[str]):
    #     for tag in v:
    #         if not tag or not tag.strip():
    #             raise ValueError("Tags must not be empty")
    #     return v

    
class VodCreate(VodBase):
    pass

class VodUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    thumbnail_url: Optional[str] = None
    video_quality: Optional[str] = None
    
    
class VodResponse(VodBase):
   id: ObjectIdStr = Field(..., alias="_id")
   model_config = ConfigDict(populate_by_name=True)

# Schema cho pagination response
# T = TypeVar('T')

# class PaginatedResponse(BaseModel, Generic[T]):
#     items: List[T]
#     total: int
#     page: int
#     limit: int
#     total_pages: int
    
#     @classmethod
#     def create(cls, items: List[T], total: int, page: int, limit: int):
#         total_pages = (total + limit - 1) // limit  # Ceiling division
#         return cls(
#             items=items,
#             total=total,
#             page=page, 
#             limit=limit,
#             total_pages=total_pages
#         )



    