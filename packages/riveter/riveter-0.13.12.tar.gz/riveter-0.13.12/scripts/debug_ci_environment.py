#!/usr/bin/env python3
"""
Debug script to help identify CI vs local environment differences.
Run this in both environments to compare outputs.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return f"✅ {description}: {result.stdout.strip()}"
    except Exception as e:
        return f"❌ {description}: {str(e)}"


def main():
    print("🔍 CI Environment Debug Information")
    print("=" * 50)

    # Python environment
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")

    # Git environment
    print("\n📋 Git Configuration:")
    git_checks = [
        ("git --version", "Git version"),
        ("git config --global user.name", "Global user name"),
        ("git config --global user.email", "Global user email"),
        ("git config --global init.defaultBranch", "Default branch"),
        ("git branch --show-current", "Current branch"),
        ("git remote -v", "Git remotes"),
        ("git status --porcelain", "Git status"),
    ]

    for cmd, desc in git_checks:
        print(run_command(cmd, desc))

    # Environment variables
    print("\n🌍 Environment Variables:")
    env_vars = [
        "CI",
        "GITHUB_ACTIONS",
        "GITHUB_TOKEN",
        "GITHUB_REPOSITORY",
        "GITHUB_ACTOR",
        "GITHUB_REF_NAME",
        "RUNNER_OS",
        "HOME",
    ]

    for var in env_vars:
        value = os.environ.get(var, "Not set")
        # Mask sensitive values
        if "TOKEN" in var and value != "Not set":
            value = f"{value[:10]}..." if len(value) > 10 else "***"
        print(f"  {var}: {value}")

    # File system checks
    print("\n📁 File System:")
    important_files = [
        "pyproject.toml",
        "CHANGELOG.md",
        "README.md",
        ".git/config",
        "scripts/workflow_error_handler.py",
    ]

    for file_path in important_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}: exists")
        else:
            print(f"  ❌ {file_path}: missing")

    # Test-specific checks
    print("\n🧪 Test Environment:")
    test_checks = [
        ("python -c 'import tempfile; print(tempfile.gettempdir())'", "Temp directory"),
        ("python -c 'import os; print(os.access(\"/tmp\", os.W_OK))'", "Temp dir writable"),
        (
            "python -c 'import subprocess; "
            'print(subprocess.run(["git", "init", "--help"], '
            "capture_output=True).returncode == 0)'",
            "Git init available",
        ),
    ]

    for cmd, desc in test_checks:
        print(run_command(cmd, desc))

    print("\n" + "=" * 50)
    print("🏁 Debug information complete")


if __name__ == "__main__":
    main()
