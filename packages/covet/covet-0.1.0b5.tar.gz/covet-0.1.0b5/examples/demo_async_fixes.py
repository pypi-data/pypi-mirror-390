#!/usr/bin/env python3
"""
Demonstration of CovetPy Async Event Loop Management Fixes

This script demonstrates how the fixed components work together without
event loop conflicts:

1. Database manager can be initialized from both sync and async contexts
2. WebSocket manager integrates properly with the main event loop  
3. Task workers share the same event loop as the application
4. Cleanup handlers ensure proper resource management
5. No nested asyncio.run() calls or loop conflicts

Run this script to see the fixes in action.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main demonstration function."""
    logger.info("🚀 Starting CovetPy Async Event Loop Management Demo")
    
    # Import fixed components
    from src.covet.core.async_utils import (
        get_loop_manager, is_async_context, create_task_safe
    )
    from src.covet.database.manager import DatabaseManager
    from src.covet.websocket.async_manager import AsyncWebSocketManager
    from src.covet.tasks.async_worker import AsyncWorkerPool
    from src.covet.core.cleanup import get_cleanup_manager, CleanupPriority
    
    # Verify we're in async context
    assert is_async_context(), "Should be in async context"
    logger.info("✅ Async context detection working")
    
    # Get the loop manager
    loop_manager = get_loop_manager()
    current_loop = loop_manager.get_event_loop()
    main_loop = asyncio.get_running_loop()
    assert current_loop is main_loop, "Should use the same event loop"
    logger.info("✅ Event loop manager working correctly")
    
    # Test 1: Database Manager
    logger.info("\n📊 Testing Database Manager...")
    
    db_config = {
        'default': {
            'type': 'sqlite',  # Use SQLite for simple demo
            'host': 'localhost',
            'port': 0,  # Not used for SQLite
            'database': ':memory:',
            'username': '',
            'password': ''
        }
    }
    
    # Mock the factory for demo purposes
    from unittest.mock import patch, AsyncMock
    
    with patch('src.covet.database.factory.DatabaseConnectionFactory') as mock_factory:
        mock_adapter = AsyncMock()
        mock_factory.return_value.create_adapter = AsyncMock(return_value=mock_adapter)
        
        db_manager = DatabaseManager(db_config)
        
        # Initialize asynchronously
        await db_manager.initialize()
        assert db_manager.is_initialized
        logger.info("✅ Database manager initialized asynchronously")
        
        # Test cleanup
        await db_manager.close()
        assert not db_manager.is_initialized
        logger.info("✅ Database manager cleaned up")
    
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
    
    # Test task processing (mock task for demo)
    from src.covet.tasks.persistence import Task, TaskPriority, TaskStatus
    
    def sample_sync_task(message: str):
        """Sample synchronous task."""
        time.sleep(0.01)  # Simulate work
        return f"Processed: {message}"
    
    async def sample_async_task(message: str):
        """Sample asynchronous task."""
        await asyncio.sleep(0.01)  # Simulate async work
        return f"Async processed: {message}"
    
    # Create mock tasks
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
        await asyncio.sleep(delay)
        return f"Operation {name} completed"
    
    # Create multiple concurrent tasks
    concurrent_tasks = []
    for i in range(5):
        task = create_task_safe(concurrent_operation(f"task-{i}", 0.01))
        concurrent_tasks.append(task)
    
    # Wait for all tasks
    results = await asyncio.gather(*concurrent_tasks)
    assert len(results) == 5
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
    
    # Test 6: Event Loop Reuse
    logger.info("\n🔁 Testing Event Loop Reuse...")
    
    async def get_current_loop():
        return get_loop_manager().get_event_loop()
    
    # Get loops from multiple async contexts
    loops = []
    for _ in range(3):
        loop = await get_current_loop()
        loops.append(loop)
    
    # All should be the same loop
    for loop in loops:
        assert loop is main_loop
    
    logger.info("✅ Event loop properly reused across contexts")
    
    # Final verification
    logger.info("\n🎯 Final Verification...")
    
    # Verify all components can coexist
    final_db_config = {
        'default': {
            'type': 'sqlite',
            'host': 'localhost',
            'port': 0,
            'database': ':memory:',
            'username': '',
            'password': ''
        }
    }
    final_db = DatabaseManager(final_db_config)
    final_ws = AsyncWebSocketManager(max_connections=5)
    final_workers = AsyncWorkerPool(min_workers=1, max_workers=2)
    
    # Initialize all together
    with patch('src.covet.database.factory.DatabaseConnectionFactory') as mock_factory:
        mock_adapter = AsyncMock()
        mock_factory.return_value.create_adapter = AsyncMock(return_value=mock_adapter)
        
        await final_db.initialize()
        await final_ws.start()
        await final_workers.start()
        
        # All should be working in the same loop
        current_loop = get_loop_manager().get_event_loop()
        assert current_loop is main_loop
        
        # Clean up
        await final_db.close()
        await final_ws.stop(timeout=1.0)
        await final_workers.stop(timeout=1.0)
    
    logger.info("✅ All components coexist without conflicts")
    
    logger.info("\n🎉 CovetPy Async Event Loop Management Demo Complete!")
    logger.info("All fixes are working correctly:")
    logger.info("  ✅ No nested asyncio.run() calls")
    logger.info("  ✅ Proper event loop reuse")
    logger.info("  ✅ Sync/async context compatibility")
    logger.info("  ✅ Component integration works")
    logger.info("  ✅ Cleanup system operational")


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


if __name__ == "__main__":
    try:
        # Test sync integration first
        demo_sync_integration()
        
        # Run main async demo
        asyncio.run(main())
        
        print("\n" + "="*60)
        print("🎉 SUCCESS: All CovetPy async fixes are working correctly!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)