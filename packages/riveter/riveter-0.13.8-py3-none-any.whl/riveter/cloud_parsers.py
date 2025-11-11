"""Cloud provider-specific parsers for Terraform resources.

This module provides extensible, protocol-based parsers for different cloud providers,
enabling type-safe resource parsing and normalization with support for new providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Set, Type, Union


class CloudProviderParserProtocol(Protocol):
    """Protocol for cloud provider parsers to enable extensibility."""

    provider: str

    def get_supported_resource_types(self) -> Set[str]:
        """Return set of resource types supported by this provider."""
        ...

    def parse_resource(self, resource_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a resource configuration with provider-specific handling."""
        ...

    def normalize_attributes(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize resource attributes to a common format."""
        ...

    def supports_resource_type(self, resource_type: str) -> bool:
        """Check if this parser supports the given resource type."""
        ...

    def validate_resource_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate resource configuration and return list of issues."""
        ...


class ResourceNormalizerProtocol(Protocol):
    """Protocol for resource attribute normalizers."""

    def normalize_tags(self, tags: Any) -> Dict[str, str]:
        """Normalize tag formats to consistent dict."""
        ...

    def normalize_security_groups(self, security_groups: Any) -> List[str]:
        """Normalize security group references."""
        ...

    def normalize_reference(self, reference: Any) -> str:
        """Normalize Terraform references."""
        ...


class CloudProviderParser(ABC):
    """Enhanced base class for cloud provider-specific parsers with type safety."""

    def __init__(self, provider: str) -> None:
        self.provider = provider
        self._resource_validators: Dict[str, callable] = {}
        self._attribute_transformers: Dict[str, callable] = {}

    @abstractmethod
    def get_supported_resource_types(self) -> Set[str]:
        """Return set of resource types supported by this provider."""

    @abstractmethod
    def parse_resource(self, resource_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a resource configuration with provider-specific handling."""

    @abstractmethod
    def normalize_attributes(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize resource attributes to a common format."""

    def supports_resource_type(self, resource_type: str) -> bool:
        """Check if this parser supports the given resource type."""
        return resource_type in self.get_supported_resource_types()

    def validate_resource_config(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate resource configuration and return list of issues.

        Args:
            resource_type: Type of the resource to validate
            config: Resource configuration to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check if resource type is supported
        if not self.supports_resource_type(resource_type):
            issues.append(f"Unsupported resource type: {resource_type}")
            return issues

        # Run custom validator if available
        if resource_type in self._resource_validators:
            validator_issues = self._resource_validators[resource_type](config)
            issues.extend(validator_issues)

        # Basic validation
        if not isinstance(config, dict):
            issues.append("Resource configuration must be a dictionary")
            return issues

        # Validate required fields based on resource type
        required_fields = self._get_required_fields(resource_type)
        for field in required_fields:
            if field not in config:
                issues.append(f"Missing required field: {field}")

        return issues

    def register_resource_validator(self, resource_type: str, validator: callable) -> None:
        """Register a custom validator for a resource type.

        Args:
            resource_type: Resource type to validate
            validator: Callable that takes config dict and returns list of issues
        """
        self._resource_validators[resource_type] = validator

    def register_attribute_transformer(self, attribute: str, transformer: callable) -> None:
        """Register a custom attribute transformer.

        Args:
            attribute: Attribute name to transform
            transformer: Callable that takes attribute value and returns transformed value
        """
        self._attribute_transformers[attribute] = transformer

    def _get_required_fields(self, resource_type: str) -> List[str]:
        """Get required fields for a resource type.

        Args:
            resource_type: Resource type

        Returns:
            List of required field names
        """
        # Override in subclasses to provide resource-specific required fields
        return []

    def _apply_attribute_transformers(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply registered attribute transformers to configuration.

        Args:
            config: Resource configuration

        Returns:
            Transformed configuration
        """
        transformed = dict(config)

        for attribute, transformer in self._attribute_transformers.items():
            if attribute in transformed:
                try:
                    transformed[attribute] = transformer(transformed[attribute])
                except Exception as e:
                    # Log transformation error but don't fail parsing
                    from .logging import warning

                    warning(f"Failed to transform attribute {attribute}", error=str(e))

        return transformed


class AWSParser(CloudProviderParser):
    """Parser for AWS resources."""

    def __init__(self) -> None:
        super().__init__("aws")

    def get_supported_resource_types(self) -> Set[str]:
        """Return AWS resource types."""
        return {
            "aws_instance",
            "aws_s3_bucket",
            "aws_s3_bucket_public_access_block",
            "aws_s3_bucket_encryption",
            "aws_s3_bucket_versioning",
            "aws_security_group",
            "aws_security_group_rule",
            "aws_vpc",
            "aws_subnet",
            "aws_route_table",
            "aws_internet_gateway",
            "aws_nat_gateway",
            "aws_rds_instance",
            "aws_rds_cluster",
            "aws_db_subnet_group",
            "aws_iam_role",
            "aws_iam_policy",
            "aws_iam_user",
            "aws_iam_group",
            "aws_kms_key",
            "aws_cloudtrail",
            "aws_cloudwatch_log_group",
            "aws_lambda_function",
            "aws_api_gateway_rest_api",
            "aws_elb",
            "aws_lb",
            "aws_autoscaling_group",
            "aws_launch_configuration",
            "aws_launch_template",
        }

    def parse_resource(self, resource_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AWS resource with AWS-specific handling."""
        parsed_config = dict(config)

        # Apply registered attribute transformers first
        parsed_config = self._apply_attribute_transformers(parsed_config)

        # Handle AWS-specific attribute transformations
        parsed_config = self._handle_aws_tags(parsed_config)
        parsed_config = self._handle_aws_security_groups(parsed_config)
        parsed_config = self._handle_aws_block_devices(parsed_config)

        return parsed_config

    def normalize_attributes(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize AWS resource attributes."""
        normalized = dict(resource)

        # Normalize common AWS patterns
        if "tags" in normalized:
            normalized["tags"] = self._normalize_tags(normalized["tags"])

        # Normalize security group references
        if "security_groups" in normalized:
            normalized["security_groups"] = self._normalize_security_groups(
                normalized["security_groups"]
            )

        # Normalize subnet references
        if "subnet_id" in normalized:
            normalized["subnet_id"] = self._normalize_reference(normalized["subnet_id"])

        return normalized

    def _get_required_fields(self, resource_type: str) -> List[str]:
        """Get required fields for AWS resource types."""
        aws_required_fields = {
            "aws_instance": ["instance_type"],
            "aws_s3_bucket": [],  # S3 buckets have no strictly required fields
            "aws_security_group": ["name"],
            "aws_vpc": ["cidr_block"],
            "aws_subnet": ["vpc_id", "cidr_block"],
            "aws_rds_instance": ["instance_class", "engine"],
            "aws_iam_role": ["assume_role_policy"],
            "aws_kms_key": [],
            "aws_lambda_function": ["function_name", "runtime", "handler"],
        }
        return aws_required_fields.get(resource_type, [])

    def _handle_aws_tags(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AWS tag formats."""
        if "tags" in config:
            if isinstance(config["tags"], list):
                # Convert list format to dict
                tags_dict = {}
                for tag in config["tags"]:
                    if isinstance(tag, dict) and "Key" in tag and "Value" in tag:
                        tags_dict[tag["Key"]] = tag["Value"]
                    elif isinstance(tag, dict) and "key" in tag and "value" in tag:
                        tags_dict[tag["key"]] = tag["value"]
                config["tags"] = tags_dict

        return config

    def _handle_aws_security_groups(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AWS security group references."""
        if "security_groups" in config:
            if isinstance(config["security_groups"], str):
                config["security_groups"] = [config["security_groups"]]

        if "vpc_security_group_ids" in config:
            if isinstance(config["vpc_security_group_ids"], str):
                config["vpc_security_group_ids"] = [config["vpc_security_group_ids"]]

        return config

    def _handle_aws_block_devices(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AWS block device configurations."""
        # Handle root_block_device
        if "root_block_device" in config:
            if isinstance(config["root_block_device"], list) and config["root_block_device"]:
                config["root_block_device"] = config["root_block_device"][0]

        # Handle ebs_block_device
        if "ebs_block_device" in config:
            if not isinstance(config["ebs_block_device"], list):
                config["ebs_block_device"] = [config["ebs_block_device"]]

        return config

    def _normalize_tags(self, tags: Any) -> Dict[str, str]:
        """Normalize tag formats to consistent dict."""
        if isinstance(tags, dict):
            return {str(k): str(v) for k, v in tags.items()}
        if isinstance(tags, list):
            result = {}
            for tag in tags:
                if isinstance(tag, dict):
                    if "Key" in tag and "Value" in tag:
                        result[tag["Key"]] = tag["Value"]
                    elif "key" in tag and "value" in tag:
                        result[tag["key"]] = tag["value"]
            return result
        return {}

    def _normalize_security_groups(self, security_groups: Any) -> List[str]:
        """Normalize security group references."""
        if isinstance(security_groups, str):
            return [security_groups]
        if isinstance(security_groups, list):
            return [str(sg) for sg in security_groups]
        return []

    def _normalize_reference(self, reference: Any) -> str:
        """Normalize Terraform references."""
        if isinstance(reference, str):
            return reference
        if isinstance(reference, dict) and "Ref" in reference:
            return str(reference["Ref"])
        return str(reference)


class AzureParser(CloudProviderParser):
    """Parser for Azure resources."""

    def __init__(self) -> None:
        super().__init__("azurerm")

    def get_supported_resource_types(self) -> Set[str]:
        """Return Azure resource types."""
        return {
            "azurerm_virtual_machine",
            "azurerm_linux_virtual_machine",
            "azurerm_windows_virtual_machine",
            "azurerm_storage_account",
            "azurerm_storage_container",
            "azurerm_storage_blob",
            "azurerm_network_security_group",
            "azurerm_network_security_rule",
            "azurerm_virtual_network",
            "azurerm_subnet",
            "azurerm_route_table",
            "azurerm_public_ip",
            "azurerm_network_interface",
            "azurerm_sql_server",
            "azurerm_sql_database",
            "azurerm_postgresql_server",
            "azurerm_mysql_server",
            "azurerm_key_vault",
            "azurerm_key_vault_secret",
            "azurerm_resource_group",
            "azurerm_log_analytics_workspace",
            "azurerm_monitor_diagnostic_setting",
            "azurerm_function_app",
            "azurerm_app_service",
            "azurerm_application_gateway",
            "azurerm_load_balancer",
        }

    def parse_resource(self, resource_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Azure resource with Azure-specific handling."""
        parsed_config = dict(config)

        # Apply registered attribute transformers first
        parsed_config = self._apply_attribute_transformers(parsed_config)

        # Handle Azure-specific attribute transformations
        parsed_config = self._handle_azure_tags(parsed_config)
        parsed_config = self._handle_azure_network_security_rules(parsed_config)
        parsed_config = self._handle_azure_storage_settings(parsed_config)

        return parsed_config

    def normalize_attributes(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Azure resource attributes."""
        normalized = dict(resource)

        # Normalize common Azure patterns
        if "tags" in normalized:
            normalized["tags"] = self._normalize_tags(normalized["tags"])

        # Normalize location to region for consistency
        if "location" in normalized:
            normalized["region"] = normalized["location"]

        # Normalize resource group references
        if "resource_group_name" in normalized:
            normalized["resource_group_name"] = self._normalize_reference(
                normalized["resource_group_name"]
            )

        return normalized

    def _get_required_fields(self, resource_type: str) -> List[str]:
        """Get required fields for Azure resource types."""
        azure_required_fields = {
            "azurerm_virtual_machine": ["name", "location", "resource_group_name"],
            "azurerm_linux_virtual_machine": ["name", "location", "resource_group_name", "size"],
            "azurerm_windows_virtual_machine": ["name", "location", "resource_group_name", "size"],
            "azurerm_storage_account": [
                "name",
                "location",
                "resource_group_name",
                "account_tier",
                "account_replication_type",
            ],
            "azurerm_network_security_group": ["name", "location", "resource_group_name"],
            "azurerm_virtual_network": ["name", "location", "resource_group_name", "address_space"],
            "azurerm_subnet": [
                "name",
                "resource_group_name",
                "virtual_network_name",
                "address_prefixes",
            ],
            "azurerm_resource_group": ["name", "location"],
        }
        return azure_required_fields.get(resource_type, [])

    def _handle_azure_tags(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Azure tag formats."""
        if "tags" in config:
            if isinstance(config["tags"], dict):
                # Azure tags are typically already in dict format
                config["tags"] = {str(k): str(v) for k, v in config["tags"].items()}

        return config

    def _handle_azure_network_security_rules(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Azure network security rule configurations."""
        if "security_rule" in config:
            if not isinstance(config["security_rule"], list):
                config["security_rule"] = [config["security_rule"]]

        return config

    def _handle_azure_storage_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Azure storage-specific settings."""
        # Handle storage account tier normalization
        if "account_tier" in config:
            config["account_tier"] = str(config["account_tier"]).title()

        # Handle replication type normalization
        if "account_replication_type" in config:
            config["account_replication_type"] = str(config["account_replication_type"]).upper()

        return config

    def _normalize_tags(self, tags: Any) -> Dict[str, str]:
        """Normalize Azure tag formats."""
        if isinstance(tags, dict):
            return {str(k): str(v) for k, v in tags.items()}
        return {}

    def _normalize_reference(self, reference: Any) -> str:
        """Normalize Azure resource references."""
        if isinstance(reference, str):
            return reference
        return str(reference)


class GCPParser(CloudProviderParser):
    """Parser for Google Cloud Platform resources."""

    def __init__(self) -> None:
        super().__init__("google")

    def get_supported_resource_types(self) -> Set[str]:
        """Return GCP resource types."""
        return {
            "google_compute_instance",
            "google_compute_disk",
            "google_compute_network",
            "google_compute_subnetwork",
            "google_compute_firewall",
            "google_compute_router",
            "google_compute_address",
            "google_storage_bucket",
            "google_storage_bucket_object",
            "google_sql_database_instance",
            "google_sql_database",
            "google_sql_user",
            "google_container_cluster",
            "google_container_node_pool",
            "google_project_iam_binding",
            "google_project_iam_member",
            "google_service_account",
            "google_kms_key_ring",
            "google_kms_crypto_key",
            "google_logging_project_sink",
            "google_monitoring_alert_policy",
            "google_cloud_function",
            "google_app_engine_application",
            "google_compute_backend_service",
            "google_compute_load_balancer",
        }

    def parse_resource(self, resource_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GCP resource with GCP-specific handling."""
        parsed_config = dict(config)

        # Apply registered attribute transformers first
        parsed_config = self._apply_attribute_transformers(parsed_config)

        # Handle GCP-specific attribute transformations
        parsed_config = self._handle_gcp_labels(parsed_config)
        parsed_config = self._handle_gcp_network_tags(parsed_config)
        parsed_config = self._handle_gcp_boot_disk(parsed_config)

        return parsed_config

    def normalize_attributes(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize GCP resource attributes."""
        normalized = dict(resource)

        # Normalize GCP labels to tags for consistency
        if "labels" in normalized:
            normalized["tags"] = self._normalize_labels(normalized["labels"])

        # Normalize zone to region for consistency
        if "zone" in normalized:
            # Extract region from zone (e.g., us-central1-a -> us-central1)
            zone = normalized["zone"]
            if isinstance(zone, str) and zone.count("-") >= 2:
                normalized["region"] = "-".join(zone.split("-")[:-1])

        # Normalize project references
        if "project" in normalized:
            normalized["project"] = self._normalize_reference(normalized["project"])

        return normalized

    def _get_required_fields(self, resource_type: str) -> List[str]:
        """Get required fields for GCP resource types."""
        gcp_required_fields = {
            "google_compute_instance": ["name", "machine_type", "zone"],
            "google_compute_disk": ["name", "zone"],
            "google_compute_network": ["name"],
            "google_compute_subnetwork": ["name", "ip_cidr_range", "region", "network"],
            "google_compute_firewall": ["name", "network"],
            "google_storage_bucket": ["name"],
            "google_sql_database_instance": ["name", "database_version"],
            "google_container_cluster": ["name", "location"],
            "google_service_account": ["account_id"],
            "google_kms_key_ring": ["name", "location"],
            "google_cloud_function": ["name", "runtime", "entry_point"],
        }
        return gcp_required_fields.get(resource_type, [])

    def _handle_gcp_labels(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GCP label formats."""
        if "labels" in config:
            if isinstance(config["labels"], dict):
                config["labels"] = {str(k): str(v) for k, v in config["labels"].items()}

        return config

    def _handle_gcp_network_tags(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GCP network tag configurations."""
        if "tags" in config:
            if isinstance(config["tags"], str):
                config["tags"] = [config["tags"]]
            elif not isinstance(config["tags"], list):
                config["tags"] = []

        return config

    def _handle_gcp_boot_disk(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GCP boot disk configurations."""
        if "boot_disk" in config:
            if isinstance(config["boot_disk"], list) and config["boot_disk"]:
                config["boot_disk"] = config["boot_disk"][0]

        return config

    def _normalize_labels(self, labels: Any) -> Dict[str, str]:
        """Normalize GCP labels to tags format."""
        if isinstance(labels, dict):
            return {str(k): str(v) for k, v in labels.items()}
        return {}

    def _normalize_reference(self, reference: Any) -> str:
        """Normalize GCP resource references."""
        if isinstance(reference, str):
            return reference
        return str(reference)


class CloudProviderRegistry:
    """Registry for cloud provider parsers with extensibility support."""

    def __init__(self) -> None:
        self._parsers: Dict[str, CloudProviderParserProtocol] = {}
        self._register_default_parsers()

    def _register_default_parsers(self) -> None:
        """Register default cloud provider parsers."""
        self.register_parser("aws", AWSParser())
        self.register_parser("azurerm", AzureParser())
        self.register_parser("google", GCPParser())

    def register_parser(self, provider: str, parser: CloudProviderParserProtocol) -> None:
        """Register a cloud provider parser.

        Args:
            provider: Provider name (e.g., 'aws', 'azure', 'gcp')
            parser: Parser instance implementing CloudProviderParserProtocol
        """
        self._parsers[provider] = parser
        from .logging import debug

        debug(
            f"Registered cloud provider parser",
            provider=provider,
            parser_type=type(parser).__name__,
        )

    def unregister_parser(self, provider: str) -> None:
        """Unregister a cloud provider parser.

        Args:
            provider: Provider name to unregister
        """
        if provider in self._parsers:
            del self._parsers[provider]
            from .logging import debug

            debug(f"Unregistered cloud provider parser", provider=provider)

    def get_parser(self, provider: str) -> Optional[CloudProviderParserProtocol]:
        """Get parser for a specific provider.

        Args:
            provider: Provider name

        Returns:
            Parser instance or None if not found
        """
        return self._parsers.get(provider)

    def get_parser_for_resource(self, resource_type: str) -> Optional[CloudProviderParserProtocol]:
        """Get the appropriate parser for a resource type.

        Args:
            resource_type: Resource type to find parser for

        Returns:
            Parser instance or None if no parser supports the resource type
        """
        for parser in self._parsers.values():
            if parser.supports_resource_type(resource_type):
                return parser
        return None

    def get_supported_providers(self) -> Set[str]:
        """Get set of supported provider names.

        Returns:
            Set of provider names
        """
        return set(self._parsers.keys())

    def get_all_supported_resource_types(self) -> Dict[str, Set[str]]:
        """Get all supported resource types by provider.

        Returns:
            Dictionary mapping provider names to their supported resource types
        """
        return {
            provider: parser.get_supported_resource_types()
            for provider, parser in self._parsers.items()
        }

    def validate_resource(self, resource_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate a resource configuration using the appropriate parser.

        Args:
            resource_type: Type of resource to validate
            config: Resource configuration

        Returns:
            List of validation issues (empty if valid)
        """
        parser = self.get_parser_for_resource(resource_type)
        if not parser:
            return [f"No parser found for resource type: {resource_type}"]

        return parser.validate_resource_config(resource_type, config)


class CloudProviderDetector:
    """Detects cloud provider based on resource types with extensible registry."""

    def __init__(self, registry: Optional[CloudProviderRegistry] = None) -> None:
        """Initialize detector with optional custom registry.

        Args:
            registry: Custom registry instance, creates default if None
        """
        self.registry = registry or CloudProviderRegistry()

    def detect_providers(self, resources: List[Dict[str, Any]]) -> Set[str]:
        """Detect which cloud providers are used in the resources.

        Args:
            resources: List of resource configurations

        Returns:
            Set of detected provider names
        """
        providers = set()

        for resource in resources:
            resource_type = resource.get("resource_type", "")
            parser = self.registry.get_parser_for_resource(resource_type)
            if parser:
                providers.add(parser.provider)

        return providers

    def get_parser_for_resource(self, resource_type: str) -> Optional[CloudProviderParserProtocol]:
        """Get the appropriate parser for a resource type.

        Args:
            resource_type: Resource type to find parser for

        Returns:
            Parser instance or None if not found
        """
        return self.registry.get_parser_for_resource(resource_type)

    def get_parser(self, provider: str) -> Optional[CloudProviderParserProtocol]:
        """Get parser for a specific provider.

        Args:
            provider: Provider name

        Returns:
            Parser instance or None if not found
        """
        return self.registry.get_parser(provider)

    def register_custom_parser(self, provider: str, parser: CloudProviderParserProtocol) -> None:
        """Register a custom cloud provider parser.

        Args:
            provider: Provider name
            parser: Parser instance
        """
        self.registry.register_parser(provider, parser)

    def get_supported_providers(self) -> Set[str]:
        """Get set of supported provider names.

        Returns:
            Set of provider names
        """
        return self.registry.get_supported_providers()


# Global registry instance for convenience
_global_registry: Optional[CloudProviderRegistry] = None


def get_cloud_provider_registry() -> CloudProviderRegistry:
    """Get or create global cloud provider registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = CloudProviderRegistry()
    return _global_registry


def register_cloud_provider_parser(provider: str, parser: CloudProviderParserProtocol) -> None:
    """Register a cloud provider parser in the global registry.

    Args:
        provider: Provider name
        parser: Parser instance
    """
    get_cloud_provider_registry().register_parser(provider, parser)


def get_cloud_provider_parser(provider: str) -> Optional[CloudProviderParserProtocol]:
    """Get cloud provider parser from global registry.

    Args:
        provider: Provider name

    Returns:
        Parser instance or None if not found
    """
    return get_cloud_provider_registry().get_parser(provider)


def detect_cloud_providers(resources: List[Dict[str, Any]]) -> Set[str]:
    """Detect cloud providers in resources using global registry.

    Args:
        resources: List of resource configurations

    Returns:
        Set of detected provider names
    """
    detector = CloudProviderDetector(get_cloud_provider_registry())
    return detector.detect_providers(resources)
