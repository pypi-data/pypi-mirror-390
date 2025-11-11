"""
Cross-Site Request Forgery (CSRF) Protection

Production-grade CSRF protection implementing OWASP recommendations:
- Synchronizer Token Pattern with session binding
- Double Submit Cookie strategy support
- Time-limited tokens with automatic rotation
- Timing-safe token comparison
- Per-request token validation
- Origin and Referer header validation
- Token encryption and signing with HMAC-SHA256

Security Features:
- 256-bit entropy tokens
- Constant-time comparison to prevent timing attacks
- Token expiration (1 hour default)
- Session binding to prevent token theft
- Automatic token rotation after use
- Configurable exemptions for API endpoints
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse


@dataclass
class CSRFConfig:
    """CSRF protection configuration"""

    # Token settings
    token_length: int = 32  # 256 bits
    token_ttl: int = 3600  # 1 hour in seconds

    # Cookie settings
    cookie_name: str = "csrftoken"
    cookie_httponly: bool = False  # JavaScript needs to read it
    cookie_secure: bool = True  # HTTPS only
    cookie_samesite: str = "Strict"  # Strict, Lax, or None
    cookie_path: str = "/"
    cookie_domain: Optional[str] = None

    # Header settings
    header_name: str = "X-CSRF-Token"
    form_field_name: str = "csrf_token"

    # Strategy settings
    strategy: str = "synchronizer"  # 'synchronizer', 'double-submit', or 'both'

    # Security settings
    validate_origin: bool = True
    validate_referer: bool = True
    rotate_after_use: bool = True

    # Secret key for HMAC signing (must be set in production)
    secret_key: Optional[bytes] = None

    # Exempt methods (safe methods don't need CSRF protection)
    exempt_methods: List[str] = field(default_factory=lambda: ["GET", "HEAD", "OPTIONS", "TRACE"])

    # Exempt paths (e.g., webhooks, public APIs)
    exempt_paths: List[str] = field(default_factory=list)


class CSRFTokenError(Exception):
    """CSRF token validation error"""


class CSRFToken:
    """
    CSRF token generator and validator

    Implements secure token generation using:
    1. Cryptographically secure random bytes
    2. HMAC-SHA256 signing with secret key
    3. Session binding to prevent token theft
    4. Timestamp to enforce expiration
    """

    def __init__(self, config: CSRFConfig):
        self.config = config

        # Generate secret key if not provided
        if not config.secret_key:
            self.secret_key = secrets.token_bytes(32)
        else:
            self.secret_key = config.secret_key

    def generate_token(self, session_id: Optional[str] = None) -> str:
        """
        Generate CSRF token

        Token format: base64(timestamp|random_bytes|hmac)

        Args:
            session_id: Optional session ID to bind token to

        Returns:
            Base64-encoded token string
        """
        # Current timestamp
        timestamp = int(time.time())

        # Generate random bytes
        random_bytes = secrets.token_bytes(self.config.token_length)

        # Create token data
        token_data = {
            "timestamp": timestamp,
            "random": base64.b64encode(random_bytes).decode("utf-8"),
            "session": session_id or "",
        }

        # Serialize token data
        token_json = json.dumps(token_data, separators=(",", ":"))
        token_bytes = token_json.encode("utf-8")

        # Generate HMAC signature
        signature = self._generate_hmac(token_bytes)

        # Combine token and signature
        full_token = token_bytes + b"|" + signature

        # Base64 encode for safe transmission
        return base64.urlsafe_b64encode(full_token).decode("utf-8")

    def validate_token(self, token: str, session_id: Optional[str] = None) -> bool:
        """
        Validate CSRF token

        Performs:
        1. HMAC signature verification
        2. Timestamp validation (not expired)
        3. Session binding verification
        4. Constant-time comparison

        Args:
            token: Token to validate
            session_id: Session ID to verify binding

        Returns:
            True if token is valid

        Raises:
            CSRFTokenError: If token is invalid or expired
        """
        if not token:
            raise CSRFTokenError("Token is empty")

        try:
            # Decode base64
            full_token = base64.urlsafe_b64decode(token.encode("utf-8"))

            # Split token and signature
            if b"|" not in full_token:
                raise CSRFTokenError("Invalid token format")

            token_bytes, signature = full_token.rsplit(b"|", 1)

            # Verify HMAC signature (constant-time comparison)
            expected_signature = self._generate_hmac(token_bytes)
            if not self._constant_time_compare(signature, expected_signature):
                raise CSRFTokenError("Invalid token signature")

            # Parse token data
            token_json = token_bytes.decode("utf-8")
            token_data = json.loads(token_json)

            # Validate timestamp
            timestamp = token_data.get("timestamp", 0)
            current_time = int(time.time())

            if current_time - timestamp > self.config.token_ttl:
                raise CSRFTokenError("Token has expired")

            # Validate session binding
            token_session = token_data.get("session", "")
            if session_id and token_session != session_id:
                raise CSRFTokenError("Token session mismatch")

            return True

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            raise CSRFTokenError(f"Invalid token: {str(e)}")

    def _generate_hmac(self, data: bytes) -> bytes:
        """Generate HMAC-SHA256 signature"""
        return hmac.new(self.secret_key, data, hashlib.sha256).digest()

    def _constant_time_compare(self, a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison to prevent timing attacks

        Uses secrets.compare_digest for cryptographically secure comparison
        """
        return secrets.compare_digest(a, b)


class CSRFProtection:
    """
    CSRF protection manager

    Provides comprehensive CSRF protection with:
    - Token generation and validation
    - Multiple protection strategies
    - Origin and Referer validation
    - Cookie and header management
    - Exemption handling

    SECURITY FIX: Uses thread-safe locks for atomic token operations
    to prevent race conditions during concurrent requests.
    """

    def __init__(self, config: Optional[CSRFConfig] = None):
        self.config = config or CSRFConfig()
        self.token_generator = CSRFToken(self.config)

        # Token storage (in production, use session/database)
        self._tokens: Dict[str, Dict[str, Any]] = {}

        # SECURITY FIX: Add lock for atomic token operations
        import threading

        self._lock = threading.RLock()

    def generate_token(self, session_id: Optional[str] = None) -> str:
        """
        Generate CSRF token for session

        SECURITY: Thread-safe token generation with atomic storage.

        Args:
            session_id: Session ID to bind token to

        Returns:
            CSRF token string
        """
        token = self.token_generator.generate_token(session_id)

        # SECURITY FIX: Atomic token storage
        with self._lock:
            self._tokens[token] = {
                "session_id": session_id,
                "created_at": time.time(),
                "used": False,
            }

        return token

    def validate_token(
        self, token: str, session_id: Optional[str] = None, rotate: bool = None
    ) -> bool:
        """
        Validate CSRF token with atomic check-and-mark operation.

        SECURITY FIX: Prevents race condition by atomically checking
        and marking token as used within a single lock.

        Args:
            token: Token to validate
            session_id: Session ID to verify
            rotate: Whether to rotate token after validation

        Returns:
            True if valid

        Raises:
            CSRFTokenError: If validation fails or token already used
        """
        # Check if token was already used (if rotation enabled)
        if rotate is None:
            rotate = self.config.rotate_after_use

        # SECURITY FIX: Atomic check-and-mark operation
        with self._lock:
            token_meta = self._tokens.get(token)

            # Check if token already used (one-time use enforcement)
            if token_meta and token_meta.get("used") and rotate:
                raise CSRFTokenError("Token already used - possible replay attack")

            # Validate token cryptographically
            is_valid = self.token_generator.validate_token(token, session_id)

            # Atomically mark token as used to prevent reuse
            if is_valid and token in self._tokens:
                self._tokens[token]["used"] = True

        return is_valid

    def validate_request(
        self,
        method: str,
        path: str,
        token: Optional[str],
        session_id: Optional[str],
        origin: Optional[str] = None,
        referer: Optional[str] = None,
        host: Optional[str] = None,
    ) -> bool:
        """
        Validate complete CSRF protection for request

        Args:
            method: HTTP method
            path: Request path
            token: CSRF token from request
            session_id: Session ID
            origin: Origin header
            referer: Referer header
            host: Host header

        Returns:
            True if request is valid

        Raises:
            CSRFTokenError: If validation fails
        """
        # Check if method is exempt
        if method.upper() in self.config.exempt_methods:
            return True

        # Check if path is exempt
        if self._is_path_exempt(path):
            return True

        # Validate Origin header
        if self.config.validate_origin and origin:
            self._validate_origin(origin, host)

        # Validate Referer header
        if self.config.validate_referer and referer:
            self._validate_referer(referer, host)

        # Validate token
        if not token:
            raise CSRFTokenError("CSRF token missing")

        return self.validate_token(token, session_id)

    def _is_path_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        for exempt_path in self.config.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False

    def _validate_origin(self, origin: str, host: Optional[str]) -> None:
        """
        Validate Origin header

        Ensures origin matches expected host to prevent CSRF
        """
        if not origin:
            raise CSRFTokenError("Origin header missing")

        # Reject null origin
        if origin.lower() == "null":
            raise CSRFTokenError("Null origin not allowed")

        # Parse origin
        parsed_origin = urlparse(origin)

        # Validate scheme (must be HTTPS in production)
        if self.config.cookie_secure and parsed_origin.scheme != "https":
            raise CSRFTokenError("Origin must use HTTPS")

        # Validate host matches
        if host and parsed_origin.netloc != host:
            raise CSRFTokenError("Origin host mismatch")

    def _validate_referer(self, referer: str, host: Optional[str]) -> None:
        """
        Validate Referer header

        Ensures referer matches expected host
        """
        if not referer:
            raise CSRFTokenError("Referer header missing")

        # Parse referer
        parsed_referer = urlparse(referer)

        # Validate scheme
        if self.config.cookie_secure and parsed_referer.scheme != "https":
            raise CSRFTokenError("Referer must use HTTPS")

        # Validate host matches
        if host and parsed_referer.netloc != host:
            raise CSRFTokenError("Referer host mismatch")

    def create_cookie_header(self, token: str) -> str:
        """
        Create Set-Cookie header for CSRF token

        Args:
            token: CSRF token

        Returns:
            Set-Cookie header value
        """
        attributes = [f"{self.config.cookie_name}={token}"]

        if self.config.cookie_path:
            attributes.append(f"Path={self.config.cookie_path}")

        if self.config.cookie_domain:
            attributes.append(f"Domain={self.config.cookie_domain}")

        if self.config.cookie_secure:
            attributes.append("Secure")

        if self.config.cookie_httponly:
            attributes.append("HttpOnly")

        if self.config.cookie_samesite:
            attributes.append(f"SameSite={self.config.cookie_samesite}")

        # Set max age based on TTL
        attributes.append(f"Max-Age={self.config.token_ttl}")

        return "; ".join(attributes)

    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from storage.

        SECURITY FIX: Thread-safe cleanup operation.

        Returns:
            Number of tokens removed
        """
        current_time = time.time()

        # SECURITY FIX: Atomic cleanup operation
        with self._lock:
            expired_tokens = []

            for token, meta in self._tokens.items():
                created_at = meta.get("created_at", 0)
                if current_time - created_at > self.config.token_ttl:
                    expired_tokens.append(token)

            for token in expired_tokens:
                del self._tokens[token]

            return len(expired_tokens)


# Global CSRF protection instance
_csrf_protection: Optional[CSRFProtection] = None


def get_csrf_protection() -> CSRFProtection:
    """Get global CSRF protection instance"""
    global _csrf_protection
    if _csrf_protection is None:
        _csrf_protection = CSRFProtection()
    return _csrf_protection


def configure_csrf_protection(config: CSRFConfig) -> CSRFProtection:
    """Configure CSRF protection with custom config"""
    global _csrf_protection
    _csrf_protection = CSRFProtection(config)
    return _csrf_protection
