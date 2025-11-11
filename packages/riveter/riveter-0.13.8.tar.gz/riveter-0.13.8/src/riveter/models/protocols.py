"""Protocol interfaces for Riveter components.

This module defines protocol interfaces that establish contracts
between different components of the Riveter system, enabling
dependency injection and extensibility.
"""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from .config import RiveterConfig, TerraformConfig
from .core import RuleResult, TerraformResource, ValidationResult
from .rules import Rule, RulePack


@runtime_checkable
class ConfigurationParser(Protocol):
    """Protocol for parsing Terraform configurations."""

    def parse_file(self, file_path: Path) -> TerraformConfig:
        """Parse a Terraform configuration file.

        Args:
            file_path: Path to the Terraform file

        Returns:
            Parsed Terraform configuration

        Raises:
            ConfigurationError: If parsing fails
        """
        ...

    def parse_directory(self, directory_path: Path) -> TerraformConfig:
        """Parse all Terraform files in a directory.

        Args:
            directory_path: Path to directory containing Terraform files

        Returns:
            Combined Terraform configuration

        Raises:
            ConfigurationError: If parsing fails
        """
        ...

    def validate_syntax(self, file_path: Path) -> bool:
        """Validate Terraform file syntax.

        Args:
            file_path: Path to the Terraform file

        Returns:
            True if syntax is valid, False otherwise
        """
        ...


@runtime_checkable
class RuleRepository(Protocol):
    """Protocol for loading and managing validation rules."""

    def load_rules_from_file(self, file_path: Path) -> list[Rule]:
        """Load rules from a file.

        Args:
            file_path: Path to the rules file

        Returns:
            List of loaded rules

        Raises:
            RuleError: If loading fails
        """
        ...

    def load_rule_pack(self, pack_name: str) -> RulePack:
        """Load a rule pack by name.

        Args:
            pack_name: Name of the rule pack

        Returns:
            Loaded rule pack

        Raises:
            RuleError: If pack not found or loading fails
        """
        ...

    def list_available_packs(self) -> list[str]:
        """List all available rule packs.

        Returns:
            List of rule pack names
        """
        ...

    def validate_rule(self, rule: Rule) -> bool:
        """Validate a rule definition.

        Args:
            rule: Rule to validate

        Returns:
            True if rule is valid, False otherwise
        """
        ...


@runtime_checkable
class RuleEvaluator(Protocol):
    """Protocol for evaluating rules against resources."""

    def evaluate_rule(self, rule: Rule, resource: TerraformResource) -> RuleResult:
        """Evaluate a single rule against a resource.

        Args:
            rule: Rule to evaluate
            resource: Resource to evaluate against

        Returns:
            Result of rule evaluation
        """
        ...

    def evaluate_rules(self, rules: list[Rule], resource: TerraformResource) -> list[RuleResult]:
        """Evaluate multiple rules against a resource.

        Args:
            rules: Rules to evaluate
            resource: Resource to evaluate against

        Returns:
            List of rule evaluation results
        """
        ...

    def supports_operator(self, operator: str) -> bool:
        """Check if evaluator supports a specific operator.

        Args:
            operator: Operator name to check

        Returns:
            True if operator is supported, False otherwise
        """
        ...


@runtime_checkable
class ValidationEngine(Protocol):
    """Protocol for the main validation engine."""

    def validate(
        self, config: TerraformConfig, rules: list[Rule], app_config: RiveterConfig | None = None
    ) -> ValidationResult:
        """Validate a Terraform configuration against rules.

        Args:
            config: Terraform configuration to validate
            rules: Rules to apply
            app_config: Optional application configuration

        Returns:
            Complete validation result
        """
        ...

    def validate_resource(self, resource: TerraformResource, rules: list[Rule]) -> list[RuleResult]:
        """Validate a single resource against rules.

        Args:
            resource: Resource to validate
            rules: Rules to apply

        Returns:
            List of rule results for the resource
        """
        ...


@runtime_checkable
class OutputFormatter(Protocol):
    """Protocol for formatting validation results."""

    def format(self, result: ValidationResult) -> str:
        """Format validation result for output.

        Args:
            result: Validation result to format

        Returns:
            Formatted output string
        """
        ...

    def format_summary(self, result: ValidationResult) -> str:
        """Format just the summary portion of results.

        Args:
            result: Validation result to format

        Returns:
            Formatted summary string
        """
        ...

    @property
    def format_name(self) -> str:
        """Get the name of this output format."""
        ...

    @property
    def file_extension(self) -> str:
        """Get the recommended file extension for this format."""
        ...


@runtime_checkable
class CacheProvider(Protocol):
    """Protocol for caching parsed configurations and results."""

    def get(self, key: str) -> Any | None:
        """Get a cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a cached value.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        ...

    def delete(self, key: str) -> bool:
        """Delete a cached value.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if not found
        """
        ...

    def clear(self) -> None:
        """Clear all cached values."""
        ...

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        ...


@runtime_checkable
class PluginInterface(Protocol):
    """Protocol for Riveter plugins."""

    @property
    def name(self) -> str:
        """Get plugin name."""
        ...

    @property
    def version(self) -> str:
        """Get plugin version."""
        ...

    def initialize(self, config: RiveterConfig) -> None:
        """Initialize the plugin.

        Args:
            config: Application configuration
        """
        ...

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        ...


@runtime_checkable
class RulePlugin(PluginInterface, Protocol):
    """Protocol for rule-based plugins."""

    def get_custom_operators(self) -> dict[str, Any]:
        """Get custom operators provided by this plugin.

        Returns:
            Dictionary mapping operator names to implementations
        """
        ...

    def get_rule_packs(self) -> list[RulePack]:
        """Get rule packs provided by this plugin.

        Returns:
            List of rule packs
        """
        ...


@runtime_checkable
class FormatterPlugin(PluginInterface, Protocol):
    """Protocol for output formatter plugins."""

    def get_formatters(self) -> dict[str, OutputFormatter]:
        """Get output formatters provided by this plugin.

        Returns:
            Dictionary mapping format names to formatter instances
        """
        ...


@runtime_checkable
class ParserPlugin(PluginInterface, Protocol):
    """Protocol for configuration parser plugins."""

    def get_parsers(self) -> dict[str, ConfigurationParser]:
        """Get configuration parsers provided by this plugin.

        Returns:
            Dictionary mapping parser names to parser instances
        """
        ...

    def get_supported_extensions(self) -> list[str]:
        """Get file extensions supported by this plugin.

        Returns:
            List of file extensions (including the dot)
        """
        ...
