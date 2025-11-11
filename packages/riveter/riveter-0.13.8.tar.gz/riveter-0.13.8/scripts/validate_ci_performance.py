#!/usr/bin/env python3
"""
CI/CD Performance Validation Script

This script validates that CI/CD workflows are optimized for performance
by checking for proper caching configurations and parallel execution.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


class CIPerformanceValidator:
    """Validates CI/CD performance optimizations."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.workflows_dir = project_root / ".github" / "workflows"
        self.issues: List[str] = []
        self.optimizations: List[str] = []

    def validate_all_workflows(self) -> bool:
        """Validate all workflow files for performance optimizations."""
        print("🔍 Validating CI/CD performance optimizations...")

        if not self.workflows_dir.exists():
            self.issues.append("No .github/workflows directory found")
            return False

        workflow_files = list(self.workflows_dir.glob("*.yml"))
        if not workflow_files:
            self.issues.append("No workflow files found")
            return False

        success = True
        for workflow_file in workflow_files:
            print(f"📋 Checking {workflow_file.name}...")
            if not self.validate_workflow_file(workflow_file):
                success = False

        return success

    def validate_workflow_file(self, workflow_file: Path) -> bool:
        """Validate a single workflow file."""
        try:
            with open(workflow_file, "r") as f:
                workflow = yaml.safe_load(f)
        except Exception as e:
            self.issues.append(f"{workflow_file.name}: Failed to parse YAML - {e}")
            return False

        workflow_name = workflow_file.stem
        success = True

        # Check for caching
        if not self.check_caching(workflow, workflow_name):
            success = False

        # Check for parallel execution
        if not self.check_parallel_execution(workflow, workflow_name):
            success = False

        # Check for matrix builds
        self.check_matrix_builds(workflow, workflow_name)

        # Check for dependency optimization
        self.check_dependency_optimization(workflow, workflow_name)

        return success

    def check_caching(self, workflow: Dict[str, Any], workflow_name: str) -> bool:
        """Check if workflow uses caching appropriately."""
        jobs = workflow.get("jobs", {})
        has_caching = False

        for job_name, job in jobs.items():
            steps = job.get("steps", [])
            for step in steps:
                if step.get("uses", "").startswith("actions/cache@"):
                    has_caching = True
                    cache_paths = step.get("with", {}).get("path", "")
                    if "pip" in str(cache_paths) or "cache" in str(cache_paths):
                        self.optimizations.append(f"{workflow_name}: {job_name} uses pip caching")
                    if "pytest" in str(cache_paths):
                        self.optimizations.append(
                            f"{workflow_name}: {job_name} uses pytest caching"
                        )
                    if "pyinstaller" in str(cache_paths):
                        self.optimizations.append(
                            f"{workflow_name}: {job_name} uses PyInstaller caching"
                        )

        # Some workflows might not need caching
        if not has_caching and workflow_name in ["test", "release", "release-binaries"]:
            self.issues.append(f"{workflow_name}: No caching configured")
            return False

        return True

    def check_parallel_execution(self, workflow: Dict[str, Any], workflow_name: str) -> bool:
        """Check if workflow uses parallel execution where appropriate."""
        jobs = workflow.get("jobs", {})

        for job_name, job in jobs.items():
            # Check for matrix builds
            if "strategy" in job and "matrix" in job["strategy"]:
                self.optimizations.append(
                    f"{workflow_name}: {job_name} uses matrix strategy for parallelization"
                )

            # Check for parallel test execution
            steps = job.get("steps", [])
            for step in steps:
                run_command = step.get("run", "")
                if "pytest" in run_command and "-n auto" in run_command:
                    self.optimizations.append(
                        f"{workflow_name}: {job_name} uses parallel pytest execution"
                    )

        return True

    def check_matrix_builds(self, workflow: Dict[str, Any], workflow_name: str) -> None:
        """Check for matrix build configurations."""
        jobs = workflow.get("jobs", {})

        for job_name, job in jobs.items():
            strategy = job.get("strategy", {})
            matrix = strategy.get("matrix", {})

            if matrix:
                # Check for OS matrix
                if "os" in matrix:
                    os_list = matrix["os"]
                    if isinstance(os_list, list) and len(os_list) > 1:
                        self.optimizations.append(
                            f"{workflow_name}: {job_name} tests multiple OS: {', '.join(os_list)}"
                        )

                # Check for Python version matrix
                if "python-version" in matrix:
                    py_versions = matrix["python-version"]
                    if isinstance(py_versions, list) and len(py_versions) > 1:
                        self.optimizations.append(
                            f"{workflow_name}: {job_name} tests multiple Python versions: {', '.join(py_versions)}"
                        )

    def check_dependency_optimization(self, workflow: Dict[str, Any], workflow_name: str) -> None:
        """Check for dependency installation optimizations."""
        jobs = workflow.get("jobs", {})

        for job_name, job in jobs.items():
            steps = job.get("steps", [])
            for step in steps:
                run_command = step.get("run", "")

                # Check for pip upgrade
                if "pip install --upgrade pip" in run_command:
                    self.optimizations.append(
                        f"{workflow_name}: {job_name} upgrades pip for better performance"
                    )

                # Check for development dependencies
                if "pip install -e" in run_command and "[dev]" in run_command:
                    self.optimizations.append(
                        f"{workflow_name}: {job_name} uses editable install with dev dependencies"
                    )

    def print_report(self) -> None:
        """Print the performance validation report."""
        print("\n" + "=" * 60)
        print("📊 CI/CD Performance Optimization Report")
        print("=" * 60)

        if self.optimizations:
            print(f"\n✅ Found {len(self.optimizations)} performance optimizations:")
            for opt in self.optimizations:
                print(f"  • {opt}")

        if self.issues:
            print(f"\n⚠️ Found {len(self.issues)} performance issues:")
            for issue in self.issues:
                print(f"  • {issue}")
        else:
            print("\n🎉 No performance issues found!")

        print(f"\n📈 Performance Score: {self.calculate_score()}/100")

    def calculate_score(self) -> int:
        """Calculate a performance score based on optimizations and issues."""
        base_score = 50
        optimization_points = min(len(self.optimizations) * 5, 40)
        issue_penalty = len(self.issues) * 10

        score = max(0, min(100, base_score + optimization_points - issue_penalty))
        return score


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate CI/CD performance optimizations")
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Path to project root directory"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    validator = CIPerformanceValidator(args.project_root)
    success = validator.validate_all_workflows()
    validator.print_report()

    if not success:
        print("\n❌ Performance validation failed")
        sys.exit(1)
    else:
        print("\n✅ Performance validation passed")


if __name__ == "__main__":
    main()
