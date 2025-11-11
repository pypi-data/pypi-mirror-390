"""Command registry with lazy loading and performance optimization.

This module provides a command registry system that supports lazy loading,
performance monitoring, and extensible command management.
"""

import importlib
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Type

from ..models.config import CLIArgs
from .interface import BaseCommand, Command, CommandResult
from .performance import LazyInitializer, performance_monitor


class CommandRegistry:
    """Registry for CLI commands with lazy loading and performance optimization."""

    def __init__(self) -> None:
        """Initialize command registry."""
        self._commands: Dict[str, LazyInitializer] = {}
        self._aliases: Dict[str, str] = {}
        self._command_metadata: Dict[str, Dict[str, Any]] = {}
        self._loaded_commands: Dict[str, Command] = {}

    def register_command(
        self,
        name: str,
        command_class: Type[BaseCommand] | Callable[[], Command],
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a command with lazy loading.

        Args:
            name: Command name
            command_class: Command class or factory function
            aliases: Optional command aliases
            metadata: Optional command metadata
        """
        # Create lazy initializer for the command
        if isinstance(command_class, type):
            # Class-based command
            initializer = lambda: command_class()
        else:
            # Factory function
            initializer = command_class

        self._commands[name] = LazyInitializer(initializer)

        # Register aliases
        if aliases:
            for alias in aliases:
                self._aliases[alias] = name

        # Store metadata
        if metadata:
            self._command_metadata[name] = metadata

    def register_command_module(
        self,
        name: str,
        module_path: str,
        class_name: str,
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a command from a module with lazy loading.

        Args:
            name: Command name
            module_path: Module path to import
            class_name: Class name in the module
            aliases: Optional command aliases
            metadata: Optional command metadata
        """

        def lazy_loader() -> Command:
            module = importlib.import_module(module_path)
            command_class = getattr(module, class_name)
            return command_class()

        self._commands[name] = LazyInitializer(lazy_loader)

        # Register aliases
        if aliases:
            for alias in aliases:
                self._aliases[alias] = name

        # Store metadata
        if metadata:
            self._command_metadata[name] = metadata

    def get_command(self, name: str) -> Optional[Command]:
        """Get command by name or alias with lazy loading.

        Args:
            name: Command name or alias

        Returns:
            Command instance or None if not found
        """
        # Resolve alias
        if name in self._aliases:
            name = self._aliases[name]

        # Check if already loaded
        if name in self._loaded_commands:
            return self._loaded_commands[name]

        # Check if command exists
        if name not in self._commands:
            return None

        try:
            # Lazy load the command
            command = self._commands[name].get()
            self._loaded_commands[name] = command
            return command
        except Exception as e:
            # Log error if debug mode is enabled
            if os.getenv("RIVETER_DEBUG_COMMANDS", "").lower() in ("1", "true", "yes"):
                print(f"Failed to load command '{name}': {e}", file=sys.stderr)
            return None

    def list_commands(self) -> List[str]:
        """List all registered command names.

        Returns:
            List of command names
        """
        return list(self._commands.keys())

    def list_aliases(self) -> Dict[str, str]:
        """List all command aliases.

        Returns:
            Dictionary of alias to command name mappings
        """
        return self._aliases.copy()

    def get_command_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a command.

        Args:
            name: Command name

        Returns:
            Command metadata
        """
        return self._command_metadata.get(name, {})

    def execute_command(self, name: str, args: CLIArgs) -> CommandResult:
        """Execute a command with performance monitoring.

        Args:
            name: Command name
            args: CLI arguments

        Returns:
            Command execution result
        """
        command = self.get_command(name)

        if command is None:
            return CommandResult(exit_code=1, error=f"Unknown command: {name}")

        try:
            # Execute with performance monitoring
            @performance_monitor
            def execute_with_monitoring() -> CommandResult:
                return command.execute(args)

            return execute_with_monitoring()

        except Exception as e:
            return CommandResult(exit_code=1, error=f"Command execution failed: {e}")

    def preload_commands(self, command_names: Optional[List[str]] = None) -> None:
        """Preload commands for better performance.

        Args:
            command_names: Optional list of commands to preload. If None, preloads all.
        """
        if not os.getenv("RIVETER_PRELOAD_COMMANDS", "").lower() in ("1", "true", "yes"):
            return

        commands_to_load = command_names or list(self._commands.keys())

        for name in commands_to_load:
            try:
                self.get_command(name)
            except Exception:
                # Ignore errors during preloading
                pass

    def clear_cache(self) -> None:
        """Clear the command cache."""
        self._loaded_commands.clear()

        # Reset lazy initializers
        for lazy_init in self._commands.values():
            lazy_init.reset()


class PluggableCommandSystem:
    """Pluggable command system with extension support."""

    def __init__(self, registry: CommandRegistry) -> None:
        """Initialize pluggable command system.

        Args:
            registry: Command registry to use
        """
        self._registry = registry
        self._plugin_paths: List[str] = []

    def add_plugin_path(self, path: str) -> None:
        """Add a plugin search path.

        Args:
            path: Path to search for plugins
        """
        if path not in self._plugin_paths:
            self._plugin_paths.append(path)

    def discover_plugins(self) -> None:
        """Discover and register plugins from plugin paths."""
        for path in self._plugin_paths:
            if not os.path.exists(path):
                continue

            try:
                self._discover_plugins_in_path(path)
            except Exception as e:
                if os.getenv("RIVETER_DEBUG_PLUGINS", "").lower() in ("1", "true", "yes"):
                    print(f"Plugin discovery error in {path}: {e}", file=sys.stderr)

    def _discover_plugins_in_path(self, path: str) -> None:
        """Discover plugins in a specific path.

        Args:
            path: Path to search
        """
        import glob

        # Look for Python files that might contain commands
        plugin_files = glob.glob(os.path.join(path, "*_command.py"))

        for plugin_file in plugin_files:
            try:
                self._load_plugin_file(plugin_file)
            except Exception as e:
                if os.getenv("RIVETER_DEBUG_PLUGINS", "").lower() in ("1", "true", "yes"):
                    print(f"Failed to load plugin {plugin_file}: {e}", file=sys.stderr)

    def _load_plugin_file(self, plugin_file: str) -> None:
        """Load a plugin file.

        Args:
            plugin_file: Path to plugin file
        """
        import importlib.util

        spec = importlib.util.spec_from_file_location("plugin", plugin_file)
        if spec is None or spec.loader is None:
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for command registration function
        if hasattr(module, "register_commands"):
            module.register_commands(self._registry)

    def get_registry(self) -> CommandRegistry:
        """Get the command registry.

        Returns:
            Command registry
        """
        return self._registry


# Global command registry instance
_global_registry: Optional[CommandRegistry] = None


def get_global_registry() -> CommandRegistry:
    """Get the global command registry.

    Returns:
        Global command registry
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = CommandRegistry()
        _register_builtin_commands(_global_registry)
    return _global_registry


def _register_builtin_commands(registry: CommandRegistry) -> None:
    """Register built-in commands.

    Args:
        registry: Command registry to register commands with
    """
    # Register core commands with lazy loading
    registry.register_command_module(
        "scan",
        "riveter.cli.commands",
        "ScanCommand",
        metadata={"description": "Validate Terraform configuration against rules"},
    )

    registry.register_command_module(
        "list-rule-packs",
        "riveter.cli.commands",
        "ListRulePacksCommand",
        aliases=["list-packs"],
        metadata={"description": "List all available rule packs"},
    )

    registry.register_command_module(
        "validate-rule-pack",
        "riveter.cli.commands",
        "ValidateRulePackCommand",
        aliases=["validate-pack"],
        metadata={"description": "Validate a rule pack file"},
    )


def create_pluggable_system() -> PluggableCommandSystem:
    """Create a pluggable command system.

    Returns:
        Pluggable command system
    """
    registry = get_global_registry()
    system = PluggableCommandSystem(registry)

    # Add default plugin paths
    default_paths = [
        os.path.expanduser("~/.riveter/plugins"),
        os.path.join(os.getcwd(), "riveter_plugins"),
    ]

    for path in default_paths:
        system.add_plugin_path(path)

    return system
