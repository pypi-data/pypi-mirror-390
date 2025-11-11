"""

logger = logging.getLogger(__name__)

CovetPy Middleware System Examples and Usage Guide

This file demonstrates how to use the CovetPy middleware system in various scenarios:
- Basic middleware creation and usage
- Built-in middleware configuration
- Custom middleware development
- Advanced patterns and composition
- Performance optimization techniques
- Production deployment examples
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .builtin_middleware import (
    CompressionMiddleware,
    CORSMiddleware,
    CSRFMiddleware,
    RateLimitingMiddleware,
    RateLimitRule,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    SessionMiddleware,
    create_compression_middleware,
    create_cors_middleware,
    create_csrf_middleware,
    create_rate_limiting_middleware,
    create_request_id_middleware,
    create_request_logging_middleware,
    create_security_headers_middleware,
    create_session_middleware,
)
from .http import Request, Response, error_response, json_response

# Import the middleware system
from .middleware_system import (
    BaseMiddleware,
    MiddlewareComposer,
    MiddlewareConfig,
    MiddlewareStack,
    Priority,
    add_middleware_context,
    create_middleware_stack,
    middleware,
    route_middleware,
)

# ============================================================================
# BASIC MIDDLEWARE EXAMPLES
# ============================================================================


# Example 1: Simple Function-Based Middleware
@middleware(name="timing_middleware", priority=Priority.NORMAL.value)
async def timing_middleware(request: Request, call_next) -> Response:
    """Middleware that measures request processing time"""
    start_time = time.time()

    # Add start time to request context
    add_middleware_context(request)
    request.middleware_context.set("start_time", start_time)

    # Process request
    response = await call_next(request)

    # Calculate processing time
    end_time = time.time()
    processing_time = (end_time - start_time) * 1000  # Convert to milliseconds

    # Add timing header
    response.headers["X-Processing-Time"] = f"{processing_time:.2f}ms"

    return response


# Example 2: Class-Based Middleware
class APIKeyAuthMiddleware(BaseMiddleware):
    """Middleware for API key authentication"""

    def __init__(self, api_keys: List[str], config: Optional[MiddlewareConfig] = None):
        if config is None:
            config = MiddlewareConfig(
                name="api_key_auth",
                priority=Priority.CRITICAL.value,
                routes=["/api/*"],  # Only apply to API routes
                exclude_routes=["/api/public/*"],  # Exclude public routes
            )

        super().__init__(config)
        self.api_keys = set(api_keys)

    async def process_request(self, request: Request) -> Optional[Response]:
        """Check for valid API key"""
        api_key = request.headers.get("x-api-key") or request.query.get("api_key")

        if not api_key:
            return error_response("API key required", status_code=401)

        if api_key not in self.api_keys:
            return error_response("Invalid API key", status_code=403)

        # Add authentication info to context
        add_middleware_context(request)
        request.middleware_context.set("authenticated", True)
        request.middleware_context.set("auth_method", "api_key")

        return None  # Continue processing

    async def process_response(self, request: Request, response: Response) -> Response:
        """Add authentication headers to response"""
        response.headers["X-Auth-Method"] = "API-Key"
        return response


# Example 3: Route-Specific Middleware
@route_middleware("/admin/*", priority=Priority.HIGH.value)
async def admin_only_middleware(request: Request, call_next) -> Response:
    """Middleware that ensures only admin users can access admin routes"""

    # Check if user is authenticated and is admin
    user_role = request.headers.get("x-user-role", "guest")

    if user_role != "admin":
        return error_response("Admin access required", status_code=403)

    # Add admin context
    add_middleware_context(request)
    request.middleware_context.set("is_admin", True)

    response = await call_next(request)
    response.headers["X-Admin-Access"] = "true"

    return response


# ============================================================================
# ADVANCED MIDDLEWARE PATTERNS
# ============================================================================


# Example 4: Caching Middleware
class CacheMiddleware(BaseMiddleware):
    """Simple in-memory caching middleware"""

    def __init__(
        self,
        ttl: int = 300,
        max_size: int = 1000,
        config: Optional[MiddlewareConfig] = None,
    ):
        if config is None:
            config = MiddlewareConfig(
                name="cache_middleware",
                priority=Priority.NORMAL.value,
                conditions={"method": ["GET"]},  # Only cache GET requests
            )

        super().__init__(config)
        self.ttl = ttl  # Time to live in seconds
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        return f"{request.method}:{request.path}:{request.query_string}"

    def _is_cached_response_valid(self, cached_item: Dict[str, Any]) -> bool:
        """Check if cached response is still valid"""
        return time.time() - cached_item["timestamp"] < self.ttl

    def _cleanup_cache(self) -> None:
        """Remove expired items from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items() if current_time - item["timestamp"] > self.ttl
        ]

        for key in expired_keys:
            del self.cache[key]

    async def process_request(self, request: Request) -> Optional[Response]:
        """Check cache for existing response"""
        cache_key = self._generate_cache_key(request)

        if cache_key in self.cache:
            cached_item = self.cache[cache_key]

            if self._is_cached_response_valid(cached_item):
                # Return cached response
                response = Response(
                    content=cached_item["content"],
                    status_code=cached_item["status_code"],
                    headers=cached_item["headers"],
                )
                response.headers["X-Cache"] = "HIT"
                return response
            else:
                # Remove expired item
                del self.cache[cache_key]

        # Add cache context for response processing
        add_middleware_context(request)
        request.middleware_context.set("cache_key", cache_key)

        return None

    async def process_response(self, request: Request, response: Response) -> Response:
        """Cache successful responses"""
        if response.status_code == 200:
            context = getattr(request, "middleware_context", None)
            if context:
                cache_key = context.get("cache_key")
                if cache_key:
                    # Cleanup old entries if cache is full
                    if len(self.cache) >= self.max_size:
                        self._cleanup_cache()

                    # Cache the response
                    self.cache[cache_key] = {
                        "content": response.content,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "timestamp": time.time(),
                    }

                    response.headers["X-Cache"] = "MISS"

        return response


# Example 5: Request Validation Middleware
class JSONValidationMiddleware(BaseMiddleware):
    """Middleware that validates JSON request bodies against schemas"""

    def __init__(
        self,
        schemas: Dict[str, Dict[str, Any]],
        config: Optional[MiddlewareConfig] = None,
    ):
        if config is None:
            config = MiddlewareConfig(
                name="json_validation",
                priority=Priority.HIGH.value,
                conditions={"method": ["POST", "PUT", "PATCH"]},
            )

        super().__init__(config)
        self.schemas = schemas  # Route pattern -> JSON schema mapping

    def _validate_json_schema(self, data: Any, schema: Dict[str, Any]) -> Optional[str]:
        """Simple JSON schema validation (in production, use jsonschema library)"""
        required_fields = schema.get("required", [])
        properties = schema.get("properties", {})

        if not isinstance(data, dict):
            return "Request body must be a JSON object"

        # Check required fields
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"

        # Check field types
        for field, field_schema in properties.items():
            if field in data:
                expected_type = field_schema.get("type")
                actual_value = data[field]

                if expected_type == "string" and not isinstance(actual_value, str):
                    return f"Field '{field}' must be a string"
                elif expected_type == "integer" and not isinstance(actual_value, int):
                    return f"Field '{field}' must be an integer"
                elif expected_type == "boolean" and not isinstance(actual_value, bool):
                    return f"Field '{field}' must be a boolean"

        return None  # Valid

    async def process_request(self, request: Request) -> Optional[Response]:
        """Validate JSON request body"""
        # Find matching schema
        schema = None
        for pattern, pattern_schema in self.schemas.items():
            if self._match_route(request.path, pattern):
                schema = pattern_schema
                break

        if not schema:
            return None  # No schema defined for this route

        # Parse JSON body
        try:
            if hasattr(request, "_body") and request._body:
                json_data = json.loads(request._body.decode("utf-8"))
            else:
                return error_response("Request body is required", status_code=400)
        except json.JSONDecodeError:
            return error_response("Invalid JSON in request body", status_code=400)

        # Validate against schema
        validation_error = self._validate_json_schema(json_data, schema)
        if validation_error:
            return error_response(validation_error, status_code=400)

        # Add validated data to context
        add_middleware_context(request)
        request.middleware_context.set("validated_json", json_data)

        return None

    async def process_response(self, request: Request, response: Response) -> Response:
        """Add validation headers"""
        response.headers["X-JSON-Validated"] = "true"
        return response


# Example 6: Database Transaction Middleware
class DatabaseTransactionMiddleware(BaseMiddleware):
    """Middleware that wraps requests in database transactions"""

    def __init__(self, db_pool, config: Optional[MiddlewareConfig] = None):
        if config is None:
            config = MiddlewareConfig(
                name="db_transaction",
                priority=Priority.HIGH.value,
                conditions={"method": ["POST", "PUT", "PATCH", "DELETE"]},
            )

        super().__init__(config)
        self.db_pool = db_pool

    async def process_request(self, request: Request) -> Optional[Request]:
        """Start database transaction"""
        try:
            # Get database connection from pool
            connection = await self.db_pool.acquire()
            transaction = await connection.begin()

            # Store in request context
            add_middleware_context(request)
            request.middleware_context.set("db_connection", connection)
            request.middleware_context.set("db_transaction", transaction)

        except Exception as e:
            return error_response(f"Database error: {str(e)}", status_code=500)

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Commit or rollback transaction based on response status"""
        context = getattr(request, "middleware_context", None)
        if not context:
            return response

        connection = context.get("db_connection")
        transaction = context.get("db_transaction")

        if connection and transaction:
            try:
                if response.status_code < 400:
                    # Success - commit transaction
                    await transaction.commit()
                    response.headers["X-DB-Status"] = "committed"
                else:
                    # Error - rollback transaction
                    await transaction.rollback()
                    response.headers["X-DB-Status"] = "rolled_back"
            except Exception as e:
                await transaction.rollback()
                response.headers["X-DB-Status"] = f"error: {str(e)}"
            finally:
                # Return connection to pool
                await self.db_pool.release(connection)

        return response

    async def process_error(self, request: Request, error: Exception) -> Optional[Response]:
        """Rollback transaction on error"""
        context = getattr(request, "middleware_context", None)
        if context:
            connection = context.get("db_connection")
            transaction = context.get("db_transaction")

            if connection and transaction:
                try:
                    await transaction.rollback()
                    await self.db_pool.release(connection)
                except Exception:
                    pass  # Ignore cleanup errors

        return None  # Let error propagate


# ============================================================================
# PRODUCTION MIDDLEWARE STACK EXAMPLES
# ============================================================================


def create_production_middleware_stack(
    secret_key: str,
    allowed_origins: List[str],
    api_keys: List[str],
    rate_limit_requests: int = 1000,
    rate_limit_window: int = 3600,
) -> MiddlewareStack:
    """Create a production-ready middleware stack"""

    stack = create_middleware_stack()

    # Critical security middleware (highest priority)
    stack.add(create_request_id_middleware(), priority=Priority.CRITICAL.value)

    stack.add(
        create_security_headers_middleware(
            hsts_max_age=31536000,  # 1 year
            hsts_include_subdomains=True,
            csp_policy="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            frame_options="DENY",
            content_type_options="nosniff",
        ),
        priority=Priority.CRITICAL.value,
    )

    stack.add(create_csrf_middleware(secret_key), priority=Priority.CRITICAL.value)

    # High priority middleware
    stack.add(
        create_cors_middleware(
            allow_origins=allowed_origins,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization", "X-API-Key"],
            allow_credentials=True,
            max_age=86400,
        ),
        priority=Priority.HIGH.value,
    )

    stack.add(
        create_rate_limiting_middleware(
            default_rule=RateLimitRule(rate_limit_requests, rate_limit_window),
            strategy="sliding_window",
        ),
        priority=Priority.HIGH.value,
    )

    # API authentication
    stack.add(APIKeyAuthMiddleware(api_keys), priority=Priority.HIGH.value)

    # Normal priority middleware
    stack.add(
        create_compression_middleware(minimum_size=1024, compression_level=6, enable_brotli=True),
        priority=Priority.NORMAL.value,
    )

    stack.add(
        create_request_logging_middleware(
            log_level=logging.INFO,
            log_headers=True,
            log_body=False,  # Don't log sensitive request bodies in production
            mask_sensitive=True,
        ),
        priority=Priority.NORMAL.value,
    )

    stack.add(
        create_session_middleware(
            secret_key=secret_key,
            max_age=1209600,  # 2 weeks
            secure=True,
            http_only=True,
            same_site="strict",
        ),
        priority=Priority.NORMAL.value,
    )

    # Low priority middleware
    stack.add(CacheMiddleware(ttl=300, max_size=1000), priority=Priority.LOW.value)

    return stack


def create_api_middleware_stack(
    api_keys: List[str], rate_limit_per_minute: int = 60, enable_caching: bool = True
) -> MiddlewareStack:
    """Create middleware stack optimized for API endpoints"""

    stack = create_middleware_stack()

    # Essential API middleware
    stack.add(create_request_id_middleware())
    # More permissive for APIs
    stack.add(create_cors_middleware(allow_origins=["*"]))
    stack.add(APIKeyAuthMiddleware(api_keys))
    stack.add(
        create_rate_limiting_middleware(default_rule=RateLimitRule(rate_limit_per_minute, 60))
    )
    stack.add(create_compression_middleware())

    # JSON validation for specific endpoints
    validation_schemas = {
        "/api/users": {
            "type": "object",
            "required": ["name", "email"],
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "age": {"type": "integer"},
            },
        },
        "/api/products": {
            "type": "object",
            "required": ["name", "price"],
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "integer"},
                "description": {"type": "string"},
            },
        },
    }

    stack.add(JSONValidationMiddleware(validation_schemas))

    if enable_caching:
        stack.add(CacheMiddleware(ttl=60, max_size=500))  # Short TTL for APIs

    return stack


def create_web_app_middleware_stack(secret_key: str) -> MiddlewareStack:
    """Create middleware stack for traditional web applications"""

    stack = create_middleware_stack()

    # Web app security
    stack.add(
        create_security_headers_middleware(
            csp_policy="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com"
        )
    )
    stack.add(create_csrf_middleware(secret_key))
    stack.add(create_session_middleware(secret_key))

    # Performance
    stack.add(create_compression_middleware())
    stack.add(CacheMiddleware(ttl=900, max_size=2000))  # 15 minute cache

    # Monitoring
    stack.add(create_request_logging_middleware(log_headers=False))
    stack.add(create_request_id_middleware())

    return stack


# ============================================================================
# MIDDLEWARE COMPOSITION AND PATTERNS
# ============================================================================


def create_conditional_auth_middleware(public_paths: List[str]) -> BaseMiddleware:
    """Create authentication middleware that skips certain paths"""

    class ConditionalAuthMiddleware(BaseMiddleware):
        def __init__(self):
            super().__init__(
                MiddlewareConfig(
                    name="conditional_auth",
                    exclude_routes=public_paths,
                    priority=Priority.HIGH.value,
                )
            )

        async def process_request(self, request: Request) -> Optional[Response]:
            # This will only run for non-public paths due to exclude_routes
            auth_header = request.headers.get("authorization", "")

            if not auth_header.startswith("Bearer "):
                return error_response("Authentication required", status_code=401)

            # Validate token (simplified)
            token = auth_header[7:]  # Remove "Bearer "
            if len(token) < 10:  # Simple validation
                return error_response("Invalid token", status_code=401)

            return None

        async def process_response(self, request: Request, response: Response) -> Response:
            response.headers["X-Auth-Required"] = "true"
            return response

    return ConditionalAuthMiddleware()


def create_metrics_middleware() -> BaseMiddleware:
    """Create middleware for collecting application metrics"""

    class MetricsMiddleware(BaseMiddleware):
        def __init__(self):
            super().__init__(MiddlewareConfig(name="metrics"))
            self.request_count = 0
            self.response_times = []
            self.status_codes = {}

        async def process_request(self, request: Request) -> Optional[Request]:
            self.request_count += 1
            add_middleware_context(request)
            request.middleware_context.set("metrics_start_time", time.time())
            return request

        async def process_response(self, request: Request, response: Response) -> Response:
            context = getattr(request, "middleware_context", None)
            if context:
                start_time = context.get("metrics_start_time")
                if start_time:
                    response_time = (time.time() - start_time) * 1000
                    self.response_times.append(response_time)

                    # Keep only last 1000 response times
                    if len(self.response_times) > 1000:
                        self.response_times = self.response_times[-1000:]

            # Track status codes
            status_code = response.status_code
            self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1

            return response

        def get_metrics(self) -> Dict[str, Any]:
            """Get collected metrics"""
            avg_response_time = (
                sum(self.response_times) / len(self.response_times) if self.response_times else 0
            )

            return {
                "total_requests": self.request_count,
                "average_response_time_ms": round(avg_response_time, 2),
                "status_code_distribution": self.status_codes.copy(),
                "recent_response_times": self.response_times[-10:],  # Last 10
            }

    return MetricsMiddleware()


# ============================================================================
# USAGE EXAMPLES AND DEMOS
# ============================================================================


async def demo_basic_middleware_usage():
    """Demonstrate basic middleware usage"""
    logger.info("=== Basic Middleware Usage Demo ===")

    # Create middleware stack
    stack = create_middleware_stack()

    # Add some middleware
    stack.add(timing_middleware)
    stack.add(create_request_id_middleware())

    # Create a simple handler
    async def hello_handler(request):
        return Response(f"Hello from {request.path}!")

    # Create a test request
    request = Request(method="GET", url="/hello")

    # Process through middleware
    await stack.process(request, hello_handler)

    logger.info("Response: {response.content}")
    logger.info("Headers: {dict(response.headers)}")
    logger.info("Request ID: {getattr(request, 'request_id', 'N/A')}")


async def demo_production_stack():
    """Demonstrate production middleware stack"""
    logger.info("\n=== Production Stack Demo ===")

    # Create production stack
    stack = create_production_middleware_stack(
        secret_key="super-secret-key-for-production",
        allowed_origins=["https://myapp.com", "https://admin.myapp.com"],
        api_keys=["api-key-1", "api-key-2"],
        rate_limit_requests=100,
        rate_limit_window=60,
    )

    # Initialize all middleware
    await stack.initialize_all()

    logger.info(
        "Middleware stack created with {len(stack.list_middleware())} middleware components:"
    )
    for middleware_info in stack.list_middleware():
        logger.info("  - {middleware_info['name']} (priority: {middleware_info['priority']})")

    # Test with a sample request
    async def api_handler(request):
        return json_response({"message": "API response", "user": "test"})

    request = Request(
        method="GET",
        url="/api/users/1",
        headers={
            "X-API-Key": "api-key-1",
            "Origin": "https://myapp.com",
            "Accept-Encoding": "gzip",
        },
    )

    await stack.process(request, api_handler)
    logger.info("\\nAPI Response Status: {response.status_code}")
    logger.info(
        "Security Headers Applied: {len([h for h in response.headers.keys() if h.startswith('X-')])}"
    )


async def demo_custom_middleware():
    """Demonstrate custom middleware development"""
    logger.info("\n=== Custom Middleware Demo ===")

    # Create custom middleware stack
    stack = create_middleware_stack()

    # Add custom middleware
    api_keys = ["test-api-key-123", "admin-key-456"]
    stack.add(APIKeyAuthMiddleware(api_keys))

    # Add validation middleware
    schemas = {
        "/api/users": {
            "type": "object",
            "required": ["name", "email"],
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}},
        }
    }
    stack.add(JSONValidationMiddleware(schemas))

    # Add metrics
    metrics_middleware = create_metrics_middleware()
    stack.add(metrics_middleware)

    # Test handler
    async def create_user_handler(request):
        context = getattr(request, "middleware_context", None)
        validated_data = context.get("validated_json") if context else {}
        return json_response({"message": "User created", "data": validated_data})

    # Test valid request
    valid_request = Request(
        method="POST",
        url="/api/users",
        headers={"X-API-Key": "test-api-key-123", "Content-Type": "application/json"},
        body=json.dumps({"name": "John Doe", "email": "john@example.com"}).encode(),
    )

    await stack.process(valid_request, create_user_handler)
    logger.info("Valid Request Response: {response.status_code}")
    logger.info("Response Content: {response.content}")

    # Test invalid request (missing API key)
    invalid_request = Request(
        method="POST",
        url="/api/users",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"name": "Jane Doe"}).encode(),
    )

    await stack.process(invalid_request, create_user_handler)
    logger.info("Invalid Request Response: {response.status_code}")

    # Show metrics
    logger.info("Metrics: {metrics_middleware.get_metrics()}")


async def demo_middleware_composition():
    """Demonstrate middleware composition patterns"""
    logger.info("\n=== Middleware Composition Demo ===")

    # Create composed middleware
    @middleware(name="request_logger")
    async def request_logger(request, call_next):
        logger.info("[LOG] Incoming request: {request.method} {request.path}")
        response = await call_next(request)
        logger.info("[LOG] Response status: {response.status_code}")
        return response

    @middleware(name="response_headers")
    async def add_custom_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Custom-Header"] = "CovetPy"
        response.headers["X-Timestamp"] = str(int(time.time()))
        return response

    # Compose multiple middleware into one
    composed_middleware = MiddlewareComposer.compose(
        request_logger, add_custom_headers, timing_middleware
    )

    stack = create_middleware_stack()
    stack.add(composed_middleware)

    async def simple_handler(request):
        return Response("Composed middleware response")

    request = Request(method="GET", url="/test")
    await stack.process(request, simple_handler)

    logger.info("Composed Response Headers: {dict(response.headers)}")


# Main demo function
async def run_all_demos():
    """Run all middleware demos"""
    logger.info("CovetPy Middleware System Demonstrations")
    logger.info("=" * 50)

    await demo_basic_middleware_usage()
    await demo_production_stack()
    await demo_custom_middleware()
    await demo_middleware_composition()

    logger.info("\n" + "=" * 50)
    logger.info("All demos completed successfully!")


if __name__ == "__main__":
    # Run demos when executed directly
    asyncio.run(run_all_demos())
