"""Unit tests for schema management functionality."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile

from database.core.schema import (
    read_sql_files,
    parse_sql_statements,
    SQLStatement,
    apply_schema,
    format_results,
    _parse_statement
)


class TestReadSQLFiles:
    """Tests for read_sql_files function."""
    
    def test_read_sql_files_success(self):
        """Test reading SQL files from a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test SQL files
            (Path(tmpdir) / "01_tables.sql").write_text("CREATE TABLE users (id INT);")
            (Path(tmpdir) / "02_indexes.sql").write_text("CREATE INDEX idx_users ON users(id);")
            
            results = read_sql_files(tmpdir)
            
            assert len(results) == 2
            assert results[0][0] == "01_tables.sql"
            assert results[1][0] == "02_indexes.sql"
            assert "CREATE TABLE" in results[0][1]
            assert "CREATE INDEX" in results[1][1]
    
    def test_read_sql_files_empty_directory(self):
        """Test reading from directory with no SQL files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = read_sql_files(tmpdir)
            assert results == []
    
    def test_read_sql_files_nonexistent_directory(self):
        """Test reading from nonexistent directory."""
        with pytest.raises(FileNotFoundError):
            read_sql_files("/nonexistent/directory")
    
    def test_read_sql_files_not_a_directory(self):
        """Test passing a file instead of directory."""
        with tempfile.NamedTemporaryFile(suffix='.sql') as tmpfile:
            with pytest.raises(NotADirectoryError):
                read_sql_files(tmpfile.name)


class TestParseSQLStatements:
    """Tests for parse_sql_statements function."""
    
    def test_parse_create_table(self):
        """Test parsing CREATE TABLE statement."""
        sql = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
        statements = parse_sql_statements(sql)
        
        assert len(statements) == 1
        assert statements[0].statement_type == 'CREATE_TABLE'
        assert statements[0].table_name == 'users'
    
    def test_parse_create_table_if_not_exists(self):
        """Test parsing CREATE TABLE IF NOT EXISTS."""
        sql = "CREATE TABLE IF NOT EXISTS products (id INT);"
        statements = parse_sql_statements(sql)
        
        assert len(statements) == 1
        assert statements[0].statement_type == 'CREATE_TABLE'
        assert statements[0].table_name == 'products'
    
    def test_parse_create_index(self):
        """Test parsing CREATE INDEX statement."""
        sql = "CREATE INDEX idx_users_email ON users(email);"
        statements = parse_sql_statements(sql)
        
        assert len(statements) == 1
        assert statements[0].statement_type == 'CREATE_INDEX'
    
    def test_parse_create_function(self):
        """Test parsing CREATE FUNCTION statement."""
        sql = """
        CREATE OR REPLACE FUNCTION update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        statements = parse_sql_statements(sql)
        
        assert len(statements) == 1
        assert statements[0].statement_type == 'CREATE_FUNCTION'
    
    def test_parse_create_trigger(self):
        """Test parsing CREATE TRIGGER statement."""
        sql = "CREATE TRIGGER update_user_timestamp BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_timestamp();"
        statements = parse_sql_statements(sql)
        
        assert len(statements) == 1
        assert statements[0].statement_type == 'CREATE_TRIGGER'
    
    def test_parse_multiple_statements(self):
        """Test parsing multiple statements."""
        sql = """
        CREATE TABLE users (id INT);
        CREATE INDEX idx_users ON users(id);
        CREATE VIEW active_users AS SELECT * FROM users WHERE active = true;
        """
        statements = parse_sql_statements(sql)
        
        assert len(statements) == 3
        assert statements[0].statement_type == 'CREATE_TABLE'
        assert statements[1].statement_type == 'CREATE_INDEX'
        assert statements[2].statement_type == 'CREATE_VIEW'
    
    def test_parse_with_comments(self):
        """Test parsing SQL with comments."""
        sql = """
        -- This is a comment
        CREATE TABLE users ( -- inline comment
            id INT
        ); /* Multi-line
           comment */
        CREATE TABLE posts (id INT);
        """
        statements = parse_sql_statements(sql)
        
        assert len(statements) == 2
        assert all(s.statement_type == 'CREATE_TABLE' for s in statements)
    
    def test_parse_empty_string(self):
        """Test parsing empty SQL string."""
        statements = parse_sql_statements("")
        assert statements == []


class TestParseStatement:
    """Tests for _parse_statement function."""
    
    def test_parse_alter_table(self):
        """Test parsing ALTER TABLE statement."""
        stmt = _parse_statement("ALTER TABLE users ADD COLUMN email TEXT;")
        assert stmt.statement_type == 'ALTER_TABLE'
        assert stmt.table_name == 'users'
    
    def test_parse_drop_statement(self):
        """Test parsing DROP statement."""
        stmt = _parse_statement("DROP TABLE IF EXISTS users;")
        assert stmt.statement_type == 'DROP'
    
    def test_parse_insert_statement(self):
        """Test parsing INSERT statement."""
        stmt = _parse_statement("INSERT INTO users (id, name) VALUES (1, 'John');")
        assert stmt.statement_type == 'DML'
    
    def test_parse_unknown_statement(self):
        """Test parsing unknown statement type."""
        stmt = _parse_statement("GRANT ALL ON users TO admin;")
        assert stmt.statement_type == 'UNKNOWN'


class TestApplySchema:
    """Tests for apply_schema function."""
    
    @pytest.mark.asyncio
    async def test_apply_schema_success(self):
        """Test successfully applying schema."""
        # Create mock database
        mock_db = AsyncMock()
        mock_db.is_connected = True
        mock_db.execute = AsyncMock(return_value=1)
        mock_db.table_exists = AsyncMock(return_value=False)
        
        sql_files = [
            ("01_tables.sql", "CREATE TABLE users (id INT);"),
            ("02_indexes.sql", "CREATE INDEX idx_users ON users(id);")
        ]
        
        results = await apply_schema(mock_db, sql_files)
        
        assert results['total_statements'] == 2
        assert results['successful'] == 2
        assert results['failed'] == 0
        assert results['skipped'] == 0
        assert len(results['errors']) == 0
    
    @pytest.mark.asyncio
    async def test_apply_schema_table_exists(self):
        """Test applying schema when table already exists."""
        mock_db = AsyncMock()
        mock_db.is_connected = True
        mock_db.table_exists = AsyncMock(return_value=True)
        
        sql_files = [
            ("01_tables.sql", "CREATE TABLE users (id INT);")
        ]
        
        results = await apply_schema(mock_db, sql_files)
        
        assert results['total_statements'] == 1
        assert results['successful'] == 0
        assert results['skipped'] == 1
        assert results['failed'] == 0
    
    @pytest.mark.asyncio
    async def test_apply_schema_dry_run(self):
        """Test dry run mode."""
        mock_db = AsyncMock()
        mock_db.is_connected = True
        
        sql_files = [
            ("01_tables.sql", "CREATE TABLE users (id INT);")
        ]
        
        results = await apply_schema(mock_db, sql_files, dry_run=True)
        
        assert results['total_statements'] == 1
        assert results['skipped'] == 1
        assert results['successful'] == 0
        # Execute should not be called in dry run
        mock_db.execute.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_apply_schema_with_errors(self):
        """Test applying schema with execution errors."""
        mock_db = AsyncMock()
        mock_db.is_connected = True
        mock_db.execute = AsyncMock(side_effect=Exception("Execution failed"))
        mock_db.table_exists = AsyncMock(return_value=False)
        
        sql_files = [
            ("01_tables.sql", "CREATE TABLE users (id INT);")
        ]
        
        results = await apply_schema(mock_db, sql_files)
        
        assert results['total_statements'] == 1
        assert results['failed'] == 1
        assert results['successful'] == 0
        assert len(results['errors']) == 1
        assert results['errors'][0]['error'] == "Execution failed"
    
    @pytest.mark.asyncio
    async def test_apply_schema_not_connected(self):
        """Test applying schema when database not connected."""
        mock_db = AsyncMock()
        mock_db.is_connected = False
        
        sql_files = [("01_tables.sql", "CREATE TABLE users (id INT);")]
        
        with pytest.raises(RuntimeError, match="Database must be connected"):
            await apply_schema(mock_db, sql_files)
    
    @pytest.mark.asyncio
    async def test_apply_schema_parse_error(self):
        """Test handling SQL parse errors gracefully."""
        mock_db = AsyncMock()
        mock_db.is_connected = True
        
        # Malformed SQL that causes parsing issues
        sql_files = [
            ("bad.sql", "CREATE TABLE")  # Incomplete statement
        ]
        
        results = await apply_schema(mock_db, sql_files)
        
        # Should handle parsing gracefully
        assert results['total_statements'] >= 0


class TestFormatResults:
    """Tests for format_results function."""
    
    def test_format_results_success(self):
        """Test formatting successful results."""
        results = {
            'total_statements': 10,
            'successful': 10,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        output = format_results(results)
        
        assert "Total statements: 10" in output
        assert "✓ Successful:     10" in output
        assert "✗ Failed:         0" in output
    
    def test_format_results_with_errors(self):
        """Test formatting results with errors."""
        results = {
            'total_statements': 5,
            'successful': 3,
            'failed': 2,
            'skipped': 0,
            'errors': [
                {
                    'file': 'test.sql',
                    'statement': 'CREATE TABLE test',
                    'error': 'Table already exists'
                }
            ]
        }
        
        output = format_results(results)
        
        assert "✗ Failed:         2" in output
        assert "Errors:" in output
        assert "test.sql" in output
        assert "Table already exists" in output


class TestSQLStatement:
    """Tests for SQLStatement class."""
    
    def test_sql_statement_with_table_name(self):
        """Test SQLStatement with table name."""
        stmt = SQLStatement('CREATE_TABLE', 'CREATE TABLE users (id INT);', 'users')
        
        assert stmt.statement_type == 'CREATE_TABLE'
        assert stmt.table_name == 'users'
        assert 'CREATE TABLE' in stmt.content
        assert 'users' in repr(stmt)
    
    def test_sql_statement_without_table_name(self):
        """Test SQLStatement without table name."""
        stmt = SQLStatement('CREATE_INDEX', 'CREATE INDEX idx ON users(id);')
        
        assert stmt.statement_type == 'CREATE_INDEX'
        assert stmt.table_name is None
        assert 'CREATE_INDEX' in repr(stmt)
