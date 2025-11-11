"""
CovetPy Horizontal Database Sharding

Production-ready horizontal sharding system for scaling databases beyond
single-server limitations. Provides transparent sharding with automatic
routing, health monitoring, and zero-downtime rebalancing.

Key Components:
- ShardManager: Central coordinator for shard operations
- ShardRouter: Intelligent query routing and scatter-gather
- ShardStrategy: Pluggable sharding algorithms
- ShardRebalancer: Zero-downtime data migration

Quick Start:
    from covet.database.sharding import (
        ShardManager,
        ShardRouter,
        HashStrategy,
        ShardInfo,
    )

    # Define shards
    shards = [
        ShardInfo('shard1', 'db1.example.com', 5432, 'app_db'),
        ShardInfo('shard2', 'db2.example.com', 5432, 'app_db'),
        ShardInfo('shard3', 'db3.example.com', 5432, 'app_db'),
    ]

    # Initialize sharding with hash strategy
    strategy = HashStrategy(shard_key='user_id', shards=shards)
    manager = ShardManager(strategy=strategy)
    await manager.initialize()

    # Route queries
    router = ShardRouter(manager)
    result = await router.execute(
        "SELECT * FROM users WHERE user_id = $1",
        params=(12345,),
        routing_key=12345
    )

Sharding Strategies:
- HashStrategy: Even distribution via hashing
- RangeStrategy: Range-based (good for time-series)
- ConsistentHashStrategy: Minimal rebalancing
- GeographicStrategy: Data locality/compliance

Performance:
- <1ms routing overhead
- Supports 100+ shards
- Automatic failover
- Health monitoring
- Connection pooling per shard

Example Usage:
    # Hash-based sharding
    strategy = HashStrategy(shard_key='user_id', shards=shards)

    # Range-based sharding
    ranges = {
        'shard1': (0, 1000000),
        'shard2': (1000001, 2000000),
        'shard3': (2000001, None),
    }
    strategy = RangeStrategy(shard_key='user_id', shards=shards, ranges=ranges)

    # Consistent hashing
    strategy = ConsistentHashStrategy(
        shard_key='user_id',
        shards=shards,
        virtual_nodes_per_shard=150
    )

    # Geographic sharding
    strategy = GeographicStrategy(
        shard_key='region',
        shards=shards,
        default_region='us-east-1'
    )

Rebalancing:
    from covet.database.sharding import ShardRebalancer, RebalanceStrategy

    rebalancer = ShardRebalancer(manager, router)

    # Create rebalancing job
    job = await rebalancer.create_rebalance_job(
        table_name='users',
        shard_key='user_id',
        strategy=RebalanceStrategy.LIVE_MIGRATION
    )

    # Execute with progress tracking
    await rebalancer.execute_job(job.job_id)

    # Monitor progress
    status = rebalancer.get_job_status(job.job_id)
    print(f"Progress: {status['progress_percent']}%")
"""

from .manager import (
    ShardHealth,
    ShardManager,
    ShardMetrics,
)
from .rebalance import (
    RebalanceJob,
    RebalanceStatus,
    RebalanceStrategy,
    RebalanceTask,
    ShardRebalancer,
)
from .router import (
    QueryPlan,
    QueryResult,
    QueryType,
    ShardRouter,
)
from .strategies import (
    ConsistentHashStrategy,
    GeographicStrategy,
    HashStrategy,
    RangeStrategy,
    ShardInfo,
    ShardingStrategy,
    ShardRoutingResult,
    ShardStrategy,
)

__version__ = "1.0.0"

__all__ = [
    # Strategies
    "ShardingStrategy",
    "ShardInfo",
    "ShardRoutingResult",
    "ShardStrategy",
    "HashStrategy",
    "RangeStrategy",
    "ConsistentHashStrategy",
    "GeographicStrategy",
    # Manager
    "ShardManager",
    "ShardHealth",
    "ShardMetrics",
    # Router
    "ShardRouter",
    "QueryType",
    "QueryPlan",
    "QueryResult",
    # Rebalancer
    "ShardRebalancer",
    "RebalanceStrategy",
    "RebalanceStatus",
    "RebalanceTask",
    "RebalanceJob",
]
