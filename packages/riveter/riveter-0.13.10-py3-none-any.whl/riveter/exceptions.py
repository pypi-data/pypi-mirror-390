"""
Custom exception hierarchy for Riveter.

This module defines specific exception types for different failure scenarios
and provides error recovery strategies with graceful degradation.
"""

from typing import Any, Dict, List, Optional


class RiveterError(Exception):
    """Base exception for all Riveter errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestions = suggestions or []

    def __str__(self) -> str:
        """Return formatted error message with details and suggestions."""
        result = self.message

        if self.details:
            result += f"\nDetails: {self.details}"

        if self.suggestions:
            result += "\nSuggestions:"
            for suggestion in self.suggestions:
                result += f"\n  - {suggestion}"

        return result


class ConfigurationError(RiveterError):
    """Errors related to configuration parsing and validation."""

    def __init__(
        self,
        message: str,
        config_file: Optional[str] = None,
        line_number: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.config_file = config_file
        self.line_number = line_number

        # Add file and line info to details
        if config_file:
            self.details["config_file"] = config_file
        if line_number:
            self.details["line_number"] = line_number


class TerraformParsingError(RiveterError):
    """Errors parsing Terraform files."""

    def __init__(
        self,
        message: str,
        terraform_file: Optional[str] = None,
        hcl_error: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.terraform_file = terraform_file
        self.hcl_error = hcl_error

        # Add terraform-specific details
        if terraform_file:
            self.details["terraform_file"] = terraform_file
        if hcl_error:
            self.details["hcl_error"] = hcl_error

        # Add common suggestions for Terraform parsing errors
        if not self.suggestions:
            self.suggestions = [
                "Check for syntax errors in the Terraform file",
                "Ensure all brackets and quotes are properly closed",
                "Verify that the file is valid HCL format",
                "Try running 'terraform validate' on the file",
            ]


class RuleValidationError(RiveterError):
    """Errors in rule definitions and validation."""

    def __init__(
        self,
        message: str,
        rule_id: Optional[str] = None,
        rule_file: Optional[str] = None,
        field_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.rule_id = rule_id
        self.rule_file = rule_file
        self.field_path = field_path

        # Add rule-specific details
        if rule_id:
            self.details["rule_id"] = rule_id
        if rule_file:
            self.details["rule_file"] = rule_file
        if field_path:
            self.details["field_path"] = field_path


class RulePackError(RiveterError):
    """Errors in rule pack operations."""

    def __init__(
        self,
        message: str,
        pack_name: Optional[str] = None,
        pack_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.pack_name = pack_name
        self.pack_version = pack_version

        # Add pack-specific details
        if pack_name:
            self.details["pack_name"] = pack_name
        if pack_version:
            self.details["pack_version"] = pack_version


class ResourceValidationError(RiveterError):
    """Errors during resource validation against rules."""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_name: Optional[str] = None,
        rule_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.rule_id = rule_id

        # Add resource-specific details
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_name:
            self.details["resource_name"] = resource_name
        if rule_id:
            self.details["rule_id"] = rule_id


class OperatorError(RiveterError):
    """Errors in operator evaluation and comparison logic."""

    def __init__(
        self,
        message: str,
        operator: Optional[str] = None,
        expected_value: Optional[Any] = None,
        actual_value: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.operator = operator
        self.expected_value = expected_value
        self.actual_value = actual_value

        # Add operator-specific details
        if operator:
            self.details["operator"] = operator
        if expected_value is not None:
            self.details["expected_value"] = expected_value
        if actual_value is not None:
            self.details["actual_value"] = actual_value


class CloudProviderError(RiveterError):
    """Errors related to cloud provider parsing and handling."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        resource_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.provider = provider
        self.resource_type = resource_type

        # Add provider-specific details
        if provider:
            self.details["provider"] = provider
        if resource_type:
            self.details["resource_type"] = resource_type


class FileSystemError(RiveterError):
    """Errors related to file system operations."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.operation = operation

        # Add filesystem-specific details
        if file_path:
            self.details["file_path"] = file_path
        if operation:
            self.details["operation"] = operation

        # Add common suggestions for filesystem errors
        if not self.suggestions:
            self.suggestions = [
                "Check that the file or directory exists",
                "Verify that you have the necessary permissions",
                "Ensure the path is correct and accessible",
            ]


class ValidationSummaryError(RiveterError):
    """Error that aggregates multiple validation failures."""

    def __init__(self, message: str, errors: List[RiveterError], **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.errors = errors
        self.details["error_count"] = len(errors)
        self.details["error_types"] = [type(error).__name__ for error in errors]

    def get_errors_by_type(self, error_type: type) -> List[RiveterError]:
        """Get all errors of a specific type."""
        return [error for error in self.errors if isinstance(error, error_type)]

    def has_critical_errors(self) -> bool:
        """Check if any errors are considered critical."""
        critical_types = (TerraformParsingError, ConfigurationError, RulePackError)
        return any(isinstance(error, critical_types) for error in self.errors)


# Error recovery strategies
class ErrorRecoveryStrategy:
    """Base class for error recovery strategies."""

    def can_recover(self, error: RiveterError) -> bool:
        """Check if this strategy can recover from the given error."""
        raise NotImplementedError

    def recover(self, error: RiveterError) -> Any:
        """Attempt to recover from the error."""
        raise NotImplementedError


class SkipResourceStrategy(ErrorRecoveryStrategy):
    """Strategy to skip problematic resources and continue processing."""

    def can_recover(self, error: RiveterError) -> bool:
        """Can recover from resource-level errors."""
        return isinstance(error, (ResourceValidationError, OperatorError))

    def recover(self, error: RiveterError) -> None:
        """Skip the problematic resource."""
        from .logging import warning

        warning(
            f"Skipping resource due to error: {error.message}",
            error_type=type(error).__name__,
            **error.details,
        )


class SkipRuleStrategy(ErrorRecoveryStrategy):
    """Strategy to skip problematic rules and continue with others."""

    def can_recover(self, error: RiveterError) -> bool:
        """Can recover from rule-level errors."""
        return isinstance(error, RuleValidationError)

    def recover(self, error: RiveterError) -> None:
        """Skip the problematic rule."""
        from .logging import warning

        warning(
            f"Skipping rule due to error: {error.message}",
            error_type=type(error).__name__,
            **error.details,
        )


class FallbackParsingStrategy(ErrorRecoveryStrategy):
    """Strategy to use fallback parsing when cloud-specific parsing fails."""

    def can_recover(self, error: RiveterError) -> bool:
        """Can recover from cloud provider parsing errors."""
        return isinstance(error, CloudProviderError)

    def recover(self, error: RiveterError) -> Dict[str, Any]:
        """Use generic parsing as fallback."""
        from .logging import warning

        warning(
            f"Using fallback parsing due to error: {error.message}",
            error_type=type(error).__name__,
            **error.details,
        )
        return {}


class ErrorRecoveryManager:
    """Manages error recovery strategies."""

    def __init__(self) -> None:
        self.strategies = [SkipResourceStrategy(), SkipRuleStrategy(), FallbackParsingStrategy()]

    def attempt_recovery(self, error: RiveterError) -> Optional[Any]:
        """Attempt to recover from an error using available strategies."""
        for strategy in self.strategies:
            if strategy.can_recover(error):
                try:
                    return strategy.recover(error)
                except Exception as recovery_error:
                    from .logging import error as log_error

                    log_error(
                        f"Recovery strategy failed: {recovery_error}",
                        original_error=str(error),
                        strategy=type(strategy).__name__,
                    )

        return None

    def add_strategy(self, strategy: ErrorRecoveryStrategy) -> None:
        """Add a custom recovery strategy."""
        self.strategies.append(strategy)


# Global error recovery manager
_recovery_manager = ErrorRecoveryManager()


def get_recovery_manager() -> ErrorRecoveryManager:
    """Get the global error recovery manager."""
    return _recovery_manager


def handle_error_with_recovery(error: RiveterError) -> Optional[Any]:
    """Handle an error with automatic recovery attempt."""
    recovery_result = _recovery_manager.attempt_recovery(error)
    if recovery_result is None:
        # No recovery possible, re-raise the error
        raise error
    return recovery_result
