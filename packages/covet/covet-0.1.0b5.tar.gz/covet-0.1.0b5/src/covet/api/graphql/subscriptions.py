"""
GraphQL Subscriptions with PubSub

Real-time subscriptions using async generators and pub/sub pattern.
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Set

import strawberry

logger = logging.getLogger(__name__)


@dataclass
class Topic:
    """Pub/sub topic."""

    name: str
    subscribers: Set[asyncio.Queue] = field(default_factory=set)

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to topic."""
        queue: asyncio.Queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from topic."""
        self.subscribers.discard(queue)

    async def publish(self, message: Any):
        """Publish message to all subscribers."""
        for queue in list(self.subscribers):
            try:
                await queue.put(message)
            except Exception as e:
                logger.error(f"Error publishing to subscriber: {e}")
                self.subscribers.discard(queue)


class PubSub:
    """
    In-memory pub/sub system for GraphQL subscriptions.

    In production, use Redis or another distributed pub/sub system.

    Example:
        pubsub = PubSub()

        # Publish
        await pubsub.publish('user.created', {'id': 1, 'name': 'John'})

        # Subscribe
        async for message in pubsub.subscribe('user.created'):
            logger.info(message)
    """

    def __init__(self):
        """Initialize pub/sub."""
        self.topics: Dict[str, Topic] = {}
        self._lock = asyncio.Lock()

    def _get_topic(self, topic_name: str) -> Topic:
        """Get or create topic."""
        if topic_name not in self.topics:
            self.topics[topic_name] = Topic(name=topic_name)
        return self.topics[topic_name]

    async def publish(self, topic_name: str, message: Any):
        """
        Publish message to topic.

        Args:
            topic_name: Topic name
            message: Message to publish
        """
        async with self._lock:
            topic = self._get_topic(topic_name)
            await topic.publish(message)

        logger.debug(f"Published to {topic_name}: {message}")

    async def subscribe(self, topic_name: str) -> AsyncIterator[Any]:
        """
        Subscribe to topic.

        Args:
            topic_name: Topic name

        Yields:
            Messages from topic
        """
        async with self._lock:
            topic = self._get_topic(topic_name)
            queue = topic.subscribe()

        try:
            logger.debug(f"Subscribed to {topic_name}")

            while True:
                message = await queue.get()
                yield message

        finally:
            # Cleanup on disconnect
            async with self._lock:
                topic.unsubscribe(queue)
            logger.debug(f"Unsubscribed from {topic_name}")

    async def subscribe_multiple(self, *topic_names: str) -> AsyncIterator[tuple[str, Any]]:
        """
        Subscribe to multiple topics.

        Args:
            *topic_names: Topic names

        Yields:
            Tuples of (topic_name, message)
        """
        # Create queue for each topic
        queues = {}
        async with self._lock:
            for topic_name in topic_names:
                topic = self._get_topic(topic_name)
                queues[topic_name] = topic.subscribe()

        try:
            # Wait for messages from any queue
            pending_tasks = {
                asyncio.create_task(queue.get()): topic_name for topic_name, queue in queues.items()
            }

            while pending_tasks:
                done, pending_tasks = await asyncio.wait(
                    pending_tasks, return_when=asyncio.FIRST_COMPLETED
                )

                for task in done:
                    topic_name = pending_tasks.pop(task)
                    message = task.result()
                    yield (topic_name, message)

                    # Re-subscribe to topic
                    new_task = asyncio.create_task(queues[topic_name].get())
                    pending_tasks[new_task] = topic_name

        finally:
            # Cleanup
            async with self._lock:
                for topic_name, queue in queues.items():
                    topic = self._get_topic(topic_name)
                    topic.unsubscribe(queue)

    def get_subscriber_count(self, topic_name: str) -> int:
        """Get number of subscribers for topic."""
        if topic_name in self.topics:
            return len(self.topics[topic_name].subscribers)
        return 0


class SubscriptionManager:
    """
    Manages GraphQL subscriptions.

    Provides utilities for creating and managing subscription resolvers.
    """

    def __init__(self, pubsub: Optional[PubSub] = None):
        """
        Initialize subscription manager.

        Args:
            pubsub: PubSub instance (creates new one if not provided)
        """
        self.pubsub = pubsub or PubSub()

    async def publish(self, topic: str, message: Any):
        """Publish message to topic."""
        await self.pubsub.publish(topic, message)

    def subscribe(
        self,
        topic: str,
        filter_fn: Optional[Callable[[Any], bool]] = None,
    ):
        """
        Create subscription resolver.

        Args:
            topic: Topic to subscribe to
            filter_fn: Optional filter function

        Returns:
            Async generator for subscription
        """

        async def subscription_resolver() -> AsyncIterator[Any]:
            async for message in self.pubsub.subscribe(topic):
                if filter_fn is None or filter_fn(message):
                    yield message

        return subscription_resolver


# Global pub/sub instance
_global_pubsub: Optional[PubSub] = None


def get_pubsub() -> PubSub:
    """Get global pub/sub instance."""
    global _global_pubsub
    if _global_pubsub is None:
        _global_pubsub = PubSub()
    return _global_pubsub


async def publish(topic: str, message: Any):
    """Publish to global pub/sub."""
    pubsub = get_pubsub()
    await pubsub.publish(topic, message)


def subscribe(topic: str, filter_fn: Optional[Callable[[Any], bool]] = None):
    """Subscribe to global pub/sub."""
    manager = SubscriptionManager(get_pubsub())
    return manager.subscribe(topic, filter_fn)


def subscription_handler(topic: str, filter_fn: Optional[Callable[[Any], bool]] = None):
    """
    Decorator for subscription resolvers.

    Example:
        @strawberry.type
        class Subscription:
            @strawberry.subscription
            @subscription_handler('user.created')
            async def user_created(self) -> AsyncIterator[User]:
                # Automatically subscribed to 'user.created' topic
                yield
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> AsyncIterator[Any]:
            async for message in get_pubsub().subscribe(topic):
                if filter_fn is None or filter_fn(message):
                    # Call original function with message
                    result = await func(*args, message=message, **kwargs)
                    yield result

        return wrapper

    return decorator


__all__ = [
    "PubSub",
    "Topic",
    "SubscriptionManager",
    "get_pubsub",
    "publish",
    "subscribe",
    "subscription_handler",
]
