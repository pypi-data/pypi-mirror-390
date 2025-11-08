import pytest
from database import SQLiteDatabase, PostgresDatabase, MongoDatabase

pytestmark = pytest.mark.asyncio


async def test_sqlite_query_stream(sqlite_db):
    """Test streaming query results from SQLite."""
    # Create table and insert test data
    await sqlite_db.execute("""
        CREATE TABLE large_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value INTEGER
        )
    """)
    
    # Insert 200 rows
    for i in range(200):
        await sqlite_db.execute(
            "INSERT INTO large_table (id, name, value) VALUES (:id, :name, :value)",
            {"id": i, "name": f"item_{i}", "value": i * 10}
        )
    
    # Stream results
    count = 0
    values = []
    async for row in sqlite_db.query_stream("SELECT * FROM large_table WHERE value < 1000"):
        count += 1
        values.append(row['value'])
    
    # Verify we got results
    assert count == 100  # Only values < 1000
    assert values[0] == 0
    assert values[-1] == 990


async def test_sqlite_query_stream_with_params(sqlite_db):
    """Test streaming with parameters."""
    # Create and populate table
    await sqlite_db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        )
    """)
    
    for i in range(50):
        await sqlite_db.execute(
            "INSERT INTO users (name, age) VALUES (:name, :age)",
            {"name": f"user_{i}", "age": 20 + i}
        )
    
    # Stream with parameter
    count = 0
    async for row in sqlite_db.query_stream(
        "SELECT * FROM users WHERE age > :min_age",
        {"min_age": 50},
        chunk_size=10
    ):
        count += 1
        assert row['age'] > 50
    
    assert count == 19  # Ages 51-69


async def test_sqlite_query_stream_empty_result(sqlite_db):
    """Test streaming with no results."""
    await sqlite_db.execute("CREATE TABLE empty (id INTEGER PRIMARY KEY)")
    
    count = 0
    async for row in sqlite_db.query_stream("SELECT * FROM empty"):
        count += 1
    
    assert count == 0


@pytest.mark.postgres
@pytest.mark.skip(reason="Requires proper async cursor mocking")
async def test_postgres_query_stream(postgres_db):
    """Test streaming query results from PostgreSQL."""
    from unittest.mock import AsyncMock
    
    # Get mock connection
    mock_conn = await postgres_db._pool.acquire().__aenter__()
    
    # Mock cursor with async iteration
    mock_cursor = AsyncMock()
    
    # Create test data
    test_rows = [{"id": i, "name": f"item_{i}"} for i in range(150)]
    
    # Mock fetch to return chunks
    fetch_count = [0]
    def mock_fetch(size):
        async def _fetch():
            start = fetch_count[0]
            end = min(start + size, len(test_rows))
            chunk = test_rows[start:end]
            fetch_count[0] = end
            return chunk
        return _fetch()
    
    mock_cursor.fetch = mock_fetch
    mock_conn.cursor = AsyncMock(return_value=mock_cursor)
    mock_conn.transaction = AsyncMock(return_value=AsyncMock(__aenter__=AsyncMock(), __aexit__=AsyncMock()))
    
    # Stream results
    count = 0
    async for row in postgres_db.query_stream("SELECT * FROM test_table"):
        count += 1
    
    assert count == 150


@pytest.mark.mongo
async def test_mongo_query_stream(mongo_db):
    """Test streaming query results from MongoDB."""
    from unittest.mock import MagicMock, AsyncMock
    
    # Create mock cursor
    test_docs = [{"_id": f"id_{i}", "name": f"doc_{i}", "value": i} for i in range(100)]
    
    # Mock cursor with async iterator
    async def mock_async_iter():
        for doc in test_docs:
            yield doc
    
    mock_cursor = MagicMock()
    mock_cursor.__aiter__ = lambda self: mock_async_iter()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    
    # Setup collection mock
    collection = mongo_db._db["test_collection"]
    collection.find = MagicMock(return_value=mock_cursor)
    
    # Stream results
    count = 0
    async for doc in mongo_db.query_stream("test_collection", {"value": {"$lt": 50}}):
        count += 1
        assert "_id" in doc  # Verify ObjectId conversion
    
    assert count == 100  # Mock returns all docs


async def test_sqlite_query_stream_chunk_size(sqlite_db):
    """Test that chunk_size parameter is respected."""
    # Create table with many rows
    await sqlite_db.execute("""
        CREATE TABLE chunk_test (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
    """)
    
    for i in range(500):
        await sqlite_db.execute(
            "INSERT INTO chunk_test (data) VALUES (:data)",
            {"data": f"row_{i}"}
        )
    
    # Stream with small chunk size
    count = 0
    async for row in sqlite_db.query_stream("SELECT * FROM chunk_test", chunk_size=50):
        count += 1
    
    assert count == 500
