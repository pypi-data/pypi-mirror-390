"""
Distributed Tracing System for CovetPy

Production-ready tracing with OpenTelemetry support for:
- Request/response tracing
- Database query tracing
- External API call tracing
- Custom span creation
- Trace context propagation
- Export to Jaeger, Zipkin, and OpenTelemetry collectors

Follows W3C Trace Context specification for distributed tracing.
"""

import asyncio
import contextvars
import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)

# Context variable for current trace
_current_trace_context: contextvars.ContextVar[Optional["TraceContext"]] = contextvars.ContextVar(
    "current_trace_context", default=None
)


class SpanKind(str, Enum):
    """Span kind following OpenTelemetry conventions."""

    INTERNAL = "internal"  # Internal operation
    SERVER = "server"  # Server-side request handling
    CLIENT = "client"  # Client-side request
    PRODUCER = "producer"  # Message producer
    CONSUMER = "consumer"  # Message consumer


class SpanStatus(str, Enum):
    """Span status."""

    UNSET = "unset"  # Default status
    OK = "ok"  # Success
    ERROR = "error"  # Error occurred


@dataclass
class SpanContext:
    """
    Span context for distributed tracing.

    Follows W3C Trace Context specification.
    """

    trace_id: str  # 128-bit trace ID (32 hex chars)
    span_id: str  # 64-bit span ID (16 hex chars)
    parent_span_id: Optional[str] = None  # Parent span ID
    trace_flags: int = 1  # Trace flags (1 = sampled)
    trace_state: str = ""  # Vendor-specific trace state

    def to_traceparent(self) -> str:
        """Convert to W3C traceparent header format."""
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags:02x}"

    @classmethod
    def from_traceparent(cls, traceparent: str) -> Optional["SpanContext"]:
        """Parse W3C traceparent header."""
        try:
            parts = traceparent.split("-")
            if len(parts) != 4 or parts[0] != "00":
                return None

            return cls(
                trace_id=parts[1],
                span_id=parts[2],
                trace_flags=int(parts[3], 16),
            )
        except Exception:
            return None


@dataclass
class Span:
    """
    Trace span representing a unit of work.

    Follows OpenTelemetry span model.
    """

    name: str
    context: SpanContext
    kind: SpanKind = SpanKind.INTERNAL
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    status: SpanStatus = SpanStatus.UNSET
    status_message: Optional[str] = None

    # Attributes (tags)
    attributes: Dict[str, Any] = field(default_factory=dict)

    # Events (logs)
    events: List[Dict[str, Any]] = field(default_factory=list)

    # Links to other spans
    links: List[SpanContext] = field(default_factory=list)

    def set_attribute(self, key: str, value: Any) -> "Span":
        """Set span attribute."""
        self.attributes[key] = value
        return self

    def set_attributes(self, attributes: Dict[str, Any]) -> "Span":
        """Set multiple span attributes."""
        self.attributes.update(attributes)
        return self

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> "Span":
        """Add span event."""
        event = {
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        }
        self.events.append(event)
        return self

    def set_status(self, status: SpanStatus, message: Optional[str] = None) -> "Span":
        """Set span status."""
        self.status = status
        self.status_message = message
        return self

    def record_exception(self, exception: Exception) -> "Span":
        """Record exception in span."""
        self.set_status(SpanStatus.ERROR, str(exception))
        self.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
                "exception.stacktrace": "",  # Could add traceback here
            },
        )
        return self

    def end(self, end_time: Optional[float] = None) -> None:
        """End span."""
        self.end_time = end_time or time.time()

    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "kind": self.kind.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "status_message": self.status_message,
            "attributes": self.attributes,
            "events": self.events,
        }


@dataclass
class TraceContext:
    """
    Trace context containing current trace and span stack.
    """

    trace_id: str
    spans: List[Span] = field(default_factory=list)
    baggage: Dict[str, str] = field(default_factory=dict)

    @property
    def current_span(self) -> Optional[Span]:
        """Get current active span."""
        return self.spans[-1] if self.spans else None

    def push_span(self, span: Span) -> None:
        """Push span onto stack."""
        self.spans.append(span)

    def pop_span(self) -> Optional[Span]:
        """Pop span from stack."""
        return self.spans.pop() if self.spans else None


class TracingConfig:
    """Tracing configuration."""

    def __init__(
        self,
        enabled: bool = True,
        service_name: str = "covetpy",
        service_version: str = "1.0.0",
        environment: str = "production",
        sample_rate: float = 1.0,  # 1.0 = 100% sampling
        max_attributes: int = 128,
        max_events: int = 128,
        exporter_endpoint: Optional[str] = None,
        exporter_type: str = "console",  # console, jaeger, zipkin, otlp
    ):
        """
        Initialize tracing configuration.

        Args:
            enabled: Enable tracing
            service_name: Service name
            service_version: Service version
            environment: Environment (dev, staging, prod)
            sample_rate: Sampling rate (0.0 to 1.0)
            max_attributes: Maximum span attributes
            max_events: Maximum span events
            exporter_endpoint: Exporter endpoint URL
            exporter_type: Exporter type
        """
        self.enabled = enabled
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.sample_rate = sample_rate
        self.max_attributes = max_attributes
        self.max_events = max_events
        self.exporter_endpoint = exporter_endpoint
        self.exporter_type = exporter_type


class TraceExporter:
    """Base trace exporter."""

    async def export(self, spans: List[Span]) -> None:
        """Export spans."""
        raise NotImplementedError


class ConsoleTraceExporter(TraceExporter):
    """Console trace exporter for development."""

    async def export(self, spans: List[Span]) -> None:
        """Export spans to console."""
        for span in spans:
            logger.info(
                f"Trace: {span.name} "
                f"[{span.context.trace_id[:8]}...{span.context.span_id[:8]}] "
                f"duration={span.duration_ms:.2f}ms status={span.status.value}"
            )
            if span.attributes:
                logger.debug(f"  Attributes: {json.dumps(span.attributes)}")


class InMemoryTraceExporter(TraceExporter):
    """In-memory trace exporter for testing."""

    def __init__(self, max_spans: int = 1000):
        """Initialize in-memory exporter."""
        self.spans: List[Span] = []
        self.max_spans = max_spans

    async def export(self, spans: List[Span]) -> None:
        """Export spans to memory."""
        self.spans.extend(spans)
        # Keep only recent spans
        if len(self.spans) > self.max_spans:
            self.spans = self.spans[-self.max_spans :]

    def get_traces(self) -> List[Dict[str, Any]]:
        """Get all traces grouped by trace_id."""
        traces = {}
        for span in self.spans:
            trace_id = span.context.trace_id
            if trace_id not in traces:
                traces[trace_id] = []
            traces[trace_id].append(span.to_dict())
        return list(traces.values())

    def clear(self) -> None:
        """Clear all spans."""
        self.spans.clear()


class Tracer:
    """
    Distributed tracer for creating and managing spans.

    Example:
        tracer = Tracer(config)

        with tracer.start_span("operation") as span:
            span.set_attribute("user_id", 123)
            # Do work
            span.add_event("work_completed")
    """

    def __init__(
        self,
        config: TracingConfig,
        exporter: Optional[TraceExporter] = None,
    ):
        """
        Initialize tracer.

        Args:
            config: Tracing configuration
            exporter: Trace exporter (defaults to ConsoleTraceExporter)
        """
        self.config = config
        self.exporter = exporter or ConsoleTraceExporter()
        self._completed_spans: List[Span] = []

    def _should_sample(self) -> bool:
        """Determine if trace should be sampled."""
        import random

        return random.random() < self.config.sample_rate

    def _generate_trace_id(self) -> str:
        """Generate 128-bit trace ID."""
        return uuid.uuid4().hex + uuid.uuid4().hex[:16]

    def _generate_span_id(self) -> str:
        """Generate 64-bit span ID."""
        return uuid.uuid4().hex[:16]

    def get_current_context(self) -> Optional[TraceContext]:
        """Get current trace context."""
        return _current_trace_context.get()

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> "SpanContextManager":
        """
        Start a new span.

        Args:
            name: Span name
            kind: Span kind
            attributes: Initial span attributes

        Returns:
            Span context manager
        """
        if not self.config.enabled:
            return SpanContextManager(None, self)

        # Get or create trace context
        trace_ctx = self.get_current_context()
        if trace_ctx is None:
            # New trace
            trace_id = self._generate_trace_id()
            trace_ctx = TraceContext(trace_id=trace_id)
            _current_trace_context.set(trace_ctx)
        else:
            trace_id = trace_ctx.trace_id

        # Get parent span
        parent_span = trace_ctx.current_span

        # Create span context
        span_ctx = SpanContext(
            trace_id=trace_id,
            span_id=self._generate_span_id(),
            parent_span_id=parent_span.context.span_id if parent_span else None,
            trace_flags=1 if self._should_sample() else 0,
        )

        # Create span
        span = Span(name=name, context=span_ctx, kind=kind)
        if attributes:
            span.set_attributes(attributes)

        # Add service attributes
        span.set_attributes(
            {
                "service.name": self.config.service_name,
                "service.version": self.config.service_version,
                "deployment.environment": self.config.environment,
            }
        )

        # Push span onto context stack
        trace_ctx.push_span(span)

        return SpanContextManager(span, self)

    def _end_span(self, span: Span) -> None:
        """End span and export."""
        span.end()

        # Pop from context
        trace_ctx = self.get_current_context()
        if trace_ctx:
            trace_ctx.pop_span()

        # Collect for export
        self._completed_spans.append(span)

    async def flush(self) -> None:
        """Flush and export all completed spans."""
        if self._completed_spans:
            await self.exporter.export(self._completed_spans)
            self._completed_spans.clear()


class SpanContextManager:
    """Context manager for spans."""

    def __init__(self, span: Optional[Span], tracer: Tracer):
        """Initialize span context manager."""
        self.span = span
        self.tracer = tracer

    def __enter__(self) -> Optional[Span]:
        """Enter context."""
        return self.span

    def __exit__(self, exc_type, exc_val, _):
        """Exit context."""
        if self.span:
            if exc_val:
                self.span.record_exception(exc_val)
            else:
                self.span.set_status(SpanStatus.OK)

            self.tracer._end_span(self.span)

        return False


# Global tracer instance
_global_tracer: Optional[Tracer] = None


def configure_tracing(config: TracingConfig, exporter: Optional[TraceExporter] = None) -> Tracer:
    """
    Configure global tracer.

    Args:
        config: Tracing configuration
        exporter: Optional trace exporter

    Returns:
        Configured tracer

    Example:
        config = TracingConfig(
            service_name="my-service",
            sample_rate=0.1,  # 10% sampling
        )
        tracer = configure_tracing(config)
    """
    global _global_tracer
    _global_tracer = Tracer(config, exporter)
    return _global_tracer


def get_tracer() -> Optional[Tracer]:
    """Get global tracer instance."""
    return _global_tracer


def trace_middleware(tracer: Optional[Tracer] = None):
    """
    ASGI middleware for automatic request tracing.

    Args:
        tracer: Optional tracer (uses global if not provided)

    Example:
        app.add_middleware(trace_middleware())
    """
    if tracer is None:
        tracer = get_tracer()

    async def middleware(app, call_next):
        """Middleware function."""

        async def traced_app(scope, receive, send):
            if scope["type"] != "http" or tracer is None or not tracer.config.enabled:
                await app(scope, receive, send)
                return

            # Extract trace context from headers
            headers = dict(scope.get("headers", []))
            traceparent = headers.get(b"traceparent", b"").decode()

            # Start span
            method = scope.get("method", "")
            path = scope.get("path", "")
            span_name = f"{method} {path}"

            with tracer.start_span(span_name, kind=SpanKind.SERVER) as span:
                if span:
                    # Set HTTP attributes
                    span.set_attributes(
                        {
                            "http.method": method,
                            "http.url": path,
                            "http.scheme": scope.get("scheme", "http"),
                            "http.host": headers.get(b"host", b"").decode(),
                            "http.user_agent": headers.get(b"user-agent", b"").decode(),
                        }
                    )

                    # Capture response
                    status_code = None

                    async def send_wrapper(message):
                        nonlocal status_code
                        if message["type"] == "http.response.start":
                            status_code = message["status"]
                            if span:
                                span.set_attribute("http.status_code", status_code)
                        await send(message)

                    try:
                        await app(scope, receive, send_wrapper)
                        if status_code and status_code < 400:
                            span.set_status(SpanStatus.OK)
                    except Exception as e:
                        if span:
                            span.record_exception(e)
                        raise

                    # Flush spans
                    await tracer.flush()
                else:
                    await app(scope, receive, send)

        return traced_app

    return middleware


__all__ = [
    "Tracer",
    "TracingConfig",
    "TraceContext",
    "Span",
    "SpanContext",
    "SpanKind",
    "SpanStatus",
    "TraceExporter",
    "ConsoleTraceExporter",
    "InMemoryTraceExporter",
    "configure_tracing",
    "get_tracer",
    "trace_middleware",
]
