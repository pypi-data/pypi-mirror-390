"""Remote rule repository support for Riveter."""

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
from typing import Any, Dict, List, Optional
from urllib.request import urlopen, urlretrieve

from .exceptions import RiveterError
from .rule_distribution import RulePackageValidator


class RepositoryError(RiveterError):
    """Errors related to rule repository operations."""


@dataclass
class RepositoryConfig:
    """Configuration for a rule repository."""

    name: str
    url: str
    type: str  # "http", "git", "local"
    auth_token: Optional[str] = None
    branch: Optional[str] = None  # For git repositories
    public_key_path: Optional[str] = None  # For signature verification
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
    dependencies: List[str]
    tags: List[str]
    created: str
    updated: str


class RuleRepository(ABC):
    """Abstract base class for rule repositories."""

    def __init__(self, config: RepositoryConfig):
        """Initialize repository with configuration."""
        self.config = config

    @abstractmethod
    def list_packages(self) -> List[RulePackageInfo]:
        """List all available packages in the repository."""
        pass

    @abstractmethod
    def get_package_info(
        self, package_name: str, version: str = "latest"
    ) -> Optional[RulePackageInfo]:
        """Get information about a specific package."""
        pass

    @abstractmethod
    def download_package(self, package_name: str, version: str, output_path: str) -> str:
        """Download a package to the specified path."""
        pass

    @abstractmethod
    def search_packages(
        self, query: str, tags: Optional[List[str]] = None
    ) -> List[RulePackageInfo]:
        """Search for packages matching query and tags."""
        pass


class HTTPRepository(RuleRepository):
    """HTTP/HTTPS rule repository implementation."""

    def __init__(self, config: RepositoryConfig):
        """Initialize HTTP repository."""
        super().__init__(config)
        self._index_cache: Optional[Dict[str, Any]] = None
        self._cache_valid = False

    def list_packages(self) -> List[RulePackageInfo]:
        """List all available packages in the repository."""
        index = self._get_repository_index()
        packages = []

        for package_name, package_data in index.get("packages", {}).items():
            latest_version = package_data.get("latest", "")
            if latest_version and latest_version in package_data.get("versions", {}):
                version_data = package_data["versions"][latest_version]
                packages.append(
                    self._create_package_info(package_name, latest_version, version_data)
                )

        return packages

    def get_package_info(
        self, package_name: str, version: str = "latest"
    ) -> Optional[RulePackageInfo]:
        """Get information about a specific package."""
        index = self._get_repository_index()

        if package_name not in index.get("packages", {}):
            return None

        package_data = index["packages"][package_name]

        if version == "latest":
            version = package_data.get("latest", "")
            if not version:
                return None

        if version not in package_data.get("versions", {}):
            return None

        version_data = package_data["versions"][version]
        return self._create_package_info(package_name, version, version_data)

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
            raise RepositoryError(f"Failed to download package {package_name}: {str(e)}") from e

    def search_packages(
        self, query: str, tags: Optional[List[str]] = None
    ) -> List[RulePackageInfo]:
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

    def _get_repository_index(self) -> Dict[str, Any]:
        """Get repository index, using cache if valid."""
        if self._cache_valid and self._index_cache:
            return self._index_cache

        index_url = ""
        try:
            index_url = urllib.parse.urljoin(self.config.url, "index.json")

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

            self._index_cache = index_data
            self._cache_valid = True
            return dict(index_data)

        except Exception as e:
            if not index_url:
                index_url = self.config.url + "/index.json"
            raise RepositoryError(
                f"Failed to fetch repository index from {index_url}: {str(e)}"
            ) from e

    def _create_package_info(
        self, name: str, version: str, version_data: Dict[str, Any]
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


class GitRepository(RuleRepository):
    """Git repository implementation for rule packages."""

    def __init__(self, config: RepositoryConfig):
        """Initialize Git repository."""
        super().__init__(config)
        self._local_path: Optional[Path] = None

    def list_packages(self) -> List[RulePackageInfo]:
        """List all available packages in the repository."""
        self._ensure_local_copy()
        packages: List[RulePackageInfo] = []

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
    ) -> Optional[RulePackageInfo]:
        """Get information about a specific package."""
        packages = self.list_packages()

        # Filter by name
        matching_packages = [p for p in packages if p.name == package_name]

        if not matching_packages:
            return None

        if version == "latest":
            # Return the latest version
            return max(matching_packages, key=lambda p: self._version_key(p.version))
        else:
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

    def search_packages(
        self, query: str, tags: Optional[List[str]] = None
    ) -> List[RulePackageInfo]:
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

    def _extract_package_info(self, package_path: Path) -> Optional[RulePackageInfo]:
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


class LocalRepository(RuleRepository):
    """Local directory repository implementation."""

    def list_packages(self) -> List[RulePackageInfo]:
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
    ) -> Optional[RulePackageInfo]:
        """Get information about a specific package."""
        packages = self.list_packages()

        matching_packages = [p for p in packages if p.name == package_name]

        if not matching_packages:
            return None

        if version == "latest":
            return max(matching_packages, key=lambda p: self._version_key(p.version))
        else:
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

    def search_packages(
        self, query: str, tags: Optional[List[str]] = None
    ) -> List[RulePackageInfo]:
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

    def _extract_package_info(self, package_path: Path) -> Optional[RulePackageInfo]:
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
    """Manager for multiple rule repositories with dependency resolution."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize repository manager with configuration."""
        self.repositories: Dict[str, RuleRepository] = {}
        self.config_path = config_path or os.path.expanduser("~/.riveter/repositories.json")
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load repository configuration from file."""
        if not os.path.exists(self.config_path):
            # Create default configuration
            self._create_default_config()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            for repo_config_data in config_data.get("repositories", []):
                config = RepositoryConfig(**repo_config_data)
                if config.enabled:
                    self.add_repository(config)

        except Exception as e:
            raise RepositoryError(f"Failed to load repository configuration: {str(e)}") from e

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
        """Add a repository to the manager."""
        repository: RuleRepository
        if config.type == "http":
            repository = HTTPRepository(config)
        elif config.type == "git":
            repository = GitRepository(config)
        elif config.type == "local":
            repository = LocalRepository(config)
        else:
            raise RepositoryError(f"Unsupported repository type: {config.type}")

        self.repositories[config.name] = repository

    def remove_repository(self, name: str) -> bool:
        """Remove a repository from the manager."""
        if name in self.repositories:
            del self.repositories[name]
            return True
        return False

    def list_repositories(self) -> List[RepositoryConfig]:
        """List all configured repositories."""
        return [repo.config for repo in self.repositories.values()]

    def search_packages(
        self, query: str, tags: Optional[List[str]] = None, repository: Optional[str] = None
    ) -> List[RulePackageInfo]:
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
        self, package_name: str, version: str = "latest", repository: Optional[str] = None
    ) -> Optional[RulePackageInfo]:
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
        self, package_name: str, version: str, output_path: str, repository: Optional[str] = None
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
            raise RepositoryError(
                f"Failed to download package from any repository: {str(last_error)}"
            )
        else:
            raise RepositoryError(
                f"Package {package_name} version {version} not found in any repository"
            )

    def resolve_dependencies(
        self, package_name: str, version: str = "latest"
    ) -> List[RulePackageInfo]:
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
