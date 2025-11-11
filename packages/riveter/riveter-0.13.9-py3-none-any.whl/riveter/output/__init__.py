"""Output and reporting components for Riveter.

This package provides modernized output formatting and reporting
functionality with protocol-based interfaces and dependency injection.
"""

from .formatters import (
    JSONFormatter,
    JUnitXMLFormatter,
    OutputFormatter,
    SARIFFormatter,
    TableFormatter,
)
from .manager import OutputManager, ReportManager
from .protocols import FormatterProtocol, ReportManagerProtocol

__all__ = [
    "FormatterProtocol",
    "ReportManagerProtocol",
    "OutputFormatter",
    "OutputManager",
    "ReportManager",
    "TableFormatter",
    "JSONFormatter",
    "JUnitXMLFormatter",
    "SARIFFormatter",
]
