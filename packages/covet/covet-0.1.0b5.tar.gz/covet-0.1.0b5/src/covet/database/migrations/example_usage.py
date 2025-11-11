"""
CovetPy Migrations - Complete Usage Example

This file demonstrates the complete migration workflow with all supported features.
Run this file to see migrations in action with a real database.

Requirements:
    - PostgreSQL, MySQL, or SQLite database
    - CovetPy ORM models defined
    - Database adapter configured

Usage:
    python example_usage.py
"""

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# EXAMPLE 1: Basic Migration Workflow
# =============================================================================


async def example_basic_workflow():
    """
    Demonstrates the basic migration workflow:
    1. Define models
    2. Generate migrations
    3. Apply migrations
    4. Show status
    """
    from covet.database.adapters.sqlite import SQLiteAdapter
    from covet.database.migrations.commands import (
        makemigrations,
        migrate,
        showmigrations,
    )
    from covet.database.orm import Index, Model
    from covet.database.orm.fields import (
        BooleanField,
        CharField,
        DateTimeField,
        EmailField,
        IntegerField,
        TextField,
    )
    from covet.database.orm.relationships import CASCADE, ForeignKey

    logger.info("=" * 70)
    logger.info("EXAMPLE 1: Basic Migration Workflow")
    logger.info("=" * 70)

    # Define models
    class User(Model):
        username = CharField(max_length=100, unique=True)
        email = EmailField(unique=True)
        full_name = CharField(max_length=200)
        is_active = BooleanField(default=True)
        created_at = DateTimeField(auto_now_add=True)

        class Meta:
            db_table = "users"
            indexes = [Index(fields=["username"]), Index(fields=["email"])]

    class Post(Model):
        title = CharField(max_length=200)
        content = TextField()
        author = ForeignKey(User, on_delete=CASCADE, related_name="posts")
        created_at = DateTimeField(auto_now_add=True)
        views = IntegerField(default=0)

        class Meta:
            db_table = "posts"
            indexes = [
                Index(fields=["created_at"]),
                Index(fields=["author_id", "created_at"]),
            ]

    # Create temporary database
    migrations_dir = "./example_migrations"
    Path(migrations_dir).mkdir(exist_ok=True)

    # Connect to SQLite (for easy testing)
    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    try:
        # Step 1: Generate migrations
        logger.info("\n1. Generating migrations...")
        migration_file = await makemigrations(
            models=[User, Post],
            adapter=adapter,
            migrations_dir=migrations_dir,
            dialect="sqlite",
            name="initial",
        )

        if migration_file:
            logger.info(f"✓ Created: {migration_file}")
        else:
            logger.info("No changes detected")

        # Step 2: Apply migrations
        logger.info("\n2. Applying migrations...")
        applied = await migrate(adapter, migrations_dir)
        logger.info(f"✓ Applied {len(applied)} migrations")

        # Step 3: Show status
        logger.info("\n3. Migration status:")
        await showmigrations(adapter, migrations_dir, verbose=True)

        logger.info("\n✓ Example 1 completed successfully!")

    finally:
        await adapter.disconnect()


# =============================================================================
# EXAMPLE 2: Schema Evolution (Add Column)
# =============================================================================


async def example_schema_evolution():
    """
    Demonstrates schema evolution:
    1. Start with basic model
    2. Add new column
    3. Generate migration for change
    4. Apply migration
    """
    from covet.database.adapters.sqlite import SQLiteAdapter
    from covet.database.migrations.commands import makemigrations, migrate
    from covet.database.orm import Model
    from covet.database.orm.fields import CharField, EmailField, IntegerField

    logger.info("=" * 70)
    logger.info("EXAMPLE 2: Schema Evolution")
    logger.info("=" * 70)

    migrations_dir = "./example_migrations_2"
    Path(migrations_dir).mkdir(exist_ok=True)

    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    try:
        # Initial model
        class User(Model):
            username = CharField(max_length=100)
            email = EmailField()

            class Meta:
                db_table = "users"

        # First migration
        logger.info("\n1. Creating initial table...")
        await makemigrations(
            models=[User],
            adapter=adapter,
            migrations_dir=migrations_dir,
            dialect="sqlite",
            name="initial",
        )
        await migrate(adapter, migrations_dir)

        # Evolve model - add age column
        class UserV2(Model):
            username = CharField(max_length=100)
            email = EmailField()
            age = IntegerField(nullable=True, default=0)  # NEW COLUMN

            class Meta:
                db_table = "users"

        # Generate migration for new column
        logger.info("\n2. Adding age column...")
        migration_file = await makemigrations(
            models=[UserV2],
            adapter=adapter,
            migrations_dir=migrations_dir,
            dialect="sqlite",
            name="add_age_column",
        )

        if migration_file:
            logger.info(f"✓ Generated: {migration_file}")
            await migrate(adapter, migrations_dir)
            logger.info("✓ Applied migration")
        else:
            logger.info("No changes detected")

        logger.info("\n✓ Example 2 completed successfully!")

    finally:
        await adapter.disconnect()


# =============================================================================
# EXAMPLE 3: Rollback
# =============================================================================


async def example_rollback():
    """
    Demonstrates migration rollback:
    1. Apply migrations
    2. Rollback last migration
    3. Show status
    """
    from covet.database.adapters.sqlite import SQLiteAdapter
    from covet.database.migrations.commands import (
        makemigrations,
        migrate,
        rollback,
        showmigrations,
    )
    from covet.database.orm import Model
    from covet.database.orm.fields import CharField

    logger.info("=" * 70)
    logger.info("EXAMPLE 3: Migration Rollback")
    logger.info("=" * 70)

    migrations_dir = "./example_migrations_3"
    Path(migrations_dir).mkdir(exist_ok=True)

    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    try:

        class User(Model):
            username = CharField(max_length=100)

            class Meta:
                db_table = "users"

        # Apply migrations
        logger.info("\n1. Creating and applying migrations...")
        await makemigrations(
            models=[User],
            adapter=adapter,
            migrations_dir=migrations_dir,
            dialect="sqlite",
            name="create_user",
        )
        applied = await migrate(adapter, migrations_dir)
        logger.info(f"✓ Applied {len(applied)} migrations")

        # Show status
        logger.info("\n2. Status before rollback:")
        await showmigrations(adapter, migrations_dir)

        # Rollback
        logger.info("\n3. Rolling back last migration...")
        rolled_back = await rollback(adapter, migrations_dir=migrations_dir, steps=1)
        logger.info(f"✓ Rolled back {len(rolled_back)} migrations")

        # Show status after rollback
        logger.info("\n4. Status after rollback:")
        await showmigrations(adapter, migrations_dir)

        logger.info("\n✓ Example 3 completed successfully!")

    finally:
        await adapter.disconnect()


# =============================================================================
# EXAMPLE 4: Multi-Database Support
# =============================================================================


async def example_multi_database():
    """
    Demonstrates migration with different database backends:
    - PostgreSQL
    - MySQL
    - SQLite
    """
    from covet.database.migrations.generator import MigrationGenerator
    from covet.database.migrations.model_reader import ModelReader
    from covet.database.orm import Model
    from covet.database.orm.fields import CharField, IntegerField

    logger.info("=" * 70)
    logger.info("EXAMPLE 4: Multi-Database Support")
    logger.info("=" * 70)

    class User(Model):
        username = CharField(max_length=100, unique=True)
        age = IntegerField(nullable=True)

        class Meta:
            db_table = "users"

    # Generate SQL for all three databases
    reader = ModelReader()

    for dialect in ["postgresql", "mysql", "sqlite"]:
        logger.info(f"\n{dialect.upper()} Schema:")
        logger.info("-" * 40)

        # Read model schema
        schema = reader.read_model(User, dialect=dialect)

        # Generate CREATE TABLE SQL
        generator = MigrationGenerator(dialect=dialect)

        if dialect == "postgresql":
            from covet.database.migrations.generator import PostgreSQLGenerator

            sql_gen = PostgreSQLGenerator()
        elif dialect == "mysql":
            from covet.database.migrations.generator import MySQLGenerator

            sql_gen = MySQLGenerator()
        else:
            from covet.database.migrations.generator import SQLiteGenerator

            sql_gen = SQLiteGenerator()

        forward_sql, _ = sql_gen.generate_create_table("users", schema)
        logger.info(forward_sql)

    logger.info("\n✓ Example 4 completed successfully!")


# =============================================================================
# EXAMPLE 5: Foreign Key Relationships
# =============================================================================


async def example_foreign_keys():
    """
    Demonstrates foreign key handling:
    - Proper constraint ordering
    - CASCADE behavior
    - Index creation
    """
    from covet.database.adapters.sqlite import SQLiteAdapter
    from covet.database.migrations.commands import makemigrations, migrate
    from covet.database.orm import Index, Model
    from covet.database.orm.fields import CharField, TextField
    from covet.database.orm.relationships import CASCADE, ForeignKey

    logger.info("=" * 70)
    logger.info("EXAMPLE 5: Foreign Key Relationships")
    logger.info("=" * 70)

    migrations_dir = "./example_migrations_5"
    Path(migrations_dir).mkdir(exist_ok=True)

    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    try:

        class Author(Model):
            name = CharField(max_length=100)

            class Meta:
                db_table = "authors"

        class Book(Model):
            title = CharField(max_length=200)
            author = ForeignKey(Author, on_delete=CASCADE, related_name="books")

            class Meta:
                db_table = "books"

        class Review(Model):
            book = ForeignKey(Book, on_delete=CASCADE, related_name="reviews")
            content = TextField()

            class Meta:
                db_table = "reviews"

        logger.info("\n1. Creating tables with foreign keys...")
        migration_file = await makemigrations(
            models=[Author, Book, Review],
            adapter=adapter,
            migrations_dir=migrations_dir,
            dialect="sqlite",
            name="create_book_system",
        )

        if migration_file:
            logger.info(f"✓ Generated: {migration_file}")

            # Read and display the generated SQL
            with open(migration_file, "r") as f:
                logger.info("\nGenerated migration SQL:")
                logger.info("-" * 40)
                in_forward = False
                for line in f:
                    if "forward_sql = [" in line:
                        in_forward = True
                    elif in_forward and "]" in line:
                        break
                    elif in_forward and line.strip():
                        logger.info(line.rstrip())

            await migrate(adapter, migrations_dir)
            logger.info("\n✓ Applied migration")

        logger.info("\n✓ Example 5 completed successfully!")

    finally:
        await adapter.disconnect()


# =============================================================================
# EXAMPLE 6: Dry Run Mode
# =============================================================================


async def example_dry_run():
    """
    Demonstrates dry run mode:
    - Preview changes without applying
    - Useful for code review
    """
    from covet.database.adapters.sqlite import SQLiteAdapter
    from covet.database.migrations.commands import makemigrations
    from covet.database.orm import Model
    from covet.database.orm.fields import CharField, IntegerField

    logger.info("=" * 70)
    logger.info("EXAMPLE 6: Dry Run Mode")
    logger.info("=" * 70)

    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    try:

        class Product(Model):
            name = CharField(max_length=200)
            price = IntegerField()
            quantity = IntegerField()

            class Meta:
                db_table = "products"

        logger.info("\n1. Dry run - preview changes without creating files...")
        migration_file = await makemigrations(
            models=[Product],
            adapter=adapter,
            migrations_dir="./migrations_dry",
            dialect="sqlite",
            name="create_product",
            dry_run=True,  # Preview only
        )

        if migration_file:
            logger.info(f"Would create: {migration_file}")
        else:
            logger.info("✓ Dry run completed - no files created")

        logger.info("\n✓ Example 6 completed successfully!")

    finally:
        await adapter.disconnect()


# =============================================================================
# Run All Examples
# =============================================================================


async def main():
    """Run all examples."""
    logger.info("\n" + "=" * 70)
    logger.info("CovetPy Migrations - Complete Examples")
    logger.info("=" * 70 + "\n")

    try:
        await example_basic_workflow()
        await example_schema_evolution()
        await example_rollback()
        await example_multi_database()
        await example_foreign_keys()
        await example_dry_run()

        logger.info("\n" + "=" * 70)
        logger.info("✓ All examples completed successfully!")
        logger.info("=" * 70 + "\n")

    except Exception as e:
        logger.error(f"\n✗ Error running examples: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
