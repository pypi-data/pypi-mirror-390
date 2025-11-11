"""
GraphQL Schema Definition System

Modern schema builder using Strawberry GraphQL with full type safety.
Provides decorators and utilities for defining GraphQL types, fields,
and operations.
"""

import dataclasses
import inspect
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum as PyEnum
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import strawberry
from strawberry import Schema
from strawberry.types import Info as StrawberryInfo

try:
    from strawberry.schema.config import StrawberryConfig
except ImportError:
    # Fallback for older versions
    StrawberryConfig = None

# Re-export Strawberry decorators with type aliases
ObjectType = strawberry.type
InputType = strawberry.input
InterfaceType = strawberry.interface
UnionType = strawberry.union
EnumType = strawberry.enum

# Aliases for consistency
graphql_type = strawberry.type
graphql_input = strawberry.input
graphql_interface = strawberry.interface
graphql_enum = strawberry.enum
graphql_scalar = strawberry.scalar
field = strawberry.field

# Direct exports for backward compatibility
enum = strawberry.enum
type = strawberry.type  # Add plain 'type' alias (Note: shadows built-in type)
input = strawberry.input  # Add plain 'input' alias (Note: shadows built-in input)
interface = strawberry.interface  # Add plain 'interface' alias
type_decorator = strawberry.type
input_decorator = strawberry.input
interface_decorator = strawberry.interface
scalar = strawberry.scalar


# Custom scalar types
@strawberry.scalar(
    serialize=lambda v: v.isoformat(),
    parse_value=lambda v: datetime.fromisoformat(v) if isinstance(v, str) else v,
)
class DateTime:
    """DateTime scalar for precise timestamp handling."""

    __doc__ = "ISO 8601 formatted datetime string"


@strawberry.scalar(
    serialize=lambda v: v.isoformat(),
    parse_value=lambda v: date.fromisoformat(v) if isinstance(v, str) else v,
)
class Date:
    """Date scalar for date-only values."""

    __doc__ = "ISO 8601 formatted date string (YYYY-MM-DD)"


@strawberry.scalar(
    serialize=lambda v: v.isoformat(),
    parse_value=lambda v: time.fromisoformat(v) if isinstance(v, str) else v,
)
class Time:
    """Time scalar for time-only values."""

    __doc__ = "ISO 8601 formatted time string (HH:MM:SS)"


@strawberry.scalar(
    serialize=lambda v: str(v),
    parse_value=lambda v: Decimal(v) if isinstance(v, (str, int, float)) else v,
)
class DecimalScalar:
    """Decimal scalar for precise numeric values."""

    __doc__ = "High-precision decimal number as string"


@strawberry.scalar(
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
class JSON:
    """JSON scalar for arbitrary JSON data."""

    __doc__ = "Arbitrary JSON data"


@strawberry.scalar(
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
class Upload:
    """File upload scalar."""

    __doc__ = "File upload (multipart/form-data)"


class ScalarType:
    """Custom scalar type registry."""

    DateTime = DateTime
    Date = Date
    Time = Time
    Decimal = DecimalScalar
    JSON = JSON
    Upload = Upload


class GraphQLSchema:
    """
    GraphQL Schema builder with Strawberry.

    Provides high-level interface for building GraphQL schemas with
    queries, mutations, subscriptions, and custom types.

    Example:
        schema_builder = GraphQLSchema()

        @schema_builder.type()
        class User:
            id: int
            name: str
            email: str

        @schema_builder.query()
        class Query:
            @strawberry.field
            async def user(self, id: int) -> User:
                return await get_user(id)

        schema = schema_builder.build()
    """

    def __init__(
        self,
        enable_federation: bool = False,
        enable_query_cost_analysis: bool = True,
        max_query_depth: int = 10,
        max_query_complexity: int = 1000,
    ):
        """
        Initialize schema builder.

        Args:
            enable_federation: Enable Apollo Federation support
            enable_query_cost_analysis: Enable query cost analysis
            max_query_depth: Maximum query depth
            max_query_complexity: Maximum query complexity
        """
        self.query_type: Optional[Type] = None
        self.mutation_type: Optional[Type] = None
        self.subscription_type: Optional[Type] = None
        self.types: List[Type] = []
        self.directives: List[Any] = []

        self.enable_federation = enable_federation
        self.enable_query_cost_analysis = enable_query_cost_analysis
        self.max_query_depth = max_query_depth
        self.max_query_complexity = max_query_complexity

        self._schema: Optional[Schema] = None

    def type(self, cls: Optional[Type] = None, **kwargs):
        """
        Register GraphQL object type.

        Args:
            cls: Class to convert to GraphQL type
            **kwargs: Additional Strawberry type options

        Returns:
            Decorated class or decorator
        """

        def decorator(target_cls: Type) -> Type:
            # Apply Strawberry type decorator
            typed_cls = strawberry.type(target_cls, **kwargs)
            self.types.append(typed_cls)
            return typed_cls

        if cls is None:
            return decorator
        return decorator(cls)

    def input(self, cls: Optional[Type] = None, **kwargs):
        """Register GraphQL input type."""

        def decorator(target_cls: Type) -> Type:
            input_cls = strawberry.input(target_cls, **kwargs)
            self.types.append(input_cls)
            return input_cls

        if cls is None:
            return decorator
        return decorator(cls)

    def interface(self, cls: Optional[Type] = None, **kwargs):
        """Register GraphQL interface type."""

        def decorator(target_cls: Type) -> Type:
            interface_cls = strawberry.interface(target_cls, **kwargs)
            self.types.append(interface_cls)
            return interface_cls

        if cls is None:
            return decorator
        return decorator(cls)

    def enum(self, cls: Optional[Type] = None, **kwargs):
        """Register GraphQL enum type."""

        def decorator(target_cls: Type) -> Type:
            enum_cls = strawberry.enum(target_cls, **kwargs)
            self.types.append(enum_cls)
            return enum_cls

        if cls is None:
            return decorator
        return decorator(cls)

    def query(self, cls: Optional[Type] = None):
        """
        Register root Query type.

        Args:
            cls: Query class

        Returns:
            Decorated class or decorator
        """

        def decorator(target_cls: Type) -> Type:
            self.query_type = strawberry.type(target_cls)
            return self.query_type

        if cls is None:
            return decorator
        return decorator(cls)

    def mutation(self, cls: Optional[Type] = None):
        """Register root Mutation type."""

        def decorator(target_cls: Type) -> Type:
            self.mutation_type = strawberry.type(target_cls)
            return self.mutation_type

        if cls is None:
            return decorator
        return decorator(cls)

    def subscription(self, cls: Optional[Type] = None):
        """Register root Subscription type."""

        def decorator(target_cls: Type) -> Type:
            self.subscription_type = strawberry.type(target_cls)
            return self.subscription_type

        if cls is None:
            return decorator
        return decorator(cls)

    def directive(self, directive: Any):
        """Register custom directive."""
        self.directives.append(directive)

    def build(self) -> Schema:
        """
        Build Strawberry schema from registered types.

        Returns:
            Strawberry Schema instance

        Raises:
            ValueError: If no Query type is defined
        """
        if not self.query_type:
            raise ValueError("Query type is required")

        # Build schema configuration
        schema_kwargs = {
            "query": self.query_type,
            "mutation": self.mutation_type,
            "subscription": self.subscription_type,
            "types": self.types,
            "directives": self.directives,
        }

        # Add config if available
        if StrawberryConfig is not None:
            config = StrawberryConfig(
                auto_camel_case=True,  # Convert snake_case to camelCase
            )
            schema_kwargs["config"] = config

        # Create schema
        self._schema = strawberry.Schema(**schema_kwargs)

        return self._schema

    @property
    def schema(self) -> Schema:
        """Get built schema (builds if not already built)."""
        if self._schema is None:
            return self.build()
        return self._schema

    def get_sdl(self) -> str:
        """Get GraphQL Schema Definition Language (SDL) representation."""
        return str(self.schema)


class FieldResolver:
    """
    Field resolver with advanced features like caching and batching.

    Example:
        @strawberry.field
        async def posts(self, info: Info) -> List[Post]:
            resolver = FieldResolver(info)
            return await resolver.resolve_with_dataloader('posts', self.id)
    """

    def __init__(self, info: StrawberryInfo):
        """
        Initialize field resolver.

        Args:
            info: Strawberry Info object containing context
        """
        self.info = info
        self.context = info.context

    async def resolve_with_dataloader(
        self,
        loader_name: str,
        key: Any,
    ) -> Any:
        """
        Resolve field using DataLoader.

        Args:
            loader_name: Name of the DataLoader
            key: Key to load

        Returns:
            Loaded value
        """
        # Get DataLoader from context
        loaders = getattr(self.context, "dataloaders", {})
        loader = loaders.get(loader_name)

        if loader is None:
            raise ValueError(f"DataLoader '{loader_name}' not found in context")

        return await loader.load(key)

    async def resolve_with_cache(
        self,
        cache_key: str,
        resolver: Callable,
        ttl: Optional[int] = None,
    ) -> Any:
        """
        Resolve field with caching.

        Args:
            cache_key: Cache key
            resolver: Resolver function
            ttl: Time to live in seconds

        Returns:
            Resolved value
        """
        # Get cache from context
        cache = getattr(self.context, "cache", None)

        if cache is None:
            # No cache available, resolve directly
            return await resolver()

        # Try to get from cache
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

        # Resolve and cache
        value = await resolver()
        await cache.set(cache_key, value, ttl=ttl)

        return value

    def get_selections(self) -> List[str]:
        """
        Get selected field names from GraphQL query.

        Returns:
            List of selected field names
        """
        selections = []
        for selection in self.info.selected_fields:
            selections.append(selection.name)
        return selections

    def has_selection(self, field_name: str) -> bool:
        """Check if field is selected in query."""
        return field_name in self.get_selections()


def lazy_type(type_name: str, module: str):
    """
    Create lazy type reference for circular dependencies.

    Args:
        type_name: Name of the type
        module: Module path

    Returns:
        Lazy type annotation

    Example:
        @strawberry.type
        class User:
            posts: List['Post'] = strawberry.field(
                resolver=lambda: lazy_type('Post', __name__)
            )
    """
    return strawberry.lazy(module, type_name)


def create_union(*types: Type, name: Optional[str] = None):
    """
    Create GraphQL union type.

    Args:
        *types: Types to include in union
        name: Union name (auto-generated if not provided)

    Returns:
        Union type

    Example:
        SearchResult = create_union(User, Post, Comment, name="SearchResult")
    """
    if name is None:
        name = "Union_" + "_".join(t.__name__ for t in types)

    return strawberry.union(name, types)


def create_generic_type(base_type: Type[Any], type_var: TypeVar):
    """
    Create generic GraphQL type.

    Args:
        base_type: Base type class
        type_var: Type variable

    Returns:
        Generic type

    Example:
        T = TypeVar('T')

        @strawberry.type
        class Result(Generic[T]):
            success: bool
            data: Optional[T]
            error: Optional[str]

        UserResult = create_generic_type(Result, User)
    """
    return base_type[type_var]


__all__ = [
    "GraphQLSchema",
    "ObjectType",
    "InputType",
    "InterfaceType",
    "UnionType",
    "EnumType",
    "ScalarType",
    "field",
    "graphql_type",
    "graphql_input",
    "graphql_interface",
    "graphql_enum",
    "graphql_scalar",
    "FieldResolver",
    "DateTime",
    "Date",
    "Time",
    "DecimalScalar",
    "JSON",
    "Upload",
    "lazy_type",
    "create_union",
    "create_generic_type",
    # Backward compatibility exports
    "enum",
    "type",  # Plain type alias
    "input",  # Plain input alias
    "interface",  # Plain interface alias
    "type_decorator",
    "input_decorator",
    "interface_decorator",
    "scalar",
]


class GraphQLField:
    """GraphQL field for schema definition."""
    def __init__(self, type_, resolver=None, args=None, description=None):
        self.type_ = type_
        self.resolver = resolver
        self.args = args or {}
        self.description = description

__all__ = ["GraphQLField"]



class GraphQLScalarType:
    """GraphQL scalar type."""
    def __init__(self, name):
        self.name = name
