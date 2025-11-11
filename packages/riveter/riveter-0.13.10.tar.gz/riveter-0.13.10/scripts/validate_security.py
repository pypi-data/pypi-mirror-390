#!/usr/bin/env python3
"""
Security validation script for the automated release workflow.

This script validates the security configuration of the repository and workflow
to ensure all security measures are properly configured.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class SecurityValidator:
    """Validates security configuration for the release workflow."""

    def __init__(self, repo_path: str = "."):
        """Initialize the security validator.

        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path)
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks: List[str] = []

    def validate_workflow_permissions(self) -> bool:
        """Validate GitHub Actions workflow permissions."""
        workflow_file = self.repo_path / ".github" / "workflows" / "release.yml"

        if not workflow_file.exists():
            self.issues.append("Release workflow file not found")
            return False

        try:
            with open(workflow_file, "r") as f:
                content = f.read()

            # Check for required permissions
            required_permissions = ["contents: write", "id-token: write", "actions: read"]
            missing_permissions = []

            for perm in required_permissions:
                if perm not in content:
                    missing_permissions.append(perm)

            if missing_permissions:
                self.issues.append(
                    f"Missing workflow permissions: {', '.join(missing_permissions)}"
                )
                return False

            self.passed_checks.append("Workflow permissions configured correctly")
            return True

        except Exception as e:
            self.issues.append(f"Error reading workflow file: {e}")
            return False

    def validate_secret_usage(self) -> bool:
        """Validate proper secret usage in workflow."""
        workflow_file = self.repo_path / ".github" / "workflows" / "release.yml"

        if not workflow_file.exists():
            return False

        try:
            with open(workflow_file, "r") as f:
                content = f.read()

            # Check for required secrets
            if "secrets.PYPI_API_TOKEN" not in content:
                self.issues.append("PYPI_API_TOKEN secret not referenced in workflow")
                return False

            if "secrets.GITHUB_TOKEN" not in content:
                self.issues.append("GITHUB_TOKEN secret not referenced in workflow")
                return False

            # Check for secure secret handling patterns
            secure_patterns = [
                r"env:\s*\n\s*PYPI_API_TOKEN:\s*\$\{\{\s*secrets\.PYPI_API_TOKEN\s*\}\}",
                r'TWINE_PASSWORD="\$\{PYPI_API_TOKEN\}"',
                r"unset\s+TWINE_PASSWORD",
                r"unset\s+PYPI_API_TOKEN",
            ]

            missing_patterns = []
            for pattern in secure_patterns:
                if not re.search(pattern, content, re.MULTILINE):
                    missing_patterns.append("Secure credential handling pattern")

            if missing_patterns:
                self.warnings.append("Some secure credential handling patterns may be missing")

            # Check for insecure patterns (secrets in command line)
            insecure_patterns = [
                r"--password\s+\$\{\{\s*secrets\.",
                r"--token\s+\$\{\{\s*secrets\.",
            ]

            for pattern in insecure_patterns:
                if re.search(pattern, content):
                    self.issues.append("Insecure secret usage detected (secrets in command line)")
                    return False

            self.passed_checks.append("Secret usage patterns are secure")
            return True

        except Exception as e:
            self.issues.append(f"Error validating secret usage: {e}")
            return False

    def validate_security_documentation(self) -> bool:
        """Validate security documentation exists and is complete."""
        docs_path = self.repo_path / "docs"

        required_docs = ["SECURITY_SETUP.md", "SECURITY_CHECKLIST.md"]

        missing_docs = []
        for doc in required_docs:
            doc_path = docs_path / doc
            if not doc_path.exists():
                missing_docs.append(doc)

        if missing_docs:
            self.issues.append(f"Missing security documentation: {', '.join(missing_docs)}")
            return False

        # Check documentation content
        try:
            security_setup = docs_path / "SECURITY_SETUP.md"
            with open(security_setup, "r") as f:
                setup_content = f.read()

            required_sections = [
                "Required Repository Secrets",
                "PYPI_API_TOKEN",
                "GITHUB_TOKEN",
                "Secret Validation",
                "Security Best Practices",
                "Troubleshooting",
            ]

            missing_sections = []
            for section in required_sections:
                if section not in setup_content:
                    missing_sections.append(section)

            if missing_sections:
                self.warnings.append(
                    f"Security setup documentation may be incomplete: {', '.join(missing_sections)}"
                )

            self.passed_checks.append("Security documentation exists and appears complete")
            return True

        except Exception as e:
            self.issues.append(f"Error validating security documentation: {e}")
            return False

    def validate_pyproject_security(self) -> bool:
        """Validate pyproject.toml security configuration."""
        pyproject_file = self.repo_path / "pyproject.toml"

        if not pyproject_file.exists():
            self.issues.append("pyproject.toml not found")
            return False

        try:
            with open(pyproject_file, "r") as f:
                content = f.read()

            # Check for project name (should be 'riveter')
            if 'name = "riveter"' not in content:
                self.warnings.append("Project name in pyproject.toml should be 'riveter'")

            # Check for version field
            if not re.search(r'version\s*=\s*"[\d\.]+"', content):
                self.issues.append("Version field not found or invalid in pyproject.toml")
                return False

            self.passed_checks.append("pyproject.toml configuration is valid")
            return True

        except Exception as e:
            self.issues.append(f"Error validating pyproject.toml: {e}")
            return False

    def validate_environment_security(self) -> bool:
        """Validate environment security configuration."""
        gitignore_file = self.repo_path / ".gitignore"
        if gitignore_file.exists():
            try:
                with open(gitignore_file, "r") as f:
                    gitignore_content = f.read()

                # Check if common sensitive patterns are ignored
                recommended_ignores = [".env", "*.key", "*.pem"]
                missing_ignores = []

                for pattern in recommended_ignores:
                    if pattern not in gitignore_content:
                        missing_ignores.append(pattern)

                if missing_ignores:
                    self.warnings.append(
                        f"Consider adding to .gitignore: {', '.join(missing_ignores)}"
                    )

                self.passed_checks.append("Environment security configuration checked")
                return True

            except Exception as e:
                self.warnings.append(f"Error reading .gitignore: {e}")
                return True
        else:
            self.warnings.append(".gitignore file not found")
            return True

    def check_for_hardcoded_secrets(self) -> bool:
        """Check for hardcoded secrets in the repository."""
        # Patterns that might indicate hardcoded secrets (excluding template/example patterns)
        secret_patterns = [
            r"pypi-[A-Za-z0-9_-]{100,}",  # PyPI tokens (but not in comments or examples)
            r"ghp_[A-Za-z0-9]{36}",  # GitHub personal access tokens
            r"ghs_[A-Za-z0-9]{36}",  # GitHub app tokens
            r'password\s*=\s*["\'][^"\']{8,}["\']',  # Hardcoded passwords (8+ chars)
            r'token\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']',  # Real tokens
        ]

        # Files to check
        files_to_check = [
            ".github/workflows/release.yml",
            "pyproject.toml",
            "README.md",
            "scripts/*.py",
        ]

        found_secrets = []

        for file_pattern in files_to_check:
            if "*" in file_pattern:
                # Handle glob patterns
                from glob import glob

                files = glob(str(self.repo_path / file_pattern))
            else:
                files = [self.repo_path / file_pattern]

            for file_path in files:
                file_path = Path(file_path)
                if not file_path.exists():
                    continue

                try:
                    with open(file_path, "r") as f:
                        content = f.read()

                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            # Filter out obvious test/example values and template patterns
                            real_matches = []
                            for match in matches:
                                # Skip if it's in a comment or documentation
                                if any(
                                    indicator in content.lower()
                                    for indicator in [
                                        "# " + match.lower(),
                                        "example",
                                        "test",
                                        "dummy",
                                        "fake",
                                        "sample",
                                        "template",
                                        "placeholder",
                                        "your_token_here",
                                        "secrets.",
                                        "${{",
                                        "env:",
                                        "format:",
                                        "pypi-AgEI",
                                    ]
                                ):
                                    continue
                                real_matches.append(match)

                            if real_matches:
                                found_secrets.append(f"{file_path.name}: potential secret pattern")

                except Exception as e:
                    self.warnings.append(f"Error checking {file_path} for secrets: {e}")

        if found_secrets:
            self.issues.append(f"Potential hardcoded secrets found: {', '.join(found_secrets)}")
            return False

        self.passed_checks.append("No hardcoded secrets detected")
        return True

    def run_validation(self) -> Tuple[bool, Dict[str, List[str]]]:
        """Run all security validations.

        Returns:
            Tuple of (success, results) where results contains issues, warnings, and passed checks
        """
        print("🔍 Running security validation...")
        print()

        # Run all validation checks
        checks = [
            ("Workflow Permissions", self.validate_workflow_permissions),
            ("Secret Usage", self.validate_secret_usage),
            ("Security Documentation", self.validate_security_documentation),
            ("Project Configuration", self.validate_pyproject_security),
            ("Environment Security", self.validate_environment_security),
            ("Hardcoded Secrets Check", self.check_for_hardcoded_secrets),
        ]

        all_passed = True

        for check_name, check_func in checks:
            print(f"🔍 {check_name}...", end=" ")
            try:
                result = check_func()
                if result:
                    print("✅")
                else:
                    print("❌")
                    all_passed = False
            except Exception as e:
                print(f"💥 Error: {e}")
                self.issues.append(f"{check_name}: {e}")
                all_passed = False

        print()

        # Print results
        if self.passed_checks:
            print("✅ Passed Checks:")
            for check in self.passed_checks:
                print(f"   • {check}")
            print()

        if self.warnings:
            print("⚠️ Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()

        if self.issues:
            print("❌ Issues Found:")
            for issue in self.issues:
                print(f"   • {issue}")
            print()

        results = {
            "issues": self.issues,
            "warnings": self.warnings,
            "passed_checks": self.passed_checks,
        }

        return all_passed, results


def main():
    """Main function to run security validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate security configuration for release workflow"
    )
    parser.add_argument("--repo-path", default=".", help="Path to repository root")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument(
        "--fail-on-warnings", action="store_true", help="Fail if warnings are found"
    )

    args = parser.parse_args()

    validator = SecurityValidator(args.repo_path)
    success, results = validator.run_validation()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if success and not results["warnings"]:
            print("🎉 All security validations passed!")
        elif success and results["warnings"]:
            print("✅ Security validations passed with warnings")
            if args.fail_on_warnings:
                success = False
        else:
            print("❌ Security validation failed")

        print()
        print("📖 For setup instructions, see: docs/SECURITY_SETUP.md")
        print("📋 For security checklist, see: docs/SECURITY_CHECKLIST.md")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
