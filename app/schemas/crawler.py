from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class RawMovieData(BaseModel):
    """
    Schema cho raw data từ crawler trước khi chuẩn hóa
    """
    url: str = Field(..., description="URL trang phim")
    title: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[str] = None  # Raw string từ HTML
    view_count: Optional[str] = None  # Raw string từ HTML
    release_year: Optional[str] = None  # Raw string từ HTML
    duration: Optional[str] = None  # Raw string như "1g 23ph"
    genre: Optional[List[str]] = None
    country: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    video_quality: Optional[str] = None
    actors: Optional[List[str]] = None
    director: Optional[str] = None
    age_rating: Optional[str] = None
    access_type:Optional[str] = None
    
class ProcessedMovieData(BaseModel):
    """
    Schema cho data đã chuẩn hóa, ready để save MongoDB
    """
    url: str
    title: str
    description: Optional[str] = None
    rating: Optional[float] = None  # Converted to float
    view_count: Optional[int] = None  # Converted to int
    release_year: Optional[int] = None  # Converted to int
    duration: Optional[int] = None  # Converted to minutes
    genre: Optional[List[str]] = Field(default_factory=list)
    country: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    video_quality: Optional[str] = None
    actors: Optional[List[str]] = Field(default_factory=list)
    director: Optional[str] = None
    age_rating: Optional[str] = None
    access_type:Optional[str] = None

class CrawlStatus(BaseModel):
    """
    Schema cho trạng thái crawling
    """
    total_urls: int
    processed: int
    failed: int
    status: str  # "idle", "running", "completed", "failed"
    current_url: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    errors: Optional[List[str]] = Field(default_factory=list)
