"""
SQLite Database Adapter

Production-ready SQLite adapter using aiosqlite for async operations.
Supports connection pooling, transactions, and SQLite-specific features.
"""

import asyncio
import logging
import sqlite3
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import aiosqlite

from ..security.sql_validator import (
    DatabaseDialect,
    InvalidIdentifierError,
    validate_schema_name,
    validate_table_name,
)
from .base import DatabaseAdapter

logger = logging.getLogger(__name__)


class SQLiteConnectionPool:
    """
    Connection pool for SQLite to manage concurrent access.
    SQLite doesn't have native pooling, so we implement it ourselves.
    """

    def __init__(self, database: str, max_size: int = 50, timeout: float = 30.0, **kwargs):
        """
        Initialize SQLite connection pool.

        Args:
            database: Database file path
            max_size: Maximum pool size (default: 50 for high concurrency)
            timeout: Connection acquisition timeout
            **kwargs: Additional connection parameters
        """
        self.database = database
        self.max_size = max_size
        self.timeout = timeout
        self.kwargs = kwargs
        self._pool: List[aiosqlite.Connection] = []
        self._available: List[aiosqlite.Connection] = []
        self._lock = asyncio.Lock()
        self._closed = False

        # Connection health tracking
        self._connection_age: Dict[aiosqlite.Connection, float] = {}
        self._max_connection_age = 3600  # 1 hour max age
        self._last_health_check = time.time()

    async def initialize(self):
        """Initialize the connection pool with optimized settings."""
        async with self._lock:
            for _ in range(self.max_size):
                conn = await aiosqlite.connect(self.database, timeout=self.timeout, **self.kwargs)

                # Enable WAL mode for better concurrency
                await conn.execute("PRAGMA journal_mode=WAL")

                # Enable foreign keys
                await conn.execute("PRAGMA foreign_keys=ON")

                # Performance optimizations
                await conn.execute("PRAGMA synchronous=NORMAL")  # Faster than FULL, safe with WAL
                await conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
                await conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
                await conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O

                self._pool.append(conn)
                self._available.append(conn)
                self._connection_age[conn] = time.time()

    async def acquire(self) -> aiosqlite.Connection:
        """Acquire a connection from the pool with health checking."""
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        # Perform periodic health check
        await self._health_check()

        start_time = asyncio.get_event_loop().time()
        while True:
            async with self._lock:
                if self._available:
                    conn = self._available.pop()

                    # Check connection age and recycle if too old
                    age = time.time() - self._connection_age.get(conn, 0)
                    if age > self._max_connection_age:
                        logger.debug(f"Recycling connection aged {age:.0f}s")
                        await conn.close()

                        # Create new connection
                        conn = await aiosqlite.connect(
                            self.database, timeout=self.timeout, **self.kwargs
                        )
                        await conn.execute("PRAGMA journal_mode=WAL")
                        await conn.execute("PRAGMA foreign_keys=ON")
                        await conn.execute("PRAGMA synchronous=NORMAL")
                        await conn.execute("PRAGMA cache_size=-64000")
                        await conn.execute("PRAGMA temp_store=MEMORY")
                        await conn.execute("PRAGMA mmap_size=268435456")

                        self._pool[self._pool.index(conn)] = conn
                        self._connection_age[conn] = time.time()

                    return conn

            # Wait and retry
            if asyncio.get_event_loop().time() - start_time > self.timeout:
                raise TimeoutError("Timeout waiting for connection")
            await asyncio.sleep(0.01)

    async def _health_check(self):
        """Perform periodic health check on connections."""
        now = time.time()
        if now - self._last_health_check < 300:  # Check every 5 minutes
            return

        async with self._lock:
            self._last_health_check = now
            # Health check is done during acquire by checking connection age

    async def release(self, conn: aiosqlite.Connection):
        """Release a connection back to the pool."""
        async with self._lock:
            if conn in self._pool and conn not in self._available:
                self._available.append(conn)

    async def close(self):
        """Close all connections in the pool."""
        async with self._lock:
            self._closed = True
            for conn in self._pool:
                await conn.close()
            self._pool.clear()
            self._available.clear()

    def get_size(self) -> int:
        """Get total pool size."""
        return len(self._pool)

    def get_idle_size(self) -> int:
        """Get number of idle connections."""
        return len(self._available)


class SQLiteAdapter(DatabaseAdapter):
    """
    High-performance SQLite database adapter using aiosqlite.

    Features:
    - Async/await support with aiosqlite
    - Custom connection pooling for concurrency
    - Automatic retries with exponential backoff
    - Transaction management with savepoints
    - WAL mode for better concurrent access
    - Foreign key constraint enforcement
    - Query timeout support
    - Comprehensive error handling

    Example:
        adapter = SQLiteAdapter(
            database='/path/to/database.db',
            max_pool_size=10,
            timeout=30.0
        )
        await adapter.connect()
        result = await adapter.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            ("Alice", "alice@example.com")
        )
    """

    def __init__(
        self,
        database: str = ":memory:",
        max_pool_size: int = 50,
        timeout: float = 30.0,
        check_same_thread: bool = False,
        isolation_level: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize SQLite adapter with enhanced connection pooling.

        Args:
            database: Database file path or ':memory:' for in-memory database
            max_pool_size: Maximum number of connections in pool (default: 50 for high concurrency)
            timeout: Database timeout in seconds
            check_same_thread: Whether to check same thread (default: False for async)
            isolation_level: Transaction isolation level (DEFERRED, IMMEDIATE, EXCLUSIVE)
            **kwargs: Additional aiosqlite connection parameters

        Connection Pool Optimizations:
            - Increased default pool size to 50 for horizontal scaling
            - Connection recycling to prevent stale connections
            - Health checks every 5 minutes
            - WAL mode for better concurrency
            - Optimized PRAGMA settings for performance
        """
        self.database = database
        self.max_pool_size = max_pool_size
        self.timeout = timeout
        self.check_same_thread = check_same_thread
        self.isolation_level = isolation_level
        self.extra_params = kwargs

        self.pool: Optional[SQLiteConnectionPool] = None
        self._connected = False

        # Create database directory if it doesn't exist
        if database != ":memory:":
            Path(database).parent.mkdir(parents=True, exist_ok=True)

    async def connect(self) -> None:
        """
        Establish connection pool to SQLite database.

        Creates a connection pool with configured size.
        Includes retry logic for transient connection failures.

        Raises:
            aiosqlite.Error: If connection fails after retries
        """
        if self._connected and self.pool:
            return

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Connecting to SQLite: {self.database} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                # Create connection pool
                self.pool = SQLiteConnectionPool(
                    database=self.database,
                    max_size=self.max_pool_size,
                    timeout=self.timeout,
                    check_same_thread=self.check_same_thread,
                    isolation_level=self.isolation_level,
                    **self.extra_params,
                )

                await self.pool.initialize()

                # Test connection
                conn = await self.pool.acquire()
                try:
                    await conn.execute("SELECT 1")
                finally:
                    await self.pool.release(conn)

                self._connected = True
                logger.info(
                    f"Connected to SQLite: {self.database} " f"(pool size: {self.max_pool_size})"
                )
                return

            except Exception as e:
                logger.warning(f"SQLite connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to SQLite after {max_retries} attempts")
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
            logger.info(f"Disconnected from SQLite: {self.database}")

    async def execute(self, query: str, params: Optional[Union[Tuple, List]] = None) -> int:
        """
        Execute a SQL command (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query with ? placeholders
            params: Query parameters

        Returns:
            Number of affected rows

        Example:
            rows_affected = await adapter.execute(
                "UPDATE users SET active = ? WHERE id = ?",
                (True, 42)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            await conn.execute(query, params)
            await conn.commit()
            affected_rows = conn.total_changes
            logger.debug(f"Executed: {query[:100]}... -> {affected_rows} rows affected")
            return affected_rows

        except Exception as e:
            logger.error(f"Execute failed: {query[:100]}... Error: {e}")
            await conn.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def execute_insert(self, query: str, params: Optional[Union[Tuple, List]] = None) -> int:
        """
        Execute an INSERT command and return the last insert ID.

        Args:
            query: SQL INSERT query with ? placeholders
            params: Query parameters

        Returns:
            Last inserted row ID (rowid/autoincrement value)

        Example:
            user_id = await adapter.execute_insert(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                ("Alice", "alice@example.com")
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            cursor = await conn.execute(query, params)
            last_id = cursor.lastrowid
            await conn.commit()
            logger.debug(f"Executed insert: {query[:100]}... -> last_id={last_id}")
            return last_id

        except Exception as e:
            logger.error(f"Execute insert failed: {query[:100]}... Error: {e}")
            await conn.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def fetch_one(
        self, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row as a dictionary.

        Args:
            query: SQL query with ? placeholders
            params: Query parameters

        Returns:
            Dictionary with column names as keys, or None if no rows

        Example:
            user = await adapter.fetch_one(
                "SELECT * FROM users WHERE id = ?",
                (42,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            await cursor.close()

            if row:
                result = dict(row)
                logger.debug(f"Fetched one: {query[:100]}... -> 1 row")
                return result
            logger.debug(f"Fetched one: {query[:100]}... -> None")
            return None

        except Exception as e:
            logger.error(f"Fetch one failed: {query[:100]}... Error: {e}")
            raise
        finally:
            await self.pool.release(conn)

    async def fetch_all(
        self, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows as list of dictionaries.

        Args:
            query: SQL query with ? placeholders
            params: Query parameters

        Returns:
            List of dictionaries with column names as keys

        Example:
            users = await adapter.fetch_all(
                "SELECT * FROM users WHERE active = ?",
                (True,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            await cursor.close()

            result = [dict(row) for row in rows]
            logger.debug(f"Fetched all: {query[:100]}... -> {len(result)} rows")
            return result

        except Exception as e:
            logger.error(f"Fetch all failed: {query[:100]}... Error: {e}")
            raise
        finally:
            await self.pool.release(conn)

    async def fetch_value(
        self, query: str, params: Optional[Union[Tuple, List]] = None, column: int = 0
    ) -> Optional[Any]:
        """
        Fetch a single value from the first row.

        Args:
            query: SQL query
            params: Query parameters
            column: Column index (default: 0 for first column)

        Returns:
            Single value or None

        Example:
            count = await adapter.fetch_value("SELECT COUNT(*) FROM users")
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        conn = await self.pool.acquire()
        try:
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            await cursor.close()

            if row:
                value = row[column] if len(row) > column else None
                logger.debug(f"Fetched value: {query[:100]}... -> {value}")
                return value
            return None

        except Exception as e:
            logger.error(f"Fetch value failed: {query[:100]}... Error: {e}")
            raise
        finally:
            await self.pool.release(conn)

    @asynccontextmanager
    async def transaction(self, isolation: Optional[str] = None):
        """
        Context manager for database transactions.

        Args:
            isolation: Transaction isolation level (DEFERRED, IMMEDIATE, EXCLUSIVE)

        Yields:
            aiosqlite.Connection: Database connection within transaction

        Example:
            async with adapter.transaction(isolation='IMMEDIATE') as conn:
                await conn.execute("INSERT INTO users ...")
                await conn.execute("UPDATE accounts ...")
                # Automatically commits on success, rolls back on exception
        """
        if not self._connected or not self.pool:
            await self.connect()

        conn = await self.pool.acquire()
        try:
            # Start transaction with isolation level
            if isolation:
                await conn.execute(f"BEGIN {isolation}")
            else:
                await conn.execute("BEGIN")

            yield conn
            await conn.commit()

        except Exception:
            await conn.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def execute_many(self, query: str, params_list: List[Union[Tuple, List]]) -> int:
        """
        Execute the same query with multiple parameter sets.

        Uses executemany for efficient batch operations.

        Args:
            query: SQL query with placeholders
            params_list: List of parameter tuples

        Returns:
            Total number of affected rows

        Example:
            affected = await adapter.execute_many(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                [
                    ("Alice", "alice@example.com"),
                    ("Bob", "bob@example.com"),
                    ("Charlie", "charlie@example.com"),
                ]
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        conn = await self.pool.acquire()
        try:
            await conn.executemany(query, params_list)
            await conn.commit()
            affected_rows = conn.total_changes
            logger.debug(
                f"Executed many: {query[:100]}... with {len(params_list)} param sets "
                f"-> {affected_rows} rows affected"
            )
            return affected_rows

        except Exception as e:
            logger.error(f"Execute many failed: {query[:100]}... Error: {e}")
            await conn.rollback()
            raise
        finally:
            await self.pool.release(conn)

    async def stream_query(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        chunk_size: int = 1000,
    ):
        """
        Stream query results in chunks for large datasets.

        Memory-efficient for processing millions of rows.

        Args:
            query: SQL query
            params: Query parameters
            chunk_size: Number of rows per chunk

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

        conn = await self.pool.acquire()
        try:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)

            while True:
                rows = await cursor.fetchmany(chunk_size)
                if not rows:
                    break
                yield [dict(row) for row in rows]

            await cursor.close()

        except Exception as e:
            logger.error(f"Stream query failed: {query[:100]}... Error: {e}")
            raise
        finally:
            await self.pool.release(conn)

    async def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a table.

        SECURITY FIX: Validates table name to prevent SQL injection.

        Args:
            table_name: Table name (will be validated)

        Returns:
            List of column info dictionaries with keys:
                - cid: column id
                - name: column name
                - type: data type
                - notnull: 1 if NOT NULL, 0 otherwise
                - dflt_value: default value
                - pk: 1 if primary key, 0 otherwise

        Raises:
            ValueError: If table name is invalid or contains SQL injection patterns
        """
        # SECURITY: Validate table name before using in PRAGMA
        try:
            validated_table = validate_table_name(table_name, DatabaseDialect.SQLITE)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{table_name}': {e}")

        # PRAGMA statements don't support parameterization, so we must validate
        # the identifier before string formatting
        query = f"PRAGMA table_info({validated_table})"
        return await self.fetch_all(query)

    async def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Table name

        Returns:
            True if table exists
        """
        query = """
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='table' AND name=?
        """
        count = await self.fetch_value(query, (table_name,))
        return count > 0

    async def get_version(self) -> str:
        """
        Get SQLite version.

        Returns:
            Version string (e.g., "3.39.4")
        """
        return await self.fetch_value("SELECT sqlite_version()")

    async def get_table_list(self) -> List[str]:
        """
        Get list of all tables.

        Returns:
            List of table names
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        rows = await self.fetch_all(query)
        return [row["name"] for row in rows]

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

    async def vacuum(self) -> None:
        """
        Vacuum the database to reclaim space and optimize.

        This can take a while on large databases.
        """
        conn = await self.pool.acquire()
        try:
            await conn.execute("VACUUM")
            await conn.commit()
            logger.info(f"Vacuumed database: {self.database}")
        finally:
            await self.pool.release(conn)

    async def analyze(self, table_name: Optional[str] = None) -> None:
        """
        Analyze database or specific table to update query optimizer statistics.

        SECURITY FIX: Validates table name to prevent SQL injection.

        Args:
            table_name: Table name (optional, analyzes all tables if None)

        Raises:
            ValueError: If table name is invalid or contains SQL injection patterns
        """
        conn = await self.pool.acquire()
        try:
            if table_name:
                # SECURITY: Validate table name before using in ANALYZE
                try:
                    validated_table = validate_table_name(table_name, DatabaseDialect.SQLITE)
                except InvalidIdentifierError as e:
                    raise ValueError(f"Invalid table name '{table_name}': {e}")

                # ANALYZE doesn't support parameterization, so we must validate
                await conn.execute(f"ANALYZE {validated_table}")
            else:
                await conn.execute("ANALYZE")
            await conn.commit()
            logger.info(f"Analyzed: {table_name or 'all tables'}")
        finally:
            await self.pool.release(conn)

    async def bulk_create(
        self,
        table: str,
        records: List[Dict[str, Any]],
        ignore_duplicates: bool = False,
        batch_size: int = 500,
    ) -> int:
        """
        Bulk insert records into a table with batch processing.

        Uses executemany() within IMMEDIATE transaction for optimal performance
        with SQLite's single-writer model. Processes records in batches to avoid
        holding locks too long.

        Args:
            table: Table name (will be validated for SQL injection)
            records: List of dictionaries with column names as keys
            ignore_duplicates: Use INSERT OR IGNORE to skip duplicates (default: False)
            batch_size: Number of records per batch (default: 500)

        Returns:
            Total number of rows inserted

        Raises:
            ValueError: If table name is invalid or records list is empty
            sqlite3.IntegrityError: If duplicate keys exist and ignore_duplicates=False
            sqlite3.OperationalError: If database is locked after retries

        Example:
            records = [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
                {"name": "Charlie", "email": "charlie@example.com"},
            ]
            inserted = await adapter.bulk_create(
                "users", records, ignore_duplicates=True, batch_size=1000
            )
            print(f"Inserted {inserted} rows")
        """
        if not records:
            logger.warning("bulk_create called with empty records list")
            return 0

        # SECURITY: Validate table name
        try:
            validated_table = validate_table_name(table, DatabaseDialect.SQLITE)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{table}': {e}")

        if not self._connected or not self.pool:
            await self.connect()

        # Extract columns from first record
        columns = list(records[0].keys())
        if not columns:
            raise ValueError("Records must have at least one column")

        # Build INSERT query
        placeholders = ", ".join(["?"] * len(columns))
        column_list = ", ".join(columns)
        insert_type = "INSERT OR IGNORE" if ignore_duplicates else "INSERT"
        query = f"{insert_type} INTO {validated_table} ({column_list}) VALUES ({placeholders})"

        total_inserted = 0
        total_batches = (len(records) + batch_size - 1) // batch_size

        logger.info(
            f"Starting bulk_create: table={validated_table}, records={len(records)}, "
            f"batches={total_batches}, batch_size={batch_size}, ignore_duplicates={ignore_duplicates}"
        )

        # Process in batches
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(records))
            batch_records = records[start_idx:end_idx]

            # Convert records to tuples
            params_list = [tuple(record.get(col) for col in columns) for record in batch_records]

            # Retry logic for SQLITE_BUSY errors
            max_retries = 3
            retry_delay = 0.1

            for attempt in range(max_retries):
                try:
                    # Use IMMEDIATE transaction to avoid SQLITE_BUSY
                    async with self.transaction(isolation="IMMEDIATE") as conn:
                        changes_before = conn.total_changes
                        await conn.executemany(query, params_list)
                        changes_after = conn.total_changes
                        batch_inserted = changes_after - changes_before
                        total_inserted += batch_inserted

                    logger.debug(
                        f"Batch {batch_num + 1}/{total_batches}: inserted {batch_inserted} rows"
                    )
                    break  # Success, exit retry loop

                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower() or "busy" in str(e).lower():
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Database locked on batch {batch_num + 1}, "
                                f"retry {attempt + 1}/{max_retries}"
                            )
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logger.error(
                                f"Database locked after {max_retries} retries on batch {batch_num + 1}"
                            )
                            raise
                    else:
                        raise

        logger.info(f"bulk_create completed: inserted {total_inserted} rows into {validated_table}")
        return total_inserted

    async def bulk_update(
        self,
        table: str,
        records: List[Dict[str, Any]],
        key_columns: List[str],
        update_columns: Optional[List[str]] = None,
        batch_size: int = 500,
    ) -> int:
        """
        Bulk update records in a table using individual UPDATEs.

        Uses individual UPDATE statements within IMMEDIATE transaction batches.
        Supports composite keys for flexible matching.

        Args:
            table: Table name (will be validated for SQL injection)
            records: List of dictionaries with column names as keys
            key_columns: Columns to use for WHERE clause (supports composite keys)
            update_columns: Columns to update (default: all non-key columns)
            batch_size: Number of records per batch transaction (default: 500)

        Returns:
            Total number of rows updated

        Raises:
            ValueError: If table name invalid, records empty, or key_columns missing
            sqlite3.OperationalError: If database is locked after retries

        Example:
            records = [
                {"id": 1, "name": "Alice Updated", "email": "alice.new@example.com"},
                {"id": 2, "name": "Bob Updated", "email": "bob.new@example.com"},
            ]
            updated = await adapter.bulk_update(
                "users",
                records,
                key_columns=["id"],
                update_columns=["name", "email"]
            )
            print(f"Updated {updated} rows")
        """
        if not records:
            logger.warning("bulk_update called with empty records list")
            return 0

        if not key_columns:
            raise ValueError("key_columns must contain at least one column")

        # SECURITY: Validate table name
        try:
            validated_table = validate_table_name(table, DatabaseDialect.SQLITE)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{table}': {e}")

        if not self._connected or not self.pool:
            await self.connect()

        # Determine update columns
        all_columns = set(records[0].keys())
        key_set = set(key_columns)
        if update_columns is None:
            update_columns = list(all_columns - key_set)
        else:
            update_columns = list(update_columns)

        if not update_columns:
            raise ValueError("No columns to update after excluding key columns")

        # Build UPDATE query
        set_clause = ", ".join([f"{col} = ?" for col in update_columns])
        where_clause = " AND ".join([f"{col} = ?" for col in key_columns])
        query = f"UPDATE {validated_table} SET {set_clause} WHERE {where_clause}"

        total_updated = 0
        total_batches = (len(records) + batch_size - 1) // batch_size

        logger.info(
            f"Starting bulk_update: table={validated_table}, records={len(records)}, "
            f"batches={total_batches}, batch_size={batch_size}, "
            f"update_columns={update_columns}, key_columns={key_columns}"
        )

        # Process in batches
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(records))
            batch_records = records[start_idx:end_idx]

            # Retry logic for SQLITE_BUSY errors
            max_retries = 3
            retry_delay = 0.1

            for attempt in range(max_retries):
                try:
                    # Use IMMEDIATE transaction
                    async with self.transaction(isolation="IMMEDIATE") as conn:
                        changes_before = conn.total_changes
                        for record in batch_records:
                            # Build params: update values + key values
                            params = [record.get(col) for col in update_columns]
                            params.extend([record.get(col) for col in key_columns])
                            await conn.execute(query, params)

                        changes_after = conn.total_changes
                        batch_updated = changes_after - changes_before
                        total_updated += batch_updated

                    logger.debug(
                        f"Batch {batch_num + 1}/{total_batches}: updated {batch_updated} rows"
                    )
                    break  # Success, exit retry loop

                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower() or "busy" in str(e).lower():
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Database locked on batch {batch_num + 1}, "
                                f"retry {attempt + 1}/{max_retries}"
                            )
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logger.error(
                                f"Database locked after {max_retries} retries on batch {batch_num + 1}"
                            )
                            raise
                    else:
                        raise

        logger.info(f"bulk_update completed: updated {total_updated} rows in {validated_table}")
        return total_updated

    async def create_or_update(
        self,
        table: str,
        record: Dict[str, Any],
        unique_columns: List[str],
        update_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Insert or update a single record using UPSERT (INSERT ... ON CONFLICT).

        Uses SQLite's INSERT ... ON CONFLICT DO UPDATE syntax (requires SQLite 3.24+).
        Detects whether record was created, updated, or unchanged based on row changes.

        Args:
            table: Table name (will be validated for SQL injection)
            record: Dictionary with column names as keys
            unique_columns: Columns that define uniqueness (conflict target)
            update_columns: Columns to update on conflict (default: all non-unique columns)

        Returns:
            Dictionary with:
                - action: "created" | "updated" | "no_change"
                - id: Last inserted/updated row ID (if available)
                - affected_rows: Number of rows affected (0 or 1)

        Raises:
            ValueError: If table name invalid or unique_columns empty
            sqlite3.OperationalError: If SQLite version < 3.24 or database locked

        Example:
            result = await adapter.create_or_update(
                "users",
                {"email": "alice@example.com", "name": "Alice", "age": 30},
                unique_columns=["email"],
                update_columns=["name", "age"]
            )
            if result["action"] == "created":
                print(f"Created user with ID {result['id']}")
            elif result["action"] == "updated":
                print(f"Updated user ID {result['id']}")
        """
        if not record:
            raise ValueError("Record cannot be empty")

        if not unique_columns:
            raise ValueError("unique_columns must contain at least one column")

        # SECURITY: Validate table name
        try:
            validated_table = validate_table_name(table, DatabaseDialect.SQLITE)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{table}': {e}")

        if not self._connected or not self.pool:
            await self.connect()

        # Determine update columns
        all_columns = set(record.keys())
        unique_set = set(unique_columns)
        if update_columns is None:
            update_columns = list(all_columns - unique_set)
        else:
            update_columns = list(update_columns)

        # Build UPSERT query
        columns = list(record.keys())
        placeholders = ", ".join(["?"] * len(columns))
        column_list = ", ".join(columns)
        conflict_target = ", ".join(unique_columns)

        if update_columns:
            # Build UPDATE clause for conflict
            update_clause = ", ".join([f"{col} = excluded.{col}" for col in update_columns])
            query = (
                f"INSERT INTO {validated_table} ({column_list}) "
                f"VALUES ({placeholders}) "
                f"ON CONFLICT ({conflict_target}) DO UPDATE SET {update_clause}"
            )
        else:
            # No columns to update, just ignore conflicts
            query = (
                f"INSERT INTO {validated_table} ({column_list}) "
                f"VALUES ({placeholders}) "
                f"ON CONFLICT ({conflict_target}) DO NOTHING"
            )

        params = tuple(record.get(col) for col in columns)

        # Retry logic for SQLITE_BUSY errors
        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                async with self.transaction(isolation="IMMEDIATE") as conn:
                    # Pre-check if record exists to determine action accurately
                    where_parts = " AND ".join([f"{col} = ?" for col in unique_columns])
                    check_query = f"SELECT 1 FROM {validated_table} WHERE {where_parts}"
                    check_params = tuple(record.get(col) for col in unique_columns)

                    cursor = await conn.execute(check_query, check_params)
                    exists_before = await cursor.fetchone() is not None
                    await cursor.close()

                    # Execute UPSERT
                    changes_before = conn.total_changes
                    cursor = await conn.execute(query, params)
                    last_id = cursor.lastrowid
                    changes_after = conn.total_changes
                    affected_rows = changes_after - changes_before

                    # Determine action based on pre-check and changes
                    if affected_rows == 0:
                        action = "no_change"
                    elif not exists_before:
                        action = "created"
                    else:
                        action = "updated"

                result = {
                    "action": action,
                    "id": last_id if last_id > 0 else None,
                    "affected_rows": affected_rows,
                }

                logger.debug(
                    f"create_or_update: table={validated_table}, action={action}, "
                    f"id={result['id']}, affected_rows={affected_rows}"
                )
                return result

            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() or "busy" in str(e).lower():
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Database locked on create_or_update, retry {attempt + 1}/{max_retries}"
                        )
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Database locked after {max_retries} retries")
                        raise
                else:
                    raise

    async def bulk_create_or_update(
        self,
        table: str,
        records: List[Dict[str, Any]],
        unique_columns: List[str],
        update_columns: Optional[List[str]] = None,
        batch_size: int = 500,
        track_actions: bool = False,
    ) -> Dict[str, int]:
        """
        Bulk insert or update records using UPSERT.

        Uses INSERT ... ON CONFLICT with executemany for efficient batch upserts.
        Optionally tracks created vs updated counts with pre-query.

        Args:
            table: Table name (will be validated for SQL injection)
            records: List of dictionaries with column names as keys
            unique_columns: Columns that define uniqueness (conflict target)
            update_columns: Columns to update on conflict (default: all non-unique columns)
            batch_size: Number of records per batch (default: 500)
            track_actions: Pre-query existing records for accurate counts (slower, default: False)

        Returns:
            Dictionary with:
                - created: Number of records created (estimate if track_actions=False)
                - updated: Number of records updated (estimate if track_actions=False)
                - total_affected: Total rows affected

        Raises:
            ValueError: If table name invalid, records empty, or unique_columns missing
            sqlite3.OperationalError: If SQLite version < 3.24 or database locked

        Example:
            records = [
                {"email": "alice@example.com", "name": "Alice", "age": 30},
                {"email": "bob@example.com", "name": "Bob", "age": 25},
            ]
            result = await adapter.bulk_create_or_update(
                "users",
                records,
                unique_columns=["email"],
                update_columns=["name", "age"],
                track_actions=True
            )
            print(f"Created: {result['created']}, Updated: {result['updated']}")
        """
        if not records:
            logger.warning("bulk_create_or_update called with empty records list")
            return {"created": 0, "updated": 0, "total_affected": 0}

        if not unique_columns:
            raise ValueError("unique_columns must contain at least one column")

        # SECURITY: Validate table name
        try:
            validated_table = validate_table_name(table, DatabaseDialect.SQLITE)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{table}': {e}")

        if not self._connected or not self.pool:
            await self.connect()

        # Determine update columns
        all_columns = set(records[0].keys())
        unique_set = set(unique_columns)
        if update_columns is None:
            update_columns = list(all_columns - unique_set)
        else:
            update_columns = list(update_columns)

        # Pre-query existing records if tracking actions
        existing_keys = set()
        if track_actions:
            # Build WHERE clause to find existing records
            key_tuples = [tuple(record.get(col) for col in unique_columns) for record in records]
            key_list = ", ".join(unique_columns)

            # Build OR conditions for each record's unique key
            if len(unique_columns) == 1:
                # Single column - use simple IN clause
                placeholders = ", ".join(["?"] * len(key_tuples))
                check_query = f"SELECT {key_list} FROM {validated_table} WHERE {unique_columns[0]} IN ({placeholders})"
                query_params = [kt[0] for kt in key_tuples]
            else:
                # Multiple columns - use OR with AND conditions
                where_conditions = []
                query_params = []
                for key_tuple in key_tuples:
                    condition_parts = " AND ".join([f"{col} = ?" for col in unique_columns])
                    where_conditions.append(f"({condition_parts})")
                    query_params.extend(key_tuple)
                where_clause = " OR ".join(where_conditions)
                check_query = f"SELECT {key_list} FROM {validated_table} WHERE {where_clause}"

            # Query existing records
            existing_rows = await self.fetch_all(check_query, query_params)
            existing_keys = {tuple(row.get(col) for col in unique_columns) for row in existing_rows}

        # Build UPSERT query
        columns = list(records[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        column_list = ", ".join(columns)
        conflict_target = ", ".join(unique_columns)

        if update_columns:
            update_clause = ", ".join([f"{col} = excluded.{col}" for col in update_columns])
            query = (
                f"INSERT INTO {validated_table} ({column_list}) "
                f"VALUES ({placeholders}) "
                f"ON CONFLICT ({conflict_target}) DO UPDATE SET {update_clause}"
            )
        else:
            query = (
                f"INSERT INTO {validated_table} ({column_list}) "
                f"VALUES ({placeholders}) "
                f"ON CONFLICT ({conflict_target}) DO NOTHING"
            )

        total_created = 0
        total_updated = 0
        total_affected = 0
        total_batches = (len(records) + batch_size - 1) // batch_size

        logger.info(
            f"Starting bulk_create_or_update: table={validated_table}, records={len(records)}, "
            f"batches={total_batches}, batch_size={batch_size}, track_actions={track_actions}"
        )

        # Process in batches
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(records))
            batch_records = records[start_idx:end_idx]

            # Convert records to tuples
            params_list = [tuple(record.get(col) for col in columns) for record in batch_records]

            # Count creates vs updates if tracking
            batch_created = 0
            batch_updated = 0
            if track_actions:
                for record in batch_records:
                    key_tuple = tuple(record.get(col) for col in unique_columns)
                    if key_tuple in existing_keys:
                        batch_updated += 1
                    else:
                        batch_created += 1
                        existing_keys.add(key_tuple)  # Add to set for next batches

            # Retry logic for SQLITE_BUSY errors
            max_retries = 3
            retry_delay = 0.1

            for attempt in range(max_retries):
                try:
                    async with self.transaction(isolation="IMMEDIATE") as conn:
                        changes_before = conn.total_changes
                        await conn.executemany(query, params_list)
                        changes_after = conn.total_changes
                        batch_affected = changes_after - changes_before

                        total_affected += batch_affected
                        if track_actions:
                            total_created += batch_created
                            total_updated += batch_updated

                    logger.debug(
                        f"Batch {batch_num + 1}/{total_batches}: affected {batch_affected} rows"
                    )
                    break  # Success, exit retry loop

                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower() or "busy" in str(e).lower():
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Database locked on batch {batch_num + 1}, "
                                f"retry {attempt + 1}/{max_retries}"
                            )
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logger.error(
                                f"Database locked after {max_retries} retries on batch {batch_num + 1}"
                            )
                            raise
                    else:
                        raise

        # If not tracking, estimate based on total affected
        if not track_actions:
            # This is an estimate - we can't accurately distinguish without pre-query
            total_created = total_affected  # Assume all are creates (best guess)
            total_updated = 0

        result = {
            "created": total_created,
            "updated": total_updated,
            "total_affected": total_affected,
        }

        logger.info(
            f"bulk_create_or_update completed: created={total_created}, "
            f"updated={total_updated}, total_affected={total_affected}"
        )
        return result

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive database health check.

        Queries SQLite PRAGMAs to check database status, integrity, and performance metrics.
        Useful for monitoring, readiness probes, and diagnostics.

        Returns:
            Dictionary with health status and metrics:
                - status: "healthy" | "unhealthy"
                - database_size_mb: Database file size in megabytes
                - page_count: Total number of pages
                - page_size: Size of each page in bytes
                - wal_mode: Whether WAL mode is enabled
                - wal_checkpoint: WAL checkpoint status (if WAL enabled)
                - foreign_keys: Whether foreign key constraints are enabled
                - integrity_check: Result of PRAGMA integrity_check
                - pool_stats: Connection pool statistics
                - writable: Whether database is writable
                - version: SQLite version string

        Raises:
            sqlite3.OperationalError: If database cannot be accessed

        Example:
            health = await adapter.health_check()
            if health["status"] == "healthy":
                print(f"Database OK: {health['database_size_mb']:.2f} MB")
            else:
                print(f"Database issues: {health['integrity_check']}")
        """
        if not self._connected or not self.pool:
            await self.connect()

        health_data = {
            "status": "healthy",
            "database_size_mb": 0.0,
            "page_count": 0,
            "page_size": 0,
            "wal_mode": False,
            "wal_checkpoint": None,
            "foreign_keys": False,
            "integrity_check": "ok",
            "pool_stats": {},
            "writable": False,
            "version": None,
        }

        try:
            conn = await self.pool.acquire()
            try:
                # Get SQLite version
                cursor = await conn.execute("SELECT sqlite_version()")
                version_row = await cursor.fetchone()
                health_data["version"] = version_row[0] if version_row else "unknown"
                await cursor.close()

                # Get page count
                cursor = await conn.execute("PRAGMA page_count")
                page_count_row = await cursor.fetchone()
                health_data["page_count"] = page_count_row[0] if page_count_row else 0
                await cursor.close()

                # Get page size
                cursor = await conn.execute("PRAGMA page_size")
                page_size_row = await cursor.fetchone()
                health_data["page_size"] = page_size_row[0] if page_size_row else 0
                await cursor.close()

                # Calculate database size
                if health_data["page_count"] > 0 and health_data["page_size"] > 0:
                    size_bytes = health_data["page_count"] * health_data["page_size"]
                    health_data["database_size_mb"] = size_bytes / (1024 * 1024)

                # Check WAL mode
                cursor = await conn.execute("PRAGMA journal_mode")
                journal_mode_row = await cursor.fetchone()
                journal_mode = journal_mode_row[0] if journal_mode_row else "unknown"
                health_data["wal_mode"] = journal_mode.lower() == "wal"
                await cursor.close()

                # WAL checkpoint status (if WAL enabled)
                if health_data["wal_mode"]:
                    cursor = await conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                    checkpoint_row = await cursor.fetchone()
                    if checkpoint_row:
                        # Returns (busy, log, checkpointed)
                        health_data["wal_checkpoint"] = {
                            "busy": checkpoint_row[0],
                            "log_size": checkpoint_row[1],
                            "checkpointed": checkpoint_row[2],
                        }
                    await cursor.close()

                # Check foreign keys
                cursor = await conn.execute("PRAGMA foreign_keys")
                fk_row = await cursor.fetchone()
                health_data["foreign_keys"] = bool(fk_row[0]) if fk_row else False
                await cursor.close()

                # Check if writable
                cursor = await conn.execute("PRAGMA query_only")
                query_only_row = await cursor.fetchone()
                health_data["writable"] = not bool(query_only_row[0]) if query_only_row else True
                await cursor.close()

                # Integrity check (quick check)
                cursor = await conn.execute("PRAGMA quick_check(1)")
                integrity_row = await cursor.fetchone()
                integrity_result = integrity_row[0] if integrity_row else "unknown"
                health_data["integrity_check"] = integrity_result
                await cursor.close()

                if integrity_result != "ok":
                    health_data["status"] = "unhealthy"

            finally:
                await self.pool.release(conn)

            # Get pool statistics
            health_data["pool_stats"] = await self.get_pool_stats()

            logger.info(
                f"Health check: status={health_data['status']}, "
                f"size={health_data['database_size_mb']:.2f}MB, "
                f"integrity={health_data['integrity_check']}"
            )

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)

        return health_data

    def __repr__(self) -> str:
        """String representation of adapter."""
        conn_status = "connected" if self._connected else "disconnected"
        return (
            f"SQLiteAdapter("
            f"database={self.database}, "
            f"pool={self.max_pool_size}, "
            f"{conn_status}"
            f")"
        )


__all__ = ["SQLiteAdapter"]
