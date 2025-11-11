"""
Advanced CORS Middleware for CovetPy

Production-ready CORS (Cross-Origin Resource Sharing) middleware with:
- Dynamic origin validation with regex patterns
- Wildcard and multiple origin support
- Credentials (cookies/auth headers) support
- Preflight caching with configurable max-age
- Exposed headers configuration
- Method and header validation
- Security-first defaults with HTTPS enforcement
- Vary header handling for caching
- Origin validation against whitelist/blacklist

Security Features:
- Null origin rejection
- Strict origin validation
- HTTPS enforcement for credentials
- Configurable allowed methods and headers
- Automatic Vary header injection
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Pattern, Union
from urllib.parse import urlparse


@dataclass
class CORSConfig:
    """CORS configuration"""

    # Origin settings
    allow_origins: List[str] = field(default_factory=lambda: ["*"])
    allow_origin_regex: Optional[List[Pattern]] = None

    # Method settings
    allow_methods: List[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    )

    # Header settings
    allow_headers: List[str] = field(default_factory=lambda: ["*"])
    expose_headers: List[str] = field(default_factory=list)

    # Credentials
    allow_credentials: bool = False

    # Preflight settings
    max_age: int = 86400  # 24 hours

    # Security settings
    enforce_https_with_credentials: bool = True
    reject_null_origin: bool = True

    # Vary header
    add_vary_header: bool = True


class CORSMiddleware:
    """
    Advanced CORS middleware

    Handles:
    1. Preflight requests (OPTIONS)
    2. Simple requests
    3. Credentialed requests
    4. Dynamic origin validation

    Usage:
        app = CovetApp()

        # Basic usage
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['https://example.com'],
            allow_credentials=True
        )

        # Advanced usage with regex
        import re
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['https://example.com'],
            allow_origin_regex=[
                re.compile(r'https://.*\\.example\\.com'),
                re.compile(r'https://app-\\d+\\.example\\.com')
            ],
            allow_methods=['GET', 'POST'],
            expose_headers=['X-Custom-Header'],
            max_age=3600
        )
    """

    def __init__(
        self,
        app: Optional[Callable] = None,
        allow_origins: Optional[List[str]] = None,
        allow_origin_regex: Optional[List[Union[str, Pattern]]] = None,
        allow_methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None,
        expose_headers: Optional[List[str]] = None,
        allow_credentials: bool = False,
        max_age: int = 86400,
        enforce_https_with_credentials: bool = True,
        reject_null_origin: bool = True,
        add_vary_header: bool = True,
    ):
        """
        Initialize CORS middleware

        Args:
            app: ASGI application (optional, can be set later)
            allow_origins: List of allowed origins (or ['*'] for all)
            allow_origin_regex: List of regex patterns for dynamic origins
            allow_methods: Allowed HTTP methods
            allow_headers: Allowed request headers
            expose_headers: Headers exposed to browser
            allow_credentials: Allow credentials (cookies, auth)
            max_age: Preflight cache duration in seconds
            enforce_https_with_credentials: Require HTTPS when credentials enabled
            reject_null_origin: Reject requests with null origin
            add_vary_header: Add Vary: Origin header for caching
        """
        self.app = app  # Can be None initially

        # Create config
        self.config = CORSConfig(
            allow_origins=allow_origins or ["*"],
            allow_methods=allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=allow_headers or ["*"],
            expose_headers=expose_headers or [],
            allow_credentials=allow_credentials,
            max_age=max_age,
            enforce_https_with_credentials=enforce_https_with_credentials,
            reject_null_origin=reject_null_origin,
            add_vary_header=add_vary_header,
        )

        # Compile regex patterns
        if allow_origin_regex:
            self.config.allow_origin_regex = [
                re.compile(pattern) if isinstance(pattern, str) else pattern
                for pattern in allow_origin_regex
            ]

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate CORS configuration"""
        # Can't use wildcard with credentials
        if self.config.allow_credentials and "*" in self.config.allow_origins:
            raise ValueError(
                "Cannot use wildcard origin (*) with credentials. "
                "Specify explicit origins when allow_credentials=True"
            )

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """
        ASGI interface

        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract headers
        headers = dict(scope.get("headers", []))
        origin = headers.get(b"origin", b"").decode("utf-8")
        method = scope.get("method", "GET")

        # Handle preflight request
        if method == "OPTIONS" and origin:
            await self._handle_preflight(scope, receive, send, origin, headers)
            return

        # Handle regular request with CORS headers
        if origin:
            await self._handle_request(scope, receive, send, origin)
        else:
            # No origin header - not a CORS request
            await self.app(scope, receive, send)

    async def _handle_preflight(
        self,
        scope: Dict[str, Any],
        receive: Callable,
        send: Callable,
        origin: str,
        headers: Dict[bytes, bytes],
    ):
        """
        Handle preflight request (OPTIONS)

        Validates:
        1. Origin
        2. Requested method
        3. Requested headers
        """
        # Validate origin
        allowed_origin = self._validate_origin(origin)
        if not allowed_origin:
            # Origin not allowed - return 403
            await self._send_forbidden(send, "Origin not allowed")
            return

        # Get requested method
        requested_method = (
            headers.get(b"access-control-request-method", b"").decode("utf-8").upper()
        )

        # Validate requested method
        if requested_method and requested_method not in self.config.allow_methods:
            await self._send_forbidden(send, f"Method {requested_method} not allowed")
            return

        # Get requested headers
        requested_headers = headers.get(b"access-control-request-headers", b"").decode("utf-8")

        # Validate requested headers
        if not self._validate_headers(requested_headers):
            await self._send_forbidden(send, "Requested headers not allowed")
            return

        # Build preflight response headers
        response_headers = [
            (b"access-control-allow-origin", allowed_origin.encode("utf-8")),
            (
                b"access-control-allow-methods",
                ", ".join(self.config.allow_methods).encode("utf-8"),
            ),
            (b"access-control-max-age", str(self.config.max_age).encode("utf-8")),
            (b"content-length", b"0"),
        ]

        # Add allowed headers
        if self.config.allow_headers == ["*"]:
            # Echo back requested headers
            if requested_headers:
                response_headers.append(
                    (b"access-control-allow-headers", requested_headers.encode("utf-8"))
                )
        else:
            response_headers.append(
                (
                    b"access-control-allow-headers",
                    ", ".join(self.config.allow_headers).encode("utf-8"),
                )
            )

        # Add credentials header
        if self.config.allow_credentials:
            response_headers.append((b"access-control-allow-credentials", b"true"))

        # Add Vary header
        if self.config.add_vary_header:
            response_headers.append((b"vary", b"Origin"))

        # Send response
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": response_headers,
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": b"",
            }
        )

    async def _handle_request(
        self, scope: Dict[str, Any], receive: Callable, send: Callable, origin: str
    ):
        """
        Handle regular CORS request

        Adds CORS headers to response
        """
        # Validate origin
        allowed_origin = self._validate_origin(origin)
        if not allowed_origin:
            # Origin not allowed - still process request but don't add CORS headers
            # (or could return 403 - depends on security policy)
            await self.app(scope, receive, send)
            return

        # Wrap send to add CORS headers
        async def send_with_cors(message: Dict[str, Any]):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Add CORS headers
                headers.append((b"access-control-allow-origin", allowed_origin.encode("utf-8")))

                # Add exposed headers
                if self.config.expose_headers:
                    headers.append(
                        (
                            b"access-control-expose-headers",
                            ", ".join(self.config.expose_headers).encode("utf-8"),
                        )
                    )

                # Add credentials header
                if self.config.allow_credentials:
                    headers.append((b"access-control-allow-credentials", b"true"))

                # Add Vary header
                if self.config.add_vary_header:
                    headers.append((b"vary", b"Origin"))

                message["headers"] = headers

            await send(message)

        # Call application with modified send
        await self.app(scope, receive, send_with_cors)

    def _validate_origin(self, origin: str) -> Optional[str]:
        """
        Validate origin against allowed origins

        Args:
            origin: Origin header value

        Returns:
            Allowed origin string or None if not allowed
        """
        if not origin:
            return None

        # Reject null origin if configured
        if self.config.reject_null_origin and origin.lower() == "null":
            return None

        # Check if credentials require HTTPS
        if self.config.allow_credentials and self.config.enforce_https_with_credentials:
            parsed = urlparse(origin)
            if parsed.scheme != "https":
                return None

        # Check wildcard
        if "*" in self.config.allow_origins:
            return origin

        # Check exact match
        if origin in self.config.allow_origins:
            return origin

        # Check regex patterns
        if self.config.allow_origin_regex:
            for pattern in self.config.allow_origin_regex:
                if pattern.match(origin):
                    return origin

        return None

    def _validate_headers(self, requested_headers: str) -> bool:
        """
        Validate requested headers

        Args:
            requested_headers: Comma-separated list of headers

        Returns:
            True if all headers are allowed
        """
        if not requested_headers:
            return True

        # Wildcard allows all headers
        if self.config.allow_headers == ["*"]:
            return True

        # Parse requested headers
        headers = [h.strip().lower() for h in requested_headers.split(",")]

        # Check each header
        allowed_headers_lower = [h.lower() for h in self.config.allow_headers]

        for header in headers:
            if header not in allowed_headers_lower:
                return False

        return True

    async def _send_forbidden(self, send: Callable, reason: str):
        """Send 403 Forbidden response"""
        body = f'{{"error": "CORS validation failed", "reason": "{reason}"}}'.encode("utf-8")

        await send(
            {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("utf-8")),
                ],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )


class DynamicCORSMiddleware(CORSMiddleware):
    """
    Dynamic CORS middleware with database/API validation

    Allows origin validation against external sources like:
    - Database of allowed origins
    - API endpoint validation
    - Redis cache

    Usage:
        async def validate_origin(origin: str) -> bool:
            # Check database
            allowed = await db.query(
                "SELECT 1 FROM allowed_origins WHERE origin = ?",
                [origin]
            )
            return bool(allowed)

        app.add_middleware(
            DynamicCORSMiddleware,
            origin_validator=validate_origin
        )
    """

    def __init__(self, app: Callable, origin_validator: Callable[[str], bool], **kwargs):
        """
        Initialize dynamic CORS middleware

        Args:
            app: ASGI application
            origin_validator: Async function that validates origin
            **kwargs: Other CORS configuration
        """
        super().__init__(app, **kwargs)
        self.origin_validator = origin_validator

    async def _validate_origin(self, origin: str) -> Optional[str]:
        """
        Validate origin using custom validator

        Args:
            origin: Origin to validate

        Returns:
            Origin if valid, None otherwise
        """
        # First check static configuration
        static_result = await super()._validate_origin(origin)

        if static_result:
            return static_result

        # Check dynamic validator
        try:
            is_valid = await self.origin_validator(origin)
            if is_valid:
                return origin
        except Exception:
            # Log error in production

            pass
        return None


# Example usage and documentation
CORS_USAGE_EXAMPLES = """
# CORS Middleware Usage Examples

## 1. Basic CORS (Development)

```python
from covet.middleware.cors import CORSMiddleware

app = CovetApp()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow all origins
    allow_methods=['GET', 'POST'],
)
```

## 2. Production CORS with Credentials

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'https://app.example.com',
        'https://admin.example.com'
    ],
    allow_credentials=True,  # Allow cookies
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    expose_headers=['X-Custom-Header'],
    max_age=3600
)
```

## 3. Regex Pattern Matching

```python
import re

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://example.com'],
    allow_origin_regex=[
        re.compile(r'https://.*\\.example\\.com'),  # All subdomains
        re.compile(r'https://app-\\d+\\.example\\.com')  # Numbered apps
    ],
    allow_credentials=True
)
```

## 4. Dynamic Origin Validation

```python
from covet.middleware.cors import DynamicCORSMiddleware

async def validate_origin(origin: str) -> bool:
    # Check database
    result = await db.execute(
        "SELECT 1 FROM allowed_origins WHERE origin = ?",
        [origin]
    )
    return result is not None

app.add_middleware(
    DynamicCORSMiddleware,
    origin_validator=validate_origin,
    allow_methods=['GET', 'POST'],
    allow_credentials=True
)
```

## 5. API Gateway Configuration

```python
# For API gateway with multiple frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'https://web.example.com',
        'https://mobile.example.com',
        'https://admin.example.com'
    ],
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allow_headers=['Content-Type', 'Authorization', 'X-API-Key'],
    expose_headers=['X-Total-Count', 'X-Page-Count'],
    allow_credentials=True,
    max_age=86400  # 24 hours
)
```

## Security Best Practices

1. **Never use wildcard (*) with credentials**
   - Specify explicit origins when allowing cookies/auth

2. **Use HTTPS in production**
   - Middleware enforces HTTPS when credentials enabled

3. **Limit exposed headers**
   - Only expose headers that clients need

4. **Set appropriate max-age**
   - Balance between performance and security

5. **Validate origin strictly**
   - Use regex patterns carefully to avoid bypasses
"""
