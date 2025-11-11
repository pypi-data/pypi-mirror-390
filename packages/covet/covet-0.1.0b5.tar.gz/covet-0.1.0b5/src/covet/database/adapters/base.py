"""
Base database adapter classes and utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class QueryResult:
    """Result of a database query execution."""

    success: bool
    rows: list[dict[str, Any]] = field(default_factory=list)
    affected_rows: int = 0
    execution_time: float = 0.0
    error_message: Optional[str] = None


class DatabaseAdapter:
    """Base class for database adapters."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.is_initialized = False

    async def initialize(self) -> None:
        """Initialize the database adapter."""
        pass

    async def close(self) -> None:
        """Close the database adapter."""
        self.is_initialized = False

    def update_metrics(self, execution_time: float, success: bool) -> None:
        """Update adapter metrics."""
        pass


class SqlAdapter(DatabaseAdapter):
    """Base class for SQL database adapters (PostgreSQL, MySQL, SQLite)."""

    async def execute(self, query: str, params: tuple = None) -> QueryResult:
        """Execute a SQL query."""
        return QueryResult(success=True, rows=[], affected_rows=0)

    async def fetch_one(self, query: str, params: tuple = None) -> Optional[dict]:
        """Fetch one row from a SQL query."""
        return {}

    async def fetch_all(self, query: str, params: tuple = None) -> list[dict]:
        """Fetch all rows from a SQL query."""
        return []


class NoSqlAdapter(DatabaseAdapter, Generic[T]):
    """Base class for NoSQL database adapters."""

    pass


class AdapterFactory:
    """Factory for creating database adapters."""

    _registry: dict[str, type[DatabaseAdapter]] = {}

    @classmethod
    def register_adapter(cls, db_type: str, adapter_class: type[DatabaseAdapter]) -> None:
        """Register a database adapter."""
        cls._registry[db_type] = adapter_class

    @classmethod
    def create_adapter(cls, db_type: str, config: Any) -> DatabaseAdapter:
        """Create a database adapter instance."""
        adapter_class = cls._registry.get(db_type)
        if not adapter_class:
            raise ValueError(f"No adapter registered for database type: {db_type}")
        return adapter_class(config)


class AdapterRegistry:
    """Registry for database adapters."""

    pass


def get_adapter_registry() -> AdapterRegistry:
    """Get the adapter registry."""
    return AdapterRegistry()


class DatabaseFeature:
    """Enum for database features."""

    pass


class DatabaseInfo:
    """Database information."""

    pass


def create_adapter(config: dict) -> DatabaseAdapter:
    """Create a database adapter."""
    return DatabaseAdapter(config)


def auto_detect_adapter(config: dict) -> DatabaseAdapter:
    """Auto-detect a database adapter."""
    return DatabaseAdapter(config)


def list_available_adapters() -> list[str]:
    """List available database adapters."""
    return list(AdapterFactory._registry.keys())

class TransactionContext:
    """Context manager for database transactions."""
    
    def __init__(self, adapter: DatabaseAdapter):
        self.adapter = adapter
        self.is_committed = False
        self.is_rolled_back = False
    
    async def __aenter__(self):
        """Start transaction."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End transaction."""
        if exc_type is not None and not self.is_rolled_back:
            await self.rollback()
        elif not self.is_committed and not self.is_rolled_back:
            await self.commit()
        return False
    
    async def commit(self):
        """Commit transaction."""
        self.is_committed = True
    
    async def rollback(self):
        """Rollback transaction."""
        self.is_rolled_back = True




class TransactionIsolationLevel:
    """Transaction isolation levels."""
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"
