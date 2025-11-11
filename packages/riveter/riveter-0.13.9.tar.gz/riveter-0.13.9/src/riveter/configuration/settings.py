"""Modern configuration settings management with type safety and validation.

This module provides a modernized version of the general configuration handling
that maintains backward compatibility while adding comprehensive type hints,
validation, and environment variable support.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..logging import debug, info, warning
from ..models.config import RiveterConfig


@dataclass(frozen=True)
class ConfigurationDefaults:
    """Default configuration values for Riveter."""

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


class ConfigurationLoader:
    """Loads configuration from various sources with proper validation."""

    DEFAULT_CONFIG_FILES = [
        "riveter.yml",
        "riveter.yaml",
        ".riveter.yml",
        ".riveter.yaml",
        "riveter.json",
        ".riveter.json",
    ]

    ENV_PREFIX = "RIVETER_"

    def __init__(self, defaults: ConfigurationDefaults | None = None) -> None:
        """Initialize configuration loader.

        Args:
            defaults: Default configuration values. If None, uses ConfigurationDefaults.
        """
        self.defaults = defaults or ConfigurationDefaults()
        debug("Configuration loader initialized")

    def load_config(
        self,
        config_file: str | Path | None = None,
        cli_overrides: dict[str, Any] | None = None,
        environment: str | None = None,
        load_env_vars: bool = True,
    ) -> RiveterConfig:
        """Load configuration with hierarchy: CLI args > env vars > config file > defaults.

        Args:
            config_file: Explicit configuration file path
            cli_overrides: CLI argument overrides
            environment: Environment name for environment-specific overrides
            load_env_vars: Whether to load environment variables

        Returns:
            Merged RiveterConfig object
        """
        info(
            "Loading configuration",
            config_file=str(config_file) if config_file else None,
            environment=environment,
            load_env_vars=load_env_vars,
        )

        # Start with defaults
        config_dict = self._defaults_to_dict()

        # Load from config file
        file_config = self._load_config_file(config_file)
        if file_config:
            config_dict = self._merge_config_dicts(config_dict, file_config)
            debug("Merged file configuration")

        # Load environment variables
        if load_env_vars:
            env_config = self._load_environment_variables()
            if env_config:
                config_dict = self._merge_config_dicts(config_dict, env_config)
                debug("Merged environment variables")

        # Apply CLI overrides
        if cli_overrides:
            config_dict = self._merge_config_dicts(config_dict, cli_overrides)
            debug("Merged CLI overrides")

        # Apply environment-specific overrides
        if environment:
            env_overrides = config_dict.get("environment_overrides", {}).get(environment, {})
            if env_overrides:
                config_dict = self._merge_config_dicts(config_dict, env_overrides)
                debug("Applied environment-specific overrides", environment=environment)

        # Convert to RiveterConfig
        try:
            config = self._dict_to_riveter_config(config_dict)
            info("Configuration loaded successfully")
            return config
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e!s}") from e

    def _defaults_to_dict(self) -> dict[str, Any]:
        """Convert defaults to dictionary."""
        return {
            "rule_dirs": list(self.defaults.rule_dirs),
            "rule_packs": list(self.defaults.rule_packs),
            "include_rules": list(self.defaults.include_rules),
            "exclude_rules": list(self.defaults.exclude_rules),
            "min_severity": self.defaults.min_severity,
            "output_format": self.defaults.output_format,
            "output_file": self.defaults.output_file,
            "parallel": self.defaults.parallel,
            "max_workers": self.defaults.max_workers,
            "cache_dir": self.defaults.cache_dir,
            "log_level": self.defaults.log_level,
            "log_format": self.defaults.log_format,
            "debug": self.defaults.debug,
            "environment_overrides": dict(self.defaults.environment_overrides),
        }

    def _load_config_file(self, config_file: str | Path | None) -> dict[str, Any] | None:
        """Load configuration from file."""
        if config_file:
            # Explicit config file specified
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            return self._parse_config_file(config_path)

        # Search for default config files
        for filename in self.DEFAULT_CONFIG_FILES:
            config_path = Path(filename)
            if config_path.exists():
                debug("Found default config file", filename=filename)
                return self._parse_config_file(config_path)

        debug("No configuration file found")
        return None

    def _parse_config_file(self, config_path: Path) -> dict[str, Any]:
        """Parse configuration file (YAML or JSON)."""
        try:
            with open(config_path, encoding="utf-8") as f:
                if config_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValueError(f"Configuration file must contain a dictionary: {config_path}")

            debug("Parsed configuration file", file=str(config_path), keys=list(data.keys()))
            return data

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {config_path}: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading configuration file: {config_path}: {e}") from e

    def _load_environment_variables(self) -> dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}

        # Map environment variable names to config keys
        env_mappings = {
            f"{self.ENV_PREFIX}RULE_DIRS": ("rule_dirs", self._parse_list_env),
            f"{self.ENV_PREFIX}RULE_PACKS": ("rule_packs", self._parse_list_env),
            f"{self.ENV_PREFIX}INCLUDE_RULES": ("include_rules", self._parse_list_env),
            f"{self.ENV_PREFIX}EXCLUDE_RULES": ("exclude_rules", self._parse_list_env),
            f"{self.ENV_PREFIX}MIN_SEVERITY": ("min_severity", str),
            f"{self.ENV_PREFIX}OUTPUT_FORMAT": ("output_format", str),
            f"{self.ENV_PREFIX}OUTPUT_FILE": ("output_file", str),
            f"{self.ENV_PREFIX}PARALLEL": ("parallel", self._parse_bool_env),
            f"{self.ENV_PREFIX}MAX_WORKERS": ("max_workers", int),
            f"{self.ENV_PREFIX}CACHE_DIR": ("cache_dir", str),
            f"{self.ENV_PREFIX}LOG_LEVEL": ("log_level", str),
            f"{self.ENV_PREFIX}LOG_FORMAT": ("log_format", str),
            f"{self.ENV_PREFIX}DEBUG": ("debug", self._parse_bool_env),
        }

        for env_var, (config_key, parser) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    parsed_value = parser(value)
                    env_config[config_key] = parsed_value
                    debug("Loaded environment variable", env_var=env_var, value=parsed_value)
                except (ValueError, TypeError) as e:
                    warning(
                        "Invalid environment variable value",
                        env_var=env_var,
                        value=value,
                        error=str(e),
                    )

        return env_config

    def _parse_bool_env(self, value: str) -> bool:
        """Parse boolean value from environment variable."""
        return value.lower() in ("true", "1", "yes", "on")

    def _parse_list_env(self, value: str) -> list[str]:
        """Parse list value from environment variable (comma-separated)."""
        return [item.strip() for item in value.split(",") if item.strip()]

    def _merge_config_dicts(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Merge two configuration dictionaries with override taking precedence."""
        merged = dict(base)

        for key, value in override.items():
            if key in merged and isinstance(merged[key], list) and isinstance(value, list):
                # For lists, extend rather than replace
                merged[key] = merged[key] + [item for item in value if item not in merged[key]]
            elif key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # For dicts, merge recursively
                merged[key] = self._merge_config_dicts(merged[key], value)
            else:
                # For other types, override completely
                merged[key] = value

        return merged

    def _dict_to_riveter_config(self, config_dict: dict[str, Any]) -> RiveterConfig:
        """Convert configuration dictionary to RiveterConfig object."""
        # Convert paths to Path objects
        rule_pack_paths = []
        for path_str in config_dict.get("rule_dirs", []):
            rule_pack_paths.append(Path(path_str))

        cache_dir = None
        if config_dict.get("cache_dir"):
            cache_dir = Path(config_dict["cache_dir"])

        log_file = None
        if config_dict.get("log_file"):
            log_file = Path(config_dict["log_file"])

        return RiveterConfig(
            rule_pack_paths=rule_pack_paths,
            default_rule_packs=config_dict.get("rule_packs", []),
            cache_enabled=config_dict.get("cache_enabled", True),
            cache_dir=cache_dir,
            cache_ttl=config_dict.get("cache_ttl", 3600),
            performance_mode=config_dict.get("performance_mode", False),
            max_workers=config_dict.get("max_workers"),
            default_output_format=config_dict.get("output_format", "table"),
            color_output=config_dict.get("color_output", True),
            show_progress=config_dict.get("show_progress", True),
            log_level=config_dict.get("log_level", "INFO"),
            log_file=log_file,
            fail_on_warnings=config_dict.get("fail_on_warnings", False),
            strict_mode=config_dict.get("strict_mode", False),
            plugin_paths=[],  # Will be added in future versions
            custom_operators={},  # Will be added in future versions
        )


class ConfigurationValidator:
    """Validates configuration settings and provides helpful error messages."""

    VALID_SEVERITIES = ["info", "warning", "error"]
    VALID_OUTPUT_FORMATS = ["table", "json", "junit", "sarif"]
    VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    VALID_LOG_FORMATS = ["human", "json"]

    def validate_config(self, config: RiveterConfig) -> list[str]:
        """Validate configuration and return list of validation errors.

        Args:
            config: Configuration to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate output format
        if config.default_output_format not in self.VALID_OUTPUT_FORMATS:
            errors.append(
                f"Invalid output_format '{config.default_output_format}'. "
                f"Must be one of: {self.VALID_OUTPUT_FORMATS}"
            )

        # Validate log level
        if config.log_level not in self.VALID_LOG_LEVELS:
            errors.append(
                f"Invalid log_level '{config.log_level}'. "
                f"Must be one of: {self.VALID_LOG_LEVELS}"
            )

        # Validate max_workers
        if config.max_workers is not None and config.max_workers < 1:
            errors.append("max_workers must be greater than 0")

        # Validate cache_ttl
        if config.cache_ttl < 0:
            errors.append("cache_ttl must be non-negative")

        # Validate paths exist (if specified)
        for rule_path in config.rule_pack_paths:
            if not rule_path.exists():
                warning(f"Rule pack path does not exist: {rule_path}")
                # Don't add to errors as paths may be created later

        if config.cache_dir and not config.cache_dir.parent.exists():
            errors.append(f"Cache directory parent does not exist: {config.cache_dir.parent}")

        if config.log_file and not config.log_file.parent.exists():
            errors.append(f"Log file directory does not exist: {config.log_file.parent}")

        return errors

    def validate_legacy_config(self, config_dict: dict[str, Any]) -> list[str]:
        """Validate legacy configuration dictionary format.

        Args:
            config_dict: Legacy configuration dictionary

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate severity level
        min_severity = config_dict.get("min_severity", "info")
        if min_severity not in self.VALID_SEVERITIES:
            errors.append(
                f"Invalid min_severity '{min_severity}'. "
                f"Must be one of: {self.VALID_SEVERITIES}"
            )

        # Validate output format
        output_format = config_dict.get("output_format", "table")
        if output_format not in self.VALID_OUTPUT_FORMATS:
            errors.append(
                f"Invalid output_format '{output_format}'. "
                f"Must be one of: {self.VALID_OUTPUT_FORMATS}"
            )

        # Validate log level
        log_level = config_dict.get("log_level", "INFO")
        if log_level not in self.VALID_LOG_LEVELS:
            errors.append(
                f"Invalid log_level '{log_level}'. " f"Must be one of: {self.VALID_LOG_LEVELS}"
            )

        # Validate log format
        log_format = config_dict.get("log_format", "human")
        if log_format not in self.VALID_LOG_FORMATS:
            errors.append(
                f"Invalid log_format '{log_format}'. " f"Must be one of: {self.VALID_LOG_FORMATS}"
            )

        # Validate max_workers
        max_workers = config_dict.get("max_workers")
        if max_workers is not None and max_workers < 1:
            errors.append("max_workers must be greater than 0")

        return errors


class ConfigurationWriter:
    """Writes configuration files with proper formatting."""

    def create_sample_config(self, output_file: str | Path, format_type: str = "yaml") -> None:
        """Create a sample configuration file.

        Args:
            output_file: Path to output file
            format_type: Format type ("yaml" or "json")
        """
        output_path = Path(output_file)

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

        if format_type.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(clean_config, f, indent=2)
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(clean_config, f, default_flow_style=False, sort_keys=False)

        info("Sample configuration file created", output_file=str(output_path), format=format_type)


# Legacy compatibility functions
def get_environment_from_context(resources: list[dict[str, Any]]) -> str | None:
    """Detect environment from resource context (tags, attributes, etc.).

    This function maintains backward compatibility with the original implementation.

    Args:
        resources: List of resource dictionaries

    Returns:
        Detected environment name or None
    """
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


# Legacy class for backward compatibility
class ConfigManager:
    """Legacy configuration manager for backward compatibility."""

    def __init__(self) -> None:
        """Initialize legacy config manager."""
        self._loader = ConfigurationLoader()
        self._validator = ConfigurationValidator()
        self._writer = ConfigurationWriter()
        warning("Using legacy ConfigManager. Consider migrating to ConfigurationLoader.")

    def load_config(
        self,
        config_file: str | None = None,
        cli_overrides: dict[str, Any] | None = None,
        environment: str | None = None,
    ) -> dict[str, Any]:
        """Load configuration in legacy format."""
        config = self._loader.load_config(config_file, cli_overrides, environment)
        return config.to_dict()

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate legacy configuration format."""
        return self._validator.validate_legacy_config(config)

    def create_sample_config(self, output_file: str) -> None:
        """Create sample configuration file."""
        format_type = "json" if output_file.endswith(".json") else "yaml"
        self._writer.create_sample_config(output_file, format_type)
