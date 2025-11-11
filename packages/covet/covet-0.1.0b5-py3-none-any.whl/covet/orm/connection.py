"""
Database Connection Management

Production-ready connection pooling, transaction management, and database adapters.
"""

import asyncio
import logging
import queue
import threading
import time
import weakref
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import Any, AsyncContextManager, ContextManager, Dict, List, Optional, Union

from .exceptions import ConnectionError, ORMError, TransactionError

logger = logging.getLogger(__name__)


@dataclass
class ConnectionConfig:
    """Database connection configuration."""

    engine: str
    host: str = "localhost"
    port: Optional[int] = None
    database: str = ""
    username: str = ""
    password: str = ""
    charset: str = "utf8mb4"

    # Connection pool settings
    min_connections: int = 1
    max_connections: int = 10
    max_idle_time: int = 300  # 5 minutes
    connection_timeout: int = 30
    pool_recycle: int = 3600  # 1 hour

    # SSL settings
    ssl_mode: str = "preferred"
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    ssl_ca: Optional[str] = None

    # Additional options
    options: Dict[str, Any] = None

    def __post_init__(self):
        if self.options is None:
            self.options = {}
        if self.port is None:
            self.port = self._get_default_port()

    def _get_default_port(self) -> int:
        """Get default port for the database engine."""
        defaults = {
            "postgresql": 5432,
            "mysql": 3306,
            "sqlite": 0,  # No port for SQLite
        }
        return defaults.get(self.engine, 0)

    def get_dsn(self) -> str:
        """Get database DSN."""
        if self.engine == "sqlite":
            return f"sqlite:///{self.database}"
        elif self.engine == "postgresql":
            dsn = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.engine == "mysql":
            dsn = f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database engine: {self.engine}")

        if self.options:
            params = "&".join([f"{k}={v}" for k, v in self.options.items()])
            dsn += f"?{params}"

        return dsn


class DatabaseConnection:
    """Wrapper for database connections."""

    def __init__(self, raw_connection, config: ConnectionConfig, created_at: float = None):
        self.raw_connection = raw_connection
        self.config = config
        self.created_at = created_at or time.time()
        self.last_used = self.created_at
        self.in_use = False
        self.transaction_level = 0
        self._closed = False

    def execute(self, sql: str, params: Optional[List[Any]] = None) -> Any:
        """Execute SQL query."""
        self.last_used = time.time()
        try:
            cursor = self.raw_connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            raise ConnectionError(f"Query execution failed: {e}")

    async def aexecute(self, sql: str, params: Optional[List[Any]] = None) -> Any:
        """Execute SQL query asynchronously."""
        self.last_used = time.time()
        try:
            cursor = await self.raw_connection.cursor()
            if params:
                await cursor.execute(sql, params)
            else:
                await cursor.execute(sql)
            return cursor
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            raise ConnectionError(f"Query execution failed: {e}")

    def commit(self):
        """Commit transaction."""
        try:
            self.raw_connection.commit()
        except Exception as e:
            logger.error(f"Commit error: {e}")
            raise TransactionError(f"Commit failed: {e}")

    async def acommit(self):
        """Commit transaction asynchronously."""
        try:
            await self.raw_connection.commit()
        except Exception as e:
            logger.error(f"Commit error: {e}")
            raise TransactionError(f"Commit failed: {e}")

    def rollback(self):
        """Rollback transaction."""
        try:
            self.raw_connection.rollback()
        except Exception as e:
            logger.error(f"Rollback error: {e}")
            raise TransactionError(f"Rollback failed: {e}")

    async def arollback(self):
        """Rollback transaction asynchronously."""
        try:
            await self.raw_connection.rollback()
        except Exception as e:
            logger.error(f"Rollback error: {e}")
            raise TransactionError(f"Rollback failed: {e}")

    def close(self):
        """Close the connection."""
        if not self._closed:
            try:
                self.raw_connection.close()
                self._closed = True
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

    async def aclose(self):
        """Close the connection asynchronously."""
        if not self._closed:
            try:
                await self.raw_connection.close()
                self._closed = True
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

    def is_expired(self) -> bool:
        """Check if connection is expired."""
        if self._closed:
            return True
        now = time.time()
        return (now - self.last_used) > self.config.max_idle_time

    def is_stale(self) -> bool:
        """Check if connection should be recycled."""
        if self._closed:
            return True
        now = time.time()
        return (now - self.created_at) > self.config.pool_recycle

    @property
    def is_closed(self) -> bool:
        """Check if connection is closed."""
        return self._closed


class ConnectionPool:
    """Thread-safe connection pool."""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._pool = queue.Queue(maxsize=config.max_connections)
        self._connections = weakref.WeakSet()
        self._lock = threading.RLock()
        self._total_connections = 0
        self._closed = False

        # Initialize minimum connections
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool."""
        for _ in range(self.config.min_connections):
            try:
                conn = self._create_connection()
                self._pool.put(conn)
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
                break

    def _create_connection(self) -> DatabaseConnection:
        """Create a new database connection."""
        if self.config.engine == "sqlite":
            import sqlite3

            raw_conn = sqlite3.connect(self.config.database)
            raw_conn.row_factory = sqlite3.Row
        elif self.config.engine == "postgresql":
            try:
                import psycopg2
                import psycopg2.extras

                raw_conn = psycopg2.connect(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.username,
                    password=self.config.password,
                    **self.config.options,
                )
                raw_conn.cursor_factory = psycopg2.extras.RealDictCursor
            except ImportError:
                raise ConnectionError("psycopg2 is required for PostgreSQL connections")
        elif self.config.engine == "mysql":
            try:
                import pymysql

                raw_conn = pymysql.connect(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.username,
                    password=self.config.password,
                    charset=self.config.charset,
                    cursorclass=pymysql.cursors.DictCursor,
                    **self.config.options,
                )
            except ImportError:
                raise ConnectionError("PyMySQL is required for MySQL connections")
        else:
            raise ConnectionError(f"Unsupported database engine: {self.config.engine}")

        conn = DatabaseConnection(raw_conn, self.config)
        self._connections.add(conn)

        with self._lock:
            self._total_connections += 1

        return conn

    def get_connection(self, timeout: Optional[float] = None) -> DatabaseConnection:
        """Get a connection from the pool."""
        if self._closed:
            raise ConnectionError("Connection pool is closed")

        timeout = timeout or self.config.connection_timeout

        try:
            # Try to get an existing connection
            conn = self._pool.get(timeout=timeout)

            # Check if connection is still valid
            if conn.is_expired() or conn.is_stale():
                conn.close()
                conn = self._create_connection()

            conn.in_use = True
            return conn

        except queue.Empty:
            # No connections available, try to create a new one
            with self._lock:
                if self._total_connections < self.config.max_connections:
                    conn = self._create_connection()
                    conn.in_use = True
                    return conn

            raise ConnectionError("No connections available and maximum pool size reached")

    def return_connection(self, conn: DatabaseConnection):
        """Return a connection to the pool."""
        if conn.is_closed or conn.is_expired() or conn.is_stale():
            conn.close()
            with self._lock:
                self._total_connections -= 1
            return

        conn.in_use = False

        try:
            # Reset connection state
            if conn.transaction_level > 0:
                conn.rollback()
                conn.transaction_level = 0

            self._pool.put_nowait(conn)
        except queue.Full:
            # Pool is full, close the connection
            conn.close()
            with self._lock:
                self._total_connections -= 1

    def close_all(self):
        """Close all connections in the pool."""
        self._closed = True

        # Close connections in the pool
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except queue.Empty:
                break

        # Close any remaining connections
        for conn in list(self._connections):
            if not conn.is_closed:
                conn.close()

        with self._lock:
            self._total_connections = 0

    @contextmanager
    def connection(self):
        """Context manager for getting a connection."""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.return_connection(conn)

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return {
            "total_connections": self._total_connections,
            "available_connections": self._pool.qsize(),
            "in_use_connections": self._total_connections - self._pool.qsize(),
            "max_connections": self.config.max_connections,
            "min_connections": self.config.min_connections,
        }


class AsyncConnectionPool:
    """Async connection pool."""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._pool = asyncio.Queue(maxsize=config.max_connections)
        self._connections = weakref.WeakSet()
        self._lock = asyncio.Lock()
        self._total_connections = 0
        self._closed = False

    async def _initialize_pool(self):
        """Initialize the connection pool."""
        for _ in range(self.config.min_connections):
            try:
                conn = await self._create_connection()
                await self._pool.put(conn)
            except Exception as e:
                logger.error(f"Failed to initialize async connection pool: {e}")
                break

    async def _create_connection(self) -> DatabaseConnection:
        """Create a new async database connection."""
        if self.config.engine == "postgresql":
            try:
                import asyncpg

                raw_conn = await asyncpg.connect(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.username,
                    password=self.config.password,
                    **self.config.options,
                )
            except ImportError:
                raise ConnectionError("asyncpg is required for async PostgreSQL connections")
        elif self.config.engine == "mysql":
            try:
                import aiomysql

                raw_conn = await aiomysql.connect(
                    host=self.config.host,
                    port=self.config.port,
                    db=self.config.database,
                    user=self.config.username,
                    password=self.config.password,
                    charset=self.config.charset,
                    **self.config.options,
                )
            except ImportError:
                raise ConnectionError("aiomysql is required for async MySQL connections")
        elif self.config.engine == "sqlite":
            try:
                import aiosqlite

                raw_conn = await aiosqlite.connect(self.config.database)
            except ImportError:
                raise ConnectionError("aiosqlite is required for async SQLite connections")
        else:
            raise ConnectionError(f"Unsupported async database engine: {self.config.engine}")

        conn = DatabaseConnection(raw_conn, self.config)
        self._connections.add(conn)

        async with self._lock:
            self._total_connections += 1

        return conn

    async def get_connection(self, timeout: Optional[float] = None) -> DatabaseConnection:
        """Get a connection from the pool."""
        if self._closed:
            raise ConnectionError("Connection pool is closed")

        timeout = timeout or self.config.connection_timeout

        try:
            # Try to get an existing connection
            conn = await asyncio.wait_for(self._pool.get(), timeout=timeout)

            # Check if connection is still valid
            if conn.is_expired() or conn.is_stale():
                await conn.aclose()
                conn = await self._create_connection()

            conn.in_use = True
            return conn

        except asyncio.TimeoutError:
            # No connections available, try to create a new one
            async with self._lock:
                if self._total_connections < self.config.max_connections:
                    conn = await self._create_connection()
                    conn.in_use = True
                    return conn

            raise ConnectionError("No connections available and maximum pool size reached")

    async def return_connection(self, conn: DatabaseConnection):
        """Return a connection to the pool."""
        if conn.is_closed or conn.is_expired() or conn.is_stale():
            await conn.aclose()
            async with self._lock:
                self._total_connections -= 1
            return

        conn.in_use = False

        try:
            # Reset connection state
            if conn.transaction_level > 0:
                await conn.arollback()
                conn.transaction_level = 0

            await self._pool.put(conn)
        except asyncio.QueueFull:
            # Pool is full, close the connection
            await conn.aclose()
            async with self._lock:
                self._total_connections -= 1

    async def close_all(self):
        """Close all connections in the pool."""
        self._closed = True

        # Close connections in the pool
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                await conn.aclose()
            except asyncio.QueueEmpty:
                break

        # Close any remaining connections
        for conn in list(self._connections):
            if not conn.is_closed:
                await conn.aclose()

        async with self._lock:
            self._total_connections = 0

    @asynccontextmanager
    async def connection(self):
        """Async context manager for getting a connection."""
        conn = await self.get_connection()
        try:
            yield conn
        finally:
            await self.return_connection(conn)


class TransactionManager:
    """Transaction management."""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection

    @contextmanager
    def transaction(self, savepoint: Optional[str] = None):
        """Transaction context manager."""
        if savepoint and self.connection.transaction_level > 0:
            # Use savepoint for nested transactions
            self.connection.execute(f"SAVEPOINT {savepoint}")
            try:
                self.connection.transaction_level += 1
                yield
                self.connection.execute(f"RELEASE SAVEPOINT {savepoint}")
            except Exception:
                self.connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                raise
            finally:
                self.connection.transaction_level -= 1
        else:
            # Use full transaction
            try:
                if self.connection.transaction_level == 0:
                    # Start new transaction
                    self.connection.execute("BEGIN")
                self.connection.transaction_level += 1
                yield
                if self.connection.transaction_level == 1:
                    self.connection.commit()
            except Exception:
                if self.connection.transaction_level == 1:
                    self.connection.rollback()
                raise
            finally:
                self.connection.transaction_level = max(0, self.connection.transaction_level - 1)

    @asynccontextmanager
    async def atransaction(self, savepoint: Optional[str] = None):
        """Async transaction context manager."""
        if savepoint and self.connection.transaction_level > 0:
            # Use savepoint for nested transactions
            await self.connection.aexecute(f"SAVEPOINT {savepoint}")
            try:
                self.connection.transaction_level += 1
                yield
                await self.connection.aexecute(f"RELEASE SAVEPOINT {savepoint}")
            except Exception:
                await self.connection.aexecute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                raise
            finally:
                self.connection.transaction_level -= 1
        else:
            # Use full transaction
            try:
                if self.connection.transaction_level == 0:
                    # Start new transaction
                    await self.connection.aexecute("BEGIN")
                self.connection.transaction_level += 1
                yield
                if self.connection.transaction_level == 1:
                    await self.connection.acommit()
            except Exception:
                if self.connection.transaction_level == 1:
                    await self.connection.arollback()
                raise
            finally:
                self.connection.transaction_level = max(0, self.connection.transaction_level - 1)


# Global connection registry
_connection_pools: Dict[str, Union[ConnectionPool, AsyncConnectionPool]] = {}


def register_database(name: str, config: ConnectionConfig, async_pool: bool = False):
    """Register a database connection pool."""
    if async_pool:
        pool = AsyncConnectionPool(config)
    else:
        pool = ConnectionPool(config)
    _connection_pools[name] = pool
    return pool


def get_connection_pool(
    name: str = "default",
) -> Union[ConnectionPool, AsyncConnectionPool]:
    """Get a connection pool by name."""
    if name not in _connection_pools:
        raise ConnectionError(f"Database '{name}' not registered")
    return _connection_pools[name]


def close_all_connections():
    """Close all connection pools."""
    for pool in _connection_pools.values():
        if isinstance(pool, AsyncConnectionPool):
            asyncio.create_task(pool.close_all())
        else:
            pool.close_all()
    _connection_pools.clear()
