"""
SQLite Bulk Operations Demo

Demonstrates the 5 new production-ready methods for SQLite adapter:
1. bulk_create() - Bulk insert with duplicate handling
2. bulk_update() - Bulk update with composite keys
3. create_or_update() - Single record UPSERT
4. bulk_create_or_update() - Bulk UPSERT operations
5. health_check() - Comprehensive database health monitoring

Requirements:
    pip install aiosqlite
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.covet.database.adapters.sqlite import SQLiteAdapter

# Configure logging to see the operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def demo_bulk_create():
    """Demonstrate bulk_create with batch processing and duplicate handling."""
    print("\n" + "=" * 80)
    print("DEMO 1: bulk_create() - Bulk Insert Operations")
    print("=" * 80)

    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    # Create test table
    await adapter.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER
        )
    """)

    # Prepare test data (1000 users)
    records = [
        {"email": f"user{i}@example.com", "name": f"User {i}", "age": 20 + (i % 50)}
        for i in range(1, 1001)
    ]

    # Bulk insert with batch processing
    print(f"\nInserting {len(records)} records with batch_size=500...")
    inserted = await adapter.bulk_create("users", records, batch_size=500)
    print(f"Result: Inserted {inserted} rows")

    # Try inserting duplicates with ignore_duplicates=True
    duplicate_records = records[:100]  # First 100 records again
    print(f"\nAttempting to insert {len(duplicate_records)} duplicate records with ignore_duplicates=True...")
    inserted = await adapter.bulk_create("users", duplicate_records, ignore_duplicates=True)
    print(f"Result: Inserted {inserted} rows (duplicates were ignored)")

    # Verify total count
    total = await adapter.fetch_value("SELECT COUNT(*) FROM users")
    print(f"\nTotal users in database: {total}")

    await adapter.disconnect()


async def demo_bulk_update():
    """Demonstrate bulk_update with composite keys."""
    print("\n" + "=" * 80)
    print("DEMO 2: bulk_update() - Bulk Update Operations")
    print("=" * 80)

    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    # Create test table with composite key
    await adapter.execute("""
        CREATE TABLE products (
            sku TEXT NOT NULL,
            warehouse_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL,
            last_updated TEXT,
            PRIMARY KEY (sku, warehouse_id)
        )
    """)

    # Insert initial data
    initial_records = [
        {"sku": "PROD001", "warehouse_id": 1, "quantity": 100, "price": 19.99, "last_updated": "2025-01-01"},
        {"sku": "PROD001", "warehouse_id": 2, "quantity": 150, "price": 19.99, "last_updated": "2025-01-01"},
        {"sku": "PROD002", "warehouse_id": 1, "quantity": 200, "price": 29.99, "last_updated": "2025-01-01"},
        {"sku": "PROD002", "warehouse_id": 2, "quantity": 250, "price": 29.99, "last_updated": "2025-01-01"},
    ]
    await adapter.bulk_create("products", initial_records)
    print(f"Created {len(initial_records)} initial products")

    # Prepare update records (update quantity and last_updated)
    update_records = [
        {"sku": "PROD001", "warehouse_id": 1, "quantity": 75, "last_updated": "2025-10-21"},
        {"sku": "PROD001", "warehouse_id": 2, "quantity": 125, "last_updated": "2025-10-21"},
        {"sku": "PROD002", "warehouse_id": 1, "quantity": 175, "last_updated": "2025-10-21"},
        {"sku": "PROD002", "warehouse_id": 2, "quantity": 225, "last_updated": "2025-10-21"},
    ]

    # Bulk update with composite key
    print(f"\nUpdating {len(update_records)} records using composite key (sku, warehouse_id)...")
    updated = await adapter.bulk_update(
        "products",
        update_records,
        key_columns=["sku", "warehouse_id"],
        update_columns=["quantity", "last_updated"]
    )
    print(f"Result: Updated {updated} rows")

    # Verify updates
    results = await adapter.fetch_all("SELECT * FROM products ORDER BY sku, warehouse_id")
    print("\nUpdated products:")
    for row in results:
        print(f"  {row['sku']} @ Warehouse {row['warehouse_id']}: "
              f"qty={row['quantity']}, updated={row['last_updated']}")

    await adapter.disconnect()


async def demo_create_or_update():
    """Demonstrate create_or_update UPSERT operation."""
    print("\n" + "=" * 80)
    print("DEMO 3: create_or_update() - Single Record UPSERT")
    print("=" * 80)

    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    # Create test table
    await adapter.execute("""
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT
        )
    """)

    # First upsert - should create new record
    print("\n1. Creating new setting...")
    result = await adapter.create_or_update(
        "settings",
        {"key": "theme", "value": "dark", "updated_at": "2025-10-21 10:00:00"},
        unique_columns=["key"]
    )
    print(f"   Result: {result}")
    print(f"   Action: {result['action']}, ID: {result['id']}, Affected: {result['affected_rows']}")

    # Second upsert - should update existing record
    print("\n2. Updating existing setting...")
    result = await adapter.create_or_update(
        "settings",
        {"key": "theme", "value": "light", "updated_at": "2025-10-21 11:00:00"},
        unique_columns=["key"],
        update_columns=["value", "updated_at"]
    )
    print(f"   Result: {result}")
    print(f"   Action: {result['action']}, ID: {result['id']}, Affected: {result['affected_rows']}")

    # Third upsert - same values, should result in update but no actual change
    print("\n3. Upserting with same values...")
    result = await adapter.create_or_update(
        "settings",
        {"key": "theme", "value": "light", "updated_at": "2025-10-21 11:00:00"},
        unique_columns=["key"],
        update_columns=["value", "updated_at"]
    )
    print(f"   Result: {result}")
    print(f"   Action: {result['action']}, Affected: {result['affected_rows']}")

    # Verify final state
    settings = await adapter.fetch_all("SELECT * FROM settings")
    print("\nFinal settings:")
    for setting in settings:
        print(f"  {setting['key']}: {setting['value']} (updated: {setting['updated_at']})")

    await adapter.disconnect()


async def demo_bulk_create_or_update():
    """Demonstrate bulk_create_or_update with tracking."""
    print("\n" + "=" * 80)
    print("DEMO 4: bulk_create_or_update() - Bulk UPSERT Operations")
    print("=" * 80)

    adapter = SQLiteAdapter(database=":memory:")
    await adapter.connect()

    # Create test table
    await adapter.execute("""
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL,
            location TEXT NOT NULL,
            last_sync TEXT
        )
    """)

    # Initial batch - all new records
    print("\n1. First batch - creating new records...")
    initial_records = [
        {"sku": f"SKU{i:04d}", "quantity": i * 10, "location": "A1", "last_sync": "2025-10-21 08:00"}
        for i in range(1, 501)
    ]
    result = await adapter.bulk_create_or_update(
        "inventory",
        initial_records,
        unique_columns=["sku"],
        batch_size=200,
        track_actions=True  # Enable accurate tracking
    )
    print(f"   Result: Created={result['created']}, Updated={result['updated']}, "
          f"Total Affected={result['total_affected']}")

    # Second batch - mix of updates and new records
    print("\n2. Second batch - updating existing + creating new...")
    mixed_records = [
        # Update first 250 (change quantity and last_sync)
        *[{"sku": f"SKU{i:04d}", "quantity": i * 15, "location": "A1", "last_sync": "2025-10-21 12:00"}
          for i in range(1, 251)],
        # Create next 250 new records
        *[{"sku": f"SKU{i:04d}", "quantity": i * 10, "location": "B2", "last_sync": "2025-10-21 12:00"}
          for i in range(501, 751)]
    ]
    result = await adapter.bulk_create_or_update(
        "inventory",
        mixed_records,
        unique_columns=["sku"],
        update_columns=["quantity", "last_sync"],  # Don't update location
        batch_size=200,
        track_actions=True
    )
    print(f"   Result: Created={result['created']}, Updated={result['updated']}, "
          f"Total Affected={result['total_affected']}")

    # Verify final count
    total = await adapter.fetch_value("SELECT COUNT(*) FROM inventory")
    print(f"\nTotal inventory items: {total}")

    # Show some sample records
    samples = await adapter.fetch_all("SELECT * FROM inventory WHERE sku IN ('SKU0001', 'SKU0250', 'SKU0500', 'SKU0750') ORDER BY sku")
    print("\nSample records:")
    for record in samples:
        print(f"  {record['sku']}: qty={record['quantity']}, "
              f"location={record['location']}, synced={record['last_sync']}")

    await adapter.disconnect()


async def demo_health_check():
    """Demonstrate comprehensive health_check."""
    print("\n" + "=" * 80)
    print("DEMO 5: health_check() - Database Health Monitoring")
    print("=" * 80)

    # Create a file-based database for realistic health check
    db_path = Path("/tmp/covet_health_demo.db")
    db_path.unlink(missing_ok=True)  # Clean up if exists

    adapter = SQLiteAdapter(database=str(db_path), max_pool_size=5)
    await adapter.connect()

    # Create some tables and data
    print("\nSetting up test database...")
    await adapter.execute("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
    """)

    records = [{"id": i, "data": f"test_data_{i}"} for i in range(1, 1001)]
    await adapter.bulk_create("test_table", records)
    print(f"Created test_table with {len(records)} records")

    # Perform health check
    print("\nPerforming comprehensive health check...")
    health = await adapter.health_check()

    # Display health check results
    print("\n" + "-" * 80)
    print(f"Health Status: {health['status'].upper()}")
    print("-" * 80)
    print(f"SQLite Version:        {health['version']}")
    print(f"Database Size:         {health['database_size_mb']:.2f} MB")
    print(f"Page Count:            {health['page_count']:,}")
    print(f"Page Size:             {health['page_size']:,} bytes")
    print(f"WAL Mode Enabled:      {health['wal_mode']}")
    if health['wal_checkpoint']:
        print(f"WAL Checkpoint:")
        print(f"  - Busy:              {health['wal_checkpoint']['busy']}")
        print(f"  - Log Size:          {health['wal_checkpoint']['log_size']}")
        print(f"  - Checkpointed:      {health['wal_checkpoint']['checkpointed']}")
    print(f"Foreign Keys:          {health['foreign_keys']}")
    print(f"Writable:              {health['writable']}")
    print(f"Integrity Check:       {health['integrity_check']}")
    print(f"\nConnection Pool:")
    print(f"  - Total Size:        {health['pool_stats']['size']}")
    print(f"  - Free Connections:  {health['pool_stats']['free']}")
    print(f"  - Used Connections:  {health['pool_stats']['used']}")
    print("-" * 80)

    # Test health check on unhealthy database (simulate)
    print("\n\nSimulating unhealthy database scenario...")
    # Note: Actual corruption would require filesystem manipulation
    # This is just a demonstration of the health_check structure
    if health['status'] == 'healthy':
        print("Database is healthy (expected for new database)")

    await adapter.disconnect()

    # Cleanup
    db_path.unlink(missing_ok=True)
    print("\nCleaned up test database")


async def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("SQLite Bulk Operations - Complete Demonstration")
    print("=" * 80)
    print("This demo showcases 5 new production-ready methods:")
    print("  1. bulk_create()           - Efficient bulk inserts with duplicate handling")
    print("  2. bulk_update()           - Bulk updates with composite key support")
    print("  3. create_or_update()      - Single record UPSERT operations")
    print("  4. bulk_create_or_update() - Bulk UPSERT with action tracking")
    print("  5. health_check()          - Comprehensive database health monitoring")

    try:
        await demo_bulk_create()
        await demo_bulk_update()
        await demo_create_or_update()
        await demo_bulk_create_or_update()
        await demo_health_check()

        print("\n" + "=" * 80)
        print("All demonstrations completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
