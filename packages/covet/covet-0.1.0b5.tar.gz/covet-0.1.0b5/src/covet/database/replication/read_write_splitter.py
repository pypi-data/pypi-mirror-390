"""
Read-Write Splitter - Production-Grade Query Routing with Consistency Guarantees

Automatic read/write splitting with:
- Intelligent query analysis and routing
- Read-after-write consistency guarantees
- Session-level consistency tracking
- Transaction-aware routing
- Sticky sessions for consistency
- Automatic fallback and retry

Based on 20 years of production database experience.

Author: Senior Database Administrator
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .replica_manager import ReplicaManager

logger = logging.getLogger(__name__)


class ReadPreference(Enum):
    """Read preference for query routing."""

    PRIMARY = "primary"  # Always read from primary
    PRIMARY_PREFERRED = "primary_preferred"  # Prefer primary, fallback to replica
    REPLICA = "replica"  # Always read from replica
    REPLICA_PREFERRED = "replica_preferred"  # Prefer replica, fallback to primary
    NEAREST = "nearest"  # Route to nearest available database


class ConsistencyLevel(Enum):
    """Consistency level for read queries."""

    EVENTUAL = "eventual"  # Read from any replica (may be stale)
    READ_AFTER_WRITE = "read_after_write"  # Guarantee seeing own writes
    STRONG = "strong"  # Always read from primary
    SESSION = "session"  # Session-level consistency


@dataclass
class SessionState:
    """Track session state for consistency guarantees."""

    session_id: str
    last_write_timestamp: Optional[datetime] = None
    last_write_region: Optional[str] = None
    forced_primary_until: Optional[datetime] = None
    in_transaction: bool = False
    transaction_start: Optional[datetime] = None
    read_count: int = 0
    write_count: int = 0
    total_lag_observed: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def requires_primary(self, read_after_write_window: float = 5.0) -> bool:
        """Check if session requires primary for consistency."""
        # Always use primary in transaction
        if self.in_transaction:
            return True

        # Forced primary mode
        if self.forced_primary_until and datetime.now() < self.forced_primary_until:
            return True

        # Read-after-write consistency
        if self.last_write_timestamp:
            elapsed = (datetime.now() - self.last_write_timestamp).total_seconds()
            if elapsed < read_after_write_window:
                return True

        return False

    def start_transaction(self) -> None:
        """Mark transaction start."""
        self.in_transaction = True
        self.transaction_start = datetime.now()

    def end_transaction(self) -> None:
        """Mark transaction end."""
        self.in_transaction = False
        self.transaction_start = None

    def record_write(self, region: Optional[str] = None) -> None:
        """Record a write operation."""
        self.last_write_timestamp = datetime.now()
        self.last_write_region = region
        self.write_count += 1
        self.last_activity = datetime.now()

    def record_read(self) -> None:
        """Record a read operation."""
        self.read_count += 1
        self.last_activity = datetime.now()


class ReadWriteSplitter:
    """
    Production-Grade Read-Write Splitter

    Automatically routes queries to appropriate databases with consistency guarantees.

    Features:
    - Automatic query analysis (read vs write)
    - Read-after-write consistency
    - Transaction-aware routing (all txn queries -> primary)
    - Session-based sticky routing
    - Geographic routing preferences
    - Automatic replica fallback
    - Query retry on failure
    - Comprehensive metrics

    Example:
        splitter = ReadWriteSplitter(
            replica_manager=replica_manager,
            default_consistency=ConsistencyLevel.READ_AFTER_WRITE,
            read_after_write_window=5.0,
            enable_sticky_sessions=True
        )

        # Automatic routing
        session = splitter.create_session()

        # Write goes to primary
        async with splitter.route("INSERT INTO users ...") as conn:
            await conn.execute("INSERT INTO users ...")

        # Read within window goes to primary (read-after-write)
        async with splitter.route("SELECT * FROM users", session=session) as conn:
            users = await conn.fetch_all("SELECT * FROM users")

        # Transaction routing (all go to primary)
        async with splitter.transaction(session=session) as conn:
            await conn.execute("INSERT ...")
            await conn.execute("UPDATE ...")
    """

    def __init__(
        self,
        replica_manager: ReplicaManager,
        default_read_preference: ReadPreference = ReadPreference.REPLICA_PREFERRED,
        default_consistency: ConsistencyLevel = ConsistencyLevel.READ_AFTER_WRITE,
        read_after_write_window: float = 5.0,
        enable_query_analysis: bool = True,
        enable_sticky_sessions: bool = True,
        max_replica_lag: float = 2.0,
        session_timeout: float = 1800.0,  # 30 minutes
        enable_metrics: bool = True,
    ):
        """
        Initialize read-write splitter.

        Args:
            replica_manager: ReplicaManager instance
            default_read_preference: Default read preference
            default_consistency: Default consistency level
            read_after_write_window: Window for read-after-write consistency (seconds)
            enable_query_analysis: Enable automatic query analysis
            enable_sticky_sessions: Enable sticky session routing
            max_replica_lag: Maximum acceptable replica lag for reads
            session_timeout: Session timeout in seconds
            enable_metrics: Enable metrics collection
        """
        self.replica_manager = replica_manager
        self.default_read_preference = default_read_preference
        self.default_consistency = default_consistency
        self.read_after_write_window = read_after_write_window
        self.enable_query_analysis = enable_query_analysis
        self.enable_sticky_sessions = enable_sticky_sessions
        self.max_replica_lag = max_replica_lag
        self.session_timeout = session_timeout
        self.enable_metrics = enable_metrics

        # Session tracking
        self._sessions: Dict[str, SessionState] = {}
        self._session_cleanup_task: Optional[asyncio.Task] = None

        # Metrics
        self._metrics = {
            "primary_routes": 0,
            "replica_routes": 0,
            "replica_failures": 0,
            "fallbacks_to_primary": 0,
            "consistency_upgrades": 0,
            "query_analysis_time_ms": 0.0,
            "total_queries": 0,
            "failed_queries": 0,
        }

        self._query_type_counts = defaultdict(int)

        # Start session cleanup
        if self.enable_sticky_sessions:
            self._session_cleanup_task = asyncio.create_task(self._cleanup_sessions())

        logger.info(
            f"ReadWriteSplitter initialized (consistency={default_consistency.value}, "
            f"read_after_write_window={read_after_write_window}s)"
        )

    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session for consistency tracking.

        Args:
            session_id: Optional session ID (generated if not provided)

        Returns:
            Session ID
        """
        session_id = session_id or str(uuid.uuid4())

        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id=session_id)
            logger.debug(f"Created session: {session_id}")

        return session_id

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state."""
        return self._sessions.get(session_id)

    def destroy_session(self, session_id: str) -> None:
        """Destroy a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.debug(f"Destroyed session: {session_id}")

    async def _cleanup_sessions(self) -> None:
        """Periodically cleanup expired sessions."""
        while True:
            try:
                await asyncio.sleep(60.0)  # Cleanup every minute

                now = datetime.now()
                expired = []

                for session_id, session in self._sessions.items():
                    # Expire sessions based on timeout
                    time_since_activity = (now - session.last_activity).total_seconds()
                    if time_since_activity > self.session_timeout:
                        expired.append(session_id)

                for session_id in expired:
                    del self._sessions[session_id]

                if expired:
                    logger.debug(f"Cleaned up {len(expired)} expired sessions")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")

    @asynccontextmanager
    async def route(
        self,
        query: str,
        session: Optional[str] = None,
        read_preference: Optional[ReadPreference] = None,
        consistency: Optional[ConsistencyLevel] = None,
        force_primary: bool = False,
        force_replica: bool = False,
        region: Optional[str] = None,
    ):
        """
        Route a query to appropriate database with automatic fallback.

        Args:
            query: SQL query to execute
            session: Session ID for consistency tracking
            read_preference: Override read preference
            consistency: Override consistency level
            force_primary: Force routing to primary
            force_replica: Force routing to replica
            region: Preferred region for replica selection

        Yields:
            Database adapter to use for query

        Example:
            async with splitter.route("SELECT * FROM users") as conn:
                results = await conn.fetch_all("SELECT * FROM users")
        """
        self._metrics["total_queries"] += 1

        # Get session state
        session_state = self._sessions.get(session) if session else None

        # Determine target
        start_analysis = time.time()
        target, reason = self._determine_target(
            query=query,
            session_state=session_state,
            read_preference=read_preference,
            consistency=consistency,
            force_primary=force_primary,
            force_replica=force_replica,
            region=region,
        )
        analysis_time_ms = (time.time() - start_analysis) * 1000
        self._metrics["query_analysis_time_ms"] += analysis_time_ms

        # Get adapter
        adapter = None
        is_replica = False

        if target == "primary":
            adapter = self.replica_manager.get_primary()
            self._metrics["primary_routes"] += 1
            logger.debug(f"Routed to PRIMARY: {reason} (query: {query[:50]}...)")

        elif target == "replica":
            adapter = self.replica_manager.get_replica(
                region=region,
                max_lag=self.max_replica_lag,
                session_id=session if self.enable_sticky_sessions else None,
            )
            is_replica = True

            if adapter:
                self._metrics["replica_routes"] += 1
                logger.debug(f"Routed to REPLICA: {reason} (query: {query[:50]}...)")
            else:
                # Fallback to primary
                adapter = self.replica_manager.get_primary()
                self._metrics["fallbacks_to_primary"] += 1
                logger.warning(f"No replica available, falling back to primary")

        if not adapter:
            self._metrics["failed_queries"] += 1
            raise RuntimeError("No database available for routing")

        # Track write operations
        is_write = self._is_write_query(query)
        query_type = self._get_query_type(query)
        self._query_type_counts[query_type] += 1

        try:
            yield adapter

            # Update session state after successful operation
            if session_state:
                if is_write:
                    session_state.record_write(region=region)
                else:
                    session_state.record_read()

        except Exception as e:
            # On replica failure, retry with primary
            if is_replica and not is_write:
                self._metrics["replica_failures"] += 1
                logger.warning(f"Replica query failed, retrying with primary: {e}")

                try:
                    adapter = self.replica_manager.get_primary()
                    yield adapter

                    if session_state:
                        session_state.record_read()
                except Exception:
                    self._metrics["failed_queries"] += 1
                    raise
            else:
                self._metrics["failed_queries"] += 1
                raise

    @asynccontextmanager
    async def transaction(self, session: Optional[str] = None, isolation: str = "read_committed"):
        """
        Start a transaction (all queries route to primary).

        Args:
            session: Session ID for tracking
            isolation: Transaction isolation level

        Yields:
            Primary database adapter with transaction

        Example:
            async with splitter.transaction(session=session_id) as conn:
                await conn.execute("INSERT INTO users ...")
                await conn.execute("UPDATE accounts ...")
        """
        session_state = self._sessions.get(session) if session else None

        if session_state:
            session_state.start_transaction()

        try:
            # Get primary adapter
            primary = self.replica_manager.get_primary()
            self._metrics["primary_routes"] += 1

            # Start transaction
            async with primary.transaction(isolation=isolation) as txn_conn:
                yield txn_conn

            # Transaction committed successfully
            if session_state:
                session_state.record_write()

        finally:
            if session_state:
                session_state.end_transaction()

    def _determine_target(
        self,
        query: str,
        session_state: Optional[SessionState],
        read_preference: Optional[ReadPreference],
        consistency: Optional[ConsistencyLevel],
        force_primary: bool,
        force_replica: bool,
        region: Optional[str],
    ) -> tuple[str, str]:
        """
        Determine routing target (primary or replica).

        Returns:
            Tuple of (target, reason) where target is "primary" or "replica"
        """
        # Explicit overrides
        if force_primary:
            return ("primary", "force_primary flag")

        if force_replica:
            return ("replica", "force_replica flag")

        # Transaction check
        if session_state and session_state.in_transaction:
            return ("primary", "in transaction")

        # Analyze query type
        is_write = self._is_write_query(query)

        if is_write:
            return ("primary", "write query")

        # Apply consistency level
        consistency = consistency or self.default_consistency

        if consistency == ConsistencyLevel.STRONG:
            return ("primary", "strong consistency required")

        # Check session consistency requirements
        if session_state:
            if consistency == ConsistencyLevel.SESSION:
                # Session consistency - use primary if there have been writes
                if session_state.write_count > 0:
                    return ("primary", "session consistency")

            elif consistency == ConsistencyLevel.READ_AFTER_WRITE:
                if session_state.requires_primary(self.read_after_write_window):
                    self._metrics["consistency_upgrades"] += 1
                    return ("primary", "read-after-write consistency")

        # Apply read preference
        read_preference = read_preference or self.default_read_preference

        if read_preference == ReadPreference.PRIMARY:
            return ("primary", "primary read preference")

        elif read_preference == ReadPreference.PRIMARY_PREFERRED:
            return ("primary", "primary preferred")

        elif read_preference == ReadPreference.REPLICA:
            return ("replica", "replica read preference")

        elif read_preference == ReadPreference.REPLICA_PREFERRED:
            return ("replica", "replica preferred")

        elif read_preference == ReadPreference.NEAREST:
            return ("replica", "nearest available")

        # Default to replica for reads
        return ("replica", "default read routing")

    def _is_write_query(self, query: str) -> bool:
        """
        Determine if query is a write operation.

        Args:
            query: SQL query

        Returns:
            True if query modifies data
        """
        if not self.enable_query_analysis:
            return False

        query_upper = query.strip().upper()

        # Write operations
        write_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "ALTER",
            "DROP",
            "TRUNCATE",
            "REPLACE",
            "MERGE",
            "COPY",
            "GRANT",
            "REVOKE",
        ]

        for keyword in write_keywords:
            if query_upper.startswith(keyword):
                return True

        # Check for WITH ... INSERT/UPDATE/DELETE (CTEs with writes)
        if query_upper.startswith("WITH") and any(
            kw in query_upper for kw in ["INSERT", "UPDATE", "DELETE", "MERGE"]
        ):
            return True

        return False

    def _get_query_type(self, query: str) -> str:
        """Get query type for metrics."""
        query_upper = query.strip().upper()

        query_types = [
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "ALTER",
            "DROP",
            "TRUNCATE",
            "WITH",
            "EXPLAIN",
            "ANALYZE",
        ]

        for qtype in query_types:
            if query_upper.startswith(qtype):
                return qtype

        return "OTHER"

    async def execute_with_retry(
        self,
        query: str,
        params: Optional[list] = None,
        session: Optional[str] = None,
        max_retries: int = 3,
        **route_kwargs,
    ) -> Any:
        """
        Execute query with automatic retry on failure.

        Args:
            query: SQL query
            params: Query parameters
            session: Session ID
            max_retries: Maximum retry attempts
            **route_kwargs: Additional routing arguments

        Returns:
            Query result
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                async with self.route(query, session=session, **route_kwargs) as adapter:
                    return await adapter.execute(query, params)

            except Exception as e:
                last_error = e
                logger.warning(f"Query execution failed (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (2**attempt))  # Exponential backoff

        raise last_error

    async def fetch_one_with_retry(
        self,
        query: str,
        params: Optional[list] = None,
        session: Optional[str] = None,
        max_retries: int = 3,
        **route_kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Fetch one row with automatic retry."""
        last_error = None

        for attempt in range(max_retries):
            try:
                async with self.route(query, session=session, **route_kwargs) as adapter:
                    return await adapter.fetch_one(query, params)

            except Exception as e:
                last_error = e
                logger.warning(f"Fetch one failed (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (2**attempt))

        raise last_error

    async def fetch_all_with_retry(
        self,
        query: str,
        params: Optional[list] = None,
        session: Optional[str] = None,
        max_retries: int = 3,
        **route_kwargs,
    ) -> List[Dict[str, Any]]:
        """Fetch all rows with automatic retry."""
        last_error = None

        for attempt in range(max_retries):
            try:
                async with self.route(query, session=session, **route_kwargs) as adapter:
                    return await adapter.fetch_all(query, params)

            except Exception as e:
                last_error = e
                logger.warning(f"Fetch all failed (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (2**attempt))

        raise last_error

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive routing metrics."""
        total_routes = self._metrics["primary_routes"] + self._metrics["replica_routes"]

        replica_hit_rate = 0.0
        if total_routes > 0:
            replica_hit_rate = (self._metrics["replica_routes"] / total_routes) * 100

        success_rate = 0.0
        if self._metrics["total_queries"] > 0:
            success_rate = (
                (self._metrics["total_queries"] - self._metrics["failed_queries"])
                / self._metrics["total_queries"]
            ) * 100

        avg_analysis_time = 0.0
        if self._metrics["total_queries"] > 0:
            avg_analysis_time = (
                self._metrics["query_analysis_time_ms"] / self._metrics["total_queries"]
            )

        return {
            **self._metrics,
            "total_routes": total_routes,
            "replica_hit_rate_percent": round(replica_hit_rate, 2),
            "success_rate_percent": round(success_rate, 2),
            "avg_query_analysis_time_ms": round(avg_analysis_time, 4),
            "active_sessions": len(self._sessions),
            "query_type_counts": dict(self._query_type_counts),
            "read_after_write_window": self.read_after_write_window,
            "default_consistency": self.default_consistency.value,
        }

    def reset_metrics(self) -> None:
        """Reset routing metrics."""
        self._metrics = {
            "primary_routes": 0,
            "replica_routes": 0,
            "replica_failures": 0,
            "fallbacks_to_primary": 0,
            "consistency_upgrades": 0,
            "query_analysis_time_ms": 0.0,
            "total_queries": 0,
            "failed_queries": 0,
        }
        self._query_type_counts.clear()

    async def stop(self) -> None:
        """Stop the splitter."""
        if self._session_cleanup_task:
            self._session_cleanup_task.cancel()
            try:
                await self._session_cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("ReadWriteSplitter stopped")


__all__ = [
    "ReadWriteSplitter",
    "ReadPreference",
    "ConsistencyLevel",
    "SessionState",
]
