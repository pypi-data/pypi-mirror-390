"""Type definitions for the caching system."""

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class CacheKeyType(Enum):
    """Types of cache keys."""

    TERRAFORM_CONFIG = "terraform_config"
    RULE_PACK = "rule_pack"
    RULE_VALIDATION = "rule_validation"
    VALIDATION_RESULT = "validation_result"
    PLUGIN_DATA = "plugin_data"
    PERFORMANCE_DATA = "performance_data"


@dataclass(frozen=True)
class CacheKey:
    """Represents a cache key with metadata."""

    key_type: CacheKeyType
    identifier: str
    version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Ensure metadata is immutable
        if self.metadata:
            object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def cache_key(self) -> str:
        """Generate the actual cache key string."""
        parts = [self.key_type.value, self.identifier]

        if self.version:
            parts.append(self.version)

        # Add metadata hash if present
        if self.metadata:
            metadata_str = str(sorted(self.metadata.items()))
            metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()[:8]
            parts.append(metadata_hash)

        return ":".join(parts)

    @classmethod
    def for_terraform_config(cls, file_path: Path, file_mtime: float) -> "CacheKey":
        """Create cache key for Terraform configuration."""
        return cls(
            key_type=CacheKeyType.TERRAFORM_CONFIG,
            identifier=str(file_path),
            version=str(int(file_mtime)),
        )

    @classmethod
    def for_rule_pack(cls, pack_name: str, pack_version: str) -> "CacheKey":
        """Create cache key for rule pack."""
        return cls(
            key_type=CacheKeyType.RULE_PACK,
            identifier=pack_name,
            version=pack_version,
        )

    @classmethod
    def for_validation_result(
        cls, config_path: Path, rule_pack_names: List[str], config_mtime: float
    ) -> "CacheKey":
        """Create cache key for validation result."""
        rule_packs_hash = hashlib.md5(":".join(sorted(rule_pack_names)).encode()).hexdigest()[:8]

        return cls(
            key_type=CacheKeyType.VALIDATION_RESULT,
            identifier=f"{config_path}:{rule_packs_hash}",
            version=str(int(config_mtime)),
        )


@dataclass
class CacheEntry:
    """Represents a cached entry with metadata."""

    key: CacheKey
    value: Any
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: Optional[int] = None

    @property
    def age(self) -> float:
        """Get the age of the entry in seconds."""
        return time.time() - self.created_at

    @property
    def time_since_access(self) -> float:
        """Get time since last access in seconds."""
        return time.time() - self.accessed_at

    @property
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.ttl is None:
            return False
        return self.age > self.ttl

    def touch(self) -> None:
        """Update access time and count."""
        self.accessed_at = time.time()
        self.access_count += 1

    def estimate_size(self) -> int:
        """Estimate the size of the cached value in bytes."""
        if self.size_bytes is not None:
            return self.size_bytes

        # Simple size estimation
        import sys

        try:
            size = sys.getsizeof(self.value)
            if hasattr(self.value, "__dict__"):
                size += sum(sys.getsizeof(v) for v in self.value.__dict__.values())
            self.size_bytes = size
            return size
        except (TypeError, AttributeError):
            return 1024  # Default estimate


@dataclass
class CacheStats:
    """Statistics about cache performance."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    entries: int = 0
    total_size_bytes: int = 0
    average_access_time: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate

    def record_hit(self, access_time: float = 0.0) -> None:
        """Record a cache hit."""
        self.hits += 1
        if access_time > 0:
            # Update running average
            total_accesses = self.hits + self.misses
            self.average_access_time = (
                self.average_access_time * (total_accesses - 1) + access_time
            ) / total_accesses

    def record_miss(self, access_time: float = 0.0) -> None:
        """Record a cache miss."""
        self.misses += 1
        if access_time > 0:
            # Update running average
            total_accesses = self.hits + self.misses
            self.average_access_time = (
                self.average_access_time * (total_accesses - 1) + access_time
            ) / total_accesses

    def record_eviction(self) -> None:
        """Record a cache eviction."""
        self.evictions += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "entries": self.entries,
            "total_size_bytes": self.total_size_bytes,
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
            "average_access_time": self.average_access_time,
        }


@dataclass
class CacheConfiguration:
    """Configuration for cache behavior."""

    max_entries: int = 1000
    max_size_bytes: int = 100 * 1024 * 1024  # 100MB
    default_ttl: Optional[float] = None  # No expiration by default
    cleanup_interval: float = 300.0  # 5 minutes
    enable_disk_cache: bool = True
    disk_cache_path: Optional[Path] = None
    compression_enabled: bool = True
    encryption_enabled: bool = False

    def __post_init__(self) -> None:
        """Set up default disk cache path if not provided."""
        if self.enable_disk_cache and self.disk_cache_path is None:
            self.disk_cache_path = Path.home() / ".riveter" / "cache"


@dataclass
class InvalidationRule:
    """Rule for cache invalidation."""

    key_pattern: str
    condition: str  # "file_changed", "time_expired", "manual"
    parameters: Dict[str, Any] = field(default_factory=dict)

    def matches_key(self, cache_key: CacheKey) -> bool:
        """Check if this rule matches a cache key."""
        import fnmatch

        return fnmatch.fnmatch(cache_key.cache_key, self.key_pattern)

    def should_invalidate(self, entry: CacheEntry) -> bool:
        """Check if an entry should be invalidated based on this rule."""
        if self.condition == "time_expired":
            max_age = self.parameters.get("max_age", 3600)  # 1 hour default
            return entry.age > max_age

        elif self.condition == "file_changed":
            file_path = self.parameters.get("file_path")
            if file_path and Path(file_path).exists():
                file_mtime = Path(file_path).stat().st_mtime
                cached_mtime = float(entry.key.version or 0)
                return file_mtime > cached_mtime

        elif self.condition == "manual":
            return True

        return False
