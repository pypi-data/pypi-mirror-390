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

Example:
    Basic validation:
        results = validate_resources(rules, resources)

    With severity filtering:
        results = validate_resources(rules, resources, min_severity=Severity.WARNING)

    Processing results:
        for result in results:
            if not result.passed:
                print(f"Rule {result.rule.id} failed: {result.message}")
"""

from typing import Any, Dict, List, Optional

from .rules import AssertionResult, Rule, Severity


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
        resource: Dict[str, Any],
        passed: bool,
        message: str,
        assertion_results: Optional[List[AssertionResult]] = None,
        execution_time: float = 0.0,
    ):
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

    def to_dict(self) -> Dict[str, Any]:
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
    rules: List[Rule], resources: List[Dict[str, Any]], min_severity: Severity = Severity.INFO
) -> List[ValidationResult]:
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
    import time

    results = []
    # Track which rules have been applied to at least one resource
    applied_rules = set()

    # Filter rules by minimum severity
    filtered_rules = [
        rule for rule in rules if _severity_meets_minimum(rule.severity, min_severity)
    ]

    for resource in resources:
        # Skip resources without a resource_type
        if "resource_type" not in resource:
            continue

        for rule in filtered_rules:
            # Handle wildcard resource types or exact matches
            if rule.resource_type != "*" and resource.get("resource_type") != rule.resource_type:
                continue

            start_time = time.time()

            if not rule.matches_resource(resource):
                continue

            # Mark this rule as applied to at least one resource
            applied_rules.add(rule.id)

            # Use the enhanced assertion validation
            assertion_results = rule.validate_assertions(resource)

            # Determine overall pass/fail status
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

            # Add result whether it passed or failed
            results.append(
                ValidationResult(
                    rule=rule,
                    resource=resource,
                    passed=all_passed,
                    message=message,
                    assertion_results=assertion_results,
                    execution_time=execution_time,
                )
            )

    # Check for rules that were never applied to any resources
    for rule in filtered_rules:
        if rule.id not in applied_rules:
            # Create a dummy resource with just the resource_type for reporting
            dummy_resource = {"resource_type": rule.resource_type, "id": "N/A"}
            results.append(
                ValidationResult(
                    rule=rule,
                    resource=dummy_resource,
                    passed=False,  # Mark as failed so it stands out
                    message="SKIPPED: No matching resources found for this rule",
                    assertion_results=[],
                    execution_time=0.0,
                )
            )

    return results


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
    results: List[ValidationResult], min_severity: Severity
) -> List[ValidationResult]:
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
