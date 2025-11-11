"""
CovetPy Backup System - Usage Examples

This file demonstrates various backup and recovery scenarios.
"""

import asyncio
from datetime import datetime

from .backup_manager import BackupManager
from .backup_metadata import BackupType
from .compression import CompressionType
from .encryption import EncryptionType
from .restore_manager import RestoreManager
from .scheduler import BackupSchedule, BackupScheduler, ScheduleFrequency
from .storage import LocalStorage, S3Storage


async def example_basic_backup():
    """Example 1: Create a basic database backup."""
    # Initialize backup manager
    manager = BackupManager(backup_dir="/var/backups/covet")

    # PostgreSQL database configuration
    db_config = {
        "database_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "myapp",
        "user": "postgres",
        "password": "secret",
    }

    # Create backup
    metadata = await manager.create_backup(
        database_config=db_config,
        compress=True,  # Enable compression
        encryption_password="my_secure_password",  # Optional encryption
    )

    print(f"Backup created: {metadata.backup_id}")
    print(f"Size: {metadata.get_human_readable_size()}")
    print(f"Duration: {metadata.duration_seconds:.2f}s")


async def example_compressed_encrypted_backup():
    """Example 2: Create compressed and encrypted backup."""
    manager = BackupManager(backup_dir="/var/backups/covet")

    db_config = {
        "database_type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "production_db",
        "user": "root",
        "password": "secret",
    }

    # Create backup with specific compression and encryption
    metadata = await manager.create_backup(
        database_config=db_config,
        backup_type=BackupType.FULL,
        compress=True,
        compression_type=CompressionType.LZMA,  # Best compression ratio
        compress_level=9,  # Maximum compression
        encrypt=True,
        encryption_type=EncryptionType.AES_256_GCM,  # AES-256-GCM
        encryption_password="very_secure_password",
        retention_days=90,  # Keep for 90 days
        tags={"environment": "production", "purpose": "daily_backup"},
    )

    print(f"Backup ID: {metadata.backup_id}")
    print(f"Compression ratio: {metadata.compression_ratio:.2f}x")
    print(f"Encrypted: {metadata.encrypted}")


async def example_s3_backup():
    """Example 3: Create backup and upload to S3."""
    manager = BackupManager(backup_dir="/var/backups/covet")

    # Add S3 storage backend
    s3_storage = S3Storage(
        bucket_name="my-database-backups",
        region="us-east-1",
        storage_class="GLACIER",  # Use Glacier for cost savings
        encryption="aws:kms",  # Use KMS encryption
    )
    manager.add_storage_backend("s3", s3_storage)

    db_config = {
        "database_type": "postgresql",
        "host": "db.example.com",
        "port": 5432,
        "database": "production",
        "user": "backup_user",
        "password": "secure_password",
    }

    # Create backup and upload to S3
    metadata = await manager.create_backup(
        database_config=db_config,
        compress=True,
        encrypt=True,
        encryption_password="backup_encryption_key",
        storage_backend="s3",  # Upload to S3
        retention_days=30,
    )

    print(f"Backup uploaded to S3: {metadata.storage_path}")
    print(f"Storage location: {metadata.storage_location}")


async def example_restore_backup():
    """Example 4: Restore a database from backup."""
    from .backup_metadata import BackupCatalog

    # Initialize managers
    catalog = BackupCatalog("/var/backups/covet/catalog")
    storage_backends = {"local": LocalStorage("/var/backups/covet")}

    restore_manager = RestoreManager(
        backup_catalog=catalog,
        storage_backends=storage_backends,
        temp_dir="/tmp/restore",  # nosec B108 - temp file usage reviewed
    )

    # Target database configuration
    target_db = {
        "database_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "myapp_restored",
        "user": "postgres",
        "password": "secret",
    }

    # Restore backup
    result = await restore_manager.restore_backup(
        backup_id="20241010_120000",  # Backup ID from catalog
        target_database=target_db,
        verify_before_restore=True,  # Verify integrity first
        verify_after_restore=True,  # Verify restore succeeded
    )

    print(f"Restore completed in {result['duration_seconds']:.2f}s")
    print(f"Target database: {result['target_database']}")


async def example_point_in_time_recovery():
    """Example 5: PostgreSQL Point-in-Time Recovery (PITR)."""
    from .backup_metadata import BackupCatalog

    catalog = BackupCatalog("/var/backups/covet/catalog")
    storage_backends = {"local": LocalStorage("/var/backups/covet")}

    restore_manager = RestoreManager(
        backup_catalog=catalog,
        storage_backends=storage_backends,
    )

    target_db = {
        "database_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "production_pitr",
        "user": "postgres",
        "password": "secret",
        "data_directory": "/var/lib/postgresql/data",
    }

    # Recover to specific point in time
    result = await restore_manager.point_in_time_recovery(
        backup_id="20241010_020000",  # Base backup
        target_time="2024-10-10 14:30:00",  # Recover to this time
        target_database=target_db,
    )

    print(f"PITR configured for recovery to: {result['target_time']}")
    print("Start PostgreSQL to complete recovery")


async def example_automated_backups():
    """Example 6: Schedule automated backups."""
    manager = BackupManager(backup_dir="/var/backups/covet")
    scheduler = BackupScheduler(manager)

    # Daily backup at 2 AM
    daily_schedule = BackupSchedule(
        name="production_daily",
        description="Daily production database backup",
        database_config={
            "database_type": "postgresql",
            "host": "db.production.com",
            "port": 5432,
            "database": "production",
            "user": "backup_user",
            "password": "backup_password",
        },
        frequency=ScheduleFrequency.DAILY,
        hour=2,  # 2 AM
        minute=0,
        compress=True,
        encrypt=True,
        storage_backend="s3",
        retention_days=30,
        notify_on_failure=True,
    )

    # Weekly full backup on Sundays
    weekly_schedule = BackupSchedule(
        name="production_weekly",
        description="Weekly full backup",
        database_config={
            "database_type": "postgresql",
            "host": "db.production.com",
            "port": 5432,
            "database": "production",
            "user": "backup_user",
            "password": "backup_password",
        },
        frequency=ScheduleFrequency.WEEKLY,
        day_of_week=6,  # Sunday
        hour=1,  # 1 AM
        compress=True,
        encrypt=True,
        storage_backend="s3",
        retention_days=90,
    )

    # Add schedules
    scheduler.add_schedule(daily_schedule)
    scheduler.add_schedule(weekly_schedule)

    # Start scheduler
    await scheduler.start()

    print("Backup scheduler started")
    print(f"Next daily backup: {scheduler.get_next_run_time('production_daily')}")
    print(f"Next weekly backup: {scheduler.get_next_run_time('production_weekly')}")

    # Run until interrupted
    try:
        await scheduler.wait()
    except KeyboardInterrupt:
        await scheduler.stop()


async def example_backup_verification():
    """Example 7: Verify backup integrity."""
    manager = BackupManager(backup_dir="/var/backups/covet")

    # Verify specific backup
    backup_id = "20241010_120000"
    is_valid = await manager.verify_backup(backup_id)

    if is_valid:
        print(f"Backup {backup_id} is valid")
    else:
        print(f"Backup {backup_id} is CORRUPTED!")

    # List all backups
    backups = manager.list_backups()
    print(f"\nTotal backups: {len(backups)}")

    for backup in backups[:5]:  # Show first 5
        print(f"\n{backup.backup_id}:")
        print(f"  Database: {backup.database_name}")
        print(f"  Size: {backup.get_human_readable_size()}")
        print(f"  Created: {backup.created_at}")
        print(f"  Verified: {backup.verified}")


async def example_backup_statistics():
    """Example 8: Get backup statistics."""
    manager = BackupManager(backup_dir="/var/backups/covet")

    stats = manager.get_statistics()

    print("Backup Statistics:")
    print(f"  Total backups: {stats['total_backups']}")
    print(f"  Total size: {stats['total_size_human']}")
    print(f"  Oldest backup: {stats['oldest_backup']}")
    print(f"  Newest backup: {stats['newest_backup']}")
    print("\nBy Status:")
    for status, count in stats["by_status"].items():
        print(f"  {status}: {count}")
    print("\nBy Type:")
    for backup_type, count in stats["by_type"].items():
        print(f"  {backup_type}: {count}")


async def example_selective_restore():
    """Example 9: Restore specific tables/schemas."""
    from .backup_metadata import BackupCatalog

    catalog = BackupCatalog("/var/backups/covet/catalog")
    storage_backends = {"local": LocalStorage("/var/backups/covet")}

    restore_manager = RestoreManager(
        backup_catalog=catalog,
        storage_backends=storage_backends,
    )

    target_db = {
        "database_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "myapp",
        "user": "postgres",
        "password": "secret",
    }

    # Restore only specific tables
    result = await restore_manager.restore_backup(
        backup_id="20241010_120000",
        target_database=target_db,
        tables=["users", "orders", "products"],  # Only these tables
    )

    print(f"Restored tables: {result['tables_restored']}")

    # Restore specific schema
    result2 = await restore_manager.restore_backup(
        backup_id="20241010_120000",
        target_database=target_db,
        schemas=["public", "analytics"],  # Only these schemas
    )

    print(f"Restored schemas: {result2['schemas_restored']}")


async def example_cleanup_old_backups():
    """Example 10: Clean up expired backups."""
    manager = BackupManager(backup_dir="/var/backups/covet")

    # Dry run - see what would be deleted
    dry_run_results = await manager.cleanup_expired_backups(dry_run=True)
    print(f"Would delete {len(dry_run_results)} expired backups:")
    for backup_id in dry_run_results:
        print(f"  - {backup_id}")

    # Actually delete expired backups
    deleted = await manager.cleanup_expired_backups(dry_run=False)
    print(f"\nDeleted {len(deleted)} expired backups")


# Main example runner
async def main():
    """Run all examples."""
    print("=== CovetPy Backup System Examples ===\n")

    examples = [
        ("Basic Backup", example_basic_backup),
        ("Compressed & Encrypted Backup", example_compressed_encrypted_backup),
        ("S3 Backup", example_s3_backup),
        ("Restore Backup", example_restore_backup),
        ("Point-in-Time Recovery", example_point_in_time_recovery),
        ("Automated Backups", example_automated_backups),
        ("Backup Verification", example_backup_verification),
        ("Backup Statistics", example_backup_statistics),
        ("Selective Restore", example_selective_restore),
        ("Cleanup Old Backups", example_cleanup_old_backups),
    ]

    for name, example_func in examples:
        print(f"\n{'=' * 60}")
        print(f"Example: {name}")
        print(f"{'=' * 60}\n")

        try:
            # Note: Some examples require actual database connections
            # and may fail in a demo environment
            print(f"Function: {example_func.__name__}")
            print(example_func.__doc__)
        except Exception as e:
            print(f"Error (expected in demo): {e}")


if __name__ == "__main__":
    asyncio.run(main())


__all__ = [
    "example_basic_backup",
    "example_compressed_encrypted_backup",
    "example_s3_backup",
    "example_restore_backup",
    "example_point_in_time_recovery",
    "example_automated_backups",
    "example_backup_verification",
    "example_backup_statistics",
    "example_selective_restore",
    "example_cleanup_old_backups",
]
