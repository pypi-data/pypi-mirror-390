"""
Complete Documented API Example

Demonstrates all documentation features of CovetPy including:
- Automatic OpenAPI generation
- Swagger UI and ReDoc interfaces
- Multiple examples per endpoint
- Authentication documentation
- Rich model documentation
"""

import asyncio
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr

from covet.api.docs import (
    OpenAPIGenerator,
    SwaggerUI,
    SwaggerUIConfig,
    ReDocUI,
    ReDocConfig,
    ExampleGenerator,
    MarkdownGenerator,
    MarkdownConfig,
    PostmanCollection,
    SecurityScheme,
    SecuritySchemeType,
)


# === Data Models ===

class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        example="johndoe",
        description="Unique username for the user"
    )
    email: EmailStr = Field(
        ...,
        example="john@example.com",
        description="User's email address"
    )
    full_name: str = Field(
        ...,
        example="John Doe",
        description="User's full name"
    )


class UserCreate(UserBase):
    """
    User creation request.

    This model is used when creating a new user account.
    All fields are required for registration.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        example="SecurePass123!",
        description="Strong password (minimum 8 characters)"
    )


class UserUpdate(BaseModel):
    """
    User update request.

    Allows partial updates to user information.
    All fields are optional.
    """
    email: Optional[EmailStr] = Field(
        None,
        example="newemail@example.com"
    )
    full_name: Optional[str] = Field(
        None,
        example="John Smith"
    )
    password: Optional[str] = Field(
        None,
        min_length=8
    )


class UserResponse(UserBase):
    """
    User response model.

    Returns complete user information including metadata.
    """
    id: int = Field(
        ...,
        example=123,
        description="Unique user identifier"
    )
    created_at: datetime = Field(
        ...,
        example="2025-01-01T00:00:00Z",
        description="Account creation timestamp"
    )
    is_active: bool = Field(
        ...,
        example=True,
        description="Whether the account is active"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "created_at": "2025-01-01T00:00:00Z",
                "is_active": True
            }
        }


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int = Field(..., ge=1, example=1)
    page_size: int = Field(..., ge=1, le=100, example=20)
    total: int = Field(..., ge=0, example=100)
    total_pages: int = Field(..., ge=0, example=5)


class UserListResponse(BaseModel):
    """
    Paginated user list response.

    Returns a list of users with pagination metadata.
    """
    users: List[UserResponse] = Field(
        ...,
        description="List of users for current page"
    )
    pagination: PaginationMeta = Field(
        ...,
        description="Pagination information"
    )


class ErrorResponse(BaseModel):
    """
    Standard error response.

    Returned for all error conditions with descriptive information.
    """
    error: str = Field(
        ...,
        example="VALIDATION_ERROR",
        description="Machine-readable error code"
    )
    message: str = Field(
        ...,
        example="Invalid input provided",
        description="Human-readable error message"
    )
    details: Optional[dict] = Field(
        None,
        example={"field": "email", "issue": "invalid format"},
        description="Additional error context"
    )


class LoginRequest(BaseModel):
    """Login credentials."""
    username: str = Field(..., example="johndoe")
    password: str = Field(..., example="SecurePass123!")


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="JWT access token"
    )
    token_type: str = Field(
        ...,
        example="bearer",
        description="Token type (always 'bearer')"
    )
    expires_in: int = Field(
        ...,
        example=3600,
        description="Token expiration time in seconds"
    )


# === Mock Handlers ===

async def list_users(page: int = 1, page_size: int = 20) -> UserListResponse:
    """
    List all users with pagination.

    Returns a paginated list of users. Use page and page_size parameters
    to control pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Number of users per page (1-100)

    Returns:
        Paginated list of users
    """
    return UserListResponse(
        users=[],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=0,
            total_pages=0
        )
    )


async def get_user(user_id: int) -> UserResponse:
    """
    Get user by ID.

    Retrieves detailed information about a specific user.

    Args:
        user_id: User's unique identifier

    Returns:
        User details

    Raises:
        404: User not found
        401: Unauthorized (authentication required)
    """
    pass


async def create_user(user: UserCreate) -> UserResponse:
    """
    Create a new user.

    Register a new user account with the provided information.
    Username and email must be unique.

    Args:
        user: User creation data

    Returns:
        Created user details

    Raises:
        400: Invalid input (validation error)
        409: Conflict (username or email already exists)
    """
    pass


async def update_user(user_id: int, user: UserUpdate) -> UserResponse:
    """
    Update user information.

    Update one or more fields of an existing user.
    Only provided fields will be updated.

    Args:
        user_id: User's unique identifier
        user: Fields to update

    Returns:
        Updated user details

    Raises:
        404: User not found
        401: Unauthorized
        403: Forbidden (can only update own profile)
    """
    pass


async def delete_user(user_id: int):
    """
    Delete a user.

    Permanently delete a user account. This action cannot be undone.

    Args:
        user_id: User's unique identifier

    Raises:
        404: User not found
        401: Unauthorized
        403: Forbidden (insufficient permissions)
    """
    pass


async def login(credentials: LoginRequest) -> TokenResponse:
    """
    Authenticate and get access token.

    Exchange username and password for a JWT access token.
    The token should be included in subsequent requests.

    Args:
        credentials: Login credentials

    Returns:
        JWT access token

    Raises:
        401: Invalid credentials
    """
    pass


# === Documentation Setup ===

def create_documentation():
    """Create complete API documentation."""

    # Initialize OpenAPI generator
    generator = OpenAPIGenerator(
        title="User Management API",
        version="2.0.0",
        description="""
# User Management API

Complete REST API for user management with authentication.

## Features

- User CRUD operations
- JWT authentication
- Pagination support
- Comprehensive error handling

## Getting Started

1. Register a new user account
2. Login to get access token
3. Use token in Authorization header: `Bearer YOUR_TOKEN`

## Rate Limits

- 100 requests per minute per IP
- 1000 requests per hour per user

## Support

For support, email support@example.com
        """,
        contact={
            "name": "API Support",
            "email": "support@example.com",
            "url": "https://example.com/support"
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0"
        },
        servers=[
            {
                "url": "https://api.example.com/v2",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.example.com/v2",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000/v2",
                "description": "Development server"
            }
        ]
    )

    # Add JWT authentication
    generator.add_security_scheme(
        "bearer_auth",
        SecurityScheme(
            type=SecuritySchemeType.HTTP,
            scheme="bearer",
            bearer_format="JWT",
            description="JWT Bearer token authentication"
        )
    )

    # Add tags
    generator.add_tag("Authentication", "User authentication and token management")
    generator.add_tag("Users", "User management operations")

    # Authentication endpoints
    generator.add_route(
        path="/auth/login",
        method="POST",
        handler=login,
        request_model=LoginRequest,
        response_model=TokenResponse,
        tags=["Authentication"],
        summary="Login",
        description="Authenticate with username and password to get access token",
        responses={
            401: ErrorResponse
        }
    )

    # User endpoints
    generator.add_route(
        path="/users",
        method="GET",
        handler=list_users,
        response_model=UserListResponse,
        tags=["Users"],
        summary="List users",
        description="Get paginated list of all users",
        security=[{"bearer_auth": []}]
    )

    generator.add_route(
        path="/users",
        method="POST",
        handler=create_user,
        request_model=UserCreate,
        response_model=UserResponse,
        tags=["Users"],
        summary="Create user",
        description="Register a new user account",
        responses={
            400: ErrorResponse,
            409: ErrorResponse
        }
    )

    generator.add_route(
        path="/users/{user_id}",
        method="GET",
        handler=get_user,
        response_model=UserResponse,
        tags=["Users"],
        summary="Get user",
        description="Get detailed information about a specific user",
        security=[{"bearer_auth": []}],
        responses={
            404: ErrorResponse
        }
    )

    generator.add_route(
        path="/users/{user_id}",
        method="PUT",
        handler=update_user,
        request_model=UserUpdate,
        response_model=UserResponse,
        tags=["Users"],
        summary="Update user",
        description="Update user information",
        security=[{"bearer_auth": []}],
        responses={
            404: ErrorResponse,
            403: ErrorResponse
        }
    )

    generator.add_route(
        path="/users/{user_id}",
        method="DELETE",
        handler=delete_user,
        tags=["Users"],
        summary="Delete user",
        description="Permanently delete a user account",
        security=[{"bearer_auth": []}],
        responses={
            204: {"description": "User deleted successfully"},
            404: ErrorResponse,
            403: ErrorResponse
        }
    )

    return generator


def generate_all_documentation():
    """Generate all documentation formats."""

    print("Generating API documentation...")

    # Create documentation
    generator = create_documentation()

    # 1. Generate OpenAPI spec
    print("\n1. OpenAPI Specification")
    print("-" * 50)
    spec = generator.generate_spec()
    generator.save_json("openapi.json", indent=2)
    print(f"✓ Saved to openapi.json")
    print(f"  - Paths: {len(spec['paths'])}")
    print(f"  - Schemas: {len(spec['components']['schemas'])}")
    print(f"  - Security schemes: {len(spec['components']['securitySchemes'])}")

    # 2. Generate Swagger UI HTML
    print("\n2. Swagger UI")
    print("-" * 50)
    swagger = SwaggerUI(
        config=SwaggerUIConfig(
            spec_url="/openapi.json",
            title="User Management API - Swagger UI",
            persist_authorization=True,
            display_request_duration=True
        )
    )
    html = swagger.get_html()
    with open("swagger.html", "w") as f:
        f.write(html)
    print(f"✓ Saved to swagger.html")
    print(f"  - Interactive documentation with try-it-out")
    print(f"  - OAuth2 support")

    # 3. Generate ReDoc HTML
    print("\n3. ReDoc")
    print("-" * 50)
    redoc = ReDocUI(
        config=ReDocConfig(
            spec_url="/openapi.json",
            title="User Management API - ReDoc",
            hide_download_button=False
        )
    )
    html = redoc.get_html()
    with open("redoc.html", "w") as f:
        f.write(html)
    print(f"✓ Saved to redoc.html")
    print(f"  - Beautiful three-panel layout")
    print(f"  - Advanced search")

    # 4. Generate Markdown documentation
    print("\n4. Markdown Documentation")
    print("-" * 50)
    markdown_gen = MarkdownGenerator(
        spec=spec,
        config=MarkdownConfig(
            base_url="https://api.example.com/v2"
        )
    )
    markdown = markdown_gen.generate()
    with open("API_DOCUMENTATION.md", "w") as f:
        f.write(markdown)
    print(f"✓ Saved to API_DOCUMENTATION.md")
    print(f"  - MkDocs compatible")
    print(f"  - Code examples in curl, Python, JavaScript")

    # 5. Generate Postman collection
    print("\n5. Postman Collection")
    print("-" * 50)
    postman = PostmanCollection(
        name="User Management API",
        openapi_spec=spec,
        base_url="https://api.example.com/v2"
    )
    collection = postman.generate()
    with open("postman_collection.json", "w") as f:
        import json
        json.dump(collection, f, indent=2)
    print(f"✓ Saved to postman_collection.json")
    print(f"  - Ready to import into Postman")
    print(f"  - Organized by tags")
    print(f"  - Pre-configured authentication")

    # 6. Generate environment file
    env = postman.generate_environment(
        "Production",
        additional_vars={
            "base_url": "https://api.example.com/v2"
        }
    )
    with open("postman_environment.json", "w") as f:
        import json
        json.dump(env, f, indent=2)
    print(f"✓ Saved to postman_environment.json")

    print("\n" + "=" * 50)
    print("Documentation generation complete!")
    print("=" * 50)
    print("\nGenerated files:")
    print("  - openapi.json (OpenAPI 3.1 specification)")
    print("  - swagger.html (Interactive Swagger UI)")
    print("  - redoc.html (Beautiful ReDoc documentation)")
    print("  - API_DOCUMENTATION.md (Markdown documentation)")
    print("  - postman_collection.json (Postman collection)")
    print("  - postman_environment.json (Postman environment)")


if __name__ == "__main__":
    generate_all_documentation()
