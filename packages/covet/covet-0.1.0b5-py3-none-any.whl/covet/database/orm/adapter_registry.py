"""
ORM Adapter Registry

Global registry for connecting ORM models to database adapters.
Manages adapter lifecycle and provides centralized access to database connections.

Example:
    from covet.database.orm.adapter_registry import get_adapter_registry, register_adapter
    from covet.database.adapters.postgresql import PostgreSQLAdapter

    # Register an adapter
    adapter = PostgreSQLAdapter(host='localhost', database='mydb')
    await register_adapter('default', adapter)

    # Models will automatically use the registered adapter
    user = await User.objects.get(id=1)
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    Global registry for database adapters.

    Manages multiple database connections and provides thread-safe access
    to adapters for ORM operations.
    """

    def __init__(self):
        """Initialize empty adapter registry."""
        self._adapters: Dict[str, any] = {}
        self._default_alias: str = "default"

    def register(self, alias: str, adapter, make_default: bool = False):
        """
        Register a database adapter.

        Args:
            alias: Database alias (e.g., 'default', 'analytics', 'cache')
            adapter: Database adapter instance
            make_default: Whether to set this as the default adapter

        Example:
            registry.register('default', PostgreSQLAdapter(...))
            registry.register('analytics', MySQLAdapter(...))
        """
        self._adapters[alias] = adapter
        logger.info(f"Registered database adapter: {alias}")

        if make_default or "default" not in self._adapters:
            self._default_alias = alias
            logger.info(f"Set default database adapter: {alias}")

    def get(self, alias: Optional[str] = None):
        """
        Get database adapter by alias.

        Args:
            alias: Database alias (uses default if None)

        Returns:
            Database adapter

        Raises:
            ValueError: If adapter not found
        """
        alias = alias or self._default_alias

        if alias not in self._adapters:
            raise ValueError(
                f"Database adapter '{alias}' not registered. "
                f"Available: {list(self._adapters.keys())}"
            )

        return self._adapters[alias]

    def unregister(self, alias: str):
        """
        Unregister a database adapter.

        Args:
            alias: Database alias to unregister
        """
        if alias in self._adapters:
            del self._adapters[alias]
            logger.info(f"Unregistered database adapter: {alias}")

    def get_default_alias(self) -> str:
        """Get the default database alias."""
        return self._default_alias

    def set_default_alias(self, alias: str):
        """
        Set the default database alias.

        Args:
            alias: Database alias to set as default

        Raises:
            ValueError: If alias not registered
        """
        if alias not in self._adapters:
            raise ValueError(f"Database adapter '{alias}' not registered")

        self._default_alias = alias
        logger.info(f"Changed default database adapter to: {alias}")

    def list_aliases(self) -> list:
        """List all registered database aliases."""
        return list(self._adapters.keys())

    def clear(self):
        """Clear all registered adapters."""
        self._adapters.clear()
        logger.info("Cleared all database adapters from registry")


# Global adapter registry instance
_adapter_registry: Optional[AdapterRegistry] = None


def get_adapter_registry() -> AdapterRegistry:
    """
    Get the global adapter registry.

    Creates the registry if it doesn't exist.

    Returns:
        Global AdapterRegistry instance
    """
    global _adapter_registry

    if _adapter_registry is None:
        _adapter_registry = AdapterRegistry()

    return _adapter_registry


def register_adapter(alias: str, adapter, make_default: bool = False):
    """
    Register a database adapter in the global registry.

    Args:
        alias: Database alias
        adapter: Database adapter instance
        make_default: Whether to set as default

    Example:
        from covet.database.adapters.postgresql import PostgreSQLAdapter

        adapter = PostgreSQLAdapter(host='localhost', database='mydb')
        await adapter.connect()
        register_adapter('default', adapter, make_default=True)
    """
    registry = get_adapter_registry()
    registry.register(alias, adapter, make_default=make_default)


def get_adapter(alias: Optional[str] = None):
    """
    Get a database adapter from the global registry.

    Args:
        alias: Database alias (uses default if None)

    Returns:
        Database adapter

    Example:
        adapter = get_adapter('default')
        results = await adapter.fetch_all("SELECT * FROM users")
    """
    registry = get_adapter_registry()
    return registry.get(alias)


async def unregister_adapter(alias: str):
    """
    Unregister a database adapter.

    Args:
        alias: Database alias to unregister
    """
    registry = get_adapter_registry()
    registry.unregister(alias)


__all__ = [
    "AdapterRegistry",
    "get_adapter_registry",
    "register_adapter",
    "get_adapter",
    "unregister_adapter",
]
