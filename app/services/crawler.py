import asyncio
import re
from typing import List, Optional
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser

from app.schemas.crawler import RawMovieData, ProcessedMovieData
from app.schemas.vod import VodCreate
from app.core.logging import get_logger
import app.crud.vod as crud_vod

logger = get_logger(__name__)

class CrawlerService:
    """
    Service để crawl dữ liệu phim từ vieon.vn
    """
    
    MOVIE_URLS = [
        "https://vieon.vn/cuoc-ruot-duoi-tai-cuc-dia.html",
        
    ]
    
    def __init__(self):
        self.status = {
            "total_urls": len(self.MOVIE_URLS),
            "processed": 0,
            "failed": 0,
            "status": "idle",
            "current_url": None,
            "start_time": None,
            "end_time": None,
            "errors": []
        }
    
    async def crawl_single_movie(self, url: str) -> Optional[RawMovieData]:
        """
        Crawl một trang phim cụ thể
        """
        try:
            logger.info(f"Crawling movie: {url}")
            
            # HTTP request với httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
            
            # Parse HTML với selectolax
            tree = HTMLParser(response.text)
            metadata = self._extract_metadata_by_position(tree)
            # Extract dữ liệu theo HTML structure
            raw_data = RawMovieData(
            url=url,
            title=self._extract_title(tree),
            description=self._extract_description(tree),
            rating=self._extract_rating(tree),
            view_count=self._extract_view_count(tree),
            # Dùng data từ metadata
            release_year=metadata.get('release_year'),
            duration=metadata.get('duration'),
            country=metadata.get('country'),
            video_quality=metadata.get('video_quality'),
            age_rating=metadata.get('age_rating'),
            access_type=metadata.get('access_type'), 
            genre=metadata.get('genre'),
            director=metadata.get('director'),
            # Extract riêng
            thumbnail_url=self._extract_thumbnail(tree),
            video_url=self._extract_video_url(tree),
            actors=self._extract_actors(tree),
            
        )
            
            logger.info(f"Successfully crawled: {raw_data.title}")
            return raw_data
            
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {str(e)}", exc_info=True)
            return None
    
    def _extract_title(self, tree: HTMLParser) -> Optional[str]:
        """Extract title từ h2.card_title"""
        try:
            element = tree.css_first('h2.card__title')
            return element.text().strip() if element else None
        except Exception:
            return None
    
    def _extract_description(self, tree: HTMLParser) -> Optional[str]:
        """Extract description từ div.intro_info_desc"""
        try:
            element = tree.css_first('.intro__info__desc')
            return element.text().strip() if element else None
        except Exception:
            return None
    
    def _extract_rating(self, tree: HTMLParser) -> Optional[str]:
        """Extract rating từ span.rating__summary"""
        try:
            element = tree.css_first('span.rating__summary')
            logger.info(f"rating: {element.text()}")
            return element.text().strip() if element else None
        except Exception:
            return None
    
    def _extract_view_count(self, tree: HTMLParser) -> Optional[str]:
        """Extract view count từ span.viewer_summary"""
        try:
            element = tree.css_first('.viewer .viewer__summary')
            return element.text().strip() if element else None
        except Exception:
            return None

    def _extract_metadata_by_position(self, tree: HTMLParser) -> dict:
        """
        Extract metadata theo thứ tự position vì các element có cùng class
        Return dict với các key: duration, country, video_quality
        """
        try:
            # Tìm tất cả label.Tag_Base__Jb03L theo thứ tự xuất hiện
            elements_1 = tree.css('.intro__info .intro__info-left .Tag_Base__Jb03L span')
            logger.info(f"Total elements_1 found: {len(elements_1)}")
            elements_2 = tree.css('.intro__info .intro__info-right .tags-group')
            logger.info(f"Total elements_2 found: {len(elements_2)}")
            result= {
                'release_year': None,
                'access_type': 'free',
                'age_rating':None,
                'duration': None, 
                'country': None,
                'video_quality': None,
                'director': None,
                'genre': [],
            }
            
            for i, element in enumerate(elements_1):
                text = element.text().strip()
                logger.info(f"Position_1 {i}: {text}")  # Debug log
                
                # Position 0: Năm (4 chữ số, bắt đầu 20xx) or access_type
                if i == 0:
                    if len(text) == 4 and text.startswith('20'):
                        result['release_year'] = text
                    else:
                        result['access_type'] = text
                # Position 1: Độ tuổi phù hợp
                elif i == 1:
                    result['age_rating'] = text
                
                # Position 2: Country
                elif i == 2:
                    result['country'] = text
                
                # Position 3: Duration format "1g 23ph"
                elif i == 3:
                    result['duration'] = text
                
                # Position 4: Video quality
                else:
                    result['video_quality'] = text
   
            for i, group in enumerate(elements_2):
                label = group.css_first('label')
                if not label:
                    continue
                label_text = label.text().strip()
                logger.info(f"Position_2 {i}: {text}")  # Debug log
                if label_text.startswith("Đạo diễn"):
                    link = group.css('a')
                    if link:
                        result['director'] = link.text().strip()
                        logger.info(f"director: {link}")

                elif label_text.startswith("Thể loại"):
                    links = group.css('a')
                    result['genre'] = [link.text().strip() for link in links]
                    logger.info(f"genre {link}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract metadata by position: {str(e)}")
            return result
    
    def _extract_thumbnail(self, tree: HTMLParser) -> Optional[str]:
        """Extract thumbnail URL từ img tags"""
        try:
            # Tìm img trong player poster hoặc image-block
            img = tree.css_first('section.section--vod-detail img.billboard__image__hero')
            if img:
                src = img.attributes.get('src') 
                return src
            return None
        except Exception:
            return None
    
    def _extract_video_url(self, tree: HTMLParser) -> Optional[str]:
        """Extract video URL từ video tag """
        try:
            # Tìm video tag
            video = tree.css_first('video#VIE_PLAYER')
            if video:
                src = video.attributes.get('src')
                if src:
                    return src
            return None
        except Exception:
            return None
    
    def _extract_actors(self, tree: HTMLParser) -> Optional[List[str]]:
        """Extract actors từ tags-group links"""
        try:
            actors = []
            groups = tree.css('.intro__info-right .tags-group')
            for group in groups:
                label = group.css_first('label')
                if label and label.text().strip().startswith("Diễn viên"):
                # Lấy tất cả thẻ <a> trong group diễn viên
                    links = group.css('a')
                for link in links:
                    actors.append(link.text().strip())
                break  

            return actors if actors else None
        except Exception:
            return None
         
    def normalize_data(self, raw_data: RawMovieData) -> ProcessedMovieData:
        """
        Chuẩn hóa raw data thành format chuẩn
        """
        try:
            # Convert rating string to float
            rating = None
            if raw_data.rating:
                rating_match = re.search(r'(\d+\.?\d*)', raw_data.rating)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Convert view count string to int
            view_count = None
            if raw_data.view_count:
                # Parse "40.182" -> 40182
                view_str = raw_data.view_count.replace('.', '').replace(',', '')
                view_match = re.search(r'(\d+)', view_str)
                if view_match:
                    view_count = int(view_match.group(1))
            
            # Convert release year string to int
            release_year = None
            if raw_data.release_year and raw_data.release_year.isdigit():
                release_year = int(raw_data.release_year)
            
            # Convert duration to minutes
            duration = None
            if raw_data.duration:
                duration = self._parse_duration(raw_data.duration)
            
            return ProcessedMovieData(
                url=raw_data.url,
                title=raw_data.title or "Unknown",
                description=raw_data.description,
                rating=rating,
                view_count=view_count,
                release_year=release_year,
                duration=duration,
                genre=raw_data.genre or [],
                country=raw_data.country,
                thumbnail_url=raw_data.thumbnail_url,
                video_url=raw_data.video_url,
                video_quality=raw_data.video_quality,
                actors=raw_data.actors or [],
                director=raw_data.director,
                age_rating=raw_data.age_rating,
                access_type=raw_data.access_type

            )
        except Exception as e:
            logger.error(f"Failed to normalize data: {str(e)}", exc_info=True)
            raise
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """
        Parse duration string thành minutes
        Examples: "1g 23ph" -> 83
        """
        try:
            # Parse "1g 23ph" format
            vn_match = re.search(r'(\d+)g\s*(\d+)ph', duration_str)
            if vn_match:
                hours = int(vn_match.group(1))
                minutes = int(vn_match.group(2))
                return hours * 60 + minutes
            
            # Parse minutes only
            min_match = re.search(r'(\d+)\s*ph', duration_str)
            if min_match:
                return int(min_match.group(1))
            
            return None
        except Exception:
            return None
    
    async def convert_to_vod_create(self, processed_data: ProcessedMovieData) -> VodCreate:
        """
        Convert ProcessedMovieData thành VodCreate schema để save MongoDB
        """
        try:
            return VodCreate(
                url=processed_data.url,  
                title=processed_data.title,
                description=processed_data.description,
                rating=processed_data.rating,
                view_count=processed_data.view_count,
                release_year=processed_data.release_year,
                duration=processed_data.duration,
                genre=processed_data.genre,
                country=processed_data.country,
                thumbnail_url=processed_data.thumbnail_url,
                video_url=processed_data.video_url,
                video_quality=processed_data.video_quality,
                actors=processed_data.actors,
                director=processed_data.director,
                age_rating=processed_data.age_rating,
                access_type=processed_data.access_type
            )
        except Exception as e:
            logger.error(f"Failed to convert to VodCreate: {str(e)}", exc_info=True)
            raise
    
    async def crawl_all_movies(self):
        """
        Crawl tất cả movies trong MOVIE_URLS
        """
        try:
            self.status.update({
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "processed": 0,
                "failed": 0,
                "errors": []
            })
            
            logger.info(f"Starting to crawl {len(self.MOVIE_URLS)} movies")
            
            for i, url in enumerate(self.MOVIE_URLS):
                self.status["current_url"] = url
                
                try:
                    # Crawl raw data
                    raw_data = await self.crawl_single_movie(url)
                    if not raw_data:
                        self.status["failed"] += 1
                        self.status["errors"].append(f"Failed to crawl: {url}")
                        continue
                    
                    # Normalize data
                    processed_data = self.normalize_data(raw_data)
                    
                    # Convert to VodCreate
                    vod_create = await self.convert_to_vod_create(processed_data)
                    
                    # Save to MongoDB
                    await crud_vod.create_vod(vod_create)
                    
                    self.status["processed"] += 1
                    logger.info(f"Successfully saved movie: {processed_data.title}")
                    
                except Exception as e:
                    self.status["failed"] += 1
                    error_msg = f"Error processing {url}: {str(e)}"
                    self.status["errors"].append(error_msg)
                    logger.error(error_msg, exc_info=True)
                
                # Rate limiting - delay giữa requests
                if i < len(self.MOVIE_URLS) - 1:  # Không delay ở request cuối
                    await asyncio.sleep(1)
            
            self.status.update({
                "status": "completed",
                "end_time": datetime.now().isoformat(),
                "current_url": None
            })
            
            logger.info(f"Crawling completed. Processed: {self.status['processed']}, Failed: {self.status['failed']}")
            
        except Exception as e:
            self.status.update({
                "status": "failed",
                "end_time": datetime.now().isoformat(),
                "current_url": None
            })
            logger.error(f"Crawling failed: {str(e)}", exc_info=True)
    
    def get_status(self) -> dict:
        """
        Get current crawling status
        """
        return self.status.copy()
    
    async def test_single_url(self, url: str) -> dict:
        """
        Test crawl một URL để debug
        """
        try:
            logger.info(f"Testing crawl for: {url}")
            raw_data = await self.crawl_single_movie(url)
            
            if not raw_data:
                return {"success": False, "error": "Failed to extract data"}
            
            processed_data = self.normalize_data(raw_data)
            
            return {
                "success": True,
                "raw_data": raw_data.model_dump(),
                "processed_data": processed_data.model_dump()
            }
        except Exception as e:
            logger.error(f"Test failed: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
