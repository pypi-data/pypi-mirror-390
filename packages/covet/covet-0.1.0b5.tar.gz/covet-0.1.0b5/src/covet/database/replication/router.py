"""
Replication Router - Read/Write Splitting with Consistency Guarantees

Enterprise router for automatic query routing with:
- Intelligent read/write detection
- Read-after-write consistency
- Session-level consistency tracking
- Replica failover and fallback
- Geographic routing preferences

Production Features:
- Automatic stale read prevention
- Configurable consistency levels
- Query hint support (.using() method)
- Fallback to primary on replica failure
- Connection reuse and pooling
"""

import asyncio
import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .manager import ReplicaManager

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


@dataclass
class SessionState:
    """Track session state for consistency guarantees."""

    session_id: str
    last_write_timestamp: Optional[datetime] = None
    last_write_region: Optional[str] = None
    forced_primary_until: Optional[datetime] = None
    read_count: int = 0
    write_count: int = 0
    total_lag_observed: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    def requires_primary(self, read_after_write_window: float = 5.0) -> bool:
        """Check if session requires primary for consistency."""
        if self.forced_primary_until and datetime.now() < self.forced_primary_until:
            return True

        if self.last_write_timestamp:
            elapsed = (datetime.now() - self.last_write_timestamp).total_seconds()
            if elapsed < read_after_write_window:
                return True

        return False

    def record_write(self, region: Optional[str] = None) -> None:
        """Record a write operation."""
        self.last_write_timestamp = datetime.now()
        self.last_write_region = region
        self.write_count += 1

    def record_read(self) -> None:
        """Record a read operation."""
        self.read_count += 1


class ReplicationRouter:
    """
    Enterprise Replication Router

    Handles automatic read/write splitting with consistency guarantees.

    Example:
        router = ReplicationRouter(replica_manager)

        # Automatic routing
        async with router.route_query("SELECT * FROM users") as adapter:
            results = await adapter.fetch_all("SELECT * FROM users")

        # Explicit primary routing
        async with router.route_query("SELECT ...", force_primary=True) as adapter:
            results = await adapter.fetch_all("SELECT ...")

        # Session-level consistency
        session = router.create_session()
        async with router.route_query("INSERT ...", session=session) as adapter:
            await adapter.execute("INSERT ...")

        # Subsequent reads see the write
        async with router.route_query("SELECT ...", session=session) as adapter:
            results = await adapter.fetch_all("SELECT ...")
    """

    def __init__(
        self,
        replica_manager: ReplicaManager,
        default_read_preference: ReadPreference = ReadPreference.REPLICA_PREFERRED,
        default_consistency: ConsistencyLevel = ConsistencyLevel.READ_AFTER_WRITE,
        read_after_write_window: float = 5.0,
        enable_query_analysis: bool = True,
        max_replica_lag: float = 2.0,
    ):
        """
        Initialize replication router.

        Args:
            replica_manager: ReplicaManager instance
            default_read_preference: Default read preference
            default_consistency: Default consistency level
            read_after_write_window: Window for read-after-write consistency (seconds)
            enable_query_analysis: Enable automatic query analysis
            max_replica_lag: Maximum acceptable replica lag for reads
        """
        self.replica_manager = replica_manager
        self.default_read_preference = default_read_preference
        self.default_consistency = default_consistency
        self.read_after_write_window = read_after_write_window
        self.enable_query_analysis = enable_query_analysis
        self.max_replica_lag = max_replica_lag

        # Session tracking
        self._sessions: Dict[str, SessionState] = {}
        self._session_cleanup_task: Optional[asyncio.Task] = None

        # Metrics
        self._route_metrics = {
            "primary_routes": 0,
            "replica_routes": 0,
            "replica_failures": 0,
            "fallbacks_to_primary": 0,
            "consistency_upgrades": 0,
        }

        # Start session cleanup
        self._session_cleanup_task = asyncio.create_task(self._cleanup_sessions())

        logger.info("ReplicationRouter initialized")

    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session for consistency tracking.

        Args:
            session_id: Optional session ID (generated if not provided)

        Returns:
            Session ID
        """
        import uuid

        session_id = session_id or str(uuid.uuid4())

        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id=session_id)

        return session_id

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state."""
        return self._sessions.get(session_id)

    def destroy_session(self, session_id: str) -> None:
        """Destroy a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    async def _cleanup_sessions(self) -> None:
        """Periodically cleanup old sessions."""
        while True:
            try:
                await asyncio.sleep(60.0)  # Cleanup every minute

                now = datetime.now()
                expired = []

                for session_id, session in self._sessions.items():
                    # Expire sessions after 1 hour of inactivity
                    if (now - session.created_at).total_seconds() > 3600:
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
    async def route_query(
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
        Route a query to appropriate database.

        Context manager that yields database adapter.

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
            async with router.route_query("SELECT * FROM users") as adapter:
                results = await adapter.fetch_all("SELECT * FROM users")
        """
        # Get session state
        session_state = self._sessions.get(session) if session else None

        # Determine target
        target, reason = self._determine_target(
            query=query,
            session_state=session_state,
            read_preference=read_preference,
            consistency=consistency,
            force_primary=force_primary,
            force_replica=force_replica,
            region=region,
        )

        # Get adapter
        adapter = None
        is_replica = False

        if target == "primary":
            adapter = self.replica_manager.get_primary()
            self._route_metrics["primary_routes"] += 1
            logger.debug(f"Routed to PRIMARY: {reason}")

        elif target == "replica":
            adapter = self.replica_manager.get_replica(region=region, max_lag=self.max_replica_lag)
            is_replica = True

            if adapter:
                self._route_metrics["replica_routes"] += 1
                logger.debug(f"Routed to REPLICA: {reason}")
            else:
                # Fallback to primary
                adapter = self.replica_manager.get_primary()
                self._route_metrics["fallbacks_to_primary"] += 1
                logger.warning("No replica available, falling back to primary")

        if not adapter:
            raise RuntimeError("No database available for routing")

        # Track write operations
        is_write = self._is_write_query(query)

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
                self._route_metrics["replica_failures"] += 1
                logger.warning(f"Replica query failed, retrying with primary: {e}")

                adapter = self.replica_manager.get_primary()
                yield adapter

                if session_state:
                    session_state.record_read()
            else:
                raise

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

        # Analyze query type
        is_write = self._is_write_query(query)

        if is_write:
            return ("primary", "write query")

        # Apply consistency level
        consistency = consistency or self.default_consistency

        if consistency == ConsistencyLevel.STRONG:
            return ("primary", "strong consistency required")

        # Check session consistency requirements
        if session_state and consistency == ConsistencyLevel.READ_AFTER_WRITE:
            if session_state.requires_primary(self.read_after_write_window):
                self._route_metrics["consistency_upgrades"] += 1
                return ("primary", "read-after-write consistency")

        # Apply read preference
        read_preference = read_preference or self.default_read_preference

        if read_preference == ReadPreference.PRIMARY:
            return ("primary", "primary read preference")

        elif read_preference == ReadPreference.PRIMARY_PREFERRED:
            # Check if primary is healthy, otherwise use replica
            return ("primary", "primary preferred")

        elif read_preference == ReadPreference.REPLICA:
            return ("replica", "replica read preference")

        elif read_preference == ReadPreference.REPLICA_PREFERRED:
            return ("replica", "replica preferred")

        elif read_preference == ReadPreference.NEAREST:
            # For now, prefer replica (could be enhanced with latency detection)
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
        ]

        for keyword in write_keywords:
            if query_upper.startswith(keyword):
                return True

        # Check for WITH ... INSERT/UPDATE/DELETE
        if query_upper.startswith("WITH") and any(
            kw in query_upper for kw in ["INSERT", "UPDATE", "DELETE"]
        ):
            return True

        return False

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
                async with self.route_query(query, session=session, **route_kwargs) as adapter:
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
                async with self.route_query(query, session=session, **route_kwargs) as adapter:
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
                async with self.route_query(query, session=session, **route_kwargs) as adapter:
                    return await adapter.fetch_all(query, params)

            except Exception as e:
                last_error = e
                logger.warning(f"Fetch all failed (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (2**attempt))

        raise last_error

    def get_metrics(self) -> Dict[str, Any]:
        """Get routing metrics."""
        total_routes = self._route_metrics["primary_routes"] + self._route_metrics["replica_routes"]

        replica_hit_rate = 0.0
        if total_routes > 0:
            replica_hit_rate = (self._route_metrics["replica_routes"] / total_routes) * 100

        return {
            **self._route_metrics,
            "total_routes": total_routes,
            "replica_hit_rate_percent": round(replica_hit_rate, 2),
            "active_sessions": len(self._sessions),
        }

    def reset_metrics(self) -> None:
        """Reset routing metrics."""
        self._route_metrics = {
            "primary_routes": 0,
            "replica_routes": 0,
            "replica_failures": 0,
            "fallbacks_to_primary": 0,
            "consistency_upgrades": 0,
        }

    async def stop(self) -> None:
        """Stop the router."""
        if self._session_cleanup_task:
            self._session_cleanup_task.cancel()
            try:
                await self._session_cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("ReplicationRouter stopped")


class RoutingContext:
    """
    Context manager for routing with explicit configuration.

    Example:
        with RoutingContext(force_primary=True):
            # All queries in this context use primary
            user = await User.objects.get(id=1)
    """

    _contexts: List[Dict[str, Any]] = []

    def __init__(
        self,
        read_preference: Optional[ReadPreference] = None,
        consistency: Optional[ConsistencyLevel] = None,
        force_primary: bool = False,
        force_replica: bool = False,
        region: Optional[str] = None,
    ):
        self.config = {
            "read_preference": read_preference,
            "consistency": consistency,
            "force_primary": force_primary,
            "force_replica": force_replica,
            "region": region,
        }

    def __enter__(self):
        RoutingContext._contexts.append(self.config)
        return self

    def __exit__(self, exc_type, exc_val, _):
        RoutingContext._contexts.pop()

    @classmethod
    def get_current_context(cls) -> Optional[Dict[str, Any]]:
        """Get current routing context."""
        return cls._contexts[-1] if cls._contexts else None


__all__ = [
    "ReplicationRouter",
    "ReadPreference",
    "ConsistencyLevel",
    "SessionState",
    "RoutingContext",
]
