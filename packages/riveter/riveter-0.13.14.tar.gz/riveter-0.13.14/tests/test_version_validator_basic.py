"""Basic tests for version_validator module to improve coverage."""

import tempfile
import unittest
from pathlib import Path

from riveter.version_validator import ValidationSeverity, VersionValidator


class TestVersionValidatorBasic(unittest.TestCase):
    """Basic tests for version validator functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_temp_dir = Path(tempfile.mkdtemp(prefix="version_validator_test_"))

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if self.test_temp_dir.exists():
            shutil.rmtree(self.test_temp_dir)

    def test_validation_severity_enum(self):
        """Test ValidationSeverity enum values."""
        self.assertEqual(ValidationSeverity.INFO.value, "info")
        self.assertEqual(ValidationSeverity.WARNING.value, "warning")
        self.assertEqual(ValidationSeverity.ERROR.value, "error")

    def test_version_validator_initialization(self):
        """Test VersionValidator can be initialized."""
        validator = VersionValidator(self.test_temp_dir)
        self.assertIsInstance(validator, VersionValidator)
        self.assertEqual(validator.project_root, self.test_temp_dir)

    def test_version_validator_with_debug(self):
        """Test VersionValidator with debug mode."""
        validator = VersionValidator(self.test_temp_dir, debug=True)
        self.assertTrue(validator.debug)

    def test_semver_validation(self):
        """Test semantic version validation."""
        validator = VersionValidator(self.test_temp_dir)

        # Valid semantic versions
        self.assertTrue(validator._is_valid_semver("1.0.0"))
        self.assertTrue(validator._is_valid_semver("0.1.0"))
        self.assertTrue(validator._is_valid_semver("10.20.30"))

        # Invalid versions
        self.assertFalse(validator._is_valid_semver("1.0"))
        self.assertFalse(validator._is_valid_semver("1.0.0.0"))
        self.assertFalse(validator._is_valid_semver("invalid"))

    def test_validate_with_missing_pyproject(self):
        """Test validation with missing pyproject.toml."""
        validator = VersionValidator(self.test_temp_dir)

        # Should handle missing pyproject.toml gracefully
        try:
            report = validator.validate_all_components()
            # Should not crash, may have issues but should return a report
            self.assertIsNotNone(report)
        except Exception as e:
            # If it raises an exception, it should be informative
            self.assertIn("pyproject.toml", str(e).lower())


if __name__ == "__main__":
    unittest.main()
