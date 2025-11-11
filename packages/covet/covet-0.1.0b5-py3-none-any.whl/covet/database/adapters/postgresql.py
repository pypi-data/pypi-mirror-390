"""
PostgreSQL Database Adapter

Production-ready PostgreSQL adapter using asyncpg for high-performance async operations.
Supports connection pooling, transactions, prepared statements, and PostgreSQL-specific features.
"""

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple, Union

import asyncpg

from ..security.sql_validator import (
    DatabaseDialect,
    InvalidIdentifierError,
    validate_schema_name,
    validate_table_name,
)
from .base import DatabaseAdapter

logger = logging.getLogger(__name__)


class PostgreSQLAdapter(DatabaseAdapter):
    """
    High-performance PostgreSQL database adapter using asyncpg.

    Features:
    - Async/await support with asyncpg
    - Connection pooling (5-100 connections)
    - Automatic retries with exponential backoff
    - Prepared statement caching
    - Transaction management with savepoints
    - PostgreSQL-specific types (JSON, UUID, Arrays, etc.)
    - Query result streaming for large datasets
    - Comprehensive error handling

    Example:
        adapter = PostgreSQLAdapter(
            host='localhost',
            port=5432,
            database='mydb',
            user='postgres',
            password='secret',
            min_pool_size=5,
            max_pool_size=20
        )
        await adapter.connect()
        result = await adapter.execute("SELECT * FROM users WHERE id = $1", (1,))
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: str = "",
        min_pool_size: int = 5,
        max_pool_size: int = 20,
        command_timeout: float = 60.0,
        query_timeout: float = 30.0,
        statement_cache_size: int = 100,
        max_cached_statement_lifetime: int = 300,
        max_cacheable_statement_size: int = 1024 * 15,
        ssl: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize PostgreSQL adapter.

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Username
            password: Password
            min_pool_size: Minimum pool connections (default: 5)
            max_pool_size: Maximum pool connections (default: 20)
            command_timeout: Timeout for commands in seconds
            query_timeout: Timeout for queries in seconds
            statement_cache_size: Number of prepared statements to cache
            max_cached_statement_lifetime: Max lifetime of cached statements (seconds)
            max_cacheable_statement_size: Max size of cacheable statement (bytes)
            ssl: SSL mode ('require', 'prefer', 'allow', 'disable')
            **kwargs: Additional asyncpg connection parameters
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.command_timeout = command_timeout
        self.query_timeout = query_timeout
        self.statement_cache_size = statement_cache_size
        self.max_cached_statement_lifetime = max_cached_statement_lifetime
        self.max_cacheable_statement_size = max_cacheable_statement_size
        self.ssl = ssl
        self.extra_params = kwargs

        self.pool: Optional[asyncpg.Pool] = None
        self._connected = False

    async def connect(self) -> None:
        """
        Establish connection pool to PostgreSQL database.

        Creates a connection pool with configured min/max sizes.
        Includes retry logic for transient connection failures.

        Raises:
            asyncpg.PostgresError: If connection fails after retries
        """
        if self._connected and self.pool:
            return

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Connecting to PostgreSQL: {self.user}@{self.host}:{self.port}/{self.database} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                # Prepare connection parameters
                conn_params = {
                    "host": self.host,
                    "port": self.port,
                    "database": self.database,
                    "user": self.user,
                    "password": self.password,
                    "min_size": self.min_pool_size,
                    "max_size": self.max_pool_size,
                    "command_timeout": self.command_timeout,
                    "statement_cache_size": self.statement_cache_size,
                    "max_cached_statement_lifetime": self.max_cached_statement_lifetime,
                    "max_cacheable_statement_size": self.max_cacheable_statement_size,
                }

                # Add SSL configuration if specified
                if self.ssl:
                    conn_params["ssl"] = self.ssl

                # Add extra parameters
                conn_params.update(self.extra_params)

                # Create connection pool
                self.pool = await asyncpg.create_pool(**conn_params)

                # Test connection
                async with self.pool.acquire() as conn:
                    await conn.execute("SELECT 1")

                self._connected = True
                logger.info(
                    f"Connected to PostgreSQL: {self.database} "
                    f"(pool size: {self.min_pool_size}-{self.max_pool_size})"
                )
                return

            except asyncpg.PostgresError as e:
                logger.warning(f"PostgreSQL connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to PostgreSQL after {max_retries} attempts")
                    raise

    async def disconnect(self) -> None:
        """
        Close all connections in the pool.

        Gracefully closes all active connections and releases resources.
        """
        if self.pool:
            await self.pool.close()
            self.pool = None
            self._connected = False
            logger.info(f"Disconnected from PostgreSQL: {self.database}")

    async def execute(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Execute a SQL command (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query with $1, $2... placeholders
            params: Query parameters
            timeout: Query timeout in seconds (overrides default)

        Returns:
            Command result string (e.g., "INSERT 0 1", "UPDATE 5")

        Example:
            result = await adapter.execute(
                "INSERT INTO users (name, email) VALUES ($1, $2)",
                ("Alice", "alice@example.com")
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.command_timeout

        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *params, timeout=timeout)
                logger.debug(f"Executed: {query[:100]}... -> {result}")
                return result

        except asyncpg.PostgresError as e:
            logger.error(f"Execute failed: {query[:100]}... Error: {e}")
            raise

    async def fetch_one(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row as a dictionary.

        Args:
            query: SQL query with $1, $2... placeholders
            params: Query parameters
            timeout: Query timeout in seconds

        Returns:
            Dictionary with column names as keys, or None if no rows

        Example:
            user = await adapter.fetch_one(
                "SELECT * FROM users WHERE id = $1",
                (42,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.query_timeout

        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, *params, timeout=timeout)
                if row:
                    result = dict(row)
                    logger.debug(f"Fetched one: {query[:100]}... -> 1 row")
                    return result
                logger.debug(f"Fetched one: {query[:100]}... -> None")
                return None

        except asyncpg.PostgresError as e:
            logger.error(f"Fetch one failed: {query[:100]}... Error: {e}")
            raise

    async def fetch_all(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows as list of dictionaries.

        Args:
            query: SQL query with $1, $2... placeholders
            params: Query parameters
            timeout: Query timeout in seconds

        Returns:
            List of dictionaries with column names as keys

        Example:
            users = await adapter.fetch_all(
                "SELECT * FROM users WHERE active = $1",
                (True,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.query_timeout

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params, timeout=timeout)
                result = [dict(row) for row in rows]
                logger.debug(f"Fetched all: {query[:100]}... -> {len(result)} rows")
                return result

        except asyncpg.PostgresError as e:
            logger.error(f"Fetch all failed: {query[:100]}... Error: {e}")
            raise

    async def fetch_value(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
        column: int = 0,
    ) -> Optional[Any]:
        """
        Fetch a single value from the first row.

        Args:
            query: SQL query
            params: Query parameters
            timeout: Query timeout
            column: Column index (default: 0 for first column)

        Returns:
            Single value or None

        Example:
            count = await adapter.fetch_value("SELECT COUNT(*) FROM users")
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.query_timeout

        try:
            async with self.pool.acquire() as conn:
                value = await conn.fetchval(query, *params, column=column, timeout=timeout)
                logger.debug(f"Fetched value: {query[:100]}... -> {value}")
                return value

        except asyncpg.PostgresError as e:
            logger.error(f"Fetch value failed: {query[:100]}... Error: {e}")
            raise

    @asynccontextmanager
    async def transaction(self, isolation: str = "read_committed"):
        """
        Context manager for database transactions.

        Args:
            isolation: Transaction isolation level
                - 'read_uncommitted'
                - 'read_committed' (default)
                - 'repeatable_read'
                - 'serializable'

        Yields:
            asyncpg.Connection: Database connection within transaction

        Example:
            async with adapter.transaction() as conn:
                await conn.execute("INSERT INTO users ...")
                await conn.execute("UPDATE accounts ...")
                # Automatically commits on success, rolls back on exception
        """
        if not self._connected or not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.transaction(isolation=isolation):
                yield conn

    async def execute_many(
        self,
        query: str,
        params_list: List[Union[Tuple, List]],
        timeout: Optional[float] = None,
    ) -> None:
        """
        Execute the same query with multiple parameter sets.

        Uses executemany for efficient batch operations.

        Args:
            query: SQL query with placeholders
            params_list: List of parameter tuples
            timeout: Query timeout

        Example:
            await adapter.execute_many(
                "INSERT INTO users (name, email) VALUES ($1, $2)",
                [
                    ("Alice", "alice@example.com"),
                    ("Bob", "bob@example.com"),
                    ("Charlie", "charlie@example.com"),
                ]
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        timeout = timeout or self.command_timeout

        try:
            async with self.pool.acquire() as conn:
                await conn.executemany(query, params_list, timeout=timeout)
                logger.debug(f"Executed many: {query[:100]}... with {len(params_list)} param sets")

        except asyncpg.PostgresError as e:
            logger.error(f"Execute many failed: {query[:100]}... Error: {e}")
            raise

    async def copy_records_to_table(
        self,
        table_name: str,
        records: List[Tuple],
        columns: Optional[List[str]] = None,
        schema_name: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Efficiently bulk insert records using COPY protocol.

        Much faster than INSERT for large datasets (10-100x faster).

        SECURITY: Validates table and schema names to prevent SQL injection.

        Args:
            table_name: Target table name (will be validated)
            records: List of tuples with record data
            columns: Column names (optional, uses all columns if None)
            schema_name: Schema name (optional, will be validated)
            timeout: Operation timeout

        Returns:
            COPY result string

        Raises:
            ValueError: If table/schema name is invalid

        Example:
            result = await adapter.copy_records_to_table(
                'users',
                [
                    (1, 'Alice', 'alice@example.com'),
                    (2, 'Bob', 'bob@example.com'),
                ],
                columns=['id', 'name', 'email']
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        # SECURITY: Validate table and schema names
        try:
            validated_table = validate_table_name(table_name, DatabaseDialect.POSTGRESQL)
            validated_schema = None
            if schema_name:
                validated_schema = validate_schema_name(schema_name, DatabaseDialect.POSTGRESQL)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table or schema name: {e}")

        timeout = timeout or self.command_timeout * 5  # COPY can take longer

        try:
            async with self.pool.acquire() as conn:
                result = await conn.copy_records_to_table(
                    validated_table,
                    records=records,
                    columns=columns,
                    schema_name=validated_schema,
                    timeout=timeout,
                )
                logger.info(f"COPY {len(records)} records to {table_name}: {result}")
                return result

        except asyncpg.PostgresError as e:
            logger.error(f"COPY to {table_name} failed: {e}")
            raise

    async def stream_query(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        chunk_size: int = 1000,
        timeout: Optional[float] = None,
    ):
        """
        Stream query results in chunks for large datasets.

        Memory-efficient for processing millions of rows.

        Args:
            query: SQL query
            params: Query parameters
            chunk_size: Number of rows per chunk
            timeout: Query timeout

        Yields:
            List of dictionaries for each chunk

        Example:
            async for chunk in adapter.stream_query(
                "SELECT * FROM large_table",
                chunk_size=1000
            ):
                for row in chunk:
                    process_row(row)
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        timeout = timeout or self.query_timeout * 10  # Streaming can take longer

        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    cursor = await conn.cursor(query, *params, timeout=timeout)

                    while True:
                        rows = await cursor.fetch(chunk_size)
                        if not rows:
                            break
                        yield [dict(row) for row in rows]

        except asyncpg.PostgresError as e:
            logger.error(f"Stream query failed: {query[:100]}... Error: {e}")
            raise

    async def get_table_info(self, table_name: str, schema: str = "public") -> List[Dict[str, Any]]:
        """
        Get column information for a table.

        Args:
            table_name: Table name
            schema: Schema name (default: 'public')

        Returns:
            List of column info dictionaries with keys:
                - column_name
                - data_type
                - is_nullable
                - column_default
                - character_maximum_length
        """
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
        """
        return await self.fetch_all(query, (schema, table_name))

    async def table_exists(self, table_name: str, schema: str = "public") -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Table name
            schema: Schema name

        Returns:
            True if table exists
        """
        query = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = $1 AND table_name = $2
            )
        """
        return await self.fetch_value(query, (schema, table_name))

    async def get_version(self) -> str:
        """
        Get PostgreSQL server version.

        Returns:
            Version string (e.g., "PostgreSQL 14.5")
        """
        return await self.fetch_value("SELECT version()")

    async def get_pool_stats(self) -> Dict[str, int]:
        """
        Get connection pool statistics.

        Returns:
            Dictionary with pool statistics:
                - size: Current pool size
                - free: Number of free connections
                - used: Number of connections in use
        """
        if not self.pool:
            return {"size": 0, "free": 0, "used": 0}

        return {
            "size": self.pool.get_size(),
            "free": self.pool.get_idle_size(),
            "used": self.pool.get_size() - self.pool.get_idle_size(),
        }

    async def bulk_create(
        self,
        table: str,
        records: List[Dict[str, Any]],
        ignore_duplicates: bool = False,
        schema: str = "public",
    ) -> int:
        """
        Bulk insert multiple records efficiently using PostgreSQL's COPY protocol or INSERT.

        For datasets with 1000+ records, uses the COPY protocol for maximum performance.
        For smaller datasets or when ignore_duplicates=True, uses INSERT statements.

        Args:
            table: Table name (will be validated)
            records: List of dictionaries with column-value pairs
            ignore_duplicates: If True, use INSERT ... ON CONFLICT DO NOTHING
            schema: Schema name (default: 'public', will be validated)

        Returns:
            Number of rows inserted

        Raises:
            ValueError: If table/schema name is invalid
            asyncpg.PostgresError: If insert operation fails

        Example:
            # Simple bulk insert
            rows = await adapter.bulk_create(
                'users',
                [
                    {'name': 'Alice', 'email': 'alice@example.com', 'age': 28},
                    {'name': 'Bob', 'email': 'bob@example.com', 'age': 35},
                    {'name': 'Charlie', 'email': 'charlie@example.com', 'age': 42}
                ]
            )
            print(f"Inserted {rows} users")

            # Ignore duplicates (requires unique constraint)
            rows = await adapter.bulk_create(
                'products',
                [
                    {'sku': 'LAPTOP-001', 'name': 'Laptop Pro'},
                    {'sku': 'PHONE-001', 'name': 'Phone X'}
                ],
                ignore_duplicates=True
            )
        """
        if not records:
            logger.debug(f"bulk_create: No records to insert into {schema}.{table}")
            return 0

        # SECURITY: Validate table and schema names
        try:
            validated_table = validate_table_name(table, DatabaseDialect.POSTGRESQL)
            validated_schema = validate_schema_name(schema, DatabaseDialect.POSTGRESQL)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table or schema name: {e}")

        if not self._connected or not self.pool:
            await self.connect()

        # Get column names from first record (assume all records have same structure)
        columns = list(records[0].keys())
        record_count = len(records)

        logger.info(
            f"Bulk creating {record_count} records in {validated_schema}.{validated_table} "
            f"(ignore_duplicates={ignore_duplicates})"
        )

        try:
            # Strategy 1: Use COPY protocol for large datasets (1000+) without ignore_duplicates
            if record_count >= 1000 and not ignore_duplicates:
                logger.debug(
                    f"Using COPY protocol for {record_count} records in {validated_schema}.{validated_table}"
                )

                # Convert dict records to tuples in correct column order
                record_tuples = [tuple(record[col] for col in columns) for record in records]

                # Use the existing copy_records_to_table method
                await self.copy_records_to_table(
                    table_name=validated_table,
                    records=record_tuples,
                    columns=columns,
                    schema_name=validated_schema,
                )

                logger.info(f"COPY inserted {record_count} records into {validated_schema}.{validated_table}")
                return record_count

            # Strategy 2: Use INSERT for smaller datasets or when ignore_duplicates is needed
            else:
                async with self.pool.acquire() as conn:
                    # Build INSERT query
                    columns_str = ", ".join([f'"{col}"' for col in columns])
                    full_table_name = f'"{validated_schema}"."{validated_table}"'

                    if ignore_duplicates:
                        # Use temp table approach for ignore_duplicates
                        # This is more efficient than individual ON CONFLICT statements
                        temp_table_name = f"temp_bulk_insert_{uuid.uuid4().hex[:8]}"

                        async with conn.transaction():
                            # Create temp table
                            await conn.execute(
                                f"CREATE TEMP TABLE {temp_table_name} "
                                f"(LIKE {full_table_name} INCLUDING DEFAULTS) "
                                f"ON COMMIT DROP"
                            )

                            # Insert into temp table (no conflicts possible)
                            placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])
                            insert_temp_query = (
                                f"INSERT INTO {temp_table_name} ({columns_str}) "
                                f"VALUES ({placeholders})"
                            )

                            # Prepare parameter list
                            params_list = [[record[col] for col in columns] for record in records]

                            # Batch insert into temp table
                            await conn.executemany(insert_temp_query, params_list)

                            # Insert from temp table to target table, ignoring duplicates
                            insert_result = await conn.execute(
                                f"INSERT INTO {full_table_name} ({columns_str}) "
                                f"SELECT {columns_str} FROM {temp_table_name} "
                                f"ON CONFLICT DO NOTHING"
                            )

                            # Parse result to get row count (format: "INSERT 0 N")
                            rows_inserted = int(insert_result.split()[-1])

                        logger.info(
                            f"Bulk created {rows_inserted} records in {validated_schema}.{validated_table} "
                            f"(ignored {record_count - rows_inserted} duplicates)"
                        )
                        return rows_inserted

                    else:
                        # Standard INSERT with executemany
                        placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])
                        insert_query = (
                            f"INSERT INTO {full_table_name} ({columns_str}) "
                            f"VALUES ({placeholders})"
                        )

                        # Prepare parameter list
                        params_list = [[record[col] for col in columns] for record in records]

                        # Execute batch insert
                        await conn.executemany(insert_query, params_list)

                        logger.info(f"Bulk created {record_count} records in {validated_schema}.{validated_table}")
                        return record_count

        except asyncpg.PostgresError as e:
            logger.error(f"Bulk create failed in {validated_schema}.{validated_table}: {e}")
            raise

    async def bulk_update(
        self,
        table: str,
        records: List[Dict[str, Any]],
        key_columns: List[str],
        update_columns: Optional[List[str]] = None,
        schema: str = "public",
    ) -> int:
        """
        Bulk update multiple records efficiently using UPDATE FROM.

        For <1000 records, uses UPDATE FROM VALUES approach.
        For 1000+ records, uses temporary table approach for better performance.

        Args:
            table: Table name (will be validated)
            records: List of dictionaries with column-value pairs
            key_columns: Columns to use for matching records (WHERE clause)
            update_columns: Columns to update (if None, updates all except keys)
            schema: Schema name (default: 'public', will be validated)

        Returns:
            Number of rows updated

        Raises:
            ValueError: If table/schema name is invalid or no update columns
            asyncpg.PostgresError: If update operation fails

        Example:
            # Update users by ID
            rows = await adapter.bulk_update(
                'users',
                [
                    {'id': 1, 'name': 'Alice Updated', 'age': 29},
                    {'id': 2, 'name': 'Bob Updated', 'age': 36},
                    {'id': 3, 'name': 'Charlie Updated', 'age': 43}
                ],
                key_columns=['id']
            )

            # Update by composite key
            rows = await adapter.bulk_update(
                'user_settings',
                [
                    {'user_id': 1, 'setting_key': 'theme', 'value': 'dark'},
                    {'user_id': 2, 'setting_key': 'theme', 'value': 'light'}
                ],
                key_columns=['user_id', 'setting_key'],
                update_columns=['value']
            )
        """
        if not records:
            logger.debug(f"bulk_update: No records to update in {schema}.{table}")
            return 0

        # SECURITY: Validate table and schema names
        try:
            validated_table = validate_table_name(table, DatabaseDialect.POSTGRESQL)
            validated_schema = validate_schema_name(schema, DatabaseDialect.POSTGRESQL)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table or schema name: {e}")

        # Determine columns to update
        all_columns = list(records[0].keys())
        if update_columns is None:
            update_columns = [col for col in all_columns if col not in key_columns]

        if not update_columns:
            raise ValueError("No columns to update (all columns are keys)")

        if not self._connected or not self.pool:
            await self.connect()

        record_count = len(records)
        full_table_name = f'"{validated_schema}"."{validated_table}"'

        logger.info(
            f"Bulk updating {record_count} records in {validated_schema}.{validated_table} "
            f"on keys: {key_columns}"
        )

        try:
            async with self.pool.acquire() as conn:
                # Strategy 1: UPDATE FROM VALUES for smaller datasets (<1000 records)
                if record_count < 1000:
                    logger.debug(
                        f"Using UPDATE FROM VALUES for {record_count} records"
                    )

                    # Build VALUES clause with all columns (keys + update columns)
                    all_update_cols = key_columns + update_columns
                    values_rows = []

                    for i, record in enumerate(records):
                        # Create placeholders for this row
                        row_values = []
                        for col in all_update_cols:
                            param_idx = i * len(all_update_cols) + all_update_cols.index(col) + 1
                            row_values.append(f"${param_idx}")
                        values_rows.append(f"({', '.join(row_values)})")

                    values_clause = ", ".join(values_rows)

                    # Build column type hints for VALUES
                    # This helps PostgreSQL infer types correctly
                    values_columns = ", ".join([f'"{col}"' for col in all_update_cols])

                    # Build SET clause
                    set_parts = [f'"{col}" = v."{col}"' for col in update_columns]
                    set_clause = ", ".join(set_parts)

                    # Build WHERE clause for key matching
                    where_parts = [f'{full_table_name}."{col}" = v."{col}"' for col in key_columns]
                    where_clause = " AND ".join(where_parts)

                    # Construct UPDATE query
                    query = (
                        f"UPDATE {full_table_name} "
                        f"SET {set_clause} "
                        f"FROM (VALUES {values_clause}) AS v({values_columns}) "
                        f"WHERE {where_clause}"
                    )

                    # Flatten parameters in correct order
                    params = []
                    for record in records:
                        for col in all_update_cols:
                            params.append(record[col])

                    # Execute update
                    result = await conn.execute(query, *params)

                    # Parse result to get row count
                    rows_updated = int(result.split()[-1])

                    logger.info(f"Bulk updated {rows_updated} records in {validated_schema}.{validated_table}")
                    return rows_updated

                # Strategy 2: Use temp table for larger datasets (1000+)
                else:
                    logger.debug(
                        f"Using temp table approach for {record_count} records"
                    )

                    temp_table_name = f"temp_bulk_update_{uuid.uuid4().hex[:8]}"

                    async with conn.transaction():
                        # Create temp table with all columns
                        all_update_cols = key_columns + update_columns
                        columns_def = ", ".join(
                            [f'"{col}" TEXT' for col in all_update_cols]  # Use TEXT for simplicity
                        )

                        await conn.execute(
                            f"CREATE TEMP TABLE {temp_table_name} ({columns_def}) "
                            f"ON COMMIT DROP"
                        )

                        # Insert data into temp table
                        placeholders = ", ".join([f"${i+1}" for i in range(len(all_update_cols))])
                        columns_str = ", ".join([f'"{col}"' for col in all_update_cols])

                        insert_query = (
                            f"INSERT INTO {temp_table_name} ({columns_str}) "
                            f"VALUES ({placeholders})"
                        )

                        params_list = [[record[col] for col in all_update_cols] for record in records]
                        await conn.executemany(insert_query, params_list)

                        # Perform UPDATE FROM temp table
                        set_parts = [f'"{col}" = t."{col}"::{full_table_name}."{col}"::regtype::text'
                                    for col in update_columns]
                        set_clause = ", ".join(set_parts)

                        where_parts = [f'{full_table_name}."{col}" = t."{col}"::{full_table_name}."{col}"::regtype::text'
                                      for col in key_columns]
                        where_clause = " AND ".join(where_parts)

                        # Simplified SET clause without type casting for temp table
                        set_parts = [f'"{col}" = t."{col}"' for col in update_columns]
                        set_clause = ", ".join(set_parts)

                        where_parts = [f'{full_table_name}."{col}"::TEXT = t."{col}"' for col in key_columns]
                        where_clause = " AND ".join(where_parts)

                        update_query = (
                            f"UPDATE {full_table_name} "
                            f"SET {set_clause} "
                            f"FROM {temp_table_name} t "
                            f"WHERE {where_clause}"
                        )

                        result = await conn.execute(update_query)

                        # Parse result to get row count
                        rows_updated = int(result.split()[-1])

                    logger.info(f"Bulk updated {rows_updated} records in {validated_schema}.{validated_table}")
                    return rows_updated

        except asyncpg.PostgresError as e:
            logger.error(f"Bulk update failed in {validated_schema}.{validated_table}: {e}")
            raise

    async def create_or_update(
        self,
        table: str,
        record: Dict[str, Any],
        unique_columns: List[str],
        update_columns: Optional[List[str]] = None,
        schema: str = "public",
    ) -> Dict[str, Any]:
        """
        Insert record or update if it exists (UPSERT operation).

        Uses PostgreSQL's INSERT ... ON CONFLICT DO UPDATE with xmax detection
        to determine if a record was created or updated.

        Args:
            table: Table name (will be validated)
            record: Dictionary with column-value pairs
            unique_columns: Columns that define uniqueness (must have UNIQUE constraint)
            update_columns: Columns to update on conflict (if None, updates all except unique)
            schema: Schema name (default: 'public', will be validated)

        Returns:
            Dictionary with:
                - action: 'created', 'updated', or 'unchanged'
                - record: The full record (dict)
                - id: Primary key ID if available (or None)

        Raises:
            ValueError: If table/schema name is invalid
            asyncpg.PostgresError: If upsert operation fails

        Example:
            # Upsert by email (email must have UNIQUE constraint)
            result = await adapter.create_or_update(
                'users',
                {'email': 'alice@example.com', 'name': 'Alice', 'age': 28},
                unique_columns=['email']
            )
            print(f"Action: {result['action']}, ID: {result['id']}")

            # Upsert with specific update columns
            result = await adapter.create_or_update(
                'products',
                {'sku': 'LAPTOP-001', 'name': 'Laptop Pro', 'price': 1299.99, 'stock': 50},
                unique_columns=['sku'],
                update_columns=['price', 'stock']
            )
        """
        # SECURITY: Validate table and schema names
        try:
            validated_table = validate_table_name(table, DatabaseDialect.POSTGRESQL)
            validated_schema = validate_schema_name(schema, DatabaseDialect.POSTGRESQL)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table or schema name: {e}")

        # Determine columns to update on conflict
        all_columns = list(record.keys())
        if update_columns is None:
            update_columns = [col for col in all_columns if col not in unique_columns]

        if not self._connected or not self.pool:
            await self.connect()

        full_table_name = f'"{validated_schema}"."{validated_table}"'

        logger.debug(
            f"Create or update in {validated_schema}.{validated_table} "
            f"with unique columns: {unique_columns}"
        )

        try:
            async with self.pool.acquire() as conn:
                # Build INSERT clause
                columns_str = ", ".join([f'"{col}"' for col in all_columns])
                placeholders = ", ".join([f"${i+1}" for i in range(len(all_columns))])

                # Build ON CONFLICT clause
                conflict_columns = ", ".join([f'"{col}"' for col in unique_columns])

                # Build UPDATE SET clause
                update_parts = [f'"{col}" = EXCLUDED."{col}"' for col in update_columns]
                update_clause = ", ".join(update_parts)

                # Use xmax = 0 to detect if row was inserted (created) vs updated
                # xmax = 0 means the row was just inserted in this transaction
                query = (
                    f"INSERT INTO {full_table_name} ({columns_str}) "
                    f"VALUES ({placeholders}) "
                    f"ON CONFLICT ({conflict_columns}) "
                )

                if update_columns:
                    query += f"DO UPDATE SET {update_clause} "
                else:
                    query += "DO NOTHING "

                # Return the full row and xmax to detect created vs updated
                query += f"RETURNING *, (xmax = 0) AS inserted"

                # Prepare parameters
                params = [record[col] for col in all_columns]

                # Execute upsert
                row = await conn.fetchrow(query, *params)

                if row is None:
                    # This shouldn't happen with RETURNING, but handle it
                    action = "unchanged"
                    record_id = None
                    result_record = record
                else:
                    # Convert record to dict (exclude the 'inserted' flag)
                    result_record = dict(row)
                    was_inserted = result_record.pop("inserted", False)

                    # Determine action
                    if was_inserted:
                        action = "created"
                    else:
                        # Check if any values actually changed
                        # For simplicity, we'll mark it as 'updated'
                        action = "updated"

                    # Try to get ID from common ID column names
                    record_id = result_record.get("id") or result_record.get("ID")

                result = {
                    "action": action,
                    "record": result_record,
                    "id": record_id,
                }

                logger.debug(
                    f"Create or update in {validated_schema}.{validated_table}: "
                    f"{action} (id: {record_id})"
                )

                return result

        except asyncpg.PostgresError as e:
            logger.error(f"Create or update failed in {validated_schema}.{validated_table}: {e}")
            raise

    async def bulk_create_or_update(
        self,
        table: str,
        records: List[Dict[str, Any]],
        unique_columns: List[str],
        update_columns: Optional[List[str]] = None,
        schema: str = "public",
    ) -> Dict[str, int]:
        """
        Bulk insert or update multiple records (UPSERT).

        Uses PostgreSQL's INSERT ... ON CONFLICT with RETURNING to track
        created vs updated records. Uses VALUES approach for <500 records,
        temp table approach for 500+ records.

        Args:
            table: Table name (will be validated)
            records: List of dictionaries with column-value pairs
            unique_columns: Columns that define uniqueness
            update_columns: Columns to update on conflict (if None, updates all except unique)
            schema: Schema name (default: 'public', will be validated)

        Returns:
            Dictionary with:
                - created: Number of created records
                - updated: Number of updated records
                - total_affected: Total rows affected

        Raises:
            ValueError: If table/schema name is invalid
            asyncpg.PostgresError: If upsert operation fails

        Example:
            results = await adapter.bulk_create_or_update(
                'products',
                [
                    {'sku': 'LAPTOP-001', 'name': 'Laptop Pro', 'price': 1299.99},
                    {'sku': 'PHONE-001', 'name': 'Phone X', 'price': 899.99},
                    {'sku': 'TABLET-001', 'name': 'Tablet', 'price': 599.99}
                ],
                unique_columns=['sku'],
                update_columns=['name', 'price']
            )
            print(f"Created: {results['created']}, Updated: {results['updated']}")
        """
        if not records:
            logger.debug(f"bulk_create_or_update: No records for {schema}.{table}")
            return {"created": 0, "updated": 0, "total_affected": 0}

        # SECURITY: Validate table and schema names
        try:
            validated_table = validate_table_name(table, DatabaseDialect.POSTGRESQL)
            validated_schema = validate_schema_name(schema, DatabaseDialect.POSTGRESQL)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table or schema name: {e}")

        # Determine columns to update on conflict
        all_columns = list(records[0].keys())
        if update_columns is None:
            update_columns = [col for col in all_columns if col not in unique_columns]

        if not self._connected or not self.pool:
            await self.connect()

        record_count = len(records)
        full_table_name = f'"{validated_schema}"."{validated_table}"'

        logger.info(
            f"Bulk create_or_update {record_count} records in {validated_schema}.{validated_table} "
            f"with unique columns: {unique_columns}"
        )

        try:
            async with self.pool.acquire() as conn:
                # Strategy 1: VALUES approach for smaller datasets (<500 records)
                if record_count < 500:
                    logger.debug(f"Using VALUES approach for {record_count} records")

                    # Build VALUES clause
                    values_rows = []
                    params = []
                    param_idx = 1

                    for record in records:
                        row_placeholders = []
                        for col in all_columns:
                            row_placeholders.append(f"${param_idx}")
                            params.append(record[col])
                            param_idx += 1
                        values_rows.append(f"({', '.join(row_placeholders)})")

                    values_clause = ", ".join(values_rows)
                    columns_str = ", ".join([f'"{col}"' for col in all_columns])

                    # Build ON CONFLICT clause
                    conflict_columns = ", ".join([f'"{col}"' for col in unique_columns])

                    # Build UPDATE SET clause
                    if update_columns:
                        update_parts = [f'"{col}" = EXCLUDED."{col}"' for col in update_columns]
                        update_clause = f"DO UPDATE SET {', '.join(update_parts)}"
                    else:
                        update_clause = "DO NOTHING"

                    # Execute with xmax detection
                    query = (
                        f"INSERT INTO {full_table_name} ({columns_str}) "
                        f"VALUES {values_clause} "
                        f"ON CONFLICT ({conflict_columns}) "
                        f"{update_clause} "
                        f"RETURNING (xmax = 0) AS inserted"
                    )

                    rows = await conn.fetch(query, *params)

                    # Count created vs updated
                    created = sum(1 for row in rows if row["inserted"])
                    updated = len(rows) - created

                    result = {
                        "created": created,
                        "updated": updated,
                        "total_affected": len(rows),
                    }

                    logger.info(
                        f"Bulk create_or_update in {validated_schema}.{validated_table}: "
                        f"{created} created, {updated} updated"
                    )

                    return result

                # Strategy 2: Temp table for larger datasets (500+)
                else:
                    logger.debug(f"Using temp table approach for {record_count} records")

                    temp_table_name = f"temp_bulk_upsert_{uuid.uuid4().hex[:8]}"

                    async with conn.transaction():
                        # Create temp table
                        await conn.execute(
                            f"CREATE TEMP TABLE {temp_table_name} "
                            f"(LIKE {full_table_name} INCLUDING DEFAULTS) "
                            f"ON COMMIT DROP"
                        )

                        # Insert into temp table
                        placeholders = ", ".join([f"${i+1}" for i in range(len(all_columns))])
                        columns_str = ", ".join([f'"{col}"' for col in all_columns])

                        insert_query = (
                            f"INSERT INTO {temp_table_name} ({columns_str}) "
                            f"VALUES ({placeholders})"
                        )

                        params_list = [[record[col] for col in all_columns] for record in records]
                        await conn.executemany(insert_query, params_list)

                        # Perform upsert from temp table
                        conflict_columns = ", ".join([f'"{col}"' for col in unique_columns])

                        if update_columns:
                            update_parts = [f'"{col}" = EXCLUDED."{col}"' for col in update_columns]
                            update_clause = f"DO UPDATE SET {', '.join(update_parts)}"
                        else:
                            update_clause = "DO NOTHING"

                        upsert_query = (
                            f"INSERT INTO {full_table_name} ({columns_str}) "
                            f"SELECT {columns_str} FROM {temp_table_name} "
                            f"ON CONFLICT ({conflict_columns}) "
                            f"{update_clause} "
                            f"RETURNING (xmax = 0) AS inserted"
                        )

                        rows = await conn.fetch(upsert_query)

                        # Count created vs updated
                        created = sum(1 for row in rows if row["inserted"])
                        updated = len(rows) - created

                    result = {
                        "created": created,
                        "updated": updated,
                        "total_affected": len(rows),
                    }

                    logger.info(
                        f"Bulk create_or_update in {validated_schema}.{validated_table}: "
                        f"{created} created, {updated} updated"
                    )

                    return result

        except asyncpg.PostgresError as e:
            logger.error(f"Bulk create_or_update failed in {validated_schema}.{validated_table}: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on PostgreSQL connection and server.

        Queries PostgreSQL system catalogs (pg_stat_database, pg_stat_activity)
        to gather health metrics including cache hit ratio, connection counts,
        and pool statistics.

        Returns:
            Dictionary with health check results:
                - status: 'healthy', 'degraded', or 'unhealthy'
                - connected: Connection status (bool)
                - version: PostgreSQL version string
                - uptime: Server uptime in seconds
                - database_size: Current database size in bytes
                - active_connections: Number of active connections
                - idle_connections: Number of idle connections
                - max_connections: Maximum allowed connections
                - cache_hit_ratio: Buffer cache hit ratio (0.0-1.0)
                - transactions_committed: Total committed transactions
                - transactions_rolled_back: Total rolled back transactions
                - deadlocks: Number of deadlocks detected
                - pool_size: Current connection pool size
                - pool_free: Number of free connections in pool
                - pool_used: Number of connections in use

        Example:
            health = await adapter.health_check()
            if health['status'] == 'healthy':
                print(f"PostgreSQL is healthy - Version: {health['version']}")
                print(f"Cache hit ratio: {health['cache_hit_ratio']:.2%}")
            elif health['status'] == 'degraded':
                print("PostgreSQL is degraded - check metrics")
            else:
                print(f"PostgreSQL is unhealthy: {health.get('error')}")
        """
        try:
            if not self._connected or not self.pool:
                await self.connect()

            # Test basic connectivity
            await self.fetch_value("SELECT 1")

            # Get PostgreSQL version
            version = await self.get_version()

            # Get database statistics from pg_stat_database
            db_stats_query = """
                SELECT
                    pg_database_size(datname) as database_size,
                    numbackends as active_connections,
                    xact_commit as transactions_committed,
                    xact_rollback as transactions_rolled_back,
                    blks_read as blocks_read,
                    blks_hit as blocks_hit,
                    deadlocks,
                    stats_reset
                FROM pg_stat_database
                WHERE datname = $1
            """
            db_stats = await self.fetch_one(db_stats_query, (self.database,))

            # Calculate cache hit ratio
            # (blocks_hit / (blocks_hit + blocks_read))
            blocks_hit = db_stats.get("blocks_hit", 0) or 0
            blocks_read = db_stats.get("blocks_read", 0) or 0
            total_blocks = blocks_hit + blocks_read

            if total_blocks > 0:
                cache_hit_ratio = blocks_hit / total_blocks
            else:
                cache_hit_ratio = 1.0  # No reads yet, assume perfect cache

            # Get connection statistics from pg_stat_activity
            connections_query = """
                SELECT
                    COUNT(*) FILTER (WHERE state = 'active') as active,
                    COUNT(*) FILTER (WHERE state = 'idle') as idle,
                    COUNT(*) as total
                FROM pg_stat_activity
                WHERE datname = $1
            """
            conn_stats = await self.fetch_one(connections_query, (self.database,))

            # Get max connections setting
            max_connections = await self.fetch_value("SHOW max_connections")
            max_connections = int(max_connections)

            # Get server uptime
            uptime_query = "SELECT EXTRACT(EPOCH FROM (NOW() - pg_postmaster_start_time()))::INTEGER"
            uptime = await self.fetch_value(uptime_query)

            # Get pool statistics
            pool_stats = await self.get_pool_stats()

            # Determine health status
            # Degraded if:
            # - Cache hit ratio < 0.90 (90%)
            # - Connection usage > 80% of max
            # - High rollback ratio (>5% of commits)
            status = "healthy"

            connection_usage_pct = (conn_stats["total"] / max_connections) if max_connections > 0 else 0

            if cache_hit_ratio < 0.90:
                status = "degraded"
                logger.warning(
                    f"PostgreSQL cache hit ratio is low: {cache_hit_ratio:.2%} "
                    f"(threshold: 90%)"
                )

            if connection_usage_pct > 0.80:
                status = "degraded"
                logger.warning(
                    f"PostgreSQL connection usage is high: {connection_usage_pct:.2%} "
                    f"({conn_stats['total']}/{max_connections})"
                )

            commits = db_stats.get("transactions_committed", 0) or 0
            rollbacks = db_stats.get("transactions_rolled_back", 0) or 0
            total_transactions = commits + rollbacks

            if total_transactions > 0:
                rollback_ratio = rollbacks / total_transactions
                if rollback_ratio > 0.05:
                    status = "degraded"
                    logger.warning(
                        f"PostgreSQL rollback ratio is high: {rollback_ratio:.2%} "
                        f"(threshold: 5%)"
                    )

            result = {
                "status": status,
                "connected": True,
                "version": version,
                "uptime": uptime,
                "database_size": db_stats.get("database_size", 0),
                "active_connections": conn_stats["active"],
                "idle_connections": conn_stats["idle"],
                "total_connections": conn_stats["total"],
                "max_connections": max_connections,
                "cache_hit_ratio": cache_hit_ratio,
                "transactions_committed": commits,
                "transactions_rolled_back": rollbacks,
                "deadlocks": db_stats.get("deadlocks", 0),
                "pool_size": pool_stats["size"],
                "pool_free": pool_stats["free"],
                "pool_used": pool_stats["used"],
            }

            logger.info(
                f"Health check passed: {status} - "
                f"Cache: {cache_hit_ratio:.2%}, "
                f"Connections: {conn_stats['total']}/{max_connections}, "
                f"Pool: {pool_stats['used']}/{pool_stats['size']}"
            )

            return result

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
            }

    def __repr__(self) -> str:
        """String representation of adapter."""
        conn_status = "connected" if self._connected else "disconnected"
        return (
            f"PostgreSQLAdapter("
            f"{self.user}@{self.host}:{self.port}/{self.database}, "
            f"pool={self.min_pool_size}-{self.max_pool_size}, "
            f"{conn_status}"
            f")"
        )


__all__ = ["PostgreSQLAdapter"]
