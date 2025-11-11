"""
Migration Base Class
===================

Base class for all database migration files. Provides a simple,
Django-like interface for defining schema changes.

Example:
-------

```python
from covet.migrations import Migration

class CreateUsersTable(Migration):
    \"\"\"Create users table with email and password fields.\"\"\"
    
    dependencies = []  # No dependencies
    
    forward_sql = [
        \"\"\"
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        \"\"\",
        "CREATE INDEX idx_users_email ON users(email)",
    ]
    
    backward_sql = [
        "DROP INDEX IF EXISTS idx_users_email",
        "DROP TABLE IF EXISTS users",
    ]
```

Advanced Usage:
--------------

For complex migrations, you can override apply() and rollback():

```python
class DataMigration(Migration):
    \"\"\"Custom data migration.\"\"\"
    
    async def apply(self, adapter):
        # Custom forward logic
        users = await adapter.fetch_all("SELECT * FROM old_users")
        for user in users:
            await adapter.execute(
                "INSERT INTO users (email, password_hash) VALUES ($1, $2)",
                [user['email'], user['password']]
            )
    
    async def rollback(self, adapter):
        # Custom rollback logic
        await adapter.execute("DELETE FROM users WHERE migrated = true")
```

Schema Operations:
-----------------

Common patterns for schema changes:

**Create Table:**
```python
forward_sql = [
    \"\"\"
    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        content TEXT,
        author_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    \"\"\"
]
backward_sql = ["DROP TABLE IF EXISTS posts"]
```

**Add Column:**
```python
forward_sql = [
    "ALTER TABLE users ADD COLUMN last_login TIMESTAMP"
]
backward_sql = [
    "ALTER TABLE users DROP COLUMN last_login"
]
```

**Add Index:**
```python
forward_sql = [
    "CREATE INDEX idx_posts_author ON posts(author_id)",
    "CREATE INDEX idx_posts_created ON posts(created_at)",
]
backward_sql = [
    "DROP INDEX idx_posts_created",
    "DROP INDEX idx_posts_author",
]
```

**Add Foreign Key:**
```python
forward_sql = [
    \"\"\"
    ALTER TABLE posts 
    ADD CONSTRAINT fk_posts_author 
    FOREIGN KEY (author_id) REFERENCES users(id)
    ON DELETE CASCADE
    \"\"\"
]
backward_sql = [
    "ALTER TABLE posts DROP CONSTRAINT fk_posts_author"
]
```

Best Practices:
--------------

1. **Always provide backward_sql**: Every migration should be reversible
2. **Use transactions**: The system wraps operations in transactions automatically
3. **Test rollbacks**: Always test that your backward_sql works correctly
4. **Keep migrations small**: One logical change per migration
5. **Don't modify applied migrations**: Create new migrations for changes
6. **Use IF EXISTS/IF NOT EXISTS**: Makes migrations more robust
7. **Handle data carefully**: Test data migrations on production-like data

Security:
--------

All migrations are validated before execution:
- AST parsing to detect dangerous code
- Path traversal protection
- SQL injection prevention through parameterized queries
- Restricted namespace execution

Performance:
-----------

For large tables:
- Add indexes CONCURRENTLY (PostgreSQL)
- Consider maintenance windows for ALTER TABLE
- Test on production-like data volumes
- Use batched operations for data migrations

Author: CovetPy Team
License: MIT
"""

# Re-export the base Migration class from database.migrations
from ..database.migrations.runner import Migration

# Convenience wrapper for creating simple migrations
class SimpleMigration(Migration):
    """
    Simplified migration class for quick schema changes.
    
    Just set forward_sql and backward_sql class attributes.
    
    Example:
        class AddEmailIndex(SimpleMigration):
            forward_sql = ["CREATE INDEX idx_users_email ON users(email)"]
            backward_sql = ["DROP INDEX idx_users_email"]
    """
    pass

__all__ = [
    "Migration",
    "SimpleMigration",
]
