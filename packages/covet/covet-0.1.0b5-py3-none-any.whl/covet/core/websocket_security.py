"""
WebSocket Security and Authentication

This module provides comprehensive security features for WebSocket connections
including authentication, authorization, rate limiting, and security validation.
"""

import asyncio
import hashlib
import hmac
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Union
from urllib.parse import parse_qs, urlparse

import jwt

from .websocket_connection import WebSocketConnection
from .websocket_impl import CloseCode, WebSocketError

logger = logging.getLogger(__name__)


class SecurityError(WebSocketError):
    """WebSocket security-related error."""


class AuthenticationError(SecurityError):
    """Authentication failed."""


class AuthorizationError(SecurityError):
    """Authorization failed."""


class RateLimitError(SecurityError):
    """Rate limit exceeded."""


@dataclass
class SecurityConfig:
    """WebSocket security configuration."""

    # Authentication
    require_auth: bool = False
    auth_timeout: float = 30.0
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"

    # Origin validation
    allowed_origins: Optional[List[str]] = None
    require_origin: bool = False

    # Rate limiting
    enable_rate_limiting: bool = True
    max_connections_per_ip: int = 100
    max_messages_per_minute: int = 60
    max_message_size: int = 1024 * 1024  # 1MB

    # Security headers
    check_user_agent: bool = True
    blocked_user_agents: List[str] = field(default_factory=list)

    # CSRF protection
    enable_csrf_protection: bool = False
    csrf_token_header: str = "x-csrf-token"

    # IP filtering
    blocked_ips: Set[str] = field(default_factory=set)
    # If set, only these IPs are allowed
    allowed_ips: Optional[Set[str]] = None


class TokenValidator:
    """JWT token validator for WebSocket authentication."""

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and return payload.

        Args:
            token: JWT token string

        Returns:
            dict: Token payload

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])

            # Check expiration
            if "exp" in payload:
                if time.time() > payload["exp"]:
                    raise AuthenticationError("Token expired")

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {e}")

    def create_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """
        Create JWT token.

        Args:
            payload: Token payload
            expires_in: Expiration time in seconds

        Returns:
            str: JWT token
        """
        payload = payload.copy()
        payload["exp"] = time.time() + expires_in

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)


class RateLimiter:
    """Advanced rate limiter with multiple strategies."""

    def __init__(self):
        # Connection limits per IP
        self.connections_per_ip: Dict[str, int] = defaultdict(int)

        # Message rate limiting (sliding window)
        self.message_windows: Dict[str, deque] = defaultdict(deque)

        # Burst protection
        self.burst_counters: Dict[str, Dict[str, int]] = defaultdict(dict)

        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup()

    def _start_cleanup(self):
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())

    async def _cleanup_expired(self):
        """Clean up expired rate limit data."""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute

                current_time = time.time()

                # Clean up message windows
                for client_id, window in list(self.message_windows.items()):
                    # Remove messages older than 1 minute
                    while window and current_time - window[0] > 60:
                        window.popleft()

                    if not window:
                        del self.message_windows[client_id]

                # Clean up burst counters
                for client_id, counters in list(self.burst_counters.items()):
                    for window_start in list(counters.keys()):
                        if current_time - float(window_start) > 60:
                            del counters[window_start]

                    if not counters:
                        del self.burst_counters[client_id]

            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")

    def check_connection_limit(self, ip: str, max_connections: int) -> bool:
        """Check if IP is within connection limits."""
        return self.connections_per_ip[ip] < max_connections

    def add_connection(self, ip: str):
        """Register new connection for IP."""
        self.connections_per_ip[ip] += 1

    def remove_connection(self, ip: str):
        """Remove connection for IP."""
        if ip in self.connections_per_ip:
            self.connections_per_ip[ip] -= 1
            if self.connections_per_ip[ip] <= 0:
                del self.connections_per_ip[ip]

    def check_message_rate(self, client_id: str, max_per_minute: int) -> bool:
        """Check if client is within message rate limits."""
        current_time = time.time()
        window = self.message_windows[client_id]

        # Remove messages older than 1 minute
        while window and current_time - window[0] > 60:
            window.popleft()

        # Check limit
        return len(window) < max_per_minute

    def record_message(self, client_id: str):
        """Record a message for rate limiting."""
        self.message_windows[client_id].append(time.time())

    def check_burst_limit(
        self, client_id: str, max_burst: int = 10, window_seconds: int = 10
    ) -> bool:
        """Check burst rate limits (short-term)."""
        current_time = time.time()
        window_start = str(int(current_time // window_seconds) * window_seconds)

        burst_count = self.burst_counters[client_id].get(window_start, 0)
        return burst_count < max_burst

    def record_burst(self, client_id: str, window_seconds: int = 10):
        """Record a message for burst limiting."""
        current_time = time.time()
        window_start = str(int(current_time // window_seconds) * window_seconds)

        self.burst_counters[client_id][window_start] = (
            self.burst_counters[client_id].get(window_start, 0) + 1
        )


class WebSocketSecurity:
    """
    Comprehensive WebSocket security manager.

    Provides authentication, authorization, rate limiting, and security validation.
    """

    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.rate_limiter = RateLimiter()

        # Token validator
        self.token_validator = None
        if self.config.jwt_secret:
            self.token_validator = TokenValidator(self.config.jwt_secret, self.config.jwt_algorithm)

        # Authentication providers
        self.auth_providers: Dict[str, Callable] = {}

        # Authorization handlers
        self.authz_handlers: Dict[str, Callable] = {}

        # Session storage
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def add_auth_provider(self, name: str, provider: Callable):
        """Add authentication provider."""
        self.auth_providers[name] = provider

    def add_authz_handler(self, resource: str, handler: Callable):
        """Add authorization handler for a resource."""
        self.authz_handlers[resource] = handler

    async def validate_connection(self, connection: WebSocketConnection) -> bool:
        """
        Validate WebSocket connection security.

        Args:
            connection: WebSocket connection to validate

        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # IP filtering
            if not self._check_ip_filtering(connection):
                await connection.close(CloseCode.POLICY_VIOLATION, "IP not allowed")
                return False

            # Origin validation
            if not self._check_origin(connection):
                await connection.close(CloseCode.POLICY_VIOLATION, "Origin not allowed")
                return False

            # User agent validation
            if not self._check_user_agent(connection):
                await connection.close(CloseCode.POLICY_VIOLATION, "User agent not allowed")
                return False

            # Connection rate limiting
            if not self._check_connection_limits(connection):
                await connection.close(CloseCode.POLICY_VIOLATION, "Too many connections")
                return False

            # CSRF protection
            if not self._check_csrf_protection(connection):
                await connection.close(CloseCode.POLICY_VIOLATION, "CSRF validation failed")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating connection: {e}", exc_info=True)
            await connection.close(CloseCode.INTERNAL_ERROR, "Security validation error")
            return False

    async def authenticate_connection(
        self, connection: WebSocketConnection, credentials: Dict[str, Any]
    ) -> bool:
        """
        Authenticate WebSocket connection.

        Args:
            connection: WebSocket connection
            credentials: Authentication credentials

        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            auth_type = credentials.get("type", "token")

            if auth_type == "token" and self.token_validator:
                return await self._authenticate_token(connection, credentials)
            elif auth_type in self.auth_providers:
                provider = self.auth_providers[auth_type]
                return await provider(connection, credentials)
            else:
                raise AuthenticationError(f"Unknown auth type: {auth_type}")

        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {e}")
            await connection.close(CloseCode.POLICY_VIOLATION, str(e))
            return False
        except Exception as e:
            logger.error(f"Error authenticating connection: {e}", exc_info=True)
            await connection.close(CloseCode.INTERNAL_ERROR, "Authentication error")
            return False

    async def _authenticate_token(
        self, connection: WebSocketConnection, credentials: Dict[str, Any]
    ) -> bool:
        """Authenticate using JWT token."""
        token = credentials.get("token")
        if not token:
            raise AuthenticationError("Token required")

        payload = self.token_validator.validate_token(token)

        # Extract user info
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            raise AuthenticationError("Token missing user ID")

        # Authenticate connection
        connection.authenticate(
            user_id=user_id, metadata={"token_payload": payload, "auth_type": "token"}
        )

        logger.info(f"Token authentication successful for user {user_id}")
        return True

    async def authorize_action(
        self, connection: WebSocketConnection, action: str, resource: str
    ) -> bool:
        """
        Authorize action on resource.

        Args:
            connection: WebSocket connection
            action: Action to authorize (e.g., 'read', 'write', 'admin')
            resource: Resource identifier

        Returns:
            bool: True if authorized, False otherwise
        """
        if not connection.info.authenticated:
            return False

        # Check authorization handler
        handler = self.authz_handlers.get(resource)
        if handler:
            try:
                return await handler(connection, action, resource)
            except Exception as e:
                logger.error(f"Error in authorization handler: {e}", exc_info=True)
                return False

        # Default: allow if authenticated
        return True

    def check_message_limits(self, connection: WebSocketConnection, message_size: int) -> bool:
        """
        Check message size and rate limits.

        Args:
            connection: WebSocket connection
            message_size: Size of message in bytes

        Returns:
            bool: True if within limits, False otherwise
        """
        # Message size limit
        if message_size > self.config.max_message_size:
            logger.warning(f"Message too large: {message_size} bytes")
            return False

        # Rate limiting
        if self.config.enable_rate_limiting:
            client_id = f"{connection.info.remote_addr}:{connection.info.id}"

            # Check message rate
            if not self.rate_limiter.check_message_rate(
                client_id, self.config.max_messages_per_minute
            ):
                logger.warning(f"Message rate limit exceeded for {client_id}")
                return False

            # Check burst rate
            if not self.rate_limiter.check_burst_limit(client_id):
                logger.warning(f"Burst rate limit exceeded for {client_id}")
                return False

            # Record message
            self.rate_limiter.record_message(client_id)
            self.rate_limiter.record_burst(client_id)

        return True

    def _check_ip_filtering(self, connection: WebSocketConnection) -> bool:
        """Check IP filtering rules."""
        client_ip = connection.info.remote_addr.split(":")[0]

        # Check blocked IPs
        if client_ip in self.config.blocked_ips:
            logger.warning(f"Blocked IP attempted connection: {client_ip}")
            return False

        # Check allowed IPs (if set)
        if self.config.allowed_ips and client_ip not in self.config.allowed_ips:
            logger.warning(f"Non-allowed IP attempted connection: {client_ip}")
            return False

        return True

    def _check_origin(self, connection: WebSocketConnection) -> bool:
        """Check origin validation."""
        if not self.config.require_origin and not self.config.allowed_origins:
            return True

        origin = connection.info.headers.get("origin")

        # Require origin if configured
        if self.config.require_origin and not origin:
            logger.warning("Origin required but not provided")
            return False

        # Check allowed origins
        if self.config.allowed_origins and origin:
            if origin not in self.config.allowed_origins:
                logger.warning(f"Origin not allowed: {origin}")
                return False

        return True

    def _check_user_agent(self, connection: WebSocketConnection) -> bool:
        """Check user agent validation."""
        if not self.config.check_user_agent:
            return True

        user_agent = connection.info.user_agent.lower()

        # Check blocked user agents
        for blocked in self.config.blocked_user_agents:
            if blocked.lower() in user_agent:
                logger.warning(f"Blocked user agent: {user_agent}")
                return False

        return True

    def _check_connection_limits(self, connection: WebSocketConnection) -> bool:
        """Check connection limits."""
        if not self.config.enable_rate_limiting:
            return True

        client_ip = connection.info.remote_addr.split(":")[0]

        # Check connection limit
        if not self.rate_limiter.check_connection_limit(
            client_ip, self.config.max_connections_per_ip
        ):
            logger.warning(f"Connection limit exceeded for IP: {client_ip}")
            return False

        # Register connection
        self.rate_limiter.add_connection(client_ip)

        return True

    def _check_csrf_protection(self, connection: WebSocketConnection) -> bool:
        """Check CSRF protection."""
        if not self.config.enable_csrf_protection:
            return True

        # Simple CSRF token validation
        csrf_token = connection.info.headers.get(self.config.csrf_token_header)
        if not csrf_token:
            logger.warning("CSRF token required but not provided")
            return False

        # Validate CSRF token (implement your validation logic)
        # This is a basic example - implement proper validation for production
        if len(csrf_token) < 32:
            logger.warning("Invalid CSRF token")
            return False

        return True

    def cleanup_connection(self, connection: WebSocketConnection):
        """Clean up security data for connection."""
        client_ip = connection.info.remote_addr.split(":")[0]
        self.rate_limiter.remove_connection(client_ip)


# Security middleware
def security_middleware(security: WebSocketSecurity):
    """Create security middleware."""

    async def middleware(connection: WebSocketConnection, handler: Callable):
        # Validate connection
        if not await security.validate_connection(connection):
            return

        # Set up cleanup on disconnect
        original_on_disconnect = connection.on_disconnect

        async def cleanup_on_disconnect(conn):
            security.cleanup_connection(conn)
            if original_on_disconnect:
                await original_on_disconnect(conn)

        connection.on_disconnect = cleanup_on_disconnect

        # Proceed with handler
        return await handler()

    return middleware


def authentication_middleware(security: WebSocketSecurity, auth_timeout: float = 30.0):
    """Create authentication middleware."""

    async def middleware(connection: WebSocketConnection, handler: Callable):
        if not security.config.require_auth:
            return await handler()

        # Wait for authentication
        auth_task = asyncio.create_task(_wait_for_auth(connection, security, auth_timeout))

        try:
            authenticated = await auth_task
            if not authenticated:
                await connection.close(CloseCode.POLICY_VIOLATION, "Authentication required")
                return

            return await handler()

        except asyncio.TimeoutError:
            await connection.close(CloseCode.POLICY_VIOLATION, "Authentication timeout")
            return

    return middleware


async def _wait_for_auth(
    connection: WebSocketConnection, security: WebSocketSecurity, timeout: float
) -> bool:
    """Wait for authentication message."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        if connection.info.authenticated:
            return True

        await asyncio.sleep(0.1)

    return False


# Export main components
__all__ = [
    "SecurityConfig",
    "TokenValidator",
    "RateLimiter",
    "WebSocketSecurity",
    "SecurityError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "security_middleware",
    "authentication_middleware",
]
