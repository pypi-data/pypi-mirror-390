"""
CovetPy API Module

This module provides high-level API components for building web applications,
including REST API support, GraphQL integration, WebSocket real-time features,
and API documentation generation.

Example usage:
    from covet.api import RESTRouter, GraphQLSchema, WebSocketManager

    # Create REST API
    router = RESTRouter()

    @router.get("/users/{user_id}")
    async def get_user(user_id: int):
        return {"user_id": user_id, "name": "John Doe"}
"""

from typing import TYPE_CHECKING

# Import REST API components when available
try:
    from covet.api.rest import (
        APIRouter,
        Depends,
        HTTPException,
        RESTRouter,
        status,
    )

    _HAS_REST = True
except ImportError:
    _HAS_REST = False

# Import GraphQL components when available
try:
    from covet.api.graphql import (
        GraphQLResolver,
        GraphQLSchema,
        GraphQLType,
        execute_graphql,
    )

    _HAS_GRAPHQL = True
except ImportError:
    _HAS_GRAPHQL = False

# Import WebSocket components when available
try:
    from covet.api.websocket import (
        ConnectionManager,
        WebSocketConnection,
        WebSocketManager,
        WebSocketRouter,
    )

    _HAS_WEBSOCKET = True
except ImportError:
    _HAS_WEBSOCKET = False

# Import API documentation components when available
try:
    from covet.api.docs import (
        OpenAPIGenerator,
        ReDocUI,
        SwaggerUI,
        generate_schema,
    )

    _HAS_DOCS = True
except ImportError:
    _HAS_DOCS = False

# Import API versioning components when available
try:
    from covet.api.versioning import (
        HeaderVersioning,
        QueryVersioning,
        URLVersioning,
        VersioningStrategy,
    )

    _HAS_VERSIONING = True
except ImportError:
    _HAS_VERSIONING = False

# Import schema validation components when available
try:
    from covet.api.schemas import (
        BaseSchema,
        ValidationError,
        validate_request,
        validate_response,
    )

    _HAS_SCHEMAS = True
except ImportError:
    _HAS_SCHEMAS = False


# Public API exports - only include available components
__all__ = []

# REST API components
if _HAS_REST:
    __all__.extend(
        [
            "RESTRouter",  # REST API routing
            "APIRouter",  # Generic API router
            "Depends",  # Dependency injection
            "HTTPException",  # HTTP error exceptions
            "status",  # HTTP status codes
        ]
    )

# GraphQL components
if _HAS_GRAPHQL:
    __all__.extend(
        [
            "GraphQLSchema",  # GraphQL schema definition
            "GraphQLResolver",  # GraphQL field resolvers
            "GraphQLType",  # GraphQL type system
            "execute_graphql",  # GraphQL query execution
        ]
    )

# WebSocket components
if _HAS_WEBSOCKET:
    __all__.extend(
        [
            "WebSocketManager",  # WebSocket connection management
            "WebSocketConnection",  # Individual WebSocket connection
            "WebSocketRouter",  # WebSocket routing
            "ConnectionManager",  # Connection pool management
        ]
    )

# API documentation components
if _HAS_DOCS:
    __all__.extend(
        [
            "OpenAPIGenerator",  # OpenAPI 3.0 schema generation
            "SwaggerUI",  # Swagger UI integration
            "ReDocUI",  # ReDoc documentation UI
            "generate_schema",  # Schema generation utility
        ]
    )

# API versioning components
if _HAS_VERSIONING:
    __all__.extend(
        [
            "VersioningStrategy",  # Base versioning strategy
            "HeaderVersioning",  # Version via HTTP headers
            "URLVersioning",  # Version via URL paths
            "QueryVersioning",  # Version via query parameters
        ]
    )

# Schema validation components
if _HAS_SCHEMAS:
    __all__.extend(
        [
            "BaseSchema",  # Base schema class
            "ValidationError",  # Schema validation errors
            "validate_request",  # Request validation decorator
            "validate_response",  # Response validation decorator
        ]
    )


def get_available_features():
    """
    Get a list of available API features in this installation.

    Returns:
        dict: Dictionary of feature availability
    """
    return {
        "rest": _HAS_REST,
        "graphql": _HAS_GRAPHQL,
        "websocket": _HAS_WEBSOCKET,
        "docs": _HAS_DOCS,
        "versioning": _HAS_VERSIONING,
        "schemas": _HAS_SCHEMAS,
    }


# Add utility function to exports
__all__.append("get_available_features")
