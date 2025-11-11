"""
API response schemas for CovetPy.

This module defines specific response schemas for API endpoints:
- UserResponse: Single user response
- UserListResponse: Paginated list of users
- ProjectResponse: Single project response
- ProjectListResponse: Paginated list of projects

All response schemas inherit from the base response classes and provide
type-safe wrappers for API data.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .base import PaginatedResponse, SuccessResponse
from .models import Project, User


class UserResponse(SuccessResponse[User]):
    """
    Response schema for single user.

    Returns a single user object wrapped in a success response with
    timestamp and optional message.

    Attributes:
        data: User object
        success: Always True
        message: Optional success message
        timestamp: Response generation timestamp

    Example:
        >>> from .models import User
        >>> user = User(username="john_doe", email="john@example.com")
        >>> response = UserResponse(
        ...     data=user,
        ...     message="User retrieved successfully"
        ... )
    """

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "success": True,
                "message": "User retrieved successfully",
                "timestamp": "2025-10-11T00:00:00",
                "data": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "john_doe",
                    "email": "john@example.com",
                    "full_name": "John Doe",
                    "is_active": True,
                    "is_admin": False,
                    "created_at": "2025-10-11T00:00:00",
                    "updated_at": "2025-10-11T00:00:00",
                    "last_login": "2025-10-11T12:00:00",
                    "tags": ["developer"],
                    "metadata": {},
                },
            }
        }


class UserListResponse(PaginatedResponse[User]):
    """
    Response schema for list of users.

    Returns a paginated list of user objects with pagination metadata.

    Attributes:
        data: List of User objects for current page
        pagination: Pagination metadata
        success: Always True
        message: Optional success message
        timestamp: Response generation timestamp

    Example:
        >>> from .models import User
        >>> from .base import PaginationMeta
        >>> users = [
        ...     User(username="john", email="john@example.com"),
        ...     User(username="jane", email="jane@example.com")
        ... ]
        >>> pagination = PaginationMeta(
        ...     page=1, limit=20, total=2,
        ...     total_pages=1, has_next=False, has_prev=False
        ... )
        >>> response = UserListResponse(
        ...     data=users,
        ...     pagination=pagination,
        ...     message="Users retrieved successfully"
        ... )
    """

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "success": True,
                "message": "Users retrieved successfully",
                "timestamp": "2025-10-11T00:00:00",
                "data": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john_doe",
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "is_active": True,
                        "is_admin": False,
                        "created_at": "2025-10-11T00:00:00",
                        "updated_at": "2025-10-11T00:00:00",
                        "last_login": None,
                        "tags": ["developer"],
                        "metadata": {},
                    },
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "username": "jane_doe",
                        "email": "jane@example.com",
                        "full_name": "Jane Doe",
                        "is_active": True,
                        "is_admin": True,
                        "created_at": "2025-10-11T00:00:00",
                        "updated_at": "2025-10-11T00:00:00",
                        "last_login": "2025-10-11T12:00:00",
                        "tags": ["admin", "developer"],
                        "metadata": {},
                    },
                ],
                "pagination": {
                    "page": 1,
                    "limit": 20,
                    "total": 2,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False,
                },
            }
        }


class ProjectResponse(SuccessResponse[Project]):
    """
    Response schema for single project.

    Returns a single project object wrapped in a success response with
    timestamp and optional message.

    Attributes:
        data: Project object
        success: Always True
        message: Optional success message
        timestamp: Response generation timestamp

    Example:
        >>> from .models import Project
        >>> from uuid import uuid4
        >>> project = Project(
        ...     name="My Project",
        ...     description="A sample project",
        ...     owner_id=uuid4()
        ... )
        >>> response = ProjectResponse(
        ...     data=project,
        ...     message="Project retrieved successfully"
        ... )
    """

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "success": True,
                "message": "Project retrieved successfully",
                "timestamp": "2025-10-11T00:00:00",
                "data": {
                    "id": "660e8400-e29b-41d4-a716-446655440000",
                    "name": "Customer API",
                    "description": "RESTful API for customer management",
                    "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                    "is_active": True,
                    "is_public": False,
                    "created_at": "2025-10-11T00:00:00",
                    "updated_at": "2025-10-11T00:00:00",
                    "tags": ["api", "production"],
                    "metadata": {"version": "1.0.0"},
                },
            }
        }


class ProjectListResponse(PaginatedResponse[Project]):
    """
    Response schema for list of projects.

    Returns a paginated list of project objects with pagination metadata.

    Attributes:
        data: List of Project objects for current page
        pagination: Pagination metadata
        success: Always True
        message: Optional success message
        timestamp: Response generation timestamp

    Example:
        >>> from .models import Project
        >>> from .base import PaginationMeta
        >>> from uuid import uuid4
        >>> owner_id = uuid4()
        >>> projects = [
        ...     Project(name="Project A", owner_id=owner_id),
        ...     Project(name="Project B", owner_id=owner_id)
        ... ]
        >>> pagination = PaginationMeta(
        ...     page=1, limit=20, total=2,
        ...     total_pages=1, has_next=False, has_prev=False
        ... )
        >>> response = ProjectListResponse(
        ...     data=projects,
        ...     pagination=pagination,
        ...     message="Projects retrieved successfully"
        ... )
    """

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "success": True,
                "message": "Projects retrieved successfully",
                "timestamp": "2025-10-11T00:00:00",
                "data": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440000",
                        "name": "Customer API",
                        "description": "RESTful API for customer management",
                        "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                        "is_active": True,
                        "is_public": False,
                        "created_at": "2025-10-11T00:00:00",
                        "updated_at": "2025-10-11T00:00:00",
                        "tags": ["api", "production"],
                        "metadata": {},
                    },
                    {
                        "id": "770e8400-e29b-41d4-a716-446655440001",
                        "name": "Analytics Dashboard",
                        "description": "Internal analytics dashboard",
                        "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                        "is_active": True,
                        "is_public": False,
                        "created_at": "2025-10-11T00:00:00",
                        "updated_at": "2025-10-11T00:00:00",
                        "tags": ["dashboard", "internal"],
                        "metadata": {},
                    },
                ],
                "pagination": {
                    "page": 1,
                    "limit": 20,
                    "total": 2,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False,
                },
            }
        }


# Export all response schemas
__all__ = [
    "UserResponse",
    "UserListResponse",
    "ProjectResponse",
    "ProjectListResponse",
]
