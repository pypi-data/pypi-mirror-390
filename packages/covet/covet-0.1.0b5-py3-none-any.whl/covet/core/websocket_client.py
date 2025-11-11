"""
WebSocket Client Implementation

This module provides a production-ready WebSocket client with auto-reconnection,
heartbeat, and comprehensive error handling for testing and development.
"""

import asyncio
import logging
import ssl
import time
import weakref
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlparse

import aiohttp

from .websocket_impl import (
    BinaryMessage,
    CloseCode,
    ConnectionClosed,
    JSONMessage,
    OpCode,
    TextMessage,
    WebSocketFrame,
    WebSocketHandshake,
    WebSocketMessage,
    WebSocketProtocol,
    WebSocketState,
    generate_websocket_key,
)

logger = logging.getLogger(__name__)


@dataclass
class ClientConfig:
    """WebSocket client configuration."""

    # Connection
    max_message_size: int = 1024 * 1024
    connect_timeout: float = 10.0
    close_timeout: float = 5.0

    # Heartbeat
    ping_interval: float = 30.0
    ping_timeout: float = 10.0

    # Reconnection
    auto_reconnect: bool = True
    max_reconnect_attempts: int = 5
    reconnect_delay: float = 1.0
    max_reconnect_delay: float = 60.0
    backoff_factor: float = 2.0

    # Headers
    extra_headers: Dict[str, str] = field(default_factory=dict)
    user_agent: str = "CovetPy-WebSocket-Client/1.0"

    # SSL
    ssl_context: Optional[ssl.SSLContext] = None
    verify_ssl: bool = True

    # Compression
    enable_compression: bool = False
    compression_threshold: int = 1024


class WebSocketClient:
    """
    High-performance WebSocket client with auto-reconnection and heartbeat.

    Features:
    - Automatic reconnection with exponential backoff
    - Ping/pong heartbeat
    - Message type handlers
    - Event callbacks
    - Compression support
    - SSL/TLS support
    """

    def __init__(self, url: str, config: Optional[ClientConfig] = None):
        self.url = url
        self.config = config or ClientConfig()

        # Parse URL
        self.parsed_url = urlparse(url)
        if self.parsed_url.scheme not in ("ws", "wss"):
            raise ValueError("URL must use ws:// or wss:// scheme")

        # Connection state
        self.state = WebSocketState.CLOSED
        self.protocol = WebSocketProtocol(
            is_client=True, max_message_size=self.config.max_message_size
        )

        # aiohttp session
        self._session: Optional[aiohttp.ClientSession] = None
        self._websocket: Optional[aiohttp.ClientWebSocketResponse] = None

        # Event handlers
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        self.on_message: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        # Message handlers
        self._message_handlers: Dict[str, Callable] = {}

        # Reconnection state
        self._reconnect_attempts = 0
        self._reconnect_task: Optional[asyncio.Task] = None
        self._should_reconnect = True

        # Background tasks
        self._tasks: List[asyncio.Task] = []
        self._ping_task: Optional[asyncio.Task] = None

        # Statistics
        self.connect_time: Optional[float] = None
        self.last_ping: Optional[float] = None
        self.last_pong: Optional[float] = None
        self.messages_sent = 0
        self.messages_received = 0
        self.reconnect_count = 0

    async def connect(self) -> None:
        """Connect to WebSocket server."""
        if self.state in (WebSocketState.CONNECTING, WebSocketState.OPEN):
            return

        self.state = WebSocketState.CONNECTING

        try:
            # Create aiohttp session if needed
            if not self._session:
                timeout = aiohttp.ClientTimeout(total=self.config.connect_timeout)
                self._session = aiohttp.ClientSession(
                    timeout=timeout, headers=self._build_headers()
                )

            # Connect to WebSocket
            self._websocket = await self._session.ws_connect(
                self.url,
                ssl=self._build_ssl_context(),
                compress=self.config.enable_compression,
                max_msg_size=self.config.max_message_size,
            )

            self.state = WebSocketState.OPEN
            self.protocol.state = WebSocketState.OPEN
            self.connect_time = time.time()
            self._reconnect_attempts = 0

            # Start background tasks
            self._start_tasks()

            # Call connect callback
            if self.on_connect:
                try:
                    await self.on_connect(self)
                except Exception as e:
                    logger.error(f"Error in on_connect callback: {e}", exc_info=True)

            logger.info(f"WebSocket connected to {self.url}")

        except Exception as e:
            self.state = WebSocketState.CLOSED
            logger.error(f"Failed to connect to {self.url}: {e}")

            if self.config.auto_reconnect and self._should_reconnect:
                await self._schedule_reconnect()
            else:
                raise

    async def close(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = "") -> None:
        """Close WebSocket connection."""
        if self.state == WebSocketState.CLOSED:
            return

        self._should_reconnect = False
        self.state = WebSocketState.CLOSING

        # Cancel reconnect task
        if self._reconnect_task:
            self._reconnect_task.cancel()

        # Send close frame if connected
        if self._websocket and not self._websocket.closed:
            try:
                await self._websocket.close(code=code, message=reason.encode("utf-8"))
            except Exception as e:
                logger.warning(f"Error sending close frame: {e}")

        await self._cleanup()

        logger.info(f"WebSocket closed (code={code}, reason='{reason}')")

    async def send_text(self, data: str) -> None:
        """Send text message."""
        if self.state != WebSocketState.OPEN:
            raise ConnectionClosed("Connection not open")

        try:
            await self._websocket.send_str(data)
            self.messages_sent += 1
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            await self._handle_connection_error(e)

    async def send_bytes(self, data: bytes) -> None:
        """Send binary message."""
        if self.state != WebSocketState.OPEN:
            raise ConnectionClosed("Connection not open")

        try:
            await self._websocket.send_bytes(data)
            self.messages_sent += 1
        except Exception as e:
            logger.error(f"Error sending binary message: {e}")
            await self._handle_connection_error(e)

    async def send_json(self, data: Any) -> None:
        """Send JSON message."""
        if self.state != WebSocketState.OPEN:
            raise ConnectionClosed("Connection not open")

        try:
            import json

            json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
            await self._websocket.send_str(json_str)
            self.messages_sent += 1
        except Exception as e:
            logger.error(f"Error sending JSON message: {e}")
            await self._handle_connection_error(e)

    async def ping(self, data: bytes = b"") -> None:
        """Send ping frame."""
        if self.state != WebSocketState.OPEN:
            raise ConnectionClosed("Connection not open")

        try:
            await self._websocket.ping(data)
            self.last_ping = time.time()
        except Exception as e:
            logger.error(f"Error sending ping: {e}")
            await self._handle_connection_error(e)

    def set_message_handler(self, message_type: str, handler: Callable) -> None:
        """Set handler for specific message type."""
        self._message_handlers[message_type] = handler

    async def wait_until_closed(self) -> None:
        """Wait until connection is closed."""
        while self.state != WebSocketState.CLOSED:
            await asyncio.sleep(0.1)

    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for WebSocket handshake."""
        headers = {
            "User-Agent": self.config.user_agent,
        }
        headers.update(self.config.extra_headers)
        return headers

    def _build_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Build SSL context for secure connections."""
        if self.parsed_url.scheme != "wss":
            return None

        if self.config.ssl_context:
            return self.config.ssl_context

        if not self.config.verify_ssl:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context

        return None

    def _start_tasks(self) -> None:
        """Start background tasks."""
        # Message receiving task
        task = asyncio.create_task(self._message_receiver())
        self._tasks.append(task)

        # Ping task
        if self.config.ping_interval > 0:
            self._ping_task = asyncio.create_task(self._ping_handler())
            self._tasks.append(self._ping_task)

    async def _message_receiver(self) -> None:
        """Receive and handle messages."""
        try:
            async for message in self._websocket:
                if message.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_text_message(message.data)
                elif message.type == aiohttp.WSMsgType.BINARY:
                    await self._handle_binary_message(message.data)
                elif message.type == aiohttp.WSMsgType.PONG:
                    self.last_pong = time.time()
                    await self._handle_pong_message(message.data)
                elif message.type == aiohttp.WSMsgType.CLOSE:
                    logger.info(f"Received close frame: {message.data} {message.extra}")
                    break
                elif message.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {message.data}")
                    break

        except Exception as e:
            logger.error(f"Error in message receiver: {e}", exc_info=True)
            await self._handle_connection_error(e)

        finally:
            if self.state == WebSocketState.OPEN:
                await self._handle_unexpected_close()

    async def _handle_text_message(self, data: str) -> None:
        """Handle text message."""
        try:
            self.messages_received += 1
            message = TextMessage(content=data)
            await self._dispatch_message(message)
        except Exception as e:
            logger.error(f"Error handling text message: {e}", exc_info=True)
            if self.on_error:
                await self.on_error(self, e)

    async def _handle_binary_message(self, data: bytes) -> None:
        """Handle binary message."""
        try:
            self.messages_received += 1
            message = BinaryMessage(data=data)
            await self._dispatch_message(message)
        except Exception as e:
            logger.error(f"Error handling binary message: {e}", exc_info=True)
            if self.on_error:
                await self.on_error(self, e)

    async def _handle_pong_message(self, data: bytes) -> None:
        """Handle pong message."""
        logger.debug(f"Received pong: {data}")

    async def _dispatch_message(self, message: WebSocketMessage) -> None:
        """Dispatch message to handlers."""
        # Call general message handler
        if self.on_message:
            await self.on_message(self, message)

        # Call specific message type handler
        handler = self._message_handlers.get(message.message_type)
        if handler:
            await handler(self, message)

    async def _ping_handler(self) -> None:
        """Handle periodic ping/pong for keepalive."""
        while self.state == WebSocketState.OPEN:
            try:
                await asyncio.sleep(self.config.ping_interval)

                if self.state != WebSocketState.OPEN:
                    break

                # Send ping
                ping_data = str(int(time.time())).encode()
                await self.ping(ping_data)

                # Check for pong timeout (simplified)
                # In a full implementation, you'd track individual pings

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ping handler: {e}", exc_info=True)
                break

    async def _handle_connection_error(self, error: Exception) -> None:
        """Handle connection error."""
        logger.error(f"Connection error: {error}")

        self.state = WebSocketState.CLOSED

        if self.on_error:
            try:
                await self.on_error(self, error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}", exc_info=True)

        if self.config.auto_reconnect and self._should_reconnect:
            await self._schedule_reconnect()

    async def _handle_unexpected_close(self) -> None:
        """Handle unexpected connection close."""
        logger.warning("WebSocket connection closed unexpectedly")

        self.state = WebSocketState.CLOSED

        if self.on_disconnect:
            try:
                await self.on_disconnect(self)
            except Exception as e:
                logger.error(f"Error in disconnect callback: {e}", exc_info=True)

        if self.config.auto_reconnect and self._should_reconnect:
            await self._schedule_reconnect()

    async def _schedule_reconnect(self) -> None:
        """Schedule reconnection attempt."""
        if self._reconnect_attempts >= self.config.max_reconnect_attempts:
            logger.error(f"Max reconnect attempts ({self.config.max_reconnect_attempts}) reached")
            return

        # Calculate delay with exponential backoff
        delay = min(
            self.config.reconnect_delay * (self.config.backoff_factor**self._reconnect_attempts),
            self.config.max_reconnect_delay,
        )

        self._reconnect_attempts += 1
        self.reconnect_count += 1

        logger.info(f"Reconnecting in {delay:.1f} seconds (attempt {self._reconnect_attempts})")

        self._reconnect_task = asyncio.create_task(self._reconnect_after_delay(delay))

    async def _reconnect_after_delay(self, delay: float) -> None:
        """Reconnect after delay."""
        try:
            await asyncio.sleep(delay)
            if self._should_reconnect:
                await self.connect()
        except asyncio.CancelledError:
            logger.debug("Reconnect cancelled")
        except Exception as e:
            logger.error(f"Error during reconnect: {e}", exc_info=True)
            if self.config.auto_reconnect and self._should_reconnect:
                await self._schedule_reconnect()

    async def _cleanup(self) -> None:
        """Clean up resources."""
        self.state = WebSocketState.CLOSED

        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        if self._ping_task:
            self._ping_task.cancel()

        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks.clear()

        # Close session
        if self._session:
            await self._session.close()
            self._session = None

        self._websocket = None

        # Call disconnect callback
        if self.on_disconnect:
            try:
                await self.on_disconnect(self)
            except Exception as e:
                logger.error(f"Error in disconnect callback: {e}", exc_info=True)

    def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            "state": self.state.value,
            "url": self.url,
            "connect_time": self.connect_time,
            "uptime": time.time() - self.connect_time if self.connect_time else 0,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "reconnect_count": self.reconnect_count,
            "reconnect_attempts": self._reconnect_attempts,
            "last_ping": self.last_ping,
            "last_pong": self.last_pong,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        """Async context manager exit."""
        await self.close()


class WebSocketClientPool:
    """Pool of WebSocket clients for load balancing and redundancy."""

    def __init__(self, urls: List[str], config: Optional[ClientConfig] = None):
        self.urls = urls
        self.config = config or ClientConfig()
        self.clients: List[WebSocketClient] = []
        self._current_index = 0

        # Create clients
        for url in urls:
            client = WebSocketClient(url, self.config)
            self.clients.append(client)

    async def connect_all(self) -> None:
        """Connect all clients."""
        tasks = [client.connect() for client in self.clients]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def close_all(self) -> None:
        """Close all clients."""
        tasks = [client.close() for client in self.clients]
        await asyncio.gather(*tasks, return_exceptions=True)

    def get_client(self) -> Optional[WebSocketClient]:
        """Get next available client (round-robin)."""
        for _ in range(len(self.clients)):
            client = self.clients[self._current_index]
            self._current_index = (self._current_index + 1) % len(self.clients)

            if client.state == WebSocketState.OPEN:
                return client

        return None

    async def broadcast(self, message: Union[str, bytes, Any]) -> int:
        """Broadcast message to all connected clients."""
        sent_count = 0

        for client in self.clients:
            if client.state == WebSocketState.OPEN:
                try:
                    if isinstance(message, str):
                        await client.send_text(message)
                    elif isinstance(message, bytes):
                        await client.send_bytes(message)
                    else:
                        await client.send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")

        return sent_count


# Context manager for easy client usage
@asynccontextmanager
async def websocket_client(url: str, config: Optional[ClientConfig] = None):
    """Context manager for WebSocket client."""
    client = WebSocketClient(url, config)
    try:
        await client.connect()
        yield client
    finally:
        await client.close()


# Export main components
__all__ = ["ClientConfig", "WebSocketClient", "WebSocketClientPool", "websocket_client"]
