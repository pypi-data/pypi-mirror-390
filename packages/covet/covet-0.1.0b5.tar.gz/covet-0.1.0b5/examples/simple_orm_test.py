"""
Simple ORM Test - Minimal example to test the ORM

This is a simplified version that tests basic CRUD operations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from covet.orm import Database, Model, CharField, IntegerField, BooleanField

print("=" * 70)
print("Simple ORM Test")
print("=" * 70)

# Create database
db = Database('sqlite:///simple_test.db')
print(f"\n✓ Database: {db}")


# Define model
class User(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=100)
    email = CharField(max_length=255)
    active = BooleanField(default=True)

    class Meta:
        db = db
        table_name = 'users'


# Create table
db.create_tables([User])
print("✓ Table created\n")

# Test 1: Create records
print("Test 1: Create records")
print("-" * 40)
user1 = User(name='Alice', email='alice@example.com', active=1)
user1.save()
print(f"✓ Created: {user1}")

user2 = User(name='Bob', email='bob@example.com', active=1)
user2.save()
print(f"✓ Created: {user2}")

user3 = User(name='Charlie', email='charlie@example.com', active=0)
user3.save()
print(f"✓ Created: {user3}\n")

# Test 2: Query all
print("Test 2: Query all records")
print("-" * 40)
all_users = User.objects.all()
print(f"Found {len(all_users)} users:")
for user in all_users:
    print(f"  - {user}")
print()

# Test 3: Filter
print("Test 3: Filter by active=1")
print("-" * 40)
active_users = User.objects.filter(active=1)
print(f"Found {len(active_users)} active users:")
for user in active_users:
    print(f"  - {user}")
print()

# Test 4: Get first
print("Test 4: Get first user")
print("-" * 40)
first_user = User.objects.all().first()
print(f"First user: {first_user}\n")

# Test 5: Count
print("Test 5: Count records")
print("-" * 40)
count = User.objects.count()
print(f"Total users: {count}\n")

# Test 6: Raw SQL
print("Test 6: Raw SQL query")
print("-" * 40)
results = db.fetch_all("SELECT name, email FROM users WHERE active = ?", (1,))
print(f"Active users via raw SQL:")
for row in results:
    print(f"  - {row}\n")

# Test 7: Delete
print("Test 7: Delete a record")
print("-" * 40)
user_to_delete = User.objects.filter(active=0).first()
if user_to_delete:
    print(f"Deleting: {user_to_delete}")
    user_to_delete.delete()
    remaining = User.objects.count()
    print(f"✓ Deleted. Remaining users: {remaining}\n")

print("=" * 70)
print("All tests completed!")
print("=" * 70)

# Cleanup
db.close()
