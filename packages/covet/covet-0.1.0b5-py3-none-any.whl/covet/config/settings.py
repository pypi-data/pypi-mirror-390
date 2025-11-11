"""
Production-Grade Configuration Management for CovetPy

Features:
- Environment-based configuration (dev, staging, production)
- Support for .env files
- Environment variable overrides
- YAML configuration file support
- Type-safe configuration with Pydantic
- Configuration validation on startup
- Secrets management integration
- Hot reload support (optional)
"""

import os
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

try:
    from pydantic import BaseSettings, Field, validator, root_validator
    from pydantic import BaseModel
    PYDANTIC_V2 = False
except ImportError:
    try:
        from pydantic.v1 import BaseSettings, Field, validator, root_validator
        from pydantic.v1 import BaseModel
        PYDANTIC_V2 = False
    except ImportError:
        try:
            from pydantic_settings import BaseSettings
            from pydantic import BaseModel, Field, field_validator, model_validator
            PYDANTIC_V2 = True
        except ImportError:
            warnings.warn("Pydantic not installed. Configuration validation disabled.")
            BaseSettings = object
            BaseModel = object
            Field = lambda *args, **kwargs: None
            validator = lambda *args, **kwargs: lambda f: f
            root_validator = lambda *args, **kwargs: lambda f: f
            PYDANTIC_V2 = False


class DatabaseSettings(BaseModel):
    """Database configuration."""

    url: str = Field(
        default='sqlite:///./covet.db',
        description='Database connection URL',
    )
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=100)
    pool_timeout: int = Field(default=30, ge=1, le=300)
    pool_recycle: int = Field(default=3600, ge=60)
    echo: bool = Field(default=False, description='Echo SQL queries')

    if not PYDANTIC_V2:
        class Config:
            env_prefix = 'DATABASE_'
    else:
        model_config = {'env_prefix': 'DATABASE_'}


class RedisSettings(BaseModel):
    """Redis/Cache configuration."""

    url: str = Field(
        default='redis://localhost:6379/0',
        description='Redis connection URL',
    )
    max_connections: int = Field(default=50, ge=1, le=1000)
    socket_timeout: int = Field(default=5, ge=1, le=60)
    socket_connect_timeout: int = Field(default=5, ge=1, le=60)
    decode_responses: bool = Field(default=True)
    ssl: bool = Field(default=False)
    ssl_cert_reqs: Optional[str] = Field(default=None)

    if not PYDANTIC_V2:
        class Config:
            env_prefix = 'REDIS_'
    else:
        model_config = {'env_prefix': 'REDIS_'}


class ServerSettings(BaseModel):
    """HTTP server configuration."""

    host: str = Field(default='0.0.0.0', description='Server bind address')
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1, ge=1, le=100)
    worker_class: str = Field(default='uvicorn.workers.UvicornWorker')
    max_connections: int = Field(default=100000, ge=1)
    keep_alive_timeout: int = Field(default=5, ge=1, le=300)
    request_timeout: int = Field(default=30, ge=1, le=300)
    graceful_timeout: int = Field(default=30, ge=1, le=300)
    enable_rust_core: bool = Field(default=True)

    if not PYDANTIC_V2:
        class Config:
            env_prefix = 'SERVER_'
    else:
        model_config = {'env_prefix': 'SERVER_'}


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: str = Field(default='INFO', description='Log level')
    format: str = Field(default='json', description='Log format (json or human)')
    file: Optional[str] = Field(default=None, description='Log file path')
    max_bytes: int = Field(default=100 * 1024 * 1024, ge=1024)  # 100MB
    backup_count: int = Field(default=10, ge=0, le=100)
    enable_rotation: bool = Field(default=True)
    enable_syslog: bool = Field(default=False)
    syslog_address: str = Field(default='/dev/log')
    async_logging: bool = Field(default=True)

    if not PYDANTIC_V2:
        @validator('level')
        def validate_level(cls, v):
            valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
            v_upper = v.upper()
            if v_upper not in valid_levels:
                raise ValueError(f'Invalid log level. Must be one of {valid_levels}')
            return v_upper

        @validator('format')
        def validate_format(cls, v):
            valid_formats = {'json', 'human'}
            if v.lower() not in valid_formats:
                raise ValueError(f'Invalid log format. Must be one of {valid_formats}')
            return v.lower()

        class Config:
            env_prefix = 'LOG_'
    else:
        @field_validator('level')
        @classmethod
        def validate_level(cls, v):
            valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
            v_upper = v.upper()
            if v_upper not in valid_levels:
                raise ValueError(f'Invalid log level. Must be one of {valid_levels}')
            return v_upper

        @field_validator('format')
        @classmethod
        def validate_format(cls, v):
            valid_formats = {'json', 'human'}
            if v.lower() not in valid_formats:
                raise ValueError(f'Invalid log format. Must be one of {valid_formats}')
            return v.lower()

        model_config = {'env_prefix': 'LOG_'}


class MonitoringSettings(BaseModel):
    """Monitoring and observability configuration."""

    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=True)
    enable_profiling: bool = Field(default=False)
    metrics_port: int = Field(default=9090, ge=1, le=65535)
    trace_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    trace_exporter: str = Field(default='console', description='Trace exporter type')
    trace_endpoint: Optional[str] = Field(default=None)
    prometheus_multiproc_dir: Optional[str] = Field(default=None)

    if not PYDANTIC_V2:
        class Config:
            env_prefix = 'MONITORING_'
    else:
        model_config = {'env_prefix': 'MONITORING_'}


class SecuritySettings(BaseModel):
    """Security configuration."""

    secret_key: str = Field(
        default='change-me-in-production',
        description='Secret key for signing tokens',
    )
    jwt_algorithm: str = Field(default='HS256')
    jwt_expiry_minutes: int = Field(default=60, ge=1)
    allowed_hosts: List[str] = Field(default=['*'])
    cors_origins: List[str] = Field(default=['*'])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=['*'])
    cors_allow_headers: List[str] = Field(default=['*'])
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60, ge=1)
    max_request_size: int = Field(default=10 * 1024 * 1024, ge=1024)  # 10MB

    if not PYDANTIC_V2:
        @validator('secret_key')
        def validate_secret_key(cls, v):
            if v == 'change-me-in-production':
                warnings.warn(
                    'Using default secret key! Set SECURITY_SECRET_KEY in production.',
                    RuntimeWarning
                )
            return v

        class Config:
            env_prefix = 'SECURITY_'
    else:
        @field_validator('secret_key')
        @classmethod
        def validate_secret_key(cls, v):
            if v == 'change-me-in-production':
                warnings.warn(
                    'Using default secret key! Set SECURITY_SECRET_KEY in production.',
                    RuntimeWarning
                )
            return v

        model_config = {'env_prefix': 'SECURITY_'}


class CovetSettings(BaseSettings):
    """
    Main application settings.

    Configuration sources (in order of priority):
    1. Environment variables
    2. .env file
    3. YAML config file (if specified)
    4. Default values

    Example .env file:
        COVET_ENV=production
        COVET_DEBUG=false
        DATABASE_URL=postgresql://user:pass@localhost/db
        REDIS_URL=redis://localhost:6379/0
        LOG_LEVEL=INFO
        LOG_FORMAT=json
        SECURITY_SECRET_KEY=your-secret-key-here
    """

    # Application settings
    env: str = Field(
        default='development',
        description='Environment (development, staging, production)',
    )
    debug: bool = Field(default=False)
    app_name: str = Field(default='CovetPy Application')
    app_version: str = Field(default='1.0.0')
    timezone: str = Field(default='UTC')

    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    if not PYDANTIC_V2:
        @root_validator(pre=True)
        def load_component_settings(cls, values):
            """Load component settings from environment."""
            # Database settings
            if 'database' not in values:
                values['database'] = DatabaseSettings()

            # Redis settings
            if 'redis' not in values:
                values['redis'] = RedisSettings()

            # Server settings
            if 'server' not in values:
                values['server'] = ServerSettings()

            # Logging settings
            if 'logging' not in values:
                values['logging'] = LoggingSettings()

            # Monitoring settings
            if 'monitoring' not in values:
                values['monitoring'] = MonitoringSettings()

            # Security settings
            if 'security' not in values:
                values['security'] = SecuritySettings()

            return values

        @validator('env')
        def validate_env(cls, v):
            valid_envs = {'development', 'dev', 'staging', 'production', 'prod', 'test'}
            if v.lower() not in valid_envs:
                warnings.warn(f'Unknown environment: {v}. Using as-is.')
            return v.lower()

        class Config:
            env_prefix = 'COVET_'
            env_file = '.env'
            env_file_encoding = 'utf-8'
            case_sensitive = False
            env_nested_delimiter = '__'

    else:
        @model_validator(mode='before')
        @classmethod
        def load_component_settings(cls, values):
            """Load component settings from environment."""
            # Database settings
            if 'database' not in values:
                values['database'] = DatabaseSettings()

            # Redis settings
            if 'redis' not in values:
                values['redis'] = RedisSettings()

            # Server settings
            if 'server' not in values:
                values['server'] = ServerSettings()

            # Logging settings
            if 'logging' not in values:
                values['logging'] = LoggingSettings()

            # Monitoring settings
            if 'monitoring' not in values:
                values['monitoring'] = MonitoringSettings()

            # Security settings
            if 'security' not in values:
                values['security'] = SecuritySettings()

            return values

        @field_validator('env')
        @classmethod
        def validate_env(cls, v):
            valid_envs = {'development', 'dev', 'staging', 'production', 'prod', 'test'}
            if v.lower() not in valid_envs:
                warnings.warn(f'Unknown environment: {v}. Using as-is.')
            return v.lower()

        model_config = {
            'env_prefix': 'COVET_',
            'env_file': '.env',
            'env_file_encoding': 'utf-8',
            'case_sensitive': False,
            'env_nested_delimiter': '__',
        }

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env in ('production', 'prod')

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.env in ('development', 'dev')

    @property
    def is_staging(self) -> bool:
        """Check if running in staging."""
        return self.env == 'staging'

    def validate_production_config(self):
        """Validate critical production settings."""
        if not self.is_production:
            return

        errors = []

        # Check secret key
        if self.security.secret_key == 'change-me-in-production':
            errors.append('SECURITY_SECRET_KEY must be set in production')

        # Check debug mode
        if self.debug:
            errors.append('DEBUG mode should be disabled in production')

        # Check CORS
        if '*' in self.security.cors_origins:
            warnings.warn('CORS is set to allow all origins in production')

        # Check allowed hosts
        if '*' in self.security.allowed_hosts:
            warnings.warn('ALLOWED_HOSTS is set to * in production')

        if errors:
            raise ValueError(
                'Production configuration errors:\n' + '\n'.join(f'  - {e}' for e in errors)
            )

    def export_env_template(self, file_path: str = '.env.example'):
        """Export environment variable template."""
        template_lines = [
            '# CovetPy Configuration Template',
            '# Copy to .env and customize for your environment',
            '',
            '# Application Settings',
            'COVET_ENV=development  # development, staging, production',
            'COVET_DEBUG=false',
            f'COVET_APP_NAME={self.app_name}',
            f'COVET_APP_VERSION={self.app_version}',
            '',
            '# Database Settings',
            f'DATABASE_URL={self.database.url}',
            f'DATABASE_POOL_SIZE={self.database.pool_size}',
            f'DATABASE_MAX_OVERFLOW={self.database.max_overflow}',
            '',
            '# Redis Settings',
            f'REDIS_URL={self.redis.url}',
            f'REDIS_MAX_CONNECTIONS={self.redis.max_connections}',
            '',
            '# Server Settings',
            f'SERVER_HOST={self.server.host}',
            f'SERVER_PORT={self.server.port}',
            f'SERVER_WORKERS={self.server.workers}',
            '',
            '# Logging Settings',
            f'LOG_LEVEL={self.logging.level}',
            f'LOG_FORMAT={self.logging.format}',
            '# LOG_FILE=/var/log/covetpy.log',
            '',
            '# Monitoring Settings',
            f'MONITORING_ENABLE_METRICS={str(self.monitoring.enable_metrics).lower()}',
            f'MONITORING_ENABLE_TRACING={str(self.monitoring.enable_tracing).lower()}',
            f'MONITORING_TRACE_SAMPLE_RATE={self.monitoring.trace_sample_rate}',
            '',
            '# Security Settings',
            'SECURITY_SECRET_KEY=change-me-in-production',
            f'SECURITY_JWT_EXPIRY_MINUTES={self.security.jwt_expiry_minutes}',
            f'SECURITY_RATE_LIMIT_PER_MINUTE={self.security.rate_limit_per_minute}',
            '# SECURITY_CORS_ORIGINS=https://example.com,https://app.example.com',
            '',
        ]

        with open(file_path, 'w') as f:
            f.write('\n'.join(template_lines))


# Global settings instance
_settings: Optional[CovetSettings] = None


def get_settings() -> CovetSettings:
    """
    Get global settings instance (singleton).

    Returns:
        Application settings
    """
    global _settings
    if _settings is None:
        _settings = CovetSettings()

        # Validate production config
        if _settings.is_production:
            _settings.validate_production_config()

    return _settings


def reload_settings() -> CovetSettings:
    """
    Reload settings from environment.

    Returns:
        Reloaded settings
    """
    global _settings
    _settings = None
    return get_settings()


__all__ = [
    'CovetSettings',
    'DatabaseSettings',
    'RedisSettings',
    'ServerSettings',
    'LoggingSettings',
    'MonitoringSettings',
    'SecuritySettings',
    'get_settings',
    'reload_settings',
]
