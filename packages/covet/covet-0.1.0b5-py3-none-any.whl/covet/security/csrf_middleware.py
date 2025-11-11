"""
CSRF Protection Middleware

ASGI middleware providing automatic CSRF protection for web applications.

Features:
- Automatic token injection into responses
- Request validation for unsafe methods
- Session integration
- Cookie and header-based token delivery
- Configurable exemptions
- Error handling with proper HTTP status codes
"""

import json
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import parse_qs

from .csrf import CSRFConfig, CSRFProtection, CSRFTokenError


class CSRFMiddleware:
    """
    ASGI middleware for CSRF protection

    Automatically protects all unsafe HTTP methods (POST, PUT, DELETE, PATCH)
    from Cross-Site Request Forgery attacks.

    Usage:
        app = CovetApp()
        csrf_config = CSRFConfig(
            exempt_paths=['/api/webhooks', '/api/public'],
            secret_key=b'your-secret-key'
        )
        app.add_middleware(CSRFMiddleware, config=csrf_config)
    """

    def __init__(
        self,
        app: Callable,
        config: Optional[CSRFConfig] = None,
        csrf_protection: Optional[CSRFProtection] = None,
    ):
        """
        Initialize CSRF middleware

        Args:
            app: ASGI application
            config: CSRF configuration
            csrf_protection: CSRF protection instance (or creates new one)
        """
        self.app = app
        self.csrf = csrf_protection or CSRFProtection(config)
        self.config = self.csrf.config

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """
        ASGI interface

        Args:
            scope: ASGI scope dict
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] != "http":
            # Pass through non-HTTP requests
            await self.app(scope, receive, send)
            return

        # Extract request information
        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        headers = dict(scope.get("headers", []))

        # Get session ID from cookie if available
        session_id = self._get_session_id(headers)

        # Check if request needs CSRF protection
        if method.upper() in self.config.exempt_methods:
            # Safe methods - just add token to response
            await self._handle_safe_request(scope, receive, send, session_id)
            return

        if self._is_path_exempt(path):
            # Exempt path - pass through
            await self.app(scope, receive, send)
            return

        # Unsafe method - validate CSRF token
        try:
            await self._validate_csrf(scope, receive, send, method, path, headers, session_id)
        except CSRFTokenError as e:
            # CSRF validation failed - return 403 Forbidden
            await self._send_csrf_error(send, str(e))

    async def _handle_safe_request(
        self,
        scope: Dict[str, Any],
        receive: Callable,
        send: Callable,
        session_id: Optional[str],
    ):
        """
        Handle safe request (GET, HEAD, OPTIONS)

        Adds CSRF token to response for use in subsequent requests
        """
        # Generate CSRF token
        token = self.csrf.generate_token(session_id)

        # Wrap send to inject CSRF cookie
        async def send_with_csrf(message: Dict[str, Any]):
            if message["type"] == "http.response.start":
                # Add CSRF cookie to response headers
                headers = list(message.get("headers", []))

                # Create cookie header
                cookie_header = self.csrf.create_cookie_header(token)
                headers.append((b"set-cookie", cookie_header.encode("utf-8")))

                message["headers"] = headers

            await send(message)

        # Call application with modified send
        await self.app(scope, receive, send_with_csrf)

    async def _validate_csrf(
        self,
        scope: Dict[str, Any],
        receive: Callable,
        send: Callable,
        method: str,
        path: str,
        headers: Dict[bytes, bytes],
        session_id: Optional[str],
    ):
        """
        Validate CSRF token for unsafe request

        Checks:
        1. Origin header (if present)
        2. Referer header (if present)
        3. CSRF token from header or body
        """
        # Extract headers as strings
        origin = headers.get(b"origin", b"").decode("utf-8")
        referer = headers.get(b"referer", b"").decode("utf-8")
        host = headers.get(b"host", b"").decode("utf-8")

        # Try to get token from header first
        token = self._get_token_from_header(headers)

        # If not in header, read from request body
        if not token:
            token = await self._get_token_from_body(scope, receive)

        # Validate request
        self.csrf.validate_request(
            method=method,
            path=path,
            token=token,
            session_id=session_id,
            origin=origin or None,
            referer=referer or None,
            host=host or None,
        )

        # Validation successful - proceed with request
        await self.app(scope, receive, send)

    def _get_session_id(self, headers: Dict[bytes, bytes]) -> Optional[str]:
        """
        Extract session ID from cookie

        Args:
            headers: Request headers

        Returns:
            Session ID or None
        """
        cookie_header = headers.get(b"cookie", b"").decode("utf-8")

        if not cookie_header:
            return None

        # Parse cookies
        cookies = {}
        for cookie in cookie_header.split(";"):
            cookie = cookie.strip()
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                cookies[name] = value

        # Look for session cookie (configurable name)
        return cookies.get("session_id")

    def _get_token_from_header(self, headers: Dict[bytes, bytes]) -> Optional[str]:
        """
        Extract CSRF token from custom header

        Args:
            headers: Request headers

        Returns:
            CSRF token or None
        """
        header_name = self.config.header_name.lower().encode("utf-8")
        token = headers.get(header_name, b"").decode("utf-8")
        return token if token else None

    async def _get_token_from_body(self, scope: Dict[str, Any], receive: Callable) -> Optional[str]:
        """
        Extract CSRF token from request body

        Supports:
        - Form data (application/x-www-form-urlencoded)
        - Multipart form data (multipart/form-data)
        - JSON (application/json)

        Args:
            scope: ASGI scope
            receive: ASGI receive callable

        Returns:
            CSRF token or None
        """
        headers = dict(scope.get("headers", []))
        content_type = headers.get(b"content-type", b"").decode("utf-8").lower()

        # Read body
        body = b""
        while True:
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                if not message.get("more_body"):
                    break

        if not body:
            return None

        # Parse based on content type
        if "application/x-www-form-urlencoded" in content_type:
            return self._parse_form_token(body)
        elif "application/json" in content_type:
            return self._parse_json_token(body)
        elif "multipart/form-data" in content_type:
            return self._parse_multipart_token(body, content_type)

        return None

    def _parse_form_token(self, body: bytes) -> Optional[str]:
        """Parse CSRF token from form data"""
        try:
            form_data = parse_qs(body.decode("utf-8"))
            token_list = form_data.get(self.config.form_field_name, [])
            return token_list[0] if token_list else None
        except (ValueError, UnicodeDecodeError):
            return None

    def _parse_json_token(self, body: bytes) -> Optional[str]:
        """Parse CSRF token from JSON body"""
        try:
            data = json.loads(body.decode("utf-8"))
            return data.get(self.config.form_field_name)
        except (ValueError, json.JSONDecodeError):
            return None

    def _parse_multipart_token(self, body: bytes, content_type: str) -> Optional[str]:
        """
        Parse CSRF token from multipart form data

        This is a simplified parser - in production, use a library like `multipart`
        """
        try:
            # Extract boundary
            boundary = None
            for part in content_type.split(";"):
                part = part.strip()
                if part.startswith("boundary="):
                    boundary = part.split("=", 1)[1].strip('"')
                    break

            if not boundary:
                return None

            # Split parts
            boundary_bytes = f"--{boundary}".encode("utf-8")
            parts = body.split(boundary_bytes)

            # Find CSRF token field
            for part in parts:
                if self.config.form_field_name.encode("utf-8") in part:
                    # Extract value (simplified)
                    lines = part.split(b"\r\n")
                    if len(lines) >= 4:
                        # Value is typically after headers
                        return lines[-2].decode("utf-8").strip()

        except (ValueError, UnicodeDecodeError):
            # TODO: Add proper exception handling

            pass
        return None

    def _is_path_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        for exempt_path in self.config.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False

    async def _send_csrf_error(self, send: Callable, error_message: str):
        """
        Send CSRF error response

        Returns 403 Forbidden with RFC 7807 problem details
        """
        # Create RFC 7807 problem details
        problem_details = {
            "type": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403",
            "title": "Forbidden",
            "status": 403,
            "detail": error_message,
            "instance": "/csrf-validation",
        }

        body = json.dumps(problem_details).encode("utf-8")

        # Send response
        await send(
            {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    (b"content-type", b"application/problem+json"),
                    (b"content-length", str(len(body)).encode("utf-8")),
                ],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )


class DoubleSubmitCSRFMiddleware(CSRFMiddleware):
    """
    Double Submit Cookie CSRF Protection

    Alternative CSRF protection that doesn't require server-side state.

    The token is:
    1. Set in a cookie (readable by JavaScript)
    2. Sent in a custom header on each request
    3. Server compares cookie value with header value

    This is useful for stateless APIs but slightly less secure than
    synchronizer token pattern.
    """

    async def _validate_csrf(
        self,
        scope: Dict[str, Any],
        receive: Callable,
        send: Callable,
        method: str,
        path: str,
        headers: Dict[bytes, bytes],
        session_id: Optional[str],
    ):
        """
        Validate using double submit pattern

        Compares token from cookie with token from header/body
        """
        # Get token from cookie
        cookie_token = self._get_csrf_cookie(headers)

        # Get token from header or body
        header_token = self._get_token_from_header(headers)
        if not header_token:
            header_token = await self._get_token_from_body(scope, receive)

        # Validate both tokens exist and match
        if not cookie_token or not header_token:
            raise CSRFTokenError("CSRF token missing")

        if cookie_token != header_token:
            raise CSRFTokenError("CSRF token mismatch")

        # Validate token structure and expiration
        self.csrf.validate_token(cookie_token, session_id, rotate=False)

        # Validation successful
        await self.app(scope, receive, send)

    def _get_csrf_cookie(self, headers: Dict[bytes, bytes]) -> Optional[str]:
        """Extract CSRF token from cookie"""
        cookie_header = headers.get(b"cookie", b"").decode("utf-8")

        if not cookie_header:
            return None

        cookies = {}
        for cookie in cookie_header.split(";"):
            cookie = cookie.strip()
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                cookies[name] = value

        return cookies.get(self.config.cookie_name)
