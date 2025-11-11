"""
API schemas package for CovetPy.

This package provides comprehensive Pydantic schemas for API requests and responses.

Modules:
    base: Base response classes (SuccessResponse, ErrorResponse, etc.)
    models: Domain models (User, Project)
    requests: Request validation schemas (UserCreateRequest, ProjectCreateRequest, etc.)
    responses: Response schemas (UserResponse, ProjectListResponse, etc.)

Usage:
    >>> from covet.api.schemas import User, UserCreateRequest, UserResponse
    >>> from covet.api.schemas import SuccessResponse, ErrorResponse
    >>> from covet.api.schemas import PaginatedResponse, PaginationMeta

Example - Creating a user request:
    >>> from covet.api.schemas import UserCreateRequest
    >>> request = UserCreateRequest(
    ...     username="john_doe",
    ...     email="john@example.com",
    ...     password="SecurePass123!",
    ...     full_name="John Doe"
    ... )

Example - Creating a success response:
    >>> from covet.api.schemas import User, UserResponse
    >>> user = User(username="john_doe", email="john@example.com")
    >>> response = UserResponse(
    ...     data=user,
    ...     message="User created successfully"
    ... )

Example - Creating a paginated response:
    >>> from covet.api.schemas import User, UserListResponse, PaginationMeta
    >>> users = [User(username="john", email="john@example.com")]
    >>> pagination = PaginationMeta(
    ...     page=1, limit=20, total=1,
    ...     total_pages=1, has_next=False, has_prev=False
    ... )
    >>> response = UserListResponse(data=users, pagination=pagination)
"""

# Import base response classes
from .base import (
    BaseAPIResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    SuccessResponse,
    ValidationErrorResponse,
)

# Import domain models
from .models import (
    Project,
    User,
)

# Import request schemas
from .requests import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    UserCreateRequest,
    UserUpdateRequest,
)

# Import response schemas
from .responses import (
    ProjectListResponse,
    ProjectResponse,
    UserListResponse,
    UserResponse,
)

# Define public API
__all__ = [
    # Base response classes
    "BaseAPIResponse",
    "SuccessResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "PaginationMeta",
    "PaginatedResponse",
    # Domain models
    "User",
    "Project",
    # Request schemas
    "UserCreateRequest",
    "UserUpdateRequest",
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
    # Response schemas
    "UserResponse",
    "UserListResponse",
    "ProjectResponse",
    "ProjectListResponse",
]

# Package metadata
__version__ = "1.0.0"
__author__ = "CovetPy Team"
__description__ = "API schemas for CovetPy framework"
