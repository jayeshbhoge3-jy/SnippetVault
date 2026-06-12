import redis.asyncio as redis
from app.config import settings
from typing import Optional

redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None

class CacheService:
    @staticmethod
    async def set(key: str, value: str, ttl: int = None):
        client = await get_redis()
        if ttl:
            await client.setex(key, ttl, value)
        else:
            await client.set(key, value)

    @staticmethod
    async def get(key: str) -> Optional[str]:
        client = await get_redis()
        return await client.get(key)

    @staticmethod
    async def delete(key: str):
        client = await get_redis()
        await client.delete(key)

    @staticmethod
    async def delete_pattern(pattern: str):
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
