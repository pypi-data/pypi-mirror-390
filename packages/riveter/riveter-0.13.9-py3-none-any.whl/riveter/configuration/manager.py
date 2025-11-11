"""Configuration management system with dependency injection and caching.

This module provides a centralized configuration manager that handles
Terraform configuration parsing, validation, caching, and normalization
with comprehensive error handling and performance optimizations.
"""

from pathlib import Path
from typing import Any, Protocol

from ..logging import debug, error, info, warning
from ..models.config import TerraformConfig
from .cache import ConfigurationCache
from .parser import ConfigurationParser, TerraformConfigParser


class ConfigurationValidator(Protocol):
    """Protocol for configuration validators."""

    def validate(self, config: TerraformConfig) -> list[str]:
        """Validate a configuration and return list of validation errors."""
        ...


class ConfigurationNormalizer(Protocol):
    """Protocol for configuration normalizers."""

    def normalize(self, config: TerraformConfig) -> TerraformConfig:
        """Normalize a configuration and return the normalized version."""
        ...


class DefaultConfigurationValidator:
    """Default configuration validator implementation."""

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

        # Check for unused required providers
        used_providers = set()
        for resource in config.resources:
            resource_type = resource.get("resource_type", "")
            if "_" in resource_type:
                provider_type = resource_type.split("_")[0]
                used_providers.add(provider_type)

        unused_providers = set(config.required_providers.keys()) - used_providers
        for unused in unused_providers:
            errors.append(f"Required provider '{unused}' is declared but not used")

        return errors

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


class DefaultConfigurationNormalizer:
    """Default configuration normalizer implementation."""

    def normalize(self, config: TerraformConfig) -> TerraformConfig:
        """Normalize a Terraform configuration.

        Args:
            config: The configuration to normalize

        Returns:
            Normalized configuration
        """
        # Normalize resources
        normalized_resources = []
        for resource in config.resources:
            normalized_resource = self._normalize_resource(resource)
            normalized_resources.append(normalized_resource)

        # Create normalized configuration
        return TerraformConfig(
            resources=normalized_resources,
            variables=config.variables,
            outputs=config.outputs,
            providers=config.providers,
            modules=config.modules,
            data_sources=config.data_sources,
            locals=config.locals,
            source_file=config.source_file,
            terraform_version=config.terraform_version,
            required_providers=config.required_providers,
        )

    def _normalize_resource(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Normalize a single resource."""
        normalized = dict(resource)

        # Ensure consistent tag format
        if "tags" in normalized:
            tags = normalized["tags"]
            if isinstance(tags, list):
                # Convert list of tag objects to dict
                tag_dict = {}
                for tag in tags:
                    if isinstance(tag, dict):
                        if "Key" in tag and "Value" in tag:
                            tag_dict[tag["Key"]] = tag["Value"]
                        elif "key" in tag and "value" in tag:
                            tag_dict[tag["key"]] = tag["value"]
                normalized["tags"] = tag_dict
            elif not isinstance(tags, dict):
                # Convert other formats to empty dict
                normalized["tags"] = {}

        # Normalize boolean values
        for key, value in normalized.items():
            if isinstance(value, str) and value.lower() in ("true", "false"):
                normalized[key] = value.lower() == "true"

        return normalized


class ConfigurationManager:
    """Centralized configuration management with dependency injection and caching."""

    def __init__(
        self,
        parser: ConfigurationParser | None = None,
        cache: ConfigurationCache | None = None,
        validator: ConfigurationValidator | None = None,
        normalizer: ConfigurationNormalizer | None = None,
        cache_enabled: bool = True,
        validation_enabled: bool = True,
        normalization_enabled: bool = True,
    ) -> None:
        """Initialize configuration manager with dependency injection.

        Args:
            parser: Configuration parser to use. If None, TerraformConfigParser will be used.
            cache: Configuration cache to use. If None, default cache will be created.
            validator: Configuration validator to use. If None, default validator will be used.
            normalizer: Configuration normalizer to use. If None, default normalizer will be used.
            cache_enabled: Whether to enable configuration caching
            validation_enabled: Whether to enable configuration validation
            normalization_enabled: Whether to enable configuration normalization
        """
        self.parser = parser or TerraformConfigParser()
        self.cache = cache or ConfigurationCache(enabled=cache_enabled)
        self.validator = validator or DefaultConfigurationValidator()
        self.normalizer = normalizer or DefaultConfigurationNormalizer()

        self.cache_enabled = cache_enabled
        self.validation_enabled = validation_enabled
        self.normalization_enabled = normalization_enabled

        # Statistics
        self._cache_hits = 0
        self._cache_misses = 0
        self._parse_count = 0
        self._validation_errors = 0

        info(
            "Configuration manager initialized",
            cache_enabled=cache_enabled,
            validation_enabled=validation_enabled,
            normalization_enabled=normalization_enabled,
        )

    def load_terraform_config(
        self,
        file_path: str | Path,
        use_cache: bool | None = None,
        validate: bool | None = None,
        normalize: bool | None = None,
    ) -> TerraformConfig:
        """Load and process a Terraform configuration file.

        Args:
            file_path: Path to the Terraform configuration file
            use_cache: Whether to use caching (overrides instance setting)
            validate: Whether to validate configuration (overrides instance setting)
            normalize: Whether to normalize configuration (overrides instance setting)

        Returns:
            Processed TerraformConfig object

        Raises:
            TerraformParsingError: When the file cannot be parsed
            FileSystemError: When the file cannot be read
            ValueError: When validation fails and strict mode is enabled
        """
        # Convert string to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)

        use_cache = use_cache if use_cache is not None else self.cache_enabled
        validate = validate if validate is not None else self.validation_enabled
        normalize = normalize if normalize is not None else self.normalization_enabled

        info(
            "Loading Terraform configuration",
            file_path=str(file_path),
            use_cache=use_cache,
            validate=validate,
            normalize=normalize,
        )

        # Try to get from cache first
        config = None
        if use_cache:
            config = self.cache.get_config(file_path)
            if config is not None:
                self._cache_hits += 1
                debug("Configuration loaded from cache", file_path=str(file_path))
                return config
            self._cache_misses += 1

        # Parse configuration
        try:
            config = self.parser.parse(file_path)
            self._parse_count += 1
            debug("Configuration parsed from file", file_path=str(file_path))

        except Exception as e:
            error("Failed to parse configuration", file_path=str(file_path), error=str(e))
            raise

        # Validate configuration
        if validate:
            validation_errors = self.validator.validate(config)
            if validation_errors:
                self._validation_errors += len(validation_errors)
                warning(
                    "Configuration validation errors found",
                    file_path=str(file_path),
                    error_count=len(validation_errors),
                    errors=validation_errors,
                )
                # Note: We don't raise an exception here to maintain backward compatibility
                # The caller can check validation results if needed

        # Normalize configuration
        if normalize:
            try:
                config = self.normalizer.normalize(config)
                debug("Configuration normalized", file_path=str(file_path))
            except Exception as e:
                warning(
                    "Configuration normalization failed", file_path=str(file_path), error=str(e)
                )
                # Continue with unnormalized config

        # Cache the processed configuration
        if use_cache:
            try:
                self.cache.set_config(file_path, config)
                debug("Configuration cached", file_path=str(file_path))
            except Exception as e:
                warning("Failed to cache configuration", file_path=str(file_path), error=str(e))
                # Continue without caching

        info(
            "Configuration loaded successfully",
            file_path=str(file_path),
            resource_count=config.resource_count,
            resource_types=len(config.resource_types),
            provider_types=len(config.provider_types),
        )

        return config

    def validate_config(self, config: TerraformConfig) -> list[str]:
        """Validate a configuration and return validation errors.

        Args:
            config: Configuration to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        if not self.validation_enabled:
            return []

        try:
            errors = self.validator.validate(config)
            if errors:
                self._validation_errors += len(errors)
            return errors
        except Exception as e:
            error("Configuration validation failed", error=str(e))
            return [f"Validation error: {e!s}"]

    def normalize_config(self, config: TerraformConfig) -> TerraformConfig:
        """Normalize a configuration.

        Args:
            config: Configuration to normalize

        Returns:
            Normalized configuration
        """
        if not self.normalization_enabled:
            return config

        try:
            return self.normalizer.normalize(config)
        except Exception as e:
            warning("Configuration normalization failed", error=str(e))
            return config

    def invalidate_cache(self, file_path: Path | None = None) -> None:
        """Invalidate cached configurations.

        Args:
            file_path: Specific file to invalidate. If None, clears all cache.
        """
        if not self.cache_enabled:
            return

        if file_path is not None:
            self.cache.invalidate_config(file_path)
            info("Configuration cache invalidated", file_path=str(file_path))
        else:
            self.cache.clear_all()
            info("All configuration cache cleared")

    def cleanup_cache(self) -> int:
        """Clean up expired cache entries.

        Returns:
            Number of expired entries removed
        """
        if not self.cache_enabled:
            return 0

        removed_count = self.cache.cleanup_expired()
        if removed_count > 0:
            info("Cache cleanup completed", removed_count=removed_count)

        return removed_count

    def get_statistics(self) -> dict[str, Any]:
        """Get configuration manager statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "cache_enabled": self.cache_enabled,
            "validation_enabled": self.validation_enabled,
            "normalization_enabled": self.normalization_enabled,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "parse_count": self._parse_count,
            "validation_errors": self._validation_errors,
        }

        # Add cache statistics
        if self.cache_enabled:
            cache_stats = self.cache.get_cache_stats()
            stats["cache"] = cache_stats

        # Calculate cache hit rate
        total_requests = self._cache_hits + self._cache_misses
        if total_requests > 0:
            stats["cache_hit_rate"] = (self._cache_hits / total_requests) * 100.0
        else:
            stats["cache_hit_rate"] = 0.0

        return stats

    def reset_statistics(self) -> None:
        """Reset all statistics counters."""
        self._cache_hits = 0
        self._cache_misses = 0
        self._parse_count = 0
        self._validation_errors = 0

        debug("Configuration manager statistics reset")

    def configure_cache(
        self,
        enabled: bool | None = None,
        cache_dir: Path | None = None,
        default_ttl: int | None = None,
    ) -> None:
        """Reconfigure cache settings.

        Args:
            enabled: Whether to enable caching
            cache_dir: Cache directory path
            default_ttl: Default time-to-live for cache entries
        """
        if enabled is not None:
            self.cache_enabled = enabled
            self.cache.enabled = enabled

        if cache_dir is not None or default_ttl is not None:
            # Create new cache with updated settings
            from .cache import ConfigurationCache

            self.cache = ConfigurationCache(
                cache_dir=cache_dir,
                default_ttl=default_ttl or self.cache.default_ttl,
                enabled=self.cache_enabled,
            )

        info(
            "Cache configuration updated",
            enabled=self.cache_enabled,
            cache_dir=str(cache_dir) if cache_dir else None,
            default_ttl=default_ttl,
        )
