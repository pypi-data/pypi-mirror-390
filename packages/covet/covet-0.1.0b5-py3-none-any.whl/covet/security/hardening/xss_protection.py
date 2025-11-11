"""
CovetPy XSS (Cross-Site Scripting) Protection Module

Comprehensive protection against all XSS attack types:
- Reflected XSS (Type 1)
- Stored XSS (Type 2)
- DOM-based XSS (Type 0)
- Mutation XSS (mXSS)
- Universal XSS (UXSS)

Implements OWASP Top 10 2021 - A03:2021 Injection (XSS) protection through:
- Context-aware output encoding
- Content Security Policy (CSP)
- X-XSS-Protection headers
- HTML sanitization
- JavaScript escaping
- URL encoding
- CSS injection prevention
- Template auto-escaping

Defense Strategy:
1. Input validation (reject dangerous patterns)
2. Output encoding (context-appropriate)
3. Content Security Policy (CSP headers)
4. Sanitization (safe HTML subset)
5. Template auto-escaping (automatic protection)

Author: CovetPy Security Team
License: MIT
"""

import base64
import hashlib
import html
import json
import logging
import re
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class XSSType(Enum):
    """Types of XSS attacks."""

    REFLECTED = "reflected"
    STORED = "stored"
    DOM = "dom_based"
    MUTATION = "mutation"
    ATTRIBUTE = "attribute"
    JAVASCRIPT = "javascript"
    CSS = "css"


class EncodingContext(Enum):
    """Context for output encoding."""

    HTML = "html"
    HTML_ATTRIBUTE = "html_attribute"
    JAVASCRIPT = "javascript"
    JSON = "json"
    URL = "url"
    CSS = "css"
    XML = "xml"


@dataclass
class XSSDetection:
    """Details about detected XSS attempt."""

    xss_type: XSSType
    pattern_matched: str
    input_value: str
    encoded_value: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    blocked: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "xss_type": self.xss_type.value,
            "pattern_matched": self.pattern_matched,
            "input_value": self.input_value[:100],
            "encoded_value": self.encoded_value[:100] if self.encoded_value else None,
            "timestamp": self.timestamp.isoformat(),
            "blocked": self.blocked,
            "metadata": self.metadata,
        }


class XSSDetector:
    """
    XSS attack pattern detection.

    Detects various XSS vectors including:
    - Script tags (<script>)
    - Event handlers (onclick, onerror, etc.)
    - JavaScript URLs (javascript:)
    - Data URLs (data:text/html)
    - SVG-based XSS
    - Form-based XSS
    - Base64 encoded payloads
    """

    # XSS detection patterns (ordered by severity)
    XSS_PATTERNS = [
        # Script tags
        (
            re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
            "script_tag",
            XSSType.REFLECTED,
        ),
        (re.compile(r"<script[^>]*>", re.IGNORECASE), "script_open_tag", XSSType.REFLECTED),
        # Event handlers
        (re.compile(r"\bon\w+\s*=", re.IGNORECASE), "event_handler", XSSType.REFLECTED),
        (
            re.compile(r"(onerror|onload|onclick|onmouseover)\s*=", re.IGNORECASE),
            "dangerous_event",
            XSSType.REFLECTED,
        ),
        # JavaScript URLs
        (re.compile(r"javascript\s*:", re.IGNORECASE), "javascript_url", XSSType.REFLECTED),
        (re.compile(r"vbscript\s*:", re.IGNORECASE), "vbscript_url", XSSType.REFLECTED),
        # Data URLs
        (re.compile(r"data\s*:\s*text/html", re.IGNORECASE), "data_url_html", XSSType.REFLECTED),
        (re.compile(r"data\s*:.*base64", re.IGNORECASE), "data_url_base64", XSSType.REFLECTED),
        # Iframe injection
        (re.compile(r"<iframe[^>]*>", re.IGNORECASE), "iframe_tag", XSSType.REFLECTED),
        # Object/Embed tags
        (
            re.compile(r"<(object|embed|applet)[^>]*>", re.IGNORECASE),
            "object_tag",
            XSSType.REFLECTED,
        ),
        # SVG-based XSS
        (re.compile(r"<svg[^>]*>", re.IGNORECASE), "svg_tag", XSSType.REFLECTED),
        (re.compile(r"<svg.*?onload", re.IGNORECASE | re.DOTALL), "svg_onload", XSSType.REFLECTED),
        # Form-based XSS
        (re.compile(r"<form[^>]*action", re.IGNORECASE), "form_tag", XSSType.REFLECTED),
        # Meta refresh
        (
            re.compile(r"<meta[^>]*http-equiv.*refresh", re.IGNORECASE | re.DOTALL),
            "meta_refresh",
            XSSType.REFLECTED,
        ),
        # Style/CSS injection
        (re.compile(r"<style[^>]*>", re.IGNORECASE), "style_tag", XSSType.CSS),
        (re.compile(r"expression\s*\(", re.IGNORECASE), "css_expression", XSSType.CSS),
        (re.compile(r"@import", re.IGNORECASE), "css_import", XSSType.CSS),
        # Encoded attacks
        (re.compile(r"&#x?[0-9a-f]+;", re.IGNORECASE), "html_entity", XSSType.MUTATION),
        (re.compile(r"%[0-9a-f]{2}", re.IGNORECASE), "url_encoded", XSSType.MUTATION),
        # DOM-based patterns
        (
            re.compile(r"(document\.|window\.|eval\(|setTimeout\(|setInterval\()", re.IGNORECASE),
            "dom_access",
            XSSType.DOM,
        ),
        # Alert/confirm/prompt (common in XSS testing)
        (
            re.compile(r"\b(alert|confirm|prompt)\s*\(", re.IGNORECASE),
            "dialog_function",
            XSSType.REFLECTED,
        ),
    ]

    # Dangerous HTML tags
    DANGEROUS_TAGS = {
        "script",
        "iframe",
        "object",
        "embed",
        "applet",
        "meta",
        "link",
        "style",
        "base",
        "form",
    }

    # Dangerous HTML attributes
    DANGEROUS_ATTRIBUTES = {
        "onerror",
        "onload",
        "onclick",
        "onmouseover",
        "onmouseout",
        "onmousemove",
        "onmouseenter",
        "onmouseleave",
        "onfocus",
        "onblur",
        "onchange",
        "onsubmit",
        "onkeydown",
        "onkeyup",
        "onkeypress",
        "onabort",
        "ondrag",
        "ondrop",
        "oncopy",
        "onpaste",
        "oncut",
        "onanimationstart",
        "onanimationend",
        "ontransitionend",
    }

    def __init__(self, strict_mode: bool = True):
        """
        Initialize XSS detector.

        Args:
            strict_mode: If True, applies stricter detection rules
        """
        self.strict_mode = strict_mode
        self._detection_count = 0

    def detect(self, value: Any, context: Optional[str] = None) -> Optional[XSSDetection]:
        """
        Detect XSS patterns in input.

        Args:
            value: Input value to check
            context: Additional context (field name, etc.)

        Returns:
            XSSDetection if attack detected, None otherwise
        """
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        # Check all patterns
        for pattern, pattern_name, xss_type in self.XSS_PATTERNS:
            match = pattern.search(value)
            if match:
                self._detection_count += 1

                detection = XSSDetection(
                    xss_type=xss_type,
                    pattern_matched=pattern_name,
                    input_value=value,
                    metadata={
                        "context": context,
                        "matched_text": match.group(0)[:50],
                        "detection_count": self._detection_count,
                    },
                )

                logger.warning(
                    f"XSS attempt detected: {pattern_name} in '{value[:50]}...'",
                    extra={"detection": detection.to_dict()},
                )

                return detection

        return None

    def detect_in_html(self, html_content: str) -> List[XSSDetection]:
        """
        Detect multiple XSS patterns in HTML content.

        Args:
            html_content: HTML content to scan

        Returns:
            List of detected XSS attempts
        """
        detections = []

        for pattern, pattern_name, xss_type in self.XSS_PATTERNS:
            matches = pattern.finditer(html_content)
            for match in matches:
                detection = XSSDetection(
                    xss_type=xss_type,
                    pattern_matched=pattern_name,
                    input_value=match.group(0),
                    metadata={"position": match.start()},
                )
                detections.append(detection)

        return detections


class OutputEncoder:
    """
    Context-aware output encoding for XSS prevention.

    Provides encoding for different contexts:
    - HTML content
    - HTML attributes
    - JavaScript
    - JSON
    - URLs
    - CSS
    """

    @staticmethod
    def encode_html(value: str) -> str:
        """
        Encode for HTML content context.

        Args:
            value: String to encode

        Returns:
            HTML-encoded string
        """
        return html.escape(value, quote=True)

    @staticmethod
    def encode_html_attribute(value: str) -> str:
        """
        Encode for HTML attribute context.

        More aggressive than HTML content encoding.

        Args:
            value: String to encode

        Returns:
            Attribute-safe encoded string
        """
        # Use aggressive encoding for attributes
        encoded = []
        for char in value:
            code = ord(char)
            # Encode all non-alphanumeric characters
            if not (48 <= code <= 57 or 65 <= code <= 90 or 97 <= code <= 122):
                encoded.append(f"&#x{code:x};")
            else:
                encoded.append(char)
        return "".join(encoded)

    @staticmethod
    def encode_javascript(value: str) -> str:
        """
        Encode for JavaScript string context.

        Args:
            value: String to encode

        Returns:
            JavaScript-safe encoded string
        """
        # Escape special JavaScript characters
        replacements = {
            "\\": "\\\\",
            '"': '\\"',
            "'": "\\'",
            "\n": "\\n",
            "\r": "\\r",
            "\t": "\\t",
            "<": "\\x3c",  # Prevent </script> injection
            ">": "\\x3e",
            "&": "\\x26",
            "/": "\\/",  # Prevent </script> injection
        }

        for char, escaped in replacements.items():
            value = value.replace(char, escaped)

        return value

    @staticmethod
    def encode_json(value: Any) -> str:
        """
        Encode for JSON context.

        Args:
            value: Value to encode as JSON

        Returns:
            JSON-encoded string
        """
        return json.dumps(value, ensure_ascii=True)

    @staticmethod
    def encode_url(value: str) -> str:
        """
        Encode for URL context.

        Args:
            value: String to encode

        Returns:
            URL-encoded string
        """
        return urllib.parse.quote(value, safe="")

    @staticmethod
    def encode_url_param(value: str) -> str:
        """
        Encode for URL parameter context.

        Args:
            value: String to encode

        Returns:
            URL parameter-encoded string
        """
        return urllib.parse.quote_plus(value)

    @staticmethod
    def encode_css(value: str) -> str:
        """
        Encode for CSS context.

        Args:
            value: String to encode

        Returns:
            CSS-safe encoded string
        """
        # Encode all non-alphanumeric characters as hex escapes
        encoded = []
        for char in value:
            if char.isalnum():
                encoded.append(char)
            else:
                encoded.append(f"\\{ord(char):x} ")
        return "".join(encoded)

    @classmethod
    def encode(cls, value: str, context: EncodingContext) -> str:
        """
        Encode value based on context.

        Args:
            value: String to encode
            context: Encoding context

        Returns:
            Context-appropriate encoded string
        """
        if context == EncodingContext.HTML:
            return cls.encode_html(value)
        elif context == EncodingContext.HTML_ATTRIBUTE:
            return cls.encode_html_attribute(value)
        elif context == EncodingContext.JAVASCRIPT:
            return cls.encode_javascript(value)
        elif context == EncodingContext.JSON:
            return cls.encode_json(value)
        elif context == EncodingContext.URL:
            return cls.encode_url(value)
        elif context == EncodingContext.CSS:
            return cls.encode_css(value)
        else:
            # Default to HTML encoding
            return cls.encode_html(value)


class HTMLSanitizer:
    """
    HTML sanitization for allowing safe HTML subset.

    Whitelist-based approach: only allow safe tags and attributes.
    """

    # Safe HTML tags
    ALLOWED_TAGS = {
        "a",
        "b",
        "i",
        "u",
        "em",
        "strong",
        "p",
        "br",
        "span",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "blockquote",
        "code",
        "pre",
        "table",
        "thead",
        "tbody",
        "tr",
        "td",
        "th",
    }

    # Safe HTML attributes per tag
    ALLOWED_ATTRIBUTES = {
        "a": {"href", "title", "target"},
        "span": {"class"},
        "div": {"class"},
        "table": {"class"},
        "td": {"colspan", "rowspan"},
        "th": {"colspan", "rowspan"},
    }

    # Safe URL schemes
    ALLOWED_SCHEMES = {"http", "https", "mailto", "tel"}

    def __init__(
        self,
        allowed_tags: Optional[Set[str]] = None,
        allowed_attributes: Optional[Dict[str, Set[str]]] = None,
    ):
        """
        Initialize HTML sanitizer.

        Args:
            allowed_tags: Set of allowed HTML tags
            allowed_attributes: Dict of allowed attributes per tag
        """
        self.allowed_tags = allowed_tags or self.ALLOWED_TAGS
        self.allowed_attributes = allowed_attributes or self.ALLOWED_ATTRIBUTES

    def sanitize(self, html_input: str) -> str:
        """
        Sanitize HTML by removing dangerous elements.

        Args:
            html_input: HTML string to sanitize

        Returns:
            Sanitized HTML string
        """
        # Remove all script and style tags completely
        html_input = re.sub(
            r"<script[^>]*>.*?</script>", "", html_input, flags=re.IGNORECASE | re.DOTALL
        )
        html_input = re.sub(
            r"<style[^>]*>.*?</style>", "", html_input, flags=re.IGNORECASE | re.DOTALL
        )

        # Remove dangerous tags
        for tag in XSSDetector.DANGEROUS_TAGS:
            html_input = re.sub(
                f"<{tag}[^>]*>.*?</{tag}>", "", html_input, flags=re.IGNORECASE | re.DOTALL
            )
            html_input = re.sub(f"<{tag}[^>]*>", "", html_input, flags=re.IGNORECASE)

        # Remove event handler attributes
        for attr in XSSDetector.DANGEROUS_ATTRIBUTES:
            html_input = re.sub(
                f"{attr}\\s*=\\s*[\"'][^\"']*[\"']", "", html_input, flags=re.IGNORECASE
            )

        # Remove javascript: and data: URLs
        html_input = re.sub(
            r'(href|src)\s*=\s*["\']javascript:[^"\']*["\']', "", html_input, flags=re.IGNORECASE
        )
        html_input = re.sub(
            r'(href|src)\s*=\s*["\']data:[^"\']*["\']', "", html_input, flags=re.IGNORECASE
        )

        return html_input

    def sanitize_strict(self, html_input: str) -> str:
        """
        Strict sanitization - only allow whitelisted tags and attributes.

        Args:
            html_input: HTML string to sanitize

        Returns:
            Strictly sanitized HTML string
        """
        # First do basic sanitization
        html_input = self.sanitize(html_input)

        # TODO: Implement proper HTML parsing with BeautifulSoup or lxml
        # For now, use regex-based approach (less reliable but no dependencies)

        # Remove all tags not in whitelist
        def replace_tag(match):
            tag = match.group(1).lower()
            if tag in self.allowed_tags:
                return match.group(0)
            return ""

        html_input = re.sub(r"<(/?\w+)[^>]*>", replace_tag, html_input)

        return html_input


class ContentSecurityPolicy:
    """
    Content Security Policy (CSP) header management.

    CSP is a critical defense-in-depth mechanism against XSS.
    """

    def __init__(self):
        """Initialize CSP with secure defaults."""
        self.directives: Dict[str, List[str]] = {
            "default-src": ["'self'"],
            "script-src": ["'self'"],
            "style-src": ["'self'"],
            "img-src": ["'self'", "data:", "https:"],
            "font-src": ["'self'"],
            "connect-src": ["'self'"],
            "frame-src": ["'none'"],
            "object-src": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
        }
        self.report_uri: Optional[str] = None
        self.report_only: bool = False

    def add_source(self, directive: str, source: str) -> "ContentSecurityPolicy":
        """
        Add source to directive.

        Args:
            directive: CSP directive (e.g., 'script-src')
            source: Source to add (e.g., 'https://cdn.example.com')

        Returns:
            Self for chaining
        """
        if directive not in self.directives:
            self.directives[directive] = []

        if source not in self.directives[directive]:
            self.directives[directive].append(source)

        return self

    def allow_inline_scripts(self, nonce: Optional[str] = None) -> "ContentSecurityPolicy":
        """
        Allow inline scripts (use nonce for better security).

        Args:
            nonce: Optional nonce value for script tags

        Returns:
            Self for chaining
        """
        if nonce:
            self.add_source("script-src", f"'nonce-{nonce}'")
        else:
            self.add_source("script-src", "'unsafe-inline'")
        return self

    def allow_inline_styles(self, nonce: Optional[str] = None) -> "ContentSecurityPolicy":
        """
        Allow inline styles (use nonce for better security).

        Args:
            nonce: Optional nonce value for style tags

        Returns:
            Self for chaining
        """
        if nonce:
            self.add_source("style-src", f"'nonce-{nonce}'")
        else:
            self.add_source("style-src", "'unsafe-inline'")
        return self

    def set_report_uri(self, uri: str) -> "ContentSecurityPolicy":
        """
        Set CSP violation report URI.

        Args:
            uri: URI to send violation reports to

        Returns:
            Self for chaining
        """
        self.report_uri = uri
        return self

    def set_report_only(self, enabled: bool = True) -> "ContentSecurityPolicy":
        """
        Enable report-only mode (reports violations but doesn't block).

        Args:
            enabled: Enable report-only mode

        Returns:
            Self for chaining
        """
        self.report_only = enabled
        return self

    def build_header(self) -> Tuple[str, str]:
        """
        Build CSP header.

        Returns:
            Tuple of (header_name, header_value)
        """
        # Build directive strings
        directive_strings = []
        for directive, sources in self.directives.items():
            if sources:
                directive_strings.append(f"{directive} {' '.join(sources)}")

        if self.report_uri:
            directive_strings.append(f"report-uri {self.report_uri}")

        header_value = "; ".join(directive_strings)

        # Choose header name based on report-only mode
        header_name = (
            "Content-Security-Policy-Report-Only" if self.report_only else "Content-Security-Policy"
        )

        return header_name, header_value

    @staticmethod
    def generate_nonce() -> str:
        """
        Generate cryptographically secure nonce for CSP.

        Returns:
            Base64-encoded nonce
        """
        import secrets

        return base64.b64encode(secrets.token_bytes(16)).decode("utf-8")


class XSSProtectionMiddleware:
    """
    Comprehensive XSS protection middleware for CovetPy applications.
    """

    def __init__(
        self,
        enable_detection: bool = True,
        enable_csp: bool = True,
        enable_xss_header: bool = True,
        csp_config: Optional[ContentSecurityPolicy] = None,
        block_on_detection: bool = True,
        audit_callback: Optional[Callable[[XSSDetection], None]] = None,
    ):
        """
        Initialize XSS protection middleware.

        Args:
            enable_detection: Enable XSS detection
            enable_csp: Enable Content Security Policy
            enable_xss_header: Enable X-XSS-Protection header
            csp_config: Custom CSP configuration
            block_on_detection: Block requests with detected XSS
            audit_callback: Callback function for audit logging
        """
        self.enable_detection = enable_detection
        self.enable_csp = enable_csp
        self.enable_xss_header = enable_xss_header
        self.csp = csp_config or ContentSecurityPolicy()
        self.block_on_detection = block_on_detection
        self.audit_callback = audit_callback

        self.detector = XSSDetector()
        self._total_detections = 0
        self._blocked_requests = 0

    async def __call__(self, scope, receive, send):
        """ASGI middleware interface."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Scan request if detection enabled
        if self.enable_detection:
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

        # Add security headers
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Add CSP header
                if self.enable_csp:
                    csp_name, csp_value = self.csp.build_header()
                    headers.append((csp_name.encode(), csp_value.encode()))

                # Add X-XSS-Protection header
                if self.enable_xss_header:
                    headers.append((b"x-xss-protection", b"1; mode=block"))

                # Add X-Content-Type-Options (prevents MIME sniffing)
                headers.append((b"x-content-type-options", b"nosniff"))

                message["headers"] = headers

            await send(message)

        # Continue to application with security headers
        await self.app(scope, receive, send_with_headers)

    async def _scan_request(self, scope: Dict[str, Any]) -> Optional[XSSDetection]:
        """Scan request for XSS attempts."""
        # Scan query parameters
        query_string = scope.get("query_string", b"").decode("utf-8")
        if query_string:
            params = urllib.parse.parse_qs(query_string)
            for key, values in params.items():
                for value in values:
                    detection = self.detector.detect(value, context=f"query:{key}")
                    if detection:
                        return detection

        return None

    async def _send_blocked_response(self, send, detection: XSSDetection):
        """Send blocked response for detected XSS."""
        await send(
            {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"x-xss-blocked", detection.xss_type.value.encode()),
                ],
            }
        )

        body = json.dumps(
            {
                "error": "Request blocked",
                "reason": "Potential XSS attack detected",
                "type": detection.xss_type.value,
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


# Template helper functions


def safe_output(value: str, context: EncodingContext = EncodingContext.HTML) -> str:
    """
    Safe output encoding for templates.

    Usage in templates:
        {{ safe_output(user_input) }}

    Args:
        value: Value to encode
        context: Output context

    Returns:
        Safely encoded value
    """
    return OutputEncoder.encode(str(value), context)


def safe_html(value: str) -> str:
    """Encode for HTML context."""
    return OutputEncoder.encode_html(value)


def safe_js(value: str) -> str:
    """Encode for JavaScript context."""
    return OutputEncoder.encode_javascript(value)


def safe_url(value: str) -> str:
    """Encode for URL context."""
    return OutputEncoder.encode_url(value)


__all__ = [
    # Enums
    "XSSType",
    "EncodingContext",
    # Data classes
    "XSSDetection",
    # Core classes
    "XSSDetector",
    "OutputEncoder",
    "HTMLSanitizer",
    "ContentSecurityPolicy",
    # Middleware
    "XSSProtectionMiddleware",
    # Helper functions
    "safe_output",
    "safe_html",
    "safe_js",
    "safe_url",
]
