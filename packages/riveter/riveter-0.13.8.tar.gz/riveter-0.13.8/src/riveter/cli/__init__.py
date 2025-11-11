"""Modern CLI interface package.

This package provides a modernized CLI interface for Riveter while maintaining
100% backward compatibility with existing commands and behavior.

Features:
- Command routing with lazy loading
- Performance monitoring and optimization
- Pluggable command system
- Advanced caching and profiling
"""

from .interface import BaseCommand, CLIInterface, Command, CommandResult, CommandRouter
from .performance import get_performance_stats, performance_monitor, report_performance
from .registry import CommandRegistry, PluggableCommandSystem, get_global_registry

__all__ = [
    "BaseCommand",
    "CLIInterface",
    "Command",
    "CommandResult",
    "CommandRouter",
    "CommandRegistry",
    "PluggableCommandSystem",
    "performance_monitor",
    "get_performance_stats",
    "report_performance",
    "get_global_registry",
]
