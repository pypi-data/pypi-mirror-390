"""Protocol interfaces for output and reporting components.

This module defines protocol interfaces for output formatters and
report managers, enabling dependency injection and extensibility.
"""

from typing import Any, Protocol, runtime_checkable

from ..models.core import ValidationResult


@runtime_checkable
class FormatterProtocol(Protocol):
    """Protocol for output formatters."""

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
class ReportManagerProtocol(Protocol):
    """Protocol for report managers."""

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
        ...

    def get_available_formats(self) -> list[str]:
        """Get list of available output formats.

        Returns:
            List of format names
        """
        ...

    def register_formatter(self, name: str, formatter: FormatterProtocol) -> None:
        """Register a new output formatter.

        Args:
            name: Format name
            formatter: Formatter instance
        """
        ...

    def get_formatter(self, format_name: str) -> FormatterProtocol:
        """Get formatter by name.

        Args:
            format_name: Name of the format

        Returns:
            Formatter instance

        Raises:
            ValueError: If format is not supported
        """
        ...


@runtime_checkable
class OutputManagerProtocol(Protocol):
    """Protocol for output managers."""

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
        ...

    def print_to_console(self, content: str, use_rich: bool = True) -> None:
        """Print content to console.

        Args:
            content: Content to print
            use_rich: Whether to use rich formatting
        """
        ...
