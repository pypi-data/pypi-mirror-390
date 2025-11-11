"""
CovetPy Database Backup and Recovery System

Production-grade backup and recovery solution with:
- Automated backups with scheduling and rotation
- Compression (gzip, bzip2, lzma) and encryption (AES-256)
- Point-in-time recovery (PITR) for PostgreSQL
- Cloud storage integration (S3, GCS, Azure Blob)
- Integrity verification and backup testing
- Monitoring and alerting

Enterprise Features:
- Zero-downtime backups with consistent snapshots
- Incremental and differential backup strategies
- Backup verification and restore testing
- Retention policies with automatic cleanup
- Backup encryption at rest and in transit
- Audit logging and compliance reporting
"""

from .backup_manager import BackupManager
from .backup_metadata import BackupMetadata, BackupStatus, BackupType
from .backup_strategy import (
    BackupStrategy,
    MySQLBackupStrategy,
    PostgreSQLBackupStrategy,
    SQLiteBackupStrategy,
)
from .compression import CompressionEngine, CompressionType
from .encryption import EncryptionEngine, EncryptionType
from .pitr_manager import PITRManager
from .restore_manager import RestoreManager
from .scheduler import BackupScheduler
from .storage import BackupStorage, LocalStorage, S3Storage

__all__ = [
    "BackupManager",
    "BackupMetadata",
    "BackupStatus",
    "BackupType",
    "BackupStrategy",
    "PostgreSQLBackupStrategy",
    "MySQLBackupStrategy",
    "SQLiteBackupStrategy",
    "CompressionEngine",
    "CompressionType",
    "EncryptionEngine",
    "EncryptionType",
    "PITRManager",
    "RestoreManager",
    "BackupScheduler",
    "BackupStorage",
    "LocalStorage",
    "S3Storage",
]

__version__ = "1.0.0"
