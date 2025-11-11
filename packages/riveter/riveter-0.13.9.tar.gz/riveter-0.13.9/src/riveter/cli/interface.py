"""CLI interface protocols and base classes.

This module defines the core interfaces and protocols for the Riveter CLI system.
It provides the foundation for a pluggable command architecture while maintaining
complete backward compatibility.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from ..models.config import CLIArgs


@dataclass(frozen=True)
class CommandResult:
    """Result of command execution.

    Attributes:
        exit_code: Command exit code (0 for success)
        output: Command output message (optional)
        error: Error message if command failed (optional)
    """

    exit_code: int
    output: str | None = None
    error: str | None = None


@runtime_checkable
class CLIInterface(Protocol):
    """Protocol for CLI interface implementations."""

    def execute(self, args: list[str]) -> int:
        """Execute CLI with given arguments.

        Args:
            args: Command line arguments

        Returns:
            Exit code
        """
        ...


@runtime_checkable
class Command(Protocol):
    """Protocol for CLI command implementations."""

    def execute(self, args: CLIArgs) -> CommandResult:
        """Execute the command with given arguments.

        Args:
            args: Parsed CLI arguments

        Returns:
            Command execution result
        """
        ...


class BaseCommand(ABC):
    """Abstract base class for CLI commands.

    Provides common functionality and structure for all CLI commands
    while maintaining backward compatibility.
    """

    def __init__(self, name: str, description: str) -> None:
        """Initialize command.

        Args:
            name: Command name
            description: Command description
        """
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, args: CLIArgs) -> CommandResult:
        """Execute the command.

        Args:
            args: Parsed CLI arguments

        Returns:
            Command execution result
        """
        pass

    def validate_args(self, args: CLIArgs) -> list[str]:
        """Validate command arguments.

        Args:
            args: CLI arguments to validate

        Returns:
            List of validation errors (empty if valid)
        """
        return []


class CommandRouter:
    """Routes CLI commands to appropriate handlers with performance optimization.

    Provides a pluggable command system with lazy loading, performance monitoring,
    and extensibility while maintaining complete backward compatibility.
    """

    def __init__(self, use_registry: bool = True) -> None:
        """Initialize command router.

        Args:
            use_registry: Whether to use the advanced command registry
        """
        if use_registry:
            from .registry import get_global_registry

            self._registry = get_global_registry()
            self._use_registry = True
        else:
            # Fallback to simple command storage for compatibility
            self._commands: dict[str, Command] = {}
            self._aliases: dict[str, str] = {}
            self._use_registry = False

    def register_command(
        self, name: str, command: Command, aliases: list[str] | None = None
    ) -> None:
        """Register a command with the router.

        Args:
            name: Command name
            command: Command implementation
            aliases: Optional command aliases
        """
        if self._use_registry:
            # Register with the advanced registry
            self._registry.register_command(
                name, lambda: command, aliases=aliases  # Wrap in factory function
            )
        else:
            # Fallback to simple registration
            self._commands[name] = command

            if aliases:
                for alias in aliases:
                    self._aliases[alias] = name

    def get_command(self, name: str) -> Command | None:
        """Get command by name or alias.

        Args:
            name: Command name or alias

        Returns:
            Command implementation or None if not found
        """
        if self._use_registry:
            return self._registry.get_command(name)
        else:
            # Fallback to simple lookup
            if name in self._aliases:
                name = self._aliases[name]
            return self._commands.get(name)

    def list_commands(self) -> dict[str, Command] | list[str]:
        """List all registered commands.

        Returns:
            Dictionary of command name to command implementation or list of names
        """
        if self._use_registry:
            return self._registry.list_commands()
        else:
            return self._commands.copy()

    def route_command(self, command_name: str, args: CLIArgs) -> CommandResult:
        """Route command to appropriate handler with performance monitoring.

        Args:
            command_name: Name of command to execute
            args: Parsed CLI arguments

        Returns:
            Command execution result
        """
        if self._use_registry:
            # Use registry's optimized execution
            return self._registry.execute_command(command_name, args)
        else:
            # Fallback to simple execution
            command = self.get_command(command_name)

            if command is None:
                return CommandResult(exit_code=1, error=f"Unknown command: {command_name}")

            try:
                return command.execute(args)
            except Exception as e:
                return CommandResult(exit_code=1, error=f"Command execution failed: {e}")

    def preload_commands(self, command_names: list[str] | None = None) -> None:
        """Preload commands for better performance.

        Args:
            command_names: Optional list of commands to preload
        """
        if self._use_registry:
            self._registry.preload_commands(command_names)

    def enable_plugins(self) -> None:
        """Enable plugin discovery and loading."""
        if self._use_registry:
            from .registry import create_pluggable_system

            system = create_pluggable_system()
            system.discover_plugins()
