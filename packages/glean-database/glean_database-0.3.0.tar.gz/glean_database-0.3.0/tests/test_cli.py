import pytest
import json
import tempfile
import os
from click.testing import CliRunner
from database.__main__ import cli, load_config, create_database
from unittest.mock import patch, AsyncMock, MagicMock


def test_load_config_valid():
    """Test loading valid configuration file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {"database": "test.db", "host": "localhost"}
        json.dump(config, f)
        f.flush()
        
        try:
            result = load_config(f.name)
            assert result == config
        finally:
            os.unlink(f.name)


def test_load_config_file_not_found():
    """Test loading non-existent configuration file."""
    from click import ClickException
    
    with pytest.raises(ClickException, match="Configuration file not found"):
        load_config("/nonexistent/file.json")


def test_load_config_invalid_json():
    """Test loading invalid JSON configuration file."""
    from click import ClickException
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json}")
        f.flush()
        
        try:
            with pytest.raises(ClickException, match="Invalid JSON"):
                load_config(f.name)
        finally:
            os.unlink(f.name)


def test_create_database_sqlite():
    """Test creating SQLite database instance."""
    with patch.dict('database.__main__.AVAILABLE_DATABASES', {'sqlite': MagicMock()}) as mock_dbs:
        config = {"database": "test.db"}
        db = create_database("sqlite", config)
        mock_dbs['sqlite'].assert_called_once_with("test.db", cache=None)


def test_create_database_postgres_with_cache():
    """Test creating PostgreSQL database with Redis cache."""
    with patch.dict('database.__main__.AVAILABLE_DATABASES', {'postgres': MagicMock()}) as mock_dbs:
        with patch('database.__main__.RedisCache') as mock_cache:
            config = {
                "database": "testdb",
                "host": "localhost",
                "username": "user",
                "password": "pass",
                "cache": {
                    "type": "redis",
                    "host": "localhost",
                    "port": 6379,
                    "db": 0
                }
            }
            db = create_database("postgres", config.copy())
            mock_cache.assert_called_once()
            mock_dbs['postgres'].assert_called_once()


def test_create_database_mongo_with_pool():
    """Test creating MongoDB with pool configuration."""
    with patch.dict('database.__main__.AVAILABLE_DATABASES', {'mongo': MagicMock()}) as mock_dbs:
        config = {
            "database": "testdb",
            "host": "localhost",
            "pool": {
                "min_size": 5,
                "max_size": 50,
                "max_idle_time_ms": 60000
            }
        }
        db = create_database("mongo", config.copy())
        mock_dbs['mongo'].assert_called_once()
        call_kwargs = mock_dbs['mongo'].call_args[1]
        assert call_kwargs["min_pool_size"] == 5
        assert call_kwargs["max_pool_size"] == 50


def test_create_database_timescale():
    """Test creating TimescaleDB database instance."""
    with patch.dict('database.__main__.AVAILABLE_DATABASES', {'timescale': MagicMock()}) as mock_dbs:
        config = {"database": "metrics", "host": "localhost"}
        db = create_database("timescale", config)
        mock_dbs['timescale'].assert_called_once()


def test_create_database_unknown_type():
    """Test creating database with unknown type."""
    from click import ClickException
    
    with pytest.raises(ClickException, match="not available"):
        create_database("unknown", {})


def test_create_database_memory_cache():
    """Test creating database with in-memory cache."""
    with patch.dict('database.__main__.AVAILABLE_DATABASES', {'sqlite': MagicMock()}) as mock_dbs:
        with patch('database.__main__.InMemoryCache') as mock_cache:
            config = {
                "database": "test.db",
                "cache": {
                    "type": "memory",
                    "cleanup_interval": 30,
                    "max_size": 500
                }
            }
            db = create_database("sqlite", config.copy())
            mock_cache.assert_called_once_with(cleanup_interval=30, max_size=500)


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '0.1.0' in result.output


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Glean Database CLI' in result.output


def test_query_command_no_config():
    """Test query command without config file."""
    runner = CliRunner()
    result = runner.invoke(cli, ['query', '-c', '/nonexistent.json', '-t', 'sqlite', '-q', 'SELECT 1'])
    assert result.exit_code != 0
    assert 'does not exist' in result.output


def test_query_command_no_query():
    """Test query command without query string."""
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"database": "test.db"}, f)
        f.flush()
        
        try:
            result = runner.invoke(cli, ['query', '-c', f.name, '-t', 'sqlite'])
            assert result.exit_code != 0
            assert 'No query provided' in result.output
        finally:
            os.unlink(f.name)


def test_query_command_with_query():
    """Test query command with valid query."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"database": ":memory:"}, f)
        f.flush()
        
        try:
            with patch('database.__main__.SQLiteDatabase') as mock_db_class:
                mock_db = AsyncMock()
                mock_db.connect = AsyncMock(return_value=True)
                mock_db.is_connected = True
                mock_db.query = AsyncMock(return_value=[{"result": 1}])
                mock_db.disconnect = AsyncMock()
                mock_db_class.return_value = mock_db
                
                result = runner.invoke(cli, [
                    'query', '-c', f.name, '-t', 'sqlite',
                    '-q', 'SELECT 1 as result',
                    '-o', 'json'
                ])
                
                assert result.exit_code == 0
                assert 'result' in result.output
        finally:
            os.unlink(f.name)


def test_query_command_with_params():
    """Test query command with parameters."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"database": ":memory:"}, f)
        f.flush()
        
        try:
            mock_db = AsyncMock()
            mock_db.connect = AsyncMock(return_value=True)
            mock_db.is_connected = True
            mock_db.query = AsyncMock(return_value=[{"id": 1, "name": "Test"}])
            mock_db.disconnect = AsyncMock()
            
            with patch.dict('database.__main__.AVAILABLE_DATABASES', {'sqlite': MagicMock(return_value=mock_db)}):
                result = runner.invoke(cli, [
                    'query', '-c', f.name, '-t', 'sqlite',
                    '-q', 'SELECT * FROM users WHERE id = :id',
                    '-p', '{"id": 1}',
                    '-o', 'table'
                ])
                
                assert result.exit_code == 0
        finally:
            os.unlink(f.name)


def test_query_command_csv_output():
    """Test query command with CSV output."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"database": ":memory:"}, f)
        f.flush()
        
        try:
            mock_db = AsyncMock()
            mock_db.connect = AsyncMock(return_value=True)
            mock_db.is_connected = True
            mock_db.query = AsyncMock(return_value=[
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ])
            mock_db.disconnect = AsyncMock()
            
            with patch.dict('database.__main__.AVAILABLE_DATABASES', {'sqlite': MagicMock(return_value=mock_db)}):
                result = runner.invoke(cli, [
                    'query', '-c', f.name, '-t', 'sqlite',
                    '-q', 'SELECT * FROM users',
                    '-o', 'csv'
                ])
                
                assert result.exit_code == 0
                assert 'id,name' in result.output
        finally:
            os.unlink(f.name)


def test_execute_command():
    """Test execute command."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"database": ":memory:"}, f)
        f.flush()
        
        try:
            with patch('database.__main__.SQLiteDatabase') as mock_db_class:
                mock_db = AsyncMock()
                mock_db.connect = AsyncMock(return_value=True)
                mock_db.is_connected = True
                mock_db.execute = AsyncMock(return_value=1)
                mock_db.disconnect = AsyncMock()
                mock_db_class.return_value = mock_db
                
                result = runner.invoke(cli, [
                    'execute', '-c', f.name, '-t', 'sqlite',
                    '-s', 'CREATE TABLE test (id INT)'
                ])
                
                assert result.exit_code == 0
                assert 'executed successfully' in result.output
        finally:
            os.unlink(f.name)


def test_execute_command_no_statement():
    """Test execute command without statement."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"database": "test.db"}, f)
        f.flush()
        
        try:
            result = runner.invoke(cli, ['execute', '-c', f.name, '-t', 'sqlite'])
            assert result.exit_code != 0
            assert 'No statement provided' in result.output
        finally:
            os.unlink(f.name)


def test_test_connection_success():
    """Test test-connection command with successful connection."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"database": ":memory:"}, f)
        f.flush()
        
        try:
            with patch('database.__main__.SQLiteDatabase') as mock_db_class:
                mock_db = AsyncMock()
                mock_db.connect = AsyncMock(return_value=True)
                mock_db.is_connected = True
                mock_db.disconnect = AsyncMock()
                mock_db_class.return_value = mock_db
                
                result = runner.invoke(cli, [
                    'test-connection', '-c', f.name, '-t', 'sqlite'
                ])
                
                assert result.exit_code == 0
                assert 'Connection successful' in result.output
        finally:
            os.unlink(f.name)


def test_test_connection_failure():
    """Test test-connection command with failed connection."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"database": "test.db"}, f)
        f.flush()
        
        try:
            mock_db = AsyncMock()
            mock_db.connect = AsyncMock(return_value=True)
            mock_db.is_connected = False  # Connection failed
            mock_db.disconnect = AsyncMock()
            
            with patch.dict('database.__main__.AVAILABLE_DATABASES', {'sqlite': MagicMock(return_value=mock_db)}):
                result = runner.invoke(cli, [
                    'test-connection', '-c', f.name, '-t', 'sqlite'
                ])
                
                assert result.exit_code != 0
                assert 'Connection failed' in result.output
        finally:
            os.unlink(f.name)


def test_list_backends():
    """Test list-backends command."""
    runner = CliRunner()
    
    with patch('database.__main__.get_available_db_types', return_value=['mongo', 'postgres', 'sqlite']):
        result = runner.invoke(cli, ['list-backends'])
        
        assert result.exit_code == 0
        assert 'Available database backends' in result.output
        assert '• mongo' in result.output
        assert '• postgres' in result.output
        assert '• sqlite' in result.output
        assert 'Total: 3 backend(s) available' in result.output


def test_list_backends_none_available():
    """Test list-backends command when no backends are available."""
    runner = CliRunner()
    
    with patch('database.__main__.get_available_db_types', return_value=[]):
        result = runner.invoke(cli, ['list-backends'])
        
        assert result.exit_code == 0
        assert 'No database backends available' in result.output
        assert 'pip install glean-database[all]' in result.output


def test_load_command():
    """Test load command with valid JSON data."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
        json.dump({"database": ":memory:"}, config_f)
        config_f.flush()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as data_f:
            test_data = [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ]
            json.dump(test_data, data_f)
            data_f.flush()
            
            try:
                mock_db = AsyncMock()
                mock_db.connect = AsyncMock(return_value=True)
                mock_db.is_connected = True
                mock_db.execute = AsyncMock(return_value=1)
                mock_db.disconnect = AsyncMock()
                
                with patch.dict('database.__main__.AVAILABLE_DATABASES', {'sqlite': MagicMock(return_value=mock_db)}):
                    result = runner.invoke(cli, [
                        'load', '-c', config_f.name, '-t', 'sqlite',
                        '--table', 'test_table', '-f', data_f.name
                    ])
                    
                    assert result.exit_code == 0
                    assert 'Successfully loaded' in result.output
            finally:
                os.unlink(config_f.name)
                os.unlink(data_f.name)


def test_load_command_invalid_json():
    """Test load command with invalid JSON data file."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
        json.dump({"database": ":memory:"}, config_f)
        config_f.flush()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as data_f:
            data_f.write("{invalid json}")
            data_f.flush()
            
            try:
                result = runner.invoke(cli, [
                    'load', '-c', config_f.name, '-t', 'sqlite',
                    '--table', 'test_table', '-f', data_f.name
                ])
                
                assert result.exit_code != 0
                assert 'Invalid JSON' in result.output
            finally:
                os.unlink(config_f.name)
                os.unlink(data_f.name)


def test_load_command_not_array():
    """Test load command with non-array JSON."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
        json.dump({"database": ":memory:"}, config_f)
        config_f.flush()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as data_f:
            json.dump({"not": "an array"}, data_f)
            data_f.flush()
            
            try:
                result = runner.invoke(cli, [
                    'load', '-c', config_f.name, '-t', 'sqlite',
                    '--table', 'test_table', '-f', data_f.name
                ])
                
                assert result.exit_code != 0
                assert 'must contain an array' in result.output
            finally:
                os.unlink(config_f.name)
                os.unlink(data_f.name)


def test_show_config_example():
    """Test show-config-example command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['show-config-example'])
    
    assert result.exit_code == 0
    assert 'sqlite.json' in result.output
    assert 'postgres.json' in result.output
    assert 'mongo.json' in result.output
    assert 'timescale.json' in result.output
    assert 'mysql.json' in result.output
    assert 'mssql.json' in result.output
    assert 'oracle.json' in result.output
