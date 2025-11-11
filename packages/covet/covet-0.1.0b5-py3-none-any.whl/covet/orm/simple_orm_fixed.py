"""
Simple ORM for CovetPy Framework - Fixed Version
================================================
A working ORM with relationships support and proper connection management.
"""

import sqlite3
from typing import Any, Dict, List, Optional, Type, Union
from datetime import datetime
import json


class Field:
    """Base field class"""
    def __init__(self, primary_key=False, null=True, default=None, unique=False):
        self.primary_key = primary_key
        self.null = null
        self.default = default
        self.unique = unique
        self.name = None  # Set by Model metaclass

    def get_sql_type(self):
        """Return SQL type for this field"""
        return "TEXT"

    def to_db_value(self, value):
        """Convert Python value to database value"""
        if value is None:
            return None
        return str(value)

    def from_db_value(self, value):
        """Convert database value to Python value"""
        return value


class IntegerField(Field):
    """Integer field"""
    def get_sql_type(self):
        return "INTEGER"

    def to_db_value(self, value):
        if value is None:
            return None
        return int(value)

    def from_db_value(self, value):
        if value is None:
            return None
        return int(value)


class CharField(Field):
    """String field with max length"""
    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    def get_sql_type(self):
        return f"VARCHAR({self.max_length})"


class TextField(Field):
    """Text field for large strings"""
    def get_sql_type(self):
        return "TEXT"


class BooleanField(Field):
    """Boolean field"""
    def get_sql_type(self):
        return "BOOLEAN"

    def to_db_value(self, value):
        if value is None:
            return None
        return 1 if value else 0

    def from_db_value(self, value):
        if value is None:
            return None
        return bool(value)


class DateTimeField(Field):
    """DateTime field"""
    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

    def get_sql_type(self):
        return "DATETIME"

    def to_db_value(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    def from_db_value(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except:
                return value
        return value


class ForeignKey(Field):
    """Foreign key relationship"""
    def __init__(self, to_model, on_delete='CASCADE', related_name=None, **kwargs):
        super().__init__(**kwargs)
        self.to_model = to_model
        self.on_delete = on_delete
        self.related_name = related_name
        self._related_cache = None

    def get_sql_type(self):
        return "INTEGER"

    def to_db_value(self, value):
        if value is None:
            return None
        if isinstance(value, Model):
            return value.id
        return int(value)

    def from_db_value(self, value):
        if value is None:
            return None
        return int(value)


class ManyToManyField(Field):
    """Many-to-many relationship"""
    def __init__(self, to_model, through=None, related_name=None):
        super().__init__(null=True)
        self.to_model = to_model
        self.through = through
        self.related_name = related_name

    def get_sql_type(self):
        # M2M fields don't create columns in the main table
        return None


class ModelMeta(type):
    """Metaclass for Model"""
    def __new__(cls, name, bases, attrs):
        # Don't process Model base class itself
        if name == 'Model':
            return super().__new__(cls, name, bases, attrs)

        # Extract fields
        fields = {}
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Field):
                attr_value.name = attr_name
                fields[attr_name] = attr_value

        # Store fields in _fields
        attrs['_fields'] = fields

        # Add id field if not present
        if 'id' not in fields:
            id_field = IntegerField(primary_key=True)
            id_field.name = 'id'
            fields['id'] = id_field
            attrs['id'] = id_field

        # Create the class
        model_class = super().__new__(cls, name, bases, attrs)

        # Add manager
        model_class.objects = Manager(model_class)

        return model_class


class Manager:
    """Model manager for queries"""
    def __init__(self, model_class):
        self.model_class = model_class

    def all(self):
        """Get all records"""
        return QuerySet(self.model_class).all()

    def filter(self, **kwargs):
        """Filter records"""
        return QuerySet(self.model_class).filter(**kwargs)

    def get(self, **kwargs):
        """Get single record"""
        return QuerySet(self.model_class).get(**kwargs)

    def create(self, **kwargs):
        """Create and save a new record"""
        instance = self.model_class(**kwargs)
        instance.save()
        return instance

    def count(self):
        """Count all records"""
        return QuerySet(self.model_class).count()

    def select_related(self, *fields):
        """Eager load foreign key relationships"""
        return QuerySet(self.model_class).select_related(*fields)


class QuerySet:
    """Query builder and executor"""
    def __init__(self, model_class):
        self.model_class = model_class
        self.filters = []
        self._prefetch_related = []
        self._select_related = []

    def filter(self, **kwargs):
        """Add filters"""
        for key, value in kwargs.items():
            self.filters.append((key, '=', value))
        return self

    def select_related(self, *fields):
        """Eager load foreign key relationships"""
        self._select_related.extend(fields)
        return self

    def prefetch_related(self, *fields):
        """Prefetch many-to-many or reverse foreign key relationships"""
        self._prefetch_related.extend(fields)
        return self

    def all(self):
        """Execute query and return all results"""
        db = getattr(self.model_class, '_db', None)
        if not db:
            raise ValueError(f"No database configured for {self.model_class.__name__}")

        conn = db.get_connection()
        cursor = conn.cursor()

        # Build query
        table_name = self.model_class.get_table_name()
        query = f"SELECT * FROM {table_name}"
        params = []

        if self.filters:
            conditions = []
            for field, op, value in self.filters:
                conditions.append(f"{field} {op} ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert to model instances
        instances = []
        for row in rows:
            instance = self.model_class()
            for i, col in enumerate(cursor.description):
                field_name = col[0]
                if field_name in self.model_class._fields:
                    field = self.model_class._fields[field_name]
                    setattr(instance, field_name, field.from_db_value(row[i]))
                else:
                    setattr(instance, field_name, row[i])
            instance._is_new = False
            instances.append(instance)

        # Handle select_related (eager loading)
        for field_name in self._select_related:
            if field_name in self.model_class._fields:
                field = self.model_class._fields[field_name]
                if isinstance(field, ForeignKey):
                    self._load_foreign_keys(instances, field_name, field)

        # Keep connection open if it's in-memory
        if db.db_path != ':memory:':
            conn.close()

        return instances

    def _load_foreign_keys(self, instances, field_name, field):
        """Load foreign key relationships"""
        # Collect all foreign key IDs
        fk_ids = set()
        for instance in instances:
            fk_id = getattr(instance, field_name)
            if fk_id:
                fk_ids.add(fk_id)

        if not fk_ids:
            return

        # Load related objects
        related_model = field.to_model
        if isinstance(related_model, str):
            # Resolve string reference
            related_model = globals().get(related_model)

        if related_model:
            related_objects = related_model.objects.filter(id__in=list(fk_ids))
            related_dict = {obj.id: obj for obj in related_objects}

            # Attach to instances
            for instance in instances:
                fk_id = getattr(instance, field_name)
                if fk_id and fk_id in related_dict:
                    setattr(instance, f"{field_name}_obj", related_dict[fk_id])

    def get(self, **kwargs):
        """Get single record"""
        self.filter(**kwargs)
        results = self.all()
        if not results:
            raise ValueError(f"No {self.model_class.__name__} found matching query")
        if len(results) > 1:
            raise ValueError(f"Multiple {self.model_class.__name__} found matching query")
        return results[0]

    def first(self):
        """Get first record"""
        results = self.all()
        return results[0] if results else None

    def count(self):
        """Count records"""
        db = getattr(self.model_class, '_db', None)
        if not db:
            raise ValueError(f"No database configured for {self.model_class.__name__}")

        conn = db.get_connection()
        cursor = conn.cursor()

        table_name = self.model_class.get_table_name()
        query = f"SELECT COUNT(*) FROM {table_name}"
        params = []

        if self.filters:
            conditions = []
            for field, op, value in self.filters:
                conditions.append(f"{field} {op} ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        result = cursor.fetchone()[0]

        # Keep connection open if it's in-memory
        if db.db_path != ':memory:':
            conn.close()

        return result


class Model(metaclass=ModelMeta):
    """Base model class"""
    _db = None
    _table_name = None

    def __init__(self, **kwargs):
        self._is_new = True

        # Set field values
        for field_name, field in self._fields.items():
            if field_name in kwargs:
                value = kwargs[field_name]
                setattr(self, field_name, value)
            elif field.default is not None:
                if callable(field.default):
                    setattr(self, field_name, field.default())
                else:
                    setattr(self, field_name, field.default)
            else:
                setattr(self, field_name, None)

    @classmethod
    def get_table_name(cls):
        """Get table name for this model"""
        if cls._table_name:
            return cls._table_name
        return cls.__name__.lower() + 's'

    @classmethod
    def set_db(cls, db):
        """Set database for this model"""
        cls._db = db

    def save(self):
        """Save the model to database"""
        if not self._db:
            raise ValueError(f"No database configured for {self.__class__.__name__}")

        conn = self._db.get_connection()
        cursor = conn.cursor()

        table_name = self.get_table_name()

        # Handle auto_now fields
        for field_name, field in self._fields.items():
            if isinstance(field, DateTimeField):
                if field.auto_now or (field.auto_now_add and self._is_new):
                    setattr(self, field_name, datetime.now().isoformat())

        # Prepare field values
        fields = []
        values = []
        for field_name, field in self._fields.items():
            if field_name == 'id' and self._is_new:
                continue  # Skip auto-increment id on insert
            if hasattr(self, field_name):
                fields.append(field_name)
                value = getattr(self, field_name)
                values.append(field.to_db_value(value))

        if self._is_new:
            # INSERT
            placeholders = ', '.join(['?' for _ in values])
            field_names = ', '.join(fields)
            query = f"INSERT INTO {table_name} ({field_names}) VALUES ({placeholders})"
            cursor.execute(query, values)
            self.id = cursor.lastrowid
            self._is_new = False
        else:
            # UPDATE
            set_clause = ', '.join([f"{f} = ?" for f in fields])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
            values.append(self.id)
            cursor.execute(query, values)

        conn.commit()

        # Keep connection open if it's in-memory
        if self._db.db_path != ':memory:':
            conn.close()

    def delete(self):
        """Delete the model from database"""
        if self._is_new:
            return  # Not in database

        if not self._db:
            raise ValueError(f"No database configured for {self.__class__.__name__}")

        conn = self._db.get_connection()
        cursor = conn.cursor()

        table_name = self.get_table_name()
        query = f"DELETE FROM {table_name} WHERE id = ?"
        cursor.execute(query, [self.id])

        conn.commit()

        # Keep connection open if it's in-memory
        if self._db.db_path != ':memory:':
            conn.close()

        self._is_new = True

    def refresh(self):
        """Reload from database"""
        if self._is_new or not self.id:
            raise ValueError("Cannot refresh unsaved model")

        refreshed = self.__class__.objects.get(id=self.id)
        for field_name in self._fields:
            setattr(self, field_name, getattr(refreshed, field_name))


class Database:
    """Database connection manager"""
    def __init__(self, db_path):
        self.db_path = db_path
        self._connection = None

    def get_connection(self):
        """Get database connection - keep in-memory connections open"""
        if self.db_path == ':memory:':
            if not self._connection:
                self._connection = sqlite3.connect(':memory:')
                self._connection.row_factory = sqlite3.Row
            return self._connection
        else:
            return sqlite3.connect(self.db_path)

    def create_tables(self, models):
        """Create tables for models"""
        conn = self.get_connection()
        cursor = conn.cursor()

        for model in models:
            # Set database on model
            model.set_db(self)

            # Build CREATE TABLE statement
            table_name = model.get_table_name()
            columns = []

            for field_name, field in model._fields.items():
                sql_type = field.get_sql_type()
                if sql_type is None:
                    continue  # Skip M2M fields

                column_def = f"{field_name} {sql_type}"

                if field.primary_key:
                    column_def += " PRIMARY KEY"
                    if field_name == 'id':
                        column_def += " AUTOINCREMENT"

                if field.unique:
                    column_def += " UNIQUE"

                if not field.null:
                    column_def += " NOT NULL"

                columns.append(column_def)

            # Add foreign key constraints
            for field_name, field in model._fields.items():
                if isinstance(field, ForeignKey):
                    related_table = field.to_model.get_table_name() if hasattr(field.to_model, 'get_table_name') else field.to_model.lower() + 's'
                    constraint = f"FOREIGN KEY ({field_name}) REFERENCES {related_table}(id)"
                    if field.on_delete:
                        constraint += f" ON DELETE {field.on_delete}"
                    columns.append(constraint)

            # Create table
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            cursor.execute(create_sql)

            # Create M2M junction tables
            for field_name, field in model._fields.items():
                if isinstance(field, ManyToManyField):
                    self._create_m2m_table(cursor, model, field_name, field)

        conn.commit()

        # Keep connection open if it's in-memory
        if self.db_path != ':memory:':
            conn.close()

    def _create_m2m_table(self, cursor, model, field_name, field):
        """Create many-to-many junction table"""
        model_table = model.get_table_name()
        related_table = field.to_model.get_table_name() if hasattr(field.to_model, 'get_table_name') else field.to_model.lower() + 's'

        # Junction table name
        junction_table = f"{model_table}_{field_name}"

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {junction_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {model_table[:-1]}_id INTEGER NOT NULL,
            {related_table[:-1]}_id INTEGER NOT NULL,
            FOREIGN KEY ({model_table[:-1]}_id) REFERENCES {model_table}(id),
            FOREIGN KEY ({related_table[:-1]}_id) REFERENCES {related_table}(id),
            UNIQUE ({model_table[:-1]}_id, {related_table[:-1]}_id)
        )
        """
        cursor.execute(create_sql)

    def close(self):
        """Close the database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None


# Export main classes
__all__ = [
    'Database',
    'Model',
    'Field',
    'IntegerField',
    'CharField',
    'TextField',
    'BooleanField',
    'DateTimeField',
    'ForeignKey',
    'ManyToManyField',
    'QuerySet',
    'Manager'
]