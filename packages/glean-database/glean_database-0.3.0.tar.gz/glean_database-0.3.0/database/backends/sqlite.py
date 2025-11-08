from typing import Any, Dict, List, Optional, AsyncGenerator

try:
    import aiosqlite
except ImportError:
    aiosqlite = None  # type: ignore

from ..core.database import Database
from ..core.cache import Cache

class SQLiteDatabase(Database):
    """SQLite database implementation."""
    
    def __init__(self, database_path: str, cache: Optional[Cache] = None):
        """Initialize SQLite database with optional cache."""
        if aiosqlite is None:
            raise ImportError(
                "aiosqlite is required for SQLite support. "
                "Install it with: pip install glean-database[sqlite]"
            )
        super().__init__(cache)
        self._database_path = database_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            self._connection = await aiosqlite.connect(self._database_path)
            self._connection.row_factory = aiosqlite.Row
            self._connected = True
            return True
        except aiosqlite.Error:
            self._connected = False
            return False

    async def disconnect(self) -> bool:
        """Close connection to the database."""
        if self._connection:
            try:
                await self._connection.close()
                self._connection = None
                self._connected = False
                return True
            except aiosqlite.Error:
                return False
        return True

    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if not self._connected or not self._connection:
            raise RuntimeError("Database not connected")

        # Check cache first if available
        if self._cache:
            cache_key = f"{query}:{str(params)}"
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Execute query
        async with self._connection.cursor() as cursor:
            if params:
                await cursor.execute(query, params)
            else:
                await cursor.execute(query)
                
            rows = await cursor.fetchall()
            results = [dict(row) for row in rows]
            
            # Cache results if cache is available
            if self._cache:
                await self._cache.set(cache_key, results)
                
            return results

    async def execute(self, statement: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute a statement that modifies the database."""
        if not self._connected or not self._connection:
            raise RuntimeError("Database not connected")

        async with self._connection.cursor() as cursor:
            if params:
                await cursor.execute(statement, params)
            else:
                await cursor.execute(statement)
            
            await self._connection.commit()
            return cursor.rowcount
    
    async def query_stream(self, query: str, params: Optional[Dict[str, Any]] = None,
                          chunk_size: int = 100) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream query results for large datasets.
        
        Yields results one at a time without loading entire dataset into memory.
        Useful for processing large result sets efficiently.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            chunk_size: Number of rows to fetch at a time (default: 100)
            
        Yields:
            Dict representing each row
            
        Example:
            async for row in db.query_stream("SELECT * FROM large_table"):
                process_row(row)
        """
        if not self._connected or not self._connection:
            raise RuntimeError("Database not connected")
        
        async with self._connection.cursor() as cursor:
            if params:
                await cursor.execute(query, params)
            else:
                await cursor.execute(query)
            
            # Stream results in chunks
            while True:
                rows = await cursor.fetchmany(chunk_size)
                if not rows:
                    break
                
                for row in rows:
                    yield dict(row)
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        if not self._connected or not self._connection:
            raise RuntimeError("Database not connected")
        
        query = """
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, (table_name,))
            result = await cursor.fetchone()
            return result[0] > 0 if result else False
