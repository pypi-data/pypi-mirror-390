"""
CovetPy Configuration Management

Comprehensive configuration system supporting:
- Environment-based configuration loading
- Type validation and conversion
- Configuration inheritance and overrides
- Secret management and security
- Dynamic configuration updates
"""

import json
import logging
import os
from dataclasses import dataclass, field, fields
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints

from covet.core.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

# Optional YAML support
try:
    import yaml

    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False

# Optional pydantic support for advanced validation and settings
try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

    # Create fallbacks for missing pydantic functionality
    def Field(**kwargs):
        """Dummy Field function when pydantic is not available"""
        return kwargs.get("default")

    class BaseSettings:
        """Minimal BaseSettings fallback"""

        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

        def model_dump(self):
            """Fallback for model_dump method"""
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

        @classmethod
        def from_file(cls, file_path):
            """Fallback from_file method"""
            raise ConfigurationError(
                "Advanced configuration loading requires pydantic. "
                "Install pydantic and pydantic-settings to use this feature."
            )

    def SettingsConfigDict(**kwargs):
        """Dummy SettingsConfigDict"""
        return kwargs


class Environment(str, Enum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    url: str
    pool_size: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    echo_pool: bool = False
    ssl_mode: str = "prefer"

    def __post_init__(self):
        """Validate database configuration."""
        if not self.url:
            raise ConfigurationError("Database URL is required")
        if self.pool_size <= 0:
            raise ConfigurationError("Pool size must be positive")


@dataclass
class RedisConfig:
    """Redis configuration settings."""

    url: str
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 30
    socket_connect_timeout: int = 30
    retry_on_timeout: bool = True
    max_connections: int = 50

    def __post_init__(self):
        """Validate Redis configuration."""
        if not self.url:
            raise ConfigurationError("Redis URL is required")


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    secret_key: str
    algorithm: str = "HS256"
    token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    cors_origins: List[str] = field(default_factory=list)
    csrf_secret: Optional[str] = None

    def __post_init__(self):
        """Validate security configuration."""
        if not self.secret_key:
            raise ConfigurationError("Secret key is required")
        if len(self.secret_key) < 32:
            raise ConfigurationError("Secret key must be at least 32 characters")


@dataclass
class LoggingConfig:
    """Logging configuration settings."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: List[str] = field(default_factory=lambda: ["console"])
    file_path: Optional[str] = None
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    structured: bool = True
    json_format: bool = True

    def __post_init__(self):
        """Validate logging configuration."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ConfigurationError(f"Invalid log level: {self.level}")


@dataclass
class ServerConfig:
    """Server configuration settings."""

    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1
    max_requests: int = 0
    max_requests_jitter: int = 0
    timeout: int = 30
    keep_alive: int = 2
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_ca_certs: Optional[str] = None

    def __post_init__(self):
        """Validate server configuration."""
        if self.port <= 0 or self.port > 65535:
            raise ConfigurationError("Port must be between 1 and 65535")
        if self.workers <= 0:
            raise ConfigurationError("Workers must be positive")


class Config(BaseSettings):
    """
    Main configuration class using Pydantic settings.

    Automatically loads configuration from environment variables,
    configuration files, and provides type validation.
    """

    model_config = (
        SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="allow",
        )
        if HAS_PYDANTIC
        else {}
    )

    def __init__(self, **kwargs) -> None:
        """Initialize configuration with optional kwargs override."""
        if HAS_PYDANTIC:
            super().__init__(**kwargs)
        else:
            # Manual initialization for non-pydantic case
            self._set_defaults()
            for key, value in kwargs.items():
                setattr(self, key, value)

    def _set_defaults(self):
        """Set default configuration values when pydantic is not available."""
        # Environment
        self.environment = Environment.DEVELOPMENT
        self.debug = False
        self.testing = False

        # Application
        self.app_name = "CovetPy App"
        self.app_version = "0.1.0"
        self.app_description = ""

        # Server
        self.server = ServerConfig(host="127.0.0.1", port=8000)

        # Database
        self.database = None

        # Redis
        self.redis = None

        # Security
        self.security = SecurityConfig(secret_key=os.urandom(32).hex())

        # Logging
        self.logging = LoggingConfig()

        # Features
        self.enable_docs = True
        self.enable_metrics = True
        self.enable_graphql = False

        # Performance
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.request_timeout = 60
        self.keepalive_timeout = 5

        # Advanced
        self.use_rust_extensions = False
        self.enable_jit = False

    # Environment settings
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    testing: bool = Field(default=False)

    # Application settings
    app_name: str = Field(default="CovetPy App")
    app_version: str = Field(default="0.1.0")
    app_description: str = Field(default="")

    # Server configuration
    server: ServerConfig = Field(default_factory=ServerConfig)

    # Database configuration
    database: Optional[DatabaseConfig] = Field(default=None)

    # Redis configuration
    redis: Optional[RedisConfig] = Field(default=None)

    # Security configuration
    security: SecurityConfig = Field(
        default_factory=lambda: SecurityConfig(secret_key=os.urandom(32).hex())
    )

    # Logging configuration
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Feature flags
    enable_docs: bool = Field(default=True)
    enable_metrics: bool = Field(default=True)
    enable_graphql: bool = Field(default=False)

    # Performance tuning
    max_request_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    request_timeout: int = Field(default=60)
    keepalive_timeout: int = Field(default=5)

    # Advanced features
    use_rust_extensions: bool = Field(default=False)
    enable_jit: bool = Field(default=False)

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key with optional default."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        setattr(self, key, value)

    def update(self, **kwargs) -> None:
        """Update multiple configuration values."""
        for key, value in kwargs.items():
            self.set(key, value)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "Config":
        """Load configuration from file (JSON, YAML)."""
        file_path = Path(file_path)

        try:
            with open(file_path, "r") as f:
                if file_path.suffix in [".yaml", ".yml"]:
                    if not HAS_YAML:
                        raise ConfigurationError(
                            "YAML support not available. Install PyYAML to load YAML files."
                        )
                    data = yaml.safe_load(f)
                elif file_path.suffix == ".json":
                    data = json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration file format: {file_path.suffix}"
                    )

            return cls(**data)

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {file_path}: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        if HAS_PYDANTIC:
            return self.model_dump()
        else:
            # Fallback: manually convert to dictionary
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def to_file(self, file_path: Union[str, Path], format: str = "yaml") -> None:
        """Save configuration to file."""
        file_path = Path(file_path)
        data = self.to_dict()

        try:
            if format.lower() in ["yaml", "yml"]:
                if not HAS_YAML:
                    raise ConfigurationError(
                        "YAML support not available. Install PyYAML to save in YAML format. "
                        "Alternatively, use JSON format."
                    )
                with open(file_path, "w") as f:
                    yaml.dump(data, f, default_flow_style=False)
            elif format.lower() == "json":
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
            else:
                raise ConfigurationError(f"Unsupported format: {format}")

        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration to {file_path}: {e}")


class ConfigManager:
    """
    Configuration manager for handling multiple environments and sources.

    Provides a centralized way to manage configuration loading, validation,
    and updates with support for environment-specific overrides.
    """

    def __init__(self, config_dir: Optional[Union[str, Path]] = None) -> None:
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self._configs: Dict[Environment, Config] = {}
        self._current_env = Environment.DEVELOPMENT
        self._watchers = []

    def load_environment(self, env: Environment) -> Config:
        """Load configuration for specific environment."""
        if env in self._configs:
            return self._configs[env]

        # Try to load from environment-specific file
        config_file = None

        # Try YAML first if available, otherwise try JSON
        if HAS_YAML:
            yaml_file = self.config_dir / f"{env.value}.yaml"
            if yaml_file.exists():
                config_file = yaml_file

        if config_file is None:
            json_file = self.config_dir / f"{env.value}.json"
            if json_file.exists():
                config_file = json_file

        # Load configuration
        if config_file and config_file.exists():
            config = Config.from_file(config_file)
        else:
            # Create default configuration for environment
            config = Config(environment=env)

        # Apply environment-specific overrides
        self._apply_environment_overrides(config, env)

        # Cache the configuration
        self._configs[env] = config

        return config

    def get_config(self, env: Optional[Environment] = None) -> Config:
        """Get configuration for environment."""
        env = env or self._current_env
        return self.load_environment(env)

    def set_current_environment(self, env: Environment) -> None:
        """Set the current environment."""
        self._current_env = env

    def reload(self, env: Optional[Environment] = None) -> Config:
        """Reload configuration for environment."""
        env = env or self._current_env
        if env in self._configs:
            del self._configs[env]

        config = self.load_environment(env)
        self._notify_watchers(config)
        return config

    def watch(self, callback: callable) -> None:
        """Add configuration change watcher."""
        self._watchers.append(callback)

    def _apply_environment_overrides(self, config: Config, env: Environment) -> None:
        """Apply environment-specific configuration overrides."""
        # Production overrides
        if env == Environment.PRODUCTION:
            config.debug = False
            config.testing = False
            config.server.workers = max(config.server.workers, 4)
            config.logging.level = "WARNING"
            config.enable_docs = False

        # Testing overrides
        elif env == Environment.TESTING:
            config.testing = True
            config.debug = True
            config.logging.level = "DEBUG"
            config.server.workers = 1

        # Development overrides
        elif env == Environment.DEVELOPMENT:
            config.debug = True
            config.logging.level = "DEBUG"
            config.server.workers = 1

        # Staging is similar to production but with debugging
        elif env == Environment.STAGING:
            config.debug = True
            config.logging.level = "INFO"

    def _notify_watchers(self, config: Config) -> None:
        """Notify configuration change watchers."""
        for callback in self._watchers:
            try:
                callback(config)
            except Exception:
                # Log error but don't fail the configuration reload
                logger.error("Configuration watcher failed: {e}")


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> Config:
    """Get current configuration."""
    return config_manager.get_config()


def load_config(
    env: Optional[Environment] = None, config_dir: Optional[Union[str, Path]] = None
) -> Config:
    """Load configuration for environment."""
    if config_dir:
        global config_manager
        config_manager = ConfigManager(config_dir)

    if env:
        config_manager.set_current_environment(env)

    return config_manager.get_config()
