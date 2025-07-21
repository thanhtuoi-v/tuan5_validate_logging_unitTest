from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.endpoints.vod import router as vod_router
from app.core.logging import setup_logging, get_logger
from app.db.mongodb import check_db_connection, close_db_connection
from app.db.redis_client import check_redis_connection, close_redis_connection

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("VOD Service API is starting up...")

     # Test database connection
    db_conn = await check_db_connection()
    redis_conn = await check_redis_connection()

    if not db_conn:
        logger.error(f"Failed to connect to database")
    if not redis_conn:
        logger.error("Failed to connect to Redis")
    yield
    # Shutdown
    logger.info("VOD Service API is shutting down...")
    await close_db_connection()
    await close_redis_connection()

app = FastAPI(title="VOD Service API", lifespan=lifespan)

app.include_router(vod_router, prefix="/api/v1", tags=["VOD"])