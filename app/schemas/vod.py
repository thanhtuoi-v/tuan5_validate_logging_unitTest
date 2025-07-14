from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, field_validator
from bson import ObjectId
from typing_extensions import Annotated

def objectid_str(v):
    if not isinstance(v, ObjectId):
        raise TypeError("ObjectId required")
    return str(v)

ObjectIdStr = Annotated[str, BeforeValidator(objectid_str)]

class VodBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Tiêu đề VOD")
    description: Optional[str] = Field(None, max_length=500)
    url: str = Field(..., pattern=r"^https?://", description="Đường dẫn phải bắt đầu bằng http:// hoặc https://")
    tags: List[str] = Field(default_factory=list)

  # validate từng item sau khi Pydantic đã coercion thành List[str]
    @field_validator("tags", mode="after")
    def tag_non_empty(cls, v: List[str]):
        for tag in v:
            if not tag or not tag.strip():
                raise ValueError("Mỗi tag phải là chuỗi không trống")
        return v

class VodCreate(VodBase):
    pass

class VodUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, pattern=r"^https?://")
    tags: Optional[List[str]]

class VodResponse(VodBase):
   id: ObjectIdStr = Field(..., alias="_id")
   model_config = ConfigDict(populate_by_name=True)