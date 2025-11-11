"""
Structured logging system for Riveter.

This module provides structured logging capabilities with configurable levels
and formats, supporting both human-readable and JSON output for log analysis.
"""

import json
import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogFormat(Enum):
    """Log format enumeration."""

    HUMAN = "human"
    JSON = "json"


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def __init__(self, format_type: LogFormat = LogFormat.HUMAN):
        super().__init__()
        self.format_type = format_type

    def format(self, record: logging.LogRecord) -> str:
        """Format log record based on configured format type."""
        if self.format_type == LogFormat.JSON:
            return self._format_json(record)
        else:
            return self._format_human(record)

    def _format_json(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)

    def _format_human(self, record: logging.LogRecord) -> str:
        """Format log record for human readability."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level_color = self._get_level_color(record.levelname)
        reset_color = "\033[0m"

        # Format: [TIMESTAMP] LEVEL - MODULE.FUNCTION:LINE - MESSAGE
        formatted = (
            f"[{timestamp}] {level_color}{record.levelname:<7}{reset_color} - "
            f"{record.module}.{record.funcName}:{record.lineno} - {record.getMessage()}"
        )

        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted

    def _get_level_color(self, level: str) -> str:
        """Get ANSI color code for log level."""
        colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        return colors.get(level, "")


class RiveterLogger:
    """Structured logger for Riveter application."""

    def __init__(self, name: str = "riveter") -> None:
        self.name = name
        self.logger = logging.getLogger(name)
        self._configured = False

    def configure(
        self,
        level: Union[LogLevel, str] = LogLevel.INFO,
        format_type: Union[LogFormat, str] = LogFormat.HUMAN,
        output_stream: Optional[Any] = None,
    ) -> None:
        """Configure the logger with specified settings."""
        if self._configured:
            return

        # Convert string values to enums if needed
        if isinstance(level, str):
            level = LogLevel(level.upper())
        if isinstance(format_type, str):
            format_type = LogFormat(format_type.lower())

        # Set log level
        log_level = getattr(logging, level.value)
        self.logger.setLevel(log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create handler
        handler = logging.StreamHandler(output_stream or sys.stderr)
        handler.setLevel(log_level)

        # Set formatter
        formatter = StructuredFormatter(format_type)
        handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

        self._configured = True

    def debug(self, message: str, **extra_fields: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, extra_fields)

    def info(self, message: str, **extra_fields: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, message, extra_fields)

    def warning(self, message: str, **extra_fields: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, extra_fields)

    def error(self, message: str, **extra_fields: Any) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, extra_fields)

    def exception(self, message: str, **extra_fields: Any) -> None:
        """Log error message with exception traceback."""
        self._log(logging.ERROR, message, extra_fields, exc_info=True)

    def _log(
        self, level: int, message: str, extra_fields: Dict[str, Any], exc_info: bool = False
    ) -> None:
        """Internal logging method."""
        if not self._configured:
            self.configure()

        # Create log record with extra fields
        import sys

        record = self.logger.makeRecord(
            self.logger.name, level, __file__, 0, message, (), sys.exc_info() if exc_info else None
        )

        if extra_fields:
            record.extra_fields = extra_fields

        self.logger.handle(record)


# Global logger instance
_global_logger: Optional[RiveterLogger] = None


def get_logger(name: str = "riveter") -> RiveterLogger:
    """Get or create a logger instance."""
    global _global_logger
    if _global_logger is None or _global_logger.name != name:
        _global_logger = RiveterLogger(name)
    return _global_logger


def configure_logging(
    level: Union[LogLevel, str] = LogLevel.INFO,
    format_type: Union[LogFormat, str] = LogFormat.HUMAN,
    output_stream: Optional[Any] = None,
) -> None:
    """Configure global logging settings."""
    logger = get_logger()
    logger.configure(level, format_type, output_stream)


# Convenience functions for direct logging
def debug(message: str, **extra_fields: Any) -> None:
    """Log debug message using global logger."""
    get_logger().debug(message, **extra_fields)


def info(message: str, **extra_fields: Any) -> None:
    """Log info message using global logger."""
    get_logger().info(message, **extra_fields)


def warning(message: str, **extra_fields: Any) -> None:
    """Log warning message using global logger."""
    get_logger().warning(message, **extra_fields)


def error(message: str, **extra_fields: Any) -> None:
    """Log error message using global logger."""
    get_logger().error(message, **extra_fields)


def exception(message: str, **extra_fields: Any) -> None:
    """Log error message with exception traceback using global logger."""
    get_logger().exception(message, **extra_fields)
