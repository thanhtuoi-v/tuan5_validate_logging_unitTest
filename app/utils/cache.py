import json
from typing import Any, Callable
from app.db.redis_client import redis


async def get_or_set_cache(key: str, fetch_fn: Callable[[], Any], ttl: int):
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    data = await fetch_fn()
    await redis.set(key, json.dumps(data, default=str), ex=ttl)
    return data


async def invalidate_cache(*keys):
    if keys:
        await redis.delete(*keys)
        print(f"Invalidated cache keys: {keys}")
