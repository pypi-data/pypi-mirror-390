"""Protocol interfaces for the validation engine.

This module defines the protocol interfaces that enable dependency injection
and extensibility in the validation system.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from riveter.models.core import TerraformResource
from riveter.models.rules import Rule

from .result import RuleResult, ValidationResult


@runtime_checkable
class RuleEvaluatorProtocol(Protocol):
    """Protocol for rule evaluation implementations."""

    @abstractmethod
    def evaluate_rule(self, rule: Rule, resource: TerraformResource) -> RuleResult:
        """Evaluate a single rule against a resource.

        Args:
            rule: The rule to evaluate
            resource: The resource to validate

        Returns:
            RuleResult containing the evaluation outcome
        """
        ...

    @abstractmethod
    def can_evaluate_rule(self, rule: Rule) -> bool:
        """Check if this evaluator can handle the given rule.

        Args:
            rule: The rule to check

        Returns:
            True if this evaluator can handle the rule
        """
        ...


@runtime_checkable
class ValidationEngineProtocol(Protocol):
    """Protocol for validation engine implementations."""

    @abstractmethod
    def validate_resources(
        self, rules: list[Rule], resources: list[TerraformResource]
    ) -> ValidationResult:
        """Validate resources against rules.

        Args:
            rules: List of rules to apply
            resources: List of resources to validate

        Returns:
            ValidationResult containing all evaluation outcomes
        """
        ...

    @abstractmethod
    def validate_resource(self, rules: list[Rule], resource: TerraformResource) -> list[RuleResult]:
        """Validate a single resource against multiple rules.

        Args:
            rules: List of rules to apply
            resource: Resource to validate

        Returns:
            List of RuleResult objects
        """
        ...


@runtime_checkable
class CacheProviderProtocol(Protocol):
    """Protocol for caching implementations."""

    @abstractmethod
    def get(self, key: str) -> any:
        """Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    @abstractmethod
    def set(self, key: str, value: any, ttl: int | None = None) -> None:
        """Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        ...


@runtime_checkable
class PerformanceMonitorProtocol(Protocol):
    """Protocol for performance monitoring implementations."""

    @abstractmethod
    def start_timer(self, operation: str) -> str:
        """Start timing an operation.

        Args:
            operation: Name of the operation

        Returns:
            Timer ID for stopping the timer
        """
        ...

    @abstractmethod
    def stop_timer(self, timer_id: str) -> float:
        """Stop timing an operation.

        Args:
            timer_id: Timer ID from start_timer

        Returns:
            Elapsed time in seconds
        """
        ...

    @abstractmethod
    def record_metric(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a performance metric.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for the metric
        """
        ...
