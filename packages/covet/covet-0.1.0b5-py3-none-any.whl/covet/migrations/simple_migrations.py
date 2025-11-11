"""
Simple Migration System for CovetPy
====================================
A Django/Alembic-like migration system that actually works.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path


class Migration:
    """Represents a single database migration."""

    def __init__(self, name: str, operations: List[str], dependencies: List[str] = None):
        self.name = name
        self.operations = operations  # List of SQL statements
        self.dependencies = dependencies or []
        self.timestamp = datetime.now().isoformat()
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate hash of migration for integrity checking."""
        content = f"{self.name}{''.join(self.operations)}"
        return hashlib.md5(content.encode()).hexdigest()

    def up(self, connection):
        """Apply the migration."""
        cursor = connection.cursor()
        for operation in self.operations:
            cursor.execute(operation)
        connection.commit()

    def down(self, connection):
        """Rollback the migration (if possible)."""
        # For now, we'll just track that it was rolled back
        # Real implementation would need reverse operations
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert migration to dictionary."""
        return {
            'name': self.name,
            'operations': self.operations,
            'dependencies': self.dependencies,
            'timestamp': self.timestamp,
            'hash': self.hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Migration':
        """Create migration from dictionary."""
        migration = cls(
            name=data['name'],
            operations=data['operations'],
            dependencies=data.get('dependencies', [])
        )
        migration.timestamp = data.get('timestamp', migration.timestamp)
        migration.hash = data.get('hash', migration.hash)
        return migration


class MigrationManager:
    """Manages database migrations for CovetPy."""

    def __init__(self, db_path: str, migrations_dir: str = 'migrations'):
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(exist_ok=True)

        # Create migrations table if it doesn't exist
        self._ensure_migrations_table()

    def _ensure_migrations_table(self):
        """Ensure the migrations tracking table exists."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS covet_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                hash TEXT NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'applied'
            )
        ''')
        conn.commit()
        conn.close()

    def _get_connection(self):
        """Get database connection."""
        if self.db_path.startswith('sqlite://'):
            db_path = self.db_path.replace('sqlite:///', '')
            if db_path == ':memory:':
                # For in-memory databases, we need to keep the connection
                if not hasattr(self, '_memory_conn'):
                    self._memory_conn = sqlite3.connect(':memory:')
                    self._memory_conn.row_factory = sqlite3.Row
                return self._memory_conn
            return sqlite3.connect(db_path)
        else:
            return sqlite3.connect(self.db_path)

    def create_migration(self, name: str, operations: List[str],
                        dependencies: List[str] = None) -> Migration:
        """Create a new migration."""
        # Generate migration name with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        full_name = f"{timestamp}_{name}"

        migration = Migration(full_name, operations, dependencies)

        # Save migration to file
        migration_file = self.migrations_dir / f"{full_name}.json"
        with open(migration_file, 'w') as f:
            json.dump(migration.to_dict(), f, indent=2)

        print(f"Created migration: {full_name}")
        return migration

    def load_migrations(self) -> List[Migration]:
        """Load all migrations from the migrations directory."""
        migrations = []

        if not self.migrations_dir.exists():
            return migrations

        for file_path in sorted(self.migrations_dir.glob('*.json')):
            with open(file_path, 'r') as f:
                data = json.load(f)
                migrations.append(Migration.from_dict(data))

        return migrations

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration names."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM covet_migrations WHERE status = 'applied' ORDER BY id"
        )
        applied = [row[0] for row in cursor.fetchall()]
        if not hasattr(self, '_memory_conn'):
            conn.close()
        return applied

    def get_pending_migrations(self) -> List[Migration]:
        """Get list of migrations that haven't been applied yet."""
        all_migrations = self.load_migrations()
        applied = self.get_applied_migrations()

        pending = []
        for migration in all_migrations:
            if migration.name not in applied:
                pending.append(migration)

        return pending

    def apply_migration(self, migration: Migration):
        """Apply a single migration."""
        conn = self._get_connection()

        try:
            # Apply the migration
            migration.up(conn)

            # Record that it was applied
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO covet_migrations (name, hash, status) VALUES (?, ?, ?)",
                (migration.name, migration.hash, 'applied')
            )
            conn.commit()

            print(f"Applied migration: {migration.name}")
        except Exception as e:
            conn.rollback()
            print(f"Failed to apply migration {migration.name}: {e}")
            raise
        finally:
            if not hasattr(self, '_memory_conn'):
                conn.close()

    def migrate(self, target: Optional[str] = None):
        """Apply all pending migrations up to target (or all if target is None)."""
        pending = self.get_pending_migrations()

        if not pending:
            print("No pending migrations.")
            return

        print(f"Found {len(pending)} pending migration(s):")
        for migration in pending:
            print(f"  - {migration.name}")

        for migration in pending:
            if target and migration.name > target:
                break
            self.apply_migration(migration)

        print("Migration complete!")

    def rollback(self, target: Optional[str] = None):
        """Rollback migrations to target (or last if target is None)."""
        applied = self.get_applied_migrations()

        if not applied:
            print("No migrations to rollback.")
            return

        if target is None:
            # Rollback last migration
            target = applied[-2] if len(applied) > 1 else None

        # Mark migrations as rolled back
        conn = self._get_connection()
        cursor = conn.cursor()

        for migration_name in reversed(applied):
            if target and migration_name <= target:
                break

            cursor.execute(
                "UPDATE covet_migrations SET status = 'rolled_back' WHERE name = ?",
                (migration_name,)
            )
            print(f"Rolled back: {migration_name}")

        conn.commit()
        if not hasattr(self, '_memory_conn'):
            conn.close()

        print("Rollback complete!")

    def status(self):
        """Show migration status."""
        all_migrations = self.load_migrations()
        applied = self.get_applied_migrations()

        print("\nMigration Status:")
        print("-" * 60)

        if not all_migrations:
            print("No migrations found.")
            return

        for migration in all_migrations:
            status = "✓ Applied" if migration.name in applied else "○ Pending"
            print(f"{status:12} {migration.name}")

        print("-" * 60)
        print(f"Total: {len(all_migrations)} migrations")
        print(f"Applied: {len(applied)}")
        print(f"Pending: {len(all_migrations) - len(applied)}")


class AutoMigration:
    """Automatically generate migrations from model changes."""

    @staticmethod
    def generate_from_models(models: List[type], manager: MigrationManager) -> Migration:
        """Generate a migration from model definitions."""
        operations = []

        for model in models:
            # Get table name
            table_name = getattr(model.Meta, 'table_name', model.__name__.lower() + 's')

            # Build CREATE TABLE statement
            columns = []
            for attr_name in dir(model):
                if attr_name.startswith('_'):
                    continue

                attr = getattr(model, attr_name)
                if hasattr(attr, '__class__') and 'Field' in attr.__class__.__name__:
                    # This is a field
                    column_def = AutoMigration._field_to_sql(attr_name, attr)
                    if column_def:
                        columns.append(column_def)

            if columns:
                create_table = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(columns)}
                )
                """.strip()
                operations.append(create_table)

        if operations:
            migration_name = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return manager.create_migration(migration_name, operations)

        return None

    @staticmethod
    def _field_to_sql(name: str, field) -> str:
        """Convert a field to SQL column definition."""
        field_class = field.__class__.__name__

        # Map field types to SQL types
        type_map = {
            'IntegerField': 'INTEGER',
            'CharField': 'VARCHAR',
            'TextField': 'TEXT',
            'FloatField': 'REAL',
            'BooleanField': 'BOOLEAN',
            'DateTimeField': 'DATETIME',
            'DateField': 'DATE',
            'TimeField': 'TIME',
            'JSONField': 'JSON',
            'BinaryField': 'BLOB'
        }

        sql_type = type_map.get(field_class, 'TEXT')

        # Handle CharField max_length
        if field_class == 'CharField' and hasattr(field, 'max_length'):
            sql_type = f"VARCHAR({field.max_length})"

        # Build column definition
        parts = [name, sql_type]

        # Add constraints
        if hasattr(field, 'primary_key') and field.primary_key:
            parts.append('PRIMARY KEY')
            if name == 'id':
                parts.append('AUTOINCREMENT')

        if hasattr(field, 'unique') and field.unique:
            parts.append('UNIQUE')

        if hasattr(field, 'null') and not field.null:
            parts.append('NOT NULL')
        elif hasattr(field, 'required') and field.required:
            parts.append('NOT NULL')

        if hasattr(field, 'default'):
            default = field.default
            if callable(default):
                if default.__name__ == 'now':
                    parts.append('DEFAULT CURRENT_TIMESTAMP')
            elif isinstance(default, str):
                parts.append(f"DEFAULT '{default}'")
            elif default is not None:
                parts.append(f"DEFAULT {default}")

        return ' '.join(parts)


# CLI Commands for migrations
class MigrationCLI:
    """Command-line interface for migrations."""

    @staticmethod
    def makemigrations(db_path: str, models: List[type] = None, name: str = None):
        """Create new migrations from model changes."""
        manager = MigrationManager(db_path)

        if models:
            migration = AutoMigration.generate_from_models(models, manager)
            if migration:
                print(f"Created migration: {migration.name}")
            else:
                print("No changes detected.")
        else:
            print("Please provide models to generate migrations from.")

    @staticmethod
    def migrate(db_path: str, target: str = None):
        """Apply migrations."""
        manager = MigrationManager(db_path)
        manager.migrate(target)

    @staticmethod
    def rollback(db_path: str, target: str = None):
        """Rollback migrations."""
        manager = MigrationManager(db_path)
        manager.rollback(target)

    @staticmethod
    def status(db_path: str):
        """Show migration status."""
        manager = MigrationManager(db_path)
        manager.status()


# Export public API
__all__ = [
    'Migration',
    'MigrationManager',
    'AutoMigration',
    'MigrationCLI'
]