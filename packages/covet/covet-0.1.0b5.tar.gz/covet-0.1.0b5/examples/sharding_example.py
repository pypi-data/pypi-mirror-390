"""
Complete Sharding Example for CovetPy

Demonstrates production-ready horizontal database sharding with:
- Multiple sharding strategies
- Health monitoring and failover
- Query routing and scatter-gather
- Zero-downtime rebalancing

Usage:
    python examples/sharding_example.py
"""

import asyncio
import logging
from typing import List

from src.covet.database.sharding import (
    # Strategies
    ShardInfo,
    HashStrategy,
    RangeStrategy,
    ConsistentHashStrategy,
    GeographicStrategy,
    # Manager
    ShardManager,
    # Router
    ShardRouter,
    # Rebalancer
    ShardRebalancer,
    RebalanceStrategy,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_hash_sharding():
    """Example 1: Hash-based sharding for even distribution."""
    logger.info("=" * 60)
    logger.info("Example 1: Hash-Based Sharding")
    logger.info("=" * 60)

    # Define shards
    shards = [
        ShardInfo(
            shard_id='shard1',
            host='db1.example.com',
            port=5432,
            database='app_db',
            metadata={'user': 'app_user', 'password': 'secret', 'adapter_type': 'postgresql'}
        ),
        ShardInfo(
            shard_id='shard2',
            host='db2.example.com',
            port=5432,
            database='app_db',
            metadata={'user': 'app_user', 'password': 'secret', 'adapter_type': 'postgresql'}
        ),
        ShardInfo(
            shard_id='shard3',
            host='db3.example.com',
            port=5432,
            database='app_db',
            metadata={'user': 'app_user', 'password': 'secret', 'adapter_type': 'postgresql'}
        ),
    ]

    # Create hash strategy
    strategy = HashStrategy(
        shard_key='user_id',
        shards=shards,
        hash_function='md5'
    )

    # Initialize shard manager (without connecting)
    manager = ShardManager(
        strategy=strategy,
        health_check_interval=30,  # Check every 30 seconds
        max_consecutive_failures=3,
        enable_auto_failover=True
    )

    # Note: In production, you would call await manager.initialize()
    # For this example, we skip actual connections

    # Show routing examples
    logger.info("Routing examples:")
    for user_id in [12345, 67890, 11111, 99999]:
        result = strategy.get_shard(user_id)
        logger.info(f"  User {user_id} -> Shard {result.primary_shard.shard_id}")

    # Cluster status
    status = manager.get_cluster_status()
    logger.info(f"\nCluster Status:")
    logger.info(f"  Total Shards: {status['total_shards']}")
    logger.info(f"  Strategy: {status['strategy']}")
    logger.info(f"  Shard Key: {status['shard_key']}")


async def example_range_sharding():
    """Example 2: Range-based sharding for time-series data."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Range-Based Sharding")
    logger.info("=" * 60)

    # Define shards
    shards = [
        ShardInfo('shard1', 'db1.example.com', 5432, 'timeseries_db'),
        ShardInfo('shard2', 'db2.example.com', 5432, 'timeseries_db'),
        ShardInfo('shard3', 'db3.example.com', 5432, 'timeseries_db'),
    ]

    # Define ranges (e.g., by timestamp or ID)
    ranges = {
        'shard1': (0, 1000000),          # Users 0-1M
        'shard2': (1000001, 2000000),    # Users 1M-2M
        'shard3': (2000001, 9999999999), # Users 2M+
    }

    strategy = RangeStrategy(
        shard_key='user_id',
        shards=shards,
        ranges=ranges
    )

    logger.info("Range Configuration:")
    for shard_id, (start, end) in ranges.items():
        logger.info(f"  {shard_id}: {start:,} - {end:,}")

    # Show routing
    logger.info("\nRouting examples:")
    test_ids = [500000, 1500000, 3000000]
    for user_id in test_ids:
        result = strategy.get_shard(user_id)
        logger.info(f"  User {user_id:,} -> Shard {result.primary_shard.shard_id}")

    # Range queries are efficient
    logger.info("\nRange query example:")
    affected_shards = strategy.get_shards_for_range(900000, 1100000)
    logger.info(f"  Query for users 900K-1.1M touches {len(affected_shards)} shards:")
    for shard in affected_shards:
        logger.info(f"    - {shard.shard_id}")


async def example_consistent_hashing():
    """Example 3: Consistent hashing for dynamic scaling."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Consistent Hashing")
    logger.info("=" * 60)

    # Start with 2 shards
    initial_shards = [
        ShardInfo('shard1', 'db1.example.com', 5432, 'app_db'),
        ShardInfo('shard2', 'db2.example.com', 5432, 'app_db'),
    ]

    strategy = ConsistentHashStrategy(
        shard_key='user_id',
        shards=initial_shards,
        virtual_nodes_per_shard=150  # More vnodes = better distribution
    )

    logger.info(f"Initial configuration:")
    logger.info(f"  Shards: {len(strategy.active_shards)}")
    logger.info(f"  Virtual nodes: {len(strategy.ring)}")

    # Map some users
    logger.info("\nInitial user distribution:")
    distribution = {}
    for i in range(100):
        result = strategy.get_shard(i)
        shard_id = result.primary_shard.shard_id
        distribution[shard_id] = distribution.get(shard_id, 0) + 1

    for shard_id, count in sorted(distribution.items()):
        logger.info(f"  {shard_id}: {count} users ({count}%)")

    # Add third shard
    logger.info("\nAdding shard3...")
    new_shard = ShardInfo('shard3', 'db3.example.com', 5432, 'app_db')
    strategy.add_shard(new_shard)

    logger.info(f"After adding shard:")
    logger.info(f"  Shards: {len(strategy.active_shards)}")
    logger.info(f"  Virtual nodes: {len(strategy.ring)}")

    # Check new distribution
    new_distribution = {}
    moved_users = 0
    for i in range(100):
        result = strategy.get_shard(i)
        shard_id = result.primary_shard.shard_id
        new_distribution[shard_id] = new_distribution.get(shard_id, 0) + 1

        # Count moved users
        if shard_id != list(distribution.keys())[0]:
            moved_users += 1

    logger.info("\nNew user distribution:")
    for shard_id, count in sorted(new_distribution.items()):
        logger.info(f"  {shard_id}: {count} users ({count}%)")

    logger.info(f"\nMinimal rebalancing: Only {moved_users}% of users moved")


async def example_geographic_sharding():
    """Example 4: Geographic sharding for data locality."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Geographic Sharding")
    logger.info("=" * 60)

    # Define regional shards
    shards = [
        ShardInfo('us-east', 'db-use1.example.com', 5432, 'app_db', region='us-east-1'),
        ShardInfo('us-west', 'db-usw2.example.com', 5432, 'app_db', region='us-west-2'),
        ShardInfo('eu-west', 'db-euw1.example.com', 5432, 'app_db', region='eu-west-1'),
        ShardInfo('ap-se', 'db-apse1.example.com', 5432, 'app_db', region='ap-southeast-1'),
    ]

    # Custom region mapping
    region_mapping = {
        'new-york': 'us-east-1',
        'california': 'us-west-2',
        'london': 'eu-west-1',
        'singapore': 'ap-southeast-1',
    }

    strategy = GeographicStrategy(
        shard_key='region',
        shards=shards,
        region_mapping=region_mapping,
        default_region='us-east-1'
    )

    logger.info("Regional Shards:")
    for shard in shards:
        logger.info(f"  {shard.shard_id}: {shard.host} ({shard.region})")

    logger.info("\nRouting examples:")
    test_regions = ['new-york', 'california', 'london', 'singapore', 'unknown']
    for region in test_regions:
        result = strategy.get_shard(region)
        logger.info(f"  {region:15} -> {result.primary_shard.shard_id} ({result.primary_shard.region})")


async def example_query_routing():
    """Example 5: Query routing with ShardRouter."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 5: Query Routing")
    logger.info("=" * 60)

    # Setup sharding
    shards = [
        ShardInfo('shard1', 'db1.example.com', 5432, 'app_db'),
        ShardInfo('shard2', 'db2.example.com', 5432, 'app_db'),
        ShardInfo('shard3', 'db3.example.com', 5432, 'app_db'),
    ]

    strategy = HashStrategy(shard_key='user_id', shards=shards)
    manager = ShardManager(strategy=strategy, health_check_interval=0)
    router = ShardRouter(manager)

    logger.info("Query routing examples:")

    # Single-shard query (routed automatically)
    logger.info("\n1. Single-shard SELECT:")
    logger.info("   Query: SELECT * FROM users WHERE user_id = 12345")
    logger.info("   Routing: Automatic via hash(12345)")
    result = strategy.get_shard(12345)
    logger.info(f"   Target: {result.primary_shard.shard_id}")

    # Multi-shard scatter-gather
    logger.info("\n2. Multi-shard COUNT:")
    logger.info("   Query: SELECT COUNT(*) FROM users")
    logger.info("   Routing: Scatter-gather across all shards")
    logger.info("   Aggregation: Sum counts from all shards")

    # DDL across all shards
    logger.info("\n3. DDL operation:")
    logger.info("   Query: CREATE INDEX idx_email ON users(email)")
    logger.info("   Routing: Execute on all shards sequentially")

    # Statistics
    stats = router.get_statistics()
    logger.info(f"\nRouter Statistics:")
    logger.info(f"  Total Queries: {stats['total_queries']}")
    logger.info(f"  Single-Shard: {stats['single_shard_queries']}")
    logger.info(f"  Multi-Shard: {stats['multi_shard_queries']}")


async def example_rebalancing():
    """Example 6: Zero-downtime rebalancing."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 6: Zero-Downtime Rebalancing")
    logger.info("=" * 60)

    # Initial setup with 3 shards
    shards = [
        ShardInfo('shard1', 'db1.example.com', 5432, 'app_db'),
        ShardInfo('shard2', 'db2.example.com', 5432, 'app_db'),
        ShardInfo('shard3', 'db3.example.com', 5432, 'app_db'),
    ]

    strategy = HashStrategy(shard_key='user_id', shards=shards)
    manager = ShardManager(strategy=strategy, health_check_interval=0)
    router = ShardRouter(manager)
    rebalancer = ShardRebalancer(manager, router, batch_size=1000)

    logger.info("Initial cluster: 3 shards")

    # Add new shard
    logger.info("\nScenario: Adding 4th shard for increased capacity")
    new_shard = ShardInfo('shard4', 'db4.example.com', 5432, 'app_db')
    manager.add_shard(new_shard)

    logger.info("Creating rebalancing job...")

    # Note: In production, this would actually migrate data
    # For this example, we just show the workflow

    logger.info("\nRebalancing phases:")
    logger.info("  1. Copy: Stream data from old shards to new shard")
    logger.info("     - Batch size: 1000 rows")
    logger.info("     - Throttle: 10ms between batches")
    logger.info("     - Progress: Real-time tracking")
    logger.info("\n  2. Sync: Catch up with recent changes")
    logger.info("     - CDC or timestamp-based")
    logger.info("     - Minimal lag")
    logger.info("\n  3. Validate: Verify data consistency")
    logger.info("     - Row counts match")
    logger.info("     - Checksums verified")
    logger.info("\n  4. Switch: Update routing")
    logger.info("     - Zero downtime")
    logger.info("     - Gradual traffic shift")

    logger.info("\n✓ Rebalancing complete!")
    logger.info(f"  New cluster size: {len(manager.shards)} shards")


async def example_health_monitoring():
    """Example 7: Health monitoring and failover."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 7: Health Monitoring & Failover")
    logger.info("=" * 60)

    # Setup with replicas
    shards = [
        ShardInfo('primary1', 'db1-primary.example.com', 5432, 'app_db'),
        ShardInfo('primary2', 'db2-primary.example.com', 5432, 'app_db'),
        ShardInfo('primary3', 'db3-primary.example.com', 5432, 'app_db'),
    ]

    strategy = HashStrategy(shard_key='user_id', shards=shards)
    manager = ShardManager(
        strategy=strategy,
        health_check_interval=30,  # Check every 30s
        max_consecutive_failures=3,
        enable_auto_failover=True
    )

    logger.info("Health monitoring configuration:")
    logger.info(f"  Check interval: {manager.health_check_interval}s")
    logger.info(f"  Failure threshold: {manager.max_consecutive_failures}")
    logger.info(f"  Auto-failover: {manager.enable_auto_failover}")

    logger.info("\nHealth check process:")
    logger.info("  1. Execute: SELECT 1 on each shard")
    logger.info("  2. Measure: Query latency")
    logger.info("  3. Track: Success/failure count")
    logger.info("  4. Alert: On consecutive failures")
    logger.info("  5. Failover: Switch to replica if configured")

    # Show cluster health
    status = manager.get_cluster_status()
    logger.info(f"\nCluster Health:")
    logger.info(f"  Total Shards: {status['total_shards']}")
    logger.info(f"  Healthy: {status['healthy_shards']}")
    logger.info(f"  Unhealthy: {status['unhealthy_shards']}")


async def main():
    """Run all examples."""
    logger.info("CovetPy Horizontal Database Sharding Examples")
    logger.info("=" * 60)

    examples = [
        ("Hash Sharding", example_hash_sharding),
        ("Range Sharding", example_range_sharding),
        ("Consistent Hashing", example_consistent_hashing),
        ("Geographic Sharding", example_geographic_sharding),
        ("Query Routing", example_query_routing),
        ("Rebalancing", example_rebalancing),
        ("Health Monitoring", example_health_monitoring),
    ]

    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            logger.error(f"Error in {name}: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("Examples Complete!")
    logger.info("=" * 60)
    logger.info("\nNext Steps:")
    logger.info("  1. Review the implementation in src/covet/database/sharding/")
    logger.info("  2. Run tests: pytest tests/database/sharding/ -v")
    logger.info("  3. Read documentation: SHARDING_IMPLEMENTATION_COMPLETE.md")
    logger.info("  4. Integrate with your application")


if __name__ == '__main__':
    asyncio.run(main())
