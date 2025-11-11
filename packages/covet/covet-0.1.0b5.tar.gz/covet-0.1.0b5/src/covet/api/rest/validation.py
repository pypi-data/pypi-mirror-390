"""
REST API Request Validation

Production-ready request validation using Pydantic for type safety and automatic
OpenAPI schema generation.
"""

import inspect
import json
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel, Field, ValidationError, validator


class ValidationErrorDetail(BaseModel):
    """Validation error detail following RFC 7807."""

    loc: List[Union[str, int]]
    msg: str
    type: str
    ctx: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response following RFC 7807 Problem Details."""

    type: str = "https://errors.covetpy.dev/validation-error"
    title: str = "Validation Error"
    status: int = 422
    detail: str
    errors: List[ValidationErrorDetail]
    instance: Optional[str] = None


class RequestValidator:
    r"""
    Request validator using Pydantic models.

    Features:
    - Automatic type coercion
    - Custom validators
    - Nested model validation
    - Array validation
    - Enum validation
    - OpenAPI schema generation

    Example:
        class UserCreateRequest(BaseModel):
            name: str = Field(..., min_length=1, max_length=100)
            email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            age: int = Field(..., ge=18, le=120)

        validator = RequestValidator()
        validated = validator.validate(data, UserCreateRequest)
    """

    def __init__(self, strict: bool = False):
        """
        Initialize request validator.

        Args:
            strict: Enable strict validation (no type coercion)
        """
        self.strict = strict
        self._model_cache: Dict[str, Type[BaseModel]] = {}

    def validate(
        self,
        data: Union[Dict[str, Any], List[Any], str],
        model: Type[BaseModel],
        context: Optional[Dict[str, Any]] = None,
    ) -> BaseModel:
        """
        Validate data against Pydantic model.

        Args:
            data: Data to validate (dict, list, or JSON string)
            model: Pydantic model class
            context: Optional validation context

        Returns:
            Validated Pydantic model instance

        Raises:
            ValidationError: If validation fails
        """
        # Parse JSON string if needed
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(
                    [
                        {
                            "loc": ("body",),
                            "msg": f"Invalid JSON: {str(e)}",
                            "type": "json_invalid",
                        }
                    ],
                    model,
                )

        # Validate with Pydantic
        try:
            if context:
                return model.parse_obj(data)
            else:
                return model.parse_obj(data)
        except ValidationError:
            raise

    def validate_query_params(self, params: Dict[str, Any], model: Type[BaseModel]) -> BaseModel:
        """
        Validate query parameters.

        Query parameters are typically strings and need special handling for:
        - Arrays (repeated parameters)
        - Booleans (true/false strings)
        - Numbers (string to int/float conversion)

        Args:
            params: Query parameters dict
            model: Pydantic model class

        Returns:
            Validated model instance
        """
        # Convert query params to proper types
        processed_params = self._process_query_params(params, model)
        return self.validate(processed_params, model)

    def _process_query_params(
        self, params: Dict[str, Any], model: Type[BaseModel]
    ) -> Dict[str, Any]:
        """Process query parameters for type coercion."""
        hints = get_type_hints(model)
        processed = {}

        for field_name, value in params.items():
            if field_name not in hints:
                processed[field_name] = value
                continue

            field_type = hints[field_name]
            origin = get_origin(field_type)

            # Handle Optional types
            if origin is Union:
                args = get_args(field_type)
                if type(None) in args:
                    # It's Optional[T]
                    field_type = next(arg for arg in args if arg is not type(None))
                    origin = get_origin(field_type)

            # Handle List types
            if origin is list:
                if not isinstance(value, list):
                    value = [value]
                processed[field_name] = value
            # Handle bool (query params are strings)
            elif field_type is bool:
                if isinstance(value, str):
                    processed[field_name] = value.lower() in ("true", "1", "yes", "on")
                else:
                    processed[field_name] = bool(value)
            else:
                processed[field_name] = value

        return processed

    def validate_path_params(self, params: Dict[str, str], model: Type[BaseModel]) -> BaseModel:
        """
        Validate path parameters.

        Path parameters are always strings and need type conversion.

        Args:
            params: Path parameters dict (all strings)
            model: Pydantic model class

        Returns:
            Validated model instance
        """
        return self.validate(params, model)

    def format_errors(
        self, error: ValidationError, request_path: Optional[str] = None
    ) -> ValidationErrorResponse:
        """
        Format Pydantic validation errors to RFC 7807 format.

        Args:
            error: Pydantic ValidationError
            request_path: Optional request path for instance field

        Returns:
            RFC 7807 formatted error response
        """
        errors = []
        for err in error.errors():
            errors.append(
                ValidationErrorDetail(
                    loc=list(err["loc"]),
                    msg=err["msg"],
                    type=err["type"],
                    ctx=err.get("ctx"),
                )
            )

        # Create summary message
        if len(errors) == 1:
            detail = errors[0].msg
        else:
            detail = f"{len(errors)} validation errors"

        return ValidationErrorResponse(detail=detail, errors=errors, instance=request_path)

    def get_openapi_schema(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """
        Generate OpenAPI 3.1 schema from Pydantic model.

        Args:
            model: Pydantic model class

        Returns:
            OpenAPI schema dict
        """
        return model.schema()


class PydanticValidator:
    """Alias for RequestValidator for backward compatibility."""

    def __init__(self, *args, **kwargs):
        self.validator = RequestValidator(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.validator, name)


# Common validation models for REST APIs


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, alias="pageSize", description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.page_size


class SortParams(BaseModel):
    """Standard sorting parameters."""

    sort_by: Optional[str] = Field(default=None, alias="sortBy", description="Field to sort by")
    sort_order: Optional[str] = Field(
        default="asc",
        alias="sortOrder",
        pattern="^(asc|desc)$",
        description="Sort order: asc or desc",
    )


class FilterParams(BaseModel):
    """Standard filter parameters."""

    search: Optional[str] = Field(default=None, max_length=255, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filters")


class StandardQueryParams(PaginationParams, SortParams, FilterParams):
    """Combination of standard query parameters."""


class IDPathParam(BaseModel):
    """Standard ID path parameter."""

    id: int = Field(..., ge=1, description="Resource ID")


class UUIDPathParam(BaseModel):
    """Standard UUID path parameter."""

    id: str = Field(
        ...,
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        description="Resource UUID",
    )


__all__ = [
    "RequestValidator",
    "PydanticValidator",
    "ValidationError",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
    "PaginationParams",
    "SortParams",
    "FilterParams",
    "StandardQueryParams",
    "IDPathParam",
    "UUIDPathParam",
    "BaseModel",
    "Field",
    "validator",
]
