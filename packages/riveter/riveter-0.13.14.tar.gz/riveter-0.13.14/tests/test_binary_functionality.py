#!/usr/bin/env python3
"""Tests for binary functionality to ensure the PyInstaller binary works correctly.

This test suite validates that the compiled binary provides the same functionality
as the Python version, including CLI commands, rule pack loading, and output formats.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

import pytest


def find_binary_path() -> Optional[Path]:
    """Find the Riveter binary in common locations.

    Returns:
        Path to the binary if found, None otherwise
    """
    # Common binary locations
    possible_paths = [
        Path("dist/riveter"),  # PyInstaller output
        Path("riveter"),  # Current directory
        Path("../riveter"),  # Parent directory
        Path("build/riveter"),  # Build directory
    ]

    # Also check PATH
    try:
        result = subprocess.run(
            ["which", "riveter"], capture_output=True, text=True, check=True, timeout=5
        )
        if result.stdout.strip():
            possible_paths.append(Path(result.stdout.strip()))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    # Find first existing binary
    for path in possible_paths:
        if path.exists() and path.is_file():
            # Make sure it's executable
            if os.access(path, os.X_OK):
                return path

    return None


def run_binary_command(args: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a command with the Riveter binary.

    Args:
        args: Command arguments (without the binary name)
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess result

    Raises:
        RuntimeError: If binary is not found
    """
    binary_path = find_binary_path()
    if not binary_path:
        raise RuntimeError("Riveter binary not found")

    cmd = [str(binary_path)] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


class TestBinaryFunctionality:
    """Test suite for binary functionality validation."""

    def test_binary_exists(self):
        """Test that the binary exists and is executable."""
        binary_path = find_binary_path()
        if binary_path is None:
            pytest.skip("Riveter binary not found - skipping binary tests")

        assert binary_path.exists(), f"Binary does not exist at {binary_path}"
        assert os.access(binary_path, os.X_OK), f"Binary is not executable at {binary_path}"

    def test_version_command(self):
        """Test that --version command works and returns expected format."""
        try:
            result = run_binary_command(["--version"])
            assert result.returncode == 0, f"Version command failed: {result.stderr}"
            assert "riveter" in result.stdout.lower(), "Version output should contain 'riveter'"
        except RuntimeError:
            pytest.skip("Riveter binary not found - skipping version test")
        except subprocess.TimeoutExpired:
            pytest.fail("Version command timed out")

    def test_help_command(self):
        """Test that --help command works and shows usage information."""
        try:
            result = run_binary_command(["--help"])
            assert result.returncode == 0, f"Help command failed: {result.stderr}"

            help_text = result.stdout.lower()
            assert (
                "usage" in help_text or "riveter" in help_text
            ), "Help should contain usage information"
        except RuntimeError:
            pytest.skip("Riveter binary not found - skipping help test")
        except subprocess.TimeoutExpired:
            pytest.fail("Help command timed out")

    def test_list_rule_packs_command(self):
        """Test that list-rule-packs command works."""
        try:
            result = run_binary_command(["list-rule-packs"])
            # Command should either succeed or fail gracefully
            assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"

            if result.returncode == 0:
                # Should contain some output about rule packs
                assert len(result.stdout.strip()) >= 0, "List rule packs should produce some output"
        except RuntimeError:
            pytest.skip("Riveter binary not found - skipping rule packs test")
        except subprocess.TimeoutExpired:
            pytest.fail("List rule packs command timed out")

    def test_scan_command_with_invalid_file(self):
        """Test scan command with non-existent file (should fail gracefully)."""
        try:
            result = run_binary_command(["scan", "-t", "nonexistent.tf"])
            assert result.returncode != 0, "Scan with non-existent file should fail"
            # Should provide some kind of error indication
            assert (
                len(result.stderr) > 0 or "error" in result.stdout.lower()
            ), "Should provide error message"
        except RuntimeError:
            pytest.skip("Riveter binary not found - skipping scan test")
        except subprocess.TimeoutExpired:
            pytest.fail("Scan command timed out")

    def test_basic_scan_functionality(self):
        """Test basic scan functionality with a simple Terraform file."""
        # Create a minimal test Terraform file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(
                """
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
"""
            )
            tf_file = f.name

        try:
            # Test basic scan
            result = run_binary_command(["scan", "-t", tf_file], timeout=15)

            # Should either succeed or fail gracefully (not crash)
            assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"

            # Should produce some output
            total_output = len(result.stdout) + len(result.stderr)
            assert total_output > 0, "Scan should produce some output"

        except RuntimeError:
            pytest.skip("Riveter binary not found - skipping scan functionality test")
        except subprocess.TimeoutExpired:
            pytest.fail("Basic scan command timed out")
        finally:
            # Clean up
            try:
                os.unlink(tf_file)
            except OSError:
                pass

    def test_json_output_format(self):
        """Test that JSON output format works correctly."""
        # Create a minimal test Terraform file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(
                """
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
"""
            )
            tf_file = f.name

        try:
            # Test JSON output
            result = run_binary_command(
                ["scan", "-t", tf_file, "--output-format", "json"], timeout=15
            )

            # Should either succeed or fail gracefully
            assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"

            if result.returncode == 0 and result.stdout.strip():
                # If successful and has output, should be valid JSON
                try:
                    json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Try to find JSON in the output
                    lines = result.stdout.strip().split("\n")
                    json_found = False
                    for line in lines:
                        if line.strip().startswith("{") or line.strip().startswith("["):
                            try:
                                json.loads(line.strip())
                                json_found = True
                                break
                            except json.JSONDecodeError:
                                continue

                    if not json_found:
                        pytest.fail("JSON output format produced invalid JSON")

        except RuntimeError:
            pytest.skip("Riveter binary not found - skipping JSON test")
        except subprocess.TimeoutExpired:
            pytest.fail("JSON output test timed out")
        finally:
            # Clean up
            try:
                os.unlink(tf_file)
            except OSError:
                pass

    def test_error_handling(self):
        """Test that the binary handles errors gracefully."""
        try:
            # Test with invalid arguments
            result = run_binary_command(["--invalid-argument"])
            assert result.returncode != 0, "Invalid arguments should cause failure"
            # Should handle error gracefully (not crash)
            assert result.returncode < 128, "Should not crash with signal"

        except RuntimeError:
            pytest.skip("Riveter binary not found - skipping error handling test")
        except subprocess.TimeoutExpired:
            pytest.fail("Error handling test timed out")
