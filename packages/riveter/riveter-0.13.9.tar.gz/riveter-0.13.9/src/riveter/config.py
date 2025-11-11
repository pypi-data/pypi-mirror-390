"""Configuration management for Riveter.

This module provides backward compatibility for the legacy configuration
management while internally using the modernized configuration system.
"""

from dataclasses import dataclass, field
from typing import Any

from .configuration.settings import ConfigManager as ModernConfigManager
from .configuration.settings import (
    get_environment_from_context as modern_get_environment_from_context,
)
from .logging import warning


@dataclass
class RiveterConfig:
    """Configuration settings for Riveter."""

    # Rule settings
    rule_dirs: list[str] = field(default_factory=lambda: ["rules"])
    rule_packs: list[str] = field(default_factory=list)
    include_rules: list[str] = field(default_factory=list)
    exclude_rules: list[str] = field(default_factory=list)
    min_severity: str = "info"

    # Output settings
    output_format: str = "table"
    output_file: str | None = None

    # Performance settings
    parallel: bool = False
    max_workers: int | None = None
    cache_dir: str | None = None

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "human"
    debug: bool = False

    # Environment-specific overrides
    environment_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)

    def merge_with(self, other: "RiveterConfig") -> "RiveterConfig":
        """Merge this configuration with another, with other taking precedence."""
        merged = RiveterConfig()

        # Merge simple fields
        merged.output_format = (
            other.output_format if other.output_format != "table" else self.output_format
        )
        merged.output_file = other.output_file or self.output_file
        merged.parallel = other.parallel or self.parallel
        merged.max_workers = other.max_workers or self.max_workers
        merged.cache_dir = other.cache_dir or self.cache_dir
        merged.log_level = other.log_level if other.log_level != "INFO" else self.log_level
        merged.log_format = other.log_format if other.log_format != "human" else self.log_format
        merged.debug = other.debug or self.debug
        merged.min_severity = (
            other.min_severity if other.min_severity != "info" else self.min_severity
        )

        # Merge lists (other extends self)
        merged.rule_dirs = self.rule_dirs + [d for d in other.rule_dirs if d not in self.rule_dirs]
        merged.rule_packs = self.rule_packs + [
            p for p in other.rule_packs if p not in self.rule_packs
        ]
        merged.include_rules = self.include_rules + [
            r for r in other.include_rules if r not in self.include_rules
        ]
        merged.exclude_rules = self.exclude_rules + [
            r for r in other.exclude_rules if r not in self.exclude_rules
        ]

        # Merge environment overrides
        merged.environment_overrides = {**self.environment_overrides, **other.environment_overrides}

        return merged

    def apply_environment_overrides(self, environment: str | None = None) -> "RiveterConfig":
        """Apply environment-specific overrides to the configuration."""
        if not environment or environment not in self.environment_overrides:
            return self

        overrides = self.environment_overrides[environment]
        config_dict = self.to_dict()

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(self, key):
                config_dict[key] = value

        return RiveterConfig.from_dict(config_dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "rule_dirs": self.rule_dirs,
            "rule_packs": self.rule_packs,
            "include_rules": self.include_rules,
            "exclude_rules": self.exclude_rules,
            "min_severity": self.min_severity,
            "output_format": self.output_format,
            "output_file": self.output_file,
            "parallel": self.parallel,
            "max_workers": self.max_workers,
            "cache_dir": self.cache_dir,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "debug": self.debug,
            "environment_overrides": self.environment_overrides,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiveterConfig":
        """Create configuration from dictionary."""
        # Filter out None values and unknown keys
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys and v is not None}

        return cls(**filtered_data)


class ConfigManager:
    """Legacy configuration manager for backward compatibility.

    This class maintains the original interface while internally using
    the modernized configuration system.
    """

    def __init__(self) -> None:
        """Initialize legacy config manager."""
        self._modern_manager = ModernConfigManager()
        warning(
            "Using legacy ConfigManager. Consider migrating to the modern configuration system."
        )

    def load_config(
        self,
        config_file: str | None = None,
        cli_overrides: dict[str, Any] | None = None,
        environment: str | None = None,
    ) -> RiveterConfig:
        """Load configuration with hierarchy: CLI args > config file > defaults."""
        # Use modern config manager internally and convert to legacy format
        config_dict = self._modern_manager.load_config(config_file, cli_overrides, environment)
        return RiveterConfig.from_dict(config_dict)

    def validate_config(self, config: RiveterConfig) -> list[str]:
        """Validate configuration and return list of validation errors."""
        # Use modern validation internally
        config_dict = config.to_dict()
        return self._modern_manager.validate_config(config_dict)

    def create_sample_config(self, output_file: str) -> None:
        """Create a sample configuration file."""
        self._modern_manager.create_sample_config(output_file)


# Re-export the get_environment_from_context function for backward compatibility
def get_environment_from_context(resources: list[dict[str, Any]]) -> str | None:
    """Detect environment from resource context (tags, attributes, etc.).

    This function maintains backward compatibility with the original implementation.
    """
    return modern_get_environment_from_context(resources)
