from typing import Any, Dict, List, Optional, AsyncGenerator

try:
    import asyncpg
except ImportError:
    asyncpg = None  # type: ignore

from ..core.database import Database
from ..core.cache import Cache

class PostgresDatabase(Database):
    """PostgreSQL database implementation using asyncpg with connection pooling."""
    
    def __init__(
        self,
        database: str,
        host: str = 'localhost',
        port: int = 5432,
        username: str = 'postgres',
        password: Optional[str] = None,
        cache: Optional[Cache] = None,
        min_pool_size: int = 10,
        max_pool_size: int = 10,
        max_queries: int = 50000,
        max_inactive_connection_lifetime: float = 300.0
    ):
        """Initialize PostgreSQL connection with pooling.
        
        if asyncpg is None:
            raise ImportError(
                "asyncpg is required for PostgreSQL support. "
                "Install it with: pip install glean-database[postgres]"
            )
        
        Args:
            database: Database name
            host: Database host
            port: Database port
            username: Database user
            password: Database password
            cache: Optional cache backend
            min_pool_size: Minimum number of connections in pool (default: 10)
            max_pool_size: Maximum number of connections in pool (default: 10)
            max_queries: Max queries per connection before recycling (default: 50000)
            max_inactive_connection_lifetime: Max seconds a connection can be idle (default: 300)
        """
        super().__init__(cache)
        self._connection_params = {
            'database': database,
            'host': host,
            'port': port,
            'user': username,
            'password': password,
            'min_size': min_pool_size,
            'max_size': max_pool_size,
            'max_queries': max_queries,
            'max_inactive_connection_lifetime': max_inactive_connection_lifetime
        }
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            self._pool = await asyncpg.create_pool(**self._connection_params)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    async def disconnect(self) -> bool:
        """Close connection to the database."""
        if self._pool:
            try:
                await self._pool.close()
                self._connected = False
                return True
            except Exception:
                return False
        return True

    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        # Check cache first if available
        if self._cache:
            cache_key = f"pg:{query}:{str(params)}"
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Convert dict params to list for asyncpg
        query_params = []
        if params:
            # Replace :param style with $1 style and collect values
            for i, (key, value) in enumerate(params.items(), 1):
                query = query.replace(f":{key}", f"${i}")
                query_params.append(value)

        async with self._pool.acquire() as conn:
            # Execute query
            results = await conn.fetch(query, *query_params)
            
            # Convert to list of dicts
            records = [dict(record) for record in results]
            
            # Cache results if cache is available
            if self._cache:
                await self._cache.set(cache_key, records)
                
            return records

    async def execute(self, statement: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute a statement that modifies the database."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        # Convert dict params to list for asyncpg
        query_params = []
        if params:
            # Replace :param style with $1 style and collect values
            for i, (key, value) in enumerate(params.items(), 1):
                statement = statement.replace(f":{key}", f"${i}")
                query_params.append(value)

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Execute statement
                result = await conn.execute(statement, *query_params)
                
                # Parse the command tag to get affected rows
                if result and 'UPDATE' in result:
                    return int(result.split()[-1])
                elif result and 'DELETE' in result:
                    return int(result.split()[-1])
                elif result and 'INSERT' in result:
                    return 1  # or int(result.split()[-1]) for INSERT 0 N
                return 0
    
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
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        # Convert dict params to list for asyncpg
        query_params = []
        if params:
            for i, (key, value) in enumerate(params.items(), 1):
                query = query.replace(f":{key}", f"${i}")
                query_params.append(value)
        
        async with self._pool.acquire() as conn:
            # Use cursor for streaming
            async with conn.transaction():
                cursor = await conn.cursor(query, *query_params)
                
                while True:
                    # Fetch chunk
                    rows = await cursor.fetch(chunk_size)
                    if not rows:
                        break
                    
                    # Yield each row as dict
                    for row in rows:
                        yield dict(row)
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        if not self._pool:
            raise RuntimeError("Database not connected")
        
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = $1
            )
        """
        
        async with self._pool.acquire() as conn:
            result = await conn.fetchval(query, table_name)
            return result
