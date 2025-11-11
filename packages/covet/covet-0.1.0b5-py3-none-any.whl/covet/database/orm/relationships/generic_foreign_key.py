"""
Generic Foreign Key Implementation

Enables relationships to any model type (polymorphic foreign keys).
Uses ContentType framework to track model types dynamically.

Example:
    class Comment(Model):
        # Can attach to any model
        content_type = ForeignKey(ContentType, on_delete=CASCADE)
        object_id = IntegerField()
        content_object = GenericForeignKey('content_type', 'object_id')

        text = TextField()

    class Post(Model):
        title = CharField(max_length=200)
        comments = GenericRelation('Comment')

    class Photo(Model):
        caption = CharField(max_length=200)
        comments = GenericRelation('Comment')

    # Usage
    post = await Post.objects.get(id=1)
    comment = Comment(content_object=post, text='Great post!')
    await comment.save()

    # Get all comments for post
    comments = await post.comments.all()
"""

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

if TYPE_CHECKING:
    from ..models import Model

logger = logging.getLogger(__name__)


# Global content type registry
_content_type_registry: Dict[str, Type["Model"]] = {}
_model_to_content_type: Dict[Type["Model"], "ContentType"] = {}


class ContentType:
    """
    ContentType framework for tracking model types.

    Maps model classes to app_label/model identifiers for generic foreign keys.
    """

    _registry: Dict[str, "ContentType"] = {}
    _id_counter = 1

    def __init__(self, app_label: str, model: str, model_class: Type["Model"]):
        self.id = ContentType._id_counter
        ContentType._id_counter += 1

        self.app_label = app_label
        self.model = model
        self.model_class = model_class

        # Register
        key = f"{app_label}.{model}"
        ContentType._registry[key] = self
        _model_to_content_type[model_class] = self

    @classmethod
    def get_for_model(cls, model: Type["Model"]) -> "ContentType":
        """
        Get or create ContentType for a model.

        Args:
            model: Model class

        Returns:
            ContentType instance
        """
        # Check cache
        if model in _model_to_content_type:
            return _model_to_content_type[model]

        # Create new ContentType
        app_label = getattr(model, "__module__", "default").split(".")[0]
        model_name = model.__name__.lower()

        key = f"{app_label}.{model_name}"

        if key in cls._registry:
            return cls._registry[key]

        ct = ContentType(app_label, model_name, model)
        return ct

    @classmethod
    def get_by_id(cls, ct_id: int) -> Optional["ContentType"]:
        """Get ContentType by ID."""
        for ct in cls._registry.values():
            if ct.id == ct_id:
                return ct
        return None

    @classmethod
    def get_by_natural_key(cls, app_label: str, model: str) -> Optional["ContentType"]:
        """Get ContentType by app_label and model name."""
        key = f"{app_label}.{model}"
        return cls._registry.get(key)

    def __str__(self):
        return f"{self.app_label}.{self.model}"

    def __repr__(self):
        return f"<ContentType: {self.app_label}.{self.model}>"


class GenericForeignKey:
    """
    Generic foreign key field.

    Allows referencing any model type using ContentType framework.

    Args:
        ct_field: Name of field storing ContentType (default: 'content_type')
        fk_field: Name of field storing object ID (default: 'object_id')
        for_concrete_model: Whether to use concrete model for inherited models

    Example:
        class TaggedItem(Model):
            content_type = ForeignKey(ContentType, on_delete=CASCADE)
            object_id = IntegerField()
            content_object = GenericForeignKey('content_type', 'object_id')
            tag = CharField(max_length=50)
    """

    def __init__(
        self,
        ct_field: str = "content_type",
        fk_field: str = "object_id",
        for_concrete_model: bool = True,
    ):
        self.ct_field = ct_field
        self.fk_field = fk_field
        self.for_concrete_model = for_concrete_model

        self.name: Optional[str] = None
        self.model: Optional[Type["Model"]] = None
        self.cache_attr: Optional[str] = None

    def contribute_to_class(self, model: Type["Model"], name: str):
        """Called by metaclass when field is added to model."""
        self.name = name
        self.model = model
        self.cache_attr = f"_{name}_cache"

        # Set descriptor
        setattr(model, name, GenericForeignKeyDescriptor(self))

    def __get__(self, instance, owner):
        """Descriptor protocol."""
        if instance is None:
            return self

        # Check cache
        if hasattr(instance, self.cache_attr):
            return getattr(instance, self.cache_attr)

        # Get content type and object ID
        ct_id = getattr(instance, f"{self.ct_field}_id", None)
        obj_id = getattr(instance, self.fk_field, None)

        if ct_id is None or obj_id is None:
            setattr(instance, self.cache_attr, None)
            return None

        # This returns a lazy loader
        return _LazyGenericRelation(instance, self, ct_id, obj_id)

    def __set__(self, instance, value):
        """Set generic foreign key."""
        # Clear cache
        if hasattr(instance, self.cache_attr):
            delattr(instance, self.cache_attr)

        if value is None:
            setattr(instance, f"{self.ct_field}_id", None)
            setattr(instance, self.fk_field, None)
            setattr(instance, self.cache_attr, None)
        else:
            # Get ContentType for value's model
            ct = ContentType.get_for_model(value.__class__)
            setattr(instance, f"{self.ct_field}_id", ct.id)

            # Set object ID
            pk_field = value._meta.pk_field
            pk_value = getattr(value, pk_field.name)
            setattr(instance, self.fk_field, pk_value)

            # Cache value
            setattr(instance, self.cache_attr, value)


class GenericForeignKeyDescriptor:
    """Descriptor for GenericForeignKey access."""

    def __init__(self, field: GenericForeignKey):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self.field

        return self.field.__get__(instance, owner)

    def __set__(self, instance, value):
        self.field.__set__(instance, value)


class _LazyGenericRelation:
    """Helper for lazy loading generic foreign key."""

    def __init__(self, instance: "Model", field: GenericForeignKey, ct_id: int, obj_id: Any):
        self.instance = instance
        self.field = field
        self.ct_id = ct_id
        self.obj_id = obj_id

    def __await__(self):
        """Make awaitable."""
        return self._load().__await__()

    async def _load(self) -> Optional["Model"]:
        """Load the related instance."""
        # Get ContentType
        ct = ContentType.get_by_id(self.ct_id)
        if not ct:
            logger.error(f"ContentType with ID {self.ct_id} not found")
            setattr(self.instance, self.field.cache_attr, None)
            return None

        try:
            # Load object
            obj = await ct.model_class.objects.get(id=self.obj_id)
            setattr(self.instance, self.field.cache_attr, obj)
            return obj
        except Exception as e:
            logger.error(f"Error loading generic relation: {e}")
            setattr(self.instance, self.field.cache_attr, None)
            return None


class GenericRelation:
    """
    Reverse side of GenericForeignKey.

    Provides access to all objects that reference this instance via GenericForeignKey.

    Args:
        to: Model with GenericForeignKey
        related_query_name: Name for reverse filtering
        content_type_field: Name of content type field in related model
        object_id_field: Name of object ID field in related model

    Example:
        class Post(Model):
            title = CharField(max_length=200)
            comments = GenericRelation('Comment')

        class Comment(Model):
            content_type = ForeignKey(ContentType, on_delete=CASCADE)
            object_id = IntegerField()
            content_object = GenericForeignKey()
            text = TextField()

        # Usage
        post = await Post.objects.get(id=1)
        comments = await post.comments.all()
    """

    def __init__(
        self,
        to: Union[Type["Model"], str],
        related_query_name: Optional[str] = None,
        content_type_field: str = "content_type",
        object_id_field: str = "object_id",
    ):
        self.to = to
        self.related_query_name = related_query_name
        self.content_type_field = content_type_field
        self.object_id_field = object_id_field

        self.name: Optional[str] = None
        self.model: Optional[Type["Model"]] = None
        self._related_model: Optional[Type["Model"]] = None
        self._to_string: Optional[str] = None

    def contribute_to_class(self, model: Type["Model"], name: str):
        """Called by metaclass when field is added to model."""
        self.name = name
        self.model = model

        # Resolve related model
        if isinstance(self.to, str):
            self._to_string = self.to
        else:
            self._related_model = self.to

        # Set descriptor
        setattr(model, name, GenericRelationDescriptor(self))

    def get_related_model(self) -> Optional[Type["Model"]]:
        """Get related model (resolves lazy references)."""
        if self._related_model is None and self._to_string:
            from ..relationships import get_model

            self._related_model = get_model(self._to_string)
        return self._related_model

    def get_db_type(self, dialect: str = "postgresql") -> Optional[str]:
        """GenericRelation doesn't create a column."""
        return None


class GenericRelationDescriptor:
    """Descriptor for GenericRelation access."""

    def __init__(self, field: GenericRelation):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self.field

        return GenericRelationManager(instance, self.field)


class GenericRelationManager:
    """
    Manager for GenericRelation.

    Provides QuerySet-like interface for accessing related objects.
    """

    def __init__(self, instance: "Model", field: GenericRelation):
        self.instance = instance
        self.field = field
        self.related_model = field.get_related_model()

    def get_queryset(self):
        """Get QuerySet for related objects."""
        from ..managers import QuerySet

        if not self.related_model:
            raise ValueError(f"Cannot resolve related model for {self.field.name}")

        # Get ContentType for this model
        ct = ContentType.get_for_model(self.instance.__class__)

        # Get instance PK
        pk_field = self.instance._meta.pk_field
        pk_value = getattr(self.instance, pk_field.name)

        if pk_value is None:
            raise ValueError(
                f"Cannot use GenericRelation on unsaved {self.instance.__class__.__name__} instance"
            )

        # Build filter
        qs = QuerySet(self.related_model)
        qs = qs.filter(
            **{f"{self.field.content_type_field}_id": ct.id, self.field.object_id_field: pk_value}
        )

        return qs

    def all(self):
        """Get all related objects."""
        return self.get_queryset()

    def filter(self, **kwargs):
        """Filter related objects."""
        return self.get_queryset().filter(**kwargs)

    async def count(self) -> int:
        """Count related objects."""
        return await self.get_queryset().count()

    async def create(self, **kwargs) -> "Model":
        """Create related object."""
        # Set generic foreign key fields
        ct = ContentType.get_for_model(self.instance.__class__)
        pk_field = self.instance._meta.pk_field
        pk_value = getattr(self.instance, pk_field.name)

        kwargs[f"{self.field.content_type_field}_id"] = ct.id
        kwargs[self.field.object_id_field] = pk_value

        obj = self.related_model(**kwargs)
        await obj.save()
        return obj


class GenericPrefetch:
    """
    Helper for prefetching generic relations.

    Optimizes queries when loading multiple objects with generic foreign keys.

    Example:
        comments = await Comment.objects.prefetch_generic('content_object')

        # Now content_object is loaded without additional queries
        for comment in comments:
            print(comment.content_object.title)
    """

    @staticmethod
    async def prefetch_generic_fk(instances: List["Model"], field_name: str):
        """
        Prefetch generic foreign key for multiple instances.

        Args:
            instances: List of model instances
            field_name: Name of GenericForeignKey field

        Example:
            comments = await Comment.objects.all()
            await GenericPrefetch.prefetch_generic_fk(comments, 'content_object')
        """
        if not instances:
            return

        # Get field
        model = instances[0].__class__
        field = getattr(model, field_name, None)

        if not isinstance(field, GenericForeignKeyDescriptor):
            raise ValueError(f"{field_name} is not a GenericForeignKey")

        gfk = field.field

        # Group by content type
        grouped: Dict[int, List[tuple]] = defaultdict(list)

        for instance in instances:
            ct_id = getattr(instance, f"{gfk.ct_field}_id", None)
            obj_id = getattr(instance, gfk.fk_field, None)

            if ct_id is not None and obj_id is not None:
                grouped[ct_id].append((instance, obj_id))

        # Fetch each content type's objects
        for ct_id, items in grouped.items():
            ct = ContentType.get_by_id(ct_id)
            if not ct:
                continue

            # Collect object IDs
            obj_ids = [obj_id for _, obj_id in items]

            # Bulk fetch
            objects = await ct.model_class.objects.filter(id__in=obj_ids)

            # Build lookup dict
            obj_dict = {getattr(obj, obj._meta.pk_field.name): obj for obj in objects}

            # Set cached values
            for instance, obj_id in items:
                obj = obj_dict.get(obj_id)
                setattr(instance, gfk.cache_attr, obj)


__all__ = [
    "ContentType",
    "GenericForeignKey",
    "GenericRelation",
    "GenericPrefetch",
    "GenericForeignKeyDescriptor",
    "GenericRelationDescriptor",
    "GenericRelationManager",
]
