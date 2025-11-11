"""
Backup Metadata Management

Tracks backup metadata, status, and provides backup catalog functionality.
Essential for audit trails, compliance, and disaster recovery planning.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class BackupType(Enum):
    """Backup type enumeration."""

    FULL = "full"  # Complete database backup
    INCREMENTAL = "incremental"  # Changes since last backup
    DIFFERENTIAL = "differential"  # Changes since last full backup
    TRANSACTION_LOG = "transaction_log"  # Transaction log backup (for PITR)
    SNAPSHOT = "snapshot"  # Storage-level snapshot


class BackupStatus(Enum):
    """Backup status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"
    EXPIRED = "expired"
    DELETED = "deleted"


class CompressionAlgorithm(Enum):
    """Compression algorithm enumeration."""

    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZSTD = "zstd"


class EncryptionAlgorithm(Enum):
    """Encryption algorithm enumeration."""

    NONE = "none"
    AES_256_CBC = "aes-256-cbc"
    AES_256_GCM = "aes-256-gcm"
    CHACHA20_POLY1305 = "chacha20-poly1305"


@dataclass
class BackupMetadata:
    """
    Comprehensive backup metadata for tracking and auditing.

    This class stores all relevant information about a backup, including:
    - Backup identification and timing
    - Database connection details
    - File locations and sizes
    - Compression and encryption settings
    - Checksums for integrity verification
    - Status and error information
    """

    # Unique identifier for the backup
    backup_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))

    # Backup type and status
    backup_type: BackupType = BackupType.FULL
    status: BackupStatus = BackupStatus.PENDING

    # Database information
    database_type: str = ""  # postgresql, mysql, sqlite
    database_name: str = ""
    database_version: str = ""
    host: str = ""
    port: int = 0

    # Timing information
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    # File information
    backup_file: str = ""  # Path to backup file
    file_size_bytes: int = 0
    original_size_bytes: int = 0  # Size before compression
    compressed: bool = False
    compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.NONE
    compression_ratio: float = 1.0

    # Encryption
    encrypted: bool = False
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.NONE
    encryption_key_id: Optional[str] = None

    # Integrity verification
    checksum_md5: str = ""
    checksum_sha256: str = ""
    verified: bool = False
    verification_date: Optional[datetime] = None

    # Backup scope
    tables_included: List[str] = field(default_factory=list)
    tables_excluded: List[str] = field(default_factory=list)
    schemas_included: List[str] = field(default_factory=list)

    # Point-in-time recovery information (PostgreSQL)
    wal_start_lsn: Optional[str] = None  # Write-Ahead Log start position
    wal_end_lsn: Optional[str] = None  # Write-Ahead Log end position
    transaction_log_files: List[str] = field(default_factory=list)

    # Storage information
    storage_location: str = ""  # local, s3, gcs, azure
    storage_path: str = ""  # Full path or URI
    storage_class: str = "STANDARD"  # S3 storage class

    # Retention
    retention_days: int = 30
    expires_at: Optional[datetime] = None

    # Error information
    error_message: str = ""
    error_traceback: str = ""

    # Tags and metadata
    tags: Dict[str, str] = field(default_factory=dict)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        """Mark backup as started."""
        self.status = BackupStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self, file_path: str, file_size: int) -> None:
        """Mark backup as completed."""
        self.status = BackupStatus.COMPLETED
        self.completed_at = datetime.now()
        self.backup_file = file_path
        self.file_size_bytes = file_size

        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

        if self.compressed and self.original_size_bytes > 0:
            self.compression_ratio = self.original_size_bytes / self.file_size_bytes

    def fail(self, error_message: str, error_traceback: str = "") -> None:
        """Mark backup as failed."""
        self.status = BackupStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
        self.error_traceback = error_traceback

        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def calculate_checksums(self, file_path: str) -> None:
        """Calculate MD5 and SHA256 checksums for integrity verification."""
        # MD5 for backwards compatibility only (SHA256 is primary) - NOT for security
        md5_hash = hashlib.md5(usedforsecurity=False)
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read in 8MB chunks for memory efficiency
            for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)

        self.checksum_md5 = md5_hash.hexdigest()
        self.checksum_sha256 = sha256_hash.hexdigest()

    def verify_checksum(self, file_path: str) -> bool:
        """Verify backup file integrity using SHA256 checksum."""
        if not self.checksum_sha256:
            raise ValueError("No checksum available for verification")

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
                sha256_hash.update(chunk)

        calculated_checksum = sha256_hash.hexdigest()
        is_valid = calculated_checksum == self.checksum_sha256

        if is_valid:
            self.verified = True
            self.verification_date = datetime.now()
            self.status = BackupStatus.VERIFIED
        else:
            self.status = BackupStatus.CORRUPTED

        return is_valid

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "backup_id": self.backup_id,
            "backup_type": self.backup_type.value,
            "status": self.status.value,
            "database_type": self.database_type,
            "database_name": self.database_name,
            "database_version": self.database_version,
            "host": self.host,
            "port": self.port,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (self.completed_at.isoformat() if self.completed_at else None),
            "duration_seconds": self.duration_seconds,
            "backup_file": self.backup_file,
            "file_size_bytes": self.file_size_bytes,
            "original_size_bytes": self.original_size_bytes,
            "compressed": self.compressed,
            "compression_algorithm": self.compression_algorithm.value,
            "compression_ratio": self.compression_ratio,
            "encrypted": self.encrypted,
            "encryption_algorithm": self.encryption_algorithm.value,
            "encryption_key_id": self.encryption_key_id,
            "checksum_md5": self.checksum_md5,
            "checksum_sha256": self.checksum_sha256,
            "verified": self.verified,
            "verification_date": (
                self.verification_date.isoformat() if self.verification_date else None
            ),
            "tables_included": self.tables_included,
            "tables_excluded": self.tables_excluded,
            "schemas_included": self.schemas_included,
            "wal_start_lsn": self.wal_start_lsn,
            "wal_end_lsn": self.wal_end_lsn,
            "transaction_log_files": self.transaction_log_files,
            "storage_location": self.storage_location,
            "storage_path": self.storage_path,
            "storage_class": self.storage_class,
            "retention_days": self.retention_days,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "error_message": self.error_message,
            "error_traceback": self.error_traceback,
            "tags": self.tags,
            "custom_metadata": self.custom_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackupMetadata":
        """Create metadata instance from dictionary."""
        # Convert string timestamps to datetime objects
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        if data.get("verification_date"):
            data["verification_date"] = datetime.fromisoformat(data["verification_date"])
        if data.get("expires_at"):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])

        # Convert enums
        if data.get("backup_type"):
            data["backup_type"] = BackupType(data["backup_type"])
        if data.get("status"):
            data["status"] = BackupStatus(data["status"])
        if data.get("compression_algorithm"):
            data["compression_algorithm"] = CompressionAlgorithm(data["compression_algorithm"])
        if data.get("encryption_algorithm"):
            data["encryption_algorithm"] = EncryptionAlgorithm(data["encryption_algorithm"])

        return cls(**data)

    def save_to_file(self, file_path: str) -> None:
        """Save metadata to JSON file."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str) -> "BackupMetadata":
        """Load metadata from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_human_readable_size(self) -> str:
        """Get human-readable file size."""
        size = self.file_size_bytes
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def get_summary(self) -> str:
        """Get human-readable backup summary."""
        summary = [
            f"Backup ID: {self.backup_id}",
            f"Type: {self.backup_type.value}",
            f"Status: {self.status.value}",
            f"Database: {self.database_type}/{self.database_name}",
            f"Size: {self.get_human_readable_size()}",
            f"Duration: {self.duration_seconds:.2f}s",
        ]

        if self.compressed:
            summary.append(
                f"Compression: {self.compression_algorithm.value} "
                f"(ratio: {self.compression_ratio:.2f}x)"
            )

        if self.encrypted:
            summary.append(f"Encryption: {self.encryption_algorithm.value}")

        if self.verified:
            summary.append(f"Verified: {self.verification_date.strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(summary)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"BackupMetadata("
            f"id={self.backup_id}, "
            f"type={self.backup_type.value}, "
            f"status={self.status.value}, "
            f"db={self.database_name}, "
            f"size={self.get_human_readable_size()}"
            f")"
        )


class BackupCatalog:
    """
    Backup catalog for managing multiple backup metadata records.

    Provides indexing, searching, and filtering capabilities for backups.
    Essential for backup lifecycle management and compliance reporting.
    """

    def __init__(self, catalog_path: str):
        """
        Initialize backup catalog.

        Args:
            catalog_path: Path to catalog directory
        """
        self.catalog_path = Path(catalog_path)
        self.catalog_path.mkdir(parents=True, exist_ok=True)
        self._index: Dict[str, BackupMetadata] = {}
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Load all backup metadata from catalog directory."""
        for metadata_file in self.catalog_path.glob("*.json"):
            try:
                metadata = BackupMetadata.load_from_file(str(metadata_file))
                self._index[metadata.backup_id] = metadata
            except Exception as e:
                # Log error but continue loading other backups
                print(f"Error loading backup metadata {metadata_file}: {e}")

    def add(self, metadata: BackupMetadata) -> None:
        """Add backup metadata to catalog."""
        self._index[metadata.backup_id] = metadata
        metadata_file = self.catalog_path / f"{metadata.backup_id}.json"
        metadata.save_to_file(str(metadata_file))

    def get(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup metadata by ID."""
        return self._index.get(backup_id)

    def remove(self, backup_id: str) -> None:
        """Remove backup from catalog."""
        if backup_id in self._index:
            del self._index[backup_id]
            metadata_file = self.catalog_path / f"{backup_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()

    def list_all(self) -> List[BackupMetadata]:
        """List all backups in catalog."""
        return sorted(self._index.values(), key=lambda x: x.created_at, reverse=True)

    def list_by_database(self, database_name: str) -> List[BackupMetadata]:
        """List backups for specific database."""
        return [meta for meta in self.list_all() if meta.database_name == database_name]

    def list_by_status(self, status: BackupStatus) -> List[BackupMetadata]:
        """List backups with specific status."""
        return [meta for meta in self.list_all() if meta.status == status]

    def list_by_type(self, backup_type: BackupType) -> List[BackupMetadata]:
        """List backups of specific type."""
        return [meta for meta in self.list_all() if meta.backup_type == backup_type]

    def get_expired_backups(self) -> List[BackupMetadata]:
        """Get list of expired backups based on retention policy."""
        now = datetime.now()
        expired = []

        for meta in self.list_all():
            if meta.expires_at and meta.expires_at < now:
                expired.append(meta)

        return expired

    def get_latest_full_backup(self, database_name: str) -> Optional[BackupMetadata]:
        """Get the most recent successful full backup for a database."""
        backups = [
            meta
            for meta in self.list_by_database(database_name)
            if meta.backup_type == BackupType.FULL and meta.status == BackupStatus.COMPLETED
        ]
        return backups[0] if backups else None

    def get_statistics(self) -> Dict[str, Any]:
        """Get backup statistics."""
        all_backups = self.list_all()
        total_size = sum(meta.file_size_bytes for meta in all_backups)

        status_counts = {}
        for status in BackupStatus:
            status_counts[status.value] = len(self.list_by_status(status))

        type_counts = {}
        for backup_type in BackupType:
            type_counts[backup_type.value] = len(self.list_by_type(backup_type))

        return {
            "total_backups": len(all_backups),
            "total_size_bytes": total_size,
            "total_size_human": self._format_bytes(total_size),
            "by_status": status_counts,
            "by_type": type_counts,
            "oldest_backup": (all_backups[-1].created_at.isoformat() if all_backups else None),
            "newest_backup": (all_backups[0].created_at.isoformat() if all_backups else None),
        }

    @staticmethod
    def _format_bytes(size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"


__all__ = [
    "BackupMetadata",
    "BackupType",
    "BackupStatus",
    "CompressionAlgorithm",
    "EncryptionAlgorithm",
    "BackupCatalog",
]
