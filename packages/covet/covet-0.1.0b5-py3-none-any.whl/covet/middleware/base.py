"""
Middleware system for CovetPy framework.
Simple, Flask-like middleware with proper async support.
"""

from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import time
import json
from datetime import datetime


class BaseMiddleware:
    """Base middleware class"""

    def __init__(self, app=None):
        self.app = app

    async def __call__(self, request, call_next):
        """Process the request"""
        # Before request
        request = await self.process_request(request)

        # Call next middleware or handler
        response = await call_next(request)

        # After request
        response = await self.process_response(request, response)

        return response

    async def process_request(self, request):
        """Override to process request before handler"""
        return request

    async def process_response(self, request, response):
        """Override to process response after handler"""
        return response


class CORSMiddleware(BaseMiddleware):
    """CORS middleware for cross-origin requests"""

    def __init__(self, app=None, origins="*", methods="*", headers="*", credentials=False):
        super().__init__(app)
        self.origins = origins
        self.methods = methods if methods == "*" else ",".join(methods)
        self.headers = headers if headers == "*" else ",".join(headers)
        self.credentials = credentials

    async def process_response(self, request, response):
        """Add CORS headers to response"""
        # Handle preflight requests
        if request.method == "OPTIONS":
            response.status_code = 200
            response.content = ""

        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = self.origins
        response.headers["Access-Control-Allow-Methods"] = self.methods
        response.headers["Access-Control-Allow-Headers"] = self.headers

        if self.credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response


class AuthenticationMiddleware(BaseMiddleware):
    """Authentication middleware using JWT"""

    def __init__(self, app=None, auth_handler=None, exclude_paths=None):
        super().__init__(app)
        self.auth_handler = auth_handler
        self.exclude_paths = exclude_paths or ["/login", "/register", "/health"]

    async def process_request(self, request):
        """Check authentication before request"""
        # Skip auth for excluded paths
        path = getattr(request, 'path', request.url)
        if path in self.exclude_paths:
            return request

        # Get token from header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            request.user = None
            return request

        token = auth_header[7:]

        # Verify token
        if self.auth_handler:
            try:
                user = self.auth_handler.verify_token(token)
                request.user = user
            except Exception:
                request.user = None

        return request


class LoggingMiddleware(BaseMiddleware):
    """Request/response logging middleware"""

    def __init__(self, app=None, logger=None):
        super().__init__(app)
        self.logger = logger or self._default_logger

    def _default_logger(self, message):
        """Default logger that prints to console"""
        print(f"[{datetime.now().isoformat()}] {message}")

    async def process_request(self, request):
        """Log incoming request"""
        request.start_time = time.time()
        path = getattr(request, 'path', request.url)
        self.logger(f"→ {request.method} {path}")
        return request

    async def process_response(self, request, response):
        """Log outgoing response"""
        duration = time.time() - getattr(request, 'start_time', time.time())
        path = getattr(request, 'path', request.url)
        self.logger(f"← {response.status_code} {path} ({duration:.3f}s)")
        return response


class RateLimitMiddleware(BaseMiddleware):
    """Simple rate limiting middleware"""

    def __init__(self, app=None, max_requests=100, window=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window  # seconds
        self.requests = {}  # ip -> [(timestamp, count)]

    async def process_request(self, request):
        """Check rate limit before request"""
        # Get client IP
        client = getattr(request, 'client', ('127.0.0.1', 0))
        ip = request.headers.get("X-Forwarded-For", client[0] if client else "127.0.0.1")

        now = time.time()

        # Clean old entries
        if ip in self.requests:
            self.requests[ip] = [
                (ts, count) for ts, count in self.requests[ip]
                if now - ts < self.window
            ]
        else:
            self.requests[ip] = []

        # Count requests in window
        total = sum(count for _, count in self.requests[ip])

        if total >= self.max_requests:
            # Rate limit exceeded
            from covet.core.http import Response
            return Response(
                content={"error": "Rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": str(self.window)}
            )

        # Add current request
        self.requests[ip].append((now, 1))

        return request


class CompressionMiddleware(BaseMiddleware):
    """Response compression middleware"""

    def __init__(self, app=None, minimum_size=500):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def process_response(self, request, response):
        """Compress response if appropriate"""
        # Check if client accepts gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding:
            return response

        # Check response size
        body = response.get_content_bytes() if hasattr(response, 'get_content_bytes') else b""
        if len(body) < self.minimum_size:
            return response

        # Compress response
        import gzip
        compressed = gzip.compress(body)
        response.content = compressed
        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Length"] = str(len(compressed))

        return response


class SessionMiddleware(BaseMiddleware):
    """Session management middleware"""

    def __init__(self, app=None, session_store=None, cookie_name="session_id"):
        super().__init__(app)
        self.session_store = session_store or {}  # In-memory by default
        self.cookie_name = cookie_name

    async def process_request(self, request):
        """Load session before request"""
        # Get session ID from cookie
        cookies = getattr(request, 'cookies', {})
        if callable(cookies):
            cookies = cookies()
        session_id = cookies.get(self.cookie_name) if cookies else None

        if session_id and session_id in self.session_store:
            request.session = self.session_store[session_id]
        else:
            # Create new session
            import uuid
            session_id = str(uuid.uuid4())
            request.session = {}
            request.session_id = session_id

        return request

    async def process_response(self, request, response):
        """Save session after request"""
        if hasattr(request, 'session'):
            cookies = getattr(request, 'cookies', {})
            if callable(cookies):
                cookies = cookies()
            session_id = getattr(request, 'session_id', cookies.get(self.cookie_name) if cookies else None)
            if session_id:
                self.session_store[session_id] = request.session
                # Set cookie
                if hasattr(response, 'set_cookie'):
                    response.set_cookie(self.cookie_name, session_id, http_only=True)

        return response


class CSRFMiddleware(BaseMiddleware):
    """CSRF protection middleware"""

    def __init__(self, app=None, token_name="csrf_token", exclude_methods=None):
        super().__init__(app)
        self.token_name = token_name
        self.exclude_methods = exclude_methods or ["GET", "HEAD", "OPTIONS"]

    async def process_request(self, request):
        """Check CSRF token for unsafe methods"""
        if request.method in self.exclude_methods:
            return request

        # Get token from request
        token_header = request.headers.get(f"X-{self.token_name}", "")
        token_form = None

        if request.method == "POST" and request.content_type == "application/x-www-form-urlencoded":
            form_data = await request.form()
            token_form = form_data.get(self.token_name)

        token = token_header or token_form

        # Get expected token from session
        expected_token = getattr(request, 'session', {}).get(self.token_name)

        if not token or token != expected_token:
            from covet.core.http import Response
            return Response(
                content={"error": "CSRF token missing or invalid"},
                status_code=403
            )

        return request

    async def process_response(self, request, response):
        """Generate CSRF token if needed"""
        if hasattr(request, 'session') and self.token_name not in request.session:
            import secrets
            request.session[self.token_name] = secrets.token_urlsafe(32)

        return response


class ErrorHandlingMiddleware(BaseMiddleware):
    """Global error handling middleware"""

    def __init__(self, app=None, debug=False):
        super().__init__(app)
        self.debug = debug

    async def __call__(self, request, call_next):
        """Catch and handle errors"""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log error
            import traceback
            error_detail = traceback.format_exc() if self.debug else str(e)

            # Create error response
            from covet.core.http import Response

            status_code = getattr(e, 'status_code', 500)
            error_message = {
                "error": str(e),
                "type": type(e).__name__
            }

            if self.debug:
                error_message["traceback"] = error_detail

            return Response(
                content=error_message,
                status_code=status_code,
                headers={"Content-Type": "application/json"}
            )


# Middleware stack builder
class MiddlewareStack:
    """Manages middleware pipeline"""

    def __init__(self):
        self.middleware = []

    def add(self, middleware_class, *args, **kwargs):
        """Add middleware to stack"""
        middleware = middleware_class(*args, **kwargs)
        self.middleware.append(middleware)
        return self

    async def __call__(self, request, handler):
        """Execute middleware stack"""
        # Build the chain
        async def chain(req):
            return await handler(req)

        # Wrap with middleware in reverse order
        for mw in reversed(self.middleware):
            _chain = chain
            async def chain(req, m=mw, c=_chain):
                return await m(req, c)

        # Execute the chain
        return await chain(request)


# Export all middleware
__all__ = [
    'BaseMiddleware',
    'CORSMiddleware',
    'AuthenticationMiddleware',
    'LoggingMiddleware',
    'RateLimitMiddleware',
    'CompressionMiddleware',
    'SessionMiddleware',
    'CSRFMiddleware',
    'ErrorHandlingMiddleware',
    'MiddlewareStack'
]