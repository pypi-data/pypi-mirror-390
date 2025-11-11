"""
Production-Grade Structured Logging System for CovetPy

Features:
- JSON structured logging with async support
- Request ID tracking and correlation
- Multiple log outputs (stdout, file, syslog)
- Log rotation support
- Context propagation
- Performance optimized (async queue)
- Sensitive data sanitization
"""

import asyncio
import contextvars
import json
import logging
import logging.handlers
import os
import sys
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from queue import Queue
from threading import Thread

# Context variables for request tracking
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'request_id', default=None
)
user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'user_id', default=None
)
session_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'session_id', default=None
)


class SensitiveDataFilter:
    """Filter to sanitize sensitive data from logs."""

    SENSITIVE_KEYS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey',
        'access_token', 'refresh_token', 'auth', 'authorization', 'cookie',
        'session', 'csrf', 'credit_card', 'ssn', 'private_key', 'salt'
    }

    @classmethod
    def sanitize(cls, data: Any) -> Any:
        """Sanitize sensitive data from dictionaries, lists, and strings."""
        if isinstance(data, dict):
            return {
                k: '***REDACTED***' if any(s in k.lower() for s in cls.SENSITIVE_KEYS)
                else cls.sanitize(v)
                for k, v in data.items()
            }
        elif isinstance(data, (list, tuple)):
            return [cls.sanitize(item) for item in data]
        elif isinstance(data, str):
            # Don't modify strings directly - too aggressive
            return data
        else:
            return data


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Produces consistent JSON output with standard fields:
    - timestamp: ISO 8601 timestamp
    - level: Log level (DEBUG, INFO, etc.)
    - logger: Logger name
    - message: Log message
    - request_id: Request correlation ID
    - user_id: User identifier (if authenticated)
    - session_id: Session identifier
    - service: Service name
    - environment: Deployment environment
    - extra: Any additional fields
    """

    def __init__(
        self,
        service_name: str = 'covetpy',
        environment: str = 'production',
        include_extra: bool = True,
        sanitize_sensitive: bool = True,
    ):
        """
        Initialize JSON formatter.

        Args:
            service_name: Name of the service
            environment: Deployment environment (dev, staging, production)
            include_extra: Include extra fields from LogRecord
            sanitize_sensitive: Sanitize sensitive data
        """
        super().__init__()
        self.service_name = service_name
        self.environment = environment
        self.include_extra = include_extra
        self.sanitize_sensitive = sanitize_sensitive

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log structure
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'service': self.service_name,
            'environment': self.environment,
        }

        # Add context variables
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_data['user_id'] = user_id

        session_id = session_id_var.get()
        if session_id:
            log_data['session_id'] = session_id

        # Add location info
        log_data['location'] = {
            'file': record.pathname,
            'line': record.lineno,
            'function': record.funcName,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else 'Unknown',
                'message': str(record.exc_info[1]) if record.exc_info[1] else '',
                'traceback': traceback.format_exception(*record.exc_info),
            }

        # Add extra fields from LogRecord
        if self.include_extra:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in logging.LogRecord.__dict__ and not key.startswith('_'):
                    extra_fields[key] = value

            if extra_fields:
                log_data['extra'] = extra_fields

        # Sanitize sensitive data
        if self.sanitize_sensitive:
            log_data = SensitiveDataFilter.sanitize(log_data)

        return json.dumps(log_data, default=str, ensure_ascii=False)


class HumanReadableFormatter(logging.Formatter):
    """
    Human-readable formatter for development.

    Format: [2024-01-01 12:00:00.123] INFO [request_id] logger: message
    """

    def __init__(self):
        """Initialize human-readable formatter."""
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as human-readable text."""
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Build request context
        context_parts = []
        request_id = request_id_var.get()
        if request_id:
            context_parts.append(f'req={request_id[:8]}')

        user_id = user_id_var.get()
        if user_id:
            context_parts.append(f'user={user_id}')

        context = f"[{', '.join(context_parts)}]" if context_parts else ''

        # Format message
        message = f"[{timestamp}] {record.levelname:8s} {context} {record.name}: {record.getMessage()}"

        # Add exception if present
        if record.exc_info:
            message += '\n' + ''.join(traceback.format_exception(*record.exc_info))

        return message


class AsyncLogHandler(logging.Handler):
    """
    Async log handler that doesn't block request processing.

    Logs are queued and processed in a background thread.
    """

    def __init__(self, target_handler: logging.Handler, queue_size: int = 10000):
        """
        Initialize async log handler.

        Args:
            target_handler: Actual handler to send logs to
            queue_size: Maximum queue size (logs dropped if exceeded)
        """
        super().__init__()
        self.target_handler = target_handler
        self.queue: Queue = Queue(maxsize=queue_size)
        self.worker = Thread(target=self._worker, daemon=True)
        self.worker.start()

    def emit(self, record: logging.LogRecord):
        """Emit log record to queue."""
        try:
            self.queue.put_nowait(record)
        except:
            # Queue full - drop log to avoid blocking
            pass

    def _worker(self):
        """Background worker to process log queue."""
        while True:
            try:
                record = self.queue.get()
                if record is None:
                    break
                self.target_handler.emit(record)
            except Exception:
                # Silently ignore errors in log handler
                pass

    def close(self):
        """Close handler and flush queue."""
        self.queue.put(None)
        self.worker.join(timeout=5)
        self.target_handler.close()
        super().close()


class StructuredLogger:
    """
    Production-grade structured logger with comprehensive features.

    Example:
        logger = StructuredLogger(
            name='my-service',
            level='INFO',
            format='json',
            log_file='/var/log/app.log',
            enable_rotation=True,
        )

        # Set request context
        with logger.request_context(request_id='abc123', user_id='user456'):
            logger.info('User action', action='login', ip='1.2.3.4')
    """

    def __init__(
        self,
        name: str = 'covetpy',
        level: str = 'INFO',
        format: str = 'json',  # 'json' or 'human'
        log_file: Optional[str] = None,
        enable_rotation: bool = True,
        max_bytes: int = 100 * 1024 * 1024,  # 100MB
        backup_count: int = 10,
        enable_syslog: bool = False,
        syslog_address: Union[str, tuple] = '/dev/log',
        async_logging: bool = True,
        service_name: str = 'covetpy',
        environment: str = None,
        sanitize_sensitive: bool = True,
    ):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format: Output format ('json' or 'human')
            log_file: Path to log file (None = stdout only)
            enable_rotation: Enable log rotation
            max_bytes: Max file size before rotation
            backup_count: Number of backup files to keep
            enable_syslog: Enable syslog output
            syslog_address: Syslog address
            async_logging: Use async logging (recommended for production)
            service_name: Service name for logs
            environment: Environment (dev, staging, prod) - auto-detected from COVET_ENV
            sanitize_sensitive: Sanitize sensitive data
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers.clear()
        self.logger.propagate = False

        # Auto-detect environment
        if environment is None:
            environment = os.getenv('COVET_ENV', os.getenv('ENVIRONMENT', 'production'))

        self.environment = environment
        self.service_name = service_name

        # Create formatter
        if format == 'json':
            formatter = JSONFormatter(
                service_name=service_name,
                environment=environment,
                sanitize_sensitive=sanitize_sensitive,
            )
        else:
            formatter = HumanReadableFormatter()

        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        if async_logging:
            console_handler = AsyncLogHandler(console_handler)

        self.logger.addHandler(console_handler)

        # File handler with rotation
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            if enable_rotation:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                )
            else:
                file_handler = logging.FileHandler(log_file)

            file_handler.setFormatter(formatter)

            if async_logging:
                file_handler = AsyncLogHandler(file_handler)

            self.logger.addHandler(file_handler)

        # Syslog handler
        if enable_syslog:
            try:
                syslog_handler = logging.handlers.SysLogHandler(address=syslog_address)
                syslog_handler.setFormatter(formatter)

                if async_logging:
                    syslog_handler = AsyncLogHandler(syslog_handler)

                self.logger.addHandler(syslog_handler)
            except Exception as e:
                self.logger.warning(f"Failed to initialize syslog handler: {e}")

    def request_context(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Context manager for request-scoped logging.

        Example:
            with logger.request_context(request_id='abc123', user_id='user456'):
                logger.info('Processing request')
        """
        return RequestContext(request_id, user_id, session_id)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)


class RequestContext:
    """Context manager for request-scoped logging context."""

    def __init__(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize request context.

        Args:
            request_id: Request correlation ID (auto-generated if None)
            user_id: User identifier
            session_id: Session identifier
        """
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.session_id = session_id
        self.tokens = []

    def __enter__(self):
        """Enter context."""
        self.tokens.append(request_id_var.set(self.request_id))
        if self.user_id:
            self.tokens.append(user_id_var.set(self.user_id))
        if self.session_id:
            self.tokens.append(session_id_var.set(self.session_id))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        for token in self.tokens:
            token.var.reset(token)
        return False


# Global logger instance
_global_logger: Optional[StructuredLogger] = None


def configure_logging(
    level: str = None,
    format: str = None,
    log_file: str = None,
    **kwargs
) -> StructuredLogger:
    """
    Configure global structured logger.

    Auto-detects configuration from environment variables:
    - LOG_LEVEL or COVET_LOG_LEVEL
    - LOG_FORMAT (json or human)
    - LOG_FILE
    - COVET_ENV (for environment)

    Args:
        level: Log level (overrides env var)
        format: Format (overrides env var)
        log_file: Log file path (overrides env var)
        **kwargs: Additional arguments for StructuredLogger

    Returns:
        Configured logger instance
    """
    global _global_logger

    # Auto-detect from environment
    level = level or os.getenv('LOG_LEVEL', os.getenv('COVET_LOG_LEVEL', 'INFO'))
    format = format or os.getenv('LOG_FORMAT', 'json')
    log_file = log_file or os.getenv('LOG_FILE')

    _global_logger = StructuredLogger(
        level=level,
        format=format,
        log_file=log_file,
        **kwargs
    )

    return _global_logger


def get_logger(name: str = 'covetpy') -> StructuredLogger:
    """
    Get logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = configure_logging()

    return _global_logger


__all__ = [
    'StructuredLogger',
    'RequestContext',
    'JSONFormatter',
    'HumanReadableFormatter',
    'AsyncLogHandler',
    'SensitiveDataFilter',
    'configure_logging',
    'get_logger',
    'request_id_var',
    'user_id_var',
    'session_id_var',
]
