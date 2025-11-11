"""
CovetPy Security Headers Module

Comprehensive security headers middleware implementing best practices:
- Strict-Transport-Security (HSTS)
- X-Frame-Options (clickjacking prevention)
- X-Content-Type-Options (MIME sniffing prevention)
- Referrer-Policy
- Permissions-Policy (Feature-Policy)
- Content-Security-Policy (CSP)
- X-XSS-Protection (legacy browsers)
- CORS (Cross-Origin Resource Sharing)

Implements OWASP Secure Headers Project recommendations and security best practices
for defense-in-depth HTTP header security.

Author: CovetPy Security Team
License: MIT
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class FrameOptions(Enum):
    """X-Frame-Options values."""

    DENY = "DENY"
    SAMEORIGIN = "SAMEORIGIN"


class ReferrerPolicy(Enum):
    """Referrer-Policy values."""

    NO_REFERRER = "no-referrer"
    NO_REFERRER_WHEN_DOWNGRADE = "no-referrer-when-downgrade"
    ORIGIN = "origin"
    ORIGIN_WHEN_CROSS_ORIGIN = "origin-when-cross-origin"
    SAME_ORIGIN = "same-origin"
    STRICT_ORIGIN = "strict-origin"
    STRICT_ORIGIN_WHEN_CROSS_ORIGIN = "strict-origin-when-cross-origin"
    UNSAFE_URL = "unsafe-url"


@dataclass
class SecurityHeadersConfig:
    """Configuration for security headers."""

    # HSTS (HTTP Strict Transport Security)
    enable_hsts: bool = True
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False

    # Frame Options (Clickjacking)
    enable_frame_options: bool = True
    frame_options: FrameOptions = FrameOptions.DENY

    # Content Type Options
    enable_content_type_options: bool = True

    # XSS Protection (legacy)
    enable_xss_protection: bool = True
    xss_protection_mode: str = "1; mode=block"

    # Referrer Policy
    enable_referrer_policy: bool = True
    referrer_policy: ReferrerPolicy = ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN

    # Permissions Policy
    enable_permissions_policy: bool = True
    permissions_policy: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "geolocation": [],
            "microphone": [],
            "camera": [],
            "payment": [],
            "usb": [],
            "magnetometer": [],
            "gyroscope": [],
            "accelerometer": [],
        }
    )

    # Content Security Policy
    enable_csp: bool = False  # Disabled by default (needs configuration)
    csp_directives: Dict[str, List[str]] = field(default_factory=dict)
    csp_report_only: bool = False

    # CORS
    enable_cors: bool = False
    cors_allow_origins: List[str] = field(default_factory=list)
    cors_allow_methods: List[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    cors_allow_headers: List[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])
    cors_expose_headers: List[str] = field(default_factory=list)
    cors_allow_credentials: bool = False
    cors_max_age: int = 86400  # 24 hours

    # Additional Security Headers
    remove_server_header: bool = True
    remove_x_powered_by: bool = True


class SecurityHeadersMiddleware:
    """
    Comprehensive security headers middleware.

    Automatically adds security headers to all HTTP responses.
    """

    def __init__(self, config: Optional[SecurityHeadersConfig] = None):
        """
        Initialize security headers middleware.

        Args:
            config: Security headers configuration (uses defaults if None)
        """
        self.config = config or SecurityHeadersConfig()

    async def __call__(self, scope, receive, send):
        """ASGI middleware interface."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Handle CORS preflight
        if self.config.enable_cors and scope["method"] == "OPTIONS":
            await self._handle_preflight(scope, send)
            return

        # Add security headers to response
        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Add security headers
                security_headers = self._build_security_headers(scope)
                for header_name, header_value in security_headers.items():
                    headers.append((header_name.encode().lower(), header_value.encode()))

                # Remove sensitive headers
                if self.config.remove_server_header:
                    headers = [
                        (name, value) for name, value in headers if name.lower() != b"server"
                    ]
                if self.config.remove_x_powered_by:
                    headers = [
                        (name, value) for name, value in headers if name.lower() != b"x-powered-by"
                    ]

                message["headers"] = headers

            await send(message)

        # Continue to application
        await self.app(scope, receive, send_with_security_headers)

    def _build_security_headers(self, scope: Dict[str, Any]) -> Dict[str, str]:
        """Build security headers dictionary."""
        headers = {}

        # HSTS (only on HTTPS)
        if self.config.enable_hsts and scope.get("scheme") == "https":
            hsts_value = f"max-age={self.config.hsts_max_age}"
            if self.config.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.config.hsts_preload:
                hsts_value += "; preload"
            headers["Strict-Transport-Security"] = hsts_value

        # X-Frame-Options
        if self.config.enable_frame_options:
            headers["X-Frame-Options"] = self.config.frame_options.value

        # X-Content-Type-Options
        if self.config.enable_content_type_options:
            headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection (legacy)
        if self.config.enable_xss_protection:
            headers["X-XSS-Protection"] = self.config.xss_protection_mode

        # Referrer-Policy
        if self.config.enable_referrer_policy:
            headers["Referrer-Policy"] = self.config.referrer_policy.value

        # Permissions-Policy
        if self.config.enable_permissions_policy:
            permissions = []
            for feature, origins in self.config.permissions_policy.items():
                if not origins:
                    permissions.append(f"{feature}=()")
                else:
                    origins_str = " ".join(f'"{o}"' for o in origins)
                    permissions.append(f"{feature}=({origins_str})")
            if permissions:
                headers["Permissions-Policy"] = ", ".join(permissions)

        # Content-Security-Policy
        if self.config.enable_csp and self.config.csp_directives:
            csp_value = self._build_csp()
            header_name = (
                "Content-Security-Policy-Report-Only"
                if self.config.csp_report_only
                else "Content-Security-Policy"
            )
            headers[header_name] = csp_value

        # CORS headers
        if self.config.enable_cors:
            cors_headers = self._build_cors_headers(scope)
            headers.update(cors_headers)

        return headers

    def _build_csp(self) -> str:
        """Build Content-Security-Policy header value."""
        directives = []
        for directive, sources in self.config.csp_directives.items():
            if sources:
                directives.append(f"{directive} {' '.join(sources)}")
        return "; ".join(directives)

    def _build_cors_headers(self, scope: Dict[str, Any]) -> Dict[str, str]:
        """Build CORS headers."""
        headers = {}

        # Get Origin header from request
        origin = None
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"origin":
                origin = header_value.decode()
                break

        # Check if origin is allowed
        if origin and self._is_origin_allowed(origin):
            headers["Access-Control-Allow-Origin"] = origin

            if self.config.cors_allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"

            if self.config.cors_expose_headers:
                headers["Access-Control-Expose-Headers"] = ", ".join(
                    self.config.cors_expose_headers
                )

        return headers

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        if "*" in self.config.cors_allow_origins:
            return True
        return origin in self.config.cors_allow_origins

    async def _handle_preflight(self, scope: Dict[str, Any], send):
        """Handle CORS preflight request."""
        # Get Origin header
        origin = None
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"origin":
                origin = header_value.decode()
                break

        if not origin or not self._is_origin_allowed(origin):
            # Reject preflight
            await send(
                {
                    "type": "http.response.start",
                    "status": 403,
                    "headers": [(b"content-length", b"0")],
                }
            )
            await send({"type": "http.response.body", "body": b""})
            return

        # Build preflight headers
        headers = [
            (b"access-control-allow-origin", origin.encode()),
            (b"access-control-allow-methods", ", ".join(self.config.cors_allow_methods).encode()),
            (b"access-control-allow-headers", ", ".join(self.config.cors_allow_headers).encode()),
            (b"access-control-max-age", str(self.config.cors_max_age).encode()),
            (b"content-length", b"0"),
        ]

        if self.config.cors_allow_credentials:
            headers.append((b"access-control-allow-credentials", b"true"))

        await send({"type": "http.response.start", "status": 204, "headers": headers})
        await send({"type": "http.response.body", "body": b""})


def create_secure_headers_config(
    enable_all: bool = True,
    hsts_max_age: int = 31536000,
    frame_options: FrameOptions = FrameOptions.DENY,
    referrer_policy: ReferrerPolicy = ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN,
) -> SecurityHeadersConfig:
    """
    Create secure headers configuration with recommended defaults.

    Args:
        enable_all: Enable all security headers
        hsts_max_age: HSTS max age in seconds
        frame_options: X-Frame-Options value
        referrer_policy: Referrer-Policy value

    Returns:
        SecurityHeadersConfig with secure defaults
    """
    return SecurityHeadersConfig(
        enable_hsts=enable_all,
        hsts_max_age=hsts_max_age,
        hsts_include_subdomains=True,
        hsts_preload=False,
        enable_frame_options=enable_all,
        frame_options=frame_options,
        enable_content_type_options=enable_all,
        enable_xss_protection=enable_all,
        enable_referrer_policy=enable_all,
        referrer_policy=referrer_policy,
        enable_permissions_policy=enable_all,
        remove_server_header=True,
        remove_x_powered_by=True,
    )


__all__ = [
    "FrameOptions",
    "ReferrerPolicy",
    "SecurityHeadersConfig",
    "SecurityHeadersMiddleware",
    "create_secure_headers_config",
]
