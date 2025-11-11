"""
CovetPy Simple Database System

A minimal but functional database system focused on PostgreSQL with asyncpg.
Provides basic connection management, query execution, and connection pooling.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncContextManager, Dict, List, Optional

# Optional asyncpg support
try:
    import asyncpg

    HAS_ASYNCPG = True
except ImportError:
    asyncpg = None
    HAS_ASYNCPG = False

from ..core.exceptions import DatabaseError
from .core.database_config import DatabaseConfig, DatabaseConfigManager, DatabaseType

logger = logging.getLogger(__name__)


@dataclass
class SimpleDatabaseConfig:
    """Simple configuration for the database system."""

    host: str = "localhost"
    port: int = 5432
    database: str = "covet"
    username: str = "covet"
    password: str = ""
    min_pool_size: int = 5
    max_pool_size: int = 20
    command_timeout: int = 60


class SimplePostgreSQLAdapter:
    """Simple PostgreSQL adapter using asyncpg."""

    def __init__(self, config: SimpleDatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.is_connected = False

    async def connect(self) -> None:
        """Connect to the database and create connection pool."""
        if not HAS_ASYNCPG:
            raise DatabaseError(
                "asyncpg is required for PostgreSQL connections. Install with: pip install asyncpg"
            )

        try:
            dsn = f"postgresql://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"

            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=self.config.min_pool_size,
                max_size=self.config.max_pool_size,
                command_timeout=self.config.command_timeout,
            )

            # Test connection
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")

            self.is_connected = True
            logger.info(
                f"Connected to PostgreSQL: {self.config.host}:{self.config.port}/{self.config.database}"
            )

        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise DatabaseError(f"Database connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self.is_connected = False
            logger.info("Disconnected from PostgreSQL")

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        if not self.pool:
            raise DatabaseError("Database not connected")

        async with self.pool.acquire() as conn:
            yield conn

    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        async with self.get_connection() as conn:
            try:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise DatabaseError(f"Query failed: {e}")

    async def execute_command(self, command: str, *args) -> str:
        """Execute an INSERT/UPDATE/DELETE command."""
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(command, *args)
                return result
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                raise DatabaseError(f"Command failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            if not self.is_connected:
                return {"healthy": False, "error": "Not connected"}

            async with self.get_connection() as conn:
                await conn.execute("SELECT 1")

            return {
                "healthy": True,
                "connected": True,
                "pool_size": len(self.pool._holders) if self.pool else 0,
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}


class SimpleDatabaseSystem:
    """
    Simple database system with PostgreSQL support.

    Provides basic functionality:
    - Connection management
    - Query execution
    - Connection pooling
    - Health checks
    """

    def __init__(self):
        self.config: Optional[SimpleDatabaseConfig] = None
        self.adapter: Optional[SimplePostgreSQLAdapter] = None
        self.is_initialized = False
        self._initialization_time: Optional[float] = None

    async def initialize(self, config_dict: Dict[str, Any]) -> None:
        """Initialize the database system."""
        if self.is_initialized:
            logger.warning("Database system already initialized")
            return

        start_time = time.time()
        logger.info("Initializing simple database system...")

        try:
            # Parse configuration
            self.config = SimpleDatabaseConfig(**config_dict)

            # Create adapter
            self.adapter = SimplePostgreSQLAdapter(self.config)

            # Connect to database
            await self.adapter.connect()

            self.is_initialized = True
            self._initialization_time = time.time() - start_time

            logger.info(
                f"Database system initialized successfully in {self._initialization_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Failed to initialize database system: {e}")
            await self.shutdown()
            raise

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection."""
        if not self.adapter:
            raise DatabaseError("Database system not initialized")

        async with self.adapter.get_connection() as conn:
            yield conn

    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query."""
        if not self.adapter:
            raise DatabaseError("Database system not initialized")

        return await self.adapter.execute_query(query, *args)

    async def execute_command(self, command: str, *args) -> str:
        """Execute an INSERT/UPDATE/DELETE command."""
        if not self.adapter:
            raise DatabaseError("Database system not initialized")

        return await self.adapter.execute_command(command, *args)

    async def health_check(self) -> Dict[str, Any]:
        """Check system health."""
        if not self.adapter:
            return {"healthy": False, "error": "Not initialized"}

        adapter_health = await self.adapter.health_check()

        return {
            "system": {
                "initialized": self.is_initialized,
                "initialization_time": self._initialization_time,
                "healthy": adapter_health.get("healthy", False),
            },
            "database": adapter_health,
        }

    async def shutdown(self) -> None:
        """Shutdown the database system."""
        logger.info("Shutting down database system...")

        if self.adapter:
            try:
                await self.adapter.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting from database: {e}")

        self.is_initialized = False
        logger.info("Database system shutdown complete")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        """Async context manager exit."""
        await self.shutdown()


# Global database system instance
_simple_db_system: Optional[SimpleDatabaseSystem] = None


async def initialize_simple_database(config: Dict[str, Any]) -> SimpleDatabaseSystem:
    """Initialize the global simple database system."""
    global _simple_db_system

    if _simple_db_system and _simple_db_system.is_initialized:
        logger.warning("Simple database system already initialized")
        return _simple_db_system

    _simple_db_system = SimpleDatabaseSystem()
    await _simple_db_system.initialize(config)

    return _simple_db_system


def get_simple_database() -> SimpleDatabaseSystem:
    """Get the global simple database system instance."""
    if _simple_db_system is None or not _simple_db_system.is_initialized:
        raise DatabaseError(
            "Simple database system not initialized. Call initialize_simple_database() first."
        )

    return _simple_db_system


async def shutdown_simple_database() -> None:
    """Shutdown the global simple database system."""
    global _simple_db_system

    if _simple_db_system:
        await _simple_db_system.shutdown()
        _simple_db_system = None
