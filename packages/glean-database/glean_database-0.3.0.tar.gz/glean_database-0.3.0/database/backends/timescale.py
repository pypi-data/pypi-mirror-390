from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from .postgres import PostgresDatabase
from ..core.cache import Cache

class TimescaleDatabase(PostgresDatabase):
    """TimescaleDB database implementation extending PostgreSQL with time-series capabilities."""
    
    async def create_hypertable(
        self,
        table_name: str,
        time_column: str,
        chunk_time_interval: Union[str, timedelta] = '1 day',
        if_not_exists: bool = True
    ) -> bool:
        """
        Convert a regular PostgreSQL table into a TimescaleDB hypertable.
        
        Args:
            table_name: Name of the table to convert
            time_column: Name of the timestamp column
            chunk_time_interval: Time interval for chunks
            if_not_exists: Whether to ignore if hypertable already exists
        
        Returns:
            True if successful, False otherwise
        """
        try:
            interval = (
                f"INTERVAL '{chunk_time_interval}'"
                if isinstance(chunk_time_interval, str)
                else f"INTERVAL '{chunk_time_interval.total_seconds()} seconds'"
            )
            
            create_stmt = f"""
                SELECT create_hypertable(
                    '{table_name}',
                    '{time_column}',
                    chunk_time_interval => {interval},
                    if_not_exists => {'TRUE' if if_not_exists else 'FALSE'}
                );
            """
            
            await self.execute(create_stmt)
            return True
        except Exception:
            return False

    async def add_retention_policy(
        self,
        table_name: str,
        interval: Union[str, timedelta]
    ) -> bool:
        """
        Add a retention policy to automatically drop old chunks.
        
        Args:
            table_name: Name of the hypertable
            interval: Age of data to retain
            
        Returns:
            True if successful, False otherwise
        """
        try:
            retention_interval = (
                f"INTERVAL '{interval}'"
                if isinstance(interval, str)
                else f"INTERVAL '{interval.total_seconds()} seconds'"
            )
            
            policy_stmt = f"""
                SELECT add_retention_policy(
                    '{table_name}',
                    {retention_interval}
                );
            """
            
            await self.execute(policy_stmt)
            return True
        except Exception:
            return False

    async def time_bucket_query(
        self,
        bucket_width: Union[str, timedelta],
        time_column: str,
        table_name: str,
        select_columns: List[str],
        aggregates: List[str],
        where_clause: Optional[str] = None,
        group_by: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a time bucket query for time-series aggregation.
        
        Args:
            bucket_width: Width of the time bucket
            time_column: Name of the timestamp column
            table_name: Name of the table to query
            select_columns: List of columns to select
            aggregates: List of aggregate functions
            where_clause: Optional WHERE clause
            group_by: Optional additional GROUP BY columns
            order_by: Optional ORDER BY clause
            limit: Optional LIMIT clause
            
        Returns:
            List of aggregated results
        """
        bucket_interval = (
            f"INTERVAL '{bucket_width}'"
            if isinstance(bucket_width, str)
            else f"INTERVAL '{bucket_width.total_seconds()} seconds'"
        )
        
        # Build column list
        columns = [
            f"time_bucket({bucket_interval}, {time_column}) as bucket",
            *select_columns,
            *aggregates
        ]
        
        # Build GROUP BY clause
        group_columns = ["bucket"]
        if group_by:
            group_columns.extend(group_by)
        
        # Construct query
        query = f"""
            SELECT {', '.join(columns)}
            FROM {table_name}
            {f'WHERE {where_clause}' if where_clause else ''}
            GROUP BY {', '.join(group_columns)}
            {f'ORDER BY {order_by}' if order_by else 'ORDER BY bucket'}
            {f'LIMIT {limit}' if limit else ''};
        """
        
        return await self.query(query)

    async def continuous_aggregate(
        self,
        view_name: str,
        hypertable: str,
        bucket_width: Union[str, timedelta],
        time_column: str,
        select_columns: List[str],
        aggregates: List[str],
        where_clause: Optional[str] = None,
        group_by: Optional[List[str]] = None,
        with_data: bool = True
    ) -> bool:
        """
        Create a continuous aggregate view.
        
        Args:
            view_name: Name of the continuous aggregate view
            hypertable: Name of the source hypertable
            bucket_width: Width of the time bucket
            time_column: Name of the timestamp column
            select_columns: List of columns to select
            aggregates: List of aggregate functions
            where_clause: Optional WHERE clause
            group_by: Optional additional GROUP BY columns
            with_data: Whether to immediately materialize historical data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            bucket_interval = (
                f"INTERVAL '{bucket_width}'"
                if isinstance(bucket_width, str)
                else f"INTERVAL '{bucket_width.total_seconds()} seconds'"
            )
            
            # Build column list
            columns = [
                f"time_bucket({bucket_interval}, {time_column}) as bucket",
                *select_columns,
                *aggregates
            ]
            
            # Build GROUP BY clause
            group_columns = ["bucket"]
            if group_by:
                group_columns.extend(group_by)
            
            # Construct query
            create_view = f"""
                CREATE MATERIALIZED VIEW {view_name}
                WITH (timescaledb.continuous) AS
                SELECT {', '.join(columns)}
                FROM {hypertable}
                {f'WHERE {where_clause}' if where_clause else ''}
                GROUP BY {', '.join(group_columns)}
                WITH {'DATA' if with_data else 'NO DATA'};
            """
            
            await self.execute(create_view)
            return True
        except Exception:
            return False

    async def add_compression_policy(
        self,
        table_name: str,
        compress_after: Union[str, timedelta],
        segment_by: Optional[List[str]] = None,
        orderby: Optional[str] = None,
    ) -> bool:
        """
        Add a compression policy to a hypertable.
        
        Args:
            table_name: Name of the hypertable
            compress_after: When to compress chunks
            segment_by: Optional columns to segment by
            orderby: Optional column to order by within segments
            
        Returns:
            True if successful, False otherwise
        """
        try:
            compress_interval = (
                f"INTERVAL '{compress_after}'"
                if isinstance(compress_after, str)
                else f"INTERVAL '{compress_after.total_seconds()} seconds'"
            )
            
            # Build segment by and order by clauses
            segment_clause = f", segment_by => '{{{', '.join(segment_by)}}}'" if segment_by else ''
            order_clause = f", orderby => '{orderby}'" if orderby else ''
            
            compress_stmt = f"""
                ALTER TABLE {table_name} SET (
                    timescaledb.compress = true,
                    timescaledb.compress_segmentby = {'$1' if segment_by else 'NULL'}
                );
                
                SELECT add_compression_policy(
                    '{table_name}',
                    {compress_interval}
                    {segment_clause}
                    {order_clause}
                );
            """
            
            await self.execute(compress_stmt)
            return True
        except Exception:
            return False