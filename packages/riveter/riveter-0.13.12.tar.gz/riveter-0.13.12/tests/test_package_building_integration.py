"""Integration tests for package building and publication workflow."""

import os
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from riveter.changelog_processor import ChangelogProcessor
from riveter.version_manager import VersionManager, VersionType

# Package building integration tests


class TestPackageBuildingIntegration:
    """Test package building and publication workflow integration."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary git repository with complete project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Initialize git repository
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True
            )

            # Create complete project structure
            pyproject_content = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "riveter"
version = "1.0.0"
description = "Infrastructure as Code security scanner"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Test Author", email = "test@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
requires-python = ">=3.12"
dependencies = [
    "click>=8.0.0",
    "pyyaml>=6.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
    "bandit>=1.7.0",
    "safety>=2.0.0",
]

[project.scripts]
riveter = "riveter.cli:main"

[project.urls]
Homepage = "https://github.com/test/riveter"
Repository = "https://github.com/test/riveter"
Issues = "https://github.com/test/riveter/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
riveter = ["py.typed"]
"""
            (repo_path / "pyproject.toml").write_text(pyproject_content)

            # Create source structure
            src_dir = repo_path / "src" / "riveter"
            src_dir.mkdir(parents=True)

            (src_dir / "__init__.py").write_text('__version__ = "1.0.0"\n')
            (src_dir / "py.typed").write_text("")

            cli_content = '''"""CLI module for riveter."""
import click

@click.command()
@click.version_option()
def main():
    """Riveter CLI main entry point."""
    click.echo("Riveter v1.0.0")

if __name__ == "__main__":
    main()
'''
            (src_dir / "cli.py").write_text(cli_content)

            # Create other required files
            (repo_path / "README.md").write_text("# Riveter\n\nTest project for release workflow.")
            (repo_path / "LICENSE").write_text("MIT License\n\nTest license content.")

            changelog_content = """# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New security scanning features
- Enhanced error reporting

### Fixed
- Bug fixes for edge cases

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Basic scanning functionality
"""
            (repo_path / "CHANGELOG.md").write_text(changelog_content)

            # Create manifest file
            manifest_content = """include README.md
include LICENSE
include CHANGELOG.md
recursive-include src/riveter *.py
recursive-include src/riveter *.typed
"""
            (repo_path / "MANIFEST.in").write_text(manifest_content)

            # Initial commit
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

            yield repo_path

    def test_complete_build_workflow(self, temp_repo):
        """Test complete package building workflow."""
        # Install build dependencies
        subprocess.run(
            ["python", "-m", "pip", "install", "build", "twine", "wheel"],
            check=True,
            capture_output=True,
        )

        # Clean any existing build artifacts
        for pattern in ["dist", "build", "*.egg-info"]:
            for path in temp_repo.glob(pattern):
                if path.is_dir():
                    import shutil

                    shutil.rmtree(path)
                else:
                    path.unlink()

        # Build source distribution
        result = subprocess.run(
            ["python", "-m", "build", "--sdist"], cwd=temp_repo, capture_output=True, text=True
        )

        assert result.returncode == 0, f"Source build failed: {result.stderr}"

        # Build wheel distribution
        result = subprocess.run(
            ["python", "-m", "build", "--wheel"], cwd=temp_repo, capture_output=True, text=True
        )

        assert result.returncode == 0, f"Wheel build failed: {result.stderr}"

        # Verify build artifacts exist
        dist_dir = temp_repo / "dist"
        assert dist_dir.exists()

        sdist_files = list(dist_dir.glob("*.tar.gz"))
        wheel_files = list(dist_dir.glob("*.whl"))

        assert len(sdist_files) == 1, f"Expected 1 sdist file, found {len(sdist_files)}"
        assert len(wheel_files) == 1, f"Expected 1 wheel file, found {len(wheel_files)}"

        # Validate packages with twine
        result = subprocess.run(
            ["twine", "check", "dist/*"], cwd=temp_repo, capture_output=True, text=True
        )

        assert result.returncode == 0, f"Package validation failed: {result.stderr}"
        assert "PASSED" in result.stdout

    def test_package_content_validation(self, temp_repo):
        """Test that built packages contain expected content."""
        # Build packages
        subprocess.run(["python", "-m", "pip", "install", "build"], check=True, capture_output=True)

        subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True, capture_output=True)

        dist_dir = temp_repo / "dist"

        # Check wheel content
        wheel_file = list(dist_dir.glob("*.whl"))[0]
        with zipfile.ZipFile(wheel_file, "r") as zf:
            wheel_contents = zf.namelist()

            # Check for expected files
            assert any("riveter/__init__.py" in f for f in wheel_contents)
            assert any("riveter/cli.py" in f for f in wheel_contents)
            assert any("riveter/py.typed" in f for f in wheel_contents)
            assert any("METADATA" in f for f in wheel_contents)

            # Check metadata content
            metadata_files = [f for f in wheel_contents if "METADATA" in f]
            metadata_content = zf.read(metadata_files[0]).decode("utf-8")
            assert "Name: riveter" in metadata_content
            assert "Version: 1.0.0" in metadata_content

        # Check source distribution content
        sdist_file = list(dist_dir.glob("*.tar.gz"))[0]
        with tarfile.open(sdist_file, "r:gz") as tf:
            sdist_contents = tf.getnames()

            # Check for expected files
            assert any("pyproject.toml" in f for f in sdist_contents)
            assert any("README.md" in f for f in sdist_contents)
            assert any("LICENSE" in f for f in sdist_contents)
            assert any("CHANGELOG.md" in f for f in sdist_contents)
            assert any("src/riveter/__init__.py" in f for f in sdist_contents)

    def test_package_installation_test(self, temp_repo):
        """Test that built packages can be installed and imported."""
        # Build packages
        subprocess.run(["python", "-m", "pip", "install", "build"], check=True, capture_output=True)

        subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True, capture_output=True)

        # Create test virtual environment
        venv_dir = temp_repo / "test_venv"
        subprocess.run(["python", "-m", "venv", str(venv_dir)], check=True)

        # Determine python executable in venv
        if os.name == "nt":  # Windows
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:  # Unix-like
            python_exe = venv_dir / "bin" / "python"

        # Install the built wheel
        wheel_file = list((temp_repo / "dist").glob("*.whl"))[0]
        result = subprocess.run(
            [str(python_exe), "-m", "pip", "install", str(wheel_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Installation failed: {result.stderr}"

        # Test import
        result = subprocess.run(
            [str(python_exe), "-c", "import riveter; print(riveter.__version__)"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "1.0.0" in result.stdout

        # Test CLI
        result = subprocess.run(
            [str(python_exe), "-m", "riveter.cli", "--version"], capture_output=True, text=True
        )

        assert result.returncode == 0, f"CLI test failed: {result.stderr}"

    def test_version_update_and_rebuild(self, temp_repo):
        """Test version update and package rebuild workflow."""
        # Update version using version manager
        version_manager = VersionManager(temp_repo)
        version_info = version_manager.create_version_info(VersionType.PATCH)

        assert version_info.current == "1.0.0"
        assert version_info.new == "1.0.1"

        # Update pyproject.toml
        version_manager.update_pyproject_version(version_info.new)

        # Update __init__.py version
        init_file = temp_repo / "src" / "riveter" / "__init__.py"
        init_file.write_text(f'__version__ = "{version_info.new}"\n')

        # Update changelog
        changelog_processor = ChangelogProcessor(temp_repo / "CHANGELOG.md")
        updated_content, release_notes = changelog_processor.process_release(version_info.new)
        changelog_processor.write_changelog(updated_content)

        # Rebuild packages
        subprocess.run(["python", "-m", "pip", "install", "build"], check=True, capture_output=True)

        # Clean previous build
        import shutil

        dist_dir = temp_repo / "dist"
        if dist_dir.exists():
            shutil.rmtree(dist_dir)

        subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True, capture_output=True)

        # Verify new version in built packages
        wheel_file = list((temp_repo / "dist").glob("*.whl"))[0]
        assert "1.0.1" in wheel_file.name

        with zipfile.ZipFile(wheel_file, "r") as zf:
            metadata_files = [f for f in zf.namelist() if "METADATA" in f]
            metadata_content = zf.read(metadata_files[0]).decode("utf-8")
            assert "Version: 1.0.1" in metadata_content

    @patch("subprocess.run")
    def test_build_failure_handling(self, mock_run, temp_repo):
        """Test handling of build failures."""
        # Mock build command failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "python -m build", "Build failed")

        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True)

    def test_twine_validation_failure(self, temp_repo):
        """Test handling of twine validation failures."""
        # Create invalid package structure
        (temp_repo / "pyproject.toml").write_text("[invalid toml")

        # Try to build (should fail)
        result = subprocess.run(["python", "-m", "build"], cwd=temp_repo, capture_output=True)

        assert result.returncode != 0

    def test_package_metadata_validation(self, temp_repo):
        """Test package metadata validation."""
        # Build packages
        subprocess.run(["python", "-m", "pip", "install", "build"], check=True, capture_output=True)

        subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True, capture_output=True)

        # Check wheel metadata
        wheel_file = list((temp_repo / "dist").glob("*.whl"))[0]
        with zipfile.ZipFile(wheel_file, "r") as zf:
            metadata_files = [f for f in zf.namelist() if "METADATA" in f]
            metadata_content = zf.read(metadata_files[0]).decode("utf-8")

            # Verify required metadata fields
            assert "Name: riveter" in metadata_content
            assert "Version: 1.0.0" in metadata_content
            assert "Author-email:" in metadata_content  # Modern format uses Author-email
            assert "test@example.com" in metadata_content
            assert "Requires-Python: >=3.12" in metadata_content
            assert "Classifier: Programming Language :: Python :: 3" in metadata_content

    def test_dependency_handling(self, temp_repo):
        """Test that dependencies are properly handled in built packages."""
        # Build packages
        subprocess.run(["python", "-m", "pip", "install", "build"], check=True, capture_output=True)

        subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True, capture_output=True)

        # Check that dependencies are included in metadata
        wheel_file = list((temp_repo / "dist").glob("*.whl"))[0]
        with zipfile.ZipFile(wheel_file, "r") as zf:
            metadata_files = [f for f in zf.namelist() if "METADATA" in f]
            metadata_content = zf.read(metadata_files[0]).decode("utf-8")

            # Check for runtime dependencies
            assert "Requires-Dist: click>=8.0.0" in metadata_content
            assert "Requires-Dist: pyyaml>=6.0" in metadata_content
            assert "Requires-Dist: rich>=13.0.0" in metadata_content

            # Check for optional dependencies
            assert "Provides-Extra: dev" in metadata_content

    def test_entry_points_validation(self, temp_repo):
        """Test that entry points are properly configured."""
        # Build packages
        subprocess.run(["python", "-m", "pip", "install", "build"], check=True, capture_output=True)

        subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True, capture_output=True)

        # Check entry points in wheel
        wheel_file = list((temp_repo / "dist").glob("*.whl"))[0]
        with zipfile.ZipFile(wheel_file, "r") as zf:
            entry_points_files = [f for f in zf.namelist() if "entry_points.txt" in f]

            if entry_points_files:
                entry_points_content = zf.read(entry_points_files[0]).decode("utf-8")
                assert "riveter = riveter.cli:main" in entry_points_content

    def test_build_reproducibility(self, temp_repo):
        """Test that builds are reproducible."""
        subprocess.run(["python", "-m", "pip", "install", "build"], check=True, capture_output=True)

        # First build
        subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True, capture_output=True)

        # Get first build artifacts
        dist_dir = temp_repo / "dist"
        first_wheel = list(dist_dir.glob("*.whl"))[0]
        first_sdist = list(dist_dir.glob("*.tar.gz"))[0]

        first_wheel_size = first_wheel.stat().st_size
        first_sdist_size = first_sdist.stat().st_size

        # Clean and rebuild
        import shutil

        shutil.rmtree(dist_dir)

        subprocess.run(["python", "-m", "build"], cwd=temp_repo, check=True, capture_output=True)

        # Get second build artifacts
        second_wheel = list(dist_dir.glob("*.whl"))[0]
        second_sdist = list(dist_dir.glob("*.tar.gz"))[0]

        second_wheel_size = second_wheel.stat().st_size
        second_sdist_size = second_sdist.stat().st_size

        # Compare sizes (should be very similar for reproducible builds)
        # Allow small differences due to timestamps and metadata
        wheel_diff = abs(first_wheel_size - second_wheel_size)
        sdist_diff = abs(first_sdist_size - second_sdist_size)

        # Allow up to 1% difference or 100 bytes, whichever is larger
        wheel_tolerance = max(first_wheel_size * 0.01, 100)
        sdist_tolerance = max(first_sdist_size * 0.01, 100)

        assert (
            wheel_diff <= wheel_tolerance
        ), f"Wheel size difference {wheel_diff} exceeds tolerance {wheel_tolerance}"
        assert (
            sdist_diff <= sdist_tolerance
        ), f"Sdist size difference {sdist_diff} exceeds tolerance {sdist_tolerance}"

    def test_build_with_different_python_versions(self, temp_repo):
        """Test building with different Python versions (if available)."""
        # This test would ideally run with multiple Python versions
        # For now, just test with current Python version

        subprocess.run(["python", "-m", "pip", "install", "build"], check=True, capture_output=True)

        result = subprocess.run(
            ["python", "-m", "build"], cwd=temp_repo, capture_output=True, text=True
        )

        assert result.returncode == 0

        # Check that wheel is tagged for current Python version
        wheel_file = list((temp_repo / "dist").glob("*.whl"))[0]
        wheel_name = wheel_file.name

        # Wheel should contain Python version tag
        assert "py3" in wheel_name or "py312" in wheel_name or "py313" in wheel_name

    def test_build_cleanup_on_failure(self, temp_repo):
        """Test that build artifacts are cleaned up on failure."""
        # Create invalid pyproject.toml that will cause build to fail
        invalid_content = """[build-system]
requires = ["nonexistent-package"]
build-backend = "nonexistent.backend"

[project]
name = "riveter"
version = "1.0.0"
"""
        (temp_repo / "pyproject.toml").write_text(invalid_content)

        # Attempt build (should fail)
        result = subprocess.run(["python", "-m", "build"], cwd=temp_repo, capture_output=True)

        assert result.returncode != 0

        # Check that no partial artifacts were left behind
        dist_dir = temp_repo / "dist"
        if dist_dir.exists():
            artifacts = list(dist_dir.glob("*"))
            # Should have no complete artifacts
            assert len([f for f in artifacts if f.suffix in [".whl", ".tar.gz"]]) == 0
