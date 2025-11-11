"""
ORM Quick Start Guide

This example demonstrates the CovetPy ORM with synchronous (Django-like) operations.
All operations work synchronously by default - no async/await required!
"""

import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from covet.orm import (
    Database,
    Model,
    CharField,
    IntegerField,
    TextField,
    BooleanField,
    DateTimeField,
    ForeignKey,
)
from datetime import datetime


# ============================================================================
# STEP 1: Create Database Connection
# ============================================================================

print("=" * 70)
print("CovetPy ORM - Quick Start Example")
print("=" * 70)

# Create database (uses SQLite by default)
db = Database('sqlite:///quickstart.db')
print(f"\n✓ Database created: {db}")


# ============================================================================
# STEP 2: Define Models
# ============================================================================

class User(Model):
    """User model with basic fields."""
    id = IntegerField(primary_key=True)
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        db = db
        table_name = 'users'

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Post(Model):
    """Post model with foreign key relationship."""
    id = IntegerField(primary_key=True)
    title = CharField(max_length=200)
    content = TextField()
    author_id = IntegerField()  # Foreign key to User
    published = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        db = db
        table_name = 'posts'

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}')>"


print("\n✓ Models defined: User, Post")


# ============================================================================
# STEP 3: Create Tables
# ============================================================================

print("\n" + "-" * 70)
print("Creating database tables...")
print("-" * 70)

db.create_tables([User, Post])
print("✓ Tables created successfully")


# ============================================================================
# STEP 4: Create Records (Synchronous)
# ============================================================================

print("\n" + "-" * 70)
print("Creating records (synchronous operations)...")
print("-" * 70)

# Create users
user1 = User(username='alice', email='alice@example.com', is_active=1)
user1.save()
print(f"✓ Created user: {user1}")

user2 = User(username='bob', email='bob@example.com', is_active=1)
user2.save()
print(f"✓ Created user: {user2}")

user3 = User(username='charlie', email='charlie@example.com', is_active=0)
user3.save()
print(f"✓ Created user: {user3}")

# Create posts
post1 = Post(
    title='Hello World',
    content='This is my first post!',
    author_id=user1.id,
    published=1
)
post1.save()
print(f"✓ Created post: {post1}")

post2 = Post(
    title='Python Tips',
    content='Here are some Python tips...',
    author_id=user1.id,
    published=1
)
post2.save()
print(f"✓ Created post: {post2}")

post3 = Post(
    title='Draft Post',
    content='This is a draft...',
    author_id=user2.id,
    published=0
)
post3.save()
print(f"✓ Created post: {post3}")


# ============================================================================
# STEP 5: Query Records (Synchronous)
# ============================================================================

print("\n" + "-" * 70)
print("Querying records (synchronous operations)...")
print("-" * 70)

# Get all users
all_users = User.objects.all()
print(f"\n✓ All users ({len(all_users)}):")
for user in all_users:
    print(f"  - {user}")

# Filter users
active_users = User.objects.filter(is_active=1)
print(f"\n✓ Active users ({len(active_users)}):")
for user in active_users:
    print(f"  - {user}")

# Get single user
try:
    alice = User.objects.filter(username='alice').first()
    print(f"\n✓ Found user by username: {alice}")
except Exception as e:
    print(f"✗ Error: {e}")

# Get all posts
all_posts = Post.objects.all()
print(f"\n✓ All posts ({len(all_posts)}):")
for post in all_posts:
    print(f"  - {post}")

# Filter published posts
published_posts = Post.objects.filter(published=1)
print(f"\n✓ Published posts ({len(published_posts)}):")
for post in published_posts:
    print(f"  - {post}")

# Count records
user_count = User.objects.count()
post_count = Post.objects.count()
print(f"\n✓ Statistics:")
print(f"  - Total users: {user_count}")
print(f"  - Total posts: {post_count}")


# ============================================================================
# STEP 6: Update Records (Synchronous)
# ============================================================================

print("\n" + "-" * 70)
print("Updating records (synchronous operations)...")
print("-" * 70)

# Update a single record
user = User.objects.filter(username='charlie').first()
user.is_active = 1
user.save()
print(f"✓ Updated user: {user}")

# Bulk update
User.objects.filter(is_active=0).update(is_active=1)
print("✓ Bulk updated all inactive users")


# ============================================================================
# STEP 7: Delete Records (Synchronous)
# ============================================================================

print("\n" + "-" * 70)
print("Deleting records (synchronous operations)...")
print("-" * 70)

# Delete a single record
draft_post = Post.objects.filter(published=0).first()
if draft_post:
    draft_post.delete()
    print(f"✓ Deleted post: {draft_post}")

# Count remaining posts
remaining_posts = Post.objects.count()
print(f"✓ Remaining posts: {remaining_posts}")


# ============================================================================
# STEP 8: Advanced Queries
# ============================================================================

print("\n" + "-" * 70)
print("Advanced query operations...")
print("-" * 70)

# Order by
users_ordered = User.objects.order_by('-id')
print(f"\n✓ Users ordered by ID (descending):")
for user in users_ordered:
    print(f"  - {user}")

# Limit results
first_two_users = User.objects.all()[:2]
print(f"\n✓ First 2 users:")
for user in first_two_users:
    print(f"  - {user}")

# Exists check
has_active_users = User.objects.filter(is_active=1).exists()
print(f"\n✓ Has active users: {has_active_users}")

# Get or create
new_user, created = User.objects.get_or_create(
    username='dave',
    defaults={'email': 'dave@example.com', 'is_active': 1}
)
print(f"\n✓ Get or create: {new_user} (created={created})")


# ============================================================================
# STEP 9: Transactions
# ============================================================================

print("\n" + "-" * 70)
print("Transaction example...")
print("-" * 70)

try:
    with db.transaction():
        # Create user and post in transaction
        new_user = User(username='eve', email='eve@example.com')
        new_user.save()

        new_post = Post(
            title='Atomic Post',
            content='Created in transaction',
            author_id=new_user.id
        )
        new_post.save()

        print(f"✓ Transaction completed: user={new_user}, post={new_post}")
except Exception as e:
    print(f"✗ Transaction failed: {e}")


# ============================================================================
# STEP 10: Raw SQL
# ============================================================================

print("\n" + "-" * 70)
print("Raw SQL example...")
print("-" * 70)

# Execute raw query
results = db.fetch_all("SELECT username, email FROM users WHERE is_active = ?", (1,))
print(f"\n✓ Raw SQL results ({len(results)} rows):")
for row in results:
    print(f"  - {row}")


# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("Quick Start Complete!")
print("=" * 70)
print("""
✓ All operations completed successfully!

Key Features Demonstrated:
  - Synchronous operations (no async/await needed)
  - Model definition with fields and relationships
  - CRUD operations (Create, Read, Update, Delete)
  - Filtering, ordering, and limiting
  - Transactions
  - Raw SQL support

Next Steps:
  - Try async operations with async def and await
  - Explore relationships (ForeignKey, ManyToMany)
  - Use migrations for schema changes
  - Add indexes and constraints

Happy coding with CovetPy ORM!
""")

# Cleanup
print("\nClosing database connection...")
db.close()
print("✓ Database closed")
