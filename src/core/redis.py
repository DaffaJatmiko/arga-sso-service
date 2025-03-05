from typing import AsyncGenerator, Optional
import redis.asyncio as redis
import asyncio
from src.core.config import settings

redis_client: Optional[redis.Redis] = None
lock = asyncio.Lock()

async def init_redis_pool() -> None:
    """Initialize Redis connection pool"""
    global redis_client
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )

async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        async with lock:  # Mencegah race condition saat inisialisasi
            if redis_client is None:  # Double-check setelah lock
                await init_redis_pool()
    return redis_client

async def close_redis_connection() -> None:
    """Close Redis connection"""
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()  # Gunakan aclose() untuk async
        redis_client = None  # Reset redis_client setelah ditutup
