"""Rule pack management system for Riveter.

This module provides modern rule pack management with protocol-based interfaces,
comprehensive validation, and extensible loading systems. It works with immutable
Rule data structures and provides structured error handling.
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml

from .exceptions import RuleValidationError
from .logging import debug, error, info
from .models.core import Severity
from .models.rules import Rule, RulePack
from .rules import create_rule_from_dict

# Modern rule pack utility functions


def filter_rules_by_severity(rules: list[Rule], min_severity: Severity) -> list[Rule]:
    """Filter rules by minimum severity level."""
    severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2}
    min_level = severity_order[min_severity]

    return [rule for rule in rules if severity_order[rule.severity] >= min_level]


def filter_rules_by_resource_type(rules: list[Rule], resource_types: list[str]) -> list[Rule]:
    """Filter rules by resource types."""
    return [
        rule
        for rule in rules
        if rule.resource_type in resource_types or rule.applies_to_all_resources
    ]


def filter_rules_by_tags(rules: list[Rule], tags: list[str]) -> list[Rule]:
    """Filter rules by metadata tags."""
    if not tags:
        return rules

    return [rule for rule in rules if any(tag in rule.metadata.tags for tag in tags)]


def merge_rule_packs(pack1: RulePack, pack2: RulePack) -> RulePack:
    """Merge two rule packs, handling conflicts."""
    # Check for rule ID conflicts
    pack1_ids = pack1.rule_ids
    pack2_ids = pack2.rule_ids
    conflicts = pack1_ids & pack2_ids

    if conflicts:
        raise ValueError(f"Cannot merge rule packs: conflicting rule IDs: {', '.join(conflicts)}")

    # Create merged rule pack
    merged_name = f"{pack1.name}+{pack2.name}"
    merged_description = f"Merged pack: {pack1.description} + {pack2.description}"
    merged_author = f"{pack1.author or 'Unknown'}, {pack2.author or 'Unknown'}"
    merged_version = "merged"
    merged_tags = list(set((pack1.tags or []) + (pack2.tags or [])))

    return RulePack(
        name=merged_name,
        description=merged_description,
        version=merged_version,
        rules=pack1.rules + pack2.rules,
        author=merged_author,
        framework=pack1.framework or pack2.framework,
        category=pack1.category or pack2.category,
        tags=merged_tags,
        source_file=None,  # Merged packs don't have a single source file
    )


class RulePackManager:
    """Modern rule pack manager with protocol-based interfaces and extensible loading.

    Implements the RuleRepository protocol for consistent rule loading across
    the system. Provides comprehensive validation, caching, and error handling.
    """

    def __init__(self, rule_pack_dirs: list[str] | None = None):
        """Initialize rule pack manager with search directories.

        Args:
            rule_pack_dirs: Optional list of directories to search for rule packs.
                          If None, uses default system directories.
        """
        self.rule_pack_dirs = rule_pack_dirs or []

        # Add default rule pack directories
        default_dirs = [
            os.path.join(os.path.dirname(__file__), "..", "..", "rule_packs"),
            os.path.expanduser("~/.riveter/rule_packs"),
            "/usr/local/share/riveter/rule_packs",
            "/opt/homebrew/share/riveter/rule_packs",  # Homebrew on Apple Silicon
        ]

        for dir_path in default_dirs:
            if os.path.exists(dir_path) and dir_path not in self.rule_pack_dirs:
                self.rule_pack_dirs.append(dir_path)

        debug("Rule pack manager initialized", search_dirs=len(self.rule_pack_dirs))

    def load_rules_from_file(self, file_path: Path) -> list[Rule]:
        """Load rules from a file (RuleRepository protocol method).

        Args:
            file_path: Path to the rules file

        Returns:
            List of loaded rules

        Raises:
            RuleValidationError: If loading fails
        """
        from .rules import load_rules

        return load_rules(str(file_path))

    def load_rule_pack(self, pack_name: str, version: str = "latest") -> RulePack:
        """Load a rule pack by name and version.

        Args:
            pack_name: Name of the rule pack to load
            version: Version to load (default: "latest")

        Returns:
            Loaded rule pack with immutable structure

        Raises:
            FileNotFoundError: If pack not found
            RuleValidationError: If pack is invalid
        """
        pack_file = self._find_rule_pack_file(pack_name, version)
        if not pack_file:
            raise FileNotFoundError(f"Rule pack '{pack_name}' version '{version}' not found")

        info("Loading rule pack", pack_name=pack_name, version=version, file_path=pack_file)
        return self._load_rule_pack_from_file(pack_file)

    def load_rule_pack_from_file(self, file_path: str) -> RulePack:
        """Load a rule pack from a specific file path.

        Args:
            file_path: Path to the rule pack file

        Returns:
            Loaded rule pack

        Raises:
            RuleValidationError: If loading fails
        """
        return self._load_rule_pack_from_file(file_path)

    def list_available_packs(self) -> list[str]:
        """List all available rule packs (RuleRepository protocol method).

        Returns:
            List of rule pack names
        """
        packs = self.list_available_packs_detailed()
        return [pack["name"] for pack in packs]

    def validate_rule(self, rule: Rule) -> bool:
        """Validate a rule definition (RuleRepository protocol method).

        Args:
            rule: Rule to validate

        Returns:
            True if rule is valid, False otherwise
        """
        try:
            # Basic validation - rule should be properly constructed
            # if we got here with an immutable Rule object
            return (
                bool(rule.id)
                and bool(rule.description)
                and bool(rule.resource_type)
                and rule.has_assertion
            )
        except Exception:
            return False

    def _load_rule_pack_from_file(self, file_path: str) -> RulePack:
        """Internal method to load rule pack from file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise RuleValidationError(
                    "Rule pack file must contain a YAML dictionary",
                    rule_file=file_path,
                    suggestions=[
                        "Ensure the file contains a valid YAML dictionary",
                        "Check the file structure and indentation",
                        "Verify the file is not empty or corrupted",
                    ],
                )

            # Validate required sections
            if "metadata" not in data:
                raise RuleValidationError(
                    "Rule pack must contain 'metadata' section",
                    rule_file=file_path,
                    suggestions=[
                        "Add a 'metadata:' section to the rule pack file",
                        "Check the rule pack format documentation",
                        "Ensure proper YAML structure",
                    ],
                )
            if "rules" not in data:
                raise RuleValidationError(
                    "Rule pack must contain 'rules' section",
                    rule_file=file_path,
                    suggestions=[
                        "Add a 'rules:' section to the rule pack file",
                        "Ensure the rules are properly formatted as a list",
                        "Check the rule pack format documentation",
                    ],
                )

            # Parse metadata
            metadata_dict = data["metadata"]

            # Validate required metadata fields
            required_metadata = ["name", "version", "description"]
            for field in required_metadata:
                if field not in metadata_dict:
                    raise RuleValidationError(
                        f"Missing required metadata field: {field}",
                        rule_file=file_path,
                        field_path=f"metadata.{field}",
                        suggestions=[
                            f"Add the '{field}' field to the metadata section",
                            "Check the rule pack format documentation",
                            "Ensure all required metadata fields are present",
                        ],
                    )

            # Parse rules
            rules = []
            rule_ids = set()

            for i, rule_dict in enumerate(data["rules"]):
                if not isinstance(rule_dict, dict):
                    raise RuleValidationError(
                        f"Rule at index {i} must be a dictionary",
                        rule_file=file_path,
                        suggestions=[
                            f"Check rule #{i + 1} in the file",
                            "Ensure each rule is a dictionary with key-value pairs",
                            "Verify proper YAML indentation and structure",
                        ],
                    )

                # Ensure required fields
                if "id" not in rule_dict:
                    raise RuleValidationError(
                        f"Rule at index {i} must have an 'id'",
                        rule_file=file_path,
                        suggestions=[
                            f"Add an 'id' field to rule #{i + 1}",
                            "Ensure each rule has a unique identifier",
                            "Check the rule format documentation",
                        ],
                    )

                rule_id = rule_dict["id"]
                if rule_id in rule_ids:
                    raise RuleValidationError(
                        f"Duplicate rule ID '{rule_id}' in rule pack",
                        rule_id=rule_id,
                        rule_file=file_path,
                        suggestions=[
                            "Ensure each rule has a unique ID",
                            "Check for copy-paste errors in rule definitions",
                            "Use descriptive, unique identifiers for each rule",
                        ],
                    )
                rule_ids.add(rule_id)

                if "resource_type" not in rule_dict:
                    raise RuleValidationError(
                        f"Rule '{rule_id}' must have a 'resource_type'",
                        rule_id=rule_id,
                        rule_file=file_path,
                        suggestions=[
                            "Add a 'resource_type' field to the rule",
                            "Specify the Terraform resource type this rule applies to",
                            "Use '*' to apply to all resource types",
                        ],
                    )
                if "assert" not in rule_dict:
                    raise RuleValidationError(
                        f"Rule '{rule_id}' must have 'assert' conditions",
                        rule_id=rule_id,
                        rule_file=file_path,
                        suggestions=[
                            "Add an 'assert' section with validation conditions",
                            "Define what properties should be checked",
                            "Check the rule format documentation",
                        ],
                    )

                rules.append(create_rule_from_dict(rule_dict, file_path))

            # Create immutable rule pack
            rule_pack = RulePack(
                name=metadata_dict["name"],
                description=metadata_dict["description"],
                version=metadata_dict["version"],
                rules=rules,
                author=metadata_dict.get("author"),
                framework=metadata_dict.get("framework"),
                category=metadata_dict.get("category"),
                tags=metadata_dict.get("tags", []),
                source_file=Path(file_path),
            )

            debug(
                "Rule pack loaded successfully",
                pack_name=rule_pack.name,
                version=rule_pack.version,
                rule_count=rule_pack.rule_count,
                file_path=file_path,
            )

            return rule_pack

        except yaml.YAMLError as e:
            raise RuleValidationError(
                f"Invalid YAML in rule pack file '{file_path}': {e!s}",
                rule_file=file_path,
                suggestions=[
                    "Check YAML syntax and indentation",
                    "Ensure all quotes and brackets are properly closed",
                    "Use a YAML validator to check the file structure",
                ],
            ) from e
        except RuleValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise RuleValidationError(
                f"Error loading rule pack from '{file_path}': {e!s}",
                rule_file=file_path,
                suggestions=[
                    "Check file permissions and accessibility",
                    "Ensure the file is a valid rule pack format",
                    "Verify the file is not corrupted",
                ],
            ) from e

    def _find_rule_pack_file(self, pack_name: str, version: str) -> str | None:
        """Find rule pack file in search directories."""
        for directory in self.rule_pack_dirs:
            if not os.path.exists(directory):
                continue

            # Look for exact filename match first
            exact_file = os.path.join(directory, f"{pack_name}.yml")
            if os.path.exists(exact_file):
                return exact_file

            # Look for versioned files if version is specified and not "latest"
            if version != "latest":
                versioned_file = os.path.join(directory, f"{pack_name}-{version}.yml")
                if os.path.exists(versioned_file):
                    return versioned_file

        return None

    def list_available_packs_detailed(self) -> list[dict[str, str | int]]:
        """List all available rule packs in search directories with detailed information."""
        packs = []
        seen_packs = set()

        for directory in self.rule_pack_dirs:
            if not os.path.exists(directory):
                continue

            for filename in os.listdir(directory):
                if not filename.endswith(".yml") and not filename.endswith(".yaml"):
                    continue

                file_path = os.path.join(directory, filename)
                if not os.path.isfile(file_path):
                    continue

                try:
                    # Extract pack name and version from filename
                    base_name = filename.rsplit(".", 1)[0]
                    version_match = re.match(r"^(.+)-(\d+\.\d+\.\d+)$", base_name)

                    if version_match:
                        pack_name = version_match.group(1)
                        version = version_match.group(2)
                    else:
                        pack_name = base_name
                        version = "latest"

                    pack_key = f"{pack_name}:{version}"
                    if pack_key in seen_packs:
                        continue

                    seen_packs.add(pack_key)

                    # Try to load metadata
                    try:
                        pack = self._load_rule_pack_from_file(file_path)
                        packs.append(
                            {
                                "name": pack.metadata.name,
                                "version": pack.metadata.version,
                                "description": pack.metadata.description,
                                "author": pack.metadata.author,
                                "file_path": file_path,
                                "rule_count": len(pack.rules),
                            }
                        )
                    except Exception:
                        # If we can't load the pack, still list it but with limited info
                        packs.append(
                            {
                                "name": pack_name,
                                "version": version,
                                "description": "Failed to load metadata",
                                "author": "Unknown",
                                "file_path": file_path,
                                "rule_count": 0,
                            }
                        )

                except Exception:
                    continue

        return sorted(packs, key=lambda x: (x["name"], x["version"]))  # type: ignore[arg-type]

    def validate_rule_pack(self, pack_path: str) -> dict[str, Any]:
        """Validate a rule pack file and return validation results.

        Args:
            pack_path: Path to the rule pack file to validate

        Returns:
            Dictionary with validation results including errors, warnings, and metadata
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "rule_count": 0,
            "metadata": None,
        }

        try:
            # Check if file exists
            if not os.path.exists(pack_path):
                result["errors"].append(f"File does not exist: {pack_path}")
                return result

            # Try to load the rule pack
            pack = self._load_rule_pack_from_file(pack_path)

            result["valid"] = True
            result["rule_count"] = pack.rule_count
            result["metadata"] = {
                "name": pack.name,
                "version": pack.version,
                "description": pack.description,
                "author": pack.author,
            }

            # Additional validations
            if not pack.rules:
                result["warnings"].append("Rule pack contains no rules")

            # Check for duplicate rule IDs (should not happen with immutable structures)
            rule_ids = list(pack.rule_ids)
            if len(rule_ids) != len(set(rule_ids)):
                result["errors"].append("Rule pack contains duplicate rule IDs")
                result["valid"] = False

            # Validate version format
            if not re.match(r"^\d+\.\d+\.\d+$", pack.version):
                result["warnings"].append(
                    f"Version '{pack.version}' does not follow semantic versioning"
                )

            # Validate individual rules
            for rule in pack.rules:
                if not self.validate_rule(rule):
                    result["warnings"].append(f"Rule '{rule.id}' may have validation issues")

            info(
                "Rule pack validation completed",
                pack_path=pack_path,
                valid=result["valid"],
                rule_count=result["rule_count"],
                errors=len(result["errors"]),
                warnings=len(result["warnings"]),
            )

        except RuleValidationError as e:
            result["errors"].append(str(e))
            error("Rule pack validation failed", pack_path=pack_path, error=str(e))
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e!s}")
            error("Unexpected error during rule pack validation", pack_path=pack_path, error=str(e))

        return result

    def merge_rule_packs_by_name(self, pack_names: list[str], version: str = "latest") -> RulePack:
        """Merge multiple rule packs into a single pack.

        Args:
            pack_names: List of rule pack names to merge
            version: Version to load for each pack (default: "latest")

        Returns:
            Merged rule pack

        Raises:
            ValueError: If no pack names provided or packs have conflicting rule IDs
            FileNotFoundError: If any pack is not found
        """
        if not pack_names:
            raise ValueError("At least one rule pack name must be provided")

        # Load the first pack
        merged_pack = self.load_rule_pack(pack_names[0], version)

        # Merge with remaining packs
        for pack_name in pack_names[1:]:
            other_pack = self.load_rule_pack(pack_name, version)
            merged_pack = merge_rule_packs(merged_pack, other_pack)

        info(
            "Rule packs merged successfully",
            pack_names=pack_names,
            total_rules=merged_pack.rule_count,
            merged_name=merged_pack.name,
        )

        return merged_pack

    def create_rule_pack_template(self, name: str, output_path: str) -> None:
        """Create a template rule pack file.

        Args:
            name: Name for the new rule pack
            output_path: Path where the template file should be created
        """
        template = {
            "metadata": {
                "name": name,
                "version": "1.0.0",
                "description": f"Rule pack for {name}",
                "author": "Your Name",
                "framework": "custom",
                "category": "security",
                "tags": ["security", "compliance"],
            },
            "rules": [
                {
                    "id": f"{name.lower().replace('-', '_')}_example_rule",
                    "resource_type": "aws_instance",
                    "description": "Example rule - replace with actual rules",
                    "severity": "error",
                    "filter": {"tags.Environment": "production"},
                    "assert": {"instance_type": {"regex": "^(t3|m5|c5)\\.(large|xlarge)$"}},
                    "metadata": {
                        "category": "compute",
                        "tags": ["example", "ec2"],
                        "references": ["https://example.com/best-practices"],
                        "author": "Your Name",
                        "version": "1.0",
                    },
                }
            ],
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(template, f, default_flow_style=False, sort_keys=False, indent=2)

            info("Rule pack template created", name=name, output_path=output_path)
        except Exception as e:
            error(
                "Failed to create rule pack template",
                name=name,
                output_path=output_path,
                error=str(e),
            )
            raise
