import pytest
import asyncio
from datetime import timedelta

pytestmark = pytest.mark.asyncio

async def test_memory_cache_set_get(memory_cache):
    """Test basic set/get operations for in-memory cache."""
    # Test simple value
    assert await memory_cache.set("test_key", "test_value")
    assert await memory_cache.get("test_key") == "test_value"
    
    # Test with TTL
    assert await memory_cache.set("ttl_key", "ttl_value", ttl=timedelta(seconds=1))
    assert await memory_cache.get("ttl_key") == "ttl_value"
    
    # Test missing key
    assert await memory_cache.get("nonexistent") is None

async def test_memory_cache_delete(memory_cache):
    """Test delete operation for in-memory cache."""
    # Set and delete
    await memory_cache.set("del_key", "del_value")
    assert await memory_cache.delete("del_key")
    assert await memory_cache.get("del_key") is None
    
    # Delete nonexistent key
    assert not await memory_cache.delete("nonexistent")

async def test_memory_cache_clear(memory_cache):
    """Test clear operation for in-memory cache."""
    # Set multiple values
    await memory_cache.set("key1", "value1")
    await memory_cache.set("key2", "value2")
    
    # Clear cache
    assert await memory_cache.clear()
    
    # Verify all values are gone
    assert await memory_cache.get("key1") is None
    assert await memory_cache.get("key2") is None

async def test_memory_cache_expiration():
    """Test that expired keys are removed on access."""
    from database import InMemoryCache
    
    cache = InMemoryCache()
    
    # Set key with very short TTL
    await cache.set("expire_key", "expire_value", ttl=timedelta(milliseconds=100))
    assert await cache.get("expire_key") == "expire_value"
    
    # Wait for expiration
    await asyncio.sleep(0.2)
    
    # Key should be expired now
    assert await cache.get("expire_key") is None
    
    # Verify key was removed from internal cache
    assert "expire_key" not in cache._cache

async def test_memory_cache_background_cleanup():
    """Test background cleanup task removes expired keys."""
    from database import InMemoryCache
    
    # Create cache with 0.2 second cleanup interval
    cache = InMemoryCache(cleanup_interval=0.2)
    cache.start_cleanup()
    
    try:
        # Add some keys with short TTL
        await cache.set("temp1", "value1", ttl=timedelta(milliseconds=100))
        await cache.set("temp2", "value2", ttl=timedelta(milliseconds=100))
        await cache.set("permanent", "value3")  # No TTL
        
        # Keys should exist initially
        assert len(cache._cache) == 3
        
        # Wait for keys to expire and cleanup to run
        await asyncio.sleep(0.4)
        
        # Expired keys should be removed by background task
        assert "temp1" not in cache._cache
        assert "temp2" not in cache._cache
        assert "permanent" in cache._cache
        assert len(cache._cache) == 1
    finally:
        await cache.stop_cleanup()

async def test_memory_cache_cleanup_start_stop():
    """Test starting and stopping cleanup task."""
    from database import InMemoryCache
    
    cache = InMemoryCache(cleanup_interval=1)
    
    # Initially not running
    assert not cache._running
    assert cache._cleanup_task is None
    
    # Start cleanup
    cache.start_cleanup()
    assert cache._running
    assert cache._cleanup_task is not None
    
    # Stop cleanup
    await cache.stop_cleanup()
    assert not cache._running
    assert cache._cleanup_task is None

async def test_memory_cache_max_size():
    """Test cache with maximum size limit."""
    from database import InMemoryCache
    
    # Create cache with max size of 3
    cache = InMemoryCache(max_size=3)
    
    # Add 3 keys (at capacity)
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")
    
    assert len(cache._cache) == 3
    assert await cache.get("key1") == "value1"
    assert await cache.get("key2") == "value2"
    assert await cache.get("key3") == "value3"
    
    # Add 4th key - should evict oldest (key1)
    await cache.set("key4", "value4")
    
    assert len(cache._cache) == 3
    assert await cache.get("key1") is None  # Evicted
    assert await cache.get("key2") == "value2"
    assert await cache.get("key3") == "value3"
    assert await cache.get("key4") == "value4"

async def test_memory_cache_max_size_with_ttl():
    """Test that expired keys are evicted first when cache is full."""
    from database import InMemoryCache
    
    cache = InMemoryCache(max_size=3)
    
    # Add keys with different TTLs
    await cache.set("temp", "value1", ttl=timedelta(milliseconds=50))
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")
    
    # Wait for temp to expire
    await asyncio.sleep(0.1)
    
    # Add new key - should evict expired "temp" instead of key2
    await cache.set("key4", "value4")
    
    assert len(cache._cache) == 3
    assert await cache.get("temp") is None  # Expired and evicted
    assert await cache.get("key2") == "value2"
    assert await cache.get("key3") == "value3"
    assert await cache.get("key4") == "value4"

async def test_memory_cache_max_size_update_existing():
    """Test that updating existing keys doesn't trigger eviction."""
    from database import InMemoryCache
    
    cache = InMemoryCache(max_size=2)
    
    # Fill cache
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    assert len(cache._cache) == 2
    
    # Update existing key - should not evict
    await cache.set("key1", "updated_value1")
    assert len(cache._cache) == 2
    assert await cache.get("key1") == "updated_value1"
    assert await cache.get("key2") == "value2"

@pytest.mark.redis
async def test_redis_cache_set_get(redis_cache):
    """Test basic set/get operations for Redis cache."""
    import json
    
    # Configure mocks for set operation
    redis_cache._redis.set.return_value = True
    redis_cache._redis.setex.return_value = True
    
    # Test simple value
    assert await redis_cache.set("test_key", "test_value")
    redis_cache._redis.set.assert_called_once_with("test_key", json.dumps("test_value"))
    
    # Configure mock for get operation
    redis_cache._redis.get.return_value = json.dumps("test_value")
    assert await redis_cache.get("test_key") == "test_value"
    
    # Test with TTL
    assert await redis_cache.set("ttl_key", "ttl_value", ttl=timedelta(seconds=1))
    redis_cache._redis.setex.assert_called_once()
    
    # Test missing key
    redis_cache._redis.get.return_value = None
    assert await redis_cache.get("nonexistent") is None

@pytest.mark.redis
async def test_redis_cache_delete(redis_cache):
    """Test delete operation for Redis cache."""
    # Configure mocks
    redis_cache._redis.delete.return_value = 1
    
    # Delete existing key
    assert await redis_cache.delete("del_key")
    redis_cache._redis.delete.assert_called_with("del_key")
    
    # Delete nonexistent key
    redis_cache._redis.delete.return_value = 0
    assert not await redis_cache.delete("nonexistent")

@pytest.mark.redis
async def test_redis_cache_clear(redis_cache):
    """Test clear operation for Redis cache."""
    # Configure mock
    redis_cache._redis.flushdb.return_value = True
    
    # Clear cache
    assert await redis_cache.clear()
    redis_cache._redis.flushdb.assert_called_once()

@pytest.mark.redis
async def test_redis_cache_complex_types(redis_cache):
    """Test Redis cache with complex data types."""
    import json
    
    test_data = {
        "string": "value",
        "number": 42,
        "list": [1, 2, 3],
        "dict": {"key": "value"},
        "bool": True,
        "none": None
    }
    
    # Configure mocks
    redis_cache._redis.set.return_value = True
    redis_cache._redis.get.return_value = json.dumps(test_data)
    
    # Test setting complex type
    assert await redis_cache.set("complex", test_data)
    
    # Test retrieving complex type
    result = await redis_cache.get("complex")
    assert result == test_data
