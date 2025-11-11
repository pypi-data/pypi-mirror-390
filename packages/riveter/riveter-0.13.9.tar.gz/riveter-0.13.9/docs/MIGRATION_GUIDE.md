# Migration Guide for Contributors

This guide helps existing contributors understand the changes made during the Riveter modernization and how to work with the new architecture.

## Overview of Changes

The Riveter codebase has undergone a comprehensive modernization while maintaining 100% backward compatibility for users. This guide covers the key changes that affect contributors and developers.

## What Changed

### 1. Architecture Modernization

#### Before (Legacy Architecture)
```
src/riveter/
├── __init__.py
├── cli.py                  # Monolithic CLI
├── extract_config.py       # Basic config parsing
├── rules.py               # Simple rule loading
├── scanner.py             # Basic validation
├── reporter.py            # Simple reporting
└── ...                    # Various utility modules
```

#### After (Modernized Architecture)
```
src/riveter/
├── cli/                   # Modular CLI system
│   ├── interface.py       # Protocol definitions
│   ├── commands.py        # Command implementations
│   ├── registry.py        # Command registry
│   └── performance.py     # Performance optimizations
├── models/                # Immutable data models
│   ├── core.py           # Core data structures
│   ├── rules.py          # Rule models
│   └── protocols.py      # Protocol definitions
├── validation/            # Advanced validation engine
│   ├── engine.py         # Main validation engine
│   ├── evaluator.py      # Rule evaluation
│   └── cache.py          # Result caching
├── configuration/         # Configuration management
├── output/               # Output system
├── plugins/              # Plugin system
├── cache/                # Caching system
└── parallel/             # Parallel processing
```

### 2. Type Safety Implementation

#### Before
```python
def validate_resources(rules, resources):
    """Validate resources against rules."""
    results = []
    # Implementation without type hints
    return results
```

#### After
```python
def validate_resources(
    self, rules: list[Rule], resources: list[TerraformResource]
) -> ValidationResult:
    """Validate resources against rules.

    Args:
        rules: List of rules to apply
        resources: List of resources to validate

    Returns:
        ValidationResult containing all evaluation outcomes
    """
    # Implementation with complete type safety
    return ValidationResult(...)
```

### 3. Data Model Evolution

#### Before (Mutable Dictionaries)
```python
# Resources were simple dictionaries
resource = {
    "type": "aws_instance",
    "name": "web",
    "attributes": {"instance_type": "t3.large"}
}

# Results were basic objects
class DriftResult:
    def __init__(self, rule, resource, passed, message):
        self.rule = rule
        self.resource = resource
        self.passed = passed
        self.message = message
```

#### After (Immutable Data Classes)
```python
@dataclass(frozen=True)
class TerraformResource:
    """Immutable Terraform resource representation."""
    type: str
    name: str
    attributes: dict[str, Any]
    source_location: SourceLocation | None = None

    @property
    def id(self) -> str:
        return f"{self.type}.{self.name}"

@dataclass(frozen=True)
class RuleResult:
    """Immutable rule evaluation result."""
    rule_id: str
    resource: TerraformResource
    passed: bool
    message: str
    severity: Severity
    details: dict[str, Any] = field(default_factory=dict)
```

### 4. Protocol-Based Design

#### Before (Concrete Classes)
```python
class Reporter:
    def report_results(self, results):
        # Fixed implementation
        pass
```

#### After (Protocol-Based)
```python
class OutputFormatter(Protocol):
    """Protocol for output formatters."""
    def format(self, result: ValidationResult) -> str: ...

class TableFormatter(OutputFormatter):
    """Table output formatter implementation."""
    def format(self, result: ValidationResult) -> str:
        # Implementation
        pass
```

### 5. Dependency Injection

#### Before (Hard-coded Dependencies)
```python
class Scanner:
    def __init__(self):
        self.evaluator = DefaultEvaluator()  # Hard-coded
        self.cache = None  # No caching
```

#### After (Dependency Injection)
```python
class ValidationEngine:
    def __init__(
        self,
        evaluator: RuleEvaluatorProtocol | None = None,
        cache_provider: CacheProviderProtocol | None = None,
        performance_monitor: PerformanceMonitorProtocol | None = None,
        config: ValidationEngineConfig | None = None,
    ):
        self._evaluator = evaluator or DefaultRuleEvaluator()
        self._cache_provider = cache_provider
        self._performance_monitor = performance_monitor
        self._config = config or ValidationEngineConfig()
```

## Migration Patterns

### 1. Working with New Data Models

#### Accessing Resource Properties

**Before:**
```python
# Direct dictionary access
resource_type = resource["resource_type"]
instance_type = resource.get("instance_type", "unknown")
tags = resource.get("tags", {})
```

**After:**
```python
# Type-safe property access
resource_type = resource.type
instance_type = resource.get_attribute("instance_type", "unknown")
tags = resource.tags
```

#### Creating Test Data

**Before:**
```python
def create_test_resource():
    return {
        "resource_type": "aws_instance",
        "id": "web",
        "instance_type": "t3.large"
    }
```

**After:**
```python
def create_test_resource() -> TerraformResource:
    return TerraformResource(
        type="aws_instance",
        name="web",
        attributes={"instance_type": "t3.large"},
        source_location=SourceLocation(Path("test.tf"), 1)
    )
```

### 2. Working with Validation Results

#### Processing Results

**Before:**
```python
def process_results(results):
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    return len(passed), len(failed)
```

**After:**
```python
def process_results(result: ValidationResult) -> tuple[int, int]:
    return result.summary.passed, result.summary.failed

# Or use built-in properties
passed_results = result.passed_results
failed_results = result.failed_results
```

### 3. Extending Functionality

#### Adding New Commands

**Before:**
```python
# Add to cli.py directly
@click.command()
def my_command():
    pass

# Register in main CLI group
cli.add_command(my_command)
```

**After:**
```python
# Create command class
class MyCommand(BaseCommand):
    def __init__(self):
        super().__init__("my-command", "My custom command")

    def execute(self, args: CLIArgs) -> CommandResult:
        return CommandResult(exit_code=0, output="Success")

# Register with registry
registry = get_global_registry()
registry.register_command("my-command", lambda: MyCommand())
```

#### Adding New Output Formats

**Before:**
```python
# Modify reporter.py directly
def format_xml(results):
    # XML formatting logic
    pass

# Add to format mapping
FORMATTERS = {
    "table": format_table,
    "json": format_json,
    "xml": format_xml,  # Add here
}
```

**After:**
```python
# Create formatter class
class XMLFormatter(OutputFormatter):
    def format(self, result: ValidationResult) -> str:
        # XML formatting logic
        pass

# Register formatter
output_manager.register_formatter("xml", XMLFormatter())
```

### 4. Testing Patterns

#### Unit Test Structure

**Before:**
```python
def test_validation():
    rules = [{"id": "test", "resource_type": "aws_instance"}]
    resources = [{"resource_type": "aws_instance", "id": "test"}]

    results = validate_resources(rules, resources)

    assert len(results) == 1
    assert results[0].passed
```

**After:**
```python
def test_validation():
    rule = Rule(
        id="test",
        resource_type="aws_instance",
        description="Test rule",
        severity=Severity.ERROR,
        conditions=[Condition(field="instance_type", operator="eq", value="t3.large")]
    )

    resource = TerraformResource(
        type="aws_instance",
        name="test",
        attributes={"instance_type": "t3.large"}
    )

    engine = ValidationEngine()
    result = engine.validate_resources([rule], [resource])

    assert result.summary.total_results == 1
    assert result.summary.passed == 1
```

#### Mock and Fixture Patterns

**Before:**
```python
@pytest.fixture
def sample_config():
    return {
        "resources": [
            {"resource_type": "aws_instance", "id": "test"}
        ]
    }
```

**After:**
```python
@pytest.fixture
def sample_config() -> TerraformConfig:
    resource = TerraformResource(
        type="aws_instance",
        name="test",
        attributes={"instance_type": "t3.large"}
    )

    return TerraformConfig(
        resources=[resource],
        variables={},
        outputs={},
        source_file=Path("test.tf")
    )
```

## Development Workflow Changes

### 1. Code Quality Tools

#### Before
- Basic linting with flake8
- Manual code formatting
- Optional type checking

#### After
- Comprehensive quality pipeline with `make` commands
- Automated formatting with Black and isort
- Strict type checking with MyPy
- Advanced linting with Ruff
- Pre-commit hooks for quality gates

**New Commands:**
```bash
# Format code
make format

# Check code quality
make lint

# Type checking
make type-check

# Quick quality check
make quick-check

# Complete pipeline
make all
```

### 2. Testing Framework

#### Before
```bash
# Basic pytest
pytest tests/

# Manual coverage
pytest --cov=src/riveter
```

#### After
```bash
# Comprehensive testing
make test              # Tests with coverage
make test-fast         # Tests without coverage
make test-cov          # Detailed coverage report

# Performance testing
pytest tests/performance/

# Property-based testing
pytest tests/property/
```

### 3. Configuration Management

#### Before
- Multiple configuration files (setup.py, requirements.txt, etc.)
- Scattered tool configurations

#### After
- Centralized configuration in `pyproject.toml`
- All tool configurations in one place
- Modern Python packaging standards

## Breaking Changes for Contributors

### 1. Import Changes

**Before:**
```python
from riveter.scanner import scan_resources
from riveter.rules import load_rules
from riveter.reporter import report_results
```

**After:**
```python
from riveter.validation.engine import ValidationEngine
from riveter.models.rules import Rule
from riveter.output.manager import OutputManager
```

### 2. API Changes

#### Validation API

**Before:**
```python
def scan_resources(rules, resources):
    # Returns list of DriftResult
    pass
```

**After:**
```python
class ValidationEngine:
    def validate_resources(
        self, rules: list[Rule], resources: list[TerraformResource]
    ) -> ValidationResult:
        # Returns structured ValidationResult
        pass
```

#### Configuration API

**Before:**
```python
def extract_terraform_config(file_path):
    # Returns dictionary
    pass
```

**After:**
```python
class ConfigurationManager:
    def load_terraform_config(self, path: Path) -> TerraformConfig:
        # Returns immutable TerraformConfig
        pass
```

### 3. Test Structure Changes

**Before:**
```
tests/
├── test_cli.py
├── test_rules.py
├── test_scanner.py
└── fixtures/
```

**After:**
```
tests/
├── unit/                    # Unit tests by component
│   ├── cli/
│   ├── models/
│   ├── validation/
│   └── output/
├── integration/             # Integration tests
├── performance/             # Performance tests
├── property/               # Property-based tests
└── fixtures/               # Test data
```

## Migration Checklist

### For Existing Contributors

- [ ] **Update Development Environment**
  - [ ] Recreate virtual environment
  - [ ] Run `make dev-setup`
  - [ ] Verify with `make quick-check`

- [ ] **Update Import Statements**
  - [ ] Replace old imports with new module structure
  - [ ] Update test imports

- [ ] **Update Code Patterns**
  - [ ] Use new data models instead of dictionaries
  - [ ] Apply type hints to all functions
  - [ ] Use protocol-based interfaces

- [ ] **Update Tests**
  - [ ] Migrate to new test structure
  - [ ] Use new data models in test fixtures
  - [ ] Add type annotations to test functions

- [ ] **Update Documentation**
  - [ ] Review and update any custom documentation
  - [ ] Update code examples in comments

### For New Features

- [ ] **Follow New Patterns**
  - [ ] Use protocol-based design
  - [ ] Implement dependency injection
  - [ ] Create immutable data models
  - [ ] Add comprehensive type hints

- [ ] **Testing Requirements**
  - [ ] Write unit tests for individual components
  - [ ] Add integration tests for component interactions
  - [ ] Include performance tests if applicable
  - [ ] Use property-based testing for complex logic

- [ ] **Quality Standards**
  - [ ] Pass all quality checks (`make all`)
  - [ ] Maintain or improve test coverage
  - [ ] Follow architectural patterns
  - [ ] Update documentation

## Common Migration Issues

### 1. Type Errors

**Issue:** MyPy type checking failures
```
error: Argument 1 to "validate_resources" has incompatible type "Dict[str, Any]"; expected "TerraformResource"
```

**Solution:** Update to use proper data models
```python
# Before
resource = {"type": "aws_instance", "name": "web"}

# After
resource = TerraformResource(type="aws_instance", name="web", attributes={})
```

### 2. Import Errors

**Issue:** Module not found errors
```
ImportError: cannot import name 'scan_resources' from 'riveter.scanner'
```

**Solution:** Update imports to new structure
```python
# Before
from riveter.scanner import scan_resources

# After
from riveter.validation.engine import ValidationEngine
engine = ValidationEngine()
result = engine.validate_resources(rules, resources)
```

### 3. Test Failures

**Issue:** Tests failing due to changed return types
```
AttributeError: 'ValidationResult' object has no attribute 'passed'
```

**Solution:** Update test expectations
```python
# Before
assert result.passed

# After
assert result.summary.passed > 0
# or
assert len(result.passed_results) > 0
```

## Getting Help

### Resources

1. **Architecture Documentation**: [MODERNIZED_ARCHITECTURE.md](MODERNIZED_ARCHITECTURE.md)
2. **Component Interactions**: [COMPONENT_INTERACTIONS.md](COMPONENT_INTERACTIONS.md)
3. **Plugin System**: [PLUGIN_SYSTEM.md](PLUGIN_SYSTEM.md)
4. **Developer Setup**: [DEVELOPER_SETUP.md](DEVELOPER_SETUP.md)

### Support Channels

1. **GitHub Issues**: For bugs and feature requests
2. **GitHub Discussions**: For questions and help
3. **Code Review**: For guidance on specific changes
4. **Documentation**: For architectural understanding

### Migration Support

If you encounter issues during migration:

1. **Check Examples**: Look at updated test files for patterns
2. **Run Diagnostics**: Use `make quick-check` to identify issues
3. **Ask Questions**: Use GitHub Discussions for help
4. **Review PRs**: Look at recent pull requests for examples

This migration guide should help you transition smoothly to the modernized Riveter architecture while maintaining the high code quality and architectural consistency of the project.
