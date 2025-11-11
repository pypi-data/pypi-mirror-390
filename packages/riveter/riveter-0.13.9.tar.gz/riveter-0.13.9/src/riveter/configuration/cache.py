"""Configuration caching system for improved performance.

This module provides intelligent caching for parsed Terraform configurations
to avoid re-parsing unchanged files and improve overall performance.
"""

import hashlib
import pickle
import time
from pathlib import Path
from typing import Any, Protocol

from ..logging import debug, info, warning
from ..models.config import TerraformConfig


class CacheBackend(Protocol):
    """Protocol for cache backends."""

    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""
        ...

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in the cache with optional TTL."""
        ...

    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        ...

    def clear(self) -> None:
        """Clear all cached values."""
        ...

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        ...


class FileCacheBackend:
    """File-based cache backend for configuration caching."""

    def __init__(self, cache_dir: Path, default_ttl: int = 3600) -> None:
        """Initialize file cache backend.

        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        debug("Initialized file cache backend", cache_dir=str(cache_dir), default_ttl=default_ttl)

    def get(self, key: str) -> Any | None:
        """Get a value from the file cache."""
        cache_file = self._get_cache_file(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)

            # Check if cache entry has expired
            if cache_data["expires_at"] < time.time():
                debug("Cache entry expired", key=key)
                self.delete(key)
                return None

            debug("Cache hit", key=key)
            return cache_data["value"]

        except (pickle.PickleError, KeyError, OSError) as e:
            warning("Failed to read cache entry", key=key, error=str(e))
            # Clean up corrupted cache file
            try:
                cache_file.unlink()
            except OSError:
                pass
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in the file cache."""
        cache_file = self._get_cache_file(key)
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl

        cache_data = {
            "value": value,
            "created_at": time.time(),
            "expires_at": expires_at,
            "ttl": ttl,
        }

        try:
            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)

            debug("Cache entry stored", key=key, ttl=ttl)

        except (pickle.PickleError, OSError) as e:
            warning("Failed to store cache entry", key=key, error=str(e))

    def delete(self, key: str) -> None:
        """Delete a value from the file cache."""
        cache_file = self._get_cache_file(key)

        try:
            cache_file.unlink()
            debug("Cache entry deleted", key=key)
        except OSError:
            pass  # File doesn't exist or can't be deleted

    def clear(self) -> None:
        """Clear all cached values."""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            info("Cache cleared", cache_dir=str(self.cache_dir))
        except OSError as e:
            warning("Failed to clear cache", error=str(e))

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        cache_file = self._get_cache_file(key)
        return cache_file.exists()

    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a key."""
        # Use hash of key as filename to avoid filesystem issues
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def cleanup_expired(self) -> int:
        """Clean up expired cache entries and return count of removed entries."""
        removed_count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, "rb") as f:
                    cache_data = pickle.load(f)

                if cache_data["expires_at"] < current_time:
                    cache_file.unlink()
                    removed_count += 1

            except (pickle.PickleError, KeyError, OSError):
                # Remove corrupted cache files
                try:
                    cache_file.unlink()
                    removed_count += 1
                except OSError:
                    pass

        if removed_count > 0:
            info("Cleaned up expired cache entries", removed_count=removed_count)

        return removed_count


class ConfigurationCache:
    """High-level configuration caching system."""

    def __init__(
        self,
        backend: CacheBackend | None = None,
        cache_dir: Path | None = None,
        default_ttl: int = 3600,
        enabled: bool = True,
    ) -> None:
        """Initialize configuration cache.

        Args:
            backend: Cache backend to use. If None, FileCacheBackend will be used.
            cache_dir: Directory for file cache. Only used if backend is None.
            default_ttl: Default time-to-live for cache entries in seconds
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.default_ttl = default_ttl

        if not enabled:
            debug("Configuration caching disabled")
            return

        if backend is None:
            if cache_dir is None:
                cache_dir = Path.home() / ".riveter" / "cache" / "config"
            self.backend = FileCacheBackend(cache_dir, default_ttl)
        else:
            self.backend = backend

        info("Configuration cache initialized", enabled=enabled, default_ttl=default_ttl)

    def get_config(self, file_path: Path) -> TerraformConfig | None:
        """Get cached configuration for a file.

        Args:
            file_path: Path to the Terraform configuration file

        Returns:
            Cached TerraformConfig if available and valid, None otherwise
        """
        if not self.enabled:
            return None

        cache_key = self._get_cache_key(file_path)

        try:
            cached_data = self.backend.get(cache_key)
            if cached_data is None:
                return None

            # Verify file hasn't changed since caching
            if not self._is_cache_valid(
                file_path, cached_data["file_hash"], cached_data["file_mtime"]
            ):
                debug("Cache invalid due to file changes", file_path=str(file_path))
                self.backend.delete(cache_key)
                return None

            debug("Configuration cache hit", file_path=str(file_path))
            return cached_data["config"]

        except Exception as e:
            warning("Error retrieving cached configuration", file_path=str(file_path), error=str(e))
            return None

    def set_config(self, file_path: Path, config: TerraformConfig, ttl: int | None = None) -> None:
        """Cache a configuration for a file.

        Args:
            file_path: Path to the Terraform configuration file
            config: Parsed configuration to cache
            ttl: Time-to-live for this cache entry
        """
        if not self.enabled:
            return

        cache_key = self._get_cache_key(file_path)
        ttl = ttl or self.default_ttl

        try:
            file_stat = file_path.stat()
            file_hash = self._calculate_file_hash(file_path)

            cache_data = {
                "config": config,
                "file_hash": file_hash,
                "file_mtime": file_stat.st_mtime,
                "file_size": file_stat.st_size,
            }

            self.backend.set(cache_key, cache_data, ttl)
            debug("Configuration cached", file_path=str(file_path), ttl=ttl)

        except Exception as e:
            warning("Error caching configuration", file_path=str(file_path), error=str(e))

    def invalidate_config(self, file_path: Path) -> None:
        """Invalidate cached configuration for a file.

        Args:
            file_path: Path to the Terraform configuration file
        """
        if not self.enabled:
            return

        cache_key = self._get_cache_key(file_path)
        self.backend.delete(cache_key)
        debug("Configuration cache invalidated", file_path=str(file_path))

    def clear_all(self) -> None:
        """Clear all cached configurations."""
        if not self.enabled:
            return

        self.backend.clear()
        info("All configuration cache cleared")

    def cleanup_expired(self) -> int:
        """Clean up expired cache entries.

        Returns:
            Number of expired entries removed
        """
        if not self.enabled or not hasattr(self.backend, "cleanup_expired"):
            return 0

        return self.backend.cleanup_expired()

    def _get_cache_key(self, file_path: Path) -> str:
        """Generate cache key for a file path."""
        # Use absolute path to ensure consistent keys
        abs_path = file_path.resolve()
        return f"terraform_config:{abs_path}"

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file content for change detection."""
        hasher = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except OSError:
            # If we can't read the file, return a timestamp-based hash
            return hashlib.sha256(str(time.time()).encode()).hexdigest()

    def _is_cache_valid(self, file_path: Path, cached_hash: str, cached_mtime: float) -> bool:
        """Check if cached data is still valid for a file."""
        try:
            file_stat = file_path.stat()

            # Quick check: if modification time hasn't changed, assume file is unchanged
            if abs(file_stat.st_mtime - cached_mtime) < 1.0:  # 1 second tolerance
                return True

            # If mtime changed, check file hash
            current_hash = self._calculate_file_hash(file_path)
            return current_hash == cached_hash

        except OSError:
            # If we can't stat the file, consider cache invalid
            return False

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not self.enabled:
            return {"enabled": False}

        stats = {
            "enabled": True,
            "default_ttl": self.default_ttl,
            "backend_type": type(self.backend).__name__,
        }

        # Add backend-specific stats if available
        if hasattr(self.backend, "cache_dir"):
            cache_dir = self.backend.cache_dir
            try:
                cache_files = list(cache_dir.glob("*.cache"))
                total_size = sum(f.stat().st_size for f in cache_files)
                stats.update(
                    {
                        "cache_dir": str(cache_dir),
                        "entry_count": len(cache_files),
                        "total_size_bytes": total_size,
                    }
                )
            except OSError:
                pass

        return stats
