"""
CovetPy Production-Grade Middleware System

A comprehensive middleware system providing:
- High-performance middleware pipeline execution
- Before/after request hooks with error handling
- Multiple middleware types (function, class, decorator-based)
- Conditional middleware execution
- Dynamic middleware registration with priority ordering
- Per-route middleware support
- Built-in production-ready middleware components
- Type safety and async support throughout
"""

import asyncio
import gzip
import hashlib
import inspect
import json
import re
import secrets
import time
import urllib.parse
import weakref
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    Union,
    runtime_checkable,
)

import brotli

from .exceptions import HTTPException
from .http import Request, Response, error_response, json_response


class MiddlewareType(Enum):
    """Types of middleware execution points"""

    REQUEST = "request"  # Before handler execution
    RESPONSE = "response"  # After handler execution
    ERROR = "error"  # Error handling
    WEBSOCKET = "websocket"  # WebSocket connections


class Priority(Enum):
    """Middleware priority levels"""

    CRITICAL = 0  # Security, auth
    HIGH = 100  # CORS, rate limiting
    NORMAL = 500  # Logging, compression
    LOW = 1000  # Analytics, monitoring


@dataclass
class MiddlewareConfig:
    """Configuration for middleware instances"""

    name: str = ""
    enabled: bool = True
    priority: int = Priority.NORMAL.value
    routes: Optional[List[str]] = None  # Route patterns to apply to
    exclude_routes: Optional[List[str]] = None  # Route patterns to exclude
    conditions: Optional[Dict[str, Any]] = None  # Custom conditions
    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            self.name = f"middleware_{id(self)}"


@runtime_checkable
class MiddlewareProtocol(Protocol):
    """Protocol for middleware objects"""

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and call next middleware/handler"""
        ...


class BaseMiddleware(ABC):
    """Abstract base class for middleware implementations"""

    def __init__(self, config: Optional[MiddlewareConfig] = None):
        self.config = config or MiddlewareConfig()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize middleware (called once during setup)"""
        if not self._initialized:
            await self.setup()
            self._initialized = True

    async def setup(self) -> None:
        """Override this method for custom initialization"""

    async def cleanup(self) -> None:
        """Override this method for cleanup tasks"""

    @abstractmethod
    async def process_request(self, request: Request) -> Optional[Union[Request, Response]]:
        """Process incoming request. Return modified request or early response"""

    @abstractmethod
    async def process_response(self, request: Request, response: Response) -> Response:
        """Process outgoing response"""

    async def process_error(self, request: Request, error: Exception) -> Optional[Response]:
        """Process error. Return response to handle error or None to propagate"""
        return None

    def should_apply(self, request: Request) -> bool:
        """Check if middleware should apply to this request"""
        if not self.config.enabled:
            return False

        # Check route patterns
        if self.config.routes:
            if not any(self._match_route(request.path, pattern) for pattern in self.config.routes):
                return False

        if self.config.exclude_routes:
            if any(
                self._match_route(request.path, pattern) for pattern in self.config.exclude_routes
            ):
                return False

        # Check custom conditions
        if self.config.conditions:
            if not self._check_conditions(request):
                return False

        return True

    def _match_route(self, path: str, pattern: str) -> bool:
        """Match path against route pattern (supports wildcards)"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        return path == pattern

    def _check_conditions(self, request: Request) -> bool:
        """Check custom conditions"""
        conditions = self.config.conditions or {}

        for key, value in conditions.items():
            if key == "method" and request.method not in value:
                return False
            elif key == "content_type" and value not in request.content_type:
                return False
            elif key == "header" and not all(request.headers.get(h) == v for h, v in value.items()):
                return False

        return True

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Standard middleware interface"""
        if not self.should_apply(request):
            return await call_next(request)

        try:
            # Process request
            result = await self.process_request(request)

            # If middleware returns a response, short-circuit
            if isinstance(result, Response):
                return result

            # Use modified request if returned
            if isinstance(result, Request):
                request = result

            # Call next middleware/handler
            response = await call_next(request)

            # Process response
            return await self.process_response(request, response)

        except Exception as error:
            # Try to handle error
            error_response = await self.process_error(request, error)
            if error_response:
                return error_response
            raise


class FunctionMiddleware(BaseMiddleware):
    """Wrapper for function-based middleware"""

    def __init__(
        self,
        func: Callable[[Request, Callable], Awaitable[Response]],
        config: Optional[MiddlewareConfig] = None,
    ):
        super().__init__(config)
        self.func = func
        self._is_async = inspect.iscoroutinefunction(func)

    async def process_request(self, request: Request) -> Optional[Request]:
        # Function middleware handles the entire flow
        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        return response

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not self.should_apply(request):
            return await call_next(request)

        if self._is_async:
            return await self.func(request, call_next)
        else:
            # Wrap sync function
            return self.func(request, call_next)


class MiddlewareStack:
    """High-performance middleware execution pipeline"""

    def __init__(self):
        self._middleware: List[Tuple[BaseMiddleware, int]] = []  # (middleware, priority)
        self._compiled_stack: Optional[List[BaseMiddleware]] = None
        self._route_middleware: Dict[str, List[BaseMiddleware]] = {}
        self._middleware_cache: Dict[str, List[BaseMiddleware]] = {}
        self._stats = {
            "total_requests": 0,
            "middleware_executions": defaultdict(int),
            "execution_times": defaultdict(list),
        }

    def add(
        self,
        middleware: Union[BaseMiddleware, Callable, Type[BaseMiddleware]],
        config: Optional[MiddlewareConfig] = None,
        priority: Optional[int] = None,
    ) -> None:
        """Add middleware to the stack"""

        # Convert different middleware types to BaseMiddleware
        if isinstance(middleware, type) and issubclass(middleware, BaseMiddleware):
            # Class - instantiate it
            middleware_instance = middleware(config)
        elif isinstance(middleware, BaseMiddleware):
            # Already an instance
            middleware_instance = middleware
            if config and not middleware_instance.config.name:
                middleware_instance.config = config
        elif callable(middleware):
            # Function - wrap it
            middleware_instance = FunctionMiddleware(middleware, config)
        else:
            raise ValueError(f"Invalid middleware type: {type(middleware)}")

        # Set priority
        if priority is not None:
            middleware_instance.config.priority = priority
        elif config and config.priority:
            middleware_instance.config.priority = config.priority

        self._middleware.append((middleware_instance, middleware_instance.config.priority))
        self._compiled_stack = None  # Mark for recompilation
        self._middleware_cache.clear()  # Clear cache

    def remove(self, name: str) -> bool:
        """Remove middleware by name"""
        for i, (middleware, _) in enumerate(self._middleware):
            if middleware.config.name == name:
                del self._middleware[i]
                self._compiled_stack = None
                self._middleware_cache.clear()
                return True
        return False

    def insert(
        self,
        index: int,
        middleware: Union[BaseMiddleware, Callable],
        config: Optional[MiddlewareConfig] = None,
    ) -> None:
        """Insert middleware at specific position"""
        if isinstance(middleware, BaseMiddleware):
            middleware_instance = middleware
        elif callable(middleware):
            middleware_instance = FunctionMiddleware(middleware, config)
        else:
            raise ValueError(f"Invalid middleware type: {type(middleware)}")

        priority = middleware_instance.config.priority
        self._middleware.insert(index, (middleware_instance, priority))
        self._compiled_stack = None
        self._middleware_cache.clear()

    def add_route_middleware(
        self,
        route_pattern: str,
        middleware: Union[BaseMiddleware, Callable],
        config: Optional[MiddlewareConfig] = None,
    ) -> None:
        """Add middleware that applies only to specific routes"""
        if isinstance(middleware, BaseMiddleware):
            middleware_instance = middleware
        elif callable(middleware):
            middleware_instance = FunctionMiddleware(middleware, config)
        else:
            raise ValueError(f"Invalid middleware type: {type(middleware)}")

        if route_pattern not in self._route_middleware:
            self._route_middleware[route_pattern] = []

        self._route_middleware[route_pattern].append(middleware_instance)
        self._middleware_cache.clear()

    def _compile_stack(self) -> List[BaseMiddleware]:
        """Compile middleware stack sorted by priority"""
        if self._compiled_stack is None:
            # Sort by priority (lower numbers = higher priority)
            sorted_middleware = sorted(self._middleware, key=lambda x: x[1])
            self._compiled_stack = [m for m, _ in sorted_middleware]

        return self._compiled_stack

    def _get_middleware_for_request(self, request: Request) -> List[BaseMiddleware]:
        """Get all middleware that should apply to this request"""
        cache_key = f"{request.method}:{request.path}"

        if cache_key in self._middleware_cache:
            return self._middleware_cache[cache_key]

        middleware_list = []

        # Add global middleware
        for middleware in self._compile_stack():
            if middleware.should_apply(request):
                middleware_list.append(middleware)

        # Add route-specific middleware
        for pattern, route_middleware in self._route_middleware.items():
            if self._match_route_pattern(request.path, pattern):
                for middleware in route_middleware:
                    if middleware.should_apply(request):
                        middleware_list.append(middleware)

        # Sort by priority
        middleware_list.sort(key=lambda m: m.config.priority)

        # Cache the result
        self._middleware_cache[cache_key] = middleware_list

        return middleware_list

    def _match_route_pattern(self, path: str, pattern: str) -> bool:
        """Match path against route pattern"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        if "{" in pattern or "<" in pattern:
            # Convert to regex pattern
            regex_pattern = pattern
            regex_pattern = re.sub(r"\{[^}]+\}", r"[^/]+", regex_pattern)
            regex_pattern = re.sub(r"<[^>]+>", r"[^/]+", regex_pattern)
            return bool(re.match(f"^{regex_pattern}$", path))
        return path == pattern

    async def process(
        self, request: Request, handler: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request through middleware pipeline"""
        self._stats["total_requests"] += 1

        # Get applicable middleware
        middleware_list = self._get_middleware_for_request(request)

        if not middleware_list:
            # No middleware, call handler directly
            return await handler(request)

        # Create the middleware chain
        async def create_chain(
            index: int = 0,
        ) -> Callable[[Request], Awaitable[Response]]:
            if index >= len(middleware_list):
                # End of chain, call the actual handler
                return handler

            middleware = middleware_list[index]
            next_middleware = await create_chain(index + 1)

            async def middleware_wrapper(req: Request) -> Response:
                start_time = time.time()
                try:
                    self._stats["middleware_executions"][middleware.config.name] += 1
                    response = await middleware(req, next_middleware)
                    return response
                finally:
                    execution_time = time.time() - start_time
                    self._stats["execution_times"][middleware.config.name].append(execution_time)

            return middleware_wrapper

        # Execute the chain
        chain = await create_chain()
        return await chain(request)

    async def initialize_all(self) -> None:
        """Initialize all middleware"""
        for middleware, _ in self._middleware:
            await middleware.initialize()

        for route_middleware in self._route_middleware.values():
            for middleware in route_middleware:
                await middleware.initialize()

    async def cleanup_all(self) -> None:
        """Cleanup all middleware"""
        for middleware, _ in self._middleware:
            await middleware.cleanup()

        for route_middleware in self._route_middleware.values():
            for middleware in route_middleware:
                await middleware.cleanup()

    def get_stats(self) -> Dict[str, Any]:
        """Get middleware execution statistics"""
        stats = self._stats.copy()

        # Calculate average execution times
        avg_times = {}
        for name, times in self._stats["execution_times"].items():
            if times:
                avg_times[name] = sum(times) / len(times)

        stats["average_execution_times"] = avg_times
        return stats

    def list_middleware(self) -> List[Dict[str, Any]]:
        """List all registered middleware"""
        middleware_info = []

        for middleware, priority in self._middleware:
            middleware_info.append(
                {
                    "name": middleware.config.name,
                    "type": type(middleware).__name__,
                    "priority": priority,
                    "enabled": middleware.config.enabled,
                    "routes": middleware.config.routes,
                    "exclude_routes": middleware.config.exclude_routes,
                }
            )

        return sorted(middleware_info, key=lambda x: x["priority"])


# Decorator functions for easy middleware creation
def middleware(
    name: str = "",
    priority: int = Priority.NORMAL.value,
    routes: Optional[List[str]] = None,
    exclude_routes: Optional[List[str]] = None,
    conditions: Optional[Dict[str, Any]] = None,
    **options,
):
    """Decorator to create middleware from functions"""

    def decorator(func: Callable) -> FunctionMiddleware:
        config = MiddlewareConfig(
            name=name or func.__name__,
            priority=priority,
            routes=routes,
            exclude_routes=exclude_routes,
            conditions=conditions,
            options=options,
        )

        if inspect.iscoroutinefunction(func):
            return FunctionMiddleware(func, config)
        else:
            # Wrap sync function to make it async
            @wraps(func)
            async def async_wrapper(request: Request, call_next: Callable) -> Response:
                return func(request, call_next)

            return FunctionMiddleware(async_wrapper, config)

    return decorator


def route_middleware(route_pattern: str, **middleware_kwargs):
    """Decorator to create route-specific middleware"""

    def decorator(func: Callable) -> FunctionMiddleware:
        middleware_kwargs.setdefault("routes", [route_pattern])
        return middleware(**middleware_kwargs)(func)

    return decorator


# Factory function
def create_middleware_stack() -> MiddlewareStack:
    """Create a new middleware stack"""
    return MiddlewareStack()


# Middleware composition utilities
class MiddlewareComposer:
    """Utility for composing multiple middleware into one"""

    @staticmethod
    def compose(*middleware_items) -> BaseMiddleware:
        """Compose multiple middleware into a single middleware"""

        class ComposedMiddleware(BaseMiddleware):
            def __init__(self):
                super().__init__(MiddlewareConfig(name="composed_middleware"))
                self.middleware_list = []

                for item in middleware_items:
                    if isinstance(item, BaseMiddleware):
                        self.middleware_list.append(item)
                    elif callable(item):
                        self.middleware_list.append(FunctionMiddleware(item))
                    else:
                        raise ValueError(f"Invalid middleware type: {type(item)}")

            async def process_request(self, request: Request) -> Optional[Request]:
                for middleware in self.middleware_list:
                    result = await middleware.process_request(request)
                    if isinstance(result, Response):
                        return result
                    elif isinstance(result, Request):
                        request = result
                return request

            async def process_response(self, request: Request, response: Response) -> Response:
                # Process in reverse order for response
                for middleware in reversed(self.middleware_list):
                    response = await middleware.process_response(request, response)
                return response

        return ComposedMiddleware()


# Context management for middleware data
class MiddlewareContext:
    """Context object for sharing data between middleware"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._request_id: Optional[str] = None

    def set(self, key: str, value: Any) -> None:
        """Set context value"""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get context value"""
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        """Check if context has key"""
        return key in self._data

    def delete(self, key: str) -> None:
        """Delete context value"""
        self._data.pop(key, None)

    def clear(self) -> None:
        """Clear all context data"""
        self._data.clear()

    @property
    def request_id(self) -> str:
        """Get or generate request ID"""
        if self._request_id is None:
            import uuid

            self._request_id = str(uuid.uuid4())
        return self._request_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return self._data.copy()


# Add context to request objects
def add_middleware_context(request: Request) -> MiddlewareContext:
    """Add middleware context to request"""
    if not hasattr(request, "middleware_context"):
        request.middleware_context = MiddlewareContext()
    return request.middleware_context


# Export main classes and functions
__all__ = [
    "MiddlewareType",
    "Priority",
    "MiddlewareConfig",
    "MiddlewareProtocol",
    "BaseMiddleware",
    "FunctionMiddleware",
    "MiddlewareStack",
    "MiddlewareComposer",
    "MiddlewareContext",
    "middleware",
    "route_middleware",
    "create_middleware_stack",
    "add_middleware_context",
]
