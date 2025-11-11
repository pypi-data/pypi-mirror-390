#!/usr/bin/env python3
"""Pre-release validation script for Riveter.

This script performs comprehensive validation before any release to ensure:
1. Version consistency across all components
2. No critical issues that would prevent release
3. All distribution methods are properly configured
4. Documentation is up to date

Usage:
    python scripts/pre_release_validation.py
    python scripts/pre_release_validation.py --strict
    python scripts/pre_release_validation.py --fix-issues
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from riveter.version_validator import ValidationReport, ValidationSeverity, VersionValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class PreReleaseValidator:
    """Pre-release validation orchestrator."""

    def __init__(self, project_root: Path, strict: bool = False, fix_issues: bool = False):
        """Initialize pre-release validator.

        Args:
            project_root: Root directory of the project
            strict: If True, treat warnings as errors
            fix_issues: If True, attempt to fix issues automatically
        """
        self.project_root = project_root
        self.strict = strict
        self.fix_issues = fix_issues
        self.validator = VersionValidator(project_root, debug=False)

    def validate_for_release(self) -> bool:
        """Perform comprehensive pre-release validation.

        Returns:
            True if validation passes, False otherwise
        """
        logger.info("🚀 Starting pre-release validation...")

        try:
            # Perform comprehensive validation
            report = self.validator.validate_all_components()

            # Print validation report
            report_text = self.validator.generate_validation_report(report)
            print(f"\n{report_text}")

            # Check if validation passes
            if self._should_fail_validation(report):
                logger.error("❌ Pre-release validation failed")

                if self.fix_issues:
                    logger.info("🔧 Attempting to fix issues automatically...")
                    if self._attempt_fixes(report):
                        logger.info("✅ Issues fixed, re-running validation...")
                        return self.validate_for_release()
                    else:
                        logger.error("❌ Could not fix all issues automatically")
                        return False

                return False
            else:
                logger.info("✅ Pre-release validation passed")
                return True

        except Exception as e:
            logger.error(f"Pre-release validation failed with error: {e}")
            return False

    def _should_fail_validation(self, report: ValidationReport) -> bool:
        """Determine if validation should fail based on issues found.

        Args:
            report: ValidationReport to check

        Returns:
            True if validation should fail
        """
        # Always fail on critical or error issues
        critical_or_error = any(
            issue.severity in (ValidationSeverity.CRITICAL, ValidationSeverity.ERROR)
            for issue in report.issues
        )

        if critical_or_error:
            return True

        # In strict mode, also fail on warnings
        if self.strict:
            warnings = any(issue.severity == ValidationSeverity.WARNING for issue in report.issues)
            return warnings

        return False

    def _attempt_fixes(self, report: ValidationReport) -> bool:
        """Attempt to fix validation issues automatically.

        Args:
            report: ValidationReport containing issues to fix

        Returns:
            True if all fixable issues were resolved
        """
        logger.info("🔧 Attempting automatic fixes...")

        fixed_count = 0
        total_fixable = 0

        for issue in report.issues:
            if self._is_fixable_issue(issue):
                total_fixable += 1
                if self._fix_issue(issue):
                    fixed_count += 1
                    logger.info(f"✅ Fixed: {issue.component} - {issue.message}")
                else:
                    logger.warning(f"❌ Could not fix: {issue.component} - {issue.message}")

        logger.info(f"Fixed {fixed_count}/{total_fixable} fixable issues")
        return fixed_count == total_fixable and total_fixable > 0

    def _is_fixable_issue(self, issue) -> bool:
        """Check if an issue can be fixed automatically.

        Args:
            issue: ValidationIssue to check

        Returns:
            True if issue can be fixed automatically
        """
        # Define fixable issue patterns
        fixable_patterns = [
            "version differs from pyproject.toml",
            "hardcoded version",
            "missing version field",
        ]

        return any(pattern in issue.message.lower() for pattern in fixable_patterns)

    def _fix_issue(self, issue) -> bool:
        """Attempt to fix a specific validation issue.

        Args:
            issue: ValidationIssue to fix

        Returns:
            True if issue was fixed successfully
        """
        try:
            if "homebrew_formula" in issue.component and "version differs" in issue.message:
                return self._fix_formula_version(issue)
            elif "hardcoded version" in issue.message:
                return self._fix_hardcoded_version(issue)
            else:
                logger.debug(f"No automatic fix available for: {issue.message}")
                return False

        except Exception as e:
            logger.error(f"Error fixing issue {issue.component}: {e}")
            return False

    def _fix_formula_version(self, issue) -> bool:
        """Fix Homebrew formula version mismatch.

        Args:
            issue: ValidationIssue for formula version

        Returns:
            True if fixed successfully
        """
        if not issue.expected_version:
            return False

        try:
            from riveter.scripts.sync_versions import VersionSynchronizer

            synchronizer = VersionSynchronizer(self.project_root)
            synchronizer.update_homebrew_formula(issue.expected_version)
            return True
        except Exception as e:
            logger.error(f"Failed to fix formula version: {e}")
            return False

    def _fix_hardcoded_version(self, issue) -> bool:
        """Fix hardcoded version in files.

        Args:
            issue: ValidationIssue for hardcoded version

        Returns:
            True if fixed successfully
        """
        # This would require more sophisticated file parsing and replacement
        # For now, just log that manual intervention is needed
        logger.warning(f"Manual fix required for hardcoded version in {issue.component}")
        return False

    def generate_release_checklist(self, report: ValidationReport) -> str:
        """Generate a release checklist based on validation results.

        Args:
            report: ValidationReport to base checklist on

        Returns:
            Formatted checklist string
        """
        lines = []
        lines.append("📋 Pre-Release Checklist")
        lines.append("=" * 30)
        lines.append("")

        # Version consistency checks
        lines.append("🔍 Version Consistency:")
        if report.is_consistent:
            lines.append("  ✅ All component versions are consistent")
        else:
            lines.append("  ❌ Version inconsistencies found - fix before release")

        # Component-specific checks
        lines.append("")
        lines.append("📦 Component Status:")

        required_components = ["pyproject.toml", "binary", "homebrew_formula"]
        for component in required_components:
            if component in report.components:
                info = report.components[component]
                status = "✅" if info.is_valid else "❌"
                lines.append(f"  {status} {component}: {info.version or 'N/A'}")
            else:
                lines.append(f"  ❌ {component}: Missing")

        # Issue summary
        lines.append("")
        lines.append("🚨 Issues to Address:")
        if not report.issues:
            lines.append("  ✅ No issues found")
        else:
            for severity in [
                ValidationSeverity.CRITICAL,
                ValidationSeverity.ERROR,
                ValidationSeverity.WARNING,
            ]:
                issues = report.get_issues_by_severity(severity)
                if issues:
                    icon = {"critical": "🚨", "error": "❌", "warning": "⚠️"}[severity.value]
                    lines.append(f"  {icon} {len(issues)} {severity.value} issue(s)")

        # Release readiness
        lines.append("")
        ready_for_release = report.is_consistent and not report.has_errors()
        if self.strict:
            ready_for_release = ready_for_release and not any(
                issue.severity == ValidationSeverity.WARNING for issue in report.issues
            )

        status = "✅ READY" if ready_for_release else "❌ NOT READY"
        lines.append(f"🚀 Release Status: {status}")

        return "\n".join(lines)


def main() -> None:
    """Main entry point for pre-release validation."""
    parser = argparse.ArgumentParser(
        description="Pre-release validation for Riveter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/pre_release_validation.py
  python scripts/pre_release_validation.py --strict
  python scripts/pre_release_validation.py --fix-issues

This script performs comprehensive validation before release including:
- Version consistency across all components
- Component configuration validation
- Documentation checks
- Release readiness assessment
        """,
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (fail validation on warnings)",
    )

    parser.add_argument(
        "--fix-issues",
        action="store_true",
        help="Attempt to fix issues automatically where possible",
    )

    parser.add_argument(
        "--checklist",
        action="store_true",
        help="Generate and display release checklist",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose output",
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Find project root
    current_dir = Path(__file__).parent
    project_root = current_dir.parent

    if not (project_root / "pyproject.toml").exists():
        logger.error("Could not find project root (pyproject.toml not found)")
        sys.exit(1)

    try:
        validator = PreReleaseValidator(
            project_root, strict=args.strict, fix_issues=args.fix_issues
        )

        if args.checklist:
            # Generate checklist only
            report = validator.validator.validate_all_components()
            checklist = validator.generate_release_checklist(report)
            print(f"\n{checklist}")

            if not report.is_consistent or report.has_errors():
                sys.exit(1)
        else:
            # Perform full validation
            success = validator.validate_for_release()
            sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Pre-release validation failed: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
