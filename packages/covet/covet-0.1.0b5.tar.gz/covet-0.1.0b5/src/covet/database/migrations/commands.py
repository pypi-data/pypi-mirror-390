"""
Migration CLI Commands

Django-style CLI commands for managing database migrations:
- makemigrations: Generate migration files from model changes
- migrate: Apply migrations to database
- rollback: Rollback applied migrations
- showmigrations: Display migration status

These commands are designed to be integrated with a manage.py or CLI tool.

Example usage:
    # From Python
    import asyncio
    from covet.database.migrations.commands import makemigrations, migrate, rollback

    # Generate migrations
    asyncio.run(makemigrations(
        models=[User, Post, Comment],
        migrations_dir='./migrations',
        dialect='postgresql',
        name='add_user_posts'
    ))

    # Apply migrations
    asyncio.run(migrate(
        adapter=adapter,
        migrations_dir='./migrations'
    ))

    # Rollback
    asyncio.run(rollback(
        adapter=adapter,
        steps=1
    ))

For CLI integration:
    python manage.py makemigrations
    python manage.py migrate
    python manage.py migrate --rollback
    python manage.py showmigrations
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Type

from .diff_engine import DatabaseIntrospector, DiffEngine
from .generator import MigrationGenerator
from .model_reader import ModelReader
from .runner import MigrationRunner

logger = logging.getLogger(__name__)


async def makemigrations(
    models: List[Type],
    adapter,
    migrations_dir: str = "./migrations",
    dialect: str = "postgresql",
    name: Optional[str] = None,
    app_name: str = "default",
    dry_run: bool = False,
) -> Optional[str]:
    """
    Generate migration files from model changes.

    This is equivalent to Django's `python manage.py makemigrations`.
    It compares your current ORM models against the actual database schema
    and generates a migration file for any detected changes.

    Args:
        models: List of Model classes to check for changes
        adapter: Database adapter (connected)
        migrations_dir: Directory to save migration files
        dialect: Database dialect ('postgresql', 'mysql', 'sqlite')
        name: Custom migration name (auto-generated if not provided)
        app_name: App name for the migration
        dry_run: Show changes without creating migration file

    Returns:
        Path to created migration file, or None if no changes

    Example:
        from covet.database.orm import Model
        from covet.database.adapters.postgresql import PostgreSQLAdapter

        adapter = PostgreSQLAdapter(host='localhost', database='mydb')
        await adapter.connect()

        migration_file = await makemigrations(
            models=[User, Post, Comment],
            adapter=adapter,
            migrations_dir='./migrations',
            dialect='postgresql',
            name='add_posts_table'
        )

        if migration_file:
            print(f"Created: {migration_file}")
        else:
            print("No changes detected")
    """
    logger.info("Checking for model changes...")

    # Step 1: Read model schemas
    logger.info(f"Reading {len(models)} model(s)...")
    reader = ModelReader()
    model_schemas = reader.read_models(models, dialect=dialect)

    logger.info(f"Found {len(model_schemas)} table(s) in models")

    # Step 2: Read database schemas
    logger.info("Introspecting database schema...")
    introspector = DatabaseIntrospector(adapter, dialect=dialect)
    db_schemas = await introspector.get_all_schemas()

    logger.info(f"Found {len(db_schemas)} table(s) in database")

    # Step 3: Compare schemas and generate operations
    logger.info("Comparing schemas...")
    diff_engine = DiffEngine()
    operations = diff_engine.compare_schemas(model_schemas, db_schemas)

    if not operations:
        logger.info("No changes detected")
        return None

    logger.info(f"Detected {len(operations)} change(s):")
    for op in operations:
        logger.info(f"  - {op.operation_type.value}: {op.table_name}")

    if dry_run:
        logger.info("Dry run - not creating migration file")
        return None

    # Step 4: Generate migration file
    logger.info("Generating migration file...")
    generator = MigrationGenerator(dialect=dialect)

    # Get next migration number
    next_number = generator.get_next_migration_number(migrations_dir)

    # Generate migration name
    if not name:
        # Auto-generate name based on operations
        if len(operations) == 1:
            op = operations[0]
            if op.operation_type.name.startswith("CREATE"):
                name = f"create_{op.table_name}"
            elif op.operation_type.name.startswith("DROP"):
                name = f"drop_{op.table_name}"
            elif op.operation_type.name.startswith("ALTER"):
                name = f"alter_{op.table_name}"
            else:
                name = "auto"
        else:
            name = "auto"

    migration_name = f"{next_number}_{name}"

    # Generate migration
    migration_file = generator.generate_migration(
        operations=operations, migration_name=migration_name, app_name=app_name
    )

    # Save to disk
    filepath = generator.save_migration(migration_file, migrations_dir)

    logger.info(f"Created migration: {filepath}")
    return filepath


async def migrate(
    adapter,
    migrations_dir: str = "./migrations",
    target: Optional[str] = None,
    fake: bool = False,
    show_sql: bool = False,
) -> List[str]:
    """
    Apply pending migrations to the database.

    This is equivalent to Django's `python manage.py migrate`.
    It finds all unapplied migrations and executes them in order.

    Args:
        adapter: Database adapter (connected)
        migrations_dir: Directory containing migration files
        target: Target migration name (apply up to this migration)
        fake: Mark migrations as applied without executing SQL
        show_sql: Display SQL that will be executed

    Returns:
        List of applied migration names

    Example:
        from covet.database.adapters.postgresql import PostgreSQLAdapter

        adapter = PostgreSQLAdapter(host='localhost', database='mydb')
        await adapter.connect()

        # Apply all pending migrations
        applied = await migrate(adapter, './migrations')
        print(f"Applied {len(applied)} migrations")

        # Apply up to specific migration
        applied = await migrate(
            adapter,
            './migrations',
            target='0003_add_indexes'
        )

        # Fake apply (for initial migration of existing database)
        applied = await migrate(adapter, './migrations', fake=True)
    """
    # Detect dialect from adapter
    adapter_type = type(adapter).__name__

    if "PostgreSQL" in adapter_type:
        dialect = "postgresql"
    elif "MySQL" in adapter_type:
        dialect = "mysql"
    elif "SQLite" in adapter_type:
        dialect = "sqlite"
    else:
        dialect = "postgresql"  # Default

    logger.info(f"Running migrations (dialect: {dialect})...")

    # Create runner
    runner = MigrationRunner(adapter, dialect=dialect)

    # Show pending migrations if show_sql
    if show_sql:
        status = await runner.show_migrations(migrations_dir)
        pending = [name for name, applied in status.items() if not applied]

        logger.info("Pending migrations:")
        for name in pending:
            logger.info(f"  {name}")

    # Run migrations
    applied = await runner.migrate(migrations_dir=migrations_dir, target=target, fake=fake)

    if applied:
        logger.info(f"Successfully applied {len(applied)} migration(s)")
    else:
        logger.info("No migrations to apply")

    return applied


async def rollback(
    adapter, migrations_dir: Optional[str] = None, steps: int = 1, fake: bool = False
) -> List[str]:
    """
    Rollback applied migrations.

    This is equivalent to Django's `python manage.py migrate <app> <previous_migration>`.
    It reverses the last N migrations.

    Args:
        adapter: Database adapter (connected)
        migrations_dir: Directory containing migration files (optional, needed for loading migration classes)
        steps: Number of migrations to rollback (default: 1)
        fake: Mark as rolled back without executing SQL

    Returns:
        List of rolled back migration names

    Example:
        from covet.database.adapters.postgresql import PostgreSQLAdapter

        adapter = PostgreSQLAdapter(host='localhost', database='mydb')
        await adapter.connect()

        # Rollback last migration
        rolled_back = await rollback(adapter)
        print(f"Rolled back: {rolled_back}")

        # Rollback last 3 migrations
        rolled_back = await rollback(adapter, steps=3)

        # Fake rollback
        rolled_back = await rollback(adapter, fake=True)
    """
    # Detect dialect from adapter
    adapter_type = type(adapter).__name__

    if "PostgreSQL" in adapter_type:
        dialect = "postgresql"
    elif "MySQL" in adapter_type:
        dialect = "mysql"
    elif "SQLite" in adapter_type:
        dialect = "sqlite"
    else:
        dialect = "postgresql"  # Default

    logger.info(f"Rolling back {steps} migration(s)...")

    # Create runner
    runner = MigrationRunner(adapter, dialect=dialect)

    # Rollback migrations
    rolled_back = await runner.rollback(steps=steps, fake=fake)

    if rolled_back:
        logger.info(f"Successfully rolled back {len(rolled_back)} migration(s)")
    else:
        logger.info("No migrations to rollback")

    return rolled_back


async def showmigrations(
    adapter, migrations_dir: str = "./migrations", verbose: bool = False
) -> dict:
    """
    Display migration status.

    This is equivalent to Django's `python manage.py showmigrations`.
    It shows which migrations have been applied and which are pending.

    Args:
        adapter: Database adapter (connected)
        migrations_dir: Directory containing migration files
        verbose: Show detailed information (applied dates, etc.)

    Returns:
        Dictionary mapping migration names to status info

    Example:
        from covet.database.adapters.postgresql import PostgreSQLAdapter

        adapter = PostgreSQLAdapter(host='localhost', database='mydb')
        await adapter.connect()

        status = await showmigrations(adapter, './migrations')

        # Display status
        for name, info in status.items():
            mark = '[✓]' if info['applied'] else '[ ]'
            print(f"{mark} {name}")
    """
    # Detect dialect from adapter
    adapter_type = type(adapter).__name__

    if "PostgreSQL" in adapter_type:
        dialect = "postgresql"
    elif "MySQL" in adapter_type:
        dialect = "mysql"
    elif "SQLite" in adapter_type:
        dialect = "sqlite"
    else:
        dialect = "postgresql"  # Default

    logger.info("Checking migration status...")

    # Create runner
    runner = MigrationRunner(adapter, dialect=dialect)

    # Get status
    status_map = await runner.show_migrations(migrations_dir)

    # Build detailed status
    result = {}

    if verbose:
        # Get applied migrations with timestamps
        applied_migrations = await runner.history.get_applied_migrations()
        applied_dict = {m["name"]: m for m in applied_migrations}

        for migration_name, is_applied in status_map.items():
            if is_applied and migration_name in applied_dict:
                result[migration_name] = {
                    "applied": True,
                    "applied_at": applied_dict[migration_name]["applied_at"],
                    "app": applied_dict[migration_name]["app"],
                }
            else:
                result[migration_name] = {
                    "applied": False,
                    "applied_at": None,
                    "app": None,
                }
    else:
        # Simple status
        for migration_name, is_applied in status_map.items():
            result[migration_name] = {"applied": is_applied}

    # Display status
    logger.info("Migration status:")
    for migration_name, info in result.items():
        if info["applied"]:
            mark = "[✓]"
            extra = f" (applied: {info.get('applied_at', 'unknown')})" if verbose else ""
        else:
            mark = "[ ]"
            extra = ""

        logger.info(f"  {mark} {migration_name}{extra}")

    applied_count = sum(1 for info in result.values() if info["applied"])
    total_count = len(result)
    logger.info(f"Applied: {applied_count}/{total_count}")

    return result


async def squashmigrations(
    migrations_dir: str, start_migration: str, end_migration: str, squashed_name: str
):
    """
    Squash multiple migrations into one.

    Combines multiple sequential migrations into a single migration file.
    This is useful for optimizing migration history.

    Args:
        migrations_dir: Directory containing migration files
        start_migration: First migration to squash
        end_migration: Last migration to squash
        squashed_name: Name for squashed migration

    Note:
        This is an advanced operation. Ensure all migrations have been
        applied to production before squashing.

    Example:
        await squashmigrations(
            './migrations',
            start_migration='0001_initial',
            end_migration='0010_add_indexes',
            squashed_name='0001_squashed_0010'
        )
    """
    # TODO: Implement migration squashing
    raise NotImplementedError(
        "Migration squashing is not yet implemented. "
        "This is a planned feature for future releases."
    )


__all__ = [
    "makemigrations",
    "migrate",
    "rollback",
    "showmigrations",
    "squashmigrations",
]
