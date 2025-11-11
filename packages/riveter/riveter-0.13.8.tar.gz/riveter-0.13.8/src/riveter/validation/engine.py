"""Modern validation engine implementation.

This module provides the main validation engine with dependency injection,
performance optimizations, and comprehensive error handling.
"""

import time
from dataclasses import dataclass
from typing import Any

from riveter.exceptions import ResourceValidationError as ValidationError
from riveter.logging import debug, error, info, warning
from riveter.models.core import Severity, TerraformResource
from riveter.models.rules import Rule

from .cache import MemoryCache, ValidationResultCache, hash_resource_attributes
from .evaluator import DefaultRuleEvaluator
from .performance import ParallelProcessor
from .protocols import CacheProviderProtocol, PerformanceMonitorProtocol, RuleEvaluatorProtocol
from .result import RuleResult, ValidationResult, ValidationSummary


@dataclass
class ValidationEngineConfig:
    """Configuration for the validation engine."""

    # Performance settings
    parallel_enabled: bool = True
    max_workers: int | None = None
    batch_size: int = 100

    # Caching settings
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes

    # Filtering settings
    min_severity: Severity = Severity.INFO
    include_skipped: bool = False
    fail_fast: bool = False

    # Monitoring settings
    performance_monitoring: bool = True
    detailed_timing: bool = False

    # Error handling settings
    continue_on_error: bool = True
    max_errors: int | None = None


class ValidationEngine:
    """Modern validation engine with dependency injection and performance optimizations.

    This engine provides:
    - Type-safe rule evaluation
    - Parallel processing capabilities
    - Intelligent caching
    - Comprehensive error handling
    - Performance monitoring
    - Extensible evaluator system
    """

    def __init__(
        self,
        evaluator: RuleEvaluatorProtocol | None = None,
        cache_provider: CacheProviderProtocol | None = None,
        performance_monitor: PerformanceMonitorProtocol | None = None,
        config: ValidationEngineConfig | None = None,
    ) -> None:
        """Initialize the validation engine.

        Args:
            evaluator: Rule evaluator implementation
            cache_provider: Cache provider implementation
            performance_monitor: Performance monitor implementation
            config: Engine configuration
        """
        self._evaluator = evaluator or DefaultRuleEvaluator()
        self._cache_provider = cache_provider or (
            MemoryCache() if config and config.cache_enabled else None
        )
        self._performance_monitor = performance_monitor
        self._config = config or ValidationEngineConfig()

        # Performance optimizations
        self._parallel_processor = (
            ParallelProcessor(max_workers=self._config.max_workers)
            if self._config.parallel_enabled
            else None
        )
        self._validation_cache = (
            ValidationResultCache(self._cache_provider) if self._cache_provider else None
        )

        # Statistics
        self._total_evaluations = 0
        self._cache_hits = 0
        self._cache_misses = 0

        info(
            "Validation engine initialized",
            evaluator_type=type(self._evaluator).__name__,
            parallel_enabled=self._config.parallel_enabled,
            cache_enabled=self._config.cache_enabled,
            max_workers=self._config.max_workers,
            cache_provider=type(self._cache_provider).__name__ if self._cache_provider else None,
        )

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
        start_time = time.time()
        timer_id = None

        if self._performance_monitor:
            timer_id = self._performance_monitor.start_timer("validate_resources")

        info(
            "Starting validation",
            rule_count=len(rules),
            resource_count=len(resources),
            parallel_enabled=self._config.parallel_enabled,
        )

        try:
            # Filter rules by severity
            filtered_rules = self._filter_rules_by_severity(rules)

            # Track which rules have been applied
            applied_rules = set()
            results: list[RuleResult] = []
            error_count = 0

            # Generate rule-resource pairs for evaluation
            evaluation_pairs = []
            for resource in resources:
                # Skip resources without resource_type
                if not hasattr(resource, "type") or not resource.type:
                    warning(
                        "Skipping resource without type",
                        resource_id=getattr(resource, "id", "unknown"),
                    )
                    continue

                for rule in filtered_rules:
                    # Check if rule applies to resource type
                    if rule.applies_to_resource_type(resource.type):
                        evaluation_pairs.append((rule, resource))

            debug(f"Generated {len(evaluation_pairs)} rule-resource evaluation pairs")

            # Evaluate rules with performance optimization
            if (
                self._config.parallel_enabled
                and self._parallel_processor
                and len(evaluation_pairs) > self._config.batch_size
            ):
                results.extend(self._evaluate_parallel_optimized(evaluation_pairs))
            else:
                results.extend(self._evaluate_sequential(evaluation_pairs))

            # Track applied rules
            for result in results:
                if not result.metadata.get("skipped", False):
                    applied_rules.add(result.rule_id)
                if result.metadata.get("error", False):
                    error_count += 1
                    if self._config.max_errors and error_count >= self._config.max_errors:
                        warning(
                            f"Maximum error count ({self._config.max_errors}) reached, "
                            f"stopping validation"
                        )
                        break

            # Add results for rules that didn't match any resources
            if not self._config.include_skipped:
                for rule in filtered_rules:
                    if rule.id not in applied_rules:
                        # Create a dummy resource for reporting
                        dummy_resource = TerraformResource(
                            type=rule.resource_type, name="N/A", attributes={}
                        )
                        results.append(
                            RuleResult(
                                rule=rule,
                                resource=dummy_resource,
                                passed=False,
                                message="SKIPPED: No matching resources found for this rule",
                                metadata={"skipped": True, "reason": "no_matching_resources"},
                            )
                        )

            # Calculate summary statistics
            end_time = time.time()
            summary = self._create_summary(
                rules=filtered_rules,
                resources=resources,
                results=results,
                start_time=start_time,
                end_time=end_time,
            )

            if self._performance_monitor and timer_id:
                execution_time = self._performance_monitor.stop_timer(timer_id)
                self._performance_monitor.record_metric(
                    "validation_duration",
                    execution_time,
                    {"rule_count": str(len(rules)), "resource_count": str(len(resources))},
                )

            # Record performance metrics (if monitor available)
            if self._performance_monitor:
                self._performance_monitor.record_metric("cache_hits", self._cache_hits)
                self._performance_monitor.record_metric("cache_misses", self._cache_misses)

            info(
                "Validation completed",
                total_evaluations=summary.total_evaluations,
                passed=summary.passed,
                failed=summary.failed,
                duration=summary.duration,
                cache_hit_rate=self._get_cache_hit_rate(),
                parallel_stats=(
                    self._parallel_processor.performance_stats if self._parallel_processor else None
                ),
            )

            return ValidationResult(
                summary=summary,
                results=results,
                metadata={
                    "engine_config": self._config.__dict__,
                    "cache_stats": {
                        "hits": self._cache_hits,
                        "misses": self._cache_misses,
                        "hit_rate": self._get_cache_hit_rate(),
                    },
                    "performance_stats": {
                        "evaluations_per_second": summary.evaluations_per_second,
                        "parallel_enabled": self._config.parallel_enabled,
                    },
                },
            )

        except Exception as e:
            end_time = time.time()
            error_msg = f"Validation engine error: {e!s}"

            error(
                "Validation engine failed",
                error=str(e),
                duration=end_time - start_time,
                rule_count=len(rules),
                resource_count=len(resources),
            )

            # Create error summary
            summary = ValidationSummary(
                total_rules=len(rules),
                total_resources=len(resources),
                total_evaluations=0,
                passed=0,
                failed=0,
                errors=1,
                warnings=0,
                info=0,
                start_time=start_time,
                end_time=end_time,
                metadata={"error": error_msg},
            )

            return ValidationResult(
                summary=summary, results=[], metadata={"error": error_msg, "exception": str(e)}
            )

    def validate_resource(self, rules: list[Rule], resource: TerraformResource) -> list[RuleResult]:
        """Validate a single resource against multiple rules.

        Args:
            rules: List of rules to apply
            resource: Resource to validate

        Returns:
            List of RuleResult objects
        """
        debug(f"Validating single resource {resource.id} against {len(rules)} rules")

        # Filter rules that apply to this resource
        applicable_rules = [rule for rule in rules if rule.applies_to_resource_type(resource.type)]

        results = []
        for rule in applicable_rules:
            try:
                result = self._evaluate_rule_with_cache(rule, resource)
                results.append(result)

                if self._config.fail_fast and not result.passed:
                    debug(f"Fail-fast enabled, stopping after first failure: {rule.id}")
                    break

            except Exception as e:
                error(
                    "Error evaluating rule against resource",
                    rule_id=rule.id,
                    resource_id=resource.id,
                    error=str(e),
                )

                if not self._config.continue_on_error:
                    raise ValidationError(
                        f"Rule evaluation failed: {e!s}", rule_id=rule.id, resource_id=resource.id
                    ) from e

        return results

    def _filter_rules_by_severity(self, rules: list[Rule]) -> list[Rule]:
        """Filter rules by minimum severity level."""
        severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2}
        min_level = severity_order[self._config.min_severity]

        filtered = [rule for rule in rules if severity_order[rule.severity] >= min_level]

        debug(
            f"Filtered {len(rules)} rules to {len(filtered)} by "
            f"severity >= {self._config.min_severity.value}"
        )
        return filtered

    def _evaluate_parallel_optimized(
        self, evaluation_pairs: list[tuple[Rule, TerraformResource]]
    ) -> list[RuleResult]:
        """Evaluate rules in parallel with performance optimizations."""
        debug(f"Starting optimized parallel evaluation of {len(evaluation_pairs)} pairs")

        # Use the parallel processor for optimized batch processing
        if self._parallel_processor:
            results = self._parallel_processor.process_batch(
                items=evaluation_pairs,
                processor_func=lambda pair: self._evaluate_rule_with_cache(pair[0], pair[1]),
                batch_size=self._config.batch_size,
                timeout=None,  # No timeout for individual batches
            )
        else:
            results = []

        debug(f"Optimized parallel evaluation completed, {len(results)} results")
        return results

    def _evaluate_parallel(
        self, evaluation_pairs: list[tuple[Rule, TerraformResource]]
    ) -> list[RuleResult]:
        """Evaluate rules in parallel (legacy method for backward compatibility)."""
        return self._evaluate_parallel_optimized(evaluation_pairs)

    def _evaluate_sequential(
        self, evaluation_pairs: list[tuple[Rule, TerraformResource]]
    ) -> list[RuleResult]:
        """Evaluate rules sequentially."""
        results = []

        debug(f"Starting sequential evaluation of {len(evaluation_pairs)} pairs")

        for rule, resource in evaluation_pairs:
            try:
                result = self._evaluate_rule_with_cache(rule, resource)
                results.append(result)

                if self._config.fail_fast and not result.passed:
                    debug(f"Fail-fast enabled, stopping after first failure: {rule.id}")
                    break

            except Exception as e:
                error(
                    "Sequential evaluation failed",
                    rule_id=rule.id,
                    resource_id=resource.id,
                    error=str(e),
                )

                if not self._config.continue_on_error:
                    raise

                # Create error result
                results.append(
                    RuleResult(
                        rule=rule,
                        resource=resource,
                        passed=False,
                        message=f"Evaluation error: {e!s}",
                        metadata={"error": True, "exception": str(e)},
                    )
                )

        debug(f"Sequential evaluation completed, {len(results)} results")
        return results

    def _evaluate_rule_with_cache(self, rule: Rule, resource: TerraformResource) -> RuleResult:
        """Evaluate a rule with intelligent caching and performance monitoring."""
        if not self._config.cache_enabled or not self._validation_cache:
            self._cache_misses += 1
            return self._evaluator.evaluate_rule(rule, resource)

        # Generate resource hash for cache key
        resource_hash = hash_resource_attributes(resource.attributes)

        # Try to get from cache
        cached_result = self._validation_cache.get_rule_result(rule.id, resource.id, resource_hash)
        if cached_result:
            self._cache_hits += 1
            debug("Cache hit for rule evaluation", rule_id=rule.id, resource_id=resource.id)
            return cached_result

        # Cache miss - evaluate
        self._cache_misses += 1
        result = self._evaluator.evaluate_rule(rule, resource)

        # Cache the result
        self._validation_cache.set_rule_result(
            rule.id, resource.id, resource_hash, result, self._config.cache_ttl
        )

        debug("Cache miss, result cached", rule_id=rule.id, resource_id=resource.id)
        return result

    def _create_summary(
        self,
        rules: list[Rule],
        resources: list[TerraformResource],
        results: list[RuleResult],
        start_time: float,
        end_time: float,
    ) -> ValidationSummary:
        """Create validation summary from results."""
        # Count results by severity and status
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        errors = sum(1 for r in results if r.severity == Severity.ERROR and not r.passed)
        warnings = sum(1 for r in results if r.severity == Severity.WARNING and not r.passed)
        info_count = sum(1 for r in results if r.severity == Severity.INFO and not r.passed)

        return ValidationSummary(
            total_rules=len(rules),
            total_resources=len(resources),
            total_evaluations=len(results),
            passed=passed,
            failed=failed,
            errors=errors,
            warnings=warnings,
            info=info_count,
            start_time=start_time,
            end_time=end_time,
            metadata={
                "cache_enabled": self._config.cache_enabled,
                "parallel_enabled": self._config.parallel_enabled,
                "min_severity": self._config.min_severity.value,
            },
        )

    def _get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_requests = self._cache_hits + self._cache_misses
        if total_requests == 0:
            return 0.0
        return (self._cache_hits / total_requests) * 100.0

    @property
    def config(self) -> ValidationEngineConfig:
        """Get engine configuration."""
        return self._config

    @property
    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": self._get_cache_hit_rate(),
        }

    def clear_cache(self) -> None:
        """Clear the validation cache."""
        if self._cache_provider:
            self._cache_provider.clear()
            info("Validation cache cleared")

    def update_config(self, **kwargs: Any) -> None:
        """Update engine configuration."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                debug(f"Updated config: {key} = {value}")
            else:
                warning(f"Unknown config key: {key}")

        info("Validation engine configuration updated", **kwargs)
