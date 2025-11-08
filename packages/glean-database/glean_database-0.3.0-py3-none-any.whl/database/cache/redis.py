import json
from typing import Any, Optional
from datetime import timedelta

try:
    from redis.asyncio import Redis
    from redis.exceptions import RedisError
except ImportError:
    Redis = None  # type: ignore
    RedisError = Exception  # type: ignore

from ..core.cache import Cache

class RedisCache(Cache):
    """Redis-based cache implementation."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """Initialize Redis connection."""
        if Redis is None:
            raise ImportError(
                "redis is required for Redis cache support. "
                "Install it with: pip install glean-database[redis]"
            )
        self._redis = Redis(host=host, port=port, db=db)

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        value = await self._redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """Store a value in the cache."""
        try:
            serialized = json.dumps(value)
            if ttl:
                return bool(await self._redis.setex(key, int(ttl.total_seconds()), serialized))
            return bool(await self._redis.set(key, serialized))
        except (TypeError, json.JSONDecodeError):
            return False

    async def delete(self, key: str) -> bool:
        """Remove a value from the cache."""
        return bool(await self._redis.delete(key))

    async def clear(self) -> bool:
        """Clear all values from the cache."""
        try:
            await self._redis.flushdb()
            return True
        except RedisError:
            return False