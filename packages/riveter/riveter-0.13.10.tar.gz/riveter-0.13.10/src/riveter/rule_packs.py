"""Rule pack management system for Riveter."""

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import yaml

from .rules import Rule, Severity


@dataclass
class RulePackMetadata:
    """Metadata for a rule pack."""

    name: str
    version: str
    description: str
    author: str
    created: str
    updated: str
    dependencies: List[str]
    tags: List[str]
    min_riveter_version: str


@dataclass
class RulePack:
    """A collection of rules with metadata."""

    metadata: RulePackMetadata
    rules: List[Rule]

    def __post_init__(self) -> None:
        """Validate rule pack after initialization."""
        self._validate_rules()

    def _validate_rules(self) -> None:
        """Validate that all rules in the pack are valid."""
        rule_ids = set()
        for rule in self.rules:
            if rule.id in rule_ids:
                raise ValueError(
                    f"Duplicate rule ID '{rule.id}' in rule pack '{self.metadata.name}'"
                )
            rule_ids.add(rule.id)

    def filter_by_severity(self, min_severity: Severity) -> "RulePack":
        """Filter rules by minimum severity level."""
        severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2}
        min_level = severity_order[min_severity]

        filtered_rules = [rule for rule in self.rules if severity_order[rule.severity] >= min_level]

        return RulePack(metadata=self.metadata, rules=filtered_rules)

    def filter_by_resource_type(self, resource_types: List[str]) -> "RulePack":
        """Filter rules by resource types."""
        filtered_rules = [rule for rule in self.rules if rule.resource_type in resource_types]

        return RulePack(metadata=self.metadata, rules=filtered_rules)

    def filter_by_tags(self, tags: List[str]) -> "RulePack":
        """Filter rules by metadata tags."""
        if not tags:
            return self

        filtered_rules = [
            rule for rule in self.rules if any(tag in rule.metadata.get("tags", []) for tag in tags)
        ]

        return RulePack(metadata=self.metadata, rules=filtered_rules)

    def merge_with(self, other: "RulePack") -> "RulePack":
        """Merge this rule pack with another, handling conflicts."""
        # Check for rule ID conflicts
        self_ids = {rule.id for rule in self.rules}
        other_ids = {rule.id for rule in other.rules}
        conflicts = self_ids & other_ids

        if conflicts:
            raise ValueError(
                f"Cannot merge rule packs: conflicting rule IDs: {', '.join(conflicts)}"
            )

        # Create merged metadata
        merged_metadata = RulePackMetadata(
            name=f"{self.metadata.name}+{other.metadata.name}",
            version="merged",
            description=f"Merged pack: {self.metadata.description} + {other.metadata.description}",
            author=f"{self.metadata.author}, {other.metadata.author}",
            created=min(self.metadata.created, other.metadata.created),
            updated=max(self.metadata.updated, other.metadata.updated),
            dependencies=list(set(self.metadata.dependencies + other.metadata.dependencies)),
            tags=list(set(self.metadata.tags + other.metadata.tags)),
            min_riveter_version=max(
                self.metadata.min_riveter_version, other.metadata.min_riveter_version
            ),
        )

        return RulePack(metadata=merged_metadata, rules=self.rules + other.rules)

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule pack to dictionary format."""
        return {
            "metadata": {
                "name": self.metadata.name,
                "version": self.metadata.version,
                "description": self.metadata.description,
                "author": self.metadata.author,
                "created": self.metadata.created,
                "updated": self.metadata.updated,
                "dependencies": self.metadata.dependencies,
                "tags": self.metadata.tags,
                "min_riveter_version": self.metadata.min_riveter_version,
            },
            "rules": [
                {
                    "id": rule.id,
                    "resource_type": rule.resource_type,
                    "description": rule.description,
                    "severity": rule.severity.value,
                    "filter": rule.filter,
                    "assert": rule.assert_conditions,
                    "metadata": rule.metadata,
                }
                for rule in self.rules
            ],
        }


class RulePackManager:
    """Manages rule pack loading, validation, and operations."""

    def __init__(self, rule_pack_dirs: Optional[List[str]] = None):
        """Initialize rule pack manager with search directories."""
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

    def load_rule_pack(self, pack_name: str, version: str = "latest") -> RulePack:
        """Load a rule pack by name and version."""
        pack_file = self._find_rule_pack_file(pack_name, version)
        if not pack_file:
            raise FileNotFoundError(f"Rule pack '{pack_name}' version '{version}' not found")

        return self._load_rule_pack_from_file(pack_file)

    def load_rule_pack_from_file(self, file_path: str) -> RulePack:
        """Load a rule pack from a specific file path."""
        return self._load_rule_pack_from_file(file_path)

    def _load_rule_pack_from_file(self, file_path: str) -> RulePack:
        """Internal method to load rule pack from file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValueError("Rule pack file must contain a YAML dictionary")

            # Validate required sections
            if "metadata" not in data:
                raise ValueError("Rule pack must contain 'metadata' section")
            if "rules" not in data:
                raise ValueError("Rule pack must contain 'rules' section")

            # Parse metadata
            metadata_dict = data["metadata"]
            metadata = RulePackMetadata(
                name=metadata_dict["name"],
                version=metadata_dict["version"],
                description=metadata_dict["description"],
                author=metadata_dict.get("author", "Unknown"),
                created=metadata_dict.get("created", "Unknown"),
                updated=metadata_dict.get("updated", "Unknown"),
                dependencies=metadata_dict.get("dependencies", []),
                tags=metadata_dict.get("tags", []),
                min_riveter_version=metadata_dict.get("min_riveter_version", "0.1.0"),
            )

            # Parse rules
            rules = []
            for rule_dict in data["rules"]:
                if not isinstance(rule_dict, dict):
                    raise ValueError("Each rule must be a dictionary")

                # Ensure required fields
                if "id" not in rule_dict:
                    raise ValueError("Each rule must have an 'id'")
                if "resource_type" not in rule_dict:
                    raise ValueError("Each rule must have a 'resource_type'")
                if "assert" not in rule_dict:
                    raise ValueError("Each rule must have 'assert' conditions")

                rules.append(Rule(rule_dict))

            return RulePack(metadata=metadata, rules=rules)

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in rule pack file '{file_path}': {str(e)}") from e
        except KeyError as e:
            raise ValueError(f"Missing required metadata field in rule pack: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Error loading rule pack from '{file_path}': {str(e)}") from e

    def _find_rule_pack_file(self, pack_name: str, version: str) -> Optional[str]:
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

    def list_available_packs(self) -> List[Dict[str, Union[str, int]]]:
        """List all available rule packs in search directories."""
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

    def validate_rule_pack(self, pack_path: str) -> Dict[str, Any]:
        """Validate a rule pack file and return validation results."""
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
            result["rule_count"] = len(pack.rules)
            result["metadata"] = {
                "name": pack.metadata.name,
                "version": pack.metadata.version,
                "description": pack.metadata.description,
                "author": pack.metadata.author,
            }

            # Additional validations
            if not pack.rules:
                result["warnings"].append("Rule pack contains no rules")

            # Check for duplicate rule IDs (already done in RulePack.__post_init__)
            rule_ids = [rule.id for rule in pack.rules]
            if len(rule_ids) != len(set(rule_ids)):
                result["errors"].append("Rule pack contains duplicate rule IDs")
                result["valid"] = False

            # Validate version format
            if not re.match(r"^\d+\.\d+\.\d+$", pack.metadata.version):
                result["warnings"].append(
                    f"Version '{pack.metadata.version}' does not follow semantic versioning"
                )

        except Exception as e:
            result["errors"].append(str(e))

        return result

    def merge_rule_packs(self, pack_names: List[str], version: str = "latest") -> RulePack:
        """Merge multiple rule packs into a single pack."""
        if not pack_names:
            raise ValueError("At least one rule pack name must be provided")

        # Load the first pack
        merged_pack = self.load_rule_pack(pack_names[0], version)

        # Merge with remaining packs
        for pack_name in pack_names[1:]:
            other_pack = self.load_rule_pack(pack_name, version)
            merged_pack = merged_pack.merge_with(other_pack)

        return merged_pack

    def create_rule_pack_template(self, name: str, output_path: str) -> None:
        """Create a template rule pack file."""
        template = {
            "metadata": {
                "name": name,
                "version": "1.0.0",
                "description": f"Rule pack for {name}",
                "author": "Your Name",
                "created": "2024-01-01",
                "updated": "2024-01-01",
                "dependencies": [],
                "tags": ["security", "compliance"],
                "min_riveter_version": "0.1.0",
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
                        "tags": ["example"],
                        "references": ["https://example.com/best-practices"],
                    },
                }
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False, indent=2)
