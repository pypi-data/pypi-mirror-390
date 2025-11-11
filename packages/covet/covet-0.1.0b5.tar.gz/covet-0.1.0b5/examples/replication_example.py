"""
Read Replica Usage Example

This example demonstrates how to use the read replica system
in a production application.
"""

import asyncio
import os
from datetime import datetime

# Import replication components
from src.covet.database.replication import (
    setup_replication,
    teardown_replication,
    get_replication_status,
    get_replica_manager,
    get_lag_monitor,
    get_failover_manager,
    FailoverStrategy,
    ReadPreference,
    ConsistencyLevel,
    AlertSeverity,
)


async def setup_example():
    """Setup replication system."""
    print("🔧 Setting up read replica system...")

    # Configure replication
    await setup_replication(
        # Primary database
        primary={
            'host': os.getenv('PRIMARY_HOST', 'localhost'),
            'port': int(os.getenv('PRIMARY_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'production'),
            'user': os.getenv('DB_USER', 'app_user'),
            'password': os.getenv('DB_PASSWORD', 'secure_password'),
            'ssl': 'require'  # Always use SSL in production
        },

        # Read replicas
        replicas=[
            {
                'host': os.getenv('REPLICA1_HOST', 'replica1.db.example.com'),
                'port': int(os.getenv('REPLICA1_PORT', 5432)),
                'region': 'us-east-1a',
                'datacenter': 'aws-us-east',
                'weight': 100,  # Full weight
                'max_lag_seconds': 5.0
            },
            {
                'host': os.getenv('REPLICA2_HOST', 'replica2.db.example.com'),
                'port': int(os.getenv('REPLICA2_PORT', 5432)),
                'region': 'us-west-2a',
                'datacenter': 'aws-us-west',
                'weight': 80,  # Slightly lower weight for cross-region
                'max_lag_seconds': 10.0  # Higher tolerance for distance
            }
        ],

        # Health monitoring
        health_check_interval=10.0,  # Check every 10 seconds
        max_lag_threshold=5.0,  # Alert if lag > 5 seconds

        # Failover configuration
        enable_auto_failover=True,
        failover_strategy=FailoverStrategy.SUPERVISED,
        min_replicas_for_failover=1,

        # Consistency
        default_read_preference=ReadPreference.REPLICA_PREFERRED,
        default_consistency=ConsistencyLevel.READ_AFTER_WRITE,
        read_after_write_window=5.0
    )

    print("✅ Replication system initialized!")


async def register_monitoring_callbacks():
    """Register callbacks for monitoring and alerting."""
    print("\n📊 Registering monitoring callbacks...")

    # Lag alert handler
    lag_monitor = get_lag_monitor()

    async def handle_lag_alert(alert):
        """Handle replication lag alerts."""
        if alert.severity == AlertSeverity.CRITICAL:
            print(f"🚨 CRITICAL LAG ALERT: {alert.message}")
            # In production: page on-call engineer
        elif alert.severity == AlertSeverity.ERROR:
            print(f"⚠️  ERROR LAG ALERT: {alert.message}")
            # In production: send high-priority alert
        else:
            print(f"ℹ️  LAG WARNING: {alert.message}")

    lag_monitor.register_alert_callback(handle_lag_alert)

    # Failover event handler
    failover_mgr = get_failover_manager()

    async def handle_failover(event):
        """Handle failover events."""
        print(f"\n🔄 FAILOVER EVENT:")
        print(f"   Reason: {event.reason.value}")
        print(f"   Old Primary: {event.old_primary_id}")
        print(f"   New Primary: {event.new_primary_id}")
        print(f"   Duration: {event.duration_seconds:.2f}s")
        print(f"   Success: {event.success}")

    failover_mgr.register_failover_callback(handle_failover)

    print("✅ Monitoring callbacks registered")


async def demonstrate_basic_usage():
    """Demonstrate basic ORM usage with automatic routing."""
    print("\n🔄 Demonstrating automatic routing...")

    # NOTE: This assumes User model exists
    # For this example, we'll simulate with print statements

    # Automatic routing (no code changes needed)
    print("\n1. Read query (routes to replica):")
    print("   user = await User.objects.get(id=123)")
    print("   → Automatically routed to nearest healthy replica")

    print("\n2. Write query (routes to primary):")
    print("   await user.save()")
    print("   → Automatically routed to primary")

    print("\n3. Bulk read (routes to replica):")
    print("   users = await User.objects.filter(active=True).all()")
    print("   → Automatically routed to replica")


async def demonstrate_explicit_routing():
    """Demonstrate explicit routing control."""
    print("\n🎯 Demonstrating explicit routing...")

    # Force read from primary
    print("\n1. Force primary read:")
    print("   admin = await User.objects.using('primary').get(id=1)")
    print("   → Explicitly routed to primary")

    # Force read from replica
    print("\n2. Force replica read:")
    print("   users = await User.objects.using('replica').all()")
    print("   → Explicitly routed to replica")


async def demonstrate_consistency():
    """Demonstrate consistency guarantees."""
    print("\n🔒 Demonstrating consistency guarantees...")

    from src.covet.database.replication import get_replication_router

    router = get_replication_router()

    # Create session for read-after-write consistency
    session_id = router.create_session()
    print(f"\n1. Created session: {session_id}")

    print("\n2. Write to primary:")
    print("   async with router.route_query('INSERT ...', session=session_id):")
    print("       await adapter.execute('INSERT INTO orders ...')")

    print("\n3. Read immediately sees the write:")
    print("   async with router.route_query('SELECT ...', session=session_id):")
    print("       order = await adapter.fetch_one('SELECT * FROM orders ...')")
    print("   → Routed to primary due to read-after-write consistency")


async def show_status():
    """Show current replication status."""
    print("\n📈 Current Replication Status:")
    print("=" * 70)

    status = get_replication_status()

    # Replica manager status
    if status['replica_manager']:
        metrics = status['replica_manager']['metrics']
        print(f"\n📦 Replica Manager:")
        print(f"   Total Replicas: {metrics['total_replicas']}")
        print(f"   Healthy: {metrics['healthy_replicas']}")
        print(f"   Degraded: {metrics['degraded_replicas']}")
        print(f"   Unhealthy: {metrics['unhealthy_replicas']}")

        print(f"\n   Replicas:")
        for replica in status['replica_manager']['replicas']:
            print(f"      • {replica['host']} ({replica['region']})")
            print(f"        Status: {replica['status']}")
            print(f"        Lag: {replica['lag_seconds']:.2f}s")
            print(f"        Response: {replica['response_time_ms']:.2f}ms")

    # Router status
    if status['router']:
        print(f"\n🔀 Router:")
        print(f"   Primary Routes: {status['router']['primary_routes']}")
        print(f"   Replica Routes: {status['router']['replica_routes']}")
        print(f"   Replica Hit Rate: {status['router']['replica_hit_rate_percent']:.1f}%")
        print(f"   Fallbacks to Primary: {status['router']['fallbacks_to_primary']}")

    # Lag monitor status
    if status['lag_monitor']:
        print(f"\n📊 Lag Monitor:")
        metrics = status['lag_monitor']['metrics']
        print(f"   Total Measurements: {metrics['total_measurements']}")
        print(f"   Total Alerts: {metrics['total_alerts']}")
        print(f"   Active Alerts: {status['lag_monitor']['active_alerts']}")

    # Failover manager status
    if status['failover_manager']:
        print(f"\n⚡ Failover Manager:")
        metrics = status['failover_manager']
        print(f"   Total Failovers: {metrics['total_failovers']}")
        print(f"   Success Rate: {metrics['success_rate_percent']:.1f}%")
        print(f"   Avg Failover Time: {metrics['average_failover_time_seconds']:.2f}s")
        print(f"   Strategy: {metrics['strategy']}")

    print("\n" + "=" * 70)


async def demonstrate_manual_failover():
    """Demonstrate manual failover for planned maintenance."""
    print("\n🔧 Demonstrating manual failover...")

    failover_mgr = get_failover_manager()

    print("\n1. Initiating planned failover:")
    print("   event = await failover_mgr.initiate_failover(")
    print("       reason=FailoverReason.PLANNED_MAINTENANCE,")
    print("       target_replica_id='replica1:5432/production'")
    print("   )")

    print("\n2. Failover process:")
    print("   → Validating conditions...")
    print("   → Electing new primary...")
    print("   → Promoting replica...")
    print("   → Reconfiguring topology...")
    print("   ✅ Complete!")

    print("\n3. Result:")
    print("   Duration: 2.4s")
    print("   New Primary: replica1:5432/production")


async def demonstrate_monitoring():
    """Demonstrate monitoring and metrics collection."""
    print("\n📊 Monitoring and Metrics...")

    replica_mgr = get_replica_manager()
    lag_monitor = get_lag_monitor()

    # Show replica statistics
    print("\n1. Replica Lag Statistics:")
    for replica_id, config, health in replica_mgr.get_all_replicas():
        stats = lag_monitor.get_lag_statistics(replica_id)
        if stats:
            print(f"\n   {replica_id}:")
            print(f"      Mean Lag: {stats.mean_lag:.2f}s")
            print(f"      P95 Lag: {stats.p95_lag:.2f}s")
            print(f"      P99 Lag: {stats.p99_lag:.2f}s")
            print(f"      Max Lag: {stats.max_lag:.2f}s")

    # Show active alerts
    print("\n2. Active Alerts:")
    active_alerts = lag_monitor.get_active_alerts()
    if active_alerts:
        for alert in active_alerts:
            print(f"   • {alert.severity.value.upper()}: {alert.message}")
    else:
        print("   ✅ No active alerts")


async def main():
    """Main example function."""
    print("\n" + "=" * 70)
    print("  READ REPLICA SYSTEM - USAGE EXAMPLE")
    print("=" * 70)

    try:
        # Setup
        await setup_example()

        # Register callbacks
        await register_monitoring_callbacks()

        # Show current status
        await show_status()

        # Demonstrate features
        await demonstrate_basic_usage()
        await demonstrate_explicit_routing()
        await demonstrate_consistency()
        await demonstrate_manual_failover()
        await demonstrate_monitoring()

        # Keep running for monitoring
        print("\n⏰ System running... (Press Ctrl+C to stop)")
        print("\n   Monitoring health checks and replication lag...")
        print("   Check status every 30 seconds:")

        for i in range(3):  # Run for 90 seconds
            await asyncio.sleep(30)
            print(f"\n📊 Status Update #{i+1}:")
            await show_status()

    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down...")

    finally:
        # Cleanup
        await teardown_replication()
        print("✅ System shutdown complete")


if __name__ == "__main__":
    """Run the example."""
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║           CovetPy Read Replica System - Example Usage             ║
    ║                                                                    ║
    ║  This example demonstrates the complete read replica system        ║
    ║  including automatic routing, monitoring, and failover.            ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)

    # Run async main
    asyncio.run(main())
