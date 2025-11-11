"""
Enterprise Connection Pool Integration Examples

Demonstrates integration of ConnectionPool with various database adapters:
- PostgreSQL with asyncpg
- MySQL with aiomysql
- SQLite with aiosqlite
- Custom adapters

Based on 20 years of production database experience.
"""

import asyncio
import logging
from typing import Any, Optional

from covet.database.core.connection_pool import (
    ConnectionPool,
    PoolConfig,
    ConnectionProtocol,
)

# Import database adapters
try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

try:
    import aiomysql
    HAS_AIOMYSQL = True
except ImportError:
    HAS_AIOMYSQL = False

try:
    import aiosqlite
    HAS_AIOSQLITE = True
except ImportError:
    HAS_AIOSQLITE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# PostgreSQL Connection Pool Integration
# ============================================================================

class PostgreSQLConnection:
    """Wrapper for PostgreSQL connection implementing ConnectionProtocol."""

    def __init__(self, conn: 'asyncpg.Connection'):
        self._conn = conn

    async def ping(self) -> bool:
        """Test if connection is alive."""
        try:
            await self._conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close the connection."""
        await self._conn.close()

    async def execute(self, query: str, *args):
        """Execute a query."""
        return await self._conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch query results."""
        return await self._conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch single row."""
        return await self._conn.fetchrow(query, *args)


async def create_postgresql_pool_example():
    """
    Example: PostgreSQL connection pool integration.

    Uses asyncpg for high-performance PostgreSQL connections.
    """
    if not HAS_ASYNCPG:
        logger.warning("asyncpg not installed. Skipping PostgreSQL example.")
        return

    logger.info("="*80)
    logger.info("PostgreSQL Connection Pool Example")
    logger.info("="*80)

    async def connection_factory():
        """Factory to create PostgreSQL connections."""
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='postgres',
            database='testdb'
        )
        return PostgreSQLConnection(conn)

    # Configure pool
    config = PoolConfig(
        min_size=5,
        max_size=20,
        acquire_timeout=10.0,
        idle_timeout=300.0,
        max_lifetime=1800.0,
        pre_ping=True,
        auto_scale=True,
    )

    # Create pool
    pool = ConnectionPool(connection_factory, config, "postgresql_pool")

    try:
        await pool.initialize()
        logger.info(f"Pool initialized: {pool}")

        # Use connection
        async with pool.acquire() as conn:
            result = await conn.execute("SELECT version()")
            logger.info(f"PostgreSQL version query executed: {result}")

            # Fetch data
            rows = await conn.fetch("SELECT * FROM users LIMIT 5")
            logger.info(f"Fetched {len(rows)} rows")

        # Get pool statistics
        stats = pool.get_stats()
        logger.info(f"Pool stats: {stats.to_dict()}")

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        await pool.close()
        logger.info("Pool closed")


# ============================================================================
# MySQL Connection Pool Integration
# ============================================================================

class MySQLConnection:
    """Wrapper for MySQL connection implementing ConnectionProtocol."""

    def __init__(self, conn: 'aiomysql.Connection'):
        self._conn = conn

    async def ping(self) -> bool:
        """Test if connection is alive."""
        try:
            await self._conn.ping()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close the connection."""
        self._conn.close()
        await self._conn.ensure_closed()

    async def execute(self, query: str, args=None):
        """Execute a query."""
        async with self._conn.cursor() as cursor:
            await cursor.execute(query, args)
            await self._conn.commit()
            return cursor.rowcount

    async def fetchall(self, query: str, args=None):
        """Fetch all results."""
        async with self._conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchall()

    async def fetchone(self, query: str, args=None):
        """Fetch single result."""
        async with self._conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchone()


async def create_mysql_pool_example():
    """
    Example: MySQL connection pool integration.

    Uses aiomysql for MySQL/MariaDB connections.
    """
    if not HAS_AIOMYSQL:
        logger.warning("aiomysql not installed. Skipping MySQL example.")
        return

    logger.info("="*80)
    logger.info("MySQL Connection Pool Example")
    logger.info("="*80)

    async def connection_factory():
        """Factory to create MySQL connections."""
        conn = await aiomysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            db='testdb',
            charset='utf8mb4'
        )
        return MySQLConnection(conn)

    # Configure pool
    config = PoolConfig(
        min_size=5,
        max_size=20,
        acquire_timeout=10.0,
        idle_timeout=300.0,
        max_lifetime=1800.0,
        pre_ping=True,
        auto_scale=True,
    )

    # Create pool
    pool = ConnectionPool(connection_factory, config, "mysql_pool")

    try:
        await pool.initialize()
        logger.info(f"Pool initialized: {pool}")

        # Use connection
        async with pool.acquire() as conn:
            result = await conn.fetchone("SELECT VERSION() as version")
            logger.info(f"MySQL version: {result}")

            # Execute query
            rows = await conn.fetchall("SELECT * FROM users LIMIT 5")
            logger.info(f"Fetched {len(rows)} rows")

        # Get pool statistics
        stats = pool.get_stats()
        logger.info(f"Pool stats: {stats.to_dict()}")

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        await pool.close()
        logger.info("Pool closed")


# ============================================================================
# SQLite Connection Pool Integration
# ============================================================================

class SQLiteConnection:
    """Wrapper for SQLite connection implementing ConnectionProtocol."""

    def __init__(self, conn: 'aiosqlite.Connection'):
        self._conn = conn

    async def ping(self) -> bool:
        """Test if connection is alive."""
        try:
            await self._conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close the connection."""
        await self._conn.close()

    async def execute(self, query: str, parameters=None):
        """Execute a query."""
        if parameters:
            await self._conn.execute(query, parameters)
        else:
            await self._conn.execute(query)
        await self._conn.commit()

    async def fetchall(self, query: str, parameters=None):
        """Fetch all results."""
        if parameters:
            cursor = await self._conn.execute(query, parameters)
        else:
            cursor = await self._conn.execute(query)
        return await cursor.fetchall()

    async def fetchone(self, query: str, parameters=None):
        """Fetch single result."""
        if parameters:
            cursor = await self._conn.execute(query, parameters)
        else:
            cursor = await self._conn.execute(query)
        return await cursor.fetchone()


async def create_sqlite_pool_example():
    """
    Example: SQLite connection pool integration.

    Uses aiosqlite for async SQLite connections.
    """
    if not HAS_AIOSQLITE:
        logger.warning("aiosqlite not installed. Skipping SQLite example.")
        return

    logger.info("="*80)
    logger.info("SQLite Connection Pool Example")
    logger.info("="*80)

    async def connection_factory():
        """Factory to create SQLite connections."""
        conn = await aiosqlite.connect(':memory:')  # In-memory database
        # Create test table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        await conn.commit()
        return SQLiteConnection(conn)

    # Configure pool (smaller for SQLite)
    config = PoolConfig(
        min_size=2,
        max_size=10,
        acquire_timeout=5.0,
        idle_timeout=300.0,
        max_lifetime=1800.0,
        pre_ping=True,
        auto_scale=False,  # SQLite doesn't benefit from auto-scaling
    )

    # Create pool
    pool = ConnectionPool(connection_factory, config, "sqlite_pool")

    try:
        await pool.initialize()
        logger.info(f"Pool initialized: {pool}")

        # Use connection
        async with pool.acquire() as conn:
            # Insert data
            await conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                ("Alice", "alice@example.com")
            )

            # Fetch data
            rows = await conn.fetchall("SELECT * FROM users")
            logger.info(f"Fetched {len(rows)} rows: {rows}")

        # Get pool statistics
        stats = pool.get_stats()
        logger.info(f"Pool stats: {stats.to_dict()}")

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        await pool.close()
        logger.info("Pool closed")


# ============================================================================
# Advanced Usage: Multi-Database Application
# ============================================================================

async def multi_database_application():
    """
    Example: Application using multiple database pools.

    Demonstrates managing connections to multiple databases simultaneously.
    """
    logger.info("="*80)
    logger.info("Multi-Database Application Example")
    logger.info("="*80)

    from covet.database.core.connection_pool import ConnectionPoolManager

    manager = ConnectionPoolManager()

    try:
        # Create SQLite pool for local cache
        if HAS_AIOSQLITE:
            async def sqlite_factory():
                conn = await aiosqlite.connect(':memory:')
                return SQLiteConnection(conn)

            sqlite_config = PoolConfig(min_size=2, max_size=5)
            await manager.create_pool("cache", sqlite_factory, sqlite_config)
            logger.info("Created SQLite cache pool")

        # Get health summary
        health = manager.get_health_summary()
        logger.info(f"Health summary: {health}")

        # Use pools
        cache_pool = manager.get_pool("cache")
        async with cache_pool.acquire() as conn:
            await conn.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT, value TEXT)")
            await conn.execute("INSERT INTO cache VALUES (?, ?)", ("test", "value"))
            logger.info("Cached data")

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        await manager.close_all()
        logger.info("All pools closed")


# ============================================================================
# Production Monitoring Example
# ============================================================================

async def production_monitoring_example():
    """
    Example: Production monitoring and health checks.

    Demonstrates monitoring connection pool health in production.
    """
    logger.info("="*80)
    logger.info("Production Monitoring Example")
    logger.info("="*80)

    if not HAS_AIOSQLITE:
        logger.warning("aiosqlite not installed. Skipping example.")
        return

    async def connection_factory():
        conn = await aiosqlite.connect(':memory:')
        return SQLiteConnection(conn)

    config = PoolConfig(
        min_size=3,
        max_size=10,
        auto_scale=True,
        scale_check_interval=5.0,
        health_check_interval=10.0,
        leak_detection=True,
        leak_timeout=60.0,
    )

    pool = ConnectionPool(connection_factory, config, "monitored_pool")

    try:
        await pool.initialize()

        # Simulate application workload
        async def workload():
            for i in range(50):
                async with pool.acquire() as conn:
                    await conn.execute("SELECT 1")
                await asyncio.sleep(0.1)

        # Run workload
        await workload()

        # Check pool health
        stats = pool.get_stats()
        logger.info(f"Pool State: {pool.state.value}")
        logger.info(f"Total Connections: {stats.total_connections}")
        logger.info(f"Active: {stats.active_connections}")
        logger.info(f"Idle: {stats.idle_connections}")
        logger.info(f"Total Checkouts: {stats.total_checkouts:,}")
        logger.info(f"Avg Checkout Time: {stats.avg_checkout_time:.4f}s")
        logger.info(f"Failed Checkouts: {stats.failed_checkouts}")
        logger.info(f"Connection Errors: {stats.connection_errors}")

        # Metrics for Prometheus/monitoring systems
        metrics = {
            'pool_size': stats.total_connections,
            'pool_active': stats.active_connections,
            'pool_idle': stats.idle_connections,
            'pool_checkouts_total': stats.total_checkouts,
            'pool_checkout_time_avg': stats.avg_checkout_time,
            'pool_errors_total': stats.connection_errors,
        }
        logger.info(f"Prometheus metrics: {metrics}")

    finally:
        await pool.close()


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run all examples."""
    print("\n" + "#"*80)
    print("# Enterprise Connection Pool Integration Examples")
    print("#"*80 + "\n")

    examples = [
        ("PostgreSQL", create_postgresql_pool_example),
        ("MySQL", create_mysql_pool_example),
        ("SQLite", create_sqlite_pool_example),
        ("Multi-Database", multi_database_application),
        ("Monitoring", production_monitoring_example),
    ]

    for name, example_func in examples:
        try:
            print(f"\n{'='*80}")
            print(f"Running: {name} Example")
            print(f"{'='*80}\n")
            await example_func()
            print(f"\n✓ {name} example completed successfully\n")
        except Exception as e:
            print(f"\n✗ {name} example failed: {e}\n")
            import traceback
            traceback.print_exc()

    print("\n" + "#"*80)
    print("# All Examples Complete")
    print("#"*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
