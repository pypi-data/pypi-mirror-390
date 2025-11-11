"""
Live Data Streaming Example

This example demonstrates real-time data streaming using CovetPy's WebSocket
implementation with data channels, filtering, aggregation, and throttling.
"""

import asyncio
import json
import logging
import math
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from ..core.websocket_connection import WebSocketConnection, default_connection_manager
from ..core.websocket_impl import JSONMessage
from ..core.websocket_router import (
    WebSocketEndpoint,
    WebSocketRouter,
    on_connect,
    on_disconnect,
    on_json,
)

logger = logging.getLogger(__name__)


class DataStreamType(Enum):
    """Data stream types."""

    STOCK_PRICES = "stock_prices"
    SENSOR_DATA = "sensor_data"
    SYSTEM_METRICS = "system_metrics"
    USER_ACTIVITY = "user_activity"
    FINANCIAL_DATA = "financial_data"
    IOT_TELEMETRY = "iot_telemetry"
    REAL_TIME_ANALYTICS = "real_time_analytics"


class AggregationType(Enum):
    """Data aggregation types."""

    RAW = "raw"
    AVERAGE = "average"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    LAST = "last"
    MEDIAN = "median"


@dataclass
class DataPoint:
    """Individual data point."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stream_id: str = ""
    timestamp: float = field(default_factory=time.time)
    value: Union[int, float, str, Dict[str, Any]] = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "stream_id": self.stream_id,
            "timestamp": self.timestamp,
            "value": self.value,
            "metadata": self.metadata,
            "tags": self.tags,
            "formatted_time": datetime.fromtimestamp(self.timestamp).isoformat(),
        }


@dataclass
class StreamSubscription:
    """Data stream subscription configuration."""

    user_id: str
    stream_id: str
    filters: Dict[str, Any] = field(default_factory=dict)
    aggregation: AggregationType = AggregationType.RAW
    window_size: int = 1  # seconds
    throttle_rate: float = 0.1  # minimum seconds between updates
    max_points_per_update: int = 100
    active: bool = True
    last_update: float = field(default_factory=time.time)

    def should_send_update(self) -> bool:
        """Check if enough time has passed for next update."""
        return time.time() - self.last_update >= self.throttle_rate

    def matches_filters(self, data_point: DataPoint) -> bool:
        """Check if data point matches subscription filters."""
        if not self.filters:
            return True

        for key, expected_value in self.filters.items():
            if key == "tags":
                # Tag filtering
                for tag_key, tag_value in expected_value.items():
                    if data_point.tags.get(tag_key) != tag_value:
                        return False
            elif key == "value_range":
                # Value range filtering
                min_val, max_val = expected_value
                if isinstance(data_point.value, (int, float)):
                    if not (min_val <= data_point.value <= max_val):
                        return False
            elif key == "metadata":
                # Metadata filtering
                for meta_key, meta_value in expected_value.items():
                    if data_point.metadata.get(meta_key) != meta_value:
                        return False

        return True


@dataclass
class DataStream:
    """Data stream definition."""

    id: str
    name: str
    stream_type: DataStreamType
    description: str = ""
    unit: str = ""
    data_type: str = "number"  # number, string, object
    update_frequency: float = 1.0  # seconds
    retention_period: int = 3600  # seconds
    max_subscribers: int = 1000
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Runtime data
    subscribers: Set[str] = field(default_factory=set)
    data_buffer: List[DataPoint] = field(default_factory=list)
    last_update: float = field(default_factory=time.time)
    total_points: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.stream_type.value,
            "description": self.description,
            "unit": self.unit,
            "data_type": self.data_type,
            "update_frequency": self.update_frequency,
            "retention_period": self.retention_period,
            "max_subscribers": self.max_subscribers,
            "active": self.active,
            "metadata": self.metadata,
            "subscriber_count": len(self.subscribers),
            "buffer_size": len(self.data_buffer),
            "total_points": self.total_points,
            "last_update": self.last_update,
        }

    def add_data_point(self, data_point: DataPoint) -> None:
        """Add data point to stream buffer."""
        data_point.stream_id = self.id
        self.data_buffer.append(data_point)
        self.total_points += 1
        self.last_update = time.time()

        # Clean old data
        cutoff_time = time.time() - self.retention_period
        self.data_buffer = [dp for dp in self.data_buffer if dp.timestamp > cutoff_time]

    def get_recent_data(self, limit: int = 100) -> List[DataPoint]:
        """Get recent data points."""
        return self.data_buffer[-limit:] if self.data_buffer else []

    def add_subscriber(self, user_id: str) -> bool:
        """Add subscriber to stream."""
        if len(self.subscribers) >= self.max_subscribers:
            return False

        self.subscribers.add(user_id)
        return True

    def remove_subscriber(self, user_id: str) -> None:
        """Remove subscriber from stream."""
        self.subscribers.discard(user_id)


class DataAggregator:
    """Handles data aggregation for subscriptions."""

    @staticmethod
    def aggregate_data(
        data_points: List[DataPoint], aggregation: AggregationType, window_size: int = 1
    ) -> Optional[DataPoint]:
        """Aggregate data points according to aggregation type."""
        if not data_points:
            return None

        if aggregation == AggregationType.RAW:
            return data_points[-1]  # Return latest

        # Filter numeric values for mathematical aggregations
        numeric_values = []
        for dp in data_points:
            if isinstance(dp.value, (int, float)):
                numeric_values.append(dp.value)

        if not numeric_values and aggregation != AggregationType.COUNT:
            return data_points[-1]

        latest_point = data_points[-1]

        if aggregation == AggregationType.AVERAGE:
            value = sum(numeric_values) / len(numeric_values)
        elif aggregation == AggregationType.SUM:
            value = sum(numeric_values)
        elif aggregation == AggregationType.MIN:
            value = min(numeric_values)
        elif aggregation == AggregationType.MAX:
            value = max(numeric_values)
        elif aggregation == AggregationType.COUNT:
            value = len(data_points)
        elif aggregation == AggregationType.LAST:
            value = latest_point.value
        elif aggregation == AggregationType.MEDIAN:
            sorted_values = sorted(numeric_values)
            n = len(sorted_values)
            if n % 2 == 0:
                value = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
            else:
                value = sorted_values[n // 2]
        else:
            value = latest_point.value

        # Create aggregated data point
        return DataPoint(
            stream_id=latest_point.stream_id,
            timestamp=latest_point.timestamp,
            value=value,
            metadata={
                **latest_point.metadata,
                "aggregation": aggregation.value,
                "window_size": window_size,
                "points_count": len(data_points),
            },
            tags=latest_point.tags,
        )


class LiveDataManager:
    """Manages live data streams and subscriptions."""

    def __init__(self):
        self.streams: Dict[str, DataStream] = {}
        self.subscriptions: Dict[str, List[StreamSubscription]] = {}  # user_id -> subscriptions
        self.data_generators: Dict[str, asyncio.Task] = {}
        self.aggregator = DataAggregator()

        # Statistics
        self.total_data_points = 0
        self.total_updates_sent = 0
        self.start_time = time.time()

        # Create some example streams
        self._create_example_streams()

    def _create_example_streams(self):
        """Create example data streams."""
        # Stock prices
        stock_stream = DataStream(
            id="stock_prices",
            name="Stock Prices",
            stream_type=DataStreamType.STOCK_PRICES,
            description="Real-time stock price data",
            unit="USD",
            update_frequency=0.5,
        )
        self.add_stream(stock_stream)

        # System metrics
        metrics_stream = DataStream(
            id="system_metrics",
            name="System Metrics",
            stream_type=DataStreamType.SYSTEM_METRICS,
            description="Server performance metrics",
            unit="various",
            update_frequency=1.0,
        )
        self.add_stream(metrics_stream)

        # Sensor data
        sensor_stream = DataStream(
            id="temperature_sensor",
            name="Temperature Sensor",
            stream_type=DataStreamType.SENSOR_DATA,
            description="Temperature readings from IoT sensors",
            unit="°C",
            update_frequency=2.0,
        )
        self.add_stream(sensor_stream)

        # Start data generators
        self._start_data_generators()

    def add_stream(self, stream: DataStream) -> None:
        """Add a new data stream."""
        self.streams[stream.id] = stream
        logger.info(f"Added data stream: {stream.name} ({stream.id})")

    def get_stream(self, stream_id: str) -> Optional[DataStream]:
        """Get stream by ID."""
        return self.streams.get(stream_id)

    def list_streams(self) -> List[Dict[str, Any]]:
        """List all available streams."""
        return [stream.to_dict() for stream in self.streams.values()]

    def subscribe_to_stream(
        self,
        user_id: str,
        stream_id: str,
        filters: Optional[Dict[str, Any]] = None,
        aggregation: AggregationType = AggregationType.RAW,
        window_size: int = 1,
        throttle_rate: float = 0.1,
    ) -> bool:
        """Subscribe user to a data stream."""
        stream = self.get_stream(stream_id)
        if not stream or not stream.active:
            return False

        # Check subscriber limit
        if not stream.add_subscriber(user_id):
            return False

        # Create subscription
        subscription = StreamSubscription(
            user_id=user_id,
            stream_id=stream_id,
            filters=filters or {},
            aggregation=aggregation,
            window_size=window_size,
            throttle_rate=throttle_rate,
        )

        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = []

        self.subscriptions[user_id].append(subscription)

        logger.info(f"User {user_id} subscribed to stream {stream_id}")
        return True

    def unsubscribe_from_stream(self, user_id: str, stream_id: str) -> bool:
        """Unsubscribe user from a data stream."""
        if user_id not in self.subscriptions:
            return False

        # Remove subscription
        user_subscriptions = self.subscriptions[user_id]
        original_count = len(user_subscriptions)

        self.subscriptions[user_id] = [
            sub for sub in user_subscriptions if sub.stream_id != stream_id
        ]

        # Remove from stream subscribers
        stream = self.get_stream(stream_id)
        if stream:
            stream.remove_subscriber(user_id)

        removed = len(user_subscriptions) != original_count
        if removed:
            logger.info(f"User {user_id} unsubscribed from stream {stream_id}")

        return removed

    def get_user_subscriptions(self, user_id: str) -> List[StreamSubscription]:
        """Get all subscriptions for a user."""
        return self.subscriptions.get(user_id, [])

    async def add_data_point(self, stream_id: str, data_point: DataPoint) -> None:
        """Add data point to stream and notify subscribers."""
        stream = self.get_stream(stream_id)
        if not stream or not stream.active:
            return

        # Add to stream
        stream.add_data_point(data_point)
        self.total_data_points += 1

        # Notify subscribers
        await self._notify_stream_subscribers(stream_id, data_point)

    async def _notify_stream_subscribers(self, stream_id: str, data_point: DataPoint) -> None:
        """Notify all subscribers of a stream about new data."""
        stream = self.get_stream(stream_id)
        if not stream:
            return

        # Get all subscriptions for this stream
        relevant_subscriptions = []
        for user_id in stream.subscribers:
            user_subscriptions = self.subscriptions.get(user_id, [])
            for subscription in user_subscriptions:
                if subscription.stream_id == stream_id and subscription.active:
                    relevant_subscriptions.append(subscription)

        # Process each subscription
        for subscription in relevant_subscriptions:
            # Check throttle rate
            if not subscription.should_send_update():
                continue

            # Check filters
            if not subscription.matches_filters(data_point):
                continue

            # Prepare data for sending
            if subscription.aggregation == AggregationType.RAW:
                send_data = data_point
            else:
                # Get data for aggregation window
                window_start = time.time() - subscription.window_size
                window_data = [dp for dp in stream.data_buffer if dp.timestamp >= window_start]

                send_data = self.aggregator.aggregate_data(
                    window_data, subscription.aggregation, subscription.window_size
                )

                if not send_data:
                    continue

            # Send to user
            await self._send_data_to_user(subscription.user_id, send_data)
            subscription.last_update = time.time()
            self.total_updates_sent += 1

    async def _send_data_to_user(self, user_id: str, data_point: DataPoint) -> None:
        """Send data point to a specific user."""
        try:
            message_data = {"type": "data_update", "data": data_point.to_dict()}

            await default_connection_manager.broadcast_to_user(
                user_id, JSONMessage(data=message_data)
            )

        except Exception as e:
            logger.error(f"Error sending data to user {user_id}: {e}")

    def _start_data_generators(self):
        """Start data generators for example streams."""
        for stream_id in self.streams:
            if stream_id not in self.data_generators:
                task = asyncio.create_task(self._generate_data(stream_id))
                self.data_generators[stream_id] = task

    async def _generate_data(self, stream_id: str):
        """Generate sample data for a stream."""
        stream = self.get_stream(stream_id)
        if not stream:
            return

        try:
            while stream.active:
                # Generate data based on stream type
                if stream.stream_type == DataStreamType.STOCK_PRICES:
                    data_point = self._generate_stock_data(stream_id)
                elif stream.stream_type == DataStreamType.SYSTEM_METRICS:
                    data_point = self._generate_metrics_data(stream_id)
                elif stream.stream_type == DataStreamType.SENSOR_DATA:
                    data_point = self._generate_sensor_data(stream_id)
                else:
                    data_point = self._generate_random_data(stream_id)

                await self.add_data_point(stream_id, data_point)

                # Wait for next update
                await asyncio.sleep(stream.update_frequency)

        except asyncio.CancelledError:
            logger.info(f"Data generator for stream {stream_id} cancelled")
        except Exception as e:
            logger.error(f"Error in data generator for stream {stream_id}: {e}")

    def _generate_stock_data(self, stream_id: str) -> DataPoint:
        """Generate sample stock price data."""
        # Simple random walk
        base_price = 100.0
        change = random.uniform(-2.0, 2.0)
        price = max(10.0, base_price + change)

        return DataPoint(
            stream_id=stream_id,
            value=round(price, 2),
            metadata={
                "symbol": "AAPL",
                "volume": random.randint(1000, 10000),
                "change": round(change, 2),
                "change_percent": round((change / base_price) * 100, 2),
            },
            tags={"market": "NASDAQ", "sector": "technology"},
        )

    def _generate_metrics_data(self, stream_id: str) -> DataPoint:
        """Generate sample system metrics data."""
        metric_type = random.choice(["cpu", "memory", "disk", "network"])

        if metric_type == "cpu":
            value = random.uniform(10, 90)
            unit = "%"
        elif metric_type == "memory":
            value = random.uniform(4000, 16000)
            unit = "MB"
        elif metric_type == "disk":
            value = random.uniform(50, 95)
            unit = "%"
        else:  # network
            value = random.uniform(1, 100)
            unit = "Mbps"

        return DataPoint(
            stream_id=stream_id,
            value=round(value, 1),
            metadata={
                "metric_type": metric_type,
                "unit": unit,
                "hostname": "server-01",
            },
            tags={"environment": "production", "datacenter": "us-east-1"},
        )

    def _generate_sensor_data(self, stream_id: str) -> DataPoint:
        """Generate sample sensor data."""
        # Simulate temperature with daily cycle
        hour = datetime.now().hour
        base_temp = 20 + 10 * math.sin(2 * math.pi * hour / 24)
        temp = base_temp + random.uniform(-2, 2)

        return DataPoint(
            stream_id=stream_id,
            value=round(temp, 1),
            metadata={
                "sensor_id": "temp_001",
                "location": "office",
                "battery_level": random.randint(80, 100),
            },
            tags={"device_type": "temperature", "room": "conference_room_a"},
        )

    def _generate_random_data(self, stream_id: str) -> DataPoint:
        """Generate random data."""
        return DataPoint(
            stream_id=stream_id,
            value=random.uniform(0, 100),
            metadata={"generator": "random"},
            tags={"type": "synthetic"},
        )

    def get_stream_history(self, stream_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical data for a stream."""
        stream = self.get_stream(stream_id)
        if not stream:
            return []

        recent_data = stream.get_recent_data(limit)
        return [dp.to_dict() for dp in recent_data]

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        uptime = time.time() - self.start_time

        return {
            "total_streams": len(self.streams),
            "active_streams": sum(1 for s in self.streams.values() if s.active),
            "total_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "total_data_points": self.total_data_points,
            "total_updates_sent": self.total_updates_sent,
            "uptime_seconds": uptime,
            "data_points_per_second": (self.total_data_points / uptime if uptime > 0 else 0),
            "updates_per_second": self.total_updates_sent / uptime if uptime > 0 else 0,
            "stream_stats": {
                stream_id: {
                    "subscriber_count": len(stream.subscribers),
                    "buffer_size": len(stream.data_buffer),
                    "total_points": stream.total_points,
                }
                for stream_id, stream in self.streams.items()
            },
        }

    async def cleanup(self):
        """Clean up resources."""
        # Cancel all data generators
        for task in self.data_generators.values():
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.data_generators:
            await asyncio.gather(*self.data_generators.values(), return_exceptions=True)


# Global data manager
live_data_manager = LiveDataManager()


class LiveDataEndpoint(WebSocketEndpoint):
    """WebSocket endpoint for live data streaming."""

    def __init__(self):
        super().__init__()
        self.data_manager = live_data_manager

    @on_connect
    async def handle_connect(self, connection: WebSocketConnection):
        """Handle new connection."""
        await connection.accept()

        # Send welcome message with available streams
        await connection.send_json(
            {
                "type": "connected",
                "message": "Connected to live data service",
                "available_streams": self.data_manager.list_streams(),
                "server_time": time.time(),
            }
        )

        logger.info(f"New live data connection: {connection.info.id}")

    @on_disconnect
    async def handle_disconnect(self, connection: WebSocketConnection):
        """Handle connection disconnect."""
        if connection.info.authenticated and connection.info.user_id:
            # Unsubscribe from all streams
            user_subscriptions = self.data_manager.get_user_subscriptions(connection.info.user_id)
            for subscription in user_subscriptions:
                self.data_manager.unsubscribe_from_stream(
                    connection.info.user_id, subscription.stream_id
                )

        logger.info(f"Live data connection disconnected: {connection.info.id}")

    @on_json
    async def handle_message(self, connection: WebSocketConnection, message):
        """Handle JSON message."""
        try:
            data = message.data
            msg_type = data.get("type")

            if msg_type == "authenticate":
                await self._handle_authenticate(connection, data)
            elif msg_type == "list_streams":
                await self._handle_list_streams(connection, data)
            elif msg_type == "subscribe":
                await self._handle_subscribe(connection, data)
            elif msg_type == "unsubscribe":
                await self._handle_unsubscribe(connection, data)
            elif msg_type == "get_history":
                await self._handle_get_history(connection, data)
            elif msg_type == "get_subscriptions":
                await self._handle_get_subscriptions(connection, data)
            elif msg_type == "add_data":
                await self._handle_add_data(connection, data)
            elif msg_type == "get_statistics":
                await self._handle_get_statistics(connection, data)
            else:
                await connection.send_json(
                    {"type": "error", "message": f"Unknown message type: {msg_type}"}
                )

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await connection.send_json({"type": "error", "message": "Failed to process message"})

    async def _handle_authenticate(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle user authentication."""
        user_id = data.get("user_id")

        if not user_id:
            await connection.send_json({"type": "error", "message": "User ID required"})
            return

        # Simple authentication (in production, validate credentials)
        connection.authenticate(user_id, metadata={"user_id": user_id})

        await connection.send_json(
            {
                "type": "authenticated",
                "user_id": user_id,
                "available_streams": self.data_manager.list_streams(),
            }
        )

        logger.info(f"User authenticated for live data: {user_id}")

    async def _handle_list_streams(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle list streams request."""
        streams = self.data_manager.list_streams()

        await connection.send_json({"type": "streams", "streams": streams})

    async def _handle_subscribe(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle stream subscription request."""
        if not connection.info.authenticated:
            await connection.send_json({"type": "error", "message": "Authentication required"})
            return

        stream_id = data.get("stream_id")
        filters = data.get("filters", {})
        aggregation = data.get("aggregation", "raw")
        window_size = data.get("window_size", 1)
        throttle_rate = data.get("throttle_rate", 0.1)

        if not stream_id:
            await connection.send_json({"type": "error", "message": "Stream ID required"})
            return

        # Convert aggregation string to enum
        try:
            aggregation_enum = AggregationType(aggregation)
        except ValueError:
            await connection.send_json(
                {"type": "error", "message": f"Invalid aggregation type: {aggregation}"}
            )
            return

        # Subscribe to stream
        success = self.data_manager.subscribe_to_stream(
            connection.info.user_id,
            stream_id,
            filters=filters,
            aggregation=aggregation_enum,
            window_size=window_size,
            throttle_rate=throttle_rate,
        )

        if success:
            await connection.send_json(
                {
                    "type": "subscribed",
                    "stream_id": stream_id,
                    "filters": filters,
                    "aggregation": aggregation,
                    "window_size": window_size,
                    "throttle_rate": throttle_rate,
                }
            )

            # Send recent history
            history = self.data_manager.get_stream_history(stream_id, limit=10)
            if history:
                await connection.send_json(
                    {"type": "stream_history", "stream_id": stream_id, "data": history}
                )
        else:
            await connection.send_json(
                {
                    "type": "error",
                    "message": f"Failed to subscribe to stream: {stream_id}",
                }
            )

    async def _handle_unsubscribe(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle stream unsubscription request."""
        if not connection.info.authenticated:
            return

        stream_id = data.get("stream_id")
        if not stream_id:
            return

        success = self.data_manager.unsubscribe_from_stream(connection.info.user_id, stream_id)

        await connection.send_json(
            {"type": "unsubscribed", "stream_id": stream_id, "success": success}
        )

    async def _handle_get_history(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle get stream history request."""
        stream_id = data.get("stream_id")
        limit = data.get("limit", 100)

        if not stream_id:
            await connection.send_json({"type": "error", "message": "Stream ID required"})
            return

        history = self.data_manager.get_stream_history(stream_id, limit)

        await connection.send_json(
            {
                "type": "stream_history",
                "stream_id": stream_id,
                "data": history,
                "count": len(history),
            }
        )

    async def _handle_get_subscriptions(
        self, connection: WebSocketConnection, data: Dict[str, Any]
    ):
        """Handle get user subscriptions request."""
        if not connection.info.authenticated:
            return

        subscriptions = self.data_manager.get_user_subscriptions(connection.info.user_id)

        subscription_data = []
        for sub in subscriptions:
            subscription_data.append(
                {
                    "stream_id": sub.stream_id,
                    "filters": sub.filters,
                    "aggregation": sub.aggregation.value,
                    "window_size": sub.window_size,
                    "throttle_rate": sub.throttle_rate,
                    "active": sub.active,
                    "last_update": sub.last_update,
                }
            )

        await connection.send_json({"type": "subscriptions", "subscriptions": subscription_data})

    async def _handle_add_data(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle add data point request (for testing/admin)."""
        stream_id = data.get("stream_id")
        value = data.get("value")
        metadata = data.get("metadata", {})
        tags = data.get("tags", {})

        if not stream_id or value is None:
            await connection.send_json({"type": "error", "message": "Stream ID and value required"})
            return

        # Create data point
        data_point = DataPoint(stream_id=stream_id, value=value, metadata=metadata, tags=tags)

        # Add to stream
        await self.data_manager.add_data_point(stream_id, data_point)

        await connection.send_json(
            {
                "type": "data_added",
                "stream_id": stream_id,
                "data_point": data_point.to_dict(),
            }
        )

    async def _handle_get_statistics(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle get statistics request."""
        stats = self.data_manager.get_statistics()

        await connection.send_json({"type": "statistics", "stats": stats})


# Create router and add live data endpoint
def create_live_data_router() -> WebSocketRouter:
    """Create WebSocket router with live data endpoint."""
    router = WebSocketRouter()

    # Add live data endpoint
    router.add_route("/ws/live-data", LiveDataEndpoint())

    return router


# Example usage
async def run_live_data_example():
    """Run the live data example."""
    from ..core.asgi import CovetPyASGI

    # Create router
    router = create_live_data_router()

    # Create ASGI app
    CovetPyASGI()

    # Add WebSocket handling
    async def websocket_handler(scope, receive, send):
        if scope["type"] == "websocket":
            await router.handle_websocket(scope, receive, send)
        else:
            await send({"type": "http.response.start", "status": 404, "headers": []})
            await send({"type": "http.response.body", "body": b"Not Found"})

    # Run with uvicorn or similar
    logger.info("Live Data WebSocket server ready at ws://localhost:8000/ws/live-data")
    logger.info("Connect and subscribe to streams to receive real-time data!")

    # Keep running until shutdown
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        await live_data_manager.cleanup()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run example
    asyncio.run(run_live_data_example())
