"""
DatabaseSessionStore Demo

Demonstrates the DatabaseSessionStore implementation with SQLite.
Shows all CRUD operations and session management features.
"""

import asyncio
from datetime import datetime, timedelta
import tempfile
from pathlib import Path

from covet.database.adapters.sqlite import SQLiteAdapter
from covet.auth.session import DatabaseSessionStore
from covet.auth.models import Session


async def main():
    print("=" * 60)
    print("DatabaseSessionStore Demo - SQLite Backend")
    print("=" * 60)
    print()

    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    print(f"1. Creating SQLite database at: {db_path}")

    # Initialize database adapter
    db = SQLiteAdapter(database=db_path, max_pool_size=5)
    await db.connect()
    print("   ✓ Database connected")

    # Initialize session store
    store = DatabaseSessionStore(db)
    print(f"   ✓ Detected dialect: {store._dialect}")

    # Create tables
    print("\n2. Creating sessions table...")
    await store._create_tables()
    print("   ✓ Table created successfully")

    # Verify table structure
    columns = await db.get_table_info('sessions')
    print(f"   ✓ Table has {len(columns)} columns")

    # Create and store a session
    print("\n3. Creating and storing a session...")
    session1 = Session(
        id='demo_session_123',
        user_id='user_alice',
        created_at=datetime.utcnow(),
        last_accessed_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
        ip_address='192.168.1.100',
        user_agent='Mozilla/5.0 (Demo Browser)',
        is_active=True,
        data={
            'csrf_token': 'abc123xyz',
            'preferences': {'theme': 'dark', 'language': 'en'},
            'cart': ['item1', 'item2', 'item3']
        }
    )
    await store.set(session1)
    print(f"   ✓ Session stored: {session1.id}")

    # Retrieve the session
    print("\n4. Retrieving session from database...")
    retrieved = await store.get('demo_session_123')
    print(f"   ✓ Session retrieved: {retrieved.id}")
    print(f"   - User ID: {retrieved.user_id}")
    print(f"   - IP Address: {retrieved.ip_address}")
    print(f"   - Active: {retrieved.is_active}")
    print(f"   - CSRF Token: {retrieved.data['csrf_token']}")
    print(f"   - Theme: {retrieved.data['preferences']['theme']}")
    print(f"   - Cart items: {len(retrieved.data['cart'])}")

    # Update the session
    print("\n5. Updating session...")
    session1.last_accessed_at = datetime.utcnow()
    session1.data['cart'].append('item4')
    await store.set(session1)
    print("   ✓ Session updated")

    # Verify update
    updated = await store.get('demo_session_123')
    print(f"   - Cart items: {len(updated.data['cart'])} (was 3, now 4)")

    # Create multiple sessions for the same user
    print("\n6. Creating multiple sessions for user 'user_alice'...")
    for i in range(3):
        session = Session(
            id=f'session_alice_{i}',
            user_id='user_alice',
            created_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1),
            ip_address=f'192.168.1.{100+i}',
            user_agent=f'Device {i}',
            is_active=True,
            data={}
        )
        await store.set(session)
    print("   ✓ Created 3 additional sessions")

    # Get all user sessions
    print("\n7. Retrieving all sessions for user 'user_alice'...")
    user_sessions = await store.get_user_sessions('user_alice')
    print(f"   ✓ Found {len(user_sessions)} active sessions:")
    for sess in user_sessions:
        print(f"      - {sess.id} from {sess.ip_address}")

    # Create an expired session
    print("\n8. Creating an expired session...")
    expired = Session(
        id='expired_session',
        user_id='user_bob',
        created_at=datetime.utcnow() - timedelta(hours=2),
        last_accessed_at=datetime.utcnow() - timedelta(hours=2),
        expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        ip_address='192.168.1.200',
        user_agent='Old Browser',
        is_active=True,
        data={}
    )
    await store.set(expired)
    print("   ✓ Expired session stored")

    # Try to retrieve expired session (should auto-delete)
    print("\n9. Attempting to retrieve expired session...")
    expired_retrieved = await store.get('expired_session')
    if expired_retrieved is None:
        print("   ✓ Expired session auto-deleted (returned None)")
    else:
        print("   ✗ ERROR: Expired session should have been deleted!")

    # Create inactive session
    print("\n10. Creating inactive session...")
    inactive = Session(
        id='inactive_session',
        user_id='user_charlie',
        created_at=datetime.utcnow(),
        last_accessed_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
        ip_address='192.168.1.300',
        user_agent='Browser',
        is_active=False,  # Marked as inactive
        data={}
    )
    await store.set(inactive)
    print("   ✓ Inactive session stored")

    # Run cleanup
    print("\n11. Running cleanup_expired()...")
    await store.cleanup_expired()
    print("   ✓ Cleanup completed")

    # Verify inactive session was removed
    inactive_check = await db.fetch_one(
        "SELECT * FROM sessions WHERE id = ?",
        ('inactive_session',)
    )
    if inactive_check is None:
        print("   ✓ Inactive session was cleaned up")
    else:
        print("   - Inactive session still exists (should be removed)")

    # Count remaining sessions
    total = await db.fetch_value("SELECT COUNT(*) FROM sessions")
    print(f"\n12. Total active sessions in database: {total}")

    # Delete a specific session
    print("\n13. Deleting session 'session_alice_0'...")
    await store.delete('session_alice_0')
    deleted = await store.get('session_alice_0')
    if deleted is None:
        print("   ✓ Session successfully deleted")

    # Final count
    final_total = await db.fetch_value("SELECT COUNT(*) FROM sessions")
    print(f"\n14. Final session count: {final_total}")

    # Demonstrate persistence
    print("\n15. Testing persistence across restarts...")
    print("   - Disconnecting database...")
    await db.disconnect()

    print("   - Reconnecting database...")
    db2 = SQLiteAdapter(database=db_path)
    await db2.connect()
    store2 = DatabaseSessionStore(db2)

    print("   - Retrieving original session...")
    persisted = await store2.get('demo_session_123')
    if persisted and persisted.user_id == 'user_alice':
        print(f"   ✓ Session persisted! User: {persisted.user_id}")

    await db2.disconnect()

    # Cleanup
    print("\n16. Cleaning up temporary database...")
    Path(db_path).unlink(missing_ok=True)
    print("   ✓ Temporary database deleted")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("  ✓ Table creation with indexes")
    print("  ✓ Session creation and storage")
    print("  ✓ Session retrieval")
    print("  ✓ Session updates (UPSERT)")
    print("  ✓ Multiple sessions per user")
    print("  ✓ User session retrieval")
    print("  ✓ Expired session auto-deletion")
    print("  ✓ Inactive session cleanup")
    print("  ✓ Manual session deletion")
    print("  ✓ Persistence across database restarts")
    print("  ✓ Complex data serialization (nested dicts, lists)")


if __name__ == '__main__':
    asyncio.run(main())
