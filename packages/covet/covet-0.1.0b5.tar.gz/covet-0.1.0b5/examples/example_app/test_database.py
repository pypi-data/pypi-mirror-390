"""
Test actual database connectivity
"""
import sys
import asyncio
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

async def test_database():
    try:
        from covet.database import SQLiteAdapter, DatabaseManager
        print("✅ Database class imported")
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        return

    # Try to create database connection (SQLite for simplicity)
    try:
        adapter = SQLiteAdapter('example_blog.db')
        db = DatabaseManager(adapter)
        print("✅ Database instance created")

        # Try to connect
        await db.connect()
        print("✅ Database connection established")

        # Try a simple query
        result = await db.execute("SELECT 1 as test")
        print(f"✅ Query executed successfully: {result}")

        # Disconnect
        await db.disconnect()
        print("✅ Database disconnected cleanly")

    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())
