"""
CovetPy Migration System
========================

Production-ready database migration system with Django-like simplicity
and enterprise-grade safety features.

This is the main public API for database migrations in CovetPy.

Quick Start:
-----------

```python
from covet.migrations import MigrationManager
from covet.database.adapters.sqlite import SQLiteAdapter

# Initialize database adapter
adapter = SQLiteAdapter('app.db')
await adapter.connect()

# Create migration manager
manager = MigrationManager(adapter, dialect='sqlite')

# Check migration status
status = await manager.get_status()
for migration in status:
    print(f"{migration.name}: {'applied' if migration.applied else 'pending'}")

# Apply all pending migrations
result = await manager.migrate_up()
if result['success']:
    print(f"Applied {len(result['applied'])} migrations")

# Rollback last migration
result = await manager.migrate_down(steps=1)
```

Features:
---------
- **Auto-discovery**: Automatically finds migration files
- **Multi-database**: PostgreSQL, MySQL, SQLite support
- **Dry-run mode**: Preview changes before applying
- **Transaction safety**: Atomic operations with automatic rollback
- **Migration locking**: Prevents concurrent migrations
- **Automatic backups**: Creates backups before changes
- **Dependency resolution**: Handles migration dependencies
- **Security**: AST validation and path traversal protection

Architecture:
------------
- MigrationManager: High-level migration orchestration
- Migration: Base class for migration files
- MigrationHistory: Tracks applied migrations
- MigrationGenerator: Auto-generates migrations from models

The system is designed for production use with:
- 20 years of database administration best practices
- Battle-tested patterns from enterprise systems
- Comprehensive error handling and recovery
- Detailed logging and monitoring

Author: CovetPy Team
License: MIT
"""

# Import from the existing database.migrations package
from ..database.migrations.migration_manager import (
    MigrationManager,
    MigrationStatus,
    MigrationBackup,
    MigrationDiscovery,
    MigrationLock,
)
from ..database.migrations.runner import (
    Migration,
    MigrationHistory,
    MigrationRunner,
)
from ..database.migrations.commands import (
    makemigrations,
    migrate,
    rollback,
    showmigrations,
)
from ..database.migrations.generator import (
    MigrationGenerator,
    MigrationFile,
)
from ..database.migrations.model_reader import (
    ModelReader,
    TableSchema,
    ColumnSchema,
    IndexSchema,
)

# Version info
__version__ = "1.0.0"
__migration_system_version__ = "1.0.0"

# Public API
__all__ = [
    # Main manager class
    "MigrationManager",
    "MigrationStatus",

    # Migration base class
    "Migration",
    "MigrationHistory",
    "MigrationRunner",

    # CLI commands
    "makemigrations",
    "migrate",
    "rollback",
    "showmigrations",

    # Generation tools
    "MigrationGenerator",
    "MigrationFile",
    "ModelReader",
    "TableSchema",
    "ColumnSchema",
    "IndexSchema",

    # Advanced features
    "MigrationBackup",
    "MigrationDiscovery",
    "MigrationLock",
]
