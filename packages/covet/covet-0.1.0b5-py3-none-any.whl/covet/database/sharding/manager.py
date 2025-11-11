"""
Shard Manager - Central Sharding Coordinator

Production-grade shard management system for CovetPy framework.
Manages shard registry, health monitoring, failover, and routing decisions.

Key Responsibilities:
- Shard registration and discovery
- Health monitoring and automatic failover
- Connection pool management per shard
- Query routing and load balancing
- Shard topology changes (add/remove)
- Statistics and metrics collection

Architecture:
- ShardManager: Central coordinator
- ShardRegistry: Shard metadata storage
- HealthMonitor: Continuous health checks
- ConnectionManager: Per-shard connection pools
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from ..adapters.base import DatabaseAdapter
from ..adapters.mysql import MySQLAdapter
from ..adapters.postgresql import PostgreSQLAdapter
from ..adapters.sqlite import SQLiteAdapter
from .strategies import (
    ConsistentHashStrategy,
    GeographicStrategy,
    HashStrategy,
    RangeStrategy,
    ShardInfo,
)
from .strategies import ShardingStrategy as StrategyType
from .strategies import (
    ShardRoutingResult,
    ShardStrategy,
)

logger = logging.getLogger(__name__)


@dataclass
class ShardHealth:
    """
    Health status of a shard.

    Tracks connectivity, performance, and capacity metrics
    for automated failover and load balancing decisions.
    """

    shard_id: str
    is_healthy: bool = True
    last_check: datetime = field(default_factory=datetime.now)
    consecutive_failures: int = 0
    average_latency_ms: float = 0.0
    error_rate: float = 0.0
    connection_count: int = 0
    capacity_used_percent: float = 0.0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "shard_id": self.shard_id,
            "is_healthy": self.is_healthy,
            "last_check": self.last_check.isoformat(),
            "consecutive_failures": self.consecutive_failures,
            "average_latency_ms": self.average_latency_ms,
            "error_rate": self.error_rate,
            "connection_count": self.connection_count,
            "capacity_used_percent": self.capacity_used_percent,
            "last_error": self.last_error,
            "metadata": self.metadata,
        }


@dataclass
class ShardMetrics:
    """
    Performance metrics for a shard.

    Collected for monitoring, alerting, and capacity planning.
    """

    shard_id: str
    queries_per_second: float = 0.0
    reads_per_second: float = 0.0
    writes_per_second: float = 0.0
    total_queries: int = 0
    total_reads: int = 0
    total_writes: int = 0
    average_query_time_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "shard_id": self.shard_id,
            "queries_per_second": self.queries_per_second,
            "reads_per_second": self.reads_per_second,
            "writes_per_second": self.writes_per_second,
            "total_queries": self.total_queries,
            "total_reads": self.total_reads,
            "total_writes": self.total_writes,
            "average_query_time_ms": self.average_query_time_ms,
            "p50_latency_ms": self.p50_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "p99_latency_ms": self.p99_latency_ms,
            "error_count": self.error_count,
            "timestamp": self.timestamp.isoformat(),
        }


class ShardManager:
    """
    Central shard management coordinator.

    Manages the complete sharding infrastructure:
    - Shard registry and discovery
    - Connection pooling per shard
    - Health monitoring and failover
    - Query routing via strategy
    - Performance metrics collection

    Example:
        # Initialize with hash sharding
        shards = [
            ShardInfo('shard1', 'db1.example.com', 5432, 'app_db'),
            ShardInfo('shard2', 'db2.example.com', 5432, 'app_db'),
            ShardInfo('shard3', 'db3.example.com', 5432, 'app_db'),
        ]

        manager = ShardManager(
            strategy=HashStrategy(shard_key='user_id', shards=shards)
        )

        await manager.initialize()

        # Route query to appropriate shard
        shard = manager.get_shard_for_write(user_id=12345)
        adapter = await manager.get_adapter(shard.shard_id)
        await adapter.execute("INSERT INTO users ...")
    """

    def __init__(
        self,
        strategy: ShardStrategy,
        health_check_interval: int = 30,
        max_consecutive_failures: int = 3,
        enable_auto_failover: bool = True,
        connection_pool_size: int = 10,
        connection_timeout: float = 5.0,
    ):
        """
        Initialize shard manager.

        Args:
            strategy: Sharding strategy to use
            health_check_interval: Seconds between health checks
            max_consecutive_failures: Failures before marking shard unhealthy
            enable_auto_failover: Enable automatic failover to replicas
            connection_pool_size: Connections per shard
            connection_timeout: Connection timeout in seconds
        """
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.max_consecutive_failures = max_consecutive_failures
        self.enable_auto_failover = enable_auto_failover
        self.connection_pool_size = connection_pool_size
        self.connection_timeout = connection_timeout

        # Shard registry
        self.shards: Dict[str, ShardInfo] = {}
        for shard in strategy.get_all_shards():
            self.shards[shard.shard_id] = shard

        # Connection adapters per shard
        self.adapters: Dict[str, DatabaseAdapter] = {}

        # Health tracking
        self.shard_health: Dict[str, ShardHealth] = {}
        for shard_id in self.shards:
            self.shard_health[shard_id] = ShardHealth(shard_id=shard_id)

        # Metrics tracking
        self.shard_metrics: Dict[str, ShardMetrics] = {}
        for shard_id in self.shards:
            self.shard_metrics[shard_id] = ShardMetrics(shard_id=shard_id)

        # Health monitoring task
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._monitoring_active = False

        # Statistics
        self.total_queries = 0
        self.total_errors = 0
        self.start_time = datetime.now()

        logger.info(
            f"ShardManager initialized with {len(self.shards)} shards "
            f"using {strategy.__class__.__name__}"
        )

    async def initialize(self) -> None:
        """
        Initialize shard manager.

        Connects to all shards and starts health monitoring.
        """
        logger.info("Initializing shard manager...")

        # Connect to all shards
        await self._connect_all_shards()

        # Start health monitoring
        if self.health_check_interval > 0:
            self._monitoring_active = True
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            logger.info("Health monitoring started")

        logger.info("Shard manager initialized successfully")

    async def shutdown(self) -> None:
        """
        Shutdown shard manager.

        Stops health monitoring and closes all connections.
        """
        logger.info("Shutting down shard manager...")

        # Stop health monitoring
        self._monitoring_active = False
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        await self._disconnect_all_shards()

        logger.info("Shard manager shut down successfully")

    async def _connect_all_shards(self) -> None:
        """Connect to all registered shards."""
        tasks = []
        for shard_id, shard in self.shards.items():
            task = self._connect_shard(shard)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log connection results
        for i, (shard_id, result) in enumerate(zip(self.shards.keys(), results)):
            if isinstance(result, Exception):
                logger.error(f"Failed to connect to shard {shard_id}: {result}")
                self.shard_health[shard_id].is_healthy = False
                self.shard_health[shard_id].last_error = str(result)
            else:
                logger.info(f"Connected to shard {shard_id}")

    async def _connect_shard(self, shard: ShardInfo) -> None:
        """
        Connect to a single shard.

        Args:
            shard: Shard to connect to
        """
        try:
            # Detect database type from port or configuration
            # Default to PostgreSQL if not specified
            adapter = self._create_adapter(shard)

            # Connect
            await adapter.connect()

            # Store adapter
            self.adapters[shard.shard_id] = adapter

            logger.debug(f"Connected to shard {shard.shard_id}")

        except Exception as e:
            logger.error(f"Failed to connect to shard {shard.shard_id}: {e}")
            raise

    def _create_adapter(self, shard: ShardInfo) -> DatabaseAdapter:
        """
        Create database adapter for shard.

        Args:
            shard: Shard configuration

        Returns:
            Database adapter instance
        """
        # Check for adapter type hint in metadata
        adapter_type = shard.metadata.get("adapter_type", "postgresql")

        if adapter_type == "postgresql" or shard.port == 5432:
            return PostgreSQLAdapter(
                host=shard.host,
                port=shard.port,
                database=shard.database,
                user=shard.metadata.get("user", "postgres"),
                password=shard.metadata.get("password", ""),
                min_pool_size=self.connection_pool_size // 2,
                max_pool_size=self.connection_pool_size,
            )
        elif adapter_type == "mysql" or shard.port == 3306:
            return MySQLAdapter(
                host=shard.host,
                port=shard.port,
                database=shard.database,
                user=shard.metadata.get("user", "root"),
                password=shard.metadata.get("password", ""),
                pool_size=self.connection_pool_size,
            )
        elif adapter_type == "sqlite":
            return SQLiteAdapter(
                database_path=shard.metadata.get("database_path", shard.database),
            )
        else:
            # Default to PostgreSQL
            logger.warning(
                f"Unknown adapter type '{adapter_type}' for shard {shard.shard_id}, "
                f"defaulting to PostgreSQL"
            )
            return PostgreSQLAdapter(
                host=shard.host,
                port=shard.port,
                database=shard.database,
                user=shard.metadata.get("user", "postgres"),
                password=shard.metadata.get("password", ""),
                min_pool_size=self.connection_pool_size // 2,
                max_pool_size=self.connection_pool_size,
            )

    async def _disconnect_all_shards(self) -> None:
        """Disconnect from all shards."""
        tasks = []
        for shard_id, adapter in self.adapters.items():
            task = self._disconnect_shard(shard_id, adapter)
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _disconnect_shard(self, shard_id: str, adapter: DatabaseAdapter) -> None:
        """Disconnect from a single shard."""
        try:
            await adapter.disconnect()
            logger.debug(f"Disconnected from shard {shard_id}")
        except Exception as e:
            logger.error(f"Error disconnecting from shard {shard_id}: {e}")

    async def _health_monitor_loop(self) -> None:
        """
        Background task for continuous health monitoring.

        Runs periodic health checks on all shards and updates
        health status for automatic failover decisions.
        """
        logger.info("Health monitor loop started")

        while self._monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(self.health_check_interval)

        logger.info("Health monitor loop stopped")

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all shards."""
        tasks = []
        for shard_id in self.shards:
            task = self._check_shard_health(shard_id)
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_shard_health(self, shard_id: str) -> None:
        """
        Check health of a single shard.

        Performs simple query test and measures latency.
        Updates health status based on results.

        Args:
            shard_id: ID of shard to check
        """
        health = self.shard_health[shard_id]
        adapter = self.adapters.get(shard_id)

        if not adapter:
            health.is_healthy = False
            health.consecutive_failures += 1
            health.last_error = "No adapter available"
            return

        try:
            # Measure query latency
            start_time = time.time()
            await adapter.execute("SELECT 1")
            latency_ms = (time.time() - start_time) * 1000

            # Update health status
            health.is_healthy = True
            health.consecutive_failures = 0
            health.average_latency_ms = health.average_latency_ms * 0.8 + latency_ms * 0.2
            health.last_check = datetime.now()
            health.last_error = None

            logger.debug(f"Shard {shard_id} health check: OK (latency: {latency_ms:.2f}ms)")

        except Exception as e:
            # Update failure status
            health.consecutive_failures += 1
            health.last_error = str(e)
            health.last_check = datetime.now()

            # Mark unhealthy if too many consecutive failures
            if health.consecutive_failures >= self.max_consecutive_failures:
                if health.is_healthy:
                    logger.error(
                        f"Shard {shard_id} marked UNHEALTHY after "
                        f"{health.consecutive_failures} consecutive failures"
                    )
                health.is_healthy = False

            logger.warning(
                f"Shard {shard_id} health check failed "
                f"({health.consecutive_failures}/{self.max_consecutive_failures}): {e}"
            )

    def get_shard_for_write(self, routing_key: Any) -> ShardInfo:
        """
        Get shard for write operation.

        Args:
            routing_key: Value of shard key (e.g., user_id value)

        Returns:
            ShardInfo for write operation

        Raises:
            ValueError: If no healthy writable shard available
        """
        shard = self.strategy.get_write_shard(routing_key)

        # Check if shard is healthy
        health = self.shard_health.get(shard.shard_id)
        if health and not health.is_healthy:
            raise ValueError(
                f"Shard {shard.shard_id} is unhealthy. " f"Cannot perform write operation."
            )

        return shard

    def get_shard_for_read(self, routing_key: Any, prefer_replica: bool = False) -> ShardInfo:
        """
        Get shard for read operation.

        Args:
            routing_key: Value of shard key
            prefer_replica: If True, prefer replica over primary

        Returns:
            ShardInfo for read operation

        Raises:
            ValueError: If no healthy readable shard available
        """
        shard = self.strategy.get_read_shard(routing_key, prefer_replica)

        # Check if shard is healthy
        health = self.shard_health.get(shard.shard_id)
        if health and not health.is_healthy:
            # Try failover if enabled
            if self.enable_auto_failover:
                result = self.strategy.get_shard(routing_key)
                for replica in result.replica_shards:
                    replica_health = self.shard_health.get(replica.shard_id)
                    if replica_health and replica_health.is_healthy:
                        logger.info(
                            f"Failover: Using replica {replica.shard_id} "
                            f"instead of unhealthy {shard.shard_id}"
                        )
                        return replica

            raise ValueError(f"Shard {shard.shard_id} is unhealthy and no replicas available")

        return shard

    def get_shards_for_scatter(self) -> List[ShardInfo]:
        """
        Get all healthy shards for scatter-gather query.

        Returns:
            List of healthy shards
        """
        healthy_shards = []
        for shard in self.strategy.get_all_shards():
            health = self.shard_health.get(shard.shard_id)
            if health and health.is_healthy:
                healthy_shards.append(shard)

        return healthy_shards

    async def get_adapter(self, shard_id: str) -> DatabaseAdapter:
        """
        Get database adapter for a shard.

        Args:
            shard_id: Shard identifier

        Returns:
            DatabaseAdapter instance

        Raises:
            KeyError: If shard not found
        """
        adapter = self.adapters.get(shard_id)
        if not adapter:
            raise KeyError(f"No adapter found for shard {shard_id}")

        # Ensure connected
        if not adapter._connected:
            await adapter.connect()

        return adapter

    def add_shard(self, shard: ShardInfo) -> None:
        """
        Add new shard to cluster.

        Args:
            shard: Shard configuration
        """
        if shard.shard_id in self.shards:
            raise ValueError(f"Shard {shard.shard_id} already exists")

        self.shards[shard.shard_id] = shard
        self.shard_health[shard.shard_id] = ShardHealth(shard_id=shard.shard_id)
        self.shard_metrics[shard.shard_id] = ShardMetrics(shard_id=shard.shard_id)

        # Add to strategy
        self.strategy.add_shard(shard)

        logger.info(f"Added shard {shard.shard_id} to cluster")

    async def remove_shard(self, shard_id: str) -> None:
        """
        Remove shard from cluster.

        Args:
            shard_id: ID of shard to remove
        """
        if shard_id not in self.shards:
            raise KeyError(f"Shard {shard_id} not found")

        # Disconnect adapter
        if shard_id in self.adapters:
            await self._disconnect_shard(shard_id, self.adapters[shard_id])
            del self.adapters[shard_id]

        # Remove from strategy
        self.strategy.remove_shard(shard_id)

        # Remove from tracking
        del self.shards[shard_id]
        del self.shard_health[shard_id]
        del self.shard_metrics[shard_id]

        logger.info(f"Removed shard {shard_id} from cluster")

    def get_cluster_status(self) -> Dict[str, Any]:
        """
        Get cluster status overview.

        Returns:
            Dictionary with cluster statistics
        """
        total_shards = len(self.shards)
        healthy_shards = sum(1 for h in self.shard_health.values() if h.is_healthy)
        unhealthy_shards = total_shards - healthy_shards

        uptime = datetime.now() - self.start_time

        return {
            "total_shards": total_shards,
            "healthy_shards": healthy_shards,
            "unhealthy_shards": unhealthy_shards,
            "strategy": self.strategy.__class__.__name__,
            "shard_key": self.strategy.shard_key,
            "total_queries": self.total_queries,
            "total_errors": self.total_errors,
            "error_rate": (self.total_errors / self.total_queries if self.total_queries > 0 else 0),
            "uptime_seconds": uptime.total_seconds(),
            "health_monitoring_enabled": self._monitoring_active,
        }

    def get_shard_status(self, shard_id: str) -> Dict[str, Any]:
        """
        Get detailed status for a specific shard.

        Args:
            shard_id: Shard identifier

        Returns:
            Dictionary with shard status
        """
        if shard_id not in self.shards:
            raise KeyError(f"Shard {shard_id} not found")

        shard = self.shards[shard_id]
        health = self.shard_health[shard_id]
        metrics = self.shard_metrics[shard_id]

        return {
            "shard_id": shard_id,
            "shard_info": shard.to_dict(),
            "health": health.to_dict(),
            "metrics": metrics.to_dict(),
        }

    def get_all_shard_status(self) -> List[Dict[str, Any]]:
        """
        Get status for all shards.

        Returns:
            List of shard status dictionaries
        """
        return [self.get_shard_status(shard_id) for shard_id in self.shards.keys()]


__all__ = [
    "ShardManager",
    "ShardHealth",
    "ShardMetrics",
]
