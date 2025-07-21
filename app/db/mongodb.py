from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client.vod_db
vod_collection = db.get_collection("vods")

async def check_db_connection():
    try:
        await client.admin.command('ping')
        logger.info("MongoDB connected")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}", exc_info=True)
        return False
    
async def close_db_connection():
    try:
        client.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}", exc_info=True)
