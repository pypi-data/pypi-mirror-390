"""
CovetPy ORM - Production-Ready Object-Relational Mapping

A comprehensive ORM system supporting PostgreSQL, MySQL, and SQLite with:
- Field types and relationships
- Query builder with advanced filtering
- Connection pooling and transactions
- Migration system
- Async support
- Django-like synchronous API by default

Example:
    from covet.orm import Database, Model, CharField, IntegerField

    # Create database
    db = Database('sqlite:///blog.db')

    # Define model
    class Post(Model):
        id = IntegerField(primary_key=True)
        title = CharField(max_length=200)
        content = TextField()

        class Meta:
            db = db
            table_name = 'posts'

    # Create tables
    db.create_tables([Post])

    # Use the ORM (synchronous by default)
    post = Post(title='Hello', content='World')
    post.save()

    posts = Post.objects.all()
"""

from .connection import (
    ConnectionConfig,
    ConnectionPool,
    DatabaseConnection,
    register_database,
)
from .database import Database, create_database
from .exceptions import (
    DoesNotExist,
    IntegrityError,
    MultipleObjectsReturned,
    ORMError,
    TransactionError,
)
from .fields import (
    AutoField,
    BinaryField,
    BooleanField,
    CharField,
    DateTimeField,
    Field,
    FloatField,
    ForeignKey,
    IntegerField,
    JSONField,
    ManyToManyField,
    OneToManyField,
    TextField,
)
from .migrations import Migration, MigrationRunner, create_migration
from .models import Model, ModelMeta
from .query import Avg, Count, F, Max, Min, Q, QuerySet, Sum

__version__ = "1.0.0"

__all__ = [
    # Main database class
    "Database",
    "create_database",
    # Core classes
    "Model",
    "ModelMeta",
    # Field types
    "Field",
    "CharField",
    "IntegerField",
    "FloatField",
    "BooleanField",
    "DateTimeField",
    "TextField",
    "JSONField",
    "BinaryField",
    "AutoField",
    # Relationships
    "ForeignKey",
    "OneToManyField",
    "ManyToManyField",
    # Query system
    "QuerySet",
    "Q",
    "F",
    "Count",
    "Sum",
    "Avg",
    "Max",
    "Min",
    # Database connection
    "DatabaseConnection",
    "ConnectionPool",
    "ConnectionConfig",
    "register_database",
    # Migrations
    "Migration",
    "MigrationRunner",
    "create_migration",
    # Exceptions
    "ORMError",
    "DoesNotExist",
    "MultipleObjectsReturned",
    "IntegrityError",
    "TransactionError",
]
