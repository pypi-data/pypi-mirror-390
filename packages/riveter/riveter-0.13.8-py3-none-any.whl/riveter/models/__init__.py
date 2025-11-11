"""Core data models and type definitions for Riveter.

This module provides immutable data classes and type definitions for all
core entities in the Riveter system, including configurations, rules,
resources, and validation results.
"""

from .config import CLIArgs, ConfigurationSource, RiveterConfig, TerraformConfig
from .core import (
    RuleResult,
    Severity,
    SourceLocation,
    TerraformResource,
    ValidationResult,
    ValidationSummary,
)
from .protocols import (
    CacheProvider,
    ConfigurationParser,
    FormatterPlugin,
    OutputFormatter,
    ParserPlugin,
    PluginInterface,
    RuleEvaluator,
    RulePlugin,
    RuleRepository,
    ValidationEngine,
)
from .rules import Rule, RuleAssertion, RuleCondition, RuleFilter, RuleMetadata, RulePack, RuleScope
from .types import (
    JSON,
    AttributeValue,
    ConfigDict,
    FilterFunction,
    JSONDict,
    JSONList,
    OptionalPath,
    PathLike,
    ResourceDict,
    Result,
    RuleDict,
    TransformFunction,
    ValidationFunction,
    to_optional_path,
    to_path,
    validate_directory_exists,
    validate_file_exists,
    validate_non_empty_string,
    validate_positive_int,
)

__all__ = [
    # Core types
    "Severity",
    "SourceLocation",
    "TerraformResource",
    "RuleResult",
    "ValidationSummary",
    "ValidationResult",
    # Configuration types
    "CLIArgs",
    "RiveterConfig",
    "TerraformConfig",
    "ConfigurationSource",
    # Rule types
    "Rule",
    "RulePack",
    "RuleCondition",
    "RuleFilter",
    "RuleAssertion",
    "RuleMetadata",
    "RuleScope",
    # Protocol interfaces
    "ConfigurationParser",
    "RuleRepository",
    "RuleEvaluator",
    "OutputFormatter",
    "ValidationEngine",
    "CacheProvider",
    "PluginInterface",
    "RulePlugin",
    "FormatterPlugin",
    "ParserPlugin",
    # Type utilities
    "JSON",
    "JSONDict",
    "JSONList",
    "PathLike",
    "OptionalPath",
    "ResourceDict",
    "RuleDict",
    "ConfigDict",
    "AttributeValue",
    "Result",
    "ValidationFunction",
    "FilterFunction",
    "TransformFunction",
    "to_path",
    "to_optional_path",
    "validate_non_empty_string",
    "validate_positive_int",
    "validate_file_exists",
    "validate_directory_exists",
]
