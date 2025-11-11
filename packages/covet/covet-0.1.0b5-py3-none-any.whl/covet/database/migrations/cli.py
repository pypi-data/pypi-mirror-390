"""
Production-Grade Migration CLI

Command-line interface for managing database migrations with comprehensive
commands for creating, applying, and managing migrations.

Commands:
- covet migrate create <name> - Create new migration
- covet migrate up - Apply pending migrations
- covet migrate down [steps] - Rollback migrations
- covet migrate status - Show migration status
- covet migrate auto - Auto-generate from ORM changes
- covet migrate list - List all migrations

Author: CovetPy Team
License: MIT
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MigrationCLI:
    """Command-line interface for migrations."""

    def __init__(self):
        """Initialize CLI."""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog="covet migrate",
            description="Database migration management for CovetPy",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Create a new migration
  covet migrate create add_user_email_index

  # Apply all pending migrations
  covet migrate up

  # Apply migrations with dry-run
  covet migrate up --dry-run

  # Rollback last migration
  covet migrate down

  # Rollback last 3 migrations
  covet migrate down --steps 3

  # Show migration status
  covet migrate status

  # Auto-generate migration from model changes
  covet migrate auto

For more information: https://covetpy.readthedocs.io/migrations
            """,
        )

        # Global options
        parser.add_argument(
            "--database", default="default", help="Database alias to use (default: default)"
        )
        parser.add_argument(
            "--dialect",
            choices=["postgresql", "mysql", "sqlite"],
            default="postgresql",
            help="Database dialect (default: postgresql)",
        )
        parser.add_argument(
            "--migrations-dir",
            default="./migrations",
            help="Migrations directory (default: ./migrations)",
        )
        parser.add_argument("--config", help="Path to configuration file")
        parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Migration commands")

        # create command
        create_parser = subparsers.add_parser("create", help="Create a new migration file")
        create_parser.add_argument("name", help="Migration name (e.g., add_user_email_index)")
        create_parser.add_argument(
            "--empty", action="store_true", help="Create empty migration for manual editing"
        )

        # up command
        up_parser = subparsers.add_parser("up", help="Apply pending migrations")
        up_parser.add_argument("--target", help="Apply up to this migration")
        up_parser.add_argument(
            "--dry-run", action="store_true", help="Preview changes without applying"
        )
        up_parser.add_argument(
            "--fake", action="store_true", help="Mark as applied without executing SQL"
        )

        # down command
        down_parser = subparsers.add_parser("down", help="Rollback migrations")
        down_parser.add_argument(
            "--steps", type=int, default=1, help="Number of migrations to rollback (default: 1)"
        )
        down_parser.add_argument(
            "--dry-run", action="store_true", help="Preview changes without applying"
        )
        down_parser.add_argument(
            "--fake", action="store_true", help="Mark as rolled back without executing SQL"
        )

        # status command
        status_parser = subparsers.add_parser("status", help="Show migration status")
        status_parser.add_argument(
            "--verbose", action="store_true", help="Show detailed status information"
        )

        # auto command
        auto_parser = subparsers.add_parser(
            "auto", help="Auto-generate migration from model changes"
        )
        auto_parser.add_argument(
            "name",
            nargs="?",
            default="auto_migration",
            help="Migration name (default: auto_migration)",
        )
        auto_parser.add_argument(
            "--dry-run", action="store_true", help="Preview changes without creating migration"
        )

        # list command
        list_parser = subparsers.add_parser("list", help="List all migrations")
        list_parser.add_argument(
            "--applied-only", action="store_true", help="Show only applied migrations"
        )
        list_parser.add_argument(
            "--pending-only", action="store_true", help="Show only pending migrations"
        )

        # history command
        history_parser = subparsers.add_parser("history", help="Show migration history")

        return parser

    async def run(self, args=None):
        """
        Run CLI with provided arguments.

        Args:
            args: Command-line arguments (uses sys.argv if None)
        """
        parsed_args = self.parser.parse_args(args)

        # Configure logging
        if parsed_args.verbose:
            logging.getLogger("covet.database.migrations").setLevel(logging.DEBUG)

        # Load configuration
        config = await self._load_config(parsed_args)

        # Get database adapter
        adapter = await self._get_adapter(config)

        try:
            # Dispatch to command handler
            if parsed_args.command == "create":
                await self._handle_create(parsed_args, adapter, config)
            elif parsed_args.command == "up":
                await self._handle_up(parsed_args, adapter, config)
            elif parsed_args.command == "down":
                await self._handle_down(parsed_args, adapter, config)
            elif parsed_args.command == "status":
                await self._handle_status(parsed_args, adapter, config)
            elif parsed_args.command == "auto":
                await self._handle_auto(parsed_args, adapter, config)
            elif parsed_args.command == "list":
                await self._handle_list(parsed_args, adapter, config)
            elif parsed_args.command == "history":
                await self._handle_history(parsed_args, adapter, config)
            else:
                self.parser.print_help()
                sys.exit(1)

        finally:
            await adapter.disconnect()

    async def _load_config(self, args) -> dict:
        """Load configuration from file or args."""
        config = {
            "database": args.database,
            "dialect": args.dialect,
            "migrations_dir": args.migrations_dir,
        }

        if args.config:
            # Load from config file
            import json

            config_path = Path(args.config)
            if config_path.exists():
                with open(config_path) as f:
                    file_config = json.load(f)
                    config.update(file_config)

        return config

    async def _get_adapter(self, config: dict):
        """Get database adapter from configuration."""
        dialect = config["dialect"]

        # Import appropriate adapter
        if dialect == "postgresql":
            from ..adapters.postgresql import PostgreSQLAdapter

            adapter = PostgreSQLAdapter(
                host=config.get("host", "localhost"),
                port=config.get("port", 5432),
                database=config.get("database", "postgres"),
                user=config.get("user", "postgres"),
                password=config.get("password", ""),
            )
        elif dialect == "mysql":
            from ..adapters.mysql import MySQLAdapter

            adapter = MySQLAdapter(
                host=config.get("host", "localhost"),
                port=config.get("port", 3306),
                database=config.get("database", "mysql"),
                user=config.get("user", "root"),
                password=config.get("password", ""),
            )
        else:  # sqlite
            from ..adapters.sqlite import SQLiteAdapter

            adapter = SQLiteAdapter(database=config.get("database", "./db.sqlite3"))

        await adapter.connect()
        return adapter

    async def _handle_create(self, args, adapter, config):
        """Handle 'create' command."""
        from .migration_manager import MigrationManager

        manager = MigrationManager(
            adapter=adapter,
            dialect=config["dialect"],
            migrations_dir=config["migrations_dir"],
        )

        filepath = await manager.create_migration(args.name)

        print(f"\nCreated migration: {filepath}")
        print(f"\nEdit the migration file to add forward and backward SQL.")

    async def _handle_up(self, args, adapter, config):
        """Handle 'up' command."""
        from .migration_manager import MigrationManager

        manager = MigrationManager(
            adapter=adapter,
            dialect=config["dialect"],
            migrations_dir=config["migrations_dir"],
        )

        print(f"\nApplying migrations...")

        if args.dry_run:
            print("(DRY RUN MODE - No changes will be applied)\n")

        result = await manager.migrate_up(
            target=args.target,
            dry_run=args.dry_run,
            fake=args.fake,
        )

        if result["success"]:
            if result["applied"]:
                print(f"\nSuccessfully applied {len(result['applied'])} migrations:")
                for name in result["applied"]:
                    print(f"  - {name}")
            else:
                print("\nNo pending migrations.")

            print(f"\nDuration: {result['duration']:.2f}s")

        else:
            print(f"\nMigration failed: {result['error']}")
            sys.exit(1)

    async def _handle_down(self, args, adapter, config):
        """Handle 'down' command."""
        from .migration_manager import MigrationManager

        manager = MigrationManager(
            adapter=adapter,
            dialect=config["dialect"],
            migrations_dir=config["migrations_dir"],
        )

        print(f"\nRolling back {args.steps} migration(s)...")

        if args.dry_run:
            print("(DRY RUN MODE - No changes will be applied)\n")

        result = await manager.migrate_down(
            steps=args.steps,
            dry_run=args.dry_run,
            fake=args.fake,
        )

        if result["success"]:
            if result["rolled_back"]:
                print(f"\nSuccessfully rolled back {len(result['rolled_back'])} migrations:")
                for name in result["rolled_back"]:
                    print(f"  - {name}")
            else:
                print("\nNo migrations to rollback.")

            print(f"\nDuration: {result['duration']:.2f}s")

        else:
            print(f"\nRollback failed: {result['error']}")
            sys.exit(1)

    async def _handle_status(self, args, adapter, config):
        """Handle 'status' command."""
        from .migration_manager import MigrationManager

        manager = MigrationManager(
            adapter=adapter,
            dialect=config["dialect"],
            migrations_dir=config["migrations_dir"],
        )

        status_list = await manager.get_status()

        if not status_list:
            print("\nNo migrations found.")
            return

        print(f"\nMigration Status ({len(status_list)} total):")
        print("=" * 80)

        applied_count = sum(1 for s in status_list if s.applied)
        pending_count = len(status_list) - applied_count

        for status in status_list:
            mark = "[X]" if status.applied else "[ ]"
            timestamp = ""

            if status.applied and status.applied_at:
                timestamp = f" (applied {status.applied_at})"

            print(f"{mark} {status.name}{timestamp}")

        print("=" * 80)
        print(f"\nApplied: {applied_count}, Pending: {pending_count}")

    async def _handle_auto(self, args, adapter, config):
        """Handle 'auto' command."""
        from .migration_generator import MigrationGenerator
        from .schema_diff import ModelSchemaReader, SchemaComparator, SchemaReader

        print("\nAuto-generating migration from model changes...")

        # Read current database schema
        schema_reader = SchemaReader(adapter, config["dialect"])
        db_schema = await schema_reader.read_schema()

        # Read model schema
        # TODO: Import and register models
        model_schema = {}  # Placeholder

        if not model_schema:
            print("\nNo models found. Make sure your models are properly registered.")
            return

        # Compare schemas
        comparator = SchemaComparator()
        diff = comparator.compare(db_schema, model_schema)

        if not diff.has_changes():
            print("\nNo schema changes detected.")
            return

        # Print detected changes
        print("\nDetected changes:")
        if diff.added_tables:
            print(f"  - Added tables: {', '.join(diff.added_tables)}")
        if diff.removed_tables:
            print(f"  - Removed tables: {', '.join(diff.removed_tables)}")
        if diff.added_columns:
            for table, cols in diff.added_columns.items():
                print(f"  - Added columns in {table}: {', '.join(c.name for c in cols)}")
        if diff.removed_columns:
            for table, cols in diff.removed_columns.items():
                print(f"  - Removed columns in {table}: {', '.join(c.name for c in cols)}")

        if args.dry_run:
            print("\n(DRY RUN MODE - Migration file not created)")
            return

        # Generate migration
        generator = MigrationGenerator(
            dialect=config["dialect"], migrations_dir=config["migrations_dir"]
        )

        filepath = generator.generate_from_diff(diff, args.name)

        print(f"\nGenerated migration: {filepath}")

    async def _handle_list(self, args, adapter, config):
        """Handle 'list' command."""
        from .migration_manager import MigrationManager

        manager = MigrationManager(
            adapter=adapter,
            dialect=config["dialect"],
            migrations_dir=config["migrations_dir"],
        )

        status_list = await manager.get_status()

        if not status_list:
            print("\nNo migrations found.")
            return

        # Filter if requested
        if args.applied_only:
            status_list = [s for s in status_list if s.applied]
        elif args.pending_only:
            status_list = [s for s in status_list if not s.applied]

        print(f"\nMigrations ({len(status_list)}):")
        for status in status_list:
            status_str = "APPLIED" if status.applied else "PENDING"
            print(f"  {status.name} [{status_str}]")

    async def _handle_history(self, args, adapter, config):
        """Handle 'history' command."""
        from .runner import MigrationHistory

        history = MigrationHistory(adapter)
        applied = await history.get_applied_migrations()

        if not applied:
            print("\nNo migration history.")
            return

        print(f"\nMigration History ({len(applied)} applied):")
        print("=" * 80)

        for record in applied:
            print(f"{record['name']}")
            print(f"  Applied: {record['applied_at']}")
            print(f"  App: {record.get('app', 'default')}")
            print()


def main():
    """Main CLI entry point."""
    cli = MigrationCLI()

    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


__all__ = ["MigrationCLI", "main"]
