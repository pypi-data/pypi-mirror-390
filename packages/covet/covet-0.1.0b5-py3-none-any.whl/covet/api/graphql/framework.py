"""
GraphQL Framework Integration

Main GraphQL framework class that integrates all components.
"""

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import strawberry
from strawberry.schema import Schema

from .authentication import AuthContext, GraphQLAuth
from .dataloader import DataLoaderRegistry
from .execution import ExecutionContext, ExecutionResult, GraphQLExecutor
from .playground import GraphQLPlayground, playground_html
from .schema import GraphQLSchema
from .subscriptions import PubSub, SubscriptionManager, get_pubsub
from .validation import DepthLimitValidator, QueryComplexityValidator, ValidationRule
from .websocket_protocol import SubscriptionServer, create_subscription_server


@dataclass
class GraphQLConfig:
    """GraphQL framework configuration."""

    enable_introspection: bool = True
    enable_playground: bool = True
    playground_path: str = "/graphql"
    playground_type: str = "graphql-playground"  # or 'graphiql', 'apollo-sandbox'

    enable_subscriptions: bool = True
    subscription_path: str = "/graphql"

    enable_validation: bool = True
    max_query_depth: int = 10
    max_query_complexity: int = 1000

    enable_dataloader: bool = True

    debug: bool = False


class GraphQLFramework:
    """
    Production-ready GraphQL framework.

    Integrates all GraphQL components into a cohesive system.

    Example:
        from covet.api.graphql import GraphQLFramework, graphql_type, field

        framework = GraphQLFramework()

        @framework.type()
        class User:
            id: int
            name: str
            email: str

        @framework.query()
        class Query:
            @field
            async def users(self) -> List[User]:
                return await get_users()

        schema = framework.build_schema()
        app = framework.create_asgi_app()
    """

    def __init__(
        self,
        config: Optional[GraphQLConfig] = None,
        authenticator: Optional[Any] = None,
    ):
        """
        Initialize framework.

        Args:
            config: Framework configuration
            authenticator: JWT authenticator for auth integration
        """
        self.config = config or GraphQLConfig()

        # Core components
        self.schema_builder = GraphQLSchema(
            enable_query_cost_analysis=self.config.enable_validation,
            max_query_depth=self.config.max_query_depth,
            max_query_complexity=self.config.max_query_complexity,
        )

        self._executor: Optional[GraphQLExecutor] = None
        self._subscription_manager: Optional[SubscriptionManager] = None
        self._subscription_server: Optional[SubscriptionServer] = None

        # Authentication
        self.auth: Optional[GraphQLAuth] = None
        if authenticator:
            from .authentication import GraphQLAuth

            self.auth = GraphQLAuth(authenticator)

        # Validation rules
        self.validation_rules: List[ValidationRule] = []
        if self.config.enable_validation:
            self.validation_rules = [
                QueryComplexityValidator(self.config.max_query_complexity),
                DepthLimitValidator(self.config.max_query_depth),
            ]

    # Schema building methods (delegate to schema_builder)
    def type(self, cls: Optional[type] = None, **kwargs):
        """Register GraphQL object type."""
        return self.schema_builder.type(cls, **kwargs)

    def input(self, cls: Optional[type] = None, **kwargs):
        """Register GraphQL input type."""
        return self.schema_builder.input(cls, **kwargs)

    def enum(self, cls: Optional[type] = None, **kwargs):
        """Register GraphQL enum type."""
        return self.schema_builder.enum(cls, **kwargs)

    def interface(self, cls: Optional[type] = None, **kwargs):
        """Register GraphQL interface type."""
        return self.schema_builder.interface(cls, **kwargs)

    def query(self, cls: Optional[type] = None):
        """Register root Query type."""
        return self.schema_builder.query(cls)

    def mutation(self, cls: Optional[type] = None):
        """Register root Mutation type."""
        return self.schema_builder.mutation(cls)

    def subscription(self, cls: Optional[type] = None):
        """Register root Subscription type."""
        return self.schema_builder.subscription(cls)

    def build_schema(self) -> Schema:
        """Build Strawberry schema."""
        return self.schema_builder.build()

    @property
    def schema(self) -> Schema:
        """Get schema (builds if needed)."""
        return self.schema_builder.schema

    @property
    def executor(self) -> GraphQLExecutor:
        """Get executor (creates if needed)."""
        if self._executor is None:
            self._executor = GraphQLExecutor(
                schema=self.schema,
                enable_introspection=self.config.enable_introspection,
            )
        return self._executor

    @property
    def subscription_manager(self) -> SubscriptionManager:
        """Get subscription manager."""
        if self._subscription_manager is None:
            self._subscription_manager = SubscriptionManager(get_pubsub())
        return self._subscription_manager

    @property
    def subscription_server(self) -> SubscriptionServer:
        """Get subscription server."""
        if self._subscription_server is None:
            self._subscription_server = create_subscription_server(
                schema=self.schema,
                context_factory=self._create_context,
            )
        return self._subscription_server

    def _create_context(self, request: Optional[Any] = None) -> ExecutionContext:
        """Create execution context."""
        context = ExecutionContext()

        # Add authentication if available
        if self.auth and request:
            import asyncio

            auth_context = asyncio.run(self.auth.create_context_from_request(request))
            context.user = auth_context.user

        # Add dataloaders
        if self.config.enable_dataloader:
            context.dataloaders = {}

        return context

    async def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        """Execute GraphQL query."""
        # Validate query
        if self.config.enable_validation:
            from .validation import validate_query

            errors = validate_query(query, variables, self.validation_rules)
            if errors:
                from .execution import GraphQLError

                return ExecutionResult(errors=[GraphQLError(err) for err in errors])

        # Execute
        return await self.executor.execute_query(
            query,
            variables,
            operation_name,
            context or self._create_context(),
        )

    def create_asgi_app(self):
        """
        Create ASGI application.

        Returns:
            ASGI app callable
        """

        async def graphql_app(scope, receive, send):
            """ASGI application."""
            if scope["type"] == "http":
                await self._handle_http(scope, receive, send)
            elif scope["type"] == "websocket":
                await self._handle_websocket(scope, receive, send)

        return graphql_app

    async def _handle_http(self, scope, receive, send):
        """Handle HTTP request."""
        path = scope.get("path", "/")
        method = scope.get("method", "GET")

        # Serve playground
        if (
            self.config.enable_playground
            and method == "GET"
            and path == self.config.playground_path
        ):
            html = playground_html(
                endpoint=self.config.playground_path,
                subscriptions_endpoint=self.config.subscription_path,
                playground_type=self.config.playground_type,
            )

            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"text/html; charset=utf-8"]],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": html.encode("utf-8"),
                }
            )
            return

        # Handle GraphQL query
        if method == "POST" and path == self.config.playground_path:
            # Read body
            body = b""
            while True:
                message = await receive()
                body += message.get("body", b"")
                if not message.get("more_body"):
                    break

            # Parse JSON
            try:
                data = json.loads(body)
                query = data.get("query")
                variables = data.get("variables")
                operation_name = data.get("operationName")
            except json.JSONDecodeError:
                await send(
                    {
                        "type": "http.response.start",
                        "status": 400,
                        "headers": [[b"content-type", b"application/json"]],
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": b'{"errors": [{"message": "Invalid JSON"}]}',
                    }
                )
                return

            # Execute query
            result = await self.execute_query(query, variables, operation_name)

            # Send response
            response_body = json.dumps(result.to_dict()).encode("utf-8")
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": response_body,
                }
            )
            return

        # 404
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [[b"content-type", b"application/json"]],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b'{"error": "Not Found"}',
            }
        )

    async def _handle_websocket(self, scope, receive, send):
        """Handle WebSocket connection for subscriptions."""
        if not self.config.enable_subscriptions:
            return

        # Create ASGI WebSocket wrapper
        class ASGIWebSocket:
            async def accept(self, subprotocol=None):
                await send(
                    {
                        "type": "websocket.accept",
                        "subprotocol": subprotocol,
                    }
                )

            async def send_text(self, data):
                await send(
                    {
                        "type": "websocket.send",
                        "text": data,
                    }
                )

            async def receive_text(self):
                message = await receive()
                return message.get("text", "")

            async def close(self):
                await send({"type": "websocket.close"})

        websocket = ASGIWebSocket()
        await self.subscription_server.handle_websocket(websocket)


class GraphQLApp(GraphQLFramework):
    """Alias for GraphQLFramework for clarity."""


def create_graphql_app(
    config: Optional[GraphQLConfig] = None,
    authenticator: Optional[Any] = None,
) -> GraphQLFramework:
    """
    Create GraphQL application.

    Args:
        config: GraphQL configuration
        authenticator: JWT authenticator

    Returns:
        GraphQL framework instance
    """
    return GraphQLFramework(config, authenticator)


def graphql_route(framework: GraphQLFramework):
    """
    Decorator for adding GraphQL to existing ASGI app.

    Example:
        app = CovetApp()
        graphql = create_graphql_app()

        @graphql_route(graphql)
        @app.route("/graphql")
        async def graphql_handler(request):
            pass
    """

    def decorator(func):
        return framework.create_asgi_app()

    return decorator


__all__ = [
    "GraphQLFramework",
    "GraphQLApp",
    "GraphQLConfig",
    "create_graphql_app",
    "graphql_route",
]
