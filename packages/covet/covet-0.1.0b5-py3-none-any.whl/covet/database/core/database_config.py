"""
Database Configuration Management

Enterprise-grade configuration management for multi-database environments
with advanced connection pooling, failover, and performance tuning.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse


class DatabaseType(Enum):
    """Supported database types with their characteristics."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CASSANDRA = "cassandra"
    SQLITE = "sqlite"

    @property
    def is_relational(self) -> bool:
        """Check if database is relational."""
        return self in {self.POSTGRESQL, self.MYSQL, self.SQLITE}

    @property
    def is_nosql(self) -> bool:
        """Check if database is NoSQL."""
        return self in {self.MONGODB, self.REDIS, self.CASSANDRA}

    @property
    def supports_transactions(self) -> bool:
        """Check if database supports ACID transactions."""
        return self in {self.POSTGRESQL, self.MYSQL, self.MONGODB}

    @property
    def supports_sharding(self) -> bool:
        """Check if database supports horizontal sharding."""
        return self in {self.POSTGRESQL, self.MYSQL, self.MONGODB, self.CASSANDRA}


@dataclass
class SSLConfig:
    """SSL/TLS configuration for secure database connections."""

    enabled: bool = True
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_file: Optional[str] = None
    verify_mode: str = "CERT_REQUIRED"  # CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
    check_hostname: bool = True
    ciphers: Optional[str] = None


@dataclass
class ReplicationConfig:
    """Replication configuration for read/write splitting."""

    enabled: bool = False
    read_replicas: List[str] = field(default_factory=list)
    write_preference: str = "primary"  # primary, secondary, nearest
    read_preference: str = "secondary_preferred"
    max_staleness_seconds: int = 120
    replica_set_name: Optional[str] = None


@dataclass
class ShardingConfig:
    """Sharding configuration for horizontal scaling."""

    enabled: bool = False
    shard_key: Optional[str] = None
    num_shards: int = 1
    shard_strategy: str = "hash"  # hash, range, directory
    auto_rebalance: bool = True
    migration_threshold: float = 0.8  # Trigger migration at 80% capacity


@dataclass
class BackupConfig:
    """Backup and recovery configuration."""

    enabled: bool = True
    schedule: str = "0 2 * * *"  # Daily at 2 AM
    retention_days: int = 30
    compression: bool = True
    encryption: bool = True
    s3_bucket: Optional[str] = None
    local_path: str = "/var/backups/covet"
    point_in_time_recovery: bool = True


@dataclass
class MonitoringConfig:
    """Database monitoring and alerting configuration."""

    enabled: bool = True
    slow_query_threshold_ms: int = 1000
    connection_pool_alerts: bool = True
    disk_space_threshold: float = 0.85  # Alert at 85% disk usage
    cpu_threshold: float = 0.80  # Alert at 80% CPU
    memory_threshold: float = 0.85  # Alert at 85% memory
    metrics_retention_days: int = 90
    export_prometheus: bool = True
    export_grafana: bool = True


@dataclass
class DatabaseConfig:
    """
    Comprehensive database configuration for enterprise deployments.

    Supports multi-database environments with advanced features like
    connection pooling, replication, sharding, monitoring, and backup.
    """

    # Basic connection settings
    host: str = "localhost"
    port: int = 5432
    database: str = "covet"
    username: str = "covet"
    password: str = ""
    db_type: DatabaseType = DatabaseType.POSTGRESQL

    # Connection pool settings
    min_pool_size: int = 5
    max_pool_size: int = 100
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True

    # Performance settings
    connect_timeout: int = 30
    command_timeout: int = 300
    keepalive_interval: int = 30
    tcp_keepalive: bool = True

    # Advanced configurations
    ssl: SSLConfig = field(default_factory=SSLConfig)
    replication: ReplicationConfig = field(default_factory=ReplicationConfig)
    sharding: ShardingConfig = field(default_factory=ShardingConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    monitoring: "MonitoringConfig" = field(default_factory=lambda: MonitoringConfig())

    # Additional options
    options: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_url(cls, url: str, **overrides) -> "DatabaseConfig":
        """
        Create configuration from database URL.

        Examples:
            postgresql://user:pass@host:5432/dbname
            mysql://user:pass@host:3306/dbname
            mongodb://user:pass@host:27017/dbname
            redis://host:6379/0
        """
        parsed = urlparse(url)

        # Map scheme to database type
        scheme_mapping = {
            "postgresql": DatabaseType.POSTGRESQL,
            "postgres": DatabaseType.POSTGRESQL,
            "mysql": DatabaseType.MYSQL,
            "mongodb": DatabaseType.MONGODB,
            "mongo": DatabaseType.MONGODB,
            "redis": DatabaseType.REDIS,
            "cassandra": DatabaseType.CASSANDRA,
            "sqlite": DatabaseType.SQLITE,
        }

        db_type = scheme_mapping.get(parsed.scheme)
        if not db_type:
            raise ValueError(f"Unsupported database scheme: {parsed.scheme}")

        # Default ports by database type
        default_ports = {
            DatabaseType.POSTGRESQL: 5432,
            DatabaseType.MYSQL: 3306,
            DatabaseType.MONGODB: 27017,
            DatabaseType.REDIS: 6379,
            DatabaseType.CASSANDRA: 9042,
            DatabaseType.SQLITE: 0,
        }

        config = cls(
            host=parsed.hostname or "localhost",
            port=parsed.port or default_ports[db_type],
            database=parsed.path.lstrip("/") if parsed.path else "covet",
            username=parsed.username or "covet",
            password=parsed.password or "",
            db_type=db_type,
            **overrides,
        )

        return config

    @classmethod
    def from_env(cls, prefix: str = "DB_") -> "DatabaseConfig":
        """
        Create configuration from environment variables.

        Environment variables:
            DB_URL - Full database URL (overrides individual settings)
            DB_HOST - Database host
            DB_PORT - Database port
            DB_NAME - Database name
            DB_USER - Database username
            DB_PASS - Database password
            DB_TYPE - Database type
        """
        url = os.getenv(f"{prefix}URL")
        if url:
            return cls.from_url(url)

        return cls(
            host=os.getenv(f"{prefix}HOST", "localhost"),
            port=int(os.getenv(f"{prefix}PORT", "5432")),
            database=os.getenv(f"{prefix}NAME", "covet"),
            username=os.getenv(f"{prefix}USER", "covet"),
            password=os.getenv(f"{prefix}PASS", ""),
            db_type=DatabaseType(os.getenv(f"{prefix}TYPE", "postgresql")),
        )

    def get_connection_url(self) -> str:
        """Generate connection URL from configuration."""
        if self.db_type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database}"

        auth = ""
        if self.username:
            auth = f"{self.username}"
            if self.password:
                auth += f":{self.password}"
            auth += "@"

        scheme_mapping = {
            DatabaseType.POSTGRESQL: "postgresql",
            DatabaseType.MYSQL: "mysql",
            DatabaseType.MONGODB: "mongodb",
            DatabaseType.REDIS: "redis",
            DatabaseType.CASSANDRA: "cassandra",
        }

        scheme = scheme_mapping[self.db_type]
        return f"{scheme}://{auth}{self.host}:{self.port}/{self.database}"

    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues.

        Returns:
            List of validation error messages
        """
        errors = []

        # Basic validation
        if not self.host:
            errors.append("Host is required")

        if self.port <= 0 or self.port > 65535:
            errors.append("Port must be between 1 and 65535")

        if not self.database and self.db_type != DatabaseType.REDIS:
            errors.append("Database name is required")

        # Pool validation
        if self.min_pool_size < 1:
            errors.append("Minimum pool size must be at least 1")

        if self.max_pool_size < self.min_pool_size:
            errors.append("Maximum pool size must be >= minimum pool size")

        if self.max_pool_size > 10000:
            errors.append("Maximum pool size should not exceed 10,000 for optimal performance")

        # Timeout validation
        if self.connect_timeout < 1:
            errors.append("Connect timeout must be at least 1 second")

        if self.command_timeout < 1:
            errors.append("Command timeout must be at least 1 second")

        # SSL validation
        if self.ssl.enabled and self.ssl.cert_file and not os.path.exists(self.ssl.cert_file):
            errors.append(f"SSL certificate file not found: {self.ssl.cert_file}")

        # Replication validation
        if self.replication.enabled and not self.replication.read_replicas:
            errors.append("Read replicas must be specified when replication is enabled")

        # Sharding validation
        if self.sharding.enabled:
            if not self.sharding.shard_key:
                errors.append("Shard key is required when sharding is enabled")
            if self.sharding.num_shards < 1:
                errors.append("Number of shards must be at least 1")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.username,
            "password": "***" if self.password else "",
            "db_type": self.db_type.value,
            "min_pool_size": self.min_pool_size,
            "max_pool_size": self.max_pool_size,
            "pool_timeout": self.pool_timeout,
            "connect_timeout": self.connect_timeout,
            "command_timeout": self.command_timeout,
            "ssl_enabled": self.ssl.enabled,
            "replication_enabled": self.replication.enabled,
            "sharding_enabled": self.sharding.enabled,
            "backup_enabled": self.backup.enabled,
            "monitoring_enabled": self.monitoring.enabled,
        }


class DatabaseConfigManager:
    """
    Centralized configuration management for multi-database environments.

    Supports configuration validation, environment-based overrides,
    and runtime configuration updates with zero-downtime deployment.
    """

    def __init__(self) -> None:
        self._configs: Dict[str, DatabaseConfig] = {}
        self._default_config: Optional[DatabaseConfig] = None

    def add_database(self, name: str, config: DatabaseConfig) -> None:
        """Add database configuration."""
        errors = config.validate()
        if errors:
            raise ValueError(f"Invalid configuration for {name}: {', '.join(errors)}")

        self._configs[name] = config

        if self._default_config is None:
            self._default_config = config

    def get_database(self, name: str = "default") -> DatabaseConfig:
        """Get database configuration by name."""
        if name == "default":
            if self._default_config is None:
                raise ValueError("No default database configured")
            return self._default_config

        if name not in self._configs:
            raise ValueError(f"Database '{name}' not configured")

        return self._configs[name]

    def list_databases(self) -> List[str]:
        """List all configured database names."""
        return list(self._configs.keys())

    def set_default(self, name: str) -> None:
        """Set default database."""
        self._default_config = self.get_database(name)

    def remove_database(self, name: str) -> None:
        """Remove database configuration."""
        if name in self._configs:
            del self._configs[name]

        if self._default_config and name == "default":
            self._default_config = None

    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all configurations and return errors by database name."""
        all_errors = {}

        for name, config in self._configs.items():
            errors = config.validate()
            if errors:
                all_errors[name] = errors

        return all_errors
