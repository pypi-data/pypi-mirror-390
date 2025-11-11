"""Caching implementations for validation performance optimization.

This module provides various caching strategies to improve validation
performance by avoiding redundant rule evaluations.
"""

import hashlib
import time
from dataclasses import dataclass
from typing import Any

from riveter.logging import debug, info, warning

from .protocols import CacheProviderProtocol


@dataclass
class CacheEntry:
    """Represents a cached validation result."""

    value: Any
    timestamp: float
    ttl: int | None = None
    access_count: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

    def touch(self) -> None:
        """Update access count and timestamp."""
        self.access_count += 1


class MemoryCache(CacheProviderProtocol):
    """In-memory cache implementation with TTL and size limits."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300) -> None:
        """Initialize memory cache.

        Args:
            max_size: Maximum number of entries to cache
            default_ttl: Default time-to-live in seconds
        """
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

        debug(f"Memory cache initialized with max_size={max_size}, default_ttl={default_ttl}")

    def get(self, key: str) -> Any:
        """Get value from cache."""
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]

        # Check if expired
        if entry.is_expired:
            del self._cache[key]
            self._misses += 1
            debug(f"Cache entry expired: {key}")
            return None

        # Update access info
        entry.touch()
        self._hits += 1

        debug(f"Cache hit: {key}")
        return entry.value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        # Use default TTL if not specified
        if ttl is None:
            ttl = self._default_ttl

        # Evict if at capacity
        if len(self._cache) >= self._max_size and key not in self._cache:
            self._evict_lru()

        # Store entry
        self._cache[key] = CacheEntry(value=value, timestamp=time.time(), ttl=ttl)

        debug(f"Cache set: {key} (ttl={ttl})")

    def clear(self) -> None:
        """Clear all cached values."""
        count = len(self._cache)
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        info(f"Cache cleared: {count} entries removed")

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find entry with oldest timestamp and lowest access count
        lru_key = min(
            self._cache.keys(),
            key=lambda k: (self._cache[k].access_count, self._cache[k].timestamp),
        )

        del self._cache[lru_key]
        debug(f"Evicted LRU entry: {lru_key}")

    @property
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "size": len(self._cache),
            "max_size": self._max_size,
        }


class NoOpCache(CacheProviderProtocol):
    """No-operation cache that doesn't actually cache anything."""

    def get(self, key: str) -> Any:
        """Always return None (cache miss)."""
        _ = key  # Mark as intentionally unused
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Do nothing."""

    def clear(self) -> None:
        """Do nothing."""


class ValidationResultCache:
    """Specialized cache for validation results with intelligent key generation."""

    def __init__(self, cache_provider: CacheProviderProtocol) -> None:
        """Initialize with a cache provider.

        Args:
            cache_provider: Cache implementation to use
        """
        self._cache = cache_provider
        self._key_prefix = "validation_result"

    def get_rule_result(self, rule_id: str, resource_id: str, resource_hash: str) -> Any:
        """Get cached rule evaluation result.

        Args:
            rule_id: Rule identifier
            resource_id: Resource identifier
            resource_hash: Hash of resource attributes

        Returns:
            Cached result or None if not found
        """
        key = self._make_key(rule_id, resource_id, resource_hash)
        return self._cache.get(key)

    def set_rule_result(
        self,
        rule_id: str,
        resource_id: str,
        resource_hash: str,
        result: Any,
        ttl: int | None = None,
    ) -> None:
        """Cache rule evaluation result.

        Args:
            rule_id: Rule identifier
            resource_id: Resource identifier
            resource_hash: Hash of resource attributes
            result: Result to cache
            ttl: Time to live in seconds
        """
        key = self._make_key(rule_id, resource_id, resource_hash)
        self._cache.set(key, result, ttl)

    def _make_key(self, rule_id: str, resource_id: str, resource_hash: str) -> str:
        """Generate cache key for rule evaluation."""
        return f"{self._key_prefix}:{rule_id}:{resource_id}:{resource_hash}"

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()


def hash_resource_attributes(attributes: dict[str, Any]) -> str:
    """Generate a hash of resource attributes for cache key generation.

    Args:
        attributes: Resource attributes dictionary

    Returns:
        SHA256 hash of the attributes
    """
    # Convert to sorted string representation for consistent hashing
    import json

    try:
        # Sort keys for consistent ordering
        sorted_attrs = json.dumps(attributes, sort_keys=True, default=str)
        return hashlib.sha256(sorted_attrs.encode()).hexdigest()[:16]  # Use first 16 chars
    except Exception as e:
        warning(f"Failed to hash resource attributes: {e!s}")
        # Fallback to string representation hash
        return hashlib.sha256(str(attributes).encode()).hexdigest()[:16]


class CacheManager:
    """Manages multiple cache instances and provides cache statistics."""

    def __init__(self):
        """Initialize cache manager."""
        self._caches: dict[str, CacheProviderProtocol] = {}
        self._default_cache = MemoryCache()

    def register_cache(self, name: str, cache: CacheProviderProtocol) -> None:
        """Register a named cache instance.

        Args:
            name: Cache name
            cache: Cache implementation
        """
        self._caches[name] = cache
        debug(f"Registered cache: {name}")

    def get_cache(self, name: str) -> CacheProviderProtocol:
        """Get cache by name.

        Args:
            name: Cache name

        Returns:
            Cache instance or default cache if not found
        """
        return self._caches.get(name, self._default_cache)

    def clear_all(self) -> None:
        """Clear all registered caches."""
        for name, cache in self._caches.items():
            cache.clear()
            debug(f"Cleared cache: {name}")

        self._default_cache.clear()
        info("All caches cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get statistics for all caches."""
        stats = {}

        for name, cache in self._caches.items():
            if hasattr(cache, "stats"):
                stats[name] = cache.stats

        if hasattr(self._default_cache, "stats"):
            stats["default"] = self._default_cache.stats

        return stats


# Global cache manager instance (validation-specific)
cache_manager = CacheManager()
