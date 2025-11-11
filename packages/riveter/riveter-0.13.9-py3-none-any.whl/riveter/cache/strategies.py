"""Cache eviction and management strategies."""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .types import CacheEntry, CacheKey


class CacheStrategy(ABC):
    """Base class for cache management strategies."""

    @abstractmethod
    def should_evict(self, entries: Dict[str, CacheEntry], new_entry_size: int) -> List[str]:
        """Determine which entries should be evicted to make room."""
        pass

    @abstractmethod
    def on_access(self, key: str, entry: CacheEntry) -> None:
        """Called when an entry is accessed."""
        pass

    @abstractmethod
    def on_insert(self, key: str, entry: CacheEntry) -> None:
        """Called when an entry is inserted."""
        pass

    @abstractmethod
    def on_remove(self, key: str, entry: CacheEntry) -> None:
        """Called when an entry is removed."""
        pass


class LRUStrategy(CacheStrategy):
    """Least Recently Used eviction strategy."""

    def __init__(self, max_entries: int = 1000, max_size_bytes: int = 100 * 1024 * 1024):
        self.max_entries = max_entries
        self.max_size_bytes = max_size_bytes
        self.access_order: List[str] = []

    def should_evict(self, entries: Dict[str, CacheEntry], new_entry_size: int) -> List[str]:
        """Evict least recently used entries."""
        to_evict = []

        # Calculate current size
        current_size = sum(entry.estimate_size() for entry in entries.values())
        current_count = len(entries)

        # Check if we need to evict based on size
        if current_size + new_entry_size > self.max_size_bytes:
            # Evict entries until we have enough space
            for key in self.access_order:
                if key in entries:
                    entry_size = entries[key].estimate_size()
                    to_evict.append(key)
                    current_size -= entry_size
                    if current_size + new_entry_size <= self.max_size_bytes:
                        break

        # Check if we need to evict based on count
        if current_count + 1 > self.max_entries:
            entries_to_remove = (current_count + 1) - self.max_entries
            for key in self.access_order:
                if key in entries and key not in to_evict:
                    to_evict.append(key)
                    entries_to_remove -= 1
                    if entries_to_remove <= 0:
                        break

        return to_evict

    def on_access(self, key: str, entry: CacheEntry) -> None:
        """Update access order."""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        entry.touch()

    def on_insert(self, key: str, entry: CacheEntry) -> None:
        """Add to access order."""
        if key not in self.access_order:
            self.access_order.append(key)

    def on_remove(self, key: str, entry: CacheEntry) -> None:
        """Remove from access order."""
        if key in self.access_order:
            self.access_order.remove(key)


class TTLStrategy(CacheStrategy):
    """Time-To-Live based eviction strategy."""

    def __init__(self, default_ttl: float = 3600.0, max_entries: int = 1000):
        self.default_ttl = default_ttl
        self.max_entries = max_entries

    def should_evict(self, entries: Dict[str, CacheEntry], new_entry_size: int) -> List[str]:
        """Evict expired entries and oldest entries if needed."""
        to_evict = []
        current_time = time.time()

        # First, evict expired entries
        for key, entry in entries.items():
            ttl = entry.ttl or self.default_ttl
            if current_time - entry.created_at > ttl:
                to_evict.append(key)

        # If still over limit, evict oldest entries
        remaining_entries = {k: v for k, v in entries.items() if k not in to_evict}
        if len(remaining_entries) + 1 > self.max_entries:
            # Sort by creation time (oldest first)
            sorted_entries = sorted(remaining_entries.items(), key=lambda x: x[1].created_at)

            entries_to_remove = (len(remaining_entries) + 1) - self.max_entries
            for key, _ in sorted_entries[:entries_to_remove]:
                to_evict.append(key)

        return to_evict

    def on_access(self, key: str, entry: CacheEntry) -> None:
        """Update access time."""
        entry.touch()

    def on_insert(self, key: str, entry: CacheEntry) -> None:
        """Set TTL if not already set."""
        if entry.ttl is None:
            entry.ttl = self.default_ttl

    def on_remove(self, key: str, entry: CacheEntry) -> None:
        """Nothing to do on remove."""
        pass


class LFUStrategy(CacheStrategy):
    """Least Frequently Used eviction strategy."""

    def __init__(self, max_entries: int = 1000, max_size_bytes: int = 100 * 1024 * 1024):
        self.max_entries = max_entries
        self.max_size_bytes = max_size_bytes

    def should_evict(self, entries: Dict[str, CacheEntry], new_entry_size: int) -> List[str]:
        """Evict least frequently used entries."""
        to_evict = []

        # Calculate current size
        current_size = sum(entry.estimate_size() for entry in entries.values())
        current_count = len(entries)

        # Check if we need to evict
        need_size_eviction = current_size + new_entry_size > self.max_size_bytes
        need_count_eviction = current_count + 1 > self.max_entries

        if need_size_eviction or need_count_eviction:
            # Sort by access count (least frequent first)
            sorted_entries = sorted(
                entries.items(), key=lambda x: (x[1].access_count, x[1].created_at)
            )

            for key, entry in sorted_entries:
                to_evict.append(key)
                current_size -= entry.estimate_size()
                current_count -= 1

                # Check if we've freed enough space/entries
                size_ok = not need_size_eviction or (
                    current_size + new_entry_size <= self.max_size_bytes
                )
                count_ok = not need_count_eviction or (current_count + 1 <= self.max_entries)

                if size_ok and count_ok:
                    break

        return to_evict

    def on_access(self, key: str, entry: CacheEntry) -> None:
        """Update access count."""
        entry.touch()

    def on_insert(self, key: str, entry: CacheEntry) -> None:
        """Nothing to do on insert."""
        pass

    def on_remove(self, key: str, entry: CacheEntry) -> None:
        """Nothing to do on remove."""
        pass


class AdaptiveStrategy(CacheStrategy):
    """Adaptive strategy that switches between LRU and LFU based on access patterns."""

    def __init__(self, max_entries: int = 1000, max_size_bytes: int = 100 * 1024 * 1024):
        self.max_entries = max_entries
        self.max_size_bytes = max_size_bytes
        self.lru_strategy = LRUStrategy(max_entries, max_size_bytes)
        self.lfu_strategy = LFUStrategy(max_entries, max_size_bytes)
        self.current_strategy = self.lru_strategy
        self.access_pattern_window = 100
        self.access_history: List[str] = []
        self.strategy_switch_threshold = 0.3

    def _analyze_access_pattern(self) -> str:
        """Analyze recent access patterns to determine best strategy."""
        if len(self.access_history) < self.access_pattern_window:
            return "lru"  # Default to LRU

        # Calculate access frequency distribution
        recent_accesses = self.access_history[-self.access_pattern_window :]
        access_counts = {}
        for key in recent_accesses:
            access_counts[key] = access_counts.get(key, 0) + 1

        # If access pattern is highly skewed (few keys accessed frequently),
        # LFU might be better. Otherwise, LRU is probably better.
        unique_keys = len(access_counts)
        total_accesses = len(recent_accesses)

        # Calculate entropy-like measure
        if unique_keys <= 1:
            return "lru"

        frequency_variance = (
            sum((count - total_accesses / unique_keys) ** 2 for count in access_counts.values())
            / unique_keys
        )

        normalized_variance = frequency_variance / (total_accesses / unique_keys) ** 2

        return "lfu" if normalized_variance > self.strategy_switch_threshold else "lru"

    def should_evict(self, entries: Dict[str, CacheEntry], new_entry_size: int) -> List[str]:
        """Use current strategy for eviction."""
        return self.current_strategy.should_evict(entries, new_entry_size)

    def on_access(self, key: str, entry: CacheEntry) -> None:
        """Track access and potentially switch strategies."""
        self.access_history.append(key)

        # Keep history bounded
        if len(self.access_history) > self.access_pattern_window * 2:
            self.access_history = self.access_history[-self.access_pattern_window :]

        # Periodically analyze and switch strategies
        if len(self.access_history) % 50 == 0:  # Check every 50 accesses
            best_strategy = self._analyze_access_pattern()
            if best_strategy == "lfu" and isinstance(self.current_strategy, LRUStrategy):
                self.current_strategy = self.lfu_strategy
            elif best_strategy == "lru" and isinstance(self.current_strategy, LFUStrategy):
                self.current_strategy = self.lru_strategy

        # Delegate to current strategy
        self.current_strategy.on_access(key, entry)

    def on_insert(self, key: str, entry: CacheEntry) -> None:
        """Delegate to current strategy."""
        self.current_strategy.on_insert(key, entry)

    def on_remove(self, key: str, entry: CacheEntry) -> None:
        """Delegate to current strategy."""
        self.current_strategy.on_remove(key, entry)
