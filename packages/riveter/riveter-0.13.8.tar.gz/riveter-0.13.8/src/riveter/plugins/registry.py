"""Default plugin registry implementation."""

from typing import Dict, List, Optional

from .discovery import PluginRegistry as BasePluginRegistry
from .types import PluginInfo, PluginStatus


class DefaultPluginRegistry(BasePluginRegistry):
    """Default implementation of plugin registry with additional features."""

    def __init__(self) -> None:
        super().__init__()
        self._plugin_aliases: Dict[str, str] = {}
        self._plugin_tags: Dict[str, List[str]] = {}

    def register_alias(self, alias: str, plugin_name: str) -> None:
        """Register an alias for a plugin name."""
        if plugin_name in self.plugins:
            self._plugin_aliases[alias] = plugin_name

    def resolve_name(self, name_or_alias: str) -> str:
        """Resolve a plugin name or alias to the actual plugin name."""
        return self._plugin_aliases.get(name_or_alias, name_or_alias)

    def get_plugin(self, name_or_alias: str) -> Optional[PluginInfo]:
        """Get a plugin by name or alias."""
        actual_name = self.resolve_name(name_or_alias)
        return super().get_plugin(actual_name)

    def tag_plugin(self, plugin_name: str, tags: List[str]) -> None:
        """Add tags to a plugin."""
        if plugin_name in self.plugins:
            self._plugin_tags[plugin_name] = tags

    def get_plugins_by_tag(self, tag: str) -> List[PluginInfo]:
        """Get all plugins with a specific tag."""
        matching_plugins = []
        for plugin_name, tags in self._plugin_tags.items():
            if tag in tags and plugin_name in self.plugins:
                matching_plugins.append(self.plugins[plugin_name])
        return matching_plugins

    def search_plugins(self, query: str) -> List[PluginInfo]:
        """Search plugins by name, description, or tags."""
        query_lower = query.lower()
        matching_plugins = []

        for plugin in self.plugins.values():
            # Search in name
            if query_lower in plugin.name.lower():
                matching_plugins.append(plugin)
                continue

            # Search in description
            if query_lower in plugin.metadata.description.lower():
                matching_plugins.append(plugin)
                continue

            # Search in keywords
            if any(query_lower in keyword.lower() for keyword in plugin.metadata.keywords):
                matching_plugins.append(plugin)
                continue

            # Search in tags
            plugin_tags = self._plugin_tags.get(plugin.name, [])
            if any(query_lower in tag.lower() for tag in plugin_tags):
                matching_plugins.append(plugin)
                continue

        return matching_plugins

    def get_plugin_dependencies(self, plugin_name: str) -> List[str]:
        """Get the dependencies of a plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.metadata.dependencies
        return []

    def get_plugin_dependents(self, plugin_name: str) -> List[str]:
        """Get plugins that depend on the given plugin."""
        dependents = []
        for plugin in self.plugins.values():
            if plugin_name in plugin.metadata.dependencies:
                dependents.append(plugin.name)
        return dependents

    def get_load_order(self) -> List[str]:
        """Get the recommended load order for all plugins based on dependencies."""
        # Topological sort to determine load order
        visited = set()
        temp_visited = set()
        result = []

        def visit(plugin_name: str) -> None:
            if plugin_name in temp_visited:
                # Circular dependency - skip
                return

            if plugin_name in visited:
                return

            temp_visited.add(plugin_name)

            # Visit dependencies first
            plugin = self.get_plugin(plugin_name)
            if plugin:
                for dep in plugin.metadata.dependencies:
                    if dep in self.plugins:
                        visit(dep)

            temp_visited.remove(plugin_name)
            visited.add(plugin_name)
            result.append(plugin_name)

        # Visit all plugins
        for plugin_name in self.plugins:
            if plugin_name not in visited:
                visit(plugin_name)

        return result

    def export_registry(self) -> Dict[str, any]:
        """Export the registry to a dictionary."""
        return {
            "plugins": {name: plugin.to_dict() for name, plugin in self.plugins.items()},
            "aliases": self._plugin_aliases,
            "tags": self._plugin_tags,
            "statistics": self.get_plugin_statistics(),
        }

    def import_registry(self, data: Dict[str, any]) -> None:
        """Import registry data from a dictionary."""
        # Import plugins
        if "plugins" in data:
            for name, plugin_data in data["plugins"].items():
                # This would need proper deserialization logic
                pass

        # Import aliases
        if "aliases" in data:
            self._plugin_aliases.update(data["aliases"])

        # Import tags
        if "tags" in data:
            self._plugin_tags.update(data["tags"])
