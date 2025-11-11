"""
WebSocket Client Implementation

This module provides a complete WebSocket client with auto-reconnection,
connection pooling, and production-ready features.
"""

import asyncio
import json
import logging
import ssl
import time
import weakref
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlparse

try:
    import websockets

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

from .protocol import (
    BinaryMessage,
    CloseCode,
    ConnectionClosed,
    JSONMessage,
    OpCode,
    TextMessage,
    WebSocketMessage,
    WebSocketProtocol,
    WebSocketState,
)

logger = logging.getLogger(__name__)


class ClientState(Enum):
    """WebSocket client states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    CLOSING = "closing"
    CLOSED = "closed"


@dataclass
class ClientConfig:
    """Configuration for WebSocket client."""

    # Connection settings
    connect_timeout: float = 10.0
    ping_interval: float = 20.0
    ping_timeout: float = 10.0
    close_timeout: float = 10.0

    # Reconnection settings
    auto_reconnect: bool = True
    max_reconnect_attempts: int = 10
    reconnect_delay: float = 1.0
    max_reconnect_delay: float = 60.0
    reconnect_backoff: float = 2.0

    # SSL settings
    ssl_context: Optional[ssl.SSLContext] = None

    # Headers and auth
    headers: Dict[str, str] = field(default_factory=dict)
    subprotocols: List[str] = field(default_factory=list)

    # Message handling
    max_queue_size: int = 1000
    message_timeout: float = 30.0

    # Compression
    compression: Optional[str] = None


class WebSocketClient:
    """
    Production-ready WebSocket client with auto-reconnection.

    Features:
    - Automatic reconnection with exponential backoff
    - Message queuing during disconnection
    - Ping/pong heartbeat
    - SSL/TLS support
    - Event-driven architecture
    - Connection pooling support
    """

    def __init__(self, url: str, config: ClientConfig = None):
        self.url = url
        self.config = config or ClientConfig()

        # Parse URL
        self.parsed_url = urlparse(url)
        if self.parsed_url.scheme not in ("ws", "wss"):
            raise ValueError(f"Invalid WebSocket URL: {url}")

        # Connection state
        self.state = ClientState.DISCONNECTED
        self._websocket = None
        self._protocol = WebSocketProtocol(is_client=True)

        # Reconnection state
        self._reconnect_attempts = 0
        self._should_reconnect = True
        self._reconnect_task: Optional[asyncio.Task] = None

        # Message handling
        self._send_queue = asyncio.Queue(maxsize=self.config.max_queue_size)
        self._receive_queue = asyncio.Queue(maxsize=self.config.max_queue_size)
        self._send_task: Optional[asyncio.Task] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        # Event handlers
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        self.on_message: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_reconnect: Optional[Callable] = None

        # Statistics
        self.connect_time: Optional[float] = None
        self.disconnect_time: Optional[float] = None
        self.total_connections = 0
        self.total_reconnections = 0
        self.messages_sent = 0
        self.messages_received = 0

        logger.debug(f"WebSocket client created for {url}")

    async def connect(self) -> bool:
        """Connect to the WebSocket server."""
        if self.state in (ClientState.CONNECTED, ClientState.CONNECTING):
            return True

        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library is required for WebSocket client")

        self.state = ClientState.CONNECTING

        try:
            # Prepare connection parameters
            extra_headers = self.config.headers.copy()

            # Connect to WebSocket
            self._websocket = await asyncio.wait_for(
                websockets.connect(
                    self.url,
                    ssl=self.config.ssl_context,
                    extra_headers=extra_headers,
                    subprotocols=self.config.subprotocols,
                    ping_interval=self.config.ping_interval,
                    ping_timeout=self.config.ping_timeout,
                    close_timeout=self.config.close_timeout,
                    compression=self.config.compression,
                ),
                timeout=self.config.connect_timeout,
            )

            # Update state and stats
            self.state = ClientState.CONNECTED
            self.connect_time = time.time()
            self.total_connections += 1
            self._reconnect_attempts = 0

            # Start background tasks
            self._start_background_tasks()

            # Call connect handler
            if self.on_connect:
                try:
                    await self.on_connect(self)
                except Exception as e:
                    logger.error(f"Error in connect handler: {e}")

            logger.info(f"WebSocket client connected to {self.url}")
            return True

        except Exception as e:
            self.state = ClientState.DISCONNECTED
            logger.error(f"Failed to connect to {self.url}: {e}")

            if self.on_error:
                try:
                    await self.on_error(self, e)
                except Exception:
                    # TODO: Add proper exception handling

                    # Start reconnection if enabled
                    pass
            if self.config.auto_reconnect and self._should_reconnect:
                await self._schedule_reconnect()

            return False

    async def disconnect(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = ""):
        """Disconnect from the WebSocket server."""
        if self.state in (ClientState.DISCONNECTED, ClientState.CLOSED):
            return

        self._should_reconnect = False
        self.state = ClientState.CLOSING

        # Cancel reconnection if in progress
        if self._reconnect_task:
            self._reconnect_task.cancel()
            self._reconnect_task = None

        # Stop background tasks
        await self._stop_background_tasks()

        # Close WebSocket connection
        if self._websocket:
            try:
                await self._websocket.close(code, reason)
            except Exception as e:
                logger.debug(f"Error closing WebSocket: {e}")
            self._websocket = None

        # Update state and stats
        self.state = ClientState.CLOSED
        self.disconnect_time = time.time()

        # Call disconnect handler
        if self.on_disconnect:
            try:
                await self.on_disconnect(self)
            except Exception as e:
                logger.error(f"Error in disconnect handler: {e}")

        logger.info(f"WebSocket client disconnected from {self.url}")

    async def _schedule_reconnect(self):
        """Schedule reconnection attempt."""
        if not self.config.auto_reconnect or not self._should_reconnect:
            return

        if self._reconnect_attempts >= self.config.max_reconnect_attempts:
            logger.error(f"Max reconnect attempts reached for {self.url}")
            self.state = ClientState.CLOSED
            return

        # Calculate delay with exponential backoff
        delay = min(
            self.config.reconnect_delay * (self.config.reconnect_backoff**self._reconnect_attempts),
            self.config.max_reconnect_delay,
        )

        self._reconnect_attempts += 1
        self.state = ClientState.RECONNECTING

        logger.info(f"Scheduling reconnect attempt {self._reconnect_attempts} in {delay:.1f}s")

        # Schedule reconnection
        self._reconnect_task = asyncio.create_task(self._reconnect_after_delay(delay))

    async def _reconnect_after_delay(self, delay: float):
        """Reconnect after a delay."""
        try:
            await asyncio.sleep(delay)

            if self._should_reconnect:
                logger.info(f"Attempting to reconnect to {self.url}")

                if await self.connect():
                    self.total_reconnections += 1

                    if self.on_reconnect:
                        try:
                            await self.on_reconnect(self)
                        except Exception as e:
                            logger.error(f"Error in reconnect handler: {e}")

                else:
                    # Reconnection failed, schedule another attempt
                    await self._schedule_reconnect()

        except asyncio.CancelledError:
            logger.debug("Reconnection cancelled")
        except Exception as e:
            logger.error(f"Error during reconnection: {e}")
            await self._schedule_reconnect()

    def _start_background_tasks(self):
        """Start background tasks."""
        self._send_task = asyncio.create_task(self._send_worker())
        self._receive_task = asyncio.create_task(self._receive_worker())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_worker())

    async def _stop_background_tasks(self):
        """Stop background tasks."""
        tasks = [self._send_task, self._receive_task, self._heartbeat_task]

        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    # TODO: Add proper exception handling

                    pass
        self._send_task = None
        self._receive_task = None
        self._heartbeat_task = None

    async def _send_worker(self):
        """Background task to send queued messages."""
        try:
            while self.state == ClientState.CONNECTED and self._websocket:
                try:
                    # Get message from queue
                    message = await asyncio.wait_for(self._send_queue.get(), timeout=1.0)

                    if message is None:  # Shutdown signal
                        break

                    # Send message
                    if isinstance(message, str):
                        await self._websocket.send(message)
                    elif isinstance(message, bytes):
                        await self._websocket.send(message)
                    else:
                        # JSON message
                        await self._websocket.send(json.dumps(message))

                    self.messages_sent += 1

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in send worker: {e}")
                    break

        except Exception as e:
            logger.error(f"Send worker error: {e}")

    async def _receive_worker(self):
        """Background task to receive messages."""
        try:
            while self.state == ClientState.CONNECTED and self._websocket:
                try:
                    # Receive message
                    raw_message = await self._websocket.recv()

                    # Create message object
                    if isinstance(raw_message, str):
                        try:
                            # Try to parse as JSON
                            data = json.loads(raw_message)
                            message = JSONMessage(data)
                        except json.JSONDecodeError:
                            # Fall back to text message
                            message = TextMessage(raw_message)
                    else:
                        # Binary message
                        message = BinaryMessage(raw_message)

                    self.messages_received += 1

                    # Queue message for processing
                    try:
                        self._receive_queue.put_nowait(message)
                    except asyncio.QueueFull:
                        logger.warning("Receive queue full, dropping message")

                    # Call message handler
                    if self.on_message:
                        try:
                            await self.on_message(self, message)
                        except Exception as e:
                            logger.error(f"Error in message handler: {e}")

                except websockets.exceptions.ConnectionClosed as e:
                    logger.info(f"WebSocket connection closed: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error in receive worker: {e}")
                    break

        except Exception as e:
            logger.error(f"Receive worker error: {e}")

        finally:
            # Connection lost, handle reconnection
            if self.state == ClientState.CONNECTED:
                self.state = ClientState.DISCONNECTED
                self._websocket = None

                if self.config.auto_reconnect and self._should_reconnect:
                    await self._schedule_reconnect()

    async def _heartbeat_worker(self):
        """Background task for heartbeat."""
        try:
            while self.state == ClientState.CONNECTED and self._websocket:
                try:
                    await asyncio.sleep(self.config.ping_interval)

                    if self.state == ClientState.CONNECTED and self._websocket:
                        # Ping is handled automatically by websockets library

                        pass
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                    break

        except Exception as e:
            logger.error(f"Heartbeat worker error: {e}")

    async def send_text(self, text: str):
        """Send text message."""
        if self.state != ClientState.CONNECTED:
            raise ConnectionError("WebSocket not connected")

        try:
            await self._send_queue.put(text)
        except asyncio.QueueFull:
            raise Exception("Send queue full")

    async def send_bytes(self, data: bytes):
        """Send binary message."""
        if self.state != ClientState.CONNECTED:
            raise ConnectionError("WebSocket not connected")

        try:
            await self._send_queue.put(data)
        except asyncio.QueueFull:
            raise Exception("Send queue full")

    async def send_json(self, data: Any):
        """Send JSON message."""
        if self.state != ClientState.CONNECTED:
            raise ConnectionError("WebSocket not connected")

        try:
            await self._send_queue.put(data)
        except asyncio.QueueFull:
            raise Exception("Send queue full")

    async def receive(self, timeout: float = None) -> Optional[WebSocketMessage]:
        """Receive a message."""
        if timeout is None:
            timeout = self.config.message_timeout

        try:
            return await asyncio.wait_for(self._receive_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def ping(self, data: bytes = b"") -> float:
        """Send ping and measure latency."""
        if self.state != ClientState.CONNECTED or not self._websocket:
            raise ConnectionError("WebSocket not connected")

        start_time = time.time()
        pong_waiter = await self._websocket.ping(data)
        await pong_waiter
        return time.time() - start_time

    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.state == ClientState.CONNECTED

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        uptime = None
        if self.connect_time:
            uptime = time.time() - self.connect_time

        return {
            "url": self.url,
            "state": self.state.value,
            "connected": self.is_connected(),
            "connect_time": self.connect_time,
            "disconnect_time": self.disconnect_time,
            "uptime": uptime,
            "total_connections": self.total_connections,
            "total_reconnections": self.total_reconnections,
            "reconnect_attempts": self._reconnect_attempts,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "send_queue_size": self._send_queue.qsize(),
            "receive_queue_size": self._receive_queue.qsize(),
        }


class WebSocketClientPool:
    """
    Pool of WebSocket clients for load balancing and redundancy.

    Features:
    - Multiple connections to different endpoints
    - Automatic failover
    - Load balancing
    - Health monitoring
    """

    def __init__(self, urls: List[str], config: ClientConfig = None):
        self.urls = urls
        self.config = config or ClientConfig()
        self.clients: List[WebSocketClient] = []
        self._current_index = 0
        self._lock = asyncio.Lock()

        # Create clients
        for url in urls:
            client = WebSocketClient(url, self.config)
            self.clients.append(client)

        # Statistics
        self.total_messages_sent = 0
        self.total_messages_received = 0

    async def connect_all(self) -> int:
        """Connect all clients in the pool."""
        tasks = [client.connect() for client in self.clients]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        connected_count = sum(1 for result in results if result is True)
        logger.info(f"Connected {connected_count}/{len(self.clients)} clients in pool")

        return connected_count

    async def disconnect_all(self):
        """Disconnect all clients in the pool."""
        tasks = [client.disconnect() for client in self.clients]
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("All clients in pool disconnected")

    def get_next_client(self) -> Optional[WebSocketClient]:
        """Get next available client using round-robin."""
        connected_clients = [c for c in self.clients if c.is_connected()]

        if not connected_clients:
            return None

        # Round-robin selection
        client = connected_clients[self._current_index % len(connected_clients)]
        self._current_index += 1

        return client

    def get_random_client(self) -> Optional[WebSocketClient]:
        """Get random available client."""
        import random

        connected_clients = [c for c in self.clients if c.is_connected()]

        if not connected_clients:
            return None

        return random.choice(connected_clients)

    def get_least_loaded_client(self) -> Optional[WebSocketClient]:
        """Get client with least messages sent."""
        connected_clients = [c for c in self.clients if c.is_connected()]

        if not connected_clients:
            return None

        return min(connected_clients, key=lambda c: c.messages_sent)

    async def send_text(self, text: str, strategy: str = "round_robin") -> bool:
        """Send text message using specified strategy."""
        client = self._get_client_by_strategy(strategy)
        if not client:
            return False

        try:
            await client.send_text(text)
            self.total_messages_sent += 1
            return True
        except Exception as e:
            logger.error(f"Failed to send message via {client.url}: {e}")
            return False

    async def send_json(self, data: Any, strategy: str = "round_robin") -> bool:
        """Send JSON message using specified strategy."""
        client = self._get_client_by_strategy(strategy)
        if not client:
            return False

        try:
            await client.send_json(data)
            self.total_messages_sent += 1
            return True
        except Exception as e:
            logger.error(f"Failed to send message via {client.url}: {e}")
            return False

    def _get_client_by_strategy(self, strategy: str) -> Optional[WebSocketClient]:
        """Get client based on strategy."""
        if strategy == "round_robin":
            return self.get_next_client()
        elif strategy == "random":
            return self.get_random_client()
        elif strategy == "least_loaded":
            return self.get_least_loaded_client()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def get_connected_count(self) -> int:
        """Get number of connected clients."""
        return sum(1 for client in self.clients if client.is_connected())

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        client_stats = [client.get_stats() for client in self.clients]

        return {
            "total_clients": len(self.clients),
            "connected_clients": self.get_connected_count(),
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "clients": client_stats,
        }


# Context managers
@asynccontextmanager
async def websocket_client(url: str, config: ClientConfig = None):
    """Context manager for WebSocket client."""
    client = WebSocketClient(url, config)

    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()


@asynccontextmanager
async def websocket_client_pool(urls: List[str], config: ClientConfig = None):
    """Context manager for WebSocket client pool."""
    pool = WebSocketClientPool(urls, config)

    try:
        await pool.connect_all()
        yield pool
    finally:
        await pool.disconnect_all()


# Utility functions
async def test_connection(url: str, timeout: float = 10.0) -> bool:
    """Test WebSocket connection to a URL."""
    try:
        config = ClientConfig(connect_timeout=timeout, auto_reconnect=False)
        async with websocket_client(url, config) as client:
            return client.is_connected()
    except Exception as e:
        logger.error(f"Connection test failed for {url}: {e}")
        return False


async def ping_server(url: str, count: int = 3) -> Dict[str, Any]:
    """Ping WebSocket server and measure latency."""
    latencies = []
    errors = 0

    try:
        config = ClientConfig(auto_reconnect=False)
        async with websocket_client(url, config) as client:
            if not client.is_connected():
                return {"error": "Failed to connect"}

            for i in range(count):
                try:
                    latency = await client.ping()
                    latencies.append(latency * 1000)  # Convert to ms
                except Exception as e:
                    errors += 1
                    logger.debug(f"Ping {i+1} failed: {e}")

        if latencies:
            return {
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "avg_latency_ms": sum(latencies) / len(latencies),
                "packet_loss": errors / count,
                "successful_pings": len(latencies),
                "total_pings": count,
            }
        else:
            return {"error": "All pings failed"}

    except Exception as e:
        return {"error": str(e)}
