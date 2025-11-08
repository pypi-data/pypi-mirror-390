import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from ..core.cache import Cache

class InMemoryCache(Cache):
    """In-memory cache implementation with automatic expiration and size limits."""
    
    def __init__(self, cleanup_interval: int = 60, max_size: Optional[int] = None):
        """Initialize an empty cache.
        
        Args:
            cleanup_interval: Interval in seconds between expiration cleanup runs (default: 60)
            max_size: Maximum number of keys allowed in cache (default: None for unlimited)
        """
        self._cache: Dict[str, Tuple[Any, Optional[datetime]]] = {}
        self._cleanup_interval = cleanup_interval
        self._max_size = max_size
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        if key not in self._cache:
            return None
            
        value, expiry = self._cache[key]
        if expiry and datetime.now() > expiry:
            del self._cache[key]
            return None
            
        return value

    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """Store a value in the cache.
        
        If max_size is set and cache is full, the oldest key will be evicted.
        """
        # Check if we need to evict a key
        if self._max_size is not None and key not in self._cache:
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
        
        expiry = datetime.now() + ttl if ttl else None
        self._cache[key] = (value, expiry)
        return True

    async def delete(self, key: str) -> bool:
        """Remove a value from the cache."""
        try:
            del self._cache[key]
            return True
        except KeyError:
            return False

    async def clear(self) -> bool:
        """Clear all values from the cache."""
        self._cache.clear()
        return True
    
    def _evict_oldest(self):
        """Evict the oldest key from cache.
        
        Priority order:
        1. Keys with expired TTL (remove the most expired)
        2. Keys with soonest expiration
        3. First key in dict (FIFO behavior)
        """
        if not self._cache:
            return
        
        now = datetime.now()
        
        # First, try to remove expired keys
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if expiry and now > expiry
        ]
        if expired_keys:
            del self._cache[expired_keys[0]]
            return
        
        # Next, evict the key with the soonest expiration
        keys_with_expiry = [
            (key, expiry) for key, (_, expiry) in self._cache.items()
            if expiry
        ]
        if keys_with_expiry:
            # Sort by expiry time and remove the soonest to expire
            oldest_key = min(keys_with_expiry, key=lambda x: x[1])[0]
            del self._cache[oldest_key]
            return
        
        # Finally, remove the first key (FIFO)
        first_key = next(iter(self._cache))
        del self._cache[first_key]
    
    def _expire_keys(self) -> int:
        """Remove all expired keys from cache.
        
        Returns:
            Number of keys expired
        """
        now = datetime.now()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if expiry and now > expiry
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    async def _cleanup_loop(self):
        """Background task that periodically removes expired keys."""
        while self._running:
            try:
                await asyncio.sleep(self._cleanup_interval)
                if self._running:  # Check again after sleep
                    expired = self._expire_keys()
                    if expired > 0:
                        # Optional: log cleanup activity
                        pass
            except asyncio.CancelledError:
                break
            except Exception:
                # Silently continue on any error to keep cleanup running
                continue
    
    def start_cleanup(self):
        """Start the background cleanup task."""
        if not self._running:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup(self):
        """Stop the background cleanup task."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    def __del__(self):
        """Cleanup when cache is destroyed."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
