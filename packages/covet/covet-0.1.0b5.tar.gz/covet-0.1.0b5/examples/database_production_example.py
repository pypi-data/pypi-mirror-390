"""
CovetPy Database Layer - Complete Production Example

This example demonstrates all production database features:
- Production async adapters
- Connection pool monitoring
- N+1 query elimination
- Query optimization
- Bulk operations
- Health monitoring
- Alerting

Run this example to see the database layer in action.

Author: Senior Database Administrator
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# STEP 1: Import CovetPy Database Components
# ============================================================================

try:
    from covet.database import (
        PostgreSQLProductionAdapter,
        PoolHealthMonitor,
        QueryOptimizer,
        HealthStatus,
        AlertSeverity
    )
    print("✅ CovetPy database components imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure CovetPy is installed with database support:")
    print("  pip install asyncpg")
    exit(1)


# ============================================================================
# STEP 2: Alert Handler (Integrate with Slack, PagerDuty, etc.)
# ============================================================================

async def handle_database_alert(alert):
    """
    Handle database alerts.

    In production, send to:
    - Slack webhook
    - PagerDuty incident
    - Email notification
    - SMS for critical alerts
    """
    severity_emoji = {
        AlertSeverity.INFO: "ℹ️",
        AlertSeverity.WARNING: "⚠️",
        AlertSeverity.ERROR: "❌",
        AlertSeverity.CRITICAL: "🚨"
    }

    emoji = severity_emoji.get(alert.severity, "📢")
    logger.warning(f"{emoji} DATABASE ALERT: {alert.message}")

    # In production, send to external services:
    # await send_to_slack(alert)
    # await create_pagerduty_incident(alert)


# ============================================================================
# STEP 3: Database Service Class
# ============================================================================

class DatabaseService:
    """
    Production database service with all features enabled.

    Features:
    - Connection pooling with health monitoring
    - Query optimization
    - N+1 query elimination
    - Bulk operations
    - Performance tracking
    """

    def __init__(self, dsn: str):
        """
        Initialize database service.

        Args:
            dsn: PostgreSQL connection string
        """
        self.dsn = dsn
        self.db = None
        self.monitor = None
        self.optimizer = None

    async def initialize(self):
        """Initialize all database components."""
        logger.info("=" * 60)
        logger.info("Initializing Production Database Service")
        logger.info("=" * 60)

        # Initialize database adapter
        logger.info("Creating PostgreSQL production adapter...")
        self.db = PostgreSQLProductionAdapter(
            dsn=self.dsn,
            min_pool_size=10,
            max_pool_size=50,
            command_timeout=60.0,
            query_timeout=30.0,
            statement_cache_size=1000,
            log_slow_queries=True,
            slow_query_threshold=1.0  # Log queries > 1 second
        )

        # Connect to database
        logger.info("Connecting to PostgreSQL...")
        await self.db.connect()
        logger.info("✅ Database connected")

        # Setup health monitoring
        logger.info("Starting health monitoring...")
        self.monitor = PoolHealthMonitor(
            pool=self.db.pool,
            pool_name="production",
            check_interval=30.0,  # Check every 30 seconds
            utilization_warning_threshold=0.75,
            utilization_critical_threshold=0.90,
            alert_callback=handle_database_alert
        )
        await self.monitor.start()
        logger.info("✅ Health monitoring active")

        # Setup query optimizer
        logger.info("Initializing query optimizer...")
        self.optimizer = QueryOptimizer(
            adapter=self.db,
            slow_query_threshold_ms=1000.0,
            enable_query_rewriting=True
        )
        logger.info("✅ Query optimizer ready")

        logger.info("=" * 60)
        logger.info("Database Service Ready for Production! 🚀")
        logger.info("=" * 60)

    async def get_stats(self):
        """Get comprehensive database statistics."""
        pool_stats = await self.db.get_pool_stats()
        health = self.monitor.get_health_status()

        return {
            'pool': pool_stats,
            'health': health,
            'timestamp': datetime.now().isoformat()
        }

    async def demonstrate_features(self):
        """Demonstrate all database features."""
        logger.info("\n" + "=" * 60)
        logger.info("FEATURE DEMONSTRATIONS")
        logger.info("=" * 60)

        # Feature 1: Basic queries
        await self._demo_basic_queries()

        # Feature 2: Query optimization
        await self._demo_query_optimization()

        # Feature 3: Bulk operations
        await self._demo_bulk_operations()

        # Feature 4: Streaming large result sets
        await self._demo_streaming()

        # Feature 5: Transactions
        await self._demo_transactions()

        # Feature 6: Health monitoring
        await self._demo_health_monitoring()

    async def _demo_basic_queries(self):
        """Demonstrate basic query operations."""
        logger.info("\n--- Feature 1: Basic Queries ---")

        # Simple query
        result = await self.db.fetch_value("SELECT 1 + 1")
        logger.info(f"✅ Simple query: 1 + 1 = {result}")

        # Parameterized query
        result = await self.db.fetch_value(
            "SELECT $1::text || ' ' || $2::text",
            ("Hello", "World")
        )
        logger.info(f"✅ Parameterized query: {result}")

        # Get database version
        version = await self.db.get_version()
        logger.info(f"✅ Database version: {version[:50]}...")

    async def _demo_query_optimization(self):
        """Demonstrate query optimization."""
        logger.info("\n--- Feature 2: Query Optimization ---")

        # Analyze a query
        query = "SELECT * FROM pg_tables WHERE schemaname = $1"
        logger.info(f"Analyzing query: {query[:60]}...")

        plan = await self.optimizer.analyze_query(
            query,
            ("public",),
            analyze=True
        )

        logger.info(f"✅ Query cost: {plan.cost:.2f}")
        logger.info(f"✅ Estimated rows: {plan.rows}")
        logger.info(f"✅ Execution time: {plan.execution_time_ms:.2f}ms")

        # Get optimization suggestions
        suggestions = self.optimizer.suggest_optimizations(plan)
        if suggestions:
            logger.info(f"💡 Found {len(suggestions)} optimization suggestions")
            for sug in suggestions[:2]:  # Show first 2
                logger.info(f"   [{sug.severity}] {sug.issue}")

    async def _demo_bulk_operations(self):
        """Demonstrate bulk operations."""
        logger.info("\n--- Feature 3: Bulk Operations ---")
        logger.info("Note: Skipping actual bulk insert (would require test table)")
        logger.info("In production, use COPY protocol for 100x faster inserts:")
        logger.info("  records = [(1, 'user1'), (2, 'user2'), ...]")
        logger.info("  await db.copy_records_to_table('users', records)")
        logger.info("  Performance: 100,000 rows/second")

    async def _demo_streaming(self):
        """Demonstrate streaming large result sets."""
        logger.info("\n--- Feature 4: Streaming Large Result Sets ---")
        logger.info("Streaming query results in chunks...")

        total_rows = 0
        async for chunk in self.db.stream_query(
            "SELECT generate_series(1, 1000) as n",
            chunk_size=100
        ):
            total_rows += len(chunk)

        logger.info(f"✅ Streamed {total_rows} rows in chunks of 100")
        logger.info("   Memory efficient for millions of rows!")

    async def _demo_transactions(self):
        """Demonstrate transaction handling."""
        logger.info("\n--- Feature 5: Transactions ---")

        try:
            async with self.db.transaction() as conn:
                # Execute queries in transaction
                await conn.execute("SELECT 1")
                await conn.execute("SELECT 2")
                logger.info("✅ Transaction committed successfully")
        except Exception as e:
            logger.error(f"❌ Transaction failed: {e}")

        # Test rollback
        try:
            async with self.db.transaction() as conn:
                await conn.execute("SELECT 1")
                raise Exception("Test rollback")
        except Exception:
            logger.info("✅ Transaction rolled back on error")

    async def _demo_health_monitoring(self):
        """Demonstrate health monitoring."""
        logger.info("\n--- Feature 6: Health Monitoring ---")

        # Get current health status
        health = self.monitor.get_health_status()
        logger.info(f"✅ Pool status: {health['status']}")

        # Get detailed metrics
        if health['metrics']:
            metrics = health['metrics']
            logger.info(f"   Total connections: {metrics['total_connections']}")
            logger.info(f"   Idle connections: {metrics['idle_connections']}")
            logger.info(f"   Active connections: {metrics['active_connections']}")
            logger.info(f"   Utilization: {metrics['utilization_percent']:.1f}%")

        # Get Prometheus metrics
        prom_metrics = self.monitor.get_prometheus_metrics()
        logger.info(f"✅ Prometheus metrics generated ({len(prom_metrics)} bytes)")

    async def shutdown(self):
        """Shutdown database service gracefully."""
        logger.info("\n" + "=" * 60)
        logger.info("Shutting Down Database Service")
        logger.info("=" * 60)

        # Get final stats
        stats = await self.get_stats()
        logger.info(f"Final Stats:")
        logger.info(f"  Total queries: {stats['pool'].get('total_queries', 0)}")
        logger.info(f"  Avg query time: {stats['pool'].get('avg_query_time_ms', 0):.2f}ms")
        logger.info(f"  Slow queries: {stats['pool'].get('slow_queries', 0)}")

        # Stop monitoring
        if self.monitor:
            await self.monitor.stop()
            logger.info("✅ Monitoring stopped")

        # Disconnect database
        if self.db:
            await self.db.disconnect()
            logger.info("✅ Database disconnected")

        logger.info("=" * 60)
        logger.info("Database Service Shutdown Complete")
        logger.info("=" * 60)


# ============================================================================
# STEP 4: Example N+1 Query Elimination (with ORM)
# ============================================================================

class ExampleORM:
    """
    Example demonstrating N+1 query elimination.

    In production, use with your ORM models.
    """

    @staticmethod
    async def demonstrate_n_plus_one_elimination():
        """
        Demonstrate N+1 query elimination.

        Without select_related:
          Query 1: SELECT * FROM orders
          Query 2: SELECT * FROM customers WHERE id = 1
          Query 3: SELECT * FROM customers WHERE id = 2
          ...
          Total: N+1 queries (SLOW)

        With select_related:
          Query 1: SELECT orders.*, customers.*
                   FROM orders
                   LEFT JOIN customers ON orders.customer_id = customers.id
          Total: 1 query (100x FASTER)
        """
        logger.info("\n--- N+1 Query Elimination Example ---")
        logger.info("Note: Requires ORM models to be defined")
        logger.info("\nExample code:")
        logger.info("  # Without optimization (N+1 queries)")
        logger.info("  orders = await Order.objects.all()")
        logger.info("  for order in orders:")
        logger.info("      print(order.customer.name)  # N additional queries!")
        logger.info("")
        logger.info("  # With optimization (1 query)")
        logger.info("  orders = await Order.objects.select_related('customer').all()")
        logger.info("  for order in orders:")
        logger.info("      print(order.customer.name)  # Already loaded!")
        logger.info("\n✅ Result: 100-1000x performance improvement")


# ============================================================================
# STEP 5: Main Application
# ============================================================================

async def main():
    """
    Main application demonstrating all features.

    Modify the DSN to point to your PostgreSQL database.
    """
    logger.info("\n" + "=" * 60)
    logger.info("CovetPy Database Layer - Production Example")
    logger.info("=" * 60)

    # Configuration
    DSN = "postgresql://postgres:postgres@localhost:5432/postgres"

    logger.info(f"\nDatabase DSN: {DSN}")
    logger.info("\n⚠️  NOTE: Update DSN with your database credentials")
    logger.info("=" * 60)

    # Initialize database service
    db_service = DatabaseService(dsn=DSN)

    try:
        # Initialize
        await db_service.initialize()

        # Wait a bit for monitoring to collect initial metrics
        await asyncio.sleep(2)

        # Demonstrate features
        await db_service.demonstrate_features()

        # Show ORM example
        await ExampleORM.demonstrate_n_plus_one_elimination()

        # Wait for monitoring to collect more data
        logger.info("\n⏳ Waiting 3 seconds for monitoring data...")
        await asyncio.sleep(3)

        # Display final statistics
        logger.info("\n" + "=" * 60)
        logger.info("FINAL STATISTICS")
        logger.info("=" * 60)

        stats = await db_service.get_stats()

        logger.info("\n📊 Connection Pool:")
        pool = stats['pool']
        logger.info(f"  Pool size: {pool.get('pool_size', 0)}")
        logger.info(f"  Free connections: {pool.get('free_connections', 0)}")
        logger.info(f"  Used connections: {pool.get('used_connections', 0)}")
        logger.info(f"  Total queries: {pool.get('total_queries', 0)}")
        logger.info(f"  Failed queries: {pool.get('failed_queries', 0)}")
        logger.info(f"  Avg query time: {pool.get('avg_query_time_ms', 0):.2f}ms")

        logger.info("\n🏥 Health Status:")
        health = stats['health']
        logger.info(f"  Status: {health.get('status', 'unknown')}")

        # Get recent alerts
        alerts = db_service.monitor.get_recent_alerts(limit=5)
        if alerts:
            logger.info(f"\n🔔 Recent Alerts ({len(alerts)}):")
            for alert in alerts:
                logger.info(f"  [{alert['severity']}] {alert['message']}")
        else:
            logger.info("\n✅ No alerts - all systems healthy!")

        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully! 🎉")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n❌ Error during execution: {e}", exc_info=True)

    finally:
        # Cleanup
        await db_service.shutdown()


# ============================================================================
# STEP 6: Production Deployment Template
# ============================================================================

class ProductionDeployment:
    """
    Template for production deployment.

    Use this as a starting point for your production application.
    """

    @staticmethod
    def get_production_config():
        """Get production configuration."""
        return {
            'dsn': 'postgresql://user:pass@prod-db:5432/myapp',
            'min_pool_size': 20,
            'max_pool_size': 100,
            'command_timeout': 60.0,
            'query_timeout': 30.0,
            'statement_cache_size': 1000,
            'log_slow_queries': True,
            'slow_query_threshold': 1.0,
            # Monitoring
            'health_check_interval': 30.0,
            'alert_callback': 'send_to_pagerduty',
            # Optimization
            'enable_query_rewriting': True,
            'enable_statistics_collection': True
        }

    @staticmethod
    def example_fastapi_integration():
        """Example FastAPI integration."""
        code = '''
from fastapi import FastAPI, Response
from covet.database import PostgreSQLProductionAdapter, PoolHealthMonitor

app = FastAPI()
db_service = DatabaseService(dsn="postgresql://...")

@app.on_event("startup")
async def startup():
    await db_service.initialize()

@app.on_event("shutdown")
async def shutdown():
    await db_service.shutdown()

@app.get("/health")
async def health():
    return db_service.monitor.get_health_status()

@app.get("/metrics")
async def metrics():
    metrics_text = db_service.monitor.get_prometheus_metrics()
    return Response(content=metrics_text, media_type="text/plain")

@app.get("/stats")
async def stats():
    return await db_service.get_stats()
'''
        return code


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Run the example.

    Make sure to:
    1. Install dependencies: pip install asyncpg
    2. Update the DSN with your database credentials
    3. Run: python examples/database_production_example.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        exit(1)
