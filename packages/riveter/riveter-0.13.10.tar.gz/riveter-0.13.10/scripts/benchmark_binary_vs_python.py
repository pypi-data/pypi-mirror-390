#!/usr/bin/env python3
"""
Benchmark script to compare binary vs Python installation performance.

This script measures startup time, memory usage, and processing performance
between the binary distribution and Python installation of Riveter.
"""

import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

import psutil


class PerformanceBenchmark:
    """Performance benchmark runner for binary vs Python comparison."""

    def __init__(self, binary_path: str = None, python_path: str = None):
        """Initialize benchmark with paths to binary and Python installations."""
        self.binary_path = binary_path or self._find_binary_path()
        self.python_path = python_path or self._find_python_path()
        self.results = {}

    def _find_binary_path(self) -> str:
        """Find the Riveter binary path."""
        possible_paths = [
            "./dist/riveter",  # Local build
            "/usr/local/bin/riveter",  # Homebrew install
            "/opt/homebrew/bin/riveter",  # Homebrew on Apple Silicon
            "riveter",  # In PATH
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path
            elif subprocess.run(["which", path], capture_output=True).returncode == 0:
                return path

        raise FileNotFoundError("Riveter binary not found")

    def _find_python_path(self) -> str:
        """Find the Python installation path."""
        # Check if we can run riveter via Python module
        result = subprocess.run([sys.executable, "-c", "import riveter.cli"], capture_output=True)
        if result.returncode == 0:
            return sys.executable

        raise FileNotFoundError("Python Riveter installation not found")

    def run_binary_command(self, args: List[str], measure_memory: bool = False) -> Dict[str, Any]:
        """Run a command with the binary and measure performance."""
        return self._run_command([self.binary_path] + args, measure_memory)

    def run_python_command(self, args: List[str], measure_memory: bool = False) -> Dict[str, Any]:
        """Run a command with Python and measure performance."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")

        return self._run_command(
            [self.python_path, "-m", "riveter.cli"] + args, measure_memory, env=env
        )

    def _run_command(
        self, cmd: List[str], measure_memory: bool = False, env: Dict = None
    ) -> Dict[str, Any]:
        """Run a command and measure its performance."""
        start_time = time.time()

        if measure_memory:
            # Start process and monitor memory
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
            )

            # Monitor memory usage
            max_memory = 0
            try:
                ps_process = psutil.Process(process.pid)
                while process.poll() is None:
                    try:
                        memory_info = ps_process.memory_info()
                        max_memory = max(max_memory, memory_info.rss)
                        time.sleep(0.01)  # Check every 10ms
                    except psutil.NoSuchProcess:
                        break

                stdout, stderr = process.communicate()
                returncode = process.returncode

            except psutil.NoSuchProcess:
                stdout, stderr = process.communicate()
                returncode = process.returncode
        else:
            # Simple execution without memory monitoring
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode
            max_memory = 0

        end_time = time.time()
        execution_time = end_time - start_time

        return {
            "execution_time": execution_time,
            "max_memory_mb": max_memory / (1024 * 1024) if max_memory > 0 else 0,
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
        }

    def benchmark_startup_time(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark startup time for --version command."""
        print("Benchmarking startup time...")

        binary_times = []
        python_times = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")

            # Binary startup
            result = self.run_binary_command(["--version"])
            if result["returncode"] == 0:
                binary_times.append(result["execution_time"])

            # Python startup
            result = self.run_python_command(["--version"])
            if result["returncode"] == 0:
                python_times.append(result["execution_time"])

        return {
            "binary": {
                "times": binary_times,
                "mean": statistics.mean(binary_times),
                "median": statistics.median(binary_times),
                "stdev": statistics.stdev(binary_times) if len(binary_times) > 1 else 0,
                "min": min(binary_times),
                "max": max(binary_times),
            },
            "python": {
                "times": python_times,
                "mean": statistics.mean(python_times),
                "median": statistics.median(python_times),
                "stdev": statistics.stdev(python_times) if len(python_times) > 1 else 0,
                "min": min(python_times),
                "max": max(python_times),
            },
            "speedup": (
                statistics.mean(python_times) / statistics.mean(binary_times) if binary_times else 0
            ),
        }

    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage for various commands."""
        print("Benchmarking memory usage...")

        commands = [
            (["--version"], "version"),
            (["list-rule-packs"], "list_rule_packs"),
            (["--help"], "help"),
        ]

        results = {}

        for cmd_args, cmd_name in commands:
            print(f"  Testing {cmd_name}...")

            binary_result = self.run_binary_command(cmd_args, measure_memory=True)
            python_result = self.run_python_command(cmd_args, measure_memory=True)

            results[cmd_name] = {
                "binary_memory_mb": binary_result["max_memory_mb"],
                "python_memory_mb": python_result["max_memory_mb"],
                "memory_ratio": (
                    python_result["max_memory_mb"] / binary_result["max_memory_mb"]
                    if binary_result["max_memory_mb"] > 0
                    else 0
                ),
            }

        return results

    def benchmark_terraform_processing(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark Terraform file processing performance."""
        print("Benchmarking Terraform processing...")

        # Create test Terraform files of different sizes
        test_files = self._create_test_terraform_files()

        results = {}

        for file_name, file_path in test_files.items():
            print(f"  Testing {file_name}...")

            binary_times = []
            python_times = []

            for _ in range(iterations):
                # Binary processing
                result = self.run_binary_command(
                    [
                        "scan",
                        "--rule-pack",
                        "aws-security",
                        "--terraform",
                        str(file_path),
                        "--output-format",
                        "json",
                    ],
                    measure_memory=True,
                )

                if result["returncode"] in [0, 1]:  # 0 = pass, 1 = violations
                    binary_times.append(result["execution_time"])

                # Python processing
                result = self.run_python_command(
                    [
                        "scan",
                        "--rule-pack",
                        "aws-security",
                        "--terraform",
                        str(file_path),
                        "--output-format",
                        "json",
                    ],
                    measure_memory=True,
                )

                if result["returncode"] in [0, 1]:
                    python_times.append(result["execution_time"])

            if binary_times and python_times:
                results[file_name] = {
                    "binary_mean": statistics.mean(binary_times),
                    "python_mean": statistics.mean(python_times),
                    "speedup": statistics.mean(python_times) / statistics.mean(binary_times),
                    "file_size_kb": file_path.stat().st_size / 1024,
                }

        # Clean up test files
        for _, file_path in test_files.items():
            file_path.unlink()

        return results

    def _create_test_terraform_files(self) -> Dict[str, Path]:
        """Create test Terraform files of different sizes."""
        test_files = {}

        # Small file (1-2 KB)
        small_content = """
resource "aws_instance" "small_test" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name = "small-test"
    Environment = "test"
  }
}
"""

        # Medium file (10-20 KB)
        medium_content = small_content
        for i in range(20):
            medium_content += f"""
resource "aws_instance" "medium_test_{i}" {{
  ami           = "ami-{12345678 + i}"
  instance_type = "t3.small"

  tags = {{
    Name = "medium-test-{i}"
    Environment = "test"
    Index = "{i}"
  }}
}}
"""

        # Large file (100+ KB)
        large_content = medium_content
        for i in range(100):
            large_content += f"""
resource "aws_instance" "large_test_{i}" {{
  ami           = "ami-{87654321 + i}"
  instance_type = "t3.medium"

  tags = {{
    Name = "large-test-{i}"
    Environment = "production"
    Index = "{i}"
    Description = "This is a test instance number {i} for performance benchmarking"
  }}

  root_block_device {{
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }}
}}
"""

        # Write files
        for name, content in [
            ("small", small_content),
            ("medium", medium_content),
            ("large", large_content),
        ]:
            temp_file = Path(tempfile.mktemp(suffix=f"_{name}.tf"))
            temp_file.write_text(content)
            test_files[name] = temp_file

        return test_files

    def benchmark_rule_pack_loading(self) -> Dict[str, Any]:
        """Benchmark rule pack loading performance."""
        print("Benchmarking rule pack loading...")

        # Test with different rule packs
        rule_packs = [
            "aws-security",
            "gcp-security",
            "azure-security",
            "multi-cloud-security",
        ]

        results = {}

        for rule_pack in rule_packs:
            print(f"  Testing {rule_pack}...")

            # Create a minimal Terraform file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
                f.write(
                    """
resource "aws_instance" "test" {
  ami = "ami-12345678"
  instance_type = "t3.micro"
}
"""
                )
                tf_file = f.name

            try:
                # Binary
                binary_result = self.run_binary_command(
                    [
                        "scan",
                        "--rule-pack",
                        rule_pack,
                        "--terraform",
                        tf_file,
                        "--output-format",
                        "json",
                    ]
                )

                # Python
                python_result = self.run_python_command(
                    [
                        "scan",
                        "--rule-pack",
                        rule_pack,
                        "--terraform",
                        tf_file,
                        "--output-format",
                        "json",
                    ]
                )

                if binary_result["returncode"] in [0, 1] and python_result["returncode"] in [0, 1]:
                    results[rule_pack] = {
                        "binary_time": binary_result["execution_time"],
                        "python_time": python_result["execution_time"],
                        "speedup": python_result["execution_time"]
                        / binary_result["execution_time"],
                    }

            finally:
                os.unlink(tf_file)

        return results

    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run the complete benchmark suite."""
        print("Starting comprehensive performance benchmark...")
        print(f"Binary path: {self.binary_path}")
        print(f"Python path: {self.python_path}")
        print()

        results = {
            "metadata": {
                "binary_path": self.binary_path,
                "python_path": self.python_path,
                "timestamp": time.time(),
                "system_info": {
                    "cpu_count": os.cpu_count(),
                    "memory_gb": psutil.virtual_memory().total / (1024**3),
                    "platform": sys.platform,
                },
            },
            "startup_time": self.benchmark_startup_time(),
            "memory_usage": self.benchmark_memory_usage(),
            "terraform_processing": self.benchmark_terraform_processing(),
            "rule_pack_loading": self.benchmark_rule_pack_loading(),
        }

        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable benchmark report."""
        report = []
        report.append("# Riveter Binary vs Python Performance Benchmark Report")
        report.append("")
        report.append(f"**Timestamp:** {time.ctime(results['metadata']['timestamp'])}")
        report.append(f"**Binary Path:** {results['metadata']['binary_path']}")
        report.append(f"**Python Path:** {results['metadata']['python_path']}")
        report.append("")

        # System info
        sys_info = results["metadata"]["system_info"]
        report.append("## System Information")
        report.append(f"- **CPU Cores:** {sys_info['cpu_count']}")
        report.append(f"- **Memory:** {sys_info['memory_gb']:.1f} GB")
        report.append(f"- **Platform:** {sys_info['platform']}")
        report.append("")

        # Startup time
        startup = results["startup_time"]
        report.append("## Startup Time Benchmark")
        report.append(f"- **Binary Mean:** {startup['binary']['mean']:.3f}s")
        report.append(f"- **Python Mean:** {startup['python']['mean']:.3f}s")
        report.append(f"- **Speedup:** {startup['speedup']:.1f}x faster")
        report.append("")

        # Memory usage
        memory = results["memory_usage"]
        report.append("## Memory Usage Benchmark")
        for cmd, data in memory.items():
            report.append(f"### {cmd.replace('_', ' ').title()}")
            report.append(f"- **Binary:** {data['binary_memory_mb']:.1f} MB")
            report.append(f"- **Python:** {data['python_memory_mb']:.1f} MB")
            if data["memory_ratio"] > 0:
                report.append(f"- **Ratio:** {data['memory_ratio']:.1f}x")
            report.append("")

        # Terraform processing
        tf_proc = results["terraform_processing"]
        report.append("## Terraform Processing Benchmark")
        for file_type, data in tf_proc.items():
            report.append(f"### {file_type.title()} File ({data['file_size_kb']:.1f} KB)")
            report.append(f"- **Binary Mean:** {data['binary_mean']:.3f}s")
            report.append(f"- **Python Mean:** {data['python_mean']:.3f}s")
            report.append(f"- **Speedup:** {data['speedup']:.1f}x faster")
            report.append("")

        # Rule pack loading
        rule_packs = results["rule_pack_loading"]
        report.append("## Rule Pack Loading Benchmark")
        for pack, data in rule_packs.items():
            report.append(f"### {pack}")
            report.append(f"- **Binary:** {data['binary_time']:.3f}s")
            report.append(f"- **Python:** {data['python_time']:.3f}s")
            report.append(f"- **Speedup:** {data['speedup']:.1f}x faster")
            report.append("")

        return "\n".join(report)


def main():
    """Main function to run benchmarks."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark Riveter binary vs Python performance")
    parser.add_argument("--binary-path", help="Path to Riveter binary")
    parser.add_argument("--python-path", help="Path to Python executable")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--report", help="Output file for human-readable report (Markdown)")

    args = parser.parse_args()

    try:
        benchmark = PerformanceBenchmark(binary_path=args.binary_path, python_path=args.python_path)

        results = benchmark.run_full_benchmark()

        # Save JSON results
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")

        # Generate and save report
        report = benchmark.generate_report(results)
        if args.report:
            with open(args.report, "w") as f:
                f.write(report)
            print(f"Report saved to {args.report}")
        else:
            print("\n" + report)

    except Exception as e:
        print(f"Benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
