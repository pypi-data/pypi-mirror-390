"""
GraphQL WebSocket Protocol (graphql-ws)

Implements graphql-ws protocol for GraphQL subscriptions over WebSocket.
Follows: https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Dict, Optional

import strawberry

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """GraphQL-WS message types."""

    # Client messages
    CONNECTION_INIT = "connection_init"
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    COMPLETE = "complete"

    # Server messages
    CONNECTION_ACK = "connection_ack"
    NEXT = "next"
    ERROR = "error"
    COMPLETE_SERVER = "complete"


@dataclass
class GraphQLWSMessage:
    """GraphQL-WS protocol message."""

    type: MessageType
    id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        """Convert to JSON string."""
        message = {"type": self.type.value}
        if self.id is not None:
            message["id"] = self.id
        if self.payload is not None:
            message["payload"] = self.payload
        return json.dumps(message)

    @classmethod
    def from_json(cls, data: str) -> "GraphQLWSMessage":
        """Parse from JSON string."""
        try:
            obj = json.loads(data)
            return cls(
                type=MessageType(obj["type"]),
                id=obj.get("id"),
                payload=obj.get("payload"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid GraphQL-WS message: {e}")


class GraphQLWSProtocol:
    """
    GraphQL-WS protocol handler.

    Manages WebSocket connections for GraphQL subscriptions.
    """

    def __init__(
        self,
        schema: strawberry.Schema,
        context_factory: Optional[Any] = None,
        connection_init_timeout: float = 3.0,
    ):
        """
        Initialize protocol handler.

        Args:
            schema: Strawberry schema
            context_factory: Factory for creating GraphQL context
            connection_init_timeout: Timeout for connection initialization
        """
        self.schema = schema
        self.context_factory = context_factory
        self.connection_init_timeout = connection_init_timeout

        # Active subscriptions per connection
        self.subscriptions: Dict[str, Dict[str, asyncio.Task]] = {}

    async def handle_connection(
        self,
        websocket: Any,
        connection_id: str,
    ):
        """
        Handle WebSocket connection.

        Args:
            websocket: WebSocket connection
            connection_id: Unique connection ID
        """
        self.subscriptions[connection_id] = {}

        try:
            # Wait for connection_init with timeout
            try:
                init_message = await asyncio.wait_for(
                    self._receive_message(websocket),
                    timeout=self.connection_init_timeout,
                )

                if init_message.type != MessageType.CONNECTION_INIT:
                    await self._send_message(
                        websocket,
                        GraphQLWSMessage(
                            type=MessageType.ERROR,
                            payload={"message": "First message must be connection_init"},
                        ),
                    )
                    return

                # Send connection_ack
                await self._send_message(
                    websocket,
                    GraphQLWSMessage(type=MessageType.CONNECTION_ACK),
                )

            except asyncio.TimeoutError:
                logger.warning(f"Connection {connection_id} timed out waiting for init")
                return

            # Handle messages
            while True:
                message = await self._receive_message(websocket)
                await self._handle_message(websocket, connection_id, message)

        except asyncio.CancelledError:
            logger.info(f"Connection {connection_id} cancelled")
        except Exception as e:
            logger.error(f"Error in connection {connection_id}: {e}")
        finally:
            # Cleanup subscriptions
            await self._cleanup_connection(connection_id)

    async def _handle_message(
        self,
        websocket: Any,
        connection_id: str,
        message: GraphQLWSMessage,
    ):
        """Handle incoming message."""

        if message.type == MessageType.PING:
            # Respond with pong
            await self._send_message(
                websocket,
                GraphQLWSMessage(type=MessageType.PONG),
            )

        elif message.type == MessageType.PONG:
            # Ignore pong
            pass

        elif message.type == MessageType.SUBSCRIBE:
            # Start subscription
            if not message.id:
                logger.warning("SUBSCRIBE message missing id")
                return

            await self._start_subscription(
                websocket,
                connection_id,
                message.id,
                message.payload or {},
            )

        elif message.type == MessageType.COMPLETE:
            # Stop subscription
            if message.id:
                await self._stop_subscription(connection_id, message.id)

    async def _start_subscription(
        self,
        websocket: Any,
        connection_id: str,
        subscription_id: str,
        payload: Dict[str, Any],
    ):
        """Start GraphQL subscription."""

        query = payload.get("query")
        variables = payload.get("variables")
        operation_name = payload.get("operationName")

        if not query:
            await self._send_message(
                websocket,
                GraphQLWSMessage(
                    type=MessageType.ERROR,
                    id=subscription_id,
                    payload={"message": "Missing query"},
                ),
            )
            return

        # Create context
        context = self.context_factory() if self.context_factory else None

        # Create subscription task
        task = asyncio.create_task(
            self._run_subscription(
                websocket,
                subscription_id,
                query,
                variables,
                operation_name,
                context,
            )
        )

        self.subscriptions[connection_id][subscription_id] = task

    async def _run_subscription(
        self,
        websocket: Any,
        subscription_id: str,
        query: str,
        variables: Optional[Dict[str, Any]],
        operation_name: Optional[str],
        context: Any,
    ):
        """Run GraphQL subscription and send results."""
        try:
            # Execute subscription
            async for result in self.schema.subscribe(
                query,
                variable_values=variables,
                operation_name=operation_name,
                context_value=context,
            ):
                # Send result
                payload = {"data": result.data}
                if result.errors:
                    payload["errors"] = [{"message": str(err)} for err in result.errors]

                await self._send_message(
                    websocket,
                    GraphQLWSMessage(
                        type=MessageType.NEXT,
                        id=subscription_id,
                        payload=payload,
                    ),
                )

            # Send complete
            await self._send_message(
                websocket,
                GraphQLWSMessage(
                    type=MessageType.COMPLETE_SERVER,
                    id=subscription_id,
                ),
            )

        except Exception as e:
            # Send error
            await self._send_message(
                websocket,
                GraphQLWSMessage(
                    type=MessageType.ERROR,
                    id=subscription_id,
                    payload={"message": str(e)},
                ),
            )

    async def _stop_subscription(
        self,
        connection_id: str,
        subscription_id: str,
    ):
        """Stop subscription."""
        if connection_id in self.subscriptions:
            if subscription_id in self.subscriptions[connection_id]:
                task = self.subscriptions[connection_id][subscription_id]
                task.cancel()
                del self.subscriptions[connection_id][subscription_id]

    async def _cleanup_connection(self, connection_id: str):
        """Cleanup connection subscriptions."""
        if connection_id in self.subscriptions:
            for task in self.subscriptions[connection_id].values():
                task.cancel()
            del self.subscriptions[connection_id]

    async def _send_message(self, websocket: Any, message: GraphQLWSMessage):
        """Send message over WebSocket."""
        await websocket.send_text(message.to_json())

    async def _receive_message(self, websocket: Any) -> GraphQLWSMessage:
        """Receive message from WebSocket."""
        data = await websocket.receive_text()
        return GraphQLWSMessage.from_json(data)


class SubscriptionServer:
    """
    GraphQL subscription server.

    High-level interface for GraphQL subscriptions over WebSocket.
    """

    def __init__(
        self,
        schema: strawberry.Schema,
        context_factory: Optional[Any] = None,
    ):
        """
        Initialize subscription server.

        Args:
            schema: Strawberry schema
            context_factory: Context factory
        """
        self.protocol = GraphQLWSProtocol(schema, context_factory)
        self._connection_counter = 0

    async def handle_websocket(self, websocket: Any):
        """
        Handle WebSocket connection.

        Args:
            websocket: WebSocket connection (ASGI WebSocket)
        """
        # Generate connection ID
        self._connection_counter += 1
        connection_id = f"conn_{self._connection_counter}"

        # Accept connection
        await websocket.accept(subprotocol="graphql-transport-ws")

        try:
            # Handle protocol
            await self.protocol.handle_connection(websocket, connection_id)
        finally:
            # Close connection
            await websocket.close()


def create_subscription_server(
    schema: strawberry.Schema,
    context_factory: Optional[Any] = None,
) -> SubscriptionServer:
    """
    Create subscription server.

    Args:
        schema: Strawberry schema
        context_factory: Context factory

    Returns:
        Subscription server instance
    """
    return SubscriptionServer(schema, context_factory)


__all__ = [
    "GraphQLWSProtocol",
    "SubscriptionServer",
    "GraphQLWSMessage",
    "MessageType",
    "create_subscription_server",
]
