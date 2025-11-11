"""Cache provider implementations for different storage backends."""

import json
import pickle
import sqlite3
import time
from pathlib import Path
from threading import Lock, RLock
from typing import Any, Dict, List, Optional

from ..exceptions import CacheError
from ..logging import debug, error, warning
from ..models.protocols import CacheProvider
from .strategies import CacheStrategy, LRUStrategy
from .types import CacheEntry, CacheKey, CacheKeyType, CacheStats


class MemoryCacheProvider(CacheProvider):
    """In-memory cache provider with configurable eviction strategies."""

    def __init__(self, strategy: Optional[CacheStrategy] = None, enable_stats: bool = True):
        self.strategy = strategy or LRUStrategy()
        self.entries: Dict[str, CacheEntry] = {}
        self.stats = CacheStats() if enable_stats else None
        self._lock = RLock()

    def get(self, key: str) -> Any | None:
        """Get a cached value."""
        start_time = time.time()

        with self._lock:
            if key not in self.entries:
                if self.stats:
                    self.stats.record_miss(time.time() - start_time)
                return None

            entry = self.entries[key]

            # Check if expired
            if entry.is_expired:
                del self.entries[key]
                self.strategy.on_remove(key, entry)
                if self.stats:
                    self.stats.record_miss(time.time() - start_time)
                    self.stats.entries = len(self.entries)
                return None

            # Update access tracking
            self.strategy.on_access(key, entry)

            if self.stats:
                self.stats.record_hit(time.time() - start_time)

            return entry.value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a cached value."""
        with self._lock:
            # Create cache entry
            cache_key = CacheKey(key_type=CacheKeyType.PLUGIN_DATA, identifier=key)  # Default type

            entry = CacheEntry(key=cache_key, value=value, ttl=float(ttl) if ttl else None)

            # Check if we need to evict entries
            entry_size = entry.estimate_size()
            keys_to_evict = self.strategy.should_evict(self.entries, entry_size)

            # Evict entries
            for evict_key in keys_to_evict:
                if evict_key in self.entries:
                    evicted_entry = self.entries[evict_key]
                    del self.entries[evict_key]
                    self.strategy.on_remove(evict_key, evicted_entry)
                    if self.stats:
                        self.stats.record_eviction()

            # Add new entry
            self.entries[key] = entry
            self.strategy.on_insert(key, entry)

            # Update stats
            if self.stats:
                self.stats.entries = len(self.entries)
                self.stats.total_size_bytes = sum(e.estimate_size() for e in self.entries.values())

    def delete(self, key: str) -> bool:
        """Delete a cached value."""
        with self._lock:
            if key in self.entries:
                entry = self.entries[key]
                del self.entries[key]
                self.strategy.on_remove(key, entry)

                if self.stats:
                    self.stats.entries = len(self.entries)
                    self.stats.total_size_bytes = sum(
                        e.estimate_size() for e in self.entries.values()
                    )

                return True
            return False

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            for key, entry in self.entries.items():
                self.strategy.on_remove(key, entry)

            self.entries.clear()

            if self.stats:
                self.stats.entries = 0
                self.stats.total_size_bytes = 0

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        with self._lock:
            if key not in self.entries:
                return False

            entry = self.entries[key]
            if entry.is_expired:
                del self.entries[key]
                self.strategy.on_remove(key, entry)
                return False

            return True

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        removed_count = 0

        with self._lock:
            expired_keys = [key for key, entry in self.entries.items() if entry.is_expired]

            for key in expired_keys:
                entry = self.entries[key]
                del self.entries[key]
                self.strategy.on_remove(key, entry)
                removed_count += 1

            if self.stats and removed_count > 0:
                self.stats.entries = len(self.entries)
                self.stats.total_size_bytes = sum(e.estimate_size() for e in self.entries.values())

        return removed_count

    def get_stats(self) -> Optional[CacheStats]:
        """Get cache statistics."""
        return self.stats


class DiskCacheProvider(CacheProvider):
    """Disk-based cache provider using SQLite for metadata and files for data."""

    def __init__(
        self,
        cache_dir: Path,
        max_size_bytes: int = 1024 * 1024 * 1024,  # 1GB
        compression: bool = True,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_bytes
        self.compression = compression
        self.stats = CacheStats()
        self._lock = Lock()

        # Initialize SQLite database for metadata
        self.db_path = self.cache_dir / "cache.db"
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    accessed_at REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    ttl REAL,
                    size_bytes INTEGER NOT NULL
                )
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_accessed_at ON cache_entries(accessed_at)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_created_at ON cache_entries(created_at)
            """
            )

    def _get_file_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        import hashlib

        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / "data" / f"{key_hash[:2]}" / f"{key_hash}.cache"

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize a value for storage."""
        data = pickle.dumps(value)

        if self.compression:
            import gzip

            data = gzip.compress(data)

        return data

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize a value from storage."""
        if self.compression:
            import gzip

            data = gzip.decompress(data)

        return pickle.loads(data)

    def get(self, key: str) -> Any | None:
        """Get a cached value."""
        start_time = time.time()

        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT file_path, created_at, ttl FROM cache_entries WHERE key = ?", (key,)
                    )
                    row = cursor.fetchone()

                    if not row:
                        self.stats.record_miss(time.time() - start_time)
                        return None

                    file_path, created_at, ttl = row

                    # Check if expired
                    if ttl and (time.time() - created_at) > ttl:
                        self.delete(key)
                        self.stats.record_miss(time.time() - start_time)
                        return None

                    # Read data from file
                    file_path = Path(file_path)
                    if not file_path.exists():
                        # File missing, remove from database
                        conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                        self.stats.record_miss(time.time() - start_time)
                        return None

                    with open(file_path, "rb") as f:
                        data = f.read()

                    value = self._deserialize_value(data)

                    # Update access tracking
                    conn.execute(
                        "UPDATE cache_entries SET accessed_at = ?, access_count = access_count + 1 WHERE key = ?",
                        (time.time(), key),
                    )

                    self.stats.record_hit(time.time() - start_time)
                    return value

            except Exception as e:
                error(f"Error reading from disk cache: {e}")
                self.stats.record_miss(time.time() - start_time)
                return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a cached value."""
        with self._lock:
            try:
                # Serialize value
                data = self._serialize_value(value)
                data_size = len(data)

                # Check if we need to make space
                self._ensure_space(data_size)

                # Write data to file
                file_path = self._get_file_path(key)
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "wb") as f:
                    f.write(data)

                # Update database
                current_time = time.time()
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """INSERT OR REPLACE INTO cache_entries
                           (key, file_path, created_at, accessed_at, ttl, size_bytes)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            key,
                            str(file_path),
                            current_time,
                            current_time,
                            float(ttl) if ttl else None,
                            data_size,
                        ),
                    )

                debug(f"Cached {key} to disk ({data_size} bytes)")

            except Exception as e:
                error(f"Error writing to disk cache: {e}")
                raise CacheError(f"Failed to write cache entry: {e}")

    def delete(self, key: str) -> bool:
        """Delete a cached value."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT file_path FROM cache_entries WHERE key = ?", (key,)
                    )
                    row = cursor.fetchone()

                    if not row:
                        return False

                    file_path = Path(row[0])

                    # Remove file
                    if file_path.exists():
                        file_path.unlink()

                    # Remove from database
                    conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))

                    return True

            except Exception as e:
                error(f"Error deleting from disk cache: {e}")
                return False

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            try:
                # Remove all data files
                data_dir = self.cache_dir / "data"
                if data_dir.exists():
                    import shutil

                    shutil.rmtree(data_dir)

                # Clear database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM cache_entries")

            except Exception as e:
                error(f"Error clearing disk cache: {e}")

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT created_at, ttl FROM cache_entries WHERE key = ?", (key,)
                    )
                    row = cursor.fetchone()

                    if not row:
                        return False

                    created_at, ttl = row

                    # Check if expired
                    if ttl and (time.time() - created_at) > ttl:
                        self.delete(key)
                        return False

                    return True

            except Exception as e:
                error(f"Error checking disk cache existence: {e}")
                return False

    def _ensure_space(self, needed_bytes: int) -> None:
        """Ensure there's enough space for a new entry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get current total size
                cursor = conn.execute("SELECT SUM(size_bytes) FROM cache_entries")
                current_size = cursor.fetchone()[0] or 0

                if current_size + needed_bytes <= self.max_size_bytes:
                    return

                # Need to evict entries - use LRU strategy
                bytes_to_free = (current_size + needed_bytes) - self.max_size_bytes
                bytes_freed = 0

                cursor = conn.execute(
                    "SELECT key, file_path, size_bytes FROM cache_entries ORDER BY accessed_at ASC"
                )

                for key, file_path, size_bytes in cursor:
                    self.delete(key)
                    bytes_freed += size_bytes
                    self.stats.record_eviction()

                    if bytes_freed >= bytes_to_free:
                        break

        except Exception as e:
            warning(f"Error ensuring disk cache space: {e}")

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        removed_count = 0

        with self._lock:
            try:
                current_time = time.time()

                with sqlite3.connect(self.db_path) as conn:
                    # Find expired entries
                    cursor = conn.execute(
                        "SELECT key FROM cache_entries WHERE ttl IS NOT NULL AND (? - created_at) > ttl",
                        (current_time,),
                    )

                    expired_keys = [row[0] for row in cursor]

                    for key in expired_keys:
                        if self.delete(key):
                            removed_count += 1

            except Exception as e:
                error(f"Error cleaning up expired disk cache entries: {e}")

        return removed_count


class MultiLevelCacheProvider(CacheProvider):
    """Multi-level cache provider that combines memory and disk caching."""

    def __init__(
        self,
        memory_provider: MemoryCacheProvider,
        disk_provider: DiskCacheProvider,
        promote_threshold: int = 2,  # Promote to memory after N accesses
    ):
        self.memory_provider = memory_provider
        self.disk_provider = disk_provider
        self.promote_threshold = promote_threshold
        self.stats = CacheStats()
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        """Get a cached value, checking memory first, then disk."""
        start_time = time.time()

        # Try memory cache first
        value = self.memory_provider.get(key)
        if value is not None:
            self.stats.record_hit(time.time() - start_time)
            return value

        # Try disk cache
        value = self.disk_provider.get(key)
        if value is not None:
            # Check if we should promote to memory
            with self._lock:
                try:
                    with sqlite3.connect(self.disk_provider.db_path) as conn:
                        cursor = conn.execute(
                            "SELECT access_count FROM cache_entries WHERE key = ?", (key,)
                        )
                        row = cursor.fetchone()

                        if row and row[0] >= self.promote_threshold:
                            # Promote to memory cache
                            self.memory_provider.set(key, value)
                            debug(f"Promoted {key} to memory cache")

                except Exception as e:
                    warning(f"Error checking promotion criteria: {e}")

            self.stats.record_hit(time.time() - start_time)
            return value

        self.stats.record_miss(time.time() - start_time)
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a cached value in both memory and disk."""
        # Always set in disk cache for persistence
        self.disk_provider.set(key, value, ttl)

        # Also set in memory cache if it fits
        try:
            self.memory_provider.set(key, value, ttl)
        except Exception as e:
            # Memory cache might be full, that's okay
            debug(f"Could not set {key} in memory cache: {e}")

    def delete(self, key: str) -> bool:
        """Delete a cached value from both levels."""
        memory_deleted = self.memory_provider.delete(key)
        disk_deleted = self.disk_provider.delete(key)
        return memory_deleted or disk_deleted

    def clear(self) -> None:
        """Clear all cached values from both levels."""
        self.memory_provider.clear()
        self.disk_provider.clear()

    def exists(self, key: str) -> bool:
        """Check if a key exists in either cache level."""
        return self.memory_provider.exists(key) or self.disk_provider.exists(key)

    def cleanup_expired(self) -> int:
        """Remove expired entries from both levels."""
        memory_removed = self.memory_provider.cleanup_expired()
        disk_removed = self.disk_provider.cleanup_expired()
        return memory_removed + disk_removed

    def get_stats(self) -> CacheStats:
        """Get combined cache statistics."""
        memory_stats = self.memory_provider.get_stats()

        if memory_stats:
            # Combine with our stats
            combined_stats = CacheStats(
                hits=self.stats.hits + memory_stats.hits,
                misses=self.stats.misses + memory_stats.misses,
                evictions=self.stats.evictions + memory_stats.evictions,
                entries=memory_stats.entries,  # Memory entries count
                total_size_bytes=memory_stats.total_size_bytes,
                average_access_time=(
                    self.stats.average_access_time + memory_stats.average_access_time
                )
                / 2,
            )
            return combined_stats

        return self.stats
