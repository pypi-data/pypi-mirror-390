"""
ORM Database Adapter Integration - Complete Usage Example

This file demonstrates how to use the integrated ORM with database adapters.
Shows setup, model definition, and all CRUD operations with multiple databases.

Author: CovetPy Team
Date: 2025-10-10
"""

import asyncio
from datetime import datetime

from covet.database.adapters.mysql import MySQLAdapter

# Import database adapters
from covet.database.adapters.postgresql import PostgreSQLAdapter
from covet.database.adapters.sqlite import SQLiteAdapter

# Import ORM components
from covet.database.orm import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    ForeignKey,
    IntegerField,
    Model,
    TextField,
    post_save,
    receiver,
    register_adapter,
)

# ============================================================================
# Step 1: Define Models
# ============================================================================


class User(Model):
    """User model example."""

    username = CharField(max_length=100, unique=True)
    email = EmailField(unique=True)
    full_name = CharField(max_length=200, nullable=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            ("email",),
            ("username", "email"),
        ]

    def __str__(self):
        return f"User({self.username})"


class Post(Model):
    """Blog post model with foreign key relationship."""

    title = CharField(max_length=200)
    content = TextField()
    author = ForeignKey(User, on_delete=CASCADE, related_name="posts")
    published = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post({self.title})"


# ============================================================================
# Step 2: Set Up Signal Handlers (Optional)
# ============================================================================


@receiver(post_save, sender=User)
async def on_user_saved(sender, instance, created, **kwargs):
    """Signal handler for user save events."""
    if created:
        print(f"[SIGNAL] New user created: {instance.username}")
    else:
        print(f"[SIGNAL] User updated: {instance.username}")


@receiver(post_save, sender=Post)
async def on_post_saved(sender, instance, created, **kwargs):
    """Signal handler for post save events."""
    if created:
        print(f"[SIGNAL] New post created: {instance.title}")


# ============================================================================
# Step 3: Database Setup and Registration
# ============================================================================


async def setup_database_adapters():
    """
    Set up and register database adapters.

    This example shows three different databases:
    - PostgreSQL as the default database
    - MySQL as an analytics database
    - SQLite for testing/development
    """
    print("\n" + "=" * 70)
    print("SETTING UP DATABASE ADAPTERS")
    print("=" * 70 + "\n")

    # ========== PostgreSQL (Primary Database) ==========
    print("1. Setting up PostgreSQL adapter...")
    pg_adapter = PostgreSQLAdapter(
        host="localhost",
        port=5432,
        database="covet_demo",
        user="postgres",
        password="postgres",
        min_pool_size=5,
        max_pool_size=20,
    )
    await pg_adapter.connect()
    await register_adapter("default", pg_adapter, make_default=True)
    print("   ✓ PostgreSQL adapter registered as 'default'\n")

    # ========== MySQL (Analytics Database) ==========
    print("2. Setting up MySQL adapter...")
    mysql_adapter = MySQLAdapter(
        host="localhost",
        port=3306,
        database="covet_analytics",
        user="root",
        password="mysql_password",
        min_pool_size=3,
        max_pool_size=10,
    )
    await mysql_adapter.connect()
    await register_adapter("analytics", mysql_adapter)
    print("   ✓ MySQL adapter registered as 'analytics'\n")

    # ========== SQLite (Testing Database) ==========
    print("3. Setting up SQLite adapter...")
    sqlite_adapter = SQLiteAdapter(
        database=":memory:",  # In-memory database for testing
        max_pool_size=5,
    )
    await sqlite_adapter.connect()
    await register_adapter("testing", sqlite_adapter)
    print("   ✓ SQLite adapter registered as 'testing'\n")

    print("All database adapters configured successfully!\n")


# ============================================================================
# Step 4: CRUD Operations Examples
# ============================================================================


async def example_create_operations():
    """Demonstrate CREATE operations."""
    print("\n" + "=" * 70)
    print("CREATE OPERATIONS")
    print("=" * 70 + "\n")

    # Create single user
    print("1. Creating single user...")
    user1 = await User.objects.create(
        username="alice",
        email="alice@example.com",
        full_name="Alice Johnson",
        is_active=True,
    )
    print(f"   Created: {user1} (ID: {user1.id})\n")

    # Create another user using save()
    print("2. Creating user with save()...")
    user2 = User(username="bob", email="bob@example.com", full_name="Bob Smith")
    await user2.save()
    print(f"   Created: {user2} (ID: {user2.id})\n")

    # Create post with foreign key
    print("3. Creating post with foreign key...")
    post = await Post.objects.create(
        title="Getting Started with CovetPy ORM",
        content="This is a comprehensive guide to using CovetPy ORM...",
        author=user1,
        published=True,
    )
    print(f"   Created: {post} (ID: {post.id}, Author ID: {post.author})\n")

    return user1, user2, post


async def example_read_operations():
    """Demonstrate READ operations."""
    print("\n" + "=" * 70)
    print("READ OPERATIONS")
    print("=" * 70 + "\n")

    # Get single user by ID
    print("1. Get user by ID...")
    user = await User.objects.get(id=1)
    print(f"   Found: {user.username} ({user.email})\n")

    # Get user with filter
    print("2. Get user with filter...")
    user = await User.objects.get(username="alice")
    print(f"   Found: {user.username}\n")

    # Filter users
    print("3. Filter active users...")
    active_users = await User.objects.filter(is_active=True).all()
    print(f"   Found {len(active_users)} active users:")
    for u in active_users:
        print(f"      - {u.username}")
    print()

    # Field lookups
    print("4. Using field lookups...")
    users = await User.objects.filter(email__icontains="example.com").all()
    print(f"   Found {len(users)} users with 'example.com' email")
    print()

    # Complex filtering
    print("5. Complex filtering...")
    users = (
        await User.objects.filter(is_active=True)
        .exclude(username="admin")
        .order_by("-created_at")
        .limit(10)
        .all()
    )
    print(f"   Found {len(users)} users with complex filter\n")

    # Count
    print("6. Count users...")
    count = await User.objects.filter(is_active=True).count()
    print(f"   Total active users: {count}\n")

    # Exists
    print("7. Check if user exists...")
    exists = await User.objects.filter(username="alice").exists()
    print(f"   User 'alice' exists: {exists}\n")

    # First/Last
    print("8. Get first and last users...")
    first_user = await User.objects.order_by("created_at").first()
    last_user = await User.objects.order_by("created_at").last()
    print(f"   First user: {first_user.username if first_user else None}")
    print(f"   Last user: {last_user.username if last_user else None}\n")


async def example_update_operations():
    """Demonstrate UPDATE operations."""
    print("\n" + "=" * 70)
    print("UPDATE OPERATIONS")
    print("=" * 70 + "\n")

    # Update single instance
    print("1. Update single user instance...")
    user = await User.objects.get(username="alice")
    print(f"   Before: {user.full_name}")
    user.full_name = "Alice Johnson-Smith"
    await user.save()
    print(f"   After: {user.full_name}\n")

    # Update with specific fields
    print("2. Update specific fields...")
    user = await User.objects.get(username="bob")
    user.is_active = False
    await user.save(update_fields=["is_active"])
    print(f"   Updated is_active for {user.username}\n")

    # Bulk update
    print("3. Bulk update...")
    updated_count = await User.objects.filter(is_active=True).update(is_active=True)
    print(f"   Updated {updated_count} users\n")

    # Update or create
    print("4. Update or create...")
    user, created = await User.objects.update_or_create(
        username="charlie",
        defaults={
            "email": "charlie@example.com",
            "full_name": "Charlie Brown",
            "is_active": True,
        },
    )
    print(f"   {'Created' if created else 'Updated'}: {user.username}\n")


async def example_delete_operations():
    """Demonstrate DELETE operations."""
    print("\n" + "=" * 70)
    print("DELETE OPERATIONS")
    print("=" * 70 + "\n")

    # Delete single instance
    print("1. Delete single user...")
    user = await User.objects.get(username="charlie")
    result = await user.delete()
    print(f"   Deleted {result[0]} record(s)\n")

    # Bulk delete
    print("2. Bulk delete...")
    deleted_count = await User.objects.filter(is_active=False).delete()
    print(f"   Deleted {deleted_count} inactive users\n")


async def example_advanced_queries():
    """Demonstrate advanced query features."""
    print("\n" + "=" * 70)
    print("ADVANCED QUERY OPERATIONS")
    print("=" * 70 + "\n")

    # Values (return dicts)
    print("1. Values query (returns dicts)...")
    users = await User.objects.values("id", "username", "email").all()
    print(f"   Retrieved {len(users)} users as dictionaries")
    if users:
        print(f"   Example: {users[0]}\n")

    # Values list (return tuples)
    print("2. Values list query (returns tuples)...")
    usernames = await User.objects.values_list("username", flat=True).all()
    print(f"   Usernames: {usernames}\n")

    # Distinct
    print("3. Distinct query...")
    distinct_emails = await User.objects.values_list("email", flat=True).distinct().all()
    print(f"   Found {len(distinct_emails)} distinct emails\n")

    # Pagination
    print("4. Pagination...")
    page_1 = await User.objects.order_by("id").limit(2).offset(0).all()
    page_2 = await User.objects.order_by("id").limit(2).offset(2).all()
    print(f"   Page 1: {[u.username for u in page_1]}")
    print(f"   Page 2: {[u.username for u in page_2]}\n")


async def example_transactions():
    """Demonstrate transaction support."""
    print("\n" + "=" * 70)
    print("TRANSACTION OPERATIONS")
    print("=" * 70 + "\n")

    from covet.database.orm import get_adapter

    print("1. Using transactions...")
    adapter = await get_adapter("default")

    try:
        async with adapter.transaction():
            print("   Creating users in transaction...")
            user1 = await User.objects.create(username="trans_user_1", email="trans1@example.com")
            user2 = await User.objects.create(username="trans_user_2", email="trans2@example.com")
            print(f"   Created {user1.username} and {user2.username}")
            print("   Transaction committed successfully!\n")
    except Exception as e:
        print(f"   Transaction rolled back: {e}\n")


# ============================================================================
# Step 5: Main Execution
# ============================================================================


async def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("COVETPY ORM - DATABASE ADAPTER INTEGRATION EXAMPLE")
    print("=" * 70)

    try:
        # Setup adapters
        await setup_database_adapters()

        # Create sample data
        await example_create_operations()

        # Read operations
        await example_read_operations()

        # Update operations
        await example_update_operations()

        # Advanced queries
        await example_advanced_queries()

        # Transactions
        await example_transactions()

        # Delete operations (last to clean up)
        await example_delete_operations()

        print("\n" + "=" * 70)
        print("EXAMPLE COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
