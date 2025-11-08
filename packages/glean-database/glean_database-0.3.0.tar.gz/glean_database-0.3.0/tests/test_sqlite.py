import pytest
from database import SQLiteDatabase, InMemoryCache

pytestmark = pytest.mark.asyncio

async def test_sqlite_connect_disconnect(sqlite_db):
    """Test database connection and disconnection."""
    assert sqlite_db.is_connected
    await sqlite_db.disconnect()
    assert not sqlite_db.is_connected
    assert await sqlite_db.connect()
    assert sqlite_db.is_connected

async def test_sqlite_basic_operations(sqlite_db):
    """Test basic CRUD operations."""
    # Create table
    await sqlite_db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    
    # Insert data
    await sqlite_db.execute(
        "INSERT INTO users (id, name, email) VALUES (:id, :name, :email)",
        {"id": 1, "name": "John Doe", "email": "john@example.com"}
    )
    
    # Query data
    results = await sqlite_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    assert len(results) == 1
    assert results[0]["name"] == "John Doe"
    
    # Update data
    await sqlite_db.execute(
        "UPDATE users SET name = :name WHERE id = :id",
        {"id": 1, "name": "John Smith"}
    )
    
    # Verify update
    results = await sqlite_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    assert results[0]["name"] == "John Smith"
    
    # Delete data
    await sqlite_db.execute("DELETE FROM users WHERE id = :id", {"id": 1})
    
    # Verify deletion
    results = await sqlite_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    assert len(results) == 0

async def test_sqlite_with_cache(sqlite_db, memory_cache):
    """Test SQLite database with caching."""
    # Set up database with cache
    sqlite_db._cache = memory_cache
    
    # Create table and insert data
    await sqlite_db.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    
    await sqlite_db.execute(
        "INSERT INTO products (id, name, price) VALUES (:id, :name, :price)",
        {"id": 1, "name": "Test Product", "price": 9.99}
    )
    
    # First query - should hit database
    query = "SELECT * FROM products WHERE id = :id"
    params = {"id": 1}
    
    results1 = await sqlite_db.query(query, params)
    assert results1[0]["name"] == "Test Product"
    
    # Second query - should hit cache
    results2 = await sqlite_db.query(query, params)
    assert results2[0]["name"] == "Test Product"
    
    # Verify results are identical
    assert results1 == results2

async def test_sqlite_error_handling(sqlite_db):
    """Test error handling in SQLite operations."""
    # Test invalid SQL
    with pytest.raises(Exception):
        await sqlite_db.execute("INVALID SQL")
    
    # Test querying non-existent table
    with pytest.raises(Exception):
        await sqlite_db.query("SELECT * FROM nonexistent_table")
    
    # Test disconnected database operations
    await sqlite_db.disconnect()
    with pytest.raises(RuntimeError, match="Database not connected"):
        await sqlite_db.query("SELECT 1")
    with pytest.raises(RuntimeError, match="Database not connected"):
        await sqlite_db.execute("SELECT 1")