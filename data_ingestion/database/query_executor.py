"""
Safe SQL query executor for Data Ingestion Agent.

Provides secure SQL execution with:
- Parameterized queries only
- Table name validation
- Query timeout enforcement
- Result size limiting
"""

import logging
import re
import time
import uuid
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Valid table name pattern: data_{32-char-hex}
TABLE_NAME_PATTERN = re.compile(r'^data_[a-f0-9]{32}$')

# Maximum result rows to prevent memory issues
MAX_RESULT_ROWS = 10000

# Query timeout in seconds
DEFAULT_QUERY_TIMEOUT = 30


class QueryExecutionError(Exception):
    """Raised when query execution fails."""
    pass


class InvalidTableNameError(Exception):
    """Raised when table name is invalid."""
    pass


class QueryExecutor:
    """
    Safe SQL query executor with security validations.

    Ensures all queries:
    - Target only data_* tables
    - Use parameterized values
    - Have enforced timeouts
    - Return limited result sets
    """

    def __init__(
        self,
        db_session: AsyncSession,
        timeout_seconds: int = DEFAULT_QUERY_TIMEOUT,
        max_rows: int = MAX_RESULT_ROWS
    ):
        """
        Initialize query executor.

        Args:
            db_session: SQLAlchemy async session
            timeout_seconds: Query timeout
            max_rows: Maximum result rows
        """
        self._session = db_session
        self._timeout = timeout_seconds
        self._max_rows = max_rows

    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """
        Validate that table name matches expected pattern.

        Args:
            table_name: Table name to validate

        Returns:
            True if valid, False otherwise
        """
        return bool(TABLE_NAME_PATTERN.match(table_name))

    async def create_data_table(
        self,
        table_name: str,
        columns: List[Dict[str, Any]]
    ) -> bool:
        """
        Create a data table for a session.

        Args:
            table_name: Table name (must match pattern)
            columns: Column definitions from CSV schema

        Returns:
            True if created successfully

        Raises:
            InvalidTableNameError: If table name is invalid
            QueryExecutionError: If creation fails
        """
        if not self.validate_table_name(table_name):
            raise InvalidTableNameError(f"Invalid table name: {table_name}")

        # Build column definitions
        col_defs = []
        for col in columns:
            col_name = self._sanitize_column_name(col["name"])
            pg_type = self._map_dtype_to_postgres(col.get("dtype", "object"))
            nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
            col_defs.append(f'"{col_name}" {pg_type} {nullable}')

        # Add internal row ID
        col_defs.insert(0, "_row_id SERIAL PRIMARY KEY")

        create_sql = f'''
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                {", ".join(col_defs)}
            )
        '''

        try:
            start_time = time.time()
            await self._session.execute(text(create_sql))
            duration_ms = (time.time() - start_time) * 1000

            logger.info(f"Created table {table_name} with {len(columns)} columns in {duration_ms:.2f}ms")
            return True

        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            raise QueryExecutionError(f"Table creation failed: {e}")

    async def insert_data(
        self,
        table_name: str,
        columns: List[str],
        rows: List[List[Any]]
    ) -> int:
        """
        Bulk insert data into table.

        Args:
            table_name: Target table
            columns: Column names
            rows: Data rows

        Returns:
            Number of rows inserted

        Raises:
            InvalidTableNameError: If table name invalid
            QueryExecutionError: If insert fails
        """
        if not self.validate_table_name(table_name):
            raise InvalidTableNameError(f"Invalid table name: {table_name}")

        if not rows:
            return 0

        # Sanitize column names
        safe_columns = [self._sanitize_column_name(c) for c in columns]

        # Build parameterized INSERT
        col_list = ", ".join(f'"{c}"' for c in safe_columns)
        placeholders = ", ".join(f":p{i}" for i in range(len(columns)))

        insert_sql = f'INSERT INTO "{table_name}" ({col_list}) VALUES ({placeholders})'

        try:
            start_time = time.time()

            # Batch insert
            batch_size = 1000
            total_inserted = 0

            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                params_list = []

                for row in batch:
                    params = {f"p{j}": self._convert_value(v) for j, v in enumerate(row)}
                    params_list.append(params)

                for params in params_list:
                    await self._session.execute(text(insert_sql), params)
                    total_inserted += 1

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Inserted {total_inserted} rows into {table_name} in {duration_ms:.2f}ms")

            return total_inserted

        except Exception as e:
            logger.error(f"Failed to insert data into {table_name}: {e}")
            raise QueryExecutionError(f"Data insertion failed: {e}")

    async def execute_select(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Execute a SELECT query on a data table.

        Args:
            table_name: Table to query
            columns: Columns to select (None = all)
            where_clause: WHERE condition (parameterized)
            params: Query parameters
            order_by: ORDER BY clause
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of (rows as dicts, total count)

        Raises:
            InvalidTableNameError: If table name invalid
            QueryExecutionError: If query fails
        """
        if not self.validate_table_name(table_name):
            raise InvalidTableNameError(f"Invalid table name: {table_name}")

        # Enforce max rows
        effective_limit = min(limit or self._max_rows, self._max_rows)

        # Build column list
        if columns:
            safe_cols = [f'"{self._sanitize_column_name(c)}"' for c in columns]
            col_list = ", ".join(safe_cols)
        else:
            col_list = "*"

        # Build query
        query_parts = [f'SELECT {col_list} FROM "{table_name}"']

        if where_clause:
            query_parts.append(f"WHERE {where_clause}")

        if order_by:
            query_parts.append(f"ORDER BY {order_by}")

        query_parts.append(f"LIMIT {effective_limit} OFFSET {offset}")

        query_sql = " ".join(query_parts)

        # Also get total count
        count_parts = [f'SELECT COUNT(*) as total FROM "{table_name}"']
        if where_clause:
            count_parts.append(f"WHERE {where_clause}")
        count_sql = " ".join(count_parts)

        try:
            start_time = time.time()

            # Execute count query
            count_result = await self._session.execute(
                text(count_sql),
                params or {}
            )
            total_count = count_result.scalar() or 0

            # Execute main query
            result = await self._session.execute(
                text(query_sql),
                params or {}
            )

            rows = [dict(row._mapping) for row in result.fetchall()]

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"SELECT from {table_name}: {len(rows)} rows of {total_count} total in {duration_ms:.2f}ms"
            )

            return rows, total_count

        except Exception as e:
            logger.error(f"Failed to execute SELECT on {table_name}: {e}")
            raise QueryExecutionError(f"Query execution failed: {e}")

    async def execute_aggregation(
        self,
        table_name: str,
        aggregations: List[Dict[str, str]],
        group_by: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute aggregation query.

        Args:
            table_name: Table to query
            aggregations: List of {func: "SUM", column: "revenue", alias: "total_revenue"}
            group_by: Columns to group by
            where_clause: WHERE condition
            params: Query parameters

        Returns:
            Aggregation results as list of dicts
        """
        if not self.validate_table_name(table_name):
            raise InvalidTableNameError(f"Invalid table name: {table_name}")

        # Build aggregation expressions
        agg_exprs = []
        for agg in aggregations:
            func = agg.get("func", "COUNT").upper()
            if func not in ("COUNT", "SUM", "AVG", "MIN", "MAX", "STDDEV", "VARIANCE"):
                raise QueryExecutionError(f"Invalid aggregation function: {func}")

            col = self._sanitize_column_name(agg.get("column", "*"))
            alias = self._sanitize_column_name(agg.get("alias", f"{func}_{col}"))

            if col == "*":
                agg_exprs.append(f'{func}(*) AS "{alias}"')
            else:
                agg_exprs.append(f'{func}("{col}") AS "{alias}"')

        # Build group by columns
        if group_by:
            safe_group = [f'"{self._sanitize_column_name(c)}"' for c in group_by]
            group_cols = ", ".join(safe_group)
            select_cols = f'{group_cols}, {", ".join(agg_exprs)}'
            group_clause = f"GROUP BY {group_cols}"
        else:
            select_cols = ", ".join(agg_exprs)
            group_clause = ""

        # Build query
        query_parts = [f'SELECT {select_cols} FROM "{table_name}"']

        if where_clause:
            query_parts.append(f"WHERE {where_clause}")

        if group_clause:
            query_parts.append(group_clause)

        query_parts.append(f"LIMIT {self._max_rows}")

        query_sql = " ".join(query_parts)

        try:
            start_time = time.time()

            result = await self._session.execute(
                text(query_sql),
                params or {}
            )

            rows = [dict(row._mapping) for row in result.fetchall()]

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Aggregation on {table_name}: {len(rows)} groups in {duration_ms:.2f}ms")

            return rows

        except Exception as e:
            logger.error(f"Failed aggregation on {table_name}: {e}")
            raise QueryExecutionError(f"Aggregation failed: {e}")

    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get table information (columns, row count).

        Args:
            table_name: Table to inspect

        Returns:
            Dict with columns and row_count
        """
        if not self.validate_table_name(table_name):
            raise InvalidTableNameError(f"Invalid table name: {table_name}")

        try:
            # Get columns
            col_query = text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """)

            result = await self._session.execute(col_query, {"table_name": table_name})
            columns = [
                {
                    "name": row.column_name,
                    "type": row.data_type,
                    "nullable": row.is_nullable == "YES"
                }
                for row in result.fetchall()
            ]

            # Get row count
            count_result = await self._session.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            )
            row_count = count_result.scalar() or 0

            return {
                "table_name": table_name,
                "columns": columns,
                "row_count": row_count
            }

        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            raise QueryExecutionError(f"Table info query failed: {e}")

    @staticmethod
    def _sanitize_column_name(name: str) -> str:
        """Sanitize column name to prevent SQL injection."""
        # Remove any non-alphanumeric characters except underscore
        safe_name = re.sub(r'[^\w]', '_', name)
        # Ensure it doesn't start with a number
        if safe_name and safe_name[0].isdigit():
            safe_name = f"col_{safe_name}"
        return safe_name[:63]  # PostgreSQL identifier limit

    @staticmethod
    def _map_dtype_to_postgres(dtype: str) -> str:
        """Map pandas/semantic dtype to PostgreSQL type."""
        dtype_lower = str(dtype).lower()

        # Handle semantic types from CSVHandler
        if dtype_lower == "numeric":
            return "DOUBLE PRECISION"
        elif dtype_lower in ("categorical", "text"):
            return "TEXT"
        # Handle pandas dtypes
        elif "int" in dtype_lower:
            return "BIGINT"
        elif "float" in dtype_lower:
            return "DOUBLE PRECISION"
        elif "bool" in dtype_lower:
            return "BOOLEAN"
        elif "datetime" in dtype_lower or "timestamp" in dtype_lower:
            return "TIMESTAMP"
        elif "date" in dtype_lower:
            return "DATE"
        else:
            return "TEXT"

    @staticmethod
    def _convert_value(value: Any) -> Any:
        """Convert value for PostgreSQL insertion."""
        import pandas as pd
        import numpy as np

        if pd.isna(value) or value is None:
            return None
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        if isinstance(value, np.bool_):
            return bool(value)
        return value
