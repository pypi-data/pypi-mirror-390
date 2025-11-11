"""
Base API response classes for CovetPy.

This module provides foundational response schemas that are used throughout the API:
- BaseAPIResponse: Common fields for all responses (success, message, timestamp)
- SuccessResponse: Generic response wrapper for successful operations with data
- ErrorResponse: Standardized error response with error codes and details
- ValidationErrorResponse: Specialized error response for validation failures
- PaginationMeta: Metadata for paginated responses
- PaginatedResponse: Generic response wrapper for paginated data

All response classes use Pydantic for validation and serialization.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseAPIResponse(BaseModel):
    """
    Base API response with common fields.

    All API responses inherit from this class to provide consistent structure
    across the entire API surface.

    Attributes:
        success: Boolean indicating if the request was successful
        message: Optional human-readable message providing context
        timestamp: UTC timestamp of when the response was generated
    """

    success: bool = Field(default=True, description="Whether request was successful")
    message: Optional[str] = Field(default=None, description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "timestamp": "2025-10-11T00:00:00",
            }
        }


class SuccessResponse(BaseAPIResponse, Generic[T]):
    """
    Successful API response with data payload.

    This generic class wraps successful responses with strongly-typed data.
    The type parameter T specifies the type of data being returned.

    Attributes:
        data: The response payload of type T
        success: Always True for success responses

    Example:
        >>> from .models import User
        >>> response = SuccessResponse[User](
        ...     data=User(username="john", email="john@example.com"),
        ...     message="User retrieved successfully"
        ... )
    """

    data: T = Field(..., description="Response data")
    success: bool = Field(default=True)

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class ErrorResponse(BaseAPIResponse):
    """
    Error API response.

    Provides standardized error reporting across the API with error codes
    and optional detailed information for debugging.

    Attributes:
        error: Machine-readable error code (e.g., "USER_NOT_FOUND")
        details: Optional dictionary with additional error context
        success: Always False for error responses

    Example:
        >>> response = ErrorResponse(
        ...     error="VALIDATION_ERROR",
        ...     message="Invalid input provided",
        ...     details={"field": "email", "issue": "invalid format"}
        ... )
    """

    error: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    success: bool = Field(default=False)

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        schema_extra = {
            "example": {
                "success": False,
                "error": "RESOURCE_NOT_FOUND",
                "message": "The requested resource was not found",
                "details": {"resource_id": "123", "resource_type": "user"},
                "timestamp": "2025-10-11T00:00:00",
            }
        }


class ValidationErrorResponse(BaseAPIResponse):
    """
    Validation error response.

    Specialized error response for validation failures, providing detailed
    information about each validation error that occurred.

    Attributes:
        error: Always "VALIDATION_ERROR"
        validation_errors: List of validation errors with field and message
        success: Always False

    Example:
        >>> response = ValidationErrorResponse(
        ...     validation_errors=[
        ...         {"field": "email", "message": "Invalid email format"},
        ...         {"field": "password", "message": "Password too short"}
        ...     ]
        ... )
    """

    error: str = Field(default="VALIDATION_ERROR")
    validation_errors: List[Dict[str, Any]] = Field(..., description="List of validation errors")
    success: bool = Field(default=False)

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "validation_errors": [
                    {"field": "email", "message": "Invalid email format", "code": "INVALID_FORMAT"}
                ],
                "timestamp": "2025-10-11T00:00:00",
            }
        }


class PaginationMeta(BaseModel):
    """
    Pagination metadata.

    Provides comprehensive pagination information for paginated API responses.
    Includes current page, limits, totals, and navigation indicators.

    Attributes:
        page: Current page number (1-indexed)
        limit: Number of items per page (1-100)
        total: Total number of items across all pages
        total_pages: Total number of pages
        has_next: Whether there is a next page available
        has_prev: Whether there is a previous page available

    Example:
        >>> meta = PaginationMeta(
        ...     page=2,
        ...     limit=20,
        ...     total=150,
        ...     total_pages=8,
        ...     has_next=True,
        ...     has_prev=True
        ... )
    """

    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "page": 1,
                "limit": 20,
                "total": 100,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False,
            }
        }


class PaginatedResponse(BaseAPIResponse, Generic[T]):
    """
    Paginated API response.

    Generic response wrapper for paginated data. Combines a list of items
    with pagination metadata.

    Attributes:
        data: List of items of type T for the current page
        pagination: Pagination metadata
        success: Always True for successful paginated responses

    Example:
        >>> from .models import User
        >>> response = PaginatedResponse[User](
        ...     data=[user1, user2, user3],
        ...     pagination=PaginationMeta(
        ...         page=1, limit=3, total=10,
        ...         total_pages=4, has_next=True, has_prev=False
        ...     )
        ... )
    """

    data: List[T] = Field(..., description="Page of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    success: bool = Field(default=True)

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


# Export all response classes
__all__ = [
    "BaseAPIResponse",
    "SuccessResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "PaginationMeta",
    "PaginatedResponse",
]
