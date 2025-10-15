import redis.asyncio as redis
from app.config.settings import get_settings

settings = get_settings()

async def get_redis_client():
    """Get Redis client instance"""
    return redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        encoding="utf-8"
    )
