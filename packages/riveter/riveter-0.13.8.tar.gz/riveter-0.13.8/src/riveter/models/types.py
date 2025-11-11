"""Type definitions and type aliases for Riveter.

This module provides common type aliases and utility types used
throughout the Riveter codebase.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any, Generic, TypeVar

# Basic type aliases
JSON = dict[str, Any] | list[Any] | str | int | float | bool | None
JSONDict = dict[str, Any]
JSONList = list[Any]

# Path-related types
PathLike = str | Path
OptionalPath = Path | None

# Configuration types
ResourceDict = dict[str, Any]
RuleDict = dict[str, Any]
ConfigDict = dict[str, Any]
AttributeValue = str | int | float | bool | list[Any] | dict[str, Any]

# Generic types
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# Result types
class Result(Generic[T]):
    """Generic result type for operations that can succeed or fail."""

    def __init__(self, value: T | None = None, error: str | None = None) -> None:
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        """Check if result represents success."""
        return self._error is None

    @property
    def is_error(self) -> bool:
        """Check if result represents an error."""
        return self._error is not None

    @property
    def value(self) -> T:
        """Get the success value."""
        if self.is_error:
            raise ValueError(f"Cannot get value from error result: {self._error}")
        return self._value

    @property
    def error(self) -> str:
        """Get the error message."""
        if self.is_success:
            raise ValueError("Cannot get error from success result")
        return self._error

    def map(self, func: Callable[[T], "Result[Any]"]) -> "Result[Any]":
        """Map the success value through a function."""
        if self.is_error:
            return Result(error=self._error)
        return func(self._value)

    def map_error(self, func: Callable[[str], str]) -> "Result[T]":
        """Map the error message through a function."""
        if self.is_success:
            return self
        return Result(error=func(self._error))

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        """Create a success result."""
        return cls(value=value)

    @classmethod
    def from_error(cls, error: str) -> "Result[T]":
        """Create an error result."""
        return cls(error=error)


# Validation types
ValidationFunction = Callable[[Any], bool]
FilterFunction = Callable[[Any], bool]
TransformFunction = Callable[[Any], Any]

# Plugin types
PluginInitializer = Callable[[ConfigDict], None]
PluginCleanup = Callable[[], None]

# Event types
EventHandler = Callable[[str, dict[str, Any]], None]
EventFilter = Callable[[str, dict[str, Any]], bool]

# Cache types
CacheKey = str
CacheValue = Any
CacheTTL = int | None

# Performance types
TimingFunction = Callable[[], float]
MemoryFunction = Callable[[], int]

# Logging types
LogLevel = str
LogMessage = str
LogContext = dict[str, Any]

# CLI types
CommandName = str
CommandArgs = list[str]
CommandResult = int
CommandHandler = Callable[[CommandArgs], CommandResult]

# File processing types
FileProcessor = Callable[[Path], Result[Any]]
DirectoryProcessor = Callable[[Path], Result[list[Any]]]


# Utility type guards
def is_dict(value: Any) -> bool:
    """Check if value is a dictionary."""
    return isinstance(value, dict)


def is_list(value: Any) -> bool:
    """Check if value is a list."""
    return isinstance(value, list)


def is_string(value: Any) -> bool:
    """Check if value is a string."""
    return isinstance(value, str)


def is_path_like(value: Any) -> bool:
    """Check if value is path-like."""
    return isinstance(value, str | Path)


def is_json_serializable(value: Any) -> bool:
    """Check if value is JSON serializable."""
    try:
        import json

        json.dumps(value)
    except (TypeError, ValueError):
        return False
    else:
        return True


# Type conversion utilities
def to_path(value: PathLike) -> Path:
    """Convert path-like value to Path object."""
    return Path(value) if not isinstance(value, Path) else value


def to_optional_path(value: PathLike | None) -> OptionalPath:
    """Convert optional path-like value to optional Path object."""
    return to_path(value) if value is not None else None


def to_string_list(value: str | list[str]) -> list[str]:
    """Convert string or list of strings to list of strings."""
    if isinstance(value, str):
        return [value]
    return value if isinstance(value, list) else []


def to_dict(value: Any) -> dict[str, Any]:
    """Convert value to dictionary if possible."""
    if isinstance(value, dict):
        return value
    if hasattr(value, "__dict__"):
        return value.__dict__
    if hasattr(value, "to_dict"):
        return value.to_dict()
    raise TypeError(f"Cannot convert {type(value)} to dict")


# Validation utilities
def validate_non_empty_string(value: Any, name: str) -> str:
    """Validate that value is a non-empty string."""
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string, got {type(value)}")
    if not value.strip():
        raise ValueError(f"{name} cannot be empty")
    return value.strip()


def validate_positive_int(value: Any, name: str) -> int:
    """Validate that value is a positive integer."""
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer, got {type(value)}")
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def validate_path_exists(value: PathLike, name: str) -> Path:
    """Validate that path exists."""
    path = to_path(value)
    if not path.exists():
        raise FileNotFoundError(f"{name} does not exist: {path}")
    return path


def validate_file_exists(value: PathLike, name: str) -> Path:
    """Validate that file exists."""
    path = validate_path_exists(value, name)
    if not path.is_file():
        raise ValueError(f"{name} is not a file: {path}")
    return path


def validate_directory_exists(value: PathLike, name: str) -> Path:
    """Validate that directory exists."""
    path = validate_path_exists(value, name)
    if not path.is_dir():
        raise ValueError(f"{name} is not a directory: {path}")
    return path
