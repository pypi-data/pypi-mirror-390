"""
WebSocket Per-Message Deflate Compression

This module provides RFC 7692 compliant per-message deflate compression:
- Automatic compression for messages >1KB
- Configurable compression level (1-9)
- Shared compression context for efficiency
- Sliding window management
- Memory-efficient streaming compression
- Compression ratio tracking and limits
"""

import logging
import zlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class CompressionLevel(int, Enum):
    """Compression level constants."""

    NO_COMPRESSION = 0
    FAST = 1
    DEFAULT = 6
    BEST = 9


@dataclass
class CompressionConfig:
    """Configuration for per-message deflate compression."""

    enabled: bool = True
    level: int = CompressionLevel.DEFAULT
    min_size_bytes: int = 1024  # Only compress messages >1KB
    max_window_bits: int = 15  # Maximum LZ77 sliding window size
    client_max_window_bits: int = 15
    server_max_window_bits: int = 15
    client_no_context_takeover: bool = False  # Reset compression context per message
    server_no_context_takeover: bool = False
    memory_level: int = 8  # Memory usage (1-9, default 8)
    max_compression_ratio: float = 100.0  # Bomb protection

    def __post_init__(self):
        """Validate configuration."""
        if not 0 <= self.level <= 9:
            raise ValueError("Compression level must be 0-9")
        if not 8 <= self.max_window_bits <= 15:
            raise ValueError("max_window_bits must be 8-15")
        if not 1 <= self.memory_level <= 9:
            raise ValueError("memory_level must be 1-9")


class CompressionContext:
    """
    Compression context for a WebSocket connection.

    Manages compression and decompression state with optional context takeover.
    """

    def __init__(self, config: CompressionConfig, is_client: bool = False):
        self.config = config
        self.is_client = is_client

        # Compression statistics
        self.total_compressed = 0
        self.total_uncompressed = 0
        self.compression_count = 0
        self.total_compression_time = 0.0

        # Initialize compression contexts
        self._compress_obj: Optional[zlib._Compress] = None
        self._decompress_obj: Optional[zlib._Decompress] = None

        # Compression negotiation
        self.negotiated = False
        self.peer_max_window_bits = config.max_window_bits
        self.peer_no_context_takeover = False

        self._init_contexts()

    def _init_contexts(self):
        """Initialize compression/decompression objects."""
        # Compression object
        if self.is_client:
            window_bits = -self.config.client_max_window_bits
            no_context_takeover = self.config.client_no_context_takeover
        else:
            window_bits = -self.config.server_max_window_bits
            no_context_takeover = self.config.server_no_context_takeover

        if not no_context_takeover and self._compress_obj is None:
            self._compress_obj = zlib.compressobj(
                level=self.config.level,
                method=zlib.DEFLATED,
                wbits=window_bits,
                memLevel=self.config.memory_level,
            )

        # Decompression object
        if not self.peer_no_context_takeover and self._decompress_obj is None:
            self._decompress_obj = zlib.decompressobj(wbits=-self.peer_max_window_bits)

    def should_compress(self, data_size: int) -> bool:
        """Check if data should be compressed based on size."""
        if not self.config.enabled:
            return False
        return data_size >= self.config.min_size_bytes

    def compress(self, data: bytes) -> Tuple[bytes, bool]:
        """
        Compress data using per-message deflate.

        Args:
            data: Uncompressed data

        Returns:
            (compressed_data, was_compressed) tuple
        """
        if not self.should_compress(len(data)):
            return data, False

        try:
            import time

            start_time = time.time()

            # Create compressor if needed (no context takeover)
            if self.is_client:
                no_context_takeover = self.config.client_no_context_takeover
                window_bits = -self.config.client_max_window_bits
            else:
                no_context_takeover = self.config.server_no_context_takeover
                window_bits = -self.config.server_max_window_bits

            if no_context_takeover or self._compress_obj is None:
                compress_obj = zlib.compressobj(
                    level=self.config.level,
                    method=zlib.DEFLATED,
                    wbits=window_bits,
                    memLevel=self.config.memory_level,
                )
            else:
                compress_obj = self._compress_obj

            # Compress data
            compressed = compress_obj.compress(data)
            compressed += compress_obj.flush(zlib.Z_SYNC_FLUSH)

            # Remove trailing 0x00 0x00 0xff 0xff
            if compressed[-4:] == b"\x00\x00\xff\xff":
                compressed = compressed[:-4]

            # Check compression ratio (bomb protection)
            if len(data) > 0:
                ratio = len(compressed) / len(data)
                if ratio > self.config.max_compression_ratio:
                    logger.warning(
                        f"Compression ratio {ratio:.1f} exceeds limit "
                        f"{self.config.max_compression_ratio}"
                    )
                    return data, False

            # Update statistics
            self.total_compressed += len(compressed)
            self.total_uncompressed += len(data)
            self.compression_count += 1
            self.total_compression_time += time.time() - start_time

            # Reset context if no takeover
            if no_context_takeover:
                compress_obj = None
            else:
                self._compress_obj = compress_obj

            logger.debug(
                f"Compressed {len(data)} -> {len(compressed)} bytes "
                f"({len(compressed)/len(data)*100:.1f}%)"
            )

            return compressed, True

        except Exception as e:
            logger.error(f"Compression error: {e}")
            return data, False

    def decompress(self, data: bytes) -> bytes:
        """
        Decompress data using per-message deflate.

        Args:
            data: Compressed data

        Returns:
            Decompressed data

        Raises:
            zlib.error: If decompression fails
        """
        try:
            # Create decompressor if needed
            if self.peer_no_context_takeover or self._decompress_obj is None:
                decompress_obj = zlib.decompressobj(wbits=-self.peer_max_window_bits)
            else:
                decompress_obj = self._decompress_obj

            # Add trailing bytes required by zlib
            data += b"\x00\x00\xff\xff"

            # Decompress
            decompressed = decompress_obj.decompress(data)

            # Check size (bomb protection)
            if len(decompressed) > len(data) * self.config.max_compression_ratio:
                raise zlib.error(
                    f"Decompressed size exceeds limit "
                    f"({len(decompressed)} > {len(data) * self.config.max_compression_ratio})"
                )

            # Reset context if no takeover
            if not self.peer_no_context_takeover:
                self._decompress_obj = decompress_obj

            logger.debug(
                f"Decompressed {len(data)} -> {len(decompressed)} bytes "
                f"({len(decompressed)/len(data)*100:.1f}%)"
            )

            return decompressed

        except zlib.error as e:
            logger.error(f"Decompression error: {e}")
            raise

    def get_statistics(self) -> dict:
        """Get compression statistics."""
        avg_compression_ratio = 0.0
        if self.total_uncompressed > 0:
            avg_compression_ratio = self.total_compressed / self.total_uncompressed

        avg_compression_time = 0.0
        if self.compression_count > 0:
            avg_compression_time = self.total_compression_time / self.compression_count

        return {
            "enabled": self.config.enabled,
            "level": self.config.level,
            "total_compressed_bytes": self.total_compressed,
            "total_uncompressed_bytes": self.total_uncompressed,
            "compression_count": self.compression_count,
            "avg_compression_ratio": avg_compression_ratio,
            "avg_compression_time_ms": avg_compression_time * 1000,
            "bytes_saved": self.total_uncompressed - self.total_compressed,
        }


class CompressionManager:
    """
    Manages compression contexts for multiple connections.

    Provides centralized compression management with:
    - Per-connection compression contexts
    - Shared configuration
    - Global compression statistics
    """

    def __init__(self, config: Optional[CompressionConfig] = None):
        self.config = config or CompressionConfig()
        self._contexts: dict[str, CompressionContext] = {}

    def create_context(self, connection_id: str, is_client: bool = False) -> CompressionContext:
        """Create compression context for a connection."""
        context = CompressionContext(self.config, is_client=is_client)
        self._contexts[connection_id] = context
        logger.debug(f"Created compression context for connection {connection_id}")
        return context

    def get_context(self, connection_id: str) -> Optional[CompressionContext]:
        """Get compression context for a connection."""
        return self._contexts.get(connection_id)

    def remove_context(self, connection_id: str):
        """Remove compression context for a connection."""
        if connection_id in self._contexts:
            del self._contexts[connection_id]
            logger.debug(f"Removed compression context for connection {connection_id}")

    def get_global_statistics(self) -> dict:
        """Get global compression statistics across all connections."""
        total_compressed = sum(ctx.total_compressed for ctx in self._contexts.values())
        total_uncompressed = sum(ctx.total_uncompressed for ctx in self._contexts.values())
        total_compressions = sum(ctx.compression_count for ctx in self._contexts.values())

        avg_ratio = 0.0
        if total_uncompressed > 0:
            avg_ratio = total_compressed / total_uncompressed

        return {
            "total_contexts": len(self._contexts),
            "total_compressed_bytes": total_compressed,
            "total_uncompressed_bytes": total_uncompressed,
            "total_compressions": total_compressions,
            "avg_compression_ratio": avg_ratio,
            "bytes_saved": total_uncompressed - total_compressed,
            "config": {
                "enabled": self.config.enabled,
                "level": self.config.level,
                "min_size_bytes": self.config.min_size_bytes,
            },
        }


# Parse permessage-deflate extension parameters
def parse_permessage_deflate(params: str) -> CompressionConfig:
    """
    Parse permessage-deflate extension parameters from Sec-WebSocket-Extensions header.

    Example:
        permessage-deflate; client_no_context_takeover; server_max_window_bits=10
    """
    config = CompressionConfig()

    if not params:
        return config

    # Parse parameters
    parts = [p.strip() for p in params.split(";")]

    for part in parts[1:]:  # Skip first part (extension name)
        if "=" in part:
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "server_max_window_bits":
                config.server_max_window_bits = int(value)
            elif key == "client_max_window_bits":
                config.client_max_window_bits = int(value)
        else:
            key = part.strip()

            if key == "server_no_context_takeover":
                config.server_no_context_takeover = True
            elif key == "client_no_context_takeover":
                config.client_no_context_takeover = True

    return config


def format_permessage_deflate(config: CompressionConfig) -> str:
    """
    Format permessage-deflate extension parameters for Sec-WebSocket-Extensions header.

    Returns:
        Extension string (e.g., "permessage-deflate; server_max_window_bits=15")
    """
    parts = ["permessage-deflate"]

    if config.server_max_window_bits != 15:
        parts.append(f"server_max_window_bits={config.server_max_window_bits}")

    if config.client_max_window_bits != 15:
        parts.append(f"client_max_window_bits={config.client_max_window_bits}")

    if config.server_no_context_takeover:
        parts.append("server_no_context_takeover")

    if config.client_no_context_takeover:
        parts.append("client_no_context_takeover")

    return "; ".join(parts)


# Global compression manager
global_compression_manager = CompressionManager()


__all__ = [
    "CompressionLevel",
    "CompressionConfig",
    "CompressionContext",
    "CompressionManager",
    "parse_permessage_deflate",
    "format_permessage_deflate",
    "global_compression_manager",
]
