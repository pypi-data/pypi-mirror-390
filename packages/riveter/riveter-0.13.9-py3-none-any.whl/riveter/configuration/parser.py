"""Modern Terraform configuration parser with type safety and error handling.

This module provides a modernized version of the Terraform configuration parser
that maintains backward compatibility while adding comprehensive type hints,
structured error handling, and immutable data structures.
"""

from pathlib import Path
from typing import Any, Protocol

import hcl2

from ..cloud_parsers import CloudProviderDetector
from ..exceptions import FileSystemError, TerraformParsingError, handle_error_with_recovery
from ..logging import debug, error, info, warning
from ..models.config import TerraformConfig


class ConfigurationParser(Protocol):
    """Protocol for configuration parsers."""

    def parse(self, file_path: Path) -> TerraformConfig:
        """Parse a configuration file and return structured configuration."""
        ...

    def validate(self, config: TerraformConfig) -> list[str]:
        """Validate a configuration and return list of validation errors."""
        ...


class TerraformConfigParser:
    """Modern Terraform configuration parser with comprehensive error handling."""

    def __init__(self, cloud_detector: CloudProviderDetector | None = None) -> None:
        """Initialize the parser with optional cloud provider detector.

        Args:
            cloud_detector: Cloud provider detector for provider-specific parsing.
                          If None, a default detector will be created.
        """
        self._cloud_detector = cloud_detector or CloudProviderDetector()
        self._resource_count = 0
        self._error_count = 0

    def parse(self, file_path: str | Path) -> TerraformConfig:
        """Parse a Terraform configuration file.

        Args:
            file_path: Path to the Terraform configuration file

        Returns:
            Immutable TerraformConfig object containing parsed configuration

        Raises:
            TerraformParsingError: When the Terraform file cannot be parsed
            FileSystemError: When the file cannot be read
        """
        # Convert string to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)

        info("Starting Terraform configuration parsing", file_path=str(file_path))

        # Reset counters for this parse operation
        self._resource_count = 0
        self._error_count = 0

        # Validate file existence and readability
        self._validate_file_access(file_path)

        # Read and parse HCL content
        hcl_config = self._parse_hcl_file(file_path)

        # Extract configuration components
        resources = self._extract_resources(hcl_config, file_path)
        variables = self._extract_variables(hcl_config)
        outputs = self._extract_outputs(hcl_config)
        providers = self._extract_providers(hcl_config)
        modules = self._extract_modules(hcl_config)
        data_sources = self._extract_data_sources(hcl_config)
        locals_block = self._extract_locals(hcl_config)
        terraform_block = self._extract_terraform_block(hcl_config)

        # Create immutable configuration object
        config = TerraformConfig(
            resources=resources,
            variables=variables,
            outputs=outputs,
            providers=providers,
            modules=modules,
            data_sources=data_sources,
            locals=locals_block,
            source_file=file_path,
            terraform_version=terraform_block.get("required_version"),
            required_providers=terraform_block.get("required_providers", {}),
        )

        info(
            "Terraform configuration parsing completed",
            file_path=str(file_path),
            total_resources=self._resource_count,
            errors=self._error_count,
            resource_types=len(config.resource_types),
            provider_types=len(config.provider_types),
        )

        if self._error_count > 0:
            warning(
                f"Parsing completed with {self._error_count} errors. "
                f"Some resources may have been skipped."
            )

        return config

    def validate(self, config: TerraformConfig) -> list[str]:
        """Validate a Terraform configuration.

        Args:
            config: The configuration to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors: list[str] = []

        # Validate resources
        for resource in config.resources:
            resource_errors = self._validate_resource(resource)
            errors.extend(resource_errors)

        # Validate providers
        for provider_name, provider_config in config.providers.items():
            provider_errors = self._validate_provider(provider_name, provider_config)
            errors.extend(provider_errors)

        # Validate required providers are used
        unused_providers = set(config.required_providers.keys()) - config.provider_types
        for unused in unused_providers:
            errors.append(f"Required provider '{unused}' is declared but not used")

        return errors

    def _validate_file_access(self, file_path: Path) -> None:
        """Validate that the file exists and is readable."""
        if not file_path.exists():
            raise FileSystemError(
                f"Terraform file not found: {file_path}",
                file_path=str(file_path),
                operation="read",
                suggestions=[
                    "Check that the file path is correct",
                    "Ensure the file exists in the specified location",
                    "Verify you have read permissions for the file",
                ],
            )

        if not file_path.is_file():
            raise FileSystemError(
                f"Path is not a file: {file_path}",
                file_path=str(file_path),
                operation="read",
                suggestions=[
                    "Ensure the path points to a file, not a directory",
                    "Check that the file extension is correct (.tf)",
                ],
            )

        # Check file size for reasonable limits
        file_size = file_path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            warning(
                "Large Terraform file detected, parsing may be slow",
                file_path=str(file_path),
                file_size=file_size,
            )

        debug("File validation passed", file_path=str(file_path), file_size=file_size)

    def _parse_hcl_file(self, file_path: Path) -> dict[str, Any]:
        """Parse HCL file content into dictionary."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

                if not content.strip():
                    warning("Terraform file is empty", file_path=str(file_path))
                    return {}

                debug("Parsing HCL content", file_path=str(file_path), content_length=len(content))
                return hcl2.loads(content)

        except UnicodeDecodeError as e:
            raise TerraformParsingError(
                f"File encoding error in {file_path}: {e!s}",
                terraform_file=str(file_path),
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
                f"Failed to parse Terraform file {file_path}: {e!s}",
                terraform_file=str(file_path),
                hcl_error=str(e),
                suggestions=suggestions,
            ) from e

    def _extract_resources(
        self, hcl_config: dict[str, Any], file_path: Path
    ) -> list[dict[str, Any]]:
        """Extract and process resource blocks."""
        if "resource" not in hcl_config:
            warning(
                "No resource blocks found in Terraform configuration",
                file_path=str(file_path),
                available_blocks=list(hcl_config.keys()),
            )
            return []

        resources: list[dict[str, Any]] = []

        try:
            for resource_block in hcl_config["resource"]:
                for resource_type, instances in resource_block.items():
                    for name, config in instances.items():
                        try:
                            resource = self._process_resource(
                                resource_type, name, config, file_path
                            )
                            resources.append(resource)
                            self._resource_count += 1

                        except Exception as resource_error:
                            self._error_count += 1
                            error(
                                "Failed to process resource",
                                resource_type=resource_type,
                                resource_name=name,
                                error=str(resource_error),
                            )

                            # Try to recover by skipping this resource
                            self._handle_resource_error(
                                resource_type, name, resource_error, file_path
                            )

        except Exception as e:
            raise TerraformParsingError(
                f"Error processing resource blocks in {file_path}: {e!s}",
                terraform_file=str(file_path),
                suggestions=[
                    "Check the structure of resource blocks in the file",
                    "Ensure proper nesting and syntax",
                    "Verify that all resource blocks are properly formatted",
                ],
            ) from e

        return resources

    def _process_resource(
        self, resource_type: str, name: str, config: dict[str, Any], file_path: Path
    ) -> dict[str, Any]:
        """Process a single resource with provider-specific parsing."""
        debug("Processing resource", resource_type=resource_type, resource_name=name)

        # Create base resource structure
        resource = {
            "id": name,
            "resource_type": resource_type,
            "name": name,
        }

        # Add all configuration attributes
        for key, value in config.items():
            if isinstance(value, dict):
                resource[key] = dict(value)
            elif isinstance(value, list):
                resource[key] = list(value)
            else:
                resource[key] = value

        # Apply provider-specific parsing
        parser = self._cloud_detector.get_parser_for_resource(resource_type)
        if parser:
            debug(
                "Using provider-specific parser",
                resource_type=resource_type,
                parser_type=type(parser).__name__,
            )
            try:
                resource = parser.parse_resource(resource_type, resource)
                resource = parser.normalize_attributes(resource)
            except Exception as parse_error:
                warning(
                    "Provider-specific parsing failed, using fallback",
                    resource_type=resource_type,
                    resource_name=name,
                    error=str(parse_error),
                )
                resource = self._apply_legacy_parsing(resource)
        else:
            debug("Using legacy parsing for resource", resource_type=resource_type)
            resource = self._apply_legacy_parsing(resource)

        return resource

    def _apply_legacy_parsing(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Apply legacy parsing logic for backward compatibility."""
        # Convert tags from list to dict if needed (legacy AWS behavior)
        if "tags" in resource and isinstance(resource["tags"], list):
            tags_dict = {}
            for tag in resource["tags"]:
                if isinstance(tag, dict) and "Key" in tag and "Value" in tag:
                    tags_dict[tag["Key"]] = tag["Value"]
            resource["tags"] = tags_dict

        return resource

    def _handle_resource_error(
        self, resource_type: str, name: str, error: Exception, file_path: Path
    ) -> None:
        """Handle resource processing errors with recovery."""
        try:
            handle_error_with_recovery(
                TerraformParsingError(
                    f"Failed to process resource {resource_type}.{name}: {error!s}",
                    terraform_file=str(file_path),
                    suggestions=[
                        f"Check the configuration for resource {resource_type}.{name}",
                        "Verify all required attributes are present",
                        "Check for syntax errors in the resource block",
                    ],
                )
            )
        except TerraformParsingError:
            # If recovery fails, continue with next resource
            pass

    def _extract_variables(self, hcl_config: dict[str, Any]) -> dict[str, Any]:
        """Extract variable blocks."""
        if "variable" not in hcl_config:
            return {}

        variables = {}
        for var_block in hcl_config["variable"]:
            for var_name, var_config in var_block.items():
                variables[var_name] = dict(var_config) if var_config else {}

        debug("Extracted variables", count=len(variables))
        return variables

    def _extract_outputs(self, hcl_config: dict[str, Any]) -> dict[str, Any]:
        """Extract output blocks."""
        if "output" not in hcl_config:
            return {}

        outputs = {}
        for output_block in hcl_config["output"]:
            for output_name, output_config in output_block.items():
                outputs[output_name] = dict(output_config) if output_config else {}

        debug("Extracted outputs", count=len(outputs))
        return outputs

    def _extract_providers(self, hcl_config: dict[str, Any]) -> dict[str, Any]:
        """Extract provider blocks."""
        if "provider" not in hcl_config:
            return {}

        providers = {}
        for provider_block in hcl_config["provider"]:
            for provider_name, provider_config in provider_block.items():
                providers[provider_name] = dict(provider_config) if provider_config else {}

        debug("Extracted providers", count=len(providers))
        return providers

    def _extract_modules(self, hcl_config: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract module blocks."""
        if "module" not in hcl_config:
            return []

        modules = []
        for module_block in hcl_config["module"]:
            for module_name, module_config in module_block.items():
                module_data = dict(module_config) if module_config else {}
                module_data["name"] = module_name
                modules.append(module_data)

        debug("Extracted modules", count=len(modules))
        return modules

    def _extract_data_sources(self, hcl_config: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract data source blocks."""
        if "data" not in hcl_config:
            return []

        data_sources = []
        for data_block in hcl_config["data"]:
            for data_type, instances in data_block.items():
                for data_name, data_config in instances.items():
                    data_source = dict(data_config) if data_config else {}
                    data_source["type"] = data_type
                    data_source["name"] = data_name
                    data_sources.append(data_source)

        debug("Extracted data sources", count=len(data_sources))
        return data_sources

    def _extract_locals(self, hcl_config: dict[str, Any]) -> dict[str, Any]:
        """Extract locals blocks."""
        if "locals" not in hcl_config:
            return {}

        locals_dict = {}
        for locals_block in hcl_config["locals"]:
            if isinstance(locals_block, dict):
                locals_dict.update(locals_block)

        debug("Extracted locals", count=len(locals_dict))
        return locals_dict

    def _extract_terraform_block(self, hcl_config: dict[str, Any]) -> dict[str, Any]:
        """Extract terraform configuration block."""
        if "terraform" not in hcl_config:
            return {}

        terraform_config = {}
        for terraform_block in hcl_config["terraform"]:
            if isinstance(terraform_block, dict):
                terraform_config.update(terraform_block)

        # Ensure required_providers is a dict
        if "required_providers" in terraform_config:
            required_providers = terraform_config["required_providers"]
            if isinstance(required_providers, list):
                # Convert list format to dict format
                providers_dict = {}
                for provider_block in required_providers:
                    if isinstance(provider_block, dict):
                        providers_dict.update(provider_block)
                terraform_config["required_providers"] = providers_dict
            elif not isinstance(required_providers, dict):
                terraform_config["required_providers"] = {}

        debug("Extracted terraform block", config=terraform_config)
        return terraform_config

    def _validate_resource(self, resource: dict[str, Any]) -> list[str]:
        """Validate a single resource."""
        errors = []

        # Check required fields
        if not resource.get("resource_type"):
            errors.append(f"Resource missing resource_type: {resource.get('id', 'unknown')}")

        if not resource.get("name"):
            errors.append(f"Resource missing name: {resource.get('id', 'unknown')}")

        # Validate resource type format
        resource_type = resource.get("resource_type", "")
        if resource_type and "_" not in resource_type:
            errors.append(f"Invalid resource type format: {resource_type}")

        return errors

    def _validate_provider(self, provider_name: str, provider_config: dict[str, Any]) -> list[str]:
        """Validate a provider configuration."""
        errors = []

        # Basic provider validation
        if not provider_name:
            errors.append("Provider missing name")

        # Provider-specific validation could be added here

        return errors


def extract_terraform_config(tf_file: str) -> dict[str, list[dict[str, Any]]]:
    """Legacy function for backward compatibility.

    This function maintains the exact same interface as the original
    extract_terraform_config function to ensure backward compatibility.

    Args:
        tf_file: Path to the Terraform configuration file

    Returns:
        Dictionary containing extracted resources in legacy format

    Raises:
        TerraformParsingError: When the Terraform file cannot be parsed
        FileSystemError: When the file cannot be read
    """
    parser = TerraformConfigParser()
    config = parser.parse(Path(tf_file))

    # Convert to legacy format for backward compatibility
    return {"resources": config.resources}
