"""
API request schemas for CovetPy.

This module defines request schemas for API operations:
- UserCreateRequest: Schema for creating new users
- UserUpdateRequest: Schema for updating existing users
- ProjectCreateRequest: Schema for creating new projects
- ProjectUpdateRequest: Schema for updating existing projects

All request schemas include comprehensive validation rules to ensure data
integrity and security before processing.
"""

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserCreateRequest(BaseModel):
    """
    Request schema for creating a user.

    Validates all required fields for user creation including strong password
    requirements and proper email format.

    Attributes:
        username: Alphanumeric username (3-50 chars, underscore allowed)
        email: Valid email address
        password: Secure password (8-100 chars with complexity requirements)
        full_name: Optional full name

    Password Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

    Example:
        >>> request = UserCreateRequest(
        ...     username="john_doe",
        ...     email="john@example.com",
        ...     password="SecurePass123!",
        ...     full_name="John Doe"
        ... )
    """

    username: str = Field(
        ..., min_length=3, max_length=50, description="Username (alphanumeric + underscore)"
    )
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 chars with complexity requirements)",
    )
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")

    @validator("username")
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.

        Ensures username contains only alphanumeric characters and underscores.
        Prevents special characters that could cause security or routing issues.

        Args:
            v: Username to validate

        Returns:
            Validated username

        Raises:
            ValueError: If username contains invalid characters
        """
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v

    @validator("password")
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.

        Enforces strong password requirements to protect user accounts.
        Checks for:
        - Minimum length of 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            v: Password to validate

        Returns:
            Validated password

        Raises:
            ValueError: If password doesn't meet security requirements
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")

        # Check for special characters
        special_chars = r"!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError(
                "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
            )

        return v

    @validator("email")
    def validate_email_lowercase(cls, v: str) -> str:
        """
        Normalize email to lowercase.

        Args:
            v: Email to normalize

        Returns:
            Lowercase email
        """
        return v.lower()

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe",
            }
        }


class UserUpdateRequest(BaseModel):
    """
    Request schema for updating a user.

    All fields are optional to allow partial updates. Only provided fields
    will be updated.

    Attributes:
        email: Optional new email address
        full_name: Optional new full name
        is_active: Optional active status

    Example:
        >>> request = UserUpdateRequest(
        ...     email="newemail@example.com",
        ...     full_name="John Updated Doe"
        ... )
    """

    email: Optional[EmailStr] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    is_active: Optional[bool] = Field(None, description="Whether user is active")

    @validator("email")
    def validate_email_lowercase(cls, v: Optional[str]) -> Optional[str]:
        """
        Normalize email to lowercase.

        Args:
            v: Email to normalize

        Returns:
            Lowercase email or None
        """
        return v.lower() if v else None

    @validator("full_name")
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and normalize full name.

        Args:
            v: Full name to validate

        Returns:
            Trimmed full name or None

        Raises:
            ValueError: If full name is whitespace-only
        """
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Full name cannot be empty or whitespace-only")
        return trimmed

    class Config:
        """Pydantic configuration."""

        schema_extra = {
            "example": {
                "email": "updated@example.com",
                "full_name": "John Updated Doe",
                "is_active": True,
            }
        }


class ProjectCreateRequest(BaseModel):
    """
    Request schema for creating a project.

    Validates all required fields for project creation.

    Attributes:
        name: Project name (1-100 chars, required)
        description: Optional project description (max 1000 chars)
        is_public: Whether project is publicly accessible (default: False)
        tags: List of tags for categorization

    Example:
        >>> request = ProjectCreateRequest(
        ...     name="My API Project",
        ...     description="RESTful API for customer management",
        ...     is_public=True,
        ...     tags=["api", "production"]
        ... )
    """

    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    is_public: bool = Field(default=False, description="Whether project is publicly accessible")
    tags: List[str] = Field(default_factory=list, description="Project tags")

    @validator("name")
    def validate_name(cls, v: str) -> str:
        """
        Validate project name.

        Ensures name is not just whitespace.

        Args:
            v: Project name to validate

        Returns:
            Trimmed project name

        Raises:
            ValueError: If name is whitespace-only
        """
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Project name cannot be empty or whitespace-only")
        return trimmed

    @validator("description")
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and normalize description.

        Args:
            v: Description to validate

        Returns:
            Trimmed description or None
        """
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @validator("tags")
    def validate_tags(cls, v: List[str]) -> List[str]:
        """
        Validate and normalize tags.

        Args:
            v: List of tags to validate

        Returns:
            Validated and deduplicated tag list

        Raises:
            ValueError: If any tag is empty or whitespace-only
        """
        # Remove empty tags and validate
        non_empty_tags = []
        for tag in v:
            stripped = tag.strip()
            if not stripped:
                raise ValueError("Tags cannot be empty or whitespace-only")
            non_empty_tags.append(stripped)

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

        schema_extra = {
            "example": {
                "name": "Customer API",
                "description": "RESTful API for customer management",
                "is_public": False,
                "tags": ["api", "production"],
            }
        }


class ProjectUpdateRequest(BaseModel):
    """
    Request schema for updating a project.

    All fields are optional to allow partial updates. Only provided fields
    will be updated.

    Attributes:
        name: Optional new project name
        description: Optional new description
        is_active: Optional active status
        is_public: Optional public visibility status
        tags: Optional new tag list

    Example:
        >>> request = ProjectUpdateRequest(
        ...     name="Updated Project Name",
        ...     is_public=True,
        ...     tags=["api", "staging"]
        ... )
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    is_active: Optional[bool] = Field(None, description="Whether project is active")
    is_public: Optional[bool] = Field(None, description="Whether project is publicly accessible")
    tags: Optional[List[str]] = Field(None, description="Project tags")

    @validator("name")
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate project name.

        Args:
            v: Project name to validate

        Returns:
            Trimmed project name or None

        Raises:
            ValueError: If name is whitespace-only
        """
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Project name cannot be empty or whitespace-only")
        return trimmed

    @validator("description")
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and normalize description.

        Args:
            v: Description to validate

        Returns:
            Trimmed description or None
        """
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @validator("tags")
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validate and normalize tags.

        Args:
            v: List of tags to validate

        Returns:
            Validated and deduplicated tag list or None

        Raises:
            ValueError: If any tag is empty or whitespace-only
        """
        if v is None:
            return None

        # Remove empty tags and validate
        non_empty_tags = []
        for tag in v:
            stripped = tag.strip()
            if not stripped:
                raise ValueError("Tags cannot be empty or whitespace-only")
            non_empty_tags.append(stripped)

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

        schema_extra = {
            "example": {
                "name": "Updated Customer API",
                "description": "Updated description",
                "is_active": True,
                "is_public": True,
                "tags": ["api", "staging"],
            }
        }


# Export all request schemas
__all__ = [
    "UserCreateRequest",
    "UserUpdateRequest",
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
]
