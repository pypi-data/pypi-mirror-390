#!/usr/bin/env python3
"""
Homebrew Formula Validation Script

This script validates the Homebrew formula for Riveter, including:
- Ruby syntax validation
- Formula structure validation
- URL and checksum verification
- Binary asset validation
- Installation logic testing

Usage:
    python scripts/validate_homebrew_formula.py [options]

Options:
    --formula-path PATH     Path to the formula file
                            (default: ../homebrew-riveter/Formula/riveter.rb)
    --version VERSION       Version to validate (e.g., 1.2.3)
    --check-assets         Download and verify binary assets
    --verbose              Enable verbose output
    --help                 Show this help message
"""

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional


class FormulaValidator:
    """Validates Homebrew formula for Riveter."""

    def __init__(self, formula_path: str, version: Optional[str] = None, verbose: bool = False):
        self.formula_path = Path(formula_path)
        self.version = version
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with optional verbosity control."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            prefix = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "📋")
            print(f"{prefix} {message}")

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.log(message, "ERROR")

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
        self.log(message, "WARNING")

    def validate_file_exists(self) -> bool:
        """Validate that the formula file exists."""
        self.log("Validating formula file exists...")

        if not self.formula_path.exists():
            self.add_error(f"Formula file not found: {self.formula_path}")
            return False

        if not self.formula_path.is_file():
            self.add_error(f"Formula path is not a file: {self.formula_path}")
            return False

        self.log(f"Formula file found: {self.formula_path}", "SUCCESS")
        return True

    def validate_ruby_syntax(self) -> bool:
        """Validate Ruby syntax of the formula."""
        self.log("Validating Ruby syntax...")

        try:
            result = subprocess.run(
                ["ruby", "-c", str(self.formula_path)], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                self.log("Ruby syntax is valid", "SUCCESS")
                return True
            else:
                self.add_error(f"Ruby syntax error: {result.stderr.strip()}")
                return False

        except subprocess.TimeoutExpired:
            self.add_error("Ruby syntax check timed out")
            return False
        except FileNotFoundError:
            self.add_error("Ruby interpreter not found - install Ruby to validate syntax")
            return False
        except Exception as e:
            self.add_error(f"Error running Ruby syntax check: {e}")
            return False

    def validate_formula_structure(self) -> bool:
        """Validate the structure of the Homebrew formula."""
        self.log("Validating formula structure...")

        try:
            content = self.formula_path.read_text(encoding="utf-8")
        except Exception as e:
            self.add_error(f"Error reading formula file: {e}")
            return False

        # Required elements
        required_patterns = {
            "class_definition": r"class\s+Riveter\s+<\s+Formula",
            "description": r'desc\s+"[^"]+"',
            "homepage": r'homepage\s+"https?://[^"]+"',
            "version": r'version\s+"[^"]+"',
            "install_method": r"def\s+install",
            "test_method": r"def\s+test",
        }

        structure_valid = True

        for element, pattern in required_patterns.items():
            if re.search(pattern, content):
                self.log(f"Found required element: {element}", "SUCCESS")
            else:
                self.add_error(f"Missing required element: {element}")
                structure_valid = False

        # Check for platform conditionals
        if re.search(r"if\s+OS\.mac\?\s+&&\s+Hardware::CPU\.intel\?", content):
            self.log("Found macOS Intel conditional", "SUCCESS")
        else:
            self.add_error("Missing macOS Intel conditional")
            structure_valid = False

        if re.search(r"elsif\s+OS\.mac\?\s+&&\s+Hardware::CPU\.arm\?", content):
            self.log("Found macOS ARM conditional", "SUCCESS")
        else:
            self.add_error("Missing macOS ARM conditional")
            structure_valid = False

        if re.search(r"elsif\s+OS\.linux\?", content):
            self.log("Found Linux conditional", "SUCCESS")
        else:
            self.add_error("Missing Linux conditional")
            structure_valid = False

        # Check for URL and SHA256 patterns
        url_pattern = r'url\s+"https://github\.com/[^/]+/[^/]+/releases/download/[^"]+"'
        if re.search(url_pattern, content):
            self.log("Found valid URL pattern", "SUCCESS")
        else:
            self.add_error("Missing or invalid URL pattern")
            structure_valid = False

        sha256_pattern = r'sha256\s+"[a-f0-9]{64}"'
        sha256_matches = re.findall(sha256_pattern, content)
        if len(sha256_matches) >= 3:
            self.log(f"Found {len(sha256_matches)} SHA256 checksums", "SUCCESS")
        else:
            self.add_error(f"Expected at least 3 SHA256 checksums, found {len(sha256_matches)}")
            structure_valid = False

        # Check for template placeholders (should not exist in final formula)
        if "{{" in content or "}}" in content:
            self.add_error("Template placeholders found in formula - formula not properly updated")
            structure_valid = False
        else:
            self.log("No template placeholders found", "SUCCESS")

        return structure_valid

    def extract_formula_info(self) -> Optional[Dict]:
        """Extract version, URLs, and checksums from the formula."""
        self.log("Extracting formula information...")

        try:
            content = self.formula_path.read_text(encoding="utf-8")
        except Exception as e:
            self.add_error(f"Error reading formula file: {e}")
            return None

        # Extract version
        version_match = re.search(r'version\s+"([^"]+)"', content)
        if not version_match:
            self.add_error("Could not extract version from formula")
            return None

        formula_version = version_match.group(1)

        # Extract URLs and checksums
        platforms = ["macos-intel", "macos-arm64", "linux-x86_64"]
        info = {"version": formula_version, "platforms": {}}

        # Find all URL and SHA256 pairs
        url_pattern = r'url\s+"(https://github\.com/[^/]+/[^/]+/releases/download/[^"]+)"'
        sha256_pattern = r'sha256\s+"([a-f0-9]{64})"'

        urls = re.findall(url_pattern, content)
        checksums = re.findall(sha256_pattern, content)

        if len(urls) != len(checksums):
            self.add_error(f"Mismatch between URLs ({len(urls)}) and checksums ({len(checksums)})")
            return None

        # Match URLs to platforms
        for url, checksum in zip(urls, checksums, strict=False):
            for platform in platforms:
                if platform in url:
                    info["platforms"][platform] = {"url": url, "checksum": checksum}
                    break

        if len(info["platforms"]) != len(platforms):
            missing = set(platforms) - set(info["platforms"].keys())
            self.add_error(f"Missing platform information for: {', '.join(missing)}")
            return None

        self.log(f"Extracted formula info for version {formula_version}", "SUCCESS")
        return info

    def validate_version_consistency(self, formula_info: Dict) -> bool:
        """Validate version consistency."""
        self.log("Validating version consistency...")

        formula_version = formula_info["version"]

        if self.version:
            if formula_version != self.version:
                self.add_error(
                    f"Version mismatch: expected {self.version}, found {formula_version}"
                )
                return False
            else:
                self.log(f"Version matches expected: {self.version}", "SUCCESS")

        # Check that URLs contain the correct version
        for platform, info in formula_info["platforms"].items():
            url = info["url"]
            if f"riveter-{formula_version}-{platform}" not in url:
                self.add_error(f"URL for {platform} does not contain expected version pattern")
                return False

        self.log("Version consistency validated", "SUCCESS")
        return True

    def download_and_verify_assets(self, formula_info: Dict) -> bool:
        """Download and verify binary assets."""
        self.log("Downloading and verifying binary assets...")

        verification_success = True

        with tempfile.TemporaryDirectory() as temp_dir:
            for platform, info in formula_info["platforms"].items():
                url = info["url"]
                expected_checksum = info["checksum"]

                self.log(f"Downloading {platform} asset...")

                try:
                    # Download the asset
                    filename = url.split("/")[-1]
                    filepath = Path(temp_dir) / filename

                    urllib.request.urlretrieve(url, filepath)

                    # Calculate checksum
                    sha256_hash = hashlib.sha256()
                    with open(filepath, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            sha256_hash.update(chunk)

                    actual_checksum = sha256_hash.hexdigest()

                    # Verify checksum
                    if actual_checksum == expected_checksum:
                        self.log(
                            f"Checksum verified for {platform}: {actual_checksum[:16]}...",
                            "SUCCESS",
                        )
                    else:
                        self.add_error(f"Checksum mismatch for {platform}:")
                        self.add_error(f"  Expected: {expected_checksum}")
                        self.add_error(f"  Actual:   {actual_checksum}")
                        verification_success = False

                except Exception as e:
                    self.add_error(f"Error downloading/verifying {platform} asset: {e}")
                    verification_success = False

        if verification_success:
            self.log("All binary assets verified successfully", "SUCCESS")

        return verification_success

    def validate_install_logic(self) -> bool:
        """Validate the install method logic."""
        self.log("Validating install method logic...")

        try:
            content = self.formula_path.read_text(encoding="utf-8")
        except Exception as e:
            self.add_error(f"Error reading formula file: {e}")
            return False

        # Extract install method
        install_match = re.search(r"def install.*?^  end", content, re.MULTILINE | re.DOTALL)
        if not install_match:
            self.add_error("Could not find install method")
            return False

        install_content = install_match.group(0)

        # Check for required elements in install method
        required_elements = {
            "binary_check": r'File\.exist\?\("riveter"\)',
            "binary_install": r"bin\.install",
            "chmod": r"chmod",
            "version_test": r"system.*--version",
        }

        install_valid = True

        for element, pattern in required_elements.items():
            if re.search(pattern, install_content):
                self.log(f"Found install element: {element}", "SUCCESS")
            else:
                if element == "chmod":
                    self.add_warning(f"Install method missing recommended element: {element}")
                else:
                    self.add_error(f"Install method missing required element: {element}")
                    install_valid = False

        return install_valid

    def validate_test_logic(self) -> bool:
        """Validate the test method logic."""
        self.log("Validating test method logic...")

        try:
            content = self.formula_path.read_text(encoding="utf-8")
        except Exception as e:
            self.add_error(f"Error reading formula file: {e}")
            return False

        # Extract test method
        test_match = re.search(r"def test.*?^  end", content, re.MULTILINE | re.DOTALL)
        if not test_match:
            self.add_error("Could not find test method")
            return False

        test_content = test_match.group(0)

        # Check for required elements in test method
        required_tests = {
            "version_test": r"--version",
            "help_test": r"--help",
            "list_rule_packs": r"list-rule-packs",
            "scan_help": r"scan --help",
        }

        test_valid = True

        for test_name, pattern in required_tests.items():
            if re.search(pattern, test_content):
                self.log(f"Found test: {test_name}", "SUCCESS")
            else:
                if test_name == "version_test":
                    self.add_error(f"Test method missing required test: {test_name}")
                    test_valid = False
                else:
                    self.add_warning(f"Test method missing recommended test: {test_name}")

        return test_valid

    def run_validation(self, check_assets: bool = False) -> bool:
        """Run complete formula validation."""
        self.log("Starting Homebrew formula validation...")
        self.log(f"Formula path: {self.formula_path}")
        if self.version:
            self.log(f"Expected version: {self.version}")

        # Step 1: Check file exists
        if not self.validate_file_exists():
            return False

        # Step 2: Validate Ruby syntax
        syntax_valid = self.validate_ruby_syntax()

        # Step 3: Validate formula structure
        structure_valid = self.validate_formula_structure()

        # Step 4: Extract formula information
        formula_info = self.extract_formula_info()
        if not formula_info:
            return False

        # Step 5: Validate version consistency
        version_valid = self.validate_version_consistency(formula_info)

        # Step 6: Validate install and test logic
        install_valid = self.validate_install_logic()
        test_valid = self.validate_test_logic()

        # Step 7: Download and verify assets (optional)
        assets_valid = True
        if check_assets:
            assets_valid = self.download_and_verify_assets(formula_info)

        # Summary
        all_valid = (
            syntax_valid
            and structure_valid
            and version_valid
            and install_valid
            and test_valid
            and assets_valid
        )

        self.log("\n" + "=" * 50)
        self.log("VALIDATION SUMMARY")
        self.log("=" * 50)

        results = [
            ("Ruby Syntax", syntax_valid),
            ("Formula Structure", structure_valid),
            ("Version Consistency", version_valid),
            ("Install Logic", install_valid),
            ("Test Logic", test_valid),
        ]

        if check_assets:
            results.append(("Binary Assets", assets_valid))

        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name:<20} {status}")

        if self.warnings:
            self.log(f"\nWarnings: {len(self.warnings)}")
            for warning in self.warnings:
                self.log(f"  ⚠️ {warning}")

        if self.errors:
            self.log(f"\nErrors: {len(self.errors)}")
            for error in self.errors:
                self.log(f"  ❌ {error}")

        if all_valid:
            self.log("\n🎉 Formula validation PASSED", "SUCCESS")
        else:
            self.log("\n💥 Formula validation FAILED", "ERROR")

        return all_valid


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Homebrew formula for Riveter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--formula-path",
        default="../homebrew-riveter/Formula/riveter.rb",
        help="Path to the formula file",
    )

    parser.add_argument("--version", help="Version to validate (e.g., 1.2.3)")

    parser.add_argument(
        "--check-assets", action="store_true", help="Download and verify binary assets"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Resolve formula path
    formula_path = Path(args.formula_path)
    if not formula_path.is_absolute():
        # Resolve relative to script directory
        script_dir = Path(__file__).parent
        formula_path = script_dir / formula_path

    # Create validator and run validation
    validator = FormulaValidator(
        formula_path=str(formula_path), version=args.version, verbose=args.verbose
    )

    success = validator.run_validation(check_assets=args.check_assets)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
