"""
CovetPy Migration System - Comprehensive Example
================================================

This example demonstrates the complete migration workflow including:
1. Creating models
2. Generating migrations automatically
3. Applying migrations
4. Rolling back migrations
5. Manual migration creation
6. Data migrations

Prerequisites:
-------------
pip install covetpy

Running this example:
--------------------
python examples/migration_example.py
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_1_basic_usage():
    """Example 1: Basic Migration Usage"""
    logger.info("=" * 70)
    logger.info("Example 1: Basic Migration Usage")
    logger.info("=" * 70)
    
    from covet.migrations import MigrationManager
    from covet.database.adapters.sqlite import SQLiteAdapter
    
    # Initialize database
    adapter = SQLiteAdapter('example_app.db')
    await adapter.connect()
    
    # Create migration manager
    manager = MigrationManager(
        adapter=adapter,
        dialect='sqlite',
        migrations_dir='./example_migrations',
        enable_locking=False,  # Disable for demo
        enable_backup=False,   # Disable for demo
    )
    
    # Create a simple migration
    logger.info("\n1. Creating initial migration...")
    migration_file = await manager.create_migration(
        name="create_users_table",
        forward_sql=[
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "CREATE INDEX idx_users_email ON users(email)",
        ],
        backward_sql=[
            "DROP INDEX IF EXISTS idx_users_email",
            "DROP TABLE IF EXISTS users",
        ]
    )
    logger.info(f"Created migration: {migration_file}")
    
    # Check migration status
    logger.info("\n2. Checking migration status...")
    status = await manager.get_status()
    for migration in status:
        status_mark = "✓" if migration.applied else "✗"
        logger.info(f"  [{status_mark}] {migration.name}")
    
    # Apply migrations (dry run first)
    logger.info("\n3. Running dry-run...")
    result = await manager.migrate_up(dry_run=True)
    logger.info(f"Would apply: {result['applied']}")
    
    # Apply for real
    logger.info("\n4. Applying migrations...")
    result = await manager.migrate_up()
    if result['success']:
        logger.info(f"✓ Successfully applied {len(result['applied'])} migrations")
        logger.info(f"  Duration: {result['duration']:.2f}s")
    else:
        logger.error(f"✗ Migration failed: {result['error']}")
    
    # Verify table was created
    logger.info("\n5. Verifying table creation...")
    tables = await adapter.get_table_list()
    logger.info(f"Tables in database: {tables}")
    
    # Clean up
    await adapter.disconnect()
    logger.info("\n✓ Example 1 completed successfully!\n")


async def example_2_with_models():
    """Example 2: Auto-generating migrations from ORM models"""
    logger.info("=" * 70)
    logger.info("Example 2: Auto-generating migrations from ORM models")
    logger.info("=" * 70)
    
    from covet.migrations import makemigrations, migrate, showmigrations
    from covet.database.adapters.sqlite import SQLiteAdapter
    from covet.database.orm.models import Model
    from covet.database.orm.fields import (
        CharField, EmailField, DateTimeField, BooleanField
    )
    
    # Define models
    class User(Model):
        """User model"""
        username = CharField(max_length=100, unique=True)
        email = EmailField(unique=True)
        is_active = BooleanField(default=True)
        created_at = DateTimeField(auto_now_add=True)
        
        class Meta:
            db_table = 'users'
    
    class Post(Model):
        """Post model"""
        title = CharField(max_length=255)
        content = CharField(max_length=10000)
        created_at = DateTimeField(auto_now_add=True)
        
        class Meta:
            db_table = 'posts'
    
    # Initialize database
    adapter = SQLiteAdapter('example_orm.db')
    await adapter.connect()
    
    logger.info("\n1. Generating migrations from models...")
    migration_file = await makemigrations(
        models=[User, Post],
        adapter=adapter,
        migrations_dir='./orm_migrations',
        dialect='sqlite',
        name='initial_schema'
    )
    
    if migration_file:
        logger.info(f"✓ Created migration: {migration_file}")
    else:
        logger.info("No changes detected")
    
    logger.info("\n2. Showing migration status...")
    await showmigrations(adapter, './orm_migrations')
    
    logger.info("\n3. Applying migrations...")
    applied = await migrate(adapter, './orm_migrations')
    logger.info(f"✓ Applied {len(applied)} migrations")
    
    # Test the models
    logger.info("\n4. Testing model operations...")
    user = User(
        username='alice',
        email='alice@example.com',
        is_active=True
    )
    await user.save()
    logger.info(f"✓ Created user: {user}")
    
    post = Post(
        title='My First Post',
        content='Hello, World!'
    )
    await post.save()
    logger.info(f"✓ Created post: {post}")
    
    # Clean up
    await adapter.disconnect()
    logger.info("\n✓ Example 2 completed successfully!\n")


async def example_3_rollback():
    """Example 3: Rolling back migrations"""
    logger.info("=" * 70)
    logger.info("Example 3: Rolling back migrations")
    logger.info("=" * 70)
    
    from covet.migrations import MigrationManager, rollback
    from covet.database.adapters.sqlite import SQLiteAdapter
    
    # Initialize database
    adapter = SQLiteAdapter('example_rollback.db')
    await adapter.connect()
    
    # Create migration manager
    manager = MigrationManager(
        adapter=adapter,
        dialect='sqlite',
        migrations_dir='./rollback_migrations',
        enable_locking=False,
        enable_backup=True,  # Enable backup for rollback safety
    )
    
    # Create and apply some migrations
    logger.info("\n1. Creating migrations...")
    
    await manager.create_migration(
        name="create_products",
        forward_sql=["CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT)"],
        backward_sql=["DROP TABLE products"]
    )
    
    await manager.create_migration(
        name="add_price_column",
        forward_sql=["ALTER TABLE products ADD COLUMN price REAL"],
        backward_sql=["ALTER TABLE products DROP COLUMN price"]
    )
    
    logger.info("\n2. Applying migrations...")
    result = await manager.migrate_up()
    logger.info(f"Applied: {result['applied']}")
    
    logger.info("\n3. Checking status...")
    status = await manager.get_status()
    for migration in status:
        if migration.applied:
            logger.info(f"  [✓] {migration.name}")
    
    logger.info("\n4. Rolling back last migration...")
    result = await manager.migrate_down(steps=1)
    if result['success']:
        logger.info(f"✓ Rolled back: {result['rolled_back']}")
    
    logger.info("\n5. Final status:")
    status = await manager.get_status()
    for migration in status:
        mark = "✓" if migration.applied else "✗"
        logger.info(f"  [{mark}] {migration.name}")
    
    # Clean up
    await adapter.disconnect()
    logger.info("\n✓ Example 3 completed successfully!\n")


async def example_4_data_migration():
    """Example 4: Data migration"""
    logger.info("=" * 70)
    logger.info("Example 4: Data Migration")
    logger.info("=" * 70)
    
    from covet.migrations import Migration, MigrationManager
    from covet.database.adapters.sqlite import SQLiteAdapter
    
    # Initialize database
    adapter = SQLiteAdapter('example_data.db')
    await adapter.connect()
    
    # Create initial table
    await adapter.execute(
        """
        CREATE TABLE IF NOT EXISTS old_users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        )
        """
    )
    
    # Insert some test data
    await adapter.execute(
        "INSERT INTO old_users (name, email) VALUES (?, ?)",
        ['Alice Smith', 'alice@example.com']
    )
    await adapter.execute(
        "INSERT INTO old_users (name, email) VALUES (?, ?)",
        ['Bob Jones', 'bob@example.com']
    )
    
    logger.info("\n1. Creating new schema...")
    
    # Create data migration manually
    migration_dir = Path('./data_migrations')
    migration_dir.mkdir(exist_ok=True)
    
    migration_content = '''"""
Data Migration: Split name into first_name and last_name
"""
from covet.migrations import Migration

class SplitNameFieldsMigration(Migration):
    """Split name into first_name and last_name."""
    
    dependencies = []
    
    async def apply(self, adapter):
        """Forward migration."""
        # Create new table
        await adapter.execute("""
            CREATE TABLE new_users (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT
            )
        """)
        
        # Migrate data
        old_users = await adapter.fetch_all("SELECT * FROM old_users")
        
        for user in old_users:
            name_parts = user['name'].split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            await adapter.execute(
                "INSERT INTO new_users (id, first_name, last_name, email) VALUES (?, ?, ?, ?)",
                [user['id'], first_name, last_name, user['email']]
            )
        
        # Drop old table
        await adapter.execute("DROP TABLE old_users")
        
        # Rename new table
        await adapter.execute("ALTER TABLE new_users RENAME TO users")
    
    async def rollback(self, adapter):
        """Backward migration."""
        # Recreate old table
        await adapter.execute("""
            CREATE TABLE old_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        
        # Migrate data back
        users = await adapter.fetch_all("SELECT * FROM users")
        
        for user in users:
            name = f"{user['first_name']} {user['last_name']}".strip()
            await adapter.execute(
                "INSERT INTO old_users (id, name, email) VALUES (?, ?, ?)",
                [user['id'], name, user['email']]
            )
        
        # Drop new table
        await adapter.execute("DROP TABLE users")
'''
    
    # Write migration file
    migration_file = migration_dir / '2025_01_01_000001_split_name_fields.py'
    with open(migration_file, 'w') as f:
        f.write(migration_content)
    
    logger.info(f"✓ Created data migration: {migration_file}")
    
    # Apply migration
    logger.info("\n2. Applying data migration...")
    manager = MigrationManager(
        adapter=adapter,
        dialect='sqlite',
        migrations_dir=str(migration_dir),
        enable_locking=False,
        enable_backup=True,
    )
    
    result = await manager.migrate_up()
    if result['success']:
        logger.info(f"✓ Applied data migration")
    
    # Verify results
    logger.info("\n3. Verifying migrated data...")
    users = await adapter.fetch_all("SELECT * FROM users")
    for user in users:
        logger.info(f"  User: {user['first_name']} {user['last_name']} <{user['email']}>")
    
    # Clean up
    await adapter.disconnect()
    logger.info("\n✓ Example 4 completed successfully!\n")


async def example_5_advanced_operations():
    """Example 5: Advanced migration operations"""
    logger.info("=" * 70)
    logger.info("Example 5: Advanced Migration Operations")
    logger.info("=" * 70)
    
    from covet.migrations import MigrationManager
    from covet.database.adapters.sqlite import SQLiteAdapter
    
    # Initialize database
    adapter = SQLiteAdapter('example_advanced.db')
    await adapter.connect()
    
    manager = MigrationManager(
        adapter=adapter,
        dialect='sqlite',
        migrations_dir='./advanced_migrations',
        enable_locking=True,
        enable_backup=True,
    )
    
    logger.info("\n1. Creating multiple migrations...")
    
    # Create initial schema
    await manager.create_migration(
        name="create_orders",
        forward_sql=[
            """
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_email TEXT NOT NULL,
                total REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        ],
        backward_sql=["DROP TABLE orders"]
    )
    
    # Add indexes
    await manager.create_migration(
        name="add_orders_indexes",
        forward_sql=[
            "CREATE INDEX idx_orders_email ON orders(customer_email)",
            "CREATE INDEX idx_orders_status ON orders(status)",
            "CREATE INDEX idx_orders_created ON orders(created_at)",
        ],
        backward_sql=[
            "DROP INDEX idx_orders_created",
            "DROP INDEX idx_orders_status",
            "DROP INDEX idx_orders_email",
        ]
    )
    
    # Add constraint
    await manager.create_migration(
        name="add_order_items",
        forward_sql=[
            """
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
            """,
            "CREATE INDEX idx_order_items_order ON order_items(order_id)",
        ],
        backward_sql=[
            "DROP INDEX idx_order_items_order",
            "DROP TABLE order_items",
        ]
    )
    
    logger.info("\n2. Showing migration plan...")
    status = await manager.get_status()
    pending = [s for s in status if not s.applied]
    logger.info(f"  Pending migrations: {len(pending)}")
    for migration in pending:
        logger.info(f"    - {migration.name}")
    
    logger.info("\n3. Applying migrations with monitoring...")
    result = await manager.migrate_up()
    
    if result['success']:
        logger.info(f"✓ Success!")
        logger.info(f"  Applied: {len(result['applied'])} migrations")
        logger.info(f"  Duration: {result['duration']:.3f}s")
        for name in result['applied']:
            logger.info(f"    ✓ {name}")
    else:
        logger.error(f"✗ Failed: {result['error']}")
    
    logger.info("\n4. Final schema:")
    tables = await adapter.get_table_list()
    for table in tables:
        if not table.startswith('_'):
            logger.info(f"  Table: {table}")
            columns = await adapter.get_table_info(table)
            for col in columns:
                logger.info(f"    - {col['name']}: {col['type']}")
    
    # Clean up
    await adapter.disconnect()
    logger.info("\n✓ Example 5 completed successfully!\n")


async def main():
    """Run all examples"""
    logger.info("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         CovetPy Migration System - Comprehensive Examples           ║
║                                                                      ║
║  Demonstrating production-ready database migration workflows        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        await example_1_basic_usage()
        await example_2_with_models()
        await example_3_rollback()
        await example_4_data_migration()
        await example_5_advanced_operations()
        
        logger.info("=" * 70)
        logger.info("All examples completed successfully!")
        logger.info("=" * 70)
        logger.info("""
Summary of what we demonstrated:
1. Basic migration creation and application
2. Auto-generating migrations from ORM models
3. Rolling back migrations safely
4. Complex data migrations
5. Advanced operations with multiple tables and constraints

Next steps:
- Review the generated migration files in each directory
- Try creating your own migrations
- Integrate migrations into your application
- Set up CI/CD with migration automation

For production use:
- Enable locking to prevent concurrent migrations
- Enable backups for rollback safety
- Test migrations on staging before production
- Use dry-run mode to preview changes
- Monitor migration performance
- Keep migrations small and focused

Documentation: https://covetpy.readthedocs.io/migrations/
        """)
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
