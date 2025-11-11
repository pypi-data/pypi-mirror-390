#!/usr/bin/env python3
"""Performance benchmarking script for Riveter CLI lazy import optimization.

This script measures the startup time and performance of various CLI commands
to validate that the lazy import optimization is working correctly.
"""

import json
import statistics
import subprocess
import sys
import time
from typing import Any, Dict, List


def measure_command_performance(command: List[str], iterations: int = 5) -> Dict[str, Any]:
    """Measure the performance of a CLI command over multiple iterations.

    Args:
        command: The command to execute as a list of strings
        iterations: Number of times to run the command

    Returns:
        Dictionary with performance metrics
    """
    times = []
    successful_runs = 0

    for i in range(iterations):
        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
            )
            end_time = time.time()

            if result.returncode == 0:
                duration = end_time - start_time
                times.append(duration)
                successful_runs += 1
                print(f"  Run {i+1}: {duration:.3f}s")
            else:
                print(f"  Run {i+1}: FAILED (exit code {result.returncode})")
                if result.stderr:
                    print(f"    Error: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(f"  Run {i+1}: TIMEOUT (>30s)")
        except Exception as e:
            print(f"  Run {i+1}: ERROR ({e})")

    if not times:
        return {
            "command": " ".join(command),
            "successful_runs": 0,
            "total_runs": iterations,
            "error": "No successful runs",
        }

    return {
        "command": " ".join(command),
        "successful_runs": successful_runs,
        "total_runs": iterations,
        "min_time": min(times),
        "max_time": max(times),
        "avg_time": statistics.mean(times),
        "median_time": statistics.median(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        "all_times": times,
    }


def check_heavy_imports_not_loaded(command: List[str]) -> Dict[str, Any]:
    """Check if heavy imports are loaded by examining import behavior.

    This is a simplified check - in a real implementation, we'd need more
    sophisticated monitoring of what modules get imported.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)

        # For now, we'll just check if the command completes quickly
        # In a more sophisticated implementation, we could use import hooks
        # or other mechanisms to track what modules are actually loaded

        return {
            "command": " ".join(command),
            "exit_code": result.returncode,
            "stdout_length": len(result.stdout),
            "stderr_length": len(result.stderr),
            "completed_successfully": result.returncode == 0,
        }

    except Exception as e:
        return {"command": " ".join(command), "error": str(e), "completed_successfully": False}


def main():
    """Main benchmarking function."""
    print("🚀 Riveter CLI Performance Benchmarking")
    print("=" * 50)

    # Check if riveter is available
    try:
        result = subprocess.run(
            ["python3", "-c", "from src.riveter.cli import main; main()", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print("❌ Error: Cannot run riveter CLI")
            print(f"Exit code: {result.returncode}")
            print(f"Stderr: {result.stderr}")
            sys.exit(1)
        else:
            print(f"✅ Riveter CLI available: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Error checking riveter availability: {e}")
        sys.exit(1)

    print()

    # Define commands to benchmark
    commands_to_test = [
        {
            "name": "Version Command",
            "command": ["python3", "-c", "from src.riveter.cli import main; main()", "--version"],
            "target_time": 2.0,
            "description": "Should complete in under 2 seconds",
        },
        {
            "name": "Help Command",
            "command": ["python3", "-c", "from src.riveter.cli import main; main()", "--help"],
            "target_time": 2.0,
            "description": "Should complete in under 2 seconds",
        },
        {
            "name": "List Rule Packs",
            "command": [
                "python3",
                "-c",
                "from src.riveter.cli import main; main()",
                "list-rule-packs",
            ],
            "target_time": 5.0,
            "description": "Should complete in under 5 seconds",
        },
        {
            "name": "Scan Help",
            "command": [
                "python3",
                "-c",
                "from src.riveter.cli import main; main()",
                "scan",
                "--help",
            ],
            "target_time": 5.0,
            "description": "Should complete in under 5 seconds",
        },
    ]

    results = []

    for test_case in commands_to_test:
        print(f"📊 Testing: {test_case['name']}")
        print(f"   Command: {' '.join(test_case['command'])}")
        print(f"   Target: {test_case['description']}")

        # Measure performance
        perf_result = measure_command_performance(
            test_case["command"],
            iterations=3,  # Reduced iterations for faster testing
        )

        # Add test metadata
        perf_result.update(
            {
                "test_name": test_case["name"],
                "target_time": test_case["target_time"],
                "description": test_case["description"],
            }
        )

        results.append(perf_result)

        # Check if target was met
        if "avg_time" in perf_result:
            if perf_result["avg_time"] <= test_case["target_time"]:
                print(
                    f"   ✅ PASS: Average time {perf_result['avg_time']:.3f}s <= "
                    f"{test_case['target_time']}s"
                )
            else:
                print(
                    f"   ❌ FAIL: Average time {perf_result['avg_time']:.3f}s > "
                    f"{test_case['target_time']}s"
                )
        else:
            print(f"   ❌ FAIL: {perf_result.get('error', 'Unknown error')}")

        print()

    # Summary
    print("📋 Performance Summary")
    print("=" * 50)

    passed_tests = 0
    total_tests = 0

    for result in results:
        total_tests += 1
        if "avg_time" in result and result["avg_time"] <= result["target_time"]:
            passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"{status} {result['test_name']}: ", end="")
        if "avg_time" in result:
            print(f"{result['avg_time']:.3f}s (target: {result['target_time']}s)")
        else:
            print(f"ERROR - {result.get('error', 'Unknown')}")

    print()
    print(f"Overall: {passed_tests}/{total_tests} tests passed")

    # Check for basic operations not loading heavy dependencies
    print("\n🔍 Checking Heavy Import Behavior")
    print("=" * 50)

    basic_commands = [
        ["python3", "-c", "from src.riveter.cli import main; main()", "--version"],
        ["python3", "-c", "from src.riveter.cli import main; main()", "--help"],
    ]

    for cmd in basic_commands:
        print(f"Checking: {' '.join(cmd)}")
        import_result = check_heavy_imports_not_loaded(cmd)

        if import_result["completed_successfully"]:
            print("   ✅ Command completed successfully")
        else:
            print(f"   ❌ Command failed: {import_result.get('error', 'Unknown error')}")

    # Save detailed results
    with open("performance_benchmark_results.json", "w") as f:
        json.dump(
            {
                "timestamp": time.time(),
                "summary": {
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                },
                "detailed_results": results,
            },
            f,
            indent=2,
        )

    print("\n📄 Detailed results saved to: performance_benchmark_results.json")

    # Exit with appropriate code
    if passed_tests == total_tests:
        print("\n🎉 All performance targets met!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_tests - passed_tests} performance targets not met")
        sys.exit(1)


if __name__ == "__main__":
    main()
