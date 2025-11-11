"""
Migration Generator

Generates forward (apply) and backward (rollback) SQL migration files from operations.
Supports all three database backends with proper SQL syntax for each dialect.

This is where the abstract MigrationOperation objects get converted into
actual executable SQL statements. The generator is responsible for:
- Correct SQL syntax for each database
- Safe type conversions
- Proper constraint ordering
- Rollback SQL generation

Example:
    from covet.database.migrations.generator import MigrationGenerator
    from covet.database.migrations.diff_engine import MigrationOperation

    generator = MigrationGenerator(dialect='postgresql')

    # Generate migration file
    migration_file = generator.generate_migration(
        operations=operations,
        migration_name='0001_initial',
        app_name='myapp'
    )

    # Save to disk
    generator.save_migration(migration_file, '/path/to/migrations/')
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..security.sql_validator import (
    DatabaseDialect,
    SQLIdentifierError,
    quote_identifier,
    validate_column_name,
    validate_identifier,
    validate_table_name,
)
from .diff_engine import MigrationOperation, OperationType
from .model_reader import ColumnSchema, IndexSchema, RelationshipSchema, TableSchema

logger = logging.getLogger(__name__)


class MigrationFile:
    """
    Represents a migration file with forward and backward operations.

    Attributes:
        name: Migration file name (e.g., '0001_initial')
        timestamp: Creation timestamp
        app_name: App name
        dependencies: List of migration names this depends on
        operations: List of MigrationOperation objects
        forward_sql: SQL statements for applying migration
        backward_sql: SQL statements for rolling back migration
    """

    def __init__(
        self,
        name: str,
        app_name: str,
        operations: List[MigrationOperation],
        dependencies: Optional[List[str]] = None,
    ):
        self.name = name
        self.timestamp = datetime.now()
        self.app_name = app_name
        self.operations = operations
        self.dependencies = dependencies or []
        self.forward_sql: List[str] = []
        self.backward_sql: List[str] = []

    def add_forward_sql(self, sql: str):
        """Add SQL statement for forward migration."""
        if sql:
            self.forward_sql.append(sql)

    def add_backward_sql(self, sql: str):
        """Add SQL statement for backward migration."""
        if sql:
            self.backward_sql.append(sql)

    def to_python_file(self) -> str:
        """
        Generate Python migration file content.

        Returns:
            Python code as string
        """
        # Build operations code
        operations_code = []
        for op in self.operations:
            op_dict = op.to_dict()
            operations_code.append(f"        {op_dict},")

        operations_str = "\n".join(operations_code)

        # Build forward SQL
        forward_sql_list = [f'        "{sql}"' for sql in self.forward_sql]
        forward_sql_str = ",\n".join(forward_sql_list) if forward_sql_list else ""

        # Build backward SQL
        backward_sql_list = [f'        "{sql}"' for sql in self.backward_sql]
        backward_sql_str = ",\n".join(backward_sql_list) if backward_sql_list else ""

        # Build dependencies
        deps_str = ", ".join(f"'{dep}'" for dep in self.dependencies)

        content = f'''"""
Migration: {self.name}
Generated: {self.timestamp.isoformat()}
App: {self.app_name}
"""

from covet.database.migrations import Migration


class {self._get_class_name()}(Migration):
    """Auto-generated migration."""

    dependencies = [{deps_str}]

    operations = [
{operations_str}
    ]

    forward_sql = [
{forward_sql_str}
    ]

    backward_sql = [
{backward_sql_str}
    ]

    async def apply(self, adapter):
        """Apply migration."""
        for sql in self.forward_sql:
            await adapter.execute(sql)

    async def rollback(self, adapter):
        """Rollback migration."""
        for sql in self.backward_sql:
            await adapter.execute(sql)
'''
        return content

    def _get_class_name(self) -> str:
        """Generate Python class name from migration name."""
        # Convert '0001_initial' to 'Migration0001Initial'
        parts = self.name.split("_")
        class_parts = ["Migration"] + [p.capitalize() for p in parts]
        return "".join(class_parts)

    def get_filename(self) -> str:
        """Get migration filename."""
        return f"{self.name}.py"


class SQLGenerator:
    """
    Base class for SQL generation with dialect-specific implementations.

    Each database has its own quirks in SQL syntax:
    - Parameter placeholders ($1 vs %s vs ?)
    - Type names (SERIAL vs AUTO_INCREMENT)
    - ALTER TABLE syntax
    - Index creation syntax
    - Constraint syntax

    This class provides the interface that dialect-specific subclasses implement.
    """

    def __init__(self, dialect: str):
        """
        Initialize SQL generator with security validation.

        Args:
            dialect: Database dialect ('postgresql', 'mysql', 'sqlite')

        Security:
            - Maps dialect to DatabaseDialect enum for validation
            - Initializes secure identifier quoting
        """
        self.dialect = dialect.lower()

        # Map to DatabaseDialect for security validation
        dialect_map = {
            "postgresql": DatabaseDialect.POSTGRESQL,
            "mysql": DatabaseDialect.MYSQL,
            "sqlite": DatabaseDialect.SQLITE,
        }
        self.db_dialect = dialect_map.get(self.dialect, DatabaseDialect.GENERIC)

    def generate_create_table(self, table_name: str, schema: TableSchema) -> Tuple[str, str]:
        """
        Generate CREATE TABLE SQL.

        Args:
            table_name: Table name
            schema: Table schema

        Returns:
            Tuple of (forward_sql, backward_sql)
        """
        raise NotImplementedError

    def generate_drop_table(self, table_name: str) -> Tuple[str, str]:
        """
        Generate DROP TABLE SQL.

        Args:
            table_name: Table name

        Returns:
            Tuple of (forward_sql, backward_sql)
        """
        forward = f"DROP TABLE IF EXISTS {self._quote_identifier(table_name)} CASCADE"
        backward = ""  # Cannot reverse table drop
        return forward, backward

    def generate_add_column(self, table_name: str, column: ColumnSchema) -> Tuple[str, str]:
        """Generate ADD COLUMN SQL."""
        raise NotImplementedError

    def generate_drop_column(self, table_name: str, column_name: str) -> Tuple[str, str]:
        """Generate DROP COLUMN SQL."""
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"DROP COLUMN {self._quote_identifier(column_name)}"
        )
        backward = ""  # Cannot reverse column drop
        return forward, backward

    def generate_rename_column(
        self, table_name: str, old_name: str, new_name: str, column: ColumnSchema
    ) -> Tuple[str, str]:
        """
        Generate RENAME COLUMN SQL.

        This is database-specific as each dialect has different syntax.
        Must be implemented by subclasses.

        Args:
            table_name: Table name
            old_name: Current column name
            new_name: New column name
            column: Column schema (for MySQL which needs full definition)

        Returns:
            Tuple of (forward_sql, backward_sql)
        """
        raise NotImplementedError

    def generate_alter_column(
        self, table_name: str, old_column: ColumnSchema, new_column: ColumnSchema
    ) -> Tuple[List[str], List[str]]:
        """Generate ALTER COLUMN SQL."""
        raise NotImplementedError

    def generate_add_index(self, table_name: str, index: IndexSchema) -> Tuple[str, str]:
        """Generate CREATE INDEX SQL."""
        raise NotImplementedError

    def generate_drop_index(self, table_name: str, index_name: str) -> Tuple[str, str]:
        """Generate DROP INDEX SQL."""
        raise NotImplementedError

    def generate_add_foreign_key(self, table_name: str, fk: RelationshipSchema) -> Tuple[str, str]:
        """Generate ADD FOREIGN KEY SQL."""
        raise NotImplementedError

    def generate_drop_foreign_key(self, table_name: str, constraint_name: str) -> Tuple[str, str]:
        """Generate DROP FOREIGN KEY SQL."""
        raise NotImplementedError

    def _quote_identifier(self, name: str) -> str:
        """
        Quote identifier for SQL with security validation.

        This is the primary defense against CVE-SPRINT2-002 (SQL Injection).
        All table and column names are validated before being quoted.

        Args:
            name: Identifier to quote (table name, column name, etc.)

        Returns:
            Securely quoted identifier

        Raises:
            SQLIdentifierError: If identifier contains dangerous characters

        Security:
            - Validates identifier against SQL injection patterns
            - Checks for dangerous characters
            - Ensures proper quoting for database dialect
            - Prevents identifier-based SQL injection
        """
        try:
            # Validate identifier first (CVE-SPRINT2-002 fix)
            validated_name = validate_identifier(name, dialect=self.db_dialect, allow_dots=False)

            # Quote using secure method
            return quote_identifier(validated_name, self.db_dialect)

        except SQLIdentifierError as e:
            logger.error(
                f"SQL identifier validation failed for '{name}': {e}. "
                f"This may indicate a SQL injection attempt."
            )
            raise ValueError(
                f"Invalid SQL identifier '{name}': {e}. "
                f"Identifiers must contain only alphanumeric characters "
                f"and underscores, and cannot be SQL reserved keywords."
            )

    def _format_column_definition(self, column: ColumnSchema) -> str:
        """Format column definition for CREATE TABLE."""
        parts = [self._quote_identifier(column.name), column.db_type]

        if column.primary_key:
            parts.append("PRIMARY KEY")

        if not column.nullable:
            parts.append("NOT NULL")

        if column.unique and not column.primary_key:
            parts.append("UNIQUE")

        if column.default is not None:
            parts.append(f"DEFAULT {self._format_default(column.default)}")

        return " ".join(parts)

    def _format_default(self, value: Any) -> str:
        """Format default value for SQL."""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return f"'{value}'"
        else:
            return f"'{str(value)}'"


class PostgreSQLGenerator(SQLGenerator):
    """PostgreSQL-specific SQL generator."""

    def __init__(self):
        super().__init__("postgresql")

    def generate_create_table(self, table_name: str, schema: TableSchema) -> Tuple[str, str]:
        """Generate PostgreSQL CREATE TABLE."""
        lines = [f"CREATE TABLE {self._quote_identifier(table_name)} ("]

        # Add columns
        column_defs = []
        for column in schema.columns:
            column_defs.append(f"    {self._format_column_definition(column)}")

        lines.append(",\n".join(column_defs))
        lines.append(")")

        forward = "\n".join(lines)
        backward = f"DROP TABLE IF EXISTS {self._quote_identifier(table_name)} CASCADE"

        return forward, backward

    def generate_add_column(self, table_name: str, column: ColumnSchema) -> Tuple[str, str]:
        """Generate PostgreSQL ADD COLUMN."""
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"ADD COLUMN {self._format_column_definition(column)}"
        )
        backward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"DROP COLUMN {self._quote_identifier(column.name)}"
        )
        return forward, backward

    def generate_rename_column(
        self, table_name: str, old_name: str, new_name: str, column: ColumnSchema
    ) -> Tuple[str, str]:
        """
        Generate PostgreSQL RENAME COLUMN.

        PostgreSQL uses: ALTER TABLE ... RENAME COLUMN old TO new

        This is a metadata-only operation that preserves all data,
        constraints, and indexes.
        """
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"RENAME COLUMN {self._quote_identifier(old_name)} "
            f"TO {self._quote_identifier(new_name)}"
        )
        backward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"RENAME COLUMN {self._quote_identifier(new_name)} "
            f"TO {self._quote_identifier(old_name)}"
        )
        return forward, backward

    def generate_alter_column(
        self, table_name: str, old_column: ColumnSchema, new_column: ColumnSchema
    ) -> Tuple[List[str], List[str]]:
        """Generate PostgreSQL ALTER COLUMN."""
        forward_sql = []
        backward_sql = []

        table_id = self._quote_identifier(table_name)
        col_id = self._quote_identifier(new_column.name)

        # Change type
        if old_column.db_type != new_column.db_type:
            forward_sql.append(
                f"ALTER TABLE {table_id} " f"ALTER COLUMN {col_id} TYPE {new_column.db_type}"
            )
            backward_sql.append(
                f"ALTER TABLE {table_id} " f"ALTER COLUMN {col_id} TYPE {old_column.db_type}"
            )

        # Change nullable
        if old_column.nullable != new_column.nullable:
            if new_column.nullable:
                forward_sql.append(
                    f"ALTER TABLE {table_id} " f"ALTER COLUMN {col_id} DROP NOT NULL"
                )
                backward_sql.append(
                    f"ALTER TABLE {table_id} " f"ALTER COLUMN {col_id} SET NOT NULL"
                )
            else:
                forward_sql.append(f"ALTER TABLE {table_id} " f"ALTER COLUMN {col_id} SET NOT NULL")
                backward_sql.append(
                    f"ALTER TABLE {table_id} " f"ALTER COLUMN {col_id} DROP NOT NULL"
                )

        # Change default
        if old_column.default != new_column.default:
            if new_column.default is not None:
                forward_sql.append(
                    f"ALTER TABLE {table_id} "
                    f"ALTER COLUMN {col_id} SET DEFAULT {self._format_default(new_column.default)}"
                )
            else:
                forward_sql.append(f"ALTER TABLE {table_id} " f"ALTER COLUMN {col_id} DROP DEFAULT")

            if old_column.default is not None:
                backward_sql.append(
                    f"ALTER TABLE {table_id} "
                    f"ALTER COLUMN {col_id} SET DEFAULT {self._format_default(old_column.default)}"
                )
            else:
                backward_sql.append(
                    f"ALTER TABLE {table_id} " f"ALTER COLUMN {col_id} DROP DEFAULT"
                )

        return forward_sql, backward_sql

    def generate_add_index(self, table_name: str, index: IndexSchema) -> Tuple[str, str]:
        """Generate PostgreSQL CREATE INDEX."""
        unique = "UNIQUE " if index.unique else ""
        columns = ", ".join(self._quote_identifier(col) for col in index.columns)

        forward = (
            f"CREATE {unique}INDEX {self._quote_identifier(index.name)} "
            f"ON {self._quote_identifier(table_name)} ({columns})"
        )
        backward = f"DROP INDEX IF EXISTS {self._quote_identifier(index.name)}"

        return forward, backward

    def generate_drop_index(self, table_name: str, index_name: str) -> Tuple[str, str]:
        """Generate PostgreSQL DROP INDEX."""
        forward = f"DROP INDEX IF EXISTS {self._quote_identifier(index_name)}"
        backward = ""  # Cannot reverse without knowing index definition
        return forward, backward

    def generate_add_foreign_key(self, table_name: str, fk: RelationshipSchema) -> Tuple[str, str]:
        """Generate PostgreSQL ADD FOREIGN KEY."""
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"ADD CONSTRAINT {self._quote_identifier(fk.name)} "
            f"FOREIGN KEY ({self._quote_identifier(fk.column)}) "
            f"REFERENCES {self._quote_identifier(fk.referenced_table)}({self._quote_identifier(fk.referenced_column)}) "
            f"ON DELETE {fk.on_delete} ON UPDATE {fk.on_update}"
        )
        backward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"DROP CONSTRAINT IF EXISTS {self._quote_identifier(fk.name)}"
        )
        return forward, backward

    def generate_drop_foreign_key(self, table_name: str, constraint_name: str) -> Tuple[str, str]:
        """Generate PostgreSQL DROP FOREIGN KEY."""
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"DROP CONSTRAINT IF EXISTS {self._quote_identifier(constraint_name)}"
        )
        backward = ""  # Cannot reverse without knowing FK definition
        return forward, backward


class MySQLGenerator(SQLGenerator):
    """MySQL-specific SQL generator."""

    def __init__(self):
        super().__init__("mysql")

    def generate_create_table(self, table_name: str, schema: TableSchema) -> Tuple[str, str]:
        """Generate MySQL CREATE TABLE."""
        lines = [f"CREATE TABLE {self._quote_identifier(table_name)} ("]

        # Add columns
        column_defs = []
        for column in schema.columns:
            column_defs.append(f"    {self._format_column_definition(column)}")

        lines.append(",\n".join(column_defs))
        lines.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")

        forward = "\n".join(lines)
        backward = f"DROP TABLE IF EXISTS {self._quote_identifier(table_name)}"

        return forward, backward

    def generate_add_column(self, table_name: str, column: ColumnSchema) -> Tuple[str, str]:
        """Generate MySQL ADD COLUMN."""
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"ADD COLUMN {self._format_column_definition(column)}"
        )
        backward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"DROP COLUMN {self._quote_identifier(column.name)}"
        )
        return forward, backward

    def generate_rename_column(
        self, table_name: str, old_name: str, new_name: str, column: ColumnSchema
    ) -> Tuple[str, str]:
        """
        Generate MySQL RENAME COLUMN.

        MySQL uses: ALTER TABLE ... CHANGE old_name new_name column_definition

        Note: MySQL requires the full column definition, not just the name.
        This preserves data but requires specifying all column attributes.
        """
        # MySQL CHANGE requires full column definition
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"CHANGE {self._quote_identifier(old_name)} "
            f"{self._format_column_definition(column)}"
        )

        # For backward, we need to recreate the old column definition
        # but with the old name
        old_column = ColumnSchema(
            name=old_name,
            db_type=column.db_type,
            nullable=column.nullable,
            default=column.default,
            unique=column.unique,
            primary_key=column.primary_key,
            auto_increment=column.auto_increment,
        )
        backward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"CHANGE {self._quote_identifier(new_name)} "
            f"{self._format_column_definition(old_column)}"
        )

        return forward, backward

    def generate_alter_column(
        self, table_name: str, old_column: ColumnSchema, new_column: ColumnSchema
    ) -> Tuple[List[str], List[str]]:
        """Generate MySQL ALTER COLUMN."""
        # MySQL uses MODIFY COLUMN for type/null changes
        forward_sql = [
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"MODIFY COLUMN {self._format_column_definition(new_column)}"
        ]
        backward_sql = [
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"MODIFY COLUMN {self._format_column_definition(old_column)}"
        ]
        return forward_sql, backward_sql

    def generate_add_index(self, table_name: str, index: IndexSchema) -> Tuple[str, str]:
        """Generate MySQL CREATE INDEX."""
        unique = "UNIQUE " if index.unique else ""
        columns = ", ".join(self._quote_identifier(col) for col in index.columns)

        forward = (
            f"CREATE {unique}INDEX {self._quote_identifier(index.name)} "
            f"ON {self._quote_identifier(table_name)} ({columns})"
        )
        backward = (
            f"DROP INDEX {self._quote_identifier(index.name)} "
            f"ON {self._quote_identifier(table_name)}"
        )

        return forward, backward

    def generate_drop_index(self, table_name: str, index_name: str) -> Tuple[str, str]:
        """Generate MySQL DROP INDEX."""
        forward = (
            f"DROP INDEX {self._quote_identifier(index_name)} "
            f"ON {self._quote_identifier(table_name)}"
        )
        backward = ""
        return forward, backward

    def generate_add_foreign_key(self, table_name: str, fk: RelationshipSchema) -> Tuple[str, str]:
        """Generate MySQL ADD FOREIGN KEY."""
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"ADD CONSTRAINT {self._quote_identifier(fk.name)} "
            f"FOREIGN KEY ({self._quote_identifier(fk.column)}) "
            f"REFERENCES {self._quote_identifier(fk.referenced_table)}({self._quote_identifier(fk.referenced_column)}) "
            f"ON DELETE {fk.on_delete} ON UPDATE {fk.on_update}"
        )
        backward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"DROP FOREIGN KEY {self._quote_identifier(fk.name)}"
        )
        return forward, backward

    def generate_drop_foreign_key(self, table_name: str, constraint_name: str) -> Tuple[str, str]:
        """Generate MySQL DROP FOREIGN KEY."""
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"DROP FOREIGN KEY {self._quote_identifier(constraint_name)}"
        )
        backward = ""
        return forward, backward


class SQLiteGenerator(SQLGenerator):
    """SQLite-specific SQL generator."""

    def __init__(self):
        super().__init__("sqlite")

    def generate_create_table(self, table_name: str, schema: TableSchema) -> Tuple[str, str]:
        """Generate SQLite CREATE TABLE."""
        lines = [f"CREATE TABLE {self._quote_identifier(table_name)} ("]

        # Add columns
        column_defs = []
        for column in schema.columns:
            column_defs.append(f"    {self._format_column_definition(column)}")

        lines.append(",\n".join(column_defs))
        lines.append(")")

        forward = "\n".join(lines)
        backward = f"DROP TABLE IF EXISTS {self._quote_identifier(table_name)}"

        return forward, backward

    def generate_add_column(self, table_name: str, column: ColumnSchema) -> Tuple[str, str]:
        """Generate SQLite ADD COLUMN."""
        # SQLite has limited ALTER TABLE support
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"ADD COLUMN {self._format_column_definition(column)}"
        )
        # Cannot drop columns in SQLite easily
        backward = f"-- Cannot drop column in SQLite: {column.name}"
        return forward, backward

    def generate_rename_column(
        self, table_name: str, old_name: str, new_name: str, column: ColumnSchema
    ) -> Tuple[str, str]:
        """
        Generate SQLite RENAME COLUMN.

        SQLite 3.25.0+ supports: ALTER TABLE ... RENAME COLUMN old TO new

        For older SQLite versions, would require full table recreation:
        1. CREATE TABLE new_table (with new column name)
        2. INSERT INTO new_table SELECT ... FROM old_table
        3. DROP TABLE old_table
        4. ALTER TABLE new_table RENAME TO old_table

        We use the modern syntax and provide a warning for older versions.
        """
        forward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"RENAME COLUMN {self._quote_identifier(old_name)} "
            f"TO {self._quote_identifier(new_name)}"
        )
        backward = (
            f"ALTER TABLE {self._quote_identifier(table_name)} "
            f"RENAME COLUMN {self._quote_identifier(new_name)} "
            f"TO {self._quote_identifier(old_name)}"
        )

        return forward, backward

    def generate_alter_column(
        self, table_name: str, old_column: ColumnSchema, new_column: ColumnSchema
    ) -> Tuple[List[str], List[str]]:
        """Generate SQLite ALTER COLUMN."""
        # SQLite doesn't support ALTER COLUMN
        # Would need to recreate table
        forward_sql = [
            f"-- SQLite doesn't support ALTER COLUMN. "
            f"Manual table recreation required for {table_name}.{new_column.name}"
        ]
        backward_sql = [
            f"-- SQLite doesn't support ALTER COLUMN. " f"Manual table recreation required"
        ]
        return forward_sql, backward_sql

    def generate_add_index(self, table_name: str, index: IndexSchema) -> Tuple[str, str]:
        """Generate SQLite CREATE INDEX."""
        unique = "UNIQUE " if index.unique else ""
        columns = ", ".join(self._quote_identifier(col) for col in index.columns)

        forward = (
            f"CREATE {unique}INDEX {self._quote_identifier(index.name)} "
            f"ON {self._quote_identifier(table_name)} ({columns})"
        )
        backward = f"DROP INDEX IF EXISTS {self._quote_identifier(index.name)}"

        return forward, backward

    def generate_drop_index(self, table_name: str, index_name: str) -> Tuple[str, str]:
        """Generate SQLite DROP INDEX."""
        forward = f"DROP INDEX IF EXISTS {self._quote_identifier(index_name)}"
        backward = ""
        return forward, backward

    def generate_add_foreign_key(self, table_name: str, fk: RelationshipSchema) -> Tuple[str, str]:
        """Generate SQLite ADD FOREIGN KEY."""
        # SQLite doesn't support adding FK constraints to existing tables
        forward = (
            f"-- SQLite doesn't support adding FK constraints. "
            f"Table must be recreated with FK: {fk.name}"
        )
        backward = ""
        return forward, backward

    def generate_drop_foreign_key(self, table_name: str, constraint_name: str) -> Tuple[str, str]:
        """Generate SQLite DROP FOREIGN KEY."""
        # SQLite doesn't support dropping FK constraints
        forward = f"-- SQLite doesn't support dropping FK constraints: {constraint_name}"
        backward = ""
        return forward, backward


class MigrationGenerator:
    """
    Generates migration files from migration operations.

    This is the orchestrator that:
    1. Takes a list of operations
    2. Uses dialect-specific SQL generator
    3. Creates properly formatted migration files
    4. Handles numbering and dependencies

    Example:
        generator = MigrationGenerator(dialect='postgresql')

        migration_file = generator.generate_migration(
            operations=operations,
            migration_name='add_user_table',
            app_name='accounts'
        )

        # Save to disk
        path = generator.save_migration(migration_file, './migrations')
        print(f"Created: {path}")
    """

    def __init__(self, dialect: str = "postgresql"):
        """
        Initialize migration generator.

        Args:
            dialect: Database dialect ('postgresql', 'mysql', 'sqlite')
        """
        self.dialect = dialect.lower()

        # Create dialect-specific SQL generator
        if self.dialect == "postgresql":
            self.sql_generator = PostgreSQLGenerator()
        elif self.dialect == "mysql":
            self.sql_generator = MySQLGenerator()
        elif self.dialect == "sqlite":
            self.sql_generator = SQLiteGenerator()
        else:
            raise ValueError(f"Unsupported dialect: {dialect}")

    def generate_migration(
        self,
        operations: List[MigrationOperation],
        migration_name: str,
        app_name: str = "default",
        dependencies: Optional[List[str]] = None,
    ) -> MigrationFile:
        """
        Generate migration file from operations.

        Args:
            operations: List of MigrationOperation objects
            migration_name: Migration name (without number prefix)
            app_name: App name
            dependencies: List of migration names this depends on

        Returns:
            MigrationFile object
        """
        # Create migration file
        migration = MigrationFile(
            name=migration_name,
            app_name=app_name,
            operations=operations,
            dependencies=dependencies,
        )

        # Generate SQL for each operation
        for op in operations:
            forward_sql, backward_sql = self._generate_sql_for_operation(op)

            if isinstance(forward_sql, list):
                for sql in forward_sql:
                    migration.add_forward_sql(sql)
            else:
                migration.add_forward_sql(forward_sql)

            if isinstance(backward_sql, list):
                for sql in backward_sql:
                    migration.add_backward_sql(sql)
            else:
                migration.add_backward_sql(backward_sql)

        logger.info(
            f"Generated migration '{migration_name}': "
            f"{len(migration.forward_sql)} forward statements, "
            f"{len(migration.backward_sql)} backward statements"
        )

        return migration

    def _generate_sql_for_operation(self, operation: MigrationOperation) -> Tuple:
        """Generate SQL for a single operation."""
        op_type = operation.operation_type
        table_name = operation.table_name
        details = operation.details

        if op_type == OperationType.CREATE_TABLE:
            schema_dict = details["schema"]
            schema = self._dict_to_table_schema(schema_dict)
            return self.sql_generator.generate_create_table(table_name, schema)

        elif op_type == OperationType.DROP_TABLE:
            return self.sql_generator.generate_drop_table(table_name)

        elif op_type == OperationType.ADD_COLUMN:
            column_dict = details["column"]
            column = self._dict_to_column_schema(column_dict)
            return self.sql_generator.generate_add_column(table_name, column)

        elif op_type == OperationType.DROP_COLUMN:
            return self.sql_generator.generate_drop_column(table_name, details["column_name"])

        elif op_type == OperationType.RENAME_COLUMN:
            old_name = details["old_name"]
            new_name = details["new_name"]
            new_col = self._dict_to_column_schema(details["new_column"])
            return self.sql_generator.generate_rename_column(
                table_name, old_name, new_name, new_col
            )

        elif op_type == OperationType.ALTER_COLUMN:
            old_col = self._dict_to_column_schema(details["old_column"])
            new_col = self._dict_to_column_schema(details["new_column"])
            return self.sql_generator.generate_alter_column(table_name, old_col, new_col)

        elif op_type == OperationType.ADD_INDEX:
            index_dict = details["index"]
            index = self._dict_to_index_schema(index_dict)
            return self.sql_generator.generate_add_index(table_name, index)

        elif op_type == OperationType.DROP_INDEX:
            return self.sql_generator.generate_drop_index(table_name, details["index_name"])

        elif op_type == OperationType.ADD_FOREIGN_KEY:
            fk_dict = details["foreign_key"]
            fk = self._dict_to_relationship_schema(fk_dict)
            return self.sql_generator.generate_add_foreign_key(table_name, fk)

        elif op_type == OperationType.DROP_FOREIGN_KEY:
            return self.sql_generator.generate_drop_foreign_key(
                table_name, details["constraint_name"]
            )

        else:
            logger.warning(f"Unknown operation type: {op_type}")
            return "", ""

    def _dict_to_table_schema(self, schema_dict: Dict) -> TableSchema:
        """Convert dictionary to TableSchema."""
        schema = TableSchema(schema_dict["name"])

        for col_dict in schema_dict["columns"]:
            column = self._dict_to_column_schema(col_dict)
            schema.add_column(column)

        for idx_dict in schema_dict["indexes"]:
            index = self._dict_to_index_schema(idx_dict)
            schema.add_index(index)

        for fk_dict in schema_dict["relationships"]:
            fk = self._dict_to_relationship_schema(fk_dict)
            schema.add_relationship(fk)

        return schema

    def _dict_to_column_schema(self, col_dict: Dict) -> ColumnSchema:
        """Convert dictionary to ColumnSchema."""
        return ColumnSchema(
            name=col_dict["name"],
            db_type=col_dict["db_type"],
            nullable=col_dict["nullable"],
            default=col_dict["default"],
            unique=col_dict["unique"],
            primary_key=col_dict["primary_key"],
            auto_increment=col_dict["auto_increment"],
            max_length=col_dict.get("max_length"),
            precision=col_dict.get("precision"),
            scale=col_dict.get("scale"),
        )

    def _dict_to_index_schema(self, idx_dict: Dict) -> IndexSchema:
        """Convert dictionary to IndexSchema."""
        return IndexSchema(
            name=idx_dict["name"],
            columns=idx_dict["columns"],
            unique=idx_dict["unique"],
            method=idx_dict.get("method"),
        )

    def _dict_to_relationship_schema(self, fk_dict: Dict) -> RelationshipSchema:
        """Convert dictionary to RelationshipSchema."""
        return RelationshipSchema(
            name=fk_dict["name"],
            column=fk_dict["column"],
            referenced_table=fk_dict["referenced_table"],
            referenced_column=fk_dict["referenced_column"],
            on_delete=fk_dict["on_delete"],
            on_update=fk_dict["on_update"],
        )

    def save_migration(self, migration: MigrationFile, migrations_dir: str) -> str:
        """
        Save migration file to disk.

        Args:
            migration: MigrationFile object
            migrations_dir: Directory to save migration

        Returns:
            Full path to saved migration file
        """
        # Create migrations directory if it doesn't exist
        Path(migrations_dir).mkdir(parents=True, exist_ok=True)

        # Get full path
        filename = migration.get_filename()
        filepath = os.path.join(migrations_dir, filename)

        # Write migration file
        with open(filepath, "w") as f:
            f.write(migration.to_python_file())

        logger.info(f"Saved migration: {filepath}")
        return filepath

    def get_next_migration_number(self, migrations_dir: str) -> str:
        """
        Get next migration number based on existing migrations.

        Args:
            migrations_dir: Directory containing migrations

        Returns:
            Next migration number (e.g., '0001', '0002')
        """
        if not os.path.exists(migrations_dir):
            return "0001"

        # Find existing migrations
        existing = [
            f for f in os.listdir(migrations_dir) if f.endswith(".py") and not f.startswith("__")
        ]

        if not existing:
            return "0001"

        # Extract numbers
        numbers = []
        for filename in existing:
            try:
                num = int(filename.split("_")[0])
                numbers.append(num)
            except (ValueError, IndexError):
                continue

        if not numbers:
            return "0001"

        # Return next number
        next_num = max(numbers) + 1
        return f"{next_num:04d}"


__all__ = [
    "MigrationGenerator",
    "MigrationFile",
    "SQLGenerator",
    "PostgreSQLGenerator",
    "MySQLGenerator",
    "SQLiteGenerator",
]
