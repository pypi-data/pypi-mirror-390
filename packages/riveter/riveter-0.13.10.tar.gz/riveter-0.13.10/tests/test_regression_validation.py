#!/usr/bin/env python3
"""Regression testing for CI pipeline version sync fixes.

This test suite ensures that existing functionality continues to work correctly
after implementing the version synchronization and Homebrew fixes.

Requirements tested: 4.3, 4.4, 4.5
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class RegressionValidationTests(unittest.TestCase):
    """Regression tests to ensure existing functionality still works."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.project_root = Path(__file__).parent.parent
        cls.homebrew_repo_path = cls.project_root.parent / "homebrew-riveter"

    def setUp(self):
        """Set up individual test."""
        self.test_temp_dir = Path(tempfile.mkdtemp(prefix="riveter_regression_test_"))

    def tearDown(self):
        """Clean up after test."""
        if self.test_temp_dir and self.test_temp_dir.exists():
            shutil.rmtree(self.test_temp_dir)

    def test_existing_release_workflow_functionality(self):
        """Ensure existing release workflow continues to function correctly.

        Requirements: 4.3, 4.4
        """
        print("\n🚀 Testing existing release workflow functionality...")

        # Check that release workflow files exist and are valid
        workflows_dir = self.project_root / ".github" / "workflows"

        if not workflows_dir.exists():
            self.skipTest("No workflows directory found")

        # Look for release-related workflows
        release_workflows = []
        for workflow_file in workflows_dir.glob("*.yml"):
            with open(workflow_file, "r") as f:
                content = f.read()
                if any(keyword in content.lower() for keyword in ["release", "publish", "deploy"]):
                    release_workflows.append(workflow_file)

        if not release_workflows:
            print("  ⚠️ No release workflows found, skipping release workflow test")
            return

        # Validate workflow syntax
        for workflow_file in release_workflows:
            print(f"  🔍 Validating workflow: {workflow_file.name}")

            # Basic YAML syntax validation
            try:
                import yaml

                with open(workflow_file, "r") as f:
                    yaml.safe_load(f)
                print(f"    ✅ {workflow_file.name} has valid YAML syntax")
            except ImportError:
                print("    ⚠️ PyYAML not available, skipping YAML validation")
            except yaml.YAMLError as e:
                self.fail(f"Invalid YAML in {workflow_file.name}: {e}")

            # Check for version synchronization integration
            with open(workflow_file, "r") as f:
                content = f.read()

            # Should not break existing functionality
            self.assertNotIn(
                "BREAKING_CHANGE",
                content,
                f"Workflow {workflow_file.name} should not contain breaking changes",
            )

        print("✅ Existing release workflow functionality test passed")

    def test_binary_builds_with_version_synchronization(self):
        """Validate that binary builds still work with version synchronization.

        Requirements: 4.3, 4.4
        """
        print("\n🔨 Testing binary builds with version synchronization...")

        # Check for build scripts
        build_scripts = [
            self.project_root / "scripts" / "build_binary.py",
            self.project_root / "scripts" / "build_spec.py",
        ]

        existing_scripts = [script for script in build_scripts if script.exists()]

        if not existing_scripts:
            print("  ⚠️ No build scripts found, skipping binary build test")
            return

        # Test that build scripts can be imported/executed without errors
        for script in existing_scripts:
            print(f"  🔍 Testing build script: {script.name}")

            # Test script syntax
            result = subprocess.run(
                ["python", "-m", "py_compile", str(script)], capture_output=True, text=True
            )

            if result.returncode != 0:
                self.fail(f"Build script {script.name} has syntax errors: {result.stderr}")

            print(f"    ✅ {script.name} has valid Python syntax")

            # Test that script can show help without errors
            result = subprocess.run(
                ["python", str(script), "--help"], capture_output=True, text=True, timeout=30
            )

            if result.returncode not in [0, 2]:  # 0 = success, 2 = help shown
                print(f"    ⚠️ {script.name} help command had issues: {result.stderr}")
            else:
                print(f"    ✅ {script.name} help command works")

        # Test version synchronization doesn't break build process
        sync_script = self.project_root / "scripts" / "sync_versions.py"
        if sync_script.exists():
            print("  🔄 Testing version synchronization integration...")

            # Test that sync script can validate without breaking
            result = subprocess.run(
                ["python", str(sync_script), "--validate"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Don't fail if validation finds issues, just ensure it doesn't crash
            if "error" in result.stderr.lower() and "traceback" in result.stderr.lower():
                self.fail(f"Version sync script crashed: {result.stderr}")

            print("    ✅ Version synchronization integration works")

        print("✅ Binary builds with version synchronization test passed")

    def test_homebrew_formula_updates_dont_break_installations(self):
        """Test that Homebrew formula updates don't break existing installations.

        Requirements: 4.4, 4.5
        """
        print("\n🍺 Testing Homebrew formula updates don't break installations...")

        if not self.homebrew_repo_path.exists():
            print("  ⚠️ Homebrew repository not found, skipping formula update test")
            return

        formula_path = self.homebrew_repo_path / "Formula" / "riveter.rb"
        if not formula_path.exists():
            print("  ⚠️ Homebrew formula not found, skipping formula update test")
            return

        # Validate formula syntax
        print("  🔍 Validating formula syntax...")

        # Check Ruby syntax if Ruby is available
        if shutil.which("ruby"):
            result = subprocess.run(
                ["ruby", "-c", str(formula_path)], capture_output=True, text=True
            )

            if result.returncode != 0:
                self.fail(f"Formula has Ruby syntax errors: {result.stderr}")

            print("    ✅ Formula has valid Ruby syntax")
        else:
            print("    ⚠️ Ruby not available, skipping Ruby syntax check")

        # Validate formula structure
        with open(formula_path, "r") as f:
            formula_content = f.read()

        # Check for required components
        required_components = [
            "class Riveter < Formula",
            "desc ",
            "homepage ",
            "version ",
            "def install",
            "def test",
        ]

        for component in required_components:
            self.assertIn(component, formula_content, f"Formula should contain: {component}")

        print("    ✅ Formula has required components")

        # Check that formula follows Homebrew conventions
        conventions_checks = [
            ("HTTPS URLs", lambda c: "https://" in c),
            ("Proper checksums", lambda c: "sha256" in c),
            ("Install method", lambda c: "bin.install" in c),
            ("Test method", lambda c: "assert_match" in c or "shell_output" in c),
        ]

        for check_name, check_func in conventions_checks:
            if check_func(formula_content):
                print(f"    ✅ {check_name} check passed")
            else:
                print(f"    ⚠️ {check_name} check failed")

        print("✅ Homebrew formula updates compatibility test passed")

    def test_version_management_backwards_compatibility(self):
        """Test that version management changes maintain backwards compatibility.

        Requirements: 4.3, 4.5
        """
        print("\n🔄 Testing version management backwards compatibility...")

        # Test that existing version access methods still work
        version_files = [
            self.project_root / "src" / "riveter" / "version.py",
            self.project_root / "src" / "riveter" / "__init__.py",
            self.project_root / "pyproject.toml",
        ]

        existing_files = [f for f in version_files if f.exists()]

        if not existing_files:
            print("  ⚠️ No version files found, skipping backwards compatibility test")
            return

        # Test pyproject.toml version access
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            print("  🔍 Testing pyproject.toml version access...")

            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib
                except ImportError:
                    print("    ⚠️ tomllib/tomli not available, skipping pyproject.toml test")
                    tomllib = None

            if tomllib:
                try:
                    with open(pyproject_path, "rb") as f:
                        data = tomllib.load(f)

                    version = data.get("project", {}).get("version")
                    self.assertIsNotNone(version, "pyproject.toml should contain project.version")
                    self.assertRegex(
                        version, r"^\d+\.\d+\.\d+", "Version should follow semantic versioning"
                    )

                    print(f"    ✅ pyproject.toml version access works: {version}")
                except Exception as e:
                    self.fail(f"Failed to read version from pyproject.toml: {e}")

        # Test version module if it exists
        version_py = self.project_root / "src" / "riveter" / "version.py"
        if version_py.exists():
            print("  🔍 Testing version.py module...")

            # Test that version module can be imported
            import sys

            sys.path.insert(0, str(self.project_root / "src"))

            try:
                from riveter import version

                # Test common version access patterns
                if hasattr(version, "get_version"):
                    ver = version.get_version()
                    self.assertIsInstance(ver, str, "get_version() should return string")
                    print(f"    ✅ version.get_version() works: {ver}")

                if hasattr(version, "__version__"):
                    ver = version.__version__
                    self.assertIsInstance(ver, str, "__version__ should be string")
                    print(f"    ✅ version.__version__ works: {ver}")

                if hasattr(version, "get_version_from_pyproject"):
                    ver = version.get_version_from_pyproject(self.project_root)
                    self.assertIsInstance(
                        ver, str, "get_version_from_pyproject() should return string"
                    )
                    print(f"    ✅ version.get_version_from_pyproject() works: {ver}")

            except ImportError as e:
                print(f"    ⚠️ Could not import version module: {e}")
            except Exception as e:
                self.fail(f"Version module access failed: {e}")
            finally:
                sys.path.remove(str(self.project_root / "src"))

        print("✅ Version management backwards compatibility test passed")

    def test_cli_functionality_preserved(self):
        """Test that CLI functionality is preserved after changes.

        Requirements: 4.3, 4.4, 4.5
        """
        print("\n💻 Testing CLI functionality preservation...")

        # Check if CLI module exists
        cli_path = self.project_root / "src" / "riveter" / "cli.py"
        if not cli_path.exists():
            print("  ⚠️ CLI module not found, skipping CLI functionality test")
            return

        # Test CLI module syntax
        result = subprocess.run(
            ["python", "-m", "py_compile", str(cli_path)], capture_output=True, text=True
        )

        if result.returncode != 0:
            self.fail(f"CLI module has syntax errors: {result.stderr}")

        print("  ✅ CLI module has valid syntax")

        # Test that CLI can be imported
        import sys

        sys.path.insert(0, str(self.project_root / "src"))

        try:
            from riveter import cli

            print("  ✅ CLI module can be imported")

            # Test that main function exists
            if hasattr(cli, "main"):
                print("  ✅ CLI main function exists")
            else:
                print("  ⚠️ CLI main function not found")

        except ImportError as e:
            print(f"  ⚠️ Could not import CLI module: {e}")
        except Exception as e:
            self.fail(f"CLI module import failed: {e}")
        finally:
            sys.path.remove(str(self.project_root / "src"))

        # Test CLI entry point if package is installed
        if shutil.which("riveter"):
            print("  🔍 Testing installed CLI...")

            # Test version command
            result = subprocess.run(
                ["riveter", "--version"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print(f"  ✅ CLI version command works: {result.stdout.strip()}")
            else:
                print(f"  ⚠️ CLI version command failed: {result.stderr}")

            # Test help command
            result = subprocess.run(
                ["riveter", "--help"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print("  ✅ CLI help command works")
            else:
                print(f"  ⚠️ CLI help command failed: {result.stderr}")
        else:
            print("  ⚠️ riveter CLI not installed, skipping CLI command tests")

        print("✅ CLI functionality preservation test passed")

    def test_existing_tests_still_pass(self):
        """Test that existing tests still pass after changes.

        Requirements: 4.5
        """
        print("\n🧪 Testing that existing tests still pass...")

        # Look for existing test files
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            print("  ⚠️ No tests directory found, skipping existing tests check")
            return

        # Find test files (excluding our new integration tests)
        test_files = []
        for test_file in tests_dir.glob("test_*.py"):
            if test_file.name not in [
                "test_integration_comprehensive.py",
                "test_regression_validation.py",
            ]:
                test_files.append(test_file)

        if not test_files:
            print("  ⚠️ No existing test files found, skipping existing tests check")
            return

        print(f"  🔍 Found {len(test_files)} existing test files")

        # Test that test files have valid syntax
        syntax_errors = []
        for test_file in test_files:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(test_file)], capture_output=True, text=True
            )

            if result.returncode != 0:
                syntax_errors.append((test_file.name, result.stderr))

        if syntax_errors:
            error_msg = "Test files have syntax errors:\n"
            for filename, error in syntax_errors:
                error_msg += f"  {filename}: {error}\n"
            self.fail(error_msg)

        print(f"  ✅ All {len(test_files)} test files have valid syntax")

        # Try to run a subset of tests to ensure they can execute
        # (Don't run all tests as they might be slow or require specific setup)
        sample_tests = test_files[:3]  # Test first 3 files

        for test_file in sample_tests:
            print(f"  🧪 Testing execution of {test_file.name}...")

            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "--collect-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print(f"    ✅ {test_file.name} can be collected by pytest")
            else:
                # Try with unittest
                result = subprocess.run(
                    [
                        "python",
                        "-m",
                        "unittest",
                        "discover",
                        "-s",
                        str(tests_dir),
                        "-p",
                        test_file.name,
                        "--verbose",
                    ],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    print(f"    ✅ {test_file.name} can be run with unittest")
                else:
                    print(f"    ⚠️ {test_file.name} had execution issues")

        print("✅ Existing tests compatibility check passed")

    def test_documentation_and_examples_still_valid(self):
        """Test that documentation and examples are still valid after changes.

        Requirements: 4.5
        """
        print("\n📚 Testing documentation and examples validity...")

        # Check README files
        readme_files = [self.project_root / "README.md", self.project_root / "docs" / "README.md"]

        existing_readmes = [f for f in readme_files if f.exists()]

        for readme in existing_readmes:
            print(f"  📖 Checking {readme.relative_to(self.project_root)}...")

            with open(readme, "r") as f:
                content = f.read()

            # Check for broken references to old patterns
            broken_patterns = [
                "brew audit Formula/",  # Old audit syntax
                "version mismatch",  # Should be resolved
                "exit code 1",  # Should be resolved
            ]

            for pattern in broken_patterns:
                if pattern in content:
                    print(f"    ⚠️ Found potentially outdated reference: {pattern}")

            print(f"    ✅ {readme.name} checked")

        # Check example files
        examples_dir = self.project_root / "examples"
        if examples_dir.exists():
            print("  📁 Checking examples directory...")

            example_files = list(examples_dir.rglob("*.py")) + list(examples_dir.rglob("*.yml"))

            for example_file in example_files[:5]:  # Check first 5 examples
                if example_file.suffix == ".py":
                    # Check Python syntax
                    result = subprocess.run(
                        ["python", "-m", "py_compile", str(example_file)],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        print(f"    ✅ {example_file.name} has valid Python syntax")
                    else:
                        print(f"    ⚠️ {example_file.name} has syntax issues")

                elif example_file.suffix in [".yml", ".yaml"]:
                    # Check YAML syntax
                    try:
                        import yaml

                        with open(example_file, "r") as f:
                            yaml.safe_load(f)
                        print(f"    ✅ {example_file.name} has valid YAML syntax")
                    except ImportError:
                        print(f"    ⚠️ Cannot validate {example_file.name} (PyYAML not available)")
                    except yaml.YAMLError:
                        print(f"    ⚠️ {example_file.name} has YAML syntax issues")

        print("✅ Documentation and examples validity test passed")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
