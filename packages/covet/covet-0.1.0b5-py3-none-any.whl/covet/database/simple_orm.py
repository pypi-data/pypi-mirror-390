"""
CovetPy Simple ORM
A lightweight ORM for Sprint 2 database functionality
"""

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

from .security.sql_validator import (
    DatabaseDialect,
    InvalidIdentifierError,
    validate_column_name,
    validate_table_name,
)


@dataclass
class Field:
    """Database field definition."""

    name: str
    type: str = "TEXT"
    primary_key: bool = False
    nullable: bool = True
    default: Any = None
    unique: bool = False


@dataclass
class ModelMeta:
    """Model metadata."""

    table_name: str
    fields: Dict[str, Field] = field(default_factory=dict)
    primary_key: Optional[str] = None


class DatabaseConnection:
    """Simple database connection manager."""

    _connections = threading.local()

    def __init__(self, database_url: str = "covet.db"):
        self.database_url = database_url

    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._connections, "conn"):
            self._connections.conn = sqlite3.connect(self.database_url)
            self._connections.conn.row_factory = sqlite3.Row
        return self._connections.conn

    def close(self):
        """Close the connection."""
        if hasattr(self._connections, "conn"):
            self._connections.conn.close()
            delattr(self._connections, "conn")


class ModelBase:
    """Base model class for ORM functionality."""

    _meta: Optional[ModelMeta] = None
    _db: Optional[DatabaseConnection] = None

    def __init__(self, **kwargs):
        for field_name, field_def in self._meta.fields.items():
            value = kwargs.get(field_name, field_def.default)
            setattr(self, field_name, value)

    @classmethod
    def set_database(cls, db: DatabaseConnection):
        """Set the database connection."""
        cls._db = db

    @classmethod
    def create_table(cls):
        """Create the table for this model."""
        if not cls._meta or not cls._db:
            raise RuntimeError("Model not properly configured")

        conn = cls._db.get_connection()

        # SECURITY FIX: Validate table name to prevent SQL injection
        validated_table_name = validate_table_name(cls._meta.table_name, DatabaseDialect.SQLITE)

        # Build CREATE TABLE statement
        fields_sql = []
        for field_name, field_def in cls._meta.fields.items():
            # SECURITY FIX: Validate each field name
            validated_field_name = validate_column_name(field_name, DatabaseDialect.SQLITE)
            field_sql = f"{validated_field_name} {field_def.type}"

            if field_def.primary_key:
                field_sql += " PRIMARY KEY"
            if not field_def.nullable:
                field_sql += " NOT NULL"
            if field_def.unique:
                field_sql += " UNIQUE"

            fields_sql.append(field_sql)

        sql = f"CREATE TABLE IF NOT EXISTS {validated_table_name} ({', '.join(fields_sql)})"
        conn.execute(sql)
        conn.commit()

    def save(self) -> "ModelBase":
        """Save the model instance."""
        if not self._meta or not self._db:
            raise RuntimeError("Model not properly configured")

        conn = self._db.get_connection()

        # Check if this is an update or insert
        pk_field = self._meta.primary_key
        pk_value = getattr(self, pk_field) if pk_field else None

        if pk_value and self._exists(pk_value):
            # Update existing record
            self._update(conn)
        else:
            # Insert new record
            self._insert(conn)

        conn.commit()
        return self

    def _exists(self, pk_value: Any) -> bool:
        """Check if record exists."""
        conn = self._db.get_connection()
        # SECURITY FIX: Validate identifiers to prevent SQL injection
        validated_table = validate_table_name(self._meta.table_name, DatabaseDialect.SQLITE)
        validated_pk = validate_column_name(self._meta.primary_key, DatabaseDialect.SQLITE)

        cursor = conn.execute(
            f"SELECT 1 FROM {validated_table} WHERE {validated_pk} = ?",
            (pk_value,),  # nosec B608 - identifiers validated
        )
        return cursor.fetchone() is not None

    def _insert(self, conn: sqlite3.Connection):
        """Insert new record."""
        fields = list(self._meta.fields.keys())
        values = [getattr(self, field) for field in fields]

        # SECURITY FIX: Validate all identifiers
        validated_table = validate_table_name(self._meta.table_name, DatabaseDialect.SQLITE)
        validated_fields = [validate_column_name(f, DatabaseDialect.SQLITE) for f in fields]

        placeholders = ", ".join(["?" for _ in fields])
        fields_str = ", ".join(validated_fields)

        sql = f"INSERT INTO {validated_table} ({fields_str}) VALUES ({placeholders})"  # nosec B608 - identifiers validated
        cursor = conn.execute(sql, values)

        # Set primary key if auto-generated
        if self._meta.primary_key and cursor.lastrowid:
            setattr(self, self._meta.primary_key, cursor.lastrowid)

    def _update(self, conn: sqlite3.Connection):
        """Update existing record."""
        fields = [f for f in self._meta.fields.keys() if f != self._meta.primary_key]
        values = [getattr(self, field) for field in fields]
        pk_value = getattr(self, self._meta.primary_key)

        # SECURITY FIX: Validate all identifiers
        validated_table = validate_table_name(self._meta.table_name, DatabaseDialect.SQLITE)
        validated_pk = validate_column_name(self._meta.primary_key, DatabaseDialect.SQLITE)
        validated_fields = [validate_column_name(f, DatabaseDialect.SQLITE) for f in fields]

        set_clause = ", ".join([f"{field} = ?" for field in validated_fields])
        sql = f"UPDATE {validated_table} SET {set_clause} WHERE {validated_pk} = ?"  # nosec B608 - identifiers validated

        conn.execute(sql, values + [pk_value])

    def delete(self):
        """Delete the record."""
        if not self._meta or not self._db:
            raise RuntimeError("Model not properly configured")

        pk_value = getattr(self, self._meta.primary_key)
        if not pk_value:
            raise ValueError("Cannot delete record without primary key")

        # SECURITY FIX: Validate identifiers
        validated_table = validate_table_name(self._meta.table_name, DatabaseDialect.SQLITE)
        validated_pk = validate_column_name(self._meta.primary_key, DatabaseDialect.SQLITE)

        conn = self._db.get_connection()
        conn.execute(
            f"DELETE FROM {validated_table} WHERE {validated_pk} = ?",
            (pk_value,),  # nosec B608 - identifiers validated
        )
        conn.commit()

    @classmethod
    def get(cls, pk: Any) -> Optional["ModelBase"]:
        """Get record by primary key."""
        if not cls._meta or not cls._db:
            raise RuntimeError("Model not properly configured")

        # SECURITY FIX: Validate identifiers
        validated_table = validate_table_name(cls._meta.table_name, DatabaseDialect.SQLITE)
        validated_pk = validate_column_name(cls._meta.primary_key, DatabaseDialect.SQLITE)

        conn = cls._db.get_connection()
        cursor = conn.execute(
            f"SELECT * FROM {validated_table} WHERE {validated_pk} = ?",
            (pk,),  # nosec B608 - identifiers validated
        )

        row = cursor.fetchone()
        if row:
            return cls(**dict(row))
        return None

    @classmethod
    def all(cls) -> List["ModelBase"]:
        """Get all records."""
        if not cls._meta or not cls._db:
            raise RuntimeError("Model not properly configured")

        # SECURITY FIX: Validate table name
        validated_table = validate_table_name(cls._meta.table_name, DatabaseDialect.SQLITE)

        conn = cls._db.get_connection()
        cursor = conn.execute(
            f"SELECT * FROM {validated_table}"
        )  # nosec B608 - identifiers validated

        return [cls(**dict(row)) for row in cursor.fetchall()]

    @classmethod
    def filter(cls, **kwargs) -> List["ModelBase"]:
        """Filter records by field values."""
        if not cls._meta or not cls._db:
            raise RuntimeError("Model not properly configured")

        conn = cls._db.get_connection()

        # SECURITY FIX: Validate table name and all field names
        validated_table = validate_table_name(cls._meta.table_name, DatabaseDialect.SQLITE)

        where_clauses = []
        values = []
        for field, value in kwargs.items():
            # SECURITY FIX: Validate each field name
            validated_field = validate_column_name(field, DatabaseDialect.SQLITE)
            where_clauses.append(f"{validated_field} = ?")
            values.append(value)

        where_sql = " AND ".join(where_clauses)
        sql = f"SELECT * FROM {validated_table} WHERE {where_sql}"  # nosec B608 - identifiers validated

        cursor = conn.execute(sql, values)
        return [cls(**dict(row)) for row in cursor.fetchall()]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {field: getattr(self, field) for field in self._meta.fields.keys()}

    def __repr__(self) -> str:
        pk_value = getattr(self, self._meta.primary_key) if self._meta.primary_key else "new"
        return f"<{self.__class__.__name__}({self._meta.primary_key}={pk_value})>"


def create_model(
    table_name: str, fields: Dict[str, Field], db: DatabaseConnection
) -> Type[ModelBase]:
    """Create a model class dynamically."""

    # Find primary key
    primary_key = None
    for field_name, field_def in fields.items():
        if field_def.primary_key:
            primary_key = field_name
            break

    # Create metadata
    meta = ModelMeta(table_name=table_name, fields=fields, primary_key=primary_key)

    # Create model class
    class_name = "".join(word.capitalize() for word in table_name.split("_"))
    model_class = type(class_name, (ModelBase,), {"_meta": meta, "_db": db})

    return model_class


# Convenience functions for common field types
def primary_key() -> Field:
    """Create a primary key field."""
    return Field("id", "INTEGER", primary_key=True, nullable=False)


def text_field(nullable: bool = True, unique: bool = False) -> Field:
    """Create a text field."""
    return Field("", "TEXT", nullable=nullable, unique=unique)


def integer_field(nullable: bool = True, unique: bool = False) -> Field:
    """Create an integer field."""
    return Field("", "INTEGER", nullable=nullable, unique=unique)


def datetime_field(nullable: bool = True) -> Field:
    """Create a datetime field."""
    return Field("", "TEXT", nullable=nullable, default=datetime.now().isoformat())


def json_field(nullable: bool = True) -> Field:
    """Create a JSON field."""
    return Field("", "TEXT", nullable=nullable)
