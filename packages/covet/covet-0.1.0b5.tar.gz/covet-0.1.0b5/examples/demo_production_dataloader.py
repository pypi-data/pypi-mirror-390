#!/usr/bin/env python3
"""
Production DataLoader Demonstration

This demo showcases the production-ready DataLoader implementation for CovetPy's GraphQL,
demonstrating real-world scenarios including e-commerce APIs, social networks, and
enterprise applications.
"""

import asyncio
import time
import sys
import os
import json
import random
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from covet.api.graphql.dataloader_production import (
    DataLoader,
    DataLoaderRegistry,
    GraphQLDataLoaderContext,
    create_simple_loader,
    create_database_loader
)


class SimulatedDatabase:
    """Simulated database for realistic testing."""
    
    def __init__(self):
        # Generate realistic test data
        self.users = {
            i: {
                'id': i,
                'name': f'User {i}',
                'email': f'user{i}@company.com',
                'department': random.choice(['Engineering', 'Sales', 'Marketing', 'Support']),
                'created_at': f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}'
            }
            for i in range(1, 101)
        }
        
        self.products = {
            i: {
                'id': i,
                'name': f'Product {i}',
                'price': round(random.uniform(10, 1000), 2),
                'category': random.choice(['Electronics', 'Clothing', 'Books', 'Home']),
                'stock': random.randint(0, 100)
            }
            for i in range(1, 201)
        }
        
        self.orders = {
            i: {
                'id': i,
                'user_id': random.randint(1, 100),
                'product_id': random.randint(1, 200),
                'quantity': random.randint(1, 5),
                'status': random.choice(['pending', 'confirmed', 'shipped', 'delivered']),
                'created_at': f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}'
            }
            for i in range(1, 501)
        }
        
        self.reviews = {
            i: {
                'id': i,
                'user_id': random.randint(1, 100),
                'product_id': random.randint(1, 200),
                'rating': random.randint(1, 5),
                'comment': f'Review comment {i}',
                'created_at': f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}'
            }
            for i in range(1, 1001)
        }
        
        self.query_count = 0
    
    async def execute_query(self, table: str, key_column: str, keys: List[Any]) -> List[Dict[str, Any]]:
        """Simulate database query with realistic latency."""
        self.query_count += 1
        
        # Simulate network/DB latency
        latency = random.uniform(0.01, 0.05)  # 10-50ms
        await asyncio.sleep(latency)
        
        # Get data from appropriate table
        data_source = getattr(self, table)
        
        # Return matching records
        results = []
        for key in keys:
            if key in data_source:
                results.append(data_source[key])
            else:
                results.append(None)
        
        return results


async def demo_basic_functionality():
    """Demonstrate basic DataLoader functionality."""
    print("🚀 Demo 1: Basic DataLoader Functionality")
    print("=" * 50)
    
    db = SimulatedDatabase()
    
    # Create user loader
    async def batch_load_users(user_ids: List[int]) -> List[Dict[str, Any]]:
        print(f"  📊 DB Query: Loading {len(user_ids)} users")
        return await db.execute_query('users', 'id', user_ids)
    
    user_loader = DataLoader(
        batch_load_users,
        batch_size=10,
        cache=True,
        name="users"
    )
    
    print("Loading individual users...")
    
    # Load individual users
    start = time.time()
    user1 = await user_loader.load(1)
    user2 = await user_loader.load(2)
    user3 = await user_loader.load(1)  # Should hit cache
    duration = time.time() - start
    
    print(f"✅ Loaded 3 users in {duration:.3f}s")
    print(f"   User 1: {user1['name']} ({user1['email']})")
    print(f"   User 2: {user2['name']} ({user2['email']})")
    print(f"   User 3 (cached): {user3['name']} ({user3['email']})")
    
    # Show statistics
    stats = user_loader.get_stats()
    print(f"📈 Cache hits: {stats['cache_hits']}, Cache misses: {stats['cache_misses']}")
    print(f"📈 Hit rate: {stats['cache_hit_rate']}")
    
    print()


async def demo_n_plus_one_prevention():
    """Demonstrate N+1 query prevention in realistic scenario."""
    print("🛡️  Demo 2: N+1 Query Prevention - E-commerce Orders")
    print("=" * 50)
    
    db = SimulatedDatabase()
    
    # Create loaders for different entities
    async def batch_load_users(user_ids: List[int]) -> List[Dict[str, Any]]:
        print(f"  📊 DB Query: Loading {len(user_ids)} users")
        return await db.execute_query('users', 'id', user_ids)
    
    async def batch_load_products(product_ids: List[int]) -> List[Dict[str, Any]]:
        print(f"  📊 DB Query: Loading {len(product_ids)} products")  
        return await db.execute_query('products', 'id', product_ids)
    
    async def batch_load_orders(order_ids: List[int]) -> List[Dict[str, Any]]:
        print(f"  📊 DB Query: Loading {len(order_ids)} orders")
        return await db.execute_query('orders', 'id', order_ids)
    
    # Create DataLoaders
    user_loader = DataLoader(batch_load_users, name="users", cache=True)
    product_loader = DataLoader(batch_load_products, name="products", cache=True)
    order_loader = DataLoader(batch_load_orders, name="orders", cache=True)
    
    print("Scenario: Loading 20 orders with customer and product details")
    print("(This would normally be 1 + 20 + 20 = 41 database queries)")
    
    start_time = time.time()
    start_queries = db.query_count
    
    # Load orders
    order_ids = list(range(1, 21))
    orders = await order_loader.load_many(order_ids)
    
    # Load customers for each order (potential N+1)
    customer_tasks = [user_loader.load(order['user_id']) for order in orders if order]
    customers = await asyncio.gather(*customer_tasks)
    
    # Load products for each order (another potential N+1)  
    product_tasks = [product_loader.load(order['product_id']) for order in orders if order]
    products = await asyncio.gather(*product_tasks)
    
    # Combine data
    enriched_orders = []
    for order, customer, product in zip(orders, customers, products):
        if order and customer and product:
            enriched_orders.append({
                'order_id': order['id'],
                'customer': customer['name'],
                'product': product['name'],
                'quantity': order['quantity'],
                'total_price': product['price'] * order['quantity'],
                'status': order['status']
            })
    
    duration = time.time() - start_time
    queries_used = db.query_count - start_queries
    
    print(f"✅ Processed {len(enriched_orders)} orders in {duration:.3f}s")
    print(f"📊 Database queries used: {queries_used} (instead of 41)")
    print(f"🚀 Efficiency improvement: {41/queries_used:.1f}x")
    
    # Show sample results
    if enriched_orders:
        print(f"\n📋 Sample Order:")
        sample = enriched_orders[0]
        print(f"   Order #{sample['order_id']}: {sample['customer']} ordered {sample['quantity']}x {sample['product']}")
        print(f"   Total: ${sample['total_price']:.2f} - Status: {sample['status']}")
    
    # Show loader statistics
    print(f"\n📈 Loader Performance:")
    for name, loader in [("Users", user_loader), ("Products", product_loader), ("Orders", order_loader)]:
        stats = loader.get_stats()
        print(f"   {name}: {stats['total_requests']} requests, {stats['batches_executed']} batches, {stats['cache_hit_rate']} hit rate")
    
    print()


async def demo_advanced_features():
    """Demonstrate advanced DataLoader features."""
    print("⚡ Demo 3: Advanced Features - Caching, Retry, Deduplication")
    print("=" * 50)
    
    db = SimulatedDatabase()
    
    # Simulate unreliable service
    failure_count = 0
    
    async def unreliable_batch_load(ids: List[int]) -> List[Dict[str, Any]]:
        nonlocal failure_count
        failure_count += 1
        
        # Fail first 2 attempts
        if failure_count <= 2:
            print(f"  ❌ Simulated failure #{failure_count}")
            raise Exception(f"Simulated network error #{failure_count}")
        
        print(f"  ✅ Success on attempt #{failure_count}")
        return await db.execute_query('users', 'id', ids)
    
    # Create loader with retry logic
    retry_loader = DataLoader(
        unreliable_batch_load,
        retry_attempts=3,
        retry_delay=0.1,
        name="retry_demo"
    )
    
    print("Testing retry logic with unreliable service...")
    
    try:
        start = time.time()
        user = await retry_loader.load(1)
        duration = time.time() - start
        
        print(f"✅ Successfully loaded user after retries: {user['name']}")
        print(f"⏱️  Total time with retries: {duration:.3f}s")
        
        stats = retry_loader.get_stats()
        print(f"📈 Retries performed: {stats['retries']}")
        
    except Exception as e:
        print(f"❌ Failed after all retries: {e}")
    
    # Test deduplication
    print("\nTesting request deduplication...")
    
    async def tracked_batch_load(ids: List[int]) -> List[Dict[str, Any]]:
        print(f"  📊 Batch function called with {len(ids)} unique IDs: {ids}")
        return await db.execute_query('users', 'id', ids)
    
    dedup_loader = DataLoader(tracked_batch_load, name="dedup_demo")
    
    # Make duplicate requests simultaneously
    print("Making 10 requests (5 unique IDs, 5 duplicates)...")
    tasks = [
        dedup_loader.load(1),  # First time
        dedup_loader.load(2),  # First time
        dedup_loader.load(1),  # Duplicate
        dedup_loader.load(3),  # First time
        dedup_loader.load(2),  # Duplicate
        dedup_loader.load(1),  # Duplicate
        dedup_loader.load(4),  # First time
        dedup_loader.load(3),  # Duplicate
        dedup_loader.load(5),  # First time
        dedup_loader.load(1),  # Duplicate
    ]
    
    results = await asyncio.gather(*tasks)
    
    print(f"✅ All 10 requests completed")
    
    stats = dedup_loader.get_stats()
    print(f"📈 Duplicate requests detected: {stats['duplicate_requests']}")
    print(f"📈 Unique requests processed: {stats['total_requests'] - stats['duplicate_requests']}")
    
    print()


async def demo_cache_features():
    """Demonstrate advanced caching features."""
    print("💾 Demo 4: Advanced Caching - TTL, LRU, Priming")
    print("=" * 50)
    
    db = SimulatedDatabase()
    
    async def batch_load_products(product_ids: List[int]) -> List[Dict[str, Any]]:
        print(f"  📊 Loading {len(product_ids)} products from database")
        return await db.execute_query('products', 'id', product_ids)
    
    # Create loader with TTL caching
    cache_loader = DataLoader(
        batch_load_products,
        cache=True,
        cache_ttl=2.0,  # 2 second TTL
        cache_max_size=5,  # Small cache for LRU demo
        name="cache_demo"
    )
    
    print("Testing cache TTL expiration...")
    
    # Load product
    product1 = await cache_loader.load(1)
    print(f"✅ Loaded product: {product1['name']} (${product1['price']})")
    
    # Load again (should hit cache)
    product1_cached = await cache_loader.load(1)
    print(f"✅ Loaded from cache: {product1_cached['name']}")
    
    stats = cache_loader.get_stats()
    print(f"📈 Cache hits: {stats['cache_hits']}")
    
    # Wait for TTL expiration
    print("⏳ Waiting for cache TTL to expire...")
    await asyncio.sleep(2.5)
    
    # Load again (should miss cache due to TTL)
    product1_expired = await cache_loader.load(1)
    print(f"✅ Loaded after TTL expiry: {product1_expired['name']}")
    
    stats = cache_loader.get_stats()
    print(f"📈 Cache expirations: {stats['cache_expirations']}")
    
    # Test LRU eviction
    print("\nTesting LRU cache eviction...")
    
    # Fill cache beyond limit
    for i in range(2, 8):  # This will exceed cache_max_size=5
        await cache_loader.load(i)
    
    stats = cache_loader.get_stats()
    print(f"📈 Cache evictions: {stats['cache_evictions']}")
    print(f"📈 Current cache size: {stats['cache_size']}")
    
    # Test cache priming
    print("\nTesting cache priming...")
    
    primed_product = {
        'id': 999,
        'name': 'Primed Product',
        'price': 99.99,
        'category': 'Special'
    }
    
    cache_loader.prime(999, primed_product)
    
    # Load primed product (should not hit database)
    loaded_primed = await cache_loader.load(999)
    print(f"✅ Loaded primed product: {loaded_primed['name']}")
    
    print()


async def demo_registry_and_monitoring():
    """Demonstrate DataLoader registry and monitoring."""
    print("📊 Demo 5: Registry, Health Monitoring & Production Features")
    print("=" * 50)
    
    db = SimulatedDatabase()
    
    # Create registry
    registry = DataLoaderRegistry("production_system")
    
    # Create multiple loaders
    loaders = {}
    
    for entity in ['users', 'products', 'orders', 'reviews']:
        async def make_batch_fn(table_name):
            async def batch_fn(ids: List[int]) -> List[Dict[str, Any]]:
                return await db.execute_query(table_name, 'id', ids)
            return batch_fn
        
        loader = DataLoader(
            await make_batch_fn(entity),
            batch_size=20,
            cache=True,
            cache_ttl=300,  # 5 minutes
            name=f"production_{entity}"
        )
        
        loaders[entity] = loader
        registry.register(entity, loader)
    
    print(f"✅ Created registry with {len(loaders)} loaders")
    
    # Simulate some load
    print("Simulating production load...")
    
    tasks = []
    for _ in range(50):
        # Random operations
        entity = random.choice(list(loaders.keys()))
        loader = loaders[entity]
        item_id = random.randint(1, 100)
        tasks.append(loader.load(item_id))
    
    await asyncio.gather(*tasks)
    
    # Get registry statistics
    all_stats = registry.get_all_stats()
    
    print(f"\n📊 Registry Statistics:")
    print(f"   Registry: {all_stats['registry_name']}")
    print(f"   Uptime: {all_stats['uptime']:.2f}s")
    print(f"   Loaders: {all_stats['loader_count']}")
    
    for name, loader_stats in all_stats['loaders'].items():
        print(f"\n   {name.upper()} Loader:")
        print(f"     Requests: {loader_stats['total_requests']}")
        print(f"     Batches: {loader_stats['batches_executed']}")
        print(f"     Hit Rate: {loader_stats['cache_hit_rate']}")
        print(f"     Efficiency: {loader_stats['efficiency_ratio']}")
    
    # Health check
    health = registry.health_check()
    
    print(f"\n🏥 Health Check:")
    print(f"   Overall Status: {health['status'].upper()}")
    
    for name, loader_health in health['loaders'].items():
        status_emoji = "✅" if loader_health['status'] == 'healthy' else "⚠️"
        print(f"   {status_emoji} {name}: {loader_health['status']} (Hit Rate: {loader_health['cache_hit_rate']})")
    
    print()


async def demo_graphql_context():
    """Demonstrate GraphQL context integration."""
    print("🔄 Demo 6: GraphQL Context Integration")
    print("=" * 50)
    
    db = SimulatedDatabase()
    
    # Create shared registry
    shared_registry = DataLoaderRegistry("shared_loaders")
    
    # Add commonly used loaders to registry
    async def batch_load_users(user_ids: List[int]) -> List[Dict[str, Any]]:
        return await db.execute_query('users', 'id', user_ids)
    
    shared_user_loader = DataLoader(
        batch_load_users,
        cache=True,
        name="shared_users"
    )
    
    shared_registry.register("users", shared_user_loader)
    
    # Simulate GraphQL request context
    async def simulate_graphql_request(request_id: int):
        print(f"🔄 Processing GraphQL Request #{request_id}")
        
        # Create request context
        context = GraphQLDataLoaderContext(shared_registry)
        
        # Add request-specific loaders
        async def batch_load_user_orders(user_ids: List[int]) -> List[List[Dict[str, Any]]]:
            # This would load orders for each user
            all_orders = []
            for user_id in user_ids:
                user_orders = [order for order in db.orders.values() if order['user_id'] == user_id]
                all_orders.append(user_orders[:5])  # Limit to 5 orders per user
            return all_orders
        
        orders_loader = DataLoader(batch_load_user_orders, name=f"user_orders_req_{request_id}")
        context.add_loader("user_orders", orders_loader)
        
        # Simulate resolver calls
        user_loader = context.get_loader("users")
        orders_loader = context.get_loader("user_orders")
        
        # Load user data
        user = await user_loader.load(random.randint(1, 10))
        orders = await orders_loader.load(user['id'])
        
        print(f"   👤 User: {user['name']} has {len(orders)} orders")
        
        # Get context stats
        stats = context.get_context_stats()
        print(f"   📈 Request {stats['request_id']} completed in {stats['duration']:.3f}s")
        
        return stats
    
    # Simulate multiple concurrent requests
    print("Simulating 5 concurrent GraphQL requests...")
    
    request_tasks = [simulate_graphql_request(i) for i in range(1, 6)]
    request_stats = await asyncio.gather(*request_tasks)
    
    print(f"\n✅ Processed {len(request_stats)} requests")
    
    # Show shared loader stats
    shared_stats = shared_registry.get_all_stats()
    user_stats = shared_stats['loaders']['users']
    
    print(f"📊 Shared User Loader Stats:")
    print(f"   Total Requests: {user_stats['total_requests']}")
    print(f"   Cache Hit Rate: {user_stats['cache_hit_rate']}")
    print(f"   Batches: {user_stats['batches_executed']}")
    
    print()


async def demo_production_benchmark():
    """Demonstrate production-level performance."""
    print("🚀 Demo 7: Production Performance Benchmark")
    print("=" * 50)
    
    db = SimulatedDatabase()
    
    # Create high-performance loaders
    async def batch_load_users(user_ids: List[int]) -> List[Dict[str, Any]]:
        return await db.execute_query('users', 'id', user_ids)
    
    production_loader = DataLoader(
        batch_load_users,
        batch_size=50,
        max_batch_size=100,
        batch_timeout=0.005,  # 5ms for high throughput
        cache=True,
        cache_ttl=600,  # 10 minutes
        cache_max_size=5000,
        name="production_benchmark"
    )
    
    print("Running high-load benchmark...")
    print("Scenario: 1000 user loads (simulating busy GraphQL API)")
    
    start_time = time.time()
    start_queries = db.query_count
    
    # Generate random user requests (simulating real API patterns)
    tasks = []
    for _ in range(1000):
        # Weighted towards popular users (realistic caching scenario)
        if random.random() < 0.3:
            user_id = random.randint(1, 10)  # Popular users
        else:
            user_id = random.randint(1, 100)  # All users
        
        tasks.append(production_loader.load(user_id))
    
    # Execute all requests
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    end_queries = db.query_count
    
    duration = end_time - start_time
    queries_used = end_queries - start_queries
    
    print(f"\n📊 Benchmark Results:")
    print(f"   Requests: 1,000")
    print(f"   Duration: {duration:.3f}s")
    print(f"   Throughput: {1000/duration:.1f} requests/second")
    print(f"   DB Queries: {queries_used}")
    print(f"   Query Efficiency: {1000/queries_used:.1f}x reduction")
    
    # Get detailed stats
    stats = production_loader.get_stats()
    
    print(f"\n📈 Performance Metrics:")
    print(f"   Cache Hit Rate: {stats['cache_hit_rate']}")
    print(f"   Average Batch Size: {stats['avg_batch_size']}")
    print(f"   Average Batch Time: {stats['avg_batch_time']}")
    print(f"   Efficiency Ratio: {stats['efficiency_ratio']}")
    print(f"   Duplicates Handled: {stats['duplicate_requests']}")
    
    # Show batch history
    batch_history = production_loader.get_batch_history(5)
    
    print(f"\n🔍 Recent Batch History:")
    for batch in batch_history[-3:]:
        print(f"   Batch {batch['batch_id']}: {batch['keys_count']} keys in {batch['duration']:.3f}s")
    
    print()


async def main():
    """Run all DataLoader demonstrations."""
    print("🎯 CovetPy Production DataLoader Demonstration")
    print("=" * 60)
    print("Showcasing enterprise-grade GraphQL N+1 query prevention")
    print("=" * 60)
    print()
    
    demos = [
        demo_basic_functionality,
        demo_n_plus_one_prevention,
        demo_advanced_features,
        demo_cache_features,
        demo_registry_and_monitoring,
        demo_graphql_context,
        demo_production_benchmark
    ]
    
    for demo in demos:
        try:
            await demo()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("🎉 All DataLoader demonstrations completed!")
    print("\n" + "=" * 60)
    print("📋 Summary: Production-Ready Features Demonstrated")
    print("=" * 60)
    
    features = [
        "✅ Automatic request batching and N+1 prevention",
        "✅ Advanced caching with TTL and LRU eviction", 
        "✅ Request deduplication and coalescing",
        "✅ Comprehensive error handling and retry logic",
        "✅ Performance metrics and health monitoring",
        "✅ Registry management and context isolation",
        "✅ Production-level performance and throughput",
        "✅ Zero external dependencies",
        "✅ Enterprise-grade reliability and monitoring"
    ]
    
    for feature in features:
        print(feature)
    
    print("\n🚀 Ready for production GraphQL APIs!")


if __name__ == "__main__":
    asyncio.run(main())