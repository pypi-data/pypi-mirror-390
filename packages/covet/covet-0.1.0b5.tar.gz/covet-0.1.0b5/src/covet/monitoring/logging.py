"""
Structured Logging for CovetPy

JSON-formatted logging for production environments with:
- Request/response logging
- Error logging with stack traces
- Security event logging
- Performance logging
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict

from pythonjsonlogger import jsonlogger


class CovetJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ):
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["service"] = "covetpy"

        # Add context if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "ip_address"):
            log_record["ip_address"] = record.ip_address

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }


def configure_structured_logging(
    level: str = "INFO", format_type: str = "json", log_file: str = None
) -> logging.Logger:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 'json' for production, 'human' for development
        log_file: Optional file path for logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("covetpy")
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers = []  # Clear existing handlers

    if format_type == "json":
        formatter = CovetJSONFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "covetpy") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


# Request logging middleware


async def logging_middleware(app, handler):
    """Middleware for request/response logging."""
    logger = get_logger("covetpy.http")

    async def middleware(scope, receive, send):
        if scope["type"] != "http":
            return await handler(scope, receive, send)

        import time
        import uuid

        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Log request
        logger.info(
            "HTTP request started",
            extra={
                "request_id": request_id,
                "method": scope["method"],
                "path": scope["path"],
                "query_string": scope["query_string"].decode(),
                "client": scope["client"],
            },
        )

        status_code = 200

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await handler(scope, receive, send_wrapper)
        except Exception as exc:
            logger.error(
                "HTTP request failed",
                extra={
                    "request_id": request_id,
                    "method": scope["method"],
                    "path": scope["path"],
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise
        finally:
            duration = time.time() - start_time

            # Log response
            logger.info(
                "HTTP request completed",
                extra={
                    "request_id": request_id,
                    "method": scope["method"],
                    "path": scope["path"],
                    "status_code": status_code,
                    "duration_seconds": round(duration, 4),
                },
            )

    return middleware


__all__ = ["configure_structured_logging", "get_logger", "logging_middleware"]
