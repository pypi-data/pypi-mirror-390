# CovetPy Database Migration System

A comprehensive database migration system for CovetPy framework, similar to Django and Alembic.

## Features

- **Auto-generation**: Automatically detect model changes and generate migrations
- **Multi-database support**: PostgreSQL, MySQL, and SQLite
- **Version control**: Track migration history with checksums
- **Rollback support**: Safely rollback migrations when needed
- **Schema operations**: Support for all common schema changes
- **Foreign key constraints**: Manage relationships between tables
- **CLI interface**: Easy-to-use command-line tools

## Installation

Make sure CovetPy is installed:

```bash
pip install -e /path/to/NeutrinoPy
```

## Quick Start

### 1. Configure Database

Create a `covet.config.py` file in your project root:

```python
DATABASE = {
    "engine": "sqlite",
    "database": "myapp.db",
}
```

For PostgreSQL:
```python
DATABASE = {
    "engine": "postgresql",
    "database": "myapp_db",
    "host": "localhost",
    "port": 5432,
    "username": "postgres",
    "password": "password",
}
```

### 2. Define Models

Create your models using CovetPy ORM:

```python
from covet.orm.models import Model
from covet.orm.fields import AutoField, CharField, IntegerField

class User(Model):
    id = AutoField()
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=100, unique=True)
    age = IntegerField(null=True)

    class Meta:
        table_name = "users"
```

### 3. Generate Migrations

Detect changes and generate migrations:

```bash
python covet-cli.py makemigrations
```

Or with a custom name:
```bash
python covet-cli.py makemigrations --name create_user_table
```

### 4. Apply Migrations

Apply pending migrations to the database:

```bash
python covet-cli.py migrate
```

Skip confirmation:
```bash
python covet-cli.py migrate --yes
```

### 5. Check Migration Status

View all migrations and their status:

```bash
python covet-cli.py showmigrations
```

### 6. Rollback Migrations

Rollback the last applied migration:

```bash
python covet-cli.py rollback
```

Skip confirmation:
```bash
python covet-cli.py rollback --yes
```

## CLI Commands

### makemigrations

Generate migrations from model changes.

```bash
python covet-cli.py makemigrations [OPTIONS]

Options:
  --name, -n NAME           Migration name (auto-generated if not provided)
  --app, -a APP            App name (default: default)
  --migrations-dir, -d DIR Migrations directory (default: migrations)
```

### migrate

Apply pending migrations to the database.

```bash
python covet-cli.py migrate [OPTIONS]

Options:
  --fake                   Mark migrations as applied without executing
  --yes, -y               Skip confirmation
  --migrations-dir, -d DIR Migrations directory (default: migrations)
```

### rollback

Rollback the last applied migration.

```bash
python covet-cli.py rollback [OPTIONS]

Options:
  --yes, -y               Skip confirmation
  --migrations-dir, -d DIR Migrations directory (default: migrations)
```

### showmigrations

Display migration status.

```bash
python covet-cli.py showmigrations [OPTIONS]

Options:
  --migrations-dir, -d DIR Migrations directory (default: migrations)
```

## Migration Operations

### Supported Operations

1. **CreateTable** - Create a new table
2. **DropTable** - Drop an existing table
3. **AddColumn** - Add a column to a table
4. **DropColumn** - Drop a column from a table
5. **AlterColumn** - Modify a column definition
6. **RenameTable** - Rename a table
7. **RenameColumn** - Rename a column
8. **CreateIndex** - Create an index
9. **DropIndex** - Drop an index
10. **AddForeignKey** - Add a foreign key constraint
11. **DropForeignKey** - Drop a foreign key constraint
12. **RunSQL** - Execute custom SQL

### Example Migration File

```python
"""
Migration: create_users_table
App: default
Generated: 2024-01-01T12:00:00
"""

from covet.orm.migrations import Migration
from covet.orm.fields import *


def upgrade():
    """Apply migration."""
    migration = Migration(
        name="create_users_table",
        app="default",
        dependencies=[]
    )

    # Operations
    operations = [
        CreateTable("users", {
            "id": AutoField(),
            "username": CharField(max_length=50, unique=True),
            "email": CharField(max_length=100, unique=True),
            "created_at": DateTimeField(auto_now_add=True),
        })
    ]

    for op in operations:
        migration.add_operation(op)

    return migration


def downgrade():
    """Rollback migration."""
    # Rollback is handled automatically by the migration system
    pass
```

## Programmatic Usage

You can also use the migration system programmatically:

```python
from covet.orm.connection import ConnectionConfig, register_database
from covet.orm.migrations import (
    MigrationEngine,
    MigrationRunner,
    MigrationWriter,
    Migration,
    CreateTable,
    AddColumn,
)
from covet.orm.fields import CharField, IntegerField

# Setup database
config = ConnectionConfig(
    engine="sqlite",
    database="myapp.db"
)
register_database("default", config)

# Create migration manually
migration = Migration("add_age_column", "default")
migration.add_column("users", "age", IntegerField(null=True))

# Apply migration
runner = MigrationRunner("default")
runner.apply_migration(migration)

# Or auto-detect changes
engine = MigrationEngine("default")
operations = engine.detect_changes(models)
migration = engine.generate_migration("auto_migration", operations)

# Write to file
writer = MigrationWriter("migrations")
filepath = writer.write_migration(migration)
```

## Database Support

### SQLite

- Fully supported for basic operations
- Limited support for column operations (no DROP COLUMN, ALTER COLUMN, RENAME COLUMN)
- No support for adding foreign keys to existing tables

### PostgreSQL

- Full support for all operations
- Requires `psycopg2` or `asyncpg` for async operations

```bash
pip install psycopg2-binary
# or
pip install asyncpg
```

### MySQL

- Full support for all operations
- Requires `PyMySQL` or `aiomysql` for async operations

```bash
pip install PyMySQL
# or
pip install aiomysql
```

## Best Practices

1. **Version Control**: Always commit migration files to version control
2. **Testing**: Test migrations on a copy of production data before applying
3. **Rollback Plan**: Always have a rollback plan for production migrations
4. **Dependencies**: Specify migration dependencies when needed
5. **Naming**: Use descriptive names for migrations
6. **Review**: Review auto-generated migrations before applying
7. **Backups**: Always backup your database before running migrations

## Advanced Features

### Migration Dependencies

Specify dependencies between migrations:

```python
migration = Migration(
    name="add_user_profile",
    app="default",
    dependencies=["create_users_table"]
)
```

### Custom SQL Operations

Execute custom SQL in migrations:

```python
migration.run_sql(
    sql="CREATE INDEX idx_username_email ON users(username, email)",
    reverse_sql="DROP INDEX idx_username_email"
)
```

### Fake Migrations

Mark migrations as applied without executing (useful for existing databases):

```bash
python covet-cli.py migrate --fake
```

### Schema Introspection

Programmatically inspect database schema:

```python
from covet.orm.migrations import SchemaIntrospector
from covet.orm.connection import get_connection_pool

pool = get_connection_pool("default")
with pool.connection() as conn:
    introspector = SchemaIntrospector(conn)

    # Get all tables
    tables = introspector.get_tables()

    # Get table schema
    schema = introspector.get_table_schema("users")
    print(schema.columns)
    print(schema.indexes)
    print(schema.constraints)
```

## Troubleshooting

### Migration Failed

If a migration fails:
1. Check the error message
2. Fix the issue
3. Rollback if needed: `python covet-cli.py rollback`
4. Fix the migration file
5. Try again

### No Models Found

If no models are detected:
1. Make sure models inherit from `covet.orm.Model`
2. Import models in your main module
3. Check that models are properly registered

### Database Connection Issues

If you can't connect to the database:
1. Check `covet.config.py` configuration
2. Verify database credentials
3. Ensure database server is running
4. Check network connectivity

## Example Project Structure

```
myproject/
├── covet.config.py          # Database configuration
├── models.py                # Model definitions
├── migrations/              # Migration files
│   ├── __init__.py
│   ├── 20240101_120000_create_users.py
│   ├── 20240101_130000_add_age_column.py
│   └── 20240101_140000_create_products.py
├── main.py                  # Application entry point
└── covet-cli.py            # CLI entry point
```

## Contributing

Contributions are welcome! Please see the main CovetPy documentation for contribution guidelines.

## License

Part of the CovetPy framework. See main project license for details.
