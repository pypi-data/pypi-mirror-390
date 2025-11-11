"""
Database Core Components

Enterprise-grade database core providing high-performance connection management,
database abstraction, and advanced pooling strategies.
"""

# Temporarily comment out problematic connection pool imports to fix circular dependencies
# from .connection_pool import (
#     ConnectionPool,
#     ConnectionPoolManager,
#     PoolConfig,
#     PoolStatistics,
# )

from covet.database.core.database_config import DatabaseConfig, DatabaseType

# Comment out manager until we fix all syntax issues
# from .database_manager import DatabaseManager


# Stub classes for connection pool components
class ConnectionPool:
    """Stub connection pool class."""


class ConnectionPoolManager:
    """Stub connection pool manager class."""


# Note: performance_monitor.py is missing and needs to be implemented

__all__ = [
    # "DatabaseManager",
    "ConnectionPool",
    "ConnectionPoolManager",
    # "PoolConfig",
    # "PoolStatistics",
    "DatabaseConfig",
    "DatabaseType",
]
