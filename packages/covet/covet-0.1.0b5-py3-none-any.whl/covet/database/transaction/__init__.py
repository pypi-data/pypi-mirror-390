"""
CovetPy Transaction Management Module

Enterprise-grade transaction management for CovetPy framework.

Features:
- Nested transactions (3+ levels) using SAVEPOINT
- Automatic retry logic with exponential backoff
- Deadlock detection and recovery
- Multiple isolation levels (READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE)
- Transaction hooks (pre_commit, post_commit, pre_rollback, post_rollback)
- Transaction timeout support
- Comprehensive monitoring and metrics
- Real-time dashboard
- Health monitoring and alerting

Quick Start:
    from covet.database.transaction import TransactionManager, IsolationLevel

    # Initialize with database adapter
    manager = TransactionManager(database_adapter)

    # Simple transaction
    async with manager.atomic() as txn:
        await txn.connection.execute("INSERT INTO users ...")

    # Nested transactions
    async with manager.atomic() as outer:
        await outer.connection.execute("INSERT INTO orders ...")

        async with manager.atomic() as inner:
            await inner.connection.execute("INSERT INTO order_items ...")
            # Inner can rollback without affecting outer

    # With retry on deadlock
    @manager.retry(max_attempts=3)
    async def transfer_funds(from_account, to_account, amount):
        async with manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
            # Transfer logic
            pass

    # Start monitoring dashboard
    from covet.database.transaction import TransactionDashboard

    dashboard = TransactionDashboard(manager)
    await dashboard.start()

    # Get dashboard HTML
    html = dashboard.get_dashboard_html()

Author: CovetPy Framework
License: MIT
"""

from .dashboard import (
    Alert,
    AlertLevel,
    TransactionDashboard,
    TransactionSnapshot,
)
from .manager import (
    DeadlockError,
    IsolationLevel,
    SavepointError,
    Transaction,
    TransactionConfig,
    TransactionError,
    TransactionHooks,
    TransactionManager,
    TransactionMetrics,
    TransactionState,
    TransactionTimeoutError,
    rollback_to,
    savepoint,
)

__all__ = [
    # Core transaction management
    "TransactionManager",
    "Transaction",
    "TransactionConfig",
    "TransactionHooks",
    "TransactionMetrics",
    "TransactionState",
    # Isolation levels
    "IsolationLevel",
    # Exceptions
    "TransactionError",
    "DeadlockError",
    "TransactionTimeoutError",
    "SavepointError",
    # Convenience functions
    "savepoint",
    "rollback_to",
    # Dashboard and monitoring
    "TransactionDashboard",
    "TransactionSnapshot",
    "Alert",
    "AlertLevel",
]

__version__ = "1.0.0"
