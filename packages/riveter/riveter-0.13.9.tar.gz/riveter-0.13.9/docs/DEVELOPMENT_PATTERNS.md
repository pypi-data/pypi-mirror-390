# Development Patterns and Best Practices

This document outlines the development patterns, best practices, and coding standards used in the modernized Riveter codebase.

## Core Design Principles

### 1. Protocol-Based Design

Use Python protocols to define interfaces, enabling type safety and extensibility.

#### Pattern
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class OutputFormatter(Protocol):
    """Protocol for output formatters."""

    def format(self, result: ValidationResult) -> str:
        """Format validation result.

        Args:
            result: Validation result to format

        Returns:
            Formatted string representation
        """
        ...

class JSONFormatter(OutputFormatter):
    """JSON output formatter implementation."""

    def format(self, result: ValidationResult) -> str:
        return json.dumps(result.to_dict(), indent=2)
```

#### Benefits
- Type safety with MyPy
- Clear interface contracts
- Easy testing with mocks
- Runtime type checking capability

### 2. Immutable Data Models

Use frozen dataclasses for all data models to ensure immutability and thread safety.

#### Pattern
```python
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class TerraformResource:
    """Immutable Terraform resource representation."""

    type: str
    name: str
    attributes: dict[str, Any]
    source_location: SourceLocation | None = None

    @property
    def id(self) -> str:
        """Get resource identifier."""
        return f"{self.type}.{self.name}"

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get attribute with optional default."""
        return self.attributes.get(key, default)
```

#### Benefits
- Thread safety
- Prevents accidental mutations
- Clear data contracts
- Better debugging and testing

### 3. Dependency Injection

Use constructor injection to provide dependencies, enabling testability and flexibility.

#### Pattern
```python
class ValidationEngine:
    """Validation engine with dependency injection."""

    def __init__(
        self,
        evaluator: RuleEvaluatorProtocol | None = None,
        cache_provider: CacheProviderProtocol | None = None,
        performance_monitor: PerformanceMonitorProtocol | None = None,
        config: ValidationEngineConfig | None = None,
    ) -> None:
        """Initialize validation engine.

        Args:
            evaluator: Rule evaluator implementation
            cache_provider: Cache provider implementation
            performance_monitor: Performance monitor implementation
            config: Engine configuration
        """
        self._evaluator = evaluator or DefaultRuleEvaluator()
        self._cache_provider = cache_provider
        self._performance_monitor = performance_monitor
        self._config = config or ValidationEngineConfig()
```

#### Benefits
- Easy testing with mocks
- Flexible configuration
- Clear dependencies
- Supports different implementations

### 4. Type Safety

Use comprehensive type annotations throughout the codebase.

#### Pattern
```python
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

def load_configuration(
    file_path: Path,
    cache_enabled: bool = True,
    timeout: Optional[int] = None
) -> TerraformConfig:
    """Load Terraform configuration from file.

    Args:
        file_path: Path to Terraform file
        cache_enabled: Whether to use caching
        timeout: Optional timeout in seconds

    Returns:
        Parsed Terraform configuration

    Raises:
        ConfigurationError: If file cannot be parsed
        FileNotFoundError: If file does not exist
    """
    # Implementation with type safety
    pass
```

#### Benefits
- Compile-time error detection
- Better IDE support
- Self-documenting code
- Easier refactoring

## Architectural Patterns

### 1. Layered Architecture

Organize code into clear layers with defined responsibilities.

```
Application Layer (CLI)
    ↓
Service Layer (Business Logic)
    ↓
Infrastructure Layer (I/O, Caching, etc.)
    ↓
Data Layer (Models, Protocols)
```

#### Implementation
```python
# Application Layer
class CLIInterface:
    def __init__(self, command_router: CommandRouter):
        self._router = command_router

# Service Layer
class ValidationService:
    def __init__(self, engine: ValidationEngine, config_manager: ConfigurationManager):
        self._engine = engine
        self._config_manager = config_manager

# Infrastructure Layer
class FileSystemConfigurationParser:
    def parse(self, file_path: Path) -> TerraformConfig:
        # File I/O operations
        pass

# Data Layer
@dataclass(frozen=True)
class ValidationResult:
    # Data model definition
    pass
```

### 2. Registry Pattern

Use registries for managing pluggable components.

#### Pattern
```python
class ComponentRegistry:
    """Registry for managing pluggable components."""

    def __init__(self) -> None:
        self._components: dict[str, Callable[[], Any]] = {}
        self._loaded_components: dict[str, Any] = {}

    def register(self, name: str, factory: Callable[[], Any]) -> None:
        """Register component factory."""
        self._components[name] = factory

    def get(self, name: str) -> Any:
        """Get component instance (lazy loading)."""
        if name not in self._loaded_components:
            if name not in self._components:
                raise ValueError(f"Unknown component: {name}")
            self._loaded_components[name] = self._components[name]()
        return self._loaded_components[name]

    def list_components(self) -> list[str]:
        """List all registered component names."""
        return list(self._components.keys())
```

### 3. Factory Pattern

Use factories for creating complex objects with dependencies.

#### Pattern
```python
class ValidationEngineFactory:
    """Factory for creating validation engines."""

    @staticmethod
    def create_default() -> ValidationEngine:
        """Create validation engine with default configuration."""
        return ValidationEngine(
            evaluator=DefaultRuleEvaluator(),
            cache_provider=MemoryCache(),
            config=ValidationEngineConfig()
        )

    @staticmethod
    def create_performance_optimized() -> ValidationEngine:
        """Create performance-optimized validation engine."""
        return ValidationEngine(
            evaluator=OptimizedRuleEvaluator(),
            cache_provider=RedisCache(),
            performance_monitor=DetailedPerformanceMonitor(),
            config=ValidationEngineConfig(
                parallel_enabled=True,
                cache_enabled=True,
                max_workers=8
            )
        )
```

## Error Handling Patterns

### 1. Structured Exception Hierarchy

Create a clear exception hierarchy with context information.

#### Pattern
```python
class RiveterError(Exception):
    """Base exception for all Riveter errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}

class ValidationError(RiveterError):
    """Errors during validation process."""

    def __init__(
        self,
        message: str,
        rule_id: str | None = None,
        resource_id: str | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, context)
        self.rule_id = rule_id
        self.resource_id = resource_id

class ConfigurationError(RiveterError):
    """Errors related to configuration parsing."""

    def __init__(
        self,
        message: str,
        file_path: Path | None = None,
        line_number: int | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, context)
        self.file_path = file_path
        self.line_number = line_number
```

### 2. Error Recovery Patterns

Implement graceful error handling with recovery strategies.

#### Pattern
```python
class ValidationEngine:
    def validate_resources(
        self, rules: list[Rule], resources: list[TerraformResource]
    ) -> ValidationResult:
        """Validate resources with error recovery."""
        results: list[RuleResult] = []
        errors: list[ValidationError] = []

        for rule in rules:
            for resource in resources:
                try:
                    result = self._evaluate_rule(rule, resource)
                    results.append(result)
                except ValidationError as e:
                    # Log error but continue processing
                    self._logger.error(f"Rule evaluation failed: {e}", exc_info=True)
                    errors.append(e)

                    if not self._config.continue_on_error:
                        raise

                    # Create error result
                    error_result = RuleResult(
                        rule_id=rule.id,
                        resource=resource,
                        passed=False,
                        message=f"Evaluation error: {e}",
                        severity=Severity.ERROR,
                        details={"error": str(e), "exception_type": type(e).__name__}
                    )
                    results.append(error_result)

        return ValidationResult(
            summary=self._create_summary(results),
            results=results,
            metadata={"errors": [str(e) for e in errors]}
        )
```

## Performance Patterns

### 1. Lazy Loading

Load components only when needed to improve startup time.

#### Pattern
```python
class LazyComponentLoader:
    """Lazy loading component manager."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], Any]] = {}
        self._instances: dict[str, Any] = {}

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Register component factory."""
        self._factories[name] = factory

    def get_component(self, name: str) -> Any:
        """Get component instance (lazy loading)."""
        if name not in self._instances:
            if name not in self._factories:
                raise ValueError(f"Unknown component: {name}")

            # Load component on first access
            self._instances[name] = self._factories[name]()

        return self._instances[name]
```

### 2. Caching Patterns

Implement intelligent caching for expensive operations.

#### Pattern
```python
class CachedConfigurationManager:
    """Configuration manager with intelligent caching."""

    def __init__(self, cache_provider: CacheProvider, ttl: int = 300) -> None:
        self._cache = cache_provider
        self._ttl = ttl
        self._parser = TerraformParser()

    def load_terraform_config(self, file_path: Path) -> TerraformConfig:
        """Load configuration with caching."""
        # Generate cache key based on file path and modification time
        stat = file_path.stat()
        cache_key = f"config:{file_path}:{stat.st_mtime}:{stat.st_size}"

        # Try cache first
        cached_config = self._cache.get(cache_key)
        if cached_config:
            return cached_config

        # Parse and cache
        config = self._parser.parse(file_path)
        self._cache.set(cache_key, config, ttl=self._ttl)

        return config
```

### 3. Parallel Processing

Use parallel processing for CPU-intensive operations.

#### Pattern
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, TypeVar

T = TypeVar('T')
R = TypeVar('R')

class ParallelProcessor:
    """Parallel processing utility."""

    def __init__(self, max_workers: int | None = None) -> None:
        self._max_workers = max_workers

    def process_batch(
        self,
        items: list[T],
        processor_func: Callable[[T], R],
        batch_size: int = 100
    ) -> list[R]:
        """Process items in parallel batches."""
        results: list[R] = []

        # Split into batches
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            # Submit batch processing tasks
            futures = [
                executor.submit(self._process_batch_items, batch, processor_func)
                for batch in batches
            ]

            # Collect results
            for future in as_completed(futures):
                batch_results = future.result()
                results.extend(batch_results)

        return results

    def _process_batch_items(
        self, items: list[T], processor_func: Callable[[T], R]
    ) -> list[R]:
        """Process a single batch of items."""
        return [processor_func(item) for item in items]
```

## Testing Patterns

### 1. Test Structure Organization

Organize tests by component and test type.

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── cli/
│   ├── models/
│   ├── validation/
│   └── output/
├── integration/             # Integration tests (slower, multiple components)
│   ├── cli_integration/
│   └── component_integration/
├── performance/             # Performance tests
│   ├── cli_benchmarks/
│   └── component_benchmarks/
├── property/               # Property-based tests
│   └── rule_validation/
└── fixtures/               # Test data and utilities
    ├── terraform/
    ├── rules/
    └── expected_outputs/
```

### 2. Test Fixture Patterns

Create reusable test fixtures with proper typing.

#### Pattern
```python
import pytest
from pathlib import Path
from typing import Generator

@pytest.fixture
def sample_terraform_resource() -> TerraformResource:
    """Create sample Terraform resource for testing."""
    return TerraformResource(
        type="aws_instance",
        name="web",
        attributes={
            "instance_type": "t3.large",
            "tags": {"Environment": "production", "Team": "platform"}
        },
        source_location=SourceLocation(Path("main.tf"), 10)
    )

@pytest.fixture
def validation_engine() -> ValidationEngine:
    """Create validation engine for testing."""
    return ValidationEngine(
        evaluator=DefaultRuleEvaluator(),
        config=ValidationEngineConfig(cache_enabled=False)  # Disable cache for tests
    )

@pytest.fixture
def temp_terraform_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create temporary Terraform file for testing."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text('''
    resource "aws_instance" "web" {
      instance_type = "t3.large"
      tags = {
        Environment = "production"
      }
    }
    ''')
    yield tf_file
    # Cleanup handled by tmp_path fixture
```

### 3. Mock and Stub Patterns

Use proper mocking for external dependencies.

#### Pattern
```python
from unittest.mock import Mock, patch
import pytest

class TestValidationEngine:
    def test_validation_with_cache_hit(self):
        """Test validation with cache hit."""
        # Create mock cache provider
        mock_cache = Mock(spec=CacheProvider)
        mock_cache.get.return_value = RuleResult(
            rule_id="test-rule",
            resource=sample_resource,
            passed=True,
            message="Cached result",
            severity=Severity.INFO
        )

        # Create engine with mock cache
        engine = ValidationEngine(cache_provider=mock_cache)

        # Execute validation
        result = engine.validate_resources([sample_rule], [sample_resource])

        # Verify cache was used
        mock_cache.get.assert_called_once()
        assert result.summary.passed == 1

    @patch('riveter.configuration.parser.hcl2.load')
    def test_configuration_parsing_error(self, mock_hcl_load):
        """Test configuration parsing error handling."""
        # Setup mock to raise exception
        mock_hcl_load.side_effect = ValueError("Invalid HCL syntax")

        parser = TerraformParser()

        with pytest.raises(ConfigurationError) as exc_info:
            parser.parse(Path("invalid.tf"))

        assert "Invalid HCL syntax" in str(exc_info.value)
```

### 4. Property-Based Testing

Use property-based testing for complex validation logic.

#### Pattern
```python
from hypothesis import given, strategies as st
import pytest

class TestRuleValidation:
    @given(
        instance_type=st.sampled_from(["t3.micro", "t3.small", "t3.medium", "t3.large"]),
        environment=st.sampled_from(["dev", "staging", "production"]),
        tags=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.text(min_size=1, max_size=50),
            min_size=0,
            max_size=10
        )
    )
    def test_resource_validation_properties(
        self, instance_type: str, environment: str, tags: dict[str, str]
    ):
        """Test resource validation with generated data."""
        # Add required tags
        tags["Environment"] = environment

        resource = TerraformResource(
            type="aws_instance",
            name="test",
            attributes={"instance_type": instance_type, "tags": tags}
        )

        rule = Rule(
            id="test-rule",
            resource_type="aws_instance",
            description="Test rule",
            severity=Severity.ERROR,
            conditions=[
                Condition(field="tags.Environment", operator="present", value=None)
            ]
        )

        evaluator = DefaultRuleEvaluator()
        result = evaluator.evaluate_rule(rule, resource)

        # Property: Resources with Environment tag should always pass
        assert result.passed
        assert result.rule_id == "test-rule"
        assert result.resource == resource
```

## Documentation Patterns

### 1. Docstring Standards

Use Google-style docstrings with comprehensive type information.

#### Pattern
```python
def validate_terraform_configuration(
    config_path: Path,
    rule_packs: list[str],
    output_format: str = "table",
    cache_enabled: bool = True
) -> ValidationResult:
    """Validate Terraform configuration against rule packs.

    This function loads the specified Terraform configuration, applies
    the given rule packs, and returns a comprehensive validation result.

    Args:
        config_path: Path to the Terraform configuration file
        rule_packs: List of rule pack names to apply
        output_format: Output format for results (table, json, sarif, junit)
        cache_enabled: Whether to enable result caching for performance

    Returns:
        ValidationResult containing summary, individual results, and metadata

    Raises:
        ConfigurationError: If the Terraform file cannot be parsed
        RulePackError: If any rule pack cannot be loaded
        ValidationError: If validation process fails

    Example:
        >>> result = validate_terraform_configuration(
        ...     Path("main.tf"),
        ...     ["aws-security", "cis-aws"],
        ...     output_format="json"
        ... )
        >>> print(f"Passed: {result.summary.passed}, Failed: {result.summary.failed}")
        Passed: 15, Failed: 2

    Note:
        This function uses caching by default to improve performance on
        repeated validations of the same configuration.
    """
    # Implementation
    pass
```

### 2. Code Comments

Use clear, concise comments that explain the "why" not the "what".

#### Pattern
```python
class ValidationEngine:
    def _evaluate_parallel_optimized(
        self, evaluation_pairs: list[tuple[Rule, TerraformResource]]
    ) -> list[RuleResult]:
        """Evaluate rules in parallel with performance optimizations."""

        # Use parallel processing only for large datasets to avoid overhead
        # Threshold determined through benchmarking (see performance tests)
        if len(evaluation_pairs) < self._config.batch_size:
            return self._evaluate_sequential(evaluation_pairs)

        # Partition work by resource type for better cache locality
        # Resources of the same type often share similar attributes
        partitions = self._partition_by_resource_type(evaluation_pairs)

        # Process partitions in parallel, maintaining result order
        return self._parallel_processor.process_batch(
            items=partitions,
            processor_func=self._evaluate_partition,
            batch_size=self._config.batch_size
        )
```

## Configuration Patterns

### 1. Configuration Classes

Use dataclasses for configuration with validation.

#### Pattern
```python
@dataclass
class ValidationEngineConfig:
    """Configuration for the validation engine."""

    # Performance settings
    parallel_enabled: bool = True
    max_workers: int | None = None
    batch_size: int = 100

    # Caching settings
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes

    # Filtering settings
    min_severity: Severity = Severity.INFO
    include_skipped: bool = False
    fail_fast: bool = False

    # Error handling settings
    continue_on_error: bool = True
    max_errors: int | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")

        if self.cache_ttl < 0:
            raise ValueError("cache_ttl must be non-negative")

        if self.max_workers is not None and self.max_workers <= 0:
            raise ValueError("max_workers must be positive")
```

### 2. Environment-Based Configuration

Support configuration through environment variables.

#### Pattern
```python
import os
from typing import Any

class ConfigurationLoader:
    """Load configuration from multiple sources."""

    @staticmethod
    def load_from_environment() -> ValidationEngineConfig:
        """Load configuration from environment variables."""
        return ValidationEngineConfig(
            parallel_enabled=_get_bool_env("RIVETER_PARALLEL_ENABLED", True),
            max_workers=_get_int_env("RIVETER_MAX_WORKERS", None),
            batch_size=_get_int_env("RIVETER_BATCH_SIZE", 100),
            cache_enabled=_get_bool_env("RIVETER_CACHE_ENABLED", True),
            cache_ttl=_get_int_env("RIVETER_CACHE_TTL", 300),
            min_severity=_get_severity_env("RIVETER_MIN_SEVERITY", Severity.INFO),
            continue_on_error=_get_bool_env("RIVETER_CONTINUE_ON_ERROR", True),
        )

def _get_bool_env(key: str, default: bool) -> bool:
    """Get boolean environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")

def _get_int_env(key: str, default: int | None) -> int | None:
    """Get integer environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _get_severity_env(key: str, default: Severity) -> Severity:
    """Get severity environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return Severity(value.lower())
    except ValueError:
        return default
```

These patterns provide a solid foundation for developing high-quality, maintainable code in the modernized Riveter architecture while ensuring consistency, performance, and extensibility.
