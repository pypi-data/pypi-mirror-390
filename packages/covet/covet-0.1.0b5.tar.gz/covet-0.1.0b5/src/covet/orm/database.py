"""
Unified Database API - Django-like ORM Interface

This module provides a simple, synchronous-first database API similar to Django ORM.
It wraps the existing async adapters and provides both sync and async interfaces.

Example:
    # Synchronous (default)
    from covet.orm import Database, Model, CharField, IntegerField

    db = Database('sqlite:///app.db')

    class User(Model):
        id = IntegerField(primary_key=True)
        name = CharField(max_length=100)
        email = CharField(max_length=255)

        class Meta:
            db = db
            table_name = 'users'

    # Sync operations
    db.create_tables([User])

    user = User(name='Alice', email='alice@example.com')
    user.save()  # Sync save

    users = User.objects.all()  # Sync query
"""

import asyncio
import logging
import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Type, Union
from urllib.parse import urlparse

from .connection import ConnectionConfig, ConnectionPool, register_database
from .exceptions import ConnectionError, ORMError

logger = logging.getLogger(__name__)


class SyncDatabaseAdapter:
    """
    Synchronous wrapper around async database adapters.

    This allows the ORM to work synchronously by default (like Django),
    while still supporting async operations when needed.
    """

    def __init__(self, connection_url: str, **kwargs):
        """
        Initialize sync database adapter.

        Args:
            connection_url: Database URL (sqlite:///path/to/db.db, postgresql://..., mysql://...)
            **kwargs: Additional connection parameters
        """
        self.connection_url = connection_url
        self.kwargs = kwargs
        self._parse_url()

        # For SQLite, we use sync sqlite3 directly for better performance
        if self.engine == 'sqlite':
            self._setup_sqlite()
        else:
            self._setup_other()

    def _parse_url(self):
        """Parse database URL."""
        parsed = urlparse(self.connection_url)
        self.engine = parsed.scheme

        if self.engine == 'sqlite':
            # Handle both sqlite:///path and sqlite://path formats
            self.database = parsed.path.lstrip('/')
            if not self.database:
                self.database = ':memory:'
        elif self.engine in ('postgresql', 'mysql'):
            self.database = parsed.path.lstrip('/')
            self.host = parsed.hostname or 'localhost'
            self.port = parsed.port
            self.username = parsed.username or ''
            self.password = parsed.password or ''
        else:
            raise ValueError(f"Unsupported database engine: {self.engine}")

    def _setup_sqlite(self):
        """Setup SQLite with thread-local connections."""
        self._local = threading.local()
        self.connection_factory = lambda: sqlite3.connect(
            self.database,
            check_same_thread=False,
            timeout=self.kwargs.get('timeout', 30.0)
        )

    def _setup_other(self):
        """Setup PostgreSQL/MySQL with connection pooling."""
        # Use the existing ConnectionPool for PostgreSQL/MySQL
        config = ConnectionConfig(
            engine=self.engine,
            host=self.host,
            port=self.port,
            database=self.database,
            username=self.username,
            password=self.password,
            **self.kwargs
        )
        self._pool = ConnectionPool(config)

    def _get_connection(self):
        """Get a connection for the current thread."""
        if self.engine == 'sqlite':
            if not hasattr(self._local, 'connection'):
                conn = self.connection_factory()
                conn.row_factory = sqlite3.Row
                # Enable foreign keys
                conn.execute('PRAGMA foreign_keys = ON')
                self._local.connection = conn
            return self._local.connection
        else:
            return self._pool.get_connection()

    def _return_connection(self, conn):
        """Return connection to pool (for non-SQLite)."""
        if self.engine != 'sqlite':
            self._pool.return_connection(conn)

    def execute(self, query: str, params: Optional[Union[tuple, list]] = None) -> Any:
        """
        Execute a query synchronously.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Cursor object
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            if self.engine != 'sqlite':
                self._return_connection(conn)
            raise

    def execute_commit(self, query: str, params: Optional[Union[tuple, list]] = None) -> int:
        """
        Execute a query and commit synchronously.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            if self.engine != 'sqlite':
                self._return_connection(conn)

    def fetch_one(self, query: str, params: Optional[Union[tuple, list]] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch one row as a dictionary.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Dictionary with row data or None
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            cursor.close()

            if row:
                return dict(row)
            return None
        finally:
            if self.engine != 'sqlite':
                self._return_connection(conn)

    def fetch_all(self, query: str, params: Optional[Union[tuple, list]] = None) -> List[Dict[str, Any]]:
        """
        Fetch all rows as a list of dictionaries.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of dictionaries
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()

            return [dict(row) for row in rows]
        finally:
            if self.engine != 'sqlite':
                self._return_connection(conn)

    def commit(self):
        """Commit transaction."""
        if self.engine == 'sqlite':
            conn = self._get_connection()
            conn.commit()
        # For pooled connections, commit is handled per-operation

    def rollback(self):
        """Rollback transaction."""
        if self.engine == 'sqlite':
            conn = self._get_connection()
            conn.rollback()
        # For pooled connections, rollback is handled per-operation

    @contextmanager
    def transaction(self):
        """Transaction context manager."""
        conn = self._get_connection()
        try:
            if self.engine == 'sqlite':
                conn.execute('BEGIN')
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if self.engine != 'sqlite':
                self._return_connection(conn)

    def close(self):
        """Close connections."""
        if self.engine == 'sqlite':
            if hasattr(self._local, 'connection'):
                self._local.connection.close()
                del self._local.connection
        else:
            self._pool.close_all()


class Database:
    """
    Main Database class - Entry point for all database operations.

    This provides a Django-like ORM interface with synchronous operations
    by default and async support when needed.

    Example:
        # Create database instance
        db = Database('sqlite:///blog.db')

        # Define models
        class Post(Model):
            id = IntegerField(primary_key=True)
            title = CharField(max_length=200)
            content = TextField()

            class Meta:
                db = db
                table_name = 'posts'

        # Create tables
        db.create_tables([Post])

        # Use the models
        post = Post(title='Hello', content='World')
        post.save()  # Synchronous save

        posts = Post.objects.all()  # Synchronous query

        # Async operations (optional)
        async def async_example():
            await post.asave()  # Async save
            posts = await Post.objects.async_all()  # Async query
    """

    def __init__(self, connection_url: str, name: str = 'default', **kwargs):
        """
        Initialize database connection.

        Args:
            connection_url: Database URL (e.g., 'sqlite:///app.db', 'postgresql://user:pass@localhost/db')
            name: Database name for registry (default: 'default')
            **kwargs: Additional connection parameters
        """
        self.connection_url = connection_url
        self.name = name
        self.kwargs = kwargs

        # Create sync adapter
        self._sync_adapter = SyncDatabaseAdapter(connection_url, **kwargs)

        # Register with ORM system
        self._register_with_orm()

        logger.info(f"Database initialized: {connection_url}")

    def _register_with_orm(self):
        """Register database with ORM connection system."""
        parsed = urlparse(self.connection_url)
        engine = parsed.scheme

        if engine == 'sqlite':
            database = parsed.path.lstrip('/') or ':memory:'
            config = ConnectionConfig(
                engine='sqlite',
                database=database,
                **self.kwargs
            )
        elif engine == 'postgresql':
            config = ConnectionConfig(
                engine='postgresql',
                host=parsed.hostname or 'localhost',
                port=parsed.port or 5432,
                database=parsed.path.lstrip('/'),
                username=parsed.username or '',
                password=parsed.password or '',
                **self.kwargs
            )
        elif engine == 'mysql':
            config = ConnectionConfig(
                engine='mysql',
                host=parsed.hostname or 'localhost',
                port=parsed.port or 3306,
                database=parsed.path.lstrip('/'),
                username=parsed.username or '',
                password=parsed.password or '',
                **self.kwargs
            )
        else:
            raise ValueError(f"Unsupported database engine: {engine}")

        register_database(self.name, config, async_pool=False)

    def get_engine(self) -> str:
        """Get database engine name."""
        return self._sync_adapter.engine

    def execute(self, query: str, params: Optional[Union[tuple, list]] = None) -> Any:
        """
        Execute a raw SQL query synchronously.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Cursor object
        """
        return self._sync_adapter.execute(query, params)

    def execute_commit(self, query: str, params: Optional[Union[tuple, list]] = None) -> int:
        """
        Execute a query and commit.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows
        """
        return self._sync_adapter.execute_commit(query, params)

    def fetch_one(self, query: str, params: Optional[Union[tuple, list]] = None) -> Optional[Dict[str, Any]]:
        """Fetch one row."""
        return self._sync_adapter.fetch_one(query, params)

    def fetch_all(self, query: str, params: Optional[Union[tuple, list]] = None) -> List[Dict[str, Any]]:
        """Fetch all rows."""
        return self._sync_adapter.fetch_all(query, params)

    @contextmanager
    def transaction(self):
        """Transaction context manager."""
        with self._sync_adapter.transaction() as conn:
            yield conn

    def create_tables(self, models: List[Type['Model']]):
        """
        Create database tables for the given models.

        Args:
            models: List of Model classes to create tables for
        """
        for model in models:
            self._create_table_for_model(model)

    def _create_table_for_model(self, model: Type['Model']):
        """Create a single table for a model."""
        table_name = model._meta.get_table_name()
        engine = self.get_engine()

        # Build CREATE TABLE statement
        columns = []

        for field_name, field in model._meta.fields.items():
            column_def = self._get_column_definition(field, engine)
            columns.append(column_def)

        # Add unique constraints
        if model._meta.unique_together:
            for unique_fields in model._meta.unique_together:
                constraint = f"UNIQUE ({', '.join(unique_fields)})"
                columns.append(constraint)

        columns_sql = ',\n  '.join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  {columns_sql}\n)"

        logger.info(f"Creating table: {table_name}")
        self.execute_commit(sql)

    def _get_column_definition(self, field, engine: str) -> str:
        """Get SQL column definition for a field."""
        from .fields import AutoField, ForeignKey

        col_name = field.get_db_column()
        col_type = field.get_sql_type(engine)

        parts = [col_name, col_type]

        # Handle AutoField specially
        if isinstance(field, AutoField):
            # SQL type already includes PRIMARY KEY for AutoField
            return f"{col_name} {col_type}"

        # Add constraints
        if field.primary_key:
            parts.append('PRIMARY KEY')

        if not field.null:
            parts.append('NOT NULL')

        if field.unique and not field.primary_key:
            parts.append('UNIQUE')

        if field.default is not None and not callable(field.default):
            if isinstance(field.default, str):
                parts.append(f"DEFAULT '{field.default}'")
            else:
                parts.append(f"DEFAULT {field.default}")

        # Handle foreign keys
        if isinstance(field, ForeignKey):
            related_model = field.get_related_model()
            if related_model:
                related_table = related_model._meta.get_table_name()
                pk_field = related_model._meta.pk_field
                if pk_field:
                    pk_col = pk_field.get_db_column()
                    parts.append(f"REFERENCES {related_table}({pk_col})")
                    if field.on_delete:
                        parts.append(f"ON DELETE {field.on_delete}")

        return ' '.join(parts)

    def drop_tables(self, models: List[Type['Model']]):
        """
        Drop database tables for the given models.

        Args:
            models: List of Model classes to drop tables for
        """
        for model in models:
            table_name = model._meta.get_table_name()
            sql = f"DROP TABLE IF EXISTS {table_name}"
            logger.info(f"Dropping table: {table_name}")
            self.execute_commit(sql)

    def close(self):
        """Close database connections."""
        self._sync_adapter.close()
        logger.info(f"Database closed: {self.connection_url}")

    def __repr__(self):
        return f"Database('{self.connection_url}')"


# Convenience function for quick setup
def create_database(url: str, name: str = 'default', **kwargs) -> Database:
    """
    Create and return a Database instance.

    Args:
        url: Database URL
        name: Database name
        **kwargs: Additional connection parameters

    Returns:
        Database instance
    """
    return Database(url, name=name, **kwargs)
