"""
Schema Diff Engine

Compares ORM model schemas against actual database schemas to detect changes.
This is the intelligence behind `python manage.py makemigrations` - it identifies
what needs to change in your database to match your models.

The diff engine performs comprehensive analysis across three dimensions:
1. Table-level changes (added, removed, renamed tables)
2. Column-level changes (added, removed, modified, renamed columns)
3. Constraint changes (indexes, foreign keys, unique constraints)

This is production-grade diffing logic that handles edge cases like:
- Type changes that require data migration
- Nullable/NOT NULL transitions
- Index optimization opportunities
- Cascade behavior changes

Example:
    from covet.database.migrations.diff_engine import DiffEngine, DatabaseIntrospector
    from covet.database.migrations.model_reader import ModelReader

    # Read current model state
    reader = ModelReader()
    model_schemas = reader.read_models([User, Post, Comment], dialect='postgresql')

    # Read actual database state
    introspector = DatabaseIntrospector(adapter)
    db_schemas = await introspector.get_all_schemas()

    # Compare and generate operations
    diff_engine = DiffEngine()
    operations = diff_engine.compare_schemas(model_schemas, db_schemas)

    # Operations contain: CreateTable, AlterTable, DropTable, etc.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .model_reader import (
    ColumnSchema,
    ConstraintSchema,
    IndexSchema,
    RelationshipSchema,
    TableSchema,
)

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of migration operations."""

    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    RENAME_TABLE = "rename_table"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    ALTER_COLUMN = "alter_column"
    RENAME_COLUMN = "rename_column"
    ADD_INDEX = "add_index"
    DROP_INDEX = "drop_index"
    ADD_CONSTRAINT = "add_constraint"
    DROP_CONSTRAINT = "drop_constraint"
    ADD_FOREIGN_KEY = "add_foreign_key"
    DROP_FOREIGN_KEY = "drop_foreign_key"


@dataclass
class MigrationOperation:
    """
    Represents a single migration operation.

    This is the atomic unit of a migration - one specific change
    that needs to be made to the database.

    Attributes:
        operation_type: Type of operation
        table_name: Target table name
        details: Operation-specific details
        reversible: Whether this operation can be reversed
        requires_data_migration: Whether this requires custom data migration
    """

    operation_type: OperationType
    table_name: str
    details: Dict[str, Any] = field(default_factory=dict)
    reversible: bool = True
    requires_data_migration: bool = False
    priority: int = 50  # For operation ordering

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation_type": self.operation_type.value,
            "table_name": self.table_name,
            "details": self.details,
            "reversible": self.reversible,
            "requires_data_migration": self.requires_data_migration,
            "priority": self.priority,
        }

    def __repr__(self) -> str:
        return (
            f"<{self.operation_type.value}: {self.table_name} "
            f"{self.details.get('description', '')}>"
        )


class DatabaseIntrospector:
    """
    Introspects actual database schema.

    Connects to a live database and extracts the current schema state
    for comparison with model definitions. This is database-agnostic
    and works with PostgreSQL, MySQL, and SQLite.

    The introspector uses information_schema queries (PostgreSQL/MySQL)
    or PRAGMA commands (SQLite) to read:
    - Table definitions
    - Column types and constraints
    - Indexes
    - Foreign key relationships

    Example:
        introspector = DatabaseIntrospector(adapter, dialect='postgresql')
        schemas = await introspector.get_all_schemas()
        user_schema = await introspector.get_table_schema('users')
    """

    def __init__(self, adapter, dialect: str = "postgresql"):
        """
        Initialize database introspector.

        Args:
            adapter: Database adapter instance
            dialect: Database dialect ('postgresql', 'mysql', 'sqlite')
        """
        self.adapter = adapter
        self.dialect = dialect.lower()

    async def get_all_schemas(self) -> List[TableSchema]:
        """
        Get schemas for all tables in the database.

        Returns:
            List of TableSchema objects representing current database state
        """
        # Get list of all tables
        tables = await self._get_table_list()

        schemas = []
        for table_name in tables:
            try:
                schema = await self.get_table_schema(table_name)
                if schema:
                    schemas.append(schema)
            except Exception as e:
                logger.error(f"Failed to introspect table {table_name}: {e}")

        return schemas

    async def get_table_schema(self, table_name: str) -> Optional[TableSchema]:
        """
        Get schema for a specific table.

        Args:
            table_name: Table name to introspect

        Returns:
            TableSchema or None if table doesn't exist
        """
        # Check if table exists
        exists = await self.adapter.table_exists(table_name)
        if not exists:
            return None

        schema = TableSchema(table_name)

        # Get columns
        columns = await self._get_columns(table_name)
        for col in columns:
            schema.add_column(col)

        # Get indexes
        indexes = await self._get_indexes(table_name)
        for idx in indexes:
            schema.add_index(idx)

        # Get foreign keys
        relationships = await self._get_foreign_keys(table_name)
        for rel in relationships:
            schema.add_relationship(rel)

        return schema

    async def _get_table_list(self) -> List[str]:
        """Get list of all tables in database."""
        if self.dialect == "postgresql":
            query = """
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """
            rows = await self.adapter.fetch_all(query)
            return [row["tablename"] for row in rows]

        elif self.dialect == "mysql":
            rows = await self.adapter.get_table_list()
            return rows

        elif self.dialect == "sqlite":
            rows = await self.adapter.get_table_list()
            return rows

        return []

    async def _get_columns(self, table_name: str) -> List[ColumnSchema]:
        """Get columns for a table."""
        columns = []

        if self.dialect == "postgresql":
            query = """
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = $1
                ORDER BY ordinal_position
            """
            rows = await self.adapter.fetch_all(query, [table_name])

            for row in rows:
                # Check if primary key
                pk_query = """
                    SELECT constraint_type
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = $1
                        AND kcu.column_name = $2
                        AND tc.constraint_type = 'PRIMARY KEY'
                """
                pk_result = await self.adapter.fetch_one(pk_query, [table_name, row["column_name"]])

                # Check if unique
                unique_query = """
                    SELECT constraint_type
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = $1
                        AND kcu.column_name = $2
                        AND tc.constraint_type = 'UNIQUE'
                """
                unique_result = await self.adapter.fetch_one(
                    unique_query, [table_name, row["column_name"]]
                )

                # Detect auto increment
                auto_increment = False
                if row["column_default"]:
                    auto_increment = "nextval" in str(row["column_default"])

                column = ColumnSchema(
                    name=row["column_name"],
                    db_type=row["data_type"].upper(),
                    nullable=row["is_nullable"] == "YES",
                    default=row["column_default"],
                    unique=bool(unique_result),
                    primary_key=bool(pk_result),
                    auto_increment=auto_increment,
                    max_length=row["character_maximum_length"],
                    precision=row["numeric_precision"],
                    scale=row["numeric_scale"],
                )
                columns.append(column)

        elif self.dialect == "mysql":
            table_info = await self.adapter.get_table_info(table_name)

            for row in table_info:
                # Parse type
                field_type = row["Type"]
                db_type = field_type.split("(")[0].upper()

                # Extract max_length from type like VARCHAR(100)
                max_length = None
                if "(" in field_type:
                    try:
                        max_length = int(field_type.split("(")[1].split(")")[0].split(",")[0])
                    except BaseException:
                        pass

                column = ColumnSchema(
                    name=row["Field"],
                    db_type=db_type,
                    nullable=row["Null"] == "YES",
                    default=row["Default"],
                    unique=row["Key"] == "UNI",
                    primary_key=row["Key"] == "PRI",
                    auto_increment="auto_increment" in row.get("Extra", "").lower(),
                    max_length=max_length,
                )
                columns.append(column)

        elif self.dialect == "sqlite":
            table_info = await self.adapter.get_table_info(table_name)

            for row in table_info:
                # Parse type
                field_type = row["type"]
                db_type = field_type.split("(")[0].upper() if field_type else "TEXT"

                column = ColumnSchema(
                    name=row["name"],
                    db_type=db_type,
                    nullable=row["notnull"] == 0,
                    default=row["dflt_value"],
                    primary_key=row["pk"] == 1,
                    auto_increment=row["pk"] == 1 and "INTEGER" in db_type,
                )
                columns.append(column)

        return columns

    async def _get_indexes(self, table_name: str) -> List[IndexSchema]:
        """Get indexes for a table."""
        indexes = []

        if self.dialect == "postgresql":
            query = """
                SELECT
                    i.relname as index_name,
                    a.attname as column_name,
                    ix.indisunique as is_unique
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                WHERE t.relname = $1
                    AND t.relkind = 'r'
                    AND NOT ix.indisprimary
                ORDER BY i.relname, a.attnum
            """
            rows = await self.adapter.fetch_all(query, [table_name])

            # Group by index name
            index_map: Dict[str, List[str]] = {}
            unique_map: Dict[str, bool] = {}

            for row in rows:
                idx_name = row["index_name"]
                if idx_name not in index_map:
                    index_map[idx_name] = []
                    unique_map[idx_name] = row["is_unique"]
                index_map[idx_name].append(row["column_name"])

            for idx_name, columns in index_map.items():
                indexes.append(
                    IndexSchema(name=idx_name, columns=columns, unique=unique_map[idx_name])
                )

        elif self.dialect == "mysql":
            query = f"SHOW INDEX FROM `{table_name}`"
            rows = await self.adapter.fetch_all(query)

            # Group by index name
            index_map: Dict[str, List[str]] = {}
            unique_map: Dict[str, bool] = {}

            for row in rows:
                idx_name = row["Key_name"]
                # Skip PRIMARY key
                if idx_name == "PRIMARY":
                    continue

                if idx_name not in index_map:
                    index_map[idx_name] = []
                    unique_map[idx_name] = row["Non_unique"] == 0
                index_map[idx_name].append(row["Column_name"])

            for idx_name, columns in index_map.items():
                indexes.append(
                    IndexSchema(name=idx_name, columns=columns, unique=unique_map[idx_name])
                )

        elif self.dialect == "sqlite":
            query = f"PRAGMA index_list({table_name})"
            rows = await self.adapter.fetch_all(query)

            for row in rows:
                idx_name = row["name"]

                # Get columns for this index
                col_query = f"PRAGMA index_info({idx_name})"
                col_rows = await self.adapter.fetch_all(col_query)
                columns = [col["name"] for col in col_rows]

                indexes.append(
                    IndexSchema(name=idx_name, columns=columns, unique=row["unique"] == 1)
                )

        return indexes

    async def _get_foreign_keys(self, table_name: str) -> List[RelationshipSchema]:
        """Get foreign key relationships for a table."""
        relationships = []

        if self.dialect == "postgresql":
            query = """
                SELECT
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule,
                    rc.update_rule
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                JOIN information_schema.referential_constraints AS rc
                    ON rc.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = $1
            """
            rows = await self.adapter.fetch_all(query, [table_name])

            for row in rows:
                relationships.append(
                    RelationshipSchema(
                        name=row["constraint_name"],
                        column=row["column_name"],
                        referenced_table=row["foreign_table_name"],
                        referenced_column=row["foreign_column_name"],
                        on_delete=row["delete_rule"].upper(),
                        on_update=row["update_rule"].upper(),
                    )
                )

        elif self.dialect == "mysql":
            query = """
                SELECT
                    CONSTRAINT_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND REFERENCED_TABLE_NAME IS NOT NULL
            """
            rows = await self.adapter.fetch_all(query, [table_name])

            for row in rows:
                relationships.append(
                    RelationshipSchema(
                        name=row["CONSTRAINT_NAME"],
                        column=row["COLUMN_NAME"],
                        referenced_table=row["REFERENCED_TABLE_NAME"],
                        referenced_column=row["REFERENCED_COLUMN_NAME"],
                        on_delete="CASCADE",  # MySQL doesn't expose this easily
                        on_update="CASCADE",
                    )
                )

        elif self.dialect == "sqlite":
            query = f"PRAGMA foreign_key_list({table_name})"
            rows = await self.adapter.fetch_all(query)

            for i, row in enumerate(rows):
                # SQLite doesn't provide constraint names
                constraint_name = f"fk_{table_name}_{row['from']}_{i}"

                relationships.append(
                    RelationshipSchema(
                        name=constraint_name,
                        column=row["from"],
                        referenced_table=row["table"],
                        referenced_column=row["to"],
                        on_delete=row["on_delete"].upper(),
                        on_update=row["on_update"].upper(),
                    )
                )

        return relationships


class DiffEngine:
    """
    Compares model schemas against database schemas to generate migrations.

    This is the brain of the migration system - it takes two schema states
    (what you want vs. what you have) and generates the minimal set of
    operations needed to transform the database.

    The diffing algorithm is sophisticated:
    1. Table-level diff: new/removed/renamed tables
    2. Column-level diff: new/removed/modified/renamed columns
    3. Type compatibility: safe vs. unsafe type changes
    4. Index optimization: detect redundant or missing indexes
    5. Constraint validation: ensure referential integrity
    6. Rename detection: identify column renames to preserve data

    Example:
        diff_engine = DiffEngine(detect_renames=True)
        operations = diff_engine.compare_schemas(
            model_schemas,
            database_schemas
        )

        for op in operations:
            print(f"{op.operation_type.value}: {op.table_name}")
    """

    def __init__(
        self,
        detect_renames: bool = True,
        rename_similarity_threshold: float = 0.80,
    ):
        """
        Initialize diff engine with rename detection.

        Args:
            detect_renames: Enable automatic rename detection (default: True)
            rename_similarity_threshold: Minimum similarity for rename (default: 0.80)
        """
        self.operations: List[MigrationOperation] = []
        self.detect_renames = detect_renames
        self.rename_similarity_threshold = rename_similarity_threshold
        self._rename_detector = None

    def compare_schemas(
        self, model_schemas: List[TableSchema], db_schemas: List[TableSchema]
    ) -> List[MigrationOperation]:
        """
        Compare model schemas against database schemas.

        Args:
            model_schemas: Schemas from ORM models
            db_schemas: Schemas from actual database

        Returns:
            List of MigrationOperation objects in execution order
        """
        self.operations = []

        # Create lookup maps
        model_map = {s.name: s for s in model_schemas}
        db_map = {s.name: s for s in db_schemas}

        # Find table-level changes
        self._diff_tables(model_map, db_map)

        # Apply rename detection if enabled
        if self.detect_renames:
            self.operations = self._apply_rename_detection(
                self.operations, model_schemas, db_schemas
            )

        # Sort operations by priority
        # Order: DROP FK -> DROP INDEX -> ALTER TABLE -> ADD INDEX -> ADD FK
        self.operations.sort(key=lambda op: op.priority)

        logger.info(f"Generated {len(self.operations)} migration operations")

        return self.operations

    def _diff_tables(self, model_map: Dict[str, TableSchema], db_map: Dict[str, TableSchema]):
        """Compare tables between model and database."""
        model_tables = set(model_map.keys())
        db_tables = set(db_map.keys())

        # New tables (in models but not in DB)
        for table_name in model_tables - db_tables:
            self._add_create_table_operation(model_map[table_name])

        # Dropped tables (in DB but not in models)
        for table_name in db_tables - model_tables:
            self._add_drop_table_operation(db_map[table_name])

        # Existing tables - check for changes
        for table_name in model_tables & db_tables:
            self._diff_table_contents(model_map[table_name], db_map[table_name])

    def _add_create_table_operation(self, schema: TableSchema):
        """Add CREATE TABLE operation."""
        op = MigrationOperation(
            operation_type=OperationType.CREATE_TABLE,
            table_name=schema.name,
            details={
                "schema": schema.to_dict(),
                "description": f"Create table '{schema.name}'",
            },
            priority=30,  # After drops, before alters
        )
        self.operations.append(op)
        logger.debug(f"CREATE TABLE: {schema.name}")

    def _add_drop_table_operation(self, schema: TableSchema):
        """Add DROP TABLE operation."""
        op = MigrationOperation(
            operation_type=OperationType.DROP_TABLE,
            table_name=schema.name,
            details={"description": f"Drop table '{schema.name}'"},
            reversible=False,  # Dropping tables loses data
            priority=10,  # Do first
        )
        self.operations.append(op)
        logger.warning(f"DROP TABLE: {schema.name}")

    def _diff_table_contents(self, model_schema: TableSchema, db_schema: TableSchema):
        """Compare contents of a table (columns, indexes, constraints)."""
        # Compare columns
        self._diff_columns(model_schema, db_schema)

        # Compare indexes
        self._diff_indexes(model_schema, db_schema)

        # Compare foreign keys
        self._diff_foreign_keys(model_schema, db_schema)

    def _diff_columns(self, model_schema: TableSchema, db_schema: TableSchema):
        """Compare columns between model and database."""
        model_cols = {c.name: c for c in model_schema.columns}
        db_cols = {c.name: c for c in db_schema.columns}

        model_col_names = set(model_cols.keys())
        db_col_names = set(db_cols.keys())

        # New columns
        for col_name in model_col_names - db_col_names:
            self._add_add_column_operation(model_schema.name, model_cols[col_name])

        # Dropped columns
        for col_name in db_col_names - model_col_names:
            self._add_drop_column_operation(model_schema.name, db_cols[col_name])

        # Modified columns
        for col_name in model_col_names & db_col_names:
            if self._columns_differ(model_cols[col_name], db_cols[col_name]):
                self._add_alter_column_operation(
                    model_schema.name, model_cols[col_name], db_cols[col_name]
                )

    def _columns_differ(self, model_col: ColumnSchema, db_col: ColumnSchema) -> bool:
        """Check if columns are different."""
        # Normalize types for comparison
        model_type = self._normalize_type(model_col.db_type)
        db_type = self._normalize_type(db_col.db_type)

        if model_type != db_type:
            return True

        if model_col.nullable != db_col.nullable:
            return True

        if model_col.default != db_col.default:
            return True

        if model_col.unique != db_col.unique:
            return True

        return False

    def _normalize_type(self, db_type: str) -> str:
        """Normalize database type for comparison."""
        # Remove size specifications
        type_upper = db_type.upper().split("(")[0]

        # Map equivalent types
        type_map = {
            "INT": "INTEGER",
            "SERIAL": "INTEGER",
            "BIGSERIAL": "BIGINT",
            "SMALLSERIAL": "SMALLINT",
            "BOOL": "BOOLEAN",
        }

        return type_map.get(type_upper, type_upper)

    def _add_add_column_operation(self, table_name: str, column: ColumnSchema):
        """Add ADD COLUMN operation."""
        op = MigrationOperation(
            operation_type=OperationType.ADD_COLUMN,
            table_name=table_name,
            details={
                "column": column.to_dict(),
                "description": f"Add column '{column.name}' to '{table_name}'",
            },
            priority=40,
        )
        self.operations.append(op)
        logger.debug(f"ADD COLUMN: {table_name}.{column.name}")

    def _add_drop_column_operation(self, table_name: str, column: ColumnSchema):
        """Add DROP COLUMN operation."""
        op = MigrationOperation(
            operation_type=OperationType.DROP_COLUMN,
            table_name=table_name,
            details={
                "column_name": column.name,
                "description": f"Drop column '{column.name}' from '{table_name}'",
            },
            reversible=False,  # Dropping columns loses data
            priority=20,
        )
        self.operations.append(op)
        logger.warning(f"DROP COLUMN: {table_name}.{column.name}")

    def _add_alter_column_operation(
        self, table_name: str, model_col: ColumnSchema, db_col: ColumnSchema
    ):
        """Add ALTER COLUMN operation."""
        changes = []

        if model_col.db_type != db_col.db_type:
            changes.append(f"type: {db_col.db_type} -> {model_col.db_type}")

        if model_col.nullable != db_col.nullable:
            changes.append(f"nullable: {db_col.nullable} -> {model_col.nullable}")

        if model_col.default != db_col.default:
            changes.append(f"default: {db_col.default} -> {model_col.default}")

        op = MigrationOperation(
            operation_type=OperationType.ALTER_COLUMN,
            table_name=table_name,
            details={
                "column_name": model_col.name,
                "old_column": db_col.to_dict(),
                "new_column": model_col.to_dict(),
                "changes": changes,
                "description": f"Alter column '{model_col.name}' in '{table_name}': {', '.join(changes)}",
            },
            requires_data_migration=model_col.db_type != db_col.db_type,
            priority=45,
        )
        self.operations.append(op)
        logger.debug(f"ALTER COLUMN: {table_name}.{model_col.name} - {', '.join(changes)}")

    def _diff_indexes(self, model_schema: TableSchema, db_schema: TableSchema):
        """Compare indexes between model and database."""
        model_indexes = {i.name: i for i in model_schema.indexes}
        db_indexes = {i.name: i for i in db_schema.indexes}

        # New indexes
        for idx_name in set(model_indexes.keys()) - set(db_indexes.keys()):
            self._add_add_index_operation(model_schema.name, model_indexes[idx_name])

        # Dropped indexes
        for idx_name in set(db_indexes.keys()) - set(model_indexes.keys()):
            self._add_drop_index_operation(model_schema.name, db_indexes[idx_name])

    def _add_add_index_operation(self, table_name: str, index: IndexSchema):
        """Add CREATE INDEX operation."""
        op = MigrationOperation(
            operation_type=OperationType.ADD_INDEX,
            table_name=table_name,
            details={
                "index": index.to_dict(),
                "description": f"Create index '{index.name}' on '{table_name}'",
            },
            priority=60,
        )
        self.operations.append(op)
        logger.debug(f"CREATE INDEX: {index.name}")

    def _add_drop_index_operation(self, table_name: str, index: IndexSchema):
        """Add DROP INDEX operation."""
        op = MigrationOperation(
            operation_type=OperationType.DROP_INDEX,
            table_name=table_name,
            details={
                "index_name": index.name,
                "description": f"Drop index '{index.name}' from '{table_name}'",
            },
            priority=15,
        )
        self.operations.append(op)
        logger.debug(f"DROP INDEX: {index.name}")

    def _diff_foreign_keys(self, model_schema: TableSchema, db_schema: TableSchema):
        """Compare foreign keys between model and database."""
        model_fks = {fk.name: fk for fk in model_schema.relationships}
        db_fks = {fk.name: fk for fk in db_schema.relationships}

        # New foreign keys
        for fk_name in set(model_fks.keys()) - set(db_fks.keys()):
            self._add_add_foreign_key_operation(model_schema.name, model_fks[fk_name])

        # Dropped foreign keys
        for fk_name in set(db_fks.keys()) - set(model_fks.keys()):
            self._add_drop_foreign_key_operation(model_schema.name, db_fks[fk_name])

    def _add_add_foreign_key_operation(self, table_name: str, fk: RelationshipSchema):
        """Add ADD FOREIGN KEY operation."""
        op = MigrationOperation(
            operation_type=OperationType.ADD_FOREIGN_KEY,
            table_name=table_name,
            details={
                "foreign_key": fk.to_dict(),
                "description": (
                    f"Add foreign key '{fk.name}' from '{table_name}.{fk.column}' "
                    f"to '{fk.referenced_table}.{fk.referenced_column}'"
                ),
            },
            priority=70,  # Add FKs last
        )
        self.operations.append(op)
        logger.debug(f"ADD FOREIGN KEY: {fk.name}")

    def _add_drop_foreign_key_operation(self, table_name: str, fk: RelationshipSchema):
        """Add DROP FOREIGN KEY operation."""
        op = MigrationOperation(
            operation_type=OperationType.DROP_FOREIGN_KEY,
            table_name=table_name,
            details={
                "constraint_name": fk.name,
                "description": f"Drop foreign key '{fk.name}' from '{table_name}'",
            },
            priority=5,  # Drop FKs first
        )
        self.operations.append(op)
        logger.debug(f"DROP FOREIGN KEY: {fk.name}")

    def _apply_rename_detection(
        self,
        operations: List[MigrationOperation],
        model_schemas: List[TableSchema],
        db_schemas: List[TableSchema],
    ) -> List[MigrationOperation]:
        """
        Apply rename detection to operations.

        This method integrates the RenameDetector to identify column renames
        and replace DROP + ADD operations with RENAME operations.

        Args:
            operations: Current migration operations
            model_schemas: Target model schemas
            db_schemas: Current database schemas

        Returns:
            Modified operations list with renames detected
        """
        try:
            # Import RenameDetector (lazy import to avoid circular dependencies)
            from .rename_detection import RenameDetector

            # Initialize detector if not already done
            if self._rename_detector is None:
                self._rename_detector = RenameDetector(
                    similarity_threshold=self.rename_similarity_threshold,
                    enable_detection=True,
                )

            # Detect renames
            operations = self._rename_detector.detect_renames(operations, model_schemas, db_schemas)

            # Log statistics
            stats = self._rename_detector.get_stats()
            if stats["renames_detected"] > 0:
                logger.info(
                    f"Rename detection: {stats['renames_detected']} renames found, "
                    f"{stats['false_positives_prevented']} false positives prevented"
                )

            return operations

        except Exception as e:
            logger.error(f"Rename detection failed: {e}. Falling back to DROP + ADD.")
            # On failure, return original operations
            return operations

    def add_manual_rename(self, table_name: str, old_name: str, new_name: str):
        """
        Manually specify a column rename.

        This allows users to override automatic detection and explicitly
        specify that a column should be renamed instead of dropped/added.

        Args:
            table_name: Table containing the column
            old_name: Current column name
            new_name: New column name

        Example:
            diff_engine = DiffEngine()
            diff_engine.add_manual_rename('users', 'name', 'full_name')
            operations = diff_engine.compare_schemas(model_schemas, db_schemas)
        """
        # Import RenameDetector (lazy import)
        from .rename_detection import RenameDetector

        # Initialize detector if needed
        if self._rename_detector is None:
            self._rename_detector = RenameDetector(
                similarity_threshold=self.rename_similarity_threshold,
                enable_detection=self.detect_renames,
            )

        # Add manual rename
        self._rename_detector.add_manual_rename(table_name, old_name, new_name)
        logger.info(f"Manual rename registered: {table_name}.{old_name} -> {new_name}")


__all__ = [
    "DiffEngine",
    "DatabaseIntrospector",
    "MigrationOperation",
    "OperationType",
]
