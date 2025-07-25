from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from typing import Dict, Any

from app.services.crawler import CrawlerService
from app.schemas.crawler import CrawlStatus
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Dependency Injection
def get_crawler_service() -> CrawlerService:
    """
    Dependency để inject CrawlerService
    """
    return CrawlerService()

@router.post("/crawl/start", status_code=status.HTTP_202_ACCEPTED)
async def start_crawling(
    background_tasks: BackgroundTasks,
    crawler: CrawlerService = Depends(get_crawler_service)
):
    """
    Bắt đầu crawl dữ liệu phim trong background
    """
    try:
        # Check nếu đang crawl
        current_status = crawler.get_status()
        if current_status["status"] == "running":
            raise HTTPException(
                status_code=400, 
                detail="Crawling is already running"
            )
        
        # Start crawling trong background
        background_tasks.add_task(crawler.crawl_all_movies)
        
        logger.info("Started crawling movies in background")
        
        return {
            "message": f"Started crawling {len(crawler.MOVIE_URLS)} movies",
            "total_urls": len(crawler.MOVIE_URLS),
            "status": "started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start crawling: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to start crawling process"
        )

@router.get("/crawl/status")
async def get_crawl_status(
    crawler: CrawlerService = Depends(get_crawler_service)
) -> Dict[str, Any]:
    """
    Lấy trạng thái hiện tại của crawling process
    """
    try:
        status = crawler.get_status()
        # Thêm progress percentage
        if status["total_urls"] > 0:
            progress = (status["processed"] + status["failed"]) / status["total_urls"] * 100
            status["progress_percent"] = round(progress, 2)
        else:
            status["progress_percent"] = 0
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get crawl status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to get crawl status"
        )

@router.get("/crawl/stats")
async def get_crawl_stats() -> Dict[str, Any]:
    """
    Lấy thống kê tổng quan về crawled data
    """
    try:
        # Import ở đây để tránh circular import
        import app.crud.vod as crud_vod
        
        total_movies = await crud_vod.count_vods()
        
        return {
            "total_movies_in_db": total_movies,
            "available_urls": len(CrawlerService.MOVIE_URLS),
            "last_updated": "Manual crawl"  # TODO: track last crawl time
        }
        
    except Exception as e:
        logger.error(f"Failed to get crawl stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to get crawl statistics"
        )

@router.post("/crawl/test")
async def test_crawl_url(
    url: str,
    crawler: CrawlerService = Depends(get_crawler_service)
) -> Dict[str, Any]:
    """
    Test crawl một URL cụ thể để debug
    """
    try:
        if not url.startswith("https://vieon.vn/"):
            raise HTTPException(
                status_code=400,
                detail="URL must be from vieon.vn domain"
            )
        
        result = await crawler.test_single_url(url)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Crawl test failed: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test crawl failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Test crawl failed"
        )

@router.post("/crawl/reset")
async def reset_crawl_status(
    crawler: CrawlerService = Depends(get_crawler_service)
):
    """
    Reset crawl status về idle (để test lại)
    """
    try:
        crawler.status = {
            "total_urls": len(crawler.MOVIE_URLS),
            "processed": 0,
            "failed": 0,
            "status": "idle",
            "current_url": None,
            "start_time": None,
            "end_time": None,
            "errors": []
        }
        
        logger.info("Crawl status reset to idle")
        
        return {"message": "Crawl status reset successfully"}
        
    except Exception as e:
        logger.error(f"Failed to reset crawl status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to reset crawl status"
        )
