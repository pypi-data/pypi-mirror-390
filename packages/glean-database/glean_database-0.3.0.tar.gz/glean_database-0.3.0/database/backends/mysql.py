from typing import Any, Dict, List, Optional, AsyncGenerator

try:
    import aiomysql
except ImportError:
    aiomysql = None  # type: ignore

from ..core.database import Database
from ..core.cache import Cache


class MySQLDatabase(Database):
    """MySQL database implementation using aiomysql with connection pooling."""
    
    def __init__(
        self,
        database: str,
        host: str = 'localhost',
        port: int = 3306,
        username: str = 'root',
        password: Optional[str] = None,
        cache: Optional[Cache] = None,
        min_pool_size: int = 1,
        max_pool_size: int = 10,
        pool_recycle: int = 3600,
        charset: str = 'utf8mb4'
    ):
        if aiomysql is None:
            raise ImportError(
                "aiomysql is required for MySQL support. "
                "Install it with: pip install glean-database[mysql]"
            )
        """Initialize MySQL connection with pooling.
        
        Args:
            database: Database name
            host: Database host
            port: Database port
            username: Database user
            password: Database password
            cache: Optional cache backend
            min_pool_size: Minimum number of connections in pool (default: 1)
            max_pool_size: Maximum number of connections in pool (default: 10)
            pool_recycle: Seconds before recycling connections (default: 3600)
            charset: Character set to use (default: utf8mb4)
        """
        super().__init__(cache)
        self._connection_params = {
            'db': database,
            'host': host,
            'port': port,
            'user': username,
            'password': password,
            'minsize': min_pool_size,
            'maxsize': max_pool_size,
            'pool_recycle': pool_recycle,
            'charset': charset,
            'autocommit': False
        }
        self._pool: Optional[aiomysql.Pool] = None

    async def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            self._pool = await aiomysql.create_pool(**self._connection_params)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    async def disconnect(self) -> bool:
        """Close connection to the database."""
        if self._pool:
            try:
                self._pool.close()
                await self._pool.wait_closed()
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
            cache_key = f"mysql:{query}:{str(params)}"
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Convert named parameters to positional for MySQL
        query_params = None
        if params:
            query_params = tuple(params.values())
            # Replace :param with %s
            for key in params.keys():
                query = query.replace(f":{key}", "%s")

        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, query_params)
                results = await cursor.fetchall()
                
                # Cache results if cache is available
                if self._cache:
                    await self._cache.set(cache_key, results)
                    
                return results

    async def execute(self, statement: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute a statement that modifies the database."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        # Convert named parameters to positional for MySQL
        query_params = None
        if params:
            query_params = tuple(params.values())
            # Replace :param with %s
            for key in params.keys():
                statement = statement.replace(f":{key}", "%s")

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(statement, query_params)
                await conn.commit()
                return cursor.rowcount
    
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
        if not self._pool:
            raise RuntimeError("Database not connected")

        # Convert named parameters to positional for MySQL
        query_params = None
        if params:
            query_params = tuple(params.values())
            for key in params.keys():
                query = query.replace(f":{key}", "%s")

        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, query_params)
                
                while True:
                    rows = await cursor.fetchmany(chunk_size)
                    if not rows:
                        break
                    
                    for row in rows:
                        yield row
    
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
            SELECT COUNT(*) as count FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = %s
        """
        
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (table_name,))
                result = await cursor.fetchone()
                return result['count'] > 0 if result else False
