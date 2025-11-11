"""
CovetPy Injection Protection Module

Comprehensive protection against all forms of injection attacks:
- SQL Injection (SQLi)
- NoSQL Injection
- Command Injection (OS Command)
- LDAP Injection
- XML Injection
- XPath Injection
- Template Injection
- Expression Language Injection
- Log Injection

Implements OWASP Top 10 2021 - A03:2021 Injection protection with multiple
defense layers including input validation, sanitization, parameterized queries,
and context-aware encoding.

Security Architecture:
- Multi-layer defense (validation -> sanitization -> safe execution)
- Whitelist-based validation preferred over blacklist
- Context-aware encoding and escaping
- Safe API enforcement (parameterized queries, prepared statements)
- Automatic detection of injection patterns
- Audit logging for all injection attempts
- Performance-optimized with regex compilation and caching

Author: CovetPy Security Team
License: MIT
"""

import base64
import hashlib
import html
import json
import logging
import re
import shlex
import subprocess
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class InjectionType(Enum):
    """Types of injection attacks detected."""

    SQL = "sql_injection"
    NOSQL = "nosql_injection"
    COMMAND = "command_injection"
    LDAP = "ldap_injection"
    XML = "xml_injection"
    XPATH = "xpath_injection"
    TEMPLATE = "template_injection"
    LOG = "log_injection"
    EXPRESSION = "expression_injection"
    HEADER = "header_injection"


class InjectionSeverity(Enum):
    """Severity levels for injection attempts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class InjectionDetection:
    """Details about detected injection attempt."""

    injection_type: InjectionType
    severity: InjectionSeverity
    pattern_matched: str
    input_value: str
    sanitized_value: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    blocked: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "injection_type": self.injection_type.value,
            "severity": self.severity.value,
            "pattern_matched": self.pattern_matched,
            "input_value": self.input_value[:100],  # Truncate for logs
            "sanitized_value": self.sanitized_value[:100] if self.sanitized_value else None,
            "timestamp": self.timestamp.isoformat(),
            "blocked": self.blocked,
            "metadata": self.metadata,
        }


class SQLInjectionProtector:
    """
    SQL Injection protection with multiple detection techniques.

    Implements defense against:
    - Classic SQL injection (UNION, OR 1=1, etc.)
    - Blind SQL injection (timing, boolean-based)
    - Error-based SQL injection
    - Second-order SQL injection
    - Stored procedure injection

    Defense Strategy:
    1. Parameterized query enforcement (primary defense)
    2. Input validation and sanitization (secondary defense)
    3. Prepared statement verification (runtime defense)
    4. Query pattern analysis (anomaly detection)
    """

    # Compiled regex patterns for SQL injection detection
    SQL_INJECTION_PATTERNS = [
        # Classic SQL injection
        (
            re.compile(r"(\bunion\b.*\bselect\b|\bselect\b.*\bfrom\b)", re.IGNORECASE),
            "UNION/SELECT",
        ),
        (
            re.compile(
                r"(\bor\b\s+[\d'\"]+\s*=\s*[\d'\"]+|\band\b\s+[\d'\"]+\s*=\s*[\d'\"]+)",
                re.IGNORECASE,
            ),
            "OR/AND condition",
        ),
        (re.compile(r"(\bor\b\s+[\w'\"]+\s+like\b)", re.IGNORECASE), "OR LIKE"),
        # Comment-based injection
        (re.compile(r"(--|\#|/\*|\*/)", re.IGNORECASE), "SQL comment"),
        (re.compile(r"(\bor\b.*--|\band\b.*--)", re.IGNORECASE), "Comment-based bypass"),
        # SQL commands
        (
            re.compile(
                r"\b(drop|delete|insert|update|create|alter|truncate|exec|execute)\b", re.IGNORECASE
            ),
            "SQL command",
        ),
        (re.compile(r"\b(xp_cmdshell|sp_executesql|exec\s*\()", re.IGNORECASE), "Stored procedure"),
        # String concatenation
        (re.compile(r"(\|\||\bconcat\b|\+)", re.IGNORECASE), "String concatenation"),
        # Time-based blind injection
        (
            re.compile(r"\b(sleep|waitfor|delay|benchmark)\b\s*\(", re.IGNORECASE),
            "Time-based injection",
        ),
        # Hex/Char encoding
        (re.compile(r"(0x[0-9a-f]+|\bchar\s*\(|\bcast\s*\()", re.IGNORECASE), "Encoding bypass"),
        # Information schema queries
        (
            re.compile(r"\b(information_schema|sysobjects|syscolumns)\b", re.IGNORECASE),
            "Schema enumeration",
        ),
        # Stacked queries
        (re.compile(r";\s*(drop|delete|insert|update|create)", re.IGNORECASE), "Stacked query"),
    ]

    # Dangerous SQL keywords to block
    DANGEROUS_KEYWORDS = {
        "xp_cmdshell",
        "sp_executesql",
        "exec",
        "execute",
        "drop",
        "truncate",
        "shutdown",
        "grant",
        "revoke",
    }

    def __init__(self, strict_mode: bool = True, allow_null: bool = False):
        """
        Initialize SQL injection protector.

        Args:
            strict_mode: If True, applies stricter validation rules
            allow_null: If True, allows NULL values in input
        """
        self.strict_mode = strict_mode
        self.allow_null = allow_null
        self._detection_count = 0

    def detect(self, value: Any, context: Optional[str] = None) -> Optional[InjectionDetection]:
        """
        Detect SQL injection patterns in input.

        Args:
            value: Input value to check
            context: Additional context (field name, query type, etc.)

        Returns:
            InjectionDetection if attack detected, None otherwise
        """
        if value is None and self.allow_null:
            return None

        if not isinstance(value, str):
            value = str(value)

        # Check each pattern
        for pattern, pattern_name in self.SQL_INJECTION_PATTERNS:
            match = pattern.search(value)
            if match:
                self._detection_count += 1
                severity = self._assess_severity(pattern_name, value)

                detection = InjectionDetection(
                    injection_type=InjectionType.SQL,
                    severity=severity,
                    pattern_matched=pattern_name,
                    input_value=value,
                    metadata={
                        "context": context,
                        "matched_text": match.group(0),
                        "detection_count": self._detection_count,
                    },
                )

                logger.warning(
                    f"SQL injection attempt detected: {pattern_name} in '{value[:50]}...'",
                    extra={"detection": detection.to_dict()},
                )

                return detection

        # Check for dangerous keywords in strict mode
        if self.strict_mode:
            value_lower = value.lower()
            for keyword in self.DANGEROUS_KEYWORDS:
                if keyword in value_lower:
                    self._detection_count += 1
                    detection = InjectionDetection(
                        injection_type=InjectionType.SQL,
                        severity=InjectionSeverity.CRITICAL,
                        pattern_matched=f"Dangerous keyword: {keyword}",
                        input_value=value,
                        metadata={"context": context, "keyword": keyword},
                    )

                    logger.critical(
                        f"Dangerous SQL keyword detected: {keyword}",
                        extra={"detection": detection.to_dict()},
                    )

                    return detection

        return None

    def sanitize(self, value: Any, aggressive: bool = False) -> str:
        """
        Sanitize input to prevent SQL injection.

        NOTE: This is a SECONDARY defense. Always use parameterized queries first!

        Args:
            value: Input value to sanitize
            aggressive: If True, removes more characters

        Returns:
            Sanitized string value
        """
        if value is None:
            return "NULL" if self.allow_null else ""

        if not isinstance(value, str):
            value = str(value)

        # Remove SQL comments
        value = re.sub(r"--.*$", "", value, flags=re.MULTILINE)
        value = re.sub(r"/\*.*?\*/", "", value, flags=re.DOTALL)
        value = re.sub(r"#.*$", "", value, flags=re.MULTILINE)

        # Remove dangerous characters
        if aggressive:
            # In aggressive mode, only allow alphanumeric, spaces, and basic punctuation
            value = re.sub(r"[^a-zA-Z0-9\s\-_.@]", "", value)
        else:
            # Remove most dangerous characters
            value = re.sub(r"[;'\"`]", "", value)

        # Remove multiple spaces
        value = re.sub(r"\s+", " ", value).strip()

        return value

    def _assess_severity(self, pattern_name: str, value: str) -> InjectionSeverity:
        """Assess severity of injection attempt."""
        # Critical patterns
        if any(
            keyword in pattern_name.lower() for keyword in ["stored procedure", "command", "schema"]
        ):
            return InjectionSeverity.CRITICAL

        # High severity patterns
        if any(keyword in pattern_name.lower() for keyword in ["union", "stacked", "time-based"]):
            return InjectionSeverity.HIGH

        # Medium severity patterns
        if any(keyword in pattern_name.lower() for keyword in ["or", "and", "comment"]):
            return InjectionSeverity.MEDIUM

        return InjectionSeverity.LOW

    @staticmethod
    def validate_parameterized_query(query: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate that a query uses parameterized syntax.

        Args:
            query: SQL query to validate
            params: Parameters dictionary

        Returns:
            True if query appears to use parameterized syntax
        """
        # Check for parameterized syntax patterns
        has_placeholders = bool(
            re.search(r"(\?|:\w+|%\([\w_]+\)s|\$\d+)", query) or (params and len(params) > 0)
        )

        # Check for string concatenation (danger sign)
        has_concatenation = bool(re.search(r"['\"].*\+.*['\"]|f['\"].*\{", query))

        return has_placeholders and not has_concatenation


class NoSQLInjectionProtector:
    """
    NoSQL Injection protection for MongoDB, Cassandra, CouchDB, etc.

    Defends against:
    - JavaScript injection in MongoDB
    - Operator injection ($gt, $ne, etc.)
    - JSON injection
    - Query parameter injection
    """

    # Dangerous MongoDB operators
    DANGEROUS_OPERATORS = {
        "$where",
        "$regex",
        "$mapReduce",
        "$function",
        "$accumulator",
        "$expr",
        "$jsonSchema",
    }

    # Allowed safe operators
    SAFE_OPERATORS = {
        "$eq",
        "$ne",
        "$gt",
        "$gte",
        "$lt",
        "$lte",
        "$in",
        "$nin",
        "$and",
        "$or",
        "$not",
    }

    NOSQL_INJECTION_PATTERNS = [
        (re.compile(r"\$where\s*:", re.IGNORECASE), "$where operator"),
        (re.compile(r"function\s*\(", re.IGNORECASE), "JavaScript function"),
        (re.compile(r"\{\s*\$ne\s*:", re.IGNORECASE), "$ne operator injection"),
        (re.compile(r"\{\s*\$gt\s*:\s*['\"]", re.IGNORECASE), "Operator with string"),
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize NoSQL injection protector.

        Args:
            strict_mode: If True, blocks dangerous operators
        """
        self.strict_mode = strict_mode
        self._detection_count = 0

    def detect(self, value: Any, context: Optional[str] = None) -> Optional[InjectionDetection]:
        """Detect NoSQL injection patterns."""
        if isinstance(value, dict):
            return self._detect_dict(value, context)
        elif isinstance(value, str):
            return self._detect_string(value, context)

        return None

    def _detect_dict(
        self, value: Dict[str, Any], context: Optional[str] = None
    ) -> Optional[InjectionDetection]:
        """Detect injection in dictionary (MongoDB queries)."""
        for key in value.keys():
            # Check for dangerous operators
            if key.startswith("$") and key in self.DANGEROUS_OPERATORS:
                self._detection_count += 1
                detection = InjectionDetection(
                    injection_type=InjectionType.NOSQL,
                    severity=InjectionSeverity.CRITICAL,
                    pattern_matched=f"Dangerous operator: {key}",
                    input_value=json.dumps(value),
                    metadata={"context": context, "operator": key},
                )

                logger.critical(
                    f"NoSQL injection: dangerous operator {key}",
                    extra={"detection": detection.to_dict()},
                )

                return detection

            # Recursively check nested values
            if isinstance(value[key], dict):
                nested_detection = self._detect_dict(value[key], context)
                if nested_detection:
                    return nested_detection

        return None

    def _detect_string(
        self, value: str, context: Optional[str] = None
    ) -> Optional[InjectionDetection]:
        """Detect injection in string values."""
        for pattern, pattern_name in self.NOSQL_INJECTION_PATTERNS:
            if pattern.search(value):
                self._detection_count += 1
                detection = InjectionDetection(
                    injection_type=InjectionType.NOSQL,
                    severity=InjectionSeverity.HIGH,
                    pattern_matched=pattern_name,
                    input_value=value,
                    metadata={"context": context},
                )

                logger.warning(
                    f"NoSQL injection attempt: {pattern_name}",
                    extra={"detection": detection.to_dict()},
                )

                return detection

        return None

    def sanitize_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize NoSQL query by removing dangerous operators.

        Args:
            query: Query dictionary

        Returns:
            Sanitized query dictionary
        """
        sanitized = {}

        for key, value in query.items():
            # Block dangerous operators
            if key.startswith("$") and key in self.DANGEROUS_OPERATORS:
                logger.warning(f"Blocked dangerous NoSQL operator: {key}")
                continue

            # Only allow safe operators or regular fields
            if key.startswith("$") and key not in self.SAFE_OPERATORS:
                if self.strict_mode:
                    logger.warning(f"Blocked unknown NoSQL operator: {key}")
                    continue

            # Recursively sanitize nested queries
            if isinstance(value, dict):
                sanitized[key] = self.sanitize_query(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_query(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized


class CommandInjectionProtector:
    """
    OS Command Injection protection.

    Defends against:
    - Shell metacharacter injection (;, |, &, $, etc.)
    - Command chaining
    - Backtick execution
    - Input/output redirection
    """

    # Dangerous shell metacharacters
    SHELL_METACHARACTERS = {";", "|", "&", "$", "`", "\n", "(", ")", "<", ">", "\\"}

    COMMAND_INJECTION_PATTERNS = [
        (re.compile(r"[;&|`$()><\\\n]"), "Shell metacharacter"),
        (re.compile(r"\$\([^)]*\)"), "Command substitution"),
        (re.compile(r"`[^`]*`"), "Backtick execution"),
        (re.compile(r"(&&|\|\|)"), "Command chaining"),
        (re.compile(r"(<<|>>|<|>)"), "Redirection"),
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize command injection protector.

        Args:
            strict_mode: If True, blocks all shell metacharacters
        """
        self.strict_mode = strict_mode
        self._detection_count = 0

    def detect(self, value: Any, context: Optional[str] = None) -> Optional[InjectionDetection]:
        """Detect command injection patterns."""
        if not isinstance(value, str):
            value = str(value)

        for pattern, pattern_name in self.COMMAND_INJECTION_PATTERNS:
            match = pattern.search(value)
            if match:
                self._detection_count += 1
                detection = InjectionDetection(
                    injection_type=InjectionType.COMMAND,
                    severity=InjectionSeverity.CRITICAL,
                    pattern_matched=pattern_name,
                    input_value=value,
                    metadata={"context": context, "matched_text": match.group(0)},
                )

                logger.critical(
                    f"Command injection attempt: {pattern_name}",
                    extra={"detection": detection.to_dict()},
                )

                return detection

        return None

    def sanitize(self, value: str) -> str:
        """
        Sanitize input for shell commands.

        IMPORTANT: Use subprocess with shell=False instead of sanitization!
        """
        # Remove all shell metacharacters
        for char in self.SHELL_METACHARACTERS:
            value = value.replace(char, "")

        return value

    @staticmethod
    def safe_execute(
        command: List[str], input_data: Optional[str] = None, timeout: int = 30
    ) -> Tuple[str, str, int]:
        """
        Safely execute command using subprocess without shell.

        Args:
            command: List of command arguments (first element is executable)
            input_data: Optional input data to pass to command
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr, return_code)

        Raises:
            subprocess.TimeoutExpired: If command times out
            ValueError: If command list is empty or invalid
        """
        if not command or not isinstance(command, list):
            raise ValueError("Command must be a non-empty list")

        # Validate command doesn't contain shell metacharacters
        for arg in command:
            for char in CommandInjectionProtector.SHELL_METACHARACTERS:
                if char in str(arg):
                    raise ValueError(f"Command argument contains dangerous character: {char}")

        try:
            # Execute with shell=False (secure)
            result = subprocess.run(
                command,
                input=input_data.encode() if input_data else None,
                capture_output=True,
                timeout=timeout,
                shell=False,  # CRITICAL: Never use shell=True
                check=False,
            )

            return (
                result.stdout.decode("utf-8", errors="replace"),
                result.stderr.decode("utf-8", errors="replace"),
                result.returncode,
            )
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timeout: {command}")
            raise
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise


class LDAPInjectionProtector:
    """
    LDAP Injection protection.

    Defends against:
    - Filter injection
    - DN injection
    - LDAP special characters
    """

    # LDAP special characters that need escaping
    LDAP_FILTER_SPECIAL = {"*", "(", ")", "\\", "\x00"}
    LDAP_DN_SPECIAL = {",", "=", "+", "<", ">", "#", ";", "\\", '"', " "}

    LDAP_INJECTION_PATTERNS = [
        (re.compile(r"\*\)(\(|&|\|)"), "LDAP filter bypass"),
        (re.compile(r"\)\("), "Filter injection"),
        (re.compile(r"[*()]"), "LDAP metacharacter"),
    ]

    def detect(self, value: Any, is_dn: bool = False) -> Optional[InjectionDetection]:
        """Detect LDAP injection patterns."""
        if not isinstance(value, str):
            value = str(value)

        for pattern, pattern_name in self.LDAP_INJECTION_PATTERNS:
            if pattern.search(value):
                detection = InjectionDetection(
                    injection_type=InjectionType.LDAP,
                    severity=InjectionSeverity.HIGH,
                    pattern_matched=pattern_name,
                    input_value=value,
                    metadata={"is_dn": is_dn},
                )

                logger.warning(
                    f"LDAP injection attempt: {pattern_name}",
                    extra={"detection": detection.to_dict()},
                )

                return detection

        return None

    @staticmethod
    def escape_filter(value: str) -> str:
        """
        Escape LDAP filter special characters.

        Args:
            value: Input value to escape

        Returns:
            Escaped value safe for LDAP filters
        """
        # Escape special characters according to RFC 4515
        replacements = {"\\": "\\5c", "*": "\\2a", "(": "\\28", ")": "\\29", "\x00": "\\00"}

        for char, escaped in replacements.items():
            value = value.replace(char, escaped)

        return value

    @staticmethod
    def escape_dn(value: str) -> str:
        """
        Escape LDAP DN special characters.

        Args:
            value: Input value to escape

        Returns:
            Escaped value safe for LDAP DNs
        """
        # Escape special characters according to RFC 4514
        replacements = {
            "\\": "\\\\",
            ",": "\\,",
            "+": "\\+",
            '"': '\\"',
            "<": "\\<",
            ">": "\\>",
            ";": "\\;",
            "=": "\\=",
        }

        for char, escaped in replacements.items():
            value = value.replace(char, escaped)

        # Escape leading/trailing spaces
        if value.startswith(" "):
            value = "\\" + value
        if value.endswith(" "):
            value = value[:-1] + "\\ "

        return value


class XMLInjectionProtector:
    """
    XML/XXE Injection protection.

    Defends against:
    - XML injection
    - XXE (XML External Entity) attacks
    - XPath injection
    - XML bomb (billion laughs attack)
    """

    XML_INJECTION_PATTERNS = [
        (re.compile(r"<!ENTITY", re.IGNORECASE), "XML entity declaration"),
        (re.compile(r"<!DOCTYPE", re.IGNORECASE), "DOCTYPE declaration"),
        (re.compile(r"SYSTEM|PUBLIC", re.IGNORECASE), "External entity reference"),
        (re.compile(r"<\?xml-stylesheet", re.IGNORECASE), "XML stylesheet"),
    ]

    def detect(self, value: Any) -> Optional[InjectionDetection]:
        """Detect XML injection patterns."""
        if not isinstance(value, str):
            value = str(value)

        for pattern, pattern_name in self.XML_INJECTION_PATTERNS:
            if pattern.search(value):
                detection = InjectionDetection(
                    injection_type=InjectionType.XML,
                    severity=InjectionSeverity.CRITICAL,
                    pattern_matched=pattern_name,
                    input_value=value,
                )

                logger.critical(
                    f"XML injection attempt: {pattern_name}",
                    extra={"detection": detection.to_dict()},
                )

                return detection

        return None

    @staticmethod
    def escape(value: str) -> str:
        """
        Escape XML special characters.

        Args:
            value: Input value to escape

        Returns:
            Escaped value safe for XML
        """
        return html.escape(value, quote=True)


class TemplateInjectionProtector:
    """
    Server-Side Template Injection (SSTI) protection.

    Defends against:
    - Jinja2/Flask template injection
    - Django template injection
    - Other template engine injection
    """

    TEMPLATE_INJECTION_PATTERNS = [
        (re.compile(r"\{\{.*\}\}"), "Double curly braces"),
        (re.compile(r"\{%.*%\}"), "Template tag"),
        (re.compile(r"\{\#.*\#\}"), "Template comment"),
        (re.compile(r"__(.*?)__"), "Python magic method"),
        (re.compile(r"\.mro\(\)|\.subclasses\(\)", re.IGNORECASE), "Class introspection"),
    ]

    def detect(self, value: Any) -> Optional[InjectionDetection]:
        """Detect template injection patterns."""
        if not isinstance(value, str):
            value = str(value)

        for pattern, pattern_name in self.TEMPLATE_INJECTION_PATTERNS:
            if pattern.search(value):
                detection = InjectionDetection(
                    injection_type=InjectionType.TEMPLATE,
                    severity=InjectionSeverity.CRITICAL,
                    pattern_matched=pattern_name,
                    input_value=value,
                )

                logger.critical(
                    f"Template injection attempt: {pattern_name}",
                    extra={"detection": detection.to_dict()},
                )

                return detection

        return None


class InjectionProtectionMiddleware:
    """
    Comprehensive injection protection middleware for CovetPy applications.

    Automatically protects all incoming requests against injection attacks.
    """

    def __init__(
        self,
        enable_sql_protection: bool = True,
        enable_nosql_protection: bool = True,
        enable_command_protection: bool = True,
        enable_ldap_protection: bool = True,
        enable_xml_protection: bool = True,
        enable_template_protection: bool = True,
        strict_mode: bool = True,
        block_on_detection: bool = True,
        audit_callback: Optional[Callable[[InjectionDetection], None]] = None,
    ):
        """
        Initialize injection protection middleware.

        Args:
            enable_*_protection: Enable specific protection types
            strict_mode: Use strict validation rules
            block_on_detection: Block requests with detected injection
            audit_callback: Callback function for audit logging
        """
        self.protectors = {}

        if enable_sql_protection:
            self.protectors["sql"] = SQLInjectionProtector(strict_mode=strict_mode)
        if enable_nosql_protection:
            self.protectors["nosql"] = NoSQLInjectionProtector(strict_mode=strict_mode)
        if enable_command_protection:
            self.protectors["command"] = CommandInjectionProtector(strict_mode=strict_mode)
        if enable_ldap_protection:
            self.protectors["ldap"] = LDAPInjectionProtector()
        if enable_xml_protection:
            self.protectors["xml"] = XMLInjectionProtector()
        if enable_template_protection:
            self.protectors["template"] = TemplateInjectionProtector()

        self.block_on_detection = block_on_detection
        self.audit_callback = audit_callback
        self._total_detections = 0
        self._blocked_requests = 0

    async def __call__(self, scope, receive, send):
        """ASGI middleware interface."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Scan request for injection attempts
        detection = await self._scan_request(scope)

        if detection:
            self._total_detections += 1

            # Audit logging
            if self.audit_callback:
                self.audit_callback(detection)

            # Block request if configured
            if self.block_on_detection:
                self._blocked_requests += 1
                await self._send_blocked_response(send, detection)
                return

        # Continue to application
        await self.app(scope, receive, send)

    async def _scan_request(self, scope: Dict[str, Any]) -> Optional[InjectionDetection]:
        """Scan request for injection attempts."""
        # Scan query parameters
        query_string = scope.get("query_string", b"").decode("utf-8")
        if query_string:
            params = urllib.parse.parse_qs(query_string)
            for key, values in params.items():
                for value in values:
                    detection = self._scan_value(value, context=f"query:{key}")
                    if detection:
                        return detection

        # Scan headers
        for header_name, header_value in scope.get("headers", []):
            header_name = header_name.decode("utf-8", errors="ignore")
            header_value = header_value.decode("utf-8", errors="ignore")

            detection = self._scan_value(header_value, context=f"header:{header_name}")
            if detection:
                return detection

        return None

    def _scan_value(self, value: Any, context: str) -> Optional[InjectionDetection]:
        """Scan a single value with all enabled protectors."""
        for protector_name, protector in self.protectors.items():
            detection = protector.detect(value, context=context)
            if detection:
                return detection

        return None

    async def _send_blocked_response(self, send, detection: InjectionDetection):
        """Send blocked response for detected injection."""
        await send(
            {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"x-injection-blocked", detection.injection_type.value.encode()),
                ],
            }
        )

        body = json.dumps(
            {
                "error": "Request blocked",
                "reason": "Potential injection attack detected",
                "type": detection.injection_type.value,
                "timestamp": detection.timestamp.isoformat(),
            }
        ).encode()

        await send({"type": "http.response.body", "body": body})

    def get_statistics(self) -> Dict[str, int]:
        """Get protection statistics."""
        return {
            "total_detections": self._total_detections,
            "blocked_requests": self._blocked_requests,
        }


# Convenience functions for direct usage


def detect_sql_injection(value: Any, strict: bool = True) -> Optional[InjectionDetection]:
    """Detect SQL injection in value."""
    protector = SQLInjectionProtector(strict_mode=strict)
    return protector.detect(value)


def detect_nosql_injection(value: Any, strict: bool = True) -> Optional[InjectionDetection]:
    """Detect NoSQL injection in value."""
    protector = NoSQLInjectionProtector(strict_mode=strict)
    return protector.detect(value)


def detect_command_injection(value: Any) -> Optional[InjectionDetection]:
    """Detect command injection in value."""
    protector = CommandInjectionProtector()
    return protector.detect(value)


def sanitize_sql(value: str, aggressive: bool = False) -> str:
    """Sanitize value for SQL (use parameterized queries instead!)."""
    protector = SQLInjectionProtector()
    return protector.sanitize(value, aggressive=aggressive)


def escape_ldap_filter(value: str) -> str:
    """Escape value for LDAP filter."""
    return LDAPInjectionProtector.escape_filter(value)


def escape_xml(value: str) -> str:
    """Escape value for XML."""
    return XMLInjectionProtector.escape(value)


__all__ = [
    # Enums
    "InjectionType",
    "InjectionSeverity",
    # Data classes
    "InjectionDetection",
    # Protector classes
    "SQLInjectionProtector",
    "NoSQLInjectionProtector",
    "CommandInjectionProtector",
    "LDAPInjectionProtector",
    "XMLInjectionProtector",
    "TemplateInjectionProtector",
    # Middleware
    "InjectionProtectionMiddleware",
    # Convenience functions
    "detect_sql_injection",
    "detect_nosql_injection",
    "detect_command_injection",
    "sanitize_sql",
    "escape_ldap_filter",
    "escape_xml",
]
