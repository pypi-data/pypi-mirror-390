"""Output formatters for validation results with modern architecture.

This module provides backward compatibility wrappers around the modern
formatter system while maintaining the original API.
"""

from abc import ABC, abstractmethod
from typing import Any

from .output.formatters import JSONFormatter as ModernJSONFormatter
from .output.formatters import JUnitXMLFormatter as ModernJUnitXMLFormatter
from .output.formatters import OutputFormatter as ModernOutputFormatter
from .output.formatters import SARIFFormatter as ModernSARIFFormatter
from .output.manager import _convert_legacy_results
from .scanner import ValidationResult


class OutputFormatter(ABC):
    """Base class for output formatters.

    This class maintains backward compatibility with the original
    OutputFormatter interface while delegating to modern formatters.
    """

    @abstractmethod
    def format(self, results: list[ValidationResult]) -> str:
        """Format validation results into the desired output format.

        Args:
            results: List of validation results to format

        Returns:
            Formatted string representation of the results
        """

    def _calculate_summary(self, results: list[ValidationResult]) -> dict[str, int]:
        """Calculate summary statistics for results."""
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed and not r.message.startswith("SKIPPED:"))
        skipped = sum(1 for r in results if r.message.startswith("SKIPPED:"))
        total = len(results)
        active_checks = total - skipped

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "active_checks": active_checks,
        }


class JSONFormatter(OutputFormatter):
    """JSON formatter for programmatic consumption.

    This class provides backward compatibility by wrapping the modern
    JSON formatter.
    """

    def __init__(self) -> None:
        """Initialize JSON formatter."""
        self._modern_formatter = ModernJSONFormatter()

    def format(self, results: list[ValidationResult]) -> str:
        """Format results as JSON."""
        # Convert legacy results to modern format
        modern_result = _convert_legacy_results(results)

        # Use modern formatter
        return self._modern_formatter.format(modern_result)


class JUnitXMLFormatter(OutputFormatter):
    """JUnit XML formatter for CI/CD integration.

    This class provides backward compatibility by wrapping the modern
    JUnit XML formatter.
    """

    def __init__(self) -> None:
        """Initialize JUnit XML formatter."""
        self._modern_formatter = ModernJUnitXMLFormatter()

    def format(self, results: list[ValidationResult]) -> str:
        """Format results as JUnit XML."""
        # Convert legacy results to modern format
        modern_result = _convert_legacy_results(results)

        # Use modern formatter
        return self._modern_formatter.format(modern_result)


class SARIFFormatter(OutputFormatter):
    """SARIF formatter for security scanning tools.

    This class provides backward compatibility by wrapping the modern
    SARIF formatter.
    """

    def __init__(self) -> None:
        """Initialize SARIF formatter."""
        self._modern_formatter = ModernSARIFFormatter()

    def format(self, results: list[ValidationResult]) -> str:
        """Format results as SARIF (Static Analysis Results Interchange Format)."""
        # Convert legacy results to modern format
        modern_result = _convert_legacy_results(results)

        # Use modern formatter
        return self._modern_formatter.format(modern_result)
