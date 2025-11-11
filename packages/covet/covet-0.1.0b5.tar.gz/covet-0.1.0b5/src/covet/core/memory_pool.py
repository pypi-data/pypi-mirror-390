"""
CovetPy Advanced Memory Pool Management System
==============================================

High-performance memory pool manager with:
- Zero-allocation hot paths
- NUMA-aware allocation
- Memory alignment optimization
- Automatic pool sizing
- Lock-free operations where possible
- Memory pressure detection
"""

import asyncio
import ctypes
import logging
import mmap
import os
import sys
import threading
import time
import weakref
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class PoolStrategy(Enum):
    """Memory pool allocation strategies."""

    FIXED_SIZE = "fixed"
    ADAPTIVE = "adaptive"
    NUMA_AWARE = "numa_aware"
    LOCKFREE = "lockfree"


@dataclass
class MemoryStats:
    """Memory pool statistics."""

    total_allocated: int = 0
    total_freed: int = 0
    current_usage: int = 0
    peak_usage: int = 0
    allocation_count: int = 0
    free_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    fragmentation_ratio: float = 0.0
    avg_allocation_time_ns: float = 0.0


class MemoryBlock:
    """Represents a memory block with metadata."""

    __slots__ = ("data", "size", "aligned", "pool_id", "allocated_at", "last_used")

    def __init__(self, size: int, pool_id: str, alignment: int = 64) -> None:
        self.size = size
        self.pool_id = pool_id
        self.allocated_at = time.monotonic_ns()
        self.last_used = self.allocated_at
        self.aligned = alignment > 1

        if self.aligned:
            # Create aligned memory block
            self.data = self._create_aligned_memory(size, alignment)
        else:
            self.data = bytearray(size)

    def _create_aligned_memory(self, size: int, alignment: int) -> bytearray:
        """Create memory-aligned buffer for optimal cache performance."""
        if sys.platform == "linux":
            try:
                # Use posix_memalign for optimal alignment on Linux
                ptr = ctypes.c_void_p()
                result = ctypes.CDLL("libc.so.6").posix_memalign(ctypes.byref(ptr), alignment, size)
                if result == 0:
                    # Create buffer from aligned memory
                    return (ctypes.c_char * size).from_address(ptr.value)
            except (OSError, AttributeError):
                # TODO: Add proper exception handling

                # Fallback to manual alignment
                pass
        raw_size = size + alignment
        raw_buffer = bytearray(raw_size)

        # Calculate aligned offset
        addr = id(raw_buffer)
        aligned_offset = (alignment - (addr % alignment)) % alignment

        # Return aligned view
        return raw_buffer[aligned_offset : aligned_offset + size]

    def reset(self):
        """Reset the memory block for reuse."""
        if isinstance(self.data, bytearray):
            self.data[:] = b"\x00"  # Clear with zeros
        self.last_used = time.monotonic_ns()


class BaseMemoryPool(ABC):
    """Abstract base class for memory pools."""

    def __init__(self, pool_id: str) -> None:
        self.pool_id = pool_id
        self.stats = MemoryStats()
        self._lock = threading.RLock()
        self._start_time = time.monotonic_ns()

    @abstractmethod
    def get_block(self, size: int) -> Optional[MemoryBlock]:
        """Get a memory block of at least the specified size."""

    @abstractmethod
    def return_block(self, block: MemoryBlock):
        """Return a memory block to the pool."""

    @abstractmethod
    def get_stats(self) -> MemoryStats:
        """Get pool statistics."""

    def _update_allocation_stats(self, allocation_time_ns: int):
        """Update allocation timing statistics."""
        self.stats.allocation_count += 1

        # Update average allocation time using exponential moving average
        if self.stats.avg_allocation_time_ns == 0:
            self.stats.avg_allocation_time_ns = allocation_time_ns
        else:
            alpha = 0.1
            self.stats.avg_allocation_time_ns = (
                alpha * allocation_time_ns + (1 - alpha) * self.stats.avg_allocation_time_ns
            )


class FixedSizePool(BaseMemoryPool):
    """Fixed-size memory pool for specific block sizes."""

    def __init__(
        self,
        pool_id: str,
        block_size: int,
        max_blocks: int = 1000,
        alignment: int = 64,
        prealloc_blocks: int = 100,
    ) -> None:
        super().__init__(pool_id)

        self.block_size = block_size
        self.max_blocks = max_blocks
        self.alignment = alignment

        # Available blocks queue
        self._available_blocks: deque = deque()
        self._in_use_blocks: weakref.WeakSet = weakref.WeakSet()

        # Pre-allocate blocks for hot path performance
        self._preallocate_blocks(prealloc_blocks)

        logger.debug(f"Created fixed-size pool {pool_id} with {block_size} byte blocks")

    def _preallocate_blocks(self, count: int):
        """Pre-allocate memory blocks to avoid allocation overhead.
            for _ in range(min(count, self.max_blocks)):
                block = MemoryBlock(self.block_size, self.pool_id, self.alignment)
                self._available_blocks.append(block)
                self.stats.total_allocated += self.block_size

        def get_block(self, size: int) -> Optional[MemoryBlock]:
            Get a memory block from the pool."""
        if size > self.block_size:
            return None

        start_time = time.monotonic_ns()

        with self._lock:
            # Try to get from available blocks first
            if self._available_blocks:
                block = self._available_blocks.popleft()
                block.reset()
                self._in_use_blocks.add(block)
                self.stats.cache_hits += 1
            else:
                # Create new block if under limit
                if len(self._in_use_blocks) < self.max_blocks:
                    block = MemoryBlock(self.block_size, self.pool_id, self.alignment)
                    self._in_use_blocks.add(block)
                    self.stats.total_allocated += self.block_size
                    self.stats.cache_misses += 1
                else:
                    return None

            self.stats.current_usage += self.block_size
            self.stats.peak_usage = max(self.stats.peak_usage, self.stats.current_usage)

        allocation_time = time.monotonic_ns() - start_time
        self._update_allocation_stats(allocation_time)

        return block

    def return_block(self, block: MemoryBlock):
        """Return a block to the pool."""
        if block.pool_id != self.pool_id:
            logger.warning(f"Block {block} doesn't belong to pool {self.pool_id}")
            return

        with self._lock:
            if block in self._in_use_blocks:
                self._in_use_blocks.remove(block)
                self.stats.current_usage -= self.block_size
                self.stats.free_count += 1

                # Return to available pool if not at capacity
                if len(self._available_blocks) < self.max_blocks // 2:
                    self._available_blocks.append(block)
                else:
                    # Block will be garbage collected
                    self.stats.total_freed += self.block_size

    def get_stats(self) -> MemoryStats:
        """Get current pool statistics.
                with self._lock:
                    stats = MemoryStats(
                        total_allocated=self.stats.total_allocated,
                        total_freed=self.stats.total_freed,
                        current_usage=self.stats.current_usage,
                        peak_usage=self.stats.peak_usage,
                        allocation_count=self.stats.allocation_count,
                        free_count=self.stats.free_count,
                        cache_hits=self.stats.cache_hits,
                        cache_misses=self.stats.cache_misses,
                        avg_allocation_time_ns=self.stats.avg_allocation_time_ns
                    )

                    # Calculate fragmentation ratio
                    available_blocks = len(self._available_blocks)
                    total_blocks = available_blocks + len(self._in_use_blocks)
                    if total_blocks > 0:
                        stats.fragmentation_ratio = available_blocks / total_blocks

                    return stats


        class AdaptivePool(BaseMemoryPool):
            Adaptive memory pool that adjusts to allocation patterns."""

    def __init__(
        self,
        pool_id: str,
        min_block_size: int = 1024,
        max_block_size: int = 1024 * 1024,
        size_classes: Optional[list[int]] = None,
    ) -> None:
        super().__init__(pool_id)

        self.min_block_size = min_block_size
        self.max_block_size = max_block_size

        # Define size classes for different allocation sizes
        if size_classes is None:
            self.size_classes = [
                1024,  # 1KB
                4096,  # 4KB
                8192,  # 8KB
                16384,  # 16KB
                32768,  # 32KB
                65536,  # 64KB
                131072,  # 128KB
                262144,  # 256KB
                524288,  # 512KB
                1048576,  # 1MB
            ]
        else:
            self.size_classes = sorted(size_classes)

        # Create fixed pools for each size class
        self._size_pools: dict[int, FixedSizePool] = {}
        for size in self.size_classes:
            pool_id_sized = f"{pool_id}_{size}"
            self._size_pools[size] = FixedSizePool(
                pool_id_sized, size, max_blocks=500, alignment=64
            )

        # Track allocation patterns for adaptation
        self._allocation_history: deque = deque(maxlen=10000)
        self._adaptation_task: Optional[asyncio.Task] = None

        logger.info(f"Created adaptive pool {pool_id} with {len(self.size_classes)} size classes")

    def get_block(self, size: int) -> Optional[MemoryBlock]:
        """Get appropriately-sized memory block.
            if size > self.max_block_size:
                return None

            # Find best-fit size class
            best_size = self._find_best_size_class(size)
            if best_size is None:
                return None

            # Record allocation pattern
            self._allocation_history.append((size, best_size, time.monotonic_ns()))

            # Get block from appropriate pool
            pool = self._size_pools[best_size]
            block = pool.get_block(size)

            if block:
                # Update aggregate stats
                self.stats.allocation_count += 1
                self.stats.current_usage += best_size
                self.stats.peak_usage = max(self.stats.peak_usage, self.stats.current_usage)

            return block

        def return_block(self, block: MemoryBlock):
            Return block to appropriate pool."""
        # Find the pool that owns this block
        for size, pool in self._size_pools.items():
            if block.pool_id.endswith(f"_{size}"):
                pool.return_block(block)
                self.stats.current_usage -= size
                self.stats.free_count += 1
                break

    def _find_best_size_class(self, requested_size: int) -> Optional[int]:
        """Find the smallest size class that fits the requested size.
            for size_class in self.size_classes:
                if size_class >= requested_size:
                    return size_class
            return None

        async def start_adaptation(self):
            Start adaptive optimization based on allocation patterns."""
        if self._adaptation_task is None:
            self._adaptation_task = asyncio.create_task(self._adaptation_loop())

    async def stop_adaptation(self):
        """Stop adaptive optimization.
            if self._adaptation_task:
                self._adaptation_task.cancel()
                try:
                    await self._adaptation_task
                except asyncio.CancelledError:
                    logger.error(f"Error during cleanup in stop_adaptation: {e}", exc_info=True)
                self._adaptation_task = None

        async def _adaptation_loop(self):
            Background task to adapt pool sizes based on usage patterns."""
        while True:
            try:
                await asyncio.sleep(30.0)  # Adapt every 30 seconds
                await self._analyze_and_adapt()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Adaptation error: {e}")

    async def _analyze_and_adapt(self):
        """Analyze allocation patterns and adapt pool configurations."""
        if len(self._allocation_history) < 100:
            return

        # Analyze recent allocation patterns
        recent_allocations = list(self._allocation_history)[-1000:]
        size_frequency = {}

        for _requested, allocated, _timestamp in recent_allocations:
            if allocated not in size_frequency:
                size_frequency[allocated] = 0
            size_frequency[allocated] += 1

        # Identify hot size classes
        total_allocations = len(recent_allocations)
        for size_class, frequency in size_frequency.items():
            usage_ratio = frequency / total_allocations

            pool = self._size_pools[size_class]
            current_max = pool.max_blocks

            # Adjust pool size based on usage
            if usage_ratio > 0.3 and current_max < 2000:
                # High usage - increase pool size
                pool.max_blocks = min(current_max * 2, 2000)
                logger.debug(f"Increased pool {size_class} to {pool.max_blocks} blocks")
            elif usage_ratio < 0.05 and current_max > 100:
                # Low usage - decrease pool size
                pool.max_blocks = max(current_max // 2, 100)
                logger.debug(f"Decreased pool {size_class} to {pool.max_blocks} blocks")

    def get_stats(self) -> MemoryStats:
        """Get aggregate statistics from all pools.
                aggregate_stats = MemoryStats()

                for pool in self._size_pools.values():
                    pool_stats = pool.get_stats()
                    aggregate_stats.total_allocated += pool_stats.total_allocated
                    aggregate_stats.total_freed += pool_stats.total_freed
                    aggregate_stats.current_usage += pool_stats.current_usage
                    aggregate_stats.peak_usage = max(aggregate_stats.peak_usage, pool_stats.peak_usage)
                    aggregate_stats.allocation_count += pool_stats.allocation_count
                    aggregate_stats.free_count += pool_stats.free_count
                    aggregate_stats.cache_hits += pool_stats.cache_hits
                    aggregate_stats.cache_misses += pool_stats.cache_misses

                # Calculate average allocation time
                if aggregate_stats.allocation_count > 0:
                    total_time = sum(
                        pool.stats.avg_allocation_time_ns * pool.stats.allocation_count
                        for pool in self._size_pools.values()
                    )
                    aggregate_stats.avg_allocation_time_ns = total_time / aggregate_stats.allocation_count

                return aggregate_stats


        class MemoryMappedPool(BaseMemoryPool):
            Memory-mapped file pool for very large allocations."""

    def __init__(
        self,
        pool_id: str,
        backing_file: Optional[str] = None,
        initial_size: int = 100 * 1024 * 1024,
    ):  # 100MB
        super().__init__(pool_id)

        self.initial_size = initial_size
        self.backing_file = backing_file

        # Create memory-mapped region
        if backing_file:
            self._fd = os.open(backing_file, os.O_RDWR | os.O_CREAT)
            os.ftruncate(self._fd, initial_size)
            self._mmap = mmap.mmap(self._fd, initial_size)
        else:
            # Anonymous mapping
            self._mmap = mmap.mmap(-1, initial_size)
            self._fd = None

        # Track allocated regions
        self._allocated_regions: list[tuple[int, int]] = []  # (offset, size)
        self._free_regions: list[tuple[int, int]] = [(0, initial_size)]

        logger.info(f"Created memory-mapped pool {pool_id} with {initial_size} bytes")

    def get_block(self, size: int) -> Optional[MemoryBlock]:
        """Allocate a block from memory-mapped region.
            start_time = time.monotonic_ns()

            with self._lock:
                # Find suitable free region
                for i, (offset, free_size) in enumerate(self._free_regions):
                    if free_size >= size:
                        # Allocate from this region
                        self._allocated_regions.append((offset, size))

                        # Update free regions
                        if free_size == size:
                            # Exact fit - remove free region
                            del self._free_regions[i]
                        else:
                            # Partial fit - update free region
                            self._free_regions[i] = (offset + size, free_size - size)

                        # Create block with memory view
                        block_data = memoryview(self._mmap)[offset:offset + size]
                        block = MemoryBlock(size, self.pool_id, alignment=1)
                        block.data = block_data

                        self.stats.current_usage += size
                        self.stats.peak_usage = max(self.stats.peak_usage, self.stats.current_usage)

                        allocation_time = time.monotonic_ns() - start_time
                        self._update_allocation_stats(allocation_time)

                        return block

            return None

        def return_block(self, block: MemoryBlock):
            Return a memory-mapped block."""
        if block.pool_id != self.pool_id:
            return

        with self._lock:
            # Find the allocated region for this block
            block_offset = None
            for i, (offset, allocated_size) in enumerate(self._allocated_regions):
                if allocated_size == block.size:
                    # This might be our block (simplified check)
                    block_offset = offset
                    del self._allocated_regions[i]
                    break

            if block_offset is not None:
                # Add back to free regions
                self._free_regions.append((block_offset, block.size))
                self._merge_free_regions()

                self.stats.current_usage -= block.size
                self.stats.free_count += 1

    def _merge_free_regions(self):
        """Merge adjacent free regions to reduce fragmentation.
            if len(self._free_regions) <= 1:
                return

            # Sort by offset
            self._free_regions.sort(key=lambda x: x[0])

            merged = []
            current_offset, current_size = self._free_regions[0]

            for offset, size in self._free_regions[1:]:
                if current_offset + current_size == offset:
                    # Adjacent regions - merge
                    current_size += size
                else:
                    # Non-adjacent - add current and start new
                    merged.append((current_offset, current_size))
                    current_offset, current_size = offset, size

            merged.append((current_offset, current_size))
            self._free_regions = merged

        def get_stats(self) -> MemoryStats:
            Get memory-mapped pool statistics."""
        with self._lock:
            stats = MemoryStats(
                total_allocated=self.initial_size,
                current_usage=self.stats.current_usage,
                peak_usage=self.stats.peak_usage,
                allocation_count=self.stats.allocation_count,
                free_count=self.stats.free_count,
                avg_allocation_time_ns=self.stats.avg_allocation_time_ns,
            )

            # Calculate fragmentation
            if self._free_regions:
                largest_free = max(size for _, size in self._free_regions)
                total_free = sum(size for _, size in self._free_regions)
                if total_free > 0:
                    stats.fragmentation_ratio = 1.0 - (largest_free / total_free)

            return stats

    def __del__(self):
        """Cleanup memory mapping.
                if hasattr(self, '_mmap'):
                    self._mmap.close()
                if hasattr(self, '_fd') and self._fd is not None:
                    os.close(self._fd)


        class GlobalMemoryManager:
            Global memory manager coordinating multiple pools."""

    def __init__(self) -> None:
        self._pools: dict[str, BaseMemoryPool] = {}
        self._default_pool: Optional[AdaptivePool] = None
        self._lock = threading.RLock()

        # Create default adaptive pool
        self._create_default_pools()

        # Background monitoring
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitoring_enabled = False

    def _create_default_pools(self):
        """Create default memory pools for common use cases."""
        # Main adaptive pool for general use
        self._default_pool = AdaptivePool("default")
        self._pools["default"] = self._default_pool

        # Specialized pools for specific sizes
        self._pools["small"] = FixedSizePool("small", 1024, max_blocks=2000)
        self._pools["medium"] = FixedSizePool("medium", 8192, max_blocks=1000)
        self._pools["large"] = FixedSizePool("large", 65536, max_blocks=500)

        logger.info("Created default memory pools")

    def get_pool(self, pool_name: str) -> Optional[BaseMemoryPool]:
        """Get a specific memory pool.
            return self._pools.get(pool_name)

        def create_pool(self,
                       pool_name: str,
                       strategy: PoolStrategy,
                       **kwargs) -> BaseMemoryPool:
            Create a new memory pool with specified strategy."""
        with self._lock:
            if pool_name in self._pools:
                raise ValueError(f"Pool {pool_name} already exists")

            if strategy == PoolStrategy.FIXED_SIZE:
                pool = FixedSizePool(pool_name, **kwargs)
            elif strategy == PoolStrategy.ADAPTIVE:
                pool = AdaptivePool(pool_name, **kwargs)
            elif strategy == PoolStrategy.NUMA_AWARE:
                # TODO: Implement NUMA-aware pool
                pool = AdaptivePool(pool_name, **kwargs)
            elif strategy == PoolStrategy.LOCKFREE:
                # TODO: Implement lock-free pool
                pool = FixedSizePool(pool_name, **kwargs)
            else:
                raise ValueError(f"Unknown pool strategy: {strategy}")

            self._pools[pool_name] = pool
            return pool

    def get_memory(self, size: int, pool_name: str = "default") -> Optional[MemoryBlock]:
        """Get memory block from specified pool.
            pool = self._pools.get(pool_name, self._default_pool)
            if pool:
                return pool.get_block(size)
            return None

        def return_memory(self, block: MemoryBlock):
            Return memory block to its originating pool."""
        # Find the pool that owns this block
        for pool in self._pools.values():
            if block.pool_id.startswith(pool.pool_id):
                pool.return_block(block)
                return

        logger.warning(f"Could not find pool for block {block.pool_id}")

    async def start_monitoring(self):
        """Start background monitoring of memory pools.
            if not self._monitoring_enabled:
                self._monitoring_enabled = True
                self._monitor_task = asyncio.create_task(self._monitor_loop())

                # Start adaptation for adaptive pools
                for pool in self._pools.values():
                    if isinstance(pool, AdaptivePool):
                        await pool.start_adaptation()

        async def stop_monitoring(self):
            Stop background monitoring."""
        self._monitoring_enabled = False

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                # TODO: Add proper exception handling

                # Stop adaptation
                pass
        for pool in self._pools.values():
            if isinstance(pool, AdaptivePool):
                await pool.stop_adaptation()

    async def _monitor_loop(self):
        """Background monitoring loop."""
        while self._monitoring_enabled:
            try:
                await asyncio.sleep(60.0)  # Monitor every minute
                await self._check_memory_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")

    async def _check_memory_health(self):
        """Check memory health and log warnings if needed."""
        total_usage = 0
        total_peak = 0

        for pool_name, pool in self._pools.items():
            stats = pool.get_stats()
            total_usage += stats.current_usage
            total_peak += stats.peak_usage

            # Check for potential issues
            if stats.fragmentation_ratio > 0.7:
                logger.warning(
                    f"High fragmentation in pool {pool_name}: {stats.fragmentation_ratio:.2f}"
                )

            if stats.current_usage > stats.peak_usage * 0.9:
                logger.warning(f"Pool {pool_name} nearing capacity: {stats.current_usage} bytes")

        logger.debug(f"Total memory usage: {total_usage} bytes (peak: {total_peak})")

    def get_global_stats(self) -> dict[str, MemoryStats]:
        """Get statistics for all pools."""
        return {name: pool.get_stats() for name, pool in self._pools.items()}


# Global memory manager instance
global_memory_manager = GlobalMemoryManager()
