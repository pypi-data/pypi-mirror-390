from typing import Any, Dict, List, Optional, AsyncGenerator
import asyncio

try:
    import pymssql
except ImportError:
    pymssql = None  # type: ignore

from ..core.database import Database
from ..core.cache import Cache


class MSSQLDatabase(Database):
    """Microsoft SQL Server database implementation using pymssql with connection pooling."""
    
    def __init__(
        self,
        database: str,
        host: str = 'localhost',
        port: int = 1433,
        username: str = 'sa',
        password: Optional[str] = None,
        cache: Optional[Cache] = None,
        min_pool_size: int = 1,
        max_pool_size: int = 10,
        timeout: int = 30
    ):
        if pymssql is None:
            raise ImportError(
                "pymssql is required for MSSQL support. "
                "Install it with: pip install glean-database[mssql]"
            )
        """Initialize MSSQL connection with pooling.
        
        Args:
            database: Database name
            host: Database host
            port: Database port
            username: Database user
            password: Database password
            cache: Optional cache backend
            min_pool_size: Minimum number of connections in pool (default: 1)
            max_pool_size: Maximum number of connections in pool (default: 10)
            timeout: Connection timeout in seconds (default: 30)
        """
        super().__init__(cache)
        
        self._host = host
        self._port = port
        self._database = database
        self._username = username
        self._password = password
        self._timeout = timeout
        self._min_pool_size = min_pool_size
        self._max_pool_size = max_pool_size
        self._pool: List[Any] = []
        self._pool_lock = asyncio.Lock()
        self._pool_semaphore = asyncio.Semaphore(max_pool_size)

    async def _create_connection(self):
        """Create a new connection to the database."""
        loop = asyncio.get_event_loop()
        conn = await loop.run_in_executor(
            None,
            pymssql.connect,
            self._host,
            self._username,
            self._password,
            self._database,
            self._port,
            self._timeout
        )
        return conn

    async def _get_connection(self):
        """Get a connection from the pool."""
        await self._pool_semaphore.acquire()
        async with self._pool_lock:
            if self._pool:
                return self._pool.pop()
            else:
                return await self._create_connection()

    async def _release_connection(self, conn):
        """Release a connection back to the pool."""
        async with self._pool_lock:
            if len(self._pool) < self._max_pool_size:
                self._pool.append(conn)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, conn.close)
        self._pool_semaphore.release()

    async def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            # Pre-populate pool with minimum connections
            async with self._pool_lock:
                for _ in range(self._min_pool_size):
                    conn = await self._create_connection()
                    self._pool.append(conn)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    async def disconnect(self) -> bool:
        """Close connection to the database."""
        if self._pool:
            try:
                loop = asyncio.get_event_loop()
                async with self._pool_lock:
                    for conn in self._pool:
                        await loop.run_in_executor(None, conn.close)
                    self._pool.clear()
                self._connected = False
                return True
            except Exception:
                return False
        return True

    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if not self._connected:
            raise RuntimeError("Database not connected")

        # Check cache first if available
        if self._cache:
            cache_key = f"mssql:{query}:{str(params)}"
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Convert named parameters to positional for MSSQL (uses %s)
        query_params = None
        if params:
            query_params = tuple(params.values())
            # Replace :param with %s
            for key in params.keys():
                query = query.replace(f":{key}", "%s")

        conn = await self._get_connection()
        try:
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            
            # Execute query
            await loop.run_in_executor(None, cursor.execute, query, query_params or ())
            
            # Fetch all rows
            rows = await loop.run_in_executor(None, cursor.fetchall)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Convert to list of dicts
            results = [dict(zip(columns, row)) for row in rows]
            
            # Close cursor
            await loop.run_in_executor(None, cursor.close)
            
            # Cache results if cache is available
            if self._cache:
                await self._cache.set(cache_key, results)
                
            return results
        finally:
            await self._release_connection(conn)

    async def execute(self, statement: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute a statement that modifies the database."""
        if not self._connected:
            raise RuntimeError("Database not connected")

        # Convert named parameters to positional for MSSQL (uses %s)
        query_params = None
        if params:
            query_params = tuple(params.values())
            for key in params.keys():
                statement = statement.replace(f":{key}", "%s")

        conn = await self._get_connection()
        try:
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            
            # Execute statement
            await loop.run_in_executor(None, cursor.execute, statement, query_params or ())
            await loop.run_in_executor(None, conn.commit)
            
            rowcount = cursor.rowcount
            await loop.run_in_executor(None, cursor.close)
            
            return rowcount
        finally:
            await self._release_connection(conn)
    
    async def query_stream(self, query: str, params: Optional[Dict[str, Any]] = None,
                          chunk_size: int = 100) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream query results for large datasets.
        
        Yields results one at a time without loading entire dataset into memory.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            chunk_size: Number of rows to fetch at a time (default: 100)
            
        Yields:
            Dict representing each row
        """
        if not self._connected:
            raise RuntimeError("Database not connected")

        # Convert named parameters to positional for MSSQL (uses %s)
        query_params = None
        if params:
            query_params = tuple(params.values())
            for key in params.keys():
                query = query.replace(f":{key}", "%s")

        conn = await self._get_connection()
        try:
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            
            # Execute query
            await loop.run_in_executor(None, cursor.execute, query, query_params or ())
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            while True:
                rows = await loop.run_in_executor(None, cursor.fetchmany, chunk_size)
                if not rows:
                    break
                
                for row in rows:
                    yield dict(zip(columns, row))
            
            await loop.run_in_executor(None, cursor.close)
        finally:
            await self._release_connection(conn)
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        if not self._connected:
            raise RuntimeError("Database not connected")
        
        query = """
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = %s AND table_type = 'BASE TABLE'
        """
        
        conn = await self._get_connection()
        try:
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(None, conn.cursor)
            await loop.run_in_executor(None, cursor.execute, query, (table_name,))
            result = await loop.run_in_executor(None, cursor.fetchone)
            await loop.run_in_executor(None, cursor.close)
            return result[0] > 0 if result else False
        finally:
            await self._release_connection(conn)
