"""
Security Headers Middleware

Production-grade security headers implementation following OWASP guidelines.

Implements:
- Content Security Policy (CSP) with builder
- Strict Transport Security (HSTS)
- X-Frame-Options (Clickjacking protection)
- X-Content-Type-Options (MIME sniffing protection)
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy (Feature-Policy)
- Cross-Origin policies (COOP, COEP, CORP)

Security Benefits:
- XSS attack mitigation through CSP
- Clickjacking prevention
- HTTPS enforcement
- Information leakage prevention
- Feature access control
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class CSPDirective(str, Enum):
    """Content Security Policy directive names"""

    DEFAULT_SRC = "default-src"
    SCRIPT_SRC = "script-src"
    STYLE_SRC = "style-src"
    IMG_SRC = "img-src"
    FONT_SRC = "font-src"
    CONNECT_SRC = "connect-src"
    MEDIA_SRC = "media-src"
    OBJECT_SRC = "object-src"
    FRAME_SRC = "frame-src"
    WORKER_SRC = "worker-src"
    MANIFEST_SRC = "manifest-src"
    FORM_ACTION = "form-action"
    FRAME_ANCESTORS = "frame-ancestors"
    BASE_URI = "base-uri"
    UPGRADE_INSECURE_REQUESTS = "upgrade-insecure-requests"
    BLOCK_ALL_MIXED_CONTENT = "block-all-mixed-content"
    REPORT_URI = "report-uri"
    REPORT_TO = "report-to"


class CSPSource(str, Enum):
    """Common CSP source values"""

    SELF = "'self'"
    NONE = "'none'"
    UNSAFE_INLINE = "'unsafe-inline'"
    UNSAFE_EVAL = "'unsafe-eval'"
    STRICT_DYNAMIC = "'strict-dynamic'"
    UNSAFE_HASHES = "'unsafe-hashes'"
    DATA = "data:"
    HTTPS = "https:"
    BLOB = "blob:"
    MEDIASTREAM = "mediastream:"


class CSPBuilder:
    """
    Content Security Policy builder

    Provides a fluent API for building CSP headers.

    Usage:
        csp = CSPBuilder()
        csp.default_src([CSPSource.SELF])
        csp.script_src([CSPSource.SELF, 'cdn.example.com'])
        csp.style_src([CSPSource.SELF, CSPSource.UNSAFE_INLINE])
        csp.img_src([CSPSource.SELF, CSPSource.DATA, CSPSource.HTTPS])
        csp.report_uri('/csp-report')

        header_value = csp.build()
    """

    def __init__(self):
        self._directives: Dict[str, List[str]] = {}

    def default_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set default-src directive"""
        self._directives[CSPDirective.DEFAULT_SRC] = [str(s) for s in sources]
        return self

    def script_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set script-src directive"""
        self._directives[CSPDirective.SCRIPT_SRC] = [str(s) for s in sources]
        return self

    def style_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set style-src directive"""
        self._directives[CSPDirective.STYLE_SRC] = [str(s) for s in sources]
        return self

    def img_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set img-src directive"""
        self._directives[CSPDirective.IMG_SRC] = [str(s) for s in sources]
        return self

    def font_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set font-src directive"""
        self._directives[CSPDirective.FONT_SRC] = [str(s) for s in sources]
        return self

    def connect_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set connect-src directive"""
        self._directives[CSPDirective.CONNECT_SRC] = [str(s) for s in sources]
        return self

    def media_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set media-src directive"""
        self._directives[CSPDirective.MEDIA_SRC] = [str(s) for s in sources]
        return self

    def object_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set object-src directive"""
        self._directives[CSPDirective.OBJECT_SRC] = [str(s) for s in sources]
        return self

    def frame_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set frame-src directive"""
        self._directives[CSPDirective.FRAME_SRC] = [str(s) for s in sources]
        return self

    def worker_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set worker-src directive"""
        self._directives[CSPDirective.WORKER_SRC] = [str(s) for s in sources]
        return self

    def manifest_src(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set manifest-src directive"""
        self._directives[CSPDirective.MANIFEST_SRC] = [str(s) for s in sources]
        return self

    def form_action(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set form-action directive"""
        self._directives[CSPDirective.FORM_ACTION] = [str(s) for s in sources]
        return self

    def frame_ancestors(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set frame-ancestors directive"""
        self._directives[CSPDirective.FRAME_ANCESTORS] = [str(s) for s in sources]
        return self

    def base_uri(self, sources: List[Union[str, CSPSource]]) -> "CSPBuilder":
        """Set base-uri directive"""
        self._directives[CSPDirective.BASE_URI] = [str(s) for s in sources]
        return self

    def upgrade_insecure_requests(self) -> "CSPBuilder":
        """Enable upgrade-insecure-requests"""
        self._directives[CSPDirective.UPGRADE_INSECURE_REQUESTS] = []
        return self

    def block_all_mixed_content(self) -> "CSPBuilder":
        """Enable block-all-mixed-content"""
        self._directives[CSPDirective.BLOCK_ALL_MIXED_CONTENT] = []
        return self

    def report_uri(self, uri: str) -> "CSPBuilder":
        """Set report-uri directive"""
        self._directives[CSPDirective.REPORT_URI] = [uri]
        return self

    def report_to(self, group: str) -> "CSPBuilder":
        """Set report-to directive"""
        self._directives[CSPDirective.REPORT_TO] = [group]
        return self

    def add_nonce(self, directive: CSPDirective, nonce: str) -> "CSPBuilder":
        """Add nonce to directive"""
        if directive not in self._directives:
            self._directives[directive] = []
        self._directives[directive].append(f"'nonce-{nonce}'")
        return self

    def add_hash(
        self, directive: CSPDirective, hash_value: str, algorithm: str = "sha256"
    ) -> "CSPBuilder":
        """Add hash to directive"""
        if directive not in self._directives:
            self._directives[directive] = []
        self._directives[directive].append(f"'{algorithm}-{hash_value}'")
        return self

    def build(self) -> str:
        """
        Build CSP header value

        Returns:
            CSP header string
        """
        parts = []

        for directive, sources in self._directives.items():
            if sources:
                parts.append(f"{directive} {' '.join(sources)}")
            else:
                # Boolean directives (no sources)
                parts.append(directive)

        return "; ".join(parts)


@dataclass
class SecurityHeadersConfig:
    """Security headers configuration"""

    # CSP
    csp_policy: Optional[str] = None
    csp_report_only: bool = False

    # HSTS
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False

    # X-Frame-Options
    x_frame_options: str = "DENY"  # DENY, SAMEORIGIN, or ALLOW-FROM

    # X-Content-Type-Options
    x_content_type_options: bool = True

    # X-XSS-Protection
    x_xss_protection: str = "1; mode=block"

    # Referrer-Policy
    referrer_policy: str = "strict-origin-when-cross-origin"

    # Permissions-Policy (formerly Feature-Policy)
    permissions_policy: Optional[Dict[str, List[str]]] = None

    # Cross-Origin policies
    # require-corp, credentialless
    cross_origin_embedder_policy: Optional[str] = None
    cross_origin_opener_policy: Optional[str] = (
        None  # same-origin, same-origin-allow-popups, unsafe-none
    )
    cross_origin_resource_policy: Optional[str] = None  # same-site, same-origin, cross-origin

    # Server header
    hide_server_header: bool = True
    custom_server_header: Optional[str] = None


class SecurityHeadersMiddleware:
    """
    Security headers middleware

    Automatically adds security headers to all HTTP responses.

    Usage:
        app = CovetApp()

        # Basic usage with defaults
        app.add_middleware(SecurityHeadersMiddleware)

        # Custom configuration
        csp = CSPBuilder()
        csp.default_src([CSPSource.SELF])
        csp.script_src([CSPSource.SELF, 'cdn.example.com'])
        csp.style_src([CSPSource.SELF, CSPSource.UNSAFE_INLINE])
        csp.img_src([CSPSource.SELF, CSPSource.DATA])
        csp.report_uri('/csp-report')

        config = SecurityHeadersConfig(
            csp_policy=csp.build(),
            hsts_max_age=63072000,  # 2 years
            x_frame_options='SAMEORIGIN',
            permissions_policy={
                'geolocation': [],
                'camera': [],
                'microphone': []
            }
        )

        app.add_middleware(SecurityHeadersMiddleware, config=config)
    """

    def __init__(self, app: Callable, config: Optional[SecurityHeadersConfig] = None):
        """
        Initialize security headers middleware

        Args:
            app: ASGI application
            config: Security headers configuration
        """
        self.app = app
        self.config = config or SecurityHeadersConfig()

        # Build default CSP if not provided
        if not self.config.csp_policy:
            self.config.csp_policy = self._build_default_csp()

    def _build_default_csp(self) -> str:
        """Build secure default CSP"""
        csp = CSPBuilder()
        csp.default_src([CSPSource.SELF])
        csp.script_src([CSPSource.SELF])
        csp.style_src([CSPSource.SELF])
        csp.img_src([CSPSource.SELF, CSPSource.DATA])
        csp.font_src([CSPSource.SELF])
        csp.connect_src([CSPSource.SELF])
        csp.frame_ancestors([CSPSource.NONE])
        csp.base_uri([CSPSource.SELF])
        csp.form_action([CSPSource.SELF])
        csp.object_src([CSPSource.NONE])
        return csp.build()

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """
        ASGI interface

        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Wrap send to add security headers
        async def send_with_headers(message: Dict[str, Any]):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Add security headers
                headers.extend(self._build_security_headers())

                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_headers)

    def _build_security_headers(self) -> List[tuple]:
        """
        Build list of security headers

        Returns:
            List of (header_name, header_value) tuples
        """
        headers = []

        # Content-Security-Policy
        if self.config.csp_policy:
            header_name = (
                b"content-security-policy-report-only"
                if self.config.csp_report_only
                else b"content-security-policy"
            )
            headers.append((header_name, self.config.csp_policy.encode("utf-8")))

        # Strict-Transport-Security (HSTS)
        hsts_parts = [f"max-age={self.config.hsts_max_age}"]
        if self.config.hsts_include_subdomains:
            hsts_parts.append("includeSubDomains")
        if self.config.hsts_preload:
            hsts_parts.append("preload")
        headers.append((b"strict-transport-security", "; ".join(hsts_parts).encode("utf-8")))

        # X-Frame-Options
        if self.config.x_frame_options:
            headers.append((b"x-frame-options", self.config.x_frame_options.encode("utf-8")))

        # X-Content-Type-Options
        if self.config.x_content_type_options:
            headers.append((b"x-content-type-options", b"nosniff"))

        # X-XSS-Protection
        if self.config.x_xss_protection:
            headers.append((b"x-xss-protection", self.config.x_xss_protection.encode("utf-8")))

        # Referrer-Policy
        if self.config.referrer_policy:
            headers.append((b"referrer-policy", self.config.referrer_policy.encode("utf-8")))

        # Permissions-Policy
        if self.config.permissions_policy:
            policy_value = self._build_permissions_policy()
            headers.append((b"permissions-policy", policy_value.encode("utf-8")))

        # Cross-Origin-Embedder-Policy
        if self.config.cross_origin_embedder_policy:
            headers.append(
                (
                    b"cross-origin-embedder-policy",
                    self.config.cross_origin_embedder_policy.encode("utf-8"),
                )
            )

        # Cross-Origin-Opener-Policy
        if self.config.cross_origin_opener_policy:
            headers.append(
                (
                    b"cross-origin-opener-policy",
                    self.config.cross_origin_opener_policy.encode("utf-8"),
                )
            )

        # Cross-Origin-Resource-Policy
        if self.config.cross_origin_resource_policy:
            headers.append(
                (
                    b"cross-origin-resource-policy",
                    self.config.cross_origin_resource_policy.encode("utf-8"),
                )
            )

        # Server header
        if self.config.hide_server_header:
            if self.config.custom_server_header:
                headers.append((b"server", self.config.custom_server_header.encode("utf-8")))
            else:
                headers.append((b"server", b""))

        return headers

    def _build_permissions_policy(self) -> str:
        """
        Build Permissions-Policy header value

        Returns:
            Permissions-Policy header string
        """
        if not self.config.permissions_policy:
            return ""

        parts = []

        for feature, origins in self.config.permissions_policy.items():
            if not origins:
                # Feature disabled for all origins
                parts.append(f"{feature}=()")
            elif origins == ["*"]:
                # Feature enabled for all origins
                parts.append(f"{feature}=*")
            elif origins == ["self"]:
                # Feature enabled for same origin
                parts.append(f"{feature}=(self)")
            else:
                # Feature enabled for specific origins
                origin_list = " ".join(f'"{o}"' for o in origins)
                parts.append(f"{feature}=({origin_list})")

        return ", ".join(parts)


# Preset configurations for common scenarios
class SecurityPresets:
    """Preset security configurations"""

    @staticmethod
    def strict() -> SecurityHeadersConfig:
        """
        Strict security configuration

        Maximum security, may break some functionality
        """
        csp = CSPBuilder()
        csp.default_src([CSPSource.NONE])
        csp.script_src([CSPSource.SELF])
        csp.style_src([CSPSource.SELF])
        csp.img_src([CSPSource.SELF])
        csp.font_src([CSPSource.SELF])
        csp.connect_src([CSPSource.SELF])
        csp.frame_ancestors([CSPSource.NONE])
        csp.base_uri([CSPSource.SELF])
        csp.form_action([CSPSource.SELF])
        csp.object_src([CSPSource.NONE])
        csp.upgrade_insecure_requests()

        return SecurityHeadersConfig(
            csp_policy=csp.build(),
            hsts_max_age=63072000,  # 2 years
            hsts_include_subdomains=True,
            hsts_preload=True,
            x_frame_options="DENY",
            x_content_type_options=True,
            x_xss_protection="1; mode=block",
            referrer_policy="no-referrer",
            permissions_policy={
                "geolocation": [],
                "camera": [],
                "microphone": [],
                "payment": [],
                "usb": [],
                "magnetometer": [],
                "gyroscope": [],
                "accelerometer": [],
            },
            cross_origin_embedder_policy="require-corp",
            cross_origin_opener_policy="same-origin",
            cross_origin_resource_policy="same-origin",
            hide_server_header=True,
        )

    @staticmethod
    def balanced() -> SecurityHeadersConfig:
        """
        Balanced security configuration

        Good security with reasonable compatibility
        """
        csp = CSPBuilder()
        csp.default_src([CSPSource.SELF])
        csp.script_src([CSPSource.SELF])
        # Allow inline styles
        csp.style_src([CSPSource.SELF, CSPSource.UNSAFE_INLINE])
        csp.img_src([CSPSource.SELF, CSPSource.DATA, CSPSource.HTTPS])
        csp.font_src([CSPSource.SELF, CSPSource.DATA])
        csp.connect_src([CSPSource.SELF])
        csp.frame_ancestors([CSPSource.SELF])
        csp.base_uri([CSPSource.SELF])
        csp.object_src([CSPSource.NONE])

        return SecurityHeadersConfig(
            csp_policy=csp.build(),
            hsts_max_age=31536000,  # 1 year
            hsts_include_subdomains=True,
            x_frame_options="SAMEORIGIN",
            x_content_type_options=True,
            x_xss_protection="1; mode=block",
            referrer_policy="strict-origin-when-cross-origin",
            permissions_policy={"geolocation": [], "camera": [], "microphone": []},
            hide_server_header=True,
        )

    @staticmethod
    def development() -> SecurityHeadersConfig:
        """
        Development configuration

        Minimal security restrictions for development
        """
        csp = CSPBuilder()
        csp.default_src([CSPSource.SELF, CSPSource.UNSAFE_INLINE, CSPSource.UNSAFE_EVAL])
        csp.img_src([CSPSource.SELF, CSPSource.DATA, CSPSource.HTTPS])
        csp.report_uri("/csp-report")

        return SecurityHeadersConfig(
            csp_policy=csp.build(),
            csp_report_only=True,  # Report-only mode
            hsts_max_age=300,  # 5 minutes
            x_frame_options="SAMEORIGIN",
            x_content_type_options=True,
            hide_server_header=False,
        )
