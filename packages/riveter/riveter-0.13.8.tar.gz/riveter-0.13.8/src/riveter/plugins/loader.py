"""Plugin loading system for dynamically loading and initializing plugins."""

import importlib.util
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from ..exceptions import PluginError
from ..logging import debug, error, info, warning
from ..models.protocols import PluginInterface
from .types import PluginInfo, PluginLoadResult, PluginStatus


class PluginLoadError(PluginError):
    """Error loading a plugin."""

    def __init__(
        self,
        message: str,
        *,
        plugin_name: str | None = None,
        plugin_path: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            plugin_name=plugin_name,
            **kwargs,
        )
        self.plugin_name = plugin_name
        self.plugin_path = plugin_path


class PluginLoader:
    """Loads and initializes plugins."""

    def __init__(self) -> None:
        self.loaded_modules: Dict[str, Any] = {}
        self.dependency_graph: Dict[str, List[str]] = {}

    def load_plugin(self, plugin_info: PluginInfo) -> PluginLoadResult:
        """Load a single plugin."""
        start_time = time.time()
        result = PluginLoadResult(success=False)

        try:
            info(f"Loading plugin: {plugin_info.name} v{plugin_info.version}")

            # Check if plugin is already loaded
            if plugin_info.is_loaded:
                result.add_warning(f"Plugin {plugin_info.name} is already loaded")
                result.success = True
                result.plugin_info = plugin_info
                return result

            # Load the plugin module
            plugin_module = self._load_plugin_module(plugin_info)
            if not plugin_module:
                raise PluginLoadError(
                    f"Failed to load plugin module",
                    plugin_name=plugin_info.name,
                    plugin_path=plugin_info.source_path,
                )

            # Find and instantiate the plugin class
            plugin_instance = self._instantiate_plugin(plugin_module, plugin_info)
            if not plugin_instance:
                raise PluginLoadError(
                    f"Failed to instantiate plugin",
                    plugin_name=plugin_info.name,
                )

            # Update plugin info
            plugin_info.instance = plugin_instance
            plugin_info.status = PluginStatus.LOADED
            plugin_info.load_time = time.time() - start_time

            # Store loaded module
            self.loaded_modules[plugin_info.name] = plugin_module

            result.success = True
            result.plugin_info = plugin_info
            result.load_time = plugin_info.load_time

            info(
                f"Successfully loaded plugin: {plugin_info.name} "
                f"in {plugin_info.load_time:.3f}s"
            )

        except Exception as e:
            error_msg = f"Error loading plugin {plugin_info.name}: {e}"
            error(error_msg)

            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)

            result.error_message = error_msg
            result.load_time = time.time() - start_time

        return result

    def _load_plugin_module(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Load the plugin module from its source path."""
        try:
            # Determine the main module file
            main_module_file = self._find_main_module(plugin_info.source_path)
            if not main_module_file:
                raise PluginLoadError(
                    f"Could not find main module file",
                    plugin_name=plugin_info.name,
                    plugin_path=plugin_info.source_path,
                )

            # Create module spec
            module_name = f"riveter_plugin_{plugin_info.name}"
            spec = importlib.util.spec_from_file_location(module_name, main_module_file)

            if not spec or not spec.loader:
                raise PluginLoadError(
                    f"Could not create module spec",
                    plugin_name=plugin_info.name,
                    plugin_path=main_module_file,
                )

            # Load the module
            module = importlib.util.module_from_spec(spec)

            # Add to sys.modules before execution to handle relative imports
            sys.modules[module_name] = module

            try:
                spec.loader.exec_module(module)
                debug(f"Loaded module for plugin: {plugin_info.name}")
                return module

            except Exception as e:
                # Clean up sys.modules on failure
                if module_name in sys.modules:
                    del sys.modules[module_name]
                raise PluginLoadError(
                    f"Error executing plugin module: {e}",
                    plugin_name=plugin_info.name,
                    cause=e,
                )

        except PluginLoadError:
            raise
        except Exception as e:
            raise PluginLoadError(
                f"Unexpected error loading plugin module: {e}",
                plugin_name=plugin_info.name,
                cause=e,
            )

    def _find_main_module(self, plugin_path: Path) -> Optional[Path]:
        """Find the main module file for a plugin."""
        # Check for __init__.py (package-style plugin)
        init_file = plugin_path / "__init__.py"
        if init_file.exists():
            return init_file

        # Check for main.py
        main_file = plugin_path / "main.py"
        if main_file.exists():
            return main_file

        # Check for plugin.py
        plugin_file = plugin_path / "plugin.py"
        if plugin_file.exists():
            return plugin_file

        # Check for file with same name as directory
        dir_name_file = plugin_path / f"{plugin_path.name}.py"
        if dir_name_file.exists():
            return dir_name_file

        return None

    def _instantiate_plugin(
        self, module: Any, plugin_info: PluginInfo
    ) -> Optional[PluginInterface]:
        """Find and instantiate the plugin class from the module."""
        # Look for plugin class in entry points
        entry_points = plugin_info.metadata.entry_points
        if "plugin_class" in entry_points:
            class_name = entry_points["plugin_class"]
            if hasattr(module, class_name):
                plugin_class = getattr(module, class_name)
                return self._create_plugin_instance(plugin_class, plugin_info)

        # Look for common plugin class names
        common_names = [
            "Plugin",
            f"{plugin_info.name.title()}Plugin",
            f"{plugin_info.name.replace('-', '_').title()}Plugin",
            "RiveterPlugin",
        ]

        for class_name in common_names:
            if hasattr(module, class_name):
                plugin_class = getattr(module, class_name)
                if self._is_plugin_class(plugin_class):
                    return self._create_plugin_instance(plugin_class, plugin_info)

        # Look for any class that implements PluginInterface
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and self._is_plugin_class(attr)
                and not attr_name.startswith("_")
            ):
                return self._create_plugin_instance(attr, plugin_info)

        return None

    def _is_plugin_class(self, cls: Type) -> bool:
        """Check if a class is a valid plugin class."""
        try:
            # Check if it implements PluginInterface
            return isinstance(cls, type) and issubclass(cls, PluginInterface)
        except (TypeError, AttributeError):
            return False

    def _create_plugin_instance(
        self, plugin_class: Type, plugin_info: PluginInfo
    ) -> PluginInterface:
        """Create an instance of the plugin class."""
        try:
            # Try to instantiate with no arguments first
            instance = plugin_class()

            # Verify it implements the protocol
            if not isinstance(instance, PluginInterface):
                raise PluginLoadError(
                    f"Plugin class does not implement PluginInterface",
                    plugin_name=plugin_info.name,
                )

            return instance

        except Exception as e:
            raise PluginLoadError(
                f"Error instantiating plugin class: {e}",
                plugin_name=plugin_info.name,
                cause=e,
            )

    def initialize_plugin(self, plugin_info: PluginInfo, config: Dict[str, Any]) -> bool:
        """Initialize a loaded plugin."""
        if not plugin_info.is_loaded or not plugin_info.instance:
            warning(f"Cannot initialize plugin {plugin_info.name}: not loaded")
            return False

        try:
            start_time = time.time()

            # Create configuration object
            from ..models.config import RiveterConfig

            riveter_config = RiveterConfig.from_dict(config)

            # Initialize the plugin
            plugin_info.instance.initialize(riveter_config)

            plugin_info.status = PluginStatus.INITIALIZED
            plugin_info.initialization_time = time.time() - start_time
            plugin_info.configuration = config

            info(
                f"Initialized plugin: {plugin_info.name} "
                f"in {plugin_info.initialization_time:.3f}s"
            )

            return True

        except Exception as e:
            error_msg = f"Error initializing plugin {plugin_info.name}: {e}"
            error(error_msg)

            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = error_msg

            return False

    def unload_plugin(self, plugin_info: PluginInfo) -> bool:
        """Unload a plugin and clean up resources."""
        try:
            # Call cleanup if plugin is initialized
            if plugin_info.instance and plugin_info.is_initialized:
                try:
                    plugin_info.instance.cleanup()
                except Exception as e:
                    warning(f"Error during plugin cleanup for {plugin_info.name}: {e}")

            # Remove from loaded modules
            if plugin_info.name in self.loaded_modules:
                module_name = f"riveter_plugin_{plugin_info.name}"
                if module_name in sys.modules:
                    del sys.modules[module_name]
                del self.loaded_modules[plugin_info.name]

            # Reset plugin info
            plugin_info.instance = None
            plugin_info.status = PluginStatus.DISCOVERED
            plugin_info.error_message = None
            plugin_info.load_time = None
            plugin_info.initialization_time = None
            plugin_info.configuration = {}

            info(f"Unloaded plugin: {plugin_info.name}")
            return True

        except Exception as e:
            error(f"Error unloading plugin {plugin_info.name}: {e}")
            return False

    def load_plugins_batch(self, plugins: List[PluginInfo]) -> List[PluginLoadResult]:
        """Load multiple plugins, handling dependencies."""
        results = []

        # Build dependency graph
        self._build_dependency_graph(plugins)

        # Sort plugins by dependency order
        sorted_plugins = self._sort_by_dependencies(plugins)

        # Load plugins in dependency order
        for plugin in sorted_plugins:
            result = self.load_plugin(plugin)
            results.append(result)

            # Stop loading if a critical dependency fails
            if not result.success and self._is_critical_dependency(plugin, plugins):
                warning(f"Critical plugin {plugin.name} failed to load, " f"stopping batch load")
                break

        return results

    def _build_dependency_graph(self, plugins: List[PluginInfo]) -> None:
        """Build dependency graph for plugins."""
        self.dependency_graph.clear()

        for plugin in plugins:
            dependencies = plugin.metadata.dependencies
            self.dependency_graph[plugin.name] = dependencies

    def _sort_by_dependencies(self, plugins: List[PluginInfo]) -> List[PluginInfo]:
        """Sort plugins by dependency order using topological sort."""
        # Simple topological sort implementation
        visited = set()
        temp_visited = set()
        result = []
        plugin_map = {p.name: p for p in plugins}

        def visit(plugin_name: str) -> None:
            if plugin_name in temp_visited:
                # Circular dependency detected
                warning(f"Circular dependency detected involving {plugin_name}")
                return

            if plugin_name in visited:
                return

            temp_visited.add(plugin_name)

            # Visit dependencies first
            dependencies = self.dependency_graph.get(plugin_name, [])
            for dep in dependencies:
                if dep in plugin_map:
                    visit(dep)

            temp_visited.remove(plugin_name)
            visited.add(plugin_name)

            if plugin_name in plugin_map:
                result.append(plugin_map[plugin_name])

        # Visit all plugins
        for plugin in plugins:
            if plugin.name not in visited:
                visit(plugin.name)

        return result

    def _is_critical_dependency(self, plugin: PluginInfo, all_plugins: List[PluginInfo]) -> bool:
        """Check if a plugin is a critical dependency for others."""
        plugin_name = plugin.name
        for other_plugin in all_plugins:
            if plugin_name in other_plugin.metadata.dependencies:
                return True
        return False

    def get_loaded_plugins(self) -> List[str]:
        """Get names of all loaded plugins."""
        return list(self.loaded_modules.keys())

    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if a plugin is loaded."""
        return plugin_name in self.loaded_modules

    def get_plugin_module(self, plugin_name: str) -> Optional[Any]:
        """Get the loaded module for a plugin."""
        return self.loaded_modules.get(plugin_name)
