"""Advanced caching system for Riveter.

This package provides intelligent caching for configurations, rules,
and validation results with automatic invalidation and memory management.
"""

from .manager import CacheManager
from .providers import DiskCacheProvider, MemoryCacheProvider, MultiLevelCacheProvider
from .strategies import CacheStrategy, LRUStrategy, TTLStrategy
from .types import CacheEntry, CacheKey, CacheStats

__all__ = [
    "CacheEntry",
    "CacheKey",
    "CacheManager",
    "CacheStats",
    "CacheStrategy",
    "DiskCacheProvider",
    "LRUStrategy",
    "MemoryCacheProvider",
    "MultiLevelCacheProvider",
    "TTLStrategy",
]
