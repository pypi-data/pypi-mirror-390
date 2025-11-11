"""
CovetPy Dependency Injection Container

Advanced dependency injection system providing:
- Service registration and resolution
- Lifecycle management (Singleton, Transient, Scoped)
- Circular dependency detection and resolution
- Interface-based registration
- Factory functions and lazy initialization
- Decorator-based injection
"""

import inspect
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache, wraps
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from covet.core.exceptions import ContainerError

logger = logging.getLogger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class ServiceLifetime(Enum):
    """Service lifetime management options."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


@dataclass
class ServiceDescriptor:
    """Describes a registered service."""

    service_type: Type
    implementation: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    dependencies: List[Type] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class ServiceScope:
    """Manages scoped service instances."""

    def __init__(self) -> None:
        self._instances: Dict[Type, Any] = {}
        self._lock = threading.RLock()

    def get_instance(self, service_type: Type) -> Optional[Any]:
        """Get scoped instance if exists."""
        with self._lock:
            return self._instances.get(service_type)

    def set_instance(self, service_type: Type, instance: Any) -> None:
        """Set scoped instance."""
        with self._lock:
            self._instances[service_type] = instance

    def dispose(self) -> None:
        """Dispose all scoped instances."""
        with self._lock:
            for instance in self._instances.values():
                if hasattr(instance, "dispose"):
                    try:
                        instance.dispose()
                    except Exception as e:
                        # Log disposal error but continue
                        logger.error("Error disposing instance: {e}")

            self._instances.clear()


class Container:
    """
    Advanced dependency injection container with lifecycle management.

    Supports singleton, transient, and scoped service lifetimes with
    automatic dependency resolution and circular dependency detection.
    """

    def __init__(self) -> None:
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._building: set = set()
        self._lock = threading.RLock()
        self._local = threading.local()

    @property
    def _current_scope(self) -> Optional[ServiceScope]:
        """Get current service scope."""
        return getattr(self._local, "scope", None)

    def create_scope(self) -> ServiceScope:
        """Create a new service scope."""
        return ServiceScope()

    def enter_scope(self, scope: ServiceScope) -> None:
        """Enter a service scope."""
        self._local.scope = scope

    def exit_scope(self) -> None:
        """Exit current service scope."""
        if hasattr(self._local, "scope"):
            self._local.scope.dispose()
            delattr(self._local, "scope")

    def register(
        self,
        service_type: Type[T],
        implementation: Optional[Type] = None,
        factory: Optional[Callable[..., T]] = None,
        instance: Optional[T] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    ) -> "Container":
        """
        Register a service in the container.

        Args:
            service_type: The service interface or base type
            implementation: Concrete implementation class
            factory: Factory function to create instances
            instance: Pre-created instance (implies singleton)
            lifetime: Service lifetime management

        Returns:
            Self for method chaining
        """
        if sum(bool(x) for x in [implementation, factory, instance]) != 1:
            raise ContainerError(
                "Must provide exactly one of: implementation, factory, or instance"
            )

        if instance is not None:
            lifetime = ServiceLifetime.SINGLETON

        # Analyze dependencies
        dependencies = []
        if implementation:
            dependencies = self._analyze_dependencies(implementation)
        elif factory:
            dependencies = self._analyze_dependencies(factory)

        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            factory=factory,
            instance=instance,
            lifetime=lifetime,
            dependencies=dependencies,
        )

        with self._lock:
            self._services[service_type] = descriptor

            # Store singleton instance if provided
            if instance is not None:
                self._singletons[service_type] = instance

        return self

    def register_singleton(
        self,
        service_type: Type[T],
        implementation: Optional[Type] = None,
        factory: Optional[Callable[..., T]] = None,
        instance: Optional[T] = None,
    ) -> "Container":
        """Register a singleton service."""
        return self.register(
            service_type, implementation, factory, instance, ServiceLifetime.SINGLETON
        )

    def register_transient(
        self,
        service_type: Type[T],
        implementation: Optional[Type] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> "Container":
        """Register a transient service."""
        return self.register(service_type, implementation, factory, None, ServiceLifetime.TRANSIENT)

    def register_scoped(
        self,
        service_type: Type[T],
        implementation: Optional[Type] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> "Container":
        """Register a scoped service."""
        return self.register(service_type, implementation, factory, None, ServiceLifetime.SCOPED)

    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service instance.

        Args:
            service_type: The service type to resolve

        Returns:
            Service instance

        Raises:
            ContainerError: If service cannot be resolved
        """
        with self._lock:
            return self._resolve_internal(service_type)

    def try_resolve(self, service_type: Type[T]) -> Optional[T]:
        """
        Try to resolve a service instance.

        Args:
            service_type: The service type to resolve

        Returns:
            Service instance or None if not registered
        """
        try:
            return self.resolve(service_type)
        except ContainerError:
            return None

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        with self._lock:
            return service_type in self._services

    def get_services(self) -> List[Type]:
        """Get list of all registered service types."""
        with self._lock:
            return list(self._services.keys())

    def dispose(self) -> None:
        """Dispose all singleton instances."""
        with self._lock:
            for instance in self._singletons.values():
                if hasattr(instance, "dispose"):
                    try:
                        instance.dispose()
                    except Exception as e:
                        logger.error("Error disposing singleton: {e}")

            self._singletons.clear()

    def _resolve_internal(self, service_type: Type[T]) -> T:
        """Internal service resolution with circular dependency detection."""
        # Check for circular dependency
        if service_type in self._building:
            raise ContainerError(f"Circular dependency detected for {service_type}")

        # Check if service is registered
        if service_type not in self._services:
            raise ContainerError(f"Service {service_type} is not registered")

        descriptor = self._services[service_type]

        # Handle singleton lifetime
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]

            # Create singleton instance
            self._building.add(service_type)
            try:
                instance = self._create_instance(descriptor)
                self._singletons[service_type] = instance
                return instance
            finally:
                self._building.discard(service_type)

        # Handle scoped lifetime
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            scope = self._current_scope
            if scope is None:
                raise ContainerError("No active scope for scoped service")

            instance = scope.get_instance(service_type)
            if instance is not None:
                return instance

            # Create scoped instance
            self._building.add(service_type)
            try:
                instance = self._create_instance(descriptor)
                scope.set_instance(service_type, instance)
                return instance
            finally:
                self._building.discard(service_type)

        # Handle transient lifetime
        else:
            self._building.add(service_type)
            try:
                return self._create_instance(descriptor)
            finally:
                self._building.discard(service_type)

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create service instance from descriptor."""
        # Use existing instance
        if descriptor.instance is not None:
            return descriptor.instance

        # Use factory function
        if descriptor.factory is not None:
            return self._invoke_with_injection(descriptor.factory)

        # Use implementation class
        if descriptor.implementation is not None:
            return self._invoke_with_injection(descriptor.implementation)

        raise ContainerError(f"Cannot create instance for {descriptor.service_type}")

    def _invoke_with_injection(self, callable_obj: Callable) -> Any:
        """Invoke callable with dependency injection."""
        # Get type hints for parameters
        try:
            type_hints = get_type_hints(callable_obj)
        except (AttributeError, NameError):
            type_hints = {}

        # Get function signature
        sig = inspect.signature(callable_obj)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name in type_hints:
                param_type = type_hints[param_name]

                # Skip self parameter
                if param_name == "self":
                    continue

                # Resolve dependency
                try:
                    kwargs[param_name] = self._resolve_internal(param_type)
                except ContainerError:
                    # Use default value if available and dependency not found
                    if param.default is not param.empty:
                        kwargs[param_name] = param.default
                    else:
                        raise

        return callable_obj(**kwargs)

    @lru_cache(maxsize=128)
    def _analyze_dependencies(self, target: Union[Type, Callable]) -> List[Type]:
        """Analyze dependencies of a class or function."""
        dependencies = []

        try:
            # Get constructor or function signature
            if inspect.isclass(target):
                sig = inspect.signature(target.__init__)
                type_hints = get_type_hints(target.__init__)
            else:
                sig = inspect.signature(target)
                type_hints = get_type_hints(target)

            for param_name, param in sig.parameters.items():
                # Skip self parameter
                if param_name == "self":
                    continue

                # Get parameter type
                if param_name in type_hints:
                    param_type = type_hints[param_name]

                    # Handle generic types
                    origin = get_origin(param_type)
                    if origin is not None:
                        param_type = origin

                    dependencies.append(param_type)

        except Exception:
            # If analysis fails, return empty list

            pass
        return dependencies


# Lifecycle management decorators
def Singleton(cls: Type[T]) -> Type[T]:
    """Decorator to mark a class as singleton."""
    cls._lifetime = ServiceLifetime.SINGLETON
    return cls


def Transient(cls: Type[T]) -> Type[T]:
    """Decorator to mark a class as transient."""
    cls._lifetime = ServiceLifetime.TRANSIENT
    return cls


def Scoped(cls: Type[T]) -> Type[T]:
    """Decorator to mark a class as scoped."""
    cls._lifetime = ServiceLifetime.SCOPED
    return cls
    return cls


def inject(container: Container):
    """Decorator for automatic dependency injection."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get type hints
            type_hints = get_type_hints(func)
            sig = inspect.signature(func)

            # Inject dependencies
            for param_name, param in sig.parameters.items():
                if param_name in type_hints and param_name not in kwargs:
                    param_type = type_hints[param_name]

                    try:
                        kwargs[param_name] = container.resolve(param_type)
                    except ContainerError:
                        # Use default if available
                        if param.default is not param.empty:
                            kwargs[param_name] = param.default

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Global container instance
_global_container = Container()


def get_container() -> Container:
    """Get the global container instance."""
    return _global_container


def configure_container(config_func: Callable[[Container], None]) -> None:
    """Configure the global container."""
    config_func(_global_container)
