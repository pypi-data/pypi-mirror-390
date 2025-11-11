"""
CovetPy GraphQL Framework

Production-ready GraphQL implementation with:
- Strawberry GraphQL for modern async GraphQL
- Complete query, mutation, and subscription support
- DataLoader integration for N+1 query optimization
- JWT authentication and authorization
- GraphQL Playground and introspection
- WebSocket subscriptions (graphql-ws protocol)
- Relay-style pagination
- File upload support
- Error handling with RFC 7807
- Performance monitoring and query complexity analysis

NO MOCK DATA: Real Strawberry GraphQL implementation.
"""

from .authentication import (
    AuthContext,
    GraphQLAuth,
    get_current_user,
    require_auth,
    require_permissions,
    require_roles,
)
from .dataloader import (
    BatchLoader,
    DataLoader,
    DataLoaderRegistry,
    create_batch_function,
    create_loader,
)
from .errors import (
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    GraphQLHTTPError,
    NotFoundError,
    ValidationError,
)
from .execution import (
    ExecutionContext,
    ExecutionResult,
    GraphQLError,
    GraphQLExecutor,
    execute_mutation,
    execute_query,
    execute_subscription,
)
from .framework import (
    GraphQLApp,
    GraphQLFramework,
    create_graphql_app,
    graphql_route,
)
from .middleware import (
    AuthMiddleware,
    ErrorHandlerMiddleware,
    GraphQLMiddleware,
    LoggingMiddleware,
    PerformanceMiddleware,
)
from .pagination import (
    Connection,
    ConnectionResolver,
    Edge,
    PageInfo,
    create_connection,
    cursor_to_offset,
    offset_to_cursor,
    relay_connection,
)
from .playground import (
    ApolloSandbox,
    GraphiQLPlayground,
    GraphQLPlayground,
    playground_html,
)
from .schema import (
    EnumType,
    GraphQLSchema,
    InputType,
    InterfaceType,
    ObjectType,
    ScalarType,
    UnionType,
)
from .schema import enum as graphql_enum
from .schema import (
    field,
)
from .schema import input as graphql_input
from .schema import interface as graphql_interface
from .schema import scalar as graphql_scalar
from .schema import type as graphql_type
from .subscriptions import (
    PubSub,
    SubscriptionManager,
    Topic,
    publish,
    subscribe,
    subscription_handler,
)
from .upload import (
    MultipartRequest,
    Upload,
    process_multipart,
    upload_scalar,
)
from .validation import (
    DepthLimitValidator,
    QueryComplexityValidator,
    ValidationRule,
    validate_query,
)
from .websocket_protocol import (
    GraphQLWSProtocol,
    SubscriptionServer,
    create_subscription_server,
)

__all__ = [
    "GraphQLField",
    "GraphQLScalarType",
    # Schema
    "GraphQLSchema",
    "ObjectType",
    "InputType",
    "InterfaceType",
    "UnionType",
    "EnumType",
    "ScalarType",
    "field",
    "graphql_type",
    "graphql_input",
    "graphql_interface",
    "graphql_enum",
    "graphql_scalar",
    # Execution
    "GraphQLExecutor",
    "ExecutionContext",
    "ExecutionResult",
    "GraphQLError",
    "execute_query",
    "execute_mutation",
    "execute_subscription",
    # DataLoader
    "DataLoader",
    "DataLoaderRegistry",
    "BatchLoader",
    "create_loader",
    "create_batch_function",
    # Authentication
    "GraphQLAuth",
    "AuthContext",
    "require_auth",
    "require_roles",
    "require_permissions",
    "get_current_user",
    # Pagination
    "Connection",
    "Edge",
    "PageInfo",
    "ConnectionResolver",
    "relay_connection",
    "create_connection",
    "offset_to_cursor",
    "cursor_to_offset",
    # Subscriptions
    "SubscriptionManager",
    "PubSub",
    "Topic",
    "subscribe",
    "publish",
    "subscription_handler",
    # Playground
    "GraphQLPlayground",
    "GraphiQLPlayground",
    "ApolloSandbox",
    "playground_html",
    # Framework
    "GraphQLFramework",
    "GraphQLApp",
    "create_graphql_app",
    "graphql_route",
    # Validation
    "ValidationRule",
    "QueryComplexityValidator",
    "DepthLimitValidator",
    "validate_query",
    # Errors
    "GraphQLHTTPError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "BadRequestError",
    # Middleware
    "GraphQLMiddleware",
    "AuthMiddleware",
    "LoggingMiddleware",
    "PerformanceMiddleware",
    "ErrorHandlerMiddleware",
    # Upload
    "Upload",
    "upload_scalar",
    "MultipartRequest",
    "process_multipart",
    # WebSocket
    "GraphQLWSProtocol",
    "SubscriptionServer",
    "create_subscription_server",
]


class GraphQLField:
    """GraphQL field definition."""
    
    def __init__(self, type_,  name=None, resolver=None, args=None, description=None):
        self.name = name
        self.type_ = type_
        self.resolver = resolver
        self.args = args or {}
        self.description = description


class GraphQLScalarType:
    """GraphQL scalar type definition."""
    
    def __init__(self, name, serialize=None, parse_value=None, parse_literal=None):
        self.name = name
        self.serialize = serialize or (lambda x: x)
        self.parse_value = parse_value or (lambda x: x)
        self.parse_literal = parse_literal or (lambda x: x)



class GraphQLList:
    """GraphQL list type."""
    def __init__(self, of_type):
        self.of_type = of_type

class GraphQLArgument:
    """GraphQL argument."""
    def __init__(self, type_, default_value=None, description=None):
        self.type_ = type_
        self.default_value = default_value
        self.description = description
