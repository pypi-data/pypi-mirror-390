"""
CovetPy MySQL Adapter - Complete Feature Demonstration

This example demonstrates all features of the production-ready MySQL adapter:
- Connection pooling
- CRUD operations
- Transactions with isolation levels
- Batch operations
- Streaming large datasets
- Binary log parsing (CDC)
- Health monitoring
- Table optimization

Requirements:
    pip install covet aiomysql

Optional for binlog parsing:
    pip install pymysql-replication

MySQL Setup:
    CREATE DATABASE covet_demo;
    USE covet_demo;

    # Enable binary logging for replication features (optional)
    [mysqld]
    log-bin=mysql-bin
    binlog_format=ROW
    server-id=1
"""

import asyncio
from datetime import datetime

from covet.database.adapters import MySQLAdapter


async def demo_basic_operations():
    """Demonstrate basic CRUD operations"""
    print("=" * 70)
    print("DEMO 1: Basic CRUD Operations")
    print("=" * 70)

    # Initialize adapter with connection pooling
    adapter = MySQLAdapter(
        host="localhost",
        port=3306,
        database="covet_demo",
        user="root",
        password="your_password",  # Change this!
        min_pool_size=5,  # Minimum connections
        max_pool_size=20,  # Maximum connections
        charset="utf8mb4",  # Full Unicode support
    )

    try:
        # Connect to database
        await adapter.connect()
        print(f"✅ Connected to MySQL: {await adapter.get_version()}")

        # Create table
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                age INT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_active (active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        )
        print("✅ Table 'users' created")

        # INSERT - Single row with auto-increment ID
        user_id = await adapter.execute_insert(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            ("Alice Johnson", "alice@example.com", 28),
        )
        print(f"✅ Inserted user with ID: {user_id}")

        # INSERT - Multiple rows efficiently
        affected = await adapter.execute_many(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
            [
                ("Bob Smith", "bob@example.com", 35),
                ("Charlie Brown", "charlie@example.com", 42),
                ("Diana Prince", "diana@example.com", 31),
                ("Eve Adams", "eve@example.com", 26),
            ],
        )
        print(f"✅ Inserted {affected} users in batch")

        # SELECT - Fetch single row
        user = await adapter.fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
        print(f"✅ Fetched user: {user['name']} ({user['email']})")

        # SELECT - Fetch all rows
        users = await adapter.fetch_all("SELECT * FROM users WHERE age >= %s ORDER BY age", (30,))
        print(f"✅ Fetched {len(users)} users aged 30+:")
        for u in users:
            print(f"   - {u['name']}: {u['age']} years old")

        # SELECT - Fetch single value
        count = await adapter.fetch_value("SELECT COUNT(*) FROM users WHERE active = %s", (True,))
        print(f"✅ Active users count: {count}")

        # UPDATE - Modify rows
        updated = await adapter.execute("UPDATE users SET active = %s WHERE age < %s", (False, 30))
        print(f"✅ Updated {updated} users (age < 30) to inactive")

        # DELETE - Remove rows
        deleted = await adapter.execute("DELETE FROM users WHERE age > %s", (100,))
        print(f"✅ Deleted {deleted} users (age > 100)")

        # Get table information
        columns = await adapter.get_table_info("users")
        print(f"✅ Table structure ({len(columns)} columns):")
        for col in columns[:3]:  # Show first 3 columns
            print(f"   - {col['Field']}: {col['Type']} (NULL: {col['Null']})")

    finally:
        await adapter.disconnect()
        print("\n✅ Disconnected from MySQL\n")


async def demo_transactions():
    """Demonstrate transaction management with different isolation levels"""
    print("=" * 70)
    print("DEMO 2: Transaction Management")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="covet_demo",
        user="root",
        password="your_password",
    )

    try:
        await adapter.connect()

        # Create accounts table for demo
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                balance DECIMAL(10, 2) DEFAULT 0.00
            )
        """
        )

        # Insert test accounts
        await adapter.execute_many(
            "INSERT INTO accounts (name, balance) VALUES (%s, %s)",
            [("Account A", 1000.00), ("Account B", 500.00), ("Account C", 750.00)],
        )

        print("Initial balances:")
        accounts = await adapter.fetch_all("SELECT * FROM accounts ORDER BY id")
        for acc in accounts:
            print(f"  {acc['name']}: ${acc['balance']}")

        # Transaction: Transfer money between accounts
        print("\n🔄 Transferring $200 from Account A to Account B...")

        async with adapter.transaction(isolation="SERIALIZABLE") as conn:
            async with conn.cursor() as cursor:
                # Deduct from Account A
                await cursor.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE name = %s", (200.00, "Account A")
                )

                # Add to Account B
                await cursor.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE name = %s", (200.00, "Account B")
                )

                print("✅ Transaction committed successfully")

        # Verify balances
        print("\nFinal balances:")
        accounts = await adapter.fetch_all("SELECT * FROM accounts ORDER BY id")
        for acc in accounts:
            print(f"  {acc['name']}: ${acc['balance']}")

        # Demonstrate rollback
        print("\n🔄 Attempting invalid transfer (will rollback)...")
        try:
            async with adapter.transaction() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "UPDATE accounts SET balance = balance - %s WHERE name = %s",
                        (10000.00, "Account C"),
                    )
                    # Simulate an error
                    raise ValueError("Insufficient funds!")

        except ValueError as e:
            print(f"❌ Transaction rolled back: {e}")

        # Verify Account C balance unchanged
        account_c = await adapter.fetch_one("SELECT * FROM accounts WHERE name = %s", ("Account C",))
        print(f"✅ Account C balance unchanged: ${account_c['balance']}")

    finally:
        # Cleanup
        await adapter.execute("DROP TABLE IF EXISTS accounts")
        await adapter.disconnect()
        print("\n✅ Disconnected\n")


async def demo_streaming():
    """Demonstrate streaming large datasets efficiently"""
    print("=" * 70)
    print("DEMO 3: Streaming Large Datasets")
    print("=" * 70)

    adapter = MySQLAdapter(host="localhost", database="covet_demo", user="root", password="your_password")

    try:
        await adapter.connect()

        # Create large table
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_type VARCHAR(50),
                event_data JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert 10,000 test events efficiently
        print("Inserting 10,000 test events...")
        batch_data = [
            (
                f"event_type_{i % 10}",
                f'{{"user_id": {i}, "action": "click", "value": {i * 10}}}',
            )
            for i in range(10000)
        ]

        await adapter.execute_many(
            "INSERT INTO events (event_type, event_data) VALUES (%s, %s)", batch_data
        )
        print("✅ Inserted 10,000 events")

        # Stream results in chunks (memory-efficient for millions of rows)
        print("\n📊 Streaming events in chunks of 1000...")
        total_processed = 0

        async for chunk in adapter.stream_query("SELECT * FROM events ORDER BY id", chunk_size=1000):
            total_processed += len(chunk)
            # Process chunk (e.g., send to queue, write to file)
            print(f"  Processed chunk: {len(chunk)} events (Total: {total_processed})")

            # Show sample from first chunk
            if total_processed == 1000:
                sample = chunk[0]
                print(f"  Sample event: ID={sample['id']}, Type={sample['event_type']}")

        print(f"✅ Streamed total: {total_processed} events")

    finally:
        # Cleanup
        await adapter.execute("DROP TABLE IF EXISTS events")
        await adapter.disconnect()
        print("\n✅ Disconnected\n")


async def demo_connection_pooling():
    """Demonstrate connection pool management and stats"""
    print("=" * 70)
    print("DEMO 4: Connection Pool Management")
    print("=" * 70)

    adapter = MySQLAdapter(
        host="localhost",
        database="covet_demo",
        user="root",
        password="your_password",
        min_pool_size=3,
        max_pool_size=10,
    )

    try:
        await adapter.connect()

        # Check initial pool stats
        stats = await adapter.get_pool_stats()
        print(f"Initial pool stats:")
        print(f"  Total connections: {stats['size']}")
        print(f"  Free connections: {stats['free']}")
        print(f"  Used connections: {stats['used']}")

        # Simulate concurrent queries
        print("\n🔄 Running 20 concurrent queries...")

        async def run_query(i):
            result = await adapter.fetch_value("SELECT SLEEP(0.1), %s", (i,), column=1)
            return result

        # Run queries concurrently
        results = await asyncio.gather(*[run_query(i) for i in range(20)])
        print(f"✅ Completed {len(results)} concurrent queries")

        # Check pool stats after load
        stats = await adapter.get_pool_stats()
        print(f"\nPool stats after load:")
        print(f"  Total connections: {stats['size']}")
        print(f"  Free connections: {stats['free']}")
        print(f"  Used connections: {stats['used']}")

    finally:
        await adapter.disconnect()
        print("\n✅ Disconnected\n")


async def demo_health_monitoring():
    """Demonstrate database health monitoring"""
    print("=" * 70)
    print("DEMO 5: Health Check & Monitoring")
    print("=" * 70)

    adapter = MySQLAdapter(host="localhost", database="covet_demo", user="root", password="your_password")

    try:
        await adapter.connect()

        # Comprehensive health check
        health = await adapter.health_check()

        print(f"Health Status: {health['status'].upper()}")
        print(f"  Version: {health['version']}")
        print(f"  Uptime: {health['uptime']} seconds ({health['uptime'] / 3600:.2f} hours)")
        print(f"  Active threads: {health['threads']}")
        print(f"  Total queries: {health['queries']}")
        print(f"  Slow queries: {health['slow_queries']}")
        print(f"  Pool size: {health['pool_size']}")
        print(f"  Pool free: {health['pool_free']}")
        print(f"  Pool used: {health['pool_used']}")

        # Check replication status (if enabled)
        replication = await adapter.get_replication_status()
        if replication["enabled"]:
            print(f"\n📊 Replication Status:")
            print(f"  Binary log: {replication['log_file']}")
            print(f"  Position: {replication['log_pos']}")
            print(f"  Format: {replication['binlog_format']}")
        else:
            print(f"\n⚠️  Binary logging not enabled")

        # List all databases
        databases = await adapter.get_database_list()
        print(f"\n📁 Databases ({len(databases)}):")
        for db in databases[:5]:  # Show first 5
            print(f"  - {db}")

        # List all tables in current database
        tables = await adapter.get_table_list()
        print(f"\n📋 Tables in '{adapter.database}' ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")

    finally:
        await adapter.disconnect()
        print("\n✅ Disconnected\n")


async def demo_table_optimization():
    """Demonstrate table optimization and maintenance"""
    print("=" * 70)
    print("DEMO 6: Table Optimization & Maintenance")
    print("=" * 70)

    adapter = MySQLAdapter(host="localhost", database="covet_demo", user="root", password="your_password")

    try:
        await adapter.connect()

        # Ensure users table exists
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(255),
                age INT
            )
        """
        )

        # Analyze table (update statistics)
        print("Analyzing table...")
        result = await adapter.analyze_table("users")
        print(f"✅ Analyze result: {result}")

        # Optimize table (defragment, reclaim space)
        print("\nOptimizing table...")
        result = await adapter.optimize_table("users")
        print(f"✅ Optimize result: {result}")

        # Check if table exists
        exists = await adapter.table_exists("users")
        print(f"\n✅ Table 'users' exists: {exists}")

        non_existent = await adapter.table_exists("nonexistent_table")
        print(f"✅ Table 'nonexistent_table' exists: {non_existent}")

    finally:
        await adapter.disconnect()
        print("\n✅ Disconnected\n")


async def demo_retry_logic():
    """Demonstrate automatic retry with exponential backoff"""
    print("=" * 70)
    print("DEMO 7: Automatic Retry with Exponential Backoff")
    print("=" * 70)

    adapter = MySQLAdapter(host="localhost", database="covet_demo", user="root", password="your_password")

    try:
        await adapter.connect()

        # Create test table
        await adapter.execute(
            """
            CREATE TABLE IF NOT EXISTS retry_test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                value INT,
                UNIQUE KEY idx_value (value)
            )
        """
        )

        # Insert initial value
        await adapter.execute("INSERT INTO retry_test (value) VALUES (%s)", (1,))

        print("Executing query with retry logic...")
        print("(Automatically retries on deadlocks, timeouts, connection lost)")

        # Execute with retry - will automatically retry on transient errors
        rows = await adapter.execute_with_retry(
            "UPDATE retry_test SET value = value + %s WHERE id = %s",
            (10, 1),
            max_retries=5,
            initial_backoff=0.5,
        )

        print(f"✅ Query succeeded: {rows} rows affected")

        # Verify result
        result = await adapter.fetch_one("SELECT * FROM retry_test WHERE id = 1")
        print(f"✅ Updated value: {result['value']}")

    finally:
        # Cleanup
        await adapter.execute("DROP TABLE IF EXISTS retry_test")
        await adapter.disconnect()
        print("\n✅ Disconnected\n")


async def demo_binary_log_parsing():
    """
    Demonstrate binary log parsing for Change Data Capture (CDC)

    NOTE: This requires:
    1. pymysql-replication package: pip install pymysql-replication
    2. MySQL binlog enabled (see module docstring for config)
    """
    print("=" * 70)
    print("DEMO 8: Binary Log Parsing (CDC)")
    print("=" * 70)
    print("⚠️  Requires 'pymysql-replication' package and binlog enabled")
    print("⚠️  Skipping this demo - uncomment code to enable\n")

    # Uncomment to run CDC demo:
    """
    adapter = MySQLAdapter(
        host='localhost',
        database='covet_demo',
        user='root',
        password='your_password'
    )

    try:
        await adapter.connect()

        # Get replication status
        status = await adapter.get_replication_status()

        if not status['enabled']:
            print("❌ Binary logging not enabled")
            return

        print(f"Starting CDC from {status['log_file']}:{status['log_pos']}")

        # Parse binlog events (non-blocking example)
        event_count = 0
        async for event in adapter.parse_binlog_events(
            server_id=1,
            log_file=status['log_file'],
            log_pos=status['log_pos'],
            blocking=False,  # Don't wait for new events
            only_events=['write', 'update', 'delete']
        ):
            event_count += 1
            print(f"Event {event_count}: {event['event_type']} on {event['schema']}.{event['table']}")
            print(f"  Timestamp: {event['timestamp']}")
            print(f"  Rows affected: {len(event['rows'])}")

            # Process first 10 events only for demo
            if event_count >= 10:
                break

        print(f"✅ Processed {event_count} binlog events")

    finally:
        await adapter.disconnect()
        print("\\n✅ Disconnected\\n")
    """


async def main():
    """Run all MySQL adapter demos"""
    print("\n" + "=" * 70)
    print("CovetPy MySQL Adapter - Complete Feature Demo")
    print("=" * 70)
    print()
    print("⚠️  Make sure to update the MySQL credentials in each demo!")
    print("⚠️  MySQL server should be running on localhost:3306")
    print("⚠️  Database 'covet_demo' should exist")
    print()

    demos = [
        ("Basic CRUD Operations", demo_basic_operations),
        ("Transaction Management", demo_transactions),
        ("Streaming Large Datasets", demo_streaming),
        ("Connection Pool Management", demo_connection_pooling),
        ("Health Check & Monitoring", demo_health_monitoring),
        ("Table Optimization", demo_table_optimization),
        ("Retry Logic", demo_retry_logic),
        ("Binary Log Parsing (CDC)", demo_binary_log_parsing),
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
    print("All demos completed!")
    print("=" * 70)


if __name__ == "__main__":
    # Run all demos
    asyncio.run(main())
