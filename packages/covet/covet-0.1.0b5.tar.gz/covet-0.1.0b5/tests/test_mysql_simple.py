"""Simple MySQL connection test to debug issues."""

import asyncio
import sys
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy')

from src.covet.database.adapters.mysql import MySQLAdapter

async def test_connection():
    """Test basic MySQL connection."""
    print("Testing MySQL connection...")

    # Connect without database
    adapter = MySQLAdapter(
        host='localhost',
        user='root',
        password='12345678'
    )

    print("Connecting...")
    await adapter.connect()
    print("✅ Connected!")

    print("Creating database...")
    await adapter.execute("CREATE DATABASE IF NOT EXISTS covet_test_realworld")
    print("✅ Database created!")

    await adapter.disconnect()
    print("✅ Disconnected!")

    # Connect to database
    adapter2 = MySQLAdapter(
        host='localhost',
        user='root',
        password='12345678',
        database='covet_test_realworld'
    )

    print("Connecting to database...")
    await adapter2.connect()
    print("✅ Connected to database!")

    print("Creating simple table...")
    await adapter2.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255)
        )
    """)
    print("✅ Table created!")

    print("Inserting data...")
    await adapter2.execute("INSERT INTO test_table (name) VALUES ('test')")
    print("✅ Data inserted!")

    print("Fetching data...")
    result = await adapter2.fetch_all("SELECT * FROM test_table")
    print(f"✅ Data fetched: {result}")

    print("Cleaning up...")
    await adapter2.execute("DROP TABLE test_table")
    await adapter2.disconnect()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(test_connection())
