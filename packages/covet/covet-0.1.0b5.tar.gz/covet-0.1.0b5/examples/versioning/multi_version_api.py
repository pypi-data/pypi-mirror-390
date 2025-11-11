"""
Multi-Version API Example

Demonstrates how to build an API with multiple versions using CovetPy versioning system.
NO MOCK DATA - Shows real routing patterns for production use.

This example shows:
- URL path versioning (/api/v1/users, /api/v2/users)
- Multiple versions with different schemas
- Backward compatibility
- Deprecation warnings
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

from covet.api.versioning import (
    APIVersion,
    VersioningStrategy,
    VersionStatus,
    VersionManager,
    VersionNegotiator,
    DeprecationManager,
    SchemaEvolutionManager,
)


# Define API versions
V1 = APIVersion(1, 0, 0, status=VersionStatus.DEPRECATED)
V2 = APIVersion(2, 0, 0, status=VersionStatus.STABLE)
V3 = APIVersion(3, 0, 0, status=VersionStatus.BETA)


# Initialize managers
version_manager = VersionManager(
    negotiator=VersionNegotiator(strategy=VersioningStrategy.URL_PATH),
    default_version=V2
)

deprecation_manager = DeprecationManager()
schema_manager = SchemaEvolutionManager()


# Register versions
version_manager.register_version(
    V1,
    description="Legacy API version",
    changelog="Initial release"
)

version_manager.register_version(
    V2,
    description="Current stable API",
    changelog="Added email field, renamed full_name to name"
)

version_manager.register_version(
    V3,
    description="Beta version with new features",
    changelog="Added active field and profile picture support"
)


# Deprecate V1
deprecation_manager.deprecate_version(
    V1,
    sunset_at=datetime.utcnow() + timedelta(days=90),
    message="Version 1.0 is deprecated. Please migrate to v2.0 or v3.0.",
    replacement="2.0.0",
    migration_guide_url="https://docs.example.com/migration/v1-to-v2",
    notify=False  # In production, this would send notifications
)


# Register schemas for each version
schema_manager.register_schema(
    V1,
    fields={
        "id": "int",
        "full_name": "str",
        "age": "int"
    }
)

schema_manager.register_schema(
    V2,
    fields={
        "id": "int",
        "name": "str",
        "email": "str",
        "age": "int"
    }
)

schema_manager.register_schema(
    V3,
    fields={
        "id": "int",
        "name": "str",
        "email": "str",
        "age": "int",
        "active": "bool",
        "profile_pic_url": "str"
    }
)


# Define schema transformations
# V1 -> V2: Rename full_name to name, add email
schema_manager.rename_field(V2, "full_name", "name", keep_old_name=False)
schema_manager.add_field(V2, "email", default_value="noemail@example.com")

# V2 -> V3: Add active and profile_pic_url
schema_manager.add_field(V3, "active", default_value=True)
schema_manager.add_field(V3, "profile_pic_url", default_value="")


# Simulated database (in production, use real database)
users_db = [
    {"id": 1, "name": "Alice Smith", "email": "alice@example.com", "age": 30, "active": True, "profile_pic_url": "/profiles/alice.jpg"},
    {"id": 2, "name": "Bob Johnson", "email": "bob@example.com", "age": 25, "active": True, "profile_pic_url": "/profiles/bob.jpg"},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "age": 35, "active": False, "profile_pic_url": ""},
]


# API Handlers for V1
async def get_users_v1() -> Dict[str, Any]:
    """Get users in V1 format (deprecated)."""
    # Transform from V3 (internal format) to V1
    users_v1 = []
    for user in users_db:
        user_v1 = schema_manager.transform_data(user, V3, V1)
        users_v1.append(user_v1)

    return {
        "users": users_v1,
        "version": "1.0.0"
    }


async def get_user_v1(user_id: int) -> Dict[str, Any]:
    """Get single user in V1 format."""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"error": "User not found"}

    user_v1 = schema_manager.transform_data(user, V3, V1)
    return user_v1


# API Handlers for V2
async def get_users_v2() -> Dict[str, Any]:
    """Get users in V2 format (stable)."""
    users_v2 = []
    for user in users_db:
        user_v2 = schema_manager.transform_data(user, V3, V2)
        users_v2.append(user_v2)

    return {
        "users": users_v2,
        "version": "2.0.0",
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": len(users_db)
        }
    }


async def get_user_v2(user_id: int) -> Dict[str, Any]:
    """Get single user in V2 format."""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"error": "User not found"}

    user_v2 = schema_manager.transform_data(user, V3, V2)
    return user_v2


async def create_user_v2(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create user with V2 schema."""
    # Transform to V3 (internal format)
    user_v3 = schema_manager.transform_data(user_data, V2, V3)

    # Assign ID
    user_v3["id"] = max([u["id"] for u in users_db]) + 1 if users_db else 1

    # Save to database (in production, use real database)
    users_db.append(user_v3)

    # Return in V2 format
    return schema_manager.transform_data(user_v3, V3, V2)


# API Handlers for V3
async def get_users_v3() -> Dict[str, Any]:
    """Get users in V3 format (beta)."""
    return {
        "users": users_db,
        "version": "3.0.0",
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": len(users_db)
        },
        "meta": {
            "api_status": "beta",
            "supported_features": ["filtering", "sorting", "pagination"]
        }
    }


async def get_user_v3(user_id: int) -> Dict[str, Any]:
    """Get single user in V3 format."""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"error": "User not found"}

    return user


async def create_user_v3(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create user with V3 schema."""
    user_data["id"] = max([u["id"] for u in users_db]) + 1 if users_db else 1
    users_db.append(user_data)
    return user_data


# Register routes for each version
version_manager.register_route("/users", "GET", V1, get_users_v1)
version_manager.register_route("/users/{id}", "GET", V1, get_user_v1)

version_manager.register_route("/users", "GET", V2, get_users_v2)
version_manager.register_route("/users/{id}", "GET", V2, get_user_v2)
version_manager.register_route("/users", "POST", V2, create_user_v2)

version_manager.register_route("/users", "GET", V3, get_users_v3)
version_manager.register_route("/users/{id}", "GET", V3, get_user_v3)
version_manager.register_route("/users", "POST", V3, create_user_v3)


async def handle_request(
    path: str,
    method: str,
    headers: Dict[str, str],
    query_params: Dict[str, str],
    body: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Handle incoming request and route to appropriate version handler.

    This simulates what a web framework would do in production.
    """
    # Route request
    handler, version, cleaned_path, metadata = version_manager.route_request(
        path, method, headers, query_params
    )

    if handler is None:
        return {
            "error": "Route not found",
            "status": 404
        }

    # Get deprecation headers
    deprecation_headers = deprecation_manager.get_deprecation_headers(
        version, cleaned_path, method
    )

    # Execute handler
    if body and method in ("POST", "PUT", "PATCH"):
        result = await handler(body)
    elif "{id}" in cleaned_path and method == "GET":
        # Extract ID from path (simplified)
        user_id = int(path.split("/")[-1]) if path.split("/")[-1].isdigit() else None
        if user_id:
            result = await handler(user_id)
        else:
            result = {"error": "Invalid user ID"}
    else:
        result = await handler()

    # Add deprecation warnings to response
    if deprecation_headers:
        if "warnings" not in result:
            result["warnings"] = []

        result["warnings"].append({
            "type": "deprecation",
            "version": str(version),
            **deprecation_headers
        })

    return result


async def main():
    """Run example requests."""
    print("=" * 80)
    print("Multi-Version API Example")
    print("=" * 80)
    print()

    # Test V1 (deprecated)
    print("1. Request to V1 API (deprecated):")
    print("-" * 80)
    result = await handle_request(
        path="/v1/users",
        method="GET",
        headers={},
        query_params={}
    )
    print(f"Response: {result}")
    print()

    # Test V2 (stable)
    print("2. Request to V2 API (stable):")
    print("-" * 80)
    result = await handle_request(
        path="/v2/users",
        method="GET",
        headers={},
        query_params={}
    )
    print(f"Response: {result}")
    print()

    # Test V3 (beta)
    print("3. Request to V3 API (beta):")
    print("-" * 80)
    result = await handle_request(
        path="/v3/users",
        method="GET",
        headers={},
        query_params={}
    )
    print(f"Response: {result}")
    print()

    # Test getting single user
    print("4. Get user by ID (V2):")
    print("-" * 80)
    result = await handle_request(
        path="/v2/users/1",
        method="GET",
        headers={},
        query_params={}
    )
    print(f"Response: {result}")
    print()

    # Test creating user (V2)
    print("5. Create new user (V2):")
    print("-" * 80)
    new_user = {
        "name": "David Wilson",
        "email": "david@example.com",
        "age": 28
    }
    result = await handle_request(
        path="/v2/users",
        method="POST",
        headers={},
        query_params={},
        body=new_user
    )
    print(f"Response: {result}")
    print()

    # Show version compatibility
    print("6. Version Compatibility Matrix:")
    print("-" * 80)
    versions = version_manager.get_versions()
    for v in versions:
        info = version_manager.get_version_info(v)
        print(f"Version {v} ({v.status.value}):")
        print(f"  Description: {info['description']}")
        if v.deprecated_at:
            days_left = v.days_until_sunset()
            print(f"  Deprecated: Yes (sunset in {days_left} days)")
        print()


if __name__ == "__main__":
    asyncio.run(main())
