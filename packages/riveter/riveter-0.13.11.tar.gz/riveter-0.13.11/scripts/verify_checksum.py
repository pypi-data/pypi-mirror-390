#!/usr/bin/env python3
"""Checksum verification utility for Riveter binary distributions.

This script provides utilities for verifying SHA256 checksums of Riveter
binary distributions to ensure integrity and authenticity.

Usage:
    python scripts/verify_checksum.py <file_path> <expected_checksum>
    python scripts/verify_checksum.py <file_path> --checksum-file <checksum_file>
    python scripts/verify_checksum.py --verify-release <version> --platform <platform>
"""

import argparse
import hashlib
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ChecksumVerifier:
    """Handles checksum verification for Riveter binary distributions."""

    GITHUB_REPO = "riveter/riveter"
    SUPPORTED_PLATFORMS = ["macos-intel", "macos-arm64", "linux-x86_64"]

    def __init__(self, debug: bool = False):
        """Initialize the checksum verifier.

        Args:
            debug: Enable debug mode for verbose output
        """
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)

    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file.

        Args:
            file_path: Path to the file to checksum

        Returns:
            SHA256 checksum as hexadecimal string

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If checksum calculation fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.debug(f"Calculating SHA256 checksum for {file_path}")

        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            checksum = sha256_hash.hexdigest()
            logger.debug(f"SHA256 checksum: {checksum}")
            return checksum

        except Exception as e:
            raise RuntimeError(f"Failed to calculate SHA256 checksum: {e}") from e

    def read_checksum_file(self, checksum_file: Path) -> Tuple[str, str]:
        """Read checksum and filename from a checksum file.

        Args:
            checksum_file: Path to the checksum file

        Returns:
            Tuple of (checksum, filename)

        Raises:
            FileNotFoundError: If checksum file doesn't exist
            ValueError: If checksum file format is invalid
        """
        if not checksum_file.exists():
            raise FileNotFoundError(f"Checksum file not found: {checksum_file}")

        try:
            with open(checksum_file, "r") as f:
                content = f.read().strip()

            # Parse standard checksum format: "checksum  filename"
            parts = content.split(None, 1)  # Split on whitespace, max 1 split
            if len(parts) != 2:
                raise ValueError("Invalid checksum file format")

            checksum, filename = parts

            # Validate checksum format (64 hex characters for SHA256)
            if len(checksum) != 64 or not all(c in "0123456789abcdefABCDEF" for c in checksum):
                raise ValueError("Invalid SHA256 checksum format")

            logger.debug(f"Read checksum from file: {checksum} for {filename}")
            return checksum.lower(), filename

        except Exception as e:
            raise ValueError(f"Failed to read checksum file: {e}") from e

    def verify_file_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify that a file matches the expected SHA256 checksum.

        Args:
            file_path: Path to the file to verify
            expected_checksum: Expected SHA256 checksum as hexadecimal string

        Returns:
            True if checksum matches, False otherwise
        """
        try:
            actual_checksum = self.calculate_sha256(file_path)
            matches = actual_checksum.lower() == expected_checksum.lower()

            if matches:
                logger.info(f"✅ Checksum verification passed for {file_path.name}")
                logger.debug(f"Checksum: {actual_checksum}")
            else:
                logger.error(f"❌ Checksum verification failed for {file_path.name}")
                logger.error(f"Expected: {expected_checksum.lower()}")
                logger.error(f"Actual:   {actual_checksum.lower()}")

            return matches

        except Exception as e:
            logger.error(f"Checksum verification failed for {file_path}: {e}")
            return False

    def verify_with_checksum_file(self, file_path: Path, checksum_file: Path) -> bool:
        """Verify a file using a separate checksum file.

        Args:
            file_path: Path to the file to verify
            checksum_file: Path to the checksum file

        Returns:
            True if verification passes, False otherwise
        """
        try:
            expected_checksum, expected_filename = self.read_checksum_file(checksum_file)

            # Verify filename matches (optional check)
            if file_path.name != expected_filename:
                logger.warning(
                    f"Filename mismatch: expected {expected_filename}, got {file_path.name}"
                )
                logger.warning("Proceeding with checksum verification anyway...")

            return self.verify_file_checksum(file_path, expected_checksum)

        except Exception as e:
            logger.error(f"Verification with checksum file failed: {e}")
            return False

    def download_release_checksum(self, version: str, platform: str) -> Optional[str]:
        """Download checksum for a specific release from GitHub.

        Args:
            version: Release version (e.g., "1.2.3" or "v1.2.3")
            platform: Platform identifier (e.g., "macos-intel", "linux-x86_64")

        Returns:
            SHA256 checksum string if found, None otherwise
        """
        # Normalize version (ensure it starts with 'v')
        if not version.startswith("v"):
            version = f"v{version}"

        if platform not in self.SUPPORTED_PLATFORMS:
            logger.error(f"Unsupported platform: {platform}")
            logger.error(f"Supported platforms: {', '.join(self.SUPPORTED_PLATFORMS)}")
            return None

        # Construct checksum file URL
        checksum_filename = f"riveter-{version[1:]}-{platform}.tar.gz.sha256"
        url = (
            f"https://github.com/{self.GITHUB_REPO}/releases/download/{version}/{checksum_filename}"
        )

        logger.debug(f"Downloading checksum from: {url}")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Parse checksum from response
            content = response.text.strip()
            checksum = content.split()[0]  # First part is the checksum

            logger.debug(f"Downloaded checksum: {checksum}")
            return checksum.lower()

        except requests.RequestException as e:
            logger.error(f"Failed to download checksum from GitHub: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to parse downloaded checksum: {e}")
            return None

    def verify_release_binary(self, file_path: Path, version: str, platform: str) -> bool:
        """Verify a binary against the official release checksum.

        Args:
            file_path: Path to the binary file to verify
            version: Release version
            platform: Platform identifier

        Returns:
            True if verification passes, False otherwise
        """
        logger.info(f"Verifying {file_path.name} against release {version} for {platform}")

        # Download official checksum
        expected_checksum = self.download_release_checksum(version, platform)
        if expected_checksum is None:
            logger.error("Failed to download official checksum")
            return False

        # Verify file
        return self.verify_file_checksum(file_path, expected_checksum)


def main() -> None:
    """Main entry point for the checksum verification script."""
    parser = argparse.ArgumentParser(
        description="Verify SHA256 checksums for Riveter binary distributions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify with explicit checksum
  python scripts/verify_checksum.py riveter-1.2.3-macos-intel.tar.gz abc123...

  # Verify with checksum file
  python scripts/verify_checksum.py riveter-1.2.3-macos-intel.tar.gz \\
      --checksum-file riveter-1.2.3-macos-intel.tar.gz.sha256

  # Verify against official release
  python scripts/verify_checksum.py riveter-1.2.3-macos-intel.tar.gz \\
      --verify-release 1.2.3 --platform macos-intel

Supported platforms:
  macos-intel   - macOS Intel (x86_64)
  macos-arm64   - macOS Apple Silicon (ARM64)
  linux-x86_64  - Linux x86_64
        """,
    )

    parser.add_argument("file_path", type=Path, help="Path to the file to verify")

    parser.add_argument(
        "expected_checksum",
        nargs="?",
        help="Expected SHA256 checksum (if not using --checksum-file or --verify-release)",
    )

    parser.add_argument(
        "--checksum-file", type=Path, help="Path to checksum file containing expected checksum"
    )

    parser.add_argument(
        "--verify-release", help="Verify against official release checksum (specify version)"
    )

    parser.add_argument(
        "--platform",
        choices=ChecksumVerifier.SUPPORTED_PLATFORMS,
        help="Platform identifier (required with --verify-release)",
    )

    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with verbose output"
    )

    args = parser.parse_args()

    # Validate arguments
    verification_methods = sum(
        [bool(args.expected_checksum), bool(args.checksum_file), bool(args.verify_release)]
    )

    if verification_methods == 0:
        parser.error("Must specify one of: expected_checksum, --checksum-file, or --verify-release")
    elif verification_methods > 1:
        parser.error("Cannot specify multiple verification methods")

    if args.verify_release and not args.platform:
        parser.error("--platform is required when using --verify-release")

    try:
        verifier = ChecksumVerifier(debug=args.debug)

        # Perform verification based on method
        if args.expected_checksum:
            success = verifier.verify_file_checksum(args.file_path, args.expected_checksum)
        elif args.checksum_file:
            success = verifier.verify_with_checksum_file(args.file_path, args.checksum_file)
        elif args.verify_release:
            success = verifier.verify_release_binary(
                args.file_path, args.verify_release, args.platform
            )

        if success:
            print(f"\n✅ Checksum verification passed for {args.file_path.name}")
            print("The file integrity has been verified successfully.")
            sys.exit(0)
        else:
            print(f"\n❌ Checksum verification failed for {args.file_path.name}")
            print("The file may be corrupted or tampered with.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
