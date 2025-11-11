"""Modern exception hierarchy for Riveter.

This module defines a comprehensive exception hierarchy with structured error
handling, context-aware error messages, and graceful degradation patterns.
"""

import traceback
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    CRITICAL = "critical"  # System cannot continue
    ERROR = "error"  # Operation failed but system can continue
    WARNING = "warning"  # Potential issue but operation succeeded
    INFO = "info"  # Informational message

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ErrorContext:
    """Context information for errors."""

    # Location information
    file_path: Path | None = None
    line_number: int | None = None
    column_number: int | None = None

    # Component information
    component: str | None = None
    operation: str | None = None

    # Resource information
    resource_type: str | None = None
    resource_name: str | None = None
    resource_id: str | None = None

    # Rule information
    rule_id: str | None = None
    rule_file: Path | None = None

    # Additional context
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "file_path": str(self.file_path) if self.file_path else None,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "component": self.component,
            "operation": self.operation,
            "resource_type": self.resource_type,
            "resource_name": self.resource_name,
            "resource_id": self.resource_id,
            "rule_id": self.rule_id,
            "rule_file": str(self.rule_file) if self.rule_file else None,
            "metadata": self.metadata,
        }

    def with_location(
        self, file_path: Path, line: int = None, column: int = None
    ) -> "ErrorContext":
        """Create new context with location information."""
        return ErrorContext(
            file_path=file_path,
            line_number=line,
            column_number=column,
            component=self.component,
            operation=self.operation,
            resource_type=self.resource_type,
            resource_name=self.resource_name,
            resource_id=self.resource_id,
            rule_id=self.rule_id,
            rule_file=self.rule_file,
            metadata=self.metadata,
        )

    def with_resource(self, resource_type: str, resource_name: str = None) -> "ErrorContext":
        """Create new context with resource information."""
        resource_id = f"{resource_type}.{resource_name}" if resource_name else resource_type
        return ErrorContext(
            file_path=self.file_path,
            line_number=self.line_number,
            column_number=self.column_number,
            component=self.component,
            operation=self.operation,
            resource_type=resource_type,
            resource_name=resource_name,
            resource_id=resource_id,
            rule_id=self.rule_id,
            rule_file=self.rule_file,
            metadata=self.metadata,
        )

    def with_rule(self, rule_id: str, rule_file: Path = None) -> "ErrorContext":
        """Create new context with rule information."""
        return ErrorContext(
            file_path=self.file_path,
            line_number=self.line_number,
            column_number=self.column_number,
            component=self.component,
            operation=self.operation,
            resource_type=self.resource_type,
            resource_name=self.resource_name,
            resource_id=self.resource_id,
            rule_id=rule_id,
            rule_file=rule_file,
            metadata=self.metadata,
        )


class RiveterError(Exception):
    """Base exception for all Riveter errors with enhanced context and recovery."""

    def __init__(
        self,
        message: str,
        *,
        context: ErrorContext | None = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        suggestions: list[str] | None = None,
        cause: Exception | None = None,
        recoverable: bool = True,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or ErrorContext()
        self.severity = severity
        self.suggestions = suggestions or []
        self.cause = cause
        self.recoverable = recoverable
        self.details = details or {}

        # Capture stack trace for debugging
        self.stack_trace = traceback.format_stack()

    @property
    def error_code(self) -> str:
        """Get error code based on exception type."""
        return f"RIV_{self.__class__.__name__.upper()}"

    @property
    def location_info(self) -> str:
        """Get formatted location information."""
        if self.context.file_path:
            location = str(self.context.file_path)
            if self.context.line_number:
                location += f":{self.context.line_number}"
                if self.context.column_number:
                    location += f":{self.context.column_number}"
            return location
        return "unknown location"

    def __str__(self) -> str:
        """Return formatted error message with context and suggestions."""
        lines = [f"[{self.severity.value.upper()}] {self.message}"]

        # Add location information
        if self.context.file_path or self.context.component:
            location_parts = []
            if self.context.component:
                location_parts.append(f"component: {self.context.component}")
            if self.context.file_path:
                location_parts.append(f"file: {self.location_info}")
            lines.append(f"Location: {', '.join(location_parts)}")

        # Add context information
        context_info = []
        if self.context.operation:
            context_info.append(f"operation: {self.context.operation}")
        if self.context.resource_id:
            context_info.append(f"resource: {self.context.resource_id}")
        if self.context.rule_id:
            context_info.append(f"rule: {self.context.rule_id}")

        if context_info:
            lines.append(f"Context: {', '.join(context_info)}")

        # Add details
        if self.details:
            lines.append(f"Details: {self.details}")

        # Add cause information
        if self.cause:
            lines.append(f"Caused by: {self.cause}")

        # Add suggestions
        if self.suggestions:
            lines.append("Suggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context.to_dict(),
            "suggestions": self.suggestions,
            "recoverable": self.recoverable,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
            "location": self.location_info,
        }

    def with_context(self, context: ErrorContext) -> "RiveterError":
        """Create new error with additional context."""
        return self.__class__(
            self.message,
            context=context,
            severity=self.severity,
            suggestions=self.suggestions,
            cause=self.cause,
            recoverable=self.recoverable,
            details=self.details,
        )

    def with_suggestion(self, suggestion: str) -> "RiveterError":
        """Create new error with additional suggestion."""
        new_suggestions = self.suggestions + [suggestion]
        return self.__class__(
            self.message,
            context=self.context,
            severity=self.severity,
            suggestions=new_suggestions,
            cause=self.cause,
            recoverable=self.recoverable,
            details=self.details,
        )


class ConfigurationError(RiveterError):
    """Errors related to configuration parsing and validation."""

    def __init__(
        self,
        message: str,
        *,
        config_file: str | Path | None = None,
        line_number: int | None = None,
        column_number: int | None = None,
        **kwargs: Any,
    ) -> None:
        # Build context
        context = kwargs.pop("context", ErrorContext())
        if config_file:
            context = context.with_location(
                Path(config_file) if isinstance(config_file, str) else config_file,
                line_number,
                column_number,
            )

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Check the configuration file syntax",
                "Verify all required fields are present",
                "Ensure the configuration follows the expected schema",
            ]

        super().__init__(
            message,
            context=context,
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            **kwargs,
        )


class TerraformParsingError(RiveterError):
    """Errors parsing Terraform files."""

    def __init__(
        self,
        message: str,
        *,
        terraform_file: str | Path | None = None,
        line_number: int | None = None,
        hcl_error: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Build context
        context = kwargs.pop("context", ErrorContext())
        if terraform_file:
            context = context.with_location(
                Path(terraform_file) if isinstance(terraform_file, str) else terraform_file,
                line_number,
            )

        # Add HCL error to details
        details = kwargs.pop("details", {})
        if hcl_error:
            details["hcl_error"] = hcl_error

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Check for syntax errors in the Terraform file",
                "Ensure all brackets and quotes are properly closed",
                "Verify that the file is valid HCL format",
                "Try running 'terraform validate' on the file",
            ]

        super().__init__(
            message,
            context=context,
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            details=details,
            **kwargs,
        )


class RuleValidationError(RiveterError):
    """Errors in rule definitions and validation."""

    def __init__(
        self,
        message: str,
        *,
        rule_id: str | None = None,
        rule_file: str | Path | None = None,
        field_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Build context
        context = kwargs.pop("context", ErrorContext())
        if rule_id:
            context = context.with_rule(
                rule_id, Path(rule_file) if isinstance(rule_file, str) else rule_file
            )

        # Add field path to details
        details = kwargs.pop("details", {})
        if field_path:
            details["field_path"] = field_path

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Check the rule definition syntax",
                "Verify all required rule fields are present",
                "Ensure operators and values are valid",
            ]

        super().__init__(
            message,
            context=context,
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            details=details,
            **kwargs,
        )


class RulePackError(RiveterError):
    """Errors in rule pack operations."""

    def __init__(
        self,
        message: str,
        *,
        pack_name: str | None = None,
        pack_version: str | None = None,
        pack_file: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        # Build context
        context = kwargs.pop("context", ErrorContext())
        if pack_file:
            context = context.with_location(
                Path(pack_file) if isinstance(pack_file, str) else pack_file
            )

        # Add pack info to details
        details = kwargs.pop("details", {})
        if pack_name:
            details["pack_name"] = pack_name
        if pack_version:
            details["pack_version"] = pack_version

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Check that the rule pack exists and is accessible",
                "Verify the rule pack format is correct",
                "Ensure the rule pack version is compatible",
            ]

        super().__init__(
            message,
            context=context,
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            details=details,
            **kwargs,
        )


class ResourceValidationError(RiveterError):
    """Errors during resource validation against rules."""

    def __init__(
        self,
        message: str,
        *,
        resource_type: str | None = None,
        resource_name: str | None = None,
        rule_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Build context
        context = kwargs.pop("context", ErrorContext())
        if resource_type:
            context = context.with_resource(resource_type, resource_name)
        if rule_id:
            context = context.with_rule(rule_id)

        super().__init__(
            message,
            context=context,
            severity=ErrorSeverity.WARNING,  # Usually not critical
            recoverable=True,
            **kwargs,
        )


class OperatorError(RiveterError):
    """Errors in operator evaluation and comparison logic."""

    def __init__(
        self,
        message: str,
        *,
        operator: str | None = None,
        expected_value: Any | None = None,
        actual_value: Any | None = None,
        **kwargs: Any,
    ) -> None:
        # Add operator details
        details = kwargs.pop("details", {})
        if operator:
            details["operator"] = operator
        if expected_value is not None:
            details["expected_value"] = expected_value
        if actual_value is not None:
            details["actual_value"] = actual_value

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Check that the operator is supported",
                "Verify the expected and actual value types match",
                "Ensure the comparison logic is correct",
            ]

        super().__init__(
            message,
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            details=details,
            **kwargs,
        )


class CloudProviderError(RiveterError):
    """Errors related to cloud provider parsing and handling."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        resource_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Build context
        context = kwargs.pop("context", ErrorContext())
        if resource_type:
            context = context.with_resource(resource_type)

        # Add provider details
        details = kwargs.pop("details", {})
        if provider:
            details["provider"] = provider

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Check that the cloud provider is supported",
                "Verify the resource type is valid for the provider",
                "Ensure provider-specific configuration is correct",
            ]

        super().__init__(
            message,
            context=context,
            severity=ErrorSeverity.WARNING,
            suggestions=suggestions,
            details=details,
            recoverable=True,  # Can often fall back to generic parsing
            **kwargs,
        )


class FileSystemError(RiveterError):
    """Errors related to file system operations."""

    def __init__(
        self,
        message: str,
        *,
        file_path: str | Path | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Build context
        context = kwargs.pop("context", ErrorContext())
        if file_path:
            context = context.with_location(
                Path(file_path) if isinstance(file_path, str) else file_path
            )

        # Add operation to context
        if operation:
            context = ErrorContext(
                file_path=context.file_path,
                line_number=context.line_number,
                column_number=context.column_number,
                component=context.component,
                operation=operation,
                resource_type=context.resource_type,
                resource_name=context.resource_name,
                resource_id=context.resource_id,
                rule_id=context.rule_id,
                rule_file=context.rule_file,
                metadata=context.metadata,
            )

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Check that the file or directory exists",
                "Verify that you have the necessary permissions",
                "Ensure the path is correct and accessible",
            ]

        super().__init__(
            message,
            context=context,
            severity=ErrorSeverity.ERROR,
            suggestions=suggestions,
            **kwargs,
        )


# Additional specialized exceptions


class PluginError(RiveterError):
    """Errors related to plugin loading and execution."""

    def __init__(
        self,
        message: str,
        *,
        plugin_name: str | None = None,
        plugin_version: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Add plugin details
        details = kwargs.pop("details", {})
        if plugin_name:
            details["plugin_name"] = plugin_name
        if plugin_version:
            details["plugin_version"] = plugin_version

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Check that the plugin is properly installed",
                "Verify plugin compatibility with current Riveter version",
                "Review plugin configuration and dependencies",
            ]

        super().__init__(
            message,
            severity=ErrorSeverity.WARNING,
            suggestions=suggestions,
            details=details,
            recoverable=True,
            **kwargs,
        )


class CacheError(RiveterError):
    """Errors related to caching operations."""

    def __init__(
        self,
        message: str,
        *,
        cache_key: str | None = None,
        cache_operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Add cache details
        details = kwargs.pop("details", {})
        if cache_key:
            details["cache_key"] = cache_key
        if cache_operation:
            details["cache_operation"] = cache_operation

        super().__init__(
            message,
            severity=ErrorSeverity.WARNING,
            details=details,
            recoverable=True,  # Cache errors are usually recoverable
            **kwargs,
        )


class PerformanceError(RiveterError):
    """Errors related to performance issues or timeouts."""

    def __init__(
        self,
        message: str,
        *,
        operation_timeout: float | None = None,
        memory_limit: int | None = None,
        **kwargs: Any,
    ) -> None:
        # Add performance details
        details = kwargs.pop("details", {})
        if operation_timeout:
            details["operation_timeout"] = operation_timeout
        if memory_limit:
            details["memory_limit"] = memory_limit

        # Add default suggestions
        suggestions = kwargs.pop("suggestions", [])
        if not suggestions:
            suggestions = [
                "Consider reducing the scope of the operation",
                "Check system resources and available memory",
                "Try running with performance mode enabled",
            ]

        super().__init__(
            message,
            severity=ErrorSeverity.WARNING,
            suggestions=suggestions,
            details=details,
            recoverable=True,
            **kwargs,
        )


class ValidationSummaryError(RiveterError):
    """Error that aggregates multiple validation failures."""

    def __init__(self, message: str, errors: list[RiveterError], **kwargs: Any) -> None:
        # Calculate severity based on contained errors
        max_severity = ErrorSeverity.INFO
        for error in errors:
            if error.severity == ErrorSeverity.CRITICAL:
                max_severity = ErrorSeverity.CRITICAL
                break
            if error.severity == ErrorSeverity.ERROR and max_severity != ErrorSeverity.CRITICAL:
                max_severity = ErrorSeverity.ERROR
            elif error.severity == ErrorSeverity.WARNING and max_severity == ErrorSeverity.INFO:
                max_severity = ErrorSeverity.WARNING

        # Build details
        details = kwargs.pop("details", {})
        details.update(
            {
                "error_count": len(errors),
                "error_types": [type(error).__name__ for error in errors],
                "critical_count": sum(1 for e in errors if e.severity == ErrorSeverity.CRITICAL),
                "error_count_by_severity": sum(
                    1 for e in errors if e.severity == ErrorSeverity.ERROR
                ),
                "warning_count": sum(1 for e in errors if e.severity == ErrorSeverity.WARNING),
            }
        )

        super().__init__(
            message,
            severity=max_severity,
            details=details,
            recoverable=any(error.recoverable for error in errors),
            **kwargs,
        )

        self.errors = errors

    def get_errors_by_type(self, error_type: type[RiveterError]) -> list[RiveterError]:
        """Get all errors of a specific type."""
        return [error for error in self.errors if isinstance(error, error_type)]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> list[RiveterError]:
        """Get all errors with a specific severity."""
        return [error for error in self.errors if error.severity == severity]

    def has_critical_errors(self) -> bool:
        """Check if any errors are considered critical."""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)

    def has_recoverable_errors(self) -> bool:
        """Check if any errors are recoverable."""
        return any(error.recoverable for error in self.errors)

    def get_error_summary(self) -> dict[str, int]:
        """Get summary of errors by severity."""
        summary = {severity.value: 0 for severity in ErrorSeverity}
        for error in self.errors:
            summary[error.severity.value] += 1
        return summary


# Modern error recovery system
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class ErrorRecoveryStrategy(Protocol):
    """Protocol for error recovery strategies."""

    def can_recover(self, error: RiveterError) -> bool:
        """Check if this strategy can recover from the given error."""
        ...

    def recover(self, error: RiveterError) -> Any:
        """Attempt to recover from the error."""
        ...

    @property
    def strategy_name(self) -> str:
        """Get the name of this recovery strategy."""
        ...


class BaseRecoveryStrategy(ABC):
    """Base implementation for error recovery strategies."""

    @property
    def strategy_name(self) -> str:
        """Get the name of this recovery strategy."""
        return self.__class__.__name__

    @abstractmethod
    def can_recover(self, error: RiveterError) -> bool:
        """Check if this strategy can recover from the given error."""

    @abstractmethod
    def recover(self, error: RiveterError) -> Any:
        """Attempt to recover from the error."""

    def _log_recovery_attempt(self, error: RiveterError, action: str) -> None:
        """Log recovery attempt."""
        try:
            from .logging import warning

            warning(
                f"Recovery strategy '{self.strategy_name}': {action}",
                error_type=type(error).__name__,
                error_message=error.message,
                **error.context.to_dict(),
            )
        except ImportError:
            # Fallback if logging module not available
            print(f"[WARNING] Recovery: {action} - {error.message}")


class SkipResourceStrategy(BaseRecoveryStrategy):
    """Strategy to skip problematic resources and continue processing."""

    def can_recover(self, error: RiveterError) -> bool:
        """Can recover from resource-level errors."""
        return isinstance(error, (ResourceValidationError, OperatorError)) and error.recoverable

    def recover(self, error: RiveterError) -> None:
        """Skip the problematic resource."""
        self._log_recovery_attempt(error, "Skipping problematic resource")


class SkipRuleStrategy(BaseRecoveryStrategy):
    """Strategy to skip problematic rules and continue with others."""

    def can_recover(self, error: RiveterError) -> bool:
        """Can recover from rule-level errors."""
        return isinstance(error, RuleValidationError) and error.recoverable

    def recover(self, error: RiveterError) -> None:
        """Skip the problematic rule."""
        self._log_recovery_attempt(error, "Skipping problematic rule")


class FallbackParsingStrategy(BaseRecoveryStrategy):
    """Strategy to use fallback parsing when cloud-specific parsing fails."""

    def can_recover(self, error: RiveterError) -> bool:
        """Can recover from cloud provider parsing errors."""
        return isinstance(error, CloudProviderError) and error.recoverable

    def recover(self, error: RiveterError) -> dict[str, Any]:
        """Use generic parsing as fallback."""
        self._log_recovery_attempt(error, "Using fallback parsing")
        return {}


class RetryStrategy(BaseRecoveryStrategy):
    """Strategy to retry operations with exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.retry_counts: dict[str, int] = {}

    def can_recover(self, error: RiveterError) -> bool:
        """Can recover from transient errors."""
        error_key = f"{type(error).__name__}:{error.message}"
        retry_count = self.retry_counts.get(error_key, 0)

        return (
            isinstance(error, (FileSystemError, CacheError, PerformanceError))
            and error.recoverable
            and retry_count < self.max_retries
        )

    def recover(self, error: RiveterError) -> None:
        """Retry the operation with exponential backoff."""
        import time

        error_key = f"{type(error).__name__}:{error.message}"
        retry_count = self.retry_counts.get(error_key, 0)

        # Calculate delay with exponential backoff
        delay = self.base_delay * (2**retry_count)

        self._log_recovery_attempt(
            error,
            f"Retrying operation (attempt {retry_count + 1}/{self.max_retries}) after {delay}s",
        )

        time.sleep(delay)
        self.retry_counts[error_key] = retry_count + 1


class GracefulDegradationStrategy(BaseRecoveryStrategy):
    """Strategy to continue with reduced functionality."""

    def can_recover(self, error: RiveterError) -> bool:
        """Can recover from non-critical errors."""
        return error.severity in (ErrorSeverity.WARNING, ErrorSeverity.INFO) and error.recoverable

    def recover(self, error: RiveterError) -> dict[str, Any]:
        """Continue with degraded functionality."""
        self._log_recovery_attempt(error, "Continuing with reduced functionality")
        return {"degraded_mode": True, "error": error.to_dict()}


class ErrorRecoveryManager:
    """Manages error recovery strategies with modern patterns."""

    def __init__(self) -> None:
        self.strategies: list[ErrorRecoveryStrategy] = [
            RetryStrategy(),
            SkipResourceStrategy(),
            SkipRuleStrategy(),
            FallbackParsingStrategy(),
            GracefulDegradationStrategy(),
        ]
        self.recovery_history: list[dict[str, Any]] = []

    def attempt_recovery(self, error: RiveterError) -> Any | None:
        """Attempt to recover from an error using available strategies."""
        recovery_attempt = {
            "error_type": type(error).__name__,
            "error_message": error.message,
            "strategies_tried": [],
            "successful_strategy": None,
            "recovery_result": None,
        }

        for strategy in self.strategies:
            strategy_name = strategy.strategy_name
            recovery_attempt["strategies_tried"].append(strategy_name)

            if strategy.can_recover(error):
                try:
                    result = strategy.recover(error)
                    recovery_attempt["successful_strategy"] = strategy_name
                    recovery_attempt["recovery_result"] = "success"
                    self.recovery_history.append(recovery_attempt)
                    return result

                except Exception as recovery_error:
                    recovery_attempt["recovery_result"] = f"failed: {recovery_error}"
                    try:
                        from .logging import error as log_error

                        log_error(
                            f"Recovery strategy '{strategy_name}' failed",
                            original_error=error.message,
                            recovery_error=str(recovery_error),
                            **error.context.to_dict(),
                        )
                    except ImportError:
                        print(
                            f"[ERROR] Recovery strategy '{strategy_name}' failed: {recovery_error}"
                        )

        recovery_attempt["recovery_result"] = "no_strategy_available"
        self.recovery_history.append(recovery_attempt)
        return None

    def add_strategy(self, strategy: ErrorRecoveryStrategy) -> None:
        """Add a custom recovery strategy."""
        self.strategies.insert(0, strategy)  # Add at beginning for priority

    def remove_strategy(self, strategy_type: type[ErrorRecoveryStrategy]) -> bool:
        """Remove a recovery strategy by type."""
        for i, strategy in enumerate(self.strategies):
            if isinstance(strategy, strategy_type):
                del self.strategies[i]
                return True
        return False

    def get_recovery_statistics(self) -> dict[str, Any]:
        """Get statistics about recovery attempts."""
        if not self.recovery_history:
            return {"total_attempts": 0}

        total_attempts = len(self.recovery_history)
        successful_recoveries = sum(
            1 for attempt in self.recovery_history if attempt["recovery_result"] == "success"
        )

        strategy_usage = {}
        for attempt in self.recovery_history:
            successful_strategy = attempt.get("successful_strategy")
            if successful_strategy:
                strategy_usage[successful_strategy] = strategy_usage.get(successful_strategy, 0) + 1

        return {
            "total_attempts": total_attempts,
            "successful_recoveries": successful_recoveries,
            "success_rate": (
                (successful_recoveries / total_attempts) * 100 if total_attempts > 0 else 0
            ),
            "strategy_usage": strategy_usage,
        }


# Global error recovery manager
_recovery_manager = ErrorRecoveryManager()


def get_recovery_manager() -> ErrorRecoveryManager:
    """Get the global error recovery manager."""
    return _recovery_manager


def handle_error_with_recovery(error: RiveterError) -> Any | None:
    """Handle an error with automatic recovery attempt."""
    recovery_result = _recovery_manager.attempt_recovery(error)
    if recovery_result is None:
        # No recovery possible, re-raise the error
        raise error
    return recovery_result


# Context managers for error handling
class ErrorHandler:
    """Context manager for enhanced error handling."""

    def __init__(
        self,
        component: str,
        operation: str = None,
        auto_recover: bool = True,
        suppress_errors: bool = False,
    ):
        self.component = component
        self.operation = operation
        self.auto_recover = auto_recover
        self.suppress_errors = suppress_errors
        self.errors: list[RiveterError] = []

    def __enter__(self) -> "ErrorHandler":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, RiveterError):
            error = exc_val

            # Enhance error context
            if not error.context.component:
                error = error.with_context(
                    error.context.with_component(self.component, self.operation)
                )

            self.errors.append(error)

            # Attempt recovery if enabled
            if self.auto_recover:
                try:
                    recovery_result = handle_error_with_recovery(error)
                    if recovery_result is not None:
                        return True  # Suppress the exception
                except Exception:
                    pass  # Recovery failed, let original exception propagate

            # Suppress errors if requested
            if self.suppress_errors:
                return True

        return False  # Don't suppress non-Riveter exceptions

    def add_error(self, error: RiveterError) -> None:
        """Manually add an error to this context."""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0

    def get_summary_error(self) -> ValidationSummaryError | None:
        """Get a summary error if multiple errors were collected."""
        if not self.errors:
            return None

        if len(self.errors) == 1:
            return self.errors[0]

        return ValidationSummaryError(f"Multiple errors occurred in {self.component}", self.errors)


# Utility functions for creating common errors
def create_config_error(
    message: str, config_file: str | Path | None = None, **kwargs
) -> ConfigurationError:
    """Create a configuration error with common defaults."""
    return ConfigurationError(message, config_file=config_file, **kwargs)


def create_terraform_error(
    message: str, terraform_file: str | Path | None = None, **kwargs
) -> TerraformParsingError:
    """Create a Terraform parsing error with common defaults."""
    return TerraformParsingError(message, terraform_file=terraform_file, **kwargs)


def create_rule_error(message: str, rule_id: str | None = None, **kwargs) -> RuleValidationError:
    """Create a rule validation error with common defaults."""
    return RuleValidationError(message, rule_id=rule_id, **kwargs)


def create_resource_error(
    message: str, resource_type: str | None = None, resource_name: str | None = None, **kwargs
) -> ResourceValidationError:
    """Create a resource validation error with common defaults."""
    return ResourceValidationError(
        message, resource_type=resource_type, resource_name=resource_name, **kwargs
    )


# Error aggregation utilities
def collect_errors(*errors: RiveterError) -> ValidationSummaryError:
    """Collect multiple errors into a summary error."""
    error_list = [error for error in errors if error is not None]

    if not error_list:
        raise ValueError("No errors provided to collect")

    if len(error_list) == 1:
        return error_list[0]

    return ValidationSummaryError(f"Multiple errors occurred ({len(error_list)} total)", error_list)


def filter_errors_by_severity(
    errors: list[RiveterError], min_severity: ErrorSeverity = ErrorSeverity.WARNING
) -> list[RiveterError]:
    """Filter errors by minimum severity level."""
    severity_order = {
        ErrorSeverity.INFO: 1,
        ErrorSeverity.WARNING: 2,
        ErrorSeverity.ERROR: 3,
        ErrorSeverity.CRITICAL: 4,
    }

    min_level = severity_order[min_severity]
    return [error for error in errors if severity_order[error.severity] >= min_level]


# Export commonly used exceptions and utilities
__all__ = [
    # Base classes
    "RiveterError",
    "ErrorSeverity",
    "ErrorContext",
    "ErrorHandler",
    # Specific exceptions
    "ConfigurationError",
    "TerraformParsingError",
    "RuleValidationError",
    "RulePackError",
    "ResourceValidationError",
    "OperatorError",
    "CloudProviderError",
    "FileSystemError",
    "PluginError",
    "CacheError",
    "PerformanceError",
    "ValidationSummaryError",
    # Recovery system
    "ErrorRecoveryStrategy",
    "ErrorRecoveryManager",
    "get_recovery_manager",
    "handle_error_with_recovery",
    # Utilities
    "create_config_error",
    "create_terraform_error",
    "create_rule_error",
    "create_resource_error",
    "collect_errors",
    "filter_errors_by_severity",
]
