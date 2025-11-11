"""
Structured logging system for Riveter.

This module provides structured logging capabilities with configurable levels
and formats, supporting both human-readable and JSON output for log analysis.
Includes performance monitoring and security logging capabilities.
"""

import json
import logging
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Log format enumeration."""

    HUMAN = "human"
    JSON = "json"


class LogCategory(Enum):
    """Log category enumeration for structured logging."""

    GENERAL = "general"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CLI = "cli"
    VALIDATION = "validation"
    CONFIG = "config"
    RULES = "rules"


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def __init__(self, format_type: LogFormat = LogFormat.HUMAN):
        super().__init__()
        self.format_type = format_type

    def format(self, record: logging.LogRecord) -> str:
        """Format log record based on configured format type."""
        if self.format_type == LogFormat.JSON:
            return self._format_json(record)
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
            "process_id": record.process,
            "thread_id": record.thread,
        }

        # Add category if present
        if hasattr(record, "category"):
            log_data["category"] = record.category

        # Add performance metrics if present
        if hasattr(record, "duration"):
            log_data["duration_ms"] = record.duration
        if hasattr(record, "memory_usage"):
            log_data["memory_mb"] = record.memory_usage

        # Add security context if present
        if hasattr(record, "security_event"):
            log_data["security_event"] = record.security_event
        if hasattr(record, "user_context"):
            log_data["user_context"] = record.user_context

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, default=str)

    def _format_human(self, record: logging.LogRecord) -> str:
        """Format log record for human readability."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level_color = self._get_level_color(record.levelname)
        reset_color = "\033[0m"

        # Add category prefix if present
        category_prefix = ""
        if hasattr(record, "category"):
            category_prefix = f"[{record.category.upper()}] "

        # Format: [TIMESTAMP] [CATEGORY] LEVEL - MODULE.FUNCTION:LINE - MESSAGE
        formatted = (
            f"[{timestamp}] {category_prefix}{level_color}{record.levelname:<7}{reset_color} - "
            f"{record.module}.{record.funcName}:{record.lineno} - {record.getMessage()}"
        )

        # Add performance info if present
        if hasattr(record, "duration"):
            formatted += f" (took {record.duration:.3f}ms)"

        # Add memory info if present
        if hasattr(record, "memory_usage"):
            formatted += f" (memory: {record.memory_usage:.1f}MB)"

        # Add security event info if present
        if hasattr(record, "security_event"):
            formatted += f" [SECURITY: {record.security_event}]"

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
    """Structured logger for Riveter application with performance and security logging."""

    def __init__(self, name: str = "riveter") -> None:
        self.name = name
        self.logger = logging.getLogger(name)
        self._configured = False
        self._performance_timers: Dict[str, float] = {}
        self._security_context: Dict[str, Any] = {}

    def configure(
        self,
        level: LogLevel | str = LogLevel.INFO,
        format_type: LogFormat | str = LogFormat.HUMAN,
        output_stream: Any | None = None,
        log_file: Optional[Path] = None,
        enable_performance_logging: bool = True,
        enable_security_logging: bool = True,
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

        # Create console handler
        console_handler = logging.StreamHandler(output_stream or sys.stderr)
        console_handler.setLevel(log_level)
        console_formatter = StructuredFormatter(format_type)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Create file handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            # Always use JSON format for file logging
            file_formatter = StructuredFormatter(LogFormat.JSON)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

        # Store configuration flags
        self._performance_logging_enabled = enable_performance_logging
        self._security_logging_enabled = enable_security_logging

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

    def performance(
        self,
        message: str,
        duration: Optional[float] = None,
        memory_usage: Optional[float] = None,
        **extra_fields: Any,
    ) -> None:
        """Log performance-related message."""
        if not getattr(self, "_performance_logging_enabled", True):
            return

        extra_fields["category"] = LogCategory.PERFORMANCE.value
        if duration is not None:
            extra_fields["duration"] = duration
        if memory_usage is not None:
            extra_fields["memory_usage"] = memory_usage

        self._log(logging.INFO, message, extra_fields)

    def security(
        self,
        message: str,
        event_type: str,
        user_context: Optional[Dict[str, Any]] = None,
        **extra_fields: Any,
    ) -> None:
        """Log security-related message."""
        if not getattr(self, "_security_logging_enabled", True):
            return

        extra_fields["category"] = LogCategory.SECURITY.value
        extra_fields["security_event"] = event_type
        if user_context:
            extra_fields["user_context"] = user_context
        elif self._security_context:
            extra_fields["user_context"] = self._security_context

        self._log(logging.WARNING, message, extra_fields)

    def cli_command(
        self,
        message: str,
        command: str,
        args: Optional[Dict[str, Any]] = None,
        **extra_fields: Any,
    ) -> None:
        """Log CLI command execution."""
        extra_fields["category"] = LogCategory.CLI.value
        extra_fields["command"] = command
        if args:
            # Sanitize sensitive arguments
            sanitized_args = self._sanitize_args(args)
            extra_fields["args"] = sanitized_args

        self._log(logging.INFO, message, extra_fields)

    def start_timer(self, operation: str) -> None:
        """Start a performance timer for an operation."""
        self._performance_timers[operation] = time.time()

    def end_timer(self, operation: str, message: Optional[str] = None) -> float:
        """End a performance timer and log the duration."""
        if operation not in self._performance_timers:
            self.warning(f"Timer not started for operation: {operation}")
            return 0.0

        duration = (time.time() - self._performance_timers[operation]) * 1000  # Convert to ms
        del self._performance_timers[operation]

        if message is None:
            message = f"Operation '{operation}' completed"

        self.performance(message, duration=duration, operation=operation)
        return duration

    def set_security_context(self, context: Dict[str, Any]) -> None:
        """Set security context for subsequent security logs."""
        self._security_context = context

    def clear_security_context(self) -> None:
        """Clear security context."""
        self._security_context = {}

    def _sanitize_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize command arguments to remove sensitive information."""
        sanitized = {}
        sensitive_keys = {
            "password",
            "token",
            "key",
            "secret",
            "credential",
            "auth",
            "api_key",
            "access_token",
        }

        for key, value in args.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(type(value).__name__)

        return sanitized

    def _log(
        self, level: int, message: str, extra_fields: dict[str, Any], exc_info: bool = False
    ) -> None:
        """Internal logging method."""
        if not self._configured:
            self.configure()

        # Create log record with extra fields
        import sys

        record = self.logger.makeRecord(
            self.logger.name, level, __file__, 0, message, (), sys.exc_info() if exc_info else None
        )

        # Add extra fields as record attributes
        if extra_fields:
            for key, value in extra_fields.items():
                setattr(record, key, value)
            record.extra_fields = extra_fields

        self.logger.handle(record)


# Global logger instance
_global_logger: RiveterLogger | None = None


def get_logger(name: str = "riveter") -> RiveterLogger:
    """Get or create a logger instance."""
    global _global_logger
    if _global_logger is None or _global_logger.name != name:
        _global_logger = RiveterLogger(name)
    return _global_logger


def configure_logging(
    level: LogLevel | str = LogLevel.INFO,
    format_type: LogFormat | str = LogFormat.HUMAN,
    output_stream: Any | None = None,
    log_file: Optional[Path] = None,
    enable_performance_logging: bool = True,
    enable_security_logging: bool = True,
) -> None:
    """Configure global logging settings."""
    logger = get_logger()
    logger.configure(
        level,
        format_type,
        output_stream,
        log_file,
        enable_performance_logging,
        enable_security_logging,
    )


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


def performance(
    message: str,
    duration: Optional[float] = None,
    memory_usage: Optional[float] = None,
    **extra_fields: Any,
) -> None:
    """Log performance message using global logger."""
    get_logger().performance(message, duration, memory_usage, **extra_fields)


def security(
    message: str,
    event_type: str,
    user_context: Optional[Dict[str, Any]] = None,
    **extra_fields: Any,
) -> None:
    """Log security message using global logger."""
    get_logger().security(message, event_type, user_context, **extra_fields)


def cli_command(
    message: str,
    command: str,
    args: Optional[Dict[str, Any]] = None,
    **extra_fields: Any,
) -> None:
    """Log CLI command using global logger."""
    get_logger().cli_command(message, command, args, **extra_fields)


def start_timer(operation: str) -> None:
    """Start performance timer using global logger."""
    get_logger().start_timer(operation)


def end_timer(operation: str, message: Optional[str] = None) -> float:
    """End performance timer using global logger."""
    return get_logger().end_timer(operation, message)


def set_security_context(context: Dict[str, Any]) -> None:
    """Set security context using global logger."""
    get_logger().set_security_context(context)


def clear_security_context() -> None:
    """Clear security context using global logger."""
    get_logger().clear_security_context()
