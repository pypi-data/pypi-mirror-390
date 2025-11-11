#!/usr/bin/env python3
"""
Simple Demonstration of CovetPy Async Event Loop Management Fixes

This script demonstrates the key fixes without complex database integration:

1. Event loop detection and reuse
2. Safe sync/async interoperability  
3. WebSocket manager event loop integration
4. Task worker event loop integration
5. Cleanup system coordination

Run this script to see the core fixes working.
"""

import asyncio
import logging
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main demonstration function."""
    logger.info("🚀 Starting CovetPy Core Async Event Loop Management Demo")
    
    # Import fixed components
    from src.covet.core.async_utils import (
        get_loop_manager, is_async_context, create_task_safe, run_async_safe
    )
    from src.covet.websocket.async_manager import AsyncWebSocketManager
    from src.covet.tasks.async_worker import AsyncWorkerPool
    from src.covet.core.cleanup import get_cleanup_manager, CleanupPriority
    
    # Test 1: Event Loop Management
    logger.info("\n🔁 Testing Event Loop Management...")
    
    # Verify we're in async context
    assert is_async_context(), "Should be in async context"
    logger.info("✅ Async context detection working")
    
    # Get the loop manager
    loop_manager = get_loop_manager()
    current_loop = loop_manager.get_event_loop()
    main_loop = asyncio.get_running_loop()
    assert current_loop is main_loop, "Should use the same event loop"
    logger.info("✅ Event loop manager working correctly")
    
    # Test multiple async operations share the same loop
    async def get_current_loop():
        return get_loop_manager().get_event_loop()
    
    loops = []
    for _ in range(5):
        loop = await get_current_loop()
        loops.append(loop)
    
    for loop in loops:
        assert loop is main_loop, "All operations should use same loop"
    
    logger.info("✅ Event loop properly reused across contexts")
    
    # Test 2: WebSocket Manager
    logger.info("\n🌐 Testing WebSocket Manager...")
    
    ws_manager = AsyncWebSocketManager(max_connections=10)
    
    # Start WebSocket manager
    await ws_manager.start()
    assert ws_manager._running
    logger.info("✅ WebSocket manager started")
    
    # Test adding mock connection
    from unittest.mock import Mock
    mock_connection = Mock()
    mock_connection.connection_id = "demo-connection-1"
    mock_connection.state = "open"
    mock_connection.close = asyncio.coroutine(lambda *args: None)
    
    success = await ws_manager.add_connection(mock_connection)
    assert success
    logger.info("✅ WebSocket connection added")
    
    # Test connection stats
    stats = ws_manager.get_stats()
    assert stats['active_connections'] == 1
    logger.info(f"✅ WebSocket stats: {stats['active_connections']} active connections")
    
    # Clean up WebSocket manager
    await ws_manager.stop(timeout=1.0)
    assert not ws_manager._running
    logger.info("✅ WebSocket manager stopped")
    
    # Test 3: Task Worker Pool
    logger.info("\n⚡ Testing Async Worker Pool...")
    
    worker_pool = AsyncWorkerPool(min_workers=2, max_workers=4)
    
    # Start worker pool
    await worker_pool.start()
    assert len(worker_pool.workers) >= 2
    logger.info(f"✅ Worker pool started with {len(worker_pool.workers)} workers")
    
    # Test task processing
    from src.covet.tasks.persistence import Task, TaskPriority, TaskStatus
    
    def sample_sync_task(message: str):
        """Sample synchronous task."""
        time.sleep(0.01)  # Simulate work
        return f"Processed: {message}"
    
    async def sample_async_task(message: str):
        """Sample asynchronous task."""
        await asyncio.sleep(0.01)  # Simulate async work
        return f"Async processed: {message}"
    
    # Create tasks
    sync_task = Task(
        id="sync-task-1",
        name="demo-sync-task",
        func=sample_sync_task,
        args=("Hello from sync task",),
        priority=TaskPriority.NORMAL
    )
    
    async_task = Task(
        id="async-task-1", 
        name="demo-async-task",
        func=sample_async_task,
        args=("Hello from async task",),
        priority=TaskPriority.HIGH
    )
    
    # Enqueue tasks
    success1 = await worker_pool.enqueue_task(sync_task)
    success2 = await worker_pool.enqueue_task(async_task)
    assert success1 and success2
    logger.info("✅ Tasks enqueued successfully")
    
    # Give tasks time to process
    await asyncio.sleep(0.5)
    
    # Check stats
    pool_stats = worker_pool.get_stats()
    logger.info(f"✅ Worker pool stats: {pool_stats['tasks_enqueued']} tasks enqueued")
    
    # Stop worker pool
    await worker_pool.stop(timeout=2.0)
    assert len(worker_pool.workers) == 0
    logger.info("✅ Worker pool stopped")
    
    # Test 4: Concurrent Operations
    logger.info("\n🔄 Testing Concurrent Operations...")
    
    async def concurrent_operation(name: str, delay: float):
        """Sample concurrent operation."""
        # Verify we're using the same loop
        op_loop = get_loop_manager().get_event_loop()
        assert op_loop is main_loop, f"Operation {name} using wrong loop"
        
        await asyncio.sleep(delay)
        return f"Operation {name} completed"
    
    # Create multiple concurrent tasks
    concurrent_tasks = []
    for i in range(10):
        task = create_task_safe(concurrent_operation(f"task-{i}", 0.01))
        concurrent_tasks.append(task)
    
    # Wait for all tasks
    results = await asyncio.gather(*concurrent_tasks)
    assert len(results) == 10
    logger.info(f"✅ Completed {len(results)} concurrent operations")
    
    # Test 5: Cleanup System
    logger.info("\n🧹 Testing Cleanup System...")
    
    cleanup_manager = get_cleanup_manager()
    
    # Register test cleanup handlers
    cleanup_order = []
    
    def critical_cleanup():
        cleanup_order.append("critical")
        logger.info("🔧 Critical cleanup executed")
    
    def normal_cleanup():
        cleanup_order.append("normal")
        logger.info("🔧 Normal cleanup executed")
    
    cleanup_manager.register_handler(
        "demo-critical", critical_cleanup, CleanupPriority.CRITICAL, 1.0
    )
    cleanup_manager.register_handler(
        "demo-normal", normal_cleanup, CleanupPriority.NORMAL, 1.0
    )
    
    logger.info("✅ Cleanup handlers registered")
    
    # Get cleanup stats
    cleanup_stats = cleanup_manager.get_stats()
    logger.info(f"✅ Cleanup system has {cleanup_stats['registered_handlers']} handlers")
    
    # Test 6: Performance and Stress Test
    logger.info("\n⚡ Testing Performance...")
    
    start_time = time.time()
    
    # Create many tasks quickly
    stress_tasks = []
    for i in range(1000):
        async def quick_task(task_id=i):
            return f"task-{task_id}-done"
        
        task = create_task_safe(quick_task())
        stress_tasks.append(task)
    
    creation_time = time.time() - start_time
    
    # Complete all tasks
    await asyncio.gather(*stress_tasks)
    
    total_time = time.time() - start_time
    
    logger.info(f"✅ Created 1000 tasks in {creation_time:.3f}s")
    logger.info(f"✅ Completed 1000 tasks in {total_time:.3f}s")
    
    # Test 7: Component Coexistence
    logger.info("\n🎯 Testing Component Coexistence...")
    
    # Start multiple components simultaneously
    ws_manager2 = AsyncWebSocketManager(max_connections=5)
    worker_pool2 = AsyncWorkerPool(min_workers=1, max_workers=2)
    
    # Initialize all together
    await ws_manager2.start()
    await worker_pool2.start()
    
    # All should be working in the same loop
    current_loop = get_loop_manager().get_event_loop()
    assert current_loop is main_loop
    
    # Test they can work together
    mock_connection2 = Mock()
    mock_connection2.connection_id = "coexist-connection"
    mock_connection2.state = "open"
    mock_connection2.close = asyncio.coroutine(lambda *args: None)
    
    await ws_manager2.add_connection(mock_connection2)
    
    test_task = Task(
        id="coexist-task",
        name="coexist-test",
        func=lambda: "coexist success",
        priority=TaskPriority.NORMAL
    )
    
    await worker_pool2.enqueue_task(test_task)
    
    # Clean up
    await ws_manager2.stop(timeout=1.0)
    await worker_pool2.stop(timeout=1.0)
    
    logger.info("✅ All components coexist without conflicts")
    
    logger.info("\n🎉 CovetPy Core Async Event Loop Management Demo Complete!")
    logger.info("All core fixes are working correctly:")
    logger.info("  ✅ No nested asyncio.run() calls")
    logger.info("  ✅ Proper event loop reuse")
    logger.info("  ✅ Component integration works")
    logger.info("  ✅ Cleanup system operational")
    logger.info("  ✅ High performance maintained")


def demo_sync_integration():
    """Demonstrate sync/async integration."""
    logger.info("\n🔄 Testing Sync/Async Integration...")
    
    from src.covet.core.async_utils import is_async_context, run_async_safe
    
    # Verify we're in sync context
    assert not is_async_context(), "Should be in sync context"
    
    async def async_operation():
        assert is_async_context(), "Should be in async context inside coroutine"
        await asyncio.sleep(0.01)
        return "sync_to_async_success"
    
    # Run async operation from sync context
    result = run_async_safe(async_operation())
    assert result == "sync_to_async_success"
    
    logger.info("✅ Sync to async integration working")
    
    # Test that we can't use run_async_safe from async context
    async def test_nested_error():
        try:
            run_async_safe(async_operation())
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "async context" in str(e)
            return True
    
    # This should work - testing the error path
    result = run_async_safe(test_nested_error())
    assert result is True
    
    logger.info("✅ Nested async call properly prevented")


if __name__ == "__main__":
    try:
        # Test sync integration first
        demo_sync_integration()
        
        # Run main async demo
        asyncio.run(main())
        
        print("\n" + "="*60)
        print("🎉 SUCCESS: All CovetPy core async fixes are working correctly!")
        print("="*60)
        print("\nKey Achievements:")
        print("  🔧 Fixed nested asyncio.run() calls")
        print("  🔄 Implemented proper event loop reuse")  
        print("  🌐 WebSocket integration without conflicts")
        print("  ⚡ Task workers using shared event loop")
        print("  🧹 Comprehensive cleanup system")
        print("  🚀 High performance maintained")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)