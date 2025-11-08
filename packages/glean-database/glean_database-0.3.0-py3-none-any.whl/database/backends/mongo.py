from typing import Any, Dict, List, Optional, AsyncGenerator
import urllib.parse

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from bson.objectid import ObjectId
except ImportError:
    AsyncIOMotorClient = None  # type: ignore
    ObjectId = None  # type: ignore

from ..core.database import Database
from ..core.cache import Cache

class MongoDatabase(Database):
    """MongoDB database implementation using Motor with connection pooling."""
    
    def __init__(
        self,
        database: str,
        host: str = 'localhost',
        port: int = 27017,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cache: Optional[Cache] = None,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 300000
    ):
        """Initialize MongoDB connection with connection pooling.
        
        if AsyncIOMotorClient is None:
            raise ImportError(
                "motor is required for MongoDB support. "
                "Install it with: pip install glean-database[mongo]"
            )
        
        Args:
            database: Database name
            host: Database host
            port: Database port  
            username: Database user
            password: Database password
            cache: Optional cache backend
            max_pool_size: Maximum number of connections in pool (default: 100)
            min_pool_size: Minimum number of connections in pool (default: 10)
            max_idle_time_ms: Max milliseconds a connection can be idle (default: 300000)
        """
        super().__init__(cache)
        self._database_name = database
        self._pool_options = {
            'maxPoolSize': max_pool_size,
            'minPoolSize': min_pool_size,
            'maxIdleTimeMS': max_idle_time_ms
        }
        
        # Build connection string with pool options
        pool_params = '&'.join(f"{k}={v}" for k, v in self._pool_options.items())
        if username and password:
            uri = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}:{port}/?{pool_params}"
        else:
            uri = f"mongodb://{host}:{port}/?{pool_params}"
            
        self._client: Optional[AsyncIOMotorClient] = None
        self._uri = uri
        self._db = None

    async def connect(self) -> bool:
        """Establish connection to the database."""
        try:
            self._client = AsyncIOMotorClient(self._uri)
            self._db = self._client[self._database_name]
            # Verify connection by listing collections
            await self._db.list_collection_names()
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    async def disconnect(self) -> bool:
        """Close connection to the database."""
        if self._client:
            try:
                self._client.close()
                self._connected = False
                return True
            except Exception:
                return False
        return True

    async def query(self, collection: str, query: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.
        
        Args:
            collection: The collection to query
            query: The MongoDB query dict
            params: Optional parameters like sort, limit, etc.
            
        Returns:
            List of documents matching the query
        """
        if not self._db:
            raise RuntimeError("Database not connected")

        # Check cache first if available
        if self._cache:
            cache_key = f"mongo:{collection}:{query}:{str(params)}"
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Process parameters
        options = params or {}
        sort = options.get('sort')
        limit = options.get('limit')
        skip = options.get('skip')

        # Execute query
        cursor = self._db[collection].find(query)
        
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        results = []
        async for document in cursor:
            # Convert ObjectId to string for JSON serialization
            if '_id' in document:
                document['_id'] = str(document['_id'])
            results.append(document)

        # Cache results if cache is available
        if self._cache:
            await self._cache.set(cache_key, results)

        return results

    async def execute(
        self, 
        collection: str, 
        operation: str, 
        documents: List[Dict[str, Any]],
        filter_query: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Execute a write operation on the database.
        
        Args:
            collection: The collection to operate on
            operation: The operation type ('insert', 'update', or 'delete')
            documents: Documents to insert/update
            filter_query: Filter for update/delete operations
            
        Returns:
            Number of documents affected
        """
        if not self._db:
            raise RuntimeError("Database not connected")

        result = 0
        coll = self._db[collection]

        if operation == 'insert':
            if len(documents) == 1:
                await coll.insert_one(documents[0])
                result = 1
            else:
                result = (await coll.insert_many(documents)).inserted_ids.__len__()
        
        elif operation == 'update' and filter_query:
            if len(documents) == 1:
                result = (await coll.update_many(filter_query, documents[0])).modified_count
            else:
                total = 0
                for doc in documents:
                    total += (await coll.update_many(filter_query, doc)).modified_count
                result = total
        
        elif operation == 'delete' and filter_query:
            result = (await coll.delete_many(filter_query)).deleted_count

        return result
    
    async def query_stream(self, collection: str, query: Dict[str, Any],
                          params: Optional[Dict[str, Any]] = None,
                          chunk_size: int = 100) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream query results for large datasets.
        
        Yields results one at a time without loading entire dataset into memory.
        Useful for processing large MongoDB collections efficiently.
        
        Args:
            collection: The collection to query
            query: The MongoDB query dict
            params: Optional parameters like sort, skip, limit
            chunk_size: Number of documents to fetch at a time (default: 100)
            
        Yields:
            Dict representing each document
            
        Example:
            async for doc in db.query_stream("users", {"active": True}):
                process_document(doc)
        """
        if not self._db:
            raise RuntimeError("Database not connected")
        
        # Process parameters
        options = params or {}
        sort = options.get('sort')
        skip = options.get('skip')
        limit = options.get('limit')
        
        # Execute query with cursor
        cursor = self._db[collection].find(query, batch_size=chunk_size)
        
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        # Stream results
        async for document in cursor:
            # Convert ObjectId to string for JSON serialization
            if '_id' in document:
                document['_id'] = str(document['_id'])
            yield document
