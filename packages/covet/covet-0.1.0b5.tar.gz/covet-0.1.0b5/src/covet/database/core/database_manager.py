"""Database manager."""

class DatabaseManager:
    """Manage multiple database connections."""
    
    def __init__(self):
        self.connections = {}
    
    def add_connection(self, name, connection):
        """Add a named connection."""
        self.connections[name] = connection
    
    def get_connection(self, name="default"):
        """Get connection by name."""
        return self.connections.get(name)

__all__ = ["DatabaseManager"]



from dataclasses import dataclass

@dataclass
class DatabaseManagerConfig:
    """Database manager configuration."""
    default_connection: str = "default"
    connection_timeout: int = 10
