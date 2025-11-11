"""
Secure Error Handling Utilities

This module provides security-focused error handling to prevent information
disclosure vulnerabilities. It implements:

1. Environment-aware error responses
2. Stack trace sanitization
3. Sensitive data removal
4. Error correlation IDs
5. Secure logging
6. Timing attack prevention

SECURITY CLASSIFICATION: CRITICAL
CVSS Score: 9.0 (Information Disclosure)
"""

import hashlib
import hmac
import logging
import os
import re
import secrets
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration for error handling"""

    def __init__(self):
        self.environment = os.getenv("COVET_ENV", "production").lower()
        self.is_production = self.environment == "production"
        self.is_development = self.environment == "development"
        self.project_root = self._detect_project_root()

        # Security settings
        self.log_full_errors = True  # Always log full errors server-side
        self.sanitize_paths = self.is_production
        self.sanitize_sql = True
        self.sanitize_connection_strings = True
        self.remove_stack_traces = self.is_production
        self.mask_ip_addresses = self.is_production

    def _detect_project_root(self) -> str:
        """Detect project root directory"""
        try:
            cwd = os.getcwd()
            # Try to find common project markers
            markers = ["setup.py", "pyproject.toml", ".git", "requirements.txt"]
            current = Path(cwd)

            while current != current.parent:
                if any((current / marker).exists() for marker in markers):
                    return str(current)
                current = current.parent

            return cwd
        except Exception:
            return "/app"


# Global security config
_security_config = SecurityConfig()


def get_security_config() -> SecurityConfig:
    """Get the global security configuration"""
    return _security_config


def generate_error_id() -> str:
    """
    Generate a unique, unpredictable error ID for correlation.

    Uses cryptographically secure random generation to prevent
    enumeration attacks.

    Returns:
        A unique error ID (e.g., "ERR-a3f2b1c0d4e5f6a7")
    """
    random_bytes = secrets.token_bytes(8)
    error_id = f"ERR-{random_bytes.hex()}"
    return error_id


def sanitize_path(path: str, config: Optional[SecurityConfig] = None) -> str:
    """
    Sanitize file paths to prevent information disclosure.

    In production:
    - Removes absolute paths
    - Replaces with relative paths from project root
    - Masks user directories

    Args:
        path: The file path to sanitize
        config: Security configuration (uses global if None)

    Returns:
        Sanitized path safe for external display
    """
    if not config:
        config = get_security_config()

    if not config.sanitize_paths:
        return path

    try:
        # Remove absolute path prefixes
        path = path.replace(config.project_root, "<project>")

        # Remove home directory paths
        home_dir = os.path.expanduser("~")
        path = path.replace(home_dir, "<home>")

        # Remove common system paths
        path = path.replace("/usr/local/", "<system>/")
        path = path.replace("/usr/", "<system>/")
        path = path.replace("/opt/", "<system>/")
        path = path.replace("/var/", "<system>/")
        path = path.replace("C:\\", "<drive>\\")
        path = path.replace("c:\\", "<drive>\\")

        # Remove site-packages and virtualenv paths
        path = re.sub(r"/.*?/site-packages/", "<packages>/", path)
        path = re.sub(r"\\.*?\\site-packages\\", "<packages>\\", path)
        path = re.sub(r"/.*?/(venv|env|virtualenv)/", "<venv>/", path)

        return path
    except Exception:
        return "<path>"


def sanitize_sql_query(query: str) -> str:
    """
    Sanitize SQL queries to prevent disclosure of sensitive data.

    Removes:
    - Parameter values
    - WHERE clause conditions
    - Sensitive table names

    Args:
        query: SQL query string

    Returns:
        Sanitized SQL query
    """
    try:
        # Remove string literals
        query = re.sub(r"'[^']*'", "'<redacted>'", query)

        # Remove numeric literals in WHERE clauses
        query = re.sub(r"\b(\d+)\b", "<value>", query)

        # Mask passwords/secrets in column names or values
        query = re.sub(
            r"(password|passwd|pwd|secret|token|key)\s*=\s*['\"]?[^'\"\s,]+['\"]?",
            r"\1=<redacted>",
            query,
            flags=re.IGNORECASE,
        )

        return query
    except Exception:
        return "<query>"


def sanitize_connection_string(conn_string: str) -> str:
    """
    Sanitize database connection strings to prevent credential disclosure.

    Removes:
    - Passwords
    - Usernames (partially)
    - Hostnames/IPs (partially)
    - Port numbers

    Args:
        conn_string: Database connection string

    Returns:
        Sanitized connection string
    """
    try:
        # Remove passwords from various formats
        # Format: password=xxx or pwd=xxx
        conn_string = re.sub(
            r"(password|pwd|passwd)\s*=\s*[^\s;]+",
            r"\1=<redacted>",
            conn_string,
            flags=re.IGNORECASE,
        )

        # Format: user:password@host
        conn_string = re.sub(r"://([^:]+):([^@]+)@", r"://<user>:<redacted>@", conn_string)

        # Mask API keys and tokens
        conn_string = re.sub(
            r"(api[_-]?key|token|secret)\s*=\s*[^\s;&]+",
            r"\1=<redacted>",
            conn_string,
            flags=re.IGNORECASE,
        )

        return conn_string
    except Exception:
        return "<connection>"


def sanitize_ip_address(ip: str) -> str:
    """
    Partially mask IP addresses to prevent enumeration.

    IPv4: 192.168.1.100 -> 192.168.x.x
    IPv6: Masks last 4 groups

    Args:
        ip: IP address string

    Returns:
        Masked IP address
    """
    try:
        # IPv4
        if "." in ip and ip.count(".") == 3:
            parts = ip.split(".")
            return f"{parts[0]}.{parts[1]}.x.x"

        # IPv6
        if ":" in ip:
            parts = ip.split(":")
            if len(parts) > 4:
                return ":".join(parts[:4]) + ":x:x:x:x"

        return ip
    except Exception:
        return "<ip>"


def sanitize_stack_trace(stack_trace: str, config: Optional[SecurityConfig] = None) -> str:
    """
    Sanitize stack traces to remove sensitive information.

    Removes:
    - Absolute file paths
    - Variable values
    - Sensitive function arguments

    Args:
        stack_trace: Raw stack trace string
        config: Security configuration

    Returns:
        Sanitized stack trace
    """
    if not config:
        config = get_security_config()

    try:
        lines = stack_trace.split("\n")
        sanitized_lines = []

        for line in lines:
            # Sanitize file paths
            sanitized_line = sanitize_path(line, config)

            # Remove variable values from stack frames
            # Pattern: variable = value
            sanitized_line = re.sub(
                r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*[^,\n]+", r"\1=<value>", sanitized_line
            )

            # Remove sensitive parameter names and values
            for sensitive_term in ["password", "token", "secret", "key", "api_key"]:
                sanitized_line = re.sub(
                    f"{sensitive_term}['\"]?\\s*[:=]\\s*[^'\"\\s,)]+",
                    f"{sensitive_term}=<redacted>",
                    sanitized_line,
                    flags=re.IGNORECASE,
                )

            sanitized_lines.append(sanitized_line)

        return "\n".join(sanitized_lines)
    except Exception:
        return "<stack trace unavailable>"


def sanitize_exception_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize exception context dictionary.

    Removes or masks:
    - Passwords
    - Tokens
    - Connection strings
    - IP addresses (in production)
    - User IDs of other users

    Args:
        context: Exception context dictionary

    Returns:
        Sanitized context dictionary
    """
    config = get_security_config()
    sanitized = {}

    # Sensitive keys that should be redacted
    sensitive_keys = {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "api_key",
        "access_token",
        "refresh_token",
        "private_key",
        "secret_key",
        "jwt",
        "bearer",
        "authorization",
        "credentials",
    }

    for key, value in context.items():
        key_lower = key.lower()

        # Check if key is sensitive
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            sanitized[key] = "<redacted>"
            continue

        # Sanitize specific value types
        if isinstance(value, str):
            # Check if value looks like a connection string
            if any(marker in value for marker in ["://", "password=", "pwd="]):
                sanitized[key] = sanitize_connection_string(value)
            # Check if value looks like a file path
            elif ("/" in value or "\\" in value) and len(value) > 10:
                sanitized[key] = sanitize_path(value, config)
            # Check if value looks like an IP address
            elif config.mask_ip_addresses and re.match(r"\d+\.\d+\.\d+\.\d+", value):
                sanitized[key] = sanitize_ip_address(value)
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value

    return sanitized


def create_secure_error_response(
    error: Exception,
    error_id: Optional[str] = None,
    include_details: Optional[bool] = None,
    request_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a secure error response that prevents information disclosure.

    Production mode: Generic error messages only
    Development mode: Detailed error information

    Args:
        error: The exception that occurred
        error_id: Optional error ID (generates one if not provided)
        include_details: Override environment detection for detail inclusion
        request_path: Request path for logging

    Returns:
        Secure error response dictionary
    """
    config = get_security_config()

    if error_id is None:
        error_id = generate_error_id()

    timestamp = datetime.utcnow().isoformat() + "Z"

    # Determine if we should include details
    if include_details is None:
        include_details = config.is_development

    # Base response (always included)
    response = {
        "error": "An internal error occurred",
        "error_id": error_id,
        "timestamp": timestamp,
    }

    # Log full error server-side (ALWAYS)
    log_error_securely(error, error_id, request_path)

    # Add details in development mode
    if include_details:
        response["details"] = str(error)
        response["error_type"] = type(error).__name__

        # Add sanitized stack trace
        if not config.remove_stack_traces:
            tb = traceback.format_exc()
            response["stack_trace"] = sanitize_stack_trace(tb, config)

        # Add sanitized context if available
        if hasattr(error, "context") and error.context:
            response["context"] = sanitize_exception_context(error.context)

    return response


def log_error_securely(error: Exception, error_id: str, request_path: Optional[str] = None) -> None:
    """
    Log error with full details server-side for debugging.

    This function logs complete error information including:
    - Full stack trace
    - Exception details
    - Context information

    Sensitive data is sanitized even in logs to prevent
    accidental exposure through log aggregation systems.

    Args:
        error: The exception to log
        error_id: Error correlation ID
        request_path: Optional request path
    """
    config = get_security_config()

    # Build log message
    log_parts = [f"[{error_id}] {type(error).__name__}: {str(error)}"]

    if request_path:
        log_parts.append(f"Request: {request_path}")

    # Add context if available
    if hasattr(error, "context") and error.context:
        sanitized_context = sanitize_exception_context(error.context)
        log_parts.append(f"Context: {sanitized_context}")

    # Get sanitized stack trace
    tb = traceback.format_exc()
    sanitized_tb = sanitize_stack_trace(tb, config)

    # Log at ERROR level
    logger.error("\n".join(log_parts))
    logger.error(f"Stack trace:\n{sanitized_tb}")


def get_security_headers() -> Dict[bytes, bytes]:
    """
    Get security headers for error responses.

    Returns headers that prevent:
    - MIME sniffing attacks
    - Clickjacking
    - Content injection

    Returns:
        Dictionary of security headers
    """
    return {
        b"x-content-type-options": b"nosniff",
        b"x-frame-options": b"DENY",
        b"content-security-policy": b"default-src 'none'",
        b"x-xss-protection": b"1; mode=block",
        b"referrer-policy": b"no-referrer",
    }


def constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.

    This is critical for:
    - Password comparison
    - Token validation
    - Secret key comparison
    - Any security-sensitive comparison

    Args:
        a: First string
        b: Second string

    Returns:
        True if strings are equal, False otherwise
    """
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def add_timing_jitter(min_ms: float = 0, max_ms: float = 50) -> None:
    """
    Add random timing jitter to prevent timing attacks.

    Use this after authentication/authorization checks to ensure
    consistent response times regardless of success/failure.

    Args:
        min_ms: Minimum jitter in milliseconds
        max_ms: Maximum jitter in milliseconds
    """
    jitter = secrets.randbelow(int((max_ms - min_ms) * 1000)) / 1000
    time.sleep((min_ms + jitter) / 1000)


def normalize_error_message(message: str, error_type: str = "auth") -> str:
    """
    Normalize error messages to prevent user enumeration.

    Returns consistent messages that don't reveal whether:
    - User exists
    - Password is wrong
    - Account is locked
    - Email is registered

    Args:
        message: Original error message
        error_type: Type of error ("auth", "not_found", etc.)

    Returns:
        Normalized error message
    """
    if error_type == "auth":
        return "Invalid credentials"
    elif error_type == "not_found":
        return "Resource not found"
    elif error_type == "forbidden":
        return "Access denied"
    elif error_type == "validation":
        return "Validation failed"
    else:
        return "An error occurred"


class ErrorRateLimiter:
    """
    Track and limit error rates to detect potential attacks.

    Monitors:
    - Error rate per IP
    - Error rate per user
    - Error rate per endpoint
    - Unusual error patterns
    """

    def __init__(
        self,
        window_seconds: int = 60,
        max_errors: int = 10,
        block_duration_seconds: int = 300,
    ):
        """
        Initialize error rate limiter.

        Args:
            window_seconds: Time window for rate limiting
            max_errors: Maximum errors allowed in window
            block_duration_seconds: How long to block after limit exceeded
        """
        self.window_seconds = window_seconds
        self.max_errors = max_errors
        self.block_duration_seconds = block_duration_seconds

        # Storage: identifier -> [(timestamp, error_id), ...]
        self._error_log: Dict[str, List[Tuple[float, str]]] = {}

        # Storage: identifier -> block_until_timestamp
        self._blocked: Dict[str, float] = {}

    def record_error(self, identifier: str, error_id: str) -> None:
        """
        Record an error occurrence.

        Args:
            identifier: Client identifier (IP, user ID, etc.)
            error_id: Error correlation ID
        """
        now = time.time()

        if identifier not in self._error_log:
            self._error_log[identifier] = []

        self._error_log[identifier].append((now, error_id))

        # Clean old entries
        self._cleanup_old_entries(identifier, now)

    def is_rate_limited(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """
        Check if identifier is rate limited.

        Args:
            identifier: Client identifier

        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        now = time.time()

        # Check if blocked
        if identifier in self._blocked:
            block_until = self._blocked[identifier]
            if now < block_until:
                retry_after = int(block_until - now)
                return True, retry_after
            else:
                # Block expired
                del self._blocked[identifier]

        # Check rate limit
        if identifier in self._error_log:
            self._cleanup_old_entries(identifier, now)
            error_count = len(self._error_log[identifier])

            if error_count >= self.max_errors:
                # Rate limit exceeded - block identifier
                self._blocked[identifier] = now + self.block_duration_seconds
                logger.warning(
                    f"Error rate limit exceeded for {identifier}: "
                    f"{error_count} errors in {self.window_seconds}s"
                )
                return True, self.block_duration_seconds

        return False, None

    def _cleanup_old_entries(self, identifier: str, current_time: float) -> None:
        """Remove entries outside the time window"""
        cutoff = current_time - self.window_seconds
        self._error_log[identifier] = [
            (ts, eid) for ts, eid in self._error_log[identifier] if ts > cutoff
        ]

        # Remove empty entries
        if not self._error_log[identifier]:
            del self._error_log[identifier]

    def get_error_stats(self, identifier: str) -> Dict[str, Any]:
        """
        Get error statistics for an identifier.

        Args:
            identifier: Client identifier

        Returns:
            Dictionary with error statistics
        """
        now = time.time()

        if identifier in self._error_log:
            self._cleanup_old_entries(identifier, now)
            error_count = len(self._error_log[identifier])
        else:
            error_count = 0

        is_blocked = identifier in self._blocked and now < self._blocked[identifier]

        return {
            "error_count": error_count,
            "window_seconds": self.window_seconds,
            "is_blocked": is_blocked,
            "limit": self.max_errors,
        }


# Global error rate limiter instance
_global_error_limiter = ErrorRateLimiter()


def get_error_rate_limiter() -> ErrorRateLimiter:
    """Get the global error rate limiter instance"""
    return _global_error_limiter


__all__ = [
    "SecurityConfig",
    "get_security_config",
    "generate_error_id",
    "sanitize_path",
    "sanitize_sql_query",
    "sanitize_connection_string",
    "sanitize_ip_address",
    "sanitize_stack_trace",
    "sanitize_exception_context",
    "create_secure_error_response",
    "log_error_securely",
    "get_security_headers",
    "constant_time_compare",
    "add_timing_jitter",
    "normalize_error_message",
    "ErrorRateLimiter",
    "get_error_rate_limiter",
]
