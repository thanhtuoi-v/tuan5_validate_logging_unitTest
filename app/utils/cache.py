import json
from typing import Any, Callable
from app.db.redis_client import redis_client
from app.core.logging import get_logger
from app.schemas.vod import VodResponse

logger = get_logger(__name__)

async def get_or_set_cache(key: str, fetch_fn: Callable[[], Any], ttl: int):
    try:
        cached = await redis_client.get(key)
        if cached:
            logger.debug(f"Cache hit for key: {key}")
            cached_data = json.loads(cached)
        # Convert dict back to VodResponse objects
            if isinstance(cached_data, list):
                return [VodResponse(**item) for item in cached_data]
            else:
                return VodResponse(**cached_data)
        data = await fetch_fn()
        await redis_client.set(key, json.dumps(data, default=str), ex=ttl)
        logger.debug(f"Cached data for key: {key} with TTL: {ttl}s")
        return data
    except Exception as e:
        logger.error(f"Cache error for key {key}: {str(e)}", exc_info=True)
        logger.warning(f"Falling back to direct fetch for key: {key}")
        return await fetch_fn()



async def invalidate_cache(*keys):
    if keys:
        await redis_client.delete(*keys)
        print(f"Invalidated cache keys: {keys}")
