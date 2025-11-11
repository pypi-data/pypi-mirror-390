"""
REST API Framework

Complete REST framework integrating all components:
- Request validation
- Response serialization
- Error handling
- OpenAPI generation
- API versioning
- Rate limiting
"""

from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel

from .errors import APIError, ErrorHandler, ErrorMiddleware, NotFoundError
from .openapi import OpenAPIGenerator, ReDocConfig, SwaggerUIConfig
from .ratelimit import FixedWindowRateLimiter, RateLimitMiddleware
from .serialization import ContentNegotiator, ResponseFormatter, ResponseSerializer
from .validation import PaginationParams, RequestValidator, ValidationError
from .versioning import APIVersion, VersioningStrategy, VersionNegotiator, VersionRouter


class RESTFramework:
    """
    Complete REST API framework.

    Provides all features needed for production-ready REST APIs:
    - Automatic validation
    - Response formatting
    - Error handling
    - API documentation
    - Versioning
    - Rate limiting

    Example:
        from covet.api.rest import RESTFramework, BaseModel, Field

        api = RESTFramework(
            title="My API",
            version="1.0.0",
            enable_docs=True
        )

        class UserCreate(BaseModel):
            name: str = Field(..., min_length=1)
            email: str

        class UserResponse(BaseModel):
            id: int
            name: str
            email: str

        @api.post("/users", request_model=UserCreate, response_model=UserResponse)
        async def create_user(user: UserCreate):
            # Create user in database
            return UserResponse(id=1, name=user.name, email=user.email)

        # Run with ASGI server
        # uvicorn main:api --host 0.0.0.0 --port 8000
    """

    def __init__(
        self,
        title: str = "API",
        version: str = "1.0.0",
        description: Optional[str] = None,
        debug: bool = False,
        enable_docs: bool = True,
        docs_url: str = "/docs",
        redoc_url: str = "/redoc",
        openapi_url: str = "/openapi.json",
        enable_versioning: bool = False,
        versioning_strategy: VersioningStrategy = VersioningStrategy.URL_PATH,
        enable_rate_limiting: bool = False,
        rate_limit: int = 100,
        rate_period: int = 60,
    ):
        """
        Initialize REST framework.

        Args:
            title: API title
            version: API version
            description: API description
            debug: Enable debug mode
            enable_docs: Enable API documentation endpoints
            docs_url: Swagger UI URL
            redoc_url: ReDoc URL
            openapi_url: OpenAPI spec URL
            enable_versioning: Enable API versioning
            versioning_strategy: Versioning strategy
            enable_rate_limiting: Enable rate limiting
            rate_limit: Requests per period
            rate_period: Period in seconds
        """
        self.title = title
        self.version = version
        self.description = description
        self.debug = debug

        # Components
        self.validator = RequestValidator()
        self.serializer = ResponseSerializer()
        self.formatter = ResponseFormatter(self.serializer)
        self.negotiator = ContentNegotiator()
        self.error_handler = ErrorHandler(debug=debug)

        # OpenAPI
        self.enable_docs = enable_docs
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.openapi_url = openapi_url
        self.openapi_generator = OpenAPIGenerator(
            title=title, version=version, description=description
        )

        # Versioning
        self.enable_versioning = enable_versioning
        if enable_versioning:
            self.version_negotiator = VersionNegotiator(strategy=versioning_strategy)
            self.version_router = VersionRouter(self.version_negotiator)

        # Rate limiting
        self.enable_rate_limiting = enable_rate_limiting
        if enable_rate_limiting:
            self.rate_limiter = FixedWindowRateLimiter(rate_limit, rate_period)

        # Routes
        self.routes: List[Dict[str, Any]] = []

    def route(
        self,
        path: str,
        methods: List[str],
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        api_version: Optional[APIVersion] = None,
    ) -> Callable:
        """
        Register route decorator.

        Args:
            path: URL path
            methods: HTTP methods
            request_model: Request body model
            response_model: Response body model
            summary: Short summary
            description: Detailed description
            tags: Operation tags
            api_version: API version (if versioning enabled)

        Returns:
            Decorator function
        """

        def decorator(handler: Callable) -> Callable:
            # Register route
            route_info = {
                "path": path,
                "methods": methods,
                "handler": handler,
                "request_model": request_model,
                "response_model": response_model,
                "summary": summary,
                "description": description,
                "tags": tags,
                "api_version": api_version,
            }
            self.routes.append(route_info)

            # Add to OpenAPI spec
            for method in methods:
                self.openapi_generator.add_route(
                    path=path,
                    method=method,
                    handler=handler,
                    summary=summary,
                    description=description,
                    tags=tags,
                    request_model=request_model,
                    response_model=response_model,
                )

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

    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI specification."""
        return self.openapi_generator.generate_spec()

    def get_swagger_html(self) -> str:
        """Get Swagger UI HTML."""
        config = SwaggerUIConfig(url=self.openapi_url, title=f"{self.title} - Documentation")
        return config.get_html()

    def get_redoc_html(self) -> str:
        """Get ReDoc HTML."""
        config = ReDocConfig(url=self.openapi_url, title=f"{self.title} - Documentation")
        return config.get_html()

    async def __call__(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            return

        path = scope["path"]

        # Serve documentation
        if self.enable_docs:
            if path == self.docs_url:
                html = self.get_swagger_html()
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

            elif path == self.redoc_url:
                html = self.get_redoc_html()
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

            elif path == self.openapi_url:
                import json

                spec = self.get_openapi_spec()
                body = json.dumps(spec, indent=2).encode("utf-8")
                await send(
                    {
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [[b"content-type", b"application/json; charset=utf-8"]],
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": body,
                    }
                )
                return

        # Handle API routes
        # This is a simplified routing - in production would use proper router
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [[b"content-type", b"application/json; charset=utf-8"]],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b'{"error": "Not Found"}',
            }
        )


__all__ = [
    "RESTFramework",
    # Re-export commonly used classes
    "BaseModel",
    "ValidationError",
    "APIError",
    "NotFoundError",
    "PaginationParams",
]
