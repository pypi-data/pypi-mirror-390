"""
Database Migration System

Production-ready schema migration system with dependency tracking,
rollback support, and multi-database compatibility.
"""

import datetime
import hashlib
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Type

from .connection import DatabaseConnection, get_connection_pool
from .exceptions import MigrationError, ORMError
from .fields import Field

logger = logging.getLogger(__name__)


@dataclass
class MigrationState:
    """Migration execution state."""

    name: str
    app: str
    applied_at: datetime.datetime
    checksum: str


class MigrationOperation(ABC):
    """Base class for migration operations."""

    @abstractmethod
    def execute(self, connection: DatabaseConnection, engine: str):
        """Execute the operation."""

    @abstractmethod
    def rollback(self, connection: DatabaseConnection, engine: str):
        """Rollback the operation."""

    @abstractmethod
    def describe(self) -> str:
        """Describe the operation."""


class CreateTable(MigrationOperation):
    """Create table operation."""

    def __init__(
        self,
        table_name: str,
        fields: Dict[str, Field],
        indexes: List[str] = None,
        constraints: List[str] = None,
    ):
        self.table_name = table_name
        self.fields = fields
        self.indexes = indexes or []
        self.constraints = constraints or []

    def execute(self, connection: DatabaseConnection, engine: str):
        """Create the table."""
        # Build CREATE TABLE statement
        field_definitions = []

        for field_name, field_obj in self.fields.items():
            field_sql = f"{field_name} {field_obj.get_sql_type(engine)}"

            if field_obj.primary_key:
                field_sql += " PRIMARY KEY"
            if not field_obj.null:
                field_sql += " NOT NULL"
            if field_obj.unique:
                field_sql += " UNIQUE"
            if field_obj.default is not None:
                if isinstance(field_obj.default, str):
                    field_sql += f" DEFAULT '{field_obj.default}'"
                else:
                    field_sql += f" DEFAULT {field_obj.default}"

            field_definitions.append(field_sql)

        # Add constraints
        for constraint in self.constraints:
            field_definitions.append(constraint)

        fields_sql = ",\n    ".join(field_definitions)
        sql = f"CREATE TABLE {self.table_name} (\n    {fields_sql}\n)"

        connection.execute(sql)

        # Create indexes
        for index in self.indexes:
            connection.execute(index)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Drop the table."""
        connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")

    def describe(self) -> str:
        return f"Create table '{self.table_name}'"


class DropTable(MigrationOperation):
    """Drop table operation."""

    def __init__(self, table_name: str):
        self.table_name = table_name

    def execute(self, connection: DatabaseConnection, engine: str):
        """Drop the table."""
        connection.execute(f"DROP TABLE {self.table_name}")

    def rollback(self, connection: DatabaseConnection, engine: str):
        """This operation cannot be automatically rolled back."""
        raise MigrationError(f"Cannot rollback DropTable operation for {self.table_name}")

    def describe(self) -> str:
        return f"Drop table '{self.table_name}'"


class AddColumn(MigrationOperation):
    """Add column operation."""

    def __init__(self, table_name: str, column_name: str, field: Field):
        self.table_name = table_name
        self.column_name = column_name
        self.field = field

    def execute(self, connection: DatabaseConnection, engine: str):
        """Add the column."""
        field_sql = f"{self.column_name} {self.field.get_sql_type(engine)}"

        if not self.field.null:
            field_sql += " NOT NULL"
        if self.field.unique:
            field_sql += " UNIQUE"
        if self.field.default is not None:
            if isinstance(self.field.default, str):
                field_sql += f" DEFAULT '{self.field.default}'"
            else:
                field_sql += f" DEFAULT {self.field.default}"

        sql = f"ALTER TABLE {self.table_name} ADD COLUMN {field_sql}"
        connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Drop the column."""
        if engine == "sqlite":
            raise MigrationError("SQLite does not support dropping columns")
        sql = f"ALTER TABLE {self.table_name} DROP COLUMN {self.column_name}"
        connection.execute(sql)

    def describe(self) -> str:
        return f"Add column '{self.column_name}' to table '{self.table_name}'"


class DropColumn(MigrationOperation):
    """Drop column operation."""

    def __init__(self, table_name: str, column_name: str):
        self.table_name = table_name
        self.column_name = column_name

    def execute(self, connection: DatabaseConnection, engine: str):
        """Drop the column."""
        if engine == "sqlite":
            raise MigrationError("SQLite does not support dropping columns")
        sql = f"ALTER TABLE {self.table_name} DROP COLUMN {self.column_name}"
        connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """This operation cannot be automatically rolled back."""
        raise MigrationError(
            f"Cannot rollback DropColumn operation for {self.table_name}.{self.column_name}"
        )

    def describe(self) -> str:
        return f"Drop column '{self.column_name}' from table '{self.table_name}'"


class AlterColumn(MigrationOperation):
    """Alter column operation."""

    def __init__(self, table_name: str, column_name: str, field: Field, old_field: Field = None):
        self.table_name = table_name
        self.column_name = column_name
        self.field = field
        self.old_field = old_field

    def execute(self, connection: DatabaseConnection, engine: str):
        """Alter the column."""
        if engine == "sqlite":
            raise MigrationError("SQLite has limited ALTER COLUMN support")

        field_sql = f"{self.column_name} {self.field.get_sql_type(engine)}"

        if not self.field.null:
            field_sql += " NOT NULL"
        if self.field.default is not None:
            if isinstance(self.field.default, str):
                field_sql += f" DEFAULT '{self.field.default}'"
            else:
                field_sql += f" DEFAULT {self.field.default}"

        if engine == "postgresql":
            # PostgreSQL requires separate statements for type and constraints
            type_sql = f"ALTER TABLE {self.table_name} ALTER COLUMN {self.column_name} TYPE {self.field.get_sql_type(engine)}"
            connection.execute(type_sql)

            if not self.field.null:
                null_sql = (
                    f"ALTER TABLE {self.table_name} ALTER COLUMN {self.column_name} SET NOT NULL"
                )
                connection.execute(null_sql)
        else:
            sql = f"ALTER TABLE {self.table_name} MODIFY COLUMN {field_sql}"
            connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Rollback to old field definition."""
        if not self.old_field:
            raise MigrationError("Cannot rollback AlterColumn without old field definition")
        # Create reverse operation
        reverse_op = AlterColumn(self.table_name, self.column_name, self.old_field, self.field)
        reverse_op.execute(connection, engine)

    def describe(self) -> str:
        return f"Alter column '{self.column_name}' in table '{self.table_name}'"


class RenameTable(MigrationOperation):
    """Rename table operation."""

    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name

    def execute(self, connection: DatabaseConnection, engine: str):
        """Rename the table."""
        if engine == "mysql":
            sql = f"RENAME TABLE {self.old_name} TO {self.new_name}"
        else:
            sql = f"ALTER TABLE {self.old_name} RENAME TO {self.new_name}"
        connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Rename back to old name."""
        if engine == "mysql":
            sql = f"RENAME TABLE {self.new_name} TO {self.old_name}"
        else:
            sql = f"ALTER TABLE {self.new_name} RENAME TO {self.old_name}"
        connection.execute(sql)

    def describe(self) -> str:
        return f"Rename table '{self.old_name}' to '{self.new_name}'"


class RenameColumn(MigrationOperation):
    """Rename column operation."""

    def __init__(self, table_name: str, old_name: str, new_name: str):
        self.table_name = table_name
        self.old_name = old_name
        self.new_name = new_name

    def execute(self, connection: DatabaseConnection, engine: str):
        """Rename the column."""
        if engine == "sqlite":
            raise MigrationError("SQLite does not support renaming columns")
        elif engine == "mysql":
            # MySQL requires the full column definition
            raise MigrationError("MySQL column renaming requires full column definition")
        else:
            sql = f"ALTER TABLE {self.table_name} RENAME COLUMN {self.old_name} TO {self.new_name}"
            connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Rename back to old name."""
        if engine == "sqlite":
            raise MigrationError("SQLite does not support renaming columns")
        elif engine == "mysql":
            raise MigrationError("MySQL column renaming requires full column definition")
        else:
            sql = f"ALTER TABLE {self.table_name} RENAME COLUMN {self.new_name} TO {self.old_name}"
            connection.execute(sql)

    def describe(self) -> str:
        return f"Rename column '{self.old_name}' to '{self.new_name}' in table '{self.table_name}'"


class CreateIndex(MigrationOperation):
    """Create index operation."""

    def __init__(
        self,
        index_name: str,
        table_name: str,
        columns: List[str],
        unique: bool = False,
        partial: str = None,
    ):
        self.index_name = index_name
        self.table_name = table_name
        self.columns = columns
        self.unique = unique
        self.partial = partial

    def execute(self, connection: DatabaseConnection, engine: str):
        """Create the index."""
        unique_sql = "UNIQUE " if self.unique else ""
        columns_sql = ", ".join(self.columns)
        sql = f"CREATE {unique_sql}INDEX {self.index_name} ON {self.table_name} ({columns_sql})"

        if self.partial:
            sql += f" WHERE {self.partial}"

        connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Drop the index."""
        if engine == "mysql":
            sql = f"DROP INDEX {self.index_name} ON {self.table_name}"
        else:
            sql = f"DROP INDEX {self.index_name}"
        connection.execute(sql)

    def describe(self) -> str:
        unique_text = "unique " if self.unique else ""
        return f"Create {unique_text}index '{self.index_name}' on table '{self.table_name}'"


class DropIndex(MigrationOperation):
    """Drop index operation."""

    def __init__(self, index_name: str, table_name: str = None):
        self.index_name = index_name
        self.table_name = table_name

    def execute(self, connection: DatabaseConnection, engine: str):
        """Drop the index."""
        if engine == "mysql" and self.table_name:
            sql = f"DROP INDEX {self.index_name} ON {self.table_name}"
        else:
            sql = f"DROP INDEX {self.index_name}"
        connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """This operation cannot be automatically rolled back."""
        raise MigrationError(f"Cannot rollback DropIndex operation for {self.index_name}")

    def describe(self) -> str:
        return f"Drop index '{self.index_name}'"


class RunSQL(MigrationOperation):
    """Run custom SQL operation."""

    def __init__(self, sql: str, reverse_sql: str = None, params: List[Any] = None):
        self.sql = sql
        self.reverse_sql = reverse_sql
        self.params = params or []

    def execute(self, connection: DatabaseConnection, engine: str):
        """Execute the SQL."""
        connection.execute(self.sql, self.params)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Execute reverse SQL."""
        if not self.reverse_sql:
            raise MigrationError("Cannot rollback RunSQL operation without reverse_sql")
        connection.execute(self.reverse_sql, self.params)

    def describe(self) -> str:
        return f"Run custom SQL: {self.sql[:50]}..."


class Migration:
    """Database migration."""

    def __init__(self, name: str, app: str = "default", dependencies: List[str] = None):
        self.name = name
        self.app = app
        self.dependencies = dependencies or []
        self.operations: List[MigrationOperation] = []

    def add_operation(self, operation: MigrationOperation):
        """Add an operation to the migration."""
        self.operations.append(operation)

    def create_table(
        self,
        table_name: str,
        fields: Dict[str, Field],
        indexes: List[str] = None,
        constraints: List[str] = None,
    ):
        """Add create table operation."""
        op = CreateTable(table_name, fields, indexes, constraints)
        self.add_operation(op)

    def drop_table(self, table_name: str):
        """Add drop table operation."""
        op = DropTable(table_name)
        self.add_operation(op)

    def add_column(self, table_name: str, column_name: str, field: Field):
        """Add column operation."""
        op = AddColumn(table_name, column_name, field)
        self.add_operation(op)

    def drop_column(self, table_name: str, column_name: str):
        """Add drop column operation."""
        op = DropColumn(table_name, column_name)
        self.add_operation(op)

    def alter_column(
        self, table_name: str, column_name: str, field: Field, old_field: Field = None
    ):
        """Add alter column operation."""
        op = AlterColumn(table_name, column_name, field, old_field)
        self.add_operation(op)

    def rename_table(self, old_name: str, new_name: str):
        """Add rename table operation."""
        op = RenameTable(old_name, new_name)
        self.add_operation(op)

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        """Add rename column operation."""
        op = RenameColumn(table_name, old_name, new_name)
        self.add_operation(op)

    def create_index(
        self,
        index_name: str,
        table_name: str,
        columns: List[str],
        unique: bool = False,
        partial: str = None,
    ):
        """Add create index operation."""
        op = CreateIndex(index_name, table_name, columns, unique, partial)
        self.add_operation(op)

    def drop_index(self, index_name: str, table_name: str = None):
        """Add drop index operation."""
        op = DropIndex(index_name, table_name)
        self.add_operation(op)

    def run_sql(self, sql: str, reverse_sql: str = None, params: List[Any] = None):
        """Add custom SQL operation."""
        op = RunSQL(sql, reverse_sql, params)
        self.add_operation(op)

    def add_foreign_key(
        self,
        table_name: str,
        column_name: str,
        referenced_table: str,
        referenced_column: str = "id",
        on_delete: str = "CASCADE",
        on_update: str = "CASCADE",
        constraint_name: str = None,
    ):
        """Add foreign key constraint operation."""
        op = AddForeignKey(
            table_name,
            column_name,
            referenced_table,
            referenced_column,
            on_delete,
            on_update,
            constraint_name,
        )
        self.add_operation(op)

    def drop_foreign_key(self, table_name: str, constraint_name: str):
        """Add drop foreign key operation."""
        op = DropForeignKey(table_name, constraint_name)
        self.add_operation(op)

    def get_checksum(self) -> str:
        """Get migration checksum for integrity verification using SHA-256 instead of MD5 for security."""
        content = f"{self.name}:{self.app}:{len(self.operations)}"
        for op in self.operations:
            content += f":{op.describe()}"
        return hashlib.sha256(content.encode()).hexdigest()

    def execute(self, connection: DatabaseConnection, engine: str):
        """Execute the migration."""
        for i, operation in enumerate(self.operations):
            try:
                operation.execute(connection, engine)
            except Exception as e:
                raise MigrationError(
                    f"Migration {self.name} failed at operation {i}: {operation.describe()}: {e}"
                )

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Rollback the migration."""
        # Execute operations in reverse order
        for i, operation in enumerate(reversed(self.operations)):
            try:
                operation.rollback(connection, engine)
            except Exception as e:
                op_index = len(self.operations) - i - 1
                raise MigrationError(
                    f"Migration {self.name} rollback failed at operation {op_index}: {operation.describe()}: {e}"
                )


class MigrationRunner:
    """Migration execution engine."""

    def __init__(self, database: str = "default"):
        self.database = database
        self.pool = get_connection_pool(database)
        self._ensure_migration_table()

    def _ensure_migration_table(self):
        """Ensure migration tracking table exists."""
        with self.pool.connection() as conn:
            engine = conn.config.engine
            if engine == "postgresql":
                sql = """
                CREATE TABLE IF NOT EXISTS covet_migrations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    app VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum VARCHAR(32) NOT NULL,
                    UNIQUE(name, app)
                )
                """
            elif engine == "mysql":
                sql = """
                CREATE TABLE IF NOT EXISTS covet_migrations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    app VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum VARCHAR(32) NOT NULL,
                    UNIQUE KEY unique_migration (name, app)
                ) ENGINE=InnoDB
                """
            else:  # SQLite
                sql = """
                CREATE TABLE IF NOT EXISTS covet_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    app TEXT NOT NULL,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    checksum TEXT NOT NULL,
                    UNIQUE(name, app)
                )
                """
            conn.execute(sql)
            conn.commit()

    def get_applied_migrations(self) -> Dict[str, MigrationState]:
        """Get list of applied migrations."""
        with self.pool.connection() as conn:
            cursor = conn.execute(
                "SELECT name, app, applied_at, checksum FROM covet_migrations ORDER BY applied_at"
            )
            migrations = {}
            for row in cursor.fetchall():
                key = f"{row['app']}.{row['name']}"
                migrations[key] = MigrationState(
                    name=row["name"],
                    app=row["app"],
                    applied_at=row["applied_at"],
                    checksum=row["checksum"],
                )
            return migrations

    def is_migration_applied(self, migration: Migration) -> bool:
        """Check if a migration has been applied."""
        applied = self.get_applied_migrations()
        key = f"{migration.app}.{migration.name}"
        return key in applied

    def apply_migration(self, migration: Migration, fake: bool = False):
        """Apply a migration."""
        if self.is_migration_applied(migration):
            logger.info("Migration {migration.app}.{migration.name} already applied")
            return

        logger.info("Applying migration {migration.app}.{migration.name}")

        with self.pool.connection() as conn:
            engine = conn.config.engine

            if not fake:
                # Execute migration operations
                migration.execute(conn, engine)

            # Record migration as applied
            conn.execute(
                "INSERT INTO covet_migrations (name, app, checksum) VALUES (?, ?, ?)",
                [migration.name, migration.app, migration.get_checksum()],
            )
            conn.commit()

        logger.info("✓ Applied migration {migration.app}.{migration.name}")

    def rollback_migration(self, migration: Migration):
        """Rollback a migration."""
        if not self.is_migration_applied(migration):
            logger.info("Migration {migration.app}.{migration.name} not applied")
            return

        logger.info("Rolling back migration {migration.app}.{migration.name}")

        with self.pool.connection() as conn:
            engine = conn.config.engine

            # Execute rollback operations
            migration.rollback(conn, engine)

            # Remove migration record
            conn.execute(
                "DELETE FROM covet_migrations WHERE name = ? AND app = ?",
                [migration.name, migration.app],
            )
            conn.commit()

        logger.info("✓ Rolled back migration {migration.app}.{migration.name}")

    def apply_migrations(self, migrations: List[Migration], fake: bool = False):
        """Apply multiple migrations in order."""
        # Sort by dependencies (simple topological sort)
        sorted_migrations = self._sort_migrations(migrations)

        for migration in sorted_migrations:
            self.apply_migration(migration, fake)

    def rollback_migrations(self, migrations: List[Migration]):
        """Rollback multiple migrations in reverse order."""
        # Sort by dependencies and reverse
        sorted_migrations = self._sort_migrations(migrations)

        for migration in reversed(sorted_migrations):
            if self.is_migration_applied(migration):
                self.rollback_migration(migration)

    def _sort_migrations(self, migrations: List[Migration]) -> List[Migration]:
        """Sort migrations by dependencies."""
        # Simple topological sort
        sorted_migs = []
        remaining = migrations[:]

        while remaining:
            # Find migrations with no unresolved dependencies
            ready = []
            for migration in remaining:
                deps_satisfied = True
                for dep in migration.dependencies:
                    if not any(m.name == dep for m in sorted_migs):
                        deps_satisfied = False
                        break
                if deps_satisfied:
                    ready.append(migration)

            if not ready:
                raise MigrationError("Circular dependency detected in migrations")

            # Add ready migrations to sorted list
            for migration in ready:
                sorted_migs.append(migration)
                remaining.remove(migration)

        return sorted_migs

    def migrate(self, target: Optional[str] = None, fake: bool = False):
        """Run migrations up to target."""
        # This would typically load migrations from files
        # For now, just a placeholder
        logger.info("Migration system ready. Use apply_migration() to run specific migrations.")

    def show_migrations(self):
        """Show migration status."""
        applied = self.get_applied_migrations()
        logger.info("Applied migrations:")
        for key, state in applied.items():
            logger.info("  ✓ {key} (applied at {state.applied_at})")


class AddForeignKey(MigrationOperation):
    """Add foreign key constraint."""

    def __init__(
        self,
        table_name: str,
        column_name: str,
        referenced_table: str,
        referenced_column: str = "id",
        on_delete: str = "CASCADE",
        on_update: str = "CASCADE",
        constraint_name: str = None,
    ):
        self.table_name = table_name
        self.column_name = column_name
        self.referenced_table = referenced_table
        self.referenced_column = referenced_column
        self.on_delete = on_delete
        self.on_update = on_update
        self.constraint_name = constraint_name or f"fk_{table_name}_{column_name}"

    def execute(self, connection: DatabaseConnection, engine: str):
        """Add foreign key constraint."""
        if engine == "sqlite":
            raise MigrationError("SQLite does not support adding foreign keys to existing tables")

        sql = f"""
        ALTER TABLE {self.table_name}
        ADD CONSTRAINT {self.constraint_name}
        FOREIGN KEY ({self.column_name})
        REFERENCES {self.referenced_table}({self.referenced_column})
        ON DELETE {self.on_delete}
        ON UPDATE {self.on_update}
        """
        connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """Drop the foreign key constraint."""
        if engine == "sqlite":
            raise MigrationError("SQLite does not support dropping foreign keys")

        if engine == "mysql":
            sql = f"ALTER TABLE {self.table_name} DROP FOREIGN KEY {self.constraint_name}"
        else:
            sql = f"ALTER TABLE {self.table_name} DROP CONSTRAINT {self.constraint_name}"
        connection.execute(sql)

    def describe(self) -> str:
        return f"Add foreign key '{self.constraint_name}' to table '{self.table_name}'"


class DropForeignKey(MigrationOperation):
    """Drop foreign key constraint."""

    def __init__(self, table_name: str, constraint_name: str):
        self.table_name = table_name
        self.constraint_name = constraint_name

    def execute(self, connection: DatabaseConnection, engine: str):
        """Drop the foreign key constraint."""
        if engine == "sqlite":
            raise MigrationError("SQLite does not support dropping foreign keys")

        if engine == "mysql":
            sql = f"ALTER TABLE {self.table_name} DROP FOREIGN KEY {self.constraint_name}"
        else:
            sql = f"ALTER TABLE {self.table_name} DROP CONSTRAINT {self.constraint_name}"
        connection.execute(sql)

    def rollback(self, connection: DatabaseConnection, engine: str):
        """This operation cannot be automatically rolled back."""
        raise MigrationError(f"Cannot rollback DropForeignKey operation for {self.constraint_name}")

    def describe(self) -> str:
        return f"Drop foreign key '{self.constraint_name}' from table '{self.table_name}'"


@dataclass
class TableSchema:
    """Represents database table schema."""

    name: str
    columns: Dict[str, "ColumnSchema"]
    indexes: List["IndexSchema"]
    constraints: List["ConstraintSchema"]


@dataclass
class ColumnSchema:
    """Represents database column schema."""

    name: str
    data_type: str
    nullable: bool
    default: Optional[Any]
    primary_key: bool
    unique: bool


@dataclass
class IndexSchema:
    """Represents database index schema."""

    name: str
    table_name: str
    columns: List[str]
    unique: bool


@dataclass
class ConstraintSchema:
    """Represents database constraint schema."""

    name: str
    type: str  # 'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK'
    definition: str


class SchemaIntrospector:
    """Introspect database schema."""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.engine = connection.config.engine

    def get_tables(self) -> List[str]:
        """Get list of all tables in the database."""
        if self.engine == "postgresql":
            sql = """
            SELECT tablename FROM pg_catalog.pg_tables
            WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'
            """
        elif self.engine == "mysql":
            sql = "SHOW TABLES"
        else:  # SQLite
            sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"

        cursor = self.connection.execute(sql)
        return [row[0] for row in cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> TableSchema:
        """Get schema for a specific table."""
        columns = self.get_columns(table_name)
        indexes = self.get_indexes(table_name)
        constraints = self.get_constraints(table_name)

        return TableSchema(
            name=table_name, columns=columns, indexes=indexes, constraints=constraints
        )

    def get_columns(self, table_name: str) -> Dict[str, ColumnSchema]:
        """Get columns for a table."""
        if self.engine == "postgresql":
            sql = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
            """
            cursor = self.connection.execute(sql, [table_name])
        elif self.engine == "mysql":
            sql = f"DESCRIBE {table_name}"
            cursor = self.connection.execute(sql)
        else:  # SQLite
            sql = f"PRAGMA table_info({table_name})"
            cursor = self.connection.execute(sql)

        columns = {}
        for row in cursor.fetchall():
            if self.engine == "sqlite":
                columns[row["name"]] = ColumnSchema(
                    name=row["name"],
                    data_type=row["type"],
                    nullable=not row["notnull"],
                    default=row["dflt_value"],
                    primary_key=bool(row["pk"]),
                    unique=False,  # Would need separate query
                )
            elif self.engine == "mysql":
                columns[row["Field"]] = ColumnSchema(
                    name=row["Field"],
                    data_type=row["Type"],
                    nullable=row["Null"] == "YES",
                    default=row["Default"],
                    primary_key=row["Key"] == "PRI",
                    unique=row["Key"] == "UNI",
                )
            else:  # PostgreSQL
                columns[row["column_name"]] = ColumnSchema(
                    name=row["column_name"],
                    data_type=row["data_type"],
                    nullable=row["is_nullable"] == "YES",
                    default=row["column_default"],
                    primary_key=False,  # Would need separate query
                    unique=False,  # Would need separate query
                )

        return columns

    def get_indexes(self, table_name: str) -> List[IndexSchema]:
        """Get indexes for a table."""
        indexes = []

        if self.engine == "postgresql":
            sql = """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = %s
            """
            cursor = self.connection.execute(sql, [table_name])
            for row in cursor.fetchall():
                # Parse index definition to extract details
                indexes.append(
                    IndexSchema(
                        name=row["indexname"],
                        table_name=table_name,
                        columns=[],  # Would need to parse indexdef
                        unique="UNIQUE" in row["indexdef"],
                    )
                )
        elif self.engine == "mysql":
            sql = f"SHOW INDEX FROM {table_name}"
            cursor = self.connection.execute(sql)
            # Group by index name
            index_dict = {}
            for row in cursor.fetchall():
                idx_name = row["Key_name"]
                if idx_name not in index_dict:
                    index_dict[idx_name] = {
                        "columns": [],
                        "unique": not row["Non_unique"],
                    }
                index_dict[idx_name]["columns"].append(row["Column_name"])

            for idx_name, idx_data in index_dict.items():
                indexes.append(
                    IndexSchema(
                        name=idx_name,
                        table_name=table_name,
                        columns=idx_data["columns"],
                        unique=idx_data["unique"],
                    )
                )
        else:  # SQLite
            sql = f"PRAGMA index_list({table_name})"
            cursor = self.connection.execute(sql)
            for row in cursor.fetchall():
                # Get columns for this index
                idx_sql = f"PRAGMA index_info({row['name']})"
                idx_cursor = self.connection.execute(idx_sql)
                columns = [r["name"] for r in idx_cursor.fetchall()]

                indexes.append(
                    IndexSchema(
                        name=row["name"],
                        table_name=table_name,
                        columns=columns,
                        unique=bool(row["unique"]),
                    )
                )

        return indexes

    def get_constraints(self, table_name: str) -> List[ConstraintSchema]:
        """Get constraints for a table."""
        constraints = []

        if self.engine == "postgresql":
            sql = """
            SELECT conname, contype, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conrelid = %s::regclass
            """
            cursor = self.connection.execute(sql, [table_name])
            for row in cursor.fetchall():
                constraint_types = {
                    "p": "PRIMARY KEY",
                    "f": "FOREIGN KEY",
                    "u": "UNIQUE",
                    "c": "CHECK",
                }
                constraints.append(
                    ConstraintSchema(
                        name=row["conname"],
                        type=constraint_types.get(row["contype"], "UNKNOWN"),
                        definition=row["definition"],
                    )
                )
        elif self.engine == "mysql":
            sql = f"""  # nosec B608 - table_name validated in config
            SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_NAME = '{table_name}'
            """
            cursor = self.connection.execute(sql)
            for row in cursor.fetchall():
                constraints.append(
                    ConstraintSchema(
                        name=row["CONSTRAINT_NAME"],
                        type=row["CONSTRAINT_TYPE"],
                        definition="",
                    )
                )

        return constraints


class MigrationEngine:
    """Auto-generate migrations from model changes."""

    def __init__(self, database: str = "default"):
        self.database = database
        self.pool = get_connection_pool(database)

    def detect_changes(self, models: List[Type]) -> List[MigrationOperation]:
        """Detect changes between models and database schema."""
        operations = []

        with self.pool.connection() as conn:
            introspector = SchemaIntrospector(conn)
            existing_tables = set(introspector.get_tables())

            # Import here to avoid circular dependency
            from .models import Model

            for model_class in models:
                if not issubclass(model_class, Model):
                    continue

                table_name = model_class._meta.get_table_name()

                if table_name not in existing_tables:
                    # New table - create it
                    operations.extend(self._create_table_operations(model_class))
                else:
                    # Existing table - detect changes
                    operations.extend(self._detect_table_changes(model_class, introspector))

            # Detect dropped tables
            model_tables = {m._meta.get_table_name() for m in models if issubclass(m, Model)}
            for table in existing_tables:
                if table not in model_tables and table != "covet_migrations":
                    operations.append(DropTable(table))

        return operations

    def _create_table_operations(self, model_class) -> List[MigrationOperation]:
        """Generate operations to create a table."""
        operations = []
        table_name = model_class._meta.get_table_name()
        fields = {}

        for field_name, field in model_class._meta.fields.items():
            fields[field_name] = field

        operations.append(CreateTable(table_name, fields))

        # Add indexes
        for index in model_class._meta.indexes:
            # Parse index configuration and create operation
            pass

        return operations

    def _detect_table_changes(
        self, model_class, introspector: SchemaIntrospector
    ) -> List[MigrationOperation]:
        """Detect changes to an existing table."""
        operations = []
        table_name = model_class._meta.get_table_name()
        db_schema = introspector.get_table_schema(table_name)

        # Get model fields
        model_fields = {name: field for name, field in model_class._meta.fields.items()}
        db_columns = set(db_schema.columns.keys())
        model_columns = set(model_fields.keys())

        # Detect new columns
        new_columns = model_columns - db_columns
        for col_name in new_columns:
            operations.append(AddColumn(table_name, col_name, model_fields[col_name]))

        # Detect removed columns
        removed_columns = db_columns - model_columns
        for col_name in removed_columns:
            operations.append(DropColumn(table_name, col_name))

        # Detect changed columns (simplified - would need more sophisticated
        # comparison)
        common_columns = model_columns & db_columns
        for col_name in common_columns:
            model_field = model_fields[col_name]
            db_column = db_schema.columns[col_name]
            # Would need to compare types, nullability, etc.
            # This is a simplified version

        return operations

    def generate_migration(
        self, name: str, operations: List[MigrationOperation], app: str = "default"
    ) -> Migration:
        """Generate a migration from operations."""
        migration = Migration(name, app)
        for op in operations:
            migration.add_operation(op)
        return migration


class MigrationWriter:
    """Write migration files to disk."""

    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = migrations_dir
        os.makedirs(migrations_dir, exist_ok=True)

    def write_migration(self, migration: Migration) -> str:
        """Write migration to a file."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{migration.name}.py"
        filepath = os.path.join(self.migrations_dir, filename)

        content = self._generate_migration_code(migration)

        with open(filepath, "w") as f:
            f.write(content)

        return filepath

    def _generate_migration_code(self, migration: Migration) -> str:
        """Generate Python code for the migration."""
        operations_code = []

        for op in migration.operations:
            operations_code.append(self._operation_to_code(op))

        operations_str = ",\n        ".join(operations_code)

        code = f'''"""
Migration: {migration.name}
App: {migration.app}
Generated: {datetime.datetime.now().isoformat()}
"""

from covet.orm.migrations import Migration
from covet.orm.fields import *


def upgrade():
    """Apply migration."""
    migration = Migration(
        name="{migration.name}",
        app="{migration.app}",
        dependencies={migration.dependencies}
    )

    # Operations
    operations = [
        {operations_str}
    ]

    for op in operations:
        migration.add_operation(op)

    return migration


def downgrade():
    """Rollback migration."""
    # Rollback is handled automatically by the migration system
    pass
'''
        return code

    def _operation_to_code(self, operation: MigrationOperation) -> str:
        """Convert operation to Python code."""
        op_type = type(operation).__name__

        if isinstance(operation, CreateTable):
            fields_code = "{\n"
            for field_name, field in operation.fields.items():
                field_type = type(field).__name__
                fields_code += f'            "{field_name}": {field_type}(),\n'
            fields_code += "        }"
            return f'CreateTable("{operation.table_name}", {fields_code})'

        elif isinstance(operation, AddColumn):
            field_type = type(operation.field).__name__
            return f'AddColumn("{operation.table_name}", "{operation.column_name}", {field_type}())'

        elif isinstance(operation, DropColumn):
            return f'DropColumn("{operation.table_name}", "{operation.column_name}")'

        elif isinstance(operation, CreateIndex):
            return f'CreateIndex("{operation.index_name}", "{operation.table_name}", {operation.columns}, unique={operation.unique})'

        else:
            return f"{op_type}()"


class MigrationLoader:
    """Load migrations from files."""

    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = migrations_dir

    def load_migrations(self) -> List[Migration]:
        """Load all migrations from the migrations directory."""
        migrations = []

        if not os.path.exists(self.migrations_dir):
            return migrations

        # Get all Python files
        migration_files = sorted(
            [f for f in os.listdir(self.migrations_dir) if f.endswith(".py") and f != "__init__.py"]
        )

        for filename in migration_files:
            filepath = os.path.join(self.migrations_dir, filename)
            migration = self._load_migration_file(filepath)
            if migration:
                migrations.append(migration)

        return migrations

    def _load_migration_file(self, filepath: str) -> Optional[Migration]:
        """Load a single migration file."""
        try:
            # Import the migration module
            import importlib.util

            spec = importlib.util.spec_from_file_location("migration", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get the upgrade function
            if hasattr(module, "upgrade"):
                return module.upgrade()

        except Exception as e:
            logger.error(f"Failed to load migration {filepath}: {e}")
            return None


def create_migration(name: str, app: str = "default", dependencies: List[str] = None) -> Migration:
    """Create a new migration."""
    return Migration(name, app, dependencies)
