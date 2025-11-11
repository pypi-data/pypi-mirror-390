"""
MySQL Database Adapter

Production-ready MySQL/MariaDB adapter using aiomysql for high-performance async operations.
Supports connection pooling, transactions, and MySQL-specific features.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple, Union

import aiomysql

from ..security.sql_validator import (
    DatabaseDialect,
    validate_schema_name,
    validate_table_name,
)
from .base import DatabaseAdapter

logger = logging.getLogger(__name__)


class MySQLAdapter(DatabaseAdapter):
    """
    High-performance MySQL/MariaDB database adapter using aiomysql.

    Features:
    - Async/await support with aiomysql
    - Connection pooling (5-100 connections)
    - Automatic retries with exponential backoff
    - Transaction management with isolation levels
    - MySQL-specific types (JSON, DATETIME, etc.)
    - Streaming cursor support for large datasets
    - Comprehensive error handling

    Example:
        adapter = MySQLAdapter(
            host='localhost',
            port=3306,
            database='mydb',
            user='root',
            password='secret',
            min_pool_size=5,
            max_pool_size=20
        )
        await adapter.connect()
        result = await adapter.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com")
        )
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        database: str = "mysql",
        user: str = "root",
        password: str = "",
        charset: str = "utf8mb4",
        min_pool_size: int = 5,
        max_pool_size: int = 20,
        connect_timeout: float = 10.0,
        autocommit: bool = False,
        ssl: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize MySQL adapter.

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Username
            password: Password
            charset: Character set (default: utf8mb4 for full Unicode support)
            min_pool_size: Minimum pool connections (default: 5)
            max_pool_size: Maximum pool connections (default: 20)
            connect_timeout: Connection timeout in seconds
            autocommit: Enable autocommit mode
            ssl: SSL configuration dictionary
            **kwargs: Additional aiomysql connection parameters
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.charset = charset
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.connect_timeout = connect_timeout
        self.autocommit = autocommit
        self.ssl = ssl
        self.extra_params = kwargs

        self.pool: Optional[aiomysql.Pool] = None
        self._connected = False

    async def connect(self) -> None:
        """
        Establish connection pool to MySQL database.

        Creates a connection pool with configured min/max sizes.
        Includes retry logic for transient connection failures.

        Raises:
            aiomysql.Error: If connection fails after retries
        """
        if self._connected and self.pool:
            return

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Connecting to MySQL: {self.user}@{self.host}:{self.port}/{self.database} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                # Prepare connection parameters
                conn_params = {
                    "host": self.host,
                    "port": self.port,
                    "user": self.user,
                    "password": self.password,
                    "db": self.database,
                    "charset": self.charset,
                    "minsize": self.min_pool_size,
                    "maxsize": self.max_pool_size,
                    "connect_timeout": self.connect_timeout,
                    "autocommit": self.autocommit,
                }

                # Add SSL configuration if specified
                if self.ssl:
                    conn_params["ssl"] = self.ssl

                # Add extra parameters
                conn_params.update(self.extra_params)

                # Create connection pool
                self.pool = await aiomysql.create_pool(**conn_params)

                # Test connection
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute("SELECT 1")

                self._connected = True
                logger.info(
                    f"Connected to MySQL: {self.database} "
                    f"(pool size: {self.min_pool_size}-{self.max_pool_size})"
                )
                return

            except aiomysql.Error as e:
                logger.warning(f"MySQL connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to MySQL after {max_retries} attempts")
                    raise

    async def disconnect(self) -> None:
        """
        Close all connections in the pool.

        Gracefully closes all active connections and releases resources.
        """
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            self._connected = False
            logger.info(f"Disconnected from MySQL: {self.database}")

    async def execute(self, query: str, params: Optional[Union[Tuple, List]] = None) -> int:
        """
        Execute a SQL command (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query with %s placeholders
            params: Query parameters

        Returns:
            Number of affected rows

        Example:
            rows_affected = await adapter.execute(
                "UPDATE users SET active = %s WHERE id = %s",
                (True, 42)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        conn = None

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    affected_rows = cursor.rowcount
                    await conn.commit()
                    logger.debug(f"Executed: {query[:100]}... -> {affected_rows} rows affected")
                    return affected_rows

        except aiomysql.Error as e:
            # CRITICAL: Rollback transaction to release locks
            if conn:
                try:
                    await conn.rollback()
                    logger.debug(f"Rolled back transaction after error: {e}")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

            logger.error(f"Execute failed: {query[:100]}... Error: {e}")
            raise

    async def execute_insert(self, query: str, params: Optional[Union[Tuple, List]] = None) -> int:
        """
        Execute an INSERT command and return the last insert ID.

        Args:
            query: SQL INSERT query with %s placeholders
            params: Query parameters

        Returns:
            Last inserted row ID (auto_increment value)

        Example:
            user_id = await adapter.execute_insert(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                ("Alice", "alice@example.com")
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()
        conn = None

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    last_id = cursor.lastrowid
                    await conn.commit()
                    logger.debug(f"Executed insert: {query[:100]}... -> last_id={last_id}")
                    return last_id

        except aiomysql.Error as e:
            # CRITICAL: Rollback transaction to release locks
            if conn:
                try:
                    await conn.rollback()
                    logger.debug(f"Rolled back transaction after error: {e}")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

            logger.error(f"Execute insert failed: {query[:100]}... Error: {e}")
            raise

    async def fetch_one(
        self, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row as a dictionary.

        Args:
            query: SQL query with %s placeholders
            params: Query parameters

        Returns:
            Dictionary with column names as keys, or None if no rows

        Example:
            user = await adapter.fetch_one(
                "SELECT * FROM users WHERE id = %s",
                (42,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    row = await cursor.fetchone()
                    if row:
                        logger.debug(f"Fetched one: {query[:100]}... -> 1 row")
                        return dict(row)
                    logger.debug(f"Fetched one: {query[:100]}... -> None")
                    return None

        except aiomysql.Error as e:
            logger.error(f"Fetch one failed: {query[:100]}... Error: {e}")
            raise

    async def fetch_all(
        self, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows as list of dictionaries.

        Args:
            query: SQL query with %s placeholders
            params: Query parameters

        Returns:
            List of dictionaries with column names as keys

        Example:
            users = await adapter.fetch_all(
                "SELECT * FROM users WHERE active = %s",
                (True,)
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        params = params or ()

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    rows = await cursor.fetchall()
                    result = [dict(row) for row in rows]
                    logger.debug(f"Fetched all: {query[:100]}... -> {len(result)} rows")
                    return result

        except aiomysql.Error as e:
            logger.error(f"Fetch all failed: {query[:100]}... Error: {e}")
            raise

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

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    row = await cursor.fetchone()
                    if row:
                        value = row[column] if len(row) > column else None
                        logger.debug(f"Fetched value: {query[:100]}... -> {value}")
                        return value
                    return None

        except aiomysql.Error as e:
            logger.error(f"Fetch value failed: {query[:100]}... Error: {e}")
            raise

    @asynccontextmanager
    async def transaction(self, isolation: Optional[str] = None):
        """
        Context manager for database transactions.

        Args:
            isolation: Transaction isolation level
                - 'READ UNCOMMITTED'
                - 'READ COMMITTED'
                - 'REPEATABLE READ' (MySQL default)
                - 'SERIALIZABLE'

        Yields:
            aiomysql.Connection: Database connection within transaction

        Example:
            async with adapter.transaction(isolation='SERIALIZABLE') as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("INSERT INTO users ...")
                    await cursor.execute("UPDATE accounts ...")
                # Automatically commits on success, rolls back on exception
        """
        if not self._connected or not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            # Set isolation level if specified
            if isolation:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation}")

            # Start transaction
            await conn.begin()

            try:
                yield conn
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

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
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                [
                    ("Alice", "alice@example.com"),
                    ("Bob", "bob@example.com"),
                    ("Charlie", "charlie@example.com"),
                ]
            )
        """
        if not self._connected or not self.pool:
            await self.connect()

        conn = None

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.executemany(query, params_list)
                    affected_rows = cursor.rowcount
                    await conn.commit()
                    logger.debug(
                        f"Executed many: {query[:100]}... with {len(params_list)} param sets "
                        f"-> {affected_rows} rows affected"
                    )
                    return affected_rows

        except aiomysql.Error as e:
            # CRITICAL: Rollback transaction to release locks
            if conn:
                try:
                    await conn.rollback()
                    logger.debug(f"Rolled back transaction after error: {e}")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

            logger.error(f"Execute many failed: {query[:100]}... Error: {e}")
            raise

    async def stream_query(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        chunk_size: int = 1000,
    ):
        """
        Stream query results in chunks for large datasets.

        Memory-efficient for processing millions of rows using SSCursor.

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

        try:
            async with self.pool.acquire() as conn:
                # Use SSCursor (streaming cursor) to avoid loading all rows
                # into memory
                async with conn.cursor(aiomysql.SSCursor) as cursor:
                    await cursor.execute(query, params)

                    while True:
                        rows = await cursor.fetchmany(chunk_size)
                        if not rows:
                            break

                        # Get column names from cursor description
                        columns = [desc[0] for desc in cursor.description]

                        # Convert rows to dictionaries
                        result = [dict(zip(columns, row)) for row in rows]
                        yield result

        except aiomysql.Error as e:
            logger.error(f"Stream query failed: {query[:100]}... Error: {e}")
            raise

    async def get_table_info(
        self, table_name: str, database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get column information for a table.

        Args:
            table_name: Table name
            database: Database name (default: current database)

        Returns:
            List of column info dictionaries with keys:
                - Field: column name
                - Type: data type
                - Null: YES or NO
                - Key: PRI, UNI, MUL, or empty
                - Default: default value
                - Extra: auto_increment, etc.
        """
        database = database or self.database
        # SECURITY FIX: Validate identifiers to prevent SQL injection
        validated_database = validate_schema_name(database, DatabaseDialect.MYSQL)
        validated_table = validate_table_name(table_name, DatabaseDialect.MYSQL)

        query = f"SHOW COLUMNS FROM `{validated_database}`.`{validated_table}`"
        return await self.fetch_all(query)

    async def table_exists(self, table_name: str, database: Optional[str] = None) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Table name
            database: Database name (default: current database)

        Returns:
            True if table exists
        """
        database = database or self.database
        query = """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
        """
        count = await self.fetch_value(query, (database, table_name))
        return count > 0

    async def get_version(self) -> str:
        """
        Get MySQL server version.

        Returns:
            Version string (e.g., "8.0.32-MySQL")
        """
        return await self.fetch_value("SELECT VERSION()")

    async def get_database_list(self) -> List[str]:
        """
        Get list of all databases.

        Returns:
            List of database names
        """
        rows = await self.fetch_all("SHOW DATABASES")
        return [row["Database"] for row in rows]

    async def get_table_list(self, database: Optional[str] = None) -> List[str]:
        """
        Get list of tables in a database.

        Args:
            database: Database name (default: current database)

        Returns:
            List of table names
        """
        database = database or self.database
        # SECURITY FIX: Validate database name to prevent SQL injection
        validated_database = validate_schema_name(database, DatabaseDialect.MYSQL)

        rows = await self.fetch_all(f"SHOW TABLES FROM `{validated_database}`")
        key = f"Tables_in_{validated_database}"
        return [row[key] for row in rows]

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
            "size": self.pool.size,
            "free": self.pool.freesize,
            "used": self.pool.size - self.pool.freesize,
        }

    async def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """
        Optimize a table (defragment, update statistics).

        Args:
            table_name: Table name

        Returns:
            Result dictionary with optimization status
        """
        # SECURITY FIX: Validate table name to prevent SQL injection
        validated_table = validate_table_name(table_name, DatabaseDialect.MYSQL)

        result = await self.fetch_one(f"OPTIMIZE TABLE `{validated_table}`")
        return result

    async def analyze_table(self, table_name: str) -> Dict[str, Any]:
        """
        Analyze a table (update key distribution statistics).

        Args:
            table_name: Table name

        Returns:
            Result dictionary with analysis status
        """
        # SECURITY FIX: Validate table name to prevent SQL injection
        validated_table = validate_table_name(table_name, DatabaseDialect.MYSQL)

        result = await self.fetch_one(f"ANALYZE TABLE `{validated_table}`")
        return result

    async def execute_with_retry(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        max_retries: int = 5,
        initial_backoff: float = 1.0,
        max_backoff: float = 32.0,
        exponential_base: float = 2.0,
    ) -> int:
        """
        Execute query with automatic retry and exponential backoff.

        Automatically retries on transient errors:
        - Connection lost (2006, 2013)
        - Deadlock detected (1213)
        - Lock wait timeout (1205)
        - Server gone away (2006)

        Args:
            query: SQL query
            params: Query parameters
            max_retries: Maximum retry attempts (default: 5)
            initial_backoff: Initial backoff in seconds (default: 1.0)
            max_backoff: Maximum backoff in seconds (default: 32.0)
            exponential_base: Backoff multiplier (default: 2.0)

        Returns:
            Number of affected rows

        Raises:
            aiomysql.Error: If all retries exhausted

        Example:
            # Will automatically retry on transient errors
            rows = await adapter.execute_with_retry(
                "UPDATE accounts SET balance = balance - %s WHERE id = %s",
                (100, 42),
                max_retries=5
            )
        """
        # Retriable MySQL error codes
        RETRIABLE_ERRORS = {
            1205,  # Lock wait timeout exceeded
            1213,  # Deadlock found when trying to get lock
            2006,  # MySQL server has gone away
            2013,  # Lost connection to MySQL server during query
        }

        last_error = None
        backoff = initial_backoff

        for attempt in range(max_retries):
            try:
                result = await self.execute(query, params)
                if attempt > 0:
                    logger.info(f"Query succeeded after {attempt + 1} attempts: {query[:100]}...")
                return result

            except aiomysql.Error as e:
                last_error = e
                error_code = getattr(e, "args", [None])[0]

                # Check if error is retriable
                if error_code not in RETRIABLE_ERRORS:
                    logger.error(f"Non-retriable error {error_code}: {e}")
                    raise

                # Last attempt - don't retry
                if attempt == max_retries - 1:
                    logger.error(f"Query failed after {max_retries} attempts: {query[:100]}...")
                    raise

                # Log retry attempt
                logger.warning(
                    f"Retriable error {error_code} on attempt {attempt + 1}/{max_retries}: {e}. "
                    f"Retrying in {backoff:.2f}s..."
                )

                # Wait with exponential backoff
                await asyncio.sleep(backoff)

                # Increase backoff for next attempt
                backoff = min(backoff * exponential_base, max_backoff)

        # Should never reach here, but just in case
        raise last_error

    async def parse_binlog_events(
        self,
        server_id: int = 1,
        log_file: Optional[str] = None,
        log_pos: int = 4,
        blocking: bool = False,
        only_events: Optional[List[str]] = None,
        skip_to_timestamp: Optional[int] = None,
    ):
        """
        Parse MySQL binary log events for replication and change data capture.

        This is a simplified binlog parser for common use cases. For production
        CDC (Change Data Capture), consider using dedicated tools like Debezium.

        Args:
            server_id: Server ID for binlog connection (default: 1)
            log_file: Binary log file name (e.g., 'mysql-bin.000001')
            log_pos: Starting position in log file (default: 4)
            blocking: Whether to block and wait for new events
            only_events: List of event types to include (e.g., ['write', 'update', 'delete'])
            skip_to_timestamp: Skip events before this Unix timestamp

        Yields:
            Dictionary with event information:
                - log_file: Binary log file name
                - log_pos: Position in log file
                - timestamp: Event timestamp
                - event_type: Type of event (insert, update, delete)
                - schema: Database name
                - table: Table name
                - rows: Affected row data

        Example:
            async for event in adapter.parse_binlog_events(
                server_id=1,
                log_file='mysql-bin.000001',
                only_events=['write', 'update', 'delete']
            ):
                print(f"Event: {event['event_type']} on {event['schema']}.{event['table']}")
                print(f"Rows: {event['rows']}")

        Note:
            Requires 'pymysqlreplication' package:
            pip install pymysql-replication

            MySQL server must have binlog enabled:
            [mysqld]
            log-bin=mysql-bin
            binlog_format=ROW
            server-id=1
        """
        try:
            from pymysqlreplication import BinLogStreamReader
            from pymysqlreplication.row_event import (
                DeleteRowsEvent,
                UpdateRowsEvent,
                WriteRowsEvent,
            )
        except ImportError:
            raise ImportError(
                "Binary log parsing requires 'pymysql-replication' package. "
                "Install it with: pip install pymysql-replication"
            )

        # Map event types
        event_type_map = {
            WriteRowsEvent: "insert",
            UpdateRowsEvent: "update",
            DeleteRowsEvent: "delete",
        }

        # Build event filter
        if only_events:
            event_filter = []
            if "write" in only_events or "insert" in only_events:
                event_filter.append(WriteRowsEvent)
            if "update" in only_events:
                event_filter.append(UpdateRowsEvent)
            if "delete" in only_events:
                event_filter.append(DeleteRowsEvent)
        else:
            event_filter = [WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent]

        # Connection settings for binlog reader
        mysql_settings = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "passwd": self.password,
        }

        # Create binlog stream
        stream = BinLogStreamReader(
            connection_settings=mysql_settings,
            server_id=server_id,
            log_file=log_file,
            log_pos=log_pos,
            blocking=blocking,
            only_events=event_filter,
            skip_to_timestamp=skip_to_timestamp,
        )

        logger.info(
            f"Starting binlog parsing from {log_file or 'current'}:{log_pos} "
            f"with events: {only_events or 'all'}"
        )

        try:
            for binlog_event in stream:
                event_type = event_type_map.get(type(binlog_event))
                if not event_type:
                    continue

                # Extract event data
                event_data = {
                    "log_file": binlog_event.packet.log_file,
                    "log_pos": binlog_event.packet.log_pos,
                    "timestamp": binlog_event.timestamp,
                    "event_type": event_type,
                    "schema": binlog_event.schema,
                    "table": binlog_event.table,
                    "rows": [],
                }

                # Extract row data based on event type
                if isinstance(binlog_event, WriteRowsEvent):
                    # INSERT events
                    for row in binlog_event.rows:
                        event_data["rows"].append({"values": row["values"]})

                elif isinstance(binlog_event, UpdateRowsEvent):
                    # UPDATE events
                    for row in binlog_event.rows:
                        event_data["rows"].append(
                            {"before": row["before_values"], "after": row["after_values"]}
                        )

                elif isinstance(binlog_event, DeleteRowsEvent):
                    # DELETE events
                    for row in binlog_event.rows:
                        event_data["rows"].append({"values": row["values"]})

                yield event_data

        finally:
            stream.close()
            logger.info("Binlog stream closed")

    async def get_replication_status(self) -> Dict[str, Any]:
        """
        Get MySQL replication status.

        Returns:
            Dictionary with replication information:
                - log_file: Current binary log file
                - log_pos: Current position in binary log
                - binlog_format: Binary log format (ROW, STATEMENT, MIXED)

        Example:
            status = await adapter.get_replication_status()
            print(f"Current binlog: {status['log_file']} at {status['log_pos']}")
        """
        # Check if binlog is enabled
        binlog_enabled = await self.fetch_value("SELECT @@log_bin")

        if not binlog_enabled:
            return {
                "enabled": False,
                "log_file": None,
                "log_pos": None,
                "binlog_format": None,
            }

        # Get master status
        master_status = await self.fetch_one("SHOW MASTER STATUS")

        if not master_status:
            return {
                "enabled": True,
                "log_file": None,
                "log_pos": None,
                "binlog_format": await self.fetch_value("SELECT @@binlog_format"),
            }

        return {
            "enabled": True,
            "log_file": master_status.get("File"),
            "log_pos": master_status.get("Position"),
            "binlog_format": await self.fetch_value("SELECT @@binlog_format"),
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on MySQL connection and server.

        Returns:
            Dictionary with health check results:
                - status: 'healthy' or 'unhealthy'
                - connected: Connection status
                - version: MySQL version
                - uptime: Server uptime in seconds
                - threads: Number of threads connected
                - queries: Total queries executed
                - slow_queries: Number of slow queries
                - pool_size: Current pool size
                - pool_free: Number of free connections

        Example:
            health = await adapter.health_check()
            if health['status'] == 'healthy':
                print(f"MySQL is healthy - Version: {health['version']}")
        """
        try:
            if not self._connected or not self.pool:
                await self.connect()

            # Test basic connectivity
            await self.fetch_value("SELECT 1")

            # Get server status
            status_vars = await self.fetch_all("SHOW STATUS")
            status_dict = {row["Variable_name"]: row["Value"] for row in status_vars}

            # Get version
            version = await self.get_version()

            # Get pool stats
            pool_stats = await self.get_pool_stats()

            return {
                "status": "healthy",
                "connected": True,
                "version": version,
                "uptime": int(status_dict.get("Uptime", 0)),
                "threads": int(status_dict.get("Threads_connected", 0)),
                "queries": int(status_dict.get("Queries", 0)),
                "slow_queries": int(status_dict.get("Slow_queries", 0)),
                "pool_size": pool_stats["size"],
                "pool_free": pool_stats["free"],
                "pool_used": pool_stats["used"],
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
            }

    async def bulk_create(
        self, table: str, records: List[Dict[str, Any]], ignore_duplicates: bool = False
    ) -> int:
        """
        Bulk insert multiple records efficiently.

        Args:
            table: Table name
            records: List of dictionaries with column-value pairs
            ignore_duplicates: If True, use INSERT IGNORE to skip duplicates

        Returns:
            Number of rows inserted

        Example:
            rows = await adapter.bulk_create(
                'users',
                [
                    {'name': 'Alice', 'email': 'alice@example.com', 'age': 28},
                    {'name': 'Bob', 'email': 'bob@example.com', 'age': 35},
                    {'name': 'Charlie', 'email': 'charlie@example.com', 'age': 42}
                ]
            )
            print(f"Inserted {rows} users")
        """
        if not records:
            return 0

        # SECURITY FIX: Validate table name to prevent SQL injection
        validated_table = validate_table_name(table, DatabaseDialect.MYSQL)

        # Get column names from first record (assume all records have same structure)
        columns = list(records[0].keys())

        # Build INSERT query
        columns_str = ", ".join([f"`{col}`" for col in columns])
        placeholders = ", ".join(["%s"] * len(columns))

        if ignore_duplicates:
            query = f"INSERT IGNORE INTO `{validated_table}` ({columns_str}) VALUES ({placeholders})"
        else:
            query = f"INSERT INTO `{validated_table}` ({columns_str}) VALUES ({placeholders})"

        # Prepare parameter list
        params_list = [[record[col] for col in columns] for record in records]

        # Execute batch insert
        affected = await self.execute_many(query, params_list)

        logger.info(f"Bulk created {affected} records in table '{table}'")
        return affected

    async def bulk_update(
        self,
        table: str,
        records: List[Dict[str, Any]],
        key_columns: List[str],
        update_columns: Optional[List[str]] = None,
    ) -> int:
        """
        Bulk update multiple records efficiently.

        Updates records based on key columns. If update_columns is None,
        all columns except keys are updated.

        Args:
            table: Table name
            records: List of dictionaries with column-value pairs
            key_columns: Columns to use for identifying records (WHERE clause)
            update_columns: Columns to update (if None, updates all except keys)

        Returns:
            Total number of rows updated

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

            # Update by multiple keys
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
            return 0

        # SECURITY FIX: Validate table name to prevent SQL injection
        validated_table = validate_table_name(table, DatabaseDialect.MYSQL)

        # Determine columns to update
        all_columns = list(records[0].keys())
        if update_columns is None:
            update_columns = [col for col in all_columns if col not in key_columns]

        # Build UPDATE queries for each record
        total_affected = 0

        for record in records:
            # Build SET clause
            set_parts = [f"`{col}` = %s" for col in update_columns]
            set_clause = ", ".join(set_parts)

            # Build WHERE clause
            where_parts = [f"`{col}` = %s" for col in key_columns]
            where_clause = " AND ".join(where_parts)

            query = f"UPDATE `{validated_table}` SET {set_clause} WHERE {where_clause}"

            # Prepare parameters: update values + key values
            params = [record[col] for col in update_columns] + [record[col] for col in key_columns]

            # Execute update
            affected = await self.execute(query, params)
            total_affected += affected

        logger.info(f"Bulk updated {total_affected} records in table '{table}'")
        return total_affected

    async def create_or_update(
        self,
        table: str,
        record: Dict[str, Any],
        unique_columns: List[str],
        update_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Insert record or update if it exists (UPSERT operation).

        Uses MySQL's INSERT ... ON DUPLICATE KEY UPDATE syntax.

        Args:
            table: Table name
            record: Dictionary with column-value pairs
            unique_columns: Columns that define uniqueness (must have UNIQUE constraint)
            update_columns: Columns to update on conflict (if None, updates all except unique)

        Returns:
            Dictionary with:
                - action: 'created' or 'updated'
                - id: Last insert ID (for created) or None
                - affected_rows: Number of rows affected

        Example:
            # Upsert by email (email must have UNIQUE constraint)
            result = await adapter.create_or_update(
                'users',
                {'email': 'alice@example.com', 'name': 'Alice', 'age': 28},
                unique_columns=['email']
            )
            print(f"Action: {result['action']}")

            # Upsert with specific update columns
            result = await adapter.create_or_update(
                'products',
                {'sku': 'LAPTOP-001', 'name': 'Laptop Pro', 'price': 1299.99, 'stock': 50},
                unique_columns=['sku'],
                update_columns=['price', 'stock']  # Only update these on conflict
            )
        """
        # SECURITY FIX: Validate table name to prevent SQL injection
        validated_table = validate_table_name(table, DatabaseDialect.MYSQL)

        # Determine columns to update on conflict
        all_columns = list(record.keys())
        if update_columns is None:
            update_columns = [col for col in all_columns if col not in unique_columns]

        # Build INSERT clause
        columns_str = ", ".join([f"`{col}`" for col in all_columns])
        placeholders = ", ".join(["%s"] * len(all_columns))

        # Build ON DUPLICATE KEY UPDATE clause using alias syntax (MySQL 8.0.19+)
        # Old deprecated syntax: VALUES(`col`)
        # New syntax: alias.col
        update_parts = [f"`{col}` = new_data.`{col}`" for col in update_columns]
        update_clause = ", ".join(update_parts)

        query = (
            f"INSERT INTO `{validated_table}` ({columns_str}) "
            f"VALUES ({placeholders}) AS new_data "
            f"ON DUPLICATE KEY UPDATE {update_clause}"
        )

        # Prepare parameters
        params = [record[col] for col in all_columns]

        # Execute query
        if not self._connected or not self.pool:
            await self.connect()

        conn = None

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    affected_rows = cursor.rowcount
                    last_id = cursor.lastrowid
                    await conn.commit()

                    # Determine action based on affected rows
                    # affected_rows == 1: INSERT (created)
                    # affected_rows == 2: UPDATE (updated)
                    # affected_rows == 0: No change (duplicate values)
                    if affected_rows == 1:
                        action = "created"
                    elif affected_rows == 2:
                        action = "updated"
                    else:
                        action = "no_change"

                    result = {
                        "action": action,
                        "id": last_id if action == "created" else None,
                        "affected_rows": affected_rows,
                    }

                    logger.debug(
                        f"Create or update in '{table}': {action} "
                        f"(affected: {affected_rows}, id: {last_id})"
                    )

                    return result

        except aiomysql.Error as e:
            # CRITICAL: Rollback transaction to release locks
            if conn:
                try:
                    await conn.rollback()
                    logger.debug(f"Rolled back transaction after error: {e}")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

            logger.error(f"Create or update failed in '{table}': {e}")
            raise

    async def bulk_create_or_update(
        self,
        table: str,
        records: List[Dict[str, Any]],
        unique_columns: List[str],
        update_columns: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        Bulk insert or update multiple records (UPSERT).

        Uses MySQL's INSERT ... ON DUPLICATE KEY UPDATE for efficient batch upserts.

        Args:
            table: Table name
            records: List of dictionaries with column-value pairs
            unique_columns: Columns that define uniqueness
            update_columns: Columns to update on conflict

        Returns:
            Dictionary with:
                - created: Approximate number of created records
                - updated: Approximate number of updated records
                - total_affected: Total rows affected

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
            return {"created": 0, "updated": 0, "total_affected": 0}

        # SECURITY FIX: Validate table name to prevent SQL injection
        validated_table = validate_table_name(table, DatabaseDialect.MYSQL)

        # Determine columns to update on conflict
        all_columns = list(records[0].keys())
        if update_columns is None:
            update_columns = [col for col in all_columns if col not in unique_columns]

        # Build INSERT clause
        columns_str = ", ".join([f"`{col}`" for col in all_columns])
        placeholders = ", ".join(["%s"] * len(all_columns))

        # Build ON DUPLICATE KEY UPDATE clause using alias syntax (MySQL 8.0.19+)
        # Old deprecated syntax: VALUES(`col`)
        # New syntax: alias.col
        update_parts = [f"`{col}` = new_data.`{col}`" for col in update_columns]
        update_clause = ", ".join(update_parts)

        query = (
            f"INSERT INTO `{validated_table}` ({columns_str}) "
            f"VALUES ({placeholders}) AS new_data "
            f"ON DUPLICATE KEY UPDATE {update_clause}"
        )

        # Prepare parameter list
        params_list = [[record[col] for col in all_columns] for record in records]

        # Execute batch upsert
        if not self._connected or not self.pool:
            await self.connect()

        conn = None

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.executemany(query, params_list)
                    affected_rows = cursor.rowcount
                    await conn.commit()

                    # Approximate created/updated counts
                    # This is approximate because executemany doesn't give us per-row info
                    # affected_rows counts: 1 per insert, 2 per update
                    # So: created ≈ records that added 1, updated ≈ records that added 2
                    approximate_updated = max(0, affected_rows - len(records))
                    approximate_created = len(records) - approximate_updated

                    result = {
                        "created": approximate_created,
                        "updated": approximate_updated,
                        "total_affected": affected_rows,
                    }

                    logger.info(
                        f"Bulk create_or_update in '{table}': "
                        f"{approximate_created} created, {approximate_updated} updated "
                        f"(total affected: {affected_rows})"
                    )

                    return result

        except aiomysql.Error as e:
            # CRITICAL: Rollback transaction to release locks
            if conn:
                try:
                    await conn.rollback()
                    logger.debug(f"Rolled back transaction after error: {e}")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

            logger.error(f"Bulk create_or_update failed in '{table}': {e}")
            raise

    def __repr__(self) -> str:
        """String representation of adapter."""
        conn_status = "connected" if self._connected else "disconnected"
        return (
            f"MySQLAdapter("
            f"{self.user}@{self.host}:{self.port}/{self.database}, "
            f"pool={self.min_pool_size}-{self.max_pool_size}, "
            f"{conn_status}"
            f")"
        )


__all__ = ["MySQLAdapter"]
