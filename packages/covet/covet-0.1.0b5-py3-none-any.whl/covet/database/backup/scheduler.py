"""
Backup Scheduler - Automated Backup Management

Production-grade scheduler for automated backups with:
- Cron-style scheduling
- Backup rotation policies
- Automatic cleanup of old backups
- Monitoring and alerting
- Failure recovery and retry logic
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ScheduleFrequency(Enum):
    """Backup schedule frequency."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # Cron expression


class RetentionPolicy(Enum):
    """Backup retention policy strategy."""

    GFS = "gfs"  # Grandfather-Father-Son (daily, weekly, monthly)
    SIMPLE = "simple"  # Keep N most recent backups
    TIME_BASED = "time_based"  # Keep backups for N days
    CUSTOM = "custom"  # Custom policy function


@dataclass
class BackupSchedule:
    """
    Backup schedule configuration.

    Defines when and how backups should be created.
    """

    # Schedule identification
    name: str
    description: str = ""

    # Database configuration
    database_config: Dict[str, Any] = field(default_factory=dict)

    # Schedule frequency
    frequency: ScheduleFrequency = ScheduleFrequency.DAILY
    cron_expression: Optional[str] = None  # For CUSTOM frequency
    hour: int = 2  # Hour to run (0-23)
    minute: int = 0  # Minute to run (0-59)
    day_of_week: int = 0  # Day of week for WEEKLY (0=Monday)
    day_of_month: int = 1  # Day of month for MONTHLY (1-31)

    # Backup options
    compress: bool = True
    encrypt: bool = False
    storage_backend: str = "local"

    # Retention policy
    retention_policy: RetentionPolicy = RetentionPolicy.TIME_BASED
    retention_days: int = 30  # For TIME_BASED policy
    retention_count: int = 7  # For SIMPLE policy
    gfs_daily: int = 7  # Keep daily backups for 7 days
    gfs_weekly: int = 4  # Keep weekly backups for 4 weeks
    gfs_monthly: int = 12  # Keep monthly backups for 12 months

    # Monitoring
    enabled: bool = True
    notify_on_success: bool = False
    notify_on_failure: bool = True
    alert_email: Optional[str] = None

    # Advanced options
    max_retries: int = 3
    retry_delay_seconds: int = 300  # 5 minutes
    timeout_seconds: int = 3600  # 1 hour


@dataclass
class ScheduledBackupResult:
    """Result of a scheduled backup execution."""

    schedule_name: str
    backup_id: Optional[str] = None
    success: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_message: str = ""
    retry_count: int = 0


class BackupScheduler:
    """
    Automated backup scheduler with cron-like functionality.

    Features:
    - Multiple concurrent schedules
    - Automatic retry on failure
    - Backup rotation and cleanup
    - Monitoring and alerting
    - Graceful shutdown

    Example:
        # Create scheduler
        scheduler = BackupScheduler(backup_manager)

        # Add daily backup schedule
        schedule = BackupSchedule(
            name="production_daily",
            database_config={
                "database_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "production",
                "user": "postgres",
                "password": "secret"
            },
            frequency=ScheduleFrequency.DAILY,
            hour=2,  # 2 AM
            retention_days=30,
            compress=True,
            encrypt=True
        )
        scheduler.add_schedule(schedule)

        # Start scheduler
        await scheduler.start()

        # Run until stopped
        await scheduler.wait()

        # Stop scheduler
        await scheduler.stop()
    """

    def __init__(
        self,
        backup_manager: Any,  # BackupManager instance
        check_interval_seconds: int = 60,
    ):
        """
        Initialize backup scheduler.

        Args:
            backup_manager: BackupManager instance for creating backups
            check_interval_seconds: How often to check for scheduled backups
        """
        self.backup_manager = backup_manager
        self.check_interval = check_interval_seconds

        self._schedules: Dict[str, BackupSchedule] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_run: Dict[str, datetime] = {}
        self._results: List[ScheduledBackupResult] = []

    def add_schedule(self, schedule: BackupSchedule) -> None:
        """
        Add a backup schedule.

        Args:
            schedule: BackupSchedule configuration
        """
        if schedule.name in self._schedules:
            logger.warning(f"Replacing existing schedule: {schedule.name}")

        self._schedules[schedule.name] = schedule
        logger.info(f"Added backup schedule: {schedule.name}")

    def remove_schedule(self, name: str) -> None:
        """
        Remove a backup schedule.

        Args:
            name: Schedule name
        """
        if name in self._schedules:
            del self._schedules[name]
            logger.info(f"Removed backup schedule: {name}")

    def get_schedule(self, name: str) -> Optional[BackupSchedule]:
        """Get schedule by name."""
        return self._schedules.get(name)

    def list_schedules(self) -> List[BackupSchedule]:
        """List all schedules."""
        return list(self._schedules.values())

    async def start(self) -> None:
        """Start the backup scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Backup scheduler started")

    async def stop(self) -> None:
        """Stop the backup scheduler."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Backup scheduler stopped")

    async def wait(self) -> None:
        """Wait for scheduler to finish (blocks until stopped)."""
        if self._task:
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def run_schedule_now(self, name: str) -> ScheduledBackupResult:
        """
        Run a specific schedule immediately (manual trigger).

        Args:
            name: Schedule name

        Returns:
            ScheduledBackupResult
        """
        schedule = self._schedules.get(name)
        if not schedule:
            raise ValueError(f"Schedule not found: {name}")

        logger.info(f"Manually triggering backup schedule: {name}")
        return await self._execute_backup(schedule)

    def get_next_run_time(self, name: str) -> Optional[datetime]:
        """
        Get next scheduled run time for a schedule.

        Args:
            name: Schedule name

        Returns:
            Next run time or None if not scheduled
        """
        schedule = self._schedules.get(name)
        if not schedule or not schedule.enabled:
            return None

        now = datetime.now()
        last_run = self._last_run.get(name)

        return self._calculate_next_run(schedule, last_run or now)

    def get_recent_results(
        self, limit: int = 100, schedule_name: Optional[str] = None
    ) -> List[ScheduledBackupResult]:
        """
        Get recent backup results.

        Args:
            limit: Maximum number of results
            schedule_name: Filter by schedule name

        Returns:
            List of ScheduledBackupResult
        """
        results = self._results

        if schedule_name:
            results = [r for r in results if r.schedule_name == schedule_name]

        return sorted(results, key=lambda x: x.started_at or datetime.min, reverse=True)[:limit]

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        logger.info("Scheduler loop started")

        while self._running:
            try:
                await self._check_schedules()
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)

        logger.info("Scheduler loop stopped")

    async def _check_schedules(self) -> None:
        """Check all schedules and run if due."""
        now = datetime.now()

        for name, schedule in self._schedules.items():
            if not schedule.enabled:
                continue

            # Check if schedule is due
            if self._is_schedule_due(schedule, name, now):
                logger.info(f"Schedule due: {name}")

                # Run backup in background
                asyncio.create_task(self._execute_backup_with_retry(schedule))

                # Update last run time
                self._last_run[name] = now

    def _is_schedule_due(self, schedule: BackupSchedule, name: str, now: datetime) -> bool:
        """Check if a schedule is due to run."""
        last_run = self._last_run.get(name)

        # First run
        if last_run is None:
            return True

        # Calculate next run time
        next_run = self._calculate_next_run(schedule, last_run)

        return now >= next_run

    def _calculate_next_run(self, schedule: BackupSchedule, from_time: datetime) -> datetime:
        """Calculate next run time for a schedule."""
        if schedule.frequency == ScheduleFrequency.HOURLY:
            next_run = from_time.replace(minute=schedule.minute, second=0, microsecond=0)
            if next_run <= from_time:
                next_run += timedelta(hours=1)
            return next_run

        elif schedule.frequency == ScheduleFrequency.DAILY:
            next_run = from_time.replace(
                hour=schedule.hour, minute=schedule.minute, second=0, microsecond=0
            )
            if next_run <= from_time:
                next_run += timedelta(days=1)
            return next_run

        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            # Find next occurrence of target day of week
            days_ahead = schedule.day_of_week - from_time.weekday()
            if days_ahead <= 0:
                days_ahead += 7

            next_run = from_time + timedelta(days=days_ahead)
            next_run = next_run.replace(
                hour=schedule.hour, minute=schedule.minute, second=0, microsecond=0
            )
            return next_run

        elif schedule.frequency == ScheduleFrequency.MONTHLY:
            # Next occurrence of target day of month
            next_run = from_time.replace(
                day=schedule.day_of_month,
                hour=schedule.hour,
                minute=schedule.minute,
                second=0,
                microsecond=0,
            )

            if next_run <= from_time:
                # Move to next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)

            return next_run

        elif schedule.frequency == ScheduleFrequency.CUSTOM:
            # TODO: Implement cron expression parsing
            # For now, default to daily
            return from_time + timedelta(days=1)

        else:
            # Default to daily
            return from_time + timedelta(days=1)

    async def _execute_backup_with_retry(self, schedule: BackupSchedule) -> ScheduledBackupResult:
        """Execute backup with retry logic."""
        result = ScheduledBackupResult(schedule_name=schedule.name)

        for attempt in range(schedule.max_retries + 1):
            try:
                backup_result = await self._execute_backup(schedule)

                if backup_result.success:
                    result = backup_result
                    break

                # Retry on failure
                if attempt < schedule.max_retries:
                    logger.warning(
                        f"Backup failed (attempt {attempt + 1}/{schedule.max_retries + 1}), "
                        f"retrying in {schedule.retry_delay_seconds}s"
                    )
                    await asyncio.sleep(schedule.retry_delay_seconds)
                else:
                    result = backup_result

            except Exception as e:
                logger.error(f"Backup execution error: {e}", exc_info=True)
                result.error_message = str(e)

                if attempt < schedule.max_retries:
                    await asyncio.sleep(schedule.retry_delay_seconds)

        # Store result
        self._results.append(result)

        # Trim results list (keep last 1000)
        if len(self._results) > 1000:
            self._results = self._results[-1000:]

        # Send notifications
        await self._send_notification(schedule, result)

        # Apply retention policy
        await self._apply_retention_policy(schedule)

        return result

    async def _execute_backup(self, schedule: BackupSchedule) -> ScheduledBackupResult:
        """Execute a single backup."""
        result = ScheduledBackupResult(schedule_name=schedule.name, started_at=datetime.now())

        try:
            # Create backup
            metadata = await asyncio.wait_for(
                self.backup_manager.create_backup(
                    database_config=schedule.database_config,
                    compress=schedule.compress,
                    encrypt=schedule.encrypt,
                    storage_backend=schedule.storage_backend,
                    retention_days=schedule.retention_days,
                    tags={"schedule": schedule.name, "automated": "true"},
                ),
                timeout=schedule.timeout_seconds,
            )

            result.backup_id = metadata.backup_id
            result.success = True

        except asyncio.TimeoutError:
            result.error_message = f"Backup timeout after {schedule.timeout_seconds}s"
            logger.error(result.error_message)

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Backup failed: {e}", exc_info=True)

        finally:
            result.completed_at = datetime.now()
            if result.started_at:
                result.duration_seconds = (result.completed_at - result.started_at).total_seconds()

        return result

    async def _apply_retention_policy(self, schedule: BackupSchedule) -> None:
        """Apply retention policy to backups."""
        try:
            if schedule.retention_policy == RetentionPolicy.TIME_BASED:
                # Simple time-based cleanup
                await self.backup_manager.cleanup_expired_backups()

            elif schedule.retention_policy == RetentionPolicy.SIMPLE:
                # Keep N most recent backups
                backups = self.backup_manager.list_backups(
                    database_name=schedule.database_config.get("database")
                )

                # Sort by creation time (newest first)
                backups = sorted(backups, key=lambda x: x.created_at, reverse=True)

                # Delete old backups
                for backup in backups[schedule.retention_count :]:
                    await self.backup_manager.delete_backup(backup.backup_id)

            elif schedule.retention_policy == RetentionPolicy.GFS:
                # Grandfather-Father-Son retention
                await self._apply_gfs_policy(schedule)

        except Exception as e:
            logger.error(f"Failed to apply retention policy: {e}")

    async def _apply_gfs_policy(self, schedule: BackupSchedule) -> None:
        """Apply Grandfather-Father-Son retention policy."""
        from .backup_metadata import BackupType

        backups = self.backup_manager.list_backups(
            database_name=schedule.database_config.get("database")
        )

        now = datetime.now()

        # Categorize backups
        daily_cutoff = now - timedelta(days=schedule.gfs_daily)
        weekly_cutoff = now - timedelta(weeks=schedule.gfs_weekly)
        monthly_cutoff = now - timedelta(days=schedule.gfs_monthly * 30)

        to_keep = set()

        # Keep daily backups
        for backup in backups:
            if backup.created_at >= daily_cutoff:
                to_keep.add(backup.backup_id)

        # Keep weekly backups (one per week)
        weekly_backups = {}
        for backup in backups:
            if daily_cutoff > backup.created_at >= weekly_cutoff:
                week = backup.created_at.isocalendar()[1]
                if week not in weekly_backups:
                    weekly_backups[week] = backup
                    to_keep.add(backup.backup_id)

        # Keep monthly backups (one per month)
        monthly_backups = {}
        for backup in backups:
            if weekly_cutoff > backup.created_at >= monthly_cutoff:
                month = backup.created_at.month
                if month not in monthly_backups:
                    monthly_backups[month] = backup
                    to_keep.add(backup.backup_id)

        # Delete backups not in keep set
        for backup in backups:
            if backup.backup_id not in to_keep:
                await self.backup_manager.delete_backup(backup.backup_id)

    async def _send_notification(
        self, schedule: BackupSchedule, result: ScheduledBackupResult
    ) -> None:
        """Send notification about backup result."""
        should_notify = (result.success and schedule.notify_on_success) or (
            not result.success and schedule.notify_on_failure
        )

        if not should_notify:
            return

        # In production, integrate with notification service
        # (email, Slack, PagerDuty, etc.)
        logger.info(
            f"Notification: Backup {schedule.name} - "
            f"{'SUCCESS' if result.success else 'FAILED'}"
        )


__all__ = ["BackupScheduler", "BackupSchedule", "ScheduleFrequency", "RetentionPolicy"]
