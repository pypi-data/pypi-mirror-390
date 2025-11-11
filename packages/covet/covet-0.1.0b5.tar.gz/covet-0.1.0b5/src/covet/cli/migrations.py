"""
CovetPy Migration Management CLI

Command-line interface for database migrations.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Find project root by looking for common markers."""
    current = Path.cwd()
    markers = ["pyproject.toml", "setup.py", "requirements.txt", ".git"]

    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent

    return Path.cwd()


def setup_environment():
    """Setup Python path and import necessary modules."""
    project_root = get_project_root()
    sys.path.insert(0, str(project_root))

    # Try to import CovetPy modules
    try:
        from covet.orm.connection import ConnectionConfig, register_database
        from covet.orm.migrations import (
            MigrationEngine,
            MigrationLoader,
            MigrationRunner,
            MigrationWriter,
        )
        from covet.orm.models import ModelRegistry

        return {
            "ConnectionConfig": ConnectionConfig,
            "register_database": register_database,
            "MigrationEngine": MigrationEngine,
            "MigrationLoader": MigrationLoader,
            "MigrationRunner": MigrationRunner,
            "MigrationWriter": MigrationWriter,
            "ModelRegistry": ModelRegistry,
        }
    except ImportError as e:
        logger.error(f"Failed to import CovetPy modules: {e}")
        logger.error("Make sure CovetPy is installed and in your Python path")
        sys.exit(1)


def load_database_config() -> dict:
    """Load database configuration from environment or config file."""
    # Try to load from environment variables
    config = {
        "engine": os.getenv("DB_ENGINE", "sqlite"),
        "database": os.getenv("DB_NAME", "db.sqlite3"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT"),
        "username": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
    }

    # Try to load from config file
    config_file = Path.cwd() / "covet.config.py"
    if config_file.exists():
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("covet_config", config_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "DATABASE"):
                config.update(module.DATABASE)
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}")

    return config


def setup_database(modules: dict):
    """Setup database connection."""
    config_dict = load_database_config()

    ConnectionConfig = modules["ConnectionConfig"]
    register_database = modules["register_database"]

    config = ConnectionConfig(**config_dict)
    register_database("default", config)

    logger.info(f"Connected to {config.engine} database: {config.database}")


def discover_models(modules: dict) -> List:
    """Discover all model classes in the project."""
    ModelRegistry = modules["ModelRegistry"]
    models = ModelRegistry.get_all_models()

    if not models:
        logger.warning("No models found in the project")
        logger.info("Make sure your models inherit from covet.orm.Model and are imported")

    return models


def makemigrations(args, modules: dict):
    """Generate migrations from model changes."""
    logger.info("Detecting model changes...")

    setup_database(modules)

    MigrationEngine = modules["MigrationEngine"]
    MigrationWriter = modules["MigrationWriter"]

    # Discover models
    models = discover_models(modules)

    if not models:
        logger.error("No models found. Cannot generate migrations.")
        return

    # Detect changes
    engine = MigrationEngine(database="default")
    operations = engine.detect_changes(models)

    if not operations:
        logger.info("No changes detected.")
        return

    # Display detected changes
    logger.info(f"Detected {len(operations)} changes:")
    for i, op in enumerate(operations, 1):
        logger.info(f"  {i}. {op.describe()}")

    # Ask for migration name
    migration_name = (
        args.name
        or input("\nEnter migration name (or press Enter for auto-generated name): ").strip()
    )

    if not migration_name:
        # Auto-generate name based on operations
        if len(operations) == 1:
            migration_name = operations[0].describe().lower().replace(" ", "_")
        else:
            migration_name = "auto_migration"

    # Generate migration
    migration = engine.generate_migration(migration_name, operations, app=args.app)

    # Write migration file
    migrations_dir = args.migrations_dir or "migrations"
    writer = MigrationWriter(migrations_dir)
    filepath = writer.write_migration(migration)

    logger.info(f"\nMigration created: {filepath}")
    logger.info(f"Run 'covet migrate' to apply these changes.")


def migrate(args, modules: dict):
    """Apply pending migrations."""
    logger.info("Applying migrations...")

    setup_database(modules)

    MigrationLoader = modules["MigrationLoader"]
    MigrationRunner = modules["MigrationRunner"]

    # Load migrations
    migrations_dir = args.migrations_dir or "migrations"
    loader = MigrationLoader(migrations_dir)
    migrations = loader.load_migrations()

    if not migrations:
        logger.info("No migrations found.")
        return

    # Get runner
    runner = MigrationRunner(database="default")

    # Filter pending migrations
    applied = runner.get_applied_migrations()
    pending = [m for m in migrations if f"{m.app}.{m.name}" not in applied]

    if not pending:
        logger.info("No pending migrations.")
        return

    # Display pending migrations
    logger.info(f"Found {len(pending)} pending migrations:")
    for migration in pending:
        logger.info(f"  - {migration.app}.{migration.name}")

    # Apply migrations
    if not args.yes:
        confirm = input("\nApply these migrations? [y/N]: ").strip().lower()
        if confirm != "y":
            logger.info("Cancelled.")
            return

    try:
        runner.apply_migrations(pending, fake=args.fake)
        logger.info("\nAll migrations applied successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


def rollback(args, modules: dict):
    """Rollback last migration."""
    logger.info("Rolling back migrations...")

    setup_database(modules)

    MigrationLoader = modules["MigrationLoader"]
    MigrationRunner = modules["MigrationRunner"]

    # Get runner
    runner = MigrationRunner(database="default")

    # Get applied migrations
    applied = runner.get_applied_migrations()

    if not applied:
        logger.info("No migrations to rollback.")
        return

    # Get last migration
    last_key = list(applied.keys())[-1]
    last_migration_state = applied[last_key]

    logger.info(f"Rolling back: {last_key}")
    logger.info(f"Applied at: {last_migration_state.applied_at}")

    # Load migration
    migrations_dir = args.migrations_dir or "migrations"
    loader = MigrationLoader(migrations_dir)
    migrations = loader.load_migrations()

    # Find the migration to rollback
    migration_to_rollback = None
    for migration in migrations:
        if (
            migration.name == last_migration_state.name
            and migration.app == last_migration_state.app
        ):
            migration_to_rollback = migration
            break

    if not migration_to_rollback:
        logger.error(f"Migration file not found for {last_key}")
        return

    # Confirm rollback
    if not args.yes:
        confirm = input("\nRollback this migration? [y/N]: ").strip().lower()
        if confirm != "y":
            logger.info("Cancelled.")
            return

    try:
        runner.rollback_migration(migration_to_rollback)
        logger.info("Migration rolled back successfully!")
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        sys.exit(1)


def showmigrations(args, modules: dict):
    """Show migration status."""
    logger.info("Migration status:\n")

    setup_database(modules)

    MigrationLoader = modules["MigrationLoader"]
    MigrationRunner = modules["MigrationRunner"]

    # Load all migrations
    migrations_dir = args.migrations_dir or "migrations"
    loader = MigrationLoader(migrations_dir)
    all_migrations = loader.load_migrations()

    # Get applied migrations
    runner = MigrationRunner(database="default")
    applied = runner.get_applied_migrations()

    if not all_migrations:
        logger.info("No migrations found.")
        return

    # Display status
    for migration in all_migrations:
        key = f"{migration.app}.{migration.name}"
        if key in applied:
            status = "[X] APPLIED"
            applied_at = applied[key].applied_at
            logger.info(f"{status} {key} (applied at {applied_at})")
        else:
            status = "[ ] PENDING"
            logger.info(f"{status} {key}")

    # Summary
    logger.info(
        f"\nTotal: {len(all_migrations)} | Applied: {len(applied)} | Pending: {len(all_migrations) - len(applied)}"
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CovetPy Migration Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # makemigrations command
    makemigrations_parser = subparsers.add_parser(
        "makemigrations", help="Generate migrations from model changes"
    )
    makemigrations_parser.add_argument(
        "--name", "-n", help="Migration name (auto-generated if not provided)"
    )
    makemigrations_parser.add_argument("--app", "-a", default="default", help="App name")
    makemigrations_parser.add_argument(
        "--migrations-dir", "-d", help="Migrations directory (default: migrations)"
    )

    # migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Apply pending migrations")
    migrate_parser.add_argument(
        "--fake",
        action="store_true",
        help="Mark migrations as applied without executing",
    )
    migrate_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    migrate_parser.add_argument(
        "--migrations-dir", "-d", help="Migrations directory (default: migrations)"
    )

    # rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback last migration")
    rollback_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    rollback_parser.add_argument(
        "--migrations-dir", "-d", help="Migrations directory (default: migrations)"
    )

    # showmigrations command
    showmigrations_parser = subparsers.add_parser("showmigrations", help="Show migration status")
    showmigrations_parser.add_argument(
        "--migrations-dir", "-d", help="Migrations directory (default: migrations)"
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Setup environment
    modules = setup_environment()

    # Execute command
    commands = {
        "makemigrations": makemigrations,
        "migrate": migrate,
        "rollback": rollback,
        "showmigrations": showmigrations,
    }

    if args.command in commands:
        try:
            commands[args.command](args, modules)
        except KeyboardInterrupt:
            logger.info("\nOperation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
