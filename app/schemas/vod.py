from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, field_validator, field_serializer
from typing_extensions import Annotated
from datetime import date
from app.utils.data_utils import objectid_str

ObjectIdStr = Annotated[str, BeforeValidator(objectid_str)]

class VodBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    url: str = Field(..., pattern=r"^https?://")
    tags: List[str] = Field(default_factory=list)
    release_date: Optional[date]
    duration: Optional[int] = Field(None, ge=0, description="Length in minutes")
    genres: Optional[List[str]]


  # Validate từng item của tags không được rỗng (sau khi đã chuyển sang List[str])
    @field_validator("tags", mode="after")
    def tag_non_empty(cls, v: List[str]):
        for tag in v:
            if not tag or not tag.strip():
                raise ValueError("Tags must not be empty")
        return v

    
class VodCreate(VodBase):
    pass

class VodUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, pattern=r"^https?://")
    tags: Optional[List[str]]
    release_date: Optional[date]
    duration: Optional[int]
    genres: Optional[List[str]]
    
class VodResponse(VodBase):
   id: ObjectIdStr = Field(..., alias="_id")
   model_config = ConfigDict(populate_by_name=True)

   # Định dạng release_date thành chuỗi 'dd-mm-yyyy' khi trả response
   @field_serializer("release_date", mode="plain")
   def _fmt_date(self, v: Optional[date], info) -> Optional[str]:
       return v.strftime("%d-%m-%Y") if v else None

    