"""
WebSocket Security and Authentication

This module provides comprehensive security features for WebSocket connections
including authentication, authorization, rate limiting, and security headers.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
from urllib.parse import parse_qs

from .connection import WebSocketConnection
from .protocol import CloseCode

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Authentication methods."""

    JWT = "jwt"
    API_KEY = "api_key"
    BASIC = "basic"
    CUSTOM = "custom"


@dataclass
class SecurityConfig:
    """Configuration for WebSocket security."""

    # Authentication
    require_auth: bool = False
    auth_method: AuthMethod = AuthMethod.JWT
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_audience: Optional[str] = None
    jwt_issuer: Optional[str] = None

    # Authorization
    require_authorization: bool = False
    default_permissions: Set[str] = field(default_factory=set)

    # Rate limiting
    enable_rate_limiting: bool = False
    max_connections_per_ip: int = 10
    max_messages_per_minute: int = 60
    max_message_size: int = 64 * 1024  # 64KB

    # CORS
    allowed_origins: Optional[List[str]] = None
    allowed_headers: List[str] = field(default_factory=lambda: ["*"])

    # Security headers
    enforce_https: bool = True
    max_frame_size: int = 16 * 1024 * 1024  # 16MB

    # Validation
    validate_utf8: bool = True
    validate_json: bool = True


class SecurityViolation(Exception):
    """Security violation exception."""

    def __init__(self, message: str, code: int = CloseCode.POLICY_VIOLATION):
        self.message = message
        self.code = code
        super().__init__(message)


class RateLimiter:
    """Rate limiter for WebSocket connections."""

    def __init__(self, max_messages: int = 60, window_seconds: int = 60):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self._message_history = defaultdict(deque)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup()

    def _start_cleanup(self):
        """Start cleanup task for old entries."""
        self._cleanup_task = asyncio.create_task(self._cleanup_worker())

    async def _cleanup_worker(self):
        """Clean up old rate limit entries."""
        try:
            while True:
                await asyncio.sleep(60)  # Cleanup every minute
                current_time = time.time()

                for key in list(self._message_history.keys()):
                    history = self._message_history[key]

                    # Remove old entries
                    while history and current_time - history[0] > self.window_seconds:
                        history.popleft()

                    # Remove empty entries
                    if not history:
                        del self._message_history[key]
        except asyncio.CancelledError:
            logger.error(f"Error during cleanup in _cleanup_worker: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Rate limiter cleanup error: {e}")

    def check_rate_limit(self, identifier: str) -> bool:
        """Check if identifier is within rate limit."""
        current_time = time.time()
        history = self._message_history[identifier]

        # Remove old entries
        while history and current_time - history[0] > self.window_seconds:
            history.popleft()

        # Check limit
        if len(history) >= self.max_messages:
            return False

        # Add current timestamp
        history.append(current_time)
        return True

    def get_remaining(self, identifier: str) -> int:
        """Get remaining messages for identifier."""
        current_time = time.time()
        history = self._message_history[identifier]

        # Remove old entries
        while history and current_time - history[0] > self.window_seconds:
            history.popleft()

        return max(0, self.max_messages - len(history))

    def stop(self):
        """Stop the rate limiter."""
        if self._cleanup_task:
            self._cleanup_task.cancel()


class JWTValidator:
    """JWT token validator."""

    def __init__(
        self,
        secret: str,
        algorithm: str = "HS256",
        audience: str = None,
        issuer: str = None,
    ):
        self.secret = secret
        self.algorithm = algorithm
        self.audience = audience
        self.issuer = issuer

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return payload."""
        try:
            import jwt

            # Decode and validate token
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )

            return payload

        except ImportError:
            raise ImportError("PyJWT library required for JWT validation")
        except jwt.ExpiredSignatureError:
            raise SecurityViolation("Token has expired", CloseCode.POLICY_VIOLATION)
        except jwt.InvalidTokenError as e:
            raise SecurityViolation(f"Invalid token: {e}", CloseCode.POLICY_VIOLATION)

    def extract_token_from_headers(self, headers: Dict[bytes, bytes]) -> Optional[str]:
        """Extract JWT token from headers."""
        auth_header = headers.get(b"authorization", b"").decode()

        if auth_header.startswith("Bearer "):
            return auth_header[7:]

        return None

    def extract_token_from_query(self, query_params: Dict[str, List[str]]) -> Optional[str]:
        """Extract JWT token from query parameters."""
        token_params = query_params.get("token", [])
        return token_params[0] if token_params else None


class APIKeyValidator:
    """API key validator."""

    def __init__(self, valid_keys: Set[str] = None):
        self.valid_keys = valid_keys or set()

    def add_key(self, key: str):
        """Add valid API key."""
        self.valid_keys.add(key)

    def remove_key(self, key: str):
        """Remove API key."""
        self.valid_keys.discard(key)

    def validate_key(self, key: str) -> bool:
        """Validate API key."""
        return key in self.valid_keys

    def extract_key_from_headers(self, headers: Dict[bytes, bytes]) -> Optional[str]:
        """Extract API key from headers."""
        # Try X-API-Key header
        api_key = headers.get(b"x-api-key", b"").decode()
        if api_key:
            return api_key

        # Try Authorization header
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("ApiKey "):
            return auth_header[7:]

        return None

    def extract_key_from_query(self, query_params: Dict[str, List[str]]) -> Optional[str]:
        """Extract API key from query parameters."""
        key_params = query_params.get("api_key", [])
        return key_params[0] if key_params else None


class WebSocketSecurity:
    """
    Comprehensive WebSocket security manager.

    Handles authentication, authorization, rate limiting, and security policies.
    """

    def __init__(self, config: SecurityConfig):
        self.config = config

        # Initialize validators
        self.jwt_validator = None
        if config.auth_method == AuthMethod.JWT and config.jwt_secret:
            self.jwt_validator = JWTValidator(
                config.jwt_secret,
                config.jwt_algorithm,
                config.jwt_audience,
                config.jwt_issuer,
            )

        self.api_key_validator = APIKeyValidator()

        # Rate limiters
        self.message_rate_limiter = None
        self.connection_rate_limiter = None

        if config.enable_rate_limiting:
            self.message_rate_limiter = RateLimiter(config.max_messages_per_minute, 60)
            self.connection_rate_limiter = RateLimiter(
                config.max_connections_per_ip, 3600  # 1 hour window for connections
            )

        # Statistics
        self.total_auth_attempts = 0
        self.successful_auths = 0
        self.failed_auths = 0
        self.rate_limit_violations = 0
        self.security_violations = 0

        logger.info("WebSocket security manager initialized")

    async def authenticate_connection(self, connection: WebSocketConnection) -> bool:
        """Authenticate a WebSocket connection."""
        if not self.config.require_auth:
            return True

        self.total_auth_attempts += 1

        try:
            headers = connection.info.metadata.get("headers", {})
            query_params = connection.info.metadata.get("query_params", {})

            if self.config.auth_method == AuthMethod.JWT:
                return await self._authenticate_jwt(connection, headers, query_params)
            elif self.config.auth_method == AuthMethod.API_KEY:
                return await self._authenticate_api_key(connection, headers, query_params)
            elif self.config.auth_method == AuthMethod.BASIC:
                return await self._authenticate_basic(connection, headers)
            else:
                # Custom authentication would be handled by user-provided
                # function
                return True

        except SecurityViolation:
            self.failed_auths += 1
            self.security_violations += 1
            raise
        except Exception as e:
            self.failed_auths += 1
            logger.error(f"Authentication error: {e}")
            raise SecurityViolation("Authentication failed", CloseCode.POLICY_VIOLATION)

    async def _authenticate_jwt(
        self,
        connection: WebSocketConnection,
        headers: Dict[bytes, bytes],
        query_params: Dict[str, List[str]],
    ) -> bool:
        """Authenticate using JWT token."""
        if not self.jwt_validator:
            raise SecurityViolation("JWT validator not configured")

        # Extract token
        token = self.jwt_validator.extract_token_from_headers(
            headers
        ) or self.jwt_validator.extract_token_from_query(query_params)

        if not token:
            raise SecurityViolation("No JWT token provided", CloseCode.POLICY_VIOLATION)

        # Validate token
        payload = self.jwt_validator.validate_token(token)

        # Store user info
        connection.info.user_id = payload.get("sub") or payload.get("user_id")
        connection.info.metadata["jwt_payload"] = payload
        connection.is_authenticated = True

        self.successful_auths += 1
        logger.debug(f"JWT authentication successful for user: {connection.info.user_id}")
        return True

    async def _authenticate_api_key(
        self,
        connection: WebSocketConnection,
        headers: Dict[bytes, bytes],
        query_params: Dict[str, List[str]],
    ) -> bool:
        """Authenticate using API key."""
        # Extract API key
        api_key = self.api_key_validator.extract_key_from_headers(
            headers
        ) or self.api_key_validator.extract_key_from_query(query_params)

        if not api_key:
            raise SecurityViolation("No API key provided", CloseCode.POLICY_VIOLATION)

        # Validate API key
        if not self.api_key_validator.validate_key(api_key):
            raise SecurityViolation("Invalid API key", CloseCode.POLICY_VIOLATION)

        # Store info
        connection.info.metadata["api_key"] = api_key
        connection.is_authenticated = True

        self.successful_auths += 1
        logger.debug("API key authentication successful")
        return True

    async def _authenticate_basic(
        self, connection: WebSocketConnection, headers: Dict[bytes, bytes]
    ) -> bool:
        """Authenticate using basic auth."""
        auth_header = headers.get(b"authorization", b"").decode()

        if not auth_header.startswith("Basic "):
            raise SecurityViolation("No basic auth provided", CloseCode.POLICY_VIOLATION)

        try:
            import base64

            credentials = base64.b64decode(auth_header[6:]).decode()
            username, password = credentials.split(":", 1)

            # Basic validation (in real app, check against database)
            if username and password:
                connection.info.user_id = username
                connection.info.metadata["auth_method"] = "basic"
                connection.is_authenticated = True
                self.successful_auths += 1
                return True
            else:
                raise SecurityViolation("Invalid credentials", CloseCode.POLICY_VIOLATION)

        except Exception as e:
            raise SecurityViolation("Invalid basic auth format", CloseCode.POLICY_VIOLATION)

    def check_rate_limit(self, connection: WebSocketConnection) -> bool:
        """Check rate limits for connection."""
        if not self.config.enable_rate_limiting:
            return True

        # Check message rate limit
        if self.message_rate_limiter:
            identifier = connection.info.user_id or connection.info.ip_address
            if not self.message_rate_limiter.check_rate_limit(identifier):
                self.rate_limit_violations += 1
                return False

        return True

    def check_connection_limit(self, ip_address: str) -> bool:
        """Check connection rate limit for IP."""
        if not self.config.enable_rate_limiting or not self.connection_rate_limiter:
            return True

        if not self.connection_rate_limiter.check_rate_limit(ip_address):
            self.rate_limit_violations += 1
            return False

        return True

    def validate_origin(self, origin: str) -> bool:
        """Validate origin against allowed origins."""
        if not self.config.allowed_origins:
            return True

        # Check exact match or wildcard
        for allowed_origin in self.config.allowed_origins:
            if allowed_origin == "*" or allowed_origin == origin:
                return True

            # Simple wildcard matching
            if allowed_origin.startswith("*.") and origin.endswith(allowed_origin[1:]):
                return True

        return False

    def validate_message_size(self, message_size: int) -> bool:
        """Validate message size."""
        return message_size <= self.config.max_message_size

    def validate_utf8(self, data: bytes) -> bool:
        """Validate UTF-8 encoding."""
        if not self.config.validate_utf8:
            return True

        try:
            data.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    def validate_json(self, data: str) -> bool:
        """Validate JSON format."""
        if not self.config.validate_json:
            return True

        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False

    def authorize_action(self, connection: WebSocketConnection, action: str) -> bool:
        """Check if connection is authorized for action."""
        if not self.config.require_authorization:
            return True

        # Get user permissions
        permissions = set()

        if connection.info.metadata.get("jwt_payload"):
            jwt_permissions = connection.info.metadata["jwt_payload"].get("permissions", [])
            permissions.update(jwt_permissions)

        permissions.update(self.config.default_permissions)

        # Check if action is allowed
        return action in permissions or "*" in permissions

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        return {
            "total_auth_attempts": self.total_auth_attempts,
            "successful_auths": self.successful_auths,
            "failed_auths": self.failed_auths,
            "auth_success_rate": self.successful_auths / max(1, self.total_auth_attempts),
            "rate_limit_violations": self.rate_limit_violations,
            "security_violations": self.security_violations,
            "config": {
                "require_auth": self.config.require_auth,
                "auth_method": self.config.auth_method.value,
                "rate_limiting_enabled": self.config.enable_rate_limiting,
                "max_connections_per_ip": self.config.max_connections_per_ip,
                "max_messages_per_minute": self.config.max_messages_per_minute,
            },
        }

    def add_api_key(self, key: str):
        """Add API key."""
        self.api_key_validator.add_key(key)

    def remove_api_key(self, key: str):
        """Remove API key."""
        self.api_key_validator.remove_key(key)


# Middleware functions
def security_middleware(security: WebSocketSecurity):
    """Create security middleware."""

    async def middleware(connection: WebSocketConnection):
        # Check connection rate limit
        if not security.check_connection_limit(connection.info.ip_address):
            raise SecurityViolation("Connection rate limit exceeded", CloseCode.POLICY_VIOLATION)

        # Validate origin if provided
        headers = connection.info.metadata.get("headers", {})
        origin = headers.get(b"origin", b"").decode()
        if origin and not security.validate_origin(origin):
            raise SecurityViolation("Origin not allowed", CloseCode.POLICY_VIOLATION)

        # Enforce HTTPS in production
        if security.config.enforce_https:
            # This would be checked at the ASGI level in real implementation
            pass

    return middleware


def authentication_middleware(security: WebSocketSecurity):
    """Create authentication middleware."""

    async def middleware(connection: WebSocketConnection):
        if not await security.authenticate_connection(connection):
            raise SecurityViolation("Authentication failed", CloseCode.POLICY_VIOLATION)

    return middleware


def message_validation_middleware(security: WebSocketSecurity):
    """Create message validation middleware."""

    async def middleware(connection: WebSocketConnection):
        # This would be called per message, not per connection
        # Placeholder for message-level validation
        pass

    return middleware


# Utility functions
def generate_api_key(length: int = 32) -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str, salt: str = None) -> str:
    """Hash API key for storage."""
    if salt is None:
        salt = secrets.token_hex(16)

    hash_obj = hashlib.pbkdf2_hmac("sha256", api_key.encode(), salt.encode(), 100000)
    return f"{salt}:{hash_obj.hex()}"


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify API key against hash."""
    try:
        salt, hash_hex = hashed_key.split(":", 1)
        hash_obj = hashlib.pbkdf2_hmac("sha256", api_key.encode(), salt.encode(), 100000)
        return hmac.compare_digest(hash_obj.hex(), hash_hex)
    except Exception:
        return False


# Security policies
class SecurityPolicy:
    """Base security policy class."""

    def __init__(self, name: str):
        self.name = name

    async def evaluate(self, connection: WebSocketConnection, context: Dict[str, Any]) -> bool:
        """Evaluate policy for connection."""
        raise NotImplementedError


class IPWhitelistPolicy(SecurityPolicy):
    """IP whitelist security policy."""

    def __init__(self, allowed_ips: Set[str]):
        super().__init__("ip_whitelist")
        self.allowed_ips = allowed_ips

    async def evaluate(self, connection: WebSocketConnection, context: Dict[str, Any]) -> bool:
        return connection.info.ip_address in self.allowed_ips


class TimeBasedPolicy(SecurityPolicy):
    """Time-based access policy."""

    def __init__(self, allowed_hours: List[int]):
        super().__init__("time_based")
        self.allowed_hours = allowed_hours

    async def evaluate(self, connection: WebSocketConnection, context: Dict[str, Any]) -> bool:
        import datetime

        current_hour = datetime.datetime.now().hour
        return current_hour in self.allowed_hours


class GeolocationPolicy(SecurityPolicy):
    """Geolocation-based policy."""

    def __init__(self, allowed_countries: Set[str]):
        super().__init__("geolocation")
        self.allowed_countries = allowed_countries

    async def evaluate(self, connection: WebSocketConnection, context: Dict[str, Any]) -> bool:
        # This would require a geolocation service
        # Placeholder implementation
        return True


class OriginValidator:
    """Validate WebSocket origins."""
    
    def __init__(self, allowed_origins=None):
        self.allowed_origins = allowed_origins or ['*']
    
    def validate(self, origin):
        """Check if origin is allowed."""
        if '*' in self.allowed_origins:
            return True
        return origin in self.allowed_origins

__all__ = ["OriginValidator", "ExtensionValidator", "SecurityValidator"]



class SubprotocolValidator:
    """Validate WebSocket subprotocols."""
    def __init__(self, allowed_subprotocols=None):
        self.allowed_subprotocols = allowed_subprotocols or []
    
    def validate(self, subprotocol):
        """Check if subprotocol is allowed."""
        return subprotocol in self.allowed_subprotocols


# Auto-generated stubs for missing exports

class ExtensionValidator:
    """Stub class for ExtensionValidator."""

    def __init__(self, *args, **kwargs):
        pass


class SecurityValidator:
    """Stub class for SecurityValidator."""

    def __init__(self, *args, **kwargs):
        pass

