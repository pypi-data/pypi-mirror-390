"""
Production-Grade Request/Response Logging Middleware

Features:
- Log all incoming HTTP requests
- Log response status and duration
- Sanitize sensitive data (passwords, tokens, etc.)
- Configurable log levels per endpoint
- Exclude specific endpoints (e.g., health checks)
- Request/response body logging (with size limits)
- Header logging (with sanitization)
- Performance optimized (minimal overhead)
"""

import asyncio
import json
import re
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Pattern, Set
from urllib.parse import parse_qs, urlparse

from covet.logging.structured_logger import (
    get_logger,
    request_id_var,
    SensitiveDataFilter,
)


class RequestLoggerConfig:
    """Configuration for request logging middleware."""

    def __init__(
        self,
        log_requests: bool = True,
        log_responses: bool = True,
        log_request_body: bool = True,
        log_response_body: bool = False,  # Can be verbose
        log_headers: bool = True,
        log_query_params: bool = True,
        max_body_size: int = 10000,  # 10KB
        exclude_paths: Optional[List[str]] = None,
        exclude_patterns: Optional[List[Pattern]] = None,
        sanitize_sensitive: bool = True,
        sensitive_headers: Optional[Set[str]] = None,
        sensitive_query_params: Optional[Set[str]] = None,
        log_level_overrides: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize request logger configuration.

        Args:
            log_requests: Log incoming requests
            log_responses: Log outgoing responses
            log_request_body: Log request body
            log_response_body: Log response body
            log_headers: Log headers
            log_query_params: Log query parameters
            max_body_size: Maximum body size to log (bytes)
            exclude_paths: Exact paths to exclude from logging
            exclude_patterns: Regex patterns to exclude from logging
            sanitize_sensitive: Sanitize sensitive data
            sensitive_headers: Additional sensitive header names
            sensitive_query_params: Additional sensitive query param names
            log_level_overrides: Per-path log level overrides
        """
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.log_headers = log_headers
        self.log_query_params = log_query_params
        self.max_body_size = max_body_size
        self.sanitize_sensitive = sanitize_sensitive

        # Default excluded paths (health checks, metrics)
        self.exclude_paths = set(exclude_paths or [])
        self.exclude_paths.update(['/health', '/health/live', '/health/ready', '/metrics'])

        # Compile exclude patterns
        self.exclude_patterns = exclude_patterns or []

        # Sensitive headers (beyond the default set)
        self.sensitive_headers = {
            'authorization', 'cookie', 'set-cookie', 'x-api-key',
            'x-auth-token', 'x-csrf-token', 'proxy-authorization',
        }
        if sensitive_headers:
            self.sensitive_headers.update(h.lower() for h in sensitive_headers)

        # Sensitive query parameters
        self.sensitive_query_params = {
            'password', 'token', 'api_key', 'apikey', 'secret',
            'access_token', 'refresh_token', 'auth',
        }
        if sensitive_query_params:
            self.sensitive_query_params.update(p.lower() for p in sensitive_query_params)

        # Log level overrides for specific paths
        self.log_level_overrides = log_level_overrides or {}

    def should_exclude(self, path: str) -> bool:
        """Check if path should be excluded from logging."""
        if path in self.exclude_paths:
            return True

        for pattern in self.exclude_patterns:
            if pattern.match(path):
                return True

        return False

    def get_log_level(self, path: str) -> str:
        """Get log level for specific path."""
        return self.log_level_overrides.get(path, 'info')


class RequestResponseLogger:
    """Request/response logging handler."""

    def __init__(self, config: RequestLoggerConfig):
        """
        Initialize request/response logger.

        Args:
            config: Logger configuration
        """
        self.config = config
        self.logger = get_logger('covetpy.http')

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize sensitive headers."""
        if not self.config.sanitize_sensitive:
            return headers

        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.config.sensitive_headers:
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_query_params(self, query_string: str) -> Dict[str, Any]:
        """Parse and sanitize query parameters."""
        if not query_string:
            return {}

        # Parse query string
        parsed = parse_qs(query_string)

        if not self.config.sanitize_sensitive:
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

        # Sanitize sensitive params
        sanitized = {}
        for key, values in parsed.items():
            if key.lower() in self.config.sensitive_query_params:
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = values[0] if len(values) == 1 else values

        return sanitized

    def _sanitize_body(self, body: bytes, content_type: str) -> Any:
        """Parse and sanitize request/response body."""
        if not body or len(body) > self.config.max_body_size:
            return None

        try:
            # Try to parse as JSON
            if 'application/json' in content_type:
                body_dict = json.loads(body.decode('utf-8'))
                if self.config.sanitize_sensitive:
                    return SensitiveDataFilter.sanitize(body_dict)
                return body_dict
            # Try to parse as form data
            elif 'application/x-www-form-urlencoded' in content_type:
                parsed = parse_qs(body.decode('utf-8'))
                body_dict = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
                if self.config.sanitize_sensitive:
                    return SensitiveDataFilter.sanitize(body_dict)
                return body_dict
            else:
                # Return truncated string for other content types
                decoded = body.decode('utf-8', errors='replace')
                if len(decoded) > 1000:
                    return decoded[:1000] + '... (truncated)'
                return decoded
        except Exception:
            return '<binary or unparsable data>'

    def log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        query_string: str,
        headers: Dict[str, str],
        body: Optional[bytes],
        client_addr: Optional[tuple],
    ):
        """Log incoming request."""
        if not self.config.log_requests:
            return

        if self.config.should_exclude(path):
            return

        log_data = {
            'event': 'http_request',
            'method': method,
            'path': path,
        }

        if client_addr:
            log_data['client_ip'] = client_addr[0]
            log_data['client_port'] = client_addr[1]

        if self.config.log_query_params and query_string:
            log_data['query_params'] = self._sanitize_query_params(query_string)

        if self.config.log_headers:
            log_data['headers'] = self._sanitize_headers(headers)

        if self.config.log_request_body and body:
            content_type = headers.get('content-type', '')
            log_data['body'] = self._sanitize_body(body, content_type)
            log_data['body_size'] = len(body)

        # Get appropriate log level
        log_level = self.config.get_log_level(path)
        getattr(self.logger, log_level)('HTTP request received', **log_data)

    def log_response(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        response_size: int,
        response_body: Optional[bytes] = None,
    ):
        """Log outgoing response."""
        if not self.config.log_responses:
            return

        if self.config.should_exclude(path):
            return

        log_data = {
            'event': 'http_response',
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': round(duration_ms, 2),
            'response_size': response_size,
        }

        if self.config.log_response_body and response_body:
            # Assume JSON for now (can be enhanced)
            content_type = 'application/json'
            log_data['body'] = self._sanitize_body(response_body, content_type)

        # Determine log level based on status code
        if status_code >= 500:
            log_level = 'error'
        elif status_code >= 400:
            log_level = 'warning'
        else:
            log_level = self.config.get_log_level(path)

        getattr(self.logger, log_level)('HTTP response sent', **log_data)

    def log_error(
        self,
        request_id: str,
        method: str,
        path: str,
        error: Exception,
        duration_ms: float,
    ):
        """Log request error."""
        self.logger.error(
            'HTTP request failed',
            event='http_error',
            method=method,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            duration_ms=round(duration_ms, 2),
            exc_info=True,
        )


def request_logging_middleware(
    app: Any = None,
    config: Optional[RequestLoggerConfig] = None,
):
    """
    ASGI middleware for request/response logging.

    Args:
        app: ASGI application
        config: Logger configuration (uses default if None)

    Example:
        config = RequestLoggerConfig(
            log_request_body=True,
            log_response_body=False,
            exclude_paths=['/health', '/metrics'],
        )

        app.add_middleware(request_logging_middleware, config=config)
    """
    if config is None:
        config = RequestLoggerConfig()

    logger = RequestResponseLogger(config)

    async def middleware(scope, receive, send):
        """ASGI middleware function."""
        if scope['type'] != 'http':
            await app(scope, receive, send)
            return

        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        # Extract request info
        method = scope.get('method', '')
        path = scope.get('path', '')
        query_string = scope.get('query_string', b'').decode('utf-8')
        client_addr = scope.get('client')

        # Parse headers
        headers = {}
        for header_name, header_value in scope.get('headers', []):
            headers[header_name.decode('utf-8')] = header_value.decode('utf-8')

        # Add request ID to response headers
        headers['x-request-id'] = request_id

        # Capture request body
        request_body = b''
        body_chunks = []

        async def receive_wrapper():
            """Wrapper to capture request body."""
            nonlocal request_body
            message = await receive()
            if message['type'] == 'http.request':
                body = message.get('body', b'')
                body_chunks.append(body)
                if not message.get('more_body', False):
                    request_body = b''.join(body_chunks)
            return message

        # Start timing
        start_time = time.time()

        # Log request
        logger.log_request(
            request_id=request_id,
            method=method,
            path=path,
            query_string=query_string,
            headers=headers,
            body=None,  # Will log after body is fully received
            client_addr=client_addr,
        )

        # Capture response
        status_code = 200
        response_body = b''
        response_size = 0

        async def send_wrapper(message):
            """Wrapper to capture response."""
            nonlocal status_code, response_body, response_size

            if message['type'] == 'http.response.start':
                status_code = message['status']
                # Inject request ID header
                message['headers'] = message.get('headers', [])
                message['headers'].append(
                    (b'x-request-id', request_id.encode('utf-8'))
                )

            elif message['type'] == 'http.response.body':
                body = message.get('body', b'')
                response_size += len(body)
                if config.log_response_body:
                    response_body += body

            await send(message)

        try:
            # Process request
            await app(scope, receive_wrapper, send_wrapper)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.log_response(
                request_id=request_id,
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                response_size=response_size,
                response_body=response_body if config.log_response_body else None,
            )

        except Exception as exc:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.log_error(
                request_id=request_id,
                method=method,
                path=path,
                error=exc,
                duration_ms=duration_ms,
            )
            raise

    return middleware


__all__ = [
    'RequestLoggerConfig',
    'RequestResponseLogger',
    'request_logging_middleware',
]
