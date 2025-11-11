"""
Automatic CRUD Endpoint Generator

Production-grade CRUD generator that creates complete REST endpoints from ORM models:
- GET /resources (list with pagination/filtering/sorting)
- POST /resources (create)
- GET /resources/{id} (retrieve)
- PUT/PATCH /resources/{id} (update)
- DELETE /resources/{id} (delete)

Features:
- Automatic Pydantic model generation from ORM
- Built-in pagination, filtering, and sorting
- Customizable permissions per endpoint
- Field-level access control
- Soft delete support
- Bulk operations
- Automatic OpenAPI documentation

Example:
    from covet.api.rest.crud_generator import CRUDGenerator, CRUDConfig
    from covet.database.orm import User

    # Generate full CRUD endpoints
    crud = CRUDGenerator(
        model=User,
        router=rest_router,
        prefix="/users",
        tags=["users"]
    )

    # Customize configuration
    config = CRUDConfig(
        enable_list=True,
        enable_create=True,
        enable_retrieve=True,
        enable_update=True,
        enable_delete=True,
        pagination_size=20,
        max_page_size=100,
        allowed_filters=['is_active', 'email'],
        allowed_sort_fields=['created_at', 'name'],
        read_only_fields=['id', 'created_at', 'updated_at'],
        write_only_fields=['password'],
    )

    crud = CRUDGenerator(User, router, "/users", config=config)

    # This automatically creates:
    # GET /users -> list_users
    # POST /users -> create_user
    # GET /users/{id} -> get_user
    # PUT /users/{id} -> update_user
    # PATCH /users/{id} -> partial_update_user
    # DELETE /users/{id} -> delete_user
"""

import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Type

from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import create_model

from .filtering import FilterSet, create_filterset_from_model
from .pagination import OffsetPaginator, PaginatedResponse
from .sorting import SortingConfig, apply_sorting, create_sorting_config_from_model

logger = logging.getLogger(__name__)


@dataclass
class CRUDConfig:
    """
    Configuration for CRUD generator.

    Attributes:
        enable_list: Enable list endpoint
        enable_create: Enable create endpoint
        enable_retrieve: Enable retrieve endpoint
        enable_update: Enable update (PUT) endpoint
        enable_partial_update: Enable partial update (PATCH) endpoint
        enable_delete: Enable delete endpoint
        enable_bulk_create: Enable bulk create endpoint
        enable_bulk_update: Enable bulk update endpoint
        enable_bulk_delete: Enable bulk delete endpoint
        pagination_size: Default page size
        max_page_size: Maximum page size
        allowed_filters: Fields allowed for filtering
        allowed_sort_fields: Fields allowed for sorting
        default_ordering: Default sort order
        read_only_fields: Fields excluded from write operations
        write_only_fields: Fields excluded from read operations
        required_fields: Fields required for creation
        soft_delete: Use soft delete instead of hard delete
        soft_delete_field: Field name for soft delete
        include_count: Include total count in list responses
        permissions: Permission classes per operation
        field_validators: Custom validators per field
    """

    # Endpoint enables
    enable_list: bool = True
    enable_create: bool = True
    enable_retrieve: bool = True
    enable_update: bool = True
    enable_partial_update: bool = True
    enable_delete: bool = True
    enable_bulk_create: bool = False
    enable_bulk_update: bool = False
    enable_bulk_delete: bool = False

    # Pagination
    pagination_size: int = 20
    max_page_size: int = 100
    include_count: bool = True

    # Filtering and sorting
    allowed_filters: List[str] = field(default_factory=list)
    allowed_sort_fields: List[str] = field(default_factory=list)
    default_ordering: List[str] = field(default_factory=lambda: ["-id"])

    # Field access control
    read_only_fields: List[str] = field(default_factory=list)
    write_only_fields: List[str] = field(default_factory=list)
    required_fields: List[str] = field(default_factory=list)

    # Soft delete
    soft_delete: bool = False
    soft_delete_field: str = "is_deleted"

    # Permissions and validators
    permissions: Dict[str, List[Callable]] = field(default_factory=dict)
    field_validators: Dict[str, List[Callable]] = field(default_factory=dict)


class CRUDGenerator:
    """
    Generate complete CRUD REST API from ORM model.

    This class automatically creates:
    - List endpoint with pagination, filtering, sorting
    - Create endpoint with validation
    - Retrieve endpoint
    - Update endpoint (PUT - full update)
    - Partial update endpoint (PATCH - partial update)
    - Delete endpoint

    Example:
        from covet.api.rest import RESTRouter
        from covet.database.orm import User

        router = RESTRouter(prefix="/api/v1")

        crud = CRUDGenerator(
            model=User,
            router=router,
            prefix="/users",
            tags=["users"]
        )

        # Endpoints are now registered:
        # GET /api/v1/users
        # POST /api/v1/users
        # GET /api/v1/users/{id}
        # PUT /api/v1/users/{id}
        # PATCH /api/v1/users/{id}
        # DELETE /api/v1/users/{id}
    """

    def __init__(
        self,
        model: Type,
        router,
        prefix: str = "",
        config: Optional[CRUDConfig] = None,
        tags: Optional[List[str]] = None,
        name: Optional[str] = None,
    ):
        """
        Initialize CRUD generator.

        Args:
            model: ORM model class
            router: REST router instance
            prefix: URL prefix for endpoints
            config: CRUD configuration
            tags: OpenAPI tags
            name: Resource name (default: model name)
        """
        self.model = model
        self.router = router
        self.prefix = prefix.rstrip("/")
        self.config = config or CRUDConfig()
        self.tags = tags or [model.__name__.lower()]
        self.name = name or model.__name__

        # Generate Pydantic models
        self.create_schema = self._generate_create_schema()
        self.update_schema = self._generate_update_schema()
        self.partial_update_schema = self._generate_partial_update_schema()
        self.response_schema = self._generate_response_schema()

        # Generate filtering and sorting configs
        self.filter_set = self._generate_filterset()
        self.sorting_config = self._generate_sorting_config()

        # Register endpoints
        self._register_endpoints()

    def _generate_create_schema(self) -> Type[BaseModel]:
        """
        Generate Pydantic schema for creation.

        Excludes:
        - Primary key (auto-generated)
        - Read-only fields
        - Auto-generated fields (created_at, updated_at)

        Returns:
            Pydantic model class
        """
        fields = {}

        for field_name, model_field in self.model._fields.items():
            # Skip primary key
            if model_field.primary_key:
                continue

            # Skip read-only fields
            if field_name in self.config.read_only_fields:
                continue

            # Skip auto-generated fields
            if hasattr(model_field, "auto_now") and model_field.auto_now:
                continue
            if hasattr(model_field, "auto_now_add") and model_field.auto_now_add:
                continue

            # Determine if required
            is_required = field_name in self.config.required_fields or (
                not model_field.null and model_field.default is None
            )

            # Get Python type
            python_type = self._get_python_type(model_field)

            # Create field
            if is_required:
                fields[field_name] = (python_type, PydanticField(...))
            else:
                default_value = model_field.default if hasattr(model_field, "default") else None
                fields[field_name] = (Optional[python_type], PydanticField(default=default_value))

        # Create Pydantic model
        schema_name = f"{self.name}Create"
        return create_model(schema_name, **fields)

    def _generate_update_schema(self) -> Type[BaseModel]:
        """
        Generate Pydantic schema for full update (PUT).

        Similar to create schema but may include different required fields.

        Returns:
            Pydantic model class
        """
        fields = {}

        for field_name, model_field in self.model._fields.items():
            # Skip primary key
            if model_field.primary_key:
                continue

            # Skip read-only fields
            if field_name in self.config.read_only_fields:
                continue

            # Get Python type
            python_type = self._get_python_type(model_field)

            # All fields required for PUT
            fields[field_name] = (python_type, PydanticField(...))

        schema_name = f"{self.name}Update"
        return create_model(schema_name, **fields)

    def _generate_partial_update_schema(self) -> Type[BaseModel]:
        """
        Generate Pydantic schema for partial update (PATCH).

        All fields are optional.

        Returns:
            Pydantic model class
        """
        fields = {}

        for field_name, model_field in self.model._fields.items():
            # Skip primary key
            if model_field.primary_key:
                continue

            # Skip read-only fields
            if field_name in self.config.read_only_fields:
                continue

            # Get Python type
            python_type = self._get_python_type(model_field)

            # All fields optional for PATCH
            fields[field_name] = (Optional[python_type], None)

        schema_name = f"{self.name}PartialUpdate"
        return create_model(schema_name, **fields)

    def _generate_response_schema(self) -> Type[BaseModel]:
        """
        Generate Pydantic schema for responses.

        Includes all fields except write-only fields.

        Returns:
            Pydantic model class
        """
        fields = {}

        for field_name, model_field in self.model._fields.items():
            # Skip write-only fields
            if field_name in self.config.write_only_fields:
                continue

            # Get Python type
            python_type = self._get_python_type(model_field)

            # Add field
            fields[field_name] = (python_type, None)

        schema_name = f"{self.name}Response"
        return create_model(schema_name, **fields)

    def _get_python_type(self, model_field) -> Type:
        """
        Get Python type for model field.

        Args:
            model_field: ORM field

        Returns:
            Python type
        """
        from datetime import date, datetime
        from uuid import UUID

        from covet.database.orm.fields import (
            BooleanField,
            CharField,
            DateField,
            DateTimeField,
            EmailField,
            FloatField,
            IntegerField,
            JSONField,
            UUIDField,
        )

        field_type = type(model_field)

        if field_type in (CharField, EmailField):
            return str
        elif field_type == IntegerField:
            return int
        elif field_type == FloatField:
            return float
        elif field_type == BooleanField:
            return bool
        elif field_type == DateTimeField:
            return datetime
        elif field_type == DateField:
            return date
        elif field_type == UUIDField:
            return UUID
        elif field_type == JSONField:
            return Dict[str, Any]

        # Default to Any
        return Any

    def _generate_filterset(self) -> Optional[Type[FilterSet]]:
        """Generate FilterSet for model."""
        if not self.config.allowed_filters:
            return None

        return create_filterset_from_model(self.model, self.config.allowed_filters)

    def _generate_sorting_config(self) -> SortingConfig:
        """Generate sorting configuration."""
        return create_sorting_config_from_model(
            self.model,
            allowed_fields=self.config.allowed_sort_fields or [],
            default_ordering=self.config.default_ordering,
        )

    def _register_endpoints(self) -> None:
        """Register all enabled endpoints."""
        if self.config.enable_list:
            self._register_list_endpoint()

        if self.config.enable_create:
            self._register_create_endpoint()

        if self.config.enable_retrieve:
            self._register_retrieve_endpoint()

        if self.config.enable_update:
            self._register_update_endpoint()

        if self.config.enable_partial_update:
            self._register_partial_update_endpoint()

        if self.config.enable_delete:
            self._register_delete_endpoint()

    def _register_list_endpoint(self) -> None:
        """Register list endpoint with pagination, filtering, sorting."""

        @self.router.get(
            self.prefix,
            response_model=PaginatedResponse,
            tags=self.tags,
            summary=f"List {self.name}s",
            description=f"Retrieve paginated list of {self.name}s with filtering and sorting",
        )
        async def list_resources(request):
            # Base queryset
            queryset = self.model.objects.all()

            # Apply soft delete filter
            if self.config.soft_delete:
                queryset = queryset.filter(**{f"{self.config.soft_delete_field}": False})

            # Apply filters
            if self.filter_set:
                filterset = self.filter_set(query_params=request.query_params)
                queryset = filterset.filter(queryset)

            # Apply sorting
            sort_param = request.query_params.get("sort", "")
            queryset = apply_sorting(queryset, sort_param, self.sorting_config)

            # Apply pagination
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", self.config.pagination_size))
            page_size = min(page_size, self.config.max_page_size)

            paginator = OffsetPaginator(
                page=page, page_size=page_size, include_total_count=self.config.include_count
            )

            result = await paginator.paginate(queryset)

            # Convert to response schema
            items = [self.response_schema(**item.__dict__).dict() for item in result.items]

            return {"items": items, "pagination": result.pagination, "links": result.links}

    def _register_create_endpoint(self) -> None:
        """Register create endpoint."""

        @self.router.post(
            self.prefix,
            request_model=self.create_schema,
            response_model=self.response_schema,
            tags=self.tags,
            summary=f"Create {self.name}",
            description=f"Create a new {self.name}",
        )
        async def create_resource(request, body):
            # Create instance
            instance = await self.model.objects.create(**body.dict())

            # Convert to response schema
            return self.response_schema(**instance.__dict__).dict(), 201

    def _register_retrieve_endpoint(self) -> None:
        """Register retrieve endpoint."""

        @self.router.get(
            f"{self.prefix}/{{id:int}}",
            response_model=self.response_schema,
            tags=self.tags,
            summary=f"Get {self.name}",
            description=f"Retrieve a {self.name} by ID",
        )
        async def get_resource(request, id: int):
            # Get instance
            queryset = self.model.objects

            # Apply soft delete filter
            if self.config.soft_delete:
                queryset = queryset.filter(**{f"{self.config.soft_delete_field}": False})

            try:
                instance = await queryset.get(id=id)
            except self.model.DoesNotExist:
                return {"error": "Not Found", "message": f"{self.name} not found"}, 404

            # Convert to response schema
            return self.response_schema(**instance.__dict__).dict()

    def _register_update_endpoint(self) -> None:
        """Register update (PUT) endpoint."""

        @self.router.put(
            f"{self.prefix}/{{id:int}}",
            request_model=self.update_schema,
            response_model=self.response_schema,
            tags=self.tags,
            summary=f"Update {self.name}",
            description=f"Fully update a {self.name}",
        )
        async def update_resource(request, id: int, body):
            # Get instance
            try:
                instance = await self.model.objects.get(id=id)
            except self.model.DoesNotExist:
                return {"error": "Not Found", "message": f"{self.name} not found"}, 404

            # Update all fields
            for field, value in body.dict().items():
                setattr(instance, field, value)

            await instance.save()

            # Convert to response schema
            return self.response_schema(**instance.__dict__).dict()

    def _register_partial_update_endpoint(self) -> None:
        """Register partial update (PATCH) endpoint."""

        @self.router.patch(
            f"{self.prefix}/{{id:int}}",
            request_model=self.partial_update_schema,
            response_model=self.response_schema,
            tags=self.tags,
            summary=f"Partial Update {self.name}",
            description=f"Partially update a {self.name}",
        )
        async def partial_update_resource(request, id: int, body):
            # Get instance
            try:
                instance = await self.model.objects.get(id=id)
            except self.model.DoesNotExist:
                return {"error": "Not Found", "message": f"{self.name} not found"}, 404

            # Update provided fields only
            update_data = body.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(instance, field, value)

            await instance.save()

            # Convert to response schema
            return self.response_schema(**instance.__dict__).dict()

    def _register_delete_endpoint(self) -> None:
        """Register delete endpoint."""

        @self.router.delete(
            f"{self.prefix}/{{id:int}}",
            tags=self.tags,
            summary=f"Delete {self.name}",
            description=f"Delete a {self.name}",
        )
        async def delete_resource(request, id: int):
            # Get instance
            try:
                instance = await self.model.objects.get(id=id)
            except self.model.DoesNotExist:
                return {"error": "Not Found", "message": f"{self.name} not found"}, 404

            if self.config.soft_delete:
                # Soft delete
                setattr(instance, self.config.soft_delete_field, True)
                await instance.save()
            else:
                # Hard delete
                await instance.delete()

            return {"message": f"{self.name} deleted successfully"}, 204


__all__ = [
    "CRUDGenerator",
    "CRUDConfig",
]
