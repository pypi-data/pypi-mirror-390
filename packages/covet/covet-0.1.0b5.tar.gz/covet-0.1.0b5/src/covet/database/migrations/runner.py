"""
Migration Runner

Executes migrations with transaction support, tracks migration history,
and provides rollback capabilities. This is the execution engine that
actually applies migrations to your database.

The runner is responsible for:
- Maintaining migration history table
- Executing migrations in transactions
- Rolling back on errors
- Preventing duplicate execution
- Dependency resolution

Example:
    from covet.database.migrations.runner import MigrationRunner
    from covet.database.adapters.postgresql import PostgreSQLAdapter

    adapter = PostgreSQLAdapter(host='localhost', database='mydb')
    await adapter.connect()

    runner = MigrationRunner(adapter, dialect='postgresql')

    # Apply all pending migrations
    await runner.migrate(migrations_dir='./migrations')

    # Rollback last migration
    await runner.rollback()

    # Show migration status
    status = await runner.show_migrations(migrations_dir='./migrations')
"""

import importlib.util
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..security.sql_validator import (
    DatabaseDialect,
    quote_identifier,
    validate_table_name,
)
from .security import (
    PathValidator,
    SafeMigrationValidator,
    SecurityError,
    create_safe_namespace,
)

logger = logging.getLogger(__name__)


class Migration:
    """
    Base class for migration files.

    All generated migration files inherit from this class.
    Provides the interface for applying and rolling back migrations.
    """

    dependencies: List[str] = []
    operations: List[Dict[str, Any]] = []
    forward_sql: List[str] = []
    backward_sql: List[str] = []

    async def apply(self, adapter):
        """
        Apply migration (execute forward SQL).

        Args:
            adapter: Database adapter

        Example:
            await migration.apply(adapter)
        """
        for sql in self.forward_sql:
            if sql and not sql.strip().startswith("--"):
                logger.debug(f"Executing: {sql[:100]}...")
                await adapter.execute(sql)

    async def rollback(self, adapter):
        """
        Rollback migration (execute backward SQL).

        Args:
            adapter: Database adapter

        Example:
            await migration.rollback(adapter)
        """
        for sql in self.backward_sql:
            if sql and not sql.strip().startswith("--"):
                logger.debug(f"Executing rollback: {sql[:100]}...")
                await adapter.execute(sql)


class MigrationHistory:
    """
    Tracks applied migrations in the database.

    Uses a special table (_covet_migrations) to record:
    - Migration name
    - Applied timestamp
    - App name
    - Success/failure status

    This is how we know what migrations have already been applied.
    """

    def __init__(self, adapter, table_name: str = "_covet_migrations"):
        """
        Initialize migration history.

        Args:
            adapter: Database adapter
            table_name: Name of history table (default: _covet_migrations)

        Security:
            - Validates table name to prevent SQL injection
        """
        self.adapter = adapter

        # Detect dialect for security validation
        adapter_type = type(adapter).__name__
        if "PostgreSQL" in adapter_type:
            self.dialect = DatabaseDialect.POSTGRESQL
        elif "MySQL" in adapter_type:
            self.dialect = DatabaseDialect.MYSQL
        elif "SQLite" in adapter_type:
            self.dialect = DatabaseDialect.SQLITE
        else:
            self.dialect = DatabaseDialect.GENERIC

        # Validate table name (CVE-SPRINT2-002 fix)
        self.table_name = validate_table_name(table_name, self.dialect)
        self.quoted_table_name = quote_identifier(self.table_name, self.dialect)

    async def ensure_table_exists(self):
        """
        Create migration history table if it doesn't exist.

        This table stores the record of all applied migrations.
        """
        # Check if table exists
        exists = await self.adapter.table_exists(self.table_name)

        if not exists:
            logger.info(f"Creating migration history table: {self.table_name}")

            # Detect dialect
            adapter_type = type(self.adapter).__name__

            # Use quoted table name for security (CVE-SPRINT2-002 fix)
            if "PostgreSQL" in adapter_type:
                sql = f"""
                    CREATE TABLE {self.quoted_table_name} (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        app VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """
            elif "MySQL" in adapter_type:
                sql = f"""
                    CREATE TABLE {self.quoted_table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        app VARCHAR(255) NOT NULL,
                        applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            elif "SQLite" in adapter_type:
                sql = f"""
                    CREATE TABLE {self.quoted_table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        app TEXT NOT NULL,
                        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """
            else:
                # Generic SQL
                sql = f"""
                    CREATE TABLE {self.quoted_table_name} (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        app VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP NOT NULL
                    )
                """

            await self.adapter.execute(sql)
            logger.info("Migration history table created")

    async def is_applied(self, migration_name: str) -> bool:
        """
        Check if a migration has been applied.

        Args:
            migration_name: Migration name

        Returns:
            True if migration has been applied
        """
        await self.ensure_table_exists()

        # Detect parameter style
        adapter_type = type(self.adapter).__name__

        # Use quoted table name for security (CVE-SPRINT2-002 fix)
        if "PostgreSQL" in adapter_type:
            query = f"SELECT COUNT(*) FROM {self.quoted_table_name} WHERE name = $1"  # nosec B608 - table_name validated
        elif "MySQL" in adapter_type:
            query = f"SELECT COUNT(*) FROM {self.quoted_table_name} WHERE name = %s"  # nosec B608 - table_name validated
        elif "SQLite" in adapter_type:
            query = f"SELECT COUNT(*) FROM {self.quoted_table_name} WHERE name = ?"  # nosec B608 - table_name validated
        else:
            query = f"SELECT COUNT(*) FROM {self.quoted_table_name} WHERE name = ?"  # nosec B608 - table_name validated

        count = await self.adapter.fetch_value(query, [migration_name])
        return count > 0

    async def record_applied(self, migration_name: str, app_name: str = "default"):
        """
        Record that a migration has been applied.

        Args:
            migration_name: Migration name
            app_name: App name
        """
        await self.ensure_table_exists()

        # Detect parameter style
        adapter_type = type(self.adapter).__name__

        # Use quoted table name for security (CVE-SPRINT2-002 fix)
        if "PostgreSQL" in adapter_type:
            query = f"""  # nosec B608 - table_name validated in config
                INSERT INTO {self.quoted_table_name} (name, app, applied_at)
                VALUES ($1, $2, $3)
            """
        elif "MySQL" in adapter_type:
            query = f"""  # nosec B608 - table_name validated in config
                INSERT INTO {self.quoted_table_name} (name, app, applied_at)
                VALUES (%s, %s, %s)
            """
        elif "SQLite" in adapter_type:
            query = f"""  # nosec B608 - table_name validated in config
                INSERT INTO {self.quoted_table_name} (name, app, applied_at)
                VALUES (?, ?, ?)
            """
        else:
            query = f"""  # nosec B608 - table_name validated in config
                INSERT INTO {self.quoted_table_name} (name, app, applied_at)
                VALUES (?, ?, ?)
            """

        now = datetime.now().isoformat()
        await self.adapter.execute(query, [migration_name, app_name, now])

        logger.info(f"Recorded migration: {migration_name}")

    async def record_rolled_back(self, migration_name: str):
        """
        Remove migration from history (after rollback).

        Args:
            migration_name: Migration name
        """
        await self.ensure_table_exists()

        # Detect parameter style
        adapter_type = type(self.adapter).__name__

        # Use quoted table name for security (CVE-SPRINT2-002 fix)
        if "PostgreSQL" in adapter_type:
            query = f"DELETE FROM {self.quoted_table_name} WHERE name = $1"  # nosec B608 - table_name validated
        elif "MySQL" in adapter_type:
            query = f"DELETE FROM {self.quoted_table_name} WHERE name = %s"  # nosec B608 - table_name validated
        elif "SQLite" in adapter_type:
            query = f"DELETE FROM {self.quoted_table_name} WHERE name = ?"  # nosec B608 - table_name validated
        else:
            query = f"DELETE FROM {self.quoted_table_name} WHERE name = ?"  # nosec B608 - table_name validated

        await self.adapter.execute(query, [migration_name])

        logger.info(f"Removed migration from history: {migration_name}")

    async def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """
        Get list of all applied migrations.

        Returns:
            List of migration records with name, app, applied_at
        """
        await self.ensure_table_exists()

        # Use quoted table name for security (CVE-SPRINT2-002 fix)
        query = f"""  # nosec B608 - table_name validated in config
            SELECT name, app, applied_at
            FROM {self.quoted_table_name}
            ORDER BY applied_at
        """

        rows = await self.adapter.fetch_all(query)
        return rows

    async def get_last_migration(self) -> Optional[str]:
        """
        Get the name of the last applied migration.

        Returns:
            Migration name or None if no migrations applied
        """
        await self.ensure_table_exists()

        # Use quoted table name for security (CVE-SPRINT2-002 fix)
        query = f"""  # nosec B608 - table_name validated in config
            SELECT name
            FROM {self.quoted_table_name}
            ORDER BY applied_at DESC
            LIMIT 1
        """

        row = await self.adapter.fetch_one(query)
        return row["name"] if row else None


class MigrationRunner:
    """
    Executes database migrations with transaction support.

    This is the core component that:
    1. Loads migration files from disk
    2. Checks which have been applied
    3. Executes pending migrations in order
    4. Tracks migration history
    5. Handles rollbacks

    The runner ensures:
    - Migrations are executed in dependency order
    - Each migration runs in a transaction (atomic)
    - Failed migrations don't corrupt the database
    - Migration history is accurate

    Example:
        runner = MigrationRunner(adapter, dialect='postgresql')

        # Apply all pending migrations
        applied = await runner.migrate('./migrations')
        print(f"Applied {len(applied)} migrations")

        # Rollback last migration
        await runner.rollback()

        # Show status
        status = await runner.show_migrations('./migrations')
        for name, is_applied in status.items():
            print(f"{name}: {'✓' if is_applied else '✗'}")
    """

    def __init__(
        self,
        adapter,
        dialect: str = "postgresql",
        history_table: str = "_covet_migrations",
        migrations_directory: Optional[str] = None,
    ):
        """
        Initialize migration runner.

        Args:
            adapter: Database adapter
            dialect: Database dialect
            history_table: Name of migration history table
            migrations_directory: Directory containing migrations (for security validation)
        """
        self.adapter = adapter
        self.dialect = dialect.lower()
        self.history = MigrationHistory(adapter, history_table)
        self.migrations_directory = migrations_directory

        # Initialize security validators
        self.migration_validator = SafeMigrationValidator()
        self.path_validator = None  # Initialized when migrations_dir is known

    async def migrate(
        self, migrations_dir: str, target: Optional[str] = None, fake: bool = False
    ) -> List[str]:
        """
        Apply pending migrations.

        Args:
            migrations_dir: Directory containing migration files
            target: Target migration name (apply up to this migration)
            fake: Mark migrations as applied without executing SQL

        Returns:
            List of applied migration names

        Example:
            # Apply all pending migrations
            applied = await runner.migrate('./migrations')

            # Apply up to specific migration
            applied = await runner.migrate('./migrations', target='0003_add_indexes')

            # Fake migration (mark as applied without executing)
            applied = await runner.migrate('./migrations', fake=True)
        """
        # Ensure history table exists
        await self.history.ensure_table_exists()

        # Load all migrations
        migrations = await self._load_migrations(migrations_dir)

        # Get applied migrations
        applied_migrations = await self.history.get_applied_migrations()
        applied_names = {m["name"] for m in applied_migrations}

        # Filter pending migrations
        pending = [(name, mig) for name, mig in migrations if name not in applied_names]

        if not pending:
            logger.info("No pending migrations")
            return []

        # If target specified, only apply up to target
        if target:
            target_index = None
            for i, (name, _) in enumerate(pending):
                if name == target:
                    target_index = i
                    break

            if target_index is None:
                raise ValueError(f"Target migration not found: {target}")

            pending = pending[: target_index + 1]

        logger.info(f"Found {len(pending)} pending migrations")

        # Apply migrations
        applied = []
        for migration_name, migration_instance in pending:
            try:
                logger.info(f"Applying migration: {migration_name}")

                if not fake:
                    # Execute in transaction
                    async with self.adapter.transaction():
                        await migration_instance.apply(self.adapter)

                # Record in history
                await self.history.record_applied(migration_name)

                applied.append(migration_name)
                logger.info(f"✓ Applied: {migration_name}")

            except Exception as e:
                logger.error(f"✗ Failed to apply {migration_name}: {e}")
                logger.error(f"Migration stopped at: {migration_name}")
                raise

        logger.info(f"Successfully applied {len(applied)} migrations")
        return applied

    async def rollback(self, steps: int = 1, fake: bool = False) -> List[str]:
        """
        Rollback migrations.

        Args:
            steps: Number of migrations to rollback (default: 1)
            fake: Mark as rolled back without executing SQL

        Returns:
            List of rolled back migration names

        Example:
            # Rollback last migration
            await runner.rollback()

            # Rollback last 3 migrations
            await runner.rollback(steps=3)

            # Fake rollback (mark as rolled back without executing)
            await runner.rollback(fake=True)
        """
        # Get applied migrations
        applied_migrations = await self.history.get_applied_migrations()

        if not applied_migrations:
            logger.info("No migrations to rollback")
            return []

        # Get last N migrations to rollback
        to_rollback = applied_migrations[-steps:]
        to_rollback.reverse()  # Rollback in reverse order

        logger.info(f"Rolling back {len(to_rollback)} migrations")

        rolled_back = []
        for migration_record in to_rollback:
            migration_name = migration_record["name"]

            try:
                logger.info(f"Rolling back migration: {migration_name}")

                # Load migration instance
                migration_instance = await self._load_migration_by_name(
                    migration_name,
                    # We need to search for the file
                    migration_name,
                )

                if not migration_instance:
                    logger.warning(
                        f"Cannot find migration file: {migration_name}. "
                        f"Removing from history anyway."
                    )
                elif not fake:
                    # Execute rollback in transaction
                    async with self.adapter.transaction():
                        await migration_instance.rollback(self.adapter)

                # Remove from history
                await self.history.record_rolled_back(migration_name)

                rolled_back.append(migration_name)
                logger.info(f"✓ Rolled back: {migration_name}")

            except Exception as e:
                logger.error(f"✗ Failed to rollback {migration_name}: {e}")
                logger.error(f"Rollback stopped at: {migration_name}")
                raise

        logger.info(f"Successfully rolled back {len(rolled_back)} migrations")
        return rolled_back

    async def show_migrations(self, migrations_dir: str) -> Dict[str, bool]:
        """
        Show migration status (applied vs pending).

        Args:
            migrations_dir: Directory containing migration files

        Returns:
            Dictionary mapping migration names to applied status

        Example:
            status = await runner.show_migrations('./migrations')
            for name, is_applied in status.items():
                status_mark = '✓' if is_applied else '✗'
                print(f"[{status_mark}] {name}")
        """
        # Load all migrations
        migrations = await self._load_migrations(migrations_dir)

        # Get applied migrations
        applied_migrations = await self.history.get_applied_migrations()
        applied_names = {m["name"] for m in applied_migrations}

        # Build status map
        status = {}
        for migration_name, _ in migrations:
            status[migration_name] = migration_name in applied_names

        return status

    async def _load_migrations(self, migrations_dir: str) -> List[Tuple[str, Migration]]:
        """
        Load all migration files from directory with security validation.

        Args:
            migrations_dir: Directory containing migration files

        Returns:
            List of (migration_name, migration_instance) tuples sorted by name

        Security:
            - Initializes path validator for directory
            - Validates each migration file before loading
            - Skips files that fail security validation
        """
        if not os.path.exists(migrations_dir):
            logger.warning(f"Migrations directory does not exist: {migrations_dir}")
            return []

        # Initialize path validator for this directory
        self.path_validator = PathValidator(migrations_dir)
        self.migrations_directory = migrations_dir

        migrations = []

        # Find all Python files
        for filename in sorted(os.listdir(migrations_dir)):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            migration_name = filename[:-3]  # Remove .py extension
            filepath = os.path.join(migrations_dir, filename)

            try:
                migration_instance = self._load_migration_file(filepath)
                migrations.append((migration_name, migration_instance))
            except SecurityError as e:
                logger.error(
                    f"Security validation failed for {filename}: {e}. "
                    f"Migration will be skipped for security reasons."
                )
                # Do not load migrations that fail security validation
                raise
            except Exception as e:
                logger.error(f"Failed to load migration {filename}: {e}")
                raise

        return migrations

    async def _load_migration_by_name(
        self, migration_name: str, search_path: str
    ) -> Optional[Migration]:
        """
        Load a specific migration by name.

        Args:
            migration_name: Migration name (without .py extension)
            search_path: Path to search for migration file

        Returns:
            Migration instance or None
        """
        # Try to find the file
        if os.path.isdir(search_path):
            filepath = os.path.join(search_path, f"{migration_name}.py")
        else:
            filepath = search_path

        if not os.path.exists(filepath):
            return None

        return self._load_migration_file(filepath)

    def _load_migration_file(self, filepath: str) -> Migration:
        """
        Load migration from Python file with security validation.

        Security measures:
        1. Path traversal validation (CVE-SPRINT2-003)
        2. AST-based code validation (CVE-SPRINT2-001)
        3. Restricted namespace execution

        Args:
            filepath: Full path to migration file

        Returns:
            Migration instance

        Raises:
            SecurityError: If security validation fails
            ValueError: If migration file is invalid

        Security:
            - Validates path is within migrations directory
            - Checks for dangerous code patterns using AST
            - Executes in restricted namespace
            - Prevents arbitrary code execution
        """
        # Step 1: Validate path to prevent path traversal (CVE-SPRINT2-003)
        if self.path_validator:
            try:
                validated_path = self.path_validator.validate_path(filepath)
                filepath = str(validated_path)
            except SecurityError as e:
                logger.error(f"Path validation failed: {e}")
                raise

        # Step 2: Validate migration code using AST (CVE-SPRINT2-001)
        try:
            self.migration_validator.validate_migration_file(filepath)
        except SecurityError as e:
            logger.error(f"Migration security validation failed: {e}")
            raise

        # Step 3: Load migration using importlib (safer than exec)
        try:
            import importlib.util
            import sys

            # Generate unique module name to avoid collisions
            module_name = f"_migration_{hash(filepath)}"

            # Load module using importlib (CVE-COVET-2025-001 fix)
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if not spec or not spec.loader:
                raise ValueError(f"Cannot create module spec for {filepath}")

            module = importlib.util.module_from_spec(spec)

            # Restrict module namespace (defense in depth)
            # Remove dangerous builtins before execution
            safe_builtins = (
                {
                    k: v
                    for k, v in __builtins__.items()
                    if k not in ["eval", "exec", "compile", "__import__", "open", "input"]
                }
                if isinstance(__builtins__, dict)
                else {}
            )

            # Add Migration base class to module namespace
            module.Migration = Migration

            # Execute module with restricted builtins
            original_builtins = module.__dict__.get("__builtins__")
            try:
                module.__dict__["__builtins__"] = safe_builtins
                spec.loader.exec_module(module)
            finally:
                # Restore original builtins
                if original_builtins is not None:
                    module.__dict__["__builtins__"] = original_builtins

            # Find Migration class in module
            migration_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, Migration) and obj is not Migration:
                    migration_class = obj
                    break

            if not migration_class:
                raise ValueError(f"No Migration class found in {filepath}")

            # Instantiate migration
            logger.debug(f"Successfully loaded migration: {filepath}")
            return migration_class()

        except SecurityError:
            # Re-raise security errors
            raise
        except Exception as e:
            logger.error(f"Failed to load migration {filepath}: {e}")
            raise ValueError(f"Invalid migration file {filepath}: {e}")


__all__ = [
    "MigrationRunner",
    "Migration",
    "MigrationHistory",
]
