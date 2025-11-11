"""TOML file handling with validation and error recovery.

This module provides robust TOML file operations with:
- Reading using tomllib (Python 3.11+ built-in)
- Writing using tomli-w
- Structure validation
- Error handling and recovery
- Formatting preservation where possible
"""

import re
from pathlib import Path
from typing import Any, Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None

try:
    import tomli_w
except ImportError:
    tomli_w = None


class TOMLError(Exception):
    """Base exception for TOML operations."""

    pass


class TOMLReadError(TOMLError):
    """Exception raised when reading TOML files fails."""

    pass


class TOMLWriteError(TOMLError):
    """Exception raised when writing TOML files fails."""

    pass


class TOMLValidationError(TOMLError):
    """Exception raised when TOML validation fails."""

    pass


class TOMLHandler:
    """Handles TOML file operations with validation and error recovery."""

    def __init__(self, file_path: Path) -> None:
        """Initialize TOML handler.

        Args:
            file_path: Path to the TOML file.
        """
        self.file_path = Path(file_path)
        self._original_content: Optional[str] = None
        self._parsed_data: Optional[dict[str, Any]] = None

    def read(self) -> dict[str, Any]:
        """Read and parse TOML file using tomllib.

        Returns:
            Parsed TOML data as dictionary.

        Raises:
            TOMLReadError: If file cannot be read or parsed.
        """
        if not self.file_path.exists():
            raise TOMLReadError(f"TOML file not found: {self.file_path}")

        try:
            # Store original content for potential recovery
            self._original_content = self.file_path.read_text(encoding="utf-8")

            # Parse using tomllib (Python 3.11+ built-in) or tomli fallback
            if tomllib is None:
                raise TOMLReadError("tomllib/tomli not available. Install with: pip install tomli")

            with open(self.file_path, "rb") as f:
                self._parsed_data = tomllib.load(f)

            return self._parsed_data

        except Exception as e:
            if "TOMLDecodeError" in str(type(e)) or "tomllib" in str(type(e)):
                raise TOMLReadError(f"Failed to parse TOML file {self.file_path}: {e}") from e
            else:
                raise TOMLReadError(f"Failed to parse TOML file {self.file_path}: {e}") from e
        except OSError as e:
            raise TOMLReadError(f"Failed to read TOML file {self.file_path}: {e}") from e
        except (ValueError, TypeError) as e:
            raise TOMLReadError(f"Invalid TOML format in {self.file_path}: {e}") from e

    def write(self, data: dict[str, Any], *, preserve_formatting: bool = True) -> None:
        """Write data to TOML file using tomli-w.

        Args:
            data: Dictionary to write as TOML.
            preserve_formatting: If True, attempts to preserve original formatting
                                for simple updates. If False, writes fresh TOML.

        Raises:
            TOMLWriteError: If file cannot be written.
        """
        if tomli_w is None:
            raise TOMLWriteError(
                "tomli-w package is required for writing TOML files. "
                "Install it with: pip install tomli-w"
            )

        try:
            # Validate data can be serialized to TOML
            self._validate_toml_data(data)

            # If preserve_formatting is True and we have original content,
            # try to preserve formatting for simple updates
            if preserve_formatting and self._original_content and self._parsed_data:
                try:
                    preserved_content = self._preserve_formatting_update(
                        self._original_content, self._parsed_data, data
                    )
                    if preserved_content:
                        self.file_path.write_text(preserved_content, encoding="utf-8")
                        return
                except Exception:
                    # Fall back to standard write if preservation fails
                    pass

            # Standard write using tomli-w
            toml_string = tomli_w.dumps(data)
            self.file_path.write_text(toml_string, encoding="utf-8")

        except OSError as e:
            raise TOMLWriteError(f"Failed to write TOML file {self.file_path}: {e}") from e
        except Exception as e:
            raise TOMLWriteError(f"Unexpected error writing TOML file {self.file_path}: {e}") from e

    def _validate_toml_data(self, data: dict[str, Any]) -> None:
        """Validate that data can be serialized to TOML.

        Args:
            data: Dictionary to validate.

        Raises:
            TOMLValidationError: If data cannot be serialized to TOML.
        """
        if not isinstance(data, dict):
            raise TOMLValidationError(f"TOML data must be a dictionary, got {type(data)}")

        try:
            # Try to serialize to catch any issues
            if tomli_w:
                tomli_w.dumps(data)
        except Exception as e:
            raise TOMLValidationError(f"Data cannot be serialized to TOML: {e}") from e

    def _preserve_formatting_update(
        self, original: str, old_data: dict[str, Any], new_data: dict[str, Any]
    ) -> Optional[str]:
        """Attempt to preserve formatting when updating simple values.

        This is a best-effort approach for simple updates like version changes.
        Returns None if preservation is not possible.

        Args:
            original: Original file content.
            old_data: Original parsed data.
            new_data: New data to write.

        Returns:
            Updated content with preserved formatting, or None if not possible.
        """
        # Only attempt preservation for simple updates
        # (e.g., single value changes in top-level or nested tables)
        if not self._is_simple_update(old_data, new_data):
            return None

        updated_content = original

        # Find and replace changed values while preserving formatting
        for key_path, old_value, new_value in self._find_changed_values(old_data, new_data):
            # Build regex pattern for this specific key-value pair
            pattern = self._build_value_pattern(key_path, old_value)
            if pattern:
                replacement = self._build_replacement(key_path, new_value)
                updated_content = re.sub(pattern, replacement, updated_content, count=1)

        return updated_content

    def _is_simple_update(self, old_data: dict[str, Any], new_data: dict[str, Any]) -> bool:
        """Check if update is simple enough for formatting preservation.

        Args:
            old_data: Original data.
            new_data: New data.

        Returns:
            True if update is simple (few value changes, no structural changes).
        """
        # Check if keys are the same (no structural changes)
        if set(self._flatten_keys(old_data)) != set(self._flatten_keys(new_data)):
            return False

        # Count number of changed values
        changes = list(self._find_changed_values(old_data, new_data))
        # Only preserve for 1-3 simple value changes
        return 0 < len(changes) <= 3

    def _flatten_keys(self, data: dict[str, Any], prefix: str = "") -> list[str]:
        """Flatten nested dictionary keys into dot-notation paths.

        Args:
            data: Dictionary to flatten.
            prefix: Current key prefix.

        Returns:
            List of flattened key paths.
        """
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            if isinstance(value, dict):
                keys.extend(self._flatten_keys(value, full_key))
        return keys

    def _find_changed_values(
        self, old_data: dict[str, Any], new_data: dict[str, Any], prefix: str = ""
    ) -> list[tuple[str, Any, Any]]:
        """Find all changed values between two dictionaries.

        Args:
            old_data: Original data.
            new_data: New data.
            prefix: Current key prefix.

        Returns:
            List of (key_path, old_value, new_value) tuples.
        """
        changes = []

        for key in old_data.keys():
            if key not in new_data:
                continue

            full_key = f"{prefix}.{key}" if prefix else key
            old_value = old_data[key]
            new_value = new_data[key]

            if isinstance(old_value, dict) and isinstance(new_value, dict):
                changes.extend(self._find_changed_values(old_value, new_value, full_key))
            elif old_value != new_value:
                changes.append((full_key, old_value, new_value))

        return changes

    def _build_value_pattern(self, key_path: str, old_value: Any) -> Optional[str]:
        """Build regex pattern to match a specific key-value pair.

        Args:
            key_path: Dot-notation key path.
            old_value: Old value to match.

        Returns:
            Regex pattern string, or None if pattern cannot be built.
        """
        # Get the final key name
        key = key_path.split(".")[-1]

        # Escape special regex characters in the key
        escaped_key = re.escape(key)

        # Build pattern based on value type
        if isinstance(old_value, str):
            escaped_value = re.escape(old_value)
            # Match: key = "value" or key = 'value'
            return rf'({escaped_key}\s*=\s*["\'])({escaped_value})(["\'])'
        elif isinstance(old_value, (int, float)):
            # Match: key = 123 or key = 1.23
            return rf"({escaped_key}\s*=\s*)({re.escape(str(old_value))})"
        elif isinstance(old_value, bool):
            # Match: key = true or key = false
            value_str = "true" if old_value else "false"
            return rf"({escaped_key}\s*=\s*)({value_str})"

        return None

    def _build_replacement(self, key_path: str, new_value: Any) -> str:
        """Build replacement string for a value.

        Args:
            key_path: Dot-notation key path.
            new_value: New value.

        Returns:
            Replacement string.
        """
        if isinstance(new_value, str):
            # Preserve quote style from original (captured in group 1 and 3)
            return rf"\g<1>{new_value}\g<3>"
        elif isinstance(new_value, (int, float)):
            return rf"\g<1>{new_value}"
        elif isinstance(new_value, bool):
            value_str = "true" if new_value else "false"
            return rf"\g<1>{value_str}"

        return str(new_value)

    def validate_structure(self, required_keys: Optional[list[str]] = None) -> bool:
        """Validate TOML file structure.

        Args:
            required_keys: List of required keys in dot notation (e.g., "project.version").

        Returns:
            True if structure is valid.

        Raises:
            TOMLValidationError: If structure validation fails.
        """
        if self._parsed_data is None:
            raise TOMLValidationError("No data loaded. Call read() first.")

        if required_keys:
            for key_path in required_keys:
                if not self._has_key_path(self._parsed_data, key_path):
                    raise TOMLValidationError(f"Required key '{key_path}' not found in TOML file")

        return True

    def _has_key_path(self, data: dict[str, Any], key_path: str) -> bool:
        """Check if a dot-notation key path exists in data.

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

    def get_value(self, key_path: str, default: Any = None) -> Any:
        """Get value from parsed TOML data using dot notation.

        Args:
            key_path: Dot-notation key path (e.g., "project.version").
            default: Default value if key not found.

        Returns:
            Value at key path, or default if not found.

        Raises:
            TOMLReadError: If no data is loaded.
        """
        if self._parsed_data is None:
            raise TOMLReadError("No data loaded. Call read() first.")

        keys = key_path.split(".")
        current = self._parsed_data

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]

        return current

    def set_value(self, key_path: str, value: Any) -> None:
        """Set value in parsed TOML data using dot notation.

        Args:
            key_path: Dot-notation key path (e.g., "project.version").
            value: Value to set.

        Raises:
            TOMLReadError: If no data is loaded.
            TOMLValidationError: If key path is invalid.
        """
        if self._parsed_data is None:
            raise TOMLReadError("No data loaded. Call read() first.")

        keys = key_path.split(".")
        current = self._parsed_data

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                raise TOMLValidationError(
                    f"Cannot set value: '{key}' in path '{key_path}' is not a table"
                )
            current = current[key]

        # Set the final value
        current[keys[-1]] = value

    def backup(self) -> None:
        """Create a backup of the TOML file.

        Raises:
            TOMLError: If backup creation fails.
        """
        if not self.file_path.exists():
            raise TOMLError(f"Cannot backup non-existent file: {self.file_path}")

        backup_path = self.file_path.with_suffix(self.file_path.suffix + ".backup")

        try:
            backup_path.write_text(self.file_path.read_text(encoding="utf-8"), encoding="utf-8")
        except OSError as e:
            raise TOMLError(f"Failed to create backup: {e}") from e

    def restore_from_backup(self) -> None:
        """Restore TOML file from backup.

        Raises:
            TOMLError: If restore fails.
        """
        backup_path = self.file_path.with_suffix(self.file_path.suffix + ".backup")

        if not backup_path.exists():
            raise TOMLError(f"Backup file not found: {backup_path}")

        try:
            self.file_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
            # Reload data after restore
            self.read()
        except OSError as e:
            raise TOMLError(f"Failed to restore from backup: {e}") from e
