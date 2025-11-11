#!/usr/bin/env python3
"""PyInstaller build script for Riveter binary distribution.

This script creates standalone executables for Riveter that include all
dependencies and can run without requiring Python to be installed.

Supports:
- Platform detection and cross-platform builds
- Command-line arguments for target platform specification
- Error handling and logging for build process
- Automatic inclusion of rule packs and static assets

Usage:
    python scripts/build_binary.py
    python scripts/build_binary.py --target macos-intel
    python scripts/build_binary.py --target linux-x86_64 --debug
"""

import argparse
import hashlib
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class BinaryBuilder:
    """Handles PyInstaller binary creation for Riveter."""

    SUPPORTED_PLATFORMS = {
        "macos-intel": {"os": "darwin", "arch": "x86_64"},
        "macos-arm64": {"os": "darwin", "arch": "arm64"},
        "linux-x86_64": {"os": "linux", "arch": "x86_64"},
    }

    def __init__(self, project_root: Path, debug: bool = False):
        """Initialize the binary builder.

        Args:
            project_root: Root directory of the Riveter project
            debug: Enable debug mode for verbose output
        """
        self.project_root = project_root
        self.debug = debug
        self.src_dir = project_root / "src"
        self.rule_packs_dir = project_root / "rule_packs"
        self.scripts_dir = project_root / "scripts"
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"

        if debug:
            logger.setLevel(logging.DEBUG)

    def detect_current_platform(self) -> str:
        """Detect the current platform and return the target identifier.

        Returns:
            Platform identifier (e.g., 'macos-intel', 'linux-x86_64')

        Raises:
            ValueError: If platform is not supported
        """
        system = platform.system().lower()
        machine = platform.machine().lower()

        logger.debug(f"Detected system: {system}, machine: {machine}")

        if system == "darwin":
            if machine in ["x86_64", "amd64"]:
                return "macos-intel"
            elif machine in ["arm64", "aarch64"]:
                return "macos-arm64"
            else:
                raise ValueError(f"Unsupported macOS architecture: {machine}")
        elif system == "linux":
            if machine in ["x86_64", "amd64"]:
                return "linux-x86_64"
            else:
                raise ValueError(f"Unsupported Linux architecture: {machine}")
        else:
            raise ValueError(f"Unsupported operating system: {system}")

    def validate_environment(self) -> None:
        """Validate that the build environment is properly set up.

        Raises:
            RuntimeError: If environment validation fails
        """
        logger.info("Validating build environment...")

        # Check if PyInstaller is available
        try:
            subprocess.run(
                [sys.executable, "-c", "import PyInstaller"],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug("PyInstaller is available")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "PyInstaller is not installed. Install it with: pip install pyinstaller"
            ) from e

        # Check if source directory exists
        if not self.src_dir.exists():
            raise RuntimeError(f"Source directory not found: {self.src_dir}")

        # Check if CLI entry point exists
        cli_path = self.src_dir / "riveter" / "cli.py"
        if not cli_path.exists():
            raise RuntimeError(f"CLI entry point not found: {cli_path}")

        # Check if rule packs directory exists
        if not self.rule_packs_dir.exists():
            logger.warning(f"Rule packs directory not found: {self.rule_packs_dir}")

        logger.info("Environment validation completed successfully")

    def clean_build_artifacts(self) -> None:
        """Clean previous build artifacts."""
        logger.info("Cleaning previous build artifacts...")

        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                logger.debug(f"Removing directory: {directory}")
                shutil.rmtree(directory)

        # Remove spec files
        for spec_file in self.project_root.glob("*.spec"):
            logger.debug(f"Removing spec file: {spec_file}")
            spec_file.unlink()

        logger.info("Build artifacts cleaned")

    def create_entry_script(self) -> Path:
        """Create a wrapper script for the CLI entry point."""
        entry_script = self.project_root / "riveter_entry.py"

        entry_content = '''#!/usr/bin/env python3
"""Entry point wrapper for Riveter CLI."""

import sys
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import and run main
from riveter.cli import main

if __name__ == "__main__":
    main()
'''

        with open(entry_script, "w") as f:
            f.write(entry_content)

        return entry_script

    def get_hidden_imports(self) -> List[str]:
        """Get list of hidden imports for PyInstaller.

        Returns:
            List of module names to include as hidden imports
        """
        hidden_imports = [
            # Core Riveter modules
            "riveter.cli",
            "riveter.scanner",
            "riveter.rules",
            "riveter.config",
            "riveter.extract_config",
            "riveter.logging",
            "riveter.performance",
            "riveter.reporter",
            "riveter.rule_distribution",
            "riveter.rule_filter",
            "riveter.rule_linter",
            "riveter.rule_packs",
            "riveter.rule_repository",
            "riveter.formatters",
            "riveter.operators",
            "riveter.exceptions",
            "riveter.cloud_parsers",
            "riveter.changelog_processor",
            "riveter.toml_handler",
            "riveter.version_manager",
            # Third-party dependencies that might need explicit inclusion
            "yaml",
            "hcl2",
            "hcl2.parser",
            "hcl2.api",
            "lark",
            "lark.parsers",
            "lark.parsers.lalr_parser",
            "lark.lexer",
            "lark.grammar",
            "lark.common",
            "lark.tree",
            "click",
            "rich",
            "cryptography",
            "requests",
            # Standard library modules that might be missed
            "json",
            "pathlib",
            "subprocess",
            "tempfile",
            "shutil",
            "os",
            "sys",
            "platform",
            "logging",
            "argparse",
            "re",
            "datetime",
            "hashlib",
            "base64",
        ]

        logger.debug(f"Hidden imports: {hidden_imports}")
        return hidden_imports

    def get_data_files(self) -> List[tuple[str, str]]:
        """Get list of data files to include in the binary.

        Returns:
            List of (source, destination) tuples for data files
        """
        data_files = []

        # Include rule packs if they exist
        if self.rule_packs_dir.exists():
            for rule_pack in self.rule_packs_dir.glob("*.yml"):
                data_files.append((str(rule_pack), "rule_packs"))
                logger.debug(f"Including rule pack: {rule_pack}")

        # Include HCL parser grammar files
        try:
            import hcl2

            hcl2_path = Path(hcl2.__file__).parent
            hcl2_lark = hcl2_path / "hcl2.lark"
            if hcl2_lark.exists():
                data_files.append((str(hcl2_lark), "hcl2"))
                logger.debug(f"Including HCL grammar file: {hcl2_lark}")
            else:
                logger.warning(f"HCL grammar file not found at {hcl2_lark}")
        except ImportError:
            logger.warning("hcl2 module not found, HCL parsing may not work in binary")

        # Include any other static assets
        # Add more data files here as needed

        logger.debug(f"Data files: {data_files}")
        return data_files

    def _update_version_file(self, version: str) -> None:
        """Update the _version.py file with the specified version.

        Args:
            version: Version string to set
        """
        version_file = self.project_root / "src" / "riveter" / "_version.py"
        if not version_file.exists():
            logger.warning(f"Version file not found: {version_file}")
            return

        try:
            with open(version_file, "r") as f:
                content = f.read()

            # Update the __version__ variable
            updated_content = re.sub(
                r'(__version__\s*=\s*["\'])[\d.]+(["\'])', f"\\g<1>{version}\\g<2>", content
            )

            with open(version_file, "w") as f:
                f.write(updated_content)

            logger.info(f"Updated version in _version.py to {version}")

        except Exception as e:
            logger.warning(f"Failed to update _version.py: {e}")

    def generate_spec_file(self, target_platform: str) -> Path:
        """Generate PyInstaller spec file for the target platform.

        Args:
            target_platform: Target platform identifier

        Returns:
            Path to the generated spec file
        """
        logger.info(f"Generating PyInstaller spec file for {target_platform}")

        # Import the spec generator
        import sys

        sys.path.insert(0, str(self.scripts_dir))
        from build_spec import generate_spec

        spec_path = self.project_root / f"riveter-{target_platform}.spec"

        # Create entry point wrapper script
        entry_script = self.create_entry_script()

        spec_content = generate_spec(
            entry_point=str(entry_script),
            hidden_imports=self.get_hidden_imports(),
            data_files=self.get_data_files(),
            target_platform=target_platform,
            debug=self.debug,
        )

        with open(spec_path, "w") as f:
            f.write(spec_content)

        logger.debug(f"Spec file generated: {spec_path}")
        return spec_path

    def run_pyinstaller(self, spec_file: Path, target_platform: str) -> None:
        """Run PyInstaller with the generated spec file.

        Args:
            spec_file: Path to the PyInstaller spec file
            target_platform: Target platform identifier

        Raises:
            RuntimeError: If PyInstaller build fails
        """
        logger.info(f"Building binary for {target_platform}...")

        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
        ]

        # Note: --debug flag is not compatible with spec files
        # Debug information is controlled by the spec file itself
        if not self.debug:
            cmd.append("--log-level=INFO")

        cmd.append(str(spec_file))

        logger.debug(f"PyInstaller command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=not self.debug, text=True, check=True
            )

            if not self.debug and result.stdout:
                logger.debug(f"PyInstaller stdout: {result.stdout}")

        except subprocess.CalledProcessError as e:
            error_msg = f"PyInstaller build failed with exit code {e.returncode}"
            if e.stderr:
                error_msg += f"\nError output: {e.stderr}"
            if e.stdout:
                error_msg += f"\nStandard output: {e.stdout}"
            raise RuntimeError(error_msg) from e

        logger.info("Binary build completed successfully")

        # Clean up entry script
        entry_script = self.project_root / "riveter_entry.py"
        if entry_script.exists():
            entry_script.unlink()
            logger.debug("Cleaned up entry script")

    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file.

        Args:
            file_path: Path to the file to checksum

        Returns:
            SHA256 checksum as hexadecimal string

        Raises:
            RuntimeError: If checksum calculation fails
        """
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

    def create_checksum_file(self, file_path: Path, checksum: str) -> Path:
        """Create a checksum file for the given file.

        Args:
            file_path: Path to the file that was checksummed
            checksum: SHA256 checksum as hexadecimal string

        Returns:
            Path to the created checksum file
        """
        checksum_path = file_path.with_suffix(file_path.suffix + ".sha256")

        # Write checksum in standard format: checksum filename
        with open(checksum_path, "w") as f:
            f.write(f"{checksum}  {file_path.name}\n")

        logger.debug(f"Created checksum file: {checksum_path}")
        return checksum_path

    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
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
                logger.debug(f"Checksum verification passed for {file_path}")
            else:
                logger.warning(
                    f"Checksum mismatch for {file_path}: "
                    f"expected {expected_checksum}, got {actual_checksum}"
                )

            return matches

        except Exception as e:
            logger.error(f"Checksum verification failed for {file_path}: {e}")
            return False

    def validate_binary(self, target_platform: str) -> None:
        """Validate that the built binary works correctly.

        Args:
            target_platform: Target platform identifier

        Raises:
            RuntimeError: If binary validation fails
        """
        logger.info("Validating built binary...")

        binary_path = self.dist_dir / "riveter"
        if not binary_path.exists():
            raise RuntimeError(f"Binary not found at expected location: {binary_path}")

        # Make binary executable on Unix systems
        if os.name != "nt":
            os.chmod(binary_path, 0o755)

        # Get expected version from pyproject.toml
        expected_version = self.get_pyproject_version()

        # Test basic functionality
        try:
            result = subprocess.run(
                [str(binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )

            logger.debug(f"Binary version output: {result.stdout.strip()}")

            # Validate that binary reports correct version
            if expected_version not in result.stdout:
                raise RuntimeError(
                    f"Binary version mismatch: expected {expected_version}, "
                    f"got {result.stdout.strip()}"
                )

            # Test help command
            result = subprocess.run(
                [str(binary_path), "--help"], capture_output=True, text=True, timeout=30, check=True
            )

            if "Riveter" not in result.stdout:
                raise RuntimeError("Binary help output doesn't contain expected content")

        except subprocess.TimeoutExpired as e:
            raise RuntimeError("Binary validation timed out") from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Binary validation failed: {e.stderr}") from e

        logger.info("Binary validation completed successfully")

    def get_pyproject_version(self) -> str:
        """Get version from pyproject.toml.

        Returns:
            Version string from pyproject.toml

        Raises:
            RuntimeError: If version cannot be read
        """
        pyproject_path = self.project_root / "pyproject.toml"

        try:
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            version = data.get("project", {}).get("version")
            if not version:
                raise RuntimeError("Version not found in pyproject.toml")

            return version
        except Exception as e:
            raise RuntimeError(f"Failed to read version from pyproject.toml: {e}") from e

    def create_archive_with_checksum(
        self, binary_path: Path, target_platform: str, version: Optional[str] = None
    ) -> Tuple[Path, str]:
        """Create a tar.gz archive of the binary with SHA256 checksum.

        Args:
            binary_path: Path to the built binary
            target_platform: Target platform identifier
            version: Version string for archive naming (optional)

        Returns:
            Tuple of (archive_path, sha256_checksum)

        Raises:
            RuntimeError: If archive creation fails
        """
        logger.info(f"Creating archive for {target_platform}")

        # Determine archive name
        if version:
            archive_name = f"riveter-{version}-{target_platform}"
        else:
            archive_name = f"riveter-{target_platform}"

        archive_dir = self.project_root / archive_name
        archive_path = self.project_root / f"{archive_name}.tar.gz"

        try:
            # Create directory for archive contents
            archive_dir.mkdir(exist_ok=True)

            # Copy binary to archive directory
            binary_name = "riveter.exe" if target_platform.startswith("windows") else "riveter"
            shutil.copy2(binary_path, archive_dir / binary_name)

            # Make binary executable in archive
            if not target_platform.startswith("windows"):
                os.chmod(archive_dir / binary_name, 0o755)

            # Create tar.gz archive
            import tarfile

            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(archive_dir, arcname=archive_name)

            # Calculate checksum
            checksum = self.calculate_sha256(archive_path)

            # Create checksum file
            self.create_checksum_file(archive_path, checksum)

            # Clean up temporary directory
            shutil.rmtree(archive_dir)

            logger.info(f"Archive created: {archive_path}")
            logger.info(f"SHA256 checksum: {checksum}")

            return archive_path, checksum

        except Exception as e:
            # Clean up on failure
            if archive_dir.exists():
                shutil.rmtree(archive_dir)
            if archive_path.exists():
                archive_path.unlink()
            raise RuntimeError(f"Failed to create archive: {e}") from e

    def build(
        self,
        target_platform: Optional[str] = None,
        create_archive: bool = False,
        version: Optional[str] = None,
    ) -> Path:
        """Build the binary for the specified or detected platform.

        Args:
            target_platform: Target platform identifier, auto-detected if None
            create_archive: Whether to create a tar.gz archive with checksum
            version: Version string for archive naming (optional)

        Returns:
            Path to the built binary (or archive if create_archive=True)

        Raises:
            ValueError: If target platform is not supported
            RuntimeError: If build process fails
        """
        if target_platform is None:
            target_platform = self.detect_current_platform()

        if target_platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(
                f"Unsupported target platform: {target_platform}. "
                f"Supported platforms: {list(self.SUPPORTED_PLATFORMS.keys())}"
            )

        logger.info(f"Building Riveter binary for {target_platform}")

        # Validate environment
        self.validate_environment()

        # Clean previous builds
        self.clean_build_artifacts()

        # Update version in _version.py if version is provided
        if version:
            self._update_version_file(version)

        # Generate spec file
        spec_file = self.generate_spec_file(target_platform)

        try:
            # Run PyInstaller
            self.run_pyinstaller(spec_file, target_platform)

            # Validate binary
            self.validate_binary(target_platform)

            binary_path = self.dist_dir / "riveter"
            logger.info(f"Binary successfully built: {binary_path}")

            # Create archive with checksum if requested
            if create_archive:
                archive_path, checksum = self.create_archive_with_checksum(
                    binary_path, target_platform, version
                )
                return archive_path

            return binary_path

        finally:
            # Clean up spec file
            if spec_file.exists():
                spec_file.unlink()


def main() -> None:
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(
        description="Build Riveter binary distribution using PyInstaller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_binary.py
  python scripts/build_binary.py --target macos-intel
  python scripts/build_binary.py --target linux-x86_64 --debug
  python scripts/build_binary.py --clean-only

Supported platforms:
  macos-intel   - macOS Intel (x86_64)
  macos-arm64   - macOS Apple Silicon (ARM64)
  linux-x86_64  - Linux x86_64
        """,
    )

    parser.add_argument(
        "--target",
        choices=list(BinaryBuilder.SUPPORTED_PLATFORMS.keys()),
        help="Target platform for binary build (auto-detected if not specified)",
    )

    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with verbose output"
    )

    parser.add_argument(
        "--clean-only", action="store_true", help="Only clean build artifacts, don't build"
    )

    parser.add_argument(
        "--create-archive", action="store_true", help="Create tar.gz archive with SHA256 checksum"
    )

    parser.add_argument("--version", help="Version string for archive naming")

    args = parser.parse_args()

    # Find project root (directory containing pyproject.toml)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent

    if not (project_root / "pyproject.toml").exists():
        logger.error("Could not find project root (pyproject.toml not found)")
        sys.exit(1)

    try:
        builder = BinaryBuilder(project_root, debug=args.debug)

        if args.clean_only:
            builder.clean_build_artifacts()
            logger.info("Build artifacts cleaned successfully")
            return

        result_path = builder.build(
            args.target, create_archive=args.create_archive, version=args.version
        )

        print("\n✅ Binary build completed successfully!")

        if args.create_archive:
            print(f"📦 Archive location: {result_path}")
            # Show archive size
            size_mb = result_path.stat().st_size / (1024 * 1024)
            print(f"📏 Archive size: {size_mb:.1f} MB")

            # Show checksum file
            checksum_file = result_path.with_suffix(result_path.suffix + ".sha256")
            if checksum_file.exists():
                print(f"🔐 Checksum file: {checksum_file}")
                with open(checksum_file, "r") as f:
                    print(f"🔐 SHA256: {f.read().strip().split()[0]}")
        else:
            print(f"📦 Binary location: {result_path}")
            # Show binary size
            size_mb = result_path.stat().st_size / (1024 * 1024)
            print(f"📏 Binary size: {size_mb:.1f} MB")

        print(f"🎯 Target platform: {args.target or builder.detect_current_platform()}")

    except Exception as e:
        logger.error(f"Build failed: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
