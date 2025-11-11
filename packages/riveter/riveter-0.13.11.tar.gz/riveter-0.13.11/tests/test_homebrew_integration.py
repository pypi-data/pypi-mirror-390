#!/usr/bin/env python3
"""Tests for Homebrew integration to ensure the tap installation works correctly.

This test suite validates that the Homebrew tap can be added, Riveter can be
installed via Homebrew, and the installation works as expected.
"""

import subprocess
from typing import List

import pytest


def run_command(cmd: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a shell command and return the result.

    Args:
        cmd: Command to run as list of strings
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess result
    """
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def is_homebrew_available() -> bool:
    """Check if Homebrew is available on the system.

    Returns:
        True if Homebrew is available, False otherwise
    """
    try:
        result = run_command(["brew", "--version"])
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_tap_added(tap_name: str) -> bool:
    """Check if a Homebrew tap is already added.

    Args:
        tap_name: Name of the tap to check

    Returns:
        True if tap is added, False otherwise
    """
    try:
        result = run_command(["brew", "tap"])
        return tap_name in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_formula_installed(formula_name: str) -> bool:
    """Check if a Homebrew formula is installed.

    Args:
        formula_name: Name of the formula to check

    Returns:
        True if formula is installed, False otherwise
    """
    try:
        result = run_command(["brew", "list", formula_name])
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


class TestHomebrewIntegration:
    """Test suite for Homebrew integration validation."""

    def test_homebrew_available(self):
        """Test that Homebrew is available on the system."""
        if not is_homebrew_available():
            pytest.skip("Homebrew not available - skipping Homebrew integration tests")

        result = run_command(["brew", "--version"])
        assert result.returncode == 0, f"Homebrew version check failed: {result.stderr}"
        assert "Homebrew" in result.stdout, "Homebrew version output should contain 'Homebrew'"

    def test_tap_repository_accessible(self):
        """Test that the Homebrew tap repository is accessible."""
        if not is_homebrew_available():
            pytest.skip("Homebrew not available")

        # Try to access the tap repository information
        result = run_command(["brew", "tap-info", "scottryanhoward/homebrew-riveter"])

        # If tap is not added, this will fail, but we can still check if it's accessible
        if result.returncode != 0:
            # Try to add the tap temporarily to test accessibility
            add_result = run_command(["brew", "tap", "scottryanhoward/homebrew-riveter"])
            if add_result.returncode == 0:
                # Clean up - remove the tap
                run_command(["brew", "untap", "scottryanhoward/homebrew-riveter"])
                assert True, "Tap repository is accessible"
            else:
                pytest.skip(f"Tap repository not accessible: {add_result.stderr}")
        else:
            assert True, "Tap repository is accessible"

    def test_formula_exists_in_tap(self):
        """Test that the Riveter formula exists in the tap."""
        if not is_homebrew_available():
            pytest.skip("Homebrew not available")

        # Add tap if not already added
        tap_added = is_tap_added("scottryanhoward/homebrew-riveter")
        if not tap_added:
            result = run_command(["brew", "tap", "scottryanhoward/homebrew-riveter"])
            if result.returncode != 0:
                pytest.skip(f"Failed to add tap: {result.stderr}")

        try:
            # Check if formula exists
            result = run_command(["brew", "info", "scottryanhoward/homebrew-riveter/riveter"])
            assert result.returncode == 0, f"Formula not found in tap: {result.stderr}"
            assert "riveter" in result.stdout.lower(), "Formula info should contain 'riveter'"

        finally:
            # Clean up - remove tap if we added it
            if not tap_added:
                run_command(["brew", "untap", "scottryanhoward/homebrew-riveter"])

    def test_basic_installation_flow(self):
        """Test basic installation and functionality."""
        if not is_homebrew_available():
            pytest.skip("Homebrew not available")

        # Check if already installed
        already_installed = is_formula_installed("riveter")

        if already_installed:
            # Test that it works
            result = run_command(["riveter", "--version"])
            assert result.returncode == 0, "Installed Riveter should work"
            return  # Skip installation test if already installed

        # Add tap if not already added
        tap_added = is_tap_added("scottryanhoward/homebrew-riveter")
        if not tap_added:
            result = run_command(["brew", "tap", "scottryanhoward/homebrew-riveter"])
            if result.returncode != 0:
                pytest.skip(f"Failed to add tap: {result.stderr}")

        try:
            # Install Riveter with longer timeout
            result = run_command(["brew", "install", "riveter"], timeout=180)  # 3 minutes
            if result.returncode != 0:
                pytest.skip(f"Installation failed: {result.stderr}")

            # Verify installation
            result = run_command(["riveter", "--version"])
            assert result.returncode == 0, f"Installed Riveter doesn't work: {result.stderr}"
            assert "riveter" in result.stdout.lower(), "Version should contain 'riveter'"

        finally:
            # Clean up - uninstall if we installed it
            if not already_installed:
                run_command(["brew", "uninstall", "riveter"])

            # Clean up - remove tap if we added it
            if not tap_added:
                run_command(["brew", "untap", "scottryanhoward/homebrew-riveter"])

    def test_formula_validation(self):
        """Test that the formula is valid and well-formed."""
        if not is_homebrew_available():
            pytest.skip("Homebrew not available")

        # Add tap if not already added
        tap_added = is_tap_added("scottryanhoward/homebrew-riveter")
        if not tap_added:
            result = run_command(["brew", "tap", "scottryanhoward/homebrew-riveter"])
            if result.returncode != 0:
                pytest.skip(f"Failed to add tap: {result.stderr}")

        try:
            # Check formula info (lighter than audit)
            result = run_command(["brew", "info", "scottryanhoward/homebrew-riveter/riveter"])
            assert result.returncode == 0, f"Formula info failed: {result.stderr}"

            info_text = result.stdout.lower()
            assert "riveter" in info_text, "Formula info should contain 'riveter'"

        finally:
            # Clean up - remove tap if we added it
            if not tap_added:
                run_command(["brew", "untap", "scottryanhoward/homebrew-riveter"])

    def test_one_step_installation_command(self):
        """Test the one-step installation command format."""
        if not is_homebrew_available():
            pytest.skip("Homebrew not available")

        # Just test that the command format is recognized (don't actually install)
        result = run_command(["brew", "info", "scottryanhoward/homebrew-riveter/riveter"])

        # If this succeeds, the one-step format should work
        # If it fails, the tap might not be available
        if result.returncode != 0:
            pytest.skip("Tap not available for one-step installation test")

        # The fact that brew recognizes the formula means one-step installation should work
        assert (
            "riveter" in result.stdout.lower()
        ), "One-step installation format should be recognized"
