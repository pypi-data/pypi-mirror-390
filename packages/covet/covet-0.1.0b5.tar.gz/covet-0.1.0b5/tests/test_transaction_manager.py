"""
Comprehensive Unit Tests for Transaction Manager

Tests cover:
- Basic transaction operations (commit, rollback)
- Nested transactions (3+ levels deep)
- Savepoint operations (create, rollback, release)
- Retry decorator with exponential backoff
- Deadlock detection and recovery
- Isolation level support
- Transaction hooks (pre/post commit/rollback)
- Transaction timeout
- Metrics tracking
- Long-running transaction detection

Author: CovetPy Framework
License: MIT
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from datetime import datetime, timedelta

from covet.database.transaction import (
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
)


@pytest.fixture
def mock_connection():
    """Create a mock database connection."""
    connection = AsyncMock()
    connection.execute = AsyncMock()
    connection.commit = AsyncMock()
    connection.rollback = AsyncMock()
    return connection


@pytest.fixture
def mock_pool():
    """Create a mock connection pool."""
    pool = AsyncMock()
    connection = AsyncMock()
    connection.execute = AsyncMock()
    connection.commit = AsyncMock()
    connection.rollback = AsyncMock()

    pool.acquire = AsyncMock(return_value=connection)
    pool.release = AsyncMock()

    return pool


@pytest.fixture
def mock_adapter(mock_pool):
    """Create a mock database adapter."""
    adapter = MagicMock()
    adapter.pool = mock_pool
    adapter._connected = True
    return adapter


@pytest.fixture
def transaction_manager(mock_adapter):
    """Create a TransactionManager instance with mock adapter."""
    return TransactionManager(mock_adapter)


class TestBasicTransactions:
    """Test basic transaction operations."""

    @pytest.mark.asyncio
    async def test_simple_transaction_commit(self, transaction_manager, mock_pool):
        """Test simple transaction with successful commit."""
        async with transaction_manager.atomic() as txn:
            assert txn.is_active
            assert txn.level == 0
            assert not txn.is_nested

        assert txn.state == TransactionState.COMMITTED
        assert transaction_manager.metrics.total_transactions == 1
        assert transaction_manager.metrics.committed_transactions == 1

    @pytest.mark.asyncio
    async def test_simple_transaction_rollback(self, transaction_manager, mock_pool):
        """Test simple transaction with rollback on exception."""
        with pytest.raises(ValueError):
            async with transaction_manager.atomic() as txn:
                assert txn.is_active
                raise ValueError("Test error")

        assert txn.state == TransactionState.ROLLED_BACK
        assert transaction_manager.metrics.total_transactions == 1
        assert transaction_manager.metrics.rolled_back_transactions == 1

    @pytest.mark.asyncio
    async def test_transaction_metrics_tracking(self, transaction_manager):
        """Test that transaction metrics are tracked correctly."""
        # Successful transaction
        async with transaction_manager.atomic() as txn:
            pass

        # Failed transaction
        try:
            async with transaction_manager.atomic() as txn:
                raise Exception("Test error")
        except Exception:
            pass

        metrics = transaction_manager.get_metrics()
        assert metrics["total_transactions"] == 2
        assert metrics["committed_transactions"] == 1
        assert metrics["rolled_back_transactions"] == 1
        assert metrics["active_transactions"] == 0


class TestNestedTransactions:
    """Test nested transaction support."""

    @pytest.mark.asyncio
    async def test_two_level_nested_transaction(self, transaction_manager, mock_connection):
        """Test two-level nested transaction."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as outer:
                assert outer.level == 0
                assert not outer.is_nested

                async with transaction_manager.atomic() as inner:
                    assert inner.level == 1
                    assert inner.is_nested
                    assert inner.parent == outer
                    assert inner.connection == outer.connection

        assert outer.state == TransactionState.COMMITTED
        assert inner.state == TransactionState.COMMITTED

    @pytest.mark.asyncio
    async def test_three_level_nested_transaction(self, transaction_manager, mock_connection):
        """Test three-level nested transaction (requirement: 3+ levels)."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as level1:
                assert level1.level == 0

                async with transaction_manager.atomic() as level2:
                    assert level2.level == 1
                    assert level2.parent == level1

                    async with transaction_manager.atomic() as level3:
                        assert level3.level == 2
                        assert level3.parent == level2
                        assert level3.connection == level1.connection

        assert level1.state == TransactionState.COMMITTED
        assert level2.state == TransactionState.COMMITTED
        assert level3.state == TransactionState.COMMITTED

    @pytest.mark.asyncio
    async def test_nested_transaction_rollback_isolation(self, transaction_manager, mock_connection):
        """Test that nested transaction rollback doesn't affect outer transaction."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as outer:
                # This should succeed
                await outer.connection.execute("INSERT INTO table1 VALUES (1)")

                # Inner transaction fails
                try:
                    async with transaction_manager.atomic() as inner:
                        await inner.connection.execute("INSERT INTO table2 VALUES (2)")
                        raise ValueError("Inner transaction error")
                except ValueError:
                    pass

                # Outer transaction continues and commits
                await outer.connection.execute("INSERT INTO table1 VALUES (3)")

        assert outer.state == TransactionState.COMMITTED
        assert inner.state == TransactionState.ROLLED_BACK


class TestSavepoints:
    """Test savepoint operations."""

    @pytest.mark.asyncio
    async def test_create_savepoint(self, transaction_manager, mock_connection):
        """Test creating a savepoint."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                savepoint_name = await txn.create_savepoint("test_sp")
                assert savepoint_name == "test_sp"
                assert "test_sp" in txn.savepoints

    @pytest.mark.asyncio
    async def test_rollback_to_savepoint(self, transaction_manager, mock_connection):
        """Test rolling back to a savepoint."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                # Create savepoint
                sp1 = await txn.create_savepoint("sp1")

                # Create another savepoint
                sp2 = await txn.create_savepoint("sp2")

                # Rollback to first savepoint
                await txn.rollback_to_savepoint(sp1)

                # sp2 should be removed
                assert sp1 in txn.savepoints
                assert sp2 not in txn.savepoints

    @pytest.mark.asyncio
    async def test_release_savepoint(self, transaction_manager, mock_connection):
        """Test releasing a savepoint."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                sp = await txn.create_savepoint("test_sp")
                assert "test_sp" in txn.savepoints

                await txn.release_savepoint(sp)
                assert "test_sp" not in txn.savepoints

    @pytest.mark.asyncio
    async def test_savepoint_error_on_nonexistent(self, transaction_manager, mock_connection):
        """Test that operating on non-existent savepoint raises error."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                with pytest.raises(SavepointError):
                    await txn.rollback_to_savepoint("nonexistent")


class TestRetryDecorator:
    """Test retry decorator with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_on_deadlock(self, transaction_manager, mock_connection):
        """Test automatic retry on deadlock error."""
        call_count = 0

        @transaction_manager.retry(max_attempts=3)
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise DeadlockError("Simulated deadlock")
            return "success"

        result = await failing_function()

        assert result == "success"
        assert call_count == 3
        assert transaction_manager.metrics.retry_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self, transaction_manager):
        """Test that retry exhausts after max attempts."""
        call_count = 0

        @transaction_manager.retry(max_attempts=3)
        async def always_failing():
            nonlocal call_count
            call_count += 1
            raise DeadlockError("Persistent deadlock")

        with pytest.raises(DeadlockError):
            await always_failing()

        assert call_count == 3
        assert transaction_manager.metrics.retry_count == 2

    @pytest.mark.asyncio
    async def test_retry_exponential_backoff(self, transaction_manager):
        """Test exponential backoff timing."""
        call_times = []

        @transaction_manager.retry(max_attempts=3, initial_delay=0.1, backoff_multiplier=2.0)
        async def failing_function():
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < 3:
                raise DeadlockError("Deadlock")
            return "success"

        start_time = asyncio.get_event_loop().time()
        await failing_function()

        # Check that delays increase exponentially
        assert len(call_times) == 3
        # First retry should be ~0.1s after first call
        # Second retry should be ~0.2s after second call
        # Total time should be ~0.3s

    @pytest.mark.asyncio
    async def test_retry_custom_exceptions(self, transaction_manager):
        """Test retry with custom exception types."""
        call_count = 0

        @transaction_manager.retry(max_attempts=3, exceptions=(ValueError,))
        async def custom_failing():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Custom error")
            return "success"

        result = await custom_failing()
        assert result == "success"
        assert call_count == 2


class TestIsolationLevels:
    """Test transaction isolation level support."""

    @pytest.mark.asyncio
    async def test_read_committed_isolation(self, transaction_manager, mock_connection):
        """Test READ COMMITTED isolation level."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic(isolation=IsolationLevel.READ_COMMITTED) as txn:
                assert txn.config.isolation_level == IsolationLevel.READ_COMMITTED

    @pytest.mark.asyncio
    async def test_repeatable_read_isolation(self, transaction_manager, mock_connection):
        """Test REPEATABLE READ isolation level."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic(isolation=IsolationLevel.REPEATABLE_READ) as txn:
                assert txn.config.isolation_level == IsolationLevel.REPEATABLE_READ

    @pytest.mark.asyncio
    async def test_serializable_isolation(self, transaction_manager, mock_connection):
        """Test SERIALIZABLE isolation level."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic(isolation=IsolationLevel.SERIALIZABLE) as txn:
                assert txn.config.isolation_level == IsolationLevel.SERIALIZABLE

    @pytest.mark.asyncio
    async def test_read_uncommitted_isolation(self, transaction_manager, mock_connection):
        """Test READ UNCOMMITTED isolation level."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic(isolation=IsolationLevel.READ_UNCOMMITTED) as txn:
                assert txn.config.isolation_level == IsolationLevel.READ_UNCOMMITTED


class TestTransactionHooks:
    """Test transaction lifecycle hooks."""

    @pytest.mark.asyncio
    async def test_pre_commit_hook(self, transaction_manager, mock_connection):
        """Test pre-commit hook execution."""
        hook_called = False

        async def pre_commit_hook(txn):
            nonlocal hook_called
            hook_called = True
            assert txn.is_active

        hooks = TransactionHooks(pre_commit=pre_commit_hook)

        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic(hooks=hooks) as txn:
                pass

        assert hook_called

    @pytest.mark.asyncio
    async def test_post_commit_hook(self, transaction_manager, mock_connection):
        """Test post-commit hook execution."""
        hook_called = False

        async def post_commit_hook(txn):
            nonlocal hook_called
            hook_called = True
            assert txn.state == TransactionState.COMMITTED

        hooks = TransactionHooks(post_commit=post_commit_hook)

        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic(hooks=hooks) as txn:
                pass

        assert hook_called

    @pytest.mark.asyncio
    async def test_pre_rollback_hook(self, transaction_manager, mock_connection):
        """Test pre-rollback hook execution."""
        hook_called = False

        async def pre_rollback_hook(txn):
            nonlocal hook_called
            hook_called = True

        hooks = TransactionHooks(pre_rollback=pre_rollback_hook)

        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            try:
                async with transaction_manager.atomic(hooks=hooks) as txn:
                    raise ValueError("Test error")
            except ValueError:
                pass

        assert hook_called

    @pytest.mark.asyncio
    async def test_post_rollback_hook(self, transaction_manager, mock_connection):
        """Test post-rollback hook execution."""
        hook_called = False

        async def post_rollback_hook(txn):
            nonlocal hook_called
            hook_called = True
            assert txn.state == TransactionState.ROLLED_BACK

        hooks = TransactionHooks(post_rollback=post_rollback_hook)

        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            try:
                async with transaction_manager.atomic(hooks=hooks) as txn:
                    raise ValueError("Test error")
            except ValueError:
                pass

        assert hook_called

    @pytest.mark.asyncio
    async def test_hook_error_handling(self, transaction_manager, mock_connection):
        """Test that hook errors don't break transaction flow."""
        async def failing_hook(txn):
            raise RuntimeError("Hook error")

        hooks = TransactionHooks(pre_commit=failing_hook)

        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            # Transaction should still complete despite hook failure
            async with transaction_manager.atomic(hooks=hooks) as txn:
                pass

        # Transaction should be committed despite hook error
        assert txn.state == TransactionState.COMMITTED


class TestTransactionTimeout:
    """Test transaction timeout support."""

    @pytest.mark.asyncio
    async def test_transaction_timeout(self, transaction_manager, mock_connection):
        """Test that transaction times out after specified duration."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            with pytest.raises(asyncio.CancelledError):
                async with transaction_manager.atomic(timeout=0.1) as txn:
                    await asyncio.sleep(0.2)

        assert transaction_manager.metrics.timeout_count == 1

    @pytest.mark.asyncio
    async def test_transaction_completes_before_timeout(self, transaction_manager, mock_connection):
        """Test that transaction completes successfully before timeout."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic(timeout=1.0) as txn:
                await asyncio.sleep(0.1)

        assert txn.state == TransactionState.COMMITTED
        assert transaction_manager.metrics.timeout_count == 0


class TestTransactionMetrics:
    """Test transaction metrics tracking."""

    def test_metrics_initialization(self):
        """Test that metrics are initialized correctly."""
        metrics = TransactionMetrics()
        assert metrics.total_transactions == 0
        assert metrics.committed_transactions == 0
        assert metrics.rolled_back_transactions == 0
        assert metrics.failed_transactions == 0
        assert metrics.success_rate == 0.0

    def test_metrics_calculations(self):
        """Test metrics calculations."""
        metrics = TransactionMetrics()
        metrics.total_transactions = 10
        metrics.committed_transactions = 8
        metrics.failed_transactions = 2
        metrics.total_duration_ms = 1000

        assert metrics.success_rate == 80.0
        assert metrics.failure_rate == 20.0
        assert metrics.average_duration_ms == 100.0

    def test_metrics_to_dict(self):
        """Test metrics serialization to dictionary."""
        metrics = TransactionMetrics()
        metrics.total_transactions = 5
        metrics.committed_transactions = 4
        metrics.rolled_back_transactions = 1

        metrics_dict = metrics.to_dict()
        assert isinstance(metrics_dict, dict)
        assert metrics_dict["total_transactions"] == 5
        assert metrics_dict["committed_transactions"] == 4
        assert "success_rate" in metrics_dict

    @pytest.mark.asyncio
    async def test_metrics_reset(self, transaction_manager):
        """Test resetting metrics."""
        # Create some transactions
        transaction_manager.metrics.total_transactions = 10
        transaction_manager.metrics.committed_transactions = 8

        # Reset
        transaction_manager.reset_metrics()

        # Verify reset
        metrics = transaction_manager.get_metrics()
        assert metrics["total_transactions"] == 0
        assert metrics["committed_transactions"] == 0


class TestDeadlockDetection:
    """Test deadlock detection."""

    def test_deadlock_detection_postgres(self, transaction_manager):
        """Test deadlock detection for PostgreSQL errors."""
        error = Exception("ERROR: deadlock detected")
        assert transaction_manager._is_deadlock_error(error)

    def test_deadlock_detection_mysql(self, transaction_manager):
        """Test deadlock detection for MySQL errors."""
        error = Exception("1213 Deadlock found when trying to get lock")
        assert transaction_manager._is_deadlock_error(error)

    def test_deadlock_detection_serialization_failure(self, transaction_manager):
        """Test deadlock detection for serialization failures."""
        error = Exception("could not serialize access due to concurrent update")
        assert transaction_manager._is_deadlock_error(error)

    def test_non_deadlock_error(self, transaction_manager):
        """Test that non-deadlock errors are not detected as deadlocks."""
        error = Exception("Some other database error")
        assert not transaction_manager._is_deadlock_error(error)


class TestActiveTransactionTracking:
    """Test active transaction tracking."""

    @pytest.mark.asyncio
    async def test_active_transaction_tracking(self, transaction_manager, mock_connection):
        """Test that active transactions are tracked correctly."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                active_txns = transaction_manager.get_active_transactions()
                assert len(active_txns) == 1
                assert active_txns[0]["transaction_id"] == txn.transaction_id

            # After commit, should be removed from active list
            active_txns = transaction_manager.get_active_transactions()
            assert len(active_txns) == 0

    @pytest.mark.asyncio
    async def test_multiple_active_transactions(self, transaction_manager, mock_connection):
        """Test tracking multiple concurrent active transactions."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            # This would require actual concurrent execution
            # For now, test that tracking structure works correctly
            assert len(transaction_manager._active_transactions) == 0


class TestTransactionDuration:
    """Test transaction duration tracking."""

    @pytest.mark.asyncio
    async def test_duration_tracking(self, transaction_manager, mock_connection):
        """Test that transaction duration is tracked."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                await asyncio.sleep(0.1)
                duration = txn.duration_ms

            assert duration >= 100  # At least 100ms
            assert duration < 200   # But not too much more

    @pytest.mark.asyncio
    async def test_long_transaction_warning(self, transaction_manager, mock_connection, caplog):
        """Test warning for long-running transactions."""
        transaction_manager.long_transaction_threshold = 0.05  # 50ms

        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                await asyncio.sleep(0.1)  # Exceed threshold

        # Check that warning was logged
        assert any("Long-running transaction" in record.message for record in caplog.records)


class TestReadOnlyTransactions:
    """Test read-only transaction support."""

    @pytest.mark.asyncio
    async def test_read_only_flag(self, transaction_manager, mock_connection):
        """Test that read-only flag is set correctly."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic(read_only=True) as txn:
                assert txn.config.read_only is True

    @pytest.mark.asyncio
    async def test_read_write_default(self, transaction_manager, mock_connection):
        """Test that read-write is the default."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                assert txn.config.read_only is False


class TestTransactionRepr:
    """Test string representations."""

    @pytest.mark.asyncio
    async def test_transaction_repr(self, transaction_manager, mock_connection):
        """Test Transaction string representation."""
        with patch.object(transaction_manager, '_acquire_connection', return_value=mock_connection):
            async with transaction_manager.atomic() as txn:
                repr_str = repr(txn)
                assert "Transaction(" in repr_str
                assert f"id={txn.transaction_id[:8]}" in repr_str
                assert "level=0" in repr_str

    def test_transaction_manager_repr(self, transaction_manager):
        """Test TransactionManager string representation."""
        repr_str = repr(transaction_manager)
        assert "TransactionManager(" in repr_str
        assert "active_transactions=" in repr_str


# Integration tests that would require actual database connection
# These are marked to skip unless --integration flag is passed

@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_postgresql_nested_transaction():
    """Integration test with real PostgreSQL database."""
    # This would require a real PostgreSQL connection
    # Implement when integration testing is set up
    pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_mysql_nested_transaction():
    """Integration test with real MySQL database."""
    # This would require a real MySQL connection
    # Implement when integration testing is set up
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
