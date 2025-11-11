#!/usr/bin/env python3
"""
Comprehensive error handling and validation for the release workflow.

This script provides enhanced error handling, validation, and retry logic
for the automated release workflow.
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


class ErrorSeverity(Enum):
    """Error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RetryStrategy(Enum):
    """Retry strategy types."""

    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    passed: bool
    message: str
    severity: ErrorSeverity
    details: Optional[Dict[str, Any]] = None


@dataclass
class RetryConfig:
    """Configuration for retry operations."""

    max_attempts: int = 3
    base_delay: float = 1.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    backoff_multiplier: float = 2.0


class WorkflowErrorHandler:
    """Enhanced error handling for release workflow operations."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize error handler.

        Args:
            project_root: Path to project root directory.
        """
        self.project_root = project_root or Path.cwd()
        self.validation_results: List[ValidationResult] = []

    def log_error(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log error with GitHub Actions formatting.

        Args:
            message: Error message.
            severity: Error severity level.
            details: Optional additional details.
        """
        # Format for GitHub Actions
        if severity == ErrorSeverity.ERROR:
            print(f"::error::{message}")
        elif severity == ErrorSeverity.WARNING:
            print(f"::warning::{message}")
        elif severity == ErrorSeverity.CRITICAL:
            print(f"::error::{message}")
            if details:
                print(f"::error::Details: {json.dumps(details, indent=2)}")
        else:
            print(f"::notice::{message}")

        # Also log to stderr for debugging
        print(f"[{severity.value.upper()}] {message}", file=sys.stderr)
        if details:
            print(f"Details: {json.dumps(details, indent=2)}", file=sys.stderr)

    def validate_branch_permissions(self, required_branch: str = "main") -> ValidationResult:
        """Validate branch and user permissions.

        Args:
            required_branch: Required branch name for releases.

        Returns:
            ValidationResult with check outcome.
        """
        try:
            # Check current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            current_branch = result.stdout.strip()

            if current_branch != required_branch:
                return ValidationResult(
                    passed=False,
                    message=(
                        f"Release must be triggered from '{required_branch}' branch, "
                        f"currently on '{current_branch}'"
                    ),
                    severity=ErrorSeverity.CRITICAL,
                    details={"current_branch": current_branch, "required_branch": required_branch},
                )

            # Check if branch is up to date with remote
            try:
                subprocess.run(
                    ["git", "fetch", "origin", required_branch],
                    cwd=self.project_root,
                    capture_output=True,
                    check=True,
                )

                result = subprocess.run(
                    ["git", "rev-list", "--count", f"HEAD..origin/{required_branch}"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                behind_count = int(result.stdout.strip())
                if behind_count > 0:
                    return ValidationResult(
                        passed=False,
                        message=(
                            f"Local branch is {behind_count} commits behind "
                            f"origin/{required_branch}"
                        ),
                        severity=ErrorSeverity.ERROR,
                        details={"commits_behind": behind_count},
                    )

            except subprocess.CalledProcessError as e:
                self.log_error(f"Failed to check branch status: {e}", ErrorSeverity.WARNING)

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip():
                return ValidationResult(
                    passed=False,
                    message="Repository has uncommitted changes",
                    severity=ErrorSeverity.ERROR,
                    details={"uncommitted_files": result.stdout.strip().split("\n")},
                )

            return ValidationResult(
                passed=True,
                message=(
                    f"Branch validation passed: on {current_branch}, up to date, "
                    "no uncommitted changes"
                ),
                severity=ErrorSeverity.INFO,
            )

        except subprocess.CalledProcessError as e:
            return ValidationResult(
                passed=False,
                message=f"Git command failed during branch validation: {e}",
                severity=ErrorSeverity.CRITICAL,
                details={"git_error": str(e)},
            )

    def validate_secrets_and_permissions(self, dry_run: bool = False) -> ValidationResult:
        """Validate required secrets and permissions.

        Args:
            dry_run: Whether this is a dry run (skips some validations).

        Returns:
            ValidationResult with check outcome.
        """
        issues = []

        # Check GitHub token
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            issues.append("GITHUB_TOKEN environment variable not set")
        elif len(github_token) < 20:
            issues.append("GITHUB_TOKEN appears to be too short")

        # Check PyPI token (only if not dry run)
        if not dry_run:
            pypi_token = os.getenv("PYPI_API_TOKEN")
            if not pypi_token:
                issues.append("PYPI_API_TOKEN environment variable not set")
            elif not pypi_token.startswith("pypi-"):
                issues.append(
                    "PYPI_API_TOKEN does not have expected format (should start with 'pypi-')"
                )
            elif len(pypi_token) < 100:
                issues.append("PYPI_API_TOKEN appears to be too short")

        # Check repository context
        repo = os.getenv("GITHUB_REPOSITORY")
        if not repo:
            issues.append("GITHUB_REPOSITORY environment variable not set")

        actor = os.getenv("GITHUB_ACTOR")
        if not actor:
            issues.append("GITHUB_ACTOR environment variable not set")

        if issues:
            return ValidationResult(
                passed=False,
                message="Secret and permission validation failed",
                severity=ErrorSeverity.CRITICAL,
                details={"issues": issues},
            )

        return ValidationResult(
            passed=True,
            message="Secret and permission validation passed",
            severity=ErrorSeverity.INFO,
            details={"dry_run": dry_run},
        )

    def validate_project_structure(self) -> ValidationResult:
        """Validate project structure and required files.

        Returns:
            ValidationResult with check outcome.
        """
        required_files = ["pyproject.toml", "CHANGELOG.md", "README.md"]

        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            return ValidationResult(
                passed=False,
                message=f"Required files missing: {', '.join(missing_files)}",
                severity=ErrorSeverity.ERROR,
                details={"missing_files": missing_files},
            )

        # Validate pyproject.toml structure
        try:
            import tomllib

            with open(self.project_root / "pyproject.toml", "rb") as f:
                data = tomllib.load(f)

            required_fields = ["project.name", "project.version"]
            missing_fields = []

            for field in required_fields:
                keys = field.split(".")
                current = data
                try:
                    for key in keys:
                        current = current[key]
                except KeyError:
                    missing_fields.append(field)

            if missing_fields:
                return ValidationResult(
                    passed=False,
                    message=(
                        f"Required fields missing in pyproject.toml: "
                        f"{', '.join(missing_fields)}"
                    ),
                    severity=ErrorSeverity.ERROR,
                    details={"missing_fields": missing_fields},
                )

        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Failed to validate pyproject.toml: {e}",
                severity=ErrorSeverity.ERROR,
                details={"error": str(e)},
            )

        return ValidationResult(
            passed=True, message="Project structure validation passed", severity=ErrorSeverity.INFO
        )

    def retry_with_backoff(
        self, operation, retry_config: RetryConfig, operation_name: str
    ) -> Tuple[bool, Any, Optional[Exception]]:
        """Execute operation with retry logic and backoff.

        Args:
            operation: Callable to execute.
            retry_config: Retry configuration.
            operation_name: Name of operation for logging.

        Returns:
            Tuple of (success, result, last_exception).
        """
        last_exception = None

        for attempt in range(1, retry_config.max_attempts + 1):
            try:
                self.log_error(
                    f"Executing {operation_name} (attempt {attempt}/{retry_config.max_attempts})",
                    ErrorSeverity.INFO,
                )

                result = operation()
                self.log_error(
                    f"{operation_name} succeeded on attempt {attempt}", ErrorSeverity.INFO
                )
                return True, result, None

            except Exception as e:
                last_exception = e
                self.log_error(
                    f"{operation_name} failed on attempt {attempt}: {e}",
                    ErrorSeverity.WARNING,
                    {"attempt": attempt, "max_attempts": retry_config.max_attempts},
                )

                if attempt < retry_config.max_attempts:
                    # Calculate delay based on strategy
                    if retry_config.strategy == RetryStrategy.LINEAR:
                        delay = retry_config.base_delay * attempt
                    elif retry_config.strategy == RetryStrategy.EXPONENTIAL:
                        delay = retry_config.base_delay * (
                            retry_config.backoff_multiplier ** (attempt - 1)
                        )
                    else:
                        delay = 0

                    if delay > 0:
                        self.log_error(
                            f"Waiting {delay:.1f} seconds before retry...", ErrorSeverity.INFO
                        )
                        time.sleep(delay)

        self.log_error(
            f"{operation_name} failed after {retry_config.max_attempts} attempts",
            ErrorSeverity.ERROR,
            {"last_error": str(last_exception)},
        )

        return False, None, last_exception

    def validate_network_connectivity(self) -> ValidationResult:
        """Validate network connectivity to required services.

        Returns:
            ValidationResult with check outcome.
        """
        services = [
            ("GitHub API", "https://api.github.com"),
            ("PyPI", "https://pypi.org"),
            ("PyPI API", "https://upload.pypi.org"),
        ]

        failed_services = []

        for service_name, url in services:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code >= 400:
                    failed_services.append(f"{service_name}: HTTP {response.status_code}")
            except requests.RequestException as e:
                failed_services.append(f"{service_name}: {str(e)}")

        if failed_services:
            return ValidationResult(
                passed=False,
                message="Network connectivity issues detected",
                severity=ErrorSeverity.WARNING,
                details={"failed_services": failed_services},
            )

        return ValidationResult(
            passed=True,
            message="Network connectivity validation passed",
            severity=ErrorSeverity.INFO,
        )

    def validate_tag_uniqueness(self, tag: str) -> ValidationResult:
        """Validate that a git tag doesn't already exist.

        Args:
            tag: Git tag to check.

        Returns:
            ValidationResult with check outcome.
        """
        try:
            # Check local tags
            result = subprocess.run(
                ["git", "tag", "-l", tag],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            if result.stdout.strip():
                return ValidationResult(
                    passed=False,
                    message=f"Git tag '{tag}' already exists locally",
                    severity=ErrorSeverity.CRITICAL,
                    details={"tag": tag, "location": "local"},
                )

            # Check remote tags
            try:
                subprocess.run(
                    ["git", "fetch", "--tags"],
                    cwd=self.project_root,
                    capture_output=True,
                    check=True,
                    timeout=30,
                )

                result = subprocess.run(
                    ["git", "tag", "-l", tag],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )

                if result.stdout.strip():
                    return ValidationResult(
                        passed=False,
                        message=f"Git tag '{tag}' already exists on remote",
                        severity=ErrorSeverity.CRITICAL,
                        details={"tag": tag, "location": "remote"},
                    )

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                self.log_error("Failed to fetch remote tags for validation", ErrorSeverity.WARNING)

            return ValidationResult(
                passed=True,
                message=f"Tag '{tag}' is unique and available",
                severity=ErrorSeverity.INFO,
                details={"tag": tag},
            )

        except subprocess.TimeoutExpired:
            return ValidationResult(
                passed=False,
                message="Git command timeout while validating tag uniqueness",
                severity=ErrorSeverity.ERROR,
                details={"error_type": "timeout"},
            )
        except subprocess.CalledProcessError as e:
            return ValidationResult(
                passed=False,
                message=f"Failed to validate tag uniqueness: {e}",
                severity=ErrorSeverity.ERROR,
                details={"git_error": str(e)},
            )

    def run_comprehensive_validation(self, tag: str, dry_run: bool = False) -> bool:
        """Run all validation checks.

        Args:
            tag: Git tag to validate.
            dry_run: Whether this is a dry run.

        Returns:
            True if all validations pass, False otherwise.
        """
        print("🔍 Running comprehensive pre-release validation...")

        validations = [
            ("Branch and Permissions", lambda: self.validate_branch_permissions()),
            ("Secrets and Permissions", lambda: self.validate_secrets_and_permissions(dry_run)),
            ("Project Structure", lambda: self.validate_project_structure()),
            ("Network Connectivity", lambda: self.validate_network_connectivity()),
            ("Tag Uniqueness", lambda: self.validate_tag_uniqueness(tag)),
        ]

        all_passed = True

        for validation_name, validation_func in validations:
            print(f"  Checking {validation_name}...")
            result = validation_func()
            self.validation_results.append(result)

            if result.passed:
                print(f"  ✅ {validation_name}: {result.message}")
            else:
                print(f"  ❌ {validation_name}: {result.message}")
                if result.details:
                    print(f"     Details: {json.dumps(result.details, indent=6)}")
                all_passed = False

        summary_msg = "✅ All checks passed" if all_passed else "❌ Some checks failed"
        print(f"\n📊 Validation Summary: {summary_msg}")

        return all_passed

    def create_rollback_documentation(self, version: str, tag: str) -> str:
        """Create rollback documentation for failed releases.

        Args:
            version: Version that failed to release.
            tag: Git tag that was created.

        Returns:
            Rollback documentation as markdown.
        """
        rollback_doc = f"""# Release Rollback Guide - {version}

## Overview
This document provides instructions for rolling back a failed release of version {version}.

## Rollback Steps

### 1. Remove Git Tag (if created)
```bash
# Remove local tag
git tag -d {tag}

# Remove remote tag (if pushed)
git push origin --delete {tag}
```

### 2. Revert Version Changes
```bash
# Reset pyproject.toml to previous version
git checkout HEAD~1 -- pyproject.toml

# Or manually edit pyproject.toml to restore previous version
```

### 3. Revert CLI Version Changes
```bash
# Reset CLI module to previous state
git checkout HEAD~1 -- src/riveter/cli.py

# Or use version sync script rollback
python scripts/sync_versions.py --rollback
```

### 4. Revert Homebrew Formula Changes
```bash
# If formula is in separate repository
cd ../homebrew-riveter
git checkout HEAD~1 -- Formula/riveter.rb

# Or use version sync script
cd ../riveter
python scripts/sync_versions.py --rollback
```

### 5. Revert Changelog Changes
```bash
# Reset CHANGELOG.md to previous state
git checkout HEAD~1 -- CHANGELOG.md

# Or manually restore the [Unreleased] section
```

### 6. Clean Up Build Artifacts
```bash
# Remove build artifacts
rm -rf dist/ build/ *.egg-info/

# Clean up any temporary files
git clean -fd

# Remove version sync backups
rm -rf .version_sync_backup/
```

### 7. PyPI Cleanup (if package was published)
⚠️ **Note**: PyPI does not allow deleting published packages. If the package was
successfully published to PyPI, you cannot remove it. Instead:

- Publish a new patch version with fixes
- Mark the problematic version as yanked (if critical issues exist)
- Update documentation to note the issue

```bash
# To yank a problematic version (if necessary)
twine upload --repository pypi --skip-existing dist/*
# Then contact PyPI support if yanking is needed
```

### 8. GitHub Release Cleanup (if created)
```bash
# Delete the GitHub release via API
gh release delete {tag} --yes

# Or delete via web interface:
# https://github.com/{os.getenv('GITHUB_REPOSITORY', 'owner/repo')}/releases
```

### 9. Homebrew Tap Cleanup (if updated)
```bash
# If Homebrew formula was updated, revert it
cd ../homebrew-riveter
git reset --hard HEAD~1
git push --force-with-lease origin main

# Or manually edit Formula/riveter.rb to restore previous version
```

### 10. Verify Rollback
```bash
# Check current version
grep version pyproject.toml

# Check CLI version consistency
python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

# Check git tags
git tag -l | grep {version}

# Check git status
git status

# Validate version consistency
python scripts/sync_versions.py --validate
```

## Automated Rollback

Use the automated rollback script for faster recovery:

```bash
# Automated version synchronization rollback
python scripts/sync_versions.py --rollback

# Automated Homebrew error recovery
python scripts/homebrew_error_recovery.py --recover

# Comprehensive workflow error recovery
python scripts/workflow_error_handler.py --create-rollback-doc {version} --tag {tag}
```

## Specific Error Recovery

### Version Synchronization Failures
```bash
# Check version consistency
python scripts/sync_versions.py --validate --debug

# Manual version sync
python scripts/sync_versions.py --sync

# Rollback version changes
python scripts/sync_versions.py --rollback
```

### Homebrew Installation Failures
```bash
# Diagnose Homebrew errors
python scripts/homebrew_error_recovery.py --diagnose error.log --recover

# Manual Homebrew cleanup
brew untap scottryanhoward/homebrew-riveter
brew cleanup --prune=all
brew tap scottryanhoward/homebrew-riveter
```

### PyPI Publication Failures
```bash
# Check PyPI token
echo $PYPI_API_TOKEN | cut -c1-10

# Validate package before upload
twine check dist/*

# Test upload to TestPyPI first
twine upload --repository testpypi dist/*
```

## Prevention for Next Release

1. **Run dry-run first**: Always test with `dry_run: true`
2. **Check all validations**: Ensure all pre-release checks pass
3. **Review changes**: Manually review version and changelog updates
4. **Test locally**: Build and test packages locally before release
5. **Validate version sync**: Run `python scripts/sync_versions.py --validate`
6. **Test Homebrew formula**: Run `brew audit --strict riveter`
7. **Check network connectivity**: Ensure stable internet connection
8. **Verify secrets**: Ensure all required tokens are valid and have correct permissions

## Troubleshooting Common Issues

### Issue: Version Mismatch
**Symptoms**: Binary version doesn't match formula version
**Solution**:
```bash
python scripts/sync_versions.py --sync
python scripts/sync_versions.py --validate
```

### Issue: Homebrew Tap Installation Fails
**Symptoms**: `brew tap` command fails with exit code 1
**Solution**:
```bash
brew untap scottryanhoward/homebrew-riveter
brew update
brew tap scottryanhoward/homebrew-riveter
```

### Issue: Formula Audit Fails
**Symptoms**: `brew audit` command fails
**Solution**:
```bash
# Check formula syntax
ruby -c Formula/riveter.rb

# Validate URLs and checksums
python scripts/sync_versions.py --update-formula
```

### Issue: PyPI Upload Fails
**Symptoms**: `twine upload` fails with authentication error
**Solution**:
```bash
# Check token format
echo $PYPI_API_TOKEN | grep "^pypi-"

# Test with TestPyPI first
twine upload --repository testpypi dist/*
```

## Emergency Contacts

- Repository maintainers: Check CODEOWNERS file
- GitHub repository: https://github.com/{os.getenv('GITHUB_REPOSITORY', 'owner/repo')}
- Issues: https://github.com/{os.getenv('GITHUB_REPOSITORY', 'owner/repo')}/issues
- Homebrew tap: https://github.com/ScottRyanHoward/homebrew-riveter

## Recovery Verification Checklist

- [ ] Git tag removed (local and remote)
- [ ] pyproject.toml version reverted
- [ ] CLI version reverted
- [ ] Homebrew formula reverted (if applicable)
- [ ] Changelog reverted
- [ ] Build artifacts cleaned up
- [ ] Version consistency validated
- [ ] Git status clean
- [ ] No uncommitted changes
- [ ] All tests passing

---
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}
Workflow run: {os.getenv('GITHUB_RUN_ID', 'unknown')}
Recovery tools: sync_versions.py, homebrew_error_recovery.py, workflow_error_handler.py
"""
        return rollback_doc

    def save_rollback_documentation(self, version: str, tag: str) -> Path:
        """Save rollback documentation to file.

        Args:
            version: Version that failed to release.
            tag: Git tag that was created.

        Returns:
            Path to saved rollback documentation.
        """
        rollback_doc = self.create_rollback_documentation(version, tag)

        # Create rollback directory if it doesn't exist
        rollback_dir = self.project_root / ".github" / "rollback"
        rollback_dir.mkdir(parents=True, exist_ok=True)

        # Save rollback documentation
        rollback_file = rollback_dir / f"rollback-{version}-{int(time.time())}.md"
        rollback_file.write_text(rollback_doc, encoding="utf-8")

        print(f"📝 Rollback documentation saved to: {rollback_file}")

        return rollback_file


def main():
    """Main entry point for error handler script."""
    import argparse

    parser = argparse.ArgumentParser(description="Release workflow error handler and validator")
    parser.add_argument("--validate", action="store_true", help="Run comprehensive validation")
    parser.add_argument("--tag", required=True, help="Git tag to validate/create")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--create-rollback-doc", help="Create rollback documentation for version")
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    handler = WorkflowErrorHandler(args.project_root)

    if args.validate:
        success = handler.run_comprehensive_validation(args.tag, args.dry_run)
        sys.exit(0 if success else 1)

    if args.create_rollback_doc:
        handler.save_rollback_documentation(args.create_rollback_doc, args.tag)
        sys.exit(0)

    print("No action specified. Use --validate or --create-rollback-doc")
    sys.exit(1)


if __name__ == "__main__":
    main()
