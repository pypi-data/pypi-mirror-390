"""
CovetPy Simple Plugin System
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Plugin:
    """Simple plugin class."""

    name: str
    version: str = "1.0.0"
    enabled: bool = True


class PluginManager:
    """Simple plugin manager."""

    def __init__(self, registry=None, lifecycle=None, loader=None):
        self.plugins: Dict[str, Plugin] = {}
        self.registry = registry
        self.lifecycle = lifecycle
        self.loader = loader

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        self.plugins[plugin.name] = plugin

    def get(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self.plugins.get(name)

    def list_enabled(self) -> List[Plugin]:
        """List enabled plugins."""
        return [p for p in self.plugins.values() if p.enabled]


class PluginRegistry:
    """Simple plugin registry."""

    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.registry: Dict[str, Plugin] = {}
        self.plugin_dirs = plugin_dirs or []

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        self.registry[plugin.name] = plugin

    def get(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self.registry.get(name)
