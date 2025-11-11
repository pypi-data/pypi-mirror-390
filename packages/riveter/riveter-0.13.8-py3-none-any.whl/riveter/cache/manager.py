"""Cache manager for coordinating caching across Riveter components."""

import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..exceptions import CacheError
from ..logging import debug, info, warning
from ..models.config import RiveterConfig
from ..models.protocols import CacheProvider
from .providers import DiskCacheProvider, MemoryCacheProvider, MultiLevelCacheProvider
from .strategies import AdaptiveStrategy, LRUStrategy, TTLStrategy
from .types import CacheConfiguration, CacheKey, CacheStats, InvalidationRule


class CacheManager:
    """Manages caching across all Riveter components."""

    def __init__(self, config: Optional[CacheConfiguration] = None):
        self.config = config or CacheConfiguration()
        self.providers: Dict[str, CacheProvider] = {}
        self.invalidation_rules: List[InvalidationRule] = []
        self._cleanup_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # Initialize default providers
        self._setup_default_providers()

        # Start cleanup thread
        self._start_cleanup_thread()

    def _setup_default_providers(self) -> None:
        """Set up default cache providers."""
        # Memory cache for frequently accessed data
        memory_strategy = AdaptiveStrategy(
            max_entries=self.config.max_entries // 2, max_size_bytes=self.config.max_size_bytes // 4
        )
        memory_provider = MemoryCacheProvider(strategy=memory_strategy)

        # Disk cache for persistent storage
        if self.config.enable_disk_cache:
            disk_provider = DiskCacheProvider(
                cache_dir=self.config.disk_cache_path,
                max_size_bytes=self.config.max_size_bytes,
                compression=self.config.compression_enabled,
            )

            # Multi-level cache combining memory and disk
            self.providers["default"] = MultiLevelCacheProvider(
                memory_provider=memory_provider, disk_provider=disk_provider
            )
        else:
            self.providers["default"] = memory_provider

        # Specialized caches for different data types
        self.providers["terraform_configs"] = MemoryCacheProvider(
            strategy=TTLStrategy(default_ttl=1800.0)  # 30 minutes
        )

        self.providers["rule_packs"] = MemoryCacheProvider(strategy=LRUStrategy(max_entries=100))

        self.providers["validation_results"] = MemoryCacheProvider(
            strategy=TTLStrategy(default_ttl=600.0)  # 10 minutes
        )

    def get_provider(self, provider_name: str = "default") -> CacheProvider:
        """Get a cache provider by name."""
        if provider_name not in self.providers:
            raise CacheError(f"Cache provider '{provider_name}' not found")
        return self.providers[provider_name]

    def register_provider(self, name: str, provider: CacheProvider) -> None:
        """Register a custom cache provider."""
        self.providers[name] = provider
        debug(f"Registered cache provider: {name}")

    def cache_terraform_config(self, file_path: Path, config: Any) -> None:
        """Cache a parsed Terraform configuration."""
        if not file_path.exists():
            return

        file_mtime = file_path.stat().st_mtime
        cache_key = CacheKey.for_terraform_config(file_path, file_mtime)

        provider = self.get_provider("terraform_configs")
        provider.set(cache_key.cache_key, config, ttl=1800)  # 30 minutes

        debug(f"Cached Terraform config: {file_path}")

    def get_terraform_config(self, file_path: Path) -> Optional[Any]:
        """Get a cached Terraform configuration."""
        if not file_path.exists():
            return None

        file_mtime = file_path.stat().st_mtime
        cache_key = CacheKey.for_terraform_config(file_path, file_mtime)

        provider = self.get_provider("terraform_configs")
        config = provider.get(cache_key.cache_key)

        if config:
            debug(f"Cache hit for Terraform config: {file_path}")

        return config

    def cache_rule_pack(self, pack_name: str, pack_version: str, rule_pack: Any) -> None:
        """Cache a loaded rule pack."""
        cache_key = CacheKey.for_rule_pack(pack_name, pack_version)

        provider = self.get_provider("rule_packs")
        provider.set(cache_key.cache_key, rule_pack)

        debug(f"Cached rule pack: {pack_name} v{pack_version}")

    def get_rule_pack(self, pack_name: str, pack_version: str) -> Optional[Any]:
        """Get a cached rule pack."""
        cache_key = CacheKey.for_rule_pack(pack_name, pack_version)

        provider = self.get_provider("rule_packs")
        rule_pack = provider.get(cache_key.cache_key)

        if rule_pack:
            debug(f"Cache hit for rule pack: {pack_name} v{pack_version}")

        return rule_pack

    def cache_validation_result(
        self, config_path: Path, rule_pack_names: List[str], result: Any
    ) -> None:
        """Cache a validation result."""
        if not config_path.exists():
            return

        config_mtime = config_path.stat().st_mtime
        cache_key = CacheKey.for_validation_result(config_path, rule_pack_names, config_mtime)

        provider = self.get_provider("validation_results")
        provider.set(cache_key.cache_key, result, ttl=600)  # 10 minutes

        debug(f"Cached validation result for: {config_path}")

    def get_validation_result(self, config_path: Path, rule_pack_names: List[str]) -> Optional[Any]:
        """Get a cached validation result."""
        if not config_path.exists():
            return None

        config_mtime = config_path.stat().st_mtime
        cache_key = CacheKey.for_validation_result(config_path, rule_pack_names, config_mtime)

        provider = self.get_provider("validation_results")
        result = provider.get(cache_key.cache_key)

        if result:
            debug(f"Cache hit for validation result: {config_path}")

        return result

    def invalidate_terraform_config(self, file_path: Path) -> bool:
        """Invalidate cached Terraform configuration."""
        # We need to invalidate all versions of this file
        pattern = f"terraform_config:{file_path}:*"
        return self._invalidate_by_pattern(pattern, "terraform_configs")

    def invalidate_rule_pack(self, pack_name: str, pack_version: Optional[str] = None) -> bool:
        """Invalidate cached rule pack."""
        if pack_version:
            cache_key = CacheKey.for_rule_pack(pack_name, pack_version)
            provider = self.get_provider("rule_packs")
            return provider.delete(cache_key.cache_key)
        else:
            # Invalidate all versions
            pattern = f"rule_pack:{pack_name}:*"
            return self._invalidate_by_pattern(pattern, "rule_packs")

    def invalidate_validation_results(self, config_path: Optional[Path] = None) -> bool:
        """Invalidate validation results."""
        if config_path:
            pattern = f"validation_result:{config_path}:*"
        else:
            pattern = "validation_result:*"

        return self._invalidate_by_pattern(pattern, "validation_results")

    def _invalidate_by_pattern(self, pattern: str, provider_name: str) -> bool:
        """Invalidate cache entries matching a pattern."""
        try:
            provider = self.get_provider(provider_name)

            # This is a simplified implementation
            # In practice, you'd need to track keys or implement pattern matching
            if hasattr(provider, "entries"):
                # Memory cache provider
                import fnmatch

                keys_to_delete = [
                    key for key in provider.entries.keys() if fnmatch.fnmatch(key, pattern)
                ]

                for key in keys_to_delete:
                    provider.delete(key)

                return len(keys_to_delete) > 0

            return False

        except Exception as e:
            warning(f"Error invalidating cache pattern {pattern}: {e}")
            return False

    def add_invalidation_rule(self, rule: InvalidationRule) -> None:
        """Add a cache invalidation rule."""
        self.invalidation_rules.append(rule)
        debug(f"Added invalidation rule: {rule.key_pattern}")

    def remove_invalidation_rule(self, rule: InvalidationRule) -> bool:
        """Remove a cache invalidation rule."""
        if rule in self.invalidation_rules:
            self.invalidation_rules.remove(rule)
            return True
        return False

    def apply_invalidation_rules(self) -> int:
        """Apply all invalidation rules and return number of invalidated entries."""
        total_invalidated = 0

        for provider_name, provider in self.providers.items():
            if hasattr(provider, "entries"):
                entries_to_invalidate = []

                for key, entry in provider.entries.items():
                    for rule in self.invalidation_rules:
                        if rule.matches_key(entry.key) and rule.should_invalidate(entry):
                            entries_to_invalidate.append(key)
                            break

                for key in entries_to_invalidate:
                    if provider.delete(key):
                        total_invalidated += 1

        if total_invalidated > 0:
            debug(f"Invalidated {total_invalidated} cache entries via rules")

        return total_invalidated

    def cleanup_expired(self) -> int:
        """Clean up expired entries from all providers."""
        total_cleaned = 0

        for provider_name, provider in self.providers.items():
            if hasattr(provider, "cleanup_expired"):
                cleaned = provider.cleanup_expired()
                total_cleaned += cleaned

                if cleaned > 0:
                    debug(f"Cleaned {cleaned} expired entries from {provider_name}")

        return total_cleaned

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            "providers": {},
            "total_entries": 0,
            "total_size_bytes": 0,
            "overall_hit_rate": 0.0,
        }

        total_hits = 0
        total_requests = 0

        for provider_name, provider in self.providers.items():
            provider_stats = None

            if hasattr(provider, "get_stats"):
                provider_stats = provider.get_stats()
            elif hasattr(provider, "stats"):
                provider_stats = provider.stats

            if provider_stats:
                stats["providers"][provider_name] = provider_stats.to_dict()
                stats["total_entries"] += provider_stats.entries
                stats["total_size_bytes"] += provider_stats.total_size_bytes

                total_hits += provider_stats.hits
                total_requests += provider_stats.hits + provider_stats.misses

        if total_requests > 0:
            stats["overall_hit_rate"] = total_hits / total_requests

        return stats

    def clear_all_caches(self) -> None:
        """Clear all cache providers."""
        for provider_name, provider in self.providers.items():
            provider.clear()
            info(f"Cleared cache provider: {provider_name}")

    def _start_cleanup_thread(self) -> None:
        """Start the background cleanup thread."""
        if self.config.cleanup_interval <= 0:
            return

        def cleanup_worker():
            while not self._shutdown_event.wait(self.config.cleanup_interval):
                try:
                    # Clean up expired entries
                    expired_count = self.cleanup_expired()

                    # Apply invalidation rules
                    invalidated_count = self.apply_invalidation_rules()

                    if expired_count > 0 or invalidated_count > 0:
                        debug(
                            f"Cache cleanup: {expired_count} expired, {invalidated_count} invalidated"
                        )

                except Exception as e:
                    warning(f"Error during cache cleanup: {e}")

        self._cleanup_thread = threading.Thread(
            target=cleanup_worker, name="CacheCleanup", daemon=True
        )
        self._cleanup_thread.start()
        debug("Started cache cleanup thread")

    def shutdown(self) -> None:
        """Shutdown the cache manager and cleanup resources."""
        info("Shutting down cache manager")

        # Stop cleanup thread
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._shutdown_event.set()
            self._cleanup_thread.join(timeout=5.0)

        # Final cleanup
        self.cleanup_expired()

        # Clear providers if needed
        # Note: We don't clear by default to preserve cache across restarts

        info("Cache manager shutdown complete")

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the cache system."""
        health = {
            "status": "healthy",
            "issues": [],
            "warnings": [],
            "statistics": self.get_cache_statistics(),
        }

        # Check each provider
        for provider_name, provider in self.providers.items():
            try:
                # Try a simple operation
                test_key = f"__health_check_{int(time.time())}"
                provider.set(test_key, "test", ttl=1)
                value = provider.get(test_key)
                provider.delete(test_key)

                if value != "test":
                    health["issues"].append(f"Provider {provider_name} failed health check")
                    health["status"] = "degraded"

            except Exception as e:
                health["issues"].append(f"Provider {provider_name} error: {e}")
                health["status"] = "degraded"

        # Check disk space if using disk cache
        if self.config.enable_disk_cache and self.config.disk_cache_path:
            try:
                import shutil

                disk_usage = shutil.disk_usage(self.config.disk_cache_path)
                free_space = disk_usage.free

                if free_space < 100 * 1024 * 1024:  # Less than 100MB
                    health["warnings"].append("Low disk space for cache")

            except Exception as e:
                health["warnings"].append(f"Could not check disk space: {e}")

        return health
