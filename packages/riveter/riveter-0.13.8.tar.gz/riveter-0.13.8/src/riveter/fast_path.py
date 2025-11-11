# type: ignore
"""Fast path command detection and execution for Riveter CLI performance optimization.

This module provides lightweight command detection and execution paths for basic
CLI operations like --version and --help, avoiding heavy imports and Click
framework overhead for simple commands.

The fast path router:
- Detects command type before any heavy imports
- Routes lightweight commands through optimized execution paths
- Maintains complete backward compatibility with existing CLI
- Preserves identical output formatting and behavior
"""

import sys
from typing import Any


class FastPathRouter:
    """Lightweight command router for performance-critical CLI operations.

    This class provides minimal argument parsing to detect command types
    and route them through optimized execution paths when possible.

    Performance optimizations:
    - Cached version information
    - Minimal import overhead
    - Lazy loading of dependencies
    - Intelligent command detection
    """

    def __init__(self) -> None:
        """Initialize the fast path router."""
        self._version_cache: str | None = None
        self._rule_pack_cache: list[dict[str, Any]] | None = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl: float = 300.0  # 5 minutes cache TTL

    def is_lightweight_command(self, args: list[str]) -> bool:
        """Determine if the command can use fast path execution.

        Args:
            args: Command line arguments (excluding program name)

        Returns:
            True if command can use fast path, False otherwise
        """
        if not args:
            return False

        # Check for version flags (highest priority for performance)
        if any(arg in ["--version", "-V"] for arg in args):
            return True

        # Check for help flags
        if any(arg in ["--help", "-h"] for arg in args):
            return True

        # Check for basic commands that can be optimized
        if args[0] in ["list-rule-packs", "list-installed-packs"]:
            # Only if no complex options are present
            complex_options = [
                "--format",
                "--debug",
                "--log-level",
                "--verbose",
                "--config",
                "--rule-dirs",
                "--environment",
            ]
            if not any(opt in args for opt in complex_options):
                return True

        # Check for simple validation commands
        if args[0] == "validate-rule-pack" and len(args) == 2:
            # Simple validation without complex options
            return True

        return False

    def route_command(self, args: list[str]) -> int | None:
        """Route command to fast path execution if possible.

        Args:
            args: Command line arguments (excluding program name)

        Returns:
            Exit code if command was handled, None if should delegate to full CLI
        """
        if not self.is_lightweight_command(args):
            return None

        try:
            # Handle version commands
            if any(arg in ["--version", "-V"] for arg in args):
                return self._safe_execute(self._handle_version)

            # Handle help commands
            if any(arg in ["--help", "-h"] for arg in args):
                return self._safe_execute(self._handle_help, args)

            # Handle basic list commands
            if args[0] == "list-rule-packs":
                return self._safe_execute(self._handle_list_rule_packs)

            if args[0] == "list-installed-packs":
                return self._safe_execute(self._handle_list_installed_packs)

        except Exception as e:
            # Log error for debugging but don't fail
            self._log_fallback_reason("route_command", str(e))
            return None

        return None

    def _safe_execute(self, handler_func: Any, *args: Any) -> int | None:
        """Safely execute a handler function with fallback on failure.

        Args:
            handler_func: The handler function to execute
            *args: Arguments to pass to the handler function

        Returns:
            Exit code if successful, None to trigger fallback
        """
        try:
            result = handler_func(*args) if args else handler_func()
            return int(result) if result is not None else 0
        except ImportError as e:
            # Module import failed - likely missing dependencies
            self._log_fallback_reason("import_error", f"Failed to import required module: {e!s}")
            return None
        except FileNotFoundError as e:
            # File or directory not found - delegate to full CLI for better error handling
            self._log_fallback_reason("file_not_found", str(e))
            return None
        except PermissionError as e:
            # Permission issues - delegate to full CLI
            self._log_fallback_reason("permission_error", str(e))
            return None
        except Exception as e:
            # Any other error - delegate to full CLI for proper error handling
            self._log_fallback_reason("unexpected_error", str(e))
            return None

    def _log_fallback_reason(self, error_type: str, message: str) -> None:
        """Log the reason for falling back to full CLI.

        Args:
            error_type: Type of error that caused fallback
            message: Error message
        """
        # Only log if debug mode is enabled
        import os

        if os.getenv("RIVETER_DEBUG_FAST_PATH", "").lower() in ("1", "true", "yes"):
            print(f"Fast path fallback ({error_type}): {message}", file=sys.stderr)

    def _handle_version(self) -> int:
        """Handle version command with fast path and simplified fallback strategies.

        Returns:
            Exit code (0 for success)
        """
        if self._version_cache is None:
            # Strategy 1: Try importlib.metadata (most reliable)
            try:
                import importlib.metadata

                self._version_cache = importlib.metadata.version("riveter")
            except Exception:
                # Strategy 2: Try reading from pyproject.toml
                try:
                    self._version_cache = self._read_version_from_pyproject()
                except Exception:
                    # Final fallback
                    self._version_cache = "unknown"

        print(f"riveter, version {self._version_cache}")
        return 0

    def _read_version_from_pyproject(self) -> str:
        """Read version directly from pyproject.toml as fallback.

        Returns:
            Version string from pyproject.toml

        Raises:
            Exception: If version cannot be read
        """
        from pathlib import Path

        # Find pyproject.toml file
        current_dir = Path(__file__).parent
        for _ in range(5):  # Search up to 5 levels up
            pyproject_path = current_dir / "pyproject.toml"
            if pyproject_path.exists():
                break
            current_dir = current_dir.parent
        else:
            raise FileNotFoundError("pyproject.toml not found")

        # Read version from pyproject.toml
        with open(pyproject_path, encoding="utf-8") as f:
            content = f.read()

        # Simple regex to extract version
        import re

        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if version_match:
            return version_match.group(1)

        raise ValueError("Version not found in pyproject.toml")

    def _handle_help(self, args: list[str]) -> int | None:
        """Handle help command with fast path.

        Args:
            args: Command line arguments

        Returns:
            Exit code if handled, None to delegate to full CLI
        """
        # For complex help requests, delegate to full CLI
        if len(args) > 1 and args[1] not in ["--help", "-h"]:
            return None

        # Basic help output
        help_text = """Usage: riveter [OPTIONS] COMMAND [ARGS]...

  Riveter - Infrastructure Rule Enforcement as Code.

  Riveter is a command-line tool for validating Terraform configurations
  against custom rules and compliance standards. It supports multiple cloud
  providers, advanced rule operators, and various output formats.

  Use 'riveter COMMAND --help' for more information on specific commands.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  scan                      Validate Terraform configuration against rules.
  list-rule-packs          List all available rule packs.
  validate-rule-pack       Validate a rule pack file.
  create-rule-pack-template Create a template rule pack file.
  create-config            Create a sample configuration file.
  validate-rules           Validate rule syntax and best practices.
  install-rule-pack        Install a rule pack from a repository.
  update-rule-packs        Update installed rule packs to latest versions.
  list-installed-packs     List all installed rule packs.
"""
        print(help_text)
        return 0

    def _handle_list_rule_packs(self) -> int | None:
        """Handle list-rule-packs command with fast path (simplified to avoid hanging).

        Returns:
            Exit code if handled, None to delegate to full CLI
        """
        # For now, delegate to full CLI to avoid any potential hanging issues
        # The fast path optimization can be re-enabled once the cache issues are resolved
        return None

    def _handle_list_installed_packs(self) -> int | None:
        """Handle list-installed-packs command with fast path (simplified to avoid hanging).

        Returns:
            Exit code if handled, None to delegate to full CLI
        """
        # For now, delegate to full CLI to avoid any potential hanging issues
        # The fast path optimization can be re-enabled once the cache issues are resolved
        return None


def create_fast_path_entry_point() -> int:
    """Create a fast path entry point that routes commands efficiently.

    This function serves as the main entry point and decides whether to use
    fast path execution or delegate to the full CLI framework.

    Returns:
        Exit code from command execution
    """
    # Get command line arguments (excluding program name)
    args = sys.argv[1:]

    # Initialize fast path router
    router = FastPathRouter()

    # Try fast path execution first
    exit_code = router.route_command(args)

    if exit_code is not None:
        # Fast path handled the command
        return exit_code

    # Delegate to full CLI for complex commands
    try:
        from .cli import main

        main()
        return 0
    except SystemExit as e:
        return e.code if e.code is not None else 0
    except Exception:
        return 1


# For backward compatibility, expose the original main function
def main() -> None:
    """Main entry point with fast path routing."""
    exit_code = create_fast_path_entry_point()
    if exit_code != 0:
        sys.exit(exit_code)
