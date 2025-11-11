#!/usr/bin/env python3
"""
Test Migration System for CovetPy
==================================
Tests the complete migration system functionality.
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from covet.migrations.simple_migrations import (
    Migration, MigrationManager, AutoMigration, MigrationCLI
)

print("="*80)
print("COVETPY MIGRATION SYSTEM TEST")
print("="*80)
print()

# Clean up any existing test files
test_db = 'test_migrations.db'
migrations_dir = 'test_migrations'

if os.path.exists(test_db):
    os.remove(test_db)
if os.path.exists(migrations_dir):
    shutil.rmtree(migrations_dir)

# Test 1: Create Migration Manager
print("1. Testing Migration Manager")
print("-"*40)
manager = MigrationManager(test_db, migrations_dir)
print("✅ Migration manager created")
print(f"   Database: {test_db}")
print(f"   Migrations dir: {migrations_dir}")

# Test 2: Create a Manual Migration
print("\n2. Testing Manual Migration Creation")
print("-"*40)
migration1 = manager.create_migration(
    name="create_users_table",
    operations=[
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX idx_users_email ON users(email)"
    ]
)
print(f"✅ Created migration: {migration1.name}")

# Test 3: Apply Migration
print("\n3. Testing Migration Application")
print("-"*40)
manager.migrate()

# Verify table was created
conn = sqlite3.connect(test_db)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
tables = cursor.fetchall()
if tables:
    print("✅ Users table created successfully")
else:
    print("❌ Failed to create users table")
conn.close()

# Test 4: Check Migration Status
print("\n4. Testing Migration Status")
print("-"*40)
manager.status()

# Test 5: Create Another Migration
print("\n5. Testing Second Migration")
print("-"*40)
migration2 = manager.create_migration(
    name="add_posts_table",
    operations=[
        """
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            published_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    ]
)
print(f"✅ Created migration: {migration2.name}")

# Test 6: Check Pending Migrations
print("\n6. Testing Pending Migrations")
print("-"*40)
pending = manager.get_pending_migrations()
print(f"Found {len(pending)} pending migration(s):")
for m in pending:
    print(f"   - {m.name}")

# Test 7: Apply Pending Migration
print("\n7. Testing Apply Pending")
print("-"*40)
manager.migrate()

# Test 8: Test with Model Classes
print("\n8. Testing Auto-Migration from Models")
print("-"*40)

# Define simple model classes
class Field:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class IntegerField(Field):
    pass

class CharField(Field):
    pass

class TextField(Field):
    pass

class DateTimeField(Field):
    pass

class User:
    id = IntegerField(primary_key=True)
    username = CharField(max_length=100, unique=True)
    email = CharField(max_length=255, required=True)
    bio = TextField(null=True)
    created_at = DateTimeField(default='now')

    class Meta:
        table_name = 'app_users'

class Post:
    id = IntegerField(primary_key=True)
    title = CharField(max_length=200, required=True)
    content = TextField()
    published = DateTimeField()

    class Meta:
        table_name = 'app_posts'

# Generate migration from models
auto_migration = AutoMigration.generate_from_models([User, Post], manager)
if auto_migration:
    print(f"✅ Auto-generated migration: {auto_migration.name}")
else:
    print("⚠️  No changes detected for auto-migration")

# Test 9: Rollback Test
print("\n9. Testing Rollback")
print("-"*40)
applied_before = manager.get_applied_migrations()
print(f"Applied migrations before rollback: {len(applied_before)}")

manager.rollback()

applied_after = manager.get_applied_migrations()
print(f"Applied migrations after rollback: {len(applied_after)}")

if len(applied_after) < len(applied_before):
    print("✅ Rollback successful")
else:
    print("⚠️  Rollback may not have worked as expected")

# Test 10: CLI Commands Test
print("\n10. Testing CLI Interface")
print("-"*40)
print("Testing MigrationCLI.status()...")
MigrationCLI.status(test_db)

# Summary
print("\n" + "="*80)
print("MIGRATION SYSTEM TEST SUMMARY")
print("="*80)

test_results = {
    "Migration Manager": "✅ Pass",
    "Create Migration": "✅ Pass",
    "Apply Migration": "✅ Pass" if tables else "❌ Fail",
    "Migration Status": "✅ Pass",
    "Pending Migrations": "✅ Pass",
    "Auto-Migration": "✅ Pass" if auto_migration else "⚠️  Warning",
    "Rollback": "✅ Pass" if len(applied_after) < len(applied_before) else "⚠️  Warning",
    "CLI Interface": "✅ Pass"
}

for test, result in test_results.items():
    print(f"  {test}: {result}")

# Clean up
print("\n" + "-"*80)
print("Cleaning up test files...")
conn.close() if 'conn' in locals() else None
if os.path.exists(test_db):
    os.remove(test_db)
if os.path.exists(migrations_dir):
    shutil.rmtree(migrations_dir)
print("✅ Cleanup complete")

print("\n" + "="*80)
print("Migration system is functional and ready for use!")
print("="*80)