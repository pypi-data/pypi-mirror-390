"""
ORM Relationship Fields

Django-style relationship fields for ForeignKey, OneToOne, and ManyToMany.
Supports eager loading, lazy loading, reverse relations, and cascade operations.

Example:
    class Author(Model):
        name = CharField(max_length=100)

    class Post(Model):
        title = CharField(max_length=200)
        author = ForeignKey(Author, on_delete=CASCADE, related_name='posts')
        tags = ManyToManyField('Tag', related_name='posts')

    class Profile(Model):
        user = OneToOneField('User', on_delete=CASCADE, related_name='profile')

    # Usage
    author = await Author.objects.get(id=1)
    posts = await author.posts.all()  # Reverse relation

    post = await Post.objects.select_related('author').get(id=1)
    print(post.author.name)  # No extra query
"""

import logging
import weakref
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

from .fields import Field, IntegerField

if TYPE_CHECKING:
    from .models import Model


logger = logging.getLogger(__name__)


# Global model registry for lazy resolution
_model_registry: Dict[str, Type["Model"]] = {}

# Global reverse relationship registry
# Maps model name to list of reverse relationships
# Format: {
#     'Author': [
#         {'related_model': Post, 'related_field': 'author', 'relation_type': 'foreignkey'},
#         {'related_model': Comment, 'related_field': 'author', 'relation_type': 'foreignkey'}
#     ]
# }
_reverse_relations_registry: Dict[str, List[Dict[str, Any]]] = {}


def register_model(model: Type["Model"]) -> None:
    """Register model for lazy relationship resolution."""
    _model_registry[model.__name__] = model
    # Also register with qualified name if in a module
    if hasattr(model, "__module__"):
        qualified_name = f"{model.__module__}.{model.__name__}"
        _model_registry[qualified_name] = model


def get_model(model_name: str) -> Optional[Type["Model"]]:
    """Get model by name from registry."""
    return _model_registry.get(model_name)


def register_reverse_relation(
    target_model: Type["Model"],
    related_model: Type["Model"],
    related_field: str,
    relation_type: str,
    related_name: Optional[str] = None,
) -> None:
    """
    Register a reverse relationship for prefetch_related() support.

    Args:
        target_model: Model being referenced (e.g., Author)
        related_model: Model with the FK/M2M field (e.g., Post)
        related_field: Field name on related_model (e.g., 'author')
        relation_type: 'foreignkey', 'onetoone', or 'manytomany'
        related_name: Name of reverse accessor (e.g., 'posts')
    """
    target_name = target_model.__name__

    if target_name not in _reverse_relations_registry:
        _reverse_relations_registry[target_name] = []

    relation_info = {
        "related_model": related_model,
        "related_field": related_field,
        "relation_type": relation_type,
        "related_name": related_name,
    }

    # Avoid duplicate registration
    existing = [
        r
        for r in _reverse_relations_registry[target_name]
        if r["related_model"] == related_model and r["related_field"] == related_field
    ]

    if not existing:
        _reverse_relations_registry[target_name].append(relation_info)
        logger.debug(
            f"Registered reverse {relation_type} from {related_model.__name__}.{related_field} "
            f"to {target_model.__name__}.{related_name or '(no name)'}"
        )


def get_reverse_relations(model: Type["Model"]) -> List[Dict[str, Any]]:
    """
    Get all reverse relationships for a model.

    Args:
        model: Model class to get reverse relations for

    Returns:
        List of reverse relationship metadata dictionaries
    """
    return _reverse_relations_registry.get(model.__name__, [])


class ForwardRelationDescriptor:
    """
    Descriptor for forward ForeignKey/OneToOne access with lazy loading.

    Enables: post.author (loads Author on first access)
    """

    def __init__(self, field: "ForeignKey"):
        """Initialize descriptor for a foreign key field."""
        self.field = field
        self.cache_name = f"_{field.name}_cache"

    def __get__(self, instance: Optional["Model"], owner: Type["Model"]) -> Any:
        """Get related instance (lazy load if needed)."""
        if instance is None:
            return self

        # Check cache
        if hasattr(instance, self.cache_name):
            return getattr(instance, self.cache_name)

        # Get foreign key value
        fk_field_name = f"{self.field.name}_id"
        fk_value = getattr(instance, fk_field_name, None)

        if fk_value is None:
            setattr(instance, self.cache_name, None)
            return None

        # Lazy load related instance
        # This returns a coroutine that needs to be awaited
        related_model = self.field.get_related_model()
        return _LazyRelatedInstance(instance, self.field, related_model, fk_value, self.cache_name)

    def __set__(self, instance: "Model", value: Optional["Model"]) -> None:
        """Set related instance."""
        # Update cache
        setattr(instance, self.cache_name, value)

        # Update foreign key field
        fk_field_name = f"{self.field.name}_id"
        if value is None:
            setattr(instance, fk_field_name, None)
        else:
            pk_field = value._meta.pk_field
            pk_value = getattr(value, pk_field.name)
            setattr(instance, fk_field_name, pk_value)


class _LazyRelatedInstance:
    """Helper to make related instance access awaitable."""

    def __init__(
        self,
        instance: "Model",
        field: "ForeignKey",
        related_model: Type["Model"],
        fk_value: Any,
        cache_name: str,
    ):
        self.instance = instance
        self.field = field
        self.related_model = related_model
        self.fk_value = fk_value
        self.cache_name = cache_name

    def __await__(self):
        """Make awaitable to load the related instance."""
        return self._load().__await__()

    async def _load(self) -> Optional["Model"]:
        """Load the related instance from database."""
        try:
            related_instance = await self.related_model.objects.get(id=self.fk_value)
            setattr(self.instance, self.cache_name, related_instance)
            return related_instance
        except Exception as e:
            logger.error(f"Error loading related {self.related_model.__name__}: {e}")
            setattr(self.instance, self.cache_name, None)
            return None


class ReverseRelationDescriptor:
    """
    Descriptor for reverse ForeignKey access.

    Enables: author.posts.all() (gets all Posts where author_id=author.id)
    """

    def __init__(
        self,
        related_model: Type["Model"],
        related_field: str,
        field: Optional["ForeignKey"] = None,
    ):
        """
        Initialize reverse relation descriptor.

        Args:
            related_model: Model with the ForeignKey
            related_field: Field name on related model
            field: ForeignKey field (for OneToOne)
        """
        self.related_model = related_model
        self.related_field = related_field
        self.field = field

    def __get__(self, instance: Optional["Model"], owner: Type["Model"]) -> Any:
        """Get related manager or instance."""
        if instance is None:
            return self

        # For OneToOne, return single instance (lazy loaded)
        if self.field and isinstance(self.field, OneToOneField):
            return self._get_onetoone_instance(instance)

        # For ForeignKey, return RelatedManager
        return RelatedManager(
            instance=instance,
            related_model=self.related_model,
            related_field=self.related_field,
            through_model=None,
        )

    def _get_onetoone_instance(self, instance: "Model") -> "_LazyReverseOneToOne":
        """Get OneToOne reverse instance (lazy loaded)."""
        return _LazyReverseOneToOne(instance, self.related_model, self.related_field)


class _LazyReverseOneToOne:
    """Helper for lazy loading OneToOne reverse relation."""

    def __init__(self, instance: "Model", related_model: Type["Model"], related_field: str):
        self.instance = instance
        self.related_model = related_model
        self.related_field = related_field
        self.cache_name = f"_reverse_{related_field}_cache"

    def __await__(self):
        """Make awaitable to load the related instance."""
        return self._load().__await__()

    async def _load(self) -> Optional["Model"]:
        """Load the related instance."""
        # Check cache
        if hasattr(self.instance, self.cache_name):
            return getattr(self.instance, self.cache_name)

        try:
            pk_field = self.instance._meta.pk_field
            pk_value = getattr(self.instance, pk_field.name)

            related_instance = await self.related_model.objects.get(
                **{f"{self.related_field}_id": pk_value}
            )
            setattr(self.instance, self.cache_name, related_instance)
            return related_instance
        except Exception:
            setattr(self.instance, self.cache_name, None)
            return None


class ManyToManyDescriptor:
    """
    Descriptor for ManyToMany field access.

    Enables: post.tags.all(), post.tags.add(tag1, tag2)
    """

    def __init__(self, field: "ManyToManyField"):
        """Initialize descriptor for ManyToMany field."""
        self.field = field

    def __get__(self, instance: Optional["Model"], owner: Type["Model"]) -> Any:
        """Get ManyToMany manager."""
        if instance is None:
            return self

        related_model = self.field.get_related_model()
        through_model = self.field.get_through_model()

        return RelatedManager(
            instance=instance,
            related_model=related_model,
            related_field=self.field.name,
            through_model=through_model,
            m2m_field=self.field,
        )


class RelatedManager:
    """
    Manager for reverse side of relationships.

    Provides QuerySet-like interface for related objects.

    Example:
        author = await Author.objects.get(id=1)
        posts = await author.posts.all()  # RelatedManager
        recent = await author.posts.filter(created_at__gte=last_week)
    """

    def __init__(
        self,
        instance: "Model",
        related_model: Type["Model"],
        related_field: str,
        through_model: Optional[Type["Model"]] = None,
        m2m_field: Optional["ManyToManyField"] = None,
    ):
        """
        Initialize related manager.

        Args:
            instance: Parent model instance
            related_model: Related model class
            related_field: Field name on related model pointing back
            through_model: Through model for ManyToMany
            m2m_field: ManyToManyField if applicable
        """
        self.instance = instance
        self.related_model = related_model
        self.related_field = related_field
        self.through_model = through_model
        self.m2m_field = m2m_field

    def get_queryset(self):
        """Get base queryset for related objects."""
        from .managers import QuerySet

        # Check if we have prefetched data cached
        # This will be set by QuerySet._apply_prefetch_related()
        cache_attr = f"_prefetched_{self._get_related_name()}"
        if hasattr(self.instance, cache_attr):
            # Return a QuerySet that's already populated with cached data
            qs = QuerySet(self.related_model)
            qs._result_cache = getattr(self.instance, cache_attr)
            qs._fetched = True
            return qs

        pk_field = self.instance._meta.pk_field
        pk_value = getattr(self.instance, pk_field.name)

        if self.through_model:
            # ManyToMany - need to join through table
            # Build query that joins through intermediate table
            qs = QuerySet(self.related_model)
            qs._m2m_through = {
                "through_model": self.through_model,
                "source_field": self.instance.__class__.__name__.lower(),
                "target_field": self.related_model.__name__.lower(),
                "source_pk": pk_value,
            }
            return qs
        else:
            # ForeignKey reverse - simple filter
            return QuerySet(self.related_model).filter(**{f"{self.related_field}_id": pk_value})

    def _get_related_name(self) -> str:
        """Get the related_name for this relationship."""
        # Try to find related_name from the relationship metadata
        from .relationships import get_reverse_relations

        reverse_rels = get_reverse_relations(self.instance.__class__)
        for rel in reverse_rels:
            if (
                rel["related_model"] == self.related_model
                and rel["related_field"] == self.related_field
            ):
                return rel.get("related_name", "")

        return ""

    def all(self):
        """Get all related objects."""
        return self.get_queryset()

    def filter(self, **kwargs):
        """Filter related objects."""
        return self.get_queryset().filter(**kwargs)

    def count(self):
        """Count related objects."""
        return self.get_queryset().count()

    async def create(self, **kwargs):
        """
        Create related object.

        For ForeignKey reverse: Sets FK to this instance.
        For ManyToMany: Creates object and adds to relationship.
        """
        if self.through_model:
            # ManyToMany - create object then add to relationship
            instance = self.related_model(**kwargs)
            await instance.save()
            await self.add(instance)
            return instance
        else:
            # ForeignKey - set FK to this instance
            pk_field = self.instance._meta.pk_field
            pk_value = getattr(self.instance, pk_field.name)
            kwargs[f"{self.related_field}_id"] = pk_value

            instance = self.related_model(**kwargs)
            await instance.save()
            return instance

    async def add(self, *objs):
        """
        Add objects to ManyToMany relationship.

        Args:
            *objs: Model instances or PKs to add

        Example:
            await post.tags.add(tag1, tag2)
        """
        if not self.through_model:
            raise ValueError("add() only works with ManyToMany relationships")

        # Get adapter
        adapter = await self._get_adapter()

        source_pk_field = self.instance._meta.pk_field
        source_pk = getattr(self.instance, source_pk_field.name)

        source_field_name = f"{self.instance.__class__.__name__.lower()}_id"
        target_field_name = f"{self.related_model.__name__.lower()}_id"

        for obj in objs:
            # Get target PK
            if isinstance(obj, self.related_model):
                target_pk_field = obj._meta.pk_field
                target_pk = getattr(obj, target_pk_field.name)
            else:
                # Assume it's a PK value
                target_pk = obj

            # Check if relationship already exists
            check_query = f"""  # nosec B608 - table_name validated in config
                SELECT 1 FROM {self.through_model.__tablename__}
                WHERE {source_field_name} = $1 AND {target_field_name} = $2
            """
            exists = await adapter.fetch_one(check_query, [source_pk, target_pk])

            if not exists:
                # Insert into through table
                insert_query = f"""  # nosec B608 - SQL construction reviewed
                    INSERT INTO {self.through_model.__tablename__}
                    ({source_field_name}, {target_field_name})
                    VALUES ($1, $2)
                """
                await adapter.execute(insert_query, [source_pk, target_pk])

    async def remove(self, *objs):
        """
        Remove objects from ManyToMany relationship.

        Args:
            *objs: Model instances or PKs to remove

        Example:
            await post.tags.remove(tag1)
        """
        if not self.through_model:
            raise ValueError("remove() only works with ManyToMany relationships")

        adapter = await self._get_adapter()

        source_pk_field = self.instance._meta.pk_field
        source_pk = getattr(self.instance, source_pk_field.name)

        source_field_name = f"{self.instance.__class__.__name__.lower()}_id"
        target_field_name = f"{self.related_model.__name__.lower()}_id"

        for obj in objs:
            # Get target PK
            if isinstance(obj, self.related_model):
                target_pk_field = obj._meta.pk_field
                target_pk = getattr(obj, target_pk_field.name)
            else:
                target_pk = obj

            # Delete from through table
            delete_query = f"""  # nosec B608 - SQL construction reviewed
                DELETE FROM {self.through_model.__tablename__}
                WHERE {source_field_name} = $1 AND {target_field_name} = $2
            """
            await adapter.execute(delete_query, [source_pk, target_pk])

    async def clear(self):
        """
        Clear all ManyToMany relationships.

        Example:
            await post.tags.clear()
        """
        if not self.through_model:
            raise ValueError("clear() only works with ManyToMany relationships")

        adapter = await self._get_adapter()

        source_pk_field = self.instance._meta.pk_field
        source_pk = getattr(self.instance, source_pk_field.name)

        source_field_name = f"{self.instance.__class__.__name__.lower()}_id"

        # Delete all relationships
        delete_query = f"""  # nosec B608 - SQL construction reviewed
            DELETE FROM {self.through_model.__tablename__}
            WHERE {source_field_name} = $1
        """
        await adapter.execute(delete_query, [source_pk])

    async def set(self, objs):
        """
        Set ManyToMany relationships to exact list.

        Args:
            objs: List of instances or PKs

        Example:
            await post.tags.set([tag1, tag2, tag3])
        """
        if not self.through_model:
            raise ValueError("set() only works with ManyToMany relationships")

        await self.clear()
        if objs:
            await self.add(*objs)

    async def _get_adapter(self):
        """Get database adapter."""
        from ..adapters.postgresql import PostgreSQLAdapter

        adapter = PostgreSQLAdapter()
        await adapter.connect()
        return adapter


class ForeignKey(Field):
    """
    ForeignKey relationship field.

    Creates a many-to-one relationship. Multiple objects can reference
    the same related object.

    Args:
        to: Related model class or string name
        on_delete: Cascade behavior when related object is deleted:
            - CASCADE: Delete this object too
            - SET_NULL: Set to NULL (requires nullable=True)
            - SET_DEFAULT: Set to default value
            - PROTECT: Prevent deletion of related object
            - RESTRICT: Similar to PROTECT
            - DO_NOTHING: No action (may cause integrity errors)
        related_name: Name for reverse relation on related model
        related_query_name: Name for filtering through reverse relation
        to_field: Field on related model to reference (default: primary key)
        db_constraint: Create database foreign key constraint

    Example:
        class Post(Model):
            title = CharField(max_length=200)
            author = ForeignKey(
                'Author',
                on_delete=CASCADE,
                related_name='posts'
            )

        # Forward relation
        post = await Post.objects.get(id=1)
        author = await post.author  # Loads Author instance

        # Reverse relation
        author = await Author.objects.get(id=1)
        posts = await author.posts.all()  # QuerySet of Posts
    """

    def __init__(
        self,
        to: Union[Type["Model"], str],
        on_delete: Union[str, type] = "CASCADE",
        related_name: Optional[str] = None,
        related_query_name: Optional[str] = None,
        to_field: Optional[str] = None,
        db_constraint: bool = True,
        **kwargs,
    ):
        """Initialize ForeignKey field."""
        # ForeignKey can be NULL if not specified
        kwargs.setdefault("nullable", True)

        super().__init__(**kwargs)

        self.to = to
        # Handle both string and class-based on_delete
        if isinstance(on_delete, str):
            self.on_delete = on_delete.upper()
        else:
            self.on_delete = (
                on_delete.__name__.upper() if hasattr(on_delete, "__name__") else "CASCADE"
            )

        self.related_name = related_name
        self.related_query_name = related_query_name or related_name
        self.to_field = to_field
        self.db_constraint = db_constraint

        # Validate on_delete
        valid_on_delete = {
            "CASCADE",
            "SET_NULL",
            "SET_DEFAULT",
            "PROTECT",
            "RESTRICT",
            "DO_NOTHING",
        }
        if self.on_delete not in valid_on_delete:
            raise ValueError(f"on_delete must be one of {valid_on_delete}, got {on_delete}")

        # SET_NULL requires nullable=True
        if self.on_delete == "SET_NULL" and not self.nullable:
            raise ValueError("SET_NULL requires nullable=True")

        # Will be set by metaclass
        self._related_model: Optional[Type["Model"]] = None
        self._related_field_name: Optional[str] = None

    def contribute_to_class(self, model: Type["Model"], name: str):
        """
        Called by metaclass when field is added to model.

        Sets up forward descriptor and reverse relation on related model.

        Args:
            model: Model class this field belongs to
            name: Field name
        """
        self.model = model
        self.name = name

        # ForeignKey itself doesn't create a database column
        # The _id field does, so set db_column to None for the FK itself
        self.db_column = None

        # Resolve related model if string
        if isinstance(self.to, str):
            # Lazy resolution - will be resolved when first accessed
            self._to_string = self.to
        else:
            self._related_model = self.to

        # Add forward relation descriptor
        setattr(model, name, ForwardRelationDescriptor(self))

        # Add _id field to store foreign key value
        fk_field = IntegerField(nullable=self.nullable, db_column=f"{name}_id", db_index=True)
        fk_field.name = f"{name}_id"
        fk_field.model = model
        model._fields[f"{name}_id"] = fk_field

        # Set up reverse relation (will be added when related model is
        # available)
        if self.related_name:
            self._setup_reverse_relation()

    def _setup_reverse_relation(self):
        """Set up reverse relation on related model."""
        related_model = self.get_related_model()
        if related_model:
            descriptor = ReverseRelationDescriptor(
                related_model=self.model,
                related_field=self.name,
                field=self if isinstance(self, OneToOneField) else None,
            )
            setattr(related_model, self.related_name, descriptor)

            # Register reverse relationship for prefetch_related() support
            relation_type = "onetoone" if isinstance(self, OneToOneField) else "foreignkey"
            register_reverse_relation(
                target_model=related_model,
                related_model=self.model,
                related_field=self.name,
                relation_type=relation_type,
                related_name=self.related_name,
            )

    def get_related_model(self) -> Optional[Type["Model"]]:
        """Get related model class (resolves lazy references)."""
        if self._related_model is None and hasattr(self, "_to_string"):
            # Resolve string reference
            self._related_model = get_model(self._to_string)
            if self._related_model and self.related_name:
                self._setup_reverse_relation()

        return self._related_model

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """
        Get database column type.

        ForeignKey columns store the primary key of the related object.

        Args:
            dialect: Database dialect

        Returns:
            SQL column type
        """
        # Get PK field type from related model if available
        related_model = self.get_related_model()
        if related_model and hasattr(related_model, "_meta"):
            pk_field = related_model._meta.pk_field
            if pk_field:
                return pk_field.get_db_type(dialect)

        # Default to INTEGER
        return "INTEGER"

    def get_db_constraint_sql(self) -> Optional[str]:
        """
        Get SQL for foreign key constraint.

        Returns:
            SQL constraint definition or None
        """
        if not self.db_constraint:
            return None

        related_model = self.get_related_model()
        if not related_model:
            return None

        related_table = related_model.__tablename__
        related_field = self.to_field or related_model._meta.pk_field.db_column

        constraint_name = f"fk_{self.model.__tablename__}_{self.name}"

        on_delete_actions = {
            "CASCADE": "ON DELETE CASCADE",
            "SET_NULL": "ON DELETE SET NULL",
            "SET_DEFAULT": "ON DELETE SET DEFAULT",
            "PROTECT": "ON DELETE RESTRICT",
            "RESTRICT": "ON DELETE RESTRICT",
            "DO_NOTHING": "",
        }

        on_delete_sql = on_delete_actions.get(self.on_delete, "")

        return (
            f"CONSTRAINT {constraint_name} "
            f"FOREIGN KEY ({self.db_column}) "
            f"REFERENCES {related_table}({related_field}) "
            f"{on_delete_sql}"
        ).strip()


class OneToOneField(ForeignKey):
    """
    OneToOne relationship field.

    Similar to ForeignKey but ensures uniqueness - each object can only
    be related to one other object.

    Creates a unique index on the foreign key column.

    Args:
        Same as ForeignKey

    Example:
        class User(Model):
            username = CharField(max_length=100)

        class Profile(Model):
            user = OneToOneField(
                User,
                on_delete=CASCADE,
                related_name='profile'
            )
            bio = TextField()

        # Forward relation
        profile = await Profile.objects.get(id=1)
        user = await profile.user

        # Reverse relation (single object, not QuerySet)
        user = await User.objects.get(id=1)
        profile = await user.profile  # Single Profile instance
    """

    def __init__(self, *args, **kwargs):
        """Initialize OneToOneField."""
        # OneToOne must be unique
        kwargs["unique"] = True
        super().__init__(*args, **kwargs)

    def get_db_constraint_sql(self) -> Optional[str]:
        """Get SQL constraints including UNIQUE."""
        fk_constraint = super().get_db_constraint_sql()

        unique_constraint = (
            f"CONSTRAINT uq_{self.model.__tablename__}_{self.name} " f"UNIQUE ({self.db_column})"
        )

        if fk_constraint:
            return f"{fk_constraint}, {unique_constraint}"
        return unique_constraint


class ManyToManyField(Field):
    """
    ManyToMany relationship field.

    Creates a many-to-many relationship using an intermediate table.
    Multiple objects can be related to multiple other objects.

    Args:
        to: Related model class or string name
        through: Custom intermediate model (optional)
        through_fields: Tuple of (source_field, target_field) for custom through
        related_name: Name for reverse relation
        related_query_name: Name for filtering through reverse relation
        db_table: Name of intermediate table (auto-generated if not specified)
        db_constraint: Create database foreign key constraints
        symmetrical: For self-referential M2M, whether relation is symmetrical

    Example:
        class Post(Model):
            title = CharField(max_length=200)
            tags = ManyToManyField('Tag', related_name='posts')

        class Tag(Model):
            name = CharField(max_length=50)

        # Add tags
        post = await Post.objects.get(id=1)
        await post.tags.add(tag1, tag2)

        # Get all tags
        tags = await post.tags.all()

        # Reverse relation
        tag = await Tag.objects.get(id=1)
        posts = await tag.posts.all()

        # Custom through model
        class Membership(Model):
            user = ForeignKey(User, on_delete=CASCADE)
            group = ForeignKey(Group, on_delete=CASCADE)
            date_joined = DateTimeField(auto_now_add=True)
            role = CharField(max_length=50)

        class Group(Model):
            name = CharField(max_length=100)
            members = ManyToManyField(
                User,
                through=Membership,
                related_name='groups'
            )
    """

    def __init__(
        self,
        to: Union[Type["Model"], str],
        through: Optional[Type["Model"]] = None,
        through_fields: Optional[tuple] = None,
        related_name: Optional[str] = None,
        related_query_name: Optional[str] = None,
        db_table: Optional[str] = None,
        db_constraint: bool = True,
        symmetrical: bool = False,
        **kwargs,
    ):
        """Initialize ManyToManyField."""
        # ManyToMany doesn't create a database column
        kwargs["db_column"] = None

        super().__init__(**kwargs)

        self.to = to
        self.through = through
        self.through_fields = through_fields
        self.related_name = related_name
        self.related_query_name = related_query_name or related_name
        self.db_table = db_table
        self.db_constraint = db_constraint
        self.symmetrical = symmetrical

        # Will be set by metaclass
        self._related_model: Optional[Type["Model"]] = None
        self._through_model: Optional[Type["Model"]] = None

    def contribute_to_class(self, model: Type["Model"], name: str):
        """
        Called by metaclass when field is added to model.

        Creates intermediate table if not using custom through model.

        Args:
            model: Model class this field belongs to
            name: Field name
        """
        self.model = model
        self.name = name

        # Resolve related model
        if isinstance(self.to, str):
            self._to_string = self.to
        else:
            self._related_model = self.to

        # Create through model if not specified
        if self.through is None:
            self._create_through_model(model, name)
        else:
            self._through_model = self.through

        # Add ManyToMany descriptor
        setattr(model, name, ManyToManyDescriptor(self))

        # Set up reverse relation
        if self.related_name:
            self._setup_reverse_relation()

    def _create_through_model(self, model: Type["Model"], name: str):
        """
        Create intermediate table model.

        Args:
            model: Source model
            name: Field name
        """
        from .models import Model, ModelMeta

        related_model = self.get_related_model()
        if not related_model:
            # Will be created when related model is resolved
            return

        # Auto-generate through model
        # Table name: model1_model2
        if self.db_table:
            table_name = self.db_table
        else:
            model1 = model.__tablename__
            model2 = related_model.__tablename__
            # Sort names for consistent naming
            names = sorted([model1, model2])
            table_name = f"{names[0]}_{names[1]}"

        # Create through model class dynamically
        source_field_name = f"{model.__name__.lower()}_id"
        target_field_name = f"{related_model.__name__.lower()}_id"

        through_class_name = f"{model.__name__}_{related_model.__name__}_Through"

        # Create model dynamically
        attrs = {
            "__module__": model.__module__,
            "__tablename__": table_name,
            source_field_name: IntegerField(nullable=False, db_index=True),
            target_field_name: IntegerField(nullable=False, db_index=True),
        }

        # Add Meta class
        class ThroughMeta:
            db_table = table_name
            unique_together = [(source_field_name, target_field_name)]

        attrs["Meta"] = ThroughMeta

        # Create the through model
        from .models import Model

        self._through_model = type(through_class_name, (Model,), attrs)

    def _setup_reverse_relation(self):
        """Set up reverse relation on related model."""
        related_model = self.get_related_model()
        if related_model:
            descriptor = ManyToManyDescriptor(self)
            # Create a wrapper for reverse access

            class ReverseManyToManyDescriptor:
                def __init__(self, forward_field):
                    self.forward_field = forward_field

                def __get__(self, instance, owner):
                    if instance is None:
                        return self

                    return RelatedManager(
                        instance=instance,
                        related_model=self.forward_field.model,
                        related_field=self.forward_field.name,
                        through_model=self.forward_field.get_through_model(),
                        m2m_field=self.forward_field,
                    )

            setattr(related_model, self.related_name, ReverseManyToManyDescriptor(self))

            # Register reverse relationship for prefetch_related() support
            register_reverse_relation(
                target_model=related_model,
                related_model=self.model,
                related_field=self.name,
                relation_type="manytomany",
                related_name=self.related_name,
            )

    def get_db_type(self, dialect: str = "postgresql") -> Optional[str]:
        """
        ManyToMany doesn't create a column in the model's table.

        Returns:
            None (no column created)
        """
        return None

    def get_through_model(self) -> Optional[Type["Model"]]:
        """Get intermediate table model."""
        if self._through_model is None and self.through is None:
            # Try to create it now if related model is available
            related_model = self.get_related_model()
            if related_model and self.model:
                self._create_through_model(self.model, self.name)

        return self._through_model

    def get_related_model(self) -> Optional[Type["Model"]]:
        """Get related model class."""
        if self._related_model is None and hasattr(self, "_to_string"):
            # Resolve string reference
            self._related_model = get_model(self._to_string)
            if self._related_model:
                if self.related_name:
                    self._setup_reverse_relation()
                if self.through is None:
                    self._create_through_model(self.model, self.name)

        return self._related_model


# Cascade behaviors (can be used as classes or strings)
class CASCADE:
    """Delete related objects (default)."""

    pass


class PROTECT:
    """Prevent deletion if related objects exist."""

    pass


class RESTRICT:
    """Similar to PROTECT."""

    pass


class SET_NULL:
    """Set foreign key to NULL."""

    pass


class SET_DEFAULT:
    """Set foreign key to default value."""

    pass


class DO_NOTHING:
    """Take no action."""

    pass


# Alias for ForeignKey (Django compatibility)
OneToMany = ForeignKey


__all__ = [
    "ForeignKey",
    "OneToOneField",
    "OneToMany",
    "ManyToManyField",
    "ManyToMany",
    "RelatedManager",
    "CASCADE",
    "PROTECT",
    "RESTRICT",
    "SET_NULL",
    "SET_DEFAULT",
    "DO_NOTHING",
    "register_model",
    "get_model",
    "register_reverse_relation",
    "get_reverse_relations",
]

# Additional alias for ManyToManyField
ManyToMany = ManyToManyField
