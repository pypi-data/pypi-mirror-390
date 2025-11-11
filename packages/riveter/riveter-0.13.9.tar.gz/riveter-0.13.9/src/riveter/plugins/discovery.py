"""Plugin discovery system for finding and cataloging available plugins."""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..exceptions import PluginError
from ..logging import debug, info, warning
from .types import PluginDiscoveryResult, PluginInfo, PluginMetadata, PluginStatus


class PluginDiscovery:
    """Discovers plugins from various sources."""

    def __init__(self) -> None:
        self.discovery_paths: List[Path] = []
        self.discovered_plugins: Dict[str, PluginInfo] = {}
        self._setup_default_paths()

    def _setup_default_paths(self) -> None:
        """Set up default plugin discovery paths."""
        # Standard plugin directories
        self.discovery_paths = [
            Path.home() / ".riveter" / "plugins",
            Path("/usr/local/lib/riveter/plugins"),
            Path("/opt/riveter/plugins"),
        ]

        # Add current working directory plugins folder if it exists
        cwd_plugins = Path.cwd() / "plugins"
        if cwd_plugins.exists():
            self.discovery_paths.append(cwd_plugins)

        # Add environment-specified paths
        import os

        env_paths = os.environ.get("RIVETER_PLUGIN_PATH", "")
        if env_paths:
            for path_str in env_paths.split(":"):
                path = Path(path_str.strip())
                if path.exists():
                    self.discovery_paths.append(path)

    def add_discovery_path(self, path: Path) -> None:
        """Add a path to search for plugins."""
        if path not in self.discovery_paths:
            self.discovery_paths.append(path)
            debug(f"Added plugin discovery path: {path}")

    def remove_discovery_path(self, path: Path) -> None:
        """Remove a path from plugin discovery."""
        if path in self.discovery_paths:
            self.discovery_paths.remove(path)
            debug(f"Removed plugin discovery path: {path}")

    def discover_plugins(self, force_refresh: bool = False) -> PluginDiscoveryResult:
        """Discover all available plugins."""
        start_time = time.time()
        result = PluginDiscoveryResult(
            discovered_plugins=[],
            discovery_paths=self.discovery_paths.copy(),
        )

        if force_refresh:
            self.discovered_plugins.clear()

        info(f"Starting plugin discovery in {len(self.discovery_paths)} paths")

        for path in self.discovery_paths:
            try:
                self._discover_in_path(path, result)
            except Exception as e:
                error_msg = f"Error discovering plugins in {path}: {e}"
                result.add_error(error_msg)
                warning(error_msg)

        # Update internal registry
        for plugin in result.discovered_plugins:
            self.discovered_plugins[plugin.name] = plugin

        result.discovery_time = time.time() - start_time
        info(
            f"Plugin discovery completed in {result.discovery_time:.2f}s, "
            f"found {result.plugin_count} plugins"
        )

        return result

    def _discover_in_path(self, path: Path, result: PluginDiscoveryResult) -> None:
        """Discover plugins in a specific path."""
        if not path.exists():
            debug(f"Plugin path does not exist: {path}")
            return

        if not path.is_dir():
            debug(f"Plugin path is not a directory: {path}")
            return

        debug(f"Discovering plugins in: {path}")

        # Look for plugin manifest files
        for manifest_file in path.rglob("plugin.json"):
            try:
                plugin_info = self._load_plugin_manifest(manifest_file)
                if plugin_info:
                    result.discovered_plugins.append(plugin_info)
                    debug(f"Discovered plugin: {plugin_info.name} v{plugin_info.version}")
            except Exception as e:
                error_msg = f"Error loading plugin manifest {manifest_file}: {e}"
                result.add_error(error_msg)
                warning(error_msg)

        # Look for Python packages with plugin metadata
        for py_file in path.rglob("__init__.py"):
            plugin_dir = py_file.parent
            if plugin_dir == path:
                continue  # Skip root __init__.py

            try:
                plugin_info = self._discover_python_plugin(plugin_dir)
                if plugin_info:
                    # Check if we already found this plugin via manifest
                    existing = next(
                        (p for p in result.discovered_plugins if p.name == plugin_info.name), None
                    )
                    if not existing:
                        result.discovered_plugins.append(plugin_info)
                        debug(
                            f"Discovered Python plugin: {plugin_info.name} v{plugin_info.version}"
                        )
            except Exception as e:
                debug(f"Error discovering Python plugin in {plugin_dir}: {e}")

    def _load_plugin_manifest(self, manifest_file: Path) -> Optional[PluginInfo]:
        """Load plugin information from a manifest file."""
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            # Validate required fields
            required_fields = ["name", "version", "description", "author", "license"]
            for field in required_fields:
                if field not in manifest_data:
                    raise PluginError(f"Missing required field '{field}' in plugin manifest")

            metadata = PluginMetadata.from_dict(manifest_data)

            return PluginInfo(
                metadata=metadata,
                source_path=manifest_file.parent,
                status=PluginStatus.DISCOVERED,
            )

        except json.JSONDecodeError as e:
            raise PluginError(f"Invalid JSON in plugin manifest: {e}")
        except Exception as e:
            raise PluginError(f"Error loading plugin manifest: {e}")

    def _discover_python_plugin(self, plugin_dir: Path) -> Optional[PluginInfo]:
        """Discover a Python plugin by examining its structure."""
        # Look for plugin metadata in __init__.py
        init_file = plugin_dir / "__init__.py"
        if not init_file.exists():
            return None

        try:
            # Try to extract plugin metadata from the module
            import importlib.util
            import sys

            spec = importlib.util.spec_from_file_location(f"plugin_{plugin_dir.name}", init_file)
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)

            # Temporarily add to sys.modules to handle relative imports
            sys.modules[spec.name] = module
            try:
                spec.loader.exec_module(module)

                # Look for plugin metadata
                if hasattr(module, "__plugin_metadata__"):
                    metadata_dict = module.__plugin_metadata__
                    metadata = PluginMetadata.from_dict(metadata_dict)

                    return PluginInfo(
                        metadata=metadata,
                        source_path=plugin_dir,
                        status=PluginStatus.DISCOVERED,
                    )

            finally:
                # Clean up sys.modules
                if spec.name in sys.modules:
                    del sys.modules[spec.name]

        except Exception as e:
            debug(f"Could not examine Python plugin {plugin_dir}: {e}")

        return None

    def get_discovered_plugins(self) -> List[PluginInfo]:
        """Get all discovered plugins."""
        return list(self.discovered_plugins.values())

    def get_plugin_by_name(self, name: str) -> Optional[PluginInfo]:
        """Get a specific plugin by name."""
        return self.discovered_plugins.get(name)

    def get_plugins_by_type(self, plugin_type: str) -> List[PluginInfo]:
        """Get all plugins of a specific type."""
        return [
            plugin
            for plugin in self.discovered_plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]

    def refresh_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Refresh information for a specific plugin."""
        plugin = self.discovered_plugins.get(plugin_name)
        if not plugin:
            return None

        # Re-discover the plugin
        try:
            manifest_file = plugin.source_path / "plugin.json"
            if manifest_file.exists():
                updated_plugin = self._load_plugin_manifest(manifest_file)
            else:
                updated_plugin = self._discover_python_plugin(plugin.source_path)

            if updated_plugin:
                self.discovered_plugins[plugin_name] = updated_plugin
                return updated_plugin

        except Exception as e:
            warning(f"Error refreshing plugin {plugin_name}: {e}")

        return plugin

    def validate_plugin_structure(self, plugin_path: Path) -> List[str]:
        """Validate plugin directory structure and return any issues."""
        issues = []

        if not plugin_path.exists():
            issues.append("Plugin directory does not exist")
            return issues

        if not plugin_path.is_dir():
            issues.append("Plugin path is not a directory")
            return issues

        # Check for manifest or Python module
        has_manifest = (plugin_path / "plugin.json").exists()
        has_init = (plugin_path / "__init__.py").exists()

        if not has_manifest and not has_init:
            issues.append("No plugin.json manifest or __init__.py found")

        # If has manifest, validate it
        if has_manifest:
            try:
                self._load_plugin_manifest(plugin_path / "plugin.json")
            except Exception as e:
                issues.append(f"Invalid plugin manifest: {e}")

        # Check for common plugin files
        expected_files = ["README.md", "LICENSE"]
        for expected_file in expected_files:
            if not (plugin_path / expected_file).exists():
                issues.append(f"Missing recommended file: {expected_file}")

        return issues


class PluginRegistry:
    """Registry for managing discovered and loaded plugins."""

    def __init__(self) -> None:
        self.plugins: Dict[str, PluginInfo] = {}
        self.discovery = PluginDiscovery()

    def register_plugin(self, plugin_info: PluginInfo) -> None:
        """Register a plugin in the registry."""
        self.plugins[plugin_info.name] = plugin_info
        debug(f"Registered plugin: {plugin_info.name} v{plugin_info.version}")

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin from the registry."""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            debug(f"Unregistered plugin: {plugin_name}")
            return True
        return False

    def get_plugin(self, name: str) -> Optional[PluginInfo]:
        """Get a plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self, status_filter: Optional[PluginStatus] = None) -> List[PluginInfo]:
        """List all plugins, optionally filtered by status."""
        plugins = list(self.plugins.values())
        if status_filter:
            plugins = [p for p in plugins if p.status == status_filter]
        return plugins

    def get_plugins_by_type(self, plugin_type: str) -> List[PluginInfo]:
        """Get all plugins of a specific type."""
        return [
            plugin for plugin in self.plugins.values() if plugin.metadata.plugin_type == plugin_type
        ]

    def discover_plugins(self, force_refresh: bool = False) -> PluginDiscoveryResult:
        """Discover plugins and update registry."""
        result = self.discovery.discover_plugins(force_refresh)

        # Update registry with discovered plugins
        for plugin in result.discovered_plugins:
            self.register_plugin(plugin)

        return result

    def get_plugin_statistics(self) -> Dict[str, int]:
        """Get statistics about registered plugins."""
        stats = {
            "total": len(self.plugins),
            "by_status": {},
            "by_type": {},
        }

        for plugin in self.plugins.values():
            # Count by status
            status = plugin.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Count by type
            plugin_type = plugin.metadata.plugin_type
            stats["by_type"][plugin_type] = stats["by_type"].get(plugin_type, 0) + 1

        return stats
