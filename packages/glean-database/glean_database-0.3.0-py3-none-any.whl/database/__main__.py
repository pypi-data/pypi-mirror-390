#!/usr/bin/env python3
"""CLI tool for glean-database.

Provides command-line access to database operations with support
for multiple database backends and connection configuration via JSON.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List

import click

from database import InMemoryCache, RedisCache

# Dynamically discover available database backends
AVAILABLE_DATABASES = {}

try:
    from database import SQLiteDatabase
    AVAILABLE_DATABASES['sqlite'] = SQLiteDatabase
except ImportError:
    pass

try:
    from database import PostgresDatabase
    AVAILABLE_DATABASES['postgres'] = PostgresDatabase
except ImportError:
    pass

try:
    from database import MongoDatabase
    AVAILABLE_DATABASES['mongo'] = MongoDatabase
except ImportError:
    pass

try:
    from database import TimescaleDatabase
    AVAILABLE_DATABASES['timescale'] = TimescaleDatabase
except ImportError:
    pass

try:
    from database import MySQLDatabase
    AVAILABLE_DATABASES['mysql'] = MySQLDatabase
except ImportError:
    pass

try:
    from database import MSSQLDatabase
    AVAILABLE_DATABASES['mssql'] = MSSQLDatabase
except ImportError:
    pass

try:
    from database import OracleDatabase
    AVAILABLE_DATABASES['oracle'] = OracleDatabase
except ImportError:
    pass


def get_available_db_types() -> List[str]:
    """Get list of available database types."""
    return sorted(AVAILABLE_DATABASES.keys())


def load_config(config_path: str) -> Dict[str, Any]:
    """Load database configuration from JSON file.
    
    Args:
        config_path: Path to JSON configuration file
        
    Returns:
        Dictionary with connection parameters
        
    Raises:
        click.ClickException: If file not found or invalid JSON
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise click.ClickException(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in configuration file: {e}")


def create_database(db_type: str, config: Dict[str, Any]):
    """Create database instance from configuration.
    
    Args:
        db_type: Database type (sqlite, postgres, mongo, timescale, mysql, mssql, oracle)
        config: Connection parameters
        
    Returns:
        Database instance
        
    Raises:
        click.ClickException: If database type is not available or unknown
    """
    if db_type not in AVAILABLE_DATABASES:
        available = ', '.join(get_available_db_types())
        raise click.ClickException(
            f"Database type '{db_type}' is not available. "
            f"Available types: {available}. "
            f"Install missing drivers with: pip install glean-database[{db_type}]"
        )
    # Extract cache configuration if present
    cache = None
    if 'cache' in config:
        cache_config = config.pop('cache')
        cache_type = cache_config.get('type', 'memory')
        
        if cache_type == 'redis':
            cache = RedisCache(
                host=cache_config.get('host', 'localhost'),
                port=cache_config.get('port', 6379),
                db=cache_config.get('db', 0)
            )
        else:
            cache = InMemoryCache(
                cleanup_interval=cache_config.get('cleanup_interval', 60),
                max_size=cache_config.get('max_size')
            )
    
    # Extract pool configuration if present
    pool_config = config.pop('pool', {})
    
    # Get database class
    DatabaseClass = AVAILABLE_DATABASES[db_type]
    
    # Create database instance based on type
    if db_type == 'sqlite':
        return DatabaseClass(config['database'], cache=cache)
    
    elif db_type in ('postgres', 'timescale'):
        return DatabaseClass(
            database=config['database'],
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            username=config.get('username', 'postgres'),
            password=config.get('password'),
            cache=cache,
            min_pool_size=pool_config.get('min_size', 10),
            max_pool_size=pool_config.get('max_size', 10),
            max_queries=pool_config.get('max_queries', 50000),
            max_inactive_connection_lifetime=pool_config.get('max_inactive_lifetime', 300.0)
        )
    
    elif db_type == 'mongo':
        return DatabaseClass(
            database=config['database'],
            host=config.get('host', 'localhost'),
            port=config.get('port', 27017),
            username=config.get('username'),
            password=config.get('password'),
            cache=cache,
            max_pool_size=pool_config.get('max_size', 100),
            min_pool_size=pool_config.get('min_size', 10),
            max_idle_time_ms=pool_config.get('max_idle_time_ms', 300000)
        )
    
    elif db_type == 'mysql':
        return DatabaseClass(
            database=config['database'],
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            username=config.get('username', 'root'),
            password=config.get('password'),
            cache=cache,
            min_pool_size=pool_config.get('min_size', 1),
            max_pool_size=pool_config.get('max_size', 10),
            pool_recycle=pool_config.get('pool_recycle', 3600)
        )
    
    elif db_type == 'mssql':
        return DatabaseClass(
            database=config['database'],
            host=config.get('host', 'localhost'),
            port=config.get('port', 1433),
            username=config.get('username', 'sa'),
            password=config.get('password'),
            cache=cache,
            min_pool_size=pool_config.get('min_size', 1),
            max_pool_size=pool_config.get('max_size', 10),
            timeout=pool_config.get('timeout', 30)
        )
    
    elif db_type == 'oracle':
        return DatabaseClass(
            database=config['database'],
            host=config.get('host', 'localhost'),
            port=config.get('port', 1521),
            username=config.get('username', 'system'),
            password=config.get('password'),
            cache=cache,
            service_name=config.get('service_name'),
            min_pool_size=pool_config.get('min_size', 1),
            max_pool_size=pool_config.get('max_size', 10)
        )
    
    else:
        # This should never happen due to the check above
        raise click.ClickException(f"Unknown database type: {db_type}")


@click.group(epilog=f"""Available backends: {', '.join(get_available_db_types()) or 'none'}\n\nUse 'list-backends' command for installation instructions.""")
@click.version_option(version='0.1.0')
def cli():
    """Glean Database CLI - Unified database access tool.
    
    Dynamically supports available database backends based on installed drivers.
    """
    pass


@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to JSON configuration file')
@click.option('--type', '-t', 'db_type', required=True,
              type=click.Choice(get_available_db_types(), case_sensitive=False),
              help='Database type')
@click.option('--query', '-q', help='SQL/query string to execute')
@click.option('--file', '-f', type=click.Path(exists=True),
              help='File containing query/operation')
@click.option('--params', '-p', help='JSON string with query parameters')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'csv']),
              default='table', help='Output format')
def query(config: str, db_type: str, query: Optional[str], file: Optional[str],
          params: Optional[str], output: str):
    """Execute a query against the database.
    
    Examples:
    
        # Query from command line
        glean-db query -c config.json -t postgres -q "SELECT * FROM users"
        
        # Query from file with parameters
        glean-db query -c config.json -t postgres -f query.sql -p '{"id": 1}'
        
        # Output as JSON
        glean-db query -c config.json -t sqlite -q "SELECT * FROM users" -o json
    """
    async def run_query():
        # Load configuration
        db_config = load_config(config)
        db = create_database(db_type, db_config)
        
        try:
            # Connect to database
            await db.connect()
            if not db.is_connected:
                raise click.ClickException("Failed to connect to database")
            
            # Get query string
            query_str = query
            if file:
                with open(file, 'r') as f:
                    query_str = f.read()
            
            if not query_str:
                raise click.ClickException("No query provided. Use --query or --file")
            
            # Parse parameters
            query_params = None
            if params:
                try:
                    query_params = json.loads(params)
                except json.JSONDecodeError as e:
                    raise click.ClickException(f"Invalid JSON in parameters: {e}")
            
            # Execute query
            if db_type == 'mongo':
                # MongoDB uses collection name as first parameter
                collection = click.prompt("Collection name", type=str)
                results = await db.query(collection, query_params or {})
            else:
                results = await db.query(query_str, query_params)
            
            # Output results
            if output == 'json':
                click.echo(json.dumps(results, indent=2, default=str))
            elif output == 'csv':
                if results:
                    # Print header
                    click.echo(','.join(results[0].keys()))
                    # Print rows
                    for row in results:
                        click.echo(','.join(str(v) for v in row.values()))
            else:  # table format
                if not results:
                    click.echo("No results returned")
                else:
                    # Simple table format
                    keys = list(results[0].keys())
                    widths = {k: max(len(k), max(len(str(r[k])) for r in results)) 
                             for k in keys}
                    
                    # Header
                    header = ' | '.join(k.ljust(widths[k]) for k in keys)
                    click.echo(header)
                    click.echo('-' * len(header))
                    
                    # Rows
                    for row in results:
                        click.echo(' | '.join(str(row[k]).ljust(widths[k]) for k in keys))
                    
                    click.echo(f"\n{len(results)} row(s) returned")
        
        finally:
            await db.disconnect()
    
    asyncio.run(run_query())


@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to JSON configuration file')
@click.option('--type', '-t', 'db_type', required=True,
              type=click.Choice(get_available_db_types(), case_sensitive=False),
              help='Database type')
@click.option('--statement', '-s', help='SQL/command to execute')
@click.option('--file', '-f', type=click.Path(exists=True),
              help='File containing statement')
@click.option('--params', '-p', help='JSON string with parameters')
def execute(config: str, db_type: str, statement: Optional[str], 
            file: Optional[str], params: Optional[str]):
    """Execute a statement that modifies the database.
    
    Examples:
    
        # Create table
        glean-db execute -c config.json -t sqlite -s "CREATE TABLE users (id INT, name TEXT)"
        
        # Insert with parameters
        glean-db execute -c config.json -t postgres -f insert.sql -p '{"id": 1, "name": "John"}'
    """
    async def run_execute():
        # Load configuration
        db_config = load_config(config)
        db = create_database(db_type, db_config)
        
        try:
            # Connect to database
            await db.connect()
            if not db.is_connected:
                raise click.ClickException("Failed to connect to database")
            
            # Get statement string
            stmt = statement
            if file:
                with open(file, 'r') as f:
                    stmt = f.read()
            
            if not stmt:
                raise click.ClickException("No statement provided. Use --statement or --file")
            
            # Parse parameters
            stmt_params = None
            if params:
                try:
                    stmt_params = json.loads(params)
                except json.JSONDecodeError as e:
                    raise click.ClickException(f"Invalid JSON in parameters: {e}")
            
            # Execute statement
            if db_type == 'mongo':
                collection = click.prompt("Collection name", type=str)
                operation = click.prompt("Operation (insert/update/delete)", type=str)
                documents = json.loads(stmt)
                if not isinstance(documents, list):
                    documents = [documents]
                result = await db.execute(collection, operation, documents, stmt_params)
            else:
                result = await db.execute(stmt, stmt_params)
            
            click.echo(f"✓ Statement executed successfully")
            click.echo(f"  {result} row(s) affected")
        
        finally:
            await db.disconnect()
    
    asyncio.run(run_execute())


@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to JSON configuration file')
@click.option('--type', '-t', 'db_type', required=True,
              type=click.Choice(get_available_db_types(), case_sensitive=False),
              help='Database type')
@click.option('--table', required=True, help='Table name to load data into')
@click.option('--file', '-f', required=True, type=click.Path(exists=True),
              help='JSON file with data to load')
@click.option('--batch-size', '-b', default=100, type=int,
              help='Number of rows to insert per batch (default: 100)')
@click.option('--create-table/--no-create-table', default=False,
              help='Automatically create table if it does not exist')
def load(config: str, db_type: str, table: str, file: str, batch_size: int, create_table: bool):
    """Load data from JSON file into a database table.
    
    The JSON file should contain an array of objects where each object represents a row.
    All objects should have the same keys (column names).
    
    Examples:
    
        # Load data from JSON file
        glean-db load -c config.json -t sqlite --table users -f data.json
        
        # Load with auto-create table
        glean-db load -c config.json -t postgres --table users -f data.json --create-table
        
        # Load with custom batch size
        glean-db load -c config.json -t mysql --table products -f products.json -b 500
    
    JSON file format:
        [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
    """
    async def run_load():
        # Load data from JSON file
        try:
            with open(file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON in data file: {e}")
        except Exception as e:
            raise click.ClickException(f"Error reading data file: {e}")
        
        # Validate data format
        if not isinstance(data, list):
            raise click.ClickException("JSON file must contain an array of objects")
        
        if not data:
            click.echo("⚠ Warning: JSON file is empty, nothing to load")
            return
        
        if not all(isinstance(row, dict) for row in data):
            raise click.ClickException("All elements in JSON array must be objects (dictionaries)")
        
        # Get column names from first row
        columns = list(data[0].keys())
        if not columns:
            raise click.ClickException("Objects in JSON array must have at least one key")
        
        # Validate all rows have the same columns
        for i, row in enumerate(data):
            if set(row.keys()) != set(columns):
                raise click.ClickException(
                    f"Row {i} has different columns. Expected: {columns}, Got: {list(row.keys())}"
                )
        
        # Load configuration and create database
        db_config = load_config(config)
        db = create_database(db_type, db_config)
        
        try:
            # Connect to database
            await db.connect()
            if not db.is_connected:
                raise click.ClickException("Failed to connect to database")
            
            click.echo(f"Loading {len(data)} row(s) into table '{table}'...")
            
            # Create table if requested (SQL databases only)
            if create_table and db_type not in ('mongo',):
                # Infer column types from data
                column_defs = []
                for col in columns:
                    # Simple type inference based on first non-null value
                    sample_val = next((row[col] for row in data if row.get(col) is not None), None)
                    if sample_val is None:
                        col_type = "TEXT"
                    elif isinstance(sample_val, bool):
                        col_type = "BOOLEAN"
                    elif isinstance(sample_val, int):
                        col_type = "INTEGER"
                    elif isinstance(sample_val, float):
                        col_type = "REAL" if db_type == 'sqlite' else "FLOAT"
                    else:
                        col_type = "TEXT"
                    column_defs.append(f"{col} {col_type}")
                
                create_stmt = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(column_defs)})"
                try:
                    await db.execute(create_stmt)
                    click.echo(f"✓ Table '{table}' ready")
                except Exception as e:
                    raise click.ClickException(f"Failed to create table: {e}")
            
            # Insert data in batches
            total_inserted = 0
            
            if db_type == 'mongo':
                # MongoDB: use insert_many
                # MongoDB execute expects (collection, operation, documents, filter)
                result = await db.execute(table, 'insert', data, None)
                total_inserted = len(data)
            else:
                # SQL databases: use INSERT statements
                placeholders = ', '.join([f":{col}" for col in columns])
                insert_stmt = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    
                    for row in batch:
                        try:
                            await db.execute(insert_stmt, row)
                            total_inserted += 1
                        except Exception as e:
                            click.echo(f"⚠ Warning: Failed to insert row {i + batch.index(row)}: {e}")
                    
                    if i + batch_size < len(data):
                        click.echo(f"  Inserted {total_inserted}/{len(data)} rows...")
            
            click.echo(f"\n✓ Successfully loaded {total_inserted} row(s) into '{table}'")
            
            if total_inserted < len(data):
                click.echo(f"⚠ {len(data) - total_inserted} row(s) failed to insert")
        
        finally:
            await db.disconnect()
    
    asyncio.run(run_load())


@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to JSON configuration file')
@click.option('--type', '-t', 'db_type', required=True,
              type=click.Choice(get_available_db_types(), case_sensitive=False),
              help='Database type')
def test_connection(config: str, db_type: str):
    """Test database connection.
    
    Examples:
    
        glean-db test-connection -c config.json -t postgres
    """
    async def test_conn():
        db_config = load_config(config)
        db = create_database(db_type, db_config)
        
        try:
            click.echo(f"Testing connection to {db_type} database...")
            await db.connect()
            
            if db.is_connected:
                click.echo("✓ Connection successful!")
            else:
                raise click.ClickException("✗ Connection failed")
        
        finally:
            await db.disconnect()
    
    asyncio.run(test_conn())


@cli.command()
def list_backends():
    """List available database backends.
    
    Shows which database backends are currently available based on installed drivers.
    """
    available = get_available_db_types()
    
    if not available:
        click.echo("No database backends available.")
        click.echo("\nInstall backends with: pip install glean-database[all]")
        return
    
    click.echo("Available database backends:\n")
    for db_type in available:
        click.echo(f"  • {db_type}")
    
    click.echo(f"\nTotal: {len(available)} backend(s) available")
    click.echo("\nTo install additional backends:")
    click.echo("  pip install glean-database[<backend>]")
    click.echo("\nExamples:")
    click.echo("  pip install glean-database[mysql]")
    click.echo("  pip install glean-database[postgres,mongo]")
    click.echo("  pip install glean-database[all]")


@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to JSON configuration file')
@click.option('--type', '-t', 'db_type', required=True,
              type=click.Choice(get_available_db_types(), case_sensitive=False),
              help='Database type')
@click.option('--directory', '-d', required=True, type=click.Path(exists=True),
              help='Directory containing .sql schema files')
@click.option('--dry-run', is_flag=True,
              help='Parse and validate SQL files without executing')
def init_schema(config: str, db_type: str, directory: str, dry_run: bool):
    """Initialize database schema from SQL files.
    
    Reads all .sql files from the specified directory (in alphabetical order)
    and executes them against the database. Automatically handles CREATE TABLE,
    CREATE INDEX, CREATE FUNCTION, and other DDL statements.
    
    Examples:
    
        # Initialize schema from SQL files
        glean-db init-schema -c config.json -t postgres -d ~/sql/postgres/
        
        # Dry run to validate SQL files
        glean-db init-schema -c config.json -t postgres -d ~/sql/ --dry-run
    
    Features:
    - Processes .sql files in alphabetical order (e.g., 01_tables.sql, 02_indexes.sql)
    - Skips tables that already exist (uses CREATE TABLE IF NOT EXISTS)
    - Handles multi-line statements, comments, and functions
    - Provides detailed execution results
    """
    async def run_init_schema():
        from database.core.schema import read_sql_files, apply_schema, format_results
        
        # Load configuration and create database
        db_config = load_config(config)
        db = create_database(db_type, db_config)
        
        try:
            # Read SQL files
            click.echo(f"Reading SQL files from: {directory}")
            try:
                sql_files = read_sql_files(directory)
            except FileNotFoundError as e:
                raise click.ClickException(str(e))
            except Exception as e:
                raise click.ClickException(f"Failed to read SQL files: {e}")
            
            if not sql_files:
                click.echo("⚠ No .sql files found in directory")
                return
            
            click.echo(f"Found {len(sql_files)} SQL file(s):")
            for filename, content in sql_files:
                click.echo(f"  • {filename}")
            
            if dry_run:
                click.echo("\n[DRY RUN MODE] - No changes will be made\n")
            
            # Connect to database
            click.echo(f"\nConnecting to {db_type} database...")
            await db.connect()
            if not db.is_connected:
                raise click.ClickException("Failed to connect to database")
            click.echo("✓ Connected")
            
            # Apply schema
            click.echo(f"\nApplying schema...")
            results = await apply_schema(db, sql_files, dry_run=dry_run)
            
            # Display results
            click.echo(format_results(results))
            
            # Exit with error code if there were failures
            if results['failed'] > 0:
                raise click.ClickException(f"Schema initialization completed with {results['failed']} error(s)")
            else:
                click.echo("\n✓ Schema initialization completed successfully!")
        
        finally:
            await db.disconnect()
    
    asyncio.run(run_init_schema())


@cli.command()
def show_config_example():
    """Show example configuration file format.
    
    Creates example configuration files for each database type.
    """
    examples = {
        'sqlite.json': {
            'database': './my_database.db',
            'cache': {
                'type': 'memory',
                'cleanup_interval': 60,
                'max_size': 1000
            }
        },
        'postgres.json': {
            'database': 'mydb',
            'host': 'localhost',
            'port': 5432,
            'username': 'postgres',
            'password': 'secret',
            'pool': {
                'min_size': 10,
                'max_size': 20,
                'max_queries': 50000,
                'max_inactive_lifetime': 300.0
            },
            'cache': {
                'type': 'redis',
                'host': 'localhost',
                'port': 6379,
                'db': 0
            }
        },
        'mongo.json': {
            'database': 'mydb',
            'host': 'localhost',
            'port': 27017,
            'username': 'admin',
            'password': 'secret',
            'pool': {
                'min_size': 10,
                'max_size': 100,
                'max_idle_time_ms': 300000
            }
        },
        'timescale.json': {
            'database': 'metrics_db',
            'host': 'localhost',
            'port': 5432,
            'username': 'postgres',
            'password': 'secret',
            'pool': {
                'min_size': 10,
                'max_size': 20,
                'max_queries': 50000,
                'max_inactive_lifetime': 300.0
            },
            'cache': {
                'type': 'memory',
                'cleanup_interval': 30,
                'max_size': 5000
            }
        },
        'mysql.json': {
            'database': 'mydb',
            'host': 'localhost',
            'port': 3306,
            'username': 'root',
            'password': 'secret',
            'pool': {
                'min_size': 1,
                'max_size': 10,
                'pool_recycle': 3600
            }
        },
        'mssql.json': {
            'database': 'mydb',
            'host': 'localhost',
            'port': 1433,
            'username': 'sa',
            'password': 'secret',
            'pool': {
                'min_size': 1,
                'max_size': 10,
                'timeout': 30
            }
        },
        'oracle.json': {
            'database': 'ORCL',
            'host': 'localhost',
            'port': 1521,
            'username': 'system',
            'password': 'secret',
            'service_name': 'ORCL',
            'pool': {
                'min_size': 1,
                'max_size': 10
            }
        }
    }
    
    click.echo("Example configuration files:\n")
    
    for filename, config in examples.items():
        click.echo(f"=== {filename} ===")
        click.echo(json.dumps(config, indent=2))
        click.echo()


if __name__ == '__main__':
    cli()
