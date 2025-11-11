"""Report and output management with dependency injection.

This module provides modernized report management functionality
with protocol-based interfaces and dependency injection support.
"""

import sys
from pathlib import Path
from typing import Any

from rich.console import Console

from ..models.core import ValidationResult
from .formatters import JSONFormatter, JUnitXMLFormatter, SARIFFormatter, TableFormatter
from .protocols import FormatterProtocol, OutputManagerProtocol, ReportManagerProtocol

console = Console()


class OutputManager:
    """Manages output operations with support for files and console."""

    def __init__(self, console_instance: Console | None = None) -> None:
        """Initialize output manager.

        Args:
            console_instance: Optional Rich console instance
        """
        self._console = console_instance or console

    def write_output(
        self,
        content: str,
        output_file: str | None = None,
        format_name: str = "text",
    ) -> None:
        """Write formatted content to output.

        Args:
            content: Content to write
            output_file: Optional output file path
            format_name: Format name for file extension
        """
        if output_file:
            output_path = Path(output_file)
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # Write to stdout
            print(content)

    def print_to_console(self, content: str, use_rich: bool = True) -> None:
        """Print content to console.

        Args:
            content: Content to print
            use_rich: Whether to use rich formatting
        """
        if use_rich and hasattr(self._console, "print"):
            self._console.print(content)
        else:
            print(content)


class ReportManager:
    """Manages validation result reporting with pluggable formatters.

    This class provides a modernized interface for generating and outputting
    validation reports while maintaining backward compatibility with existing
    behavior.
    """

    def __init__(
        self,
        output_manager: OutputManagerProtocol | None = None,
        formatters: dict[str, FormatterProtocol] | None = None,
    ) -> None:
        """Initialize report manager.

        Args:
            output_manager: Optional output manager instance
            formatters: Optional dictionary of formatters
        """
        self._output_manager = output_manager or OutputManager()
        self._formatters: dict[str, FormatterProtocol] = formatters or {}

        # Register default formatters if none provided
        if not self._formatters:
            self._register_default_formatters()

    def _register_default_formatters(self) -> None:
        """Register the default set of output formatters."""
        # Import here to avoid circular imports
        from ..reporter import console as reporter_console

        self._formatters = {
            "table": TableFormatter(reporter_console),
            "json": JSONFormatter(),
            "junit": JUnitXMLFormatter(),
            "sarif": SARIFFormatter(),
        }

    def report(
        self,
        result: ValidationResult,
        output_format: str = "table",
        output_file: str | None = None,
    ) -> int:
        """Generate and output a validation report.

        Args:
            result: Validation result to report
            output_format: Output format name
            output_file: Optional output file path

        Returns:
            Exit code (0 for success, non-zero for failures)
        """
        try:
            formatter = self.get_formatter(output_format.lower())
            formatted_output = formatter.format(result)

            if output_format.lower() == "table":
                # For table format, the formatter prints directly to console
                # formatted_output will be empty, so we don't need to do anything
                pass
            else:
                # For other formats, write to file or stdout
                self._output_manager.write_output(formatted_output, output_file, output_format)

            # Calculate exit code based on failures
            return 1 if result.summary.has_failures else 0

        except Exception as e:
            # Handle errors gracefully
            error_msg = f"Error generating report: {e}"
            self._output_manager.print_to_console(f"[red]{error_msg}[/red]", use_rich=True)
            return 1

    def get_available_formats(self) -> list[str]:
        """Get list of available output formats.

        Returns:
            List of format names
        """
        return list(self._formatters.keys())

    def register_formatter(self, name: str, formatter: FormatterProtocol) -> None:
        """Register a new output formatter.

        Args:
            name: Format name
            formatter: Formatter instance
        """
        self._formatters[name.lower()] = formatter

    def get_formatter(self, format_name: str) -> FormatterProtocol:
        """Get formatter by name.

        Args:
            format_name: Name of the format

        Returns:
            Formatter instance

        Raises:
            ValueError: If format is not supported
        """
        formatter = self._formatters.get(format_name.lower())
        if formatter is None:
            available = ", ".join(self.get_available_formats())
            raise ValueError(f"Unsupported output format: {format_name}. Available: {available}")
        return formatter


# Backward compatibility functions that maintain the original API
def report_results(
    results: list[Any],
    output_format: str = "table",
    output_file: str | None = None,
) -> int:
    """Report validation results using the legacy interface.

    This function maintains backward compatibility with the original
    report_results function while using the modernized components.

    Args:
        results: List of legacy ValidationResult objects
        output_format: Output format ('table', 'json', 'junit', 'sarif')
        output_file: Optional output file path

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    # Import here to avoid circular imports
    from ..scanner import ValidationResult as LegacyValidationResult

    # Convert legacy results to modern format if needed
    if not results:
        # Handle empty results case
        import time

        from ..models.core import ValidationResult, ValidationSummary

        summary = ValidationSummary(
            total_rules=0,
            total_resources=0,
            passed=0,
            failed=0,
            errors=0,
            warnings=0,
            info=0,
            start_time=time.time(),
            end_time=time.time(),
        )

        modern_result = ValidationResult(
            summary=summary, results=[], metadata={"legacy_conversion": True}
        )
    else:
        # Convert legacy ValidationResult objects to modern format
        modern_result = _convert_legacy_results(results)

    # Use modern report manager
    manager = ReportManager()
    return manager.report(modern_result, output_format, output_file)


def _convert_legacy_results(legacy_results: list[Any]) -> "ValidationResult":
    """Convert legacy ValidationResult objects to modern format.

    Args:
        legacy_results: List of legacy ValidationResult objects

    Returns:
        Modern ValidationResult object
    """
    import time

    from ..models.core import (
        RuleResult,
        Severity,
        TerraformResource,
        ValidationResult,
        ValidationSummary,
    )

    # Convert legacy results to modern RuleResult objects
    modern_results = []
    passed_count = 0
    failed_count = 0
    error_count = 0
    warning_count = 0
    info_count = 0

    for legacy_result in legacy_results:
        # Skip skipped results for failure counting
        is_skipped = legacy_result.message.startswith("SKIPPED:")

        # Create TerraformResource from legacy resource dict
        resource = TerraformResource(
            type=legacy_result.resource.get("resource_type", "unknown"),
            name=legacy_result.resource.get("id", "unknown"),
            attributes=legacy_result.resource,
        )

        # Create modern RuleResult
        rule_result = RuleResult(
            rule_id=legacy_result.rule.id,
            resource=resource,
            passed=legacy_result.passed,
            message=legacy_result.message,
            severity=legacy_result.severity,
            details={
                "execution_time": getattr(legacy_result, "execution_time", 0.0),
                "assertion_results": getattr(legacy_result, "assertion_results", []),
                "is_skipped": is_skipped,
            },
        )

        modern_results.append(rule_result)

        # Count results (excluding skipped for failure counts)
        if not is_skipped:
            if legacy_result.passed:
                passed_count += 1
            else:
                failed_count += 1

                # Count by severity
                if legacy_result.severity == Severity.ERROR:
                    error_count += 1
                elif legacy_result.severity == Severity.WARNING:
                    warning_count += 1
                elif legacy_result.severity == Severity.INFO:
                    info_count += 1

    # Create summary
    summary = ValidationSummary(
        total_rules=len(set(r.rule_id for r in modern_results)),
        total_resources=len(set(r.resource.id for r in modern_results)),
        passed=passed_count,
        failed=failed_count,
        errors=error_count,
        warnings=warning_count,
        info=info_count,
        start_time=time.time(),
        end_time=time.time(),
    )

    return ValidationResult(
        summary=summary, results=modern_results, metadata={"legacy_conversion": True}
    )
