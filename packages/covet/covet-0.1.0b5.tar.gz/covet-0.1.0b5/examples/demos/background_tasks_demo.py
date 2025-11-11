#!/usr/bin/env python3
"""
CovetPy Background Tasks System - Production Demo

This demo showcases the complete, production-ready background tasks system
that integrates with both simple and enterprise CovetPy task queues.

Features demonstrated:
- Task submission with priority handling
- Async and sync task execution
- Retry logic with exponential backoff
- Task scheduling with intervals and cron
- Real-time monitoring and metrics
- Error handling and recovery
- Enterprise system integration
"""

import asyncio
import logging
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from covet.core.background_tasks import (
    BackgroundTaskManager,
    TaskPriority,
    submit_task,
    schedule_task,
    schedule_cron,
    get_task_result,
    get_system_metrics,
    background_task,
    scheduled_task,
    ENTERPRISE_AVAILABLE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Example task functions
async def send_email_task(recipient: str, subject: str, body: str):
    """Simulate sending an email."""
    logger.info(f"Sending email to {recipient}: {subject}")
    await asyncio.sleep(0.5)  # Simulate email sending
    return f"Email sent to {recipient}"


def process_image_task(image_path: str, filter_name: str):
    """Simulate image processing."""
    logger.info(f"Processing image {image_path} with filter {filter_name}")
    time.sleep(1.0)  # Simulate CPU-intensive work
    return f"Processed {image_path} with {filter_name} filter"


async def backup_database_task(database_name: str):
    """Simulate database backup."""
    logger.info(f"Starting backup of {database_name}")
    await asyncio.sleep(2.0)  # Simulate backup process
    return f"Backup of {database_name} completed"


def generate_report_task(report_type: str, data_size: int):
    """Simulate report generation."""
    if data_size > 1000:
        raise ValueError(f"Data size {data_size} too large for report")
    
    logger.info(f"Generating {report_type} report with {data_size} records")
    time.sleep(0.3)
    return f"{report_type} report generated with {data_size} records"


# Decorated task examples
@background_task(priority=TaskPriority.HIGH, max_retries=3)
async def critical_notification_task(user_id: int, message: str):
    """High-priority notification task."""
    logger.info(f"Sending critical notification to user {user_id}: {message}")
    await asyncio.sleep(0.2)
    return f"Critical notification sent to user {user_id}"


@scheduled_task(interval=30.0)  # Run every 30 seconds
async def cleanup_temp_files():
    """Periodic cleanup task."""
    logger.info("Cleaning up temporary files...")
    await asyncio.sleep(0.1)
    return "Temporary files cleaned"


class BackgroundTasksDemo:
    """Production demo of the background tasks system."""
    
    def __init__(self):
        self.task_manager = None
        self.submitted_tasks = []
    
    async def run_demo(self):
        """Run the complete demonstration."""
        logger.info("="*60)
        logger.info("COVETPY BACKGROUND TASKS SYSTEM - PRODUCTION DEMO")
        logger.info("="*60)
        
        try:
            # Initialize the system
            await self.initialize_system()
            
            # Demo 1: Basic task submission
            await self.demo_basic_tasks()
            
            # Demo 2: Priority-based execution
            await self.demo_priority_tasks()
            
            # Demo 3: Retry logic
            await self.demo_retry_logic()
            
            # Demo 4: Task scheduling
            await self.demo_scheduled_tasks()
            
            # Demo 5: Real-time monitoring
            await self.demo_monitoring()
            
            # Demo 6: Error handling
            await self.demo_error_handling()
            
            # Demo 7: Performance metrics
            await self.demo_performance_metrics()
            
            # Final system status
            await self.show_final_status()
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
        finally:
            await self.cleanup()
    
    async def initialize_system(self):
        """Initialize the background tasks system."""
        logger.info("Initializing Background Tasks System...")
        
        self.task_manager = BackgroundTaskManager(
            max_workers=4,
            enable_persistence=True,
            persistence_path="demo_tasks.db",
            use_enterprise=ENTERPRISE_AVAILABLE
        )
        
        await self.task_manager.start()
        
        logger.info(f"✓ Task Manager started with {self.task_manager.max_workers} workers")
        logger.info(f"✓ Enterprise integration: {'Enabled' if self.task_manager.use_enterprise else 'Disabled'}")
        logger.info(f"✓ Persistence: {'Enabled' if self.task_manager.enable_persistence else 'Disabled'}")
        print()
    
    async def demo_basic_tasks(self):
        """Demonstrate basic task submission and execution."""
        logger.info("DEMO 1: Basic Task Submission and Execution")
        logger.info("-" * 50)
        
        # Submit various types of tasks
        tasks = [
            await self.task_manager.submit_task(
                send_email_task, "user@example.com", "Welcome", "Welcome to our service!"
            ),
            await self.task_manager.submit_task(
                process_image_task, "/uploads/photo.jpg", "sepia"
            ),
            await self.task_manager.submit_task(
                backup_database_task, "production_db"
            )
        ]
        
        self.submitted_tasks.extend(tasks)
        
        # Wait for completion
        logger.info(f"Submitted {len(tasks)} tasks, waiting for completion...")
        
        for task_id in tasks:
            result = await self.task_manager.get_result(task_id, timeout=10.0)
            if result:
                logger.info(f"✓ Task {task_id[:8]}: {result.result}")
            else:
                logger.warning(f"✗ Task {task_id[:8]}: Timed out")
        
        print()
    
    async def demo_priority_tasks(self):
        """Demonstrate priority-based task execution."""
        logger.info("DEMO 2: Priority-Based Task Execution")
        logger.info("-" * 50)
        
        # Submit tasks with different priorities
        priorities = [
            (TaskPriority.LOW, "low-priority-report"),
            (TaskPriority.HIGH, "urgent-notification"),
            (TaskPriority.NORMAL, "regular-processing"),
            (TaskPriority.CRITICAL, "system-alert")
        ]
        
        tasks = []
        for priority, task_type in priorities:
            task_id = await self.task_manager.submit_task(
                generate_report_task,
                task_type,
                100,
                priority=priority
            )
            tasks.append((task_id, priority, task_type))
            logger.info(f"Submitted {task_type} with {priority.name} priority")
        
        # Monitor execution order
        await asyncio.sleep(2.0)
        
        for task_id, priority, task_type in tasks:
            result = await self.task_manager.get_result(task_id, timeout=1.0)
            if result:
                logger.info(f"✓ {priority.name}: {result.result}")
        
        print()
    
    async def demo_retry_logic(self):
        """Demonstrate retry logic with exponential backoff."""
        logger.info("DEMO 3: Retry Logic with Exponential Backoff")
        logger.info("-" * 50)
        
        # Submit a task that will fail initially
        task_id = await self.task_manager.submit_task(
            generate_report_task,
            "large-report",
            1500,  # This will cause an error
            max_retries=3
        )
        
        logger.info("Submitted task that will fail (data_size > 1000)...")
        
        # Wait for completion (it should fail after retries)
        result = await self.task_manager.get_result(task_id, timeout=10.0)
        
        if result:
            logger.info(f"✓ Task completed with status: {result.status}")
            if result.error:
                logger.info(f"  Error: {result.error}")
        
        print()
    
    async def demo_scheduled_tasks(self):
        """Demonstrate task scheduling."""
        logger.info("DEMO 4: Task Scheduling")
        logger.info("-" * 50)
        
        # Schedule a task to run in 3 seconds
        future_time = datetime.now() + timedelta(seconds=3)
        
        task_id = await schedule_task(
            cleanup_temp_files,
            interval=5.0,  # Every 5 seconds
            start_time=future_time
        )
        
        logger.info(f"Scheduled cleanup task to start at {future_time.strftime('%H:%M:%S')}")
        logger.info("Waiting for scheduled execution...")
        
        # Wait to see the scheduled execution
        await asyncio.sleep(6.0)
        
        print()
    
    async def demo_monitoring(self):
        """Demonstrate real-time monitoring."""
        logger.info("DEMO 5: Real-Time Monitoring")
        logger.info("-" * 50)
        
        # Submit multiple tasks for monitoring
        monitoring_tasks = []
        for i in range(5):
            task_id = await self.task_manager.submit_task(
                process_image_task,
                f"image_{i}.jpg",
                "blur"
            )
            monitoring_tasks.append(task_id)
        
        logger.info(f"Submitted {len(monitoring_tasks)} tasks for monitoring...")
        
        # Monitor progress
        for _ in range(3):
            metrics = self.task_manager.get_metrics()
            worker_stats = self.task_manager.get_worker_stats()
            
            active_workers = metrics.get('active_workers', 0)
            queue_size = metrics.get('queue_size', 0)
            
            logger.info(f"Active workers: {active_workers}, Queue size: {queue_size}")
            await asyncio.sleep(1.0)
        
        print()
    
    async def demo_error_handling(self):
        """Demonstrate comprehensive error handling."""
        logger.info("DEMO 6: Error Handling and Recovery")
        logger.info("-" * 50)
        
        def error_prone_task(error_type: str):
            if error_type == "value_error":
                raise ValueError("Invalid value provided")
            elif error_type == "runtime_error":
                raise RuntimeError("Runtime error occurred")
            return "Task completed successfully"
        
        # Submit tasks with different error types
        error_tasks = [
            await self.task_manager.submit_task(error_prone_task, "value_error"),
            await self.task_manager.submit_task(error_prone_task, "runtime_error"),
            await self.task_manager.submit_task(error_prone_task, "success")
        ]
        
        logger.info("Submitted tasks with different error scenarios...")
        
        for i, task_id in enumerate(error_tasks):
            result = await self.task_manager.get_result(task_id, timeout=5.0)
            if result:
                if result.status.value == "completed":
                    logger.info(f"✓ Task {i+1}: {result.result}")
                else:
                    logger.info(f"✗ Task {i+1}: {result.status.value} - {result.error}")
        
        print()
    
    async def demo_performance_metrics(self):
        """Demonstrate performance metrics collection."""
        logger.info("DEMO 7: Performance Metrics")
        logger.info("-" * 50)
        
        # Get comprehensive metrics
        metrics = self.task_manager.get_metrics()
        
        logger.info("System Metrics:")
        for key, value in metrics.items():
            if key != 'health' and key != 'enterprise_stats':
                logger.info(f"  {key}: {value}")
        
        # Health status
        health = metrics.get('health', {})
        logger.info("Health Status:")
        for key, value in health.items():
            logger.info(f"  {key}: {value}")
        
        print()
    
    async def show_final_status(self):
        """Show final system status."""
        logger.info("FINAL SYSTEM STATUS")
        logger.info("-" * 50)
        
        metrics = self.task_manager.get_metrics()
        
        logger.info(f"Total tasks submitted: {metrics.get('tasks_submitted', 0)}")
        logger.info(f"Tasks completed: {metrics.get('tasks_completed', 0)}")
        logger.info(f"Tasks failed: {metrics.get('tasks_failed', 0)}")
        logger.info(f"Tasks cancelled: {metrics.get('tasks_cancelled', 0)}")
        logger.info(f"Average execution time: {metrics.get('average_execution_time', 0):.2f}s")
        
        # Worker health
        worker_stats = self.task_manager.get_worker_stats()
        healthy_workers = sum(1 for stats in worker_stats if stats.get('running', False))
        logger.info(f"Healthy workers: {healthy_workers}/{len(worker_stats)}")
        
        print()
    
    async def cleanup(self):
        """Clean up demo resources."""
        logger.info("Cleaning up demo resources...")
        
        if self.task_manager:
            await self.task_manager.stop()
        
        # Clean up demo database
        demo_db = Path("demo_tasks.db")
        if demo_db.exists():
            demo_db.unlink()
            logger.info("Demo database cleaned up")
        
        logger.info("✓ Demo completed successfully")


async def main():
    """Run the production demo."""
    demo = BackgroundTasksDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())