"""
CovetPy MySQL Adapter - Bulk Operations Demo

Demonstrates the new bulk operation methods:
- bulk_create: Insert multiple records efficiently
- bulk_update: Update multiple records efficiently
- create_or_update: Upsert single record (insert or update if exists)
- bulk_create_or_update: Batch upsert multiple records

Requirements:
    pip install covet aiomysql

MySQL Setup:
    CREATE DATABASE covet_demo;
"""

import asyncio
from datetime import datetime

from covet.database.adapters import MySQLAdapter


async def demo_bulk_create():
    """Demonstrate bulk_create for efficient batch inserts"""
    print("=" * 70)
    print("DEMO 1: bulk_create() - Batch Insert")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="covet_demo",
        user="root",
        password="your_password",  # CHANGE THIS!
    )

    try:
        await adapter.connect()

        # Create table
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                age INT,
                city VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Bulk insert - insert 1000 users efficiently
        print("Inserting 1000 users...")
        users_data = [
            {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 50),
                "city": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"][i % 5],
            }
            for i in range(1, 1001)
        ]

        rows_inserted = await adapter.bulk_create("users", users_data)
        print(f"✅ Inserted {rows_inserted} users in one batch operation")

        # Verify
        count = await adapter.fetch_value("SELECT COUNT(*) FROM users")
        print(f"✅ Total users in database: {count}")

        # Bulk insert with ignore_duplicates (skip errors on duplicate emails)
        print("\nTrying to insert duplicates with ignore_duplicates=True...")
        duplicate_data = [
            {"name": "User 1 Updated", "email": "user1@example.com", "age": 99, "city": "Miami"},
            {"name": "New User", "email": "newuser@example.com", "age": 25, "city": "Seattle"},
        ]

        rows_inserted = await adapter.bulk_create("users", duplicate_data, ignore_duplicates=True)
        print(f"✅ Inserted {rows_inserted} new users (duplicates ignored)")

        # Check the duplicate wasn't updated (INSERT IGNORE doesn't update)
        user1 = await adapter.fetch_one("SELECT * FROM users WHERE email = %s", ("user1@example.com",))
        print(f"✅ User 1 name unchanged: '{user1['name']}' (INSERT IGNORE preserved original)")

    finally:
        await adapter.execute("DROP TABLE IF EXISTS users")
        await adapter.disconnect()
        print("\n✅ Cleaned up and disconnected\n")


async def demo_bulk_update():
    """Demonstrate bulk_update for batch updates"""
    print("=" * 70)
    print("DEMO 2: bulk_update() - Batch Update")
    print("=" * 70)

    adapter = MySQLAdapter(host="localhost", database="covet_demo", user="root", password="your_password")

    try:
        await adapter.connect()

        # Create products table
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200),
                price DECIMAL(10, 2),
                stock INT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
        )

        # Insert initial products
        products = [
            {"sku": "LAPTOP-001", "name": "Laptop Pro", "price": 1299.99, "stock": 50},
            {"sku": "PHONE-001", "name": "Smartphone X", "price": 899.99, "stock": 100},
            {"sku": "TABLET-001", "name": "Tablet Pro", "price": 599.99, "stock": 75},
            {"sku": "MONITOR-001", "name": "Monitor 4K", "price": 499.99, "stock": 30},
            {"sku": "KEYBOARD-001", "name": "Mechanical Keyboard", "price": 149.99, "stock": 200},
        ]
        await adapter.bulk_create("products", products)
        print("✅ Created 5 products")

        # Bulk update prices and stock (update by id)
        print("\nUpdating prices and stock for 3 products...")
        updates = [
            {"id": 1, "price": 1199.99, "stock": 45},  # Price drop for Laptop
            {"id": 2, "price": 799.99, "stock": 120},  # Price drop for Phone, more stock
            {"id": 3, "price": 549.99, "stock": 80},  # Price drop for Tablet
        ]

        rows_updated = await adapter.bulk_update("products", updates, key_columns=["id"])
        print(f"✅ Updated {rows_updated} products")

        # Verify updates
        print("\nUpdated prices:")
        products = await adapter.fetch_all("SELECT sku, name, price, stock FROM products ORDER BY id")
        for p in products[:3]:
            print(f"  {p['sku']}: ${p['price']} (Stock: {p['stock']})")

        # Bulk update with specific columns only
        print("\nUpdating only stock (not price) for 2 products...")
        stock_updates = [
            {"sku": "MONITOR-001", "stock": 50, "price": 999.99},  # Price won't be updated
            {"sku": "KEYBOARD-001", "stock": 250, "price": 999.99},  # Price won't be updated
        ]

        rows_updated = await adapter.bulk_update(
            "products", stock_updates, key_columns=["sku"], update_columns=["stock"]  # Only update stock
        )
        print(f"✅ Updated stock for {rows_updated} products (prices unchanged)")

        # Verify
        monitor = await adapter.fetch_one("SELECT * FROM products WHERE sku = %s", ("MONITOR-001",))
        print(f"✅ Monitor price unchanged: ${monitor['price']}, stock: {monitor['stock']}")

    finally:
        await adapter.execute("DROP TABLE IF EXISTS products")
        await adapter.disconnect()
        print("\n✅ Cleaned up and disconnected\n")


async def demo_create_or_update():
    """Demonstrate create_or_update (upsert) single record"""
    print("=" * 70)
    print("DEMO 3: create_or_update() - Single Record Upsert")
    print("=" * 70)

    adapter = MySQLAdapter(host="localhost", database="covet_demo", user="root", password="your_password")

    try:
        await adapter.connect()

        # Create products table with unique SKU
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200),
                price DECIMAL(10, 2),
                stock INT,
                last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
        )

        # First upsert - should create new record
        print("First upsert (creates new record)...")
        result = await adapter.create_or_update(
            "inventory",
            {"sku": "LAPTOP-PRO-15", "name": "Laptop Pro 15-inch", "price": 2499.99, "stock": 25},
            unique_columns=["sku"],
        )

        print(f"✅ Action: {result['action']}")
        print(f"   New ID: {result['id']}")
        print(f"   Affected rows: {result['affected_rows']}")

        # Second upsert with same SKU - should update existing record
        print("\nSecond upsert with same SKU (updates existing)...")
        result = await adapter.create_or_update(
            "inventory",
            {"sku": "LAPTOP-PRO-15", "name": "Laptop Pro 15-inch (Updated)", "price": 2299.99, "stock": 30},
            unique_columns=["sku"],
        )

        print(f"✅ Action: {result['action']}")
        print(f"   ID: {result['id']} (None because it was an update)")
        print(f"   Affected rows: {result['affected_rows']}")

        # Verify the update
        laptop = await adapter.fetch_one("SELECT * FROM inventory WHERE sku = %s", ("LAPTOP-PRO-15",))
        print(f"\n✅ Updated record:")
        print(f"   Name: {laptop['name']}")
        print(f"   Price: ${laptop['price']}")
        print(f"   Stock: {laptop['stock']}")

        # Upsert with selective column updates
        print("\nUpsert with selective updates (only price and stock)...")
        result = await adapter.create_or_update(
            "inventory",
            {
                "sku": "LAPTOP-PRO-15",
                "name": "This name won't be updated",
                "price": 2199.99,  # Will update
                "stock": 35,  # Will update
            },
            unique_columns=["sku"],
            update_columns=["price", "stock"],  # Only update these columns
        )

        print(f"✅ Action: {result['action']}")

        # Verify selective update
        laptop = await adapter.fetch_one("SELECT * FROM inventory WHERE sku = %s", ("LAPTOP-PRO-15",))
        print(f"✅ Name unchanged: {laptop['name']}")
        print(f"   Price updated: ${laptop['price']}")
        print(f"   Stock updated: {laptop['stock']}")

    finally:
        await adapter.execute("DROP TABLE IF EXISTS inventory")
        await adapter.disconnect()
        print("\n✅ Cleaned up and disconnected\n")


async def demo_bulk_create_or_update():
    """Demonstrate bulk_create_or_update (batch upsert)"""
    print("=" * 70)
    print("DEMO 4: bulk_create_or_update() - Batch Upsert")
    print("=" * 70)

    adapter = MySQLAdapter(host="localhost", database="covet_demo", user="root", password="your_password")

    try:
        await adapter.connect()

        # Create product catalog table
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS catalog (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200),
                description TEXT,
                price DECIMAL(10, 2),
                stock INT,
                last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """
        )

        # Initial catalog sync (all new products)
        print("Initial catalog sync (creates 5 products)...")
        catalog_data = [
            {
                "sku": "LAPTOP-001",
                "name": "Laptop Pro",
                "description": "High-performance laptop",
                "price": 1299.99,
                "stock": 50,
            },
            {
                "sku": "PHONE-001",
                "name": "Smartphone X",
                "description": "Latest smartphone",
                "price": 899.99,
                "stock": 100,
            },
            {
                "sku": "TABLET-001",
                "name": "Tablet Pro",
                "description": "Professional tablet",
                "price": 599.99,
                "stock": 75,
            },
            {
                "sku": "MONITOR-001",
                "name": "Monitor 4K",
                "description": "Ultra HD monitor",
                "price": 499.99,
                "stock": 30,
            },
            {
                "sku": "KEYBOARD-001",
                "name": "Mechanical Keyboard",
                "description": "RGB mechanical keyboard",
                "price": 149.99,
                "stock": 200,
            },
        ]

        result = await adapter.bulk_create_or_update("catalog", catalog_data, unique_columns=["sku"])

        print(f"✅ Created: {result['created']}")
        print(f"   Updated: {result['updated']}")
        print(f"   Total affected: {result['total_affected']}")

        # Second sync with some updates and new products
        print("\nSecond catalog sync (3 updates + 2 new products)...")
        updated_catalog = [
            # Existing products with new prices/stock (will update)
            {
                "sku": "LAPTOP-001",
                "name": "Laptop Pro",
                "description": "High-performance laptop",
                "price": 1199.99,  # Price drop
                "stock": 45,  # Stock decrease
            },
            {
                "sku": "PHONE-001",
                "name": "Smartphone X",
                "description": "Latest smartphone",
                "price": 799.99,  # Price drop
                "stock": 120,  # Stock increase
            },
            {
                "sku": "TABLET-001",
                "name": "Tablet Pro Plus",  # Name changed
                "description": "Professional tablet with more features",
                "price": 649.99,  # Price increase
                "stock": 80,
            },
            # New products (will create)
            {
                "sku": "MOUSE-001",
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse",
                "price": 49.99,
                "stock": 300,
            },
            {
                "sku": "HEADSET-001",
                "name": "Gaming Headset",
                "description": "7.1 surround sound headset",
                "price": 129.99,
                "stock": 150,
            },
        ]

        result = await adapter.bulk_create_or_update("catalog", updated_catalog, unique_columns=["sku"])

        print(f"✅ Created: {result['created']}")
        print(f"   Updated: {result['updated']}")
        print(f"   Total affected: {result['total_affected']}")

        # Verify the results
        print("\nFinal catalog:")
        products = await adapter.fetch_all("SELECT sku, name, price, stock FROM catalog ORDER BY sku")
        for p in products:
            print(f"  {p['sku']}: {p['name']} - ${p['price']} (Stock: {p['stock']})")

        # Bulk upsert with selective updates
        print("\nBulk upsert with selective updates (only price and stock)...")
        price_updates = [
            {"sku": "LAPTOP-001", "name": "Won't update", "price": 1099.99, "stock": 40},
            {"sku": "PHONE-001", "name": "Won't update", "price": 749.99, "stock": 130},
            {"sku": "NEW-PRODUCT", "name": "New Camera", "price": 899.99, "stock": 20},  # Will create
        ]

        result = await adapter.bulk_create_or_update(
            "catalog",
            price_updates,
            unique_columns=["sku"],
            update_columns=["price", "stock"],  # Only update these columns on conflict
        )

        print(f"✅ Created: {result['created']} (NEW-PRODUCT)")
        print(f"   Updated: {result['updated']} (LAPTOP-001, PHONE-001)")

        # Verify selective updates
        laptop = await adapter.fetch_one("SELECT * FROM catalog WHERE sku = %s", ("LAPTOP-001",))
        print(f"\n✅ Laptop name unchanged: {laptop['name']}")
        print(f"   Price updated: ${laptop['price']}")
        print(f"   Stock updated: {laptop['stock']}")

    finally:
        await adapter.execute("DROP TABLE IF EXISTS catalog")
        await adapter.disconnect()
        print("\n✅ Cleaned up and disconnected\n")


async def demo_real_world_use_case():
    """Real-world example: Syncing product catalog from external API"""
    print("=" * 70)
    print("DEMO 5: Real-World Use Case - Catalog Sync from External API")
    print("=" * 70)

    adapter = MySQLAdapter(host="localhost", database="covet_demo", user="root", password="your_password")

    try:
        await adapter.connect()

        # Create products table
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200),
                category VARCHAR(100),
                price DECIMAL(10, 2),
                stock INT,
                is_active BOOLEAN DEFAULT TRUE,
                last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_category (category),
                INDEX idx_active (is_active)
            )
        """
        )

        print("Simulating catalog sync from external API...\n")

        # Simulate fetching data from external API
        def fetch_products_from_api():
            """Simulate API response with product data"""
            return [
                {
                    "sku": "ELEC-LAPTOP-001",
                    "name": "Dell XPS 15",
                    "category": "Electronics",
                    "price": 1499.99,
                    "stock": 25,
                },
                {
                    "sku": "ELEC-PHONE-001",
                    "name": "iPhone 15 Pro",
                    "category": "Electronics",
                    "price": 999.99,
                    "stock": 50,
                },
                {
                    "sku": "BOOK-TECH-001",
                    "name": "Python Programming",
                    "category": "Books",
                    "price": 49.99,
                    "stock": 100,
                },
                {
                    "sku": "CLOTH-SHIRT-001",
                    "name": "Cotton T-Shirt",
                    "category": "Clothing",
                    "price": 19.99,
                    "stock": 500,
                },
                {
                    "sku": "ELEC-TABLET-001",
                    "name": "iPad Pro 12.9",
                    "category": "Electronics",
                    "price": 1099.99,
                    "stock": 30,
                },
            ]

        # First sync
        print("📥 First sync from API...")
        api_products = fetch_products_from_api()
        result = await adapter.bulk_create_or_update("products", api_products, unique_columns=["sku"])

        print(f"✅ Synced {len(api_products)} products:")
        print(f"   Created: {result['created']}")
        print(f"   Updated: {result['updated']}")

        # Simulate second sync with price changes
        print("\n📥 Second sync with price updates...")

        def fetch_updated_products():
            return [
                {
                    "sku": "ELEC-LAPTOP-001",
                    "name": "Dell XPS 15",
                    "category": "Electronics",
                    "price": 1399.99,  # Price drop
                    "stock": 20,  # Stock decrease
                },
                {
                    "sku": "ELEC-PHONE-001",
                    "name": "iPhone 15 Pro",
                    "category": "Electronics",
                    "price": 949.99,  # Price drop
                    "stock": 60,  # Stock increase
                },
                {
                    "sku": "BOOK-TECH-001",
                    "name": "Python Programming",
                    "category": "Books",
                    "price": 44.99,  # Price drop
                    "stock": 95,
                },
                {
                    "sku": "CLOTH-SHIRT-001",
                    "name": "Cotton T-Shirt",
                    "category": "Clothing",
                    "price": 19.99,
                    "stock": 450,
                },
                {
                    "sku": "ELEC-TABLET-001",
                    "name": "iPad Pro 12.9",
                    "category": "Electronics",
                    "price": 1099.99,
                    "stock": 25,
                },
                # New product added to API
                {
                    "sku": "ELEC-WATCH-001",
                    "name": "Apple Watch Series 9",
                    "category": "Electronics",
                    "price": 399.99,
                    "stock": 40,
                },
            ]

        api_products = fetch_updated_products()
        result = await adapter.bulk_create_or_update("products", api_products, unique_columns=["sku"])

        print(f"✅ Synced {len(api_products)} products:")
        print(f"   Created: {result['created']} (new products)")
        print(f"   Updated: {result['updated']} (existing products)")

        # Display final inventory by category
        print("\n📊 Final Inventory by Category:")
        categories = await adapter.fetch_all(
            """
            SELECT category, COUNT(*) as count, SUM(stock) as total_stock
            FROM products
            WHERE is_active = TRUE
            GROUP BY category
            ORDER BY category
        """
        )

        for cat in categories:
            print(f"  {cat['category']}: {cat['count']} products, {cat['total_stock']} total stock")

        # Show products with price changes
        print("\n💰 Products (sorted by price):")
        products = await adapter.fetch_all(
            "SELECT sku, name, price, stock FROM products WHERE is_active = TRUE ORDER BY price DESC LIMIT 5"
        )

        for p in products:
            print(f"  {p['name']}: ${p['price']} (Stock: {p['stock']})")

        print("\n✅ Catalog sync complete!")
        print(f"   Total products in database: {len(products)}")

    finally:
        await adapter.execute("DROP TABLE IF EXISTS products")
        await adapter.disconnect()
        print("\n✅ Cleaned up and disconnected\n")


async def main():
    """Run all bulk operation demos"""
    print("\n" + "=" * 70)
    print("CovetPy MySQL Adapter - Bulk Operations Demo")
    print("=" * 70)
    print()
    print("⚠️  Update MySQL credentials in each demo function!")
    print()

    demos = [
        ("Bulk Create", demo_bulk_create),
        ("Bulk Update", demo_bulk_update),
        ("Create or Update (Upsert)", demo_create_or_update),
        ("Bulk Create or Update", demo_bulk_create_or_update),
        ("Real-World Catalog Sync", demo_real_world_use_case),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'▶' * 35}")
        print(f"Demo {i}/{len(demos)}: {name}")
        print(f"{'▶' * 35}\n")

        try:
            await demo_func()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            print(f"   Make sure MySQL is running and credentials are correct\n")

    print("\n" + "=" * 70)
    print("All bulk operation demos completed!")
    print("=" * 70)
    print()
    print("Summary of new methods:")
    print("  • bulk_create() - Efficient batch inserts")
    print("  • bulk_update() - Batch updates with flexible key columns")
    print("  • create_or_update() - Single record upsert")
    print("  • bulk_create_or_update() - Batch upsert for sync operations")
    print()
    print("Perfect for:")
    print("  ✓ API data synchronization")
    print("  ✓ ETL pipelines")
    print("  ✓ Inventory management")
    print("  ✓ Bulk imports from CSV/Excel")
    print("  ✓ Catalog updates")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
