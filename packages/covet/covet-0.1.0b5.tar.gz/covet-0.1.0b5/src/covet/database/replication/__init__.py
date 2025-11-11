"""
Read Replica Support for High-Availability Deployments

Enterprise-grade read replica management system with:
- Automatic read/write splitting
- Geographic replica selection
- Replication lag monitoring
- Zero-downtime failover
- Health checking and auto-recovery

Example:
    from covet.database.replication import ReplicaManager

    # Configure replicas
    replica_manager = ReplicaManager(
        primary={'host': 'primary.db.example.com', 'port': 5432},
        replicas=[
            {'host': 'replica1.db.example.com', 'region': 'us-east'},
            {'host': 'replica2.db.example.com', 'region': 'us-west'},
        ]
    )

    # Automatic routing
    user = await User.objects.get(id=123)  # Routes to nearest replica
    await user.update(name='Bob')  # Routes to primary

    # Explicit routing
    users = await User.objects.using('replica').all()
"""

from .failover import FailoverEvent, FailoverManager, FailoverStrategy
from .lag_monitor import LagAlert, LagMonitor, LagThreshold
from .manager import ReplicaConfig, ReplicaManager, ReplicaRole, ReplicaStatus
from .router import ConsistencyLevel, ReadPreference, ReplicationRouter

__all__ = [
    # Manager
    "ReplicaManager",
    "ReplicaConfig",
    "ReplicaRole",
    "ReplicaStatus",
    # Router
    "ReplicationRouter",
    "ReadPreference",
    "ConsistencyLevel",
    # Lag Monitor
    "LagMonitor",
    "LagAlert",
    "LagThreshold",
    # Failover
    "FailoverManager",
    "FailoverStrategy",
    "FailoverEvent",
]

__version__ = "1.0.0"
