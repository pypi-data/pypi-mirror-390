"""
CovetPy MySQL Adapter - Quick Start Guide

A simple 5-minute introduction to using MySQL with CovetPy.

Installation:
    pip install covet aiomysql

MySQL Setup:
    CREATE DATABASE myapp;
"""

import asyncio

from covet.database.adapters import MySQLAdapter


async def quickstart():
    """Quick start example showing the basics"""

    # 1. Create adapter
    adapter = MySQLAdapter(
        host="localhost",
        port=3306,
        database="myapp",
        user="root",
        password="your_password",  # CHANGE THIS!
        min_pool_size=5,
        max_pool_size=20,
    )

    # 2. Connect
    await adapter.connect()
    print(f"✅ Connected to MySQL: {await adapter.get_version()}")

    try:
        # 3. Create a table
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        print("✅ Table created")

        # 4. Insert data
        product_id = await adapter.execute_insert(
            "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
            ("Laptop Pro", 1299.99, 50),
        )
        print(f"✅ Inserted product ID: {product_id}")

        # 5. Insert multiple rows
        await adapter.execute_many(
            "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
            [
                ("Smartphone X", 899.99, 100),
                ("Headphones", 249.99, 200),
                ("Monitor 4K", 599.99, 75),
            ],
        )
        print("✅ Inserted 3 more products")

        # 6. Query data
        products = await adapter.fetch_all("SELECT * FROM products ORDER BY price DESC")
        print(f"\n📦 Products ({len(products)}):")
        for p in products:
            print(f"  {p['name']}: ${p['price']} (Stock: {p['stock']})")

        # 7. Update data
        await adapter.execute("UPDATE products SET stock = stock + %s WHERE name = %s", (25, "Laptop Pro"))
        print("\n✅ Updated Laptop Pro stock")

        # 8. Get single product
        product = await adapter.fetch_one("SELECT * FROM products WHERE name = %s", ("Laptop Pro",))
        print(f"✅ Laptop Pro stock: {product['stock']}")

        # 9. Count products
        count = await adapter.fetch_value("SELECT COUNT(*) FROM products WHERE price > %s", (500,))
        print(f"✅ Premium products (>$500): {count}")

        # 10. Transaction example
        print("\n🔄 Processing order transaction...")
        async with adapter.transaction() as conn:
            async with conn.cursor() as cursor:
                # Decrease stock
                await cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (1, product_id))

                # Could add order record here
                # await cursor.execute("INSERT INTO orders ...")

        print("✅ Transaction completed")

        # 11. Health check
        health = await adapter.health_check()
        print(f"\n💚 Database health: {health['status']}")
        print(f"   Uptime: {health['uptime'] / 3600:.1f} hours")
        print(f"   Connections: {health['pool_size']} total, {health['pool_free']} free")

    finally:
        # 12. Cleanup and disconnect
        await adapter.execute("DROP TABLE IF EXISTS products")
        await adapter.disconnect()
        print("\n✅ Cleaned up and disconnected")


if __name__ == "__main__":
    print("=" * 60)
    print("CovetPy MySQL Adapter - Quick Start")
    print("=" * 60)
    print()

    asyncio.run(quickstart())

    print()
    print("=" * 60)
    print("Quick start complete!")
    print()
    print("Next steps:")
    print("  1. Check examples/mysql_adapter_complete_demo.py")
    print("  2. Read the adapter docs")
    print("  3. Build your application!")
    print("=" * 60)
