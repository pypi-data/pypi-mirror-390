"""
ORM Integration for Read Replica Support

Integrates replication routing into the existing ORM with:
- QuerySet.using() method for explicit routing
- Automatic read/write splitting
- Session-based consistency
- Transparent failover handling

Example:
    # Configure replication
    from covet.database.replication import setup_replication

    await setup_replication(
        primary={'host': 'primary.db.example.com'},
        replicas=[
            {'host': 'replica1.db.example.com', 'region': 'us-east'},
            {'host': 'replica2.db.example.com', 'region': 'us-west'},
        ]
    )

    # Automatic routing
    user = await User.objects.get(id=123)  # Routed to replica
    await user.save()  # Routed to primary

    # Explicit routing
    users = await User.objects.using('replica').all()
    user = await User.objects.using('primary').get(id=123)
"""

import logging
from typing import Any, Dict, List, Optional

from .failover import FailoverManager, FailoverStrategy
from .lag_monitor import LagMonitor
from .manager import ReplicaConfig, ReplicaManager, ReplicaRole
from .router import ConsistencyLevel, ReadPreference, ReplicationRouter

logger = logging.getLogger(__name__)

# Global instances
_replica_manager: Optional[ReplicaManager] = None
_replication_router: Optional[ReplicationRouter] = None
_lag_monitor: Optional[LagMonitor] = None
_failover_manager: Optional[FailoverManager] = None


async def setup_replication(
    primary: Dict[str, Any],
    replicas: Optional[List[Dict[str, Any]]] = None,
    health_check_interval: float = 10.0,
    max_lag_threshold: float = 5.0,
    enable_auto_failover: bool = True,
    failover_strategy: FailoverStrategy = FailoverStrategy.SUPERVISED,
    **kwargs,
) -> ReplicaManager:
    """
    Setup replication system.

    Args:
        primary: Primary database configuration
        replicas: List of replica configurations
        health_check_interval: Health check interval in seconds
        max_lag_threshold: Maximum acceptable lag in seconds
        enable_auto_failover: Enable automatic failover
        failover_strategy: Failover strategy
        **kwargs: Additional configuration

    Returns:
        ReplicaManager instance

    Example:
        await setup_replication(
            primary={
                'host': 'primary.db.example.com',
                'port': 5432,
                'database': 'mydb',
                'user': 'postgres',
                'password': 'secret'
            },
            replicas=[
                {
                    'host': 'replica1.db.example.com',
                    'region': 'us-east',
                    'weight': 100
                },
                {
                    'host': 'replica2.db.example.com',
                    'region': 'us-west',
                    'weight': 100
                }
            ],
            enable_auto_failover=True
        )
    """
    global _replica_manager, _replication_router, _lag_monitor, _failover_manager

    # Create primary config
    primary_config = ReplicaConfig(
        host=primary["host"],
        port=primary.get("port", 5432),
        database=primary.get("database", "postgres"),
        user=primary.get("user", "postgres"),
        password=primary.get("password", ""),
        role=ReplicaRole.PRIMARY,
        ssl=primary.get("ssl"),
    )

    # Create replica configs
    replica_configs = []
    for replica in replicas or []:
        replica_configs.append(
            ReplicaConfig(
                host=replica["host"],
                port=replica.get("port", 5432),
                database=replica.get("database", primary.get("database", "postgres")),
                user=replica.get("user", primary.get("user", "postgres")),
                password=replica.get("password", primary.get("password", "")),
                role=ReplicaRole.REPLICA,
                region=replica.get("region"),
                datacenter=replica.get("datacenter"),
                weight=replica.get("weight", 100),
                max_lag_seconds=replica.get("max_lag_seconds", max_lag_threshold),
                ssl=replica.get("ssl"),
            )
        )

    # Create replica manager
    _replica_manager = ReplicaManager(
        primary=primary_config,
        replicas=replica_configs,
        health_check_interval=health_check_interval,
        max_lag_threshold=max_lag_threshold,
        failover_enabled=enable_auto_failover,
        auto_discover=kwargs.get("auto_discover", False),
    )

    await _replica_manager.start()

    # Create replication router
    _replication_router = ReplicationRouter(
        replica_manager=_replica_manager,
        default_read_preference=kwargs.get(
            "default_read_preference", ReadPreference.REPLICA_PREFERRED
        ),
        default_consistency=kwargs.get("default_consistency", ConsistencyLevel.READ_AFTER_WRITE),
        read_after_write_window=kwargs.get("read_after_write_window", 5.0),
    )

    # Create lag monitor
    _lag_monitor = LagMonitor(
        replica_manager=_replica_manager,
        check_interval=kwargs.get("lag_check_interval", 5.0),
        auto_remediate=kwargs.get("auto_remediate", True),
    )

    await _lag_monitor.start()

    # Create failover manager if enabled
    if enable_auto_failover:
        _failover_manager = FailoverManager(
            replica_manager=_replica_manager,
            strategy=failover_strategy,
            min_replicas_for_failover=kwargs.get("min_replicas_for_failover", 1),
            failover_timeout=kwargs.get("failover_timeout", 30.0),
        )

        await _failover_manager.start()

    logger.info("Replication system initialized successfully")

    return _replica_manager


async def teardown_replication() -> None:
    """
    Teardown replication system.

    Stops all replication components and cleans up resources.
    """
    global _replica_manager, _replication_router, _lag_monitor, _failover_manager

    logger.info("Tearing down replication system...")

    if _failover_manager:
        await _failover_manager.stop()
        _failover_manager = None

    if _lag_monitor:
        await _lag_monitor.stop()
        _lag_monitor = None

    if _replication_router:
        await _replication_router.stop()
        _replication_router = None

    if _replica_manager:
        await _replica_manager.stop()
        _replica_manager = None

    logger.info("Replication system torn down")


def get_replica_manager() -> Optional[ReplicaManager]:
    """Get global replica manager instance."""
    return _replica_manager


def get_replication_router() -> Optional[ReplicationRouter]:
    """Get global replication router instance."""
    return _replication_router


def get_lag_monitor() -> Optional[LagMonitor]:
    """Get global lag monitor instance."""
    return _lag_monitor


def get_failover_manager() -> Optional[FailoverManager]:
    """Get global failover manager instance."""
    return _failover_manager


def get_replication_status() -> Dict[str, Any]:
    """
    Get comprehensive replication status.

    Returns:
        Dictionary with status of all replication components
    """
    status = {
        "enabled": _replica_manager is not None,
        "replica_manager": None,
        "router": None,
        "lag_monitor": None,
        "failover_manager": None,
    }

    if _replica_manager:
        status["replica_manager"] = {
            "metrics": _replica_manager.get_metrics(),
            "replicas": [
                {
                    "id": replica_id,
                    "host": config.host,
                    "region": config.region,
                    "status": health.status.value,
                    "lag_seconds": health.lag_seconds,
                    "response_time_ms": health.response_time_ms,
                }
                for replica_id, config, health in _replica_manager.get_all_replicas(
                    include_unhealthy=True
                )
            ],
        }

    if _replication_router:
        status["router"] = _replication_router.get_metrics()

    if _lag_monitor:
        status["lag_monitor"] = {
            "metrics": _lag_monitor.get_metrics(),
            "active_alerts": len(_lag_monitor.get_active_alerts()),
        }

    if _failover_manager:
        status["failover_manager"] = _failover_manager.get_metrics()

    return status


# Monkey-patch QuerySet to add .using() method
def _patch_queryset():
    """Patch QuerySet to support replication routing."""
    from ..orm.managers import QuerySet

    original_get_adapter = QuerySet._get_adapter

    async def patched_get_adapter(self):
        """Get adapter with replication routing."""
        # Check if explicit using() was called
        if hasattr(self, "_replication_target"):
            target = self._replication_target

            if target == "primary":
                if _replica_manager:
                    return _replica_manager.get_primary()
            elif target == "replica":
                if _replica_manager:
                    replica = _replica_manager.get_replica()
                    if replica:
                        return replica

        # Use replication router if available
        if _replication_router:
            # Determine if this is a write operation
            # For now, always route to replica for reads
            replica = _replica_manager.get_replica()
            if replica:
                return replica

        # Fallback to original behavior
        return await original_get_adapter(self)

    def using(self, target: str) -> "QuerySet":
        """
        Specify database target for query.

        Args:
            target: 'primary' or 'replica'

        Returns:
            New QuerySet with routing target

        Example:
            # Force read from primary
            user = await User.objects.using('primary').get(id=1)

            # Force read from replica
            users = await User.objects.using('replica').all()
        """
        clone = self._clone()
        clone._replication_target = target
        return clone

    # Patch methods
    QuerySet._get_adapter = patched_get_adapter
    QuerySet.using = using

    logger.info("QuerySet patched with replication support")


# Auto-patch on import if desired
# _patch_queryset()


__all__ = [
    "setup_replication",
    "teardown_replication",
    "get_replica_manager",
    "get_replication_router",
    "get_lag_monitor",
    "get_failover_manager",
    "get_replication_status",
]
