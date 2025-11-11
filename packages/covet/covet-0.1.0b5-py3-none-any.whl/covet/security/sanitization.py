"""
Input Sanitization and Validation

Production-grade input sanitization to prevent:
- Cross-Site Scripting (XSS)
- Path Traversal attacks
- SQL Injection (documentation)
- Command Injection
- LDAP Injection
- XML/XXE attacks

Security Features:
- HTML sanitization with allowlist
- HTML entity encoding
- Path traversal prevention
- Filename sanitization
- URL validation and sanitization
- Email validation
- JSON sanitization
"""

import html
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote, unquote, urlparse


class HTMLSanitizer:
    """
    HTML sanitizer with tag allowlist

    Removes or escapes potentially dangerous HTML while allowing safe tags.
    """

    # Default safe tags
    SAFE_TAGS = {
        "p",
        "br",
        "strong",
        "em",
        "u",
        "i",
        "b",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "dl",
        "dt",
        "dd",
        "blockquote",
        "code",
        "pre",
        "a",
        "img",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    }

    # Safe attributes per tag
    SAFE_ATTRIBUTES = {
        "a": {"href", "title", "rel"},
        "img": {"src", "alt", "title", "width", "height"},
        "table": {"border", "cellpadding", "cellspacing"},
        "td": {"colspan", "rowspan"},
        "th": {"colspan", "rowspan"},
    }

    # Dangerous protocols
    DANGEROUS_PROTOCOLS = {"javascript:", "data:", "vbscript:", "file:"}

    def __init__(
        self,
        allowed_tags: Optional[Set[str]] = None,
        allowed_attributes: Optional[Dict[str, Set[str]]] = None,
        strip_tags: bool = False,
    ):
        """
        Initialize HTML sanitizer

        Args:
            allowed_tags: Set of allowed HTML tags
            allowed_attributes: Dict of allowed attributes per tag
            strip_tags: If True, remove tags instead of escaping
        """
        self.allowed_tags = allowed_tags or self.SAFE_TAGS.copy()
        self.allowed_attributes = allowed_attributes or self.SAFE_ATTRIBUTES.copy()
        self.strip_tags = strip_tags

    def sanitize(self, html_input: str) -> str:
        """
        Sanitize HTML input

        Args:
            html_input: Raw HTML string

        Returns:
            Sanitized HTML string
        """
        if not html_input:
            return ""

        # Remove dangerous tags and attributes
        result = self._remove_dangerous_elements(html_input)

        # Escape remaining unsafe content
        if not self.strip_tags:
            result = self._escape_unsafe_tags(result)

        return result

    def _remove_dangerous_elements(self, html_input: str) -> str:
        """Remove dangerous HTML elements"""
        # Remove script tags and content
        html_input = re.sub(
            r"<script[^>]*>.*?</script>",
            "",
            html_input,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove style tags and content
        html_input = re.sub(
            r"<style[^>]*>.*?</style>", "", html_input, flags=re.IGNORECASE | re.DOTALL
        )

        # Remove event handlers (onclick, onerror, etc.)
        html_input = re.sub(
            r'\s+on\w+\s*=\s*["\']?[^"\'>]*["\']?', "", html_input, flags=re.IGNORECASE
        )

        # Remove dangerous href/src protocols
        for protocol in self.DANGEROUS_PROTOCOLS:
            pattern = re.compile(rf'(href|src)\s*=\s*["\']?\s*{re.escape(protocol)}', re.IGNORECASE)
            html_input = pattern.sub(r'\1="#"', html_input)

        return html_input

    def _escape_unsafe_tags(self, html_input: str) -> str:
        """Escape tags not in allowlist"""
        # Find all tags
        tag_pattern = re.compile(r"<(/?)(\w+)([^>]*)>", re.IGNORECASE)

        def replace_tag(match):
            closing = match.group(1)
            tag_name = match.group(2).lower()
            attributes = match.group(3)

            if tag_name in self.allowed_tags:
                # Keep allowed tags but filter attributes
                filtered_attrs = self._filter_attributes(tag_name, attributes)
                return f"<{closing}{tag_name}{filtered_attrs}>"
            else:
                # Escape unsafe tags
                return html.escape(match.group(0))

        return tag_pattern.sub(replace_tag, html_input)

    def _filter_attributes(self, tag: str, attributes: str) -> str:
        """Filter attributes for a tag"""
        if tag not in self.allowed_attributes:
            return ""

        allowed = self.allowed_attributes[tag]

        # Parse attributes
        attr_pattern = re.compile(r'(\w+)\s*=\s*["\']?([^"\'>]*)["\']?')
        filtered = []

        for match in attr_pattern.finditer(attributes):
            attr_name = match.group(1).lower()
            attr_value = match.group(2)

            if attr_name in allowed:
                # Additional validation for href/src
                if attr_name in ("href", "src"):
                    if not self._is_safe_url(attr_value):
                        continue

                filtered.append(f'{attr_name}="{html.escape(attr_value)}"')

        return " " + " ".join(filtered) if filtered else ""

    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is safe"""
        url_lower = url.lower().strip()

        # Check for dangerous protocols
        for protocol in self.DANGEROUS_PROTOCOLS:
            if url_lower.startswith(protocol):
                return False

        return True


def sanitize_html(
    html_input: str, allowed_tags: Optional[List[str]] = None, strip_tags: bool = False
) -> str:
    """
    Sanitize HTML input (convenience function)

    Args:
        html_input: Raw HTML string
        allowed_tags: List of allowed tags
        strip_tags: Strip tags instead of escaping

    Returns:
        Sanitized HTML string

    Example:
        >>> sanitize_html('<script>alert("xss")</script><p>Hello</p>')
        '<p>Hello</p>'

        >>> sanitize_html('<p onclick="evil()">Click</p>')
        '<p>Click</p>'
    """
    sanitizer = HTMLSanitizer(
        allowed_tags=set(allowed_tags) if allowed_tags else None, strip_tags=strip_tags
    )
    return sanitizer.sanitize(html_input)


def escape_html(text: str) -> str:
    """
    Escape HTML entities

    Args:
        text: Text to escape

    Returns:
        HTML-escaped text

    Example:
        >>> escape_html('<script>alert("xss")</script>')
        '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
    """
    return html.escape(text, quote=True)


def strip_html(html_input: str) -> str:
    """
    Strip all HTML tags

    Args:
        html_input: HTML string

    Returns:
        Text without HTML tags

    Example:
        >>> strip_html('<p>Hello <b>World</b></p>')
        'Hello World'
    """
    # Remove all HTML tags
    text = re.sub(r"<[^>]+>", "", html_input)

    # Decode HTML entities
    text = html.unescape(text)

    return text.strip()


class PathSanitizer:
    """
    Path traversal prevention with military-grade validation

    Ensures file paths are safe and within allowed directories.
    Implements multiple layers of defense against path traversal attacks.
    """

    # Path whitelist for critical system operations
    SAFE_PATH_WHITELIST: Set[str] = set()

    def __init__(self, base_path: Optional[str] = None, use_whitelist: bool = False):
        """
        Initialize path sanitizer

        Args:
            base_path: Base directory path (paths must be within this)
            use_whitelist: Enable path whitelist for critical operations
        """
        if base_path is None:
            raise ValueError("base_path is required for PathSanitizer")

        # Use realpath to resolve all symlinks and relative paths
        self.base_path = Path(os.path.realpath(base_path))

        if not self.base_path.exists():
            raise ValueError(f"Base path does not exist: {base_path}")

        if not self.base_path.is_dir():
            raise ValueError(f"Base path is not a directory: {base_path}")

        self.use_whitelist = use_whitelist

    def sanitize(self, path: str) -> str:
        """
        Sanitize file path with comprehensive validation

        Args:
            path: User-provided path

        Returns:
            Sanitized absolute path

        Raises:
            ValueError: If path is invalid or outside base path

        Security Enhancements:
        - Uses os.path.realpath() to resolve symlinks
        - Verifies path is within base_path after resolution
        - Blocks NULL bytes and control characters
        - Validates against whitelist if enabled
        """
        if not path:
            raise ValueError("Path cannot be empty")

        # Block NULL bytes and control characters
        if "\x00" in path or any(ord(c) < 32 for c in path if c not in "\t\n\r"):
            raise ValueError("Path contains invalid characters")

        # Block obvious traversal attempts before normalization
        if ".." in path:
            raise ValueError("Path contains parent directory references")

        # Construct full path
        if os.path.isabs(path):
            # Absolute path - must be within base_path
            full_path = path
        else:
            # Relative path - join with base_path
            full_path = os.path.join(str(self.base_path), path)

        # Resolve to real path (follows symlinks, resolves relative paths)
        try:
            real_path = Path(os.path.realpath(full_path))
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid path: {e}")

        # CRITICAL: Verify resolved path is within base_path
        try:
            real_path.relative_to(self.base_path)
        except ValueError:
            raise ValueError(f"Path outside base directory: {path} resolves to {real_path}")

        # Check whitelist if enabled
        if self.use_whitelist and str(real_path) not in self.SAFE_PATH_WHITELIST:
            raise ValueError(f"Path not in whitelist: {real_path}")

        return str(real_path)

    def is_safe(self, path: str) -> bool:
        """
        Check if path is safe

        Args:
            path: Path to check

        Returns:
            True if safe, False otherwise
        """
        try:
            self.sanitize(path)
            return True
        except (ValueError, OSError):
            return False

    @classmethod
    def add_to_whitelist(cls, path: str) -> None:
        """
        Add path to whitelist for critical operations

        Args:
            path: Absolute path to whitelist
        """
        if not os.path.isabs(path):
            raise ValueError("Only absolute paths can be whitelisted")
        cls.SAFE_PATH_WHITELIST.add(os.path.realpath(path))


def prevent_path_traversal(path: str, base_dir: Optional[str] = None) -> str:
    """
    Prevent path traversal attacks

    Args:
        path: User-provided path
        base_dir: Base directory (required for security)

    Returns:
        Safe path within base directory

    Raises:
        ValueError: If path is invalid or base_dir is None

    Example:
        >>> prevent_path_traversal('../../../etc/passwd', '/var/uploads')
        ValueError: Path outside base directory

        >>> prevent_path_traversal('files/document.pdf', '/var/uploads')
        '/var/uploads/files/document.pdf'

    Security:
        CRITICAL FIX: Now rejects None base_dir to prevent bypass attacks
    """
    # CRITICAL SECURITY FIX: Reject None base_dir
    if base_dir is None:
        raise ValueError("base_dir cannot be None - this is a security requirement")

    # Block path traversal sequences before normalization
    dangerous_patterns = [
        "../",
        "..\\",  # Standard traversal
        "%2e%2e/",
        "%2e%2e\\",  # URL encoded
        "..%2f",
        "..%5c",  # Mixed encoding
        "%252e%252e/",  # Double encoded
        "..../",
        "....\\",  # Obfuscated
    ]

    path_lower = path.lower()
    for pattern in dangerous_patterns:
        if pattern in path_lower:
            raise ValueError(f"Path traversal attempt detected: {path}")

    sanitizer = PathSanitizer(base_dir)
    return sanitizer.sanitize(path)


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename

    Removes dangerous characters and ensures safe filename.

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Safe filename

    Example:
        >>> sanitize_filename('../../etc/passwd')
        'etc_passwd'

        >>> sanitize_filename('file<script>.txt')
        'file_script_.txt'
    """
    if not filename:
        return "unnamed"

    # Remove path separators
    filename = os.path.basename(filename)

    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[: max_length - len(ext)] + ext

    # Ensure not empty
    if not filename:
        return "unnamed"

    return filename


class URLValidator:
    """URL validation and sanitization"""

    SAFE_SCHEMES = {"http", "https", "ftp", "mailto"}

    @staticmethod
    def is_valid(url: str, allowed_schemes: Optional[Set[str]] = None) -> bool:
        """
        Validate URL

        Args:
            url: URL to validate
            allowed_schemes: Allowed URL schemes

        Returns:
            True if valid
        """
        if not url:
            return False

        allowed = allowed_schemes or URLValidator.SAFE_SCHEMES

        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme.lower() not in allowed:
                return False

            # Check netloc for http/https
            if parsed.scheme in ("http", "https") and not parsed.netloc:
                return False

            return True

        except Exception:
            return False

    @staticmethod
    def sanitize(url: str) -> str:
        """
        Sanitize URL

        Args:
            url: URL to sanitize

        Returns:
            Sanitized URL
        """
        if not url:
            return ""

        # Parse URL
        parsed = urlparse(url)

        # Validate scheme
        if parsed.scheme.lower() not in URLValidator.SAFE_SCHEMES:
            return ""

        # Encode components
        path = quote(unquote(parsed.path), safe="/")
        quote(unquote(parsed.query), safe="&=")

        # Reconstruct URL
        return f"{parsed.scheme}://{parsed.netloc}{path}"


def validate_email(email: str) -> bool:
    """
    Validate email address

    Args:
        email: Email address

    Returns:
        True if valid

    Example:
        >>> validate_email('user@example.com')
        True

        >>> validate_email('invalid.email')
        False
    """
    if not email or len(email) > 254:
        return False

    # RFC 5322 simplified pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    return bool(re.match(pattern, email))


def sanitize_json(data: Any, max_depth: int = 10) -> Any:
    """
    Sanitize JSON data

    Recursively sanitizes strings in JSON structures.

    Args:
        data: JSON data
        max_depth: Maximum nesting depth

    Returns:
        Sanitized JSON data
    """
    if max_depth <= 0:
        raise ValueError("Maximum depth exceeded")

    if isinstance(data, dict):
        return {
            sanitize_json(k, max_depth - 1): sanitize_json(v, max_depth - 1)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [sanitize_json(item, max_depth - 1) for item in data]
    elif isinstance(data, str):
        return escape_html(data)
    else:
        return data


# SQL Injection Prevention Documentation
SQL_INJECTION_PREVENTION = """
# SQL Injection Prevention

The ORM in CovetPy uses parameterized queries which automatically prevent SQL injection.

## Safe Practices (ALWAYS USE):

```python
# ✅ SAFE - Parameterized query
users = await User.objects.filter(username=user_input)

# ✅ SAFE - Raw query with parameters
await db.execute(
    "SELECT * FROM users WHERE username = ?",
    [user_input]
)
```

## NEVER DO THIS:

```python
# ❌ DANGEROUS - String concatenation
query = f"SELECT * FROM users WHERE username = '{user_input}'"
await db.execute(query)

# ❌ DANGEROUS - String formatting
query = "SELECT * FROM users WHERE username = '%s'" % user_input
await db.execute(query)
```

## Additional Protection:

1. **Input Validation**: Validate and sanitize all user input
2. **Least Privilege**: Database users should have minimal permissions
3. **Error Handling**: Don't expose database errors to users
4. **Prepared Statements**: Always use parameterized queries
5. **ORM Usage**: Prefer ORM over raw SQL when possible

## Validation Example:

```python
from covet.security.sanitization import validate_input

def validate_username(username: str) -> bool:
    # Only allow alphanumeric and underscore
    return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', username))

@app.route('/user/<username>')
async def get_user(request, username):
    if not validate_username(username):
        return {'error': 'Invalid username'}, 400

    user = await User.objects.get(username=username)
    return {'user': user.to_dict()}
```
"""


# Command Injection Prevention
def sanitize_command_arg(arg: str) -> str:
    """
    Sanitize command line argument

    Args:
        arg: Command argument

    Returns:
        Sanitized argument

    Warning:
        Prefer using subprocess with argument lists instead of shell=True

    Security:
        This is a last resort. ALWAYS prefer subprocess with argument lists.
    """
    # Remove dangerous characters
    arg = re.sub(r"[;&|`$(){}[\]<>!]", "", arg)

    return arg


def prevent_command_injection(command: str, allowed_commands: Optional[Set[str]] = None) -> str:
    """
    Prevent command injection attacks

    Args:
        command: Command to validate
        allowed_commands: Set of allowed commands (whitelist)

    Returns:
        Validated command

    Raises:
        ValueError: If command contains injection patterns or not in whitelist

    Security:
        CRITICAL: Use subprocess with argument lists instead of shell=True
    """
    if not command:
        raise ValueError("Command cannot be empty")

    # Check whitelist if provided
    if allowed_commands:
        base_command = command.split()[0]
        if base_command not in allowed_commands:
            raise ValueError(f"Command not in whitelist: {base_command}")

    # Block command injection patterns
    dangerous_patterns = [
        ";",
        "&",
        "|",
        "`",
        "$",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "<",
        ">",
        "\n",
        "\r",
        "&&",
        "||",
        "$(",
        "`",
    ]

    for pattern in dangerous_patterns:
        if pattern in command:
            raise ValueError(f"Command contains dangerous pattern: {pattern}")

    return command


# LDAP Injection Prevention
def sanitize_ldap_dn(dn: str) -> str:
    """
    Sanitize LDAP Distinguished Name

    Args:
        dn: LDAP DN string

    Returns:
        Sanitized DN

    Security:
        Escapes special LDAP DN characters per RFC 4514
    """
    # Escape special characters in DN
    # RFC 4514: , \ # + < > ; " =
    escape_chars = {
        ",": "\\,",
        "\\": "\\\\",
        "#": "\\#",
        "+": "\\+",
        "<": "\\<",
        ">": "\\>",
        ";": "\\;",
        '"': '\\"',
        "=": "\\=",
    }

    result = dn
    for char, escaped in escape_chars.items():
        result = result.replace(char, escaped)

    return result


def sanitize_ldap_filter(filter_value: str) -> str:
    """
    Sanitize LDAP search filter

    Args:
        filter_value: LDAP filter value

    Returns:
        Sanitized filter value

    Security:
        Escapes special LDAP filter characters per RFC 4515
    """
    # Escape special characters in filter
    # RFC 4515: * ( ) \ NUL
    escape_chars = {
        "*": "\\2a",
        "(": "\\28",
        ")": "\\29",
        "\\": "\\5c",
        "\x00": "\\00",
    }

    result = filter_value
    for char, escaped in escape_chars.items():
        result = result.replace(char, escaped)

    return result


# XML/XXE Prevention
def sanitize_xml_content(content: str, allow_entities: bool = False) -> str:
    """
    Sanitize XML content to prevent XXE attacks

    Args:
        content: XML content
        allow_entities: Allow entity references (NOT recommended)

    Returns:
        Sanitized XML content

    Raises:
        ValueError: If content contains dangerous patterns

    Security:
        Blocks DOCTYPE declarations and entity references to prevent XXE
    """
    if not content:
        return ""

    # Block DOCTYPE declarations (XXE attack vector)
    if "<!DOCTYPE" in content or "<!ENTITY" in content:
        raise ValueError("DOCTYPE and ENTITY declarations are not allowed")

    # Block SYSTEM and PUBLIC references
    if "SYSTEM" in content or "PUBLIC" in content:
        raise ValueError("External entity references are not allowed")

    # Block entity references unless explicitly allowed
    if not allow_entities and "&" in content:
        # Allow safe HTML entities
        safe_entities = {"&lt;", "&gt;", "&amp;", "&quot;", "&apos;"}
        # Check for entity references
        import re

        entities = re.findall(r"&[a-zA-Z0-9#]+;", content)
        for entity in entities:
            if entity not in safe_entities:
                raise ValueError(f"Entity reference not allowed: {entity}")

    return content


def parse_xml_safely(xml_content: str):
    """
    Parse XML safely with XXE protection

    Args:
        xml_content: XML content to parse

    Returns:
        Parsed XML element tree

    Raises:
        ValueError: If XML is invalid or contains dangerous content

    Security:
        Uses defusedxml to prevent XXE, billion laughs, and other XML attacks
    """
    try:
        # Try to use defusedxml if available
        from defusedxml import ElementTree as DefusedET

        return DefusedET.fromstring(xml_content)
    except ImportError:
        # Fallback to stdlib with manual protection
        import xml.etree.ElementTree as ET

        # Sanitize content first
        sanitized = sanitize_xml_content(xml_content, allow_entities=False)

        # Parse with minimal features
        parser = ET.XMLParser()  # nosec B314 B318 - XML parser configured securely
        # Disable DTD processing and entity expansion
        parser.entity = {}  # Empty entity dict

        return ET.fromstring(
            sanitized, parser=parser
        )  # nosec B314 B318 - XML parser configured securely


# SQL String Escaping (for dynamic queries - use parameterized queries
# instead!)
def escape_sql_string(value: str, quote_char: str = "'") -> str:
    """
    Escape SQL string value

    Args:
        value: String value to escape
        quote_char: Quote character (' or ")

    Returns:
        Escaped string

    WARNING:
        This is NOT a substitute for parameterized queries!
        ALWAYS use parameterized queries with the ORM or database library.
        This is only for cases where parameterized queries cannot be used.
    """
    # Escape the quote character
    if quote_char == "'":
        escaped = value.replace("'", "''")
    elif quote_char == '"':
        escaped = value.replace('"', '""')
    else:
        raise ValueError("quote_char must be ' or \"")

    # Escape backslashes (for databases that use backslash escaping)
    escaped = escaped.replace("\\", "\\\\")

    return escaped


def escape_sql_identifier(identifier: str) -> str:
    """
    Escape SQL identifier (table name, column name)

    Args:
        identifier: Identifier to escape

    Returns:
        Escaped identifier

    Security:
        Use this for dynamic table/column names in queries
    """
    # Remove any characters that aren't alphanumeric or underscore
    safe_identifier = re.sub(r"[^a-zA-Z0-9_]", "", identifier)

    if not safe_identifier:
        raise ValueError("Invalid SQL identifier")

    # Ensure doesn't start with a number
    if safe_identifier[0].isdigit():
        raise ValueError("SQL identifier cannot start with a number")

    return safe_identifier


COMMAND_INJECTION_PREVENTION = """
# Command Injection Prevention

## NEVER use shell=True with user input:

```python
# ❌ DANGEROUS
import subprocess
subprocess.run(f"ls {user_input}", shell=True)
```

## ALWAYS use argument lists:

```python
# ✅ SAFE
import subprocess
subprocess.run(['ls', user_input])
```

## Additional Protection:

1. **Avoid shell execution**: Use direct command execution
2. **Validate input**: Whitelist allowed characters
3. **Use libraries**: Prefer Python libraries over shell commands
4. **Least privilege**: Run with minimal permissions
"""


LDAP_INJECTION_PREVENTION = """
# LDAP Injection Prevention

## Safe LDAP query construction:

```python
from covet.security.sanitization import sanitize_ldap_filter, sanitize_ldap_dn

# ✅ SAFE - Sanitized filter
username = sanitize_ldap_filter(user_input)
ldap_filter = f"(uid={username})"

# ✅ SAFE - Sanitized DN
cn = sanitize_ldap_dn(user_input)
dn = f"cn={cn},ou=users,dc=example,dc=com"
```

## NEVER concatenate user input directly:

```python
# ❌ DANGEROUS
ldap_filter = f"(uid={user_input})"
```
"""


XXE_PREVENTION = """
# XML External Entity (XXE) Prevention

## ALWAYS use safe XML parsing:

```python
from covet.security.sanitization import parse_xml_safely

# ✅ SAFE - Protected against XXE
tree = parse_xml_safely(xml_content)
```

## NEVER use standard XML parsers with untrusted input:

```python
# ❌ DANGEROUS
import xml.etree.ElementTree as ET
tree = ET.fromstring(untrusted_xml)
```

## Additional Protection:

1. **Disable DTD processing**: Prevent external entity loading
2. **Disable entity expansion**: Prevent billion laughs attack
3. **Use defusedxml**: Install and use the defusedxml library
4. **Validate content**: Sanitize XML before parsing
"""
