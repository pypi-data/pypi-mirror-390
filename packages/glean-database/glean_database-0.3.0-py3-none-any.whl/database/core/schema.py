"""Schema management utilities for loading and applying SQL schemas.

Provides functionality to read SQL files from a directory and apply them to databases,
with support for creating new tables and modifying existing ones.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SQLStatement:
    """Represents a parsed SQL statement."""
    
    def __init__(self, statement_type: str, content: str, table_name: Optional[str] = None):
        """Initialize SQL statement.
        
        Args:
            statement_type: Type of statement (CREATE_TABLE, CREATE_INDEX, CREATE_FUNCTION, etc.)
            content: Full SQL statement text
            table_name: Table name if applicable
        """
        self.statement_type = statement_type
        self.content = content.strip()
        self.table_name = table_name
    
    def __repr__(self) -> str:
        table_info = f" ({self.table_name})" if self.table_name else ""
        return f"SQLStatement({self.statement_type}{table_info})"


def read_sql_files(directory: str) -> List[Tuple[str, str]]:
    """Read all .sql files from a directory.
    
    Args:
        directory: Path to directory containing SQL files
        
    Returns:
        List of tuples (filename, content) sorted by filename
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        PermissionError: If directory isn't readable
    """
    path = Path(directory).expanduser().resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")
    
    sql_files = sorted(path.glob("*.sql"))
    
    if not sql_files:
        logger.warning(f"No .sql files found in {directory}")
        return []
    
    results = []
    for sql_file in sql_files:
        try:
            content = sql_file.read_text(encoding='utf-8')
            results.append((sql_file.name, content))
            logger.info(f"Read SQL file: {sql_file.name} ({len(content)} bytes)")
        except Exception as e:
            logger.error(f"Failed to read {sql_file.name}: {e}")
            raise
    
    return results


def parse_sql_statements(sql_content: str) -> List[SQLStatement]:
    """Parse SQL content into individual statements.
    
    Handles multi-line statements, comments, and various SQL statement types.
    
    Args:
        sql_content: SQL text content
        
    Returns:
        List of SQLStatement objects
    """
    # Remove single-line comments (-- ...)
    lines = []
    for line in sql_content.split('\n'):
        # Remove comment part but keep the rest of the line
        comment_pos = line.find('--')
        if comment_pos >= 0:
            line = line[:comment_pos]
        lines.append(line)
    
    sql_content = '\n'.join(lines)
    
    # Remove multi-line comments (/* ... */)
    sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
    
    # Split by semicolons, but be careful about semicolons in strings or function bodies
    # This is a simplified approach - for production use a proper SQL parser
    statements = []
    current_statement = []
    in_function_body = False  # Tracks if we're inside a function body (between $$ delimiters)
    dollar_delimiter_count = 0
    in_string = False
    string_char = None
    
    for line in sql_content.split('\n'):
        line_stripped = line.strip()
        
        # Count $$ delimiters on this line
        dollar_delimiter_count += line.count('$$')
        
        # If we see odd number of $$, we're inside function body
        in_function_body = (dollar_delimiter_count % 2) == 1
        
        # Track string literals
        for char in line:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
        
        current_statement.append(line)
        
        # Check for end of statement (semicolon, not in string, not in function body)
        if line_stripped.endswith(';') and not in_string and not in_function_body:
            stmt_text = '\n'.join(current_statement)
            if stmt_text.strip():
                statements.append(_parse_statement(stmt_text))
            current_statement = []
            dollar_delimiter_count = 0  # Reset for next statement
    
    # Handle any remaining statement without semicolon
    if current_statement:
        stmt_text = '\n'.join(current_statement).strip()
        if stmt_text:
            statements.append(_parse_statement(stmt_text))
    
    return statements


def _parse_statement(statement: str) -> SQLStatement:
    """Parse a single SQL statement to determine its type and extract metadata.
    
    Args:
        statement: SQL statement text
        
    Returns:
        SQLStatement object
    """
    statement = statement.strip()
    statement_upper = statement.upper()
    
    # CREATE TABLE
    if 'CREATE TABLE' in statement_upper:
        match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', 
                         statement, re.IGNORECASE)
        table_name = match.group(1) if match else None
        return SQLStatement('CREATE_TABLE', statement, table_name)
    
    # CREATE INDEX
    elif 'CREATE INDEX' in statement_upper or 'CREATE UNIQUE INDEX' in statement_upper:
        return SQLStatement('CREATE_INDEX', statement)
    
    # CREATE TRIGGER (must come before FUNCTION check)
    elif 'CREATE TRIGGER' in statement_upper:
        return SQLStatement('CREATE_TRIGGER', statement)
    
    # CREATE FUNCTION/PROCEDURE (including OR REPLACE variant)
    elif 'CREATE' in statement_upper and ('FUNCTION' in statement_upper or 'PROCEDURE' in statement_upper):
        return SQLStatement('CREATE_FUNCTION', statement)
    
    # CREATE VIEW
    elif 'CREATE VIEW' in statement_upper:
        match = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)', 
                         statement, re.IGNORECASE)
        view_name = match.group(1) if match else None
        return SQLStatement('CREATE_VIEW', statement, view_name)
    
    # ALTER TABLE
    elif 'ALTER TABLE' in statement_upper:
        match = re.search(r'ALTER\s+TABLE\s+(\w+)', statement, re.IGNORECASE)
        table_name = match.group(1) if match else None
        return SQLStatement('ALTER_TABLE', statement, table_name)
    
    # DROP statements
    elif statement_upper.startswith('DROP'):
        return SQLStatement('DROP', statement)
    
    # INSERT/UPDATE/DELETE
    elif statement_upper.startswith(('INSERT', 'UPDATE', 'DELETE')):
        return SQLStatement('DML', statement)
    
    # Unknown
    else:
        return SQLStatement('UNKNOWN', statement)


async def apply_schema(db, sql_files: List[Tuple[str, str]], 
                       dry_run: bool = False) -> Dict[str, Any]:
    """Apply SQL schema files to a database.
    
    Executes SQL statements in order, handling errors gracefully.
    Prefers modifying existing tables over dropping and recreating.
    
    Args:
        db: Database instance (must be connected)
        sql_files: List of (filename, content) tuples
        dry_run: If True, parse but don't execute statements
        
    Returns:
        Dictionary with execution results:
        {
            'total_statements': int,
            'successful': int,
            'failed': int,
            'skipped': int,
            'errors': List[Dict[str, Any]]
        }
    """
    if not db.is_connected:
        raise RuntimeError("Database must be connected before applying schema")
    
    results = {
        'total_statements': 0,
        'successful': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }
    
    for filename, content in sql_files:
        logger.info(f"Processing {filename}")
        
        try:
            statements = parse_sql_statements(content)
            logger.info(f"Parsed {len(statements)} statements from {filename}")
            
            for stmt in statements:
                results['total_statements'] += 1
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would execute: {stmt}")
                    results['skipped'] += 1
                    continue
                
                try:
                    # Handle CREATE TABLE with IF NOT EXISTS
                    if stmt.statement_type == 'CREATE_TABLE':
                        # Check if table exists
                        if hasattr(db, 'table_exists'):
                            exists = await db.table_exists(stmt.table_name)
                            if exists:
                                logger.info(f"Table {stmt.table_name} already exists, skipping creation")
                                results['skipped'] += 1
                                continue
                    
                    # Execute the statement
                    await db.execute(stmt.content)
                    logger.info(f"✓ Executed: {stmt}")
                    results['successful'] += 1
                    
                except Exception as e:
                    # Log error but continue with other statements
                    error_info = {
                        'file': filename,
                        'statement': str(stmt),
                        'error': str(e)
                    }
                    results['errors'].append(error_info)
                    results['failed'] += 1
                    logger.error(f"✗ Failed to execute {stmt}: {e}")
        
        except Exception as e:
            # Error parsing the file
            logger.error(f"Failed to parse {filename}: {e}")
            results['errors'].append({
                'file': filename,
                'statement': 'FILE_PARSE_ERROR',
                'error': str(e)
            })
            results['failed'] += 1
    
    return results


def format_results(results: Dict[str, Any]) -> str:
    """Format schema application results as a readable string.
    
    Args:
        results: Results dictionary from apply_schema
        
    Returns:
        Formatted string
    """
    lines = [
        "\nSchema Application Results:",
        "=" * 50,
        f"Total statements: {results['total_statements']}",
        f"✓ Successful:     {results['successful']}",
        f"⊘ Skipped:        {results['skipped']}",
        f"✗ Failed:         {results['failed']}",
    ]
    
    if results['errors']:
        lines.append("\nErrors:")
        lines.append("-" * 50)
        for i, error in enumerate(results['errors'], 1):
            lines.append(f"\n{i}. File: {error['file']}")
            lines.append(f"   Statement: {error['statement']}")
            lines.append(f"   Error: {error['error']}")
    
    return '\n'.join(lines)
