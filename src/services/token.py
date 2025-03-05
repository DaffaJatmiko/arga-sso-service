from datetime import timedelta
from typing import Optional
import redis.asyncio as redis

from src.core.config import settings

class TokenBlacklistService:
    def __init__(self, redis: redis.Redis):
        self._redis = redis
        self._prefix = "blacklist:token:"

    async def add_to_blacklist(
        self,
        token: str,
        expires_in: Optional[int] = None
    ) -> None:
        """
        Add token to blacklist
        
        Args:
            token: The token to blacklist
            expires_in: Time in seconds until token expires. 
                       Defaults to ACCESS_TOKEN_EXPIRE_MINUTES
        """
        if expires_in is None:
            expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        await self._redis.setex(
            f"{self._prefix}{token}",
            expires_in,
            "1"
        )

    async def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return await self._redis.exists(f"{self._prefix}{token}") > 0

    async def clear_blacklist(self) -> None:
        """Clear all blacklisted tokens (useful for testing)"""
        async for key in self._redis.scan_iter(f"{self._prefix}*"):
            await self._redis.delete(key)