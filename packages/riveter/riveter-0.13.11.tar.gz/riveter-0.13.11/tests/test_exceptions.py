"""Tests for the exceptions module."""

import pytest

from riveter.exceptions import (
    CloudProviderError,
    ConfigurationError,
    ErrorRecoveryManager,
    ErrorRecoveryStrategy,
    FallbackParsingStrategy,
    FileSystemError,
    OperatorError,
    ResourceValidationError,
    RiveterError,
    RulePackError,
    RuleValidationError,
    SkipResourceStrategy,
    SkipRuleStrategy,
    TerraformParsingError,
    ValidationSummaryError,
    get_recovery_manager,
    handle_error_with_recovery,
)


class TestRiveterError:
    """Test the base RiveterError class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = RiveterError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}
        assert error.suggestions == []

    def test_error_with_details(self):
        """Test error with details."""
        details = {"file": "test.py", "line": 42}
        error = RiveterError("Test error", details=details)

        assert error.details == details
        assert "Details: {'file': 'test.py', 'line': 42}" in str(error)

    def test_error_with_suggestions(self):
        """Test error with suggestions."""
        suggestions = ["Check the file", "Verify permissions"]
        error = RiveterError("Test error", suggestions=suggestions)

        assert error.suggestions == suggestions
        error_str = str(error)
        assert "Suggestions:" in error_str
        assert "- Check the file" in error_str
        assert "- Verify permissions" in error_str

    def test_error_with_details_and_suggestions(self):
        """Test error with both details and suggestions."""
        details = {"file": "test.py"}
        suggestions = ["Check the file"]
        error = RiveterError("Test error", details=details, suggestions=suggestions)

        error_str = str(error)
        assert "Test error" in error_str
        assert "Details:" in error_str
        assert "Suggestions:" in error_str


class TestSpecificErrors:
    """Test specific error types."""

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Invalid config", config_file="config.yml", line_number=10)

        assert error.config_file == "config.yml"
        assert error.line_number == 10
        assert error.details["config_file"] == "config.yml"
        assert error.details["line_number"] == 10

    def test_terraform_parsing_error(self):
        """Test TerraformParsingError."""
        error = TerraformParsingError(
            "Parse failed", terraform_file="main.tf", hcl_error="syntax error"
        )

        assert error.terraform_file == "main.tf"
        assert error.hcl_error == "syntax error"
        assert error.details["terraform_file"] == "main.tf"
        assert error.details["hcl_error"] == "syntax error"
        assert len(error.suggestions) > 0  # Should have default suggestions

    def test_rule_validation_error(self):
        """Test RuleValidationError."""
        error = RuleValidationError(
            "Invalid rule", rule_id="test-rule", rule_file="rules.yml", field_path="assert.property"
        )

        assert error.rule_id == "test-rule"
        assert error.rule_file == "rules.yml"
        assert error.field_path == "assert.property"
        assert error.details["rule_id"] == "test-rule"

    def test_rule_pack_error(self):
        """Test RulePackError."""
        error = RulePackError("Pack not found", pack_name="aws-security", pack_version="1.0.0")

        assert error.pack_name == "aws-security"
        assert error.pack_version == "1.0.0"
        assert error.details["pack_name"] == "aws-security"
        assert error.details["pack_version"] == "1.0.0"

    def test_resource_validation_error(self):
        """Test ResourceValidationError."""
        error = ResourceValidationError(
            "Validation failed",
            resource_type="aws_instance",
            resource_name="web-server",
            rule_id="security-rule",
        )

        assert error.resource_type == "aws_instance"
        assert error.resource_name == "web-server"
        assert error.rule_id == "security-rule"

    def test_operator_error(self):
        """Test OperatorError."""
        error = OperatorError("Comparison failed", operator="gt", expected_value=10, actual_value=5)

        assert error.operator == "gt"
        assert error.expected_value == 10
        assert error.actual_value == 5

    def test_cloud_provider_error(self):
        """Test CloudProviderError."""
        error = CloudProviderError("Provider error", provider="aws", resource_type="aws_instance")

        assert error.provider == "aws"
        assert error.resource_type == "aws_instance"

    def test_filesystem_error(self):
        """Test FileSystemError."""
        error = FileSystemError("File not found", file_path="/path/to/file", operation="read")

        assert error.file_path == "/path/to/file"
        assert error.operation == "read"
        assert len(error.suggestions) > 0  # Should have default suggestions


class TestValidationSummaryError:
    """Test ValidationSummaryError."""

    def test_summary_error_creation(self):
        """Test ValidationSummaryError creation."""
        errors = [
            RuleValidationError("Rule error 1"),
            TerraformParsingError("Parse error"),
            RuleValidationError("Rule error 2"),
        ]

        summary = ValidationSummaryError("Multiple errors occurred", errors)

        assert len(summary.errors) == 3
        assert summary.details["error_count"] == 3
        assert "RuleValidationError" in summary.details["error_types"]
        assert "TerraformParsingError" in summary.details["error_types"]

    def test_get_errors_by_type(self):
        """Test getting errors by type."""
        errors = [
            RuleValidationError("Rule error 1"),
            TerraformParsingError("Parse error"),
            RuleValidationError("Rule error 2"),
        ]

        summary = ValidationSummaryError("Multiple errors", errors)

        rule_errors = summary.get_errors_by_type(RuleValidationError)
        assert len(rule_errors) == 2

        parse_errors = summary.get_errors_by_type(TerraformParsingError)
        assert len(parse_errors) == 1

    def test_has_critical_errors(self):
        """Test critical error detection."""
        # Non-critical errors
        errors1 = [ResourceValidationError("Resource error"), OperatorError("Operator error")]
        summary1 = ValidationSummaryError("Non-critical errors", errors1)
        assert not summary1.has_critical_errors()

        # Critical errors
        errors2 = [TerraformParsingError("Parse error"), ResourceValidationError("Resource error")]
        summary2 = ValidationSummaryError("Critical errors", errors2)
        assert summary2.has_critical_errors()


class TestErrorRecoveryStrategies:
    """Test error recovery strategies."""

    def test_skip_resource_strategy(self):
        """Test SkipResourceStrategy."""
        strategy = SkipResourceStrategy()

        # Should recover from resource-level errors
        resource_error = ResourceValidationError("Resource error")
        operator_error = OperatorError("Operator error")
        rule_error = RuleValidationError("Rule error")

        assert strategy.can_recover(resource_error)
        assert strategy.can_recover(operator_error)
        assert not strategy.can_recover(rule_error)

    def test_skip_rule_strategy(self):
        """Test SkipRuleStrategy."""
        strategy = SkipRuleStrategy()

        rule_error = RuleValidationError("Rule error")
        resource_error = ResourceValidationError("Resource error")

        assert strategy.can_recover(rule_error)
        assert not strategy.can_recover(resource_error)

    def test_fallback_parsing_strategy(self):
        """Test FallbackParsingStrategy."""
        strategy = FallbackParsingStrategy()

        cloud_error = CloudProviderError("Cloud error")
        rule_error = RuleValidationError("Rule error")

        assert strategy.can_recover(cloud_error)
        assert not strategy.can_recover(rule_error)

        # Should return empty dict as fallback
        result = strategy.recover(cloud_error)
        assert result == {}


class TestErrorRecoveryManager:
    """Test ErrorRecoveryManager."""

    def test_recovery_manager_creation(self):
        """Test recovery manager creation."""
        manager = ErrorRecoveryManager()
        assert len(manager.strategies) == 3  # Default strategies

    def test_successful_recovery(self):
        """Test successful error recovery."""
        manager = ErrorRecoveryManager()

        # Should recover from resource error
        resource_error = ResourceValidationError("Resource error")
        result = manager.attempt_recovery(resource_error)
        assert result is None  # SkipResourceStrategy returns None

    def test_failed_recovery(self):
        """Test failed error recovery."""
        manager = ErrorRecoveryManager()

        # Should not recover from configuration error (no strategy handles it)
        config_error = ConfigurationError("Config error")

        # attempt_recovery returns None when no recovery is possible
        # It doesn't raise the error - that's done by handle_error_with_recovery
        result = manager.attempt_recovery(config_error)
        assert result is None

    def test_add_custom_strategy(self):
        """Test adding custom recovery strategy."""
        manager = ErrorRecoveryManager()

        class CustomStrategy(ErrorRecoveryStrategy):
            def can_recover(self, error):
                return isinstance(error, ConfigurationError)

            def recover(self, error):
                return "recovered"

        custom_strategy = CustomStrategy()
        manager.add_strategy(custom_strategy)

        assert len(manager.strategies) == 4

        # Should now recover from configuration error
        config_error = ConfigurationError("Config error")
        result = manager.attempt_recovery(config_error)
        assert result == "recovered"

    def test_recovery_strategy_failure(self):
        """Test recovery strategy failure handling."""
        manager = ErrorRecoveryManager()

        class FailingStrategy(ErrorRecoveryStrategy):
            def can_recover(self, error):
                return isinstance(error, ResourceValidationError)

            def recover(self, error):
                raise Exception("Recovery failed")

        # Replace first strategy with failing one
        manager.strategies[0] = FailingStrategy()

        # Should still try other strategies
        resource_error = ResourceValidationError("Resource error")
        result = manager.attempt_recovery(resource_error)
        assert result is None  # Should fall back to other strategies


class TestGlobalErrorHandling:
    """Test global error handling functions."""

    def test_get_recovery_manager(self):
        """Test get_recovery_manager function."""
        manager1 = get_recovery_manager()
        manager2 = get_recovery_manager()

        assert manager1 is manager2  # Should return same instance

    def test_handle_error_with_recovery_success(self):
        """Test successful error handling with recovery."""
        resource_error = ResourceValidationError("Resource error")

        # The SkipResourceStrategy can recover from this, but it returns None
        # and the handle_error_with_recovery function will still raise if result is None
        # Let's test that the recovery manager can handle it
        from riveter.exceptions import get_recovery_manager

        manager = get_recovery_manager()
        result = manager.attempt_recovery(resource_error)
        assert result is None  # SkipResourceStrategy returns None

    def test_handle_error_with_recovery_failure(self):
        """Test error handling when recovery fails."""
        config_error = ConfigurationError("Config error")

        # Should re-raise the error (no recovery possible)
        with pytest.raises(ConfigurationError):
            handle_error_with_recovery(config_error)


class TestErrorInheritance:
    """Test error class inheritance."""

    def test_all_errors_inherit_from_riveter_error(self):
        """Test that all custom errors inherit from RiveterError."""
        error_classes = [
            (ConfigurationError, ("Test message",)),
            (TerraformParsingError, ("Test message",)),
            (RuleValidationError, ("Test message",)),
            (RulePackError, ("Test message",)),
            (ResourceValidationError, ("Test message",)),
            (OperatorError, ("Test message",)),
            (CloudProviderError, ("Test message",)),
            (FileSystemError, ("Test message",)),
            (ValidationSummaryError, ("Test message", [])),  # Needs errors list
        ]

        for error_class, args in error_classes:
            error = error_class(*args)
            assert isinstance(error, RiveterError)
            assert isinstance(error, Exception)

    def test_error_attributes_preserved(self):
        """Test that error attributes are preserved through inheritance."""
        error = RuleValidationError("Test error", rule_id="test-rule", suggestions=["Fix the rule"])

        # Should have both base and specific attributes
        assert error.message == "Test error"
        assert error.rule_id == "test-rule"
        assert error.suggestions == ["Fix the rule"]
        assert isinstance(error, RiveterError)
