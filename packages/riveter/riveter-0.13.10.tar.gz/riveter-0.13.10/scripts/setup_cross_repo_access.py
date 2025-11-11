#!/usr/bin/env python3
"""Setup script for cross-repository access tokens.

This script helps configure the necessary GitHub tokens for cross-repository
operations between the riveter and homebrew-riveter repositories.

Usage:
    python scripts/setup_cross_repo_access.py --check
    python scripts/setup_cross_repo_access.py --instructions
"""

import argparse
import sys


def check_token_requirements():
    """Check if the necessary tokens are configured."""
    print("🔍 Checking cross-repository access configuration...")
    print()

    print("📋 Required for cross-repository operations:")
    print("1. HOMEBREW_UPDATE_TOKEN secret (recommended)")
    print("   - OR -")
    print("2. GITHUB_TOKEN with appropriate permissions (fallback)")
    print()

    print("🔗 Repository connections needed:")
    print("- Source: ScottRyanHoward/riveter")
    print("- Target: ScottRyanHoward/homebrew-riveter")
    print()

    print("✅ Current setup should work because:")
    print("- Both repositories are owned by the same user")
    print("- GITHUB_TOKEN has access to same-user repositories")
    print("- Workflow uses fallback: HOMEBREW_UPDATE_TOKEN || GITHUB_TOKEN")
    print()

    print("⚠️ You may need HOMEBREW_UPDATE_TOKEN if:")
    print("- The homebrew repository becomes private")
    print("- You want more granular permissions")
    print("- GITHUB_TOKEN permissions are restricted")


def show_setup_instructions():
    """Show detailed setup instructions for the token."""
    print("🔧 Setup Instructions for Cross-Repository Access")
    print("=" * 60)
    print()

    print("## Option 1: Use Default GITHUB_TOKEN (Recommended)")
    print()
    print("The workflow is configured to use the automatic GITHUB_TOKEN first.")
    print("This should work for same-user repositories without additional setup.")
    print()
    print("✅ No action required if both repos are owned by the same user!")
    print()

    print("## Option 2: Create Personal Access Token (If Needed)")
    print()
    print("If you encounter permission issues, create a Personal Access Token:")
    print()
    print("### Step 1: Create the Token")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token' → 'Generate new token (classic)'")
    print("3. Set expiration (recommend 90 days)")
    print("4. Select scopes:")
    print("   ✅ repo (Full control of private repositories)")
    print("   ✅ workflow (Update GitHub Action workflows)")
    print("5. Click 'Generate token'")
    print("6. Copy the token (you won't see it again!)")
    print()

    print("### Step 2: Add to Repository Secrets")
    print("1. Go to: https://github.com/ScottRyanHoward/riveter/settings/secrets/actions")
    print("2. Click 'New repository secret'")
    print("3. Name: HOMEBREW_UPDATE_TOKEN")
    print("4. Value: [paste your token]")
    print("5. Click 'Add secret'")
    print()

    print("### Step 3: Verify Setup")
    print("Run a test workflow or check the workflow logs to ensure:")
    print("- Token has access to both repositories")
    print("- Can checkout the homebrew-riveter repository")
    print("- Can push commits to the homebrew repository")
    print()

    print("## Security Best Practices")
    print()
    print("🔒 Token Security:")
    print("- Use minimal required permissions")
    print("- Set reasonable expiration dates")
    print("- Rotate tokens regularly")
    print("- Monitor token usage in GitHub settings")
    print()
    print("🔒 Repository Security:")
    print("- Workflow pushes directly to main (no PR approval needed)")
    print("- Commits are signed by github-actions[bot]")
    print("- All changes are tracked in git history")
    print("- Formula syntax is validated before commit")


def test_repository_access():
    """Test if we can access the required repositories."""
    print("🧪 Testing repository access...")
    print()

    try:
        import requests

        # Test access to main repository
        print("📡 Testing access to ScottRyanHoward/riveter...")
        response = requests.get("https://api.github.com/repos/ScottRyanHoward/riveter")
        if response.status_code == 200:
            print("✅ Main repository is accessible")
        else:
            print(f"❌ Main repository access failed: {response.status_code}")

        # Test access to homebrew repository
        print("📡 Testing access to ScottRyanHoward/homebrew-riveter...")
        response = requests.get("https://api.github.com/repos/ScottRyanHoward/homebrew-riveter")
        if response.status_code == 200:
            print("✅ Homebrew repository is accessible")
        else:
            print(f"❌ Homebrew repository access failed: {response.status_code}")
            print("   This may indicate the repository is private or doesn't exist")

    except ImportError:
        print("⚠️ requests library not available, skipping API tests")
        print("   Install with: pip install requests")
    except Exception as e:
        print(f"❌ Error testing repository access: {e}")

    print()
    print("💡 Note: These tests only check public API access.")
    print("   Actual workflow permissions may differ.")


def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="Setup cross-repository access for Homebrew formula updates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup_cross_repo_access.py --check
  python scripts/setup_cross_repo_access.py --instructions
  python scripts/setup_cross_repo_access.py --test

This script helps configure GitHub tokens for automatic Homebrew formula updates.
        """,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current token configuration requirements",
    )

    parser.add_argument(
        "--instructions",
        action="store_true",
        help="Show detailed setup instructions",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Test repository access",
    )

    args = parser.parse_args()

    if not any([args.check, args.instructions, args.test]):
        parser.print_help()
        return

    try:
        if args.check:
            check_token_requirements()

        if args.instructions:
            show_setup_instructions()

        if args.test:
            test_repository_access()

    except KeyboardInterrupt:
        print("\n⚠️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
