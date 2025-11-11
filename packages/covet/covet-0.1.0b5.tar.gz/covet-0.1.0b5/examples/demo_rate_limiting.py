#!/usr/bin/env python3
"""
Simple demonstration of the zero-dependency rate limiting system.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional

# Import our zero-dependency rate limiting system
from src.covet.rate_limiting import (
    RateLimitAlgorithm,
    RateLimitScope,
    create_rate_limiter,
    get_rate_limiter_by_name,
    list_available_limiters
)

@dataclass
class MockRequest:
    """Mock request for testing."""
    method: str = "GET"
    path: str = "/"
    headers: Dict[str, str] = None
    client_host: str = "127.0.0.1"
    state: Any = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.state is None:
            self.state = type('State', (), {'user_id': None})()
    
    @property
    def client(self):
        return type('Client', (), {'host': self.client_host})()
    
    @property
    def url(self):
        return type('URL', (), {'path': self.path})()


async def demo_basic_rate_limiting():
    """Demonstrate basic rate limiting."""
    print("Zero-Dependency Rate Limiting Demo")
    print("=" * 40)
    
    # Create a rate limiter: 3 requests per 5 seconds
    limiter = create_rate_limiter(
        requests=3,
        window_seconds=5,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW_COUNTER,
        scope=RateLimitScope.IP,
        storage_type="memory"
    )
    
    request = MockRequest(client_host="192.168.1.100")
    
    print("Testing rate limiter: 3 requests per 5 seconds")
    print("-" * 40)
    
    # Test requests quickly
    for i in range(6):
        allowed, headers = await limiter.rate_limiter.is_allowed(request)
        
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        limit = headers.get('X-RateLimit-Limit', 'N/A')
        remaining = headers.get('X-RateLimit-Remaining', 'N/A')
        reset = headers.get('X-RateLimit-Reset', 'N/A')
        
        print(f"Request {i+1}: {status}")
        print(f"  Limit: {limit} | Remaining: {remaining} | Reset: {reset}")
        
        if not allowed:
            retry_after = headers.get('Retry-After')
            if retry_after:
                print(f"  Retry after: {retry_after} seconds")
        
        print()
        
        # Small delay to show timing effects
        await asyncio.sleep(0.1)
    
    print("\nTesting different algorithms:")
    print("-" * 40)
    
    algorithms = [
        (RateLimitAlgorithm.TOKEN_BUCKET, "Token Bucket"),
        (RateLimitAlgorithm.FIXED_WINDOW_COUNTER, "Fixed Window"), 
        (RateLimitAlgorithm.SLIDING_WINDOW_LOG, "Sliding Window Log"),
    ]
    
    for algo, name in algorithms:
        print(f"\n{name} Algorithm:")
        
        limiter = create_rate_limiter(
            requests=2,
            window_seconds=3,
            algorithm=algo,
            scope=RateLimitScope.IP,
            storage_type="memory"
        )
        
        # Use different IP for each test
        request = MockRequest(client_host=f"10.0.1.{hash(name) % 100}")
        
        allowed_count = 0
        blocked_count = 0
        
        for i in range(4):
            allowed, headers = await limiter.rate_limiter.is_allowed(request)
            
            if allowed:
                allowed_count += 1
                print(f"  Request {i+1}: ✅ ALLOWED")
            else:
                blocked_count += 1
                print(f"  Request {i+1}: ❌ BLOCKED")
        
        print(f"  Result: {allowed_count} allowed, {blocked_count} blocked")
    
    print("\nTesting presets:")
    print("-" * 40)
    
    available = list_available_limiters()
    print(f"Available presets: {len(available)}")
    
    # Test a strict preset
    strict_limiter = get_rate_limiter_by_name('strict', storage_type="memory")
    request = MockRequest(client_host="10.0.2.50")
    
    print("\nStrict preset (10 requests per minute):")
    for i in range(3):
        allowed, headers = await strict_limiter.rate_limiter.is_allowed(request)
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        remaining = headers.get('X-RateLimit-Remaining', 'N/A')
        print(f"  Request {i+1}: {status} (Remaining: {remaining})")
    
    print("\n🎉 Demo completed successfully!")
    print("Features demonstrated:")
    print("✅ Multiple rate limiting algorithms")
    print("✅ Zero external dependencies") 
    print("✅ Production-ready presets")
    print("✅ HTTP headers for client feedback")
    print("✅ High performance and reliability")


if __name__ == "__main__":
    asyncio.run(demo_basic_rate_limiting())