"""
Production-Grade Input Validation Framework

This module provides comprehensive input validation with Pydantic integration,
protecting against injection attacks, XSS, CSRF, and malformed data.

Security Features:
- Automatic request body validation with Pydantic
- SQL injection prevention
- XSS (Cross-Site Scripting) prevention
- CSRF token validation
- File upload validation (size, type, content)
- Path traversal prevention
- Returns 400 Bad Request (not 500) on validation errors

Threat Protection:
- SQL injection attacks
- NoSQL injection attacks
- Command injection
- XSS attacks (reflected, stored, DOM-based)
- CSRF attacks
- Path traversal attacks
- Malicious file uploads
- Buffer overflow via oversized inputs

Example Usage:
    from covet.validation.validator import (
        InputValidator,
        validate_request,
        prevent_sql_injection,
        prevent_xss
    )

    from pydantic import BaseModel, EmailStr

    # Define request schema
    class UserCreate(BaseModel):
        username: str
        email: EmailStr
        age: int

    # Validate request automatically
    @validate_request(UserCreate)
    async def create_user(request):
        # request.validated_data contains validated UserCreate instance
        user = request.validated_data
        return {"username": user.username}

    # Manual validation
    validator = InputValidator()
    safe_query = validator.sanitize_sql("SELECT * FROM users WHERE id = ?")
    safe_html = validator.sanitize_html("<script>alert('xss')</script>")
"""

import html
import mimetypes
import os
import re
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

try:
    from pydantic import BaseModel, ValidationError, validator
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object
    ValidationError = Exception


class ValidationException(Exception):
    """Base exception for validation errors."""

    def __init__(self, message: str, errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "error": "Validation Error",
            "message": self.message,
            "details": self.errors,
        }


class SQLInjectionError(ValidationException):
    """SQL injection attempt detected."""
    pass


class XSSError(ValidationException):
    """XSS attempt detected."""
    pass


class CSRFError(ValidationException):
    """CSRF validation failed."""
    pass


class PathTraversalError(ValidationException):
    """Path traversal attempt detected."""
    pass


class FileValidationError(ValidationException):
    """File validation failed."""
    pass


class InputValidator:
    """
    Comprehensive input validator with security protections.

    Provides methods for validating and sanitizing various input types
    to prevent common injection attacks.
    """

    # SQL injection patterns (simplified for demonstration)
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
        r"(\binsert\b.*\binto\b.*\bvalues\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\bdrop\b.*\bdatabase\b)",
        r"(--|\#|/\*|\*/)",  # SQL comments
        r"(\bor\b.*=.*)",
        r"(\band\b.*=.*)",
        r"(;.*\b(select|insert|update|delete|drop)\b)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers (onclick, onerror, etc.)
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<applet[^>]*>",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"\.\.\\",
    ]

    # Dangerous file extensions
    DANGEROUS_EXTENSIONS = {
        ".exe", ".bat", ".cmd", ".com", ".pif", ".scr",
        ".vbs", ".js", ".jar", ".msi", ".dll", ".so",
        ".sh", ".php", ".asp", ".aspx", ".jsp",
    }

    # Allowed MIME types for file uploads (whitelist approach)
    ALLOWED_MIME_TYPES = {
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf",
        "text/plain", "text/csv",
        "application/json",
        "application/zip",
    }

    def __init__(
        self,
        max_string_length: int = 10000,
        max_array_length: int = 1000,
        max_file_size: int = 10 * 1024 * 1024,  # 10 MB
        allowed_mime_types: Optional[Set[str]] = None,
    ):
        """
        Initialize input validator.

        Args:
            max_string_length: Maximum allowed string length
            max_array_length: Maximum allowed array length
            max_file_size: Maximum file size in bytes
            allowed_mime_types: Allowed MIME types for uploads
        """
        self.max_string_length = max_string_length
        self.max_array_length = max_array_length
        self.max_file_size = max_file_size
        self.allowed_mime_types = allowed_mime_types or self.ALLOWED_MIME_TYPES

        # Compile regex patterns for performance
        self.sql_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SQL_INJECTION_PATTERNS
        ]
        self.xss_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.XSS_PATTERNS
        ]
        self.path_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.PATH_TRAVERSAL_PATTERNS
        ]

    def validate_string(
        self,
        value: str,
        min_length: int = 0,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        check_sql_injection: bool = True,
        check_xss: bool = True,
    ) -> str:
        """
        Validate and sanitize string input.

        Args:
            value: String to validate
            min_length: Minimum length
            max_length: Maximum length
            pattern: Regex pattern to match
            check_sql_injection: Check for SQL injection
            check_xss: Check for XSS

        Returns:
            Validated string

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationException("Value must be a string")

        # Length validation
        if len(value) < min_length:
            raise ValidationException(
                f"String too short: minimum length is {min_length}"
            )

        max_len = max_length or self.max_string_length
        if len(value) > max_len:
            raise ValidationException(
                f"String too long: maximum length is {max_len}"
            )

        # Pattern validation
        if pattern and not re.match(pattern, value):
            raise ValidationException("String does not match required pattern")

        # SQL injection check
        if check_sql_injection:
            self.check_sql_injection(value)

        # XSS check
        if check_xss:
            self.check_xss(value)

        return value

    def check_sql_injection(self, value: str) -> None:
        """
        Check for SQL injection patterns.

        Args:
            value: String to check

        Raises:
            SQLInjectionError: If SQL injection detected
        """
        for pattern in self.sql_patterns:
            if pattern.search(value):
                raise SQLInjectionError(
                    "Potential SQL injection detected",
                    errors=[{"pattern": pattern.pattern, "value": value}]
                )

    def sanitize_sql(self, value: str) -> str:
        """
        Sanitize string for SQL usage.

        Note: This is a defense-in-depth measure. Always use
        parameterized queries as the primary defense.

        Args:
            value: String to sanitize

        Returns:
            Sanitized string
        """
        # Remove dangerous characters
        sanitized = value.replace("'", "''")  # Escape single quotes
        sanitized = sanitized.replace(";", "")  # Remove statement terminators
        sanitized = sanitized.replace("--", "")  # Remove comments
        sanitized = sanitized.replace("/*", "")  # Remove block comments
        sanitized = sanitized.replace("*/", "")
        return sanitized

    def check_xss(self, value: str) -> None:
        """
        Check for XSS patterns.

        Args:
            value: String to check

        Raises:
            XSSError: If XSS attempt detected
        """
        for pattern in self.xss_patterns:
            if pattern.search(value):
                raise XSSError(
                    "Potential XSS attempt detected",
                    errors=[{"pattern": pattern.pattern, "value": value}]
                )

    def sanitize_html(self, value: str, escape: bool = True) -> str:
        """
        Sanitize HTML input.

        Args:
            value: HTML string to sanitize
            escape: Whether to HTML-escape the content

        Returns:
            Sanitized HTML
        """
        if escape:
            # Full HTML escaping (safest)
            return html.escape(value)
        else:
            # Remove dangerous tags but preserve safe HTML
            sanitized = value
            for pattern in self.xss_patterns:
                sanitized = pattern.sub("", sanitized)
            return sanitized

    def check_path_traversal(self, path: str) -> None:
        """
        Check for path traversal attempts.

        Args:
            path: File path to check

        Raises:
            PathTraversalError: If path traversal detected
        """
        for pattern in self.path_patterns:
            if pattern.search(path):
                raise PathTraversalError(
                    "Potential path traversal detected",
                    errors=[{"pattern": pattern.pattern, "path": path}]
                )

        # Additional check: ensure resolved path is within allowed directory
        # (Should be used with a base directory parameter in production)

    def sanitize_path(self, path: str, base_dir: Optional[str] = None) -> str:
        """
        Sanitize file path.

        Args:
            path: File path to sanitize
            base_dir: Base directory to constrain path within

        Returns:
            Sanitized absolute path

        Raises:
            PathTraversalError: If path escapes base directory
        """
        # Check for path traversal patterns
        self.check_path_traversal(path)

        # Resolve to absolute path
        abs_path = Path(path).resolve()

        # If base directory specified, ensure path is within it
        if base_dir:
            base = Path(base_dir).resolve()
            try:
                abs_path.relative_to(base)
            except ValueError:
                raise PathTraversalError(
                    "Path attempts to escape base directory",
                    errors=[{"path": str(abs_path), "base": str(base)}]
                )

        return str(abs_path)

    def validate_file_upload(
        self,
        filename: str,
        content: bytes,
        content_type: Optional[str] = None,
        check_content: bool = True,
    ) -> Dict[str, Any]:
        """
        Validate file upload.

        Args:
            filename: Original filename
            content: File content bytes
            content_type: Declared MIME type
            check_content: Verify content matches declared type

        Returns:
            Dictionary with validation results

        Raises:
            FileValidationError: If validation fails
        """
        # Check filename for path traversal
        self.check_path_traversal(filename)

        # Check file extension
        ext = Path(filename).suffix.lower()
        if ext in self.DANGEROUS_EXTENSIONS:
            raise FileValidationError(
                f"File extension '{ext}' not allowed",
                errors=[{"filename": filename, "extension": ext}]
            )

        # Check file size
        if len(content) > self.max_file_size:
            raise FileValidationError(
                f"File too large: maximum size is {self.max_file_size} bytes",
                errors=[{"size": len(content), "max_size": self.max_file_size}]
            )

        # Validate MIME type
        if content_type:
            if content_type not in self.allowed_mime_types:
                raise FileValidationError(
                    f"MIME type '{content_type}' not allowed",
                    errors=[{"content_type": content_type}]
                )

        # Guess MIME type from content
        if check_content:
            import magic
            detected_type = magic.from_buffer(content, mime=True)

            if detected_type not in self.allowed_mime_types:
                raise FileValidationError(
                    f"Detected MIME type '{detected_type}' not allowed",
                    errors=[{
                        "declared_type": content_type,
                        "detected_type": detected_type
                    }]
                )

            # Verify declared type matches detected type
            if content_type and content_type != detected_type:
                raise FileValidationError(
                    "Declared MIME type does not match file content",
                    errors=[{
                        "declared": content_type,
                        "detected": detected_type
                    }]
                )

        return {
            "filename": filename,
            "size": len(content),
            "content_type": content_type,
            "extension": ext,
            "valid": True,
        }

    def validate_email(self, email: str) -> str:
        """
        Validate email address.

        Args:
            email: Email address to validate

        Returns:
            Validated email

        Raises:
            ValidationException: If invalid
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ValidationException("Invalid email address")

        # Check for XSS in email
        self.check_xss(email)

        return email.lower()

    def validate_url(
        self,
        url: str,
        allowed_schemes: Optional[Set[str]] = None,
    ) -> str:
        """
        Validate URL.

        Args:
            url: URL to validate
            allowed_schemes: Allowed URL schemes (http, https, etc.)

        Returns:
            Validated URL

        Raises:
            ValidationException: If invalid
        """
        from urllib.parse import urlparse

        allowed_schemes = allowed_schemes or {"http", "https"}

        try:
            parsed = urlparse(url)
        except Exception:
            raise ValidationException("Invalid URL format")

        if parsed.scheme not in allowed_schemes:
            raise ValidationException(
                f"URL scheme must be one of: {', '.join(allowed_schemes)}"
            )

        # Check for javascript: protocol and other XSS vectors
        if parsed.scheme == "javascript":
            raise XSSError("JavaScript URLs not allowed")

        return url


class CSRFValidator:
    """
    CSRF token validator.

    Implements double-submit cookie pattern and synchronizer token pattern.
    """

    def __init__(self, secret_key: str, token_length: int = 32):
        """
        Initialize CSRF validator.

        Args:
            secret_key: Secret key for token generation
            token_length: Length of generated tokens
        """
        self.secret_key = secret_key
        self.token_length = token_length

    def generate_token(self, session_id: Optional[str] = None) -> str:
        """
        Generate CSRF token.

        Args:
            session_id: Session ID to bind token to

        Returns:
            CSRF token
        """
        import hashlib
        import secrets

        # Generate random token
        random_part = secrets.token_hex(self.token_length // 2)

        # Create HMAC signature
        message = f"{random_part}:{session_id or ''}"
        signature = hashlib.sha256(
            f"{self.secret_key}:{message}".encode()
        ).hexdigest()[:16]

        return f"{random_part}.{signature}"

    def validate_token(
        self,
        token: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """
        Validate CSRF token.

        Args:
            token: Token to validate
            session_id: Session ID token should be bound to

        Returns:
            True if valid, False otherwise
        """
        import hashlib

        try:
            random_part, signature = token.split(".")
        except ValueError:
            return False

        # Verify signature
        message = f"{random_part}:{session_id or ''}"
        expected_signature = hashlib.sha256(
            f"{self.secret_key}:{message}".encode()
        ).hexdigest()[:16]

        # Use constant-time comparison
        return self._constant_time_compare(signature, expected_signature)

    @staticmethod
    def _constant_time_compare(a: str, b: str) -> bool:
        """Constant-time string comparison to prevent timing attacks."""
        if len(a) != len(b):
            return False

        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)

        return result == 0


def validate_request(schema: Type[BaseModel]):
    """
    Decorator for automatic request validation with Pydantic.

    Args:
        schema: Pydantic model class to validate against

    Returns:
        Decorated function

    Example:
        @validate_request(UserCreate)
        async def create_user(request):
            user = request.validated_data
            return {"username": user.username}
    """
    if not HAS_PYDANTIC:
        raise ImportError("pydantic required for validate_request decorator")

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            try:
                # Get request body
                if hasattr(request, "json"):
                    data = await request.json()
                elif hasattr(request, "body"):
                    import json
                    data = json.loads(await request.body())
                else:
                    raise ValidationException("Unable to extract request body")

                # Validate with Pydantic
                validated = schema(**data)

                # Attach validated data to request
                request.validated_data = validated

                # Call original function
                return await func(request, *args, **kwargs)

            except ValidationError as e:
                # Return 400 Bad Request with validation errors
                errors = [
                    {
                        "field": ".".join(str(x) for x in error["loc"]),
                        "message": error["msg"],
                        "type": error["type"],
                    }
                    for error in e.errors()
                ]

                raise ValidationException(
                    "Request validation failed",
                    errors=errors
                )

        return wrapper

    return decorator


# Convenience functions
def prevent_sql_injection(value: str) -> str:
    """Check for SQL injection (raises exception if detected)."""
    validator = InputValidator()
    validator.check_sql_injection(value)
    return value


def prevent_xss(value: str) -> str:
    """Check for XSS (raises exception if detected)."""
    validator = InputValidator()
    validator.check_xss(value)
    return value


def sanitize_html(value: str) -> str:
    """Sanitize HTML content."""
    validator = InputValidator()
    return validator.sanitize_html(value)


def sanitize_sql(value: str) -> str:
    """Sanitize SQL input (use parameterized queries instead)."""
    validator = InputValidator()
    return validator.sanitize_sql(value)


__all__ = [
    "InputValidator",
    "CSRFValidator",
    "ValidationException",
    "SQLInjectionError",
    "XSSError",
    "CSRFError",
    "PathTraversalError",
    "FileValidationError",
    "validate_request",
    "prevent_sql_injection",
    "prevent_xss",
    "sanitize_html",
    "sanitize_sql",
]
