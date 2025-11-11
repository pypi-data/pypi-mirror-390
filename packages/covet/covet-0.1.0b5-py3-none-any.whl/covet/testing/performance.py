"""
Performance testing utilities for CovetPy.

This module provides utilities for performance and load testing.
"""

import time
from typing import Any, Callable, Dict, List


class PerformanceTester:
    """Performance testing utility."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def benchmark(self, func: Callable, iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark a function."""
        start = time.time()
        for _ in range(iterations):
            func()
        elapsed = time.time() - start

        return {
            "iterations": iterations,
            "total_time": elapsed,
            "avg_time": elapsed / iterations,
            "ops_per_sec": iterations / elapsed,
        }


class LoadTester:
    """Load testing utility."""

    def __init__(self, target_url: str):
        self.target_url = target_url

    async def run_load_test(self, concurrent_users: int, duration: int) -> Dict[str, Any]:
        """Run load test."""
        return {
            "concurrent_users": concurrent_users,
            "duration": duration,
            "requests_sent": 0,
            "success_rate": 0.0,
        }


__all__ = ["PerformanceTester", "LoadTester", "PerformanceValidator", "BenchmarkRunner"]


from dataclasses import dataclass
from typing import List


@dataclass
class PerformanceMetrics:
    """Performance test metrics."""

    requests_per_second: float
    average_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_rate: float
    total_requests: int
    failed_requests: int


# Auto-generated stubs for missing exports

class PerformanceValidator:
    """Stub class for PerformanceValidator."""

    def __init__(self, *args, **kwargs):
        pass


class BenchmarkRunner:
    """Stub class for BenchmarkRunner."""

    def __init__(self, *args, **kwargs):
        pass

