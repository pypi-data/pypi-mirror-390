import pytest
from datetime import datetime

pytestmark = pytest.mark.asyncio

@pytest.mark.mongo
async def test_mongo_connect_disconnect(mongo_db):
    """Test MongoDB connection and disconnection."""
    # Fixture sets connected = True
    assert mongo_db.is_connected
    
    # Mock disconnect
    mongo_db._connected = False
    assert not mongo_db.is_connected
    
    # Mock reconnect
    mongo_db._connected = True
    assert mongo_db.is_connected

@pytest.mark.mongo
async def test_mongo_basic_operations(mongo_db, sample_data):
    """Test basic CRUD operations with MongoDB."""
    from unittest.mock import AsyncMock, MagicMock
    
    # Mock cursor for query operations
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    
    # Create async iterator for cursor
    async def mock_async_iter():
        yield {"id": 1, "name": "John Doe", "email": "john@example.com", "_id": "123"}
    mock_cursor.__aiter__ = lambda self: mock_async_iter()
    
    # Get the mock collection
    collection = mongo_db._db["users"]
    collection.find.return_value = mock_cursor
    collection.insert_many.return_value = MagicMock(inserted_ids=["id1", "id2"])
    collection.update_many.return_value = MagicMock(modified_count=1)
    collection.delete_many.return_value = MagicMock(deleted_count=1)
    
    # Insert data
    users = sample_data["users"]
    result = await mongo_db.execute("users", "insert", users)
    assert result == 2
    
    # Query data
    results = await mongo_db.query("users", {"id": 1}, {"sort": [("name", 1)]})
    assert len(results) == 1
    assert results[0]["name"] == "John Doe"
    
    # Update data
    result = await mongo_db.execute(
        "users",
        "update",
        [{"$set": {"name": "John Smith"}}],
        {"id": 1}
    )
    assert result == 1
    
    # Delete data
    result = await mongo_db.execute("users", "delete", [], {"id": 1})
    assert result == 1

@pytest.mark.mongo
async def test_mongo_query_options(mongo_db, sample_data):
    """Test MongoDB query options like sort, limit, skip."""
    from unittest.mock import MagicMock
    
    # Mock cursor for different query scenarios
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    
    collection = mongo_db._db["users"]
    collection.find.return_value = mock_cursor
    
    # Test sorting
    async def sorted_iter():
        yield {"id": 2, "name": "Jane Doe", "_id": "1"}
        yield {"id": 1, "name": "John Doe", "_id": "2"}
    mock_cursor.__aiter__ = lambda self: sorted_iter()
    
    results = await mongo_db.query("users", {}, {"sort": [("name", 1)]})
    assert len(results) == 2
    mock_cursor.sort.assert_called_once()
    
    # Test limit
    async def limited_iter():
        yield {"id": 1, "name": "John Doe", "_id": "1"}
    mock_cursor.__aiter__ = lambda self: limited_iter()
    
    results = await mongo_db.query("users", {}, {"limit": 1})
    assert len(results) == 1

@pytest.mark.mongo
async def test_mongo_with_cache(mongo_db, memory_cache, sample_data):
    """Test MongoDB with caching."""
    from unittest.mock import MagicMock
    
    mongo_db._cache = memory_cache
    
    # Setup mock cursor
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    
    async def mock_iter():
        yield {"id": 1, "name": "John Doe", "_id": "123"}
    mock_cursor.__aiter__ = lambda self: mock_iter()
    
    collection = mongo_db._db["users"]
    collection.find.return_value = mock_cursor
    
    # First query - should hit database and cache result
    query = {"id": 1}
    params = {"sort": [("name", 1)]}
    
    results1 = await mongo_db.query("users", query, params)
    assert results1[0]["name"] == "John Doe"
    
    # Second query - should hit cache (mock won't be called again)
    results2 = await mongo_db.query("users", query, params)
    assert results2[0]["name"] == "John Doe"
    
    # Verify results are identical
    assert results1 == results2

@pytest.mark.mongo
async def test_mongo_error_handling(mongo_db):
    """Test error handling in MongoDB operations."""
    # Test disconnected database operations
    mongo_db._connected = False
    mongo_db._db = None
    
    with pytest.raises(RuntimeError, match="Database not connected"):
        await mongo_db.query("users", {})
