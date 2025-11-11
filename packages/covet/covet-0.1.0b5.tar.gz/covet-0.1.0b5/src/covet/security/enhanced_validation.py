"""
Enhanced Input Validation with Security Focus for CovetPy Framework.

This module provides comprehensive input validation to prevent security vulnerabilities including:
- Email validation (RFC 5322 compliant)
- Username validation with security rules
- Password strength validation
- Path traversal prevention
- SQL injection prevention
- XSS prevention
- URL validation

Example:
    from covet.security.enhanced_validation import EnhancedValidator

    # Email validation
    is_valid = EnhancedValidator.validate_email("user@example.com")

    # Password validation
    is_valid, errors = EnhancedValidator.validate_password("SecurePass123!")

    # Path validation
    is_valid, error = EnhancedValidator.validate_path("/var/www/uploads/file.txt", ["/var/www/uploads"])
"""

import html
import re
import urllib.parse
from pathlib import Path
from typing import Any, List, Optional, Tuple


class EnhancedValidator:
    """
    Enhanced input validation for security.

    Provides static methods for validating and sanitizing various types of input
    to prevent common security vulnerabilities.
    """

    # Email regex pattern (RFC 5322 compliant - simplified)
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )

    # Username pattern (alphanumeric + underscore, must start with letter or underscore)
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    # SQL identifier pattern (table/column names)
    SQL_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    # Dangerous characters for path traversal
    PATH_TRAVERSAL_PATTERNS = [
        "..",
        "~",
        "//",
        "\\\\",
    ]

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bupdate\b.*\bset\b)",
        r"('.*--)",
        r"(;.*--)",
        r"(\bor\b.*=.*)",
        r"(\band\b.*=.*)",
    ]

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format (RFC 5322 compliant).

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> EnhancedValidator.validate_email("user@example.com")
            (True, None)
            >>> EnhancedValidator.validate_email("invalid.email")
            (False, "Email must contain @ symbol")
        """
        if not email or not isinstance(email, str):
            return False, "Email is required and must be a string"

        # Length check (max 320 chars total, 64 for local part, 255 for domain)
        if len(email) > 320:
            return False, "Email must not exceed 320 characters"

        # Split and validate parts
        parts = email.rsplit("@", 1)
        if len(parts) != 2:
            return False, "Email must contain @ symbol"

        local_part, domain = parts
        if len(local_part) > 64:
            return False, "Email local part must not exceed 64 characters"
        if len(domain) > 255:
            return False, "Email domain must not exceed 255 characters"

        # Regex validation
        if not EnhancedValidator.EMAIL_PATTERN.match(email):
            return False, "Email format is invalid"

        return True, None

    @staticmethod
    def validate_username(
        username: str, min_length: int = 3, max_length: int = 50
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate username.

        Rules:
        - Alphanumeric + underscore only
        - 3-50 characters (configurable)
        - Must start with letter or underscore (not number)
        - No consecutive underscores

        Args:
            username: Username to validate
            min_length: Minimum length (default: 3)
            max_length: Maximum length (default: 50)

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> EnhancedValidator.validate_username("john_doe")
            (True, None)
            >>> EnhancedValidator.validate_username("ab")
            (False, "Username must be at least 3 characters long")
        """
        if not username or not isinstance(username, str):
            return False, "Username is required and must be a string"

        # Length check
        if len(username) < min_length:
            return False, f"Username must be at least {min_length} characters long"

        if len(username) > max_length:
            return False, f"Username must not exceed {max_length} characters"

        # Pattern check
        if not EnhancedValidator.USERNAME_PATTERN.match(username):
            return (
                False,
                "Username must start with a letter or underscore and contain only alphanumeric characters and underscores",
            )

        # No consecutive underscores
        if "__" in username:
            return False, "Username cannot contain consecutive underscores"

        # Cannot be only underscores
        if username.replace("_", "") == "":
            return False, "Username cannot consist only of underscores"

        return True, None

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength.

        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, list_of_errors)

        Example:
            >>> EnhancedValidator.validate_password("SecurePass123!")
            (True, [])
            >>> EnhancedValidator.validate_password("weak")
            (False, ["Password must be at least 8 characters", ...])
        """
        errors = []

        if not password or not isinstance(password, str):
            return False, ["Password is required and must be a string"]

        # Length check
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")

        # Maximum length check (prevent DoS)
        if len(password) > 128:
            errors.append("Password must not exceed 128 characters")

        # Uppercase check
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        # Lowercase check
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        # Digit check
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")

        # Special character check
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
            errors.append(
                "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
            )

        # Common password check (basic)
        common_passwords = [
            "password",
            "12345678",
            "qwerty",
            "abc123",
            "password123",
            "welcome",
            "admin",
            "letmein",
            "monkey",
            "dragon",
        ]
        if password.lower() in common_passwords:
            errors.append("Password is too common. Please choose a more unique password")

        return len(errors) == 0, errors

    @staticmethod
    def validate_path(
        path: str, allowed_dirs: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate file path against directory traversal.

        Security checks:
        - No '..' in path
        - Path resolves within allowed directories
        - No symlink attacks (checks resolved path)

        Args:
            path: File path to validate
            allowed_dirs: List of allowed directory paths (absolute paths)

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> EnhancedValidator.validate_path("/var/www/uploads/file.txt", ["/var/www/uploads"])
            (True, None)
            >>> EnhancedValidator.validate_path("/var/www/../etc/passwd", ["/var/www/uploads"])
            (False, "Path traversal detected")
        """
        if not path or not isinstance(path, str):
            return False, "Path is required and must be a string"

        # Check for dangerous patterns
        for pattern in EnhancedValidator.PATH_TRAVERSAL_PATTERNS:
            if pattern in path:
                return False, f"Path traversal pattern detected: {pattern}"

        # Check for null bytes
        if "\x00" in path:
            return False, "Null byte detected in path"

        try:
            # Resolve path (follows symlinks)
            resolved_path = Path(path).resolve()

            # If allowed_dirs specified, check if path is within allowed directories
            if allowed_dirs:
                is_allowed = False
                for allowed_dir in allowed_dirs:
                    try:
                        allowed_path = Path(allowed_dir).resolve()
                        # Check if resolved_path is within allowed_path
                        resolved_path.relative_to(allowed_path)
                        is_allowed = True
                        break
                    except ValueError:
                        # Not relative to this allowed_dir, try next
                        continue

                if not is_allowed:
                    return False, f"Path is not within allowed directories"

            return True, None

        except (OSError, ValueError) as e:
            return False, f"Invalid path: {str(e)}"

    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """
        Sanitize SQL identifier (table/column name).

        Rules:
        - Must match ^[a-zA-Z_][a-zA-Z0-9_]*$
        - Raise ValueError if invalid

        Args:
            identifier: SQL identifier to sanitize

        Returns:
            Sanitized identifier (unchanged if valid)

        Raises:
            ValueError: If identifier is invalid

        Example:
            >>> EnhancedValidator.sanitize_sql_identifier("users_table")
            'users_table'
            >>> EnhancedValidator.sanitize_sql_identifier("DROP TABLE users")
            ValueError: Invalid SQL identifier
        """
        if not identifier or not isinstance(identifier, str):
            raise ValueError("SQL identifier is required and must be a string")

        # Length check (most databases limit to 64 chars)
        if len(identifier) > 64:
            raise ValueError("SQL identifier must not exceed 64 characters")

        # Pattern check
        if not EnhancedValidator.SQL_IDENTIFIER_PATTERN.match(identifier):
            raise ValueError(
                "Invalid SQL identifier. Must start with letter or underscore "
                "and contain only alphanumeric characters and underscores"
            )

        return identifier

    @staticmethod
    def sanitize_html(html_content: str) -> str:
        """
        Sanitize HTML to prevent XSS attacks.

        This is a basic implementation that escapes all HTML entities.
        For more advanced HTML sanitization, use libraries like bleach.

        Args:
            html_content: HTML content to sanitize

        Returns:
            Sanitized HTML with escaped entities

        Example:
            >>> EnhancedValidator.sanitize_html("<script>alert('xss')</script>")
            '&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;'
        """
        if not html_content or not isinstance(html_content, str):
            return ""

        # Escape HTML entities
        return html.escape(html_content, quote=True)

    @staticmethod
    def validate_url(
        url: str, allowed_schemes: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format and allowed schemes.

        Args:
            url: URL to validate
            allowed_schemes: List of allowed schemes (e.g., ['http', 'https'])
                           If None, allows http and https

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> EnhancedValidator.validate_url("https://example.com")
            (True, None)
            >>> EnhancedValidator.validate_url("javascript:alert('xss')")
            (False, "URL scheme not allowed")
        """
        if not url or not isinstance(url, str):
            return False, "URL is required and must be a string"

        # Length check (prevent DoS)
        if len(url) > 2048:
            return False, "URL exceeds maximum length (2048 characters)"

        # Default allowed schemes
        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]

        try:
            parsed = urllib.parse.urlparse(url)

            # Check scheme
            if parsed.scheme not in allowed_schemes:
                return (
                    False,
                    f"URL scheme not allowed. Allowed schemes: {', '.join(allowed_schemes)}",
                )

            # Check for netloc (domain)
            if not parsed.netloc:
                return False, "URL must have a domain"

            # Check for suspicious patterns
            if "@" in parsed.netloc:
                return False, "URL contains suspicious '@' in domain"

            # Check for IP address in private ranges (optional security)
            # This is a basic check - for production, use ipaddress module
            if re.match(r"^(10\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.)", parsed.netloc):
                return False, "URL points to private IP address"

            return True, None

        except Exception as e:
            return False, f"Invalid URL: {str(e)}"

    @staticmethod
    def detect_sql_injection(input_string: str) -> Tuple[bool, List[str]]:
        """
        Detect potential SQL injection patterns.

        This is a basic detection mechanism. Always use parameterized queries.

        Args:
            input_string: String to check for SQL injection

        Returns:
            Tuple of (is_suspicious, list_of_detected_patterns)

        Example:
            >>> EnhancedValidator.detect_sql_injection("admin' OR '1'='1")
            (True, ["or statement"])
        """
        if not input_string or not isinstance(input_string, str):
            return False, []

        detected_patterns = []
        input_lower = input_string.lower()

        for pattern in EnhancedValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                detected_patterns.append(pattern)

        return len(detected_patterns) > 0, detected_patterns

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent security issues.

        Removes:
        - Path separators (/, \\)
        - Null bytes
        - Control characters
        - Leading/trailing dots and spaces

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename

        Example:
            >>> EnhancedValidator.sanitize_filename("../../etc/passwd")
            'etc_passwd'
        """
        if not filename or not isinstance(filename, str):
            return "unnamed"

        # Remove path separators
        filename = filename.replace("/", "_").replace("\\", "_")

        # Remove null bytes and control characters
        filename = "".join(char for char in filename if ord(char) >= 32 and char != "\x00")

        # Remove leading/trailing dots and spaces
        filename = filename.strip(". ")

        # Replace multiple underscores
        filename = re.sub(r"_+", "_", filename)

        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
            filename = name[:250] + ("." + ext if ext else "")

        # Ensure not empty
        if not filename:
            return "unnamed"

        return filename

    @staticmethod
    def validate_integer(
        value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Validate and parse integer value.

        Args:
            value: Value to validate and parse
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)

        Returns:
            Tuple of (is_valid, parsed_value, error_message)

        Example:
            >>> EnhancedValidator.validate_integer("42", min_value=0, max_value=100)
            (True, 42, None)
        """
        try:
            parsed = int(value)

            if min_value is not None and parsed < min_value:
                return False, None, f"Value must be at least {min_value}"

            if max_value is not None and parsed > max_value:
                return False, None, f"Value must not exceed {max_value}"

            return True, parsed, None

        except (ValueError, TypeError):
            return False, None, "Invalid integer value"

    @staticmethod
    def validate_float(
        value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None
    ) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Validate and parse float value.

        Args:
            value: Value to validate and parse
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)

        Returns:
            Tuple of (is_valid, parsed_value, error_message)

        Example:
            >>> EnhancedValidator.validate_float("3.14", min_value=0.0)
            (True, 3.14, None)
        """
        try:
            parsed = float(value)

            if min_value is not None and parsed < min_value:
                return False, None, f"Value must be at least {min_value}"

            if max_value is not None and parsed > max_value:
                return False, None, f"Value must not exceed {max_value}"

            return True, parsed, None

        except (ValueError, TypeError):
            return False, None, "Invalid float value"


# Export all public APIs
__all__ = [
    "EnhancedValidator",
]
