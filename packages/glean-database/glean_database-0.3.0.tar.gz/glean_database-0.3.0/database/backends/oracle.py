from typing import Any, Dict, List, Optional, AsyncGenerator

try:
    import oracledb
except ImportError:
    oracledb = None  # type: ignore

from ..core.database import Database
from ..core.cache import Cache


class OracleDatabase(Database):
    """Oracle database implementation using oracledb with connection pooling."""
    
    def __init__(
        self,
        database: str,
        host: str = 'localhost',
        port: int = 1521,
        username: str = 'system',
        password: Optional[str] = None,
        cache: Optional[Cache] = None,
        service_name: Optional[str] = None,
        min_pool_size: int = 1,
        max_pool_size: int = 10,
        increment: int = 1,
        encoding: str = 'UTF-8'
    ):
        if oracledb is None:
            raise ImportError(
                "oracledb is required for Oracle support. "
                "Install it with: pip install glean-database[oracle]"
            )
        """Initialize Oracle connection with pooling.
        
        Args:
            database: Database SID or service name
            host: Database host
            port: Database port
            username: Database user
            password: Database password
            cache: Optional cache backend
            service_name: Service name (if different from database)
            min_pool_size: Minimum number of connections in pool (default: 1)
            max_pool_size: Maximum number of connections in pool (default: 10)
            increment: Connection pool increment (default: 1)
            encoding: Character encoding (default: UTF-8)
        """
        super().__init__(cache)
        self._connection_params = {
            'user': username,
            'password': password,
            'host': host,
            'port': port,
            'service_name': service_name or database,
            'encoding': encoding
        }
        self._pool_params = {
            'min': min_pool_size,
            'max': max_pool_size,
            'increment': increment
        }
        self._pool: Optional[oracledb.ConnectionPool] = None
        
        # Initialize Oracle client in thin mode (no Oracle Client needed)
        oracledb.init_oracle_client(lib_dir=None)

    async def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            # Create DSN
            dsn = oracledb.makedsn(
                self._connection_params['host'],
                self._connection_params['port'],
                service_name=self._connection_params['service_name']
            )
            
            # Create connection pool
            self._pool = oracledb.create_pool(
                user=self._connection_params['user'],
                password=self._connection_params['password'],
                dsn=dsn,
                **self._pool_params
            )
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
            cache_key = f"oracle:{query}:{str(params)}"
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Oracle uses :param style, which matches our API
        connection = self._pool.acquire()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(query, params or {})
                
                # Get column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Fetch all rows
                rows = cursor.fetchall()
                
                # Convert to list of dicts
                results = [dict(zip(columns, row)) for row in rows]
                
                # Cache results if cache is available
                if self._cache:
                    # Note: This is sync code, would need async wrapper for proper async caching
                    import asyncio
                    asyncio.create_task(self._cache.set(cache_key, results))
                    
                return results
            finally:
                cursor.close()
        finally:
            self._pool.release(connection)

    async def execute(self, statement: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute a statement that modifies the database."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        connection = self._pool.acquire()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(statement, params or {})
                connection.commit()
                return cursor.rowcount
            finally:
                cursor.close()
        finally:
            self._pool.release(connection)
    
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

        connection = self._pool.acquire()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(query, params or {})
                cursor.arraysize = chunk_size
                
                # Get column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                while True:
                    rows = cursor.fetchmany(chunk_size)
                    if not rows:
                        break
                    
                    for row in rows:
                        yield dict(zip(columns, row))
            finally:
                cursor.close()
        finally:
            self._pool.release(connection)
    
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
            SELECT COUNT(*) FROM user_tables WHERE table_name = :table_name
        """
        
        connection = self._pool.acquire()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(query, {'table_name': table_name.upper()})
                result = cursor.fetchone()
                return result[0] > 0 if result else False
            finally:
                cursor.close()
        finally:
            self._pool.release(connection)
