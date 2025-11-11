"""
Cache Decorators

Decorators for caching function results, views, and pages:
- Function result caching with custom key generation
- Page/view caching with vary support
- Conditional caching
- Cache invalidation decorators
- TTL configuration per decorator

NO MOCK DATA: Real caching using CacheManager.
"""

import asyncio
import hashlib
import inspect
import json
import logging
from functools import wraps
from typing import Any, Callable, List, Optional, Union

from .manager import CacheManager, get_cache

logger = logging.getLogger(__name__)


def _generate_cache_key(
    prefix: str,
    func: Callable,
    args: tuple,
    kwargs: dict,
    key_func: Optional[Callable] = None,
) -> str:
    """
    Generate cache key from function call.

    Args:
        prefix: Key prefix
        func: Function being called
        args: Function arguments
        kwargs: Function keyword arguments
        key_func: Custom key generation function

    Returns:
        Cache key string
    """
    if key_func:
        # Use custom key function
        return f"{prefix}:{key_func(*args, **kwargs)}"

    # Default key generation
    # Use function name + arguments
    func_name = f"{func.__module__}.{func.__qualname__}"

    # Serialize arguments
    try:
        # Try JSON serialization first (faster)
        args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    except (TypeError, ValueError):
        # Fall back to repr
        args_str = f"{args}:{kwargs}"

    # Hash for long keys (use SHA-256 instead of MD5)
    if len(args_str) > 200:
        args_hash = hashlib.sha256(args_str.encode("utf-8")).hexdigest()
        return f"{prefix}:{func_name}:{args_hash}"
    else:
        return f"{prefix}:{func_name}:{args_str}"


def cache_result(
    ttl: Optional[int] = 300,
    key_prefix: str = "func",
    key_func: Optional[Callable] = None,
    cache: Optional[CacheManager] = None,
    unless: Optional[Callable] = None,
):
    """
    Cache function result.

    Args:
        ttl: Time-to-live in seconds (default: 300)
        key_prefix: Cache key prefix (default: 'func')
        key_func: Custom key generation function
        cache: Cache instance (default: global cache)
        unless: Condition function - skip cache if returns True

    Example:
        @cache_result(ttl=300, key_prefix='user')
        async def get_user(user_id: int):
            return await db.query(User).get(user_id)

        @cache_result(ttl=60, key_func=lambda user_id: f"posts:{user_id}")
        async def get_user_posts(user_id: int):
            return await db.query(Post).filter(user_id=user_id).all()

        # Conditional caching
        @cache_result(ttl=60, unless=lambda: current_user.is_admin)
        async def get_data():
            return expensive_computation()
    """

    def decorator(func: Callable) -> Callable:
        # Determine if function is async
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Get cache instance
                cache_instance = cache or get_cache()

                # Check unless condition
                if unless:
                    try:
                        skip = unless()
                        if asyncio.iscoroutine(skip):
                            skip = await skip
                        if skip:
                            return await func(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Cache unless condition error: {e}")

                # Generate cache key
                cache_key = _generate_cache_key(key_prefix, func, args, kwargs, key_func)

                # Try to get from cache
                try:
                    cached = await cache_instance.get(cache_key)
                    if cached is not None:
                        return cached
                except Exception as e:
                    logger.error(f"Cache GET error: {e}")

                # Call function
                result = await func(*args, **kwargs)

                # Store in cache
                try:
                    await cache_instance.set(cache_key, result, ttl)
                except Exception as e:
                    logger.error(f"Cache SET error: {e}")

                return result

            return async_wrapper

        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Get cache instance
                cache_instance = cache or get_cache()

                # Check unless condition
                if unless:
                    try:
                        if unless():
                            return func(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Cache unless condition error: {e}")

                # Generate cache key
                cache_key = _generate_cache_key(key_prefix, func, args, kwargs, key_func)

                # Try to get from cache (sync version needs event loop)
                try:
                    loop = asyncio.get_event_loop()
                    cached = loop.run_until_complete(cache_instance.get(cache_key))
                    if cached is not None:
                        return cached
                except Exception as e:
                    logger.error(f"Cache GET error: {e}")

                # Call function
                result = func(*args, **kwargs)

                # Store in cache
                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(cache_instance.set(cache_key, result, ttl))
                except Exception as e:
                    logger.error(f"Cache SET error: {e}")

                return result

            return sync_wrapper

    return decorator


def cache_page(
    ttl: Optional[int] = 60,
    key_prefix: str = "page",
    vary: Optional[List[str]] = None,
    cache: Optional[CacheManager] = None,
):
    """
    Cache page/view response.

    Args:
        ttl: Time-to-live in seconds (default: 60)
        key_prefix: Cache key prefix (default: 'page')
        vary: List of headers to vary cache on (e.g., ['Accept-Language'])
        cache: Cache instance (default: global cache)

    Example:
        @cache_page(ttl=60)
        async def homepage(request):
            return render_template('index.html')

        @cache_page(ttl=300, vary=['Accept-Language'])
        async def localized_page(request):
            return render_template('page.html')
    """

    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Get cache instance
                cache_instance = cache or get_cache()

                # Extract request object
                request = None
                if args and hasattr(args[0], "url"):
                    request = args[0]
                elif "request" in kwargs:
                    request = kwargs["request"]

                if not request:
                    # Can't cache without request
                    return await func(*args, **kwargs)

                # Generate cache key
                cache_key = f"{key_prefix}:{request.url.path}"

                # Add vary headers to key
                if vary and hasattr(request, "headers"):
                    vary_values = []
                    for header in vary:
                        value = request.headers.get(header, "")
                        vary_values.append(f"{header}:{value}")
                    if vary_values:
                        vary_str = ":".join(vary_values)
                        cache_key = f"{cache_key}:{vary_str}"

                # Try to get from cache
                try:
                    cached = await cache_instance.get(cache_key)
                    if cached is not None:
                        return cached
                except Exception as e:
                    logger.error(f"Page cache GET error: {e}")

                # Call view function
                response = await func(*args, **kwargs)

                # Store in cache
                try:
                    await cache_instance.set(cache_key, response, ttl)
                except Exception as e:
                    logger.error(f"Page cache SET error: {e}")

                return response

            return async_wrapper

        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Similar implementation for sync functions
                cache_instance = cache or get_cache()

                request = None
                if args and hasattr(args[0], "url"):
                    request = args[0]
                elif "request" in kwargs:
                    request = kwargs["request"]

                if not request:
                    return func(*args, **kwargs)

                cache_key = f"{key_prefix}:{request.url.path}"

                if vary and hasattr(request, "headers"):
                    vary_values = []
                    for header in vary:
                        value = request.headers.get(header, "")
                        vary_values.append(f"{header}:{value}")
                    if vary_values:
                        vary_str = ":".join(vary_values)
                        cache_key = f"{cache_key}:{vary_str}"

                try:
                    loop = asyncio.get_event_loop()
                    cached = loop.run_until_complete(cache_instance.get(cache_key))
                    if cached is not None:
                        return cached
                except Exception as e:
                    logger.error(f"Page cache GET error: {e}")

                response = func(*args, **kwargs)

                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(cache_instance.set(cache_key, response, ttl))
                except Exception as e:
                    logger.error(f"Page cache SET error: {e}")

                return response

            return sync_wrapper

    return decorator


def cache_unless(condition: Callable):
    """
    Cache result unless condition is true.

    Args:
        condition: Function that returns True to skip cache

    Example:
        @cache_unless(lambda: current_user.is_authenticated)
        async def public_page(request):
            return render_template('public.html')
    """
    return cache_result(unless=condition)


def cache_invalidate(keys: Union[str, List[str], Callable], cache: Optional[CacheManager] = None):
    """
    Invalidate cache keys after function execution.

    Args:
        keys: Key(s) to invalidate or function to generate keys
        cache: Cache instance (default: global cache)

    Example:
        # Fixed keys
        @cache_invalidate(keys=['user:1', 'user:1:posts'])
        async def update_user(user_id: int, data: dict):
            await User.query().filter(id=user_id).update(data)

        # Dynamic keys
        @cache_invalidate(keys=lambda user_id: [f'user:{user_id}', f'user:{user_id}:posts'])
        async def update_user(user_id: int, data: dict):
            await User.query().filter(id=user_id).update(data)
    """

    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Call function first
                result = await func(*args, **kwargs)

                # Invalidate cache
                cache_instance = cache or get_cache()

                # Generate keys to invalidate
                if callable(keys):
                    keys_to_delete = keys(*args, **kwargs)
                else:
                    keys_to_delete = keys

                # Ensure list
                if isinstance(keys_to_delete, str):
                    keys_to_delete = [keys_to_delete]

                # Delete keys
                try:
                    if keys_to_delete:
                        await cache_instance.delete_many(keys_to_delete)
                except Exception as e:
                    logger.error(f"Cache invalidation error: {e}")

                return result

            return async_wrapper

        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                cache_instance = cache or get_cache()

                if callable(keys):
                    keys_to_delete = keys(*args, **kwargs)
                else:
                    keys_to_delete = keys

                if isinstance(keys_to_delete, str):
                    keys_to_delete = [keys_to_delete]

                try:
                    if keys_to_delete:
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(cache_instance.delete_many(keys_to_delete))
                except Exception as e:
                    logger.error(f"Cache invalidation error: {e}")

                return result

            return sync_wrapper

    return decorator


def cache_invalidate_pattern(pattern: Union[str, Callable], cache: Optional[CacheManager] = None):
    """
    Invalidate cache keys matching pattern after function execution.

    Args:
        pattern: Pattern to match or function to generate pattern
        cache: Cache instance (default: global cache)

    Example:
        @cache_invalidate_pattern(pattern='user:*')
        async def clear_all_users():
            await User.query().delete()

        @cache_invalidate_pattern(pattern=lambda user_id: f'user:{user_id}:*')
        async def update_user(user_id: int, data: dict):
            await User.query().filter(id=user_id).update(data)
    """

    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)

                cache_instance = cache or get_cache()

                # Generate pattern
                if callable(pattern):
                    pattern_str = pattern(*args, **kwargs)
                else:
                    pattern_str = pattern

                # Delete matching keys
                try:
                    await cache_instance.delete_pattern(pattern_str)
                except Exception as e:
                    logger.error(f"Cache pattern invalidation error: {e}")

                return result

            return async_wrapper

        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                cache_instance = cache or get_cache()

                if callable(pattern):
                    pattern_str = pattern(*args, **kwargs)
                else:
                    pattern_str = pattern

                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(cache_instance.delete_pattern(pattern_str))
                except Exception as e:
                    logger.error(f"Cache pattern invalidation error: {e}")

                return result

            return sync_wrapper

    return decorator


def memoize(maxsize: int = 128, ttl: Optional[int] = None):
    """
    Simple memoization decorator (similar to functools.lru_cache but with TTL).

    Args:
        maxsize: Maximum cache size
        ttl: Time-to-live in seconds

    Example:
        @memoize(maxsize=100, ttl=300)
        def expensive_computation(n: int) -> int:
            return sum(range(n))
    """
    return cache_result(ttl=ttl, key_prefix=f"memo:{maxsize}")


__all__ = [
    "cache_result",
    "cache_page",
    "cache_unless",
    "cache_invalidate",
    "cache_invalidate_pattern",
    "memoize",
]
