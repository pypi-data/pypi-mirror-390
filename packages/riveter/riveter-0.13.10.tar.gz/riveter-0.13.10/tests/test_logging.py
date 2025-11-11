"""Tests for the logging module."""

import json
import logging
import sys
from io import StringIO

from riveter.logging import (
    LogFormat,
    LogLevel,
    RiveterLogger,
    StructuredFormatter,
    configure_logging,
    get_logger,
)


class TestStructuredFormatter:
    """Test the StructuredFormatter class."""

    def test_human_format(self):
        """Test human-readable log formatting."""
        formatter = StructuredFormatter(LogFormat.HUMAN)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test_module"
        record.funcName = "test_function"

        formatted = formatter.format(record)

        assert "INFO" in formatted
        assert "test_module.test_function:42" in formatted
        assert "Test message" in formatted

    def test_json_format(self):
        """Test JSON log formatting."""
        formatter = StructuredFormatter(LogFormat.JSON)
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Test error",
            args=(),
            exc_info=None,
        )
        record.module = "test_module"
        record.funcName = "test_function"

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert log_data["level"] == "ERROR"
        assert log_data["message"] == "Test error"
        assert log_data["module"] == "test_module"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 42

    def test_json_format_with_extra_fields(self):
        """Test JSON formatting with extra fields."""
        formatter = StructuredFormatter(LogFormat.JSON)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test_module"
        record.funcName = "test_function"
        record.extra_fields = {"user_id": "123", "action": "login"}

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert log_data["user_id"] == "123"
        assert log_data["action"] == "login"

    def test_exception_formatting(self):
        """Test exception formatting in logs."""
        formatter = StructuredFormatter(LogFormat.HUMAN)

        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info(),
            )
            record.module = "test_module"
            record.funcName = "test_function"

            formatted = formatter.format(record)

            assert "Error occurred" in formatted
            assert "ValueError: Test exception" in formatted
            assert "Traceback" in formatted


class TestRiveterLogger:
    """Test the RiveterLogger class."""

    def test_logger_creation(self):
        """Test logger creation."""
        logger = RiveterLogger("test_logger")
        assert logger.name == "test_logger"
        assert not logger._configured

    def test_logger_configuration(self):
        """Test logger configuration."""
        output = StringIO()
        logger = RiveterLogger("test_logger")
        logger.configure(LogLevel.DEBUG, LogFormat.HUMAN, output)

        assert logger._configured
        assert len(logger.logger.handlers) == 1
        assert logger.logger.level == logging.DEBUG

    def test_logging_methods(self):
        """Test various logging methods."""
        output = StringIO()
        logger = RiveterLogger("test_logger")
        logger.configure(LogLevel.DEBUG, LogFormat.HUMAN, output)

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        log_output = output.getvalue()
        assert "Debug message" in log_output
        assert "Info message" in log_output
        assert "Warning message" in log_output
        assert "Error message" in log_output

    def test_logging_with_extra_fields(self):
        """Test logging with extra fields."""
        output = StringIO()
        logger = RiveterLogger("test_logger")
        logger.configure(LogLevel.INFO, LogFormat.JSON, output)

        logger.info("Test message", user_id="123", action="test")

        log_output = output.getvalue()
        log_data = json.loads(log_output.strip())

        assert log_data["message"] == "Test message"
        assert log_data["user_id"] == "123"
        assert log_data["action"] == "test"

    def test_exception_logging(self):
        """Test exception logging."""
        output = StringIO()
        logger = RiveterLogger("test_logger")
        logger.configure(LogLevel.INFO, LogFormat.HUMAN, output)

        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred")

        log_output = output.getvalue()
        assert "Exception occurred" in log_output
        assert "ValueError: Test exception" in log_output

    def test_log_level_filtering(self):
        """Test log level filtering."""
        output = StringIO()
        logger = RiveterLogger("test_logger")
        logger.configure(LogLevel.WARNING, LogFormat.HUMAN, output)

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        log_output = output.getvalue()
        assert "Debug message" not in log_output
        assert "Info message" not in log_output
        assert "Warning message" in log_output
        assert "Error message" in log_output


class TestGlobalLogging:
    """Test global logging functions."""

    def test_get_logger(self):
        """Test get_logger function."""
        logger1 = get_logger("test")
        logger2 = get_logger("test")
        logger3 = get_logger("other")

        assert logger1 is logger2  # Same name should return same instance
        assert logger1 is not logger3  # Different name should return different instance

    def test_configure_logging(self):
        """Test global logging configuration."""
        output = StringIO()
        configure_logging(LogLevel.INFO, LogFormat.JSON, output)

        from riveter.logging import info

        info("Test message", test_field="value")

        log_output = output.getvalue()
        log_data = json.loads(log_output.strip())

        assert log_data["message"] == "Test message"
        assert log_data["test_field"] == "value"

    def test_convenience_functions(self):
        """Test convenience logging functions."""
        # Reset global logger state
        from riveter.logging import _global_logger

        if _global_logger:
            _global_logger._configured = False

        output = StringIO()
        configure_logging(LogLevel.DEBUG, LogFormat.HUMAN, output)

        from riveter.logging import debug, error, info, warning

        debug("Debug message")
        info("Info message")
        warning("Warning message")
        error("Error message")

        log_output = output.getvalue()
        assert "Debug message" in log_output
        assert "Info message" in log_output
        assert "Warning message" in log_output
        assert "Error message" in log_output

    def test_enum_string_conversion(self):
        """Test that string values are converted to enums."""
        output = StringIO()
        logger = RiveterLogger("test")

        # Should accept string values and convert to enums
        logger.configure("DEBUG", "json", output)

        assert logger._configured
        assert logger.logger.level == logging.DEBUG


class TestLogFormatting:
    """Test log formatting edge cases."""

    def test_color_codes_in_human_format(self):
        """Test that color codes are applied in human format."""
        formatter = StructuredFormatter(LogFormat.HUMAN)

        # Test different log levels
        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ]

        for level, level_name in levels:
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="test.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None,
            )
            record.module = "test_module"
            record.funcName = "test_function"

            formatted = formatter.format(record)
            assert level_name in formatted

    def test_timestamp_formatting(self):
        """Test timestamp formatting in logs."""
        formatter = StructuredFormatter(LogFormat.JSON)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test_module"
        record.funcName = "test_function"

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Should have ISO format timestamp
        assert "timestamp" in log_data
        assert "T" in log_data["timestamp"]  # ISO format indicator

    def test_multiple_configurations(self):
        """Test that multiple configurations don't interfere."""
        logger = RiveterLogger("test")

        # First configuration
        output1 = StringIO()
        logger.configure(LogLevel.INFO, LogFormat.HUMAN, output1)
        logger.info("Message 1")

        # Second configuration should be ignored (already configured)
        output2 = StringIO()
        logger.configure(LogLevel.DEBUG, LogFormat.JSON, output2)
        logger.info("Message 2")

        # Both messages should go to first output
        assert "Message 1" in output1.getvalue()
        assert "Message 2" in output1.getvalue()
        assert output2.getvalue() == ""  # Second output should be empty
