"""
ORM Signal System

Django-style signal system for model lifecycle events.
Allows hooking into model operations for validation, logging, caching, etc.

Signals:
    - pre_init: Before model instance creation
    - post_init: After model instance creation
    - pre_save: Before saving to database
    - post_save: After saving to database
    - pre_delete: Before deletion from database
    - post_delete: After deletion from database
    - pre_update: Before updating in database
    - post_update: After updating in database

Example:
    from covet.database.orm.signals import post_save

    @post_save.connect
    async def on_user_saved(sender, instance, created, **kwargs):
        if created:
            logger.info('New user created: {instance.username}')
        else:
            logger.info('User updated: {instance.username}')
"""

import asyncio
import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Type

logger = logging.getLogger(__name__)


class Signal:
    """
    Signal dispatcher for model events.

    Manages signal receivers and dispatches events to registered handlers.
    Supports both sync and async receivers.
    """

    def __init__(self, name: str, providing_args: Optional[List[str]] = None):
        """
        Initialize signal.

        Args:
            name: Signal name (e.g., 'post_save')
            providing_args: List of argument names provided to receivers
        """
        self.name = name
        self.providing_args = providing_args or []
        # sender -> [receivers]
        self._receivers: Dict[str, List[Callable]] = {}
        self._receiver_ids: Set[int] = set()

    def connect(
        self,
        receiver: Optional[Callable] = None,
        sender: Optional[Type] = None,
        weak: bool = True,
        dispatch_uid: Optional[str] = None,
    ) -> Callable:
        """
        Connect a receiver function to this signal.

        Can be used as decorator or direct function call.

        Args:
            receiver: Function to call when signal fires
            sender: Only receive signals from this sender class
            weak: Use weak references (not implemented yet)
            dispatch_uid: Unique identifier for this receiver

        Returns:
            Receiver function (for decorator usage)

        Example:
            # As decorator
            @post_save.connect
            async def my_handler(sender, instance, **kwargs):
                pass

            # With sender filter
            @post_save.connect(sender=User)
            async def user_saved(sender, instance, **kwargs):
                pass

            # Direct call
            post_save.connect(my_handler, sender=User)
        """

        def decorator(func: Callable) -> Callable:
            receiver_id = id(func)

            # Prevent duplicate registration
            if receiver_id in self._receiver_ids:
                logger.warning(f"Receiver {func.__name__} already connected to {self.name}")
                return func

            sender_key = self._get_sender_key(sender)

            if sender_key not in self._receivers:
                self._receivers[sender_key] = []

            self._receivers[sender_key].append(func)
            self._receiver_ids.add(receiver_id)

            logger.debug(
                f"Connected receiver {func.__name__} to signal {self.name} "
                f"(sender: {sender_key})"
            )

            return func

        # Support both @signal.connect and @signal.connect(sender=Model)
        if receiver is not None:
            return decorator(receiver)
        return decorator

    def disconnect(
        self,
        receiver: Optional[Callable] = None,
        sender: Optional[Type] = None,
        dispatch_uid: Optional[str] = None,
    ) -> bool:
        """
        Disconnect a receiver from this signal.

        Args:
            receiver: Function to disconnect
            sender: Sender class filter
            dispatch_uid: Unique identifier

        Returns:
            True if receiver was found and removed
        """
        if receiver is None:
            return False

        receiver_id = id(receiver)
        sender_key = self._get_sender_key(sender)

        if sender_key in self._receivers:
            try:
                self._receivers[sender_key].remove(receiver)
                self._receiver_ids.discard(receiver_id)
                logger.debug(f"Disconnected receiver {receiver.__name__} from signal {self.name}")
                return True
            except ValueError:
                # TODO: Add proper exception handling

                pass
        return False

    async def send(self, sender: Type, **kwargs) -> List[tuple]:
        """
        Send signal to all connected receivers.

        Args:
            sender: Sender class (usually Model class)
            **kwargs: Additional arguments for receivers

        Returns:
            List of (receiver, response) tuples

        Example:
            responses = await post_save.send(
                sender=User,
                instance=user_instance,
                created=True
            )
        """
        responses = []

        # Get receivers for this sender and wildcard receivers
        receivers = []
        sender_key = self._get_sender_key(sender)

        # Add sender-specific receivers
        if sender_key in self._receivers:
            receivers.extend(self._receivers[sender_key])

        # Add wildcard receivers (None sender)
        if None in self._receivers:
            receivers.extend(self._receivers[None])

        # Execute all receivers
        for receiver in receivers:
            try:
                # Check if receiver is async
                if asyncio.iscoroutinefunction(receiver):
                    response = await receiver(sender=sender, **kwargs)
                else:
                    response = receiver(sender=sender, **kwargs)

                responses.append((receiver, response))

            except Exception as e:
                logger.error(
                    f"Error in signal receiver {receiver.__name__} " f"for signal {self.name}: {e}",
                    exc_info=True,
                )
                # Continue with other receivers even if one fails

        return responses

    def send_robust(self, sender: Type, **kwargs) -> List[tuple]:
        """
        Send signal, catching and logging all exceptions.

        Unlike send(), continues even if receivers raise exceptions.
        Returns list of (receiver, response/exception) tuples.

        Args:
            sender: Sender class
            **kwargs: Arguments for receivers

        Returns:
            List of (receiver, response or exception) tuples
        """
        # For now, send() already handles exceptions robustly
        return asyncio.create_task(self.send(sender, **kwargs))

    def has_listeners(self, sender: Optional[Type] = None) -> bool:
        """
        Check if signal has any connected receivers.

        Args:
            sender: Check for specific sender, or any if None

        Returns:
            True if signal has receivers
        """
        if sender is None:
            return len(self._receiver_ids) > 0

        sender_key = self._get_sender_key(sender)
        return sender_key in self._receivers and len(self._receivers[sender_key]) > 0

    def _get_sender_key(self, sender: Optional[Type]) -> Optional[str]:
        """
        Get normalized sender key for receiver lookup.

        Args:
            sender: Sender class or None

        Returns:
            Sender key string or None
        """
        if sender is None:
            return None

        # Use fully qualified class name
        if inspect.isclass(sender):
            return f"{sender.__module__}.{sender.__name__}"

        return str(sender)

    def __repr__(self) -> str:
        """String representation."""
        num_receivers = len(self._receiver_ids)
        return f"Signal('{self.name}', receivers={num_receivers})"


# Pre-defined model signals
pre_init = Signal("pre_init", providing_args=["instance", "args", "kwargs"])

post_init = Signal("post_init", providing_args=["instance"])

pre_save = Signal("pre_save", providing_args=["instance", "raw", "using"])

post_save = Signal("post_save", providing_args=["instance", "created", "raw", "using"])

pre_delete = Signal("pre_delete", providing_args=["instance", "using"])

post_delete = Signal("post_delete", providing_args=["instance", "using"])

pre_update = Signal("pre_update", providing_args=["instance", "using"])

post_update = Signal("post_update", providing_args=["instance", "using"])

# Relationship signals
m2m_changed = Signal(
    "m2m_changed", providing_args=["instance", "action", "reverse", "model", "pk_set"]
)


class receiver:
    """
    Decorator for connecting receivers to signals.

    Example:
        from covet.database.orm.signals import receiver, post_save

        @receiver(post_save, sender=User)
        async def user_saved_handler(sender, instance, created, **kwargs):
            if created:
                await send_welcome_email(instance.email)
    """

    def __init__(self, signal, **kwargs):
        """
        Initialize receiver decorator.

        Args:
            signal: Signal or list of signals to connect to
            **kwargs: Additional connection arguments (e.g., sender)
        """
        if isinstance(signal, (list, tuple)):
            self.signals = signal
        else:
            self.signals = [signal]

        self.kwargs = kwargs

    def __call__(self, func: Callable) -> Callable:
        """
        Connect function to signals.

        Args:
            func: Receiver function

        Returns:
            Original function (unmodified)
        """
        for signal in self.signals:
            signal.connect(func, **self.kwargs)

        return func


__all__ = [
    "Signal",
    "receiver",
    "pre_init",
    "post_init",
    "pre_save",
    "post_save",
    "pre_delete",
    "post_delete",
    "pre_update",
    "post_update",
    "m2m_changed",
]
