"""
Server utilities for CovetPy.

Provides server implementations and utilities.
"""

from typing import Optional


class Server:
    """Base server class."""

    def __init__(
        self, host: str = "0.0.0.0", port: int = 8000
    ):  # nosec B104 - binding to all interfaces is intentional for framework
        self.host = host
        self.port = port

    async def start(self):
        """Start server."""
        pass

    async def stop(self):
        """Stop server."""
        pass


__all__ = ["Server"]


async def run_server(
    app, host: str = "0.0.0.0", port: int = 8000
):  # nosec B104 - binding to all interfaces is intentional for framework
    """Run ASGI application server."""
    try:
        import uvicorn

        uvicorn.run(app, host=host, port=port)
    except ImportError:
        print("uvicorn not installed. Install with: pip install uvicorn")


from dataclasses import dataclass

@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "info"

__all__ = ["ServerConfig"]



def create_production_server(config=None):
    """Create production server instance."""
    cfg = config or ServerConfig()
    return cfg
