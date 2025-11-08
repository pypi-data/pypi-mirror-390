from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import timedelta

class Cache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The cached value or None if not found
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: The key to store the value under
            value: The value to cache
            ttl: Optional time-to-live for the cached value
            
        Returns:
            True if successfully stored, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Remove a value from the cache.
        
        Args:
            key: The key to remove
            
        Returns:
            True if successfully removed, False otherwise
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """
        Clear all values from the cache.
        
        Returns:
            True if successfully cleared, False otherwise
        """
        pass