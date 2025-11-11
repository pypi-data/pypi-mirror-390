"""Configuration data models for Riveter.

This module defines data structures for CLI arguments, application
configuration, and Terraform configuration parsing.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ConfigurationSource(Enum):
    """Source of configuration data."""

    CLI_ARGS = "cli_args"
    CONFIG_FILE = "config_file"
    ENVIRONMENT = "environment"
    DEFAULT = "default"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CLIArgs:
    """Command-line arguments for Riveter CLI."""

    # Input files
    terraform_file: str | None = None
    rules_file: str | None = None
    rule_packs: tuple[str, ...] = field(default_factory=tuple)

    # Output configuration
    output_format: str | None = None
    output_file: Path | None = None

    # Configuration
    config_file: str | None = None

    # Filtering options
    include_rules: tuple[str, ...] = field(default_factory=tuple)
    exclude_rules: tuple[str, ...] = field(default_factory=tuple)
    min_severity: str | None = None
    rule_dirs: tuple[str, ...] = field(default_factory=tuple)
    environment: str | None = None

    # Behavior flags
    debug: bool = False
    verbose: bool = False
    quiet: bool = False
    dry_run: bool = False
    fail_fast: bool = False

    # Logging options
    log_level: str | None = None
    log_format: str = "human"

    # Performance options
    parallel: bool = False
    cache_dir: str | None = None
    baseline: str | None = None
    benchmark: bool = False

    # Command-specific arguments
    rule_pack_file: str | None = None  # For validate-rule-pack command
    pack_name: str | None = None  # For create-rule-pack-template command
    rules_file_arg: str | None = None  # For validate-rules command
    format: str = "table"  # For various commands
    min_severity_arg: str = "error"  # For validate-rules command

    def __post_init__(self):
        """Validate CLI arguments after initialization."""
        # Convert string paths to Path objects
        if isinstance(self.terraform_file, str):
            object.__setattr__(self, "terraform_file", Path(self.terraform_file))
        if isinstance(self.rules_file, str):
            object.__setattr__(self, "rules_file", Path(self.rules_file))
        if isinstance(self.output_file, str):
            object.__setattr__(self, "output_file", Path(self.output_file))
        if isinstance(self.config_file, str):
            object.__setattr__(self, "config_file", Path(self.config_file))
        if isinstance(self.cache_dir, str):
            object.__setattr__(self, "cache_dir", Path(self.cache_dir))

    @property
    def has_input_files(self) -> bool:
        """Check if input files are specified."""
        return self.terraform_file is not None or bool(self.rule_packs)

    @property
    def has_output_file(self) -> bool:
        """Check if output file is specified."""
        return self.output_file is not None

    @property
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return bool(
            self.include_rules
            or self.exclude_rules
            or self.include_resources
            or self.exclude_resources
            or self.severity_filter
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "terraform_file": str(self.terraform_file) if self.terraform_file else None,
            "rules_file": str(self.rules_file) if self.rules_file else None,
            "rule_packs": self.rule_packs,
            "output_format": self.output_format,
            "output_file": str(self.output_file) if self.output_file else None,
            "verbose": self.verbose,
            "quiet": self.quiet,
            "dry_run": self.dry_run,
            "fail_fast": self.fail_fast,
            "include_rules": self.include_rules,
            "exclude_rules": self.exclude_rules,
            "include_resources": self.include_resources,
            "exclude_resources": self.exclude_resources,
            "severity_filter": self.severity_filter,
            "parallel": self.parallel,
            "max_workers": self.max_workers,
            "config_file": str(self.config_file) if self.config_file else None,
            "cache_enabled": self.cache_enabled,
            "cache_dir": str(self.cache_dir) if self.cache_dir else None,
        }


@dataclass(frozen=True)
class RiveterConfig:
    """Application configuration for Riveter."""

    # Rule pack configuration
    rule_pack_paths: list[Path] = field(default_factory=list)
    default_rule_packs: list[str] = field(default_factory=list)

    # Performance configuration
    cache_enabled: bool = True
    cache_dir: Path | None = None
    cache_ttl: int = 3600  # seconds
    performance_mode: bool = False
    max_workers: int | None = None

    # Output configuration
    default_output_format: str = "table"
    color_output: bool = True
    show_progress: bool = True

    # Logging configuration
    log_level: str = "INFO"
    log_file: Path | None = None

    # Validation configuration
    fail_on_warnings: bool = False
    strict_mode: bool = False

    # Extension configuration
    plugin_paths: list[Path] = field(default_factory=list)
    custom_operators: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Convert string paths to Path objects
        rule_pack_paths = []
        for path in self.rule_pack_paths:
            if isinstance(path, str):
                rule_pack_paths.append(Path(path))
            else:
                rule_pack_paths.append(path)
        object.__setattr__(self, "rule_pack_paths", rule_pack_paths)

        if isinstance(self.cache_dir, str):
            object.__setattr__(self, "cache_dir", Path(self.cache_dir))
        if isinstance(self.log_file, str):
            object.__setattr__(self, "log_file", Path(self.log_file))

        plugin_paths = []
        for path in self.plugin_paths:
            if isinstance(path, str):
                plugin_paths.append(Path(path))
            else:
                plugin_paths.append(path)
        object.__setattr__(self, "plugin_paths", plugin_paths)

    @property
    def effective_cache_dir(self) -> Path:
        """Get effective cache directory."""
        if self.cache_dir:
            return self.cache_dir
        return Path.home() / ".riveter" / "cache"

    @property
    def effective_log_level(self) -> str:
        """Get effective log level."""
        return self.log_level.upper()

    def merge_with_cli_args(self, cli_args: CLIArgs) -> "RiveterConfig":
        """Merge configuration with CLI arguments."""
        # CLI arguments take precedence over config file
        return RiveterConfig(
            rule_pack_paths=self.rule_pack_paths,
            default_rule_packs=self.default_rule_packs,
            cache_enabled=(
                cli_args.cache_enabled if hasattr(cli_args, "cache_enabled") else self.cache_enabled
            ),
            cache_dir=cli_args.cache_dir or self.cache_dir,
            cache_ttl=self.cache_ttl,
            performance_mode=self.performance_mode,
            max_workers=cli_args.max_workers or self.max_workers,
            default_output_format=cli_args.output_format or self.default_output_format,
            color_output=self.color_output and not cli_args.quiet,
            show_progress=self.show_progress and not cli_args.quiet,
            log_level=(
                "DEBUG" if cli_args.verbose else ("ERROR" if cli_args.quiet else self.log_level)
            ),
            log_file=self.log_file,
            fail_on_warnings=self.fail_on_warnings,
            strict_mode=self.strict_mode,
            plugin_paths=self.plugin_paths,
            custom_operators=self.custom_operators,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "rule_pack_paths": [str(p) for p in self.rule_pack_paths],
            "default_rule_packs": self.default_rule_packs,
            "cache_enabled": self.cache_enabled,
            "cache_dir": str(self.cache_dir) if self.cache_dir else None,
            "cache_ttl": self.cache_ttl,
            "performance_mode": self.performance_mode,
            "max_workers": self.max_workers,
            "default_output_format": self.default_output_format,
            "color_output": self.color_output,
            "show_progress": self.show_progress,
            "log_level": self.log_level,
            "log_file": str(self.log_file) if self.log_file else None,
            "fail_on_warnings": self.fail_on_warnings,
            "strict_mode": self.strict_mode,
            "plugin_paths": [str(p) for p in self.plugin_paths],
            "custom_operators": self.custom_operators,
        }


@dataclass(frozen=True)
class TerraformConfig:
    """Parsed Terraform configuration."""

    resources: list[dict[str, Any]]
    variables: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    providers: dict[str, Any] = field(default_factory=dict)
    modules: list[dict[str, Any]] = field(default_factory=list)
    data_sources: list[dict[str, Any]] = field(default_factory=list)
    locals: dict[str, Any] = field(default_factory=dict)

    # Metadata
    source_file: Path | None = None
    terraform_version: str | None = None
    required_providers: dict[str, Any] = field(default_factory=dict)

    @property
    def resource_count(self) -> int:
        """Get total number of resources."""
        return len(self.resources)

    @property
    def resource_types(self) -> set[str]:
        """Get set of all resource types."""
        return {resource.get("resource_type", "") for resource in self.resources}

    @property
    def provider_types(self) -> set[str]:
        """Get set of all provider types."""
        provider_types = set()

        # From explicit providers
        provider_types.update(self.providers.keys())

        # From required providers
        provider_types.update(self.required_providers.keys())

        # Infer from resource types
        for resource in self.resources:
            resource_type = resource.get("resource_type", "")
            if "_" in resource_type:
                provider_type = resource_type.split("_")[0]
                provider_types.add(provider_type)

        return provider_types

    def get_resources_by_type(self, resource_type: str) -> list[dict[str, Any]]:
        """Get all resources of a specific type."""
        return [r for r in self.resources if r.get("resource_type") == resource_type]

    def get_resource_by_id(self, resource_id: str) -> dict[str, Any] | None:
        """Get a resource by its ID (type.name)."""
        for resource in self.resources:
            resource_type = resource.get("resource_type", "")
            resource_name = resource.get("name", "")
            if f"{resource_type}.{resource_name}" == resource_id:
                return resource
        return None

    def has_provider(self, provider_name: str) -> bool:
        """Check if configuration uses a specific provider."""
        return provider_name in self.provider_types

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "resources": self.resources,
            "variables": self.variables,
            "outputs": self.outputs,
            "providers": self.providers,
            "modules": self.modules,
            "data_sources": self.data_sources,
            "locals": self.locals,
            "source_file": str(self.source_file) if self.source_file else None,
            "terraform_version": self.terraform_version,
            "required_providers": self.required_providers,
            "metadata": {
                "resource_count": self.resource_count,
                "resource_types": list(self.resource_types),
                "provider_types": list(self.provider_types),
            },
        }
