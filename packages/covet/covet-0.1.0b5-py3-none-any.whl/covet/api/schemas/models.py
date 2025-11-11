"""
API data models for CovetPy.

This module defines the core domain models used across the API:
- User: User account and profile information
- Project: Project/workspace data and metadata

These models use Pydantic for validation, serialization, and OpenAPI schema generation.
All models include proper validation rules, type hints, and comprehensive documentation.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, validator


class User(BaseModel):
    """
    User data model.

    Represents a user account in the system with authentication, profile,
    and metadata information. Includes comprehensive validation for username
    format and type safety for all fields.

    Attributes:
        id: Unique identifier (UUID v4)
        username: Alphanumeric username (3-50 chars, underscore allowed)
        email: Valid email address
        full_name: Optional full name of the user
        is_active: Whether the user account is active
        is_admin: Whether the user has administrator privileges
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
        last_login: Most recent login timestamp
        tags: List of user tags for categorization
        metadata: Additional user metadata as key-value pairs

    Example:
        >>> user = User(
        ...     username="john_doe",
        ...     email="john@example.com",
        ...     full_name="John Doe",
        ...     tags=["developer", "team-lead"]
        ... )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique user ID")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_admin: bool = Field(default=False, description="Whether user is admin")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    tags: List[str] = Field(default_factory=list, description="User tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("username")
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.

        Ensures username contains only alphanumeric characters and underscores.
        This prevents issues with URL routing, database queries, and XSS attacks.

        Args:
            v: Username value to validate

        Returns:
            Validated username

        Raises:
            ValueError: If username contains invalid characters
        """
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v

    @validator("email")
    def validate_email_lowercase(cls, v: str) -> str:
        """
        Normalize email to lowercase.

        Ensures email addresses are stored consistently for lookup and comparison.

        Args:
            v: Email value to normalize

        Returns:
            Lowercase email address
        """
        return v.lower()

    @validator("tags")
    def validate_tags(cls, v: List[str]) -> List[str]:
        """
        Validate and normalize tags.

        Ensures tags are non-empty strings and removes duplicates.

        Args:
            v: List of tags to validate

        Returns:
            Validated and deduplicated tag list

        Raises:
            ValueError: If any tag is empty or whitespace-only
        """
        # Remove empty tags
        non_empty_tags = [tag.strip() for tag in v if tag.strip()]

        # Check for empty tags after stripping
        if len(non_empty_tags) != len(v):
            raise ValueError("Tags cannot be empty or whitespace-only")

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in non_empty_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_admin": False,
                "created_at": "2025-10-11T00:00:00",
                "updated_at": "2025-10-11T00:00:00",
                "last_login": "2025-10-11T12:00:00",
                "tags": ["developer", "team-lead"],
                "metadata": {"department": "Engineering", "location": "San Francisco"},
            }
        }


class Project(BaseModel):
    """
    Project data model.

    Represents a project or workspace in the system. Projects are owned by
    users and can contain various resources and configurations.

    Attributes:
        id: Unique identifier (UUID v4)
        name: Project name (1-100 chars)
        description: Optional project description
        owner_id: UUID of the user who owns this project
        is_active: Whether the project is active
        is_public: Whether the project is publicly accessible
        created_at: Project creation timestamp
        updated_at: Last modification timestamp
        tags: List of project tags for categorization
        metadata: Additional project metadata as key-value pairs

    Example:
        >>> project = Project(
        ...     name="My API Project",
        ...     description="RESTful API for customer management",
        ...     owner_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        ...     is_public=True,
        ...     tags=["api", "production"]
        ... )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique project ID")
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    owner_id: UUID = Field(..., description="Project owner user ID")
    is_active: bool = Field(default=True, description="Whether project is active")
    is_public: bool = Field(default=False, description="Whether project is public")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    tags: List[str] = Field(default_factory=list, description="Project tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("name")
    def validate_name(cls, v: str) -> str:
        """
        Validate project name.

        Ensures name is not just whitespace and trims leading/trailing spaces.

        Args:
            v: Project name to validate

        Returns:
            Trimmed project name

        Raises:
            ValueError: If name is empty or whitespace-only
        """
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Project name cannot be empty or whitespace-only")
        return trimmed

    @validator("description")
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and normalize description.

        Trims whitespace and converts empty descriptions to None.

        Args:
            v: Project description to validate

        Returns:
            Trimmed description or None if empty
        """
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @validator("tags")
    def validate_tags(cls, v: List[str]) -> List[str]:
        """
        Validate and normalize tags.

        Ensures tags are non-empty strings and removes duplicates.

        Args:
            v: List of tags to validate

        Returns:
            Validated and deduplicated tag list

        Raises:
            ValueError: If any tag is empty or whitespace-only
        """
        # Remove empty tags
        non_empty_tags = [tag.strip() for tag in v if tag.strip()]

        # Check for empty tags after stripping
        if len(non_empty_tags) != len(v):
            raise ValueError("Tags cannot be empty or whitespace-only")

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in non_empty_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}
        schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "name": "Customer API",
                "description": "RESTful API for customer management",
                "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                "is_active": True,
                "is_public": False,
                "created_at": "2025-10-11T00:00:00",
                "updated_at": "2025-10-11T00:00:00",
                "tags": ["api", "production"],
                "metadata": {"version": "1.0.0", "environment": "production"},
            }
        }


# Export all models
__all__ = [
    "User",
    "Project",
]
