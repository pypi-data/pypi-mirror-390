#!/usr/bin/env python3
"""Extract Terraform configuration into Riveter-compatible format."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import hcl2

from .cloud_parsers import CloudProviderDetector
from .exceptions import FileSystemError, TerraformParsingError, handle_error_with_recovery
from .logging import debug, error, info, warning


def extract_terraform_config(tf_file: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extract Terraform configuration into Riveter format.

    This function converts Terraform HCL into a format that Riveter can understand.
    It now includes multi-cloud provider support with provider-specific parsing
    while maintaining backward compatibility.

    The output format is:
    {
        "resources": [
            {
                "id": "resource_name",
                "resource_type": "provider_resource_type",
                "property1": "value1",
                "property2": "value2",
                ...
            }
        ]
    }

    Args:
        tf_file: Path to the Terraform configuration file

    Returns:
        Dictionary containing extracted resources

    Raises:
        TerraformParsingError: When the Terraform file cannot be parsed
        FileSystemError: When the file cannot be read
    """
    info("Starting Terraform configuration extraction", file_path=tf_file)

    try:
        # Check if file exists and is readable
        tf_path = Path(tf_file)
        if not tf_path.exists():
            raise FileSystemError(
                f"Terraform file not found: {tf_file}",
                file_path=tf_file,
                operation="read",
                suggestions=[
                    "Check that the file path is correct",
                    "Ensure the file exists in the specified location",
                    "Verify you have read permissions for the file",
                ],
            )

        if not tf_path.is_file():
            raise FileSystemError(
                f"Path is not a file: {tf_file}",
                file_path=tf_file,
                operation="read",
                suggestions=[
                    "Ensure the path points to a file, not a directory",
                    "Check that the file extension is correct (.tf)",
                ],
            )

        debug("Reading Terraform file", file_path=tf_file, file_size=tf_path.stat().st_size)

        # Read and parse the HCL file
        try:
            with open(tf_file, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    warning("Terraform file is empty", file_path=tf_file)
                    return {"resources": []}

                tf_config = hcl2.loads(content)

        except UnicodeDecodeError as e:
            raise TerraformParsingError(
                f"File encoding error in {tf_file}: {str(e)}",
                terraform_file=tf_file,
                hcl_error=str(e),
                suggestions=[
                    "Ensure the file is saved with UTF-8 encoding",
                    "Check for binary content or special characters",
                    "Try opening the file in a text editor to verify content",
                ],
            ) from e
        except Exception as e:
            # Parse HCL-specific errors for better messages
            error_msg = str(e).lower()
            suggestions = [
                "Check for syntax errors in the Terraform file",
                "Ensure all brackets and quotes are properly closed",
                "Verify that the file is valid HCL format",
                "Try running 'terraform validate' on the file",
            ]

            if "unexpected token" in error_msg:
                suggestions.insert(0, "Look for unexpected characters or tokens in the file")
            elif "unterminated" in error_msg:
                suggestions.insert(0, "Check for unterminated strings or comments")
            elif "invalid character" in error_msg:
                suggestions.insert(0, "Look for invalid characters or encoding issues")

            raise TerraformParsingError(
                f"Failed to parse Terraform file {tf_file}: {str(e)}",
                terraform_file=tf_file,
                hcl_error=str(e),
                suggestions=suggestions,
            ) from e

    except (FileSystemError, TerraformParsingError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise FileSystemError(
            f"Unexpected error reading Terraform file {tf_file}: {str(e)}",
            file_path=tf_file,
            operation="read",
            suggestions=[
                "Check file permissions and accessibility",
                "Ensure sufficient disk space and memory",
                "Try with a different file or smaller configuration",
            ],
        ) from e

    resources = []

    # Find resource blocks
    if "resource" not in tf_config:
        warning(
            "No resource blocks found in Terraform configuration",
            file_path=tf_file,
            available_blocks=list(tf_config.keys()),
        )

        if not tf_config:
            info("Terraform file appears to be empty or contains no configuration blocks")
        else:
            info("Configuration contains non-resource blocks", blocks=list(tf_config.keys()))
            debug("Full configuration structure", config=tf_config)

        return {"resources": []}

    # Initialize cloud provider detector
    detector = CloudProviderDetector()
    debug("Initialized cloud provider detector")

    # Process each resource block
    resource_count = 0
    error_count = 0

    try:
        for resource_block in tf_config["resource"]:
            for resource_type, instances in resource_block.items():
                for name, config in instances.items():
                    try:
                        debug(
                            "Processing resource", resource_type=resource_type, resource_name=name
                        )

                        # Create the base resource
                        resource = {"id": name, "resource_type": resource_type}

                        # Add all configuration items
                        for key, value in config.items():
                            if isinstance(value, dict):
                                resource[key] = dict(value)
                            elif isinstance(value, list):
                                # Keep lists as lists, don't try to flatten them
                                resource[key] = list(value)
                            else:
                                resource[key] = value

                        # Apply provider-specific parsing
                        parser = detector.get_parser_for_resource(resource_type)
                        if parser:
                            debug(
                                "Using provider-specific parser",
                                resource_type=resource_type,
                                parser_type=type(parser).__name__,
                            )
                            try:
                                # Use provider-specific parsing
                                resource = parser.parse_resource(resource_type, resource)
                                resource = parser.normalize_attributes(resource)
                            except Exception as parse_error:
                                warning(
                                    "Provider-specific parsing failed, using fallback",
                                    resource_type=resource_type,
                                    resource_name=name,
                                    error=str(parse_error),
                                )
                                # Fallback to legacy parsing
                                resource = _apply_legacy_parsing(resource)
                        else:
                            debug("Using legacy parsing for resource", resource_type=resource_type)
                            # Fallback to legacy parsing for backward compatibility
                            resource = _apply_legacy_parsing(resource)

                        resources.append(resource)
                        resource_count += 1

                    except Exception as resource_error:
                        error_count += 1
                        error(
                            "Failed to process resource",
                            resource_type=resource_type,
                            resource_name=name,
                            error=str(resource_error),
                        )

                        # Try to recover by skipping this resource
                        try:
                            handle_error_with_recovery(
                                TerraformParsingError(
                                    (
                                        f"Failed to process resource {resource_type}.{name}: "
                                        f"{str(resource_error)}"
                                    ),
                                    terraform_file=tf_file,
                                    suggestions=[
                                        (
                                            f"Check the configuration for resource "
                                            f"{resource_type}.{name}"
                                        ),
                                        "Verify all required attributes are present",
                                        "Check for syntax errors in the resource block",
                                    ],
                                )
                            )
                        except TerraformParsingError:
                            # If recovery fails, continue with next resource
                            continue

    except Exception as e:
        raise TerraformParsingError(
            f"Error processing resource blocks in {tf_file}: {str(e)}",
            terraform_file=tf_file,
            suggestions=[
                "Check the structure of resource blocks in the file",
                "Ensure proper nesting and syntax",
                "Verify that all resource blocks are properly formatted",
            ],
        ) from e

    info(
        "Terraform configuration extraction completed",
        file_path=tf_file,
        total_resources=resource_count,
        errors=error_count,
    )

    if error_count > 0:
        warning(
            f"Extraction completed with {error_count} errors. Some resources may have been skipped."
        )

    return {"resources": resources}


def _apply_legacy_parsing(resource: Dict[str, Any]) -> Dict[str, Any]:
    """Apply legacy parsing logic for backward compatibility."""
    # Convert tags from list to dict if needed (legacy AWS behavior)
    if "tags" in resource and isinstance(resource["tags"], list):
        tags_dict = {}
        for tag in resource["tags"]:
            if isinstance(tag, dict) and "Key" in tag and "Value" in tag:
                tags_dict[tag["Key"]] = tag["Value"]
        resource["tags"] = tags_dict

    return resource


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: extract_config.py <terraform_file>")
        sys.exit(1)

    tf_file = sys.argv[1]
    config = extract_terraform_config(tf_file)

    # Write to resources.json
    output_file = Path(tf_file).parent / "resources.json"
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    main()
