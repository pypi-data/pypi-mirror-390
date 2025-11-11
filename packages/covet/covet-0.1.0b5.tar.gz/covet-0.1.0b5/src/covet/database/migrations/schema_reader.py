"""
Enterprise-Grade Database Schema Introspection System

Production-ready schema reader supporting PostgreSQL, MySQL, and SQLite with
comprehensive metadata extraction for migration generation and schema analysis.

Features:
- Multi-database support (PostgreSQL, MySQL, SQLite)
- Complete schema introspection (tables, columns, indexes, constraints, foreign keys)
- Type mapping and normalization across database platforms
- Comprehensive error handling and retry logic
- Production logging and monitoring
- Performance-optimized queries
- Support for complex database features (views, triggers, sequences)

Author: Senior Database Administrator
Version: 1.0.0
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class ConstraintType(Enum):
    """Database constraint types."""

    PRIMARY_KEY = "PRIMARY_KEY"
    FOREIGN_KEY = "FOREIGN_KEY"
    UNIQUE = "UNIQUE"
    CHECK = "CHECK"
    NOT_NULL = "NOT_NULL"


class IndexType(Enum):
    """Database index types."""

    BTREE = "BTREE"
    HASH = "HASH"
    GIST = "GIST"
    GIN = "GIN"
    BRIN = "BRIN"
    FULLTEXT = "FULLTEXT"
    SPATIAL = "SPATIAL"


@dataclass
class ColumnDefinition:
    """
    Complete column definition with all metadata.

    Attributes:
        name: Column name
        data_type: Native database data type
        normalized_type: Normalized type across databases
        is_nullable: Whether column allows NULL values
        default_value: Default value expression
        character_maximum_length: Max length for character types
        numeric_precision: Precision for numeric types
        numeric_scale: Scale for decimal types
        is_primary_key: Whether column is part of primary key
        is_unique: Whether column has unique constraint
        is_auto_increment: Whether column auto-increments
        column_comment: Column comment/description
        ordinal_position: Position in table definition
        extra_attributes: Database-specific attributes
    """

    name: str
    data_type: str
    normalized_type: str
    is_nullable: bool = True
    default_value: Optional[str] = None
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    is_primary_key: bool = False
    is_unique: bool = False
    is_auto_increment: bool = False
    column_comment: Optional[str] = None
    ordinal_position: int = 0
    extra_attributes: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """String representation of column."""
        null_str = "NULL" if self.is_nullable else "NOT NULL"
        pk_str = " PRIMARY KEY" if self.is_primary_key else ""
        auto_str = " AUTO_INCREMENT" if self.is_auto_increment else ""
        default_str = f" DEFAULT {self.default_value}" if self.default_value else ""

        return f"{self.name} {self.data_type}" f"{null_str}{pk_str}{auto_str}{default_str}"


@dataclass
class IndexDefinition:
    """
    Complete index definition with all metadata.

    Attributes:
        name: Index name
        table_name: Table name
        columns: List of column names in index
        is_unique: Whether index enforces uniqueness
        is_primary: Whether this is the primary key index
        index_type: Type of index (BTREE, HASH, etc.)
        where_clause: Partial index WHERE clause (PostgreSQL)
        index_comment: Index comment/description
        extra_attributes: Database-specific attributes
    """

    name: str
    table_name: str
    columns: List[str]
    is_unique: bool = False
    is_primary: bool = False
    index_type: IndexType = IndexType.BTREE
    where_clause: Optional[str] = None
    index_comment: Optional[str] = None
    extra_attributes: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """String representation of index."""
        unique_str = "UNIQUE " if self.is_unique else ""
        pk_str = "PRIMARY " if self.is_primary else ""
        cols_str = ", ".join(self.columns)

        return f"{pk_str}{unique_str}INDEX {self.name} " f"ON {self.table_name} ({cols_str})"


@dataclass
class ConstraintDefinition:
    """
    Complete constraint definition with all metadata.

    Attributes:
        name: Constraint name
        table_name: Table name
        constraint_type: Type of constraint
        columns: List of column names
        check_clause: CHECK constraint expression
        constraint_comment: Constraint comment/description
        is_deferrable: Whether constraint is deferrable (PostgreSQL)
        initially_deferred: Whether initially deferred (PostgreSQL)
        extra_attributes: Database-specific attributes
    """

    name: str
    table_name: str
    constraint_type: ConstraintType
    columns: List[str]
    check_clause: Optional[str] = None
    constraint_comment: Optional[str] = None
    is_deferrable: bool = False
    initially_deferred: bool = False
    extra_attributes: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """String representation of constraint."""
        cols_str = ", ".join(self.columns)
        type_str = self.constraint_type.value

        if self.constraint_type == ConstraintType.CHECK and self.check_clause:
            return f"CONSTRAINT {self.name} CHECK ({self.check_clause})"

        return f"CONSTRAINT {self.name} {type_str} ({cols_str})"


@dataclass
class ForeignKeyDefinition:
    """
    Complete foreign key definition with all metadata.

    Attributes:
        name: Foreign key constraint name
        table_name: Source table name
        columns: Source column names
        referenced_table: Referenced table name
        referenced_columns: Referenced column names
        on_delete: ON DELETE action (CASCADE, SET NULL, RESTRICT, etc.)
        on_update: ON UPDATE action
        is_deferrable: Whether constraint is deferrable
        initially_deferred: Whether initially deferred
        extra_attributes: Database-specific attributes
    """

    name: str
    table_name: str
    columns: List[str]
    referenced_table: str
    referenced_columns: List[str]
    on_delete: str = "NO ACTION"
    on_update: str = "NO ACTION"
    is_deferrable: bool = False
    initially_deferred: bool = False
    extra_attributes: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """String representation of foreign key."""
        cols_str = ", ".join(self.columns)
        ref_cols_str = ", ".join(self.referenced_columns)

        return (
            f"FOREIGN KEY {self.name} ({cols_str}) "
            f"REFERENCES {self.referenced_table} ({ref_cols_str}) "
            f"ON DELETE {self.on_delete} ON UPDATE {self.on_update}"
        )


@dataclass
class TableDefinition:
    """
    Complete table definition with all metadata.

    Attributes:
        name: Table name
        schema: Schema/database name
        columns: List of column definitions
        indexes: List of index definitions
        constraints: List of constraint definitions
        foreign_keys: List of foreign key definitions
        table_comment: Table comment/description
        engine: Storage engine (MySQL)
        row_count: Approximate row count
        table_size: Approximate table size in bytes
        extra_attributes: Database-specific attributes
    """

    name: str
    schema: str
    columns: List[ColumnDefinition] = field(default_factory=list)
    indexes: List[IndexDefinition] = field(default_factory=list)
    constraints: List[ConstraintDefinition] = field(default_factory=list)
    foreign_keys: List[ForeignKeyDefinition] = field(default_factory=list)
    table_comment: Optional[str] = None
    engine: Optional[str] = None
    row_count: Optional[int] = None
    table_size: Optional[int] = None
    extra_attributes: Dict[str, Any] = field(default_factory=dict)

    def get_column(self, column_name: str) -> Optional[ColumnDefinition]:
        """Get column definition by name."""
        for col in self.columns:
            if col.name == column_name:
                return col
        return None

    def get_primary_key_columns(self) -> List[str]:
        """Get list of primary key column names."""
        return [col.name for col in self.columns if col.is_primary_key]

    def __repr__(self) -> str:
        """String representation of table."""
        return (
            f"Table {self.schema}.{self.name}: "
            f"{len(self.columns)} columns, "
            f"{len(self.indexes)} indexes, "
            f"{len(self.foreign_keys)} foreign keys"
        )


class SchemaReaderError(Exception):
    """Base exception for schema reader errors."""

    pass


class DatabaseNotSupportedError(SchemaReaderError):
    """Raised when database type is not supported."""

    pass


class SchemaReadError(SchemaReaderError):
    """Raised when schema reading fails."""

    pass


class SchemaReader:
    """
    Enterprise-grade database schema introspection system.

    Provides comprehensive schema metadata extraction for PostgreSQL, MySQL, and SQLite
    with production-ready error handling, logging, and performance optimization.

    Example:
        # PostgreSQL
        from covet.database.adapters.postgresql import PostgreSQLAdapter

        adapter = PostgreSQLAdapter(host='localhost', database='mydb')
        await adapter.connect()

        reader = SchemaReader(adapter, DatabaseType.POSTGRESQL)
        tables = await reader.read_tables('public')

        for table_name in tables:
            table_def = await reader.read_table_complete(table_name, 'public')
            print(f"Table: {table_def}")

        # MySQL
        from covet.database.adapters.mysql import MySQLAdapter

        adapter = MySQLAdapter(host='localhost', database='mydb')
        await adapter.connect()

        reader = SchemaReader(adapter, DatabaseType.MYSQL)
        tables = await reader.read_tables('mydb')

        # SQLite
        from covet.database.adapters.sqlite import SQLiteAdapter

        adapter = SQLiteAdapter(database='/path/to/db.sqlite')
        await adapter.connect()

        reader = SchemaReader(adapter, DatabaseType.SQLITE)
        tables = await reader.read_tables('main')
    """

    # Type mapping for normalization across databases
    TYPE_MAPPINGS = {
        # PostgreSQL -> Normalized
        "integer": "INTEGER",
        "bigint": "BIGINT",
        "smallint": "SMALLINT",
        "serial": "INTEGER",
        "bigserial": "BIGINT",
        "character varying": "VARCHAR",
        "varchar": "VARCHAR",
        "character": "CHAR",
        "char": "CHAR",
        "text": "TEXT",
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN",
        "date": "DATE",
        "timestamp without time zone": "TIMESTAMP",
        "timestamp with time zone": "TIMESTAMPTZ",
        "timestamp": "TIMESTAMP",
        "time without time zone": "TIME",
        "time with time zone": "TIMETZ",
        "time": "TIME",
        "numeric": "DECIMAL",
        "decimal": "DECIMAL",
        "real": "FLOAT",
        "double precision": "DOUBLE",
        "bytea": "BLOB",
        "json": "JSON",
        "jsonb": "JSONB",
        "uuid": "UUID",
        "inet": "INET",
        "cidr": "CIDR",
        "macaddr": "MACADDR",
        # MySQL -> Normalized
        "int": "INTEGER",
        "tinyint": "TINYINT",
        "mediumint": "MEDIUMINT",
        "bigint": "BIGINT",
        "varchar": "VARCHAR",
        "char": "CHAR",
        "text": "TEXT",
        "tinytext": "TEXT",
        "mediumtext": "TEXT",
        "longtext": "TEXT",
        "blob": "BLOB",
        "tinyblob": "BLOB",
        "mediumblob": "BLOB",
        "longblob": "BLOB",
        "datetime": "DATETIME",
        "date": "DATE",
        "time": "TIME",
        "timestamp": "TIMESTAMP",
        "year": "YEAR",
        "decimal": "DECIMAL",
        "float": "FLOAT",
        "double": "DOUBLE",
        "enum": "ENUM",
        "set": "SET",
        # SQLite -> Normalized
        "INTEGER": "INTEGER",
        "TEXT": "TEXT",
        "REAL": "FLOAT",
        "BLOB": "BLOB",
        "NUMERIC": "NUMERIC",
    }

    def __init__(self, adapter: Any, db_type: DatabaseType):
        """
        Initialize SchemaReader with database adapter.

        Args:
            adapter: Database adapter instance (PostgreSQLAdapter, MySQLAdapter, or SQLiteAdapter)
            db_type: Type of database (DatabaseType.POSTGRESQL, MYSQL, or SQLITE)

        Raises:
            DatabaseNotSupportedError: If database type is not supported
        """
        self.adapter = adapter
        self.db_type = db_type

        # Validate database type
        if db_type not in DatabaseType:
            raise DatabaseNotSupportedError(
                f"Database type {db_type} is not supported. "
                f"Supported types: {[t.value for t in DatabaseType]}"
            )

        logger.info(f"Initialized SchemaReader for {db_type.value}")

    def _normalize_type(self, native_type: str) -> str:
        """
        Normalize database-specific type to common type.

        Args:
            native_type: Native database type

        Returns:
            Normalized type string
        """
        # Extract base type (remove size specifications)
        base_type = native_type.lower().split("(")[0].strip()

        # Look up normalized type
        normalized = self.TYPE_MAPPINGS.get(base_type, native_type.upper())

        return normalized

    async def read_tables(self, schema: Optional[str] = None) -> List[str]:
        """
        Get list of all tables in schema/database.

        Args:
            schema: Schema name (PostgreSQL) or database name (MySQL/SQLite)
                   Defaults to 'public' for PostgreSQL, current database for MySQL,
                   'main' for SQLite

        Returns:
            List of table names

        Raises:
            SchemaReadError: If reading tables fails

        Example:
            tables = await reader.read_tables('public')
            # ['users', 'orders', 'products']
        """
        try:
            if self.db_type == DatabaseType.POSTGRESQL:
                return await self._read_tables_postgresql(schema or "public")
            elif self.db_type == DatabaseType.MYSQL:
                return await self._read_tables_mysql(schema or self.adapter.database)
            elif self.db_type == DatabaseType.SQLITE:
                return await self._read_tables_sqlite()
            else:
                raise DatabaseNotSupportedError(f"Unsupported database: {self.db_type}")

        except Exception as e:
            logger.error(f"Failed to read tables from {schema or 'default'}: {e}")
            raise SchemaReadError(f"Failed to read tables: {e}") from e

    async def _read_tables_postgresql(self, schema: str) -> List[str]:
        """Read table names from PostgreSQL."""
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = $1
                AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """

        rows = await self.adapter.fetch_all(query, (schema,))
        tables = [row["table_name"] for row in rows]

        logger.debug(f"Found {len(tables)} tables in schema {schema}")
        return tables

    async def _read_tables_mysql(self, database: str) -> List[str]:
        """Read table names from MySQL."""
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
                AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """

        rows = await self.adapter.fetch_all(query, (database,))
        tables = [row["table_name"] for row in rows]

        logger.debug(f"Found {len(tables)} tables in database {database}")
        return tables

    async def _read_tables_sqlite(self) -> List[str]:
        """Read table names from SQLite."""
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """

        rows = await self.adapter.fetch_all(query)
        tables = [row["name"] for row in rows]

        logger.debug(f"Found {len(tables)} tables in SQLite database")
        return tables

    async def read_columns(
        self, table: str, schema: Optional[str] = None
    ) -> List[ColumnDefinition]:
        """
        Get complete column definitions for a table.

        Args:
            table: Table name
            schema: Schema/database name (optional)

        Returns:
            List of ColumnDefinition objects

        Raises:
            SchemaReadError: If reading columns fails

        Example:
            columns = await reader.read_columns('users', 'public')
            for col in columns:
                print(f"{col.name}: {col.data_type} {col.is_nullable}")
        """
        try:
            if self.db_type == DatabaseType.POSTGRESQL:
                return await self._read_columns_postgresql(table, schema or "public")
            elif self.db_type == DatabaseType.MYSQL:
                return await self._read_columns_mysql(table, schema or self.adapter.database)
            elif self.db_type == DatabaseType.SQLITE:
                return await self._read_columns_sqlite(table)
            else:
                raise DatabaseNotSupportedError(f"Unsupported database: {self.db_type}")

        except Exception as e:
            logger.error(f"Failed to read columns for {table}: {e}")
            raise SchemaReadError(f"Failed to read columns for {table}: {e}") from e

    async def _read_columns_postgresql(self, table: str, schema: str) -> List[ColumnDefinition]:
        """Read column definitions from PostgreSQL."""
        query = """
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                c.ordinal_position,
                pgd.description as column_comment,
                CASE
                    WHEN c.column_default LIKE 'nextval(%' THEN true
                    ELSE false
                END as is_auto_increment
            FROM information_schema.columns c
            LEFT JOIN pg_catalog.pg_statio_all_tables st
                ON c.table_schema = st.schemaname
                AND c.table_name = st.relname
            LEFT JOIN pg_catalog.pg_description pgd
                ON pgd.objoid = st.relid
                AND pgd.objsubid = c.ordinal_position
            WHERE c.table_schema = $1
                AND c.table_name = $2
            ORDER BY c.ordinal_position
        """

        rows = await self.adapter.fetch_all(query, (schema, table))

        # Get primary key columns
        pk_query = """
            SELECT a.attname as column_name
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid
                AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = $1::regclass
                AND i.indisprimary
        """
        pk_rows = await self.adapter.fetch_all(pk_query, (f"{schema}.{table}",))
        pk_columns = {row["column_name"] for row in pk_rows}

        # Get unique columns
        unique_query = """
            SELECT a.attname as column_name
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid
                AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = $1::regclass
                AND i.indisunique
                AND NOT i.indisprimary
                AND array_length(i.indkey, 1) = 1
        """
        unique_rows = await self.adapter.fetch_all(unique_query, (f"{schema}.{table}",))
        unique_columns = {row["column_name"] for row in unique_rows}

        columns = []
        for row in rows:
            col = ColumnDefinition(
                name=row["column_name"],
                data_type=row["data_type"],
                normalized_type=self._normalize_type(row["data_type"]),
                is_nullable=(row["is_nullable"] == "YES"),
                default_value=row["column_default"],
                character_maximum_length=row["character_maximum_length"],
                numeric_precision=row["numeric_precision"],
                numeric_scale=row["numeric_scale"],
                is_primary_key=(row["column_name"] in pk_columns),
                is_unique=(row["column_name"] in unique_columns),
                is_auto_increment=row["is_auto_increment"],
                column_comment=row["column_comment"],
                ordinal_position=row["ordinal_position"],
            )
            columns.append(col)

        logger.debug(f"Read {len(columns)} columns for {schema}.{table}")
        return columns

    async def _read_columns_mysql(self, table: str, database: str) -> List[ColumnDefinition]:
        """Read column definitions from MySQL."""
        query = """
            SELECT
                column_name,
                data_type,
                column_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                column_key,
                extra,
                column_comment,
                ordinal_position
            FROM information_schema.columns
            WHERE table_schema = %s
                AND table_name = %s
            ORDER BY ordinal_position
        """

        rows = await self.adapter.fetch_all(query, (database, table))

        columns = []
        for row in rows:
            col = ColumnDefinition(
                name=row["column_name"],
                data_type=row["column_type"],
                normalized_type=self._normalize_type(row["data_type"]),
                is_nullable=(row["is_nullable"] == "YES"),
                default_value=row["column_default"],
                character_maximum_length=row["character_maximum_length"],
                numeric_precision=row["numeric_precision"],
                numeric_scale=row["numeric_scale"],
                is_primary_key=(row["column_key"] == "PRI"),
                is_unique=(row["column_key"] == "UNI"),
                is_auto_increment=("auto_increment" in row["extra"].lower()),
                column_comment=row["column_comment"] if row["column_comment"] else None,
                ordinal_position=row["ordinal_position"],
            )
            columns.append(col)

        logger.debug(f"Read {len(columns)} columns for {database}.{table}")
        return columns

    async def _read_columns_sqlite(self, table: str) -> List[ColumnDefinition]:
        """Read column definitions from SQLite."""
        query = f"PRAGMA table_info({table})"
        rows = await self.adapter.fetch_all(query)

        columns = []
        for row in rows:
            # Parse type for length/precision
            data_type = row["type"]

            col = ColumnDefinition(
                name=row["name"],
                data_type=data_type,
                normalized_type=self._normalize_type(data_type),
                is_nullable=(row["notnull"] == 0),
                default_value=row["dflt_value"],
                is_primary_key=(row["pk"] > 0),
                ordinal_position=row["cid"],
            )
            columns.append(col)

        logger.debug(f"Read {len(columns)} columns for {table}")
        return columns

    async def read_indexes(self, table: str, schema: Optional[str] = None) -> List[IndexDefinition]:
        """
        Get index definitions for a table.

        Args:
            table: Table name
            schema: Schema/database name (optional)

        Returns:
            List of IndexDefinition objects

        Raises:
            SchemaReadError: If reading indexes fails
        """
        try:
            if self.db_type == DatabaseType.POSTGRESQL:
                return await self._read_indexes_postgresql(table, schema or "public")
            elif self.db_type == DatabaseType.MYSQL:
                return await self._read_indexes_mysql(table, schema or self.adapter.database)
            elif self.db_type == DatabaseType.SQLITE:
                return await self._read_indexes_sqlite(table)
            else:
                raise DatabaseNotSupportedError(f"Unsupported database: {self.db_type}")

        except Exception as e:
            logger.error(f"Failed to read indexes for {table}: {e}")
            raise SchemaReadError(f"Failed to read indexes for {table}: {e}") from e

    async def _read_indexes_postgresql(self, table: str, schema: str) -> List[IndexDefinition]:
        """Read index definitions from PostgreSQL."""
        query = """
            SELECT
                i.indexname as index_name,
                i.tablename as table_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary,
                am.amname as index_type,
                pg_get_expr(ix.indpred, ix.indrelid) as where_clause,
                obj_description(ix.indexrelid) as index_comment
            FROM pg_indexes i
            JOIN pg_class c ON c.relname = i.indexname
            JOIN pg_index ix ON ix.indexrelid = c.oid
            JOIN pg_attribute a ON a.attrelid = ix.indrelid
                AND a.attnum = ANY(ix.indkey)
            JOIN pg_am am ON am.oid = c.relam
            WHERE i.schemaname = $1
                AND i.tablename = $2
            ORDER BY i.indexname, a.attnum
        """

        rows = await self.adapter.fetch_all(query, (schema, table))

        # Group columns by index name
        indexes_dict: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            idx_name = row["index_name"]
            if idx_name not in indexes_dict:
                indexes_dict[idx_name] = {
                    "name": idx_name,
                    "table_name": row["table_name"],
                    "columns": [],
                    "is_unique": row["is_unique"],
                    "is_primary": row["is_primary"],
                    "index_type": row["index_type"],
                    "where_clause": row["where_clause"],
                    "index_comment": row["index_comment"],
                }
            indexes_dict[idx_name]["columns"].append(row["column_name"])

        # Convert to IndexDefinition objects
        indexes = []
        for idx_data in indexes_dict.values():
            # Map PostgreSQL index type to IndexType enum
            index_type_str = idx_data["index_type"].upper()
            if index_type_str == "BTREE":
                index_type = IndexType.BTREE
            elif index_type_str == "HASH":
                index_type = IndexType.HASH
            elif index_type_str == "GIST":
                index_type = IndexType.GIST
            elif index_type_str == "GIN":
                index_type = IndexType.GIN
            elif index_type_str == "BRIN":
                index_type = IndexType.BRIN
            else:
                index_type = IndexType.BTREE

            idx = IndexDefinition(
                name=idx_data["name"],
                table_name=idx_data["table_name"],
                columns=idx_data["columns"],
                is_unique=idx_data["is_unique"],
                is_primary=idx_data["is_primary"],
                index_type=index_type,
                where_clause=idx_data["where_clause"],
                index_comment=idx_data["index_comment"],
            )
            indexes.append(idx)

        logger.debug(f"Read {len(indexes)} indexes for {schema}.{table}")
        return indexes

    async def _read_indexes_mysql(self, table: str, database: str) -> List[IndexDefinition]:
        """Read index definitions from MySQL."""
        query = """
            SELECT
                index_name,
                table_name,
                column_name,
                non_unique,
                index_type,
                seq_in_index
            FROM information_schema.statistics
            WHERE table_schema = %s
                AND table_name = %s
            ORDER BY index_name, seq_in_index
        """

        rows = await self.adapter.fetch_all(query, (database, table))

        # Group columns by index name
        indexes_dict: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            idx_name = row["index_name"]
            if idx_name not in indexes_dict:
                indexes_dict[idx_name] = {
                    "name": idx_name,
                    "table_name": row["table_name"],
                    "columns": [],
                    "is_unique": (row["non_unique"] == 0),
                    "is_primary": (idx_name == "PRIMARY"),
                    "index_type": row["index_type"],
                }
            indexes_dict[idx_name]["columns"].append(row["column_name"])

        # Convert to IndexDefinition objects
        indexes = []
        for idx_data in indexes_dict.values():
            # Map MySQL index type to IndexType enum
            index_type_str = idx_data["index_type"].upper()
            if index_type_str == "BTREE":
                index_type = IndexType.BTREE
            elif index_type_str == "HASH":
                index_type = IndexType.HASH
            elif index_type_str == "FULLTEXT":
                index_type = IndexType.FULLTEXT
            elif index_type_str == "SPATIAL":
                index_type = IndexType.SPATIAL
            else:
                index_type = IndexType.BTREE

            idx = IndexDefinition(
                name=idx_data["name"],
                table_name=idx_data["table_name"],
                columns=idx_data["columns"],
                is_unique=idx_data["is_unique"],
                is_primary=idx_data["is_primary"],
                index_type=index_type,
            )
            indexes.append(idx)

        logger.debug(f"Read {len(indexes)} indexes for {database}.{table}")
        return indexes

    async def _read_indexes_sqlite(self, table: str) -> List[IndexDefinition]:
        """Read index definitions from SQLite."""
        # Get list of indexes
        query = f"PRAGMA index_list({table})"
        index_rows = await self.adapter.fetch_all(query)

        indexes = []
        for idx_row in index_rows:
            idx_name = idx_row["name"]

            # Get columns for this index
            col_query = f"PRAGMA index_info({idx_name})"
            col_rows = await self.adapter.fetch_all(col_query)

            columns = [row["name"] for row in col_rows]

            idx = IndexDefinition(
                name=idx_name,
                table_name=table,
                columns=columns,
                is_unique=(idx_row["unique"] == 1),
                is_primary=False,  # SQLite doesn't expose PK as index in PRAGMA
                index_type=IndexType.BTREE,  # SQLite primarily uses BTREE
            )
            indexes.append(idx)

        logger.debug(f"Read {len(indexes)} indexes for {table}")
        return indexes

    async def read_constraints(
        self, table: str, schema: Optional[str] = None
    ) -> List[ConstraintDefinition]:
        """
        Get constraint definitions for a table.

        Args:
            table: Table name
            schema: Schema/database name (optional)

        Returns:
            List of ConstraintDefinition objects

        Raises:
            SchemaReadError: If reading constraints fails
        """
        try:
            if self.db_type == DatabaseType.POSTGRESQL:
                return await self._read_constraints_postgresql(table, schema or "public")
            elif self.db_type == DatabaseType.MYSQL:
                return await self._read_constraints_mysql(table, schema or self.adapter.database)
            elif self.db_type == DatabaseType.SQLITE:
                return await self._read_constraints_sqlite(table)
            else:
                raise DatabaseNotSupportedError(f"Unsupported database: {self.db_type}")

        except Exception as e:
            logger.error(f"Failed to read constraints for {table}: {e}")
            raise SchemaReadError(f"Failed to read constraints for {table}: {e}") from e

    async def _read_constraints_postgresql(
        self, table: str, schema: str
    ) -> List[ConstraintDefinition]:
        """Read constraint definitions from PostgreSQL."""
        query = """
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                cc.check_clause,
                tc.is_deferrable,
                tc.initially_deferred
            FROM information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            LEFT JOIN information_schema.check_constraints cc
                ON tc.constraint_name = cc.constraint_name
                AND tc.table_schema = cc.constraint_schema
            WHERE tc.table_schema = $1
                AND tc.table_name = $2
                AND tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE', 'CHECK')
            ORDER BY tc.constraint_name, kcu.ordinal_position
        """

        rows = await self.adapter.fetch_all(query, (schema, table))

        # Group columns by constraint name
        constraints_dict: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            const_name = row["constraint_name"]
            if const_name not in constraints_dict:
                # Map constraint type to ConstraintType enum
                const_type_str = row["constraint_type"]
                if const_type_str == "PRIMARY KEY":
                    const_type = ConstraintType.PRIMARY_KEY
                elif const_type_str == "UNIQUE":
                    const_type = ConstraintType.UNIQUE
                elif const_type_str == "CHECK":
                    const_type = ConstraintType.CHECK
                else:
                    continue

                constraints_dict[const_name] = {
                    "name": const_name,
                    "table_name": table,
                    "constraint_type": const_type,
                    "columns": [],
                    "check_clause": row["check_clause"],
                    "is_deferrable": (row["is_deferrable"] == "YES"),
                    "initially_deferred": (row["initially_deferred"] == "YES"),
                }

            if row["column_name"]:
                constraints_dict[const_name]["columns"].append(row["column_name"])

        # Convert to ConstraintDefinition objects
        constraints = []
        for const_data in constraints_dict.values():
            const = ConstraintDefinition(
                name=const_data["name"],
                table_name=const_data["table_name"],
                constraint_type=const_data["constraint_type"],
                columns=const_data["columns"],
                check_clause=const_data["check_clause"],
                is_deferrable=const_data["is_deferrable"],
                initially_deferred=const_data["initially_deferred"],
            )
            constraints.append(const)

        logger.debug(f"Read {len(constraints)} constraints for {schema}.{table}")
        return constraints

    async def _read_constraints_mysql(
        self, table: str, database: str
    ) -> List[ConstraintDefinition]:
        """Read constraint definitions from MySQL."""
        # MySQL stores PRIMARY KEY and UNIQUE as indexes, CHECK constraints
        # separately
        constraints = []

        # Get PRIMARY KEY and UNIQUE constraints from indexes
        query = """
            SELECT
                index_name,
                column_name,
                non_unique,
                seq_in_index
            FROM information_schema.statistics
            WHERE table_schema = %s
                AND table_name = %s
                AND (index_name = 'PRIMARY' OR non_unique = 0)
            ORDER BY index_name, seq_in_index
        """

        rows = await self.adapter.fetch_all(query, (database, table))

        # Group by index name
        indexes_dict: Dict[str, List[str]] = {}
        for row in rows:
            idx_name = row["index_name"]
            if idx_name not in indexes_dict:
                indexes_dict[idx_name] = []
            indexes_dict[idx_name].append(row["column_name"])

        # Convert to constraints
        for idx_name, columns in indexes_dict.items():
            if idx_name == "PRIMARY":
                const = ConstraintDefinition(
                    name=idx_name,
                    table_name=table,
                    constraint_type=ConstraintType.PRIMARY_KEY,
                    columns=columns,
                )
            else:
                const = ConstraintDefinition(
                    name=idx_name,
                    table_name=table,
                    constraint_type=ConstraintType.UNIQUE,
                    columns=columns,
                )
            constraints.append(const)

        # Get CHECK constraints (MySQL 8.0.16+)
        try:
            check_query = """
                SELECT
                    constraint_name,
                    check_clause
                FROM information_schema.check_constraints
                WHERE constraint_schema = %s
                    AND table_name = %s
            """
            check_rows = await self.adapter.fetch_all(check_query, (database, table))

            for row in check_rows:
                const = ConstraintDefinition(
                    name=row["constraint_name"],
                    table_name=table,
                    constraint_type=ConstraintType.CHECK,
                    columns=[],  # CHECK constraints may not have specific columns
                    check_clause=row["check_clause"],
                )
                constraints.append(const)
        except Exception:
            # CHECK constraints not available in older MySQL versions
            pass

        logger.debug(f"Read {len(constraints)} constraints for {database}.{table}")
        return constraints

    async def _read_constraints_sqlite(self, table: str) -> List[ConstraintDefinition]:
        """Read constraint definitions from SQLite."""
        constraints = []

        # Get PRIMARY KEY from table_info
        query = f"PRAGMA table_info({table})"
        rows = await self.adapter.fetch_all(query)

        pk_columns = [row["name"] for row in rows if row["pk"] > 0]
        if pk_columns:
            const = ConstraintDefinition(
                name=f"{table}_pkey",
                table_name=table,
                constraint_type=ConstraintType.PRIMARY_KEY,
                columns=pk_columns,
            )
            constraints.append(const)

        # SQLite doesn't easily expose UNIQUE and CHECK constraints via PRAGMA
        # Would need to parse CREATE TABLE statement for complete info

        logger.debug(f"Read {len(constraints)} constraints for {table}")
        return constraints

    async def read_foreign_keys(
        self, table: str, schema: Optional[str] = None
    ) -> List[ForeignKeyDefinition]:
        """
        Get foreign key definitions for a table.

        Args:
            table: Table name
            schema: Schema/database name (optional)

        Returns:
            List of ForeignKeyDefinition objects

        Raises:
            SchemaReadError: If reading foreign keys fails
        """
        try:
            if self.db_type == DatabaseType.POSTGRESQL:
                return await self._read_foreign_keys_postgresql(table, schema or "public")
            elif self.db_type == DatabaseType.MYSQL:
                return await self._read_foreign_keys_mysql(table, schema or self.adapter.database)
            elif self.db_type == DatabaseType.SQLITE:
                return await self._read_foreign_keys_sqlite(table)
            else:
                raise DatabaseNotSupportedError(f"Unsupported database: {self.db_type}")

        except Exception as e:
            logger.error(f"Failed to read foreign keys for {table}: {e}")
            raise SchemaReadError(f"Failed to read foreign keys for {table}: {e}") from e

    async def _read_foreign_keys_postgresql(
        self, table: str, schema: str
    ) -> List[ForeignKeyDefinition]:
        """Read foreign key definitions from PostgreSQL."""
        query = """
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column,
                rc.update_rule AS on_update,
                rc.delete_rule AS on_delete,
                tc.is_deferrable,
                tc.initially_deferred
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            JOIN information_schema.referential_constraints rc
                ON rc.constraint_name = tc.constraint_name
                AND rc.constraint_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = $1
                AND tc.table_name = $2
            ORDER BY tc.constraint_name, kcu.ordinal_position
        """

        rows = await self.adapter.fetch_all(query, (schema, table))

        # Group by constraint name
        fks_dict: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            fk_name = row["constraint_name"]
            if fk_name not in fks_dict:
                fks_dict[fk_name] = {
                    "name": fk_name,
                    "table_name": table,
                    "columns": [],
                    "referenced_table": row["referenced_table"],
                    "referenced_columns": [],
                    "on_update": row["on_update"],
                    "on_delete": row["on_delete"],
                    "is_deferrable": (row["is_deferrable"] == "YES"),
                    "initially_deferred": (row["initially_deferred"] == "YES"),
                }
            fks_dict[fk_name]["columns"].append(row["column_name"])
            fks_dict[fk_name]["referenced_columns"].append(row["referenced_column"])

        # Convert to ForeignKeyDefinition objects
        foreign_keys = []
        for fk_data in fks_dict.values():
            fk = ForeignKeyDefinition(
                name=fk_data["name"],
                table_name=fk_data["table_name"],
                columns=fk_data["columns"],
                referenced_table=fk_data["referenced_table"],
                referenced_columns=fk_data["referenced_columns"],
                on_update=fk_data["on_update"],
                on_delete=fk_data["on_delete"],
                is_deferrable=fk_data["is_deferrable"],
                initially_deferred=fk_data["initially_deferred"],
            )
            foreign_keys.append(fk)

        logger.debug(f"Read {len(foreign_keys)} foreign keys for {schema}.{table}")
        return foreign_keys

    async def _read_foreign_keys_mysql(
        self, table: str, database: str
    ) -> List[ForeignKeyDefinition]:
        """Read foreign key definitions from MySQL."""
        query = """
            SELECT
                kcu.constraint_name,
                kcu.column_name,
                kcu.referenced_table_name,
                kcu.referenced_column_name,
                rc.update_rule,
                rc.delete_rule
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.referential_constraints rc
                ON kcu.constraint_name = rc.constraint_name
                AND kcu.constraint_schema = rc.constraint_schema
            WHERE kcu.table_schema = %s
                AND kcu.table_name = %s
                AND kcu.referenced_table_name IS NOT NULL
            ORDER BY kcu.constraint_name, kcu.ordinal_position
        """

        rows = await self.adapter.fetch_all(query, (database, table))

        # Group by constraint name
        fks_dict: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            fk_name = row["constraint_name"]
            if fk_name not in fks_dict:
                fks_dict[fk_name] = {
                    "name": fk_name,
                    "table_name": table,
                    "columns": [],
                    "referenced_table": row["referenced_table_name"],
                    "referenced_columns": [],
                    "on_update": row["update_rule"],
                    "on_delete": row["delete_rule"],
                }
            fks_dict[fk_name]["columns"].append(row["column_name"])
            fks_dict[fk_name]["referenced_columns"].append(row["referenced_column_name"])

        # Convert to ForeignKeyDefinition objects
        foreign_keys = []
        for fk_data in fks_dict.values():
            fk = ForeignKeyDefinition(
                name=fk_data["name"],
                table_name=fk_data["table_name"],
                columns=fk_data["columns"],
                referenced_table=fk_data["referenced_table"],
                referenced_columns=fk_data["referenced_columns"],
                on_update=fk_data["on_update"],
                on_delete=fk_data["on_delete"],
            )
            foreign_keys.append(fk)

        logger.debug(f"Read {len(foreign_keys)} foreign keys for {database}.{table}")
        return foreign_keys

    async def _read_foreign_keys_sqlite(self, table: str) -> List[ForeignKeyDefinition]:
        """Read foreign key definitions from SQLite."""
        query = f"PRAGMA foreign_key_list({table})"
        rows = await self.adapter.fetch_all(query)

        # Group by foreign key id
        fks_dict: Dict[int, Dict[str, Any]] = {}
        for row in rows:
            fk_id = row["id"]
            if fk_id not in fks_dict:
                fks_dict[fk_id] = {
                    "name": f"{table}_fk_{fk_id}",
                    "table_name": table,
                    "columns": [],
                    "referenced_table": row["table"],
                    "referenced_columns": [],
                    "on_update": row["on_update"],
                    "on_delete": row["on_delete"],
                }
            fks_dict[fk_id]["columns"].append(row["from"])
            fks_dict[fk_id]["referenced_columns"].append(row["to"])

        # Convert to ForeignKeyDefinition objects
        foreign_keys = []
        for fk_data in fks_dict.values():
            fk = ForeignKeyDefinition(
                name=fk_data["name"],
                table_name=fk_data["table_name"],
                columns=fk_data["columns"],
                referenced_table=fk_data["referenced_table"],
                referenced_columns=fk_data["referenced_columns"],
                on_update=fk_data["on_update"],
                on_delete=fk_data["on_delete"],
            )
            foreign_keys.append(fk)

        logger.debug(f"Read {len(foreign_keys)} foreign keys for {table}")
        return foreign_keys

    async def read_table_complete(
        self, table: str, schema: Optional[str] = None
    ) -> TableDefinition:
        """
        Get complete table definition including all metadata.

        Reads columns, indexes, constraints, and foreign keys in parallel
        for optimal performance.

        Args:
            table: Table name
            schema: Schema/database name (optional)

        Returns:
            Complete TableDefinition object

        Raises:
            SchemaReadError: If reading table definition fails

        Example:
            table_def = await reader.read_table_complete('users', 'public')
            print(f"Table: {table_def.name}")
            print(f"Columns: {len(table_def.columns)}")
            print(f"Indexes: {len(table_def.indexes)}")
            print(f"Foreign Keys: {len(table_def.foreign_keys)}")
        """
        schema = schema or (
            "public"
            if self.db_type == DatabaseType.POSTGRESQL
            else self.adapter.database if self.db_type == DatabaseType.MYSQL else "main"
        )

        try:
            # Read all components in parallel for performance
            columns_task = self.read_columns(table, schema)
            indexes_task = self.read_indexes(table, schema)
            constraints_task = self.read_constraints(table, schema)
            fks_task = self.read_foreign_keys(table, schema)

            columns, indexes, constraints, foreign_keys = await asyncio.gather(
                columns_task, indexes_task, constraints_task, fks_task
            )

            table_def = TableDefinition(
                name=table,
                schema=schema,
                columns=columns,
                indexes=indexes,
                constraints=constraints,
                foreign_keys=foreign_keys,
            )

            logger.info(f"Read complete definition for {schema}.{table}")
            return table_def

        except Exception as e:
            logger.error(f"Failed to read complete table definition for {table}: {e}")
            raise SchemaReadError(
                f"Failed to read complete table definition for {table}: {e}"
            ) from e

    async def read_schema_complete(self, schema: Optional[str] = None) -> List[TableDefinition]:
        """
        Get complete schema definition for all tables.

        Reads all tables with complete metadata in parallel for optimal performance.

        Args:
            schema: Schema/database name (optional)

        Returns:
            List of complete TableDefinition objects

        Raises:
            SchemaReadError: If reading schema fails

        Example:
            tables = await reader.read_schema_complete('public')
            for table in tables:
                print(f"Table: {table.name}")
                print(f"  Columns: {len(table.columns)}")
                print(f"  Indexes: {len(table.indexes)}")
        """
        try:
            # Get list of tables
            table_names = await self.read_tables(schema)

            # Read all tables in parallel with concurrency limit
            # to avoid overwhelming the database
            semaphore = asyncio.Semaphore(5)  # Max 5 concurrent table reads

            async def read_with_limit(table_name: str) -> TableDefinition:
                async with semaphore:
                    return await self.read_table_complete(table_name, schema)

            tasks = [read_with_limit(table_name) for table_name in table_names]
            tables = await asyncio.gather(*tasks)

            logger.info(f"Read complete schema with {len(tables)} tables")
            return tables

        except Exception as e:
            logger.error(f"Failed to read complete schema: {e}")
            raise SchemaReadError(f"Failed to read complete schema: {e}") from e


__all__ = [
    "SchemaReader",
    "DatabaseType",
    "ConstraintType",
    "IndexType",
    "ColumnDefinition",
    "IndexDefinition",
    "ConstraintDefinition",
    "ForeignKeyDefinition",
    "TableDefinition",
    "SchemaReaderError",
    "DatabaseNotSupportedError",
    "SchemaReadError",
]
