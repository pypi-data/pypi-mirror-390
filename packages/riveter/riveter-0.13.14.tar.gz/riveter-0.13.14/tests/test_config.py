"""Tests for configuration management."""

import json
import os
import tempfile

import pytest
import yaml

from riveter.config import ConfigManager, RiveterConfig, get_environment_from_context


class TestRiveterConfig:
    """Test RiveterConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RiveterConfig()

        assert config.rule_dirs == ["rules"]
        assert config.rule_packs == []
        assert config.include_rules == []
        assert config.exclude_rules == []
        assert config.min_severity == "info"
        assert config.output_format == "table"
        assert config.output_file is None
        assert config.parallel is False
        assert config.max_workers is None
        assert config.cache_dir is None
        assert config.log_level == "INFO"
        assert config.log_format == "human"
        assert config.debug is False
        assert config.environment_overrides == {}

    def test_merge_with_simple_fields(self):
        """Test merging configurations with simple field overrides."""
        base_config = RiveterConfig(output_format="table", min_severity="info", debug=False)

        override_config = RiveterConfig(output_format="json", min_severity="warning", debug=True)

        merged = base_config.merge_with(override_config)

        assert merged.output_format == "json"
        assert merged.min_severity == "warning"
        assert merged.debug is True

    def test_merge_with_lists(self):
        """Test merging configurations with list fields."""
        base_config = RiveterConfig(
            rule_dirs=["rules", "custom"], rule_packs=["aws-security"], include_rules=["*security*"]
        )

        override_config = RiveterConfig(
            rule_dirs=["additional"],
            rule_packs=["cis-aws"],
            include_rules=["*encryption*"],
            exclude_rules=["*test*"],
        )

        merged = base_config.merge_with(override_config)

        assert merged.rule_dirs == ["rules", "custom", "additional"]
        assert merged.rule_packs == ["aws-security", "cis-aws"]
        assert merged.include_rules == ["*security*", "*encryption*"]
        assert merged.exclude_rules == ["*test*"]

    def test_merge_with_environment_overrides(self):
        """Test merging environment overrides."""
        base_config = RiveterConfig(
            environment_overrides={"dev": {"debug": True}, "prod": {"min_severity": "error"}}
        )

        override_config = RiveterConfig(
            environment_overrides={
                "prod": {"parallel": True},
                "staging": {"min_severity": "warning"},
            }
        )

        merged = base_config.merge_with(override_config)

        expected_overrides = {
            "dev": {"debug": True},
            "prod": {"parallel": True},  # Override replaces
            "staging": {"min_severity": "warning"},
        }

        assert merged.environment_overrides == expected_overrides

    def test_apply_environment_overrides(self):
        """Test applying environment-specific overrides."""
        config = RiveterConfig(
            min_severity="info",
            debug=False,
            environment_overrides={
                "production": {"min_severity": "error", "parallel": True},
                "development": {"debug": True, "min_severity": "info"},
            },
        )

        # Apply production overrides
        prod_config = config.apply_environment_overrides("production")
        assert prod_config.min_severity == "error"
        assert prod_config.parallel is True
        assert prod_config.debug is False  # Not overridden

        # Apply development overrides
        dev_config = config.apply_environment_overrides("development")
        assert dev_config.debug is True
        assert dev_config.min_severity == "info"
        assert dev_config.parallel is False  # Not overridden

        # No environment specified
        no_env_config = config.apply_environment_overrides(None)
        assert no_env_config.min_severity == "info"
        assert no_env_config.debug is False
        assert no_env_config.parallel is False

    def test_to_dict_and_from_dict(self):
        """Test conversion to/from dictionary."""
        original_config = RiveterConfig(
            rule_dirs=["rules", "custom"],
            rule_packs=["aws-security"],
            min_severity="warning",
            output_format="json",
            debug=True,
            environment_overrides={"prod": {"min_severity": "error"}},
        )

        config_dict = original_config.to_dict()
        restored_config = RiveterConfig.from_dict(config_dict)

        assert restored_config.rule_dirs == original_config.rule_dirs
        assert restored_config.rule_packs == original_config.rule_packs
        assert restored_config.min_severity == original_config.min_severity
        assert restored_config.output_format == original_config.output_format
        assert restored_config.debug == original_config.debug
        assert restored_config.environment_overrides == original_config.environment_overrides

    def test_from_dict_filters_unknown_keys(self):
        """Test that from_dict filters out unknown keys."""
        data = {
            "rule_dirs": ["rules"],
            "min_severity": "warning",
            "unknown_field": "should_be_ignored",
            "another_unknown": 123,
        }

        config = RiveterConfig.from_dict(data)

        assert config.rule_dirs == ["rules"]
        assert config.min_severity == "warning"
        assert not hasattr(config, "unknown_field")
        assert not hasattr(config, "another_unknown")


class TestConfigManager:
    """Test ConfigManager class."""

    def test_load_config_defaults_only(self):
        """Test loading configuration with defaults only."""
        config_manager = ConfigManager()
        config = config_manager.load_config()

        # Should return default configuration
        assert config.rule_dirs == ["rules"]
        assert config.min_severity == "info"
        assert config.output_format == "table"

    def test_load_config_with_yaml_file(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "rule_dirs": ["custom-rules", "shared-rules"],
            "rule_packs": ["aws-security", "cis-aws"],
            "min_severity": "warning",
            "output_format": "json",
            "parallel": True,
            "max_workers": 4,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name

        try:
            config_manager = ConfigManager()
            config = config_manager.load_config(config_file=config_file)

            # Lists are merged (file extends defaults), so we expect both
            assert "custom-rules" in config.rule_dirs
            assert "shared-rules" in config.rule_dirs
            assert "rules" in config.rule_dirs  # Default is preserved
            assert config.rule_packs == ["aws-security", "cis-aws"]
            assert config.min_severity == "warning"
            assert config.output_format == "json"
            assert config.parallel is True
            assert config.max_workers == 4
        finally:
            os.unlink(config_file)

    def test_load_config_with_json_file(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "rule_dirs": ["json-rules"],
            "min_severity": "error",
            "debug": True,
            "environment_overrides": {"production": {"parallel": True, "max_workers": 8}},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            config_manager = ConfigManager()
            config = config_manager.load_config(config_file=config_file)

            # Lists are merged (file extends defaults)
            assert "json-rules" in config.rule_dirs
            assert "rules" in config.rule_dirs  # Default is preserved
            assert config.min_severity == "error"
            assert config.debug is True
            assert config.environment_overrides == config_data["environment_overrides"]
        finally:
            os.unlink(config_file)

    def test_load_config_with_cli_overrides(self):
        """Test loading configuration with CLI overrides."""
        config_data = {"min_severity": "info", "output_format": "table", "debug": False}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name

        try:
            cli_overrides = {
                "min_severity": "error",
                "debug": True,
                "include_rules": ["*security*"],
            }

            config_manager = ConfigManager()
            config = config_manager.load_config(
                config_file=config_file, cli_overrides=cli_overrides
            )

            # CLI overrides should take precedence
            assert config.min_severity == "error"
            assert config.debug is True
            assert config.include_rules == ["*security*"]
            # File config should still apply for non-overridden values
            assert config.output_format == "table"
        finally:
            os.unlink(config_file)

    def test_load_config_with_environment_overrides(self):
        """Test loading configuration with environment overrides."""
        config_data = {
            "min_severity": "info",
            "parallel": False,
            "environment_overrides": {
                "production": {"min_severity": "error", "parallel": True, "max_workers": 8}
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name

        try:
            config_manager = ConfigManager()
            config = config_manager.load_config(config_file=config_file, environment="production")

            # Environment overrides should be applied
            assert config.min_severity == "error"
            assert config.parallel is True
            assert config.max_workers == 8
        finally:
            os.unlink(config_file)

    def test_load_config_hierarchy(self):
        """Test configuration hierarchy: CLI > config file > defaults."""
        config_data = {
            "min_severity": "warning",
            "output_format": "json",
            "debug": False,
            "rule_dirs": ["file-rules"],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name

        try:
            cli_overrides = {
                "min_severity": "error",  # Override file
                "debug": True,  # Override file
                "include_rules": ["*security*"],  # Not in file, override default
            }

            config_manager = ConfigManager()
            config = config_manager.load_config(
                config_file=config_file, cli_overrides=cli_overrides
            )

            # CLI overrides
            assert config.min_severity == "error"
            assert config.debug is True
            assert config.include_rules == ["*security*"]

            # File config (not overridden by CLI)
            assert config.output_format == "json"
            # Lists are merged (file extends defaults)
            assert "file-rules" in config.rule_dirs
            assert "rules" in config.rule_dirs  # Default is preserved

            # Defaults (not overridden by file or CLI)
            assert config.rule_packs == []
        finally:
            os.unlink(config_file)

    def test_load_config_auto_discovery(self):
        """Test automatic configuration file discovery."""
        config_data = {"min_severity": "warning", "debug": True}

        # Create a config file with a default name
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "riveter.yml")
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                config_manager = ConfigManager()
                config = config_manager.load_config()  # No explicit config file

                assert config.min_severity == "warning"
                assert config.debug is True
            finally:
                os.chdir(original_cwd)

    def test_load_config_file_not_found(self):
        """Test error handling when config file doesn't exist."""
        config_manager = ConfigManager()

        with pytest.raises(FileNotFoundError):
            config_manager.load_config(config_file="nonexistent.yml")

    def test_load_config_invalid_yaml(self):
        """Test error handling for invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_file = f.name

        try:
            config_manager = ConfigManager()
            with pytest.raises(ValueError, match="Invalid configuration file format"):
                config_manager.load_config(config_file=config_file)
        finally:
            os.unlink(config_file)

    def test_load_config_invalid_json(self):
        """Test error handling for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json content}')
            config_file = f.name

        try:
            config_manager = ConfigManager()
            with pytest.raises(ValueError, match="Invalid configuration file format"):
                config_manager.load_config(config_file=config_file)
        finally:
            os.unlink(config_file)

    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        config = RiveterConfig(
            min_severity="warning",
            output_format="json",
            log_level="INFO",
            log_format="human",
            max_workers=4,
        )

        config_manager = ConfigManager()
        errors = config_manager.validate_config(config)

        assert errors == []

    def test_validate_config_invalid_severity(self):
        """Test validation with invalid severity."""
        config = RiveterConfig(min_severity="invalid")

        config_manager = ConfigManager()
        errors = config_manager.validate_config(config)

        assert len(errors) == 1
        assert "Invalid min_severity" in errors[0]

    def test_validate_config_invalid_output_format(self):
        """Test validation with invalid output format."""
        config = RiveterConfig(output_format="invalid")

        config_manager = ConfigManager()
        errors = config_manager.validate_config(config)

        assert len(errors) == 1
        assert "Invalid output_format" in errors[0]

    def test_validate_config_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = RiveterConfig(log_level="INVALID")

        config_manager = ConfigManager()
        errors = config_manager.validate_config(config)

        assert len(errors) == 1
        assert "Invalid log_level" in errors[0]

    def test_validate_config_invalid_max_workers(self):
        """Test validation with invalid max_workers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = RiveterConfig(rule_dirs=[temp_dir], max_workers=0)  # Use existing directory

            config_manager = ConfigManager()
            errors = config_manager.validate_config(config)

            assert len(errors) == 1
            assert "max_workers must be greater than 0" in errors[0]

    def test_validate_config_multiple_errors(self):
        """Test validation with multiple errors."""
        config = RiveterConfig(
            min_severity="invalid",
            output_format="invalid",
            max_workers=-1,
        )

        config_manager = ConfigManager()
        errors = config_manager.validate_config(config)

        assert len(errors) == 3
        assert any("Invalid min_severity" in error for error in errors)
        assert any("Invalid output_format" in error for error in errors)
        assert any("max_workers must be greater than 0" in error for error in errors)

    def test_create_sample_config_yaml(self):
        """Test creating sample YAML configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            config_file = f.name

        try:
            config_manager = ConfigManager()
            config_manager.create_sample_config(config_file)

            # Verify file was created and contains expected content
            assert os.path.exists(config_file)

            with open(config_file, "r") as f:
                content = yaml.safe_load(f)

            assert "rule_dirs" in content
            assert "rule_packs" in content
            assert "min_severity" in content
            assert "environment_overrides" in content
            assert isinstance(content["environment_overrides"], dict)
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_create_sample_config_json(self):
        """Test creating sample JSON configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_file = f.name

        try:
            config_manager = ConfigManager()
            config_manager.create_sample_config(config_file)

            # Verify file was created and contains expected content
            assert os.path.exists(config_file)

            with open(config_file, "r") as f:
                content = json.load(f)

            assert "rule_dirs" in content
            assert "rule_packs" in content
            assert "min_severity" in content
            assert "environment_overrides" in content
            assert isinstance(content["environment_overrides"], dict)
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)


class TestEnvironmentDetection:
    """Test environment detection functionality."""

    def test_get_environment_from_context_with_environment_tag(self):
        """Test environment detection from Environment tag."""
        resources = [
            {
                "id": "web_server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "production", "Name": "web-server"},
            }
        ]

        environment = get_environment_from_context(resources)
        assert environment == "production"

    def test_get_environment_from_context_with_env_tag(self):
        """Test environment detection from env tag."""
        resources = [
            {
                "id": "database",
                "resource_type": "aws_rds_instance",
                "tags": {"env": "staging", "Name": "database"},
            }
        ]

        environment = get_environment_from_context(resources)
        assert environment == "staging"

    def test_get_environment_from_context_with_resource_name(self):
        """Test environment detection from resource name."""
        resources = [
            {
                "id": "prod_web_server",
                "name": "prod-web-server-01",
                "resource_type": "aws_instance",
                "tags": {"Name": "prod-web-server-01"},
            }
        ]

        environment = get_environment_from_context(resources)
        assert environment == "prod"

    def test_get_environment_from_context_multiple_resources(self):
        """Test environment detection with multiple resources."""
        resources = [
            {"id": "web_server", "resource_type": "aws_instance", "tags": {"Name": "web-server"}},
            {
                "id": "database",
                "resource_type": "aws_rds_instance",
                "tags": {"Environment": "development", "Name": "database"},
            },
        ]

        environment = get_environment_from_context(resources)
        assert environment == "development"

    def test_get_environment_from_context_no_environment(self):
        """Test environment detection when no environment indicators are found."""
        resources = [
            {
                "id": "web_server",
                "resource_type": "aws_instance",
                "tags": {"Name": "web-server", "Owner": "team-a"},
            }
        ]

        environment = get_environment_from_context(resources)
        assert environment is None

    def test_get_environment_from_context_empty_resources(self):
        """Test environment detection with empty resources list."""
        environment = get_environment_from_context([])
        assert environment is None

    def test_get_environment_from_context_case_insensitive(self):
        """Test environment detection is case insensitive."""
        resources = [
            {
                "id": "web_server",
                "resource_type": "aws_instance",
                "tags": {"ENVIRONMENT": "PRODUCTION", "Name": "web-server"},
            }
        ]

        environment = get_environment_from_context(resources)
        assert environment == "production"
