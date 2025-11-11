"""
Sharding Strategy Implementations

Production-grade sharding strategies for horizontal database scaling.
Supports multiple algorithms optimized for different use cases:
- Hash-based: Even distribution, good for general purpose
- Range-based: Chronological data, time-series
- Consistent hashing: Dynamic shard scaling with minimal rebalancing
- Geographic: Data locality, compliance requirements

Each strategy provides:
- Shard selection for writes
- Shard routing for reads
- Multi-shard query planning
- Rebalancing support
"""

import bisect
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ShardingStrategy(str, Enum):
    """Supported sharding strategies."""

    HASH = "hash"
    RANGE = "range"
    CONSISTENT_HASH = "consistent_hash"
    GEOGRAPHIC = "geographic"
    CUSTOM = "custom"


@dataclass
class ShardInfo:
    """
    Shard configuration and metadata.

    Represents a single database shard with connection details,
    capacity information, and operational status.
    """

    shard_id: str
    host: str
    port: int
    database: str
    weight: float = 1.0  # For weighted distribution
    is_active: bool = True
    is_read_only: bool = False  # For maintenance/rebalancing
    capacity_used: float = 0.0  # Percentage 0-100
    priority: int = 0  # Lower = higher priority
    region: Optional[str] = None  # Geographic region
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.shard_id)

    def __eq__(self, other):
        if not isinstance(other, ShardInfo):
            return False
        return self.shard_id == other.shard_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "shard_id": self.shard_id,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "weight": self.weight,
            "is_active": self.is_active,
            "is_read_only": self.is_read_only,
            "capacity_used": self.capacity_used,
            "priority": self.priority,
            "region": self.region,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class ShardRoutingResult:
    """
    Result of shard routing operation.

    Contains the selected shard(s) and routing metadata
    for query execution.
    """

    primary_shard: ShardInfo
    replica_shards: List[ShardInfo] = field(default_factory=list)
    is_multi_shard: bool = False
    routing_key: Optional[str] = None
    routing_metadata: Dict[str, Any] = field(default_factory=dict)


class ShardStrategy(ABC):
    """
    Base class for all sharding strategies.

    Provides interface for:
    - Shard selection based on routing key
    - Query distribution across shards
    - Shard rebalancing support
    """

    def __init__(self, shard_key: str, shards: List[ShardInfo]):
        """
        Initialize shard strategy.

        Args:
            shard_key: Field name to use for sharding (e.g., 'user_id')
            shards: List of available shards
        """
        self.shard_key = shard_key
        self.shards = shards
        self.active_shards = [s for s in shards if s.is_active]

        if not self.active_shards:
            raise ValueError("No active shards available")

        logger.info(
            f"{self.__class__.__name__} initialized with {len(self.active_shards)} "
            f"active shards (key: {shard_key})"
        )

    @abstractmethod
    def get_shard(self, routing_key: Any) -> ShardRoutingResult:
        """
        Get shard for a given routing key.

        Args:
            routing_key: Value to route on (e.g., user_id value)

        Returns:
            ShardRoutingResult with selected shard(s)
        """
        pass

    @abstractmethod
    def get_shards_for_range(self, start_key: Any, end_key: Any) -> List[ShardInfo]:
        """
        Get shards that contain data in the specified range.

        Args:
            start_key: Range start (inclusive)
            end_key: Range end (inclusive)

        Returns:
            List of shards containing data in range
        """
        pass

    def get_all_shards(self) -> List[ShardInfo]:
        """Get all active shards."""
        return self.active_shards.copy()

    def get_write_shard(self, routing_key: Any) -> ShardInfo:
        """
        Get shard for write operations.

        Args:
            routing_key: Routing key value

        Returns:
            Shard for writes (excludes read-only shards)
        """
        result = self.get_shard(routing_key)

        if result.primary_shard.is_read_only:
            raise ValueError(
                f"Shard {result.primary_shard.shard_id} is read-only. "
                f"Cannot perform write operations."
            )

        return result.primary_shard

    def get_read_shard(self, routing_key: Any, prefer_replica: bool = False) -> ShardInfo:
        """
        Get shard for read operations.

        Args:
            routing_key: Routing key value
            prefer_replica: If True, prefer replica over primary

        Returns:
            Shard for reads (can include replicas)
        """
        result = self.get_shard(routing_key)

        if prefer_replica and result.replica_shards:
            # Select least loaded replica
            return min(result.replica_shards, key=lambda s: s.capacity_used)

        return result.primary_shard

    def add_shard(self, shard: ShardInfo) -> None:
        """Add new shard to strategy."""
        if shard not in self.shards:
            self.shards.append(shard)
            if shard.is_active:
                self.active_shards.append(shard)
            logger.info(f"Added shard {shard.shard_id} to strategy")

    def remove_shard(self, shard_id: str) -> None:
        """Remove shard from strategy."""
        self.shards = [s for s in self.shards if s.shard_id != shard_id]
        self.active_shards = [s for s in self.active_shards if s.shard_id != shard_id]
        logger.info(f"Removed shard {shard_id} from strategy")

    def get_shard_by_id(self, shard_id: str) -> Optional[ShardInfo]:
        """Get shard by ID."""
        for shard in self.shards:
            if shard.shard_id == shard_id:
                return shard
        return None


class HashStrategy(ShardStrategy):
    """
    Hash-based sharding strategy.

    Uses consistent hashing to distribute data across shards.
    Provides even distribution and good performance for general-purpose use.

    Algorithm:
    1. Hash the routing key using MD5/SHA256
    2. Apply modulo operation with shard count
    3. Select corresponding shard from sorted list

    Pros:
    - Even distribution
    - Simple and fast
    - Predictable performance

    Cons:
    - Adding/removing shards requires rebalancing
    - No range queries across routing key
    """

    def __init__(
        self,
        shard_key: str,
        shards: List[ShardInfo],
        hash_function: str = "md5",
        virtual_nodes: int = 1,
    ):
        """
        Initialize hash-based sharding.

        Args:
            shard_key: Field to shard on
            shards: Available shards
            hash_function: Hash algorithm ('md5', 'sha256', 'murmur3')
            virtual_nodes: Virtual nodes per shard (for better distribution)
        """
        super().__init__(shard_key, shards)
        self.hash_function = hash_function
        self.virtual_nodes = virtual_nodes

        # Sort shards by ID for consistent mapping
        self.active_shards = sorted(self.active_shards, key=lambda s: s.shard_id)

    def _hash_key(self, key: Any) -> int:
        """Hash a routing key to integer."""
        # Convert key to string
        key_str = str(key)

        # Hash based on configured function
        if self.hash_function == "md5":
            return int(hashlib.md5(key_str.encode(), usedforsecurity=False).hexdigest(), 16)
        elif self.hash_function == "sha256":
            return int(hashlib.sha256(key_str.encode()).hexdigest(), 16)
        else:
            # Fallback to simple hash
            return hash(key_str)

    def get_shard(self, routing_key: Any) -> ShardRoutingResult:
        """
        Get shard for routing key using hash.

        Args:
            routing_key: Key to route (e.g., user ID)

        Returns:
            ShardRoutingResult with selected shard
        """
        if not self.active_shards:
            raise ValueError("No active shards available")

        # Hash the key and map to shard
        hash_value = self._hash_key(routing_key)
        shard_index = hash_value % len(self.active_shards)
        shard = self.active_shards[shard_index]

        logger.debug(
            f"HashStrategy: key={routing_key} -> hash={hash_value} " f"-> shard={shard.shard_id}"
        )

        return ShardRoutingResult(
            primary_shard=shard,
            routing_key=str(routing_key),
            routing_metadata={
                "hash_value": hash_value,
                "shard_index": shard_index,
                "strategy": "hash",
            },
        )

    def get_shards_for_range(self, start_key: Any, end_key: Any) -> List[ShardInfo]:
        """
        For hash strategy, range queries require all shards.

        Hash distribution means consecutive keys are on different shards,
        so we must query all shards for range queries.
        """
        logger.warning(
            "HashStrategy.get_shards_for_range: Hash strategy requires "
            "querying all shards for range queries"
        )
        return self.active_shards


class RangeStrategy(ShardStrategy):
    """
    Range-based sharding strategy.

    Distributes data based on key ranges. Excellent for time-series data
    and scenarios where range queries are common.

    Example ranges:
    - Shard 1: user_id 1-1000000
    - Shard 2: user_id 1000001-2000000
    - Shard 3: user_id 2000001+

    Pros:
    - Efficient range queries
    - Good for time-series data
    - Easy to add new shards (append new range)

    Cons:
    - Can lead to hot spots if data distribution is uneven
    - Requires careful range planning
    """

    def __init__(
        self,
        shard_key: str,
        shards: List[ShardInfo],
        ranges: Optional[Dict[str, Tuple[Any, Any]]] = None,
    ):
        """
        Initialize range-based sharding.

        Args:
            shard_key: Field to shard on
            shards: Available shards
            ranges: Dict mapping shard_id -> (min, max) range
                   If None, ranges are auto-generated
        """
        super().__init__(shard_key, shards)

        if ranges:
            self.ranges = ranges
        else:
            # Auto-generate equal ranges
            self.ranges = self._auto_generate_ranges()

        # Build sorted list of (range_end, shard) for binary search
        self._range_list = []
        for shard in self.active_shards:
            if shard.shard_id in self.ranges:
                _, range_end = self.ranges[shard.shard_id]
                self._range_list.append((range_end, shard))

        self._range_list.sort(key=lambda x: x[0])

        logger.info(f"RangeStrategy initialized with ranges: {self.ranges}")

    def _auto_generate_ranges(self) -> Dict[str, Tuple[Any, Any]]:
        """Auto-generate equal-sized ranges for shards."""
        # For auto-generation, we assume integer keys
        # Each shard gets 1 billion IDs
        ranges = {}
        range_size = 1_000_000_000

        for i, shard in enumerate(sorted(self.active_shards, key=lambda s: s.shard_id)):
            start = i * range_size
            end = (i + 1) * range_size - 1
            ranges[shard.shard_id] = (start, end)

        return ranges

    def get_shard(self, routing_key: Any) -> ShardRoutingResult:
        """
        Get shard for routing key using range lookup.

        Args:
            routing_key: Key to route

        Returns:
            ShardRoutingResult with selected shard
        """
        if not self._range_list:
            raise ValueError("No range configuration available")

        # Binary search for appropriate range
        # Find first range where routing_key <= range_end
        key_value = self._normalize_key(routing_key)

        for range_end, shard in self._range_list:
            if key_value <= self._normalize_key(range_end):
                logger.debug(f"RangeStrategy: key={routing_key} -> shard={shard.shard_id}")
                return ShardRoutingResult(
                    primary_shard=shard,
                    routing_key=str(routing_key),
                    routing_metadata={
                        "range": self.ranges[shard.shard_id],
                        "strategy": "range",
                    },
                )

        # If no range matched, use last shard
        last_shard = self._range_list[-1][1]
        return ShardRoutingResult(
            primary_shard=last_shard,
            routing_key=str(routing_key),
        )

    def get_shards_for_range(self, start_key: Any, end_key: Any) -> List[ShardInfo]:
        """
        Get shards that contain data in the specified range.

        This is efficient for range strategy as we can determine
        exactly which shards contain the range.
        """
        start_value = self._normalize_key(start_key)
        end_value = self._normalize_key(end_key)

        matching_shards = []

        for shard in self.active_shards:
            if shard.shard_id not in self.ranges:
                continue

            range_start, range_end = self.ranges[shard.shard_id]
            range_start = self._normalize_key(range_start)
            range_end = self._normalize_key(range_end)

            # Check if ranges overlap
            if range_start <= end_value and start_value <= range_end:
                matching_shards.append(shard)

        logger.debug(
            f"RangeStrategy: range [{start_key}, {end_key}] -> " f"{len(matching_shards)} shards"
        )

        return matching_shards

    def _normalize_key(self, key: Any) -> Any:
        """Normalize key for comparison."""
        # Try to convert to int if possible
        try:
            return int(key)
        except (ValueError, TypeError):
            pass

        # Try datetime
        if isinstance(key, datetime):
            return key.timestamp()

        # Return as-is for string comparison
        return key

    def add_range(self, shard_id: str, start: Any, end: Any) -> None:
        """Add or update range for a shard."""
        self.ranges[shard_id] = (start, end)

        # Rebuild range list
        self._range_list = []
        for shard in self.active_shards:
            if shard.shard_id in self.ranges:
                _, range_end = self.ranges[shard.shard_id]
                self._range_list.append((range_end, shard))

        self._range_list.sort(key=lambda x: x[0])


class ConsistentHashStrategy(ShardStrategy):
    """
    Consistent hashing strategy with virtual nodes.

    Advanced hash-based sharding that minimizes data movement when
    shards are added or removed. Uses virtual nodes for better distribution.

    Algorithm:
    1. Create virtual nodes for each shard on hash ring
    2. Hash routing key to position on ring
    3. Select first virtual node clockwise from key position
    4. Map virtual node back to physical shard

    Pros:
    - Minimal rebalancing when adding/removing shards
    - Good distribution with virtual nodes
    - Supports weighted sharding

    Cons:
    - More complex than simple hash
    - Slight overhead from virtual node lookup
    """

    def __init__(
        self,
        shard_key: str,
        shards: List[ShardInfo],
        virtual_nodes_per_shard: int = 150,
        hash_function: str = "md5",
    ):
        """
        Initialize consistent hashing.

        Args:
            shard_key: Field to shard on
            shards: Available shards
            virtual_nodes_per_shard: Number of virtual nodes per shard
                                    (more = better distribution)
            hash_function: Hash algorithm
        """
        super().__init__(shard_key, shards)
        self.virtual_nodes_per_shard = virtual_nodes_per_shard
        self.hash_function = hash_function

        # Hash ring: sorted list of (hash_value, shard)
        self.ring: List[Tuple[int, ShardInfo]] = []
        self._build_ring()

    def _build_ring(self) -> None:
        """Build consistent hash ring with virtual nodes."""
        self.ring = []

        for shard in self.active_shards:
            # Create virtual nodes based on shard weight
            num_virtual_nodes = int(self.virtual_nodes_per_shard * shard.weight)

            for i in range(num_virtual_nodes):
                # Create unique virtual node identifier
                virtual_key = f"{shard.shard_id}:vnode:{i}"
                hash_value = self._hash(virtual_key)
                self.ring.append((hash_value, shard))

        # Sort ring by hash value
        self.ring.sort(key=lambda x: x[0])

        logger.info(
            f"ConsistentHashStrategy: Built ring with {len(self.ring)} "
            f"virtual nodes for {len(self.active_shards)} shards"
        )

    def _hash(self, key: str) -> int:
        """Hash a key to position on ring."""
        if self.hash_function == "md5":
            return int(hashlib.md5(key.encode(), usedforsecurity=False).hexdigest(), 16)
        elif self.hash_function == "sha256":
            return int(hashlib.sha256(key.encode()).hexdigest(), 16)
        else:
            return hash(key)

    def get_shard(self, routing_key: Any) -> ShardRoutingResult:
        """
        Get shard for routing key using consistent hashing.

        Args:
            routing_key: Key to route

        Returns:
            ShardRoutingResult with selected shard
        """
        if not self.ring:
            raise ValueError("Hash ring is empty")

        # Hash the routing key
        key_hash = self._hash(str(routing_key))

        # Binary search for first node >= key_hash
        # If not found, wrap around to first node
        idx = bisect.bisect_left([h for h, _ in self.ring], key_hash)

        if idx >= len(self.ring):
            idx = 0

        _, shard = self.ring[idx]

        logger.debug(
            f"ConsistentHashStrategy: key={routing_key} -> "
            f"hash={key_hash} -> shard={shard.shard_id}"
        )

        return ShardRoutingResult(
            primary_shard=shard,
            routing_key=str(routing_key),
            routing_metadata={
                "hash_value": key_hash,
                "ring_position": idx,
                "strategy": "consistent_hash",
            },
        )

    def get_shards_for_range(self, start_key: Any, end_key: Any) -> List[ShardInfo]:
        """Consistent hash requires all shards for range queries."""
        return self.active_shards

    def add_shard(self, shard: ShardInfo) -> None:
        """Add new shard and rebuild ring."""
        super().add_shard(shard)
        self._build_ring()

    def remove_shard(self, shard_id: str) -> None:
        """Remove shard and rebuild ring."""
        super().remove_shard(shard_id)
        self._build_ring()


class GeographicStrategy(ShardStrategy):
    """
    Geographic/location-based sharding strategy.

    Routes data based on geographic regions for data locality
    and compliance requirements (GDPR, data residency laws).

    Example:
    - Shard 1: US East
    - Shard 2: US West
    - Shard 3: EU
    - Shard 4: APAC

    Pros:
    - Data locality (low latency)
    - Compliance with data residency laws
    - Can isolate regional failures

    Cons:
    - Uneven distribution if user base is geographically concentrated
    - Cross-region queries are expensive
    """

    def __init__(
        self,
        shard_key: str,
        shards: List[ShardInfo],
        region_mapping: Optional[Dict[str, str]] = None,
        default_region: Optional[str] = None,
    ):
        """
        Initialize geographic sharding.

        Args:
            shard_key: Field containing region/location
            shards: Available shards (must have 'region' set)
            region_mapping: Custom mapping of values to regions
            default_region: Default region if key not mapped
        """
        super().__init__(shard_key, shards)

        # Verify all shards have regions
        for shard in self.active_shards:
            if not shard.region:
                raise ValueError(f"Shard {shard.shard_id} missing required 'region' field")

        # Build region -> shard mapping
        self.region_to_shard: Dict[str, ShardInfo] = {}
        for shard in self.active_shards:
            self.region_to_shard[shard.region] = shard

        self.region_mapping = region_mapping or {}
        self.default_region = default_region or list(self.region_to_shard.keys())[0]

        logger.info(
            f"GeographicStrategy: Initialized with regions: " f"{list(self.region_to_shard.keys())}"
        )

    def get_shard(self, routing_key: Any) -> ShardRoutingResult:
        """
        Get shard for routing key based on region.

        Args:
            routing_key: Region identifier or value to map

        Returns:
            ShardRoutingResult with region-specific shard
        """
        # Apply region mapping if configured
        region = self.region_mapping.get(str(routing_key), str(routing_key))

        # Get shard for region
        shard = self.region_to_shard.get(region)

        if not shard:
            # Fall back to default region
            logger.warning(f"Region '{region}' not found, using default: {self.default_region}")
            shard = self.region_to_shard[self.default_region]

        return ShardRoutingResult(
            primary_shard=shard,
            routing_key=str(routing_key),
            routing_metadata={
                "region": region,
                "strategy": "geographic",
            },
        )

    def get_shards_for_range(self, start_key: Any, end_key: Any) -> List[ShardInfo]:
        """For geographic strategy, range queries may span regions."""
        # Could be optimized if we know the region distribution
        # For now, return all shards
        return self.active_shards

    def add_region_mapping(self, value: str, region: str) -> None:
        """Add custom mapping from value to region."""
        self.region_mapping[value] = region


__all__ = [
    "ShardingStrategy",
    "ShardInfo",
    "ShardRoutingResult",
    "ShardStrategy",
    "HashStrategy",
    "RangeStrategy",
    "ConsistentHashStrategy",
    "GeographicStrategy",
]
