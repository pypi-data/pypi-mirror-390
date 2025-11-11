"""Plugin system for Riveter.

This package provides a comprehensive plugin architecture that allows
extending Riveter with custom rules, parsers, formatters, and other
functionality while maintaining backward compatibility.
"""

from .discovery import PluginDiscovery, PluginRegistry
from .loader import PluginLoader, PluginLoadError
from .manager import PluginManager
from .registry import DefaultPluginRegistry
from .types import PluginInfo, PluginMetadata, PluginStatus

__all__ = [
    "DefaultPluginRegistry",
    "PluginDiscovery",
    "PluginInfo",
    "PluginLoadError",
    "PluginLoader",
    "PluginManager",
    "PluginMetadata",
    "PluginRegistry",
    "PluginStatus",
]
