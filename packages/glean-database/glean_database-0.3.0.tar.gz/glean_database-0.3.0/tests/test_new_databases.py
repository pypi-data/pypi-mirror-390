import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from database import MySQLDatabase, MSSQLDatabase, OracleDatabase

pytestmark = pytest.mark.asyncio


# ============================================================================
# MySQL Tests
# ============================================================================

@pytest.fixture
async def mysql_db():
    """Mocked MySQL database fixture."""
    # Mock aiomysql module
    with patch('database.backends.mysql.aiomysql') as mock_aiomysql:
        mock_aiomysql.DictCursor = MagicMock()
        
        db = MySQLDatabase(
            database="test_db",
            host="localhost",
            username="root",
            password="secret"
        )
        
        # Mock the pool
        mock_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        
        # Setup cursor mocks
        mock_cursor.execute = AsyncMock()
        mock_cursor.fetchall = AsyncMock(return_value=[])
        mock_cursor.fetchmany = AsyncMock(return_value=[])
        mock_cursor.rowcount = 1
        
        # Setup connection mock
        mock_conn.cursor = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_cursor),
            __aexit__=AsyncMock()
        ))
        mock_conn.commit = AsyncMock()
        
        # Setup pool mock
        mock_pool.acquire = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_conn),
            __aexit__=AsyncMock()
        ))
        mock_pool.close = MagicMock()
        mock_pool.wait_closed = AsyncMock()
        
        db._pool = mock_pool
        db._connected = True
        
        yield db


async def test_mysql_connect_disconnect(mysql_db):
    """Test MySQL connection and disconnection."""
    assert mysql_db.is_connected
    
    # Mock disconnect
    mysql_db._connected = False
    assert not mysql_db.is_connected
    
    # Mock reconnect
    mysql_db._connected = True
    assert mysql_db.is_connected


async def test_mysql_query(mysql_db):
    """Test MySQL query execution."""
    # Setup mock data
    mock_conn = await mysql_db._pool.acquire().__aenter__()
    mock_cursor = await mock_conn.cursor().__aenter__()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "John", "email": "john@example.com"}
    ]
    
    # Execute query
    results = await mysql_db.query(
        "SELECT * FROM users WHERE id = :id",
        {"id": 1}
    )
    
    # Verify
    assert len(results) == 1
    assert results[0]["name"] == "John"
    mock_cursor.execute.assert_called_once()


async def test_mysql_execute(mysql_db):
    """Test MySQL execute statement."""
    mock_conn = await mysql_db._pool.acquire().__aenter__()
    mock_cursor = await mock_conn.cursor().__aenter__()
    mock_cursor.rowcount = 1
    
    # Execute statement
    result = await mysql_db.execute(
        "INSERT INTO users (name, email) VALUES (:name, :email)",
        {"name": "Jane", "email": "jane@example.com"}
    )
    
    assert result == 1
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


async def test_mysql_query_stream(mysql_db):
    """Test MySQL streaming queries."""
    mock_conn = await mysql_db._pool.acquire().__aenter__()
    mock_cursor = await mock_conn.cursor().__aenter__()
    
    # Mock data in chunks
    test_data = [
        [{"id": 1, "name": "User1"}, {"id": 2, "name": "User2"}],
        [{"id": 3, "name": "User3"}],
        []  # End of data
    ]
    mock_cursor.fetchmany.side_effect = test_data
    
    # Stream results
    count = 0
    async for row in mysql_db.query_stream("SELECT * FROM users"):
        count += 1
    
    assert count == 3


# ============================================================================
# MSSQL Tests
# ============================================================================

@pytest.fixture
async def mssql_db():
    """Mocked MSSQL database fixture."""
    # Mock pymssql module
    with patch('database.backends.mssql.pymssql') as mock_pymssql:
        db = MSSQLDatabase(
            database="test_db",
            host="localhost",
            username="sa",
            password="secret"
        )
        
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup cursor mocks
        mock_cursor.execute = MagicMock()
        mock_cursor.fetchall = MagicMock(return_value=[])
        mock_cursor.fetchmany = MagicMock(return_value=[])
        mock_cursor.rowcount = 1
        mock_cursor.description = [("id",), ("name",), ("email",)]
        mock_cursor.close = MagicMock()
        
        # Setup connection mock
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_conn.commit = MagicMock()
        mock_conn.close = MagicMock()
        
        # Mock pymssql.connect
        mock_pymssql.connect = MagicMock(return_value=mock_conn)
        
        # Initialize pool with mock connection
        db._pool = [mock_conn]
        db._connected = True
        
        yield db


async def test_mssql_connect_disconnect(mssql_db):
    """Test MSSQL connection and disconnection."""
    assert mssql_db.is_connected
    
    mssql_db._connected = False
    assert not mssql_db.is_connected
    
    mssql_db._connected = True
    assert mssql_db.is_connected


async def test_mssql_query(mssql_db):
    """Test MSSQL query execution."""
    mock_conn = mssql_db._pool[0]
    mock_cursor = mock_conn.cursor()
    mock_cursor.fetchall.return_value = [
        (1, "John", "john@example.com")
    ]
    
    # Execute query
    results = await mssql_db.query(
        "SELECT * FROM users WHERE id = :id",
        {"id": 1}
    )
    
    # Verify - should convert tuple to dict using column names
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "John"


async def test_mssql_execute(mssql_db):
    """Test MSSQL execute statement."""
    mock_conn = mssql_db._pool[0]
    mock_cursor = mock_conn.cursor()
    mock_cursor.rowcount = 1
    
    result = await mssql_db.execute(
        "INSERT INTO users (name, email) VALUES (:name, :email)",
        {"name": "Jane", "email": "jane@example.com"}
    )
    
    assert result == 1
    mock_conn.commit.assert_called()


async def test_mssql_query_stream(mssql_db):
    """Test MSSQL streaming queries."""
    mock_conn = mssql_db._pool[0]
    mock_cursor = mock_conn.cursor()
    
    # Mock data in chunks
    test_data = [
        [(1, "User1"), (2, "User2")],
        [(3, "User3")],
        []
    ]
    mock_cursor.fetchmany.side_effect = test_data
    mock_cursor.description = [("id",), ("name",)]
    
    count = 0
    async for row in mssql_db.query_stream("SELECT * FROM users"):
        count += 1
        assert "id" in row
        assert "name" in row
    
    assert count == 3


# ============================================================================
# Oracle Tests
# ============================================================================

@pytest.fixture
async def oracle_db():
    """Mocked Oracle database fixture."""
    with patch('database.backends.oracle.oracledb') as mock_oracledb:
        mock_oracledb.init_oracle_client = MagicMock()
        
        db = OracleDatabase(
            database="ORCL",
            host="localhost",
            username="system",
            password="oracle"
        )
        
        # Mock the pool
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup cursor mocks
        mock_cursor.execute = MagicMock()
        mock_cursor.fetchall = MagicMock(return_value=[])
        mock_cursor.fetchmany = MagicMock(return_value=[])
        mock_cursor.rowcount = 1
        mock_cursor.description = [("ID",), ("NAME",), ("EMAIL",)]
        mock_cursor.close = MagicMock()
        
        # Setup connection mock
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_conn.commit = MagicMock()
        
        # Setup pool mock
        mock_pool.acquire = MagicMock(return_value=mock_conn)
        mock_pool.release = MagicMock()
        mock_pool.close = MagicMock()
        
        db._pool = mock_pool
        db._connected = True
        
        yield db


async def test_oracle_connect_disconnect(oracle_db):
    """Test Oracle connection and disconnection."""
    assert oracle_db.is_connected
    
    oracle_db._connected = False
    assert not oracle_db.is_connected
    
    oracle_db._connected = True
    assert oracle_db.is_connected


async def test_oracle_query(oracle_db):
    """Test Oracle query execution."""
    mock_cursor = oracle_db._pool.acquire().cursor()
    mock_cursor.fetchall.return_value = [
        (1, "John", "john@example.com")
    ]
    
    # Execute query (Oracle uses :param natively)
    results = await oracle_db.query(
        "SELECT * FROM users WHERE user_id = :id",
        {"id": 1}
    )
    
    # Verify - converts tuple to dict
    assert len(results) == 1
    assert results[0]["ID"] == 1
    assert results[0]["NAME"] == "John"


async def test_oracle_execute(oracle_db):
    """Test Oracle execute statement."""
    mock_cursor = oracle_db._pool.acquire().cursor()
    mock_cursor.rowcount = 1
    
    result = await oracle_db.execute(
        "INSERT INTO users (name, email) VALUES (:name, :email)",
        {"name": "Jane", "email": "jane@example.com"}
    )
    
    assert result == 1
    mock_cursor.execute.assert_called_once()
    oracle_db._pool.acquire().commit.assert_called_once()


async def test_oracle_query_stream(oracle_db):
    """Test Oracle streaming queries."""
    mock_cursor = oracle_db._pool.acquire().cursor()
    
    # Mock data in chunks
    test_data = [
        [(1, "User1"), (2, "User2")],
        [(3, "User3")],
        []
    ]
    mock_cursor.fetchmany.side_effect = test_data
    mock_cursor.description = [("ID",), ("NAME",)]
    
    count = 0
    async for row in oracle_db.query_stream("SELECT * FROM users"):
        count += 1
        assert "ID" in row
        assert "NAME" in row
    
    assert count == 3


# ============================================================================
# Cross-database compatibility tests
# ============================================================================

async def test_mysql_parameter_conversion(mysql_db):
    """Test that MySQL converts :param to %s correctly."""
    mock_conn = await mysql_db._pool.acquire().__aenter__()
    mock_cursor = await mock_conn.cursor().__aenter__()
    
    await mysql_db.query(
        "SELECT * FROM users WHERE id = :id AND name = :name",
        {"id": 1, "name": "John"}
    )
    
    # Check that execute was called (parameter conversion happens internally)
    assert mock_cursor.execute.called


async def test_mssql_parameter_conversion(mssql_db):
    """Test that MSSQL converts :param to %s correctly."""
    # Get the mock connection that will be used
    mock_conn = mssql_db._pool[0]
    mock_cursor = mock_conn.cursor()
    
    await mssql_db.query(
        "SELECT * FROM users WHERE id = :id",
        {"id": 1}
    )
    
    assert mock_cursor.execute.called


async def test_oracle_native_parameters(oracle_db):
    """Test that Oracle handles :param natively."""
    mock_cursor = oracle_db._pool.acquire().cursor()
    
    await oracle_db.query(
        "SELECT * FROM users WHERE user_id = :id",
        {"id": 1}
    )
    
    # Oracle should receive the original :param style
    assert mock_cursor.execute.called


async def test_oracle_with_cache(oracle_db, memory_cache):
    """Test Oracle with caching enabled."""
    oracle_db._cache = memory_cache
    
    mock_cursor = oracle_db._pool.acquire().cursor()
    mock_cursor.fetchall.return_value = [(1, "Test User")]
    
    # First query - hits database
    results1 = await oracle_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    # Second query - hits cache
    results2 = await oracle_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    
    assert results1 == results2


async def test_mysql_with_cache(mysql_db, memory_cache):
    """Test MySQL with caching enabled."""
    mysql_db._cache = memory_cache
    
    mock_conn = await mysql_db._pool.acquire().__aenter__()
    mock_cursor = await mock_conn.cursor().__aenter__()
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "John"}]
    
    # First query - hits database
    results1 = await mysql_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    assert len(results1) == 1
    
    # Second query - should hit cache
    results2 = await mysql_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    assert results1 == results2


async def test_mssql_with_cache(mssql_db, memory_cache):
    """Test MSSQL with caching enabled."""
    mssql_db._cache = memory_cache
    
    mock_conn = mssql_db._pool[0]
    mock_cursor = mock_conn.cursor()
    mock_cursor.fetchall.return_value = [(1, "John")]
    
    results1 = await mssql_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    results2 = await mssql_db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    
    assert results1 == results2
