"""
DataLoader Implementation for N+1 Query Optimization

Implements Facebook's DataLoader pattern for batching and caching
database queries to prevent N+1 query problems in GraphQL.
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    TypeVar,
    Union,
)

T = TypeVar("T")
K = TypeVar("K")


@dataclass
class LoaderStats:
    """DataLoader statistics."""

    cache_hits: int = 0
    cache_misses: int = 0
    batch_loads: int = 0
    total_keys: int = 0
    avg_batch_size: float = 0.0

    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100


class DataLoader(Generic[K, T]):
    """
    DataLoader for batching and caching.

    Collects individual loads over a single frame of execution and then
    calls the batch loading function with all requested keys.

    Example:
        async def batch_load_users(user_ids: List[int]) -> List[User]:
            users = await db.get_users_by_ids(user_ids)
            # Return users in same order as user_ids
            user_map = {u.id: u for u in users}
            return [user_map.get(id) for id in user_ids]

        user_loader = DataLoader(batch_load_fn=batch_load_users)

        # These will be batched into single database call
        user1 = await user_loader.load(1)
        user2 = await user_loader.load(2)
        user3 = await user_loader.load(3)
    """

    def __init__(
        self,
        batch_load_fn: Callable[[List[K]], Awaitable[List[T]]],
        max_batch_size: int = 100,
        cache: bool = True,
        cache_key_fn: Optional[Callable[[K], str]] = None,
    ):
        """
        Initialize DataLoader.

        Args:
            batch_load_fn: Async function that loads multiple keys
            max_batch_size: Maximum batch size
            cache: Enable caching
            cache_key_fn: Custom cache key function
        """
        self.batch_load_fn = batch_load_fn
        self.max_batch_size = max_batch_size
        self.enable_cache = cache
        self.cache_key_fn = cache_key_fn or str

        # Internal state
        self._cache: Dict[str, T] = {}
        self._queue: List[tuple[K, asyncio.Future]] = []
        self._batch_task: Optional[asyncio.Task] = None

        # Statistics
        self.stats = LoaderStats()

    async def load(self, key: K) -> T:
        """
        Load a single value by key.

        Args:
            key: Key to load

        Returns:
            Loaded value
        """
        # Check cache
        if self.enable_cache:
            cache_key = self.cache_key_fn(key)
            if cache_key in self._cache:
                self.stats.cache_hits += 1
                return self._cache[cache_key]
            self.stats.cache_misses += 1

        # Create future for this load
        future: asyncio.Future = asyncio.Future()
        self._queue.append((key, future))

        # Schedule batch if not already scheduled
        if self._batch_task is None:
            self._batch_task = asyncio.create_task(self._dispatch_batch())

        return await future

    async def load_many(self, keys: List[K]) -> List[T]:
        """
        Load multiple values by keys.

        Args:
            keys: List of keys to load

        Returns:
            List of loaded values
        """
        return await asyncio.gather(*[self.load(key) for key in keys])

    async def _dispatch_batch(self):
        """Dispatch a batch of loads."""
        # Wait for next tick to collect more requests
        await asyncio.sleep(0)

        # Get queued loads
        queue = self._queue
        self._queue = []
        self._batch_task = None

        if not queue:
            return

        # Split into batches if needed
        batches = [
            queue[i : i + self.max_batch_size] for i in range(0, len(queue), self.max_batch_size)
        ]

        for batch in batches:
            await self._load_batch(batch)

    async def _load_batch(self, batch: List[tuple[K, asyncio.Future]]):
        """Load a single batch."""
        keys = [key for key, _ in batch]
        futures = [future for _, future in batch]

        try:
            # Call batch load function
            values = await self.batch_load_fn(keys)

            # Update statistics
            self.stats.batch_loads += 1
            self.stats.total_keys += len(keys)
            self.stats.avg_batch_size = self.stats.total_keys / self.stats.batch_loads

            # Validate response
            if len(values) != len(keys):
                raise ValueError(
                    f"Batch load function must return same number of values as keys. "
                    f"Expected {len(keys)}, got {len(values)}"
                )

            # Resolve futures and update cache
            for key, value, future in zip(keys, values, futures):
                if self.enable_cache:
                    cache_key = self.cache_key_fn(key)
                    self._cache[cache_key] = value

                if not future.done():
                    future.set_result(value)

        except Exception as e:
            # Reject all futures with the error
            for future in futures:
                if not future.done():
                    future.set_exception(e)

    def clear(self, key: Optional[K] = None):
        """
        Clear cache.

        Args:
            key: Specific key to clear, or None to clear all
        """
        if key is None:
            self._cache.clear()
        else:
            cache_key = self.cache_key_fn(key)
            self._cache.pop(cache_key, None)

    def prime(self, key: K, value: T):
        """
        Prime cache with value.

        Args:
            key: Key
            value: Value to cache
        """
        cache_key = self.cache_key_fn(key)
        self._cache[cache_key] = value


class DataLoaderRegistry:
    """
    Registry for managing multiple DataLoaders.

    Typically stored in GraphQL context for request-scoped loaders.

    Example:
        registry = DataLoaderRegistry()
        registry.register('users', user_loader)
        registry.register('posts', post_loader)

        # In resolver
        user_loader = registry.get('users')
        user = await user_loader.load(user_id)
    """

    def __init__(self):
        """Initialize registry."""
        self._loaders: Dict[str, DataLoader] = {}

    def register(self, name: str, loader: DataLoader):
        """
        Register a DataLoader.

        Args:
            name: Loader name
            loader: DataLoader instance
        """
        self._loaders[name] = loader

    def get(self, name: str) -> Optional[DataLoader]:
        """
        Get DataLoader by name.

        Args:
            name: Loader name

        Returns:
            DataLoader instance or None
        """
        return self._loaders.get(name)

    def clear_all(self):
        """Clear all loader caches."""
        for loader in self._loaders.values():
            loader.clear()

    def get_stats(self) -> Dict[str, LoaderStats]:
        """Get statistics for all loaders."""
        return {name: loader.stats for name, loader in self._loaders.items()}


class BatchLoader:
    """
    Base class for creating batch loaders.

    Subclass this and implement batch_load() method.

    Example:
        class UserLoader(BatchLoader):
            async def batch_load(self, user_ids: List[int]) -> List[User]:
                users = await db.get_users_by_ids(user_ids)
                user_map = {u.id: u for u in users}
                return [user_map.get(id) for id in user_ids]

        loader = UserLoader().create_loader()
    """

    async def batch_load(self, keys: List[K]) -> List[T]:
        """
        Load multiple keys.

        Must be implemented by subclass.

        Args:
            keys: List of keys to load

        Returns:
            List of values in same order as keys
        """
        raise NotImplementedError

    def create_loader(self, **kwargs) -> DataLoader:
        """
        Create DataLoader instance.

        Args:
            **kwargs: DataLoader options

        Returns:
            DataLoader instance
        """
        return DataLoader(batch_load_fn=self.batch_load, **kwargs)


def create_loader(batch_fn: Callable[[List[K]], Awaitable[List[T]]], **kwargs) -> DataLoader[K, T]:
    """
    Create DataLoader from batch function.

    Args:
        batch_fn: Batch loading function
        **kwargs: DataLoader options

    Returns:
        DataLoader instance
    """
    return DataLoader(batch_load_fn=batch_fn, **kwargs)


def create_batch_function(
    load_fn: Callable[[K], Awaitable[T]],
) -> Callable[[List[K]], Awaitable[List[T]]]:
    """
    Create batch function from single-key loader.

    Args:
        load_fn: Function that loads single key

    Returns:
        Batch loading function
    """

    async def batch_fn(keys: List[K]) -> List[T]:
        return await asyncio.gather(*[load_fn(key) for key in keys])

    return batch_fn


__all__ = [
    "DataLoader",
    "DataLoaderRegistry",
    "BatchLoader",
    "LoaderStats",
    "create_loader",
    "create_batch_function",
]
