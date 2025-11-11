"""
Security Middleware

Production-ready security middleware including:
- Authentication middleware
- Authorization (RBAC) middleware
- Security headers middleware
- Rate limiting middleware
- CORS middleware
- CSRF protection middleware
"""

import json
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set

from ..core.http import Request, Response
from ..core.middleware import Middleware
from .auth import AuthManager, TokenManager, get_auth_manager
from .exceptions import (
    AuthException,
    PermissionDeniedError,
    RateLimitExceededError,
    SecurityViolationError,
)
from .exceptions import to_dict as exception_to_dict
from .rbac import AccessContext, RBACManager, get_rbac_manager
from .session import SessionManager, get_session_manager


@dataclass
class SecurityConfig:
    """Security middleware configuration"""

    # Authentication
    require_auth_paths: List[str] = field(default_factory=lambda: ["/api/"])
    exclude_auth_paths: List[str] = field(default_factory=lambda: ["/auth/", "/health"])

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 15
    rate_limit_by_user: bool = True
    rate_limit_by_ip: bool = True

    # Security headers
    enable_security_headers: bool = True
    hsts_max_age: int = 31536000  # 1 year
    csp_policy: str = "default-src 'self'"

    # CORS
    cors_origins: List[str] = field(default_factory=list)
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_headers: List[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])

    # CSRF
    csrf_protection: bool = True
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"


class RateLimiter:
    """Thread-safe rate limiter"""

    def __init__(self, max_requests: int, window_minutes: int):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Clean old requests
            self.requests[key] = [
                timestamp for timestamp in self.requests[key] if timestamp > window_start
            ]

            # Check limit
            if len(self.requests[key]) >= self.max_requests:
                return False

            # Record request
            self.requests[key].append(now)
            return True

    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests in window"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Clean old requests
            self.requests[key] = [
                timestamp for timestamp in self.requests[key] if timestamp > window_start
            ]

            return max(0, self.max_requests - len(self.requests[key]))

    def get_reset_time(self, key: str) -> Optional[float]:
        """Get time until rate limit resets"""
        with self.lock:
            if not self.requests[key]:
                return None

            oldest_request = min(self.requests[key])
            reset_time = oldest_request + self.window_seconds

            return max(0, reset_time - time.time())


class AuthMiddleware(Middleware):
    """
    Authentication middleware

    Verifies JWT tokens or sessions and adds user to request context
    """

    def __init__(
        self,
        config: Optional[SecurityConfig] = None,
        auth_manager: Optional[AuthManager] = None,
    ):
        self.config = config or SecurityConfig()
        self.auth_manager = auth_manager or get_auth_manager()
        self.token_manager = TokenManager(self.auth_manager)

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process authentication middleware"""
        try:
            # Check if path requires authentication
            if not self._requires_auth(request.url.path):
                return await call_next(request)

            # Extract authentication credentials
            user = None

            # Try JWT token first
            token = self._get_bearer_token(request)
            if token:
                user = self.token_manager.verify_bearer_token(token)

            # Try session if no token
            if not user:
                session_id = self._get_session_id(request)
                if session_id:
                    ip_address = self._get_client_ip(request)
                    user = self.token_manager.verify_session_token(session_id, ip_address)

            if not user:
                return self._auth_required_response()

            # Add user to request context
            request.state.user = user
            request.state.user_id = user.id

            return await call_next(request)

        except AuthException as e:
            return self._error_response(exception_to_dict(e), e.status_code)
        except Exception:
            return self._error_response({"error": "Authentication failed"}, 401)

    def _requires_auth(self, path: str) -> bool:
        """Check if path requires authentication"""
        # Check exclusions first
        for exclude_path in self.config.exclude_auth_paths:
            if path.startswith(exclude_path):
                return False

        # Check required paths
        for required_path in self.config.require_auth_paths:
            if path.startswith(required_path):
                return True

        return False

    def _get_bearer_token(self, request: Request) -> Optional[str]:
        """Extract bearer token"""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None

    def _get_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID"""
        cookies = getattr(request, "cookies", {})
        return cookies.get("session_id")

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP", "")
        if real_ip:
            return real_ip

        return getattr(request, "remote_addr", "127.0.0.1")

    def _auth_required_response(self) -> Response:
        """Return authentication required response"""
        return self._error_response({"error": "Authentication required"}, 401)

    def _error_response(self, data: Dict[str, Any], status_code: int) -> Response:
        """Create error response"""
        return Response(
            content=json.dumps(data),
            status_code=status_code,
            headers={"Content-Type": "application/json"},
        )


class RBACMiddleware(Middleware):
    """
    Role-Based Access Control middleware

    Checks user permissions for requested resources
    """

    def __init__(
        self,
        resource: str,
        action: str,
        rbac_manager: Optional[RBACManager] = None,
        context_factory: Optional[Callable] = None,
    ):
        self.resource = resource
        self.action = action
        self.rbac_manager = rbac_manager or get_rbac_manager()
        self.context_factory = context_factory

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process RBAC middleware"""
        try:
            # Get current user from request context
            user = getattr(request.state, "user", None)
            if not user:
                return self._error_response({"error": "Authentication required"}, 401)

            # Create access context
            context = AccessContext(
                user_id=user.id,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("User-Agent", ""),
                request_time=datetime.utcnow(),
            )

            # Add custom context if factory provided
            if self.context_factory:
                custom_context = self.context_factory(request, user)
                if custom_context:
                    context.additional_context.update(custom_context)

            # Check permission
            decision = self.rbac_manager.check_permission(
                user.id, self.resource, self.action, context
            )

            if not decision.allowed:
                return self._error_response(
                    {
                        "error": "Permission denied",
                        "message": decision.reason,
                        "required_permission": f"{self.resource}:{self.action}",
                    },
                    403,
                )

            return await call_next(request)

        except PermissionDeniedError as e:
            return self._error_response(exception_to_dict(e), e.status_code)
        except Exception:
            return self._error_response({"error": "Authorization failed"}, 403)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return getattr(request, "remote_addr", "127.0.0.1")

    def _error_response(self, data: Dict[str, Any], status_code: int) -> Response:
        """Create error response"""
        return Response(
            content=json.dumps(data),
            status_code=status_code,
            headers={"Content-Type": "application/json"},
        )


class RateLimitMiddleware(Middleware):
    """
    Rate limiting middleware
    """

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests, self.config.rate_limit_window_minutes
        )

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process rate limiting middleware"""
        try:
            # Generate rate limit key
            keys = []

            if self.config.rate_limit_by_ip:
                ip_address = self._get_client_ip(request)
                keys.append(f"ip:{ip_address}")

            if self.config.rate_limit_by_user:
                user = getattr(request.state, "user", None)
                if user:
                    keys.append(f"user:{user.id}")

            # Check rate limits
            for key in keys:
                if not self.rate_limiter.is_allowed(key):
                    remaining = self.rate_limiter.get_remaining_requests(key)
                    reset_time = self.rate_limiter.get_reset_time(key)

                    headers = {
                        "X-RateLimit-Limit": str(self.config.rate_limit_requests),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(int(time.time() + (reset_time or 0))),
                        "Retry-After": str(int(reset_time or 0)),
                    }

                    return Response(
                        content=json.dumps({"error": "Rate limit exceeded"}),
                        status_code=429,
                        headers={**headers, "Content-Type": "application/json"},
                    )

            response = await call_next(request)

            # Add rate limit headers to response
            if keys:
                key = keys[0]  # Use first key for headers
                remaining = self.rate_limiter.get_remaining_requests(key)
                reset_time = self.rate_limiter.get_reset_time(key)

                response.headers.update(
                    {
                        "X-RateLimit-Limit": str(self.config.rate_limit_requests),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(int(time.time() + (reset_time or 0))),
                    }
                )

            return response

        except Exception:
            return Response(
                content=json.dumps({"error": "Rate limiting failed"}),
                status_code=500,
                headers={"Content-Type": "application/json"},
            )

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return getattr(request, "remote_addr", "127.0.0.1")


class SecurityHeadersMiddleware(Middleware):
    """
    Security headers middleware
    """

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""
        response = await call_next(request)

        if not self.config.enable_security_headers:
            return response

        # Add security headers
        headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            # Enable XSS filtering
            "X-XSS-Protection": "1; mode=block",
            # Prevent page from being embedded in frames
            "X-Frame-Options": "DENY",
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Content Security Policy
            "Content-Security-Policy": self.config.csp_policy,
            # Remove server information
            "Server": "CovetPy",
        }

        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            headers["Strict-Transport-Security"] = (
                f"max-age={self.config.hsts_max_age}; includeSubDomains"
            )

        response.headers.update(headers)
        return response


class CORSMiddleware(Middleware):
    """
    CORS (Cross-Origin Resource Sharing) middleware
    """

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Handle CORS requests"""
        origin = request.headers.get("Origin")

        # Handle preflight requests
        if request.method == "OPTIONS":
            return self._preflight_response(origin)

        response = await call_next(request)

        # Add CORS headers
        if origin and self._is_origin_allowed(origin):
            response.headers.update(
                {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Expose-Headers": "Content-Length, X-JSON",
                }
            )

        return response

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if not self.config.cors_origins:
            return True  # Allow all origins if none specified

        if "*" in self.config.cors_origins:
            return True

        return origin in self.config.cors_origins

    def _preflight_response(self, origin: str) -> Response:
        """Handle preflight OPTIONS request"""
        headers = {}

        if origin and self._is_origin_allowed(origin):
            headers.update(
                {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": ", ".join(self.config.cors_methods),
                    "Access-Control-Allow-Headers": ", ".join(self.config.cors_headers),
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "86400",  # 24 hours
                }
            )

        return Response(content="", status_code=200, headers=headers)


class CSRFMiddleware(Middleware):
    """
    CSRF (Cross-Site Request Forgery) protection middleware
    """

    def __init__(
        self,
        config: Optional[SecurityConfig] = None,
        session_manager: Optional[SessionManager] = None,
    ):
        self.config = config or SecurityConfig()
        self.session_manager = session_manager or get_session_manager()
        self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process CSRF protection"""
        if not self.config.csrf_protection:
            return await call_next(request)

        # Skip CSRF for safe methods
        if request.method in self.safe_methods:
            return await call_next(request)

        # Get session
        session_id = self._get_session_id(request)
        if not session_id:
            return self._csrf_error_response()

        session = self.session_manager.get_session(session_id)
        if not session:
            return self._csrf_error_response()

        # Get CSRF token from header
        csrf_token = request.headers.get(self.config.csrf_header_name)
        if not csrf_token:
            return self._csrf_error_response()

        # Validate CSRF token
        if not self.session_manager.validate_csrf_token(session, csrf_token):
            return self._csrf_error_response()

        return await call_next(request)

    def _get_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID"""
        cookies = getattr(request, "cookies", {})
        return cookies.get("session_id")

    def _csrf_error_response(self) -> Response:
        """Return CSRF error response"""
        return Response(
            content=json.dumps({"error": "CSRF token validation failed"}),
            status_code=403,
            headers={"Content-Type": "application/json"},
        )


# Convenience functions for creating middleware
def require_auth(config: Optional[SecurityConfig] = None) -> AuthMiddleware:
    """Create authentication middleware"""
    return AuthMiddleware(config)


def require_permission(
    resource: str, action: str, context_factory: Optional[Callable] = None
) -> RBACMiddleware:
    """Create RBAC middleware for specific permission"""
    return RBACMiddleware(resource, action, context_factory=context_factory)


def rate_limit(config: Optional[SecurityConfig] = None) -> RateLimitMiddleware:
    """Create rate limiting middleware"""
    return RateLimitMiddleware(config)


def security_headers(
    config: Optional[SecurityConfig] = None,
) -> SecurityHeadersMiddleware:
    """Create security headers middleware"""
    return SecurityHeadersMiddleware(config)


def cors(config: Optional[SecurityConfig] = None) -> CORSMiddleware:
    """Create CORS middleware"""
    return CORSMiddleware(config)


def csrf_protection(config: Optional[SecurityConfig] = None) -> CSRFMiddleware:
    """Create CSRF protection middleware"""
    return CSRFMiddleware(config)
