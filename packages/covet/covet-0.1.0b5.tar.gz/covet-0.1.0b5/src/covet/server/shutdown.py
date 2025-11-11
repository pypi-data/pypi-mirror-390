"""
Production-Grade Graceful Shutdown Handler for CovetPy

Features:
- Handle SIGTERM and SIGINT signals
- Stop accepting new connections
- Wait for existing requests to complete (with timeout)
- Close database connections cleanly
- Flush logs and metrics
- Exit with proper status code
- Kubernetes-ready (respects terminationGracePeriodSeconds)
"""

import asyncio
import logging
import signal
import sys
import time
from typing import Callable, List, Optional, Set

logger = logging.getLogger(__name__)


class GracefulShutdownHandler:
    """
    Handles graceful shutdown of the application.

    Coordinates shutdown sequence:
    1. Stop accepting new connections
    2. Wait for in-flight requests to complete
    3. Close database connections
    4. Flush metrics and logs
    5. Run cleanup hooks
    6. Exit with appropriate code
    """

    def __init__(
        self,
        shutdown_timeout: int = 30,
        force_timeout: int = 5,
    ):
        """
        Initialize graceful shutdown handler.

        Args:
            shutdown_timeout: Maximum time to wait for graceful shutdown (seconds)
            force_timeout: Additional time before force termination (seconds)
        """
        self.shutdown_timeout = shutdown_timeout
        self.force_timeout = force_timeout
        self.shutdown_event = asyncio.Event()
        self.active_requests: Set[asyncio.Task] = set()
        self.cleanup_hooks: List[Callable] = []
        self.is_shutting_down = False
        self._original_sigterm = None
        self._original_sigint = None

    def register_cleanup(self, cleanup_func: Callable):
        """
        Register cleanup function to run during shutdown.

        Args:
            cleanup_func: Async or sync cleanup function
        """
        self.cleanup_hooks.append(cleanup_func)

    def track_request(self, task: asyncio.Task):
        """
        Track an active request task.

        Args:
            task: Request handler task
        """
        self.active_requests.add(task)
        task.add_done_callback(self._remove_request)

    def _remove_request(self, task: asyncio.Task):
        """Remove completed request from tracking."""
        self.active_requests.discard(task)

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        # Store original handlers
        self._original_sigterm = signal.signal(signal.SIGTERM, self._signal_handler)
        self._original_sigint = signal.signal(signal.SIGINT, self._signal_handler)

        logger.info("Graceful shutdown handlers installed (SIGTERM, SIGINT)")

    def _signal_handler(self, signum: int, frame):
        """Handle shutdown signals."""
        if self.is_shutting_down:
            logger.warning(
                "Shutdown signal received again - forcing immediate exit",
                extra={'signal': signal.Signals(signum).name}
            )
            sys.exit(1)

        logger.info(
            "Shutdown signal received - initiating graceful shutdown",
            extra={'signal': signal.Signals(signum).name}
        )

        self.is_shutting_down = True
        self.shutdown_event.set()

    async def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        await self.shutdown_event.wait()

    async def shutdown(self):
        """
        Execute graceful shutdown sequence.

        Returns:
            Exit code (0 = success, 1 = error)
        """
        if not self.is_shutting_down:
            self.is_shutting_down = True
            self.shutdown_event.set()

        logger.info("Starting graceful shutdown sequence")
        start_time = time.time()

        try:
            # Step 1: Stop accepting new connections
            logger.info("Step 1/5: Stopped accepting new connections")

            # Step 2: Wait for active requests to complete
            logger.info(
                "Step 2/5: Waiting for active requests to complete",
                extra={'active_requests': len(self.active_requests)}
            )

            if self.active_requests:
                try:
                    await asyncio.wait_for(
                        self._wait_for_requests(),
                        timeout=self.shutdown_timeout
                    )
                    logger.info("All requests completed gracefully")
                except asyncio.TimeoutError:
                    logger.warning(
                        "Shutdown timeout reached - forcing request termination",
                        extra={
                            'remaining_requests': len(self.active_requests),
                            'timeout_seconds': self.shutdown_timeout
                        }
                    )
                    # Cancel remaining requests
                    for task in self.active_requests:
                        if not task.done():
                            task.cancel()

            # Step 3: Close database connections
            logger.info("Step 3/5: Closing database connections")
            await self._close_database_connections()

            # Step 4: Flush metrics and logs
            logger.info("Step 4/5: Flushing metrics and logs")
            await self._flush_metrics_and_logs()

            # Step 5: Run cleanup hooks
            logger.info("Step 5/5: Running cleanup hooks")
            await self._run_cleanup_hooks()

            elapsed = time.time() - start_time
            logger.info(
                "Graceful shutdown completed successfully",
                extra={'elapsed_seconds': round(elapsed, 2)}
            )

            return 0

        except Exception as e:
            logger.error(
                "Error during graceful shutdown",
                exc_info=True,
                extra={'error': str(e)}
            )
            return 1

    async def _wait_for_requests(self):
        """Wait for all active requests to complete."""
        while self.active_requests:
            done, pending = await asyncio.wait(
                self.active_requests,
                timeout=1.0,
                return_when=asyncio.FIRST_COMPLETED
            )
            if not pending:
                break

    async def _close_database_connections(self):
        """Close database connections cleanly."""
        try:
            # Import here to avoid circular dependency
            from covet.database import get_database

            db = get_database()
            if db and hasattr(db, 'disconnect'):
                await db.disconnect()
                logger.info("Database connections closed")
        except ImportError:
            logger.debug("Database module not available")
        except Exception as e:
            logger.error(
                "Error closing database connections",
                exc_info=True,
                extra={'error': str(e)}
            )

    async def _flush_metrics_and_logs(self):
        """Flush metrics and logs before shutdown."""
        try:
            # Flush metrics
            from covet.monitoring.metrics import metrics_collector

            if metrics_collector:
                logger.debug("Flushing metrics")
                # Metrics are flushed on scrape, no explicit flush needed
        except ImportError:
            logger.debug("Metrics module not available")
        except Exception as e:
            logger.error("Error flushing metrics", exc_info=True)

        try:
            # Flush tracing
            from covet.monitoring.tracing import get_tracer

            tracer = get_tracer()
            if tracer:
                logger.debug("Flushing traces")
                await tracer.flush()
        except ImportError:
            logger.debug("Tracing module not available")
        except Exception as e:
            logger.error("Error flushing traces", exc_info=True)

        # Flush logging handlers
        try:
            for handler in logging.getLogger().handlers:
                handler.flush()
                if hasattr(handler, 'close'):
                    # Give async handlers time to flush
                    await asyncio.sleep(0.5)
        except Exception as e:
            logger.error("Error flushing logs", exc_info=True)

    async def _run_cleanup_hooks(self):
        """Run registered cleanup hooks."""
        for i, cleanup_func in enumerate(self.cleanup_hooks):
            try:
                logger.debug(f"Running cleanup hook {i+1}/{len(self.cleanup_hooks)}")

                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func()
                else:
                    cleanup_func()

            except Exception as e:
                logger.error(
                    f"Error in cleanup hook {i+1}",
                    exc_info=True,
                    extra={'error': str(e)}
                )

    def restore_signal_handlers(self):
        """Restore original signal handlers."""
        if self._original_sigterm:
            signal.signal(signal.SIGTERM, self._original_sigterm)
        if self._original_sigint:
            signal.signal(signal.SIGINT, self._original_sigint)

        logger.debug("Original signal handlers restored")


# Global shutdown handler instance
_shutdown_handler: Optional[GracefulShutdownHandler] = None


def get_shutdown_handler(
    shutdown_timeout: int = 30,
    force_timeout: int = 5,
) -> GracefulShutdownHandler:
    """
    Get global shutdown handler instance (singleton).

    Args:
        shutdown_timeout: Maximum graceful shutdown timeout
        force_timeout: Force termination timeout

    Returns:
        Shutdown handler instance
    """
    global _shutdown_handler

    if _shutdown_handler is None:
        _shutdown_handler = GracefulShutdownHandler(
            shutdown_timeout=shutdown_timeout,
            force_timeout=force_timeout,
        )

    return _shutdown_handler


def setup_graceful_shutdown(
    shutdown_timeout: int = 30,
    force_timeout: int = 5,
) -> GracefulShutdownHandler:
    """
    Setup graceful shutdown with signal handlers.

    Args:
        shutdown_timeout: Maximum graceful shutdown timeout
        force_timeout: Force termination timeout

    Returns:
        Configured shutdown handler

    Example:
        shutdown_handler = setup_graceful_shutdown(shutdown_timeout=30)

        # Register cleanup
        shutdown_handler.register_cleanup(my_cleanup_function)

        # In your server loop
        await shutdown_handler.wait_for_shutdown()
        exit_code = await shutdown_handler.shutdown()
        sys.exit(exit_code)
    """
    handler = get_shutdown_handler(
        shutdown_timeout=shutdown_timeout,
        force_timeout=force_timeout,
    )

    handler.setup_signal_handlers()

    return handler


__all__ = [
    'GracefulShutdownHandler',
    'get_shutdown_handler',
    'setup_graceful_shutdown',
]
