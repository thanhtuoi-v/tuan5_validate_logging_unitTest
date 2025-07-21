import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

async def check_redis_connection():
    try:
        await redis_client.ping()
        logger.info("Redis connected")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}", exc_info=True)
        return False

async def close_redis_connection():
    try:
        await redis_client.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {str(e)}", exc_info=True)
   
