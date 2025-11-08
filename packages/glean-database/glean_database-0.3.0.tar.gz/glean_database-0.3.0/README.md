# Glean Database

## Overview

Glean Database is a unified, async-first Python library providing a consistent interface for interacting with multiple database systems and caching layers. It abstracts away the complexities of different database clients while offering built-in caching capabilities to optimize query performance.

### Key Features

- **🔌 Unified Interface**: Single API for 7 database systems (SQLite, PostgreSQL, MySQL, MSSQL, Oracle, MongoDB, TimescaleDB)
- **⚡ Async-First**: Built on `asyncio` for high-performance concurrent operations
- **💾 Integrated Caching**: Optional caching layer with in-memory and Redis backends
- **🎯 Type-Safe**: Full type hints for better IDE support and code safety
- **🧪 Fully Tested**: 58% code coverage with comprehensive unit tests
- **📊 Time-Series Support**: Native TimescaleDB integration for time-series data
- **🌊 Result Streaming**: Memory-efficient streaming for large datasets
- **🏊 Connection Pooling**: Built-in connection pooling for all SQL databases

## Installation

```bash
# Basic installation (includes SQLite, PostgreSQL, MongoDB, TimescaleDB)
pip install glean-database

# With MySQL support
pip install glean-database[mysql]

# With MSSQL support  
pip install glean-database[mssql]

# With Oracle support
pip install glean-database[oracle]

# With all database backends
pip install glean-database[all]

# For development
pip install glean-database[dev]
```

## Quick Start

### SQLite

```python
from database import SQLiteDatabase

async def main():
    db = SQLiteDatabase("my_database.db")
    await db.connect()
    
    # Create table
    await db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    
    # Insert data
    await db.execute(
        "INSERT INTO users (id, name, email) VALUES (:id, :name, :email)",
        {"id": 1, "name": "John Doe", "email": "john@example.com"}
    )
    
    # Query data
    results = await db.query("SELECT * FROM users WHERE id = :id", {"id": 1})
    print(results)
    
    await db.disconnect()
```

### PostgreSQL

```python
from database import PostgresDatabase

async def main():
    db = PostgresDatabase(
        database="mydb",
        host="localhost",
        port=5432,
        username="postgres",
        password="secret"
    )
    await db.connect()
    
    # Use named parameters with :param style
    results = await db.query(
        "SELECT * FROM users WHERE email = :email",
        {"email": "john@example.com"}
    )
    
    await db.disconnect()
```

### MongoDB

```python
from database import MongoDatabase

async def main():
    db = MongoDatabase(
        database="mydb",
        host="localhost",
        port=27017
    )
    await db.connect()
    
    # Insert documents
    await db.execute(
        "users",
        "insert",
        [{"name": "John Doe", "email": "john@example.com"}]
    )
    
    # Query documents
    results = await db.query(
        "users",
        {"email": "john@example.com"},
        {"sort": [("name", 1)]}
    )
    
    await db.disconnect()
```

### MySQL

```python
from database import MySQLDatabase

async def main():
    db = MySQLDatabase(
        database="mydb",
        host="localhost",
        port=3306,
        username="root",
        password="secret"
    )
    await db.connect()
    
    # Use named parameters with :param style
    results = await db.query(
        "SELECT * FROM users WHERE email = :email",
        {"email": "john@example.com"}
    )
    
    await db.disconnect()
```

### MSSQL (SQL Server)

```python
from database import MSSQLDatabase

async def main():
    db = MSSQLDatabase(
        database="mydb",
        host="localhost",
        port=1433,
        username="sa",
        password="YourStrong@Passw0rd"
    )
    await db.connect()
    
    # Use named parameters
    results = await db.query(
        "SELECT * FROM users WHERE id = :id",
        {"id": 1}
    )
    
    await db.disconnect()
```

### Oracle

```python
from database import OracleDatabase

async def main():
    db = OracleDatabase(
        database="ORCL",
        host="localhost",
        port=1521,
        username="system",
        password="oracle",
        service_name="ORCLPDB1"
    )
    await db.connect()
    
    # Oracle uses :param style natively
    results = await db.query(
        "SELECT * FROM users WHERE user_id = :id",
        {"id": 1}
    )
    
    await db.disconnect()
```

### TimescaleDB

```python
from database import TimescaleDatabase
from datetime import timedelta

async def main():
    db = TimescaleDatabase(
        database="metrics_db",
        host="localhost",
        port=5432,
        username="postgres"
    )
    await db.connect()
    
    # Create hypertable
    await db.execute("""
        CREATE TABLE metrics (
            time TIMESTAMPTZ NOT NULL,
            sensor_id TEXT NOT NULL,
            temperature DOUBLE PRECISION
        )
    """)
    
    await db.create_hypertable(
        "metrics",
        "time",
        chunk_time_interval="1 day"
    )
    
    # Add retention policy (keep data for 30 days)
    await db.add_retention_policy("metrics", "30 days")
    
    # Time bucket aggregation
    results = await db.time_bucket_query(
        bucket_width="1 hour",
        time_column="time",
        table_name="metrics",
        select_columns=["sensor_id"],
        aggregates=["AVG(temperature) as avg_temp"],
        order_by="bucket DESC",
        limit=10
    )
    
    await db.disconnect()
```

## Caching

Add caching to any database backend to improve query performance:

```python
from database import PostgresDatabase, RedisCache, InMemoryCache

# With Redis cache
cache = RedisCache(host="localhost", port=6379)
db = PostgresDatabase(database="mydb", cache=cache)

# Or with in-memory cache
cache = InMemoryCache()
db = PostgresDatabase(database="mydb", cache=cache)

# With background cleanup (recommended for in-memory cache with TTLs)
cache = InMemoryCache(cleanup_interval=60)  # Clean up every 60 seconds
cache.start_cleanup()  # Start background task
db = PostgresDatabase(database="mydb", cache=cache)

# Don't forget to stop cleanup when done
await cache.stop_cleanup()
```

Caching is automatic - identical queries with the same parameters will be served from cache.

### Memory Cache with Automatic Expiration

The `InMemoryCache` supports automatic cleanup of expired keys:

- **On-access expiration**: Expired keys are removed when accessed
- **Background cleanup**: Optional background task periodically removes expired keys
- **Configurable interval**: Set cleanup interval in seconds (default: 60)
- **Max size limit**: Limit cache to a maximum number of keys

```python
from database import InMemoryCache
from datetime import timedelta

# Create cache with 30-second cleanup interval
cache = InMemoryCache(cleanup_interval=30)

# Start background cleanup task
cache.start_cleanup()

# Use cache normally
await cache.set("key", "value", ttl=timedelta(minutes=5))

# Stop cleanup when done
await cache.stop_cleanup()
```

### Memory Cache with Size Limits

Limit the cache to a maximum number of keys to prevent unbounded memory growth:

```python
from database import InMemoryCache

# Cache limited to 1000 keys
cache = InMemoryCache(max_size=1000)

# When cache is full, oldest keys are evicted in this priority:
# 1. Expired keys (if any)
# 2. Keys with soonest expiration
# 3. First key inserted (FIFO)

await cache.set("key1", "value1")
await cache.set("key2", "value2", ttl=timedelta(hours=1))
# ... add up to 1000 keys

# Adding 1001st key will automatically evict the oldest
await cache.set("key1001", "value1001")  # Oldest key removed
```

## Query Result Streaming

For large datasets, use streaming to process results without loading everything into memory.

### SQLite Streaming

```python
from database import SQLiteDatabase

db = SQLiteDatabase("large_database.db")
await db.connect()

# Stream results one at a time
count = 0
async for row in db.query_stream("SELECT * FROM large_table"):
    process_row(row)  # Process without loading all rows
    count += 1

print(f"Processed {count} rows")
```

### PostgreSQL & TimescaleDB Streaming

```python
from database import PostgresDatabase

db = PostgresDatabase(database="mydb")
await db.connect()

# Stream with custom chunk size
async for row in db.query_stream(
    "SELECT * FROM metrics WHERE date > :start_date",
    {"start_date": "2024-01-01"},
    chunk_size=500  # Fetch 500 rows at a time
):
    await process_metric(row)
```

### MongoDB Streaming

```python
from database import MongoDatabase

db = MongoDatabase(database="mydb")
await db.connect()

# Stream documents with query
async for doc in db.query_stream(
    "large_collection",
    {"status": "active"},
    {"sort": [("created_at", -1)]},
    chunk_size=100
):
    await process_document(doc)
```

### Benefits

- **Memory Efficient**: Only loads chunks into memory, not entire dataset
- **Faster Start**: Begin processing immediately without waiting for full query
- **Scalable**: Handle datasets of any size without memory issues
- **Configurable**: Adjust chunk size for optimal performance

### Use Cases

- Processing millions of records
- ETL operations on large datasets
- Real-time data streaming
- Memory-constrained environments
- Progressive data export/import

## Connection Pooling

Glean Database includes built-in connection pooling for PostgreSQL, TimescaleDB, and MongoDB to optimize performance and resource usage.

### PostgreSQL & TimescaleDB

```python
from database import PostgresDatabase

db = PostgresDatabase(
    database="mydb",
    host="localhost",
    username="postgres",
    password="secret",
    min_pool_size=10,      # Minimum connections (default: 10)
    max_pool_size=20,      # Maximum connections (default: 10)
    max_queries=50000,     # Max queries per connection (default: 50000)
    max_inactive_connection_lifetime=300.0  # Max idle time in seconds (default: 300)
)

await db.connect()  # Creates connection pool
# Pool automatically manages connections
await db.disconnect()  # Closes pool
```

### MongoDB

```python
from database import MongoDatabase

db = MongoDatabase(
    database="mydb",
    host="localhost",
    username="admin",
    password="secret",
    max_pool_size=100,     # Maximum connections (default: 100)
    min_pool_size=10,      # Minimum connections (default: 10)
    max_idle_time_ms=300000  # Max idle time in milliseconds (default: 300000)
)

await db.connect()  # Creates connection pool
```

### Configuration via JSON

```json
{
  "database": "mydb",
  "host": "localhost",
  "port": 5432,
  "username": "postgres",
  "password": "secret",
  "pool": {
    "min_size": 10,
    "max_size": 20,
    "max_queries": 50000,
    "max_inactive_lifetime": 300.0
  }
}
```

### Benefits

- **Reduced Overhead**: Reuse existing connections instead of creating new ones
- **Better Performance**: Faster query execution with warm connections
- **Resource Management**: Automatic cleanup of idle connections
- **Scalability**: Handle more concurrent operations efficiently

## Architecture

### Core Components

```
database/
├── core/
│   ├── database.py      # Abstract Database base class
│   └── cache.py         # Abstract Cache base class
├── backends/
│   ├── sqlite.py        # SQLite implementation
│   ├── postgres.py      # PostgreSQL implementation
│   ├── mongo.py         # MongoDB implementation
│   └── timescale.py     # TimescaleDB implementation
└── cache/
    ├── memory.py        # In-memory cache
    └── redis.py         # Redis cache
```

### Design Principles

1. **Abstraction**: Common `Database` and `Cache` base classes define the interface
2. **Composition**: Database backends can optionally use cache backends
3. **Async-First**: All I/O operations are async for high concurrency
4. **Type Safety**: Full type hints throughout the codebase
5. **Testability**: All external dependencies are easily mockable

## API Reference

### Database Base Class

All database backends implement these methods:

#### `async def connect() -> bool`
Establish connection to the database.

#### `async def disconnect() -> bool`
Close connection to the database.

#### `async def query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]`
Execute a query and return results.

#### `async def execute(statement: str, params: Optional[Dict[str, Any]] = None) -> int`
Execute a statement that modifies the database. Returns number of affected rows.

#### `property is_connected -> bool`
Check if database is currently connected.

### TimescaleDB Extensions

TimescaleDB backend includes additional methods:

#### `async def create_hypertable(...)`
Convert a regular table to a TimescaleDB hypertable with automatic time-based partitioning.

#### `async def add_retention_policy(...)`
Automatically drop old data based on time intervals.

#### `async def add_compression_policy(...)`
Compress older chunks to save storage space.

#### `async def time_bucket_query(...)`
Execute time-bucket aggregation queries.

#### `async def continuous_aggregate(...)`
Create materialized views that automatically update.

### Cache Base Class

All cache backends implement:

#### `async def get(key: str) -> Optional[Any]`
Retrieve a value from cache.

#### `async def set(key: str, value: Any, ttl: Optional[timedelta] = None) -> bool`
Store a value in cache with optional TTL.

#### `async def delete(key: str) -> bool`
Remove a value from cache.

#### `async def clear() -> bool`
Clear all cached values.

### InMemoryCache Specific

#### `__init__(cleanup_interval: int = 60, max_size: Optional[int] = None)`
Initialize in-memory cache with optional configuration.

**Parameters:**
- `cleanup_interval`: Seconds between background cleanup runs (default: 60)
- `max_size`: Maximum number of keys allowed (default: None for unlimited)

#### `start_cleanup()`
Start the background task that periodically removes expired keys.

#### `async def stop_cleanup()`
Stop the background cleanup task.

## Command Line Interface

Glean Database includes a CLI tool for interacting with databases from the command line.

### Installation

After installing the package, the `glean-db` command will be available:

```bash
pip install glean-database
```

### Configuration

Create a JSON configuration file with your database connection parameters:

```bash
# Show example configurations
python -m database show-config-example
```

Example `config.json`:

```json
{
  "database": "./my_database.db",
  "cache": {
    "type": "memory",
    "cleanup_interval": 60,
    "max_size": 1000
  }
}
```

### Commands

#### Test Connection

```bash
python -m database test-connection -c config.json -t sqlite
```

#### Execute Queries

```bash
# Query with table output (default)
python -m database query -c config.json -t sqlite -q "SELECT * FROM users"

# Query with JSON output
python -m database query -c config.json -t sqlite -q "SELECT * FROM users" -o json

# Query with CSV output
python -m database query -c config.json -t sqlite -q "SELECT * FROM users" -o csv

# Query from file
python -m database query -c config.json -t postgres -f query.sql

# Query with parameters
python -m database query -c config.json -t postgres \
  -q "SELECT * FROM users WHERE id = :id" \
  -p '{"id": 1}'
```

#### Execute Statements

```bash
# Create table
python -m database execute -c config.json -t sqlite \
  -s "CREATE TABLE users (id INT, name TEXT, email TEXT)"

# Insert data
python -m database execute -c config.json -t sqlite \
  -s "INSERT INTO users VALUES (1, 'John', 'john@example.com')"

# Execute from file
python -m database execute -c config.json -t postgres -f schema.sql

# With parameters
python -m database execute -c config.json -t postgres \
  -s "INSERT INTO users (name, email) VALUES (:name, :email)" \
  -p '{"name": "Jane", "email": "jane@example.com"}'
```

#### Initialize Schema from SQL Files

```bash
# Initialize database schema from directory of SQL files
python -m database init-schema -c config.json -t postgres -d ~/git/glean/shared/sql/postgres/

# Dry run to validate SQL files without executing
python -m database init-schema -c config.json -t postgres -d ~/sql/ --dry-run
```

The `init-schema` command:
- Reads all `.sql` files from the directory in alphabetical order
- Parses CREATE TABLE, CREATE INDEX, CREATE FUNCTION, and other DDL statements
- Automatically skips tables that already exist (prefers modification over recreation)
- Handles multi-line statements, comments, and PostgreSQL functions
- Provides detailed execution results

### CLI Options

```
Commands:
  query             Execute a query against the database
  execute           Execute a statement that modifies the database  
  init-schema       Initialize database schema from SQL files
  test-connection   Test database connection
  list-backends     List available database backends
  show-config-example  Show example configuration file format

Options:
  -c, --config PATH              Path to JSON configuration file [required]
  -t, --type [sqlite|postgres|mongo|timescale|mysql|mssql|oracle]  Database type [required]
  -q, --query TEXT              SQL/query string to execute
  -s, --statement TEXT          SQL/command to execute
  -f, --file PATH               File containing query/statement
  -d, --directory PATH          Directory containing .sql schema files
  -p, --params TEXT             JSON string with parameters
  -o, --output [table|json|csv] Output format (default: table)
  --dry-run                     Parse SQL files without executing
  --version                     Show version
  --help                        Show help message
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=database --cov-report=term-missing

# Run specific test file
pytest tests/test_sqlite.py -v

# Run tests for specific database (requires running server)
pytest -m postgres
pytest -m mongo
pytest -m redis
pytest -m timescale
```

All unit tests use mocks and complete in under 1 second. Integration tests require running database servers.

## Development

### Setup

```bash
# Clone repository
git clone <repo-url>
cd glean-database

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"
```

### Code Style

```bash
# Format code
black database/ tests/

# Sort imports
isort database/ tests/

# Type checking
mypy database/
```

### Running Tests

See [Testing](#testing) section above.

## Requirements

- Python 3.12+
- aiosqlite >= 0.19.0
- asyncpg >= 0.28.0
- motor >= 3.3.0
- redis[hiredis] >= 5.0.0

## License

MIT

## Contributing

Contributions are welcome! Please refer to `.github/copilot-instructions.md` for development guidelines including:

- Code style standards
- Testing requirements (unit tests must complete in < 1 second)
- Documentation standards
- Error handling patterns

## Schema Management

Glean Database includes powerful schema management capabilities for initializing and maintaining database schemas from SQL files.

### Features

- **Directory-based**: Organize schema files in a directory (e.g., `01_tables.sql`, `02_indexes.sql`)
- **Automatic ordering**: Files are processed in alphabetical order
- **Idempotent**: Safely re-run schema initialization - existing tables are skipped
- **Comprehensive parsing**: Handles CREATE TABLE, CREATE INDEX, CREATE FUNCTION, triggers, views, and more
- **Comment support**: Strips SQL comments (single-line `--` and multi-line `/* */`)
- **Error handling**: Continues processing even if individual statements fail
- **Dry-run mode**: Validate SQL files without making changes

### Usage

```python
from database import PostgresDatabase
from database.core.schema import read_sql_files, apply_schema

async def initialize_database():
    db = PostgresDatabase(database="mydb", host="localhost")
    await db.connect()
    
    # Read SQL files from directory
    sql_files = read_sql_files("~/sql/postgres/")
    
    # Apply schema
    results = await apply_schema(db, sql_files)
    
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Skipped: {results['skipped']}")
    
    await db.disconnect()
```

### CLI Usage

```bash
# Initialize schema from SQL files
python -m database init-schema \
  -c config.json \
  -t postgres \
  -d ~/git/glean/shared/sql/postgres/

# Dry run to validate
python -m database init-schema \
  -c config.json \
  -t postgres \
  -d ~/sql/ \
  --dry-run
```

### Example Directory Structure

```
sql/postgres/
├── 01_mcp_tables.sql      # Core tables
├── 02_trading_tables.sql  # Domain-specific tables
├── 03_indexes.sql         # Indexes for performance
├── 04_functions.sql       # Stored procedures
└── 05_triggers.sql        # Triggers and automation
```

### Backend Support

The `table_exists()` method is implemented for:
- ✓ PostgreSQL
- ✓ SQLite
- ✓ MySQL
- ✓ MSSQL
- ✓ Oracle
- ✓ TimescaleDB (inherits from PostgreSQL)

## Roadmap

- [x] CLI tools for database management
- [x] Connection pooling configuration
- [x] Query result streaming for large datasets
- [x] MySQL support
- [x] MSSQL (SQL Server) support
- [x] Oracle support
- [x] Schema management from SQL files
- [ ] MariaDB support (use MySQL driver)
- [ ] Cassandra support
- [ ] Transaction support
- [ ] Schema migration utilities (ALTER TABLE support)
- [ ] Interactive shell (REPL)
- [ ] Schema introspection and visualization
