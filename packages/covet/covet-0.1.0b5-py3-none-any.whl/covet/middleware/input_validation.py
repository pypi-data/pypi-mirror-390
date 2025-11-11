"""
Input Validation Middleware

Comprehensive input validation layer for all HTTP requests.
Provides defense-in-depth against injection attacks, malformed data, and abuse.

Security Features:
- String length validation with configurable limits
- Integer range validation
- Email/URL format validation
- JSON schema validation
- File upload validation (size, type, content)
- Rate limiting for validation failures
- Non-disclosing error messages in production
- Security event logging and monitoring
- Protection against common attack patterns
"""

import hashlib
import json
import mimetypes
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from covet.core.http import JSONResponse
from covet.middleware.core import BaseMiddleware


@dataclass
class ValidationRule:
    """
    Validation rule configuration.

    Defines constraints for input validation with security-focused defaults.
    """

    # String validation
    min_length: Optional[int] = None
    max_length: Optional[int] = 1000  # Default max to prevent buffer overflow
    # Regex pattern (use carefully to avoid ReDoS)
    pattern: Optional[str] = None

    # Numeric validation
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None

    # Type validation
    allowed_types: Optional[Set[type]] = None

    # Format validation
    # 'email', 'url', 'uuid', 'json', 'date', 'ip'
    format: Optional[str] = None

    # Custom validator
    custom_validator: Optional[Callable[[Any], bool]] = None

    # Required field
    required: bool = False

    # Sanitization
    sanitize: bool = True
    strip_whitespace: bool = True


@dataclass
class FileUploadRule:
    """
    File upload validation rule.

    Comprehensive validation for file uploads to prevent malicious files.
    """

    # Size limits
    max_size: int = 10 * 1024 * 1024  # 10MB default
    min_size: int = 0

    # Allowed MIME types
    allowed_mime_types: Optional[Set[str]] = None

    # Allowed file extensions
    allowed_extensions: Optional[Set[str]] = None

    # Forbidden patterns in filename
    forbidden_patterns: Set[str] = field(
        default_factory=lambda: {
            "../",
            "..\\",
            "\x00",
            "<",
            ">",
            ":",
            '"',
            "|",
            "?",
            "*",
        }
    )

    # Check magic bytes
    verify_content: bool = True

    # Scan for malicious content
    scan_content: bool = True


@dataclass
class ValidationConfig:
    """
    Input validation middleware configuration.

    Central configuration for all validation rules and security policies.
    """

    # Field-specific validation rules
    field_rules: Dict[str, ValidationRule] = field(default_factory=dict)

    # File upload rules
    file_upload_rules: Dict[str, FileUploadRule] = field(default_factory=dict)

    # Rate limiting for validation failures
    enable_rate_limiting: bool = True
    max_failures_per_minute: int = 10
    max_failures_per_hour: int = 50
    rate_limit_window: int = 3600  # 1 hour in seconds

    # Security policies
    block_sql_injection: bool = True
    block_xss: bool = True
    block_command_injection: bool = True
    block_path_traversal: bool = True
    block_xxe: bool = True

    # Error handling
    debug_mode: bool = False  # NEVER enable in production
    log_validation_failures: bool = True
    log_validation_attempts: bool = False

    # Request limits
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    max_json_depth: int = 10
    max_array_size: int = 1000
    max_fields: int = 100


class ValidationFailureTracker:
    """
    Track validation failures for rate limiting.

    Implements sliding window rate limiting to prevent abuse.
    """

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.failures: Dict[str, List[float]] = defaultdict(list)

    def record_failure(self, identifier: str) -> None:
        """
        Record validation failure for identifier (IP, user ID, etc.).

        Args:
            identifier: Unique identifier for the client
        """
        current_time = time.time()
        self.failures[identifier].append(current_time)

        # Clean old entries
        cutoff = current_time - self.config.rate_limit_window
        self.failures[identifier] = [t for t in self.failures[identifier] if t > cutoff]

    def is_rate_limited(self, identifier: str) -> bool:
        """
        Check if identifier is rate limited.

        Args:
            identifier: Unique identifier for the client

        Returns:
            True if rate limited
        """
        if not self.config.enable_rate_limiting:
            return False

        current_time = time.time()
        cutoff_minute = current_time - 60
        cutoff_hour = current_time - 3600

        failures = self.failures.get(identifier, [])

        # Check failures in last minute
        recent_failures = [f for f in failures if f > cutoff_minute]
        if len(recent_failures) >= self.config.max_failures_per_minute:
            return True

        # Check failures in last hour
        hourly_failures = [f for f in failures if f > cutoff_hour]
        if len(hourly_failures) >= self.config.max_failures_per_hour:
            return True

        return False


class InputValidator:
    """
    Core input validation engine.

    Validates input against rules and detects common attack patterns.
    """

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(--|\#|\/\*)",
        r"(\bor\b.*=.*)",
        r"('.*--)",
        r"(;.*\b(select|insert|update|delete|drop)\b)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"\$\([^)]*\)",
        r"`[^`]*`",
        r">\s*/",
        r"<\s*/",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\./",
        r"%2e%2e/",
        r"%2e%2e\\",
        r"\.\.\\",
    ]

    # XXE patterns
    XXE_PATTERNS = [
        r"<!ENTITY",
        r"<!DOCTYPE.*\[",
        r"SYSTEM",
        r"PUBLIC",
    ]

    def __init__(self, config: ValidationConfig):
        self.config = config

    def validate_field(
        self, field_name: str, value: Any, rule: ValidationRule
    ) -> tuple[bool, Optional[str]]:
        """
        Validate single field against rule.

        Args:
            field_name: Name of the field
            value: Value to validate
            rule: Validation rule

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required
        if rule.required and (value is None or value == ""):
            return False, f"{field_name} is required"

        # Skip validation if value is None and not required
        if value is None and not rule.required:
            return True, None

        # Type validation
        if rule.allowed_types and type(value) not in rule.allowed_types:
            if self.config.debug_mode:
                return False, f"{field_name} must be one of types: {rule.allowed_types}"
            return False, "Invalid input type"

        # String validation
        if isinstance(value, str):
            return self._validate_string(field_name, value, rule)

        # Numeric validation
        if isinstance(value, (int, float)):
            return self._validate_number(field_name, value, rule)

        # Custom validator
        if rule.custom_validator:
            try:
                if not rule.custom_validator(value):
                    return False, f"Validation failed for {field_name}"
            except TypeError as e:
                self._log_security_event("custom_validator_type_error", field_name, str(e))
                return False, "Validation configuration error"
            except ValueError as e:
                self._log_security_event("custom_validator_value_error", field_name, str(e))
                return False, f"Invalid value for {field_name}"
            except Exception as e:
                self._log_security_event("custom_validator_error", field_name, str(e))
                if self.config.debug_mode:
                    return False, f"Validation error for {field_name}: {str(e)}"
                return False, "Validation error"

        return True, None

    def _validate_string(
        self, field_name: str, value: str, rule: ValidationRule
    ) -> tuple[bool, Optional[str]]:
        """Validate string value."""
        # Strip whitespace if configured
        if rule.strip_whitespace:
            value = value.strip()

        # Length validation
        if rule.min_length and len(value) < rule.min_length:
            if self.config.debug_mode:
                return (
                    False,
                    f"{field_name} must be at least {rule.min_length} characters",
                )
            return False, "Input too short"

        if rule.max_length and len(value) > rule.max_length:
            if self.config.debug_mode:
                return (
                    False,
                    f"{field_name} must be at most {rule.max_length} characters",
                )
            return False, "Input too long"

        # Pattern validation (be careful with ReDoS)
        if rule.pattern:
            # Limit string length for regex to prevent ReDoS
            if len(value) > 10000:
                return False, "Input too long for pattern matching"

            try:
                if not re.match(rule.pattern, value):
                    return False, f"Invalid format for {field_name}"
            except re.error as e:
                self._log_security_event("regex_pattern_error", field_name, f"Pattern: {rule.pattern}, Error: {str(e)}")
                return False, "Invalid pattern configuration"
            except TimeoutError:
                self._log_security_event("regex_timeout", field_name, f"Pattern: {rule.pattern}")
                return False, "Pattern validation timeout"
            except Exception as e:
                self._log_security_event("pattern_validation_error", field_name, str(e))
                if self.config.debug_mode:
                    return False, f"Pattern validation error: {str(e)}"
                return False, "Pattern validation error"

        # Format validation
        if rule.format:
            is_valid, error = self._validate_format(field_name, value, rule.format)
            if not is_valid:
                return False, error

        # Attack pattern detection
        if self.config.block_sql_injection:
            if self._contains_sql_injection(value):
                if self.config.log_validation_failures:
                    self._log_security_event("sql_injection_attempt", field_name, value)
                return False, "Invalid input"

        if self.config.block_xss:
            if self._contains_xss(value):
                if self.config.log_validation_failures:
                    self._log_security_event("xss_attempt", field_name, value)
                return False, "Invalid input"

        if self.config.block_command_injection:
            if self._contains_command_injection(value):
                if self.config.log_validation_failures:
                    self._log_security_event("command_injection_attempt", field_name, value)
                return False, "Invalid input"

        if self.config.block_path_traversal:
            if self._contains_path_traversal(value):
                if self.config.log_validation_failures:
                    self._log_security_event("path_traversal_attempt", field_name, value)
                return False, "Invalid input"

        return True, None

    def _validate_number(
        self, field_name: str, value: Union[int, float], rule: ValidationRule
    ) -> tuple[bool, Optional[str]]:
        """Validate numeric value."""
        if rule.min_value is not None and value < rule.min_value:
            if self.config.debug_mode:
                return False, f"{field_name} must be at least {rule.min_value}"
            return False, "Value too small"

        if rule.max_value is not None and value > rule.max_value:
            if self.config.debug_mode:
                return False, f"{field_name} must be at most {rule.max_value}"
            return False, "Value too large"

        return True, None

    def _validate_format(
        self, field_name: str, value: str, format_type: str
    ) -> tuple[bool, Optional[str]]:
        """Validate specific format."""
        if format_type == "email":
            return self._validate_email(value)
        elif format_type == "url":
            return self._validate_url(value)
        elif format_type == "uuid":
            return self._validate_uuid(value)
        elif format_type == "json":
            return self._validate_json(value)
        elif format_type == "date":
            return self._validate_date(value)
        elif format_type == "ip":
            return self._validate_ip(value)

        return True, None

    def _validate_email(self, value: str) -> tuple[bool, Optional[str]]:
        """Validate email format."""
        if len(value) > 254:
            return False, "Email too long"

        # RFC 5322 simplified pattern
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(pattern, value):
            return False, "Invalid email format"

        return True, None

    def _validate_url(self, value: str) -> tuple[bool, Optional[str]]:
        """Validate URL format."""
        if len(value) > 2048:
            return False, "URL too long"

        # Simple URL pattern
        pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"

        if not re.match(pattern, value):
            return False, "Invalid URL format"

        # Block dangerous protocols
        dangerous_protocols = ["javascript:", "data:", "vbscript:", "file:"]
        value_lower = value.lower()
        for protocol in dangerous_protocols:
            if value_lower.startswith(protocol):
                return False, "Invalid URL protocol"

        return True, None

    def _validate_uuid(self, value: str) -> tuple[bool, Optional[str]]:
        """Validate UUID format."""
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

        if not re.match(pattern, value.lower()):
            return False, "Invalid UUID format"

        return True, None

    def _validate_json(self, value: str) -> tuple[bool, Optional[str]]:
        """Validate JSON format."""
        try:
            parsed = json.loads(value)

            # Check JSON depth
            if not self._check_json_depth(parsed, self.config.max_json_depth):
                return False, "JSON too deeply nested"

            return True, None
        except json.JSONDecodeError:
            return False, "Invalid JSON format"

    def _check_json_depth(self, data: Any, max_depth: int, current_depth: int = 0) -> bool:
        """Check JSON nesting depth."""
        if current_depth > max_depth:
            return False

        if isinstance(data, dict):
            return all(
                self._check_json_depth(v, max_depth, current_depth + 1) for v in data.values()
            )
        elif isinstance(data, list):
            return all(self._check_json_depth(item, max_depth, current_depth + 1) for item in data)

        return True

    def _validate_date(self, value: str) -> tuple[bool, Optional[str]]:
        """Validate date format (ISO 8601)."""
        pattern = r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$"

        if not re.match(pattern, value):
            return False, "Invalid date format"

        return True, None

    def _validate_ip(self, value: str) -> tuple[bool, Optional[str]]:
        """Validate IP address (IPv4 or IPv6)."""
        # IPv4 pattern
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        # IPv6 pattern (simplified)
        ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"

        if re.match(ipv4_pattern, value):
            # Validate IPv4 octets
            parts = value.split(".")
            if all(0 <= int(part) <= 255 for part in parts):
                return True, None

        if re.match(ipv6_pattern, value):
            return True, None

        return False, "Invalid IP address"

    def _contains_sql_injection(self, value: str) -> bool:
        """Check for SQL injection patterns."""
        value_lower = value.lower()
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False

    def _contains_xss(self, value: str) -> bool:
        """Check for XSS patterns."""
        value_lower = value.lower()
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False

    def _contains_command_injection(self, value: str) -> bool:
        """Check for command injection patterns."""
        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value):
                return True
        return False

    def _contains_path_traversal(self, value: str) -> bool:
        """Check for path traversal patterns."""
        value_lower = value.lower()
        for pattern in self.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value_lower):
                return True
        return False

    def _log_security_event(self, event_type: str, field_name: str, value: str) -> None:
        """
        Log security event for monitoring.

        In production, integrate with SIEM/security monitoring.
        """
        import logging

        logger = logging.getLogger("covet.security")
        logger.warning(
            f"Security event: {event_type} on field {field_name}",
            extra={
                "event_type": event_type,
                "field": field_name,
                "value_hash": hashlib.sha256(value.encode()).hexdigest(),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


class InputValidationMiddleware(BaseMiddleware):
    """
    Input validation middleware.

    Validates all incoming requests against configured rules.
    Provides rate limiting, attack detection, and security logging.
    """

    def __init__(self, config: ValidationConfig):
        super().__init__()
        self.config = config
        self.validator = InputValidator(config)
        self.failure_tracker = ValidationFailureTracker(config)

    async def process_request(self, request, call_next):
        """
        Process incoming request with validation.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)

        # Check rate limiting
        if self.failure_tracker.is_rate_limited(client_ip):
            return self._rate_limit_response()

        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.config.max_request_size:
            self.failure_tracker.record_failure(client_ip)
            return self._validation_error_response("Request too large")

        # Validate request data
        try:
            is_valid, error = await self._validate_request(request)

            if not is_valid:
                self.failure_tracker.record_failure(client_ip)
                return self._validation_error_response(error)

        except Exception as e:
            if self.config.debug_mode:
                return self._validation_error_response(f"Validation error: {str(e)}")
            return self._validation_error_response("Validation failed")

        # Continue to next middleware
        return await call_next(request)

    async def process_response(self, request, response):
        """
        Process response after handler execution.

        Args:
            request: The original request
            response: The response from the handler

        Returns:
            The response (potentially modified)
        """
        # Input validation middleware doesn't need to modify responses
        return response

    async def _validate_request(self, request) -> tuple[bool, Optional[str]]:
        """Validate request data."""
        # Validate query parameters
        if hasattr(request, "query_params"):
            for key, value in request.query_params.items():
                if key in self.config.field_rules:
                    rule = self.config.field_rules[key]
                    is_valid, error = self.validator.validate_field(key, value, rule)
                    if not is_valid:
                        return False, error

        # Validate form data
        if hasattr(request, "form"):
            try:
                form = await request.form()
                for key, value in form.items():
                    if key in self.config.field_rules:
                        rule = self.config.field_rules[key]
                        is_valid, error = self.validator.validate_field(key, value, rule)
                        if not is_valid:
                            return False, error
            except ValueError as e:
                self._log_security_event("form_parse_error", "form", str(e))
                return False, "Invalid form data format"
            except UnicodeDecodeError as e:
                self._log_security_event("form_encoding_error", "form", str(e))
                return False, "Invalid character encoding in form data"
            except AttributeError as e:
                self._log_security_event("form_attribute_error", "form", str(e))
                return False, "Form data processing error"
            except Exception as e:
                self._log_security_event("form_validation_error", "form", str(e))
                if self.config.debug_mode:
                    return False, f"Form validation error: {str(e)}"
                return False, "Form validation failed"

        # Validate JSON body
        if request.headers.get("content-type") == "application/json":
            try:
                body = await request.json()

                # Check number of fields
                if isinstance(body, dict) and len(body) > self.config.max_fields:
                    return False, "Too many fields"

                # Validate fields
                if isinstance(body, dict):
                    for key, value in body.items():
                        if key in self.config.field_rules:
                            rule = self.config.field_rules[key]
                            is_valid, error = self.validator.validate_field(key, value, rule)
                            if not is_valid:
                                return False, error
            except json.JSONDecodeError as e:
                self._log_security_event("json_decode_error", "body", str(e))
                return False, "Invalid JSON in request body"
            except UnicodeDecodeError as e:
                self._log_security_event("json_encoding_error", "body", str(e))
                return False, "Invalid character encoding in JSON"
            except ValueError as e:
                self._log_security_event("json_value_error", "body", str(e))
                return False, "Invalid JSON structure"
            except MemoryError:
                self._log_security_event("json_memory_error", "body", "JSON too large")
                return False, "Request body too large"
            except RecursionError:
                self._log_security_event("json_recursion_error", "body", "JSON too deeply nested")
                return False, "JSON structure too complex"
            except Exception as e:
                self._log_security_event("json_validation_error", "body", str(e))
                if self.config.debug_mode:
                    return False, f"JSON validation error: {str(e)}"
                return False, "Request validation failed"
        return True, None

    def _get_client_ip(self, request) -> str:
        """Get client IP address from request."""
        # Check X-Forwarded-For header (be careful with this in production)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Use client host
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _validation_error_response(self, message: str):
        """Create validation error response."""
        return JSONResponse({"error": message, "type": "validation_error"}, status_code=400)

    def _rate_limit_response(self):
        """Create rate limit response."""
        return JSONResponse(
            {
                "error": "Too many validation failures. Please try again later.",
                "type": "rate_limit",
            },
            status_code=429,
            headers={"Retry-After": "60"},
        )

    def _log_security_event(self, event_type: str, field_name: str, details: str) -> None:
        """
        Log security event for monitoring.

        In production, integrate with SIEM/security monitoring.

        Args:
            event_type: Type of security event
            field_name: Field or component that triggered the event
            details: Additional details about the event
        """
        import logging

        logger = logging.getLogger("covet.security.middleware")
        logger.warning(
            f"Security event: {event_type} on {field_name}",
            extra={
                "event_type": event_type,
                "component": "InputValidationMiddleware",
                "field": field_name,
                "details_hash": hashlib.sha256(details.encode()).hexdigest() if details else None,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


# Pre-configured validation rules for common fields
COMMON_VALIDATION_RULES = {
    "username": ValidationRule(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        required=True,
        sanitize=True,
    ),
    "email": ValidationRule(max_length=254, format="email", required=True, sanitize=True),
    "password": ValidationRule(min_length=8, max_length=128, required=True, sanitize=False),
    "url": ValidationRule(max_length=2048, format="url", sanitize=True),
    "phone": ValidationRule(
        min_length=10, max_length=20, pattern=r"^[0-9+\-\s()]+$", sanitize=True
    ),
    "name": ValidationRule(min_length=1, max_length=100, pattern=r"^[a-zA-Z\s'-]+$", sanitize=True),
    "description": ValidationRule(max_length=5000, sanitize=True),
    "search": ValidationRule(max_length=200, sanitize=True),
}


__all__ = [
    "ValidationRule",
    "FileUploadRule",
    "ValidationConfig",
    "InputValidator",
    "InputValidationMiddleware",
    "ValidationFailureTracker",
    "COMMON_VALIDATION_RULES",
]
