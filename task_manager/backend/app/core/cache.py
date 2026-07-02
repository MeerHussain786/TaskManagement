"""
Redis Cache and Rate Limiting Service.

Provides async access to Redis for caching, token blacklist checking,
and endpoint rate limiting.
"""

from collections.abc import AsyncGenerator

import redis.asyncio as redis

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level redis client singleton
_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """Get or create the Redis async client singleton."""
    global _redis_client  # noqa: PLW0603
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD or None,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Close Redis connection pool."""
    global _redis_client  # noqa: PLW0603
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("redis_connection_closed")


class CacheService:
    """Wrapper around Redis for caching operations."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = get_redis_client() if self.settings.CACHE_ENABLED else None

    async def get(self, key: str) -> str | None:
        """Fetch a value from the cache."""
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error("cache_get_error", key=key, error=str(e))
            return None

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Store a value in the cache with an optional TTL (Time To Live)."""
        if not self.client:
            return False
        try:
            expire_ttl = ttl or self.settings.CACHE_TTL_SECONDS
            await self.client.set(key, value, ex=expire_ttl)
            return True
        except Exception as e:
            logger.error("cache_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Invalidate a cached item."""
        if not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error("cache_delete_error", key=key, error=str(e))
            return False

    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if request limit has been exceeded in the given time window.

        Args:
            key: Rate limiting key identifier.
            limit: Allowed request count inside the window.
            window: Expiration window size in seconds.

        Returns:
            True if request is allowed, False if rate limit is exceeded.
        """
        if not self.client:
            return True  # If redis is down, fail open to avoid service disruption

        try:
            current = await self.client.get(key)
            if current is not None and int(current) >= limit:
                return False

            async with self.client.pipeline(transaction=True) as pipe:
                await pipe.incr(key)
                if current is None:
                    await pipe.expire(key, window)
                await pipe.execute()
            return True
        except Exception as e:
            logger.error("rate_limit_error", key=key, error=str(e))
            return True
