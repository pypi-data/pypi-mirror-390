"""
Migration System Configuration

This module provides configuration options for the migration system,
including rename detection settings, safety features, and operational parameters.

Configuration can be set via:
1. Environment variables
2. Configuration file (migrations.yaml)
3. Direct instantiation

Example:
    from covet.database.migrations.config import MigrationConfig

    # Default configuration
    config = MigrationConfig()

    # Custom configuration
    config = MigrationConfig(
        detect_renames=True,
        rename_similarity_threshold=0.85,
        require_type_match_for_rename=True,
    )

    # Use with DiffEngine
    diff_engine = DiffEngine(
        detect_renames=config.detect_renames,
        rename_similarity_threshold=config.rename_similarity_threshold,
    )

Author: CovetPy Migration System
Version: 2.0.0
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class RenameDetectionConfig:
    """
    Configuration for column rename detection.

    Attributes:
        enabled: Enable automatic rename detection (default: True)
        similarity_threshold: Minimum similarity score for rename (0.0 to 1.0, default: 0.80)
        require_type_match: Require exact type match for rename (default: False)
        max_length_diff: Maximum allowed length difference ratio (default: 0.5)
        manual_renames: Dictionary of manual renames {table: {old: new}}
    """

    enabled: bool = True
    similarity_threshold: float = 0.80
    require_type_match: bool = False
    max_length_diff: float = 0.5
    manual_renames: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration."""
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError(
                f"similarity_threshold must be between 0.0 and 1.0, got {self.similarity_threshold}"
            )

        if not 0.0 <= self.max_length_diff <= 1.0:
            raise ValueError(
                f"max_length_diff must be between 0.0 and 1.0, got {self.max_length_diff}"
            )

    @classmethod
    def from_env(cls) -> "RenameDetectionConfig":
        """
        Create configuration from environment variables.

        Environment Variables:
            COVET_DETECT_RENAMES: Enable rename detection (default: true)
            COVET_RENAME_THRESHOLD: Similarity threshold (default: 0.80)
            COVET_RENAME_REQUIRE_TYPE_MATCH: Require type match (default: false)
            COVET_RENAME_MAX_LENGTH_DIFF: Max length difference (default: 0.5)

        Returns:
            RenameDetectionConfig instance
        """
        enabled = os.getenv("COVET_DETECT_RENAMES", "true").lower() == "true"
        threshold = float(os.getenv("COVET_RENAME_THRESHOLD", "0.80"))
        require_type = os.getenv("COVET_RENAME_REQUIRE_TYPE_MATCH", "false").lower() == "true"
        max_length = float(os.getenv("COVET_RENAME_MAX_LENGTH_DIFF", "0.5"))

        return cls(
            enabled=enabled,
            similarity_threshold=threshold,
            require_type_match=require_type,
            max_length_diff=max_length,
        )

    def add_manual_rename(self, table: str, old_name: str, new_name: str):
        """
        Add manual rename specification.

        Args:
            table: Table name
            old_name: Current column name
            new_name: New column name
        """
        if table not in self.manual_renames:
            self.manual_renames[table] = {}

        self.manual_renames[table][old_name] = new_name
        logger.info(f"Added manual rename: {table}.{old_name} -> {new_name}")


@dataclass
class SafetyConfig:
    """
    Safety features for migrations.

    Attributes:
        require_confirmation: Require user confirmation for destructive operations
        backup_before_migrate: Create backup before applying migrations
        dry_run_default: Default to dry-run mode
        prevent_data_loss: Prevent operations that would lose data
        max_batch_size: Maximum number of operations in one migration
    """

    require_confirmation: bool = True
    backup_before_migrate: bool = True
    dry_run_default: bool = False
    prevent_data_loss: bool = True
    max_batch_size: int = 100

    @classmethod
    def from_env(cls) -> "SafetyConfig":
        """Create configuration from environment variables."""
        require_confirmation = os.getenv("COVET_REQUIRE_CONFIRMATION", "true").lower() == "true"
        backup = os.getenv("COVET_BACKUP_BEFORE_MIGRATE", "true").lower() == "true"
        dry_run = os.getenv("COVET_DRY_RUN_DEFAULT", "false").lower() == "true"
        prevent_loss = os.getenv("COVET_PREVENT_DATA_LOSS", "true").lower() == "true"
        max_batch = int(os.getenv("COVET_MAX_BATCH_SIZE", "100"))

        return cls(
            require_confirmation=require_confirmation,
            backup_before_migrate=backup,
            dry_run_default=dry_run,
            prevent_data_loss=prevent_loss,
            max_batch_size=max_batch,
        )


@dataclass
class MigrationConfig:
    """
    Complete migration system configuration.

    This is the main configuration class that combines all settings
    for the migration system.

    Attributes:
        rename_detection: Rename detection configuration
        safety: Safety features configuration
        dialect: Database dialect ('postgresql', 'mysql', 'sqlite')
        migrations_dir: Directory for migration files
        auto_migrate: Automatically apply migrations on startup
        verbose: Enable verbose logging
    """

    rename_detection: RenameDetectionConfig = field(default_factory=RenameDetectionConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    dialect: str = "postgresql"
    migrations_dir: str = "./migrations"
    auto_migrate: bool = False
    verbose: bool = False

    @classmethod
    def from_env(cls) -> "MigrationConfig":
        """
        Create complete configuration from environment variables.

        Returns:
            MigrationConfig instance
        """
        rename_config = RenameDetectionConfig.from_env()
        safety_config = SafetyConfig.from_env()

        dialect = os.getenv("COVET_DIALECT", "postgresql")
        migrations_dir = os.getenv("COVET_MIGRATIONS_DIR", "./migrations")
        auto_migrate = os.getenv("COVET_AUTO_MIGRATE", "false").lower() == "true"
        verbose = os.getenv("COVET_VERBOSE", "false").lower() == "true"

        return cls(
            rename_detection=rename_config,
            safety=safety_config,
            dialect=dialect,
            migrations_dir=migrations_dir,
            auto_migrate=auto_migrate,
            verbose=verbose,
        )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MigrationConfig":
        """
        Create configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            MigrationConfig instance
        """
        # Extract rename detection config
        rename_dict = config_dict.get("rename_detection", {})
        rename_config = RenameDetectionConfig(
            enabled=rename_dict.get("enabled", True),
            similarity_threshold=rename_dict.get("similarity_threshold", 0.80),
            require_type_match=rename_dict.get("require_type_match", False),
            max_length_diff=rename_dict.get("max_length_diff", 0.5),
        )

        # Extract safety config
        safety_dict = config_dict.get("safety", {})
        safety_config = SafetyConfig(
            require_confirmation=safety_dict.get("require_confirmation", True),
            backup_before_migrate=safety_dict.get("backup_before_migrate", True),
            dry_run_default=safety_dict.get("dry_run_default", False),
            prevent_data_loss=safety_dict.get("prevent_data_loss", True),
            max_batch_size=safety_dict.get("max_batch_size", 100),
        )

        return cls(
            rename_detection=rename_config,
            safety=safety_config,
            dialect=config_dict.get("dialect", "postgresql"),
            migrations_dir=config_dict.get("migrations_dir", "./migrations"),
            auto_migrate=config_dict.get("auto_migrate", False),
            verbose=config_dict.get("verbose", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration as dictionary
        """
        return {
            "rename_detection": {
                "enabled": self.rename_detection.enabled,
                "similarity_threshold": self.rename_detection.similarity_threshold,
                "require_type_match": self.rename_detection.require_type_match,
                "max_length_diff": self.rename_detection.max_length_diff,
            },
            "safety": {
                "require_confirmation": self.safety.require_confirmation,
                "backup_before_migrate": self.safety.backup_before_migrate,
                "dry_run_default": self.safety.dry_run_default,
                "prevent_data_loss": self.safety.prevent_data_loss,
                "max_batch_size": self.safety.max_batch_size,
            },
            "dialect": self.dialect,
            "migrations_dir": self.migrations_dir,
            "auto_migrate": self.auto_migrate,
            "verbose": self.verbose,
        }

    def add_manual_rename(self, table: str, old_name: str, new_name: str):
        """
        Add manual rename specification.

        Args:
            table: Table name
            old_name: Current column name
            new_name: New column name
        """
        self.rename_detection.add_manual_rename(table, old_name, new_name)


# Global default configuration
_default_config: Optional[MigrationConfig] = None


def get_default_config() -> MigrationConfig:
    """
    Get global default configuration.

    Returns:
        Global MigrationConfig instance
    """
    global _default_config

    if _default_config is None:
        try:
            _default_config = MigrationConfig.from_env()
            logger.info("Loaded migration configuration from environment")
        except Exception as e:
            logger.warning(f"Failed to load config from environment: {e}. Using defaults.")
            _default_config = MigrationConfig()

    return _default_config


def set_default_config(config: MigrationConfig):
    """
    Set global default configuration.

    Args:
        config: MigrationConfig instance to use as default
    """
    global _default_config
    _default_config = config
    logger.info("Updated global migration configuration")


# Preset configurations for common scenarios


def get_conservative_config() -> MigrationConfig:
    """
    Get conservative configuration (maximum safety).

    Use this for production environments where safety is paramount.

    Features:
    - High rename similarity threshold (0.90)
    - Requires type match for renames
    - All safety features enabled
    - Dry run by default
    """
    return MigrationConfig(
        rename_detection=RenameDetectionConfig(
            enabled=True,
            similarity_threshold=0.90,
            require_type_match=True,
            max_length_diff=0.3,
        ),
        safety=SafetyConfig(
            require_confirmation=True,
            backup_before_migrate=True,
            dry_run_default=True,
            prevent_data_loss=True,
            max_batch_size=50,
        ),
    )


def get_aggressive_config() -> MigrationConfig:
    """
    Get aggressive configuration (more detections, less safety).

    Use this for development environments where you want maximum
    rename detection sensitivity.

    Features:
    - Lower rename similarity threshold (0.70)
    - No type match requirement
    - Reduced safety checks
    """
    return MigrationConfig(
        rename_detection=RenameDetectionConfig(
            enabled=True,
            similarity_threshold=0.70,
            require_type_match=False,
            max_length_diff=0.6,
        ),
        safety=SafetyConfig(
            require_confirmation=False,
            backup_before_migrate=False,
            dry_run_default=False,
            prevent_data_loss=False,
            max_batch_size=200,
        ),
    )


def get_balanced_config() -> MigrationConfig:
    """
    Get balanced configuration (default settings).

    This is the recommended configuration for most use cases.

    Features:
    - Moderate rename similarity threshold (0.80)
    - Basic safety features
    - Good balance between detection and false positives
    """
    return MigrationConfig()


__all__ = [
    "MigrationConfig",
    "RenameDetectionConfig",
    "SafetyConfig",
    "get_default_config",
    "set_default_config",
    "get_conservative_config",
    "get_aggressive_config",
    "get_balanced_config",
]
