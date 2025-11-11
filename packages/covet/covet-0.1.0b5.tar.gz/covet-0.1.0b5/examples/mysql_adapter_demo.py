#!/usr/bin/env python3
"""
MySQL Adapter Demonstration Script

This script demonstrates all features of the CovetPy MySQL adapter:
1. Connection management
2. CRUD operations
3. UTF8MB4 emoji support
4. Transactions
5. Connection pooling
6. Streaming cursors
7. Error handling with retry
8. Health checks
9. Performance monitoring

Requirements:
- MySQL server running on localhost:3306
- Database: demo_db
- User: root (or configure below)

Run:
    python examples/mysql_adapter_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from covet.database.adapters.mysql import MySQLAdapter


async def demo_basic_operations():
    """Demonstrate basic CRUD operations."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic CRUD Operations")
    print("=" * 70)

    # Create adapter
    adapter = MySQLAdapter(
        host="localhost",
        port=3306,
        database="demo_db",
        user="root",
        password="",
        charset="utf8mb4",
    )

    try:
        # Connect
        print("\n1. Connecting to MySQL...")
        await adapter.connect()
        print(f"   Connected: {adapter}")

        # Create table
        print("\n2. Creating table...")
        await adapter.execute("DROP TABLE IF EXISTS users")
        await adapter.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) CHARACTER SET utf8mb4,
                email VARCHAR(255) CHARACTER SET utf8mb4,
                age INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("   Table 'users' created")

        # INSERT
        print("\n3. Inserting data...")
        user_id = await adapter.execute_insert(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            ("Alice Smith", "alice@example.com", 30),
        )
        print(f"   Inserted user with ID: {user_id}")

        # SELECT
        print("\n4. Fetching data...")
        user = await adapter.fetch_one(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
        )
        print(f"   User: {user['name']} ({user['email']}) - Age: {user['age']}")

        # UPDATE
        print("\n5. Updating data...")
        await adapter.execute(
            "UPDATE users SET age = %s WHERE id = %s",
            (31, user_id),
        )
        print("   Updated user age to 31")

        # Verify update
        user = await adapter.fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
        print(f"   Verified: Age is now {user['age']}")

        # DELETE
        print("\n6. Deleting data...")
        affected = await adapter.execute(
            "DELETE FROM users WHERE id = %s",
            (user_id,),
        )
        print(f"   Deleted {affected} row(s)")

    finally:
        await adapter.disconnect()
        print("\n   Disconnected")


async def demo_utf8mb4_emoji():
    """Demonstrate UTF8MB4 emoji support."""
    print("\n" + "=" * 70)
    print("DEMO 2: UTF8MB4 Emoji Support 😀🎉🚀")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="demo_db",
        user="root",
        password="",
        charset="utf8mb4",
    )

    try:
        await adapter.connect()

        # Create table
        await adapter.execute("DROP TABLE IF EXISTS emoji_test")
        await adapter.execute("""
            CREATE TABLE emoji_test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message VARCHAR(500) CHARACTER SET utf8mb4
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Insert emoji
        print("\n1. Inserting emoji messages...")
        messages = [
            "Hello 😀 World!",
            "Celebrating 🎉🎊🎈",
            "Rocket launch 🚀🌟💫",
            "Love this! ❤️💯🔥",
            "Mixed languages: Hello 你好 مرحبا 😀",
        ]

        for msg in messages:
            await adapter.execute_insert(
                "INSERT INTO emoji_test (message) VALUES (%s)",
                (msg,),
            )
            print(f"   Inserted: {msg}")

        # Retrieve and verify
        print("\n2. Retrieving emoji messages...")
        all_messages = await adapter.fetch_all("SELECT * FROM emoji_test")

        for row in all_messages:
            print(f"   ID {row['id']}: {row['message']}")

        print(f"\n   Successfully stored and retrieved {len(all_messages)} emoji messages!")

    finally:
        await adapter.disconnect()


async def demo_transactions():
    """Demonstrate transaction support."""
    print("\n" + "=" * 70)
    print("DEMO 3: Transaction Support")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="demo_db",
        user="root",
        password="",
    )

    try:
        await adapter.connect()

        # Create tables
        await adapter.execute("DROP TABLE IF EXISTS accounts")
        await adapter.execute("""
            CREATE TABLE accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                balance DECIMAL(10, 2)
            ) ENGINE=InnoDB
        """)

        # Insert initial data
        await adapter.execute_insert(
            "INSERT INTO accounts (name, balance) VALUES (%s, %s)",
            ("Alice", 1000.00),
        )
        await adapter.execute_insert(
            "INSERT INTO accounts (name, balance) VALUES (%s, %s)",
            ("Bob", 500.00),
        )

        # Successful transaction
        print("\n1. Successful transaction (transfer $100 from Alice to Bob)...")
        async with adapter.transaction(isolation="REPEATABLE READ") as conn:
            async with conn.cursor() as cursor:
                # Deduct from Alice
                await cursor.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE name = %s",
                    (100.00, "Alice"),
                )
                # Add to Bob
                await cursor.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE name = %s",
                    (100.00, "Bob"),
                )
        print("   Transaction committed")

        # Verify balances
        balances = await adapter.fetch_all("SELECT name, balance FROM accounts")
        for acc in balances:
            print(f"   {acc['name']}: ${acc['balance']:.2f}")

        # Failed transaction (rollback)
        print("\n2. Failed transaction (will rollback)...")
        try:
            async with adapter.transaction() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "UPDATE accounts SET balance = balance - %s WHERE name = %s",
                        (200.00, "Alice"),
                    )
                    # Simulate error
                    raise Exception("Simulated error - transaction will rollback")
        except Exception as e:
            print(f"   Error occurred: {e}")
            print("   Transaction rolled back")

        # Verify balances unchanged
        balances = await adapter.fetch_all("SELECT name, balance FROM accounts")
        print("   Balances after rollback:")
        for acc in balances:
            print(f"   {acc['name']}: ${acc['balance']:.2f}")

    finally:
        await adapter.disconnect()


async def demo_connection_pooling():
    """Demonstrate connection pooling."""
    print("\n" + "=" * 70)
    print("DEMO 4: Connection Pooling")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="demo_db",
        user="root",
        password="",
        min_pool_size=5,
        max_pool_size=20,
    )

    try:
        print("\n1. Creating connection pool...")
        await adapter.connect()

        # Check pool stats
        stats = await adapter.get_pool_stats()
        print(f"   Pool size: {stats['size']}")
        print(f"   Free connections: {stats['free']}")
        print(f"   Used connections: {stats['used']}")

        # Run concurrent queries
        print("\n2. Running 10 concurrent queries...")

        async def run_query(i):
            result = await adapter.fetch_value("SELECT SLEEP(0.1), %s", (i,))
            return result

        start = asyncio.get_event_loop().time()
        results = await asyncio.gather(*[run_query(i) for i in range(10)])
        elapsed = asyncio.get_event_loop().time() - start

        print(f"   Completed {len(results)} queries in {elapsed:.2f}s")
        print(f"   (sequential would take ~1.0s, pool enables concurrency)")

        # Final pool stats
        stats = await adapter.get_pool_stats()
        print(f"\n3. Final pool stats:")
        print(f"   Pool size: {stats['size']}")
        print(f"   Free connections: {stats['free']}")
        print(f"   Used connections: {stats['used']}")

    finally:
        await adapter.disconnect()


async def demo_streaming():
    """Demonstrate streaming large datasets."""
    print("\n" + "=" * 70)
    print("DEMO 5: Streaming Large Datasets")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="demo_db",
        user="root",
        password="",
    )

    try:
        await adapter.connect()

        # Create table
        await adapter.execute("DROP TABLE IF EXISTS large_table")
        await adapter.execute("""
            CREATE TABLE large_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data VARCHAR(255)
            ) ENGINE=InnoDB
        """)

        # Insert 10K rows
        print("\n1. Inserting 10,000 rows...")
        batch_size = 1000
        for batch in range(10):
            values = [
                (f"data_{batch * batch_size + i}",)
                for i in range(batch_size)
            ]
            await adapter.execute_many(
                "INSERT INTO large_table (data) VALUES (%s)",
                values,
            )
        print("   10,000 rows inserted")

        # Stream results
        print("\n2. Streaming results in chunks of 1000...")
        total_rows = 0
        chunk_count = 0

        async for chunk in adapter.stream_query(
            "SELECT * FROM large_table",
            chunk_size=1000,
        ):
            chunk_count += 1
            total_rows += len(chunk)
            print(f"   Chunk {chunk_count}: {len(chunk)} rows")

        print(f"\n   Total rows streamed: {total_rows:,}")
        print("   Memory-efficient: Only 1000 rows in memory at a time!")

    finally:
        await adapter.disconnect()


async def demo_retry_and_health():
    """Demonstrate retry logic and health checks."""
    print("\n" + "=" * 70)
    print("DEMO 6: Auto-Retry and Health Checks")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="demo_db",
        user="root",
        password="",
    )

    try:
        await adapter.connect()

        # Create table
        await adapter.execute("DROP TABLE IF EXISTS retry_test")
        await adapter.execute("""
            CREATE TABLE retry_test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                value INT
            ) ENGINE=InnoDB
        """)

        # Execute with retry
        print("\n1. Executing with automatic retry...")
        affected = await adapter.execute_with_retry(
            "INSERT INTO retry_test (value) VALUES (%s)",
            (42,),
            max_retries=5,
            initial_backoff=1.0,
        )
        print(f"   Inserted {affected} row(s) (will retry on transient errors)")

        # Health check
        print("\n2. Running health check...")
        health = await adapter.health_check()

        if health["status"] == "healthy":
            print("   ✓ MySQL is healthy")
            print(f"     Version: {health['version']}")
            print(f"     Uptime: {health['uptime']} seconds")
            print(f"     Active threads: {health['threads']}")
            print(f"     Total queries: {health['queries']:,}")
            print(f"     Slow queries: {health['slow_queries']}")
            print(f"     Pool size: {health['pool_size']}")
            print(f"     Pool free: {health['pool_free']}")
        else:
            print(f"   ✗ MySQL is unhealthy: {health.get('error')}")

    finally:
        await adapter.disconnect()


async def demo_batch_operations():
    """Demonstrate batch operations."""
    print("\n" + "=" * 70)
    print("DEMO 7: Batch Operations (High Performance)")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="demo_db",
        user="root",
        password="",
    )

    try:
        await adapter.connect()

        # Create table
        await adapter.execute("DROP TABLE IF EXISTS batch_test")
        await adapter.execute("""
            CREATE TABLE batch_test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                value INT
            ) ENGINE=InnoDB
        """)

        # Batch insert
        print("\n1. Batch inserting 1,000 rows...")
        data = [
            (f"name_{i}", i)
            for i in range(1000)
        ]

        start = asyncio.get_event_loop().time()
        affected = await adapter.execute_many(
            "INSERT INTO batch_test (name, value) VALUES (%s, %s)",
            data,
        )
        elapsed = asyncio.get_event_loop().time() - start

        print(f"   Inserted {affected} rows in {elapsed:.3f}s")
        print(f"   Performance: {affected / elapsed:,.0f} inserts/sec")

        # Verify
        count = await adapter.fetch_value("SELECT COUNT(*) FROM batch_test")
        print(f"   Verified: {count:,} rows in table")

    finally:
        await adapter.disconnect()


async def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("MySQL Adapter Feature Demonstration")
    print("CovetPy Framework - Production-Ready MySQL Integration")
    print("=" * 70)

    try:
        # Run demos
        await demo_basic_operations()
        await demo_utf8mb4_emoji()
        await demo_transactions()
        await demo_connection_pooling()
        await demo_streaming()
        await demo_retry_and_health()
        await demo_batch_operations()

        print("\n" + "=" * 70)
        print("All demonstrations completed successfully! 🎉")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Create demo database if it doesn't exist
    print("\nNote: Make sure MySQL is running and demo_db exists.")
    print("Create it with: CREATE DATABASE demo_db;")
    print("\nStarting demonstrations...\n")

    asyncio.run(main())
