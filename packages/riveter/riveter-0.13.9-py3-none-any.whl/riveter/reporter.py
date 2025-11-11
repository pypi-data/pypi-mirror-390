"""Results reporting with modern architecture and backward compatibility.

This module provides the main reporting interface while delegating to
the modernized output components for actual formatting and display.
"""

from typing import Any

from rich.console import Console

from .output.manager import report_results as modern_report_results
from .scanner import ValidationResult

# Maintain backward compatibility for tests that patch this
console = Console()


def report_results(results: list[ValidationResult], output_format: str = "table") -> int:
    """Report validation results and return exit code.

    This function maintains backward compatibility with the original interface
    while using the modernized reporting components internally.

    Args:
        results: List of validation results to report
        output_format: Output format ('table', 'json', 'junit', 'sarif')

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    # Handle empty results case with original behavior for backward compatibility
    if not results and output_format.lower() == "table":
        console.print("[green]All rules passed![/green]")
        return 0

    # Delegate to modern report manager for non-empty results
    return modern_report_results(results, output_format)


# Legacy support functions for backward compatibility
def _get_formatter(output_format: str) -> Any:
    """Get the appropriate formatter for the specified output format.

    This function is maintained for backward compatibility and returns
    the legacy formatter types that tests expect.
    """
    from .formatters import JSONFormatter, JUnitXMLFormatter, SARIFFormatter

    formatters = {
        "json": JSONFormatter(),
        "junit": JUnitXMLFormatter(),
        "sarif": SARIFFormatter(),
    }

    formatter = formatters.get(output_format.lower())
    if formatter is None:
        raise ValueError(f"Unsupported output format: {output_format}")

    return formatter


def _report_results_table(results: list[ValidationResult]) -> int:
    """Report validation results using the original table format.

    This function is maintained for backward compatibility but delegates
    to the modern table formatter.
    """
    return modern_report_results(results, "table")
