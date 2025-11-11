"""
Schema Reader Usage Examples

This file demonstrates practical usage of the SchemaReader for various
database introspection scenarios.
"""

import asyncio
from pathlib import Path

from src.covet.database.adapters.postgresql import PostgreSQLAdapter
from src.covet.database.adapters.mysql import MySQLAdapter
from src.covet.database.adapters.sqlite import SQLiteAdapter
from src.covet.database.migrations.schema_reader import (
    SchemaReader,
    DatabaseType,
)


async def example_postgresql():
    """Example: Read schema from PostgreSQL database."""
    print("=" * 60)
    print("PostgreSQL Schema Introspection Example")
    print("=" * 60)

    # Initialize adapter
    adapter = PostgreSQLAdapter(
        host='localhost',
        port=5432,
        database='mydb',
        user='postgres',
        password='secret',
        min_pool_size=2,
        max_pool_size=5
    )

    try:
        await adapter.connect()
        print(f"Connected to PostgreSQL: {adapter.database}")

        # Create schema reader
        reader = SchemaReader(adapter, DatabaseType.POSTGRESQL)

        # Read all tables
        print("\n1. Reading all tables in 'public' schema...")
        tables = await reader.read_tables('public')
        print(f"   Found {len(tables)} tables: {', '.join(tables)}")

        if tables:
            # Read first table in detail
            table_name = tables[0]
            print(f"\n2. Reading complete definition for '{table_name}'...")
            table_def = await reader.read_table_complete(table_name, 'public')

            print(f"\n   Table: {table_def.schema}.{table_def.name}")
            print(f"   Columns: {len(table_def.columns)}")
            print(f"   Indexes: {len(table_def.indexes)}")
            print(f"   Constraints: {len(table_def.constraints)}")
            print(f"   Foreign Keys: {len(table_def.foreign_keys)}")

            # Display columns
            print("\n   Column Details:")
            for col in table_def.columns:
                nullable = "NULL" if col.is_nullable else "NOT NULL"
                pk = " [PK]" if col.is_primary_key else ""
                auto = " [AUTO]" if col.is_auto_increment else ""
                default = f" DEFAULT {col.default_value}" if col.default_value else ""
                print(f"     - {col.name}: {col.data_type} {nullable}{pk}{auto}{default}")

            # Display primary key
            pk_cols = table_def.get_primary_key_columns()
            if pk_cols:
                print(f"\n   Primary Key: ({', '.join(pk_cols)})")

            # Display indexes
            if table_def.indexes:
                print("\n   Indexes:")
                for idx in table_def.indexes:
                    unique = "UNIQUE " if idx.is_unique else ""
                    pk = "[PK] " if idx.is_primary else ""
                    print(f"     - {pk}{unique}{idx.name} ON ({', '.join(idx.columns)})")

            # Display foreign keys
            if table_def.foreign_keys:
                print("\n   Foreign Keys:")
                for fk in table_def.foreign_keys:
                    print(f"     - {fk.name}:")
                    print(f"       {', '.join(fk.columns)} -> "
                          f"{fk.referenced_table}({', '.join(fk.referenced_columns)})")
                    print(f"       ON DELETE {fk.on_delete}, ON UPDATE {fk.on_update}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await adapter.disconnect()
        print("\n" + "=" * 60)


async def example_mysql():
    """Example: Read schema from MySQL database."""
    print("=" * 60)
    print("MySQL Schema Introspection Example")
    print("=" * 60)

    # Initialize adapter
    adapter = MySQLAdapter(
        host='localhost',
        port=3306,
        database='mydb',
        user='root',
        password='secret',
        min_pool_size=2,
        max_pool_size=5
    )

    try:
        await adapter.connect()
        print(f"Connected to MySQL: {adapter.database}")

        # Create schema reader
        reader = SchemaReader(adapter, DatabaseType.MYSQL)

        # Read all tables
        print("\n1. Reading all tables...")
        tables = await reader.read_tables('mydb')
        print(f"   Found {len(tables)} tables: {', '.join(tables)}")

        if tables:
            # Read columns for first table
            table_name = tables[0]
            print(f"\n2. Reading columns for '{table_name}'...")
            columns = await reader.read_columns(table_name, 'mydb')

            for col in columns:
                nullable = "NULL" if col.is_nullable else "NOT NULL"
                pk = " [PK]" if col.is_primary_key else ""
                auto = " [AUTO_INCREMENT]" if col.is_auto_increment else ""
                print(f"   - {col.name}: {col.data_type} {nullable}{pk}{auto}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await adapter.disconnect()
        print("\n" + "=" * 60)


async def example_sqlite():
    """Example: Read schema from SQLite database."""
    print("=" * 60)
    print("SQLite Schema Introspection Example")
    print("=" * 60)

    # Create test database
    db_path = "/tmp/test_schema_reader.db"
    adapter = SQLiteAdapter(database=db_path)

    try:
        await adapter.connect()
        print(f"Connected to SQLite: {db_path}")

        # Create sample schema
        print("\n1. Creating sample schema...")
        await adapter.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await adapter.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                published BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        await adapter.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)
        """)

        print("   Created tables: users, posts")

        # Create schema reader
        reader = SchemaReader(adapter, DatabaseType.SQLITE)

        # Read complete schema
        print("\n2. Reading complete schema...")
        all_tables = await reader.read_schema_complete()

        for table in all_tables:
            print(f"\n   Table: {table.name}")
            print(f"   Columns ({len(table.columns)}):")
            for col in table.columns:
                nullable = "NULL" if col.is_nullable else "NOT NULL"
                pk = " [PK]" if col.is_primary_key else ""
                print(f"     - {col.name}: {col.data_type} {nullable}{pk}")

            if table.indexes:
                print(f"   Indexes ({len(table.indexes)}):")
                for idx in table.indexes:
                    unique = "UNIQUE " if idx.is_unique else ""
                    print(f"     - {unique}{idx.name} ON ({', '.join(idx.columns)})")

            if table.foreign_keys:
                print(f"   Foreign Keys ({len(table.foreign_keys)}):")
                for fk in table.foreign_keys:
                    print(f"     - {', '.join(fk.columns)} -> "
                          f"{fk.referenced_table}({', '.join(fk.referenced_columns)})")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await adapter.disconnect()
        print("\n" + "=" * 60)


async def example_migration_generation():
    """Example: Generate migration SQL from schema."""
    print("=" * 60)
    print("Migration Generation Example")
    print("=" * 60)

    # Create test database
    db_path = "/tmp/test_migration_gen.db"
    adapter = SQLiteAdapter(database=db_path)

    try:
        await adapter.connect()

        # Create sample schema
        await adapter.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
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

        # Read schema
        reader = SchemaReader(adapter, DatabaseType.SQLITE)
        tables = await reader.read_schema_complete()

        print("\nGenerated Migration SQL:")
        print("-" * 60)

        # Generate CREATE TABLE statements
        for table in tables:
            print(f"\n-- Table: {table.name}")
            print(f"CREATE TABLE {table.name} (")

            # Column definitions
            col_defs = []
            for col in table.columns:
                parts = [f"  {col.name}", col.data_type]

                if not col.is_nullable:
                    parts.append("NOT NULL")

                if col.default_value:
                    parts.append(f"DEFAULT {col.default_value}")

                if col.is_primary_key:
                    parts.append("PRIMARY KEY")

                if col.is_auto_increment:
                    parts.append("AUTOINCREMENT")

                col_defs.append(" ".join(parts))

            print(",\n".join(col_defs))
            print(");")

            # Indexes (non-primary)
            for idx in table.indexes:
                if not idx.is_primary:
                    unique = "UNIQUE " if idx.is_unique else ""
                    print(f"CREATE {unique}INDEX {idx.name} "
                          f"ON {table.name} ({', '.join(idx.columns)});")

            # Foreign keys (for databases that support ALTER TABLE ADD CONSTRAINT)
            # SQLite requires them in CREATE TABLE, but showing the pattern
            for fk in table.foreign_keys:
                print(f"-- Foreign Key: {fk.name}")
                print(f"-- FOREIGN KEY ({', '.join(fk.columns)}) "
                      f"REFERENCES {fk.referenced_table}({', '.join(fk.referenced_columns)}) "
                      f"ON DELETE {fk.on_delete} ON UPDATE {fk.on_update}")

        print("\n" + "-" * 60)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await adapter.disconnect()
        print("\n" + "=" * 60)


async def example_type_normalization():
    """Example: Demonstrate type normalization across databases."""
    print("=" * 60)
    print("Type Normalization Example")
    print("=" * 60)

    # Create readers for different databases (without connecting)
    readers = {
        'PostgreSQL': SchemaReader(None, DatabaseType.POSTGRESQL),
        'MySQL': SchemaReader(None, DatabaseType.MYSQL),
        'SQLite': SchemaReader(None, DatabaseType.SQLITE),
    }

    print("\nType Normalization Mappings:")
    print("-" * 60)

    test_types = [
        ('integer', 'int', 'INTEGER'),
        ('bigint', 'bigint', 'INTEGER'),
        ('character varying', 'varchar', 'TEXT'),
        ('timestamp without time zone', 'datetime', 'TEXT'),
        ('boolean', 'tinyint(1)', 'INTEGER'),
        ('text', 'text', 'TEXT'),
        ('numeric', 'decimal', 'NUMERIC'),
        ('real', 'float', 'REAL'),
    ]

    for pg_type, mysql_type, sqlite_type in test_types:
        print(f"\nNative Types -> Normalized:")
        print(f"  PostgreSQL: {pg_type:30} -> {readers['PostgreSQL']._normalize_type(pg_type)}")
        print(f"  MySQL:      {mysql_type:30} -> {readers['MySQL']._normalize_type(mysql_type)}")
        print(f"  SQLite:     {sqlite_type:30} -> {readers['SQLite']._normalize_type(sqlite_type)}")

    print("\n" + "=" * 60)


async def main():
    """Run all examples."""
    print("\n")
    print("*" * 60)
    print("Schema Reader - Usage Examples")
    print("*" * 60)
    print("\n")

    # Note: Uncomment the examples you want to run
    # Most require actual database connections

    # Example 1: Type normalization (no DB required)
    await example_type_normalization()

    # Example 2: SQLite (no external DB required)
    await example_sqlite()

    # Example 3: Migration generation (no external DB required)
    await example_migration_generation()

    # Example 4: PostgreSQL (requires running PostgreSQL)
    # await example_postgresql()

    # Example 5: MySQL (requires running MySQL)
    # await example_mysql()

    print("\n")
    print("*" * 60)
    print("Examples completed!")
    print("*" * 60)
    print("\n")


if __name__ == '__main__':
    asyncio.run(main())
