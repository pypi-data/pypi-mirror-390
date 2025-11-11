"""Tests for rule repository system."""

import json
import zipfile
from unittest.mock import Mock, patch
from urllib.error import URLError

import pytest

from riveter.rule_repository import (
    HTTPRepository,
    LocalRepository,
    RepositoryConfig,
    RepositoryManager,
    RulePackageInfo,
)


@pytest.fixture
def sample_repository_config():
    """Create a sample repository configuration."""
    return RepositoryConfig(
        name="test-repo",
        url="https://example.com/rules",
        type="http",
        enabled=True,
    )


@pytest.fixture
def sample_package_info():
    """Create sample package information."""
    return RulePackageInfo(
        name="test-pack",
        version="1.0.0",
        description="Test package",
        author="Test Author",
        download_url="https://example.com/test-pack-1.0.0.zip",
        checksum="abc123",
        size_bytes=1024,
        dependencies=[],
        tags=["test"],
        created="2024-01-01",
        updated="2024-01-01",
    )


@pytest.fixture
def sample_repository_index():
    """Create sample repository index data."""
    return {
        "packages": {
            "test-pack": {
                "latest": "1.0.0",
                "versions": {
                    "1.0.0": {
                        "manifest": {
                            "name": "test-pack",
                            "version": "1.0.0",
                            "description": "Test package",
                            "author": "Test Author",
                            "checksum": "abc123",
                            "size_bytes": 1024,
                            "dependencies": [],
                            "tags": ["test"],
                            "created": "2024-01-01",
                            "updated": "2024-01-01",
                        },
                        "download_path": "packages/test-pack-1.0.0.zip",
                    }
                },
            }
        }
    }


class TestRepositoryConfig:
    """Test RepositoryConfig functionality."""

    def test_repository_config_creation(self):
        """Test creating repository configuration."""
        config = RepositoryConfig(
            name="test",
            url="https://example.com",
            type="http",
            auth_token="token123",
            enabled=True,
        )

        assert config.name == "test"
        assert config.url == "https://example.com"
        assert config.type == "http"
        assert config.auth_token == "token123"
        assert config.enabled is True


class TestHTTPRepository:
    """Test HTTPRepository functionality."""

    @patch("riveter.rule_repository.urlopen")
    def test_list_packages(self, mock_urlopen, sample_repository_config, sample_repository_index):
        """Test listing packages from HTTP repository."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(sample_repository_index).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repo = HTTPRepository(sample_repository_config)
        packages = repo.list_packages()

        assert len(packages) == 1
        assert packages[0].name == "test-pack"
        assert packages[0].version == "1.0.0"

    @patch("riveter.rule_repository.urlopen")
    def test_get_package_info(
        self, mock_urlopen, sample_repository_config, sample_repository_index
    ):
        """Test getting package information."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(sample_repository_index).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repo = HTTPRepository(sample_repository_config)
        package_info = repo.get_package_info("test-pack", "1.0.0")

        assert package_info is not None
        assert package_info.name == "test-pack"
        assert package_info.version == "1.0.0"

    @patch("riveter.rule_repository.urlopen")
    def test_get_package_info_latest(
        self, mock_urlopen, sample_repository_config, sample_repository_index
    ):
        """Test getting latest package version."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(sample_repository_index).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repo = HTTPRepository(sample_repository_config)
        package_info = repo.get_package_info("test-pack", "latest")

        assert package_info is not None
        assert package_info.version == "1.0.0"

    @patch("riveter.rule_repository.urlopen")
    def test_get_nonexistent_package(
        self, mock_urlopen, sample_repository_config, sample_repository_index
    ):
        """Test getting information for nonexistent package."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(sample_repository_index).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repo = HTTPRepository(sample_repository_config)
        package_info = repo.get_package_info("nonexistent-pack", "1.0.0")

        assert package_info is None

    @patch("riveter.rule_repository.urlretrieve")
    @patch("riveter.rule_repository.urlopen")
    def test_download_package(
        self, mock_urlopen, mock_urlretrieve, sample_repository_config, sample_repository_index
    ):
        """Test downloading a package."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(sample_repository_index).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repo = HTTPRepository(sample_repository_config)
        output_path = "/tmp/test-pack.zip"

        result_path = repo.download_package("test-pack", "1.0.0", output_path)

        assert result_path == output_path
        mock_urlretrieve.assert_called_once()

    @patch("riveter.rule_repository.urlopen")
    def test_search_packages(self, mock_urlopen, sample_repository_config, sample_repository_index):
        """Test searching for packages."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(sample_repository_index).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repo = HTTPRepository(sample_repository_config)
        results = repo.search_packages("test")

        assert len(results) == 1
        assert results[0].name == "test-pack"

    @patch("riveter.rule_repository.urlopen")
    def test_repository_error_handling(self, mock_urlopen, sample_repository_config):
        """Test error handling for repository access."""
        mock_urlopen.side_effect = URLError("Connection failed")

        repo = HTTPRepository(sample_repository_config)

        with pytest.raises(Exception) as exc_info:
            repo.list_packages()

        assert "Failed to fetch repository index" in str(exc_info.value)


class TestLocalRepository:
    """Test LocalRepository functionality."""

    def test_list_packages_empty_directory(self, tmp_path):
        """Test listing packages from empty directory."""
        config = RepositoryConfig(
            name="local-repo",
            url=str(tmp_path),
            type="local",
        )

        repo = LocalRepository(config)
        packages = repo.list_packages()

        assert len(packages) == 0

    def test_list_packages_with_valid_package(self, tmp_path):
        """Test listing packages with valid package file."""
        # Create a mock package file
        package_path = tmp_path / "test-pack.zip"

        # Create a simple ZIP file with manifest
        with zipfile.ZipFile(package_path, "w") as zipf:
            manifest = {
                "name": "test-pack",
                "version": "1.0.0",
                "description": "Test package",
                "author": "Test Author",
                "checksum": "abc123",
                "size_bytes": 1024,
                "dependencies": [],
                "tags": ["test"],
                "created": "2024-01-01",
                "updated": "2024-01-01",
            }
            zipf.writestr("manifest.json", json.dumps(manifest))
            zipf.writestr("rules.yml", "metadata:\n  name: test-pack\nrules: []")

        config = RepositoryConfig(
            name="local-repo",
            url=str(tmp_path),
            type="local",
        )

        with patch("riveter.rule_repository.RulePackageValidator") as mock_validator:
            mock_validator.return_value.validate_package.return_value = {
                "valid": True,
                "manifest": manifest,
            }

            repo = LocalRepository(config)
            packages = repo.list_packages()

            assert len(packages) == 1
            assert packages[0].name == "test-pack"

    def test_download_package(self, tmp_path):
        """Test downloading (copying) a package."""
        # Create source package
        source_path = tmp_path / "test-pack.zip"
        source_path.write_text("test package content")

        config = RepositoryConfig(
            name="local-repo",
            url=str(tmp_path),
            type="local",
        )

        package_info = RulePackageInfo(
            name="test-pack",
            version="1.0.0",
            description="Test package",
            author="Test Author",
            download_url=str(source_path),
            checksum="abc123",
            size_bytes=1024,
            dependencies=[],
            tags=["test"],
            created="2024-01-01",
            updated="2024-01-01",
        )

        repo = LocalRepository(config)

        with patch.object(repo, "get_package_info", return_value=package_info):
            output_path = tmp_path / "downloaded-pack.zip"
            result_path = repo.download_package("test-pack", "1.0.0", str(output_path))

            assert result_path == str(output_path)
            assert output_path.exists()
            assert output_path.read_text() == "test package content"


class TestRepositoryManager:
    """Test RepositoryManager functionality."""

    def test_add_repository(self):
        """Test adding repositories to manager."""
        manager = RepositoryManager(config_path=None)

        config = RepositoryConfig(
            name="test-repo",
            url="https://example.com",
            type="http",
        )

        manager.add_repository(config)

        assert "test-repo" in manager.repositories
        assert isinstance(manager.repositories["test-repo"], HTTPRepository)

    def test_remove_repository(self):
        """Test removing repositories from manager."""
        manager = RepositoryManager(config_path=None)

        config = RepositoryConfig(
            name="test-repo",
            url="https://example.com",
            type="http",
        )

        manager.add_repository(config)
        result = manager.remove_repository("test-repo")

        assert result is True
        assert "test-repo" not in manager.repositories

    def test_remove_nonexistent_repository(self):
        """Test removing nonexistent repository."""
        manager = RepositoryManager(config_path=None)

        result = manager.remove_repository("nonexistent")

        assert result is False

    def test_list_repositories(self):
        """Test listing all repositories."""
        manager = RepositoryManager(config_path=None)

        config1 = RepositoryConfig(name="repo1", url="https://example1.com", type="http")
        config2 = RepositoryConfig(name="repo2", url="https://example2.com", type="http")

        manager.add_repository(config1)
        manager.add_repository(config2)

        repos = manager.list_repositories()

        assert len(repos) >= 2  # May include default repository
        repo_names = [r.name for r in repos]
        assert "repo1" in repo_names
        assert "repo2" in repo_names

    def test_search_packages_across_repositories(self, sample_package_info):
        """Test searching packages across multiple repositories."""
        manager = RepositoryManager(config_path=None)

        # Mock repositories
        mock_repo1 = Mock()
        mock_repo1.search_packages.return_value = [sample_package_info]

        mock_repo2 = Mock()
        mock_repo2.search_packages.return_value = []

        manager.repositories = {
            "repo1": mock_repo1,
            "repo2": mock_repo2,
        }

        results = manager.search_packages("test")

        assert len(results) == 1
        assert results[0].name == "test-pack"

    def test_get_package_info_from_specific_repository(self, sample_package_info):
        """Test getting package info from specific repository."""
        manager = RepositoryManager(config_path=None)

        mock_repo = Mock()
        mock_repo.get_package_info.return_value = sample_package_info

        manager.repositories = {"test-repo": mock_repo}

        result = manager.get_package_info("test-pack", "1.0.0", "test-repo")

        assert result is not None
        assert result.name == "test-pack"
        mock_repo.get_package_info.assert_called_once_with("test-pack", "1.0.0")

    def test_download_package_from_repositories(self, sample_package_info):
        """Test downloading package from repositories."""
        manager = RepositoryManager(config_path=None)

        mock_repo = Mock()
        mock_repo.download_package.return_value = "/tmp/downloaded.zip"

        manager.repositories = {"test-repo": mock_repo}

        result = manager.download_package("test-pack", "1.0.0", "/tmp/output.zip")

        assert result == "/tmp/downloaded.zip"
        mock_repo.download_package.assert_called_once_with("test-pack", "1.0.0", "/tmp/output.zip")

    def test_resolve_dependencies(self, sample_package_info):
        """Test dependency resolution."""
        manager = RepositoryManager(config_path=None)

        # Create package with dependency
        main_package = RulePackageInfo(
            name="main-pack",
            version="1.0.0",
            description="Main package",
            author="Test Author",
            download_url="https://example.com/main-pack.zip",
            checksum="abc123",
            size_bytes=1024,
            dependencies=["dep-pack>=1.0.0"],
            tags=["main"],
            created="2024-01-01",
            updated="2024-01-01",
        )

        dep_package = RulePackageInfo(
            name="dep-pack",
            version="1.0.0",
            description="Dependency package",
            author="Test Author",
            download_url="https://example.com/dep-pack.zip",
            checksum="def456",
            size_bytes=512,
            dependencies=[],
            tags=["dependency"],
            created="2024-01-01",
            updated="2024-01-01",
        )

        mock_repo = Mock()
        mock_repo.get_package_info.side_effect = lambda name, version: {
            ("main-pack", "latest"): main_package,
            ("dep-pack", "1.0.0"): dep_package,
        }.get((name, version))

        manager.repositories = {"test-repo": mock_repo}

        resolved = manager.resolve_dependencies("main-pack", "latest")

        assert len(resolved) == 2
        package_names = [p.name for p in resolved]
        assert "main-pack" in package_names
        assert "dep-pack" in package_names

    def test_unsupported_repository_type(self):
        """Test error handling for unsupported repository type."""
        manager = RepositoryManager(config_path=None)

        config = RepositoryConfig(
            name="test-repo",
            url="https://example.com",
            type="unsupported",
        )

        with pytest.raises(Exception) as exc_info:
            manager.add_repository(config)

        assert "Unsupported repository type" in str(exc_info.value)


class TestIntegration:
    """Integration tests for repository system."""

    def test_full_repository_workflow(self, tmp_path):
        """Test complete repository workflow."""
        # Create local repository with package
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        package_path = repo_dir / "test-pack.zip"

        # Create package with manifest
        with zipfile.ZipFile(package_path, "w") as zipf:
            manifest = {
                "name": "test-pack",
                "version": "1.0.0",
                "description": "Test package",
                "author": "Test Author",
                "checksum": "abc123",
                "size_bytes": 1024,
                "dependencies": [],
                "tags": ["test"],
                "created": "2024-01-01",
                "updated": "2024-01-01",
            }
            zipf.writestr("manifest.json", json.dumps(manifest))
            zipf.writestr("rules.yml", "metadata:\n  name: test-pack\nrules: []")

        # Create repository manager
        config_path = tmp_path / "repos.json"
        manager = RepositoryManager(str(config_path))

        # Add local repository
        repo_config = RepositoryConfig(
            name="local-repo",
            url=str(repo_dir),
            type="local",
        )
        manager.add_repository(repo_config)

        with patch("riveter.rule_repository.RulePackageValidator") as mock_validator:
            mock_validator.return_value.validate_package.return_value = {
                "valid": True,
                "manifest": manifest,
            }

            # Search for packages
            results = manager.search_packages("test")
            assert len(results) == 1
            assert results[0].name == "test-pack"

            # Get package info
            package_info = manager.get_package_info("test-pack", "1.0.0")
            assert package_info is not None
            assert package_info.name == "test-pack"

            # Download package
            output_path = tmp_path / "downloaded.zip"
            result_path = manager.download_package("test-pack", "1.0.0", str(output_path))
            assert result_path == str(output_path)
            assert output_path.exists()
