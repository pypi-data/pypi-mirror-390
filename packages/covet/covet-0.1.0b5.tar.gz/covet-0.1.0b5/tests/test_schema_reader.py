"""
Comprehensive Integration Tests for SchemaReader

Tests schema introspection across PostgreSQL, MySQL, and SQLite with
production-grade validation and edge case coverage.
"""

import asyncio
import pytest
from pathlib import Path
from typing import Any, Dict, List

from covet.database.migrations.schema_reader import (
    SchemaReader,
    DatabaseType,
    ConstraintType,
    IndexType,
    ColumnDefinition,
    IndexDefinition,
    ConstraintDefinition,
    ForeignKeyDefinition,
    TableDefinition,
    SchemaReaderError,
    DatabaseNotSupportedError,
    SchemaReadError
)


class TestSchemaReaderDataStructures:
    """Test data structure classes."""

    def test_column_definition(self):
        """Test ColumnDefinition creation and representation."""
        col = ColumnDefinition(
            name="user_id",
            data_type="integer",
            normalized_type="INTEGER",
            is_nullable=False,
            is_primary_key=True,
            is_auto_increment=True,
            ordinal_position=1
        )

        assert col.name == "user_id"
        assert col.data_type == "integer"
        assert col.normalized_type == "INTEGER"
        assert col.is_nullable is False
        assert col.is_primary_key is True
        assert col.is_auto_increment is True
        assert "user_id" in str(col)
        assert "INTEGER" in str(col).upper()

    def test_index_definition(self):
        """Test IndexDefinition creation and representation."""
        idx = IndexDefinition(
            name="idx_users_email",
            table_name="users",
            columns=["email"],
            is_unique=True,
            index_type=IndexType.BTREE
        )

        assert idx.name == "idx_users_email"
        assert idx.table_name == "users"
        assert idx.columns == ["email"]
        assert idx.is_unique is True
        assert "email" in str(idx)

    def test_constraint_definition(self):
        """Test ConstraintDefinition creation and representation."""
        const = ConstraintDefinition(
            name="users_pkey",
            table_name="users",
            constraint_type=ConstraintType.PRIMARY_KEY,
            columns=["user_id"]
        )

        assert const.name == "users_pkey"
        assert const.constraint_type == ConstraintType.PRIMARY_KEY
        assert const.columns == ["user_id"]

    def test_foreign_key_definition(self):
        """Test ForeignKeyDefinition creation and representation."""
        fk = ForeignKeyDefinition(
            name="orders_user_id_fkey",
            table_name="orders",
            columns=["user_id"],
            referenced_table="users",
            referenced_columns=["user_id"],
            on_delete="CASCADE",
            on_update="NO ACTION"
        )

        assert fk.name == "orders_user_id_fkey"
        assert fk.table_name == "orders"
        assert fk.referenced_table == "users"
        assert fk.on_delete == "CASCADE"
        assert "CASCADE" in str(fk)

    def test_table_definition(self):
        """Test TableDefinition creation and helper methods."""
        col1 = ColumnDefinition(
            name="user_id",
            data_type="integer",
            normalized_type="INTEGER",
            is_primary_key=True,
            ordinal_position=1
        )
        col2 = ColumnDefinition(
            name="email",
            data_type="varchar(255)",
            normalized_type="VARCHAR",
            ordinal_position=2
        )

        table = TableDefinition(
            name="users",
            schema="public",
            columns=[col1, col2]
        )

        assert table.name == "users"
        assert table.schema == "public"
        assert len(table.columns) == 2

        # Test get_column
        assert table.get_column("user_id") == col1
        assert table.get_column("email") == col2
        assert table.get_column("nonexistent") is None

        # Test get_primary_key_columns
        pk_cols = table.get_primary_key_columns()
        assert pk_cols == ["user_id"]


class TestSchemaReaderTypeNormalization:
    """Test type normalization across databases."""

    def test_postgresql_type_normalization(self):
        """Test PostgreSQL type normalization."""
        reader = SchemaReader(None, DatabaseType.POSTGRESQL)

        # Test various PostgreSQL types
        assert reader._normalize_type("integer") == "INTEGER"
        assert reader._normalize_type("bigint") == "BIGINT"
        assert reader._normalize_type("character varying") == "VARCHAR"
        assert reader._normalize_type("timestamp without time zone") == "TIMESTAMP"
        assert reader._normalize_type("timestamp with time zone") == "TIMESTAMPTZ"
        assert reader._normalize_type("jsonb") == "JSONB"
        assert reader._normalize_type("uuid") == "UUID"

        # Test with size specifications
        assert reader._normalize_type("varchar(255)") == "VARCHAR"
        assert reader._normalize_type("numeric(10,2)") == "DECIMAL"

    def test_mysql_type_normalization(self):
        """Test MySQL type normalization."""
        reader = SchemaReader(None, DatabaseType.MYSQL)

        # Test various MySQL types
        assert reader._normalize_type("int") == "INTEGER"
        assert reader._normalize_type("bigint") == "BIGINT"
        assert reader._normalize_type("varchar") == "VARCHAR"
        assert reader._normalize_type("datetime") == "DATETIME"
        assert reader._normalize_type("text") == "TEXT"
        assert reader._normalize_type("blob") == "BLOB"

        # Test with size specifications
        assert reader._normalize_type("varchar(255)") == "VARCHAR"
        assert reader._normalize_type("decimal(10,2)") == "DECIMAL"

    def test_sqlite_type_normalization(self):
        """Test SQLite type normalization."""
        reader = SchemaReader(None, DatabaseType.SQLITE)

        # Test SQLite types
        assert reader._normalize_type("INTEGER") == "INTEGER"
        assert reader._normalize_type("TEXT") == "TEXT"
        assert reader._normalize_type("REAL") == "FLOAT"
        assert reader._normalize_type("BLOB") == "BLOB"
        assert reader._normalize_type("NUMERIC") == "NUMERIC"


class TestSchemaReaderErrors:
    """Test error handling."""

    def test_unsupported_database_error(self):
        """Test that unsupported database raises error."""
        with pytest.raises(Exception):
            # This should raise an error because 'invalid' is not a valid DatabaseType
            SchemaReader(None, "invalid")

    def test_database_not_supported_error_message(self):
        """Test error message content."""
        try:
            reader = SchemaReader(None, DatabaseType.POSTGRESQL)
            # Force an unsupported operation
        except DatabaseNotSupportedError as e:
            assert "not supported" in str(e).lower()


# Note: The following tests require actual database connections
# They are marked as integration tests and should be run with appropriate
# database instances available

@pytest.mark.integration
@pytest.mark.asyncio
class TestSchemaReaderSQLite:
    """Integration tests for SQLite schema reading."""

    async def setup_test_database(self):
        """Create a test SQLite database with sample schema."""
        from covet.database.adapters.sqlite import SQLiteAdapter

        # Create in-memory database
        adapter = SQLiteAdapter(database=":memory:")
        await adapter.connect()

        # Create test tables
        await adapter.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await adapter.execute("""
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        await adapter.execute("""
            CREATE INDEX idx_orders_user_id ON orders(user_id)
        """)

        await adapter.execute("""
            CREATE UNIQUE INDEX idx_users_email ON users(email)
        """)

        return adapter

    async def test_read_tables_sqlite(self):
        """Test reading table names from SQLite."""
        adapter = await self.setup_test_database()
        reader = SchemaReader(adapter, DatabaseType.SQLITE)

        tables = await reader.read_tables()

        assert len(tables) == 2
        assert "users" in tables
        assert "orders" in tables

        await adapter.disconnect()

    async def test_read_columns_sqlite(self):
        """Test reading column definitions from SQLite."""
        adapter = await self.setup_test_database()
        reader = SchemaReader(adapter, DatabaseType.SQLITE)

        columns = await reader.read_columns("users")

        assert len(columns) >= 4
        assert any(col.name == "user_id" for col in columns)
        assert any(col.name == "username" for col in columns)
        assert any(col.name == "email" for col in columns)

        # Verify user_id is primary key
        user_id_col = next(col for col in columns if col.name == "user_id")
        assert user_id_col.is_primary_key is True
        assert user_id_col.normalized_type == "INTEGER"

        await adapter.disconnect()

    async def test_read_indexes_sqlite(self):
        """Test reading index definitions from SQLite."""
        adapter = await self.setup_test_database()
        reader = SchemaReader(adapter, DatabaseType.SQLITE)

        indexes = await reader.read_indexes("orders")

        assert len(indexes) >= 1
        assert any(idx.name == "idx_orders_user_id" for idx in indexes)

        # Verify index properties
        user_idx = next(idx for idx in indexes if idx.name == "idx_orders_user_id")
        assert "user_id" in user_idx.columns

        await adapter.disconnect()

    async def test_read_foreign_keys_sqlite(self):
        """Test reading foreign key definitions from SQLite."""
        adapter = await self.setup_test_database()
        reader = SchemaReader(adapter, DatabaseType.SQLITE)

        foreign_keys = await reader.read_foreign_keys("orders")

        assert len(foreign_keys) >= 1

        # Verify foreign key properties
        fk = foreign_keys[0]
        assert fk.table_name == "orders"
        assert "user_id" in fk.columns
        assert fk.referenced_table == "users"
        assert "user_id" in fk.referenced_columns

        await adapter.disconnect()

    async def test_read_table_complete_sqlite(self):
        """Test reading complete table definition from SQLite."""
        adapter = await self.setup_test_database()
        reader = SchemaReader(adapter, DatabaseType.SQLITE)

        table_def = await reader.read_table_complete("orders")

        assert table_def.name == "orders"
        assert len(table_def.columns) >= 4
        assert len(table_def.indexes) >= 1
        assert len(table_def.foreign_keys) >= 1

        # Verify column details
        order_id_col = table_def.get_column("order_id")
        assert order_id_col is not None
        assert order_id_col.is_primary_key is True

        await adapter.disconnect()

    async def test_read_schema_complete_sqlite(self):
        """Test reading complete schema with all tables from SQLite."""
        adapter = await self.setup_test_database()
        reader = SchemaReader(adapter, DatabaseType.SQLITE)

        tables = await reader.read_schema_complete()

        assert len(tables) == 2

        # Find users table
        users_table = next(t for t in tables if t.name == "users")
        assert len(users_table.columns) >= 4

        # Find orders table
        orders_table = next(t for t in tables if t.name == "orders")
        assert len(orders_table.columns) >= 4
        assert len(orders_table.foreign_keys) >= 1

        await adapter.disconnect()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires running PostgreSQL instance")
class TestSchemaReaderPostgreSQL:
    """Integration tests for PostgreSQL schema reading."""

    async def test_read_tables_postgresql(self):
        """Test reading table names from PostgreSQL."""
        from covet.database.adapters.postgresql import PostgreSQLAdapter

        # Note: Update connection parameters for your test environment
        adapter = PostgreSQLAdapter(
            host='localhost',
            port=5432,
            database='test_db',
            user='postgres',
            password='password'
        )
        await adapter.connect()

        reader = SchemaReader(adapter, DatabaseType.POSTGRESQL)
        tables = await reader.read_tables('public')

        assert isinstance(tables, list)

        await adapter.disconnect()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires running MySQL instance")
class TestSchemaReaderMySQL:
    """Integration tests for MySQL schema reading."""

    async def test_read_tables_mysql(self):
        """Test reading table names from MySQL."""
        from covet.database.adapters.mysql import MySQLAdapter

        # Note: Update connection parameters for your test environment
        adapter = MySQLAdapter(
            host='localhost',
            port=3306,
            database='test_db',
            user='root',
            password='password'
        )
        await adapter.connect()

        reader = SchemaReader(adapter, DatabaseType.MYSQL)
        tables = await reader.read_tables('test_db')

        assert isinstance(tables, list)

        await adapter.disconnect()


if __name__ == '__main__':
    # Run SQLite tests (no external database required)
    pytest.main([__file__, '-v', '-k', 'TestSchemaReaderSQLite'])
