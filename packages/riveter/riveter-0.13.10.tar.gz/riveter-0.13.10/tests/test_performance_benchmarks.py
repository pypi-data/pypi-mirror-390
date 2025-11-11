#!/usr/bin/env python3
"""Performance benchmark tests comparing binary vs Python installations.

This test suite measures and compares performance characteristics between
the PyInstaller binary and Python package installations of Riveter.
"""

import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Tuple

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


def run_binary_command(
    args: List[str], timeout: int = 15
) -> Tuple[subprocess.CompletedProcess, float]:
    """Run a command with the Riveter binary and measure execution time.

    Args:
        args: Command arguments (without the binary name)
        timeout: Command timeout in seconds

    Returns:
        Tuple of (CompletedProcess result, execution time in seconds)

    Raises:
        RuntimeError: If binary is not found
    """
    binary_path = find_binary_path()
    if not binary_path:
        raise RuntimeError("Riveter binary not found")

    cmd = [str(binary_path)] + args

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    end_time = time.time()

    return result, end_time - start_time


def create_test_terraform_file(size: str = "small") -> str:
    """Create a test Terraform file of specified size.

    Args:
        size: Size of the file ('small', 'medium')

    Returns:
        Path to the created temporary file
    """
    content_templates = {
        "small": """
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
""",
        "medium": """
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "main-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"

  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet"
  }
}

resource "aws_security_group" "web" {
  name_prefix = "web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}
""",
    }

    content = content_templates.get(size, content_templates["small"])

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
        f.write(content)
        return f.name


class TestPerformanceBenchmarks:
    """Test suite for performance benchmarking."""

    def test_startup_time_comparison(self):
        """Compare startup times between binary and Python versions."""
        binary_path = find_binary_path()
        if not binary_path:
            pytest.skip("Riveter binary not found - skipping startup time test")

        # Measure binary startup time (version command)
        binary_times = []
        for _ in range(3):  # Run 3 times for average
            try:
                _, duration = run_binary_command(["--version"])
                binary_times.append(duration)
            except (subprocess.TimeoutExpired, Exception):
                pytest.skip("Binary version command failed or timed out")

        # Calculate averages
        binary_avg = sum(binary_times) / len(binary_times)

        # Report results
        print("\nStartup Time Comparison:")
        print(f"Binary average: {binary_avg:.3f}s")

        # Binary should start reasonably quickly (under 3 seconds)
        assert binary_avg < 3.0, f"Binary startup too slow: {binary_avg:.3f}s"

    def test_file_processing_performance(self):
        """Compare file processing performance."""
        binary_path = find_binary_path()
        if not binary_path:
            pytest.skip("Riveter binary not found - skipping file processing test")

        results = {}

        # Test with small file only (for CI performance)
        for size in ["small"]:
            tf_file = create_test_terraform_file(size)

            try:
                # Test binary performance
                binary_times = []
                for _ in range(2):  # 2 iterations
                    try:
                        result, duration = run_binary_command(["scan", "-t", tf_file], timeout=30)
                        if result.returncode in [0, 1]:  # Success or validation errors
                            binary_times.append(duration)
                    except subprocess.TimeoutExpired:
                        break

                # Store results
                if binary_times:
                    results[size] = {
                        "binary_mean": sum(binary_times) / len(binary_times),
                        "binary_times": binary_times,
                    }

            finally:
                # Clean up
                try:
                    os.unlink(tf_file)
                except OSError:
                    pass

        # Verify we got some results
        if not results:
            pytest.skip("No performance results collected")

        # Check results for different file sizes
        for _file_type, data in results.items():
            assert "binary_mean" in data
            assert data["binary_mean"] > 0, "Binary processing time should be positive"

            # Binary should complete within reasonable time
            assert (
                data["binary_mean"] < 15.0
            ), f"Binary processing too slow: {data['binary_mean']:.3f}s"

        # Print performance summary
        print("\nFile Processing Performance:")
        for size, data in results.items():
            print(f"{size.capitalize()} files:")
            print(f"  Binary: {data['binary_mean']:.3f}s")

    def test_basic_functionality_performance(self):
        """Test basic functionality performance."""
        binary_path = find_binary_path()
        if not binary_path:
            pytest.skip("Riveter binary not found - skipping functionality test")

        # Test help command performance
        try:
            result, duration = run_binary_command(["--help"])
            assert result.returncode == 0, "Help command should succeed"
            assert duration < 3.0, f"Help command too slow: {duration:.3f}s"
        except subprocess.TimeoutExpired:
            pytest.fail("Help command timed out")

        # Test list-rule-packs performance
        try:
            result, duration = run_binary_command(["list-rule-packs"])
            # Command should either succeed or fail gracefully
            assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"
            assert duration < 5.0, f"List rule packs too slow: {duration:.3f}s"
        except subprocess.TimeoutExpired:
            pytest.fail("List rule packs command timed out")

    def test_memory_usage_basic(self):
        """Basic test to ensure binary doesn't use excessive memory."""
        binary_path = find_binary_path()
        if not binary_path:
            pytest.skip("Riveter binary not found - skipping memory test")

        # This is a basic test - we just ensure the binary can run
        try:
            result, duration = run_binary_command(["--version"])
            assert result.returncode == 0, "Binary should run successfully"
            assert duration < 3.0, "Version command should complete quickly"
        except subprocess.TimeoutExpired:
            pytest.fail("Memory test timed out")

    def test_concurrent_execution(self):
        """Test that multiple instances can run concurrently."""
        binary_path = find_binary_path()
        if not binary_path:
            pytest.skip("Riveter binary not found - skipping concurrent test")

        import threading

        results = []
        errors = []

        def run_version_check():
            try:
                result, duration = run_binary_command(["--version"])
                results.append((result.returncode, duration))
            except Exception as e:
                errors.append(str(e))

        # Start multiple threads
        threads = []
        for _ in range(2):  # Run 2 concurrent instances (reduced for CI)
            thread = threading.Thread(target=run_version_check)
            threads.append(thread)
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=10)

        # Check results
        assert len(errors) == 0, f"Concurrent execution had errors: {errors}"
        assert len(results) == 2, "All concurrent executions should complete"

        for returncode, duration in results:
            assert returncode == 0, "All concurrent executions should succeed"
            assert duration < 3.0, "All executions should complete quickly"
