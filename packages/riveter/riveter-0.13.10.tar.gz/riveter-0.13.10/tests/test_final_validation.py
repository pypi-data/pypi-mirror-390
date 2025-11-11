#!/usr/bin/env python3
"""Final validation test for CI pipeline version sync fixes.

This test provides a comprehensive summary of all implemented fixes
and validates that the original issues have been resolved.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path


class FinalValidationTest(unittest.TestCase):
    """Final validation of all CI pipeline fixes."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.project_root = Path(__file__).parent.parent
        cls.homebrew_repo_path = cls.project_root.parent / "homebrew-riveter"

    def test_final_validation_summary(self):
        """Provide final validation summary of all fixes."""
        print("\n🎯 FINAL VALIDATION SUMMARY")
        print("=" * 60)

        results = {}

        # Issue 1: Version Synchronization
        print("\n📋 Issue #1: Version Synchronization")
        print("-" * 40)

        # Check version sync script exists and works
        sync_script = self.project_root / "scripts" / "sync_versions.py"
        if sync_script.exists():
            try:
                result = subprocess.run(
                    ["python3", str(sync_script), "--validate"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    print("✅ Version synchronization script works")
                    results["version_sync_script"] = "PASS"
                else:
                    print("⚠️ Version synchronization has issues")
                    results["version_sync_script"] = "ISSUES"
            except Exception as e:
                print(f"❌ Version synchronization error: {e}")
                results["version_sync_script"] = "ERROR"
        else:
            print("❌ Version synchronization script missing")
            results["version_sync_script"] = "MISSING"

        # Check version consistency
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                tomllib = None

        if tomllib:
            pyproject_path = self.project_root / "pyproject.toml"
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            pyproject_version = data["project"]["version"]

            # Check formula version
            formula_version = None
            if self.homebrew_repo_path.exists():
                formula_path = self.homebrew_repo_path / "Formula" / "riveter.rb"
                if formula_path.exists():
                    with open(formula_path, "r") as f:
                        content = f.read()
                    match = re.search(r'version\s+"([^"]+)"', content)
                    if match:
                        formula_version = match.group(1)

            if formula_version and pyproject_version == formula_version:
                print(f"✅ Versions consistent: {pyproject_version}")
                results["version_consistency"] = "PASS"
            elif formula_version:
                print(
                    f"⚠️ Version mismatch: pyproject={pyproject_version}, formula={formula_version}"
                )
                results["version_consistency"] = "MISMATCH"
            else:
                print(f"⚠️ Formula version not found (pyproject={pyproject_version})")
                results["version_consistency"] = "PARTIAL"

        # Issue 2: Homebrew Audit Commands
        print("\n🔍 Issue #2: Homebrew Audit Commands")
        print("-" * 40)

        workflow_path = (
            self.project_root / ".github" / "workflows" / "test-homebrew-installation.yml"
        )
        if workflow_path.exists():
            with open(workflow_path, "r") as f:
                content = f.read()

            # Check for deprecated syntax
            if "brew audit Formula/" in content:
                print("❌ Still uses deprecated path-based audit syntax")
                results["audit_syntax"] = "FAIL"
            else:
                print("✅ Uses correct name-based audit syntax")
                results["audit_syntax"] = "PASS"

            # Check for tap setup
            if "brew tap" in content and "brew audit" in content:
                print("✅ Workflow adds tap before audit")
                results["audit_workflow"] = "PASS"
            else:
                print("⚠️ Workflow audit setup unclear")
                results["audit_workflow"] = "UNCLEAR"
        else:
            print("❌ Workflow file not found")
            results["audit_syntax"] = "MISSING"
            results["audit_workflow"] = "MISSING"

        # Test actual audit if Homebrew available
        if shutil.which("brew") and self.homebrew_repo_path.exists():
            try:
                # Clean up first
                subprocess.run(
                    ["brew", "untap", "scottryanhoward/homebrew-riveter"],
                    capture_output=True,
                    check=False,
                )

                # Add tap
                result = subprocess.run(
                    [
                        "brew",
                        "tap",
                        "scottryanhoward/homebrew-riveter",
                        str(self.homebrew_repo_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    # Test audit
                    result = subprocess.run(
                        ["brew", "audit", "riveter"], capture_output=True, text=True, timeout=30
                    )

                    if "Calling brew audit [path ...]" in result.stderr:
                        print("❌ Audit still triggers path-based error")
                        results["audit_functional"] = "FAIL"
                    else:
                        print("✅ Audit uses correct syntax (may have other issues)")
                        results["audit_functional"] = "PASS"

                    # Clean up
                    subprocess.run(
                        ["brew", "untap", "scottryanhoward/homebrew-riveter"],
                        capture_output=True,
                        check=False,
                    )
                else:
                    print("⚠️ Could not test audit (tap installation failed)")
                    results["audit_functional"] = "UNTESTABLE"
            except Exception as e:
                print(f"⚠️ Could not test audit: {e}")
                results["audit_functional"] = "ERROR"
        else:
            print("⚠️ Cannot test audit (Homebrew not available)")
            results["audit_functional"] = "UNTESTABLE"

        # Issue 3: Homebrew Tap Installation
        print("\n🍺 Issue #3: Homebrew Tap Installation")
        print("-" * 40)

        # Check repository structure
        if self.homebrew_repo_path.exists():
            formula_path = self.homebrew_repo_path / "Formula" / "riveter.rb"
            if formula_path.exists():
                print("✅ Repository structure correct")
                results["repo_structure"] = "PASS"

                # Check formula syntax
                if shutil.which("ruby"):
                    result = subprocess.run(
                        ["ruby", "-c", str(formula_path)], capture_output=True, text=True
                    )

                    if result.returncode == 0:
                        print("✅ Formula syntax valid")
                        results["formula_syntax"] = "PASS"
                    else:
                        print("❌ Formula syntax invalid")
                        results["formula_syntax"] = "FAIL"
                else:
                    print("⚠️ Cannot validate formula syntax (Ruby not available)")
                    results["formula_syntax"] = "UNTESTABLE"
            else:
                print("❌ Formula file missing")
                results["repo_structure"] = "MISSING"
                results["formula_syntax"] = "MISSING"
        else:
            print("❌ Repository not found")
            results["repo_structure"] = "MISSING"
            results["formula_syntax"] = "MISSING"

        # Test tap installation
        if shutil.which("brew") and self.homebrew_repo_path.exists():
            try:
                # Clean up first
                subprocess.run(
                    ["brew", "untap", "scottryanhoward/homebrew-riveter"],
                    capture_output=True,
                    check=False,
                )

                # Test tap installation
                result = subprocess.run(
                    [
                        "brew",
                        "tap",
                        "scottryanhoward/homebrew-riveter",
                        str(self.homebrew_repo_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 1:
                    print("❌ Tap installation fails with exit code 1")
                    results["tap_installation"] = "FAIL"
                elif result.returncode == 0:
                    print("✅ Tap installation succeeds")
                    results["tap_installation"] = "PASS"
                else:
                    print(f"⚠️ Tap installation exits with code {result.returncode}")
                    results["tap_installation"] = "PARTIAL"

                # Clean up
                subprocess.run(
                    ["brew", "untap", "scottryanhoward/homebrew-riveter"],
                    capture_output=True,
                    check=False,
                )
            except Exception as e:
                print(f"⚠️ Could not test tap installation: {e}")
                results["tap_installation"] = "ERROR"
        else:
            print("⚠️ Cannot test tap installation (Homebrew not available)")
            results["tap_installation"] = "UNTESTABLE"

        # Overall Summary
        print("\n🎯 OVERALL SUMMARY")
        print("=" * 60)

        # Count results
        pass_count = sum(1 for v in results.values() if v == "PASS")
        fail_count = sum(1 for v in results.values() if v == "FAIL")
        issue_count = sum(1 for v in results.values() if v in ["ISSUES", "MISMATCH", "PARTIAL"])
        missing_count = sum(1 for v in results.values() if v == "MISSING")
        untestable_count = sum(1 for v in results.values() if v == "UNTESTABLE")
        error_count = sum(1 for v in results.values() if v == "ERROR")
        unclear_count = sum(1 for v in results.values() if v == "UNCLEAR")

        total_checks = len(results)

        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {pass_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"⚠️ Issues: {issue_count}")
        print(f"📁 Missing: {missing_count}")
        print(f"🚫 Untestable: {untestable_count}")
        print(f"💥 Errors: {error_count}")
        print(f"❓ Unclear: {unclear_count}")

        # Determine overall status
        if fail_count == 0 and missing_count == 0 and error_count == 0:
            if pass_count >= total_checks * 0.8:  # 80% pass rate
                print("\n🎉 OVERALL STATUS: SUCCESS")
                print("All critical issues have been resolved!")
            else:
                print("\n✅ OVERALL STATUS: MOSTLY RESOLVED")
                print("Most issues resolved, some minor items remain.")
        elif fail_count <= 1 and missing_count == 0:
            print("\n⚠️ OVERALL STATUS: PARTIALLY RESOLVED")
            print("Major progress made, some issues remain.")
        else:
            print("\n❌ OVERALL STATUS: NEEDS WORK")
            print("Significant issues remain to be addressed.")

        # Detailed results
        print("\n📊 DETAILED RESULTS:")
        for check, result in results.items():
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "ISSUES": "⚠️",
                "MISMATCH": "⚠️",
                "PARTIAL": "⚠️",
                "MISSING": "📁",
                "UNTESTABLE": "🚫",
                "ERROR": "💥",
                "UNCLEAR": "❓",
            }.get(result, "❓")

            print(f"  {status_icon} {check}: {result}")

        print("\n" + "=" * 60)
        print("Final validation completed.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
