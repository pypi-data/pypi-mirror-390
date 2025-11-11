"""
CovetPy CSRF (Cross-Site Request Forgery) Protection Module

Comprehensive protection against CSRF attacks using multiple strategies:
- Synchronizer Token Pattern (primary defense)
- Double Submit Cookie Pattern
- SameSite Cookie Attribute
- Origin/Referer Header Validation
- Custom Request Headers
- State Parameter (for OAuth2)

Implements OWASP Top 10 2021 - A01:2021 Broken Access Control (CSRF) protection
with defense-in-depth approach.

Security Architecture:
1. Token-based protection (cryptographically secure tokens)
2. Cookie-based protection (SameSite attribute)
3. Header validation (Origin/Referer checking)
4. Time-based expiration (token TTL)
5. Per-session tokens (session binding)
6. Per-request tokens (for high security)

Author: CovetPy Security Team
License: MIT
"""

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class CSRFTokenType(Enum):
    """Types of CSRF tokens."""

    SESSION = "session"  # One token per session
    PER_REQUEST = "per_request"  # New token for each request
    DOUBLE_SUBMIT = "double_submit"  # Double submit cookie pattern


class CSRFProtectionMethod(Enum):
    """CSRF protection methods."""

    SYNCHRONIZER_TOKEN = "synchronizer_token"
    DOUBLE_SUBMIT_COOKIE = "double_submit_cookie"
    CUSTOM_HEADER = "custom_header"
    ORIGIN_VALIDATION = "origin_validation"


@dataclass
class CSRFToken:
    """CSRF token with metadata."""

    token: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    used: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if token has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if token is valid."""
        if self.used:
            return False
        if self.is_expired():
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "token": self.token,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "used": self.used,
            "metadata": self.metadata,
        }


@dataclass
class CSRFViolation:
    """Details about CSRF violation."""

    violation_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_path: Optional[str] = None
    origin: Optional[str] = None
    referer: Optional[str] = None
    token_present: bool = False
    token_valid: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "violation_type": self.violation_type,
            "timestamp": self.timestamp.isoformat(),
            "request_path": self.request_path,
            "origin": self.origin,
            "referer": self.referer,
            "token_present": self.token_present,
            "token_valid": self.token_valid,
            "metadata": self.metadata,
        }


class CSRFTokenGenerator:
    """
    Cryptographically secure CSRF token generation.

    Tokens are generated using secrets module and can be:
    - Stateless (HMAC-based, no storage required)
    - Stateful (stored in cache/database)
    """

    def __init__(self, secret_key: str, token_length: int = 32):
        """
        Initialize token generator.

        Args:
            secret_key: Secret key for HMAC (keep secret!)
            token_length: Length of generated tokens in bytes
        """
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        self.token_length = token_length

    def generate_token(
        self, session_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> str:
        """
        Generate cryptographically secure CSRF token.

        Args:
            session_id: Optional session ID to bind token to
            user_id: Optional user ID to bind token to

        Returns:
            Base64-encoded CSRF token
        """
        # Generate random token
        random_bytes = secrets.token_bytes(self.token_length)

        # Create token payload
        timestamp = str(int(time.time())).encode()
        session_bytes = (session_id or "").encode()
        user_bytes = (user_id or "").encode()

        # Combine payload
        payload = b"|".join([random_bytes, timestamp, session_bytes, user_bytes])

        # Generate HMAC signature
        signature = hmac.new(self.secret_key, payload, hashlib.sha256).digest()

        # Combine payload and signature
        token_bytes = payload + b"|" + signature

        # Encode as base64
        return base64.urlsafe_b64encode(token_bytes).decode("utf-8")

    def validate_token(
        self,
        token: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        max_age: Optional[int] = None,
    ) -> bool:
        """
        Validate CSRF token.

        Args:
            token: Token to validate
            session_id: Expected session ID
            user_id: Expected user ID
            max_age: Maximum age in seconds (None = no expiration)

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Decode token
            token_bytes = base64.urlsafe_b64decode(token.encode("utf-8"))

            # Split token into parts
            parts = token_bytes.split(b"|")
            if len(parts) != 5:
                return False

            random_bytes, timestamp_bytes, session_bytes, user_bytes, signature = parts

            # Reconstruct payload
            payload = b"|".join([random_bytes, timestamp_bytes, session_bytes, user_bytes])

            # Verify HMAC signature
            expected_signature = hmac.new(self.secret_key, payload, hashlib.sha256).digest()
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("CSRF token HMAC validation failed")
                return False

            # Verify session ID
            if session_id is not None:
                if session_bytes.decode() != session_id:
                    logger.warning("CSRF token session mismatch")
                    return False

            # Verify user ID
            if user_id is not None:
                if user_bytes.decode() != user_id:
                    logger.warning("CSRF token user mismatch")
                    return False

            # Verify age
            if max_age is not None:
                timestamp = int(timestamp_bytes.decode())
                age = int(time.time()) - timestamp
                if age > max_age:
                    logger.warning(f"CSRF token expired (age: {age}s, max: {max_age}s)")
                    return False

            return True

        except Exception as e:
            logger.error(f"CSRF token validation error: {e}")
            return False

    def generate_double_submit_token(self) -> Tuple[str, str]:
        """
        Generate token pair for double submit cookie pattern.

        Returns:
            Tuple of (cookie_token, form_token)
        """
        # Generate random token
        token = secrets.token_urlsafe(self.token_length)

        # For double submit, both tokens are the same
        # The security comes from the browser's same-origin policy
        return token, token


class CSRFTokenStore:
    """
    Token storage for stateful CSRF protection.

    Tokens can be stored in:
    - Memory (for development)
    - Redis (for production)
    - Database (for persistence)
    """

    def __init__(self):
        """Initialize token store."""
        self._tokens: Dict[str, CSRFToken] = {}

    def store_token(self, token: CSRFToken) -> None:
        """
        Store CSRF token.

        Args:
            token: Token to store
        """
        self._tokens[token.token] = token

    def get_token(self, token_value: str) -> Optional[CSRFToken]:
        """
        Retrieve CSRF token.

        Args:
            token_value: Token value

        Returns:
            CSRFToken if found, None otherwise
        """
        return self._tokens.get(token_value)

    def invalidate_token(self, token_value: str) -> None:
        """
        Invalidate CSRF token.

        Args:
            token_value: Token value to invalidate
        """
        if token_value in self._tokens:
            self._tokens[token_value].used = True

    def cleanup_expired(self) -> int:
        """
        Remove expired tokens.

        Returns:
            Number of tokens removed
        """
        expired = [token_value for token_value, token in self._tokens.items() if token.is_expired()]

        for token_value in expired:
            del self._tokens[token_value]

        return len(expired)

    def get_session_tokens(self, session_id: str) -> List[CSRFToken]:
        """
        Get all tokens for a session.

        Args:
            session_id: Session ID

        Returns:
            List of tokens for session
        """
        return [token for token in self._tokens.values() if token.session_id == session_id]


class CSRFProtector:
    """
    Main CSRF protection system.

    Implements multiple CSRF protection strategies with defense-in-depth.
    """

    # HTTP methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    # HTTP methods that are safe (no CSRF protection needed)
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

    # Header name for CSRF token
    TOKEN_HEADER_NAME = "X-CSRF-Token"

    # Cookie name for CSRF token
    COOKIE_NAME = "csrf_token"

    # Form field name for CSRF token
    FORM_FIELD_NAME = "csrf_token"

    def __init__(
        self,
        secret_key: str,
        token_type: CSRFTokenType = CSRFTokenType.SESSION,
        token_ttl: int = 3600,  # 1 hour
        use_double_submit: bool = False,
        validate_origin: bool = True,
        validate_referer: bool = True,
        require_custom_header: bool = False,
        same_site: str = "Lax",
        secure_cookie: bool = True,
        store: Optional[CSRFTokenStore] = None,
    ):
        """
        Initialize CSRF protector.

        Args:
            secret_key: Secret key for token generation
            token_type: Type of CSRF token
            token_ttl: Token time-to-live in seconds
            use_double_submit: Use double submit cookie pattern
            validate_origin: Validate Origin header
            validate_referer: Validate Referer header
            require_custom_header: Require custom header (for AJAX)
            same_site: SameSite cookie attribute ("Strict", "Lax", "None")
            secure_cookie: Use Secure cookie attribute (HTTPS only)
            store: Token store (None = create in-memory store)
        """
        self.generator = CSRFTokenGenerator(secret_key)
        self.token_type = token_type
        self.token_ttl = token_ttl
        self.use_double_submit = use_double_submit
        self.validate_origin = validate_origin
        self.validate_referer = validate_referer
        self.require_custom_header = require_custom_header
        self.same_site = same_site
        self.secure_cookie = secure_cookie
        self.store = store or CSRFTokenStore()

        self._violations: List[CSRFViolation] = []

    def generate_token(
        self, session_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> CSRFToken:
        """
        Generate new CSRF token.

        Args:
            session_id: Session ID to bind token to
            user_id: User ID to bind token to

        Returns:
            Generated CSRF token
        """
        # Generate token string
        token_value = self.generator.generate_token(session_id, user_id)

        # Create token object
        token = CSRFToken(
            token=token_value,
            created_at=datetime.utcnow(),
            expires_at=(
                datetime.utcnow() + timedelta(seconds=self.token_ttl) if self.token_ttl else None
            ),
            session_id=session_id,
            user_id=user_id,
        )

        # Store token if using stateful tokens
        if self.token_type == CSRFTokenType.PER_REQUEST:
            self.store.store_token(token)

        return token

    def validate_token(
        self, token_value: str, session_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> bool:
        """
        Validate CSRF token.

        Args:
            token_value: Token to validate
            session_id: Expected session ID
            user_id: Expected user ID

        Returns:
            True if token is valid, False otherwise
        """
        # For double submit, validation is simpler
        if self.use_double_submit:
            return bool(token_value)  # Just check presence (validated via cookie comparison)

        # For per-request tokens, check store
        if self.token_type == CSRFTokenType.PER_REQUEST:
            stored_token = self.store.get_token(token_value)
            if stored_token is None:
                logger.warning("CSRF token not found in store")
                return False

            if not stored_token.is_valid():
                logger.warning("CSRF token is invalid or expired")
                return False

            # Mark token as used (one-time use)
            self.store.invalidate_token(token_value)

            return True

        # For session tokens, validate using HMAC
        return self.generator.validate_token(
            token_value, session_id=session_id, user_id=user_id, max_age=self.token_ttl
        )

    def validate_origin(self, origin: Optional[str], host: str) -> bool:
        """
        Validate Origin header.

        Args:
            origin: Origin header value
            host: Expected host

        Returns:
            True if origin is valid, False otherwise
        """
        if not origin:
            return False

        # Parse origin
        try:
            parsed = urllib.parse.urlparse(origin)
            origin_host = parsed.netloc
        except Exception:
            return False

        # Compare hosts
        return origin_host == host

    def validate_referer(self, referer: Optional[str], host: str) -> bool:
        """
        Validate Referer header.

        Args:
            referer: Referer header value
            host: Expected host

        Returns:
            True if referer is valid, False otherwise
        """
        if not referer:
            return False

        # Parse referer
        try:
            parsed = urllib.parse.urlparse(referer)
            referer_host = parsed.netloc
        except Exception:
            return False

        # Compare hosts
        return referer_host == host

    def check_request(
        self,
        method: str,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        form_data: Optional[Dict[str, str]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[CSRFViolation]]:
        """
        Check request for CSRF protection.

        Args:
            method: HTTP method
            headers: Request headers
            cookies: Request cookies
            form_data: Form data (for POST requests)
            session_id: Session ID
            user_id: User ID

        Returns:
            Tuple of (is_valid, violation_details)
        """
        # Safe methods don't require CSRF protection
        if method.upper() in self.SAFE_METHODS:
            return True, None

        violation = CSRFViolation(
            violation_type="csrf_check",
            request_path=headers.get("path"),
            origin=headers.get("Origin"),
            referer=headers.get("Referer"),
        )

        # Check for custom header (AJAX requests)
        if self.require_custom_header:
            if self.TOKEN_HEADER_NAME not in headers:
                violation.violation_type = "missing_custom_header"
                self._violations.append(violation)
                logger.warning("CSRF: Missing custom header")
                return False, violation

        # Validate Origin header
        if self.validate_origin:
            origin = headers.get("Origin")
            host = headers.get("Host", "")
            if origin and not self.validate_origin(origin, host):
                violation.violation_type = "invalid_origin"
                self._violations.append(violation)
                logger.warning(f"CSRF: Invalid origin: {origin} != {host}")
                return False, violation

        # Validate Referer header (fallback if Origin not present)
        if self.validate_referer:
            referer = headers.get("Referer")
            host = headers.get("Host", "")
            if referer and not self.validate_referer(referer, host):
                violation.violation_type = "invalid_referer"
                self._violations.append(violation)
                logger.warning(f"CSRF: Invalid referer: {referer} != {host}")
                return False, violation

        # Get token from header or form data
        token = headers.get(self.TOKEN_HEADER_NAME)
        if not token and form_data:
            token = form_data.get(self.FORM_FIELD_NAME)

        violation.token_present = bool(token)

        if not token:
            violation.violation_type = "missing_token"
            self._violations.append(violation)
            logger.warning("CSRF: Missing token")
            return False, violation

        # For double submit, compare cookie and token
        if self.use_double_submit:
            cookie_token = cookies.get(self.COOKIE_NAME)
            if not cookie_token or not hmac.compare_digest(token, cookie_token):
                violation.violation_type = "token_mismatch"
                self._violations.append(violation)
                logger.warning("CSRF: Double submit token mismatch")
                return False, violation
            violation.token_valid = True
            return True, None

        # Validate token
        is_valid = self.validate_token(token, session_id=session_id, user_id=user_id)
        violation.token_valid = is_valid

        if not is_valid:
            violation.violation_type = "invalid_token"
            self._violations.append(violation)
            logger.warning("CSRF: Invalid token")
            return False, violation

        return True, None

    def get_violations(self) -> List[CSRFViolation]:
        """Get list of CSRF violations."""
        return self._violations.copy()

    def clear_violations(self) -> None:
        """Clear violation history."""
        self._violations.clear()


class CSRFProtectionMiddleware:
    """
    CSRF protection middleware for CovetPy applications.
    """

    def __init__(
        self,
        protector: CSRFProtector,
        exempt_paths: Optional[Set[str]] = None,
        audit_callback: Optional[Callable[[CSRFViolation], None]] = None,
    ):
        """
        Initialize CSRF protection middleware.

        Args:
            protector: CSRF protector instance
            exempt_paths: Paths exempt from CSRF protection (e.g., /api/webhook)
            audit_callback: Callback for CSRF violations
        """
        self.protector = protector
        self.exempt_paths = exempt_paths or set()
        self.audit_callback = audit_callback
        self._blocked_requests = 0

    async def __call__(self, scope, receive, send):
        """ASGI middleware interface."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        method = scope["method"]
        path = scope["path"]

        # Skip CSRF check for exempt paths
        if path in self.exempt_paths:
            return await self.app(scope, receive, send)

        # Skip CSRF check for safe methods
        if method in CSRFProtector.SAFE_METHODS:
            return await self.app(scope, receive, send)

        # Parse headers
        headers = {}
        for header_name, header_value in scope.get("headers", []):
            headers[header_name.decode("utf-8")] = header_value.decode("utf-8")

        # Parse cookies
        cookies = {}
        cookie_header = headers.get("cookie", "")
        for cookie in cookie_header.split(";"):
            if "=" in cookie:
                name, value = cookie.strip().split("=", 1)
                cookies[name] = value

        # Get session info from scope (if available)
        session_id = scope.get("session", {}).get("id")
        user_id = scope.get("user", {}).get("id")

        # Check CSRF protection
        is_valid, violation = self.protector.check_request(
            method=method,
            headers={**headers, "path": path},
            cookies=cookies,
            session_id=session_id,
            user_id=user_id,
        )

        if not is_valid:
            self._blocked_requests += 1

            # Audit callback
            if self.audit_callback and violation:
                self.audit_callback(violation)

            # Send 403 Forbidden response
            await self._send_forbidden(send, violation)
            return

        # Continue to application
        await self.app(scope, receive, send)

    async def _send_forbidden(self, send, violation: Optional[CSRFViolation]):
        """Send 403 Forbidden response."""
        await send(
            {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    (b"content-type", b"application/json"),
                ],
            }
        )

        body = json.dumps(
            {
                "error": "CSRF validation failed",
                "violation": violation.to_dict() if violation else None,
            }
        ).encode()

        await send({"type": "http.response.body", "body": body})

    def get_statistics(self) -> Dict[str, int]:
        """Get protection statistics."""
        return {
            "blocked_requests": self._blocked_requests,
            "total_violations": len(self.protector.get_violations()),
        }


# Convenience functions


def generate_csrf_token(secret_key: str, session_id: Optional[str] = None) -> str:
    """Generate CSRF token (convenience function)."""
    generator = CSRFTokenGenerator(secret_key)
    return generator.generate_token(session_id)


def validate_csrf_token(
    token: str, secret_key: str, session_id: Optional[str] = None, max_age: int = 3600
) -> bool:
    """Validate CSRF token (convenience function)."""
    generator = CSRFTokenGenerator(secret_key)
    return generator.validate_token(token, session_id=session_id, max_age=max_age)


__all__ = [
    # Enums
    "CSRFTokenType",
    "CSRFProtectionMethod",
    # Data classes
    "CSRFToken",
    "CSRFViolation",
    # Core classes
    "CSRFTokenGenerator",
    "CSRFTokenStore",
    "CSRFProtector",
    # Middleware
    "CSRFProtectionMiddleware",
    # Convenience functions
    "generate_csrf_token",
    "validate_csrf_token",
]
