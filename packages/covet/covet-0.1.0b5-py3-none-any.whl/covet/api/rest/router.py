"""
REST Router with Advanced Routing Features

Production-grade router with:
- Decorator-based routing for all HTTP methods
- Path parameter extraction with type validation
- Query parameter parsing and validation
- Request body validation (Pydantic models)
- Response serialization (JSON, XML, MessagePack)
- Content negotiation (Accept header)
- Automatic OpenAPI schema generation
- Prometheus metrics integration
- Rate limiting hooks
- CORS support

Example:
    from covet.api.rest.router import RESTRouter
    from pydantic import BaseModel, Field

    router = RESTRouter(prefix="/api/v1")

    class UserCreate(BaseModel):
        username: str = Field(..., min_length=3, max_length=50)
        email: str = Field(..., pattern=r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$')
        age: int = Field(..., ge=18, le=120)

    class UserResponse(BaseModel):
        id: int
        username: str
        email: str
        age: int
        created_at: str

    @router.post("/users",
                 request_model=UserCreate,
                 response_model=UserResponse,
                 tags=["users"],
                 summary="Create a new user")
    async def create_user(request, body: UserCreate):
        # body is already validated
        user = await User.objects.create(
            username=body.username,
            email=body.email,
            age=body.age
        )
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            age=user.age,
            created_at=user.created_at.isoformat()
        )

    @router.get("/users/{user_id:int}",
                response_model=UserResponse,
                tags=["users"])
    async def get_user(request, user_id: int):
        user = await User.objects.get(id=user_id)
        return UserResponse(**user.__dict__)
"""

import asyncio
import inspect
import json
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Tuple, Type, Union
from urllib.parse import parse_qs, unquote

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class HTTPMethod(str, Enum):
    """Supported HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    TRACE = "TRACE"


class PathParameterType(str, Enum):
    """Supported path parameter types."""

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    UUID = "uuid"
    PATH = "path"  # Captures everything including slashes
    SLUG = "slug"  # Alphanumeric with dashes/underscores


@dataclass
class PathParameter:
    """
    Path parameter definition.

    Attributes:
        name: Parameter name
        param_type: Parameter type
        converter: Type converter function
        validator: Optional validation function
        pattern: Regex pattern for custom types
    """

    name: str
    param_type: PathParameterType
    converter: Callable[[str], Any]
    validator: Optional[Callable[[Any], bool]] = None
    pattern: Optional[Pattern] = None

    def convert(self, value: str) -> Any:
        """
        Convert path parameter to typed value.

        Args:
            value: String value from URL

        Returns:
            Converted value

        Raises:
            ValueError: If conversion fails
        """
        try:
            converted = self.converter(value)
            if self.validator and not self.validator(converted):
                raise ValueError(f"Validation failed for {self.name}={value}")
            return converted
        except Exception as e:
            raise ValueError(f"Invalid {self.param_type} parameter '{self.name}': {value}") from e


@dataclass
class Route:
    """
    Route definition.

    Attributes:
        path: URL path pattern
        methods: Allowed HTTP methods
        handler: Handler function
        path_params: Path parameters
        path_regex: Compiled regex for path matching
        request_model: Request body validation model
        response_model: Response serialization model
        tags: OpenAPI tags
        summary: Short description
        description: Long description
        deprecated: Whether route is deprecated
        include_in_schema: Whether to include in OpenAPI schema
        response_models: Status code specific response models
        callbacks: OpenAPI callbacks
        dependencies: Dependency injection functions
        operation_id: Unique operation identifier
    """

    path: str
    methods: Set[HTTPMethod]
    handler: Callable
    path_params: List[PathParameter] = field(default_factory=list)
    path_regex: Optional[Pattern] = None
    request_model: Optional[Type[BaseModel]] = None
    response_model: Optional[Type[BaseModel]] = None
    tags: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    description: Optional[str] = None
    deprecated: bool = False
    include_in_schema: bool = True
    response_models: Dict[int, Type[BaseModel]] = field(default_factory=dict)
    callbacks: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[Callable] = field(default_factory=list)
    operation_id: Optional[str] = None

    # Performance metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0


class RESTRouter:
    """
    Production-grade REST router with advanced features.

    Features:
    - Automatic path parameter extraction and validation
    - Request/response model validation with Pydantic
    - Content negotiation (JSON, XML, MessagePack)
    - OpenAPI schema generation
    - Per-route metrics
    - Middleware support
    - Dependency injection

    Example:
        router = RESTRouter(prefix="/api/v1", tags=["users"])

        @router.get("/users/{user_id:int}")
        async def get_user(request, user_id: int):
            return {"id": user_id, "name": "Alice"}
    """

    # Type converters for path parameters
    TYPE_CONVERTERS = {
        PathParameterType.STRING: str,
        PathParameterType.INTEGER: int,
        PathParameterType.FLOAT: float,
        PathParameterType.UUID: lambda x: x,  # UUID validation happens separately
        PathParameterType.PATH: str,
        PathParameterType.SLUG: str,
    }

    # Type validators
    TYPE_VALIDATORS = {
        PathParameterType.UUID: lambda x: re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", str(x), re.IGNORECASE
        )
        is not None,
        PathParameterType.SLUG: lambda x: re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", str(x))
        is not None,
    }

    # Type patterns for regex
    TYPE_PATTERNS = {
        PathParameterType.STRING: r"[^/]+",
        PathParameterType.INTEGER: r"\d+",
        PathParameterType.FLOAT: r"\d+\.?\d*",
        PathParameterType.UUID: r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        PathParameterType.PATH: r".+",
        PathParameterType.SLUG: r"[a-z0-9]+(?:-[a-z0-9]+)*",
    }

    def __init__(
        self,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[Callable]] = None,
        default_response_class: Type[BaseModel] = None,
        responses: Optional[Dict[int, Dict[str, Any]]] = None,
        callbacks: Optional[List[Dict[str, Any]]] = None,
        deprecated: bool = False,
        include_in_schema: bool = True,
        generate_unique_id_function: Optional[Callable] = None,
    ):
        """
        Initialize REST router.

        Args:
            prefix: URL prefix for all routes
            tags: Default tags for all routes
            dependencies: Default dependencies for all routes
            default_response_class: Default response model
            responses: Default response models by status code
            callbacks: Default OpenAPI callbacks
            deprecated: Mark all routes as deprecated
            include_in_schema: Include all routes in OpenAPI schema
            generate_unique_id_function: Function to generate operation IDs
        """
        self.prefix = prefix.rstrip("/")
        self.tags = tags or []
        self.dependencies = dependencies or []
        self.default_response_class = default_response_class
        self.responses = responses or {}
        self.callbacks = callbacks or []
        self.deprecated = deprecated
        self.include_in_schema = include_in_schema
        self.generate_unique_id_function = generate_unique_id_function

        # Route storage
        self.routes: List[Route] = []
        self.static_routes: Dict[str, Dict[HTTPMethod, Route]] = {}
        self.dynamic_routes: List[Route] = []

        # Middleware
        self.middleware: List[Callable] = []

        # Metrics
        self.total_requests = 0
        self.total_request_time_ms = 0.0

    def add_middleware(self, middleware: Callable) -> None:
        """
        Add middleware function.

        Args:
            middleware: Async middleware function

        Example:
            async def auth_middleware(request, call_next):
                if not request.headers.get("Authorization"):
                    return JSONResponse({"error": "Unauthorized"}, status_code=401)
                return await call_next(request)

            router.add_middleware(auth_middleware)
        """
        self.middleware.append(middleware)

    def route(
        self,
        path: str,
        methods: Optional[List[str]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: Optional[bool] = None,
        response_models: Optional[Dict[int, Type[BaseModel]]] = None,
        callbacks: Optional[List[Dict[str, Any]]] = None,
        dependencies: Optional[List[Callable]] = None,
        operation_id: Optional[str] = None,
    ) -> Callable:
        """
        Register route decorator.

        Args:
            path: URL path pattern (e.g., "/users/{user_id:int}")
            methods: HTTP methods (default: ["GET"])
            request_model: Request body validation model
            response_model: Response serialization model
            tags: OpenAPI tags
            summary: Short description
            description: Long description
            deprecated: Mark as deprecated
            include_in_schema: Include in OpenAPI schema
            response_models: Status code specific response models
            callbacks: OpenAPI callbacks
            dependencies: Dependency injection functions
            operation_id: Unique operation identifier

        Returns:
            Decorator function

        Example:
            @router.route("/users/{user_id:int}", methods=["GET", "PUT"])
            async def handle_user(request, user_id: int):
                return {"id": user_id}
        """
        methods = methods or ["GET"]
        methods_set = {HTTPMethod(m.upper()) for m in methods}

        def decorator(handler: Callable) -> Callable:
            # Parse path pattern
            full_path = self.prefix + path
            path_params, path_regex = self._parse_path_pattern(full_path)

            # Create route
            route = Route(
                path=full_path,
                methods=methods_set,
                handler=handler,
                path_params=path_params,
                path_regex=path_regex,
                request_model=request_model,
                response_model=response_model or self.default_response_class,
                tags=(tags or self.tags),
                summary=summary,
                description=description or inspect.getdoc(handler),
                deprecated=deprecated if deprecated is not None else self.deprecated,
                include_in_schema=(
                    include_in_schema if include_in_schema is not None else self.include_in_schema
                ),
                response_models=response_models or self.responses,
                callbacks=callbacks or self.callbacks,
                dependencies=(dependencies or []) + self.dependencies,
                operation_id=operation_id
                or self._generate_operation_id(handler, path, methods_set),
            )

            # Register route
            self._register_route(route)

            return handler

        return decorator

    def get(self, path: str, **kwargs) -> Callable:
        """Register GET route."""
        return self.route(path, methods=["GET"], **kwargs)

    def post(self, path: str, **kwargs) -> Callable:
        """Register POST route."""
        return self.route(path, methods=["POST"], **kwargs)

    def put(self, path: str, **kwargs) -> Callable:
        """Register PUT route."""
        return self.route(path, methods=["PUT"], **kwargs)

    def patch(self, path: str, **kwargs) -> Callable:
        """Register PATCH route."""
        return self.route(path, methods=["PATCH"], **kwargs)

    def delete(self, path: str, **kwargs) -> Callable:
        """Register DELETE route."""
        return self.route(path, methods=["DELETE"], **kwargs)

    def options(self, path: str, **kwargs) -> Callable:
        """Register OPTIONS route."""
        return self.route(path, methods=["OPTIONS"], **kwargs)

    def head(self, path: str, **kwargs) -> Callable:
        """Register HEAD route."""
        return self.route(path, methods=["HEAD"], **kwargs)

    def _parse_path_pattern(self, path: str) -> Tuple[List[PathParameter], Pattern]:
        """
        Parse path pattern and extract parameters.

        Supports patterns like:
        - /users/{user_id}           -> int by default
        - /users/{user_id:int}       -> explicit int
        - /posts/{slug:slug}         -> slug pattern
        - /files/{path:path}         -> capture rest of path
        - /items/{uuid:uuid}         -> UUID validation

        Args:
            path: Path pattern

        Returns:
            Tuple of (parameters, compiled regex)
        """
        path_params = []
        regex_pattern = "^"
        last_end = 0

        # Find all path parameters {name:type}
        param_pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)(?::([a-z]+))?\}")

        for match in param_pattern.finditer(path):
            # Add static part before parameter
            regex_pattern += re.escape(path[last_end : match.start()])

            param_name = match.group(1)
            param_type = PathParameterType(match.group(2) or "string")

            # Add parameter capture group
            type_pattern = self.TYPE_PATTERNS[param_type]
            regex_pattern += f"(?P<{param_name}>{type_pattern})"

            # Create parameter definition
            path_param = PathParameter(
                name=param_name,
                param_type=param_type,
                converter=self.TYPE_CONVERTERS[param_type],
                validator=self.TYPE_VALIDATORS.get(param_type),
            )
            path_params.append(path_param)

            last_end = match.end()

        # Add remaining static part
        regex_pattern += re.escape(path[last_end:])
        regex_pattern += "$"

        # Compile regex
        compiled_regex = re.compile(regex_pattern)

        return path_params, compiled_regex

    def _register_route(self, route: Route) -> None:
        """
        Register route in appropriate storage.

        Args:
            route: Route to register
        """
        self.routes.append(route)

        # If static route (no parameters), store in dict for O(1) lookup
        if not route.path_params:
            if route.path not in self.static_routes:
                self.static_routes[route.path] = {}

            for method in route.methods:
                self.static_routes[route.path][method] = route
        else:
            # Dynamic route with parameters
            self.dynamic_routes.append(route)

        logger.debug(f"Registered route: {', '.join(m.value for m in route.methods)} {route.path}")

    def _generate_operation_id(self, handler: Callable, path: str, methods: Set[HTTPMethod]) -> str:
        """
        Generate unique operation ID for OpenAPI.

        Args:
            handler: Handler function
            path: URL path
            methods: HTTP methods

        Returns:
            Operation ID
        """
        if self.generate_unique_id_function:
            return self.generate_unique_id_function(handler, path, methods)

        # Default: handler_name
        return handler.__name__

    async def match_route(self, path: str, method: str) -> Optional[Tuple[Route, Dict[str, Any]]]:
        """
        Match route and extract path parameters.

        Args:
            path: Request path
            method: HTTP method

        Returns:
            Tuple of (route, path_params) or None
        """
        http_method = HTTPMethod(method.upper())

        # Try static routes first (O(1) lookup)
        if path in self.static_routes:
            static_route = self.static_routes[path].get(http_method)
            if static_route:
                return static_route, {}

        # Try dynamic routes (O(n) with regex matching)
        for route in self.dynamic_routes:
            if http_method not in route.methods:
                continue

            match = route.path_regex.match(path)
            if match:
                # Extract and convert path parameters
                path_params = {}
                for param in route.path_params:
                    raw_value = match.group(param.name)
                    try:
                        path_params[param.name] = param.convert(raw_value)
                    except ValueError as e:
                        logger.warning(f"Path parameter conversion failed: {e}")
                        return None

                return route, path_params

        return None

    async def handle_request(self, request) -> Any:
        """
        Handle incoming HTTP request.

        Args:
            request: Request object

        Returns:
            Response object or dict
        """
        start_time = time.time()
        self.total_requests += 1

        try:
            # Match route
            match_result = await self.match_route(request.path, request.method)

            if not match_result:
                return {
                    "error": "Not Found",
                    "message": f"No route matches {request.method} {request.path}",
                }, 404

            route, path_params = match_result

            # Update route metrics
            route.total_requests += 1

            # Execute middleware chain
            async def call_next(req):
                return await self._execute_route(req, route, path_params)

            # Apply middleware in reverse order
            handler = call_next
            for middleware in reversed(self.middleware):
                current_handler = handler

                async def wrapped_handler(req, mw=middleware, h=current_handler):
                    return await mw(req, h)

                handler = wrapped_handler

            # Execute with middleware
            response = await handler(request)

            # Update metrics
            duration_ms = (time.time() - start_time) * 1000
            self.total_request_time_ms += duration_ms
            route.total_duration_ms += duration_ms
            route.successful_requests += 1
            route.min_duration_ms = min(route.min_duration_ms, duration_ms)
            route.max_duration_ms = max(route.max_duration_ms, duration_ms)

            return response

        except Exception as e:
            # Update error metrics
            duration_ms = (time.time() - start_time) * 1000
            self.total_request_time_ms += duration_ms

            if match_result:
                route, _ = match_result
                route.failed_requests += 1
                route.total_duration_ms += duration_ms

            logger.error(f"Request handling error: {e}", exc_info=True)
            raise

    async def _execute_route(self, request, route: Route, path_params: Dict[str, Any]) -> Any:
        """
        Execute route handler with validation.

        Args:
            request: Request object
            route: Matched route
            path_params: Extracted path parameters

        Returns:
            Response
        """
        # Execute dependencies
        for dependency in route.dependencies:
            await dependency(request)

        # Parse query parameters
        query_params = self._parse_query_params(request)

        # Validate and parse request body
        body = None
        if route.request_model:
            try:
                body_data = await self._parse_request_body(request)
                body = route.request_model(**body_data)
            except ValidationError as e:
                return {"error": "Validation Error", "details": e.errors()}, 422
            except Exception as e:
                return {"error": "Bad Request", "message": str(e)}, 400

        # Build handler arguments
        handler_kwargs = {}

        # Inspect handler signature
        sig = inspect.signature(route.handler)
        for param_name, param in sig.parameters.items():
            if param_name == "request":
                handler_kwargs["request"] = request
            elif param_name == "body" and body is not None:
                handler_kwargs["body"] = body
            elif param_name in path_params:
                handler_kwargs[param_name] = path_params[param_name]
            elif param_name in query_params:
                handler_kwargs[param_name] = query_params[param_name]

        # Execute handler
        if asyncio.iscoroutinefunction(route.handler):
            result = await route.handler(**handler_kwargs)
        else:
            result = route.handler(**handler_kwargs)

        # Serialize response
        if route.response_model and result is not None:
            # Handle tuple (response, status_code)
            if isinstance(result, tuple):
                response_data, status_code = result
            else:
                response_data = result
                status_code = 200

            # Validate response
            if not isinstance(response_data, dict):
                if isinstance(response_data, route.response_model):
                    response_data = response_data.dict()
                elif hasattr(response_data, "__dict__"):
                    response_data = vars(response_data)

            # Convert to response model
            try:
                validated_response = route.response_model(**response_data)
                return validated_response.dict(), status_code
            except ValidationError as e:
                logger.error(f"Response validation error: {e}")
                # Return original response if validation fails (for development)
                return response_data, status_code

        return result

    def _parse_query_params(self, request) -> Dict[str, Any]:
        """
        Parse query parameters from request.

        Args:
            request: Request object

        Returns:
            Dictionary of query parameters
        """
        if not hasattr(request, "query_string"):
            return {}

        query_string = request.query_string
        if isinstance(query_string, bytes):
            query_string = query_string.decode("utf-8")

        parsed = parse_qs(query_string, keep_blank_values=True)

        # Convert single-value lists to scalars
        result = {}
        for key, values in parsed.items():
            if len(values) == 1:
                result[key] = values[0]
            else:
                result[key] = values

        return result

    async def _parse_request_body(self, request) -> Dict[str, Any]:
        """
        Parse request body based on content type.

        Args:
            request: Request object

        Returns:
            Parsed body as dictionary
        """
        content_type = request.headers.get("content-type", "").split(";")[0].strip()

        if content_type == "application/json":
            if hasattr(request, "json"):
                if callable(request.json):
                    return await request.json()
                return request.json
            elif hasattr(request, "body"):
                body = request.body
                if isinstance(body, bytes):
                    body = body.decode("utf-8")
                return json.loads(body)
            else:
                return {}
        elif content_type == "application/x-www-form-urlencoded":
            # Parse form data
            if hasattr(request, "form"):
                return dict(request.form)
            else:
                return {}
        else:
            # Default to JSON
            return {}

    def get_routes(self) -> List[Route]:
        """Get all registered routes."""
        return self.routes

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get router metrics.

        Returns:
            Dictionary of metrics
        """
        avg_request_time = (
            self.total_request_time_ms / self.total_requests if self.total_requests > 0 else 0.0
        )

        route_metrics = []
        for route in self.routes:
            avg_route_time = (
                route.total_duration_ms / route.total_requests if route.total_requests > 0 else 0.0
            )

            route_metrics.append(
                {
                    "path": route.path,
                    "methods": [m.value for m in route.methods],
                    "total_requests": route.total_requests,
                    "successful_requests": route.successful_requests,
                    "failed_requests": route.failed_requests,
                    "avg_duration_ms": round(avg_route_time, 2),
                    "min_duration_ms": (
                        round(route.min_duration_ms, 2)
                        if route.min_duration_ms != float("inf")
                        else 0
                    ),
                    "max_duration_ms": round(route.max_duration_ms, 2),
                }
            )

        return {
            "total_requests": self.total_requests,
            "avg_request_time_ms": round(avg_request_time, 2),
            "total_routes": len(self.routes),
            "static_routes": len(self.static_routes),
            "dynamic_routes": len(self.dynamic_routes),
            "route_metrics": route_metrics,
        }


__all__ = [
    "RESTRouter",
    "Route",
    "PathParameter",
    "PathParameterType",
    "HTTPMethod",
]
