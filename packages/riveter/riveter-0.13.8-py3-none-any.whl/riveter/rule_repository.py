"""Modern rule repository system for Riveter.

This module provides a modernized rule repository system with dependency injection,
caching, performance optimizations, and comprehensive error handling. It supports
multiple repository types and provides extensible interfaces for future enhancements.
"""

import json
import os
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import urlopen, urlretrieve

from .exceptions import RiveterError
from .logging import debug, error, info, warning
from .models.protocols import CacheProvider
from .models.rules import Rule, RulePack
from .rule_distribution import RulePackageValidator
from .rule_packs import RulePackManager


class RepositoryError(RiveterError):
    """Errors related to rule repository operations."""


class InMemoryCache:
    """Simple in-memory cache implementation for rule repository data."""

    def __init__(self):
        """Initialize empty cache."""
        self._cache: dict[str, Any] = {}
        self._ttl: dict[str, float] = {}

    def get(self, key: str) -> Any | None:
        """Get a cached value."""
        import time

        if key not in self._cache:
            return None

        # Check TTL
        if key in self._ttl and time.time() > self._ttl[key]:
            self.delete(key)
            return None

        return self._cache[key]

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a cached value."""
        import time

        self._cache[key] = value
        if ttl is not None:
            self._ttl[key] = time.time() + ttl
        elif key in self._ttl:
            del self._ttl[key]

    def delete(self, key: str) -> bool:
        """Delete a cached value."""
        deleted = key in self._cache
        self._cache.pop(key, None)
        self._ttl.pop(key, None)
        return deleted

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._ttl.clear()

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        return self.get(key) is not None


@dataclass
class RepositoryConfig:
    """Configuration for a rule repository."""

    name: str
    url: str
    type: str  # "http", "git", "local"
    auth_token: str | None = None
    branch: str | None = None  # For git repositories
    public_key_path: str | None = None  # For signature verification
    enabled: bool = True


@dataclass
class RulePackageInfo:
    """Information about a rule package in a repository."""

    name: str
    version: str
    description: str
    author: str
    download_url: str
    checksum: str
    size_bytes: int
    dependencies: list[str]
    tags: list[str]
    created: str
    updated: str


class ModernRuleRepository(ABC):
    """Modern abstract base class for rule repositories with caching and dependency injection."""

    def __init__(self, config: RepositoryConfig, cache: CacheProvider | None = None):
        """Initialize repository with configuration and optional cache.

        Args:
            config: Repository configuration
            cache: Optional cache provider for performance optimization
        """
        self.config = config
        self.cache = cache or InMemoryCache()
        self._rule_pack_manager = RulePackManager()

    @abstractmethod
    def list_packages(self) -> list[RulePackageInfo]:
        """List all available packages in the repository."""

    @abstractmethod
    def get_package_info(
        self, package_name: str, version: str = "latest"
    ) -> RulePackageInfo | None:
        """Get information about a specific package."""

    @abstractmethod
    def download_package(self, package_name: str, version: str, output_path: str) -> str:
        """Download a package to the specified path."""

    @abstractmethod
    def search_packages(self, query: str, tags: list[str] | None = None) -> list[RulePackageInfo]:
        """Search for packages matching query and tags."""

    # RuleRepository protocol methods
    def load_rules_from_file(self, file_path: Path) -> list[Rule]:
        """Load rules from a file (RuleRepository protocol method)."""
        return self._rule_pack_manager.load_rules_from_file(file_path)

    def load_rule_pack(self, pack_name: str) -> RulePack:
        """Load a rule pack by name (RuleRepository protocol method)."""
        return self._rule_pack_manager.load_rule_pack(pack_name)

    def list_available_packs(self) -> list[str]:
        """List all available rule packs (RuleRepository protocol method)."""
        return self._rule_pack_manager.list_available_packs()

    def validate_rule(self, rule: Rule) -> bool:
        """Validate a rule definition (RuleRepository protocol method)."""
        return self._rule_pack_manager.validate_rule(rule)

    def _get_cache_key(self, operation: str, *args: str) -> str:
        """Generate cache key for operation and arguments."""
        return f"{self.config.name}:{operation}:{':'.join(args)}"

    def _cache_get(self, key: str) -> Any | None:
        """Get value from cache with logging."""
        value = self.cache.get(key)
        if value is not None:
            debug("Cache hit", key=key, repository=self.config.name)
        return value

    def _cache_set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with logging."""
        self.cache.set(key, value, ttl)
        debug("Cache set", key=key, repository=self.config.name, ttl=ttl)


class HTTPRepository(ModernRuleRepository):
    """Modern HTTP/HTTPS rule repository implementation with caching and performance optimizations."""

    def __init__(self, config: RepositoryConfig, cache: CacheProvider | None = None):
        """Initialize HTTP repository with caching support.

        Args:
            config: Repository configuration
            cache: Optional cache provider for performance optimization
        """
        super().__init__(config, cache)
        self._index_cache_ttl = 300  # 5 minutes default TTL for index cache

    def list_packages(self) -> list[RulePackageInfo]:
        """List all available packages in the repository with caching."""
        cache_key = self._get_cache_key("list_packages")
        cached_packages = self._cache_get(cache_key)

        if cached_packages is not None:
            return cached_packages

        try:
            index = self._get_repository_index()
            packages = []

            for package_name, package_data in index.get("packages", {}).items():
                latest_version = package_data.get("latest", "")
                if latest_version and latest_version in package_data.get("versions", {}):
                    version_data = package_data["versions"][latest_version]
                    packages.append(
                        self._create_package_info(package_name, latest_version, version_data)
                    )

            # Cache the results
            self._cache_set(cache_key, packages, self._index_cache_ttl)

            info(
                "Listed packages from HTTP repository",
                repository=self.config.name,
                package_count=len(packages),
            )

            return packages

        except Exception as e:
            error(
                "Failed to list packages from HTTP repository",
                repository=self.config.name,
                error=str(e),
            )
            raise RepositoryError(f"Failed to list packages: {e!s}") from e

    def get_package_info(
        self, package_name: str, version: str = "latest"
    ) -> RulePackageInfo | None:
        """Get information about a specific package with caching."""
        cache_key = self._get_cache_key("package_info", package_name, version)
        cached_info = self._cache_get(cache_key)

        if cached_info is not None:
            return cached_info

        try:
            index = self._get_repository_index()

            if package_name not in index.get("packages", {}):
                debug(
                    "Package not found in repository",
                    repository=self.config.name,
                    package_name=package_name,
                )
                return None

            package_data = index["packages"][package_name]

            if version == "latest":
                version = package_data.get("latest", "")
                if not version:
                    warning(
                        "No latest version found for package",
                        repository=self.config.name,
                        package_name=package_name,
                    )
                    return None

            if version not in package_data.get("versions", {}):
                debug(
                    "Package version not found",
                    repository=self.config.name,
                    package_name=package_name,
                    version=version,
                )
                return None

            version_data = package_data["versions"][version]
            package_info = self._create_package_info(package_name, version, version_data)

            # Cache the result
            self._cache_set(cache_key, package_info, self._index_cache_ttl)

            debug(
                "Retrieved package info from HTTP repository",
                repository=self.config.name,
                package_name=package_name,
                version=version,
            )

            return package_info

        except Exception as e:
            error(
                "Failed to get package info from HTTP repository",
                repository=self.config.name,
                package_name=package_name,
                version=version,
                error=str(e),
            )
            raise RepositoryError(f"Failed to get package info: {e!s}") from e

    def download_package(self, package_name: str, version: str, output_path: str) -> str:
        """Download a package to the specified path."""
        package_info = self.get_package_info(package_name, version)
        if not package_info:
            raise RepositoryError(f"Package {package_name} version {version} not found")

        try:
            # Add authentication if available
            headers = {}
            if self.config.auth_token:
                headers["Authorization"] = f"Bearer {self.config.auth_token}"

            # Download the package
            if headers:
                import urllib.request

                req = urllib.request.Request(package_info.download_url, headers=headers)
                with urlopen(req) as response:
                    with open(output_path, "wb") as f:
                        shutil.copyfileobj(response, f)
            else:
                urlretrieve(package_info.download_url, output_path)

            return output_path

        except Exception as e:
            raise RepositoryError(f"Failed to download package {package_name}: {e!s}") from e

    def search_packages(self, query: str, tags: list[str] | None = None) -> list[RulePackageInfo]:
        """Search for packages matching query and tags."""
        all_packages = self.list_packages()
        results = []

        query_lower = query.lower()

        for package in all_packages:
            # Check if query matches name or description
            if query_lower in package.name.lower() or query_lower in package.description.lower():
                # Check tags if specified
                if tags:
                    if any(tag in package.tags for tag in tags):
                        results.append(package)
                else:
                    results.append(package)

        return results

    def _get_repository_index(self) -> dict[str, Any]:
        """Get repository index with modern caching."""
        cache_key = self._get_cache_key("index")
        cached_index = self._cache_get(cache_key)

        if cached_index is not None:
            return cached_index

        index_url = ""
        try:
            index_url = urllib.parse.urljoin(self.config.url, "index.json")

            debug("Fetching repository index", repository=self.config.name, index_url=index_url)

            # Add authentication if available
            if self.config.auth_token:
                req = urllib.request.Request(
                    index_url, headers={"Authorization": f"Bearer {self.config.auth_token}"}
                )
                with urlopen(req) as response:
                    index_data = json.loads(response.read().decode("utf-8"))
            else:
                with urlopen(index_url) as response:
                    index_data = json.loads(response.read().decode("utf-8"))

            # Cache the index
            self._cache_set(cache_key, index_data, self._index_cache_ttl)

            info(
                "Repository index fetched successfully",
                repository=self.config.name,
                package_count=len(index_data.get("packages", {})),
            )

            return dict(index_data)

        except Exception as e:
            if not index_url:
                index_url = self.config.url + "/index.json"
            error(
                "Failed to fetch repository index",
                repository=self.config.name,
                index_url=index_url,
                error=str(e),
            )
            raise RepositoryError(
                f"Failed to fetch repository index from {index_url}: {e!s}"
            ) from e

    def _create_package_info(
        self, name: str, version: str, version_data: dict[str, Any]
    ) -> RulePackageInfo:
        """Create RulePackageInfo from repository data."""
        manifest = version_data.get("manifest", {})

        return RulePackageInfo(
            name=name,
            version=version,
            description=manifest.get("description", ""),
            author=manifest.get("author", ""),
            download_url=urllib.parse.urljoin(
                self.config.url, version_data.get("download_path", "")
            ),
            checksum=manifest.get("checksum", ""),
            size_bytes=manifest.get("size_bytes", 0),
            dependencies=manifest.get("dependencies", []),
            tags=manifest.get("tags", []),
            created=manifest.get("created", ""),
            updated=manifest.get("updated", ""),
        )


class GitRepository(ModernRuleRepository):
    """Modern Git repository implementation with caching and performance optimizations."""

    def __init__(self, config: RepositoryConfig, cache: CacheProvider | None = None):
        """Initialize Git repository with caching support.

        Args:
            config: Repository configuration
            cache: Optional cache provider for performance optimization
        """
        super().__init__(config, cache)
        self._local_path: Path | None = None
        self._last_update: float | None = None
        self._update_interval = 3600  # 1 hour default update interval

    def list_packages(self) -> list[RulePackageInfo]:
        """List all available packages in the repository."""
        self._ensure_local_copy()
        packages: list[RulePackageInfo] = []

        # Look for package files in the repository
        if self._local_path is None:
            return packages
        for package_file in self._local_path.rglob("*.zip"):
            try:
                package_info = self._extract_package_info(package_file)
                if package_info:
                    packages.append(package_info)
            except Exception:
                continue  # Skip invalid packages

        if self._local_path is not None:
            for package_file in self._local_path.rglob("*.tar.gz"):
                try:
                    package_info = self._extract_package_info(package_file)
                    if package_info:
                        packages.append(package_info)
                except Exception:
                    continue  # Skip invalid packages

        return packages

    def get_package_info(
        self, package_name: str, version: str = "latest"
    ) -> RulePackageInfo | None:
        """Get information about a specific package."""
        packages = self.list_packages()

        # Filter by name
        matching_packages = [p for p in packages if p.name == package_name]

        if not matching_packages:
            return None

        if version == "latest":
            # Return the latest version
            return max(matching_packages, key=lambda p: self._version_key(p.version))
        # Return specific version
        for package in matching_packages:
            if package.version == version:
                return package
        return None

    def download_package(self, package_name: str, version: str, output_path: str) -> str:
        """Download a package to the specified path."""
        package_info = self.get_package_info(package_name, version)
        if not package_info:
            raise RepositoryError(f"Package {package_name} version {version} not found")

        # For git repositories, the download_url is actually a local path
        source_path = package_info.download_url
        if not os.path.exists(source_path):
            raise RepositoryError(f"Package file not found: {source_path}")

        shutil.copy2(source_path, output_path)
        return output_path

    def search_packages(self, query: str, tags: list[str] | None = None) -> list[RulePackageInfo]:
        """Search for packages matching query and tags."""
        all_packages = self.list_packages()
        results = []

        query_lower = query.lower()

        for package in all_packages:
            # Check if query matches name or description
            if query_lower in package.name.lower() or query_lower in package.description.lower():
                # Check tags if specified
                if tags:
                    if any(tag in package.tags for tag in tags):
                        results.append(package)
                else:
                    results.append(package)

        return results

    def _ensure_local_copy(self) -> None:
        """Ensure we have a local copy of the git repository."""
        if self._local_path and self._local_path.exists():
            # Update existing repository
            try:
                subprocess.run(
                    ["git", "pull"],
                    cwd=self._local_path,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError:
                # If pull fails, re-clone
                shutil.rmtree(self._local_path)
                self._local_path = None

        if not self._local_path:
            # Clone repository
            self._local_path = Path(tempfile.mkdtemp(prefix="riveter_git_repo_"))

            clone_cmd = ["git", "clone"]
            if self.config.branch:
                clone_cmd.extend(["-b", self.config.branch])

            clone_cmd.extend([self.config.url, str(self._local_path)])

            try:
                subprocess.run(clone_cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                raise RepositoryError(f"Failed to clone git repository: {e.stderr}") from e

    def _extract_package_info(self, package_path: Path) -> RulePackageInfo | None:
        """Extract package information from a package file."""
        try:
            validator = RulePackageValidator()
            result = validator.validate_package(str(package_path), verify_signature=False)

            if not result["valid"] or not result["manifest"]:
                return None

            manifest = result["manifest"]

            return RulePackageInfo(
                name=manifest["name"],
                version=manifest["version"],
                description=manifest["description"],
                author=manifest["author"],
                download_url=str(package_path),  # Local path for git repos
                checksum=manifest["checksum"],
                size_bytes=manifest["size_bytes"],
                dependencies=manifest["dependencies"],
                tags=manifest["tags"],
                created=manifest["created"],
                updated=manifest["updated"],
            )

        except Exception:
            return None

    def _version_key(self, version: str) -> tuple[int, ...]:
        """Convert version string to tuple for comparison."""
        try:
            return tuple(map(int, version.split(".")))
        except ValueError:
            return (0, 0, 0)


class LocalRepository(ModernRuleRepository):
    """Modern local directory repository implementation with caching."""

    def list_packages(self) -> list[RulePackageInfo]:
        """List all available packages in the local directory."""
        repo_path = Path(self.config.url)
        if not repo_path.exists():
            return []

        packages = []

        for package_file in repo_path.rglob("*.zip"):
            try:
                package_info = self._extract_package_info(package_file)
                if package_info:
                    packages.append(package_info)
            except Exception:
                continue

        for package_file in repo_path.rglob("*.tar.gz"):
            try:
                package_info = self._extract_package_info(package_file)
                if package_info:
                    packages.append(package_info)
            except Exception:
                continue

        return packages

    def get_package_info(
        self, package_name: str, version: str = "latest"
    ) -> RulePackageInfo | None:
        """Get information about a specific package."""
        packages = self.list_packages()

        matching_packages = [p for p in packages if p.name == package_name]

        if not matching_packages:
            return None

        if version == "latest":
            return max(matching_packages, key=lambda p: self._version_key(p.version))
        for package in matching_packages:
            if package.version == version:
                return package
        return None

    def download_package(self, package_name: str, version: str, output_path: str) -> str:
        """Download (copy) a package to the specified path."""
        package_info = self.get_package_info(package_name, version)
        if not package_info:
            raise RepositoryError(f"Package {package_name} version {version} not found")

        source_path = package_info.download_url
        shutil.copy2(source_path, output_path)
        return output_path

    def search_packages(self, query: str, tags: list[str] | None = None) -> list[RulePackageInfo]:
        """Search for packages matching query and tags."""
        all_packages = self.list_packages()
        results = []

        query_lower = query.lower()

        for package in all_packages:
            if query_lower in package.name.lower() or query_lower in package.description.lower():
                if tags:
                    if any(tag in package.tags for tag in tags):
                        results.append(package)
                else:
                    results.append(package)

        return results

    def _extract_package_info(self, package_path: Path) -> RulePackageInfo | None:
        """Extract package information from a package file."""
        try:
            validator = RulePackageValidator()
            result = validator.validate_package(str(package_path), verify_signature=False)

            if not result["valid"] or not result["manifest"]:
                return None

            manifest = result["manifest"]

            return RulePackageInfo(
                name=manifest["name"],
                version=manifest["version"],
                description=manifest["description"],
                author=manifest["author"],
                download_url=str(package_path),
                checksum=manifest["checksum"],
                size_bytes=manifest["size_bytes"],
                dependencies=manifest["dependencies"],
                tags=manifest["tags"],
                created=manifest["created"],
                updated=manifest["updated"],
            )

        except Exception:
            return None

    def _version_key(self, version: str) -> tuple[int, ...]:
        """Convert version string to tuple for comparison."""
        try:
            return tuple(map(int, version.split(".")))
        except ValueError:
            return (0, 0, 0)


class RepositoryManager:
    """Modern manager for multiple rule repositories with dependency injection and caching."""

    def __init__(self, config_path: str | None = None, cache: CacheProvider | None = None):
        """Initialize repository manager with configuration and caching.

        Args:
            config_path: Optional path to repository configuration file
            cache: Optional cache provider for performance optimization
        """
        self.repositories: dict[str, ModernRuleRepository] = {}
        self.config_path = config_path or os.path.expanduser("~/.riveter/repositories.json")
        self.cache = cache or InMemoryCache()
        self._load_configuration()

        info(
            "Repository manager initialized",
            config_path=self.config_path,
            repository_count=len(self.repositories),
        )

    def _load_configuration(self) -> None:
        """Load repository configuration from file."""
        if not os.path.exists(self.config_path):
            # Create default configuration
            self._create_default_config()
            return

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config_data = json.load(f)

            for repo_config_data in config_data.get("repositories", []):
                config = RepositoryConfig(**repo_config_data)
                if config.enabled:
                    self.add_repository(config)

        except Exception as e:
            raise RepositoryError(f"Failed to load repository configuration: {e!s}") from e

    def _create_default_config(self) -> None:
        """Create default repository configuration."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        default_config = {
            "repositories": [
                {
                    "name": "official",
                    "url": "https://rules.riveter.dev",
                    "type": "http",
                    "enabled": True,
                }
            ]
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

    def add_repository(self, config: RepositoryConfig) -> None:
        """Add a repository to the manager with dependency injection.

        Args:
            config: Repository configuration

        Raises:
            RepositoryError: If repository type is not supported
        """
        repository: ModernRuleRepository
        if config.type == "http":
            repository = HTTPRepository(config, self.cache)
        elif config.type == "git":
            repository = GitRepository(config, self.cache)
        elif config.type == "local":
            repository = LocalRepository(config, self.cache)
        else:
            raise RepositoryError(f"Unsupported repository type: {config.type}")

        self.repositories[config.name] = repository

        info("Repository added", name=config.name, type=config.type, url=config.url)

    def remove_repository(self, name: str) -> bool:
        """Remove a repository from the manager."""
        if name in self.repositories:
            del self.repositories[name]
            return True
        return False

    def list_repositories(self) -> list[RepositoryConfig]:
        """List all configured repositories."""
        return [repo.config for repo in self.repositories.values()]

    def clear_cache(self) -> None:
        """Clear all repository caches for fresh data."""
        self.cache.clear()
        info("Repository manager cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for monitoring."""
        # This is a simple implementation - a real cache might have more stats
        return {
            "cache_type": type(self.cache).__name__,
            "repositories": len(self.repositories),
            "enabled_repositories": len(
                [r for r in self.repositories.values() if r.config.enabled]
            ),
        }

    def refresh_repositories(self) -> None:
        """Refresh all repository data by clearing caches."""
        self.clear_cache()
        info("All repositories refreshed")

    def search_packages(
        self, query: str, tags: list[str] | None = None, repository: str | None = None
    ) -> list[RulePackageInfo]:
        """Search for packages across repositories."""
        results = []

        if repository:
            if repository in self.repositories:
                results.extend(self.repositories[repository].search_packages(query, tags))
        else:
            for repo in self.repositories.values():
                try:
                    results.extend(repo.search_packages(query, tags))
                except Exception:
                    continue  # Skip repositories that fail

        # Remove duplicates based on name and version
        seen = set()
        unique_results = []
        for package in results:
            key = (package.name, package.version)
            if key not in seen:
                seen.add(key)
                unique_results.append(package)

        return unique_results

    def get_package_info(
        self, package_name: str, version: str = "latest", repository: str | None = None
    ) -> RulePackageInfo | None:
        """Get package information from repositories."""
        if repository:
            if repository in self.repositories:
                return self.repositories[repository].get_package_info(package_name, version)
            return None

        # Search all repositories
        for repo in self.repositories.values():
            try:
                package_info = repo.get_package_info(package_name, version)
                if package_info:
                    return package_info
            except Exception:
                continue

        return None

    def download_package(
        self, package_name: str, version: str, output_path: str, repository: str | None = None
    ) -> str:
        """Download package from repositories."""
        if repository:
            if repository not in self.repositories:
                raise RepositoryError(f"Repository '{repository}' not found")
            return self.repositories[repository].download_package(
                package_name, version, output_path
            )

        # Try all repositories
        last_error = None
        for repo in self.repositories.values():
            try:
                return repo.download_package(package_name, version, output_path)
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise RepositoryError(f"Failed to download package from any repository: {last_error!s}")
        raise RepositoryError(
            f"Package {package_name} version {version} not found in any repository"
        )

    def resolve_dependencies(
        self, package_name: str, version: str = "latest"
    ) -> list[RulePackageInfo]:
        """Resolve package dependencies recursively."""
        resolved = []
        to_resolve = [(package_name, version)]
        seen = set()

        while to_resolve:
            current_name, current_version = to_resolve.pop(0)

            if (current_name, current_version) in seen:
                continue

            seen.add((current_name, current_version))

            package_info = self.get_package_info(current_name, current_version)
            if not package_info:
                raise RepositoryError(f"Package {current_name} version {current_version} not found")

            resolved.append(package_info)

            # Add dependencies to resolution queue
            for dep in package_info.dependencies:
                # Parse dependency (assume format "name>=version" or just "name")
                if ">=" in dep:
                    dep_name, dep_version = dep.split(">=", 1)
                elif "==" in dep:
                    dep_name, dep_version = dep.split("==", 1)
                else:
                    dep_name, dep_version = dep, "latest"

                to_resolve.append((dep_name.strip(), dep_version.strip()))

        return resolved
