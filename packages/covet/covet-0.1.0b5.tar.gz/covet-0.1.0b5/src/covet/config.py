"""
Secure configuration management for CovetPy.

This module provides a secure way to manage application configuration,
including proper environment variable handling and secret management.
"""

import os
import secrets
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

# Optional pydantic imports for backward compatibility
try:
    from pydantic import Field as PydanticField
    from pydantic import field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

# Use custom validation framework by default
from covet.core.validation import (
    Field,
    ValidatedModel,
    ValidationError,
    Validator,
)


class DatabaseURLValidator(Validator):
    """Custom validator for database URLs."""

    def validate(self, value: Any, field) -> str:
        """Validate database URL format."""
        if not value:
            raise ValidationError("Database URL cannot be empty", field.name)

        parsed = urlparse(value)
        if not parsed.scheme:
            raise ValidationError(
                "Database URL must include a scheme (e.g., postgresql://)", field.name
            )

        # Warn about unsafe configurations in production
        if parsed.scheme == "sqlite" and "COVET_ENV" in os.environ:
            env = os.environ["COVET_ENV"]
            if env in ["production", "staging"]:
                import warnings

                warnings.warn(
                    "SQLite should not be used in production environments",
                    UserWarning,
                    stacklevel=2,
                )

        return value

    def __str__(self) -> str:
        return "DatabaseURLValidator"


class JWTSecretKeyValidator(Validator):
    """Custom validator for JWT secret keys."""

    def validate(self, value: Any, field) -> str:
        """Validate JWT secret key strength."""
        if len(value) < 32:
            raise ValidationError("JWT secret key must be at least 32 characters long", field.name)
        return value

    def __str__(self) -> str:
        return "JWTSecretKeyValidator"


class BcryptRoundsValidator(Validator):
    """Custom validator for bcrypt rounds."""

    def validate(self, value: Any, field) -> int:
        """Validate bcrypt rounds."""
        if value < 10:
            raise ValidationError("Bcrypt rounds must be at least 10 for security", field.name)
        if value > 15:
            import warnings

            warnings.warn(
                "Bcrypt rounds > 15 may cause performance issues",
                UserWarning,
                stacklevel=2,
            )
        return value

    def __str__(self) -> str:
        return "BcryptRoundsValidator"


class CORSOriginsValidator(Validator):
    """Custom validator for CORS origins."""

    def validate(self, value: Any, field) -> list[str]:
        """Validate CORS origins."""
        if "*" in value and len(value) > 1:
            raise ValidationError("CORS origins cannot contain '*' with other origins", field.name)

        # Check for production environment
        if "COVET_ENV" in os.environ:
            env = os.environ["COVET_ENV"]
            if env == "production" and "*" in value:
                import warnings

                warnings.warn(
                    "CORS wildcard (*) should not be used in production",
                    UserWarning,
                    stacklevel=2,
                )

        return value

    def __str__(self) -> str:
        return "CORSOriginsValidator"


class EnvironmentValidator(Validator):
    """Custom validator for environment values."""

    def validate(self, value: Any, field) -> Any:
        """Validate and convert environment."""
        if isinstance(value, str):
            try:
                # Import Environment here to avoid circular imports

                valid_values = ["development", "testing", "staging", "production"]
                if value.lower() not in valid_values:
                    raise ValidationError(
                        f"Invalid environment. Must be one of: {valid_values}",
                        field.name,
                    )
                # Return the original enum value if it exists
                for env in [
                    Environment.DEVELOPMENT,
                    Environment.TESTING,
                    Environment.STAGING,
                    Environment.PRODUCTION,
                ]:
                    if env.value == value.lower():
                        return env
                # Fallback to creating from string
                return value.lower()
            except Exception:
                valid_envs = ["development", "testing", "staging", "production"]
                raise ValidationError(
                    f"Invalid environment. Must be one of: {valid_envs}", field.name
                )
        return value

    def __str__(self) -> str:
        return "EnvironmentValidator"


class DebugProductionValidator(Validator):
    """Custom validator to ensure debug is not enabled in production."""

    def __init__(self, environment_field: str = "environment") -> None:
        self.environment_field = environment_field

    def validate(self, value: Any, field) -> bool:
        """Ensure debug is not enabled in production."""
        # This validator needs access to the model instance
        # For now, we'll check environment variables
        env = os.environ.get("COVET_ENV", "").lower()
        if env == "production" and value:
            raise ValidationError("Debug mode cannot be enabled in production", field.name)
        return value

    def __str__(self) -> str:
        return "DebugProductionValidator"


class Environment(str, Enum):
    """Environment enumeration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseSettingsModel(ValidatedModel):
    """Base class for settings models with environment variable support."""

    @classmethod
    def _get_env_value(cls, field_name: str, env_prefix: str = "") -> Any:
        """Get value from environment variables."""
        env_name = f"{env_prefix}{field_name.upper()}"
        return os.environ.get(env_name)

    def __init__(self, **data) -> None:
        """Initialize with environment variable loading."""
        # Load from environment variables first
        env_data = self._load_from_env()
        # Merge with provided data (provided data takes precedence)
        merged_data = {**env_data, **data}
        super().__init__(**merged_data)

    def _load_from_env(self) -> dict[str, Any]:
        """Load configuration from environment variables."""
        env_data = {}
        env_prefix = getattr(self, "_env_prefix", "")

        for field_name in self._field_metadata.keys():
            env_value = self._get_env_value(field_name, env_prefix)
            if env_value is not None:
                env_data[field_name] = env_value

        return env_data


class DatabaseSettings(BaseSettingsModel):
    """Database configuration settings."""

    _env_prefix = "COVET_DB_"

    url: str = Field(
        default="sqlite:///./covet.db",
        description="Database connection URL",
        validators=[DatabaseURLValidator()],
    )
    pool_size: int = Field(default=10, description="Connection pool size", min_value=1)
    max_overflow: int = Field(default=20, description="Connection pool max overflow", min_value=0)
    pool_timeout: int = Field(default=30, description="Connection pool timeout", min_value=1)
    pool_recycle: int = Field(default=3600, description="Connection pool recycle time", min_value=0)
    echo: bool = Field(default=False, description="Echo SQL queries")

    # Redis configuration for caching and session storage
    redis_url: Optional[str] = Field(
        default=None, required=False, description="Redis connection URL"
    )
    redis_ssl_cert_reqs: str = Field(
        default="required",
        description="Redis SSL cert requirements",
        allowed_values={"required", "optional", "none"},
    )
    redis_ssl_check_hostname: bool = Field(default=True, description="Redis SSL hostname check")


class SecuritySettings(BaseSettingsModel):
    """Security configuration settings."""

    _env_prefix = "COVET_SECURITY_"

    # JWT Configuration
    jwt_secret_key: str = Field(
        default=secrets.token_urlsafe(64),
        description="JWT secret key",
        validators=[JWTSecretKeyValidator()],
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT algorithm",
        allowed_values={"HS256", "HS384", "HS512", "RS256", "RS384", "RS512"},
    )
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="JWT access token expiration in minutes", min_value=1
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, description="JWT refresh token expiration in days", min_value=1
    )

    # Password Configuration
    password_min_length: int = Field(
        default=8, description="Minimum password length", min_value=6, max_value=128
    )
    password_bcrypt_rounds: int = Field(
        default=12,
        description="Bcrypt rounds for password hashing",
        validators=[BcryptRoundsValidator()],
    )

    # API Key Configuration
    api_key_length: int = Field(
        default=32, description="API key length in bytes", min_value=16, max_value=64
    )
    api_key_prefix: str = Field(default="cov_", description="API key prefix", max_length=10)

    # Session Configuration
    session_cookie_name: str = Field(
        default="covet_session",
        description="Session cookie name",
        min_length=1,
        max_length=50,
    )
    session_cookie_secure: bool = Field(default=True, description="Secure session cookies")
    session_cookie_httponly: bool = Field(default=True, description="HTTP-only session cookies")
    session_cookie_samesite: str = Field(
        default="strict",
        description="SameSite session cookies",
        allowed_values={"strict", "lax", "none"},
    )
    session_expire_minutes: int = Field(
        default=720, description="Session expiration in minutes", min_value=1
    )

    # CSRF Configuration
    csrf_secret_key: str = Field(
        default=secrets.token_urlsafe(32), description="CSRF secret key", min_length=16
    )
    csrf_token_expire_minutes: int = Field(
        default=60, description="CSRF token expiration in minutes", min_value=1
    )

    # CORS Configuration
    cors_allow_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
        validators=[CORSOriginsValidator()],
    )
    cors_allow_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH"],
        description="CORS allowed methods",
    )
    cors_allow_headers: list[str] = Field(default=["*"], description="CORS allowed headers")
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")

    # Rate Limiting Configuration
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(
        default=100, description="Rate limit requests per window", min_value=1
    )
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds", min_value=1
    )
    rate_limit_storage_url: Optional[str] = Field(
        default=None, required=False, description="Rate limit storage URL (Redis)"
    )

    # Security Headers
    security_headers_enabled: bool = Field(default=True, description="Enable security headers")
    hsts_max_age: int = Field(default=31536000, description="HSTS max age in seconds", min_value=0)


class ServerSettings(BaseSettingsModel):
    """Server configuration settings."""

    _env_prefix = "COVET_SERVER_"

    host: str = Field(
        default="0.0.0.0", description="Server host"
    )  # nosec B104 - binding to all interfaces is intentional for framework
    port: int = Field(default=8000, description="Server port", min_value=1, max_value=65535)
    workers: int = Field(default=1, description="Number of worker processes", min_value=1)
    reload: bool = Field(default=False, description="Enable auto-reload")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")

    # SSL/TLS Configuration
    ssl_keyfile: Optional[str] = Field(
        default=None, required=False, description="SSL key file path"
    )
    ssl_certfile: Optional[str] = Field(
        default=None, required=False, description="SSL certificate file path"
    )
    ssl_ca_certs: Optional[str] = Field(
        default=None, required=False, description="SSL CA certificates file path"
    )


class Settings(BaseSettingsModel):
    """Main application settings."""

    _env_prefix = "COVET_"

    # Application Configuration
    app_name: str = Field(default="CovetPy", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Environment",
        validators=[EnvironmentValidator()],
    )
    debug: bool = Field(
        default=False, description="Debug mode", validators=[DebugProductionValidator()]
    )

    def __init__(self, **data) -> None:
        """Initialize with sub-configurations."""
        super().__init__(**data)

        # Initialize sub-configurations if not provided
        if not hasattr(self, "database") or self.database is None:
            self.database = DatabaseSettings()
        if not hasattr(self, "security") or self.security is None:
            self.security = SecuritySettings()
        if not hasattr(self, "server") or self.server is None:
            self.server = ServerSettings()

    # Feature Flags
    features: dict[str, bool] = Field(
        default={
            "api_versioning": True,
            "websocket_enabled": True,
            "graphql_enabled": True,
            "grpc_enabled": True,
            "metrics_enabled": True,
            "tracing_enabled": True,
        },
        description="Feature flags",
    )

    def _load_from_env(self) -> dict[str, Any]:
        """Load configuration from environment variables and .env file."""
        env_data = super()._load_from_env()

        # Try to load from .env file
        env_file_path = Path(".env")
        if env_file_path.exists():
            try:
                with open(env_file_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip("\"'")

                            # Map to field name
                            if key.startswith("COVET_"):
                                # Remove COVET_ prefix
                                field_name = key[6:].lower()
                                if field_name in self._field_metadata:
                                    env_data[field_name] = value
            except Exception:
                pass  # Ignore errors reading .env file

        return env_data

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.environment == Environment.TESTING

    def get_database_url(self) -> str:
        """Get the database URL with proper handling for different environments."""
        return self.database.url

    def get_redis_url(self) -> Optional[str]:
        """Get the Redis URL if configured."""
        return self.database.redis_url


class ConfigurationError(Exception):
    """Configuration error exception."""


def create_pydantic_compatibility() -> None:
    """Create pydantic compatibility layer if pydantic is available."""
    if not HAS_PYDANTIC:
        return

    # Create pydantic-compatible versions of our models
    try:
        from pydantic import create_model

        # This would create pydantic versions, but we'll keep it simple for now
        # and just ensure our models can be converted to/from pydantic if
        # needed
    except ImportError:
        # TODO: Add proper exception handling

        pass


def load_settings() -> Settings:
    """Load application settings with validation."""
    try:
        settings = Settings()

        # Perform additional validation for production
        if settings.is_production:
            _validate_production_config(settings)

        return settings

    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {str(e)}") from e


def _validate_production_config(settings: Settings) -> None:
    """Validate production-specific configuration requirements."""
    errors = []

    # Check for default/weak secrets
    default_jwt_key_length = 64  # Length of default generated key
    if len(settings.security.jwt_secret_key) == default_jwt_key_length:
        # This is likely a generated key, which is actually secure
        pass
    elif settings.security.jwt_secret_key in ["your-secret-key-here", "secret", "test"]:
        errors.append("JWT secret key must be changed from default value in production")

    # Check database configuration
    if settings.database.url.startswith("sqlite:"):
        errors.append("SQLite should not be used in production")

    # Check SSL configuration
    if not settings.server.ssl_certfile or not settings.server.ssl_keyfile:
        import warnings

        warnings.warn(
            "SSL/TLS not configured - HTTPS is recommended for production",
            UserWarning,
            stacklevel=2,
        )

    # Check CORS configuration
    if "*" in settings.security.cors_allow_origins:
        errors.append("CORS wildcard (*) should not be used in production")

    if errors:
        raise ConfigurationError(f"Production configuration errors: {'; '.join(errors)}")


def get_secret_key(name: str, length: int = 32) -> str:
    """Generate or retrieve a secret key."""
    env_var = f"COVET_SECRET_{name.upper()}"

    # Try to get from environment
    secret = os.environ.get(env_var)
    if secret:
        return secret

    # Generate new secret
    return secrets.token_urlsafe(length)


# Global settings instance
settings = load_settings()


# Export commonly used settings
__all__ = [
    "Settings",
    "Environment",
    "LogLevel",
    "DatabaseSettings",
    "SecuritySettings",
    "ServerSettings",
    "ConfigurationError",
    "load_settings",
    "get_secret_key",
    "settings",
]
