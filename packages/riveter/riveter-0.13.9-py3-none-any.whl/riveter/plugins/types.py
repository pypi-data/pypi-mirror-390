"""Type definitions for the plugin system."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..models.protocols import PluginInterface


class PluginStatus(Enum):
    """Status of a plugin."""

    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass(frozen=True)
class PluginMetadata:
    """Metadata about a plugin."""

    name: str
    version: str
    description: str
    author: str
    license: str
    homepage: Optional[str] = None
    repository: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    riveter_version: Optional[str] = None
    plugin_type: str = "generic"
    entry_points: Dict[str, str] = field(default_factory=dict)
    configuration_schema: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "homepage": self.homepage,
            "repository": self.repository,
            "keywords": self.keywords,
            "dependencies": self.dependencies,
            "riveter_version": self.riveter_version,
            "plugin_type": self.plugin_type,
            "entry_points": self.entry_points,
            "configuration_schema": self.configuration_schema,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """Create from dictionary representation."""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            license=data.get("license", ""),
            homepage=data.get("homepage"),
            repository=data.get("repository"),
            keywords=data.get("keywords", []),
            dependencies=data.get("dependencies", []),
            riveter_version=data.get("riveter_version"),
            plugin_type=data.get("plugin_type", "generic"),
            entry_points=data.get("entry_points", {}),
            configuration_schema=data.get("configuration_schema"),
        )


@dataclass
class PluginInfo:
    """Information about a discovered or loaded plugin."""

    metadata: PluginMetadata
    source_path: Path
    status: PluginStatus
    instance: Optional[PluginInterface] = None
    error_message: Optional[str] = None
    load_time: Optional[float] = None
    initialization_time: Optional[float] = None
    dependencies_resolved: bool = False
    configuration: Dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        """Get plugin name."""
        return self.metadata.name

    @property
    def version(self) -> str:
        """Get plugin version."""
        return self.metadata.version

    @property
    def is_loaded(self) -> bool:
        """Check if plugin is loaded."""
        return self.status in (PluginStatus.LOADED, PluginStatus.INITIALIZED)

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self.status == PluginStatus.INITIALIZED

    @property
    def has_error(self) -> bool:
        """Check if plugin has an error."""
        return self.status == PluginStatus.ERROR

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metadata": self.metadata.to_dict(),
            "source_path": str(self.source_path),
            "status": self.status.value,
            "error_message": self.error_message,
            "load_time": self.load_time,
            "initialization_time": self.initialization_time,
            "dependencies_resolved": self.dependencies_resolved,
            "configuration": self.configuration,
        }


@dataclass
class PluginDependency:
    """Represents a plugin dependency."""

    name: str
    version_spec: Optional[str] = None
    optional: bool = False

    def __str__(self) -> str:
        """String representation."""
        if self.version_spec:
            return f"{self.name}{self.version_spec}"
        return self.name

    @classmethod
    def parse(cls, spec: str) -> "PluginDependency":
        """Parse dependency specification string."""
        # Simple parsing - can be enhanced for complex version specs
        if ">=" in spec:
            name, version = spec.split(">=", 1)
            return cls(name.strip(), f">={version.strip()}")
        elif "==" in spec:
            name, version = spec.split("==", 1)
            return cls(name.strip(), f"=={version.strip()}")
        elif ">" in spec:
            name, version = spec.split(">", 1)
            return cls(name.strip(), f">{version.strip()}")
        else:
            return cls(spec.strip())


@dataclass
class PluginConfiguration:
    """Configuration for a plugin."""

    enabled: bool = True
    auto_load: bool = True
    priority: int = 0
    settings: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[PluginDependency] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "enabled": self.enabled,
            "auto_load": self.auto_load,
            "priority": self.priority,
            "settings": self.settings,
            "dependencies": [str(dep) for dep in self.dependencies],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginConfiguration":
        """Create from dictionary representation."""
        dependencies = [PluginDependency.parse(dep) for dep in data.get("dependencies", [])]
        return cls(
            enabled=data.get("enabled", True),
            auto_load=data.get("auto_load", True),
            priority=data.get("priority", 0),
            settings=data.get("settings", {}),
            dependencies=dependencies,
        )


@dataclass
class PluginLoadResult:
    """Result of plugin loading operation."""

    success: bool
    plugin_info: Optional[PluginInfo] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    load_time: Optional[float] = None

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


@dataclass
class PluginDiscoveryResult:
    """Result of plugin discovery operation."""

    discovered_plugins: List[PluginInfo]
    discovery_paths: List[Path]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    discovery_time: Optional[float] = None

    @property
    def plugin_count(self) -> int:
        """Get number of discovered plugins."""
        return len(self.discovered_plugins)

    @property
    def has_errors(self) -> bool:
        """Check if there are errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)

    def get_plugins_by_type(self, plugin_type: str) -> List[PluginInfo]:
        """Get plugins of a specific type."""
        return [
            plugin
            for plugin in self.discovered_plugins
            if plugin.metadata.plugin_type == plugin_type
        ]
