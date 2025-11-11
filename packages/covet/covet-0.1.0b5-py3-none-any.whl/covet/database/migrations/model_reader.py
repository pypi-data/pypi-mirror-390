"""
Model to Schema Converter

Extracts database schema information from ORM Model classes.
Converts Python field types to SQL types across PostgreSQL, MySQL, and SQLite.
Handles indexes, constraints, and relationships for migration generation.

This is the foundation of the migration system - it reads your ORM models
and generates a complete schema representation that can be compared with
the actual database state.

Example:
    from covet.database.orm import Model
    from covet.database.orm.fields import CharField, IntegerField
    from covet.database.migrations.model_reader import ModelReader

    class User(Model):
        username = CharField(max_length=100, unique=True)
        age = IntegerField(nullable=True)

        class Meta:
            db_table = 'users'
            indexes = [Index(fields=['username'])]

    reader = ModelReader()
    schema = reader.read_model(User, dialect='postgresql')
    # Returns complete schema with columns, indexes, constraints
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Type

logger = logging.getLogger(__name__)


class TableSchema:
    """
    Represents the complete schema of a database table.

    This is an intermediate representation that's database-agnostic
    and can be used to generate SQL for any supported database.

    Attributes:
        name: Table name
        columns: List of column definitions
        primary_key: Primary key column(s)
        indexes: List of index definitions
        constraints: List of constraint definitions
        relationships: List of foreign key relationships
    """

    def __init__(self, name: str):
        self.name = name
        self.columns: List[ColumnSchema] = []
        self.primary_key: List[str] = []
        self.indexes: List[IndexSchema] = []
        self.constraints: List[ConstraintSchema] = []
        self.relationships: List[RelationshipSchema] = []

    def add_column(self, column: "ColumnSchema"):
        """Add a column to the table schema."""
        self.columns.append(column)
        if column.primary_key:
            self.primary_key.append(column.name)

    def add_index(self, index: "IndexSchema"):
        """Add an index to the table schema."""
        self.indexes.append(index)

    def add_constraint(self, constraint: "ConstraintSchema"):
        """Add a constraint to the table schema."""
        self.constraints.append(constraint)

    def add_relationship(self, relationship: "RelationshipSchema"):
        """Add a foreign key relationship."""
        self.relationships.append(relationship)

    def get_column(self, name: str) -> Optional["ColumnSchema"]:
        """Get column by name."""
        for col in self.columns:
            if col.name == name:
                return col
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "columns": [col.to_dict() for col in self.columns],
            "primary_key": self.primary_key,
            "indexes": [idx.to_dict() for idx in self.indexes],
            "constraints": [c.to_dict() for c in self.constraints],
            "relationships": [r.to_dict() for r in self.relationships],
        }

    def __repr__(self) -> str:
        return f"<TableSchema: {self.name} ({len(self.columns)} columns)>"


class ColumnSchema:
    """
    Represents a database column definition.

    Attributes:
        name: Column name
        db_type: SQL type (VARCHAR, INTEGER, etc.)
        nullable: Whether NULL values are allowed
        default: Default value
        unique: Whether values must be unique
        primary_key: Whether this is a primary key
        auto_increment: Whether this is auto-incrementing
        max_length: Maximum length for string types
        precision: Precision for decimal types
        scale: Scale for decimal types
    """

    def __init__(
        self,
        name: str,
        db_type: str,
        nullable: bool = True,
        default: Any = None,
        unique: bool = False,
        primary_key: bool = False,
        auto_increment: bool = False,
        max_length: Optional[int] = None,
        precision: Optional[int] = None,
        scale: Optional[int] = None,
    ):
        self.name = name
        self.db_type = db_type
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.max_length = max_length
        self.precision = precision
        self.scale = scale

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "db_type": self.db_type,
            "nullable": self.nullable,
            "default": self.default,
            "unique": self.unique,
            "primary_key": self.primary_key,
            "auto_increment": self.auto_increment,
            "max_length": self.max_length,
            "precision": self.precision,
            "scale": self.scale,
        }

    def __repr__(self) -> str:
        attrs = [self.db_type]
        if self.primary_key:
            attrs.append("PK")
        if self.unique:
            attrs.append("UNIQUE")
        if not self.nullable:
            attrs.append("NOT NULL")
        return f"<Column: {self.name} {' '.join(attrs)}>"


class IndexSchema:
    """
    Represents a database index definition.

    Attributes:
        name: Index name
        columns: Column names in the index
        unique: Whether this is a unique index
        method: Index method (btree, hash, gin, gist for PostgreSQL)
    """

    def __init__(
        self,
        name: str,
        columns: List[str],
        unique: bool = False,
        method: Optional[str] = None,
    ):
        self.name = name
        self.columns = columns
        self.unique = unique
        self.method = method

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "columns": self.columns,
            "unique": self.unique,
            "method": self.method,
        }

    def __repr__(self) -> str:
        return f"<Index: {self.name} on {', '.join(self.columns)}>"


class ConstraintSchema:
    """
    Represents a database constraint definition.

    Attributes:
        name: Constraint name
        type: Constraint type (CHECK, UNIQUE, etc.)
        columns: Columns involved in constraint
        definition: SQL constraint definition
    """

    def __init__(
        self,
        name: str,
        type: str,
        columns: List[str],
        definition: str,
    ):
        self.name = name
        self.type = type
        self.columns = columns
        self.definition = definition

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "columns": self.columns,
            "definition": self.definition,
        }

    def __repr__(self) -> str:
        return f"<Constraint: {self.name} ({self.type})>"


class RelationshipSchema:
    """
    Represents a foreign key relationship.

    Attributes:
        name: Constraint name
        column: Foreign key column
        referenced_table: Target table
        referenced_column: Target column
        on_delete: ON DELETE action
        on_update: ON UPDATE action
    """

    def __init__(
        self,
        name: str,
        column: str,
        referenced_table: str,
        referenced_column: str,
        on_delete: str = "CASCADE",
        on_update: str = "CASCADE",
    ):
        self.name = name
        self.column = column
        self.referenced_table = referenced_table
        self.referenced_column = referenced_column
        self.on_delete = on_delete
        self.on_update = on_update

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "column": self.column,
            "referenced_table": self.referenced_table,
            "referenced_column": self.referenced_column,
            "on_delete": self.on_delete,
            "on_update": self.on_update,
        }

    def __repr__(self) -> str:
        return f"<FK: {self.column} -> {self.referenced_table}.{self.referenced_column}>"


class ModelReader:
    """
    Reads ORM Model classes and extracts database schema information.

    This is the core component that bridges the gap between your Python
    ORM models and the actual SQL database schema. It understands all
    CovetPy field types and can generate appropriate SQL for any supported
    database dialect.

    Features:
    - Extracts all column definitions with types
    - Maps Python fields to SQL types per database dialect
    - Handles indexes (single-column and composite)
    - Processes constraints (UNIQUE, CHECK, etc.)
    - Extracts foreign key relationships
    - Supports all 3 database backends (PostgreSQL, MySQL, SQLite)

    Example:
        reader = ModelReader()

        # Read single model
        schema = reader.read_model(User, dialect='postgresql')

        # Read all models in a module
        schemas = reader.read_models([User, Post, Comment], dialect='mysql')
    """

    def __init__(self):
        """Initialize model reader."""
        pass

    def read_model(self, model_class: Type, dialect: str = "postgresql") -> TableSchema:
        """
        Extract schema from a Model class.

        Args:
            model_class: ORM Model class to read
            dialect: Database dialect ('postgresql', 'mysql', 'sqlite')

        Returns:
            TableSchema with complete table definition

        Example:
            schema = reader.read_model(User, dialect='postgresql')
            print(schema.to_dict())
        """
        # Validate model class
        if not hasattr(model_class, "_meta"):
            raise ValueError(f"{model_class.__name__} is not a valid Model class")

        meta = model_class._meta
        table_name = meta.db_table or model_class.__tablename__

        logger.info(f"Reading model: {model_class.__name__} -> {table_name}")

        # Create table schema
        schema = TableSchema(table_name)

        # Extract columns from fields
        for field_name, field in model_class._fields.items():
            # Skip relationship fields that don't create columns
            if hasattr(field, "to") and field.db_column is None:
                # This is a ManyToManyField - handle separately
                continue

            column = self._field_to_column(field, field_name, dialect)
            schema.add_column(column)

        # Extract indexes from Meta
        if hasattr(meta, "indexes") and meta.indexes:
            for idx in meta.indexes:
                index = self._extract_index(idx, table_name)
                schema.add_index(index)

        # Extract unique_together constraints
        if hasattr(meta, "unique_together") and meta.unique_together:
            for i, fields in enumerate(meta.unique_together):
                constraint = self._create_unique_constraint(table_name, fields, i)
                schema.add_constraint(constraint)

        # Extract foreign key relationships
        for field_name, field in model_class._fields.items():
            # Check for ForeignKey fields
            if hasattr(field, "to") and hasattr(field, "get_related_model"):
                if field.db_column and field.name != field.db_column:
                    # This is a ForeignKey - extract relationship
                    relationship = self._extract_relationship(field, field_name, table_name)
                    if relationship:
                        schema.add_relationship(relationship)

        # Add implicit indexes for foreign keys and unique fields
        for column in schema.columns:
            if column.unique and not column.primary_key:
                # Add unique index
                idx_name = f"{table_name}_{column.name}_key"
                index = IndexSchema(name=idx_name, columns=[column.name], unique=True)
                schema.add_index(index)

        logger.info(
            f"Read model {model_class.__name__}: "
            f"{len(schema.columns)} columns, "
            f"{len(schema.indexes)} indexes, "
            f"{len(schema.relationships)} relationships"
        )

        return schema

    def read_models(
        self, model_classes: List[Type], dialect: str = "postgresql"
    ) -> List[TableSchema]:
        """
        Extract schemas from multiple Model classes.

        Args:
            model_classes: List of ORM Model classes
            dialect: Database dialect

        Returns:
            List of TableSchema objects
        """
        schemas = []
        for model_class in model_classes:
            try:
                schema = self.read_model(model_class, dialect)
                schemas.append(schema)
            except Exception as e:
                logger.error(f"Failed to read model {model_class.__name__}: {e}")
                raise

        return schemas

    def _field_to_column(self, field, field_name: str, dialect: str) -> ColumnSchema:
        """
        Convert ORM Field to ColumnSchema.

        Args:
            field: ORM Field instance
            field_name: Field name
            dialect: Database dialect

        Returns:
            ColumnSchema definition
        """
        # Get database type
        db_type = field.get_db_type(dialect)

        # Extract field properties
        column = ColumnSchema(
            name=field.db_column or field_name,
            db_type=db_type,
            nullable=field.nullable,
            default=field.default,
            unique=field.unique,
            primary_key=field.primary_key,
            auto_increment=getattr(field, "auto_increment", False),
        )

        # Add type-specific properties
        if hasattr(field, "max_length"):
            column.max_length = field.max_length

        if hasattr(field, "max_digits") and hasattr(field, "decimal_places"):
            column.precision = field.max_digits
            column.scale = field.decimal_places

        return column

    def _extract_index(self, index_def, table_name: str) -> IndexSchema:
        """
        Extract index definition from Model.Meta.indexes.

        Args:
            index_def: Index definition from Model.Meta
            table_name: Table name

        Returns:
            IndexSchema
        """
        # Handle Index objects from models.py
        if hasattr(index_def, "fields"):
            fields = index_def.fields
            name = index_def.name if hasattr(index_def, "name") and index_def.name else None
            unique = index_def.unique if hasattr(index_def, "unique") else False
        else:
            # Handle tuple format
            fields = index_def if isinstance(index_def, (list, tuple)) else [index_def]
            name = None
            unique = False

        # Generate index name if not provided
        if not name:
            fields_str = "_".join(str(f) for f in fields)
            name = f"{table_name}_{fields_str}_idx"

        return IndexSchema(name=name, columns=list(fields), unique=unique)

    def _create_unique_constraint(
        self, table_name: str, fields: List[str], index: int
    ) -> ConstraintSchema:
        """
        Create UNIQUE constraint from unique_together.

        Args:
            table_name: Table name
            fields: Field names
            index: Constraint index

        Returns:
            ConstraintSchema
        """
        name = f"{table_name}_{'_'.join(fields)}_key"
        columns_str = ", ".join(fields)
        definition = f"UNIQUE ({columns_str})"

        return ConstraintSchema(
            name=name, type="UNIQUE", columns=list(fields), definition=definition
        )

    def _extract_relationship(
        self, field, field_name: str, table_name: str
    ) -> Optional[RelationshipSchema]:
        """
        Extract foreign key relationship from ForeignKey field.

        Args:
            field: ForeignKey field
            field_name: Field name
            table_name: Source table name

        Returns:
            RelationshipSchema or None
        """
        try:
            # Get related model
            related_model = field.get_related_model()
            if not related_model:
                logger.warning(f"Cannot resolve related model for {field_name}")
                return None

            # Get related table and column
            related_table = related_model.__tablename__
            related_pk = related_model._meta.pk_field
            related_column = related_pk.db_column

            # Create constraint name
            constraint_name = f"fk_{table_name}_{field_name}"

            # Get foreign key column name
            fk_column = field.db_column

            # Get cascade behavior
            on_delete = field.on_delete if hasattr(field, "on_delete") else "CASCADE"

            return RelationshipSchema(
                name=constraint_name,
                column=fk_column,
                referenced_table=related_table,
                referenced_column=related_column,
                on_delete=on_delete,
                on_update="CASCADE",
            )

        except Exception as e:
            logger.error(f"Failed to extract relationship for {field_name}: {e}")
            return None


__all__ = [
    "ModelReader",
    "TableSchema",
    "ColumnSchema",
    "IndexSchema",
    "ConstraintSchema",
    "RelationshipSchema",
]
