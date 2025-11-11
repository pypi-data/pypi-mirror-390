"""
Production-Grade WebSocket Message Router

This module provides event-based message routing with:
- Event handler registration (@ws.on("event_type"))
- Request/response pattern with message IDs
- Binary message support
- Message validation (Pydantic schemas)
- Error handling and error messages
- Middleware support
- Message acknowledgements
- Structured error responses
"""

import asyncio
import inspect
import json
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

try:
    from pydantic import BaseModel, ValidationError

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object
    ValidationError = Exception

from .connection import WebSocketConnection
from .protocol import BinaryMessage, JSONMessage, TextMessage, WebSocketMessage

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Standard message types."""

    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    ACK = "ack"


@dataclass
class RoutedMessage:
    """Represents a routed message with metadata."""

    message_id: str
    event_type: str
    data: Any
    message_type: MessageType = MessageType.EVENT
    timestamp: float = 0.0
    correlation_id: Optional[str] = None
    sender_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message_id": self.message_id,
            "event_type": self.event_type,
            "data": self.data,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "sender_id": self.sender_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutedMessage":
        """Create from dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            event_type=data.get("event_type", "unknown"),
            data=data.get("data", {}),
            message_type=MessageType(data.get("message_type", MessageType.EVENT.value)),
            timestamp=data.get("timestamp", time.time()),
            correlation_id=data.get("correlation_id"),
            sender_id=data.get("sender_id"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ErrorResponse:
    """Structured error response."""

    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_code": self.error_code,
            "error_message": self.error_message,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class EventHandler:
    """
    Wraps an event handler function with metadata.

    Supports:
    - Synchronous and asynchronous handlers
    - Input validation with Pydantic
    - Middleware
    - Error handling
    """

    def __init__(
        self,
        func: Callable,
        event_type: str,
        schema: Optional[type[BaseModel]] = None,
        middleware: Optional[List[Callable]] = None,
        validate_input: bool = True,
    ):
        self.func = func
        self.event_type = event_type
        self.schema = schema
        self.middleware = middleware or []
        self.validate_input = validate_input
        self.is_async = asyncio.iscoroutinefunction(func)

        # Statistics
        self.call_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0

    async def __call__(
        self,
        connection: WebSocketConnection,
        message: RoutedMessage,
    ) -> Any:
        """Execute the handler."""
        self.call_count += 1
        start_time = time.time()

        try:
            # Validate input
            if self.validate_input and self.schema and HAS_PYDANTIC:
                try:
                    validated_data = self.schema(**message.data)
                    message.data = validated_data
                except ValidationError as e:
                    self.error_count += 1
                    raise ValueError(f"Validation error: {e}")

            # Apply middleware
            for middleware in self.middleware:
                if asyncio.iscoroutinefunction(middleware):
                    await middleware(connection, message)
                else:
                    middleware(connection, message)

            # Call handler
            if self.is_async:
                result = await self.func(connection, message)
            else:
                result = self.func(connection, message)

            # Update stats
            self.total_execution_time += time.time() - start_time

            return result

        except Exception as e:
            self.error_count += 1
            self.total_execution_time += time.time() - start_time
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics."""
        avg_time = 0.0
        if self.call_count > 0:
            avg_time = self.total_execution_time / self.call_count

        return {
            "event_type": self.event_type,
            "call_count": self.call_count,
            "error_count": self.error_count,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": avg_time,
            "success_rate": 1.0 - (self.error_count / max(self.call_count, 1)),
        }


class MessageRouter:
    """
    Event-based message router for WebSocket connections.

    Provides:
    - Event handler registration by event type
    - Request/response pattern with correlation IDs
    - Message validation
    - Error handling
    - Middleware support
    - Binary message routing
    """

    def __init__(self):
        self._handlers: Dict[str, EventHandler] = {}
        self._middleware: List[Callable] = []
        self._pending_responses: Dict[str, asyncio.Future] = {}

        # Statistics
        self.total_messages_routed = 0
        self.total_errors = 0

    def on(
        self,
        event_type: str,
        schema: Optional[type[BaseModel]] = None,
        middleware: Optional[List[Callable]] = None,
        validate_input: bool = True,
    ):
        """
        Decorator to register an event handler.

        Usage:
            @router.on("chat_message")
            async def handle_chat(connection, message):
                await connection.send_json({"echo": message.data})

            @router.on("user_update", schema=UserUpdateSchema)
            async def handle_update(connection, message):
                # message.data is validated UserUpdateSchema
                pass
        """

        def decorator(func: Callable) -> Callable:
            handler = EventHandler(
                func=func,
                event_type=event_type,
                schema=schema,
                middleware=middleware,
                validate_input=validate_input,
            )
            self._handlers[event_type] = handler
            logger.info(f"Registered handler for event: {event_type}")
            return func

        return decorator

    def register_handler(
        self,
        event_type: str,
        handler: Callable,
        schema: Optional[type[BaseModel]] = None,
        middleware: Optional[List[Callable]] = None,
    ):
        """Register an event handler programmatically."""
        event_handler = EventHandler(
            func=handler,
            event_type=event_type,
            schema=schema,
            middleware=middleware,
        )
        self._handlers[event_type] = event_handler
        logger.info(f"Registered handler for event: {event_type}")

    def add_middleware(self, middleware: Callable):
        """Add global middleware."""
        self._middleware.append(middleware)
        logger.debug(f"Added global middleware: {middleware.__name__}")

    async def route_message(
        self,
        connection: WebSocketConnection,
        raw_message: WebSocketMessage,
    ) -> Optional[Any]:
        """
        Route a message to the appropriate handler.

        Args:
            connection: WebSocket connection
            raw_message: Raw WebSocket message

        Returns:
            Handler result if any
        """
        self.total_messages_routed += 1

        try:
            # Parse message
            if isinstance(raw_message, (TextMessage, JSONMessage)):
                # Parse JSON message
                if isinstance(raw_message, TextMessage):
                    try:
                        data = json.loads(raw_message.content)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON message: {e}")
                        await self._send_error(
                            connection,
                            "INVALID_JSON",
                            "Invalid JSON format",
                            {"error": str(e)},
                        )
                        return None
                else:
                    data = raw_message.data

                # Convert to RoutedMessage
                routed_message = RoutedMessage.from_dict(data)
                routed_message.sender_id = connection.id

            elif isinstance(raw_message, BinaryMessage):
                # Handle binary messages
                routed_message = RoutedMessage(
                    message_id=str(uuid.uuid4()),
                    event_type="binary",
                    data=raw_message.data,
                    sender_id=connection.id,
                )

            else:
                logger.error(f"Unknown message type: {type(raw_message)}")
                return None

            # Apply global middleware
            for middleware in self._middleware:
                if asyncio.iscoroutinefunction(middleware):
                    await middleware(connection, routed_message)
                else:
                    middleware(connection, routed_message)

            # Handle response messages
            if routed_message.message_type == MessageType.RESPONSE:
                await self._handle_response(routed_message)
                return None

            # Find handler
            handler = self._handlers.get(routed_message.event_type)
            if not handler:
                logger.warning(f"No handler for event: {routed_message.event_type}")
                await self._send_error(
                    connection,
                    "UNKNOWN_EVENT",
                    f"No handler for event: {routed_message.event_type}",
                    {"event_type": routed_message.event_type},
                    correlation_id=routed_message.message_id,
                )
                return None

            # Execute handler
            result = await handler(connection, routed_message)

            # Send acknowledgement if requested
            if routed_message.message_type == MessageType.REQUEST:
                await self._send_response(
                    connection,
                    routed_message.message_id,
                    result,
                )

            return result

        except Exception as e:
            self.total_errors += 1
            logger.error(f"Error routing message: {e}", exc_info=True)

            # Send error response
            await self._send_error(
                connection,
                "HANDLER_ERROR",
                str(e),
                {"traceback": str(e)},
            )

            return None

    async def send_request(
        self,
        connection: WebSocketConnection,
        event_type: str,
        data: Any,
        timeout: float = 30.0,
    ) -> Any:
        """
        Send a request and wait for response.

        Args:
            connection: WebSocket connection
            event_type: Event type
            data: Request data
            timeout: Response timeout in seconds

        Returns:
            Response data

        Raises:
            asyncio.TimeoutError: If no response within timeout
        """
        message_id = str(uuid.uuid4())

        # Create future for response
        future = asyncio.Future()
        self._pending_responses[message_id] = future

        # Send request
        request = RoutedMessage(
            message_id=message_id,
            event_type=event_type,
            data=data,
            message_type=MessageType.REQUEST,
            sender_id=connection.id,
        )

        await connection.send_json(request.to_dict())

        try:
            # Wait for response
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        finally:
            # Clean up
            self._pending_responses.pop(message_id, None)

    async def _handle_response(self, message: RoutedMessage):
        """Handle response message."""
        if message.correlation_id in self._pending_responses:
            future = self._pending_responses[message.correlation_id]
            if not future.done():
                future.set_result(message.data)

    async def _send_response(
        self,
        connection: WebSocketConnection,
        correlation_id: str,
        data: Any,
    ):
        """Send response message."""
        response = RoutedMessage(
            message_id=str(uuid.uuid4()),
            event_type="response",
            data=data,
            message_type=MessageType.RESPONSE,
            correlation_id=correlation_id,
        )

        try:
            await connection.send_json(response.to_dict())
        except Exception as e:
            logger.error(f"Error sending response: {e}")

    async def _send_error(
        self,
        connection: WebSocketConnection,
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """Send error message."""
        error = ErrorResponse(
            error_code=error_code,
            error_message=error_message,
            details=details,
        )

        message = RoutedMessage(
            message_id=str(uuid.uuid4()),
            event_type="error",
            data=error.to_dict(),
            message_type=MessageType.ERROR,
            correlation_id=correlation_id,
        )

        try:
            await connection.send_json(message.to_dict())
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

    async def send_ack(
        self,
        connection: WebSocketConnection,
        message_id: str,
    ):
        """Send acknowledgement."""
        ack = RoutedMessage(
            message_id=str(uuid.uuid4()),
            event_type="ack",
            data={"acked": message_id},
            message_type=MessageType.ACK,
            correlation_id=message_id,
        )

        try:
            await connection.send_json(ack.to_dict())
        except Exception as e:
            logger.error(f"Error sending ack: {e}")

    def get_registered_events(self) -> List[str]:
        """Get list of registered event types."""
        return list(self._handlers.keys())

    def get_handler_stats(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific handler."""
        handler = self._handlers.get(event_type)
        if handler:
            return handler.get_stats()
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            "total_messages_routed": self.total_messages_routed,
            "total_errors": self.total_errors,
            "registered_handlers": len(self._handlers),
            "pending_responses": len(self._pending_responses),
            "handlers": {
                event_type: handler.get_stats() for event_type, handler in self._handlers.items()
            },
        }


# Global router instance
global_router = MessageRouter()


# Convenience decorators using global router
def on(event_type: str, schema: Optional[type[BaseModel]] = None, **kwargs):
    """Decorator for global router."""
    return global_router.on(event_type, schema=schema, **kwargs)


def add_middleware(middleware: Callable):
    """Add middleware to global router."""
    global_router.add_middleware(middleware)


# Example middleware
async def logging_middleware(connection: WebSocketConnection, message: RoutedMessage):
    """Log all messages."""
    logger.debug(
        f"Message from {connection.id}: "
        f"type={message.event_type}, "
        f"message_id={message.message_id}"
    )


async def auth_middleware(connection: WebSocketConnection, message: RoutedMessage):
    """Require authentication for all messages."""
    if not connection.is_authenticated:
        raise Exception("Authentication required")


async def rate_limit_middleware(connection: WebSocketConnection, message: RoutedMessage):
    """Apply rate limiting (placeholder)."""
    # Rate limiting logic would go here
    pass


__all__ = [
    "MessageType",
    "RoutedMessage",
    "ErrorResponse",
    "EventHandler",
    "MessageRouter",
    "global_router",
    "on",
    "add_middleware",
    "logging_middleware",
    "auth_middleware",
    "rate_limit_middleware",
]
