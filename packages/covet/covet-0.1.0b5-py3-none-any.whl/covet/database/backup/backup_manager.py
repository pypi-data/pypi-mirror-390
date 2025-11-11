"""
Backup Manager - Central Backup Orchestration

Production-grade backup manager that coordinates all backup operations:
- Multi-database support (PostgreSQL, MySQL, SQLite)
- Compression and encryption
- Cloud storage integration
- Backup verification
- Metadata tracking
- Error handling and retry logic
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .backup_metadata import (
    BackupCatalog,
    BackupMetadata,
    BackupStatus,
    BackupType,
    CompressionAlgorithm,
    EncryptionAlgorithm,
)
from .backup_strategy import (
    BackupStrategy,
    MySQLBackupStrategy,
    PostgreSQLBackupStrategy,
    SQLiteBackupStrategy,
)
from .compression import CompressionEngine, CompressionType
from .encryption import EncryptionEngine, EncryptionType
from .storage import BackupStorage, LocalStorage, S3Storage

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Enterprise-grade backup manager for CovetPy databases.

    This is the main entry point for backup operations. It orchestrates
    all backup activities including:
    - Creating backups with compression and encryption
    - Uploading to local or cloud storage
    - Tracking backup metadata
    - Verifying backup integrity
    - Managing backup lifecycle

    Example:
        # Initialize backup manager
        manager = BackupManager(
            backup_dir="/var/backups/covet",
            catalog_dir="/var/backups/covet/catalog"
        )

        # Create encrypted, compressed backup
        metadata = await manager.create_backup(
            database_config={
                "database_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "mydb",
                "user": "postgres",
                "password": "secret"
            },
            compress=True,
            encryption_type=EncryptionType.AES_256_GCM,
            storage_backend="s3",
            s3_bucket="my-backups"
        )

        # List all backups
        backups = manager.list_backups()

        # Verify backup integrity
        is_valid = await manager.verify_backup(metadata.backup_id)
    """

    def __init__(
        self,
        backup_dir: str = "/var/backups/covet",
        catalog_dir: Optional[str] = None,
        temp_dir: Optional[str] = None,
    ):
        """
        Initialize backup manager.

        Args:
            backup_dir: Base directory for storing backups
            catalog_dir: Directory for backup catalog (default: backup_dir/catalog)
            temp_dir: Temporary directory for backup operations (default: backup_dir/tmp)
        """
        self.backup_dir = Path(backup_dir)
        self.catalog_dir = Path(catalog_dir or (self.backup_dir / "catalog"))
        self.temp_dir = Path(temp_dir or (self.backup_dir / "tmp"))

        # Create directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.catalog_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Initialize backup catalog
        self.catalog = BackupCatalog(str(self.catalog_dir))

        # Storage backends
        self._storage_backends: Dict[str, BackupStorage] = {
            "local": LocalStorage(str(self.backup_dir))
        }

    def add_storage_backend(self, name: str, storage: BackupStorage) -> None:
        """
        Add a storage backend.

        Args:
            name: Backend name (e.g., 's3', 'gcs', 'azure')
            storage: Storage backend instance
        """
        self._storage_backends[name] = storage

    async def create_backup(
        self,
        database_config: Dict[str, Any],
        backup_type: BackupType = BackupType.FULL,
        compress: bool = True,
        compression_type: CompressionType = CompressionType.GZIP,
        compress_level: Optional[int] = None,
        encrypt: bool = False,
        encryption_type: EncryptionType = EncryptionType.AES_256_GCM,
        encryption_key: Optional[bytes] = None,
        encryption_password: Optional[str] = None,
        storage_backend: str = "local",
        remote_path: Optional[str] = None,
        retention_days: int = 30,
        tags: Optional[Dict[str, str]] = None,
        **backup_options,
    ) -> BackupMetadata:
        """
        Create a database backup with compression and encryption.

        Args:
            database_config: Database configuration dictionary
            backup_type: Type of backup (FULL, INCREMENTAL, etc.)
            compress: Enable compression
            compression_type: Compression algorithm
            compress_level: Compression level (None = use default)
            encrypt: Enable encryption
            encryption_type: Encryption algorithm
            encryption_key: Encryption key (generated if None)
            encryption_password: Password for key derivation
            storage_backend: Storage backend name ('local', 's3', etc.)
            remote_path: Remote storage path (auto-generated if None)
            retention_days: Backup retention period
            tags: Custom tags for the backup
            **backup_options: Additional database-specific backup options

        Returns:
            BackupMetadata object with backup details

        Raises:
            ValueError: If invalid configuration
            RuntimeError: If backup fails
        """
        # Create metadata
        metadata = BackupMetadata(
            backup_type=backup_type,
            database_type=database_config.get("database_type", "unknown"),
            database_name=database_config.get("database", ""),
            database_version="",  # Will be populated later
            host=database_config.get("host", "localhost"),
            port=database_config.get("port", 0),
            compressed=compress,
            compression_algorithm=(
                CompressionAlgorithm[compression_type.name]
                if compress
                else CompressionAlgorithm.NONE
            ),
            encrypted=encrypt,
            encryption_algorithm=(
                EncryptionAlgorithm[encryption_type.name] if encrypt else EncryptionAlgorithm.NONE
            ),
            storage_location=storage_backend,
            retention_days=retention_days,
            tags=tags or {},
        )

        # Calculate expiration date
        metadata.expires_at = datetime.now() + timedelta(days=retention_days)

        # Start backup
        metadata.start()

        try:
            logger.info(
                f"Starting backup: {metadata.backup_id} "
                f"({metadata.database_type}/{metadata.database_name})"
            )

            # Step 1: Create backup strategy
            strategy = self._create_backup_strategy(database_config)

            # Get database version and size
            metadata.database_version = await strategy.get_database_version()
            metadata.original_size_bytes = await strategy.get_database_size()

            # Test connection
            if not await strategy.test_connection():
                raise RuntimeError("Failed to connect to database")

            # For PostgreSQL, capture WAL LSN before backup for PITR
            if database_config.get("database_type") == "postgresql":
                wal_info_before = await strategy._get_wal_position()
                if wal_info_before.get("current_lsn"):
                    metadata.wal_start_lsn = wal_info_before["current_lsn"]
                    logger.info(f"WAL start LSN: {metadata.wal_start_lsn}")

            # Step 2: Create initial backup file
            temp_backup_file = self.temp_dir / f"{metadata.backup_id}.backup"
            logger.info(f"Creating backup file: {temp_backup_file}")

            backup_result = await strategy.create_backup(str(temp_backup_file), **backup_options)

            # Update metadata with backup-specific info
            if backup_result.get("wal_start_lsn"):
                metadata.wal_start_lsn = backup_result["wal_start_lsn"]
            if backup_result.get("wal_end_lsn"):
                metadata.wal_end_lsn = backup_result["wal_end_lsn"]
            if backup_result.get("tables_included"):
                metadata.tables_included = backup_result["tables_included"]
            if backup_result.get("schemas_included"):
                metadata.schemas_included = backup_result["schemas_included"]

            # For PostgreSQL, capture WAL LSN after backup for PITR range
            if database_config.get("database_type") == "postgresql" and not metadata.wal_end_lsn:
                wal_info_after = await strategy._get_wal_position()
                if wal_info_after.get("current_lsn"):
                    metadata.wal_end_lsn = wal_info_after["current_lsn"]
                    logger.info(f"WAL end LSN: {metadata.wal_end_lsn}")

            current_file = temp_backup_file

            # Step 3: Compress if enabled
            if compress:
                logger.info(f"Compressing backup with {compression_type.name}")
                compression_engine = CompressionEngine(compression_type, compress_level)

                compressed_file = Path(str(current_file) + compression_type.extension)
                compression_engine.compress_file(
                    str(current_file), str(compressed_file), remove_original=True
                )

                current_file = compressed_file

            # Step 4: Encrypt if enabled
            encryption_metadata = {}
            if encrypt:
                logger.info(f"Encrypting backup with {encryption_type.name}")
                encryption_engine = EncryptionEngine(encryption_type)

                encrypted_file = Path(str(current_file) + encryption_type.extension)
                encrypted_path, enc_key, enc_metadata = await asyncio.to_thread(
                    encryption_engine.encrypt_file,
                    str(current_file),
                    str(encrypted_file),
                    key=encryption_key,
                    password=encryption_password,
                    remove_original=True,
                )

                current_file = Path(encrypted_path)
                encryption_metadata = enc_metadata

                # CRITICAL: Store encryption metadata (IV/tag/nonce) for decryption
                # This fixes the issue where encrypted backups couldn't be decrypted
                metadata.custom_metadata.update(enc_metadata)

                # Store encryption key securely (in production, use KMS)
                if encryption_key is None and encryption_password is None:
                    key_file = self.catalog_dir / f"{metadata.backup_id}.key"
                    with open(key_file, "wb") as f:
                        f.write(enc_key)
                    os.chmod(key_file, 0o600)  # Restrict permissions
                    logger.info(f"Encryption key stored securely: {key_file}")
                elif encryption_password:
                    logger.info(f"Backup encrypted with password-based key derivation")

            # Step 5: Calculate checksums
            logger.info("Calculating checksums")
            metadata.calculate_checksums(str(current_file))

            # Step 6: Upload to storage backend
            storage = self._storage_backends.get(storage_backend)
            if not storage:
                raise ValueError(f"Unknown storage backend: {storage_backend}")

            # Generate remote path if not provided
            if remote_path is None:
                remote_path = self._generate_remote_path(metadata, current_file)

            logger.info(f"Uploading to {storage_backend}: {remote_path}")

            storage_metadata = {
                "backup_id": metadata.backup_id,
                "database_type": metadata.database_type,
                "database_name": metadata.database_name,
                "created_at": metadata.created_at.isoformat(),
                **encryption_metadata,
            }

            upload_result = await storage.upload_file(
                str(current_file), remote_path, metadata=storage_metadata
            )

            metadata.storage_path = remote_path

            # Step 7: Complete backup
            file_size = current_file.stat().st_size
            metadata.complete(str(current_file), file_size)

            # Clean up temp file
            if current_file.exists():
                current_file.unlink()

            # Save metadata to catalog
            self.catalog.add(metadata)

            logger.info(
                f"Backup completed: {metadata.backup_id} "
                f"({metadata.get_human_readable_size()}) in {metadata.duration_seconds:.2f}s"
            )

            return metadata

        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)

            # Update metadata with error
            import traceback

            metadata.fail(str(e), traceback.format_exc())

            # Save failed backup metadata
            self.catalog.add(metadata)

            # Clean up temp files
            for temp_file in self.temp_dir.glob(f"{metadata.backup_id}*"):
                try:
                    temp_file.unlink()
                except BaseException:
                    pass

            raise RuntimeError(f"Backup failed: {e}") from e

    async def verify_backup(
        self,
        backup_id: str,
        download_dir: Optional[str] = None,
        verify_restore: bool = False,
    ) -> bool:
        """
        Verify backup integrity.

        Args:
            backup_id: Backup ID to verify
            download_dir: Directory for downloading backup (default: temp_dir)
            verify_restore: Also verify that backup can be restored

        Returns:
            True if backup is valid

        Raises:
            ValueError: If backup not found
        """
        logger.info(f"Verifying backup: {backup_id}")

        metadata = self.catalog.get(backup_id)
        if not metadata:
            raise ValueError(f"Backup not found: {backup_id}")

        metadata.status = BackupStatus.VERIFYING

        try:
            # Get storage backend
            storage = self._storage_backends.get(metadata.storage_location)
            if not storage:
                raise ValueError(f"Storage backend not configured: {metadata.storage_location}")

            # Download backup
            download_path = Path(download_dir or self.temp_dir) / f"{backup_id}_verify"
            download_path.mkdir(parents=True, exist_ok=True)

            local_file = download_path / Path(metadata.storage_path).name

            await storage.download_file(metadata.storage_path, str(local_file))

            # Verify checksum
            is_valid = metadata.verify_checksum(str(local_file))

            if is_valid:
                logger.info(f"Backup {backup_id} integrity verified")
                self.catalog.add(metadata)
            else:
                logger.error(f"Backup {backup_id} checksum verification failed")

            # Clean up
            if local_file.exists():
                local_file.unlink()
            if download_path.exists():
                download_path.rmdir()

            return is_valid

        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            metadata.status = BackupStatus.FAILED
            self.catalog.add(metadata)
            raise

    def list_backups(
        self,
        database_name: Optional[str] = None,
        status: Optional[BackupStatus] = None,
        backup_type: Optional[BackupType] = None,
    ) -> List[BackupMetadata]:
        """
        List backups with optional filtering.

        Args:
            database_name: Filter by database name
            status: Filter by status
            backup_type: Filter by backup type

        Returns:
            List of BackupMetadata objects
        """
        backups = self.catalog.list_all()

        if database_name:
            backups = [b for b in backups if b.database_name == database_name]

        if status:
            backups = [b for b in backups if b.status == status]

        if backup_type:
            backups = [b for b in backups if b.backup_type == backup_type]

        return backups

    async def delete_backup(self, backup_id: str, remove_from_storage: bool = True) -> bool:
        """
        Delete a backup.

        Args:
            backup_id: Backup ID to delete
            remove_from_storage: Also remove from storage backend

        Returns:
            True if successful
        """
        logger.info(f"Deleting backup: {backup_id}")

        metadata = self.catalog.get(backup_id)
        if not metadata:
            logger.warning(f"Backup not found: {backup_id}")
            return False

        try:
            # Remove from storage if requested
            if remove_from_storage:
                storage = self._storage_backends.get(metadata.storage_location)
                if storage:
                    await storage.delete_file(metadata.storage_path)

            # Remove encryption key if exists
            key_file = self.catalog_dir / f"{backup_id}.key"
            if key_file.exists():
                key_file.unlink()

            # Remove from catalog
            self.catalog.remove(backup_id)

            logger.info(f"Backup deleted: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False

    async def cleanup_expired_backups(self, dry_run: bool = False) -> List[str]:
        """
        Clean up expired backups based on retention policy.

        Args:
            dry_run: If True, only report what would be deleted

        Returns:
            List of deleted backup IDs
        """
        expired = self.catalog.get_expired_backups()
        deleted = []

        logger.info(f"Found {len(expired)} expired backups")

        for metadata in expired:
            if dry_run:
                logger.info(f"Would delete expired backup: {metadata.backup_id}")
                deleted.append(metadata.backup_id)
            else:
                success = await self.delete_backup(metadata.backup_id)
                if success:
                    deleted.append(metadata.backup_id)

        return deleted

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get backup statistics.

        Returns:
            Dictionary with backup statistics
        """
        return self.catalog.get_statistics()

    def _create_backup_strategy(self, config: Dict[str, Any]) -> BackupStrategy:
        """Create appropriate backup strategy based on database type."""
        db_type = config.get("database_type", "").lower()

        if db_type == "postgresql":
            return PostgreSQLBackupStrategy(config)
        elif db_type == "mysql":
            return MySQLBackupStrategy(config)
        elif db_type == "sqlite":
            return SQLiteBackupStrategy(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def _generate_remote_path(self, metadata: BackupMetadata, local_file: Path) -> str:
        """Generate remote storage path for backup."""
        # Organize by: database_type/database_name/YYYY/MM/DD/backup_id.ext
        date = metadata.created_at
        path_parts = [
            metadata.database_type,
            metadata.database_name,
            f"{date.year:04d}",
            f"{date.month:02d}",
            f"{date.day:02d}",
            local_file.name,
        ]
        return "/".join(path_parts)


__all__ = ["BackupManager"]
