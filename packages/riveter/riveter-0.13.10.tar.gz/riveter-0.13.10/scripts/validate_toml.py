#!/usr/bin/env python3
"""Validate TOML files for structure and integrity.

This script validates TOML files used in the project, ensuring:
- Valid TOML syntax
- Required fields are present
- Proper structure and formatting
- Error recovery mechanisms
"""

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Any, Optional


class TOMLValidator:
    """Validates TOML files for structure and integrity."""

    def __init__(self, file_path: Path, verbose: bool = False) -> None:
        """Initialize TOML validator.

        Args:
            file_path: Path to TOML file to validate.
            verbose: Enable verbose output.
        """
        self.file_path = file_path
        self.verbose = verbose
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self, required_keys: Optional[list[str]] = None) -> bool:
        """Validate TOML file.

        Args:
            required_keys: List of required keys in dot notation.

        Returns:
            True if validation passes, False otherwise.
        """
        if not self._validate_file_exists():
            return False

        if not self._validate_syntax():
            return False

        if not self._validate_encoding():
            return False

        if required_keys and not self._validate_required_keys(required_keys):
            return False

        if not self._validate_structure():
            return False

        return True

    def _validate_file_exists(self) -> bool:
        """Validate that file exists and is readable."""
        if not self.file_path.exists():
            self.errors.append(f"File not found: {self.file_path}")
            return False

        if not self.file_path.is_file():
            self.errors.append(f"Not a file: {self.file_path}")
            return False

        try:
            self.file_path.read_text(encoding="utf-8")
        except OSError as e:
            self.errors.append(f"Cannot read file: {e}")
            return False

        if self.verbose:
            print(f"✓ File exists and is readable: {self.file_path}")

        return True

    def _validate_syntax(self) -> bool:
        """Validate TOML syntax."""
        try:
            with open(self.file_path, "rb") as f:
                tomllib.load(f)

            if self.verbose:
                print("✓ Valid TOML syntax")

            return True

        except tomllib.TOMLDecodeError as e:
            self.errors.append(f"TOML syntax error: {e}")
            return False

    def _validate_encoding(self) -> bool:
        """Validate file encoding."""
        try:
            content = self.file_path.read_text(encoding="utf-8")

            # Check for common encoding issues
            if "\r\n" in content:
                self.warnings.append(
                    "File contains Windows line endings (CRLF). "
                    "Consider using Unix line endings (LF)."
                )

            # Check for BOM
            if content.startswith("\ufeff"):
                self.warnings.append("File contains UTF-8 BOM. Consider removing it.")

            if self.verbose:
                print("✓ Valid UTF-8 encoding")

            return True

        except UnicodeDecodeError as e:
            self.errors.append(f"Encoding error: {e}")
            return False

    def _validate_required_keys(self, required_keys: list[str]) -> bool:
        """Validate that required keys exist.

        Args:
            required_keys: List of required keys in dot notation.

        Returns:
            True if all required keys exist.
        """
        try:
            with open(self.file_path, "rb") as f:
                data = tomllib.load(f)

            missing_keys = []
            for key_path in required_keys:
                if not self._has_key_path(data, key_path):
                    missing_keys.append(key_path)

            if missing_keys:
                self.errors.append(f"Missing required keys: {', '.join(missing_keys)}")
                return False

            if self.verbose:
                print(f"✓ All required keys present: {', '.join(required_keys)}")

            return True

        except Exception as e:
            self.errors.append(f"Error validating required keys: {e}")
            return False

    def _has_key_path(self, data: dict[str, Any], key_path: str) -> bool:
        """Check if dot-notation key path exists in data.

        Args:
            data: Dictionary to check.
            key_path: Dot-notation key path.

        Returns:
            True if key path exists.
        """
        keys = key_path.split(".")
        current = data

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return False
            current = current[key]

        return True

    def _validate_structure(self) -> bool:
        """Validate TOML structure for common issues."""
        try:
            with open(self.file_path, "rb") as f:
                data = tomllib.load(f)

            # Check for empty tables
            empty_tables = self._find_empty_tables(data)
            if empty_tables:
                self.warnings.append(f"Empty tables found: {', '.join(empty_tables)}")

            # Check for duplicate keys (tomllib handles this, but we can check structure)
            if self.verbose:
                print("✓ Structure validation passed")

            return True

        except Exception as e:
            self.errors.append(f"Error validating structure: {e}")
            return False

    def _find_empty_tables(self, data: dict[str, Any], prefix: str = "") -> list[str]:
        """Find empty tables in TOML data.

        Args:
            data: Dictionary to check.
            prefix: Current key prefix.

        Returns:
            List of empty table paths.
        """
        empty = []

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                if not value:
                    empty.append(full_key)
                else:
                    empty.extend(self._find_empty_tables(value, full_key))

        return empty

    def print_results(self) -> None:
        """Print validation results."""
        if self.errors:
            print("\n❌ Validation Errors:")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print("\n⚠️  Validation Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print(f"\n✅ {self.file_path} is valid")
        elif not self.errors:
            print(f"\n✅ {self.file_path} is valid (with warnings)")


def validate_pyproject_toml(file_path: Path, verbose: bool = False) -> bool:
    """Validate pyproject.toml file.

    Args:
        file_path: Path to pyproject.toml.
        verbose: Enable verbose output.

    Returns:
        True if validation passes.
    """
    validator = TOMLValidator(file_path, verbose=verbose)

    # Define required keys for pyproject.toml
    required_keys = [
        "project.name",
        "project.version",
        "project.description",
    ]

    result = validator.validate(required_keys=required_keys)
    validator.print_results()

    return result


def validate_workflow_dependencies(file_path: Path, verbose: bool = False) -> bool:
    """Validate workflow-dependencies.yml file.

    Args:
        file_path: Path to workflow-dependencies.yml.
        verbose: Enable verbose output.

    Returns:
        True if validation passes.
    """
    validator = TOMLValidator(file_path, verbose=verbose)

    # Define required keys for workflow dependencies
    required_keys = [
        "workflow_dependencies",
    ]

    result = validator.validate(required_keys=required_keys)
    validator.print_results()

    return result


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate TOML files for structure and integrity")
    parser.add_argument(
        "file",
        type=Path,
        help="Path to TOML file to validate",
    )
    parser.add_argument(
        "--type",
        choices=["pyproject", "workflow-deps", "generic"],
        default="generic",
        help="Type of TOML file (determines validation rules)",
    )
    parser.add_argument(
        "--required-keys",
        nargs="+",
        help="Required keys in dot notation (e.g., project.version)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit with error code if warnings are found",
    )

    args = parser.parse_args()

    # Validate based on type
    if args.type == "pyproject":
        success = validate_pyproject_toml(args.file, verbose=args.verbose)
    elif args.type == "workflow-deps":
        success = validate_workflow_dependencies(args.file, verbose=args.verbose)
    else:
        validator = TOMLValidator(args.file, verbose=args.verbose)
        success = validator.validate(required_keys=args.required_keys)
        validator.print_results()

        # Check for warnings if fail-on-warnings is set
        if args.fail_on_warnings and validator.warnings:
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
