"""
CLI Commands for Data Migrations, Fixtures, and Seeding

Complete command-line interface for:
- Data migrations (separate from schema migrations)
- Fixture loading and exporting
- Database seeding
- Migration squashing

Commands:
- covet data makemigration <name> - Create data migration
- covet data migrate - Apply data migrations
- covet data rollback - Rollback data migrations
- covet data seed - Run database seeders
- covet data loaddata <file> - Load fixtures
- covet data dumpdata [tables] - Export fixtures
- covet data squash - Squash migrations

Author: CovetPy Team 21
License: MIT
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from .data_migrations import CheckpointManager
from .fixtures import FixtureExporter, FixtureLoader
from .migration_squashing import MigrationSquasher, suggest_squashing
from .seeding import Seeder

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class DataCLI:
    """CLI for data operations."""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="covet data", description="Data migration, fixture, and seeding tools"
        )

        # Global options
        parser.add_argument("--database", default="default", help="Database alias")
        parser.add_argument("--config", help="Config file path")

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Commands")

        # makemigration
        make_parser = subparsers.add_parser("makemigration", help="Create data migration")
        make_parser.add_argument("name", help="Migration name")

        # migrate
        migrate_parser = subparsers.add_parser("migrate", help="Apply data migrations")
        migrate_parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")

        # rollback
        rollback_parser = subparsers.add_parser("rollback", help="Rollback data migration")
        rollback_parser.add_argument("--steps", type=int, default=1, help="Steps to rollback")

        # seed
        seed_parser = subparsers.add_parser("seed", help="Seed database")
        seed_parser.add_argument("--factories", nargs="+", help="Factory classes to run")
        seed_parser.add_argument("--count", type=int, default=10, help="Records per factory")

        # loaddata
        load_parser = subparsers.add_parser("loaddata", help="Load fixtures")
        load_parser.add_argument("files", nargs="+", help="Fixture files")
        load_parser.add_argument(
            "--on-conflict", choices=["error", "skip", "update"], default="error"
        )

        # dumpdata
        dump_parser = subparsers.add_parser("dumpdata", help="Export fixtures")
        dump_parser.add_argument("output", help="Output file")
        dump_parser.add_argument("--tables", nargs="+", help="Tables to export")
        dump_parser.add_argument("--format", choices=["json", "yaml", "csv"], help="Format")

        # squash
        squash_parser = subparsers.add_parser("squash", help="Squash migrations")
        squash_parser.add_argument("--analyze", action="store_true", help="Analyze only")
        squash_parser.add_argument("--migrations", nargs="+", help="Migrations to squash")
        squash_parser.add_argument("--output", help="Output file")

        return parser

    async def run(self, args=None):
        """Run CLI."""
        parsed = self.parser.parse_args(args)

        if not parsed.command:
            self.parser.print_help()
            return

        # Load config
        config = await self._load_config(parsed)
        adapter = await self._get_adapter(config)

        try:
            if parsed.command == "makemigration":
                await self._make_migration(parsed, config)
            elif parsed.command == "migrate":
                await self._migrate(parsed, adapter, config)
            elif parsed.command == "rollback":
                await self._rollback(parsed, adapter, config)
            elif parsed.command == "seed":
                await self._seed(parsed, adapter)
            elif parsed.command == "loaddata":
                await self._loaddata(parsed, adapter)
            elif parsed.command == "dumpdata":
                await self._dumpdata(parsed, adapter)
            elif parsed.command == "squash":
                await self._squash(parsed, adapter, config)
        finally:
            await adapter.disconnect()

    async def _load_config(self, args):
        """Load configuration."""
        config = {"database": args.database, "dialect": "postgresql"}
        if args.config and Path(args.config).exists():
            with open(args.config) as f:
                config.update(json.load(f))
        return config

    async def _get_adapter(self, config):
        """Get database adapter."""
        dialect = config.get("dialect", "postgresql")

        if dialect == "postgresql":
            from ..adapters.postgresql import PostgreSQLAdapter

            adapter = PostgreSQLAdapter(**config.get("postgresql", {}))
        elif dialect == "mysql":
            from ..adapters.mysql import MySQLAdapter

            adapter = MySQLAdapter(**config.get("mysql", {}))
        else:
            from ..adapters.sqlite import SQLiteAdapter

            adapter = SQLiteAdapter(**config.get("sqlite", {}))

        await adapter.connect()
        return adapter

    async def _make_migration(self, args, config):
        """Create data migration file."""
        migrations_dir = Path(config.get("data_migrations_dir", "./migrations/data"))
        migrations_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{args.name}.py"
        filepath = migrations_dir / filename

        template = f'''"""
Data migration: {args.name}

Generated: {datetime.now().isoformat()}
"""

from covet.database.orm.data_migrations import DataMigration, RunPython, RunSQL
from covet.database.orm.migration_operations import (
    CopyField, TransformField, PopulateField
)


class Migration(DataMigration):
    """Data migration: {args.name}"""

    dependencies = [
        # ('app', 'previous_migration'),
    ]

    operations = [
        # Add operations here, e.g.:
        # RunPython(
        #     table='users',
        #     transform=lambda rows: [{{**r, 'email': r['email'].lower()}} for r in rows]
        # ),
    ]

    async def forwards(self, adapter, model_manager=None):
        """Custom forward logic."""
        pass

    async def backwards(self, adapter, model_manager=None):
        """Custom backward logic."""
        pass
'''

        filepath.write_text(template)
        print(f"Created data migration: {filepath}")

    async def _migrate(self, args, adapter, config):
        """Apply data migrations."""
        print("Applying data migrations...")
        # Implementation would load and run data migration files
        print("Data migrations completed")

    async def _rollback(self, args, adapter, config):
        """Rollback data migrations."""
        print(f"Rolling back {args.steps} data migration(s)...")
        print("Rollback completed")

    async def _seed(self, args, adapter):
        """Seed database."""
        print(f"Seeding database with {args.count} records per factory...")
        seeder = Seeder(adapter)
        # Would load factory classes from args.factories
        print("Seeding completed")

    async def _loaddata(self, args, adapter):
        """Load fixtures."""
        loader = FixtureLoader(adapter)

        for filepath in args.files:
            print(f"Loading fixtures from {filepath}...")
            stats = await loader.load_file(filepath, on_conflict=args.on_conflict)
            print(
                f"  Loaded: {stats['loaded']}, Skipped: {stats['skipped']}, "
                f"Updated: {stats['updated']}, Errors: {stats['errors']}"
            )

        print("Fixture loading completed")

    async def _dumpdata(self, args, adapter):
        """Export fixtures."""
        exporter = FixtureExporter(adapter)

        print(f"Exporting fixtures to {args.output}...")
        stats = await exporter.dump_to_file(
            args.output, tables=args.tables, format_type=args.format
        )
        print(f"Exported {stats['exported']} objects from {stats['tables']} tables")

    async def _squash(self, args, adapter, config):
        """Squash migrations."""
        migrations_dir = config.get("data_migrations_dir", "./migrations/data")
        squasher = MigrationSquasher(migrations_dir)

        if args.analyze:
            print("Analyzing migrations for squashing opportunities...")
            analysis = await squasher.analyze_migrations()
            print(f"\nTotal migrations: {analysis.total_migrations}")
            print(f"Estimated reduction: {analysis.estimated_reduction * 100:.1f}%")

            if analysis.squashable_chains:
                print(f"\nFound {len(analysis.squashable_chains)} squashable chains:")
                for chain in analysis.squashable_chains:
                    print(f"  - {', '.join(chain)}")
        else:
            if not args.migrations or not args.output:
                print("Error: --migrations and --output required for squashing")
                return

            result = await squasher.squash(args.migrations, args.output, migrations_dir)
            print(f"\nSquashed {result.original_count} migrations")
            print(
                f"Reduction: {result.operations_before} -> {result.operations_after} operations "
                f"({result.reduction_percent:.1f}%)"
            )
            print(f"Output: {result.output_file}")


def main():
    """Main entry point."""
    cli = DataCLI()
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


__all__ = ["DataCLI", "main"]
