"""
CovetPy Transaction Management - Usage Examples

This file demonstrates all features of the transaction management system.
Run these examples to see how to use transactions in your application.

Author: CovetPy Framework
License: MIT
"""

import asyncio
import logging
from covet.database.transaction import (
    TransactionManager,
    TransactionDashboard,
    IsolationLevel,
    TransactionHooks,
    DeadlockError,
)
from covet.database.adapters.postgresql import PostgreSQLAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Basic Transaction
# ============================================================================

async def example_basic_transaction(manager: TransactionManager):
    """Demonstrate basic transaction with automatic commit."""
    logger.info("Example 1: Basic Transaction")

    async with manager.atomic() as txn:
        await txn.connection.execute(
            "INSERT INTO users (name, email) VALUES ($1, $2)",
            ("Alice", "alice@example.com")
        )
        logger.info("Transaction will commit automatically")


# ============================================================================
# Example 2: Transaction with Rollback
# ============================================================================

async def example_rollback_transaction(manager: TransactionManager):
    """Demonstrate automatic rollback on exception."""
    logger.info("Example 2: Transaction with Rollback")

    try:
        async with manager.atomic() as txn:
            await txn.connection.execute(
                "INSERT INTO users (name, email) VALUES ($1, $2)",
                ("Bob", "bob@example.com")
            )
            raise ValueError("Simulated error")
    except ValueError:
        logger.info("Transaction rolled back automatically")


# ============================================================================
# Example 3: Nested Transactions (3+ levels)
# ============================================================================

async def example_nested_transactions(manager: TransactionManager):
    """Demonstrate nested transactions with SAVEPOINT."""
    logger.info("Example 3: Nested Transactions (3 levels)")

    async with manager.atomic() as level1:
        logger.info(f"Level 1 transaction started (level={level1.level})")

        await level1.connection.execute(
            "INSERT INTO organizations (name) VALUES ($1)",
            ("Acme Corp",)
        )

        async with manager.atomic() as level2:
            logger.info(f"Level 2 transaction started (level={level2.level})")

            await level2.connection.execute(
                "INSERT INTO departments (org_id, name) VALUES ($1, $2)",
                (1, "Engineering")
            )

            async with manager.atomic() as level3:
                logger.info(f"Level 3 transaction started (level={level3.level})")

                await level3.connection.execute(
                    "INSERT INTO teams (dept_id, name) VALUES ($1, $2)",
                    (1, "Backend Team")
                )

                logger.info("All 3 levels will commit")


# ============================================================================
# Example 4: Nested Transaction with Inner Rollback
# ============================================================================

async def example_nested_rollback(manager: TransactionManager):
    """Demonstrate inner transaction rollback without affecting outer."""
    logger.info("Example 4: Nested Transaction with Inner Rollback")

    async with manager.atomic() as outer:
        await outer.connection.execute(
            "INSERT INTO accounts (id, balance) VALUES ($1, $2)",
            (1, 1000.0)
        )
        logger.info("Outer transaction: Account created")

        # Inner transaction will fail
        try:
            async with manager.atomic() as inner:
                await inner.connection.execute(
                    "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                    (100.0, 1)
                )
                raise ValueError("Payment failed")
        except ValueError:
            logger.info("Inner transaction rolled back")

        # Outer transaction continues
        await outer.connection.execute(
            "INSERT INTO audit_log (message) VALUES ($1)",
            ("Payment failed, account unchanged",)
        )
        logger.info("Outer transaction commits successfully")


# ============================================================================
# Example 5: Manual Savepoint Control
# ============================================================================

async def example_manual_savepoints(manager: TransactionManager):
    """Demonstrate manual savepoint creation and rollback."""
    logger.info("Example 5: Manual Savepoint Control")

    async with manager.atomic() as txn:
        # Create savepoint before risky operation
        sp1 = await txn.create_savepoint("before_update")
        logger.info(f"Created savepoint: {sp1}")

        await txn.connection.execute(
            "UPDATE users SET balance = balance - 100 WHERE id = $1",
            (1,)
        )

        # Simulate validation failure
        if True:  # Simulate condition
            await txn.rollback_to_savepoint(sp1)
            logger.info("Rolled back to savepoint")

        # Transaction continues with original state
        await txn.connection.execute(
            "INSERT INTO audit_log (message) VALUES ($1)",
            ("Update cancelled",)
        )


# ============================================================================
# Example 6: Retry Decorator with Deadlock Recovery
# ============================================================================

async def example_retry_decorator(manager: TransactionManager):
    """Demonstrate automatic retry on deadlock."""
    logger.info("Example 6: Retry Decorator")

    attempt_count = 0

    @manager.retry(max_attempts=3, initial_delay=0.5, backoff_multiplier=2.0)
    async def transfer_funds():
        nonlocal attempt_count
        attempt_count += 1
        logger.info(f"Transfer attempt {attempt_count}")

        async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
            # Simulate deadlock on first 2 attempts
            if attempt_count < 3:
                raise DeadlockError("Simulated deadlock")

            await txn.connection.execute(
                "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                (100.0, 1)
            )
            await txn.connection.execute(
                "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
                (100.0, 2)
            )
            logger.info("Transfer successful")

    await transfer_funds()
    logger.info(f"Completed after {attempt_count} attempts")


# ============================================================================
# Example 7: Isolation Levels
# ============================================================================

async def example_isolation_levels(manager: TransactionManager):
    """Demonstrate different isolation levels."""
    logger.info("Example 7: Isolation Levels")

    # READ COMMITTED (default) - prevents dirty reads
    async with manager.atomic(isolation=IsolationLevel.READ_COMMITTED) as txn:
        logger.info("Using READ COMMITTED isolation")
        await txn.connection.execute("SELECT * FROM users")

    # REPEATABLE READ - prevents dirty and non-repeatable reads
    async with manager.atomic(isolation=IsolationLevel.REPEATABLE_READ) as txn:
        logger.info("Using REPEATABLE READ isolation")
        await txn.connection.execute("SELECT * FROM accounts")

    # SERIALIZABLE - highest isolation, prevents all anomalies
    async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
        logger.info("Using SERIALIZABLE isolation")
        await txn.connection.execute("UPDATE accounts SET balance = balance - 100")


# ============================================================================
# Example 8: Transaction Hooks
# ============================================================================

async def example_transaction_hooks(manager: TransactionManager):
    """Demonstrate transaction lifecycle hooks."""
    logger.info("Example 8: Transaction Hooks")

    async def pre_commit_hook(txn):
        logger.info(f"PRE-COMMIT: Transaction {txn.transaction_id[:8]} about to commit")

    async def post_commit_hook(txn):
        logger.info(f"POST-COMMIT: Transaction {txn.transaction_id[:8]} committed successfully")
        # Send notification, invalidate cache, etc.

    async def pre_rollback_hook(txn):
        logger.info(f"PRE-ROLLBACK: Transaction {txn.transaction_id[:8]} about to rollback")

    async def post_rollback_hook(txn):
        logger.info(f"POST-ROLLBACK: Transaction {txn.transaction_id[:8]} rolled back")
        # Log error, trigger alerts, etc.

    hooks = TransactionHooks(
        pre_commit=pre_commit_hook,
        post_commit=post_commit_hook,
        pre_rollback=pre_rollback_hook,
        post_rollback=post_rollback_hook,
    )

    # Successful transaction
    async with manager.atomic(hooks=hooks) as txn:
        await txn.connection.execute("INSERT INTO users (name) VALUES ($1)", ("Charlie",))

    # Failed transaction
    try:
        async with manager.atomic(hooks=hooks) as txn:
            await txn.connection.execute("INSERT INTO users (name) VALUES ($1)", ("David",))
            raise ValueError("Simulated error")
    except ValueError:
        pass


# ============================================================================
# Example 9: Transaction Timeout
# ============================================================================

async def example_transaction_timeout(manager: TransactionManager):
    """Demonstrate transaction timeout."""
    logger.info("Example 9: Transaction Timeout")

    try:
        # Transaction will timeout after 2 seconds
        async with manager.atomic(timeout=2.0) as txn:
            await txn.connection.execute("SELECT * FROM users")
            logger.info("Sleeping for 3 seconds (will timeout)")
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        logger.warning("Transaction timed out (as expected)")


# ============================================================================
# Example 10: Read-Only Transactions
# ============================================================================

async def example_readonly_transaction(manager: TransactionManager):
    """Demonstrate read-only transaction optimization."""
    logger.info("Example 10: Read-Only Transaction")

    async with manager.atomic(read_only=True) as txn:
        logger.info("Read-only transaction - optimized for queries")
        result = await txn.connection.fetch("SELECT * FROM users LIMIT 10")
        logger.info(f"Retrieved {len(result)} rows")


# ============================================================================
# Example 11: Monitoring Metrics
# ============================================================================

async def example_monitoring_metrics(manager: TransactionManager):
    """Demonstrate metrics collection and monitoring."""
    logger.info("Example 11: Monitoring Metrics")

    # Run some transactions
    for i in range(5):
        async with manager.atomic() as txn:
            await txn.connection.execute(
                "INSERT INTO users (name) VALUES ($1)",
                (f"User{i}",)
            )

    # Get metrics
    metrics = manager.get_metrics()
    logger.info("Transaction Metrics:")
    logger.info(f"  Total: {metrics['total_transactions']}")
    logger.info(f"  Committed: {metrics['committed_transactions']}")
    logger.info(f"  Success Rate: {metrics['success_rate']:.1f}%")
    logger.info(f"  Avg Duration: {metrics['average_duration_ms']:.2f}ms")
    logger.info(f"  Active: {metrics['active_transactions']}")

    # Get active transactions
    active = manager.get_active_transactions()
    logger.info(f"Active Transactions: {len(active)}")


# ============================================================================
# Example 12: Transaction Dashboard
# ============================================================================

async def example_transaction_dashboard(manager: TransactionManager):
    """Demonstrate transaction dashboard."""
    logger.info("Example 12: Transaction Dashboard")

    # Create dashboard
    dashboard = TransactionDashboard(
        transaction_manager=manager,
        history_retention=3600,  # 1 hour
        snapshot_interval=10.0,  # 10 seconds
    )

    # Start dashboard
    await dashboard.start()
    logger.info("Dashboard started")

    # Run some transactions
    for i in range(10):
        async with manager.atomic() as txn:
            await txn.connection.execute(
                "INSERT INTO users (name) VALUES ($1)",
                (f"User{i}",)
            )
        await asyncio.sleep(0.5)

    # Get dashboard data
    current_metrics = dashboard.get_current_metrics()
    logger.info(f"Current Metrics: {current_metrics}")

    health_status = dashboard.get_health_status()
    logger.info(f"Health Status: {health_status['status']}")
    logger.info(f"Health Score: {health_status['health_score']}/100")

    # Get historical data
    history = dashboard.get_history(minutes=5)
    logger.info(f"History: {len(history)} snapshots")

    # Get alerts
    alerts = dashboard.get_alerts(limit=5)
    logger.info(f"Recent Alerts: {len(alerts)}")

    # Generate HTML dashboard
    html = dashboard.get_dashboard_html()
    with open('/tmp/transaction_dashboard.html', 'w') as f:
        f.write(html)
    logger.info("Dashboard HTML saved to /tmp/transaction_dashboard.html")

    # Generate JSON report
    json_report = dashboard.generate_report(format='json')
    logger.info(f"JSON Report: {len(json_report)} bytes")

    # Stop dashboard
    await dashboard.stop()
    logger.info("Dashboard stopped")


# ============================================================================
# Example 13: Complete E-commerce Order Processing
# ============================================================================

async def example_ecommerce_order(manager: TransactionManager):
    """Complete example: E-commerce order processing with full transaction management."""
    logger.info("Example 13: E-commerce Order Processing")

    @manager.retry(max_attempts=3)
    async def process_order(user_id: int, items: list, total: float):
        """Process an order with nested transactions and hooks."""

        # Hooks for notifications
        async def send_order_confirmation(txn):
            logger.info(f"Sending order confirmation email...")

        hooks = TransactionHooks(post_commit=send_order_confirmation)

        async with manager.atomic(
            isolation=IsolationLevel.SERIALIZABLE,
            hooks=hooks
        ) as order_txn:
            # Create order
            order_id = await order_txn.connection.fetchval(
                "INSERT INTO orders (user_id, total, status) VALUES ($1, $2, 'pending') RETURNING id",
                (user_id, total)
            )
            logger.info(f"Created order {order_id}")

            # Add order items (nested transactions)
            for item in items:
                try:
                    async with manager.atomic() as item_txn:
                        # Check inventory
                        available = await item_txn.connection.fetchval(
                            "SELECT quantity FROM inventory WHERE product_id = $1 FOR UPDATE",
                            (item['product_id'],)
                        )

                        if available < item['quantity']:
                            raise ValueError(f"Insufficient inventory: {item['product_id']}")

                        # Insert order item
                        await item_txn.connection.execute(
                            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
                            (order_id, item['product_id'], item['quantity'], item['price'])
                        )

                        # Update inventory
                        await item_txn.connection.execute(
                            "UPDATE inventory SET quantity = quantity - $1 WHERE product_id = $2",
                            (item['quantity'], item['product_id'])
                        )

                        logger.info(f"Added item {item['product_id']} to order")

                except ValueError as e:
                    logger.error(f"Failed to add item: {e}")
                    raise

            # Update order status
            await order_txn.connection.execute(
                "UPDATE orders SET status = 'completed' WHERE id = $1",
                (order_id,)
            )

            logger.info(f"Order {order_id} completed successfully")
            return order_id

    # Process order
    items = [
        {'product_id': 101, 'quantity': 2, 'price': 29.99},
        {'product_id': 102, 'quantity': 1, 'price': 49.99},
    ]
    total = sum(item['quantity'] * item['price'] for item in items)

    try:
        order_id = await process_order(user_id=1, items=items, total=total)
        logger.info(f"Successfully processed order {order_id}")
    except Exception as e:
        logger.error(f"Order processing failed: {e}")


# ============================================================================
# Main Function - Run All Examples
# ============================================================================

async def main():
    """Run all transaction examples."""
    logger.info("=" * 80)
    logger.info("CovetPy Transaction Management - Examples")
    logger.info("=" * 80)

    # Initialize database adapter
    # NOTE: Update these credentials for your environment
    adapter = PostgreSQLAdapter(
        host='localhost',
        port=5432,
        database='test_db',
        user='postgres',
        password='postgres',
        min_pool_size=5,
        max_pool_size=20,
    )

    try:
        # Connect to database
        await adapter.connect()
        logger.info("Connected to database")

        # Create transaction manager
        manager = TransactionManager(
            adapter,
            long_transaction_threshold=5.0  # 5 seconds
        )

        # Start background monitoring
        await manager.start_monitoring(interval=60.0)

        # Run examples
        examples = [
            ("Basic Transaction", example_basic_transaction),
            ("Rollback Transaction", example_rollback_transaction),
            ("Nested Transactions", example_nested_transactions),
            ("Nested Rollback", example_nested_rollback),
            ("Manual Savepoints", example_manual_savepoints),
            ("Retry Decorator", example_retry_decorator),
            ("Isolation Levels", example_isolation_levels),
            ("Transaction Hooks", example_transaction_hooks),
            ("Transaction Timeout", example_transaction_timeout),
            ("Read-Only Transaction", example_readonly_transaction),
            ("Monitoring Metrics", example_monitoring_metrics),
            ("Transaction Dashboard", example_transaction_dashboard),
            ("E-commerce Order", example_ecommerce_order),
        ]

        for name, example_func in examples:
            logger.info("")
            logger.info("=" * 80)
            try:
                await example_func(manager)
                logger.info(f"✓ {name} completed")
            except Exception as e:
                logger.error(f"✗ {name} failed: {e}")
            logger.info("=" * 80)
            await asyncio.sleep(1)  # Pause between examples

        # Stop monitoring
        await manager.stop_monitoring()

        # Final metrics
        logger.info("")
        logger.info("=" * 80)
        logger.info("Final Metrics:")
        metrics = manager.get_metrics()
        for key, value in metrics.items():
            logger.info(f"  {key}: {value}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error running examples: {e}")
        raise

    finally:
        # Disconnect from database
        await adapter.disconnect()
        logger.info("Disconnected from database")


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
