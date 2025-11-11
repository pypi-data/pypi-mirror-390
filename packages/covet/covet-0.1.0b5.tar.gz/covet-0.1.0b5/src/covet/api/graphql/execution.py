"""
GraphQL Execution Engine

Handles execution of GraphQL queries, mutations, and subscriptions
with proper error handling, context management, and performance monitoring.
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional

import strawberry
from strawberry.types import ExecutionResult as StrawberryExecutionResult
from strawberry.types import Info


class GraphQLError(Exception):
    """Base GraphQL error."""

    def __init__(
        self,
        message: str,
        path: Optional[List[str]] = None,
        extensions: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.path = path or []
        self.extensions = extensions or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to GraphQL error format."""
        error_dict = {"message": self.message}
        if self.path:
            error_dict["path"] = self.path
        if self.extensions:
            error_dict["extensions"] = self.extensions
        return error_dict


@dataclass
class ExecutionContext:
    """
    GraphQL execution context.

    Contains request-scoped data like user info, dataloaders, etc.
    """

    # Authentication
    user: Optional[Dict[str, Any]] = None
    request: Optional[Any] = None

    # DataLoaders
    dataloaders: Dict[str, Any] = field(default_factory=dict)

    # Caching
    cache: Optional[Any] = None

    # Performance tracking
    start_time: float = field(default_factory=time.time)

    # Custom context data
    extra: Dict[str, Any] = field(default_factory=dict)

    def get_user_id(self) -> Optional[str]:
        """Get current user ID."""
        if self.user:
            return self.user.get("id")
        return None

    def get_roles(self) -> List[str]:
        """Get current user roles."""
        if self.user:
            return self.user.get("roles", [])
        return []

    def get_permissions(self) -> List[str]:
        """Get current user permissions."""
        if self.user:
            return self.user.get("permissions", [])
        return []

    def has_permission(self, permission: str) -> bool:
        """Check if user has permission."""
        return permission in self.get_permissions()

    def has_role(self, role: str) -> bool:
        """Check if user has role."""
        return role in self.get_roles()

    def elapsed_time(self) -> float:
        """Get elapsed time since context creation."""
        return time.time() - self.start_time


@dataclass
class ExecutionResult:
    """
    GraphQL execution result.

    Wraps Strawberry ExecutionResult with additional metadata.
    """

    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[GraphQLError]] = None
    extensions: Optional[Dict[str, Any]] = None

    @classmethod
    def from_strawberry(
        cls,
        result: StrawberryExecutionResult,
        execution_time: Optional[float] = None,
    ) -> "ExecutionResult":
        """Create from Strawberry result."""
        errors = None
        if result.errors:
            errors = [
                GraphQLError(
                    message=str(err),
                    path=getattr(err, "path", None),
                    extensions=getattr(err, "extensions", None),
                )
                for err in result.errors
            ]

        extensions = result.extensions or {}
        if execution_time is not None:
            extensions["executionTime"] = f"{execution_time:.3f}ms"

        return cls(
            data=result.data,
            errors=errors,
            extensions=extensions,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {}

        if self.data is not None:
            result["data"] = self.data

        if self.errors:
            result["errors"] = [err.to_dict() for err in self.errors]

        if self.extensions:
            result["extensions"] = self.extensions

        return result

    @property
    def has_errors(self) -> bool:
        """Check if result has errors."""
        return bool(self.errors)


class GraphQLExecutor:
    """
    GraphQL query executor.

    Executes GraphQL queries, mutations, and subscriptions with
    context management and performance tracking.
    """

    def __init__(
        self,
        schema: strawberry.Schema,
        enable_introspection: bool = True,
        enable_performance_tracking: bool = True,
    ):
        """
        Initialize executor.

        Args:
            schema: Strawberry schema
            enable_introspection: Enable introspection queries
            enable_performance_tracking: Track execution performance
        """
        self.schema = schema
        self.enable_introspection = enable_introspection
        self.enable_performance_tracking = enable_performance_tracking

    async def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        """
        Execute GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name
            context: Execution context

        Returns:
            Execution result
        """
        start_time = time.time()

        # Create context if not provided
        if context is None:
            context = ExecutionContext()

        try:
            # Execute query with Strawberry
            result = await self.schema.execute(
                query,
                variable_values=variables,
                operation_name=operation_name,
                context_value=context,
            )

            # Calculate execution time
            execution_time = None
            if self.enable_performance_tracking:
                execution_time = (time.time() - start_time) * 1000

            return ExecutionResult.from_strawberry(result, execution_time)

        except Exception as e:
            # Handle unexpected errors
            error = GraphQLError(
                message=str(e),
                extensions={"code": "INTERNAL_SERVER_ERROR"},
            )
            return ExecutionResult(errors=[error])

    async def execute_mutation(
        self,
        mutation: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        """
        Execute GraphQL mutation.

        Same as execute_query but semantically distinct.
        """
        return await self.execute_query(
            mutation,
            variables,
            operation_name,
            context,
        )

    async def execute_subscription(
        self,
        subscription: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        context: Optional[ExecutionContext] = None,
    ) -> AsyncIterator[ExecutionResult]:
        """
        Execute GraphQL subscription.

        Args:
            subscription: GraphQL subscription string
            variables: Query variables
            operation_name: Operation name
            context: Execution context

        Yields:
            Execution results as they arrive
        """
        # Create context if not provided
        if context is None:
            context = ExecutionContext()

        try:
            # Execute subscription with Strawberry
            async for result in self.schema.subscribe(
                subscription,
                variable_values=variables,
                operation_name=operation_name,
                context_value=context,
            ):
                start_time = time.time()

                execution_time = None
                if self.enable_performance_tracking:
                    execution_time = (time.time() - start_time) * 1000

                yield ExecutionResult.from_strawberry(result, execution_time)

        except Exception as e:
            # Handle unexpected errors
            error = GraphQLError(
                message=str(e),
                extensions={"code": "SUBSCRIPTION_ERROR"},
            )
            yield ExecutionResult(errors=[error])


# Convenience functions
async def execute_query(
    schema: strawberry.Schema,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    context: Optional[ExecutionContext] = None,
) -> ExecutionResult:
    """Execute GraphQL query (convenience function)."""
    executor = GraphQLExecutor(schema)
    return await executor.execute_query(query, variables, context=context)


async def execute_mutation(
    schema: strawberry.Schema,
    mutation: str,
    variables: Optional[Dict[str, Any]] = None,
    context: Optional[ExecutionContext] = None,
) -> ExecutionResult:
    """Execute GraphQL mutation (convenience function)."""
    executor = GraphQLExecutor(schema)
    return await executor.execute_mutation(mutation, variables, context=context)


async def execute_subscription(
    schema: strawberry.Schema,
    subscription: str,
    variables: Optional[Dict[str, Any]] = None,
    context: Optional[ExecutionContext] = None,
) -> AsyncIterator[ExecutionResult]:
    """Execute GraphQL subscription (convenience function)."""
    executor = GraphQLExecutor(schema)
    async for result in executor.execute_subscription(subscription, variables, context=context):
        yield result


__all__ = [
    "GraphQLExecutor",
    "ExecutionContext",
    "ExecutionResult",
    "GraphQLError",
    "execute_query",
    "execute_mutation",
    "execute_subscription",
]
