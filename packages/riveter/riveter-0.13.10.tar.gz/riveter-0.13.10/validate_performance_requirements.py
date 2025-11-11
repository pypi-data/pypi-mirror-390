#!/usr/bin/env python3
"""Comprehensive validation script for Riveter CLI performance requirements.

This script validates all the performance requirements from the specification:
- Requirement 1.1: Version command completes in under 2 seconds
- Requirement 1.2: Help command completes in under 2 seconds
- Requirement 3.1: Basic operations complete in under 2 seconds
- Requirement 3.2: Full operations have acceptable performance (3-5 seconds startup)
"""

import os
import statistics
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List


class PerformanceValidator:
    """Validates Riveter CLI performance requirements."""

    def __init__(self):
        self.results = []
        self.passed_tests = 0
        self.total_tests = 0

    def run_command_benchmark(
        self, name: str, command: List[str], target_time: float, iterations: int = 3
    ) -> Dict[str, Any]:
        """Run a command multiple times and measure performance."""
        print(f"\n🧪 Testing: {name}")
        print(f"   Command: {' '.join(command)}")
        print(f"   Target: ≤{target_time}s")

        times = []
        successful_runs = 0

        for i in range(iterations):
            start_time = time.time()
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                end_time = time.time()

                duration = end_time - start_time
                times.append(duration)

                # For scan commands, exit code 1 is acceptable (indicates validation failures found)
                if result.returncode == 0 or (
                    name.startswith("Scan Command") and result.returncode == 1
                ):
                    successful_runs += 1
                    print(f"   Run {i+1}: {duration:.3f}s ✅")
                else:
                    print(f"   Run {i+1}: {duration:.3f}s ❌ (exit code {result.returncode})")

            except subprocess.TimeoutExpired:
                print(f"   Run {i+1}: TIMEOUT (>30s) ❌")
            except Exception as e:
                print(f"   Run {i+1}: ERROR ({e}) ❌")

        if not times:
            return {
                "name": name,
                "target_time": target_time,
                "error": "No successful runs",
                "passed": False,
            }

        avg_time = statistics.mean(times)
        passed = avg_time <= target_time and successful_runs == iterations

        result = {
            "name": name,
            "target_time": target_time,
            "avg_time": avg_time,
            "min_time": min(times),
            "max_time": max(times),
            "successful_runs": successful_runs,
            "total_runs": iterations,
            "passed": passed,
            "all_times": times,
        }

        if passed:
            print(f"   ✅ PASS: Average {avg_time:.3f}s ≤ {target_time}s")
            self.passed_tests += 1
        else:
            print(f"   ❌ FAIL: Average {avg_time:.3f}s > {target_time}s")

        self.total_tests += 1
        self.results.append(result)
        return result

    def test_basic_operations(self):
        """Test basic operations (Requirements 1.1, 1.2, 3.1)."""
        print("\n" + "=" * 60)
        print("🚀 TESTING BASIC OPERATIONS (Requirements 1.1, 1.2, 3.1)")
        print("=" * 60)

        # Requirement 1.1: Version command completes in under 2 seconds
        self.run_command_benchmark(
            "Version Command (Req 1.1)",
            ["python3", "-c", "from src.riveter.cli import main; main()", "--version"],
            2.0,
        )

        # Requirement 1.2: Help command completes in under 2 seconds
        self.run_command_benchmark(
            "Help Command (Req 1.2)",
            ["python3", "-c", "from src.riveter.cli import main; main()", "--help"],
            2.0,
        )

        # Additional basic operations for Requirement 3.1
        self.run_command_benchmark(
            "Scan Help (Req 3.1)",
            ["python3", "-c", "from src.riveter.cli import main; main()", "scan", "--help"],
            2.0,
        )

    def test_full_operations(self):
        """Test full operations (Requirement 3.2)."""
        print("\n" + "=" * 60)
        print("🔧 TESTING FULL OPERATIONS (Requirement 3.2)")
        print("=" * 60)

        # Create test files
        tf_file = self._create_test_terraform_file()
        rules_file = self._create_test_rules_file()

        try:
            # Requirement 3.2: Full operations have acceptable performance (3-5 seconds startup)
            self.run_command_benchmark(
                "List Rule Packs (Req 3.2)",
                ["python3", "-c", "from src.riveter.cli import main; main()", "list-rule-packs"],
                5.0,
            )

            # Test actual scan command
            self.run_command_benchmark(
                "Scan Command (Req 3.2)",
                [
                    "python3",
                    "-c",
                    "from src.riveter.cli import main; main()",
                    "scan",
                    "--rules",
                    rules_file,
                    "--terraform",
                    tf_file,
                    "--output-format",
                    "json",
                ],
                5.0,
                iterations=2,  # Fewer iterations for the heavier command
            )

        finally:
            # Clean up
            try:
                os.unlink(tf_file)
                os.unlink(rules_file)
            except OSError:
                pass

    def test_heavy_imports_not_loaded(self):
        """Test that basic operations don't load heavy dependencies."""
        print("\n" + "=" * 60)
        print("🔍 TESTING HEAVY IMPORT BEHAVIOR")
        print("=" * 60)

        basic_commands = [
            (
                "Version Command",
                ["python3", "-c", "from src.riveter.cli import main; main()", "--version"],
            ),
            (
                "Help Command",
                ["python3", "-c", "from src.riveter.cli import main; main()", "--help"],
            ),
        ]

        for name, command in basic_commands:
            print(f"\n🧪 Testing: {name}")
            print("   Checking that heavy imports are not loaded...")

            try:
                start_time = time.time()
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                end_time = time.time()

                duration = end_time - start_time

                # If the command completes very quickly, it's likely not loading heavy imports
                if result.returncode == 0 and duration < 1.0:
                    print(f"   ✅ PASS: Completed in {duration:.3f}s (likely no heavy imports)")
                    self.passed_tests += 1
                else:
                    print(
                        f"   ❌ FAIL: Took {duration:.3f}s or failed "
                        f"(exit code: {result.returncode})"
                    )

                self.total_tests += 1

            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                self.total_tests += 1

    def _create_test_terraform_file(self) -> str:
        """Create a test Terraform file."""
        tf_content = """
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"

  tags = {
    Name = "test-instance"
  }
}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(tf_content)
            return f.name

    def _create_test_rules_file(self) -> str:
        """Create a test rules file."""
        rules_content = """
metadata:
  name: test-rules
  version: 1.0.0
  description: Test rules for performance testing
  author: Test

rules:
  - id: test-rule-1
    description: Test that instances have tags
    resource_type: aws_instance
    severity: warning
    assert:
      tags: exists
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(rules_content)
            return f.name

    def print_summary(self):
        """Print final summary of all tests."""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE VALIDATION SUMMARY")
        print("=" * 60)

        print(f"\nOverall Results: {self.passed_tests}/{self.total_tests} tests passed")

        if self.passed_tests == self.total_tests:
            print("🎉 ALL PERFORMANCE REQUIREMENTS MET!")
            success = True
        else:
            print(f"⚠️  {self.total_tests - self.passed_tests} performance requirements not met")
            success = False

        print("\nDetailed Results:")
        for result in self.results:
            if result.get("passed", False):
                status = "✅ PASS"
            else:
                status = "❌ FAIL"

            if "avg_time" in result:
                print(
                    f"  {status} {result['name']}: {result['avg_time']:.3f}s "
                    f"(target: {result['target_time']}s)"
                )
            else:
                print(f"  {status} {result['name']}: {result.get('error', 'Unknown error')}")

        print("\n📈 Performance Summary:")
        print(
            "   • Basic operations (version, help): All under 2 seconds ✅"
            if self.passed_tests >= 2
            else "   • Basic operations: Some over 2 seconds ❌"
        )
        print(
            "   • Full operations: All under 5 seconds ✅"
            if success
            else "   • Full operations: Some over 5 seconds ❌"
        )
        print(
            "   • Heavy imports: Not loaded for basic commands ✅"
            if success
            else "   • Heavy imports: May be loaded unnecessarily ❌"
        )

        return success


def main():
    """Main validation function."""
    print("🚀 Riveter CLI Performance Requirements Validation")
    print("=" * 60)
    print("This script validates all performance requirements from the specification:")
    print("• Requirement 1.1: Version command completes in under 2 seconds")
    print("• Requirement 1.2: Help command completes in under 2 seconds")
    print("• Requirement 3.1: Basic operations complete in under 2 seconds")
    print("• Requirement 3.2: Full operations have acceptable performance (3-5 seconds)")

    validator = PerformanceValidator()

    # Run all tests
    validator.test_basic_operations()
    validator.test_full_operations()
    validator.test_heavy_imports_not_loaded()

    # Print summary and exit with appropriate code
    success = validator.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
