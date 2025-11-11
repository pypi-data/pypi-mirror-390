"""
Production-Grade Migration Generator

Generates migration files from schema differences or manual operations.
Provides templates for common migration patterns and ensures SQL correctness
across different database dialects.

Features:
- Template-based migration generation
- Support for all DDL operations (CREATE, ALTER, DROP)
- Multi-database SQL generation (PostgreSQL, MySQL, SQLite)
- Safe operation ordering (handle dependencies)
- Reversible migrations with automatic rollback generation
- Data-preserving operations (e.g., column renames)

Author: CovetPy Team
License: MIT
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .schema_diff import (
    ColumnInfo,
    ForeignKeyInfo,
    IndexInfo,
    SchemaDiff,
    TableSchema,
)

logger = logging.getLogger(__name__)


class SQLGenerator:
    """Generate database-specific SQL statements."""

    def __init__(self, dialect: str):
        """
        Initialize SQL generator.

        Args:
            dialect: Database dialect (postgresql, mysql, sqlite)
        """
        self.dialect = dialect.lower()

    def create_table(self, table: TableSchema) -> str:
        """Generate CREATE TABLE statement."""
        if self.dialect == "postgresql":
            return self._create_table_postgresql(table)
        elif self.dialect == "mysql":
            return self._create_table_mysql(table)
        else:  # sqlite
            return self._create_table_sqlite(table)

    def _create_table_postgresql(self, table: TableSchema) -> str:
        """Generate PostgreSQL CREATE TABLE."""
        lines = [f"CREATE TABLE {table.name} ("]

        col_defs = []
        for col in table.columns.values():
            col_def = f"    {col.name} {self._column_type_postgresql(col)}"

            if col.primary_key:
                col_def += " PRIMARY KEY"
            if not col.nullable and not col.primary_key:
                col_def += " NOT NULL"
            if col.unique and not col.primary_key:
                col_def += " UNIQUE"
            if col.default is not None:
                col_def += f" DEFAULT {self._format_default(col.default)}"

            col_defs.append(col_def)

        lines.append(",\n".join(col_defs))
        lines.append(");")

        return "\n".join(lines)

    def _create_table_mysql(self, table: TableSchema) -> str:
        """Generate MySQL CREATE TABLE."""
        lines = [f"CREATE TABLE `{table.name}` ("]

        col_defs = []
        for col in table.columns.values():
            col_def = f"    `{col.name}` {self._column_type_mysql(col)}"

            if col.auto_increment:
                col_def += " AUTO_INCREMENT"
            if not col.nullable:
                col_def += " NOT NULL"
            if col.default is not None and not col.auto_increment:
                col_def += f" DEFAULT {self._format_default(col.default)}"
            if col.primary_key:
                col_def += " PRIMARY KEY"
            if col.unique and not col.primary_key:
                col_def += " UNIQUE"

            col_defs.append(col_def)

        lines.append(",\n".join(col_defs))
        lines.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")

        return "\n".join(lines)

    def _create_table_sqlite(self, table: TableSchema) -> str:
        """Generate SQLite CREATE TABLE."""
        lines = [f"CREATE TABLE {table.name} ("]

        col_defs = []
        for col in table.columns.values():
            col_def = f"    {col.name} {self._column_type_sqlite(col)}"

            if col.primary_key:
                col_def += " PRIMARY KEY"
                if col.auto_increment:
                    col_def += " AUTOINCREMENT"
            if not col.nullable and not col.primary_key:
                col_def += " NOT NULL"
            if col.unique and not col.primary_key:
                col_def += " UNIQUE"
            if col.default is not None and not col.auto_increment:
                col_def += f" DEFAULT {self._format_default(col.default)}"

            col_defs.append(col_def)

        lines.append(",\n".join(col_defs))
        lines.append(");")

        return "\n".join(lines)

    def drop_table(self, table_name: str) -> str:
        """Generate DROP TABLE statement."""
        if self.dialect == "mysql":
            return f"DROP TABLE IF EXISTS `{table_name}`;"
        else:
            return f"DROP TABLE IF EXISTS {table_name};"

    def rename_table(self, old_name: str, new_name: str) -> str:
        """Generate RENAME TABLE statement."""
        if self.dialect == "postgresql":
            return f"ALTER TABLE {old_name} RENAME TO {new_name};"
        elif self.dialect == "mysql":
            return f"RENAME TABLE `{old_name}` TO `{new_name}`;"
        else:  # sqlite
            return f"ALTER TABLE {old_name} RENAME TO {new_name};"

    def add_column(self, table_name: str, column: ColumnInfo) -> str:
        """Generate ADD COLUMN statement."""
        if self.dialect == "postgresql":
            col_def = f"{column.name} {self._column_type_postgresql(column)}"
        elif self.dialect == "mysql":
            col_def = f"`{column.name}` {self._column_type_mysql(column)}"
        else:  # sqlite
            col_def = f"{column.name} {self._column_type_sqlite(column)}"

        if not column.nullable:
            col_def += " NOT NULL"
        if column.default is not None:
            col_def += f" DEFAULT {self._format_default(column.default)}"

        if self.dialect == "mysql":
            return f"ALTER TABLE `{table_name}` ADD COLUMN {col_def};"
        else:
            return f"ALTER TABLE {table_name} ADD COLUMN {col_def};"

    def drop_column(self, table_name: str, column_name: str) -> str:
        """Generate DROP COLUMN statement."""
        if self.dialect == "mysql":
            return f"ALTER TABLE `{table_name}` DROP COLUMN `{column_name}`;"
        else:
            return f"ALTER TABLE {table_name} DROP COLUMN {column_name};"

    def rename_column(
        self, table_name: str, old_name: str, new_name: str, column: ColumnInfo
    ) -> str:
        """Generate RENAME COLUMN statement."""
        if self.dialect == "postgresql":
            return f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name};"
        elif self.dialect == "mysql":
            col_def = f"`{new_name}` {self._column_type_mysql(column)}"
            return f"ALTER TABLE `{table_name}` CHANGE COLUMN `{old_name}` {col_def};"
        else:  # sqlite - requires table recreation
            return f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name};"

    def alter_column(self, table_name: str, old_col: ColumnInfo, new_col: ColumnInfo) -> str:
        """Generate ALTER COLUMN statement."""
        if self.dialect == "postgresql":
            return self._alter_column_postgresql(table_name, old_col, new_col)
        elif self.dialect == "mysql":
            return self._alter_column_mysql(table_name, new_col)
        else:  # sqlite - limited support
            return f"-- SQLite does not support ALTER COLUMN. Manual migration required."

    def _alter_column_postgresql(
        self, table_name: str, old_col: ColumnInfo, new_col: ColumnInfo
    ) -> str:
        """PostgreSQL column alteration."""
        statements = []

        # Change type if different
        if old_col.data_type != new_col.data_type:
            statements.append(
                f"ALTER TABLE {table_name} ALTER COLUMN {new_col.name} "
                f"TYPE {self._column_type_postgresql(new_col)} "
                f"USING {new_col.name}::{self._column_type_postgresql(new_col)};"
            )

        # Change nullability
        if old_col.nullable != new_col.nullable:
            if new_col.nullable:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {new_col.name} DROP NOT NULL;"
                )
            else:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {new_col.name} SET NOT NULL;"
                )

        # Change default
        if old_col.default != new_col.default:
            if new_col.default is not None:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {new_col.name} "
                    f"SET DEFAULT {self._format_default(new_col.default)};"
                )
            else:
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {new_col.name} DROP DEFAULT;"
                )

        return "\n".join(statements)

    def _alter_column_mysql(self, table_name: str, col: ColumnInfo) -> str:
        """MySQL column modification."""
        col_def = f"`{col.name}` {self._column_type_mysql(col)}"

        if not col.nullable:
            col_def += " NOT NULL"
        if col.default is not None:
            col_def += f" DEFAULT {self._format_default(col.default)}"

        return f"ALTER TABLE `{table_name}` MODIFY COLUMN {col_def};"

    def create_index(self, index: IndexInfo) -> str:
        """Generate CREATE INDEX statement."""
        unique = "UNIQUE " if index.unique else ""
        columns = ", ".join(index.columns)

        if self.dialect == "mysql":
            return f"CREATE {unique}INDEX `{index.name}` ON `{index.table_name}` ({columns});"
        else:
            return f"CREATE {unique}INDEX {index.name} ON {index.table_name} ({columns});"

    def drop_index(self, index: IndexInfo) -> str:
        """Generate DROP INDEX statement."""
        if self.dialect == "postgresql":
            return f"DROP INDEX IF EXISTS {index.name};"
        elif self.dialect == "mysql":
            return f"DROP INDEX `{index.name}` ON `{index.table_name}`;"
        else:  # sqlite
            return f"DROP INDEX IF EXISTS {index.name};"

    def add_foreign_key(self, fk: ForeignKeyInfo) -> str:
        """Generate ADD FOREIGN KEY statement."""
        if self.dialect == "mysql":
            return f"""ALTER TABLE `{fk.from_table}`
    ADD CONSTRAINT `{fk.name}`
    FOREIGN KEY (`{fk.from_column}`)
    REFERENCES `{fk.to_table}` (`{fk.to_column}`)
    ON DELETE {fk.on_delete} ON UPDATE {fk.on_update};"""
        else:
            return f"""ALTER TABLE {fk.from_table}
    ADD CONSTRAINT {fk.name}
    FOREIGN KEY ({fk.from_column})
    REFERENCES {fk.to_table} ({fk.to_column})
    ON DELETE {fk.on_delete} ON UPDATE {fk.on_update};"""

    def drop_foreign_key(self, table_name: str, fk_name: str) -> str:
        """Generate DROP FOREIGN KEY statement."""
        if self.dialect == "mysql":
            return f"ALTER TABLE `{table_name}` DROP FOREIGN KEY `{fk_name}`;"
        else:
            return f"ALTER TABLE {table_name} DROP CONSTRAINT {fk_name};"

    def _column_type_postgresql(self, col: ColumnInfo) -> str:
        """Get PostgreSQL column type."""
        type_map = {
            "VARCHAR": f"VARCHAR({col.max_length or 255})",
            "TEXT": "TEXT",
            "INTEGER": "INTEGER",
            "BIGINT": "BIGINT",
            "SMALLINT": "SMALLINT",
            "FLOAT": "REAL",
            "DECIMAL": f"DECIMAL({col.precision or 10},{col.scale or 2})",
            "BOOLEAN": "BOOLEAN",
            "TIMESTAMP": "TIMESTAMP",
            "DATE": "DATE",
            "TIME": "TIME",
            "JSON": "JSONB",
            "UUID": "UUID",
            "BYTEA": "BYTEA",
        }

        base_type = col.data_type.upper().split("(")[0]
        return type_map.get(base_type, col.data_type)

    def _column_type_mysql(self, col: ColumnInfo) -> str:
        """Get MySQL column type."""
        type_map = {
            "VARCHAR": f"VARCHAR({col.max_length or 255})",
            "TEXT": "TEXT",
            "INTEGER": "INT",
            "BIGINT": "BIGINT",
            "SMALLINT": "SMALLINT",
            "FLOAT": "FLOAT",
            "DECIMAL": f"DECIMAL({col.precision or 10},{col.scale or 2})",
            "BOOLEAN": "TINYINT(1)",
            "TIMESTAMP": "DATETIME",
            "DATE": "DATE",
            "TIME": "TIME",
            "JSON": "JSON",
            "UUID": "CHAR(36)",
            "BYTEA": "BLOB",
        }

        base_type = col.data_type.upper().split("(")[0]
        return type_map.get(base_type, col.data_type)

    def _column_type_sqlite(self, col: ColumnInfo) -> str:
        """Get SQLite column type."""
        type_map = {
            "VARCHAR": "TEXT",
            "TEXT": "TEXT",
            "INTEGER": "INTEGER",
            "BIGINT": "INTEGER",
            "SMALLINT": "INTEGER",
            "FLOAT": "REAL",
            "DECIMAL": "REAL",
            "BOOLEAN": "INTEGER",
            "TIMESTAMP": "TEXT",
            "DATE": "TEXT",
            "TIME": "TEXT",
            "JSON": "TEXT",
            "UUID": "TEXT",
            "BYTEA": "BLOB",
        }

        base_type = col.data_type.upper().split("(")[0]
        return type_map.get(base_type, "TEXT")

    def _format_default(self, value: Any) -> str:
        """Format default value for SQL."""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, str):
            return f"'{value}'"
        else:
            return str(value)


class MigrationGenerator:
    """
    Generate migration files from schema diffs or manual operations.

    This is the primary interface for creating migration files, either
    automatically from detected schema changes or manually from templates.
    """

    def __init__(self, dialect: str, migrations_dir: str = "./migrations"):
        """
        Initialize migration generator.

        Args:
            dialect: Database dialect (postgresql, mysql, sqlite)
            migrations_dir: Directory to save migrations
        """
        self.dialect = dialect.lower()
        self.migrations_dir = Path(migrations_dir)
        self.sql_generator = SQLGenerator(dialect)

        # Create migrations directory
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_diff(self, diff: SchemaDiff, name: str) -> str:
        """
        Generate migration from schema diff.

        Args:
            diff: Schema differences
            name: Migration name

        Returns:
            Path to generated migration file

        Example:
            generator = MigrationGenerator('postgresql')
            filepath = generator.generate_from_diff(diff, 'auto_migration')
        """
        forward_sql = []
        backward_sql = []

        # Order operations for safe execution
        # 1. Drop foreign keys
        for table_name, fks in diff.removed_foreign_keys.items():
            for fk in fks:
                forward_sql.append(self.sql_generator.drop_foreign_key(table_name, fk.name))

        # 2. Drop indexes
        for table_name, indexes in diff.removed_indexes.items():
            for idx in indexes:
                forward_sql.append(self.sql_generator.drop_index(idx))
                backward_sql.insert(0, self.sql_generator.create_index(idx))

        # 3. Drop columns
        for table_name, columns in diff.removed_columns.items():
            for col in columns:
                forward_sql.append(self.sql_generator.drop_column(table_name, col.name))
                backward_sql.insert(0, self.sql_generator.add_column(table_name, col))

        # 4. Drop tables
        for table_name in diff.removed_tables:
            forward_sql.append(self.sql_generator.drop_table(table_name))

        # 5. Create tables
        # Note: We don't have full table schema here, so this is a placeholder
        for table_name in diff.added_tables:
            forward_sql.append(f"-- TODO: CREATE TABLE {table_name}")
            backward_sql.insert(0, self.sql_generator.drop_table(table_name))

        # 6. Rename tables
        for old_name, new_name in diff.renamed_tables:
            forward_sql.append(self.sql_generator.rename_table(old_name, new_name))
            backward_sql.insert(0, self.sql_generator.rename_table(new_name, old_name))

        # 7. Add columns
        for table_name, columns in diff.added_columns.items():
            for col in columns:
                forward_sql.append(self.sql_generator.add_column(table_name, col))
                backward_sql.insert(0, self.sql_generator.drop_column(table_name, col.name))

        # 8. Rename columns
        for table_name, renames in diff.renamed_columns.items():
            for old_name, new_name in renames:
                # We need column info - get from added columns
                col = (
                    diff.added_columns.get(table_name, [None])[0]
                    if table_name in diff.added_columns
                    else None
                )
                if col:
                    forward_sql.append(
                        self.sql_generator.rename_column(table_name, old_name, new_name, col)
                    )
                    backward_sql.insert(
                        0, self.sql_generator.rename_column(table_name, new_name, old_name, col)
                    )

        # 9. Modify columns
        for table_name, modifications in diff.modified_columns.items():
            for old_col, new_col in modifications:
                forward_sql.append(self.sql_generator.alter_column(table_name, old_col, new_col))
                backward_sql.insert(
                    0, self.sql_generator.alter_column(table_name, new_col, old_col)
                )

        # 10. Create indexes
        for table_name, indexes in diff.added_indexes.items():
            for idx in indexes:
                forward_sql.append(self.sql_generator.create_index(idx))
                backward_sql.insert(0, self.sql_generator.drop_index(idx))

        # 11. Add foreign keys
        for table_name, fks in diff.added_foreign_keys.items():
            for fk in fks:
                forward_sql.append(self.sql_generator.add_foreign_key(fk))
                backward_sql.insert(0, self.sql_generator.drop_foreign_key(table_name, fk.name))

        # Generate migration file
        return self._write_migration_file(name, forward_sql, backward_sql)

    def generate_empty(self, name: str) -> str:
        """
        Generate empty migration file for manual editing.

        Args:
            name: Migration name

        Returns:
            Path to generated migration file
        """
        return self._write_migration_file(name, [], [])

    def generate_create_table(self, name: str, table: TableSchema) -> str:
        """Generate migration to create a table."""
        forward_sql = [self.sql_generator.create_table(table)]
        backward_sql = [self.sql_generator.drop_table(table.name)]

        # Add indexes
        for idx in table.indexes:
            forward_sql.append(self.sql_generator.create_index(idx))
            backward_sql.insert(0, self.sql_generator.drop_index(idx))

        return self._write_migration_file(name, forward_sql, backward_sql)

    def generate_add_column(self, name: str, table_name: str, column: ColumnInfo) -> str:
        """Generate migration to add a column."""
        forward_sql = [self.sql_generator.add_column(table_name, column)]
        backward_sql = [self.sql_generator.drop_column(table_name, column.name)]
        return self._write_migration_file(name, forward_sql, backward_sql)

    def generate_add_index(self, name: str, index: IndexInfo) -> str:
        """Generate migration to add an index."""
        forward_sql = [self.sql_generator.create_index(index)]
        backward_sql = [self.sql_generator.drop_index(index)]
        return self._write_migration_file(name, forward_sql, backward_sql)

    def _write_migration_file(
        self,
        name: str,
        forward_sql: List[str],
        backward_sql: List[str],
    ) -> str:
        """Write migration file to disk."""
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        filename = f"{timestamp}_{name}.py"
        filepath = self.migrations_dir / filename

        # Generate class name
        class_name = self._to_class_name(name)

        # Generate file content
        content = f'''"""
Migration: {name}
Created: {datetime.now().isoformat()}
Database: {self.dialect}
"""

from covet.database.migrations.runner import Migration


class {class_name}(Migration):
    """
    Migration: {name}

    Forward operations:
    {self._format_operations_comment(forward_sql)}

    Backward operations:
    {self._format_operations_comment(backward_sql)}
    """

    dependencies = []

    forward_sql = [
{self._format_sql_list(forward_sql)}
    ]

    backward_sql = [
{self._format_sql_list(backward_sql)}
    ]
'''

        # Write file
        with open(filepath, "w") as f:
            f.write(content)

        logger.info(f"Generated migration: {filename}")
        return str(filepath)

    def _to_class_name(self, name: str) -> str:
        """Convert migration name to class name."""
        import re

        words = re.sub(r"[^a-zA-Z0-9]", "_", name).split("_")
        return "".join(word.capitalize() for word in words if word) + "Migration"

    def _format_operations_comment(self, sql_list: List[str]) -> str:
        """Format SQL list as comments."""
        if not sql_list:
            return "    - No operations"

        comments = []
        for sql in sql_list[:5]:  # Show first 5
            comment = sql.split("\n")[0][:60]
            comments.append(f"    - {comment}")

        if len(sql_list) > 5:
            comments.append(f"    - ... and {len(sql_list) - 5} more operations")

        return "\n".join(comments)

    def _format_sql_list(self, sql_list: List[str]) -> str:
        """Format SQL list for Python code."""
        if not sql_list:
            return ""

        formatted = []
        for sql in sql_list:
            # Escape quotes and format as multi-line string
            escaped = sql.replace("'", "\\'").replace('"', '\\"')
            formatted.append(f'        """{escaped}"""')

        return ",\n".join(formatted)


__all__ = [
    "MigrationGenerator",
    "SQLGenerator",
]
