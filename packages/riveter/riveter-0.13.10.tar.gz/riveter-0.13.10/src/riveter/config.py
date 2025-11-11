"""Configuration management for Riveter."""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class RiveterConfig:
    """Configuration settings for Riveter."""

    # Rule settings
    rule_dirs: List[str] = field(default_factory=lambda: ["rules"])
    rule_packs: List[str] = field(default_factory=list)
    include_rules: List[str] = field(default_factory=list)
    exclude_rules: List[str] = field(default_factory=list)
    min_severity: str = "info"

    # Output settings
    output_format: str = "table"
    output_file: Optional[str] = None

    # Performance settings
    parallel: bool = False
    max_workers: Optional[int] = None
    cache_dir: Optional[str] = None

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "human"
    debug: bool = False

    # Environment-specific overrides
    environment_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)

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

    def apply_environment_overrides(self, environment: Optional[str] = None) -> "RiveterConfig":
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

    def to_dict(self) -> Dict[str, Any]:
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
    def from_dict(cls, data: Dict[str, Any]) -> "RiveterConfig":
        """Create configuration from dictionary."""
        # Filter out None values and unknown keys
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys and v is not None}

        return cls(**filtered_data)


class ConfigManager:
    """Manages configuration loading and validation."""

    DEFAULT_CONFIG_FILES = [
        "riveter.yml",
        "riveter.yaml",
        ".riveter.yml",
        ".riveter.yaml",
        "riveter.json",
        ".riveter.json",
    ]

    def __init__(self) -> None:
        self._default_config = RiveterConfig()

    def load_config(
        self,
        config_file: Optional[str] = None,
        cli_overrides: Optional[Dict[str, Any]] = None,
        environment: Optional[str] = None,
    ) -> RiveterConfig:
        """Load configuration with hierarchy: CLI args > config file > defaults."""

        # Start with defaults
        config = self._default_config

        # Load from config file
        file_config = self._load_config_file(config_file)
        if file_config:
            config = config.merge_with(file_config)

        # Apply CLI overrides
        if cli_overrides:
            cli_config = RiveterConfig.from_dict(cli_overrides)
            config = config.merge_with(cli_config)

        # Apply environment-specific overrides
        config = config.apply_environment_overrides(environment)

        return config

    def _load_config_file(self, config_file: Optional[str] = None) -> Optional[RiveterConfig]:
        """Load configuration from file."""
        if config_file:
            # Explicit config file specified
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            return self._parse_config_file(config_file)

        # Search for default config files
        for filename in self.DEFAULT_CONFIG_FILES:
            if os.path.exists(filename):
                return self._parse_config_file(filename)

        return None

    def _parse_config_file(self, config_file: str) -> RiveterConfig:
        """Parse configuration file (YAML or JSON)."""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                if config_file.endswith(".json"):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValueError(f"Configuration file must contain a dictionary: {config_file}")

            return RiveterConfig.from_dict(data)

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {config_file}: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading configuration file: {config_file}: {e}") from e

    def validate_config(self, config: RiveterConfig) -> List[str]:
        """Validate configuration and return list of validation errors."""
        errors = []

        # Validate severity level
        valid_severities = ["info", "warning", "error"]
        if config.min_severity not in valid_severities:
            errors.append(
                f"Invalid min_severity '{config.min_severity}'. Must be one of: {valid_severities}"
            )

        # Validate output format
        valid_formats = ["table", "json", "junit", "sarif"]
        if config.output_format not in valid_formats:
            errors.append(
                f"Invalid output_format '{config.output_format}'. Must be one of: {valid_formats}"
            )

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config.log_level not in valid_log_levels:
            errors.append(
                f"Invalid log_level '{config.log_level}'. Must be one of: {valid_log_levels}"
            )

        # Validate log format
        valid_log_formats = ["human", "json"]
        if config.log_format not in valid_log_formats:
            errors.append(
                f"Invalid log_format '{config.log_format}'. Must be one of: {valid_log_formats}"
            )

        # Note: Rule directory validation is skipped here as directories
        # may not exist until rules are actually loaded. The CLI will handle
        # missing directories when they are actually needed.

        # Validate max_workers
        if config.max_workers is not None and config.max_workers < 1:
            errors.append("max_workers must be greater than 0")

        return errors

    def create_sample_config(self, output_file: str) -> None:
        """Create a sample configuration file."""
        sample_config = {
            "# Riveter Configuration File": None,
            "# Rule settings": None,
            "rule_dirs": ["rules", "custom-rules"],
            "rule_packs": ["aws-security", "cis-aws"],
            "include_rules": ["*security*", "*encryption*"],
            "exclude_rules": ["*test*"],
            "min_severity": "warning",
            "# Output settings": None,
            "output_format": "table",
            "output_file": None,
            "# Performance settings": None,
            "parallel": True,
            "max_workers": 4,
            "cache_dir": ".riveter-cache",
            "# Logging settings": None,
            "log_level": "INFO",
            "log_format": "human",
            "debug": False,
            "# Environment-specific overrides": None,
            "environment_overrides": {
                "production": {"min_severity": "error", "parallel": True, "max_workers": 8},
                "development": {"min_severity": "info", "debug": True},
            },
        }

        # Remove comment keys for actual output
        clean_config = {
            k: v for k, v in sample_config.items() if not k.startswith("#") and v is not None
        }

        if output_file.endswith(".json"):
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(clean_config, f, indent=2)
        else:
            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(clean_config, f, default_flow_style=False, sort_keys=False)


def get_environment_from_context(resources: List[Dict[str, Any]]) -> Optional[str]:
    """Detect environment from resource context (tags, attributes, etc.)."""
    # Look for common environment indicators in resource tags
    for resource in resources:
        # Check tags
        tags = resource.get("tags", {})
        if isinstance(tags, dict):
            for tag_key in ["Environment", "environment", "env", "Env", "ENVIRONMENT"]:
                if tag_key in tags:
                    return str(tags[tag_key]).lower()

        # Check resource names for environment indicators
        resource_name = resource.get("name", "")
        if isinstance(resource_name, str):
            for env in [
                "prod",
                "production",
                "dev",
                "development",
                "test",
                "testing",
                "staging",
                "stage",
            ]:
                if env in resource_name.lower():
                    return env

    return None
