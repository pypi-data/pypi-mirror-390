#!/usr/bin/env python3
"""
Homebrew installation error recovery script.

This script provides automated error recovery for common Homebrew installation
failures, including tap installation issues, formula validation problems,
and binary installation errors.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of Homebrew installation errors."""

    TAP_INSTALLATION = "tap_installation"
    FORMULA_VALIDATION = "formula_validation"
    BINARY_INSTALLATION = "binary_installation"
    VERSION_MISMATCH = "version_mismatch"
    NETWORK_CONNECTIVITY = "network_connectivity"
    PERMISSIONS = "permissions"


@dataclass
class RecoveryAction:
    """Recovery action for a specific error."""

    name: str
    description: str
    command: Optional[str] = None
    function: Optional[callable] = None
    retry_count: int = 1
    delay: float = 0.0


@dataclass
class ErrorDiagnostic:
    """Diagnostic information for an error."""

    error_type: ErrorType
    error_message: str
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    environment: Optional[Dict[str, str]] = None
    recovery_actions: List[RecoveryAction] = None


class HomebrewErrorRecovery:
    """Handles error recovery for Homebrew installation issues."""

    def __init__(self, project_root: Optional[Path] = None, debug: bool = False):
        """Initialize error recovery handler.

        Args:
            project_root: Root directory of the project
            debug: Enable debug mode for verbose output
        """
        self.project_root = project_root or Path.cwd()
        self.debug = debug

        if debug:
            logger.setLevel(logging.DEBUG)

    def diagnose_error(self, error_output: str, exit_code: int) -> ErrorDiagnostic:
        """Diagnose the type of Homebrew error from output.

        Args:
            error_output: Error output from failed command
            exit_code: Exit code from failed command

        Returns:
            ErrorDiagnostic with error type and recovery actions
        """
        logger.debug(f"Diagnosing error with exit code {exit_code}")
        logger.debug(f"Error output: {error_output}")

        # Analyze error patterns
        error_lower = error_output.lower()

        if "tap" in error_lower and ("not found" in error_lower or "does not exist" in error_lower):
            return self._diagnose_tap_error(error_output, exit_code)
        elif "audit" in error_lower or "formula" in error_lower:
            return self._diagnose_formula_error(error_output, exit_code)
        elif "install" in error_lower and ("failed" in error_lower or "error" in error_lower):
            return self._diagnose_installation_error(error_output, exit_code)
        elif "version" in error_lower and "mismatch" in error_lower:
            return self._diagnose_version_error(error_output, exit_code)
        elif "network" in error_lower or "connection" in error_lower or "timeout" in error_lower:
            return self._diagnose_network_error(error_output, exit_code)
        elif "permission" in error_lower or "denied" in error_lower:
            return self._diagnose_permissions_error(error_output, exit_code)
        else:
            return self._diagnose_generic_error(error_output, exit_code)

    def _diagnose_tap_error(self, error_output: str, exit_code: int) -> ErrorDiagnostic:
        """Diagnose tap installation errors."""
        recovery_actions = [
            RecoveryAction(
                name="retry_tap_installation",
                description="Retry tap installation with exponential backoff",
                function=self._retry_tap_installation,
                retry_count=3,
                delay=5.0,
            ),
            RecoveryAction(
                name="update_homebrew",
                description="Update Homebrew and retry",
                command="brew update",
                retry_count=1,
            ),
            RecoveryAction(
                name="check_network_connectivity",
                description="Check network connectivity to GitHub",
                function=self._check_github_connectivity,
                retry_count=1,
            ),
            RecoveryAction(
                name="clear_homebrew_cache",
                description="Clear Homebrew cache and retry",
                command="brew cleanup --prune=all",
                retry_count=1,
            ),
        ]

        return ErrorDiagnostic(
            error_type=ErrorType.TAP_INSTALLATION,
            error_message="Tap installation failed",
            exit_code=exit_code,
            stderr=error_output,
            recovery_actions=recovery_actions,
        )

    def _diagnose_formula_error(self, error_output: str, exit_code: int) -> ErrorDiagnostic:
        """Diagnose formula validation errors."""
        recovery_actions = [
            RecoveryAction(
                name="validate_formula_syntax",
                description="Validate formula syntax and structure",
                function=self._validate_formula_syntax,
                retry_count=1,
            ),
            RecoveryAction(
                name="check_formula_urls",
                description="Check formula download URLs",
                function=self._check_formula_urls,
                retry_count=1,
            ),
            RecoveryAction(
                name="update_formula_checksums",
                description="Update formula checksums if needed",
                function=self._update_formula_checksums,
                retry_count=1,
            ),
        ]

        return ErrorDiagnostic(
            error_type=ErrorType.FORMULA_VALIDATION,
            error_message="Formula validation failed",
            exit_code=exit_code,
            stderr=error_output,
            recovery_actions=recovery_actions,
        )

    def _diagnose_installation_error(self, error_output: str, exit_code: int) -> ErrorDiagnostic:
        """Diagnose binary installation errors."""
        recovery_actions = [
            RecoveryAction(
                name="retry_installation",
                description="Retry installation with clean environment",
                function=self._retry_installation,
                retry_count=3,
                delay=10.0,
            ),
            RecoveryAction(
                name="install_from_source",
                description="Try installing from source",
                command="brew install --build-from-source scottryanhoward/homebrew-riveter/riveter",
                retry_count=1,
            ),
            RecoveryAction(
                name="check_dependencies",
                description="Check and install missing dependencies",
                function=self._check_dependencies,
                retry_count=1,
            ),
        ]

        return ErrorDiagnostic(
            error_type=ErrorType.BINARY_INSTALLATION,
            error_message="Binary installation failed",
            exit_code=exit_code,
            stderr=error_output,
            recovery_actions=recovery_actions,
        )

    def _diagnose_version_error(self, error_output: str, exit_code: int) -> ErrorDiagnostic:
        """Diagnose version mismatch errors."""
        recovery_actions = [
            RecoveryAction(
                name="sync_versions",
                description="Synchronize versions across components",
                function=self._sync_versions,
                retry_count=1,
            ),
            RecoveryAction(
                name="validate_version_consistency",
                description="Validate version consistency",
                function=self._validate_versions,
                retry_count=1,
            ),
        ]

        return ErrorDiagnostic(
            error_type=ErrorType.VERSION_MISMATCH,
            error_message="Version mismatch detected",
            exit_code=exit_code,
            stderr=error_output,
            recovery_actions=recovery_actions,
        )

    def _diagnose_network_error(self, error_output: str, exit_code: int) -> ErrorDiagnostic:
        """Diagnose network connectivity errors."""
        recovery_actions = [
            RecoveryAction(
                name="check_network_connectivity",
                description="Check network connectivity",
                function=self._check_network_connectivity,
                retry_count=1,
            ),
            RecoveryAction(
                name="retry_with_backoff",
                description="Retry with exponential backoff",
                function=self._retry_with_backoff,
                retry_count=5,
                delay=2.0,
            ),
        ]

        return ErrorDiagnostic(
            error_type=ErrorType.NETWORK_CONNECTIVITY,
            error_message="Network connectivity issue",
            exit_code=exit_code,
            stderr=error_output,
            recovery_actions=recovery_actions,
        )

    def _diagnose_permissions_error(self, error_output: str, exit_code: int) -> ErrorDiagnostic:
        """Diagnose permissions errors."""
        recovery_actions = [
            RecoveryAction(
                name="check_homebrew_permissions",
                description="Check Homebrew directory permissions",
                function=self._check_homebrew_permissions,
                retry_count=1,
            ),
            RecoveryAction(
                name="fix_homebrew_permissions",
                description="Fix Homebrew permissions",
                function=self._fix_homebrew_permissions,
                retry_count=1,
            ),
        ]

        return ErrorDiagnostic(
            error_type=ErrorType.PERMISSIONS,
            error_message="Permissions error",
            exit_code=exit_code,
            stderr=error_output,
            recovery_actions=recovery_actions,
        )

    def _diagnose_generic_error(self, error_output: str, exit_code: int) -> ErrorDiagnostic:
        """Diagnose generic errors."""
        recovery_actions = [
            RecoveryAction(
                name="homebrew_doctor",
                description="Run brew doctor to diagnose issues",
                command="brew doctor",
                retry_count=1,
            ),
            RecoveryAction(
                name="update_homebrew",
                description="Update Homebrew",
                command="brew update",
                retry_count=1,
            ),
            RecoveryAction(
                name="cleanup_homebrew",
                description="Clean up Homebrew",
                command="brew cleanup",
                retry_count=1,
            ),
        ]

        return ErrorDiagnostic(
            error_type=ErrorType.TAP_INSTALLATION,  # Default to tap installation
            error_message="Generic Homebrew error",
            exit_code=exit_code,
            stderr=error_output,
            recovery_actions=recovery_actions,
        )

    def execute_recovery(self, diagnostic: ErrorDiagnostic) -> bool:
        """Execute recovery actions for a diagnosed error.

        Args:
            diagnostic: Error diagnostic with recovery actions

        Returns:
            True if recovery was successful, False otherwise
        """
        logger.info(f"Executing recovery for {diagnostic.error_type.value}")
        logger.info(f"Error: {diagnostic.error_message}")

        if not diagnostic.recovery_actions:
            logger.warning("No recovery actions available")
            return False

        for action in diagnostic.recovery_actions:
            logger.info(f"Executing recovery action: {action.name}")
            logger.info(f"Description: {action.description}")

            success = False
            for attempt in range(action.retry_count):
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1} of {action.retry_count}")
                    if action.delay > 0:
                        logger.info(f"Waiting {action.delay} seconds...")
                        time.sleep(action.delay)

                try:
                    if action.command:
                        success = self._execute_command(action.command)
                    elif action.function:
                        success = action.function()
                    else:
                        logger.warning(f"No command or function defined for action {action.name}")
                        continue

                    if success:
                        logger.info(f"✅ Recovery action {action.name} succeeded")
                        break
                    else:
                        logger.warning(f"❌ Recovery action {action.name} failed")

                except Exception as e:
                    logger.error(f"❌ Recovery action {action.name} failed with exception: {e}")

            if not success:
                logger.error(f"❌ All attempts for recovery action {action.name} failed")
                return False

        logger.info("✅ All recovery actions completed successfully")
        return True

    def _execute_command(self, command: str) -> bool:
        """Execute a shell command.

        Args:
            command: Command to execute

        Returns:
            True if command succeeded, False otherwise
        """
        try:
            logger.debug(f"Executing command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.debug(f"Command succeeded: {command}")
                if result.stdout:
                    logger.debug(f"stdout: {result.stdout}")
                return True
            else:
                logger.warning(f"Command failed with exit code {result.returncode}: {command}")
                if result.stderr:
                    logger.warning(f"stderr: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return False
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False

    # Recovery action implementations
    def _retry_tap_installation(self) -> bool:
        """Retry tap installation with clean environment."""
        try:
            # Remove existing tap if present
            subprocess.run(
                ["brew", "untap", "scottryanhoward/homebrew-riveter"],
                capture_output=True,
                timeout=60,
            )

            # Add tap
            result = subprocess.run(
                ["brew", "tap", "scottryanhoward/homebrew-riveter"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Tap installation retry failed: {e}")
            return False

    def _check_github_connectivity(self) -> bool:
        """Check connectivity to GitHub."""
        try:
            import requests

            response = requests.get(
                "https://github.com/ScottRyanHoward/homebrew-riveter", timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"GitHub connectivity check failed: {e}")
            return False

    def _validate_formula_syntax(self) -> bool:
        """Validate formula syntax."""
        formula_path = self.project_root.parent / "homebrew-riveter" / "Formula" / "riveter.rb"

        if not formula_path.exists():
            logger.error("Formula file not found")
            return False

        try:
            # Check Ruby syntax
            result = subprocess.run(
                ["ruby", "-c", str(formula_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Formula syntax validation failed: {e}")
            return False

    def _check_formula_urls(self) -> bool:
        """Check formula download URLs."""
        try:
            import requests

            # This is a simplified check - in practice, you'd parse the formula
            # and check each URL
            test_urls = [
                "https://github.com/ScottRyanHoward/riveter/releases",
            ]

            for url in test_urls:
                response = requests.head(url, timeout=10)
                if response.status_code >= 400:
                    logger.error(f"URL check failed for {url}: {response.status_code}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Formula URL check failed: {e}")
            return False

    def _update_formula_checksums(self) -> bool:
        """Update formula checksums if needed."""
        # This would integrate with the version sync script
        try:
            sync_script = self.project_root / "scripts" / "sync_versions.py"
            if sync_script.exists():
                result = subprocess.run(
                    ["python", str(sync_script), "--update-formula"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                return result.returncode == 0
            else:
                logger.warning("Version sync script not found")
                return False

        except Exception as e:
            logger.error(f"Formula checksum update failed: {e}")
            return False

    def _retry_installation(self) -> bool:
        """Retry installation with clean environment."""
        try:
            # Uninstall if already installed
            subprocess.run(
                ["brew", "uninstall", "scottryanhoward/homebrew-riveter/riveter"],
                capture_output=True,
                timeout=60,
            )

            # Install
            result = subprocess.run(
                ["brew", "install", "scottryanhoward/homebrew-riveter/riveter"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Installation retry failed: {e}")
            return False

    def _check_dependencies(self) -> bool:
        """Check and install missing dependencies."""
        try:
            # Run brew doctor to check for issues
            result = subprocess.run(
                ["brew", "doctor"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            # brew doctor returns 0 if no issues, 1 if warnings/errors
            if result.returncode == 0:
                logger.info("No dependency issues found")
                return True
            else:
                logger.warning(f"Dependency issues detected: {result.stdout}")
                # Could implement specific fixes based on output
                return False

        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            return False

    def _sync_versions(self) -> bool:
        """Synchronize versions across components."""
        try:
            sync_script = self.project_root / "scripts" / "sync_versions.py"
            if sync_script.exists():
                result = subprocess.run(
                    ["python", str(sync_script), "--sync"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                return result.returncode == 0
            else:
                logger.warning("Version sync script not found")
                return False

        except Exception as e:
            logger.error(f"Version sync failed: {e}")
            return False

    def _validate_versions(self) -> bool:
        """Validate version consistency."""
        try:
            sync_script = self.project_root / "scripts" / "sync_versions.py"
            if sync_script.exists():
                result = subprocess.run(
                    ["python", str(sync_script), "--validate"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                return result.returncode == 0
            else:
                logger.warning("Version sync script not found")
                return False

        except Exception as e:
            logger.error(f"Version validation failed: {e}")
            return False

    def _check_network_connectivity(self) -> bool:
        """Check network connectivity to required services."""
        try:
            import requests

            services = [
                "https://github.com",
                "https://api.github.com",
                "https://raw.githubusercontent.com",
            ]

            for service in services:
                response = requests.get(service, timeout=10)
                if response.status_code >= 400:
                    logger.error(f"Network connectivity failed for {service}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Network connectivity check failed: {e}")
            return False

    def _retry_with_backoff(self) -> bool:
        """Retry operation with exponential backoff."""
        # This is a placeholder - the actual retry logic would be implemented
        # in the calling code using this recovery system
        logger.info("Exponential backoff retry recommended")
        return True

    def _check_homebrew_permissions(self) -> bool:
        """Check Homebrew directory permissions."""
        try:
            # Check common Homebrew directories
            homebrew_dirs = [
                "/usr/local/Homebrew",
                "/opt/homebrew",
                "/home/linuxbrew/.linuxbrew",
            ]

            for homebrew_dir in homebrew_dirs:
                if os.path.exists(homebrew_dir):
                    if not os.access(homebrew_dir, os.W_OK):
                        logger.error(f"No write access to {homebrew_dir}")
                        return False

            return True

        except Exception as e:
            logger.error(f"Permissions check failed: {e}")
            return False

    def _fix_homebrew_permissions(self) -> bool:
        """Fix Homebrew permissions."""
        try:
            # This is a simplified fix - in practice, you'd need to be more careful
            # about permissions and might need sudo
            subprocess.run(
                ["brew", "doctor"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            # If brew doctor suggests fixes, those would be implemented here
            return True

        except Exception as e:
            logger.error(f"Permissions fix failed: {e}")
            return False

    def create_error_report(self, diagnostic: ErrorDiagnostic) -> str:
        """Create a detailed error report.

        Args:
            diagnostic: Error diagnostic information

        Returns:
            Formatted error report as string
        """
        report = f"""# Homebrew Installation Error Report

## Error Summary
- **Type**: {diagnostic.error_type.value}
- **Message**: {diagnostic.error_message}
- **Exit Code**: {diagnostic.exit_code}
- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}

## Error Details
"""

        if diagnostic.stderr:
            report += f"""
### Error Output
```
{diagnostic.stderr}
```
"""

        if diagnostic.stdout:
            report += f"""
### Standard Output
```
{diagnostic.stdout}
```
"""

        if diagnostic.environment:
            report += f"""
### Environment
```json
{json.dumps(diagnostic.environment, indent=2)}
```
"""

        if diagnostic.recovery_actions:
            report += """
## Recovery Actions Attempted
"""
            for i, action in enumerate(diagnostic.recovery_actions, 1):
                report += f"""
### {i}. {action.name}
- **Description**: {action.description}
- **Retry Count**: {action.retry_count}
- **Delay**: {action.delay}s
"""

        report += """
## Manual Recovery Steps

If automated recovery fails, try these manual steps:

1. **Update Homebrew**:
   ```bash
   brew update
   brew doctor
   ```

2. **Clean Environment**:
   ```bash
   brew untap scottryanhoward/homebrew-riveter
   brew cleanup --prune=all
   ```

3. **Retry Installation**:
   ```bash
   brew tap scottryanhoward/homebrew-riveter
   brew install riveter
   ```

4. **Check Network Connectivity**:
   ```bash
   curl -I https://github.com/ScottRyanHoward/homebrew-riveter
   ```

5. **Validate Formula**:
   ```bash
   brew audit --strict riveter
   ```

## Support Information

- **Repository**: https://github.com/ScottRyanHoward/riveter
- **Homebrew Tap**: https://github.com/ScottRyanHoward/homebrew-riveter
- **Issues**: https://github.com/ScottRyanHoward/riveter/issues

---
Generated by Homebrew Error Recovery System
"""

        return report


def main():
    """Main entry point for the error recovery script."""
    parser = argparse.ArgumentParser(
        description="Homebrew installation error recovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--diagnose",
        help="Diagnose error from output file or stdin",
        metavar="ERROR_FILE",
    )

    parser.add_argument(
        "--exit-code",
        type=int,
        help="Exit code from failed command",
        default=1,
    )

    parser.add_argument(
        "--recover",
        action="store_true",
        help="Execute recovery actions after diagnosis",
    )

    parser.add_argument(
        "--report",
        help="Generate error report to file",
        metavar="REPORT_FILE",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    recovery = HomebrewErrorRecovery(debug=args.debug)

    if args.diagnose:
        # Read error output
        if args.diagnose == "-":
            error_output = sys.stdin.read()
        else:
            with open(args.diagnose, "r") as f:
                error_output = f.read()

        # Diagnose error
        diagnostic = recovery.diagnose_error(error_output, args.exit_code)

        print(f"Error Type: {diagnostic.error_type.value}")
        print(f"Error Message: {diagnostic.error_message}")
        print(f"Recovery Actions: {len(diagnostic.recovery_actions or [])}")

        # Generate report if requested
        if args.report:
            report = recovery.create_error_report(diagnostic)
            with open(args.report, "w") as f:
                f.write(report)
            print(f"Error report saved to: {args.report}")

        # Execute recovery if requested
        if args.recover:
            success = recovery.execute_recovery(diagnostic)
            sys.exit(0 if success else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
