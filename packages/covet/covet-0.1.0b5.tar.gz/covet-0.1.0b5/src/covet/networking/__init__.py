"""
Low-level networking utilities for CovetPy.

Provides network protocol implementations and utilities.
"""

from typing import Any, Optional


class NetworkProtocol:
    """Base network protocol."""

    async def send(self, data: bytes):
        """Send data over network."""
        pass

    async def receive(self, size: int = 4096) -> bytes:
        """Receive data from network."""
        return b""


__all__ = ["NetworkProtocol"]
