"""Results reporting."""

from typing import List

from rich.console import Console
from rich.table import Table

from .formatters import JSONFormatter, JUnitXMLFormatter, OutputFormatter, SARIFFormatter
from .scanner import ValidationResult

console = Console()


def report_results(results: List[ValidationResult], output_format: str = "table") -> int:
    """Report validation results and return exit code.

    Args:
        results: List of validation results to report
        output_format: Output format ('table', 'json', 'junit', 'sarif')

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    # Handle different output formats
    if output_format.lower() != "table":
        formatter = _get_formatter(output_format)
        formatted_output = formatter.format(results)
        print(formatted_output)

        # Calculate exit code
        failed = sum(1 for r in results if not r.passed and not r.message.startswith("SKIPPED:"))
        return 1 if failed > 0 else 0

    # Default table format (preserve existing behavior)
    return _report_results_table(results)


def _get_formatter(output_format: str) -> OutputFormatter:
    """Get the appropriate formatter for the specified output format."""
    formatters = {
        "json": JSONFormatter(),
        "junit": JUnitXMLFormatter(),
        "sarif": SARIFFormatter(),
    }

    formatter = formatters.get(output_format.lower())
    if formatter is None:
        raise ValueError(f"Unsupported output format: {output_format}")

    return formatter


def _report_results_table(results: List[ValidationResult]) -> int:
    """Report validation results using the original table format."""
    if not results:
        console.print("[green]All rules passed![/green]")
        return 0

    table = Table(title="Rule Validation Results")
    table.add_column("Rule ID", style="cyan")
    table.add_column("Resource Type", style="blue")
    table.add_column("Resource ID", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Message", style="white")

    skipped_count = 0
    for result in results:
        # Check if this is a skipped rule message
        is_skipped = result.message.startswith("SKIPPED:")

        if is_skipped:
            status_style = "yellow"
            message_style = "yellow"
            status_text = "⚠️ SKIPPED"
            skipped_count += 1
        else:
            status_style = "green" if result.passed else "red"
            message_style = "green" if result.passed else "red"
            status_text = "✅ PASSED" if result.passed else "❌ FAILED"

        table.add_row(
            result.rule.id,
            result.resource.get("resource_type", ""),
            result.resource.get("id", ""),
            f"[{status_style}]{status_text}[/{status_style}]",
            f"[{message_style}]{result.message}[/{message_style}]",
        )

    # Print table and summary
    console.print(table)

    # Calculate statistics
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed and not r.message.startswith("SKIPPED:"))
    total = len(results)
    active_checks = total - skipped_count

    # Print summary with skipped rules information
    summary_msg = (
        f"\nSummary: [green]{passed}[/green]/[white]{active_checks}[/white] rules passed validation"
    )
    console.print(summary_msg)

    if failed > 0:
        console.print(f"[red]{failed}[/red] rules failed validation")

    if skipped_count > 0:
        skipped_msg = (
            f"[yellow]{skipped_count}[/yellow] rules were skipped (no matching resources found):"
        )
        console.print(skipped_msg)

        # Create a list of skipped rules
        skipped_rules = [r for r in results if r.message.startswith("SKIPPED:")]

        # Print a table with the skipped rules
        skipped_table = Table(title="Skipped Rules", box=None)
        skipped_table.add_column("Rule ID", style="cyan")
        skipped_table.add_column("Resource Type", style="blue")
        skipped_table.add_column("Description", style="white")

        for rule_result in skipped_rules:
            # Safely access rule attributes with fallbacks
            rule_id = getattr(rule_result.rule, "id", "Unknown")
            resource_type = rule_result.resource.get("resource_type", "Unknown")
            description = getattr(rule_result.rule, "description", "No description available")

            skipped_table.add_row(rule_id, resource_type, description)

        console.print(skipped_table)

    # Return exit code based on failed checks (not counting skipped ones)
    return 1 if failed > 0 else 0
