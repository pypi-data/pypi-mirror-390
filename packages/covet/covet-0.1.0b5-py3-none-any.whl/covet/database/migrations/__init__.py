"""
CovetPy Database Migrations

Django-style migration system for CovetPy ORM. Supports PostgreSQL, MySQL, and SQLite.

This module provides a complete migration workflow:
1. `makemigrations` - Generate migration files from model changes
2. `migrate` - Apply migrations to database
3. `rollback` - Rollback applied migrations

Components:
- ModelReader: Extracts schema from ORM models
- DatabaseIntrospector: Reads current database schema
- DiffEngine: Compares model vs database schemas
- MigrationGenerator: Generates migration SQL
- MigrationRunner: Executes migrations

Example:
    # Generate migrations
    from covet.database.migrations import make_migrations
    await make_migrations(models=[User, Post], dialect='postgresql')

    # Apply migrations
    from covet.database.migrations import run_migrations
    await run_migrations(adapter, './migrations')

    # Rollback
    from covet.database.migrations import rollback_migrations
    await rollback_migrations(adapter, steps=1)
"""

from .diff_engine import (
    DatabaseIntrospector,
    DiffEngine,
    MigrationOperation,
    OperationType,
)
from .generator import (
    MigrationFile,
    MigrationGenerator,
    MySQLGenerator,
    PostgreSQLGenerator,
    SQLGenerator,
    SQLiteGenerator,
)
from .model_reader import (
    ColumnSchema,
    ConstraintSchema,
    IndexSchema,
    ModelReader,
    RelationshipSchema,
    TableSchema,
)
from .runner import (
    Migration,
    MigrationHistory,
    MigrationRunner,
)

__all__ = [
    # Model Reader
    "ModelReader",
    "TableSchema",
    "ColumnSchema",
    "IndexSchema",
    "ConstraintSchema",
    "RelationshipSchema",
    # Diff Engine
    "DiffEngine",
    "DatabaseIntrospector",
    "MigrationOperation",
    "OperationType",
    # Generator
    "MigrationGenerator",
    "MigrationFile",
    "SQLGenerator",
    "PostgreSQLGenerator",
    "MySQLGenerator",
    "SQLiteGenerator",
    # Runner
    "MigrationRunner",
    "Migration",
    "MigrationHistory",
]


__version__ = "1.0.0"
