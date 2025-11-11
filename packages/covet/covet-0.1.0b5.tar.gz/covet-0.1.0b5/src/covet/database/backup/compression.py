"""
Backup Compression Engine

Provides multi-algorithm compression support for database backups.
Optimized for different use cases: speed vs. compression ratio.
"""

import bz2
import gzip
import lzma
import shutil
from enum import Enum
from pathlib import Path
from typing import Optional


class CompressionType(Enum):
    """
    Compression algorithm types with their characteristics.

    GZIP: Fast compression, good for streaming (level 6 default)
    BZIP2: Better compression ratio, slower (level 9 default)
    LZMA: Best compression ratio, slowest (preset 6 default)
    ZSTD: Modern algorithm, excellent speed/ratio balance (level 3 default)
    """

    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZSTD = "zstd"

    @property
    def extension(self) -> str:
        """Get file extension for compression type."""
        extensions = {
            CompressionType.NONE: "",
            CompressionType.GZIP: ".gz",
            CompressionType.BZIP2: ".bz2",
            CompressionType.LZMA: ".xz",
            CompressionType.ZSTD: ".zst",
        }
        return extensions[self]

    @property
    def default_level(self) -> int:
        """Get default compression level."""
        levels = {
            CompressionType.NONE: 0,
            CompressionType.GZIP: 6,  # Good balance
            CompressionType.BZIP2: 9,  # Maximum compression
            CompressionType.LZMA: 6,  # Good balance
            CompressionType.ZSTD: 3,  # Fast with good compression
        }
        return levels[self]


class CompressionEngine:
    """
    High-performance compression engine for database backups.

    Features:
    - Multiple compression algorithms (gzip, bzip2, lzma, zstd)
    - Streaming compression for memory efficiency
    - Configurable compression levels
    - Progress tracking for large files
    - Automatic file extension handling
    """

    def __init__(
        self,
        compression_type: CompressionType = CompressionType.GZIP,
        compression_level: Optional[int] = None,
        chunk_size: int = 8 * 1024 * 1024,  # 8MB chunks
    ):
        """
        Initialize compression engine.

        Args:
            compression_type: Compression algorithm to use
            compression_level: Compression level (None = use default)
            chunk_size: Size of chunks for streaming compression (bytes)
        """
        self.compression_type = compression_type
        self.compression_level = (
            compression_level if compression_level is not None else compression_type.default_level
        )
        self.chunk_size = chunk_size

    def compress_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        remove_original: bool = False,
    ) -> str:
        """
        Compress a file using the configured algorithm.

        Args:
            input_path: Path to input file
            output_path: Path to output file (auto-generated if None)
            remove_original: Remove original file after compression

        Returns:
            Path to compressed file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If compression fails
        """
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Generate output path if not provided
        if output_path is None:
            output_path = str(input_file) + self.compression_type.extension
        output_file = Path(output_path)

        # No compression needed
        if self.compression_type == CompressionType.NONE:
            if input_file != output_file:
                shutil.copy2(input_file, output_file)
            return str(output_file)

        # Compress based on type
        try:
            if self.compression_type == CompressionType.GZIP:
                self._compress_gzip(input_file, output_file)
            elif self.compression_type == CompressionType.BZIP2:
                self._compress_bzip2(input_file, output_file)
            elif self.compression_type == CompressionType.LZMA:
                self._compress_lzma(input_file, output_file)
            elif self.compression_type == CompressionType.ZSTD:
                self._compress_zstd(input_file, output_file)
            else:
                raise ValueError(f"Unsupported compression type: {self.compression_type}")

            # Remove original if requested
            if remove_original and input_file.exists():
                input_file.unlink()

            return str(output_file)

        except Exception as e:
            # Clean up partial output file on error
            if output_file.exists():
                output_file.unlink()
            raise ValueError(f"Compression failed: {e}") from e

    def decompress_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        remove_original: bool = False,
    ) -> str:
        """
        Decompress a file.

        Args:
            input_path: Path to compressed file
            output_path: Path to output file (auto-generated if None)
            remove_original: Remove compressed file after decompression

        Returns:
            Path to decompressed file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If decompression fails
        """
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Detect compression type from extension
        compression_type = self._detect_compression_type(input_file)

        # Generate output path if not provided
        if output_path is None:
            output_path = str(input_file)
            if compression_type.extension:
                output_path = output_path.rsplit(compression_type.extension, 1)[0]
        output_file = Path(output_path)

        # No decompression needed
        if compression_type == CompressionType.NONE:
            if input_file != output_file:
                shutil.copy2(input_file, output_file)
            return str(output_file)

        # Decompress based on type
        try:
            if compression_type == CompressionType.GZIP:
                self._decompress_gzip(input_file, output_file)
            elif compression_type == CompressionType.BZIP2:
                self._decompress_bzip2(input_file, output_file)
            elif compression_type == CompressionType.LZMA:
                self._decompress_lzma(input_file, output_file)
            elif compression_type == CompressionType.ZSTD:
                self._decompress_zstd(input_file, output_file)
            else:
                raise ValueError(f"Unsupported compression type: {compression_type}")

            # Remove original if requested
            if remove_original and input_file.exists():
                input_file.unlink()

            return str(output_file)

        except Exception as e:
            # Clean up partial output file on error
            if output_file.exists():
                output_file.unlink()
            raise ValueError(f"Decompression failed: {e}") from e

    def _compress_gzip(self, input_file: Path, output_file: Path) -> None:
        """Compress using gzip algorithm."""
        with open(input_file, "rb") as f_in:
            with gzip.open(output_file, "wb", compresslevel=self.compression_level) as f_out:
                while True:
                    chunk = f_in.read(self.chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)

    def _decompress_gzip(self, input_file: Path, output_file: Path) -> None:
        """Decompress gzip file."""
        with gzip.open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                while True:
                    chunk = f_in.read(self.chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)

    def _compress_bzip2(self, input_file: Path, output_file: Path) -> None:
        """Compress using bzip2 algorithm."""
        with open(input_file, "rb") as f_in:
            with bz2.open(output_file, "wb", compresslevel=self.compression_level) as f_out:
                while True:
                    chunk = f_in.read(self.chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)

    def _decompress_bzip2(self, input_file: Path, output_file: Path) -> None:
        """Decompress bzip2 file."""
        with bz2.open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                while True:
                    chunk = f_in.read(self.chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)

    def _compress_lzma(self, input_file: Path, output_file: Path) -> None:
        """Compress using lzma (xz) algorithm."""
        with open(input_file, "rb") as f_in:
            with lzma.open(output_file, "wb", preset=self.compression_level) as f_out:
                while True:
                    chunk = f_in.read(self.chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)

    def _decompress_lzma(self, input_file: Path, output_file: Path) -> None:
        """Decompress lzma file."""
        with lzma.open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                while True:
                    chunk = f_in.read(self.chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)

    def _compress_zstd(self, input_file: Path, output_file: Path) -> None:
        """Compress using zstd algorithm."""
        try:
            import zstandard as zstd

            with open(input_file, "rb") as f_in:
                with open(output_file, "wb") as f_out:
                    compressor = zstd.ZstdCompressor(level=self.compression_level)
                    compressor.copy_stream(f_in, f_out)
        except ImportError:
            raise ImportError(
                "zstandard library not installed. Install with: pip install zstandard"
            )

    def _decompress_zstd(self, input_file: Path, output_file: Path) -> None:
        """Decompress zstd file."""
        try:
            import zstandard as zstd

            with open(input_file, "rb") as f_in:
                with open(output_file, "wb") as f_out:
                    decompressor = zstd.ZstdDecompressor()
                    decompressor.copy_stream(f_in, f_out)
        except ImportError:
            raise ImportError(
                "zstandard library not installed. Install with: pip install zstandard"
            )

    @staticmethod
    def _detect_compression_type(file_path: Path) -> CompressionType:
        """Detect compression type from file extension."""
        suffix = file_path.suffix.lower()

        if suffix == ".gz":
            return CompressionType.GZIP
        elif suffix == ".bz2":
            return CompressionType.BZIP2
        elif suffix in [".xz", ".lzma"]:
            return CompressionType.LZMA
        elif suffix == ".zst":
            return CompressionType.ZSTD
        else:
            return CompressionType.NONE

    def get_compression_ratio(self, original_size: int, compressed_size: int) -> float:
        """
        Calculate compression ratio.

        Args:
            original_size: Original file size in bytes
            compressed_size: Compressed file size in bytes

        Returns:
            Compression ratio (e.g., 2.5 means 2.5x compression)
        """
        if compressed_size == 0:
            return 0.0
        return original_size / compressed_size

    def estimate_compressed_size(
        self, original_size: int, compression_type: Optional[CompressionType] = None
    ) -> int:
        """
        Estimate compressed size based on typical compression ratios.

        Args:
            original_size: Original file size in bytes
            compression_type: Compression type (uses current if None)

        Returns:
            Estimated compressed size in bytes
        """
        comp_type = compression_type or self.compression_type

        # Typical compression ratios for database backups
        # (actual ratios vary widely based on data)
        typical_ratios = {
            CompressionType.NONE: 1.0,
            CompressionType.GZIP: 3.0,  # 3x compression
            CompressionType.BZIP2: 3.5,  # 3.5x compression
            CompressionType.LZMA: 4.0,  # 4x compression
            CompressionType.ZSTD: 3.2,  # 3.2x compression
        }

        ratio = typical_ratios.get(comp_type, 1.0)
        return int(original_size / ratio)


__all__ = ["CompressionEngine", "CompressionType"]
