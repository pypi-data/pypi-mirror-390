#!/usr/bin/env python3
"""Install Git hooks for version consistency validation.

This script installs pre-commit hooks that validate version consistency
before allowing commits. This helps prevent version mismatches from
being committed to the repository.

Usage:
    python scripts/install_hooks.py
    python scripts/install_hooks.py --uninstall
"""

import argparse
import shutil
import stat
import sys
from pathlib import Path


def install_pre_commit_hook(project_root: Path, force: bool = False) -> bool:
    """Install the pre-commit hook for version validation.

    Args:
        project_root: Root directory of the project
        force: Whether to overwrite existing hooks

    Returns:
        True if installation was successful, False otherwise
    """
    hooks_dir = project_root / ".git" / "hooks"
    source_hook = project_root / ".github" / "hooks" / "pre-commit-version-check"
    target_hook = hooks_dir / "pre-commit"

    # Check if .git directory exists
    if not hooks_dir.parent.exists():
        print("❌ Not a Git repository (no .git directory found)")
        return False

    # Create hooks directory if it doesn't exist
    hooks_dir.mkdir(exist_ok=True)

    # Check if source hook exists
    if not source_hook.exists():
        print(f"❌ Source hook not found: {source_hook}")
        return False

    # Check if target hook already exists
    if target_hook.exists() and not force:
        print(f"⚠️ Pre-commit hook already exists: {target_hook}")
        print("Use --force to overwrite, or --uninstall to remove")
        return False

    try:
        # Copy the hook
        shutil.copy2(source_hook, target_hook)

        # Make it executable
        current_permissions = target_hook.stat().st_mode
        target_hook.chmod(current_permissions | stat.S_IEXEC)

        print(f"✅ Pre-commit hook installed: {target_hook}")
        print("🔍 Version consistency will be validated before each commit")
        return True

    except Exception as e:
        print(f"❌ Failed to install pre-commit hook: {e}")
        return False


def uninstall_pre_commit_hook(project_root: Path) -> bool:
    """Uninstall the pre-commit hook.

    Args:
        project_root: Root directory of the project

    Returns:
        True if uninstallation was successful, False otherwise
    """
    hooks_dir = project_root / ".git" / "hooks"
    target_hook = hooks_dir / "pre-commit"

    if not target_hook.exists():
        print("ℹ️ Pre-commit hook not found (already uninstalled)")
        return True

    try:
        target_hook.unlink()
        print(f"✅ Pre-commit hook uninstalled: {target_hook}")
        return True

    except Exception as e:
        print(f"❌ Failed to uninstall pre-commit hook: {e}")
        return False


def check_hook_status(project_root: Path) -> None:
    """Check the current status of Git hooks.

    Args:
        project_root: Root directory of the project
    """
    hooks_dir = project_root / ".git" / "hooks"
    target_hook = hooks_dir / "pre-commit"

    print("🔍 Git Hooks Status:")
    print(f"  Repository: {project_root}")
    print(f"  Hooks directory: {hooks_dir}")

    if not hooks_dir.exists():
        print("  Status: ❌ No .git/hooks directory")
        return

    if target_hook.exists():
        # Check if it's our hook
        try:
            with open(target_hook, "r") as f:
                content = f.read()

            if "version consistency check" in content:
                print("  Pre-commit hook: ✅ Installed (version validation)")
            else:
                print("  Pre-commit hook: ⚠️ Installed (different hook)")
        except Exception:
            print("  Pre-commit hook: ⚠️ Installed (cannot read)")
    else:
        print("  Pre-commit hook: ❌ Not installed")

    # List other hooks
    if hooks_dir.exists():
        other_hooks = [f for f in hooks_dir.iterdir() if f.is_file() and f.name != "pre-commit"]
        if other_hooks:
            print(f"  Other hooks: {len(other_hooks)} found")
            for hook in other_hooks:
                print(f"    - {hook.name}")
        else:
            print("  Other hooks: None")


def main() -> None:
    """Main entry point for the hook installation script."""
    parser = argparse.ArgumentParser(
        description="Install Git hooks for version consistency validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/install_hooks.py
  python scripts/install_hooks.py --force
  python scripts/install_hooks.py --uninstall
  python scripts/install_hooks.py --status

The pre-commit hook will validate version consistency before each commit,
preventing version mismatches from being committed to the repository.
        """,
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing pre-commit hook",
    )

    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Uninstall the pre-commit hook",
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Check the current status of Git hooks",
    )

    args = parser.parse_args()

    # Find project root (directory containing pyproject.toml)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent

    if not (project_root / "pyproject.toml").exists():
        print("❌ Could not find project root (pyproject.toml not found)")
        sys.exit(1)

    try:
        if args.status:
            check_hook_status(project_root)
        elif args.uninstall:
            if uninstall_pre_commit_hook(project_root):
                print("\n✅ Pre-commit hook uninstalled successfully")
            else:
                print("\n❌ Failed to uninstall pre-commit hook")
                sys.exit(1)
        else:
            if install_pre_commit_hook(project_root, force=args.force):
                print("\n✅ Pre-commit hook installed successfully")
                print("\nNext steps:")
                print("1. Version consistency will be validated before each commit")
                print("2. If validation fails, run: python scripts/sync_versions.py --sync")
                print("3. To bypass validation (not recommended): git commit --no-verify")
            else:
                print("\n❌ Failed to install pre-commit hook")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
