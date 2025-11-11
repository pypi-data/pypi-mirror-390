"""Rule evaluation implementations.

This module provides the core rule evaluation logic with type safety,
performance optimizations, and comprehensive error handling.
"""

import time
from typing import Any

from riveter.exceptions import ResourceValidationError as ValidationError
from riveter.exceptions import handle_error_with_recovery
from riveter.logging import debug, error, warning
from riveter.models.core import TerraformResource
from riveter.models.rules import Rule
from riveter.operators import AttributeResolutionError, NestedAttributeResolver, OperatorFactory

from .result import AssertionResult, RuleResult


class RuleEvaluator:
    """Base class for rule evaluators."""

    def __init__(self):
        """Initialize the rule evaluator."""
        self._resolver = NestedAttributeResolver()

    def can_evaluate_rule(self, rule: Rule) -> bool:
        """Check if this evaluator can handle the given rule."""
        _ = rule  # Mark as intentionally unused
        return True  # Base evaluator can handle all rules

    def evaluate_rule(self, rule: Rule, resource: TerraformResource) -> RuleResult:
        """Evaluate a single rule against a resource."""
        start_time = time.time()

        try:
            # Check if rule applies to this resource type
            if not rule.applies_to_resource_type(resource.type):
                return RuleResult(
                    rule=rule,
                    resource=resource,
                    passed=False,
                    message=f"Rule does not apply to resource type '{resource.type}'",
                    execution_time=time.time() - start_time,
                    metadata={"skipped": True, "reason": "resource_type_mismatch"},
                )

            # Check filter conditions
            if not self._matches_filter(rule, resource):
                return RuleResult(
                    rule=rule,
                    resource=resource,
                    passed=True,  # Filtered resources are considered passing
                    message="Resource filtered out by rule conditions",
                    execution_time=time.time() - start_time,
                    metadata={"skipped": True, "reason": "filter_mismatch"},
                )

            # Evaluate assertions
            assertion_results = self._evaluate_assertions(rule, resource)

            # Determine overall result
            all_passed = all(ar.passed for ar in assertion_results)

            # Create summary message
            if all_passed:
                message = "All checks passed"
            else:
                failed_assertions = [ar for ar in assertion_results if not ar.passed]
                if len(failed_assertions) == 1:
                    message = failed_assertions[0].message
                else:
                    message = f"{len(failed_assertions)} assertion(s) failed"

            execution_time = time.time() - start_time

            debug(
                "Rule evaluation completed",
                rule_id=rule.id,
                resource_id=resource.id,
                passed=all_passed,
                execution_time=execution_time,
                assertion_count=len(assertion_results),
            )

            return RuleResult(
                rule=rule,
                resource=resource,
                passed=all_passed,
                message=message,
                assertion_results=assertion_results,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error evaluating rule '{rule.id}' against resource '{resource.id}': {e!s}"

            error(
                "Rule evaluation failed",
                rule_id=rule.id,
                resource_id=resource.id,
                error=str(e),
                execution_time=execution_time,
            )

            # Try to recover from the error
            try:
                validation_error = ValidationError(
                    error_msg,
                    rule_id=rule.id,
                    resource_id=resource.id,
                    suggestions=[
                        "Check the rule definition for syntax errors",
                        "Verify the resource structure is valid",
                        "Check for missing or invalid operators",
                    ],
                )
                handle_error_with_recovery(validation_error)
            except ValidationError:
                # Recovery failed, return error result
                pass

            return RuleResult(
                rule=rule,
                resource=resource,
                passed=False,
                message=error_msg,
                execution_time=execution_time,
                metadata={"error": True, "exception": str(e)},
            )

    def _matches_filter(self, rule: Rule, resource: TerraformResource) -> bool:
        """Check if a resource matches the rule's filter conditions."""
        if rule.filter.is_empty:
            return True

        for condition in rule.filter.conditions:
            try:
                actual = self._resolver.resolve_path(resource.attributes, condition.field)

                if condition.operator == "present":
                    result = actual is not None
                elif condition.operator == "eq":
                    result = actual == condition.value
                else:
                    # Use operator factory for complex operators
                    operator = OperatorFactory.create_operator(
                        {condition.operator: condition.value}
                    )
                    result = operator.evaluate(actual, condition.value)

                # Apply negation if needed
                if condition.negate:
                    result = not result

                # For AND logic, if any condition fails, return False
                if rule.filter.logic == "AND" and not result:
                    return False
                # For OR logic, if any condition passes, we need to continue checking all
                if rule.filter.logic == "OR" and result:
                    return True

            except AttributeResolutionError:
                # If we can't resolve the path, condition fails
                if rule.filter.logic == "AND":
                    return False
                # For OR logic, continue to next condition

        # For AND logic, all conditions passed
        # For OR logic, no conditions passed
        return rule.filter.logic == "AND"

    def _evaluate_assertions(
        self, rule: Rule, resource: TerraformResource
    ) -> list[AssertionResult]:
        """Evaluate all assertions in a rule against a resource."""
        results: list[AssertionResult] = []

        for condition in rule.assertion.conditions:
            start_time = time.time()

            try:
                actual = self._resolver.resolve_path(resource.attributes, condition.field)

                if condition.operator == "present":
                    passed = actual is not None
                    if passed:
                        message = "Property is present"
                    # Format message to match old behavior
                    elif condition.field.startswith("tags."):
                        tag_name = condition.field.split(".", 1)[1]
                        message = f"Required tag '{tag_name}' is missing"
                    else:
                        message = f"Property '{condition.field}' is missing"
                elif condition.operator == "eq":
                    passed = actual == condition.value
                    if passed:
                        message = "Values match"
                    # Format message to match old behavior
                    elif condition.field.startswith("tags."):
                        tag_name = condition.field.split(".", 1)[1]
                        message = (
                            f"Tag '{tag_name}' has value '{actual}' "
                            f"but expected '{condition.value}'"
                        )
                    else:
                        message = (
                            f"Property '{condition.field}' has value '{actual}' "
                            f"but expected '{condition.value}'"
                        )
                else:
                    # Use operator factory for complex operators
                    operator = OperatorFactory.create_operator(
                        {condition.operator: condition.value}
                    )
                    passed = operator.evaluate(actual, condition.value)
                    message = (
                        "Assertion passed"
                        if passed
                        else operator.get_error_message(actual, condition.value)
                    )

                # Apply negation if needed
                if condition.negate:
                    passed = not passed
                    message = f"NOT ({message})"

                execution_time = time.time() - start_time

                results.append(
                    AssertionResult(
                        property_path=condition.field,
                        operator=condition.operator,
                        expected=condition.value,
                        actual=actual,
                        passed=passed,
                        message=message,
                        execution_time=execution_time,
                    )
                )

            except AttributeResolutionError as e:
                execution_time = time.time() - start_time
                results.append(
                    AssertionResult(
                        property_path=condition.field,
                        operator=condition.operator,
                        expected=condition.value,
                        actual=None,
                        passed=False,
                        message=f"Failed to resolve path: {e!s}",
                        execution_time=execution_time,
                    )
                )
            except Exception as e:
                execution_time = time.time() - start_time
                error_msg = f"Error evaluating assertion: {e!s}"

                warning(
                    "Assertion evaluation failed",
                    rule_id=rule.id,
                    resource_id=resource.id,
                    field=condition.field,
                    operator=condition.operator,
                    error=str(e),
                )

                results.append(
                    AssertionResult(
                        property_path=condition.field,
                        operator=condition.operator,
                        expected=condition.value,
                        actual=None,
                        passed=False,
                        message=error_msg,
                        execution_time=execution_time,
                    )
                )

        return results


class DefaultRuleEvaluator(RuleEvaluator):
    """Default implementation of rule evaluator.

    This is the standard rule evaluator that handles all common rule types
    and operators. It can be extended or replaced with custom implementations.
    """

    def __init__(self):
        """Initialize the default rule evaluator."""
        super().__init__()
        debug("Default rule evaluator initialized")

    def can_evaluate_rule(self, rule: Rule) -> bool:
        """Check if this evaluator can handle the given rule."""
        # Default evaluator can handle all standard rules
        return rule.scope.value in ["resource", "configuration"]


class CachingRuleEvaluator(RuleEvaluator):
    """Rule evaluator with caching capabilities.

    This evaluator caches evaluation results to improve performance
    for repeated evaluations of the same rule-resource combinations.
    """

    def __init__(self, cache_provider: Any = None) -> None:
        """Initialize the caching rule evaluator.

        Args:
            cache_provider: Optional cache provider implementation
        """
        super().__init__()
        self._cache = cache_provider or {}
        debug("Caching rule evaluator initialized")

    def evaluate_rule(self, rule: Rule, resource: TerraformResource) -> RuleResult:
        """Evaluate a rule with caching."""
        # Create cache key from rule and resource
        cache_key = f"{rule.id}:{resource.id}:{hash(str(resource.attributes))}"

        # Check cache first
        if hasattr(self._cache, "get"):
            cached_result = self._cache.get(cache_key)
            if cached_result:
                debug("Cache hit for rule evaluation", rule_id=rule.id, resource_id=resource.id)
                return cached_result
        elif isinstance(self._cache, dict) and cache_key in self._cache:
            debug("Cache hit for rule evaluation", rule_id=rule.id, resource_id=resource.id)
            return self._cache[cache_key]

        # Evaluate and cache result
        result = super().evaluate_rule(rule, resource)

        if hasattr(self._cache, "set"):
            self._cache.set(cache_key, result, ttl=300)  # 5 minute TTL
        elif isinstance(self._cache, dict):
            self._cache[cache_key] = result

        debug("Cache miss, result cached", rule_id=rule.id, resource_id=resource.id)
        return result
