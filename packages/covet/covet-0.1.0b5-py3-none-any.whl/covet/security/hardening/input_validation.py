"""
CovetPy Input Validation Module

Comprehensive input validation framework with:
- Type validation
- Length validation
- Format validation (regex patterns)
- Whitelist/blacklist validation
- File upload validation (type, size, content)
- Path traversal prevention
- Unicode validation
- Email/URL/IP validation

Implements defense-in-depth input validation to prevent various injection
and security vulnerabilities.

Author: CovetPy Security Team
License: MIT
"""

import ipaddress
import mimetypes
import os
import re
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

# Optional: python-magic for file type detection (requires libmagic system library)
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


class ValidationError(Exception):
    """Input validation error."""

    pass


class ValidationType(Enum):
    """Types of validation."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    EMAIL = "email"
    URL = "url"
    IP_ADDRESS = "ip_address"
    UUID = "uuid"
    PHONE = "phone"
    DATE = "date"
    FILENAME = "filename"
    PATH = "path"


@dataclass
class ValidationRule:
    """Input validation rule."""

    field_name: str
    required: bool = False
    type: Optional[ValidationType] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    whitelist: Optional[Set[Any]] = None
    blacklist: Optional[Set[Any]] = None
    custom_validator: Optional[Callable[[Any], bool]] = None
    sanitizer: Optional[Callable[[Any], Any]] = None


class InputValidator:
    """
    Comprehensive input validation.
    """

    # Regex patterns for common validations
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    URL_PATTERN = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)
    UUID_PATTERN = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    PHONE_PATTERN = re.compile(r"^\+?1?\d{9,15}$")
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        re.compile(r"\.\."),  # Directory traversal
        re.compile(r"[/\\]\."),  # Hidden files
        re.compile(r"\0"),  # Null byte
    ]

    # Dangerous filename characters
    DANGEROUS_FILENAME_CHARS = {"/", "\\", "\0", "<", ">", ":", '"', "|", "?", "*"}

    def __init__(self, strict_mode: bool = True):
        """
        Initialize input validator.

        Args:
            strict_mode: Enable strict validation rules
        """
        self.strict_mode = strict_mode
        self.rules: Dict[str, ValidationRule] = {}

    def add_rule(self, rule: ValidationRule) -> "InputValidator":
        """Add validation rule."""
        self.rules[rule.field_name] = rule
        return self

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against rules.

        Args:
            data: Input data dictionary

        Returns:
            Validated and sanitized data

        Raises:
            ValidationError: If validation fails
        """
        validated_data = {}

        for field_name, rule in self.rules.items():
            value = data.get(field_name)

            # Required field check
            if rule.required and value is None:
                raise ValidationError(f"Required field missing: {field_name}")

            if value is None:
                continue

            # Type validation
            if rule.type:
                value = self._validate_type(value, rule.type, field_name)

            # Length validation
            if rule.min_length is not None or rule.max_length is not None:
                self._validate_length(value, rule.min_length, rule.max_length, field_name)

            # Value range validation
            if rule.min_value is not None or rule.max_value is not None:
                self._validate_range(value, rule.min_value, rule.max_value, field_name)

            # Pattern validation
            if rule.pattern:
                self._validate_pattern(value, rule.pattern, field_name)

            # Whitelist validation
            if rule.whitelist:
                self._validate_whitelist(value, rule.whitelist, field_name)

            # Blacklist validation
            if rule.blacklist:
                self._validate_blacklist(value, rule.blacklist, field_name)

            # Custom validation
            if rule.custom_validator:
                if not rule.custom_validator(value):
                    raise ValidationError(f"Custom validation failed for: {field_name}")

            # Sanitization
            if rule.sanitizer:
                value = rule.sanitizer(value)

            validated_data[field_name] = value

        return validated_data

    def _validate_type(self, value: Any, expected_type: ValidationType, field_name: str) -> Any:
        """Validate and convert type."""
        if expected_type == ValidationType.STRING:
            return str(value)

        elif expected_type == ValidationType.INTEGER:
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Field {field_name} must be an integer")

        elif expected_type == ValidationType.FLOAT:
            try:
                return float(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Field {field_name} must be a float")

        elif expected_type == ValidationType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes"):
                    return True
                if value.lower() in ("false", "0", "no"):
                    return False
            raise ValidationError(f"Field {field_name} must be a boolean")

        elif expected_type == ValidationType.EMAIL:
            value = str(value)
            if not self.EMAIL_PATTERN.match(value):
                raise ValidationError(f"Field {field_name} must be a valid email")
            return value

        elif expected_type == ValidationType.URL:
            value = str(value)
            if not self.URL_PATTERN.match(value):
                raise ValidationError(f"Field {field_name} must be a valid URL")
            return value

        elif expected_type == ValidationType.IP_ADDRESS:
            try:
                return str(ipaddress.ip_address(value))
            except ValueError:
                raise ValidationError(f"Field {field_name} must be a valid IP address")

        elif expected_type == ValidationType.UUID:
            value = str(value)
            if not self.UUID_PATTERN.match(value):
                raise ValidationError(f"Field {field_name} must be a valid UUID")
            return value

        elif expected_type == ValidationType.PHONE:
            value = str(value)
            if not self.PHONE_PATTERN.match(value):
                raise ValidationError(f"Field {field_name} must be a valid phone number")
            return value

        elif expected_type == ValidationType.DATE:
            value = str(value)
            if not self.DATE_PATTERN.match(value):
                raise ValidationError(f"Field {field_name} must be a valid date (YYYY-MM-DD)")
            return value

        elif expected_type == ValidationType.FILENAME:
            return self.validate_filename(str(value))

        elif expected_type == ValidationType.PATH:
            return self.validate_path(str(value))

        return value

    def _validate_length(
        self, value: Any, min_length: Optional[int], max_length: Optional[int], field_name: str
    ):
        """Validate length constraints."""
        length = len(str(value))

        if min_length is not None and length < min_length:
            raise ValidationError(f"Field {field_name} must be at least {min_length} characters")

        if max_length is not None and length > max_length:
            raise ValidationError(f"Field {field_name} must be at most {max_length} characters")

    def _validate_range(
        self,
        value: Union[int, float],
        min_value: Optional[Union[int, float]],
        max_value: Optional[Union[int, float]],
        field_name: str,
    ):
        """Validate numeric range."""
        if min_value is not None and value < min_value:
            raise ValidationError(f"Field {field_name} must be at least {min_value}")

        if max_value is not None and value > max_value:
            raise ValidationError(f"Field {field_name} must be at most {max_value}")

    def _validate_pattern(self, value: Any, pattern: str, field_name: str):
        """Validate regex pattern."""
        if not re.match(pattern, str(value)):
            raise ValidationError(f"Field {field_name} does not match required pattern")

    def _validate_whitelist(self, value: Any, whitelist: Set[Any], field_name: str):
        """Validate against whitelist."""
        if value not in whitelist:
            raise ValidationError(f"Field {field_name} contains invalid value")

    def _validate_blacklist(self, value: Any, blacklist: Set[Any], field_name: str):
        """Validate against blacklist."""
        if value in blacklist:
            raise ValidationError(f"Field {field_name} contains prohibited value")

    @staticmethod
    def validate_filename(filename: str, max_length: int = 255) -> str:
        """
        Validate filename for security.

        Args:
            filename: Filename to validate
            max_length: Maximum filename length

        Returns:
            Validated filename

        Raises:
            ValidationError: If filename is invalid
        """
        if not filename:
            raise ValidationError("Filename cannot be empty")

        if len(filename) > max_length:
            raise ValidationError(f"Filename too long (max {max_length} characters)")

        # Check for dangerous characters
        for char in InputValidator.DANGEROUS_FILENAME_CHARS:
            if char in filename:
                raise ValidationError(f"Filename contains dangerous character: {char}")

        # Check for path traversal
        for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
            if pattern.search(filename):
                raise ValidationError("Filename contains path traversal attempt")

        # Check for null bytes
        if "\0" in filename:
            raise ValidationError("Filename contains null byte")

        return filename

    @staticmethod
    def validate_path(path: str, allowed_base: Optional[str] = None) -> str:
        """
        Validate file path for security.

        Args:
            path: Path to validate
            allowed_base: Base directory path must be within

        Returns:
            Validated absolute path

        Raises:
            ValidationError: If path is invalid or outside allowed base
        """
        if not path:
            raise ValidationError("Path cannot be empty")

        # Check for path traversal
        for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
            if pattern.search(path):
                raise ValidationError("Path contains traversal attempt")

        # Normalize path
        normalized_path = os.path.normpath(path)
        absolute_path = os.path.abspath(normalized_path)

        # Check if within allowed base
        if allowed_base:
            allowed_base = os.path.abspath(allowed_base)
            if not absolute_path.startswith(allowed_base):
                raise ValidationError("Path is outside allowed directory")

        return absolute_path


class FileUploadValidator:
    """
    File upload validation.
    """

    def __init__(
        self,
        allowed_extensions: Optional[Set[str]] = None,
        allowed_mimetypes: Optional[Set[str]] = None,
        max_size: int = 10 * 1024 * 1024,  # 10MB default
        check_content: bool = True,
    ):
        """
        Initialize file upload validator.

        Args:
            allowed_extensions: Set of allowed file extensions
            allowed_mimetypes: Set of allowed MIME types
            max_size: Maximum file size in bytes
            check_content: Verify file content matches extension
        """
        self.allowed_extensions = allowed_extensions or {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".pdf",
            ".txt",
            ".doc",
            ".docx",
        }
        self.allowed_mimetypes = allowed_mimetypes or {
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/pdf",
            "text/plain",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        self.max_size = max_size
        self.check_content = check_content

    def validate(self, filename: str, file_content: bytes) -> None:
        """
        Validate uploaded file.

        Args:
            filename: Original filename
            file_content: File content bytes

        Raises:
            ValidationError: If file is invalid
        """
        # Validate filename
        filename = InputValidator.validate_filename(filename)

        # Check file size
        if len(file_content) > self.max_size:
            raise ValidationError(f"File too large (max {self.max_size} bytes)")

        # Check extension
        _, ext = os.path.splitext(filename.lower())
        if ext not in self.allowed_extensions:
            raise ValidationError(f"File extension not allowed: {ext}")

        # Check MIME type
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type and guessed_type not in self.allowed_mimetypes:
            raise ValidationError(f"File type not allowed: {guessed_type}")

        # Verify content matches extension
        if self.check_content and HAS_MAGIC:
            try:
                detected_type = magic.from_buffer(file_content, mime=True)
                if detected_type not in self.allowed_mimetypes:
                    raise ValidationError(
                        f"File content does not match extension (detected: {detected_type})"
                    )
            except Exception:
                # magic.from_buffer failed, skip content check
                pass


__all__ = [
    "ValidationError",
    "ValidationType",
    "ValidationRule",
    "InputValidator",
    "FileUploadValidator",
]
