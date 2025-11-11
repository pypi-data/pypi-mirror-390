#!/usr/bin/env python3
"""Extract Terraform configuration into Riveter-compatible format.

This module provides backward compatibility for the legacy extract_terraform_config
function while internally using the modernized configuration parser.
"""

import json
import sys
from pathlib import Path
from typing import Any

from .configuration.parser import extract_terraform_config as _modern_extract_terraform_config
from .logging import debug, info


def extract_terraform_config(tf_file: str) -> dict[str, list[dict[str, Any]]]:
    """Extract Terraform configuration into Riveter format.

    This function maintains backward compatibility with the original interface
    while internally using the modernized configuration parser.

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
    info("Starting Terraform configuration extraction (legacy interface)", file_path=tf_file)

    # Use the modernized parser internally
    result = _modern_extract_terraform_config(tf_file)
    debug(
        "Legacy extraction completed",
        file_path=tf_file,
        resource_count=len(result["resources"]),
    )
    return result


def main() -> None:
    if len(sys.argv) != 2:
        import sys

        sys.stderr.write("Usage: extract_config.py <terraform_file>\n")
        sys.exit(1)

    tf_file = sys.argv[1]
    config = extract_terraform_config(tf_file)

    # Write to resources.json
    output_file = Path(tf_file).parent / "resources.json"
    with output_file.open("w") as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    main()
