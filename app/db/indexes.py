from app.db.mongodb import vod_collection
from app.core.logging import get_logger

logger = get_logger(__name__)

async def create_indexes():
    """
    Tạo indexes cho MongoDB để tối ưu truy vấn
    """
    try:
        # Index cho search theo title với default language
        await vod_collection.create_index(
            [("title", "text")], 
            default_language='english',
            language_override='none'  # Không dùng field language trong document
        )
        logger.info("Created text index for title field")
        
        # Index cho sort theo release_year
        await vod_collection.create_index([("release_year", -1)])
        logger.info("Created index for release_year field")
        
        # Index cho genre
        await vod_collection.create_index([("genres", 1)])
        logger.info("Created index for genres field")
        
        logger.info("All indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}", exc_info=True)
        raise

async def get_indexes():
    """
    Lấy danh sách indexes hiện tại
    """
    try:
        indexes = await vod_collection.list_indexes().to_list(length=None)
        logger.info(f"Current indexes: {[idx['name'] for idx in indexes]}")
        return indexes
    except Exception as e:
        logger.error(f"Failed to get indexes: {str(e)}", exc_info=True)
        raise
