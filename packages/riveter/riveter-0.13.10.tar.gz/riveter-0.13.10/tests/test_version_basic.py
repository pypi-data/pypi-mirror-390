"""Basic tests for version module to improve coverage."""

import tempfile
import unittest
from pathlib import Path

from riveter.version import get_version_from_pyproject


class TestVersionBasic(unittest.TestCase):
    """Basic tests for version functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_temp_dir = Path(tempfile.mkdtemp(prefix="version_test_"))

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if self.test_temp_dir.exists():
            shutil.rmtree(self.test_temp_dir)

    def test_get_version_from_pyproject_with_missing_file(self):
        """Test get_version_from_pyproject with missing pyproject.toml."""
        with self.assertRaises(FileNotFoundError) as context:
            get_version_from_pyproject(self.test_temp_dir)

        self.assertIn("pyproject.toml", str(context.exception))

    def test_get_version_from_pyproject_with_valid_file(self):
        """Test get_version_from_pyproject with valid pyproject.toml."""
        # Create a test pyproject.toml
        pyproject_content = """[project]
name = "test-package"
version = "1.2.3"
"""
        pyproject_path = self.test_temp_dir / "pyproject.toml"
        with open(pyproject_path, "w") as f:
            f.write(pyproject_content)

        version = get_version_from_pyproject(self.test_temp_dir)
        self.assertEqual(version, "1.2.3")

    def test_get_version_from_pyproject_with_invalid_toml(self):
        """Test get_version_from_pyproject with invalid TOML."""
        # Create an invalid pyproject.toml
        pyproject_path = self.test_temp_dir / "pyproject.toml"
        with open(pyproject_path, "w") as f:
            f.write("invalid toml content [[[")

        with self.assertRaises(ValueError) as context:
            get_version_from_pyproject(self.test_temp_dir)

        self.assertIn("Invalid TOML", str(context.exception))

    def test_get_version_from_pyproject_missing_version(self):
        """Test get_version_from_pyproject with missing version field."""
        # Create a pyproject.toml without version
        pyproject_content = """[project]
name = "test-package"
"""
        pyproject_path = self.test_temp_dir / "pyproject.toml"
        with open(pyproject_path, "w") as f:
            f.write(pyproject_content)

        with self.assertRaises(ValueError) as context:
            get_version_from_pyproject(self.test_temp_dir)

        self.assertIn("Version field not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()
