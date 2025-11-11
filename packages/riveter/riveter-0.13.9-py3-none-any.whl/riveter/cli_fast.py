# type: ignore
"""Simple CLI entry point without performance optimizations.

This module provides a straightforward entry point for the Riveter CLI
without any complex performance optimizations that were causing hanging issues.
"""

import sys


def main() -> None:
    """Simple main CLI entry point."""
    try:
        # Import and run the main CLI directly
        from .cli import main as cli_main

        cli_main()

    except ImportError as e:
        print(f"Error: Cannot import CLI module: {e}", file=sys.stderr)
        print("Please check your Riveter installation.", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        # Let SystemExit propagate normally
        raise
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
