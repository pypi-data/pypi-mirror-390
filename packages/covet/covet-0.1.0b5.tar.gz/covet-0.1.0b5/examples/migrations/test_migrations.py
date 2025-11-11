#!/usr/bin/env python3
"""
Test script for CovetPy migration system.

This script demonstrates the migration system usage.
"""

import sys
from pathlib import Path

# Add CovetPy to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from covet.orm.connection import ConnectionConfig, register_database
from covet.orm.migrations import (
    Migration,
    MigrationEngine,
    MigrationRunner,
    MigrationWriter,
    MigrationLoader,
    CreateTable,
    AddColumn,
    CreateIndex,
)
from covet.orm.fields import (
    AutoField,
    CharField,
    IntegerField,
    BooleanField,
    DateTimeField,
)


def test_manual_migration():
    """Test creating and applying a migration manually."""
    print("\n=== Testing Manual Migration ===\n")

    # Setup database
    config = ConnectionConfig(engine="sqlite", database=":memory:")
    register_database("default", config)
    print("Database configured (in-memory SQLite)")

    # Create a migration
    migration = Migration("create_test_table", "default")

    # Add operations
    fields = {
        "id": AutoField(),
        "name": CharField(max_length=100, null=False),
        "active": BooleanField(default=True),
    }
    migration.create_table("test_users", fields)

    print(f"Created migration: {migration.name}")
    print(f"Operations: {len(migration.operations)}")

    # Apply migration
    runner = MigrationRunner("default")
    runner.apply_migration(migration)

    print("Migration applied successfully!")

    # Show applied migrations
    applied = runner.get_applied_migrations()
    print(f"\nApplied migrations: {len(applied)}")
    for key, state in applied.items():
        print(f"  - {key}: {state.checksum[:8]}...")

    # Rollback
    print("\nRolling back migration...")
    runner.rollback_migration(migration)
    print("Migration rolled back successfully!")


def test_auto_migration():
    """Test auto-generating migrations from models."""
    print("\n=== Testing Auto-Generated Migration ===\n")

    # Import models (this registers them)
    from models import User, Category, Product

    # Setup database
    config = ConnectionConfig(engine="sqlite", database=":memory:")
    register_database("default", config)
    print("Database configured (in-memory SQLite)")

    # Detect changes
    engine = MigrationEngine("default")
    models = [User, Category, Product]

    print(f"Detecting changes for {len(models)} models...")
    operations = engine.detect_changes(models)

    print(f"\nDetected {len(operations)} operations:")
    for i, op in enumerate(operations, 1):
        print(f"  {i}. {op.describe()}")

    if operations:
        # Generate migration
        migration = engine.generate_migration("initial", operations)
        print(f"\nGenerated migration: {migration.name}")

        # Apply migration
        runner = MigrationRunner("default")
        runner.apply_migration(migration)
        print("Migration applied successfully!")


def test_migration_file_generation():
    """Test writing and loading migration files."""
    print("\n=== Testing Migration File Generation ===\n")

    # Create a simple migration
    migration = Migration("test_file_generation", "default")
    migration.create_table(
        "file_test",
        {
            "id": AutoField(),
            "name": CharField(max_length=50),
            "count": IntegerField(default=0),
        },
    )

    # Write to file
    import tempfile
    import os

    migrations_dir = tempfile.mkdtemp()
    print(f"Migrations directory: {migrations_dir}")

    writer = MigrationWriter(migrations_dir)
    filepath = writer.write_migration(migration)

    print(f"Migration written to: {filepath}")
    print(f"File exists: {os.path.exists(filepath)}")

    # Load migrations
    loader = MigrationLoader(migrations_dir)
    loaded_migrations = loader.load_migrations()

    print(f"\nLoaded {len(loaded_migrations)} migrations")
    for mig in loaded_migrations:
        print(f"  - {mig.name}: {len(mig.operations)} operations")

    # Cleanup
    import shutil

    shutil.rmtree(migrations_dir)
    print("\nCleanup completed")


def test_schema_introspection():
    """Test database schema introspection."""
    print("\n=== Testing Schema Introspection ===\n")

    # Setup database with a table
    config = ConnectionConfig(engine="sqlite", database=":memory:")
    register_database("default", config)

    # Create a table manually
    from covet.orm.connection import get_connection_pool

    pool = get_connection_pool("default")

    with pool.connection() as conn:
        conn.execute(
            """
            CREATE TABLE introspect_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                active INTEGER DEFAULT 1
            )
        """
        )
        conn.commit()

    print("Created test table")

    # Introspect schema
    from covet.orm.migrations import SchemaIntrospector

    with pool.connection() as conn:
        introspector = SchemaIntrospector(conn)

        # Get tables
        tables = introspector.get_tables()
        print(f"\nTables: {tables}")

        # Get table schema
        schema = introspector.get_table_schema("introspect_test")
        print(f"\nTable: {schema.name}")
        print("Columns:")
        for col_name, col in schema.columns.items():
            print(f"  - {col_name}: {col.data_type} (nullable={col.nullable})")


def main():
    """Run all tests."""
    print("=" * 60)
    print("CovetPy Migration System - Test Suite")
    print("=" * 60)

    try:
        test_manual_migration()
        print("\n" + "=" * 60)

        test_auto_migration()
        print("\n" + "=" * 60)

        test_migration_file_generation()
        print("\n" + "=" * 60)

        test_schema_introspection()
        print("\n" + "=" * 60)

        print("\n✓ All tests completed successfully!")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
