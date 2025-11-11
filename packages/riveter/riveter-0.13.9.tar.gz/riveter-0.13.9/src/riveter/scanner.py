"""Resource validation and rule enforcement.

This module provides the core validation functionality for Riveter, including
the ValidationResult class for storing validation outcomes and the main
validate_resources function that applies rules to Terraform resources.

The scanner supports:
- Advanced operator-based assertions
- Severity-based filtering
- Detailed assertion result tracking
- Performance timing measurements
- Comprehensive error reporting
- Modern validation engine with dependency injection
- Parallel processing capabilities
- Intelligent caching

Example:
    Basic validation:
        results = validate_resources(rules, resources)

    With severity filtering:
        results = validate_resources(rules, resources, min_severity=Severity.WARNING)

    Processing results:
        for result in results:
            if not result.passed:
                print(f"Rule {result.rule.id} failed: {result.message}")

    Using modern validation engine:
        engine = ValidationEngine()
        result = engine.validate_resources(rules, terraform_resources)
"""

from typing import Any

from .logging import debug, info
from .models.core import Severity, TerraformResource
from .models.rules import Rule
from .rules import AssertionResult
from .validation import ValidationEngine, ValidationEngineConfig


class ValidationResult:
    """Represents the result of validating a resource against a rule.

    This class encapsulates all information about a single validation operation,
    including the rule that was applied, the resource that was checked, whether
    the validation passed, and detailed assertion results.

    Attributes:
        rule: The Rule object that was applied
        resource: The resource dictionary that was validated
        passed: Whether the overall validation passed
        message: Summary message describing the result
        severity: Severity level from the rule
        assertion_results: List of individual assertion results
        execution_time: Time taken to perform the validation

    Example:
        result = ValidationResult(
            rule=my_rule,
            resource=my_resource,
            passed=False,
            message="Security group allows unrestricted access",
            assertion_results=[assertion1, assertion2],
            execution_time=0.001
        )
    """

    def __init__(
        self,
        rule: Rule,
        resource: dict[str, Any],
        passed: bool,
        message: str,
        assertion_results: list[AssertionResult] | None = None,
        execution_time: float = 0.0,
    ) -> None:
        """Initialize a ValidationResult.

        Args:
            rule: The Rule object that was applied
            resource: The resource dictionary that was validated
            passed: Whether the overall validation passed
            message: Summary message describing the result
            assertion_results: List of individual assertion results
            execution_time: Time taken to perform the validation in seconds
        """
        self.rule = rule
        self.resource = resource
        self.passed = passed
        self.message = message
        self.severity = rule.severity
        self.assertion_results = assertion_results or []
        self.execution_time = execution_time

    def to_dict(self) -> dict[str, Any]:
        """Convert validation result to dictionary format.

        Returns:
            Dictionary representation of the validation result, suitable
            for JSON serialization or structured logging.

        Example:
            result_dict = result.to_dict()
            print(json.dumps(result_dict, indent=2))
        """
        return {
            "rule_id": self.rule.id,
            "resource_type": self.resource.get("resource_type"),
            "resource_id": self.resource.get("id"),
            "passed": self.passed,
            "severity": self.severity.value,
            "message": self.message,
            "execution_time": self.execution_time,
            "assertion_results": [
                {
                    "property_path": ar.property_path,
                    "operator": ar.operator,
                    "expected": ar.expected,
                    "actual": ar.actual,
                    "passed": ar.passed,
                    "message": ar.message,
                }
                for ar in self.assertion_results
            ],
        }


def validate_resources(
    rules: list[Rule], resources: list[dict[str, Any]], min_severity: Severity = Severity.INFO
) -> list[ValidationResult]:
    """Validate resources against rules using advanced operator framework.

    This is the main validation function that applies a list of rules to a list
    of Terraform resources. It supports advanced operators, severity filtering,
    and comprehensive result tracking.

    The function:
    1. Filters rules by minimum severity level
    2. Matches rules to resources by resource type
    3. Applies rule filters to determine applicability
    4. Executes assertions using the advanced operator framework
    5. Tracks execution time for performance analysis
    6. Reports rules that didn't match any resources

    Args:
        rules: List of Rule objects to apply to resources
        resources: List of resource dictionaries from Terraform configuration
        min_severity: Minimum severity level to include in results (default: INFO)

    Returns:
        List of ValidationResult objects, one for each rule-resource combination
        that was evaluated, plus entries for rules that matched no resources.

    Example:
        # Basic validation
        results = validate_resources(rules, resources)

        # Only show warnings and errors
        results = validate_resources(rules, resources, Severity.WARNING)

        # Process results
        failed_results = [r for r in results if not r.passed]
        for result in failed_results:
            print(f"FAIL: {result.rule.id} - {result.message}")
    """
    debug(f"Starting validation with {len(rules)} rules and {len(resources)} resources")

    # Convert dictionary resources to TerraformResource objects
    terraform_resources = []
    for resource_dict in resources:
        if "resource_type" not in resource_dict:
            continue

        terraform_resource = TerraformResource(
            type=resource_dict["resource_type"],
            name=resource_dict.get("name", resource_dict.get("id", "unknown")),
            attributes=resource_dict,
        )
        terraform_resources.append(terraform_resource)

    # Use modern validation engine with backward compatibility
    config = ValidationEngineConfig(
        min_severity=min_severity,
        parallel_enabled=False,  # Disable parallel processing for now
        cache_enabled=False,  # Disable caching for now
        include_skipped=True,  # Include skipped results for backward compatibility
        performance_monitoring=False,  # Disable performance monitoring for now
    )

    engine = ValidationEngine(config=config)
    modern_result = engine.validate_resources(rules, terraform_resources)

    # Convert modern results back to legacy ValidationResult format
    legacy_results = []
    for rule_result in modern_result.results:
        # Convert TerraformResource back to dict for backward compatibility
        resource_dict = rule_result.resource.attributes.copy()
        resource_dict["resource_type"] = rule_result.resource.type
        resource_dict["id"] = rule_result.resource.name

        legacy_result = ValidationResult(
            rule=rule_result.rule,
            resource=resource_dict,
            passed=rule_result.passed,
            message=rule_result.message,
            assertion_results=rule_result.assertion_results,
            execution_time=rule_result.execution_time,
        )
        legacy_results.append(legacy_result)

    info(
        "Validation completed",
        total_results=len(legacy_results),
        passed=len([r for r in legacy_results if r.passed]),
        failed=len([r for r in legacy_results if not r.passed]),
        duration=modern_result.summary.duration,
    )

    return legacy_results


def _severity_meets_minimum(rule_severity: Severity, min_severity: Severity) -> bool:
    """Check if rule severity meets the minimum threshold.

    Args:
        rule_severity: The severity level of the rule
        min_severity: The minimum severity threshold

    Returns:
        True if the rule severity is at or above the minimum threshold

    Example:
        # ERROR meets WARNING threshold
        assert _severity_meets_minimum(Severity.ERROR, Severity.WARNING) == True

        # INFO does not meet WARNING threshold
        assert _severity_meets_minimum(Severity.INFO, Severity.WARNING) == False
    """
    severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2}

    return severity_order[rule_severity] >= severity_order[min_severity]


def filter_results_by_severity(
    results: list[ValidationResult], min_severity: Severity
) -> list[ValidationResult]:
    """Filter validation results by minimum severity level.

    Args:
        results: List of ValidationResult objects to filter
        min_severity: Minimum severity level to include

    Returns:
        Filtered list containing only results at or above the minimum severity

    Example:
        # Only show errors and warnings
        important_results = filter_results_by_severity(results, Severity.WARNING)

        # Only show errors
        error_results = filter_results_by_severity(results, Severity.ERROR)
    """
    return [result for result in results if _severity_meets_minimum(result.severity, min_severity)]
