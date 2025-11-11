# Developer Setup Guide

This guide provides comprehensive instructions for setting up a development environment for the modernized Riveter codebase.

## Prerequisites

### System Requirements

- **Python**: 3.12 or higher
- **Git**: Latest version
- **Operating System**: macOS, Linux, or Windows with WSL2

### Recommended Tools

- **IDE**: VS Code, PyCharm, or similar with Python support
- **Terminal**: Modern terminal with color support
- **Package Manager**: pip (included with Python)

## Quick Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/riveter/riveter.git
cd riveter

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR: .\venv\Scripts\activate  # Windows

# Complete development setup (one command does everything)
make dev-setup
```

The `make dev-setup` command:
- Installs Riveter in editable mode with all development dependencies
- Sets up pre-commit hooks automatically
- Configures all development tools
- Verifies the installation

### 2. Verify Installation

```bash
# Quick verification
make quick-check

# Test CLI functionality
riveter --version
riveter list-rule-packs

# Run a sample validation
riveter scan -p aws-security -t examples/terraform/simple.tf
```

## Development Environment

### Virtual Environment Management

The modernized Riveter uses a standard Python virtual environment:

```bash
# Activate environment (required for development)
source venv/bin/activate

# Deactivate when done
deactivate

# Recreate environment if needed
rm -rf venv
python3 -m venv venv
source venv/bin/activate
make dev-setup
```

### Development Dependencies

All development dependencies are managed in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",

    # Code Quality
    "black>=23.0.0",
    "isort>=5.12.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",

    # Development Tools
    "pre-commit>=3.0.0",
    "build>=0.10.0",
    "twine>=4.0.0",
]
```

## Development Workflow

### Code Quality Pipeline

The modernized codebase uses a comprehensive quality pipeline:

```bash
# Format code (Black + isort)
make format

# Check formatting without changes
make format-check

# Run linting (Ruff)
make lint

# Run linting with auto-fix
make lint-fix

# Type checking (MyPy)
make type-check

# Quick quality checks (fast)
make quick-check

# Complete quality pipeline
make all
```

### Testing

```bash
# Run all tests with coverage
make test

# Run tests without coverage (faster)
make test-fast

# Run tests with detailed coverage report
make test-cov

# Run specific test files
pytest tests/unit/models/test_core.py

# Run tests matching a pattern
pytest -k "test_validation"

# Run tests with verbose output
pytest -v
```

### Pre-commit Hooks

Pre-commit hooks are automatically configured during `make dev-setup`:

```bash
# Manually install hooks (if needed)
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

## Architecture Overview

### Modernized Structure

The modernized Riveter follows a layered architecture:

```
src/riveter/
├── cli/                     # CLI layer
│   ├── interface.py         # Protocol definitions
│   ├── commands.py          # Command implementations
│   ├── registry.py          # Command registry
│   └── performance.py       # CLI optimizations
├── models/                  # Data models
│   ├── core.py             # Core data structures
│   ├── rules.py            # Rule models
│   ├── config.py           # Configuration models
│   └── protocols.py        # Protocol definitions
├── validation/              # Validation engine
│   ├── engine.py           # Main validation engine
│   ├── evaluator.py        # Rule evaluation
│   ├── cache.py            # Result caching
│   └── performance.py      # Performance optimizations
├── configuration/           # Configuration management
│   ├── manager.py          # Configuration manager
│   ├── parser.py           # Terraform parsing
│   └── cache.py            # Configuration caching
├── output/                  # Output system
│   ├── manager.py          # Output manager
│   ├── formatters.py       # Output formatters
│   └── protocols.py        # Output protocols
├── plugins/                 # Plugin system
│   ├── manager.py          # Plugin manager
│   ├── discovery.py        # Plugin discovery
│   └── loader.py           # Plugin loading
├── cache/                   # Caching system
│   ├── manager.py          # Cache manager
│   ├── providers.py        # Cache providers
│   └── strategies.py       # Caching strategies
└── parallel/                # Parallel processing
    ├── executor.py         # Parallel executor
    ├── scheduler.py        # Task scheduling
    └── pool.py             # Worker pool
```

### Key Design Principles

1. **Protocol-Based Design**: Uses Python protocols for type safety and extensibility
2. **Dependency Injection**: Components receive dependencies through constructors
3. **Immutable Data**: All data models are immutable using `@dataclass(frozen=True)`
4. **Type Safety**: Complete type annotations throughout the codebase
5. **Performance**: Lazy loading, caching, and parallel processing
6. **Extensibility**: Plugin system and extension points

## Development Patterns

### Adding New Features

1. **Follow Protocols**: Use protocol-based interfaces for extensibility
2. **Type Safety**: Include comprehensive type annotations
3. **Testing**: Add unit, integration, and property-based tests
4. **Documentation**: Update architecture and API documentation

### Example: Adding a New Command

```python
# 1. Define the command
from riveter.cli.interface import BaseCommand, CommandResult
from riveter.models.config import CLIArgs

class MyCommand(BaseCommand):
    def __init__(self):
        super().__init__("my-command", "My custom command")

    def execute(self, args: CLIArgs) -> CommandResult:
        # Implementation
        return CommandResult(exit_code=0, output="Success")

# 2. Register the command
from riveter.cli.registry import get_global_registry

registry = get_global_registry()
registry.register_command("my-command", lambda: MyCommand())

# 3. Add tests
class TestMyCommand:
    def test_command_execution(self):
        command = MyCommand()
        result = command.execute(create_test_args())
        assert result.exit_code == 0
```

### Example: Adding a New Output Formatter

```python
# 1. Implement the formatter protocol
from riveter.output.protocols import OutputFormatter
from riveter.models.core import ValidationResult

class MyFormatter(OutputFormatter):
    def format(self, result: ValidationResult) -> str:
        # Custom formatting logic
        return "Custom formatted output"

# 2. Register the formatter
from riveter.output.manager import OutputManager

output_manager = OutputManager()
output_manager.register_formatter("my-format", MyFormatter())

# 3. Add tests
def test_my_formatter():
    formatter = MyFormatter()
    result = create_test_validation_result()
    output = formatter.format(result)
    assert "Custom formatted output" in output
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── cli/                # CLI component tests
│   ├── models/             # Data model tests
│   ├── validation/         # Validation engine tests
│   └── output/             # Output system tests
├── integration/            # Integration tests
│   ├── cli_integration/    # End-to-end CLI tests
│   └── component_integration/ # Component interaction tests
├── performance/            # Performance tests
│   ├── cli_benchmarks/     # CLI performance tests
│   └── component_benchmarks/ # Component performance tests
└── property/               # Property-based tests
    └── rule_validation/    # Rule validation property tests
```

### Writing Tests

#### Unit Tests

```python
import pytest
from riveter.models.core import TerraformResource, SourceLocation
from pathlib import Path

class TestTerraformResource:
    def test_resource_creation(self):
        """Test resource creation with all fields."""
        resource = TerraformResource(
            type="aws_instance",
            name="web",
            attributes={"instance_type": "t3.large"},
            source_location=SourceLocation(Path("main.tf"), 10)
        )

        assert resource.type == "aws_instance"
        assert resource.name == "web"
        assert resource.id == "aws_instance.web"
        assert resource.get_attribute("instance_type") == "t3.large"

    def test_resource_tags(self):
        """Test resource tag handling."""
        resource = TerraformResource(
            type="aws_instance",
            name="web",
            attributes={
                "instance_type": "t3.large",
                "tags": {"Environment": "prod", "Team": "platform"}
            }
        )

        assert resource.has_tag("Environment")
        assert resource.get_tag("Environment") == "prod"
        assert not resource.has_tag("NonExistent")
        assert resource.get_tag("NonExistent", "default") == "default"
```

#### Integration Tests

```python
def test_validation_engine_integration(tmp_path):
    """Test complete validation workflow."""
    # Create test Terraform file
    tf_file = tmp_path / "main.tf"
    tf_file.write_text('''
    resource "aws_instance" "test" {
      instance_type = "t3.large"
      tags = {
        Environment = "production"
      }
    }
    ''')

    # Create test rule
    rule = Rule(
        id="test-rule",
        resource_type="aws_instance",
        description="Test rule",
        severity=Severity.ERROR,
        conditions=[
            Condition(
                field="instance_type",
                operator="eq",
                value="t3.large"
            )
        ]
    )

    # Load configuration
    config_manager = ConfigurationManager()
    config = config_manager.load_terraform_config(tf_file)

    # Run validation
    engine = ValidationEngine()
    result = engine.validate_resources([rule], config.resources)

    # Verify results
    assert result.summary.total_results == 1
    assert result.summary.passed == 1
    assert result.summary.failed == 0
```

#### Performance Tests

```python
def test_validation_performance(benchmark):
    """Test validation performance with large datasets."""
    rules = create_test_rules(100)
    resources = create_test_resources(1000)

    engine = ValidationEngine()

    result = benchmark(engine.validate_resources, rules, resources)

    # Verify performance expectations
    assert result.summary.duration < 5.0  # Should complete in under 5 seconds
    assert len(result.results) > 0
```

## Configuration

### Development Configuration

All tool configurations are centralized in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--cov=src/riveter",
    "--cov-fail-under=80",
    "--cov-report=html",
    "--cov-report=term-missing"
]

[tool.black]
line-length = 100
target-version = ['py312']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "W", "C90", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SIM", "TID", "TCH", "ARG", "PTH", "ERA", "PD", "PGH", "PL", "TRY", "NPY", "RUF"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm

1. Set Python interpreter to `./venv/bin/python`
2. Enable Black formatter in Settings → Tools → External Tools
3. Configure pytest as test runner
4. Enable type checking with MyPy

## Debugging

### Debug Configuration

#### VS Code Launch Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Riveter CLI",
            "type": "python",
            "request": "launch",
            "module": "riveter",
            "args": ["scan", "-p", "aws-security", "-t", "examples/terraform/simple.tf"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/unit/models/test_core.py", "-v"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### Logging Configuration

Enable debug logging during development:

```python
import logging
from riveter.logging import configure_logging

# Enable debug logging
configure_logging(level=logging.DEBUG)

# Or set environment variable
import os
os.environ['RIVETER_LOG_LEVEL'] = 'DEBUG'
```

### Performance Profiling

```python
import cProfile
import pstats
from riveter.validation.engine import ValidationEngine

def profile_validation():
    engine = ValidationEngine()
    rules = load_test_rules()
    resources = load_test_resources()

    profiler = cProfile.Profile()
    profiler.enable()

    result = engine.validate_resources(rules, resources)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

if __name__ == "__main__":
    profile_validation()
```

## Troubleshooting

### Common Issues

#### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify PYTHONPATH includes src directory
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Reinstall in editable mode
pip install -e .
```

#### Test Failures

```bash
# Run tests with verbose output
pytest -v

# Run specific failing test
pytest tests/unit/models/test_core.py::TestTerraformResource::test_resource_creation -v

# Clear pytest cache
pytest --cache-clear
```

#### Type Checking Issues

```bash
# Run MyPy with verbose output
mypy src/riveter --show-error-codes

# Check specific file
mypy src/riveter/models/core.py

# Install missing type stubs
pip install types-PyYAML types-requests
```

#### Performance Issues

```bash
# Profile test execution
pytest --profile

# Run performance tests
pytest tests/performance/ -v

# Check memory usage
python -m memory_profiler examples/profile_validation.py
```

### Getting Help

1. **Check Documentation**: Review architecture and API documentation
2. **Search Issues**: Look for similar issues on GitHub
3. **Run Diagnostics**: Use `make quick-check` to verify setup
4. **Ask Questions**: Use GitHub Discussions for help

## Contributing

### Before Contributing

1. **Read Guidelines**: Review [CONTRIBUTING.md](../CONTRIBUTING.md)
2. **Setup Environment**: Follow this setup guide
3. **Run Tests**: Ensure all tests pass with `make test`
4. **Check Quality**: Run `make all` to verify code quality

### Contribution Workflow

1. **Create Branch**: `git checkout -b feature/my-feature`
2. **Make Changes**: Follow development patterns and guidelines
3. **Add Tests**: Include comprehensive test coverage
4. **Update Docs**: Update relevant documentation
5. **Quality Check**: Run `make all` to verify everything passes
6. **Submit PR**: Create pull request with clear description

This developer setup guide provides everything needed to contribute effectively to the modernized Riveter codebase while maintaining high code quality and architectural consistency.
