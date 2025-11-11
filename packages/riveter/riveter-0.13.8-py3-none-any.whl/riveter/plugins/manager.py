"""Plugin manager for coordinating plugin discovery, loading, and lifecycle."""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..exceptions import PluginError
from ..logging import debug, error, info, warning
from ..models.config import RiveterConfig
from ..models.protocols import FormatterPlugin, ParserPlugin, PluginInterface, RulePlugin
from .discovery import PluginRegistry
from .loader import PluginLoader
from .types import PluginConfiguration, PluginInfo, PluginStatus


class PluginManager:
    """Manages the complete plugin lifecycle."""

    def __init__(self, config: Optional[RiveterConfig] = None) -> None:
        self.config = config or RiveterConfig()
        self.registry = PluginRegistry()
        self.loader = PluginLoader()
        self.plugin_configurations: Dict[str, PluginConfiguration] = {}
        self._extension_points: Dict[str, List[Any]] = {
            "rules": [],
            "formatters": [],
            "parsers": [],
            "operators": [],
        }

    def discover_plugins(self, force_refresh: bool = False) -> int:
        """Discover all available plugins."""
        info("Starting plugin discovery")
        result = self.registry.discover_plugins(force_refresh)

        if result.has_errors:
            for error_msg in result.errors:
                error(f"Plugin discovery error: {error_msg}")

        if result.has_warnings:
            for warning_msg in result.warnings:
                warning(f"Plugin discovery warning: {warning_msg}")

        info(f"Discovered {result.plugin_count} plugins in {result.discovery_time:.2f}s")
        return result.plugin_count

    def load_plugin(self, plugin_name: str, auto_initialize: bool = True) -> bool:
        """Load a specific plugin by name."""
        plugin_info = self.registry.get_plugin(plugin_name)
        if not plugin_info:
            error(f"Plugin not found: {plugin_name}")
            return False

        # Check if plugin is enabled
        plugin_config = self.plugin_configurations.get(plugin_name)
        if plugin_config and not plugin_config.enabled:
            debug(f"Plugin {plugin_name} is disabled, skipping load")
            return False

        # Load the plugin
        result = self.loader.load_plugin(plugin_info)
        if not result.success:
            error(f"Failed to load plugin {plugin_name}: {result.error_message}")
            return False

        # Initialize if requested
        if auto_initialize:
            config_dict = plugin_config.settings if plugin_config else {}
            if not self.loader.initialize_plugin(plugin_info, config_dict):
                error(f"Failed to initialize plugin {plugin_name}")
                return False

        # Register extension points
        self._register_extension_points(plugin_info)

        info(f"Successfully loaded plugin: {plugin_name}")
        return True

    def load_all_plugins(self, auto_load_only: bool = True) -> Dict[str, bool]:
        """Load all discovered plugins."""
        results = {}
        plugins_to_load = []

        for plugin_info in self.registry.list_plugins(PluginStatus.DISCOVERED):
            plugin_config = self.plugin_configurations.get(plugin_info.name)

            # Check if plugin should be auto-loaded
            if auto_load_only and plugin_config and not plugin_config.auto_load:
                debug(f"Skipping plugin {plugin_info.name} (auto_load=False)")
                continue

            plugins_to_load.append(plugin_info)

        # Load plugins in dependency order
        load_results = self.loader.load_plugins_batch(plugins_to_load)

        # Initialize loaded plugins and register extension points
        for i, result in enumerate(load_results):
            plugin_info = plugins_to_load[i]
            plugin_name = plugin_info.name

            if result.success:
                # Initialize plugin
                plugin_config = self.plugin_configurations.get(plugin_name)
                config_dict = plugin_config.settings if plugin_config else {}

                if self.loader.initialize_plugin(plugin_info, config_dict):
                    self._register_extension_points(plugin_info)
                    results[plugin_name] = True
                else:
                    results[plugin_name] = False
            else:
                results[plugin_name] = False

        loaded_count = sum(1 for success in results.values() if success)
        info(f"Loaded {loaded_count}/{len(results)} plugins")

        return results

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin."""
        plugin_info = self.registry.get_plugin(plugin_name)
        if not plugin_info:
            warning(f"Plugin not found: {plugin_name}")
            return False

        # Unregister extension points
        self._unregister_extension_points(plugin_info)

        # Unload the plugin
        success = self.loader.unload_plugin(plugin_info)
        if success:
            info(f"Unloaded plugin: {plugin_name}")
        else:
            error(f"Failed to unload plugin: {plugin_name}")

        return success

    def unload_all_plugins(self) -> Dict[str, bool]:
        """Unload all loaded plugins."""
        results = {}
        loaded_plugins = self.get_loaded_plugins()

        for plugin_info in loaded_plugins:
            results[plugin_info.name] = self.unload_plugin(plugin_info.name)

        return results

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin (unload and load again)."""
        info(f"Reloading plugin: {plugin_name}")

        # Unload first
        if not self.unload_plugin(plugin_name):
            error(f"Failed to unload plugin {plugin_name} for reload")
            return False

        # Refresh plugin discovery for this specific plugin
        plugin_info = self.registry.get_plugin(plugin_name)
        if plugin_info:
            self.registry.discovery.refresh_plugin(plugin_name)

        # Load again
        return self.load_plugin(plugin_name)

    def configure_plugin(self, plugin_name: str, configuration: PluginConfiguration) -> None:
        """Configure a plugin."""
        self.plugin_configurations[plugin_name] = configuration
        debug(f"Configured plugin: {plugin_name}")

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a plugin."""
        return self.registry.get_plugin(plugin_name)

    def list_plugins(self, status_filter: Optional[PluginStatus] = None) -> List[PluginInfo]:
        """List all plugins, optionally filtered by status."""
        return self.registry.list_plugins(status_filter)

    def get_loaded_plugins(self) -> List[PluginInfo]:
        """Get all loaded plugins."""
        return [plugin for plugin in self.registry.list_plugins() if plugin.is_loaded]

    def get_initialized_plugins(self) -> List[PluginInfo]:
        """Get all initialized plugins."""
        return [plugin for plugin in self.registry.list_plugins() if plugin.is_initialized]

    def get_plugins_by_type(self, plugin_type: str) -> List[PluginInfo]:
        """Get all plugins of a specific type."""
        return self.registry.get_plugins_by_type(plugin_type)

    def _register_extension_points(self, plugin_info: PluginInfo) -> None:
        """Register extension points provided by a plugin."""
        if not plugin_info.instance or not plugin_info.is_initialized:
            return

        instance = plugin_info.instance

        try:
            # Register rule extensions
            if isinstance(instance, RulePlugin):
                # Register custom operators
                operators = instance.get_custom_operators()
                self._extension_points["operators"].extend(operators.items())

                # Register rule packs
                rule_packs = instance.get_rule_packs()
                self._extension_points["rules"].extend(rule_packs)

                debug(
                    f"Registered {len(operators)} operators and "
                    f"{len(rule_packs)} rule packs from {plugin_info.name}"
                )

            # Register formatter extensions
            if isinstance(instance, FormatterPlugin):
                formatters = instance.get_formatters()
                self._extension_points["formatters"].extend(formatters.items())
                debug(f"Registered {len(formatters)} formatters from {plugin_info.name}")

            # Register parser extensions
            if isinstance(instance, ParserPlugin):
                parsers = instance.get_parsers()
                self._extension_points["parsers"].extend(parsers.items())
                debug(f"Registered {len(parsers)} parsers from {plugin_info.name}")

        except Exception as e:
            error(f"Error registering extension points for {plugin_info.name}: {e}")

    def _unregister_extension_points(self, plugin_info: PluginInfo) -> None:
        """Unregister extension points provided by a plugin."""
        if not plugin_info.instance:
            return

        # Remove extensions registered by this plugin
        # This is a simplified approach - in practice, you'd want to track
        # which extensions came from which plugin
        try:
            # For now, we'll just log that we're unregistering
            debug(f"Unregistering extension points for {plugin_info.name}")

            # In a full implementation, you'd remove specific extensions
            # that were registered by this plugin

        except Exception as e:
            error(f"Error unregistering extension points for {plugin_info.name}: {e}")

    def get_extension_points(self, extension_type: str) -> List[Any]:
        """Get all registered extension points of a specific type."""
        return self._extension_points.get(extension_type, [])

    def get_custom_operators(self) -> Dict[str, Any]:
        """Get all custom operators from plugins."""
        operators = {}
        for name, operator in self._extension_points["operators"]:
            operators[name] = operator
        return operators

    def get_custom_formatters(self) -> Dict[str, Any]:
        """Get all custom formatters from plugins."""
        formatters = {}
        for name, formatter in self._extension_points["formatters"]:
            formatters[name] = formatter
        return formatters

    def get_custom_parsers(self) -> Dict[str, Any]:
        """Get all custom parsers from plugins."""
        parsers = {}
        for name, parser in self._extension_points["parsers"]:
            parsers[name] = parser
        return parsers

    def get_plugin_statistics(self) -> Dict[str, Any]:
        """Get comprehensive plugin statistics."""
        registry_stats = self.registry.get_plugin_statistics()

        # Add extension point statistics
        extension_stats = {}
        for ext_type, extensions in self._extension_points.items():
            extension_stats[ext_type] = len(extensions)

        # Add performance statistics
        loaded_plugins = self.get_loaded_plugins()
        load_times = [p.load_time for p in loaded_plugins if p.load_time]
        init_times = [p.initialization_time for p in loaded_plugins if p.initialization_time]

        performance_stats = {
            "average_load_time": sum(load_times) / len(load_times) if load_times else 0,
            "average_init_time": sum(init_times) / len(init_times) if init_times else 0,
            "total_load_time": sum(load_times),
            "total_init_time": sum(init_times),
        }

        return {
            "registry": registry_stats,
            "extensions": extension_stats,
            "performance": performance_stats,
            "configurations": len(self.plugin_configurations),
        }

    def validate_plugin_dependencies(self) -> Dict[str, List[str]]:
        """Validate plugin dependencies and return any issues."""
        issues = {}

        for plugin_info in self.registry.list_plugins():
            plugin_issues = []

            for dependency in plugin_info.metadata.dependencies:
                dep_plugin = self.registry.get_plugin(dependency)
                if not dep_plugin:
                    plugin_issues.append(f"Missing dependency: {dependency}")
                elif not dep_plugin.is_loaded:
                    plugin_issues.append(f"Dependency not loaded: {dependency}")

            if plugin_issues:
                issues[plugin_info.name] = plugin_issues

        return issues

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the plugin system."""
        health = {
            "status": "healthy",
            "issues": [],
            "warnings": [],
            "statistics": self.get_plugin_statistics(),
        }

        # Check for plugins with errors
        error_plugins = self.registry.list_plugins(PluginStatus.ERROR)
        if error_plugins:
            health["status"] = "degraded"
            for plugin in error_plugins:
                health["issues"].append(f"Plugin {plugin.name} has error: {plugin.error_message}")

        # Check for dependency issues
        dependency_issues = self.validate_plugin_dependencies()
        if dependency_issues:
            health["status"] = "degraded"
            for plugin_name, issues in dependency_issues.items():
                for issue in issues:
                    health["issues"].append(f"Plugin {plugin_name}: {issue}")

        # Check for disabled plugins that others depend on
        for plugin_info in self.registry.list_plugins():
            plugin_config = self.plugin_configurations.get(plugin_info.name)
            if plugin_config and not plugin_config.enabled:
                # Check if other plugins depend on this one
                dependents = [
                    p
                    for p in self.registry.list_plugins()
                    if plugin_info.name in p.metadata.dependencies
                ]
                if dependents:
                    dependent_names = [p.name for p in dependents]
                    health["warnings"].append(
                        f"Disabled plugin {plugin_info.name} is required by: {', '.join(dependent_names)}"
                    )

        return health

    def shutdown(self) -> None:
        """Shutdown the plugin manager and clean up all resources."""
        info("Shutting down plugin manager")

        # Unload all plugins
        self.unload_all_plugins()

        # Clear extension points
        self._extension_points.clear()

        # Clear configurations
        self.plugin_configurations.clear()

        info("Plugin manager shutdown complete")
