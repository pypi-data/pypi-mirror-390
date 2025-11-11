"""
Database Adapters

Multi-database support with unified interface for PostgreSQL, MySQL,
and SQLite with optimized drivers and connection pooling.

Uses lazy imports to avoid requiring all database dependencies.
"""

from .base import AdapterFactory, DatabaseAdapter

__all__ = [
    "DatabaseAdapter",
    "AdapterFactory",
    "PostgreSQLAdapter",
    "MySQLAdapter",
    "SQLiteAdapter",
]

def __getattr__(name):
    """Lazy import database adapters to avoid requiring all dependencies."""
    if name == "SQLiteAdapter":
        from .sqlite import SQLiteAdapter
        return SQLiteAdapter
    elif name == "MySQLAdapter":
        from .mysql import MySQLAdapter
        return MySQLAdapter
    elif name == "PostgreSQLAdapter":
        from .postgresql import PostgreSQLAdapter
        return PostgreSQLAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
