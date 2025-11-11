"""
Database-Specific Backup Strategies

Implements backup strategies for different database systems using
native tools and best practices for each platform.
"""

import asyncio
import logging
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BackupStrategy(ABC):
    """
    Abstract base class for database backup strategies.

    Each database type (PostgreSQL, MySQL, SQLite, etc.) implements
    its own strategy using native backup tools and best practices.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize backup strategy.

        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.database_type = config.get("database_type", "unknown")
        self.database_name = config.get("database", "")
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 0)
        self.user = config.get("user", "")
        self.password = config.get("password", "")

    @abstractmethod
    async def create_backup(
        self,
        output_path: str,
        tables: Optional[List[str]] = None,
        schemas: Optional[List[str]] = None,
        **options,
    ) -> Dict[str, Any]:
        """
        Create database backup.

        Args:
            output_path: Path where backup file will be created
            tables: List of tables to backup (None = all tables)
            schemas: List of schemas to backup (None = all schemas)
            **options: Additional database-specific options

        Returns:
            Dictionary with backup metadata
        """
        pass

    @abstractmethod
    async def get_database_version(self) -> str:
        """Get database server version."""
        pass

    @abstractmethod
    async def get_database_size(self) -> int:
        """Get estimated database size in bytes."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test database connection."""
        pass


class PostgreSQLBackupStrategy(BackupStrategy):
    """
    PostgreSQL backup strategy using pg_dump and pg_basebackup.

    Features:
    - Full logical backups with pg_dump
    - Base backups with pg_basebackup for PITR
    - Custom format for compression and selective restore
    - Parallel dump for large databases
    - Transaction log archiving for point-in-time recovery
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pg_dump_path = config.get("pg_dump_path", "pg_dump")
        self.pg_basebackup_path = config.get("pg_basebackup_path", "pg_basebackup")
        self.psql_path = config.get("psql_path", "psql")

    async def create_backup(
        self,
        output_path: str,
        tables: Optional[List[str]] = None,
        schemas: Optional[List[str]] = None,
        format: str = "custom",  # plain, custom, directory, tar
        jobs: int = 1,  # Parallel dump jobs
        compress_level: int = 6,  # 0-9
        **options,
    ) -> Dict[str, Any]:
        """
        Create PostgreSQL backup using pg_dump.

        Args:
            output_path: Path to output file
            tables: Specific tables to backup
            schemas: Specific schemas to backup
            format: Dump format (custom, plain, directory, tar)
            jobs: Number of parallel jobs (directory format only)
            compress_level: Compression level 0-9 (custom/directory format)
            **options: Additional pg_dump options

        Returns:
            Backup metadata
        """
        logger.info(f"Creating PostgreSQL backup: {self.database_name}")

        # Build pg_dump command
        cmd = [
            self.pg_dump_path,
            f"--host={self.host}",
            f"--port={self.port}",
            f"--username={self.user}",
            f"--dbname={self.database_name}",
            f"--format={format}",
            f"--file={output_path}",
        ]

        # Add compression level for custom/directory format
        if format in ["custom", "directory"]:
            cmd.append(f"--compress={compress_level}")

        # Add parallel jobs for directory format
        if format == "directory" and jobs > 1:
            cmd.append(f"--jobs={jobs}")

        # Add specific tables
        if tables:
            for table in tables:
                cmd.extend(["--table", table])

        # Add specific schemas
        if schemas:
            for schema in schemas:
                cmd.extend(["--schema", schema])

        # Add verbose output
        cmd.append("--verbose")

        # Set password via environment variable
        env = os.environ.copy()
        if self.password:
            env["PGPASSWORD"] = self.password

        # Execute backup
        start_time = datetime.now()
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"pg_dump failed: {error_msg}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Get file size
            file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0

            # Get WAL position for PITR
            wal_info = await self._get_wal_position()

            logger.info(
                f"PostgreSQL backup completed: {output_path} "
                f"({file_size / (1024**2):.2f} MB) in {duration:.2f}s"
            )

            return {
                "database_version": await self.get_database_version(),
                "backup_size_bytes": file_size,
                "duration_seconds": duration,
                "format": format,
                "compression_level": (compress_level if format in ["custom", "directory"] else 0),
                "parallel_jobs": jobs if format == "directory" else 1,
                "tables_included": tables or [],
                "schemas_included": schemas or [],
                "wal_start_lsn": wal_info.get("current_lsn"),
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
            }

        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            raise

    async def create_base_backup(
        self, output_path: str, wal_method: str = "fetch", **options
    ) -> Dict[str, Any]:
        """
        Create PostgreSQL base backup using pg_basebackup for PITR.

        Args:
            output_path: Directory for base backup
            wal_method: WAL method (fetch, stream, none)
            **options: Additional pg_basebackup options

        Returns:
            Backup metadata
        """
        logger.info(f"Creating PostgreSQL base backup: {self.database_name}")

        # Create output directory
        Path(output_path).mkdir(parents=True, exist_ok=True)

        # Build pg_basebackup command
        cmd = [
            self.pg_basebackup_path,
            f"--host={self.host}",
            f"--port={self.port}",
            f"--username={self.user}",
            f"--pgdata={output_path}",
            f"--wal-method={wal_method}",
            "--format=tar",
            "--gzip",
            "--progress",
            "--verbose",
        ]

        # Set password via environment variable
        env = os.environ.copy()
        if self.password:
            env["PGPASSWORD"] = self.password

        # Execute backup
        start_time = datetime.now()
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"pg_basebackup failed: {error_msg}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Calculate total size of backup directory
            total_size = sum(f.stat().st_size for f in Path(output_path).rglob("*") if f.is_file())

            logger.info(
                f"PostgreSQL base backup completed: {output_path} "
                f"({total_size / (1024**2):.2f} MB) in {duration:.2f}s"
            )

            return {
                "database_version": await self.get_database_version(),
                "backup_size_bytes": total_size,
                "duration_seconds": duration,
                "wal_method": wal_method,
                "backup_type": "base_backup",
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
            }

        except Exception as e:
            logger.error(f"PostgreSQL base backup failed: {e}")
            # Clean up partial backup
            if Path(output_path).exists():
                shutil.rmtree(output_path)
            raise

    async def _get_wal_position(self) -> Dict[str, Any]:
        """Get current WAL position for PITR."""
        try:
            cmd = [
                self.psql_path,
                f"--host={self.host}",
                f"--port={self.port}",
                f"--username={self.user}",
                f"--dbname={self.database_name}",
                "--tuples-only",
                "--no-align",
                "--command=SELECT pg_current_wal_lsn();",
            ]

            env = os.environ.copy()
            if self.password:
                env["PGPASSWORD"] = self.password

            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0 and stdout:
                current_lsn = stdout.decode().strip()
                return {"current_lsn": current_lsn}

        except Exception as e:
            logger.warning(f"Failed to get WAL position: {e}")

        return {}

    async def get_database_version(self) -> str:
        """Get PostgreSQL server version."""
        try:
            cmd = [
                self.psql_path,
                f"--host={self.host}",
                f"--port={self.port}",
                f"--username={self.user}",
                f"--dbname={self.database_name}",
                "--tuples-only",
                "--no-align",
                "--command=SHOW server_version;",
            ]

            env = os.environ.copy()
            if self.password:
                env["PGPASSWORD"] = self.password

            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0 and stdout:
                return stdout.decode().strip()

        except Exception as e:
            logger.warning(f"Failed to get database version: {e}")

        return "unknown"

    async def get_database_size(self) -> int:
        """Get PostgreSQL database size in bytes."""
        try:
            # SECURITY FIX: Validate database name to prevent SQL injection
            import re

            # Validate database name contains only alphanumeric, underscore, and hyphen
            if not re.match(r"^[a-zA-Z0-9_-]+$", self.database_name):
                logger.error(f"Invalid database name format: {self.database_name}")
                return 0

            cmd = [
                self.psql_path,
                f"--host={self.host}",
                f"--port={self.port}",
                f"--username={self.user}",
                f"--dbname={self.database_name}",
                "--tuples-only",
                "--no-align",
                f"--command=SELECT pg_database_size('{self.database_name}');",
            ]

            env = os.environ.copy()
            if self.password:
                env["PGPASSWORD"] = self.password

            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0 and stdout:
                return int(stdout.decode().strip())

        except Exception as e:
            logger.warning(f"Failed to get database size: {e}")

        return 0

    async def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
        try:
            cmd = [
                self.psql_path,
                f"--host={self.host}",
                f"--port={self.port}",
                f"--username={self.user}",
                f"--dbname={self.database_name}",
                "--command=SELECT 1;",
            ]

            env = os.environ.copy()
            if self.password:
                env["PGPASSWORD"] = self.password

            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            await result.wait()
            return result.returncode == 0

        except Exception:
            return False


class MySQLBackupStrategy(BackupStrategy):
    """
    MySQL/MariaDB backup strategy using mysqldump.

    Features:
    - Full logical backups with mysqldump
    - Single transaction dumps for consistency
    - Compression support
    - Binary log position capture for replication/PITR
    - Selective table and database backup
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mysqldump_path = config.get("mysqldump_path", "mysqldump")
        self.mysql_path = config.get("mysql_path", "mysql")

    async def create_backup(
        self,
        output_path: str,
        tables: Optional[List[str]] = None,
        schemas: Optional[List[str]] = None,
        single_transaction: bool = True,
        master_data: int = 0,  # 0=no, 1=active, 2=commented
        **options,
    ) -> Dict[str, Any]:
        """
        Create MySQL backup using mysqldump.

        Args:
            output_path: Path to output file
            tables: Specific tables to backup
            schemas: Specific databases to backup
            single_transaction: Use single transaction for consistency
            master_data: Include binary log position (0=no, 1=active, 2=commented)
            **options: Additional mysqldump options

        Returns:
            Backup metadata
        """
        logger.info(f"Creating MySQL backup: {self.database_name}")

        # Build mysqldump command
        cmd = [
            self.mysqldump_path,
            f"--host={self.host}",
            f"--port={self.port}",
            f"--user={self.user}",
        ]

        # SECURITY FIX: Use environment variable for password instead of command line
        # Passwords on command line are visible in process listings (ps aux)
        env = os.environ.copy()
        if self.password:
            env["MYSQL_PWD"] = self.password

        # Add single transaction for InnoDB consistency
        if single_transaction:
            cmd.append("--single-transaction")

        # Add master data for binary log position
        if master_data > 0:
            cmd.append(f"--master-data={master_data}")

        # Add routines, triggers, events
        cmd.extend(["--routines", "--triggers", "--events"])

        # Add extended insert for faster restores
        cmd.append("--extended-insert")

        # Add result file
        cmd.append(f"--result-file={output_path}")

        # Add databases or tables
        if schemas:
            cmd.append("--databases")
            cmd.extend(schemas)
        elif tables:
            cmd.append(self.database_name)
            cmd.extend(tables)
        else:
            cmd.append("--databases")
            cmd.append(self.database_name)

        # Execute backup
        start_time = datetime.now()
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"mysqldump failed: {error_msg}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Get file size
            file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0

            logger.info(
                f"MySQL backup completed: {output_path} "
                f"({file_size / (1024**2):.2f} MB) in {duration:.2f}s"
            )

            return {
                "database_version": await self.get_database_version(),
                "backup_size_bytes": file_size,
                "duration_seconds": duration,
                "single_transaction": single_transaction,
                "master_data": master_data,
                "tables_included": tables or [],
                "schemas_included": schemas or [],
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
            }

        except Exception as e:
            logger.error(f"MySQL backup failed: {e}")
            raise

    async def get_database_version(self) -> str:
        """Get MySQL server version."""
        try:
            cmd = [
                self.mysql_path,
                f"--host={self.host}",
                f"--port={self.port}",
                f"--user={self.user}",
                "--skip-column-names",
                "--execute=SELECT VERSION();",
            ]

            # SECURITY FIX: Use environment variable for password
            env = os.environ.copy()
            if self.password:
                env["MYSQL_PWD"] = self.password

            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0 and stdout:
                return stdout.decode().strip()

        except Exception as e:
            logger.warning(f"Failed to get database version: {e}")

        return "unknown"

    async def get_database_size(self) -> int:
        """Get MySQL database size in bytes."""
        try:
            # SECURITY FIX: Use parameterized query to prevent SQL injection
            # Database name should be validated/sanitized before use
            import re

            # Validate database name contains only alphanumeric, underscore, and hyphen
            if not re.match(r"^[a-zA-Z0-9_-]+$", self.database_name):
                logger.error(f"Invalid database name format: {self.database_name}")
                return 0

            cmd = [
                self.mysql_path,
                f"--host={self.host}",
                f"--port={self.port}",
                f"--user={self.user}",
                "--skip-column-names",
                f"--execute=SELECT SUM(data_length + index_length) FROM information_schema.tables WHERE table_schema = '{self.database_name}';",  # nosec B608 - identifiers validated
            ]

            # SECURITY FIX: Use environment variable for password
            env = os.environ.copy()
            if self.password:
                env["MYSQL_PWD"] = self.password

            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0 and stdout:
                size_str = stdout.decode().strip()
                return int(size_str) if size_str and size_str != "NULL" else 0

        except Exception as e:
            logger.warning(f"Failed to get database size: {e}")

        return 0

    async def test_connection(self) -> bool:
        """Test MySQL connection."""
        try:
            cmd = [
                self.mysql_path,
                f"--host={self.host}",
                f"--port={self.port}",
                f"--user={self.user}",
                "--execute=SELECT 1;",
            ]

            # SECURITY FIX: Use environment variable for password
            env = os.environ.copy()
            if self.password:
                env["MYSQL_PWD"] = self.password

            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            await result.wait()
            return result.returncode == 0

        except Exception:
            return False


class SQLiteBackupStrategy(BackupStrategy):
    """
    SQLite backup strategy using file copy and SQLite backup API.

    Features:
    - Online backup using SQLite backup API
    - Simple file copy for offline backups
    - VACUUM INTO for optimization during backup
    - Consistent snapshot with WAL mode
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.database_path = config.get("database", "")

    async def create_backup(
        self,
        output_path: str,
        method: str = "copy",  # copy, backup_api, vacuum
        **options,
    ) -> Dict[str, Any]:
        """
        Create SQLite backup using specified method.

        Args:
            output_path: Path to output file
            method: Backup method (copy, backup_api, vacuum)
            **options: Additional options

        Returns:
            Backup metadata
        """
        logger.info(f"Creating SQLite backup: {self.database_path}")

        start_time = datetime.now()

        try:
            if method == "copy":
                # Simple file copy (database should be idle)
                await self._backup_copy(output_path)
            elif method == "backup_api":
                # Use SQLite backup API for online backup
                await self._backup_api(output_path)
            elif method == "vacuum":
                # Use VACUUM INTO for optimized backup
                await self._backup_vacuum(output_path)
            else:
                raise ValueError(f"Unknown backup method: {method}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Get file size
            file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0

            logger.info(
                f"SQLite backup completed: {output_path} "
                f"({file_size / (1024**2):.2f} MB) in {duration:.2f}s"
            )

            return {
                "database_version": await self.get_database_version(),
                "backup_size_bytes": file_size,
                "duration_seconds": duration,
                "backup_method": method,
            }

        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
            raise

    async def _backup_copy(self, output_path: str) -> None:
        """Backup using file copy."""
        # Simple file copy
        await asyncio.to_thread(shutil.copy2, self.database_path, output_path)

    async def _backup_api(self, output_path: str) -> None:
        """Backup using SQLite backup API."""
        import aiosqlite

        # Open source database
        async with aiosqlite.connect(self.database_path) as source:
            # Create backup database
            async with aiosqlite.connect(output_path) as backup:
                # Perform backup
                await source.backup(backup)

    async def _backup_vacuum(self, output_path: str) -> None:
        """Backup using VACUUM INTO (SQLite 3.27.0+)."""
        import aiosqlite

        async with aiosqlite.connect(self.database_path) as conn:
            await conn.execute(f"VACUUM INTO '{output_path}'")

    async def get_database_version(self) -> str:
        """Get SQLite version."""
        try:
            import aiosqlite

            async with aiosqlite.connect(self.database_path) as conn:
                cursor = await conn.execute("SELECT sqlite_version()")
                row = await cursor.fetchone()
                return f"SQLite {row[0]}" if row else "unknown"

        except Exception as e:
            logger.warning(f"Failed to get database version: {e}")
            return "unknown"

    async def get_database_size(self) -> int:
        """Get SQLite database file size."""
        try:
            return Path(self.database_path).stat().st_size
        except Exception:
            return 0

    async def test_connection(self) -> bool:
        """Test SQLite connection."""
        try:
            import aiosqlite

            async with aiosqlite.connect(self.database_path) as conn:
                cursor = await conn.execute("SELECT 1")
                await cursor.fetchone()
                return True
        except Exception:
            return False


__all__ = [
    "BackupStrategy",
    "PostgreSQLBackupStrategy",
    "MySQLBackupStrategy",
    "SQLiteBackupStrategy",
]
