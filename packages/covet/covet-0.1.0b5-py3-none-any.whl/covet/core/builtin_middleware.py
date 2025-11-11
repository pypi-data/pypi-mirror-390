"""
CovetPy Built-in Production Middleware Components

A comprehensive collection of production-ready middleware:
- CORS (Cross-Origin Resource Sharing)
- Authentication and Authorization
- Rate Limiting with multiple strategies
- Request/Response Logging
- Compression (gzip, brotli)
- Security Headers (OWASP compliant)
- Session Management
- CSRF Protection
- Request ID tracking
- Metrics and monitoring
"""

import asyncio
import gzip
import hashlib
import hmac
import json
import logging
import re
import secrets
import time
import weakref
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

try:
    import brotli

    HAS_BROTLI = True
except ImportError:
    brotli = None
    HAS_BROTLI = False

from .exceptions import HTTPException
from .http import Request, Response, error_response, json_response
from .middleware_system import BaseMiddleware, MiddlewareConfig, Priority


# CORS Middleware
class CORSMiddleware(BaseMiddleware):
    """Production-grade CORS middleware with comprehensive configuration"""

    def __init__(self, config: Optional[MiddlewareConfig] = None, **cors_options):
        if config is None:
            config = MiddlewareConfig(name="cors_middleware", priority=Priority.HIGH.value)

        super().__init__(config)

        # CORS configuration with secure defaults
        self.allow_origins = cors_options.get("allow_origins", ["*"])
        self.allow_methods = cors_options.get(
            "allow_methods", ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )
        self.allow_headers = cors_options.get("allow_headers", ["*"])
        self.allow_credentials = cors_options.get("allow_credentials", False)
        self.expose_headers = cors_options.get("expose_headers", [])
        self.max_age = cors_options.get("max_age", 86400)  # 24 hours

        # Compile origin patterns for better performance
        self._compiled_origins = self._compile_origin_patterns()

    def _compile_origin_patterns(self) -> List[re.Pattern]:
        """Compile origin patterns for efficient matching"""
        patterns = []
        for origin in self.allow_origins:
            if origin == "*":
                patterns.append(re.compile(r".*"))
            elif "*" in origin:
                # Convert wildcard to regex
                pattern = origin.replace("*", ".*")
                patterns.append(re.compile(f"^{pattern}$"))
            else:
                patterns.append(re.compile(f"^{re.escape(origin)}$"))
        return patterns

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if not origin:
            return False

        for pattern in self._compiled_origins:
            if pattern.match(origin):
                return True
        return False

    def _get_allowed_origin(self, request: Request) -> str:
        """Get the allowed origin for this request"""
        origin = request.headers.get("origin", "")

        if not origin:
            return ""

        if "*" in self.allow_origins and not self.allow_credentials:
            return "*"

        if self._is_origin_allowed(origin):
            return origin

        return ""

    async def process_request(self, request: Request) -> Optional[Union[Request, Response]]:
        """Handle CORS preflight requests"""
        if request.method == "OPTIONS":
            # This is a preflight request
            origin = self._get_allowed_origin(request)

            if not origin:
                return Response("", status_code=403)

            headers = {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
                "Access-Control-Max-Age": str(self.max_age),
            }

            if self.allow_headers:
                if "*" in self.allow_headers:
                    # Echo back requested headers
                    requested_headers = request.headers.get("access-control-request-headers", "")
                    if requested_headers:
                        headers["Access-Control-Allow-Headers"] = requested_headers
                else:
                    headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

            if self.allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"

            return Response("", status_code=200, headers=headers)

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Add CORS headers to response"""
        origin = self._get_allowed_origin(request)

        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin

            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

            if self.expose_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        return response


# Rate Limiting Middleware
@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""

    requests: int  # Number of requests
    window: int  # Time window in seconds
    burst: Optional[int] = None  # Burst allowance
    key_func: Optional[Callable[[Request], str]] = None  # Custom key function


class RateLimitingMiddleware(BaseMiddleware):
    """Production-grade rate limiting with multiple strategies"""

    def __init__(self, config: Optional[MiddlewareConfig] = None, **rate_options):
        if config is None:
            config = MiddlewareConfig(name="rate_limiting_middleware", priority=Priority.HIGH.value)

        super().__init__(config)

        # Rate limiting configuration
        self.default_rule = rate_options.get("default_rule", RateLimitRule(100, 60))  # 100 req/min
        self.rules: Dict[str, RateLimitRule] = rate_options.get("rules", {})
        # sliding_window, fixed_window, token_bucket
        self.strategy = rate_options.get("strategy", "sliding_window")
        self.key_func = rate_options.get("key_func", self._default_key_func)

        # Storage for rate limit data
        self._buckets: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._cleanup_interval = 300  # Cleanup every 5 minutes
        self._last_cleanup = time.time()

    def _default_key_func(self, request: Request) -> str:
        """Default key function using client IP"""
        return request.remote_addr or "unknown"

    def _get_rule_for_request(self, request: Request) -> RateLimitRule:
        """Get the appropriate rate limit rule for this request"""
        # Check for path-specific rules
        for pattern, rule in self.rules.items():
            if re.match(pattern, request.path):
                return rule
        return self.default_rule

    def _cleanup_old_entries(self) -> None:
        """Clean up old rate limit entries"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        cutoff_time = current_time - 3600  # Remove entries older than 1 hour

        for key in list(self._buckets.keys()):
            bucket = self._buckets[key]
            if bucket.get("last_access", 0) < cutoff_time:
                del self._buckets[key]

        self._last_cleanup = current_time

    def _check_sliding_window(self, key: str, rule: RateLimitRule) -> Tuple[bool, Dict[str, Any]]:
        """Sliding window rate limiting"""
        current_time = time.time()
        window_start = current_time - rule.window

        bucket = self._buckets[key]

        # Initialize or get request times
        if "requests" not in bucket:
            bucket["requests"] = deque()

        # Remove old requests
        while bucket["requests"] and bucket["requests"][0] <= window_start:
            bucket["requests"].popleft()

        # Check if we can add a new request
        current_count = len(bucket["requests"])
        allowed = current_count < rule.requests

        if allowed:
            bucket["requests"].append(current_time)

        bucket["last_access"] = current_time

        return allowed, {
            "limit": rule.requests,
            "remaining": max(0, rule.requests - current_count - (1 if allowed else 0)),
            "reset": int(current_time + rule.window),
            "retry_after": rule.window if not allowed else 0,
        }

    def _check_fixed_window(self, key: str, rule: RateLimitRule) -> Tuple[bool, Dict[str, Any]]:
        """Fixed window rate limiting"""
        current_time = time.time()
        window_id = int(current_time // rule.window)

        bucket = self._buckets[key]

        if bucket.get("window_id") != window_id:
            # New window
            bucket["window_id"] = window_id
            bucket["count"] = 0

        current_count = bucket["count"]
        allowed = current_count < rule.requests

        if allowed:
            bucket["count"] += 1

        bucket["last_access"] = current_time

        window_end = (window_id + 1) * rule.window

        return allowed, {
            "limit": rule.requests,
            "remaining": max(0, rule.requests - current_count - (1 if allowed else 0)),
            "reset": int(window_end),
            "retry_after": int(window_end - current_time) if not allowed else 0,
        }

    def _check_token_bucket(self, key: str, rule: RateLimitRule) -> Tuple[bool, Dict[str, Any]]:
        """Token bucket rate limiting"""
        current_time = time.time()
        bucket = self._buckets[key]

        # Initialize bucket
        if "tokens" not in bucket:
            bucket["tokens"] = rule.requests
            bucket["last_refill"] = current_time

        # Calculate tokens to add
        time_passed = current_time - bucket["last_refill"]
        tokens_to_add = time_passed * (rule.requests / rule.window)
        bucket["tokens"] = min(rule.requests, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time

        # Check if we can consume a token
        allowed = bucket["tokens"] >= 1

        if allowed:
            bucket["tokens"] -= 1

        bucket["last_access"] = current_time

        return allowed, {
            "limit": rule.requests,
            "remaining": int(bucket["tokens"]),
            "reset": int(
                current_time + (rule.requests - bucket["tokens"]) / (rule.requests / rule.window)
            ),
            "retry_after": (
                int((1 - bucket["tokens"]) / (rule.requests / rule.window)) if not allowed else 0
            ),
        }

    async def process_request(self, request: Request) -> Optional[Union[Request, Response]]:
        """Check rate limits"""
        self._cleanup_old_entries()

        rule = self._get_rule_for_request(request)
        key = rule.key_func(request) if rule.key_func else self.key_func(request)

        # Check rate limit based on strategy
        if self.strategy == "sliding_window":
            allowed, info = self._check_sliding_window(key, rule)
        elif self.strategy == "fixed_window":
            allowed, info = self._check_fixed_window(key, rule)
        elif self.strategy == "token_bucket":
            allowed, info = self._check_token_bucket(key, rule)
        else:
            raise ValueError(f"Unknown rate limiting strategy: {self.strategy}")

        # Add rate limit info to request context
        if hasattr(request, "context"):
            request.context["rate_limit"] = info

        if not allowed:
            headers = {
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset"]),
                "Retry-After": str(info["retry_after"]),
            }

            return json_response(
                {"error": "Rate limit exceeded", "retry_after": info["retry_after"]},
                status_code=429,
                headers=headers,
            )

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Add rate limit headers to response"""
        if hasattr(request, "context") and "rate_limit" in request.context:
            info = request.context["rate_limit"]
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset"])

        return response


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseMiddleware):
    """OWASP-compliant security headers middleware"""

    def __init__(self, config: Optional[MiddlewareConfig] = None, **security_options):
        if config is None:
            config = MiddlewareConfig(
                name="security_headers_middleware", priority=Priority.CRITICAL.value
            )

        super().__init__(config)

        # Security headers configuration
        self.hsts_max_age = security_options.get("hsts_max_age", 31536000)  # 1 year
        self.hsts_include_subdomains = security_options.get("hsts_include_subdomains", True)
        self.hsts_preload = security_options.get("hsts_preload", False)

        self.frame_options = security_options.get("frame_options", "DENY")
        self.content_type_options = security_options.get("content_type_options", "nosniff")
        self.xss_protection = security_options.get("xss_protection", "1; mode=block")
        self.referrer_policy = security_options.get(
            "referrer_policy", "strict-origin-when-cross-origin"
        )

        self.csp_policy = security_options.get("csp_policy", "default-src 'self'")
        self.permissions_policy = security_options.get(
            "permissions_policy", "geolocation=(), microphone=(), camera=()"
        )

        self.remove_server_header = security_options.get("remove_server_header", True)
        self.custom_server_header = security_options.get("custom_server_header", "CovetPy")

    async def process_request(self, request: Request) -> Optional[Request]:
        """Security checks on request"""
        # Add security context
        if not hasattr(request, "context"):
            request.context = {}

        request.context["security"] = {
            "request_time": time.time(),
            "is_https": request.scheme == "https",
        }

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Add security headers to response"""

        # HSTS (only for HTTPS)
        if request.scheme == "https":
            hsts_value = f"max-age={self.hsts_max_age}"
            if self.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.hsts_preload:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

        # Frame options
        response.headers["X-Frame-Options"] = self.frame_options

        # Content type options
        response.headers["X-Content-Type-Options"] = self.content_type_options

        # XSS protection
        response.headers["X-XSS-Protection"] = self.xss_protection

        # Referrer policy
        response.headers["Referrer-Policy"] = self.referrer_policy

        # Content Security Policy
        if self.csp_policy:
            response.headers["Content-Security-Policy"] = self.csp_policy

        # Permissions policy
        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy

        # Remove or modify server header
        if self.remove_server_header:
            response.headers.pop("Server", None)
            if self.custom_server_header:
                response.headers["Server"] = self.custom_server_header

        return response


# Compression Middleware
class CompressionMiddleware(BaseMiddleware):
    """High-performance compression middleware with multiple algorithms"""

    def __init__(self, config: Optional[MiddlewareConfig] = None, **compression_options):
        if config is None:
            config = MiddlewareConfig(name="compression_middleware", priority=Priority.NORMAL.value)

        super().__init__(config)

        # Compression configuration
        self.minimum_size = compression_options.get("minimum_size", 1024)  # 1KB
        self.compression_level = compression_options.get("compression_level", 6)
        self.compressible_types = compression_options.get(
            "compressible_types",
            {
                "text/",
                "application/json",
                "application/javascript",
                "application/xml",
                "application/rss+xml",
                "application/atom+xml",
            },
        )
        self.exclude_types = compression_options.get(
            "exclude_types",
            {"image/", "video/", "audio/", "application/zip", "application/gzip"},
        )

        # Algorithm preferences
        self.enable_brotli = compression_options.get("enable_brotli", HAS_BROTLI)
        self.enable_gzip = compression_options.get("enable_gzip", True)

    def _should_compress(self, request: Request, response: Response) -> bool:
        """Check if response should be compressed"""
        # Check content length
        content_length = len(response.get_content_bytes())
        if content_length < self.minimum_size:
            return False

        # Check content type
        content_type = response.headers.get("content-type", "").lower()

        # Check if type is excluded
        for exclude_type in self.exclude_types:
            if content_type.startswith(exclude_type):
                return False

        # Check if type is compressible
        for compressible_type in self.compressible_types:
            if content_type.startswith(compressible_type):
                return True

        return False

    def _get_accepted_encodings(self, request: Request) -> List[str]:
        """Parse Accept-Encoding header"""
        accept_encoding = request.headers.get("accept-encoding", "")

        encodings = []
        for encoding in accept_encoding.split(","):
            encoding = encoding.strip().lower()
            if ";" in encoding:
                encoding = encoding.split(";")[0].strip()

            if encoding in ["gzip", "br", "identity"]:
                encodings.append(encoding)

        return encodings

    def _compress_content(self, content: bytes, encoding: str) -> bytes:
        """Compress content with specified encoding"""
        if encoding == "br" and self.enable_brotli and brotli:
            return brotli.compress(content, quality=self.compression_level)
        elif encoding == "gzip" and self.enable_gzip:
            return gzip.compress(content, compresslevel=self.compression_level)
        else:
            return content

    async def process_request(self, request: Request) -> Optional[Request]:
        """Analyze request for compression support"""
        accepted_encodings = self._get_accepted_encodings(request)

        if not hasattr(request, "context"):
            request.context = {}

        request.context["compression"] = {
            "accepted_encodings": accepted_encodings,
            "supports_brotli": "br" in accepted_encodings and self.enable_brotli,
            "supports_gzip": "gzip" in accepted_encodings and self.enable_gzip,
        }

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Compress response if appropriate"""
        if not hasattr(request, "context") or "compression" not in request.context:
            return response

        # Check if we should compress
        if not self._should_compress(request, response):
            return response

        compression_info = request.context["compression"]
        content = response.get_content_bytes()

        # Choose compression algorithm (prefer brotli over gzip)
        if compression_info["supports_brotli"]:
            compressed_content = self._compress_content(content, "br")
            response.headers["Content-Encoding"] = "br"
        elif compression_info["supports_gzip"]:
            compressed_content = self._compress_content(content, "gzip")
            response.headers["Content-Encoding"] = "gzip"
        else:
            return response

        # Update response with compressed content
        response.content = compressed_content
        response._content_bytes = compressed_content  # Update cached bytes
        response.headers["Content-Length"] = str(len(compressed_content))
        response.headers["Vary"] = response.headers.get("Vary", "") + ", Accept-Encoding"

        return response


# Request Logging Middleware
class RequestLoggingMiddleware(BaseMiddleware):
    """Comprehensive request/response logging middleware"""

    def __init__(self, config: Optional[MiddlewareConfig] = None, **logging_options):
        if config is None:
            config = MiddlewareConfig(
                name="request_logging_middleware", priority=Priority.NORMAL.value
            )

        super().__init__(config)

        # Logging configuration
        self.logger = logging_options.get("logger", logging.getLogger("covetpy.requests"))
        self.log_level = logging_options.get("log_level", logging.INFO)
        self.log_requests = logging_options.get("log_requests", True)
        self.log_responses = logging_options.get("log_responses", True)
        self.log_headers = logging_options.get("log_headers", False)
        self.log_body = logging_options.get("log_body", False)
        self.max_body_size = logging_options.get("max_body_size", 1024)

        # Sensitive data filtering
        self.sensitive_headers = logging_options.get(
            "sensitive_headers",
            {"authorization", "cookie", "x-api-key", "x-auth-token"},
        )
        self.mask_sensitive = logging_options.get("mask_sensitive", True)

    def _mask_sensitive_data(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive headers"""
        if not self.mask_sensitive:
            return headers

        masked_headers = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                masked_headers[key] = "***MASKED***"
            else:
                masked_headers[key] = value

        return masked_headers

    def _truncate_body(self, body: str) -> str:
        """Truncate body if too long"""
        if len(body) > self.max_body_size:
            return body[: self.max_body_size] + "... (truncated)"
        return body

    async def process_request(self, request: Request) -> Optional[Request]:
        """Log incoming request"""
        if not self.log_requests:
            return request

        # Start timing
        start_time = time.time()

        if not hasattr(request, "context"):
            request.context = {}

        request.context["logging"] = {
            "start_time": start_time,
            "request_id": getattr(request, "request_id", f"req_{int(start_time * 1000)}"),
        }

        # Build log message
        log_data = {
            "request_id": request.context["logging"]["request_id"],
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("user-agent", ""),
        }

        if self.log_headers:
            log_data["headers"] = self._mask_sensitive_data(dict(request.headers))

        if self.log_body and hasattr(request, "_body") and request._body:
            try:
                if isinstance(request._body, bytes):
                    body_text = request._body.decode("utf-8", errors="replace")
                else:
                    body_text = str(request._body)
                log_data["body"] = self._truncate_body(body_text)
            except Exception:
                log_data["body"] = "<unable to decode>"

        self.logger.log(self.log_level, f"Request: {request.method} {request.path}", extra=log_data)

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Log outgoing response"""
        if not self.log_responses:
            return response

        if not hasattr(request, "context") or "logging" not in request.context:
            return response

        # Calculate request duration
        start_time = request.context["logging"]["start_time"]
        duration = time.time() - start_time

        # Build log message
        log_data = {
            "request_id": request.context["logging"]["request_id"],
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "response_size": len(response.get_content_bytes()),
        }

        if self.log_headers:
            log_data["response_headers"] = dict(response.headers)

        if self.log_body:
            try:
                content = response.get_content_bytes()
                if content:
                    body_text = content.decode("utf-8", errors="replace")
                    log_data["response_body"] = self._truncate_body(body_text)
            except Exception:
                log_data["response_body"] = "<unable to decode>"

        self.logger.log(
            self.log_level,
            f"Response: {response.status_code} for {request.method} {request.path} ({duration:.3f}s)",
            extra=log_data,
        )

        return response


# Session Middleware
class SessionMiddleware(BaseMiddleware):
    """Secure session management middleware"""

    def __init__(self, config: Optional[MiddlewareConfig] = None, **session_options):
        if config is None:
            config = MiddlewareConfig(name="session_middleware", priority=Priority.HIGH.value)

        super().__init__(config)

        # Session configuration
        self.secret_key = session_options.get("secret_key")
        if not self.secret_key:
            raise ValueError("Session middleware requires a secret_key")

        self.session_cookie = session_options.get("session_cookie", "covet_session")
        self.max_age = session_options.get("max_age", 1209600)  # 2 weeks
        self.domain = session_options.get("domain")
        self.path = session_options.get("path", "/")
        self.secure = session_options.get("secure", True)
        self.http_only = session_options.get("http_only", True)
        self.same_site = session_options.get("same_site", "lax")

        # Storage backend (in-memory by default)
        self.storage = session_options.get("storage", {})
        self.storage_backend = session_options.get("storage_backend", "memory")

    def _generate_session_id(self) -> str:
        """Generate a secure session ID"""
        return secrets.token_urlsafe(32)

    def _sign_session_id(self, session_id: str) -> str:
        """Sign session ID to prevent tampering"""
        signature = hmac.new(
            self.secret_key.encode(), session_id.encode(), hashlib.sha256
        ).hexdigest()
        return f"{session_id}.{signature}"

    def _verify_session_id(self, signed_session_id: str) -> Optional[str]:
        """Verify and extract session ID"""
        try:
            session_id, signature = signed_session_id.rsplit(".", 1)
            expected_signature = hmac.new(
                self.secret_key.encode(), session_id.encode(), hashlib.sha256
            ).hexdigest()

            if hmac.compare_digest(signature, expected_signature):
                return session_id
        except ValueError:
            logger.error(f"Error in _verify_session_id: {e}", exc_info=True)

        return None

    def _get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get session data from storage"""
        if self.storage_backend == "memory":
            return self.storage.get(session_id, {})
        else:
            # Implement other storage backends as needed
            return {}

    def _save_session_data(self, session_id: str, data: Dict[str, Any]) -> None:
        """Save session data to storage"""
        if self.storage_backend == "memory":
            self.storage[session_id] = data
        else:
            # Implement other storage backends as needed
            pass

    def _delete_session_data(self, session_id: str) -> None:
        """Delete session data from storage"""
        if self.storage_backend == "memory":
            self.storage.pop(session_id, None)
        else:
            # Implement other storage backends as needed
            pass

    async def process_request(self, request: Request) -> Optional[Request]:
        """Load session data"""
        # Get session cookie
        cookies = request.cookies()
        signed_session_id = cookies.get(self.session_cookie)

        session_data = {}
        session_id = None

        if signed_session_id:
            session_id = self._verify_session_id(signed_session_id)
            if session_id:
                session_data = self._get_session_data(session_id)

        # Add session to request context
        if not hasattr(request, "context"):
            request.context = {}

        request.context["session"] = {
            "id": session_id,
            "data": session_data,
            "modified": False,
            "new": session_id is None,
        }

        # Add convenience session object
        request.session = SessionObject(request.context["session"])

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Save session data and set cookie"""
        if not hasattr(request, "context") or "session" not in request.context:
            return response

        session_info = request.context["session"]

        # Check if session was modified
        if session_info["modified"] or session_info["new"]:
            session_id = session_info["id"]

            # Generate new session ID if needed
            if not session_id:
                session_id = self._generate_session_id()

            # Save session data
            self._save_session_data(session_id, session_info["data"])

            # Set session cookie
            signed_session_id = self._sign_session_id(session_id)
            response.set_cookie(
                name=self.session_cookie,
                value=signed_session_id,
                max_age=self.max_age,
                domain=self.domain,
                path=self.path,
                secure=self.secure,
                http_only=self.http_only,
                same_site=self.same_site,
            )

        return response


class SessionObject:
    """Session object for easy session manipulation"""

    def __init__(self, session_info: Dict[str, Any]):
        self._info = session_info

    def get(self, key: str, default: Any = None) -> Any:
        """Get session value"""
        return self._info["data"].get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set session value"""
        self._info["data"][key] = value
        self._info["modified"] = True

    def delete(self, key: str) -> None:
        """Delete session value"""
        self._info["data"].pop(key, None)
        self._info["modified"] = True

    def clear(self) -> None:
        """Clear all session data"""
        self._info["data"].clear()
        self._info["modified"] = True

    def __contains__(self, key: str) -> bool:
        return key in self._info["data"]

    def __getitem__(self, key: str) -> Any:
        return self._info["data"][key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.delete(key)


# CSRF Protection Middleware
class CSRFMiddleware(BaseMiddleware):
    """CSRF protection middleware"""

    def __init__(self, config: Optional[MiddlewareConfig] = None, **csrf_options):
        if config is None:
            config = MiddlewareConfig(name="csrf_middleware", priority=Priority.CRITICAL.value)

        super().__init__(config)

        # CSRF configuration
        self.secret_key = csrf_options.get("secret_key")
        if not self.secret_key:
            raise ValueError("CSRF middleware requires a secret_key")

        self.token_name = csrf_options.get("token_name", "csrf_token")
        self.header_name = csrf_options.get("header_name", "X-CSRFToken")
        self.cookie_name = csrf_options.get("cookie_name", "csrf_token")
        self.safe_methods = csrf_options.get("safe_methods", {"GET", "HEAD", "OPTIONS", "TRACE"})
        self.exempt_paths = csrf_options.get("exempt_paths", set())

        # Cookie settings
        self.cookie_secure = csrf_options.get("cookie_secure", True)
        self.cookie_http_only = csrf_options.get("cookie_http_only", False)  # JS needs access
        self.cookie_same_site = csrf_options.get("cookie_same_site", "strict")

    def _generate_csrf_token(self) -> str:
        """Generate a CSRF token"""
        return secrets.token_urlsafe(32)

    def _get_csrf_token_from_request(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request"""
        # Try header first
        token = request.headers.get(self.header_name.lower())
        if token:
            return token

        # Try form data if POST request
        if request.method == "POST" and request.is_form():
            try:
                form_data = request.get_body_bytes().decode("utf-8")
                for part in form_data.split("&"):
                    if "=" in part:
                        key, value = part.split("=", 1)
                        if key == self.token_name:
                            return urllib.parse.unquote_plus(value)
            except Exception:
                logger.error(f"Error in _get_csrf_token_from_request: {e}", exc_info=True)

        return None

    def _is_exempt(self, request: Request) -> bool:
        """Check if request is exempt from CSRF protection"""
        return request.path in self.exempt_paths

    async def process_request(self, request: Request) -> Optional[Union[Request, Response]]:
        """Check CSRF token for unsafe methods"""
        if self._is_exempt(request) or request.method in self.safe_methods:
            return request

        # Get CSRF token from cookie
        cookies = request.cookies()
        csrf_cookie = cookies.get(self.cookie_name)

        if not csrf_cookie:
            return json_response({"error": "CSRF token missing"}, status_code=403)

        # Get CSRF token from request
        csrf_token = self._get_csrf_token_from_request(request)

        if not csrf_token:
            return json_response({"error": "CSRF token not found in request"}, status_code=403)

        # Verify tokens match
        if not hmac.compare_digest(csrf_cookie, csrf_token):
            return json_response({"error": "CSRF token invalid"}, status_code=403)

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Set CSRF token cookie"""
        cookies = request.cookies()

        # Only set cookie if it doesn't exist
        if self.cookie_name not in cookies:
            csrf_token = self._generate_csrf_token()

            response.set_cookie(
                name=self.cookie_name,
                value=csrf_token,
                secure=self.cookie_secure,
                http_only=self.cookie_http_only,
                same_site=self.cookie_same_site,
            )

        return response


# Request ID Middleware
class RequestIDMiddleware(BaseMiddleware):
    """Request ID tracking middleware"""

    def __init__(self, config: Optional[MiddlewareConfig] = None, **request_id_options):
        if config is None:
            config = MiddlewareConfig(
                name="request_id_middleware", priority=Priority.CRITICAL.value
            )

        super().__init__(config)

        self.header_name = request_id_options.get("header_name", "X-Request-ID")
        self.response_header = request_id_options.get("response_header", True)
        self.generator = request_id_options.get("generator", self._default_generator)

    def _default_generator(self) -> str:
        """Default request ID generator"""
        import uuid

        return str(uuid.uuid4())

    async def process_request(self, request: Request) -> Optional[Request]:
        """Add request ID to request"""
        # Check if request already has an ID
        request_id = request.headers.get(self.header_name.lower())

        if not request_id:
            request_id = self.generator()

        # Add to request context
        if not hasattr(request, "context"):
            request.context = {}

        request.context["request_id"] = request_id

        # Also set as attribute for easy access
        request.request_id = request_id

        return request

    async def process_response(self, request: Request, response: Response) -> Response:
        """Add request ID to response headers"""
        if self.response_header and hasattr(request, "context"):
            request_id = request.context.get("request_id")
            if request_id:
                response.headers[self.header_name] = request_id

        return response


# Factory functions for easy middleware creation
def create_cors_middleware(**options) -> CORSMiddleware:
    """Create CORS middleware with options"""
    return CORSMiddleware(**options)


def create_rate_limiting_middleware(**options) -> RateLimitingMiddleware:
    """Create rate limiting middleware with options"""
    return RateLimitingMiddleware(**options)


def create_security_headers_middleware(**options) -> SecurityHeadersMiddleware:
    """Create security headers middleware with options"""
    return SecurityHeadersMiddleware(**options)


def create_compression_middleware(**options) -> CompressionMiddleware:
    """Create compression middleware with options"""
    return CompressionMiddleware(**options)


def create_request_logging_middleware(**options) -> RequestLoggingMiddleware:
    """Create request logging middleware with options"""
    return RequestLoggingMiddleware(**options)


def create_session_middleware(secret_key: str, **options) -> SessionMiddleware:
    """Create session middleware with secret key"""
    return SessionMiddleware(secret_key=secret_key, **options)


def create_csrf_middleware(secret_key: str, **options) -> CSRFMiddleware:
    """Create CSRF middleware with secret key"""
    return CSRFMiddleware(secret_key=secret_key, **options)


def create_request_id_middleware(**options) -> RequestIDMiddleware:
    """Create request ID middleware with options"""
    return RequestIDMiddleware(**options)


# Export all middleware classes and factory functions
__all__ = [
    "CORSMiddleware",
    "RateLimitingMiddleware",
    "RateLimitRule",
    "SecurityHeadersMiddleware",
    "CompressionMiddleware",
    "RequestLoggingMiddleware",
    "SessionMiddleware",
    "SessionObject",
    "CSRFMiddleware",
    "RequestIDMiddleware",
    "create_cors_middleware",
    "create_rate_limiting_middleware",
    "create_security_headers_middleware",
    "create_compression_middleware",
    "create_request_logging_middleware",
    "create_session_middleware",
    "create_csrf_middleware",
    "create_request_id_middleware",
]
