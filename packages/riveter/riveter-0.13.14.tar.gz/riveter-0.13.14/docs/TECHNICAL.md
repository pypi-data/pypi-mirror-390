# Riveter Technical Documentation

This document provides a detailed technical overview of how Riveter works internally. It's designed for developers who want to understand the codebase or contribute to the project.

## Architecture Overview

Riveter is built with a modular architecture that supports both core functionality and automated release workflows:

### Core Functionality
1. **Parse Terraform Configuration** → **Load Rules** → **Scan Resources** → **Report Results**

### Release Automation
2. **Version Management** → **Changelog Processing** → **Package Building** → **GitHub Release Creation**

The tool is split into several core modules and automation scripts, each with a specific responsibility:

## Core Modules

### Core Analysis Engine

#### `extract_config.py`

This module is responsible for parsing Terraform HCL files into a normalized format that Riveter can process.

```python
def extract_terraform_config(tf_file: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extract Terraform configuration into Riveter format."""
```

Key features:
- Uses `python-hcl2` to parse Terraform HCL syntax
- Normalizes resource blocks into a consistent format
- Handles nested structures (lists, maps)
- Converts tag formats from lists to dictionaries when needed

Output format:
```json
{
    "resources": [
        {
            "id": "resource_name",
            "resource_type": "aws_instance",
            "instance_type": "t3.large",
            "tags": {
                "Environment": "production"
            }
        }
    ]
}
```

#### `rules.py`

This module handles loading and parsing rule definitions from YAML files.

```python
def load_rules(rules_file: str) -> List[Rule]:
    """Load rules from a YAML file."""
```

Key features:
- YAML parsing with PyYAML
- Rule validation and normalization
- Support for filtering and assertions

Rule format:
```yaml
rules:
  - id: rule-id
    description: Rule description
    resource_type: aws_instance
    filter:
      tags:
        Environment: production
    assert:
      instance_type: t3.large
```

#### `scanner.py`

The core scanning engine that checks resources against rules.

```python
def scan_resources(rules: List[Rule], resources: List[Dict[str, Any]]) -> List[DriftResult]:
    """Scan resources for drift against rules."""
```

Key features:
- Resource filtering based on rule criteria
- Deep comparison of resource attributes
- Support for nested attribute checking
- Detailed result reporting

The scanner uses a `DriftResult` class to track each rule check:
```python
class DriftResult:
    def __init__(self, rule: Rule, resource: Dict[str, Any], passed: bool, message: str):
        self.rule = rule
        self.resource = resource
        self.passed = passed
        self.message = message
```

#### `reporter.py`

Handles formatting and displaying scan results.

```python
def report_results(results: List[DriftResult]) -> int:
    """Format and display scan results."""
```

Key features:
- Rich terminal output with tables
- Color-coded pass/fail status
- Detailed error messages
- Summary statistics

#### `cli.py`

The command-line interface that ties everything together.

```python
@click.command()
def scan(rules_file: str, terraform_file: str) -> None:
    """Scan Terraform configuration for drift."""
```

Key features:
- Click-based CLI
- File validation
- Error handling
- Exit code management

### Release Automation Components

#### `version_manager.py`

Handles semantic versioning and version updates across the project.

```python
class VersionManager:
    def calculate_next_version(self, current: str, version_type: VersionType) -> str:
        """Calculate the next semantic version."""
```

Key features:
- Semantic version parsing and validation
- Version bumping (major, minor, patch)
- pyproject.toml version updates
- Git tag creation and validation
- Integration with changelog processing

#### `changelog_processor.py`

Processes CHANGELOG.md files for release notes generation.

```python
class ChangelogProcessor:
    def process_release(self, version: str) -> Tuple[str, ReleaseNotes]:
        """Process changelog for a new release."""
```

Key features:
- Markdown changelog parsing
- Unreleased section processing
- Release notes extraction
- GitHub-compatible formatting
- Automatic date insertion

#### `workflow_error_handler.py`

Comprehensive validation and error handling for the release workflow.

```python
class WorkflowErrorHandler:
    def run_comprehensive_validation(self, tag: str, dry_run: bool = False) -> bool:
        """Run all pre-release validation checks."""
```

Key features:
- Branch and permissions validation
- Secret and token validation
- Project structure validation
- Network connectivity checks
- Tag uniqueness validation
- Rollback documentation generation
- GitHub Actions integration

### GitHub Actions Workflows

#### `.github/workflows/release.yml`

Automated release workflow with comprehensive validation and security checks.

Key stages:
1. **Validation**: Pre-release checks and environment validation
2. **Testing**: Multi-platform test suite (Ubuntu, macOS)
3. **Security**: Security scanning and dependency checks
4. **Build**: Package building and validation
5. **Version Management**: Semantic version updates
6. **Changelog**: Release notes generation
7. **Release**: GitHub release creation and PyPI publishing

#### `.github/workflows/test.yml`

Continuous integration workflow for pull requests and pushes.

Key features:
- Multi-platform testing (Ubuntu, macOS)
- Multiple Python versions (3.12, 3.13)
- Comprehensive test suite
- Code quality checks (linting, formatting, type checking)
- Security scanning
- Coverage reporting

## Flow of Execution

### Core Analysis Flow

1. **CLI Entry**
   - User runs `riveter scan -r rules.yml -t main.tf`
   - `cli.py` validates input files and options

2. **Configuration Loading**
   - `extract_config.py` parses the Terraform file
   - `rules.py` loads and validates the rules

3. **Scanning**
   - `scanner.py` processes each resource against each rule
   - Filtering is applied first
   - Assertions are checked
   - Results are collected

4. **Reporting**
   - `reporter.py` formats the results
   - Table is displayed with pass/fail status
   - Summary is shown
   - Exit code is set based on results

### Release Automation Flow

1. **Trigger**
   - Manual workflow dispatch from GitHub Actions
   - User selects version type (major, minor, patch)
   - Optional dry-run mode

2. **Validation**
   - Branch permissions (must be on main)
   - Environment variables and secrets
   - Project structure integrity
   - Network connectivity
   - Tag uniqueness

3. **Testing**
   - Full test suite across platforms
   - Security scanning
   - Code quality checks
   - Build validation

4. **Version Management**
   - Calculate next semantic version
   - Update pyproject.toml
   - Create and push git tag

5. **Changelog Processing**
   - Extract unreleased changes
   - Generate release notes
   - Update changelog with release date

6. **Package Building**
   - Build source distribution
   - Build wheel distribution
   - Validate package integrity

7. **Release Creation**
   - Create GitHub release
   - Upload build artifacts
   - Publish to PyPI (if not dry-run)

## Example Flow

Let's follow a simple security group rule through the system:

1. **Rule Definition** (rules.yml):
```yaml
rules:
  - id: security-group-allowed-ports
    description: Only allow HTTP/HTTPS
    resource_type: aws_security_group
    assert:
      ingress:
        - from_port: 443
          to_port: 443
          protocol: tcp
```

2. **Terraform Config** (main.tf):
```hcl
resource "aws_security_group" "web" {
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
  }
}
```

3. **Extraction**:
```json
{
  "resources": [
    {
      "id": "web",
      "resource_type": "aws_security_group",
      "ingress": [
        {
          "from_port": 22,
          "to_port": 22,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

4. **Scanning**:
- Rule matches resource type
- No filters to apply
- Assertion fails: ingress ports don't match

5. **Result**:
```python
DriftResult(
    rule=rule,
    resource=resource,
    passed=False,
    message="Property 'ingress' has invalid value"
)
```

## Contributing

When adding new features, consider:

### Core Functionality

1. **Rule Engine Extensions**
   - Add new assertion types in `scanner.py`
   - Update rule validation in `rules.py`
   - Add corresponding tests

2. **Resource Support**
   - Enhance `extract_config.py` for new resource types
   - Add special handling for complex structures
   - Update cloud provider parsers

3. **Reporting Improvements**
   - Add new output formats in `reporter.py`
   - Enhance error messages and suggestions
   - Support new formatters (JSON, SARIF, JUnit)

4. **CLI Features**
   - Add new commands in `cli.py`
   - Implement new options and flags
   - Maintain backward compatibility

### Release Automation

5. **Workflow Enhancements**
   - Extend validation checks in `workflow_error_handler.py`
   - Add new security validations
   - Improve error recovery and rollback procedures

6. **Version Management**
   - Enhance semantic versioning logic
   - Add support for pre-release versions
   - Improve changelog automation

7. **CI/CD Improvements**
   - Add new test platforms or Python versions
   - Enhance security scanning
   - Optimize build and deployment processes

### Development Guidelines

- **Testing**: All new features must include comprehensive tests
- **Documentation**: Update both user and technical documentation
- **Security**: Follow security best practices, especially for release automation
- **Compatibility**: Maintain backward compatibility where possible
- **Performance**: Consider performance implications of new features

## Source Code Details

This section provides a detailed explanation of each Python file in the `src/riveter` directory, describing how each component works and its role in the system.

### `__init__.py`

A simple initialization file that defines the package version and provides a brief description of Riveter.

```python
__version__ = "0.1.0"
```

This file makes the directory a proper Python package and allows for version tracking.

### `cli.py`

Implements the command-line interface using the Click library.

Key components:
- Defines the main CLI group and commands
- Implements the `scan` command with options for rules and Terraform files
- Orchestrates the workflow by calling other modules in sequence
- Handles errors and sets appropriate exit codes

The main workflow in the `scan` function:
1. Loads rules from the specified YAML file
2. Extracts Terraform configuration from the specified file
3. Scans resources against the rules
4. Reports results and sets the exit code

Error handling is implemented with try/except blocks to provide clear error messages.

### `extract_config.py`

Responsible for parsing Terraform HCL files and converting them to a normalized format that Riveter can process.

Key features:
- Uses the `hcl2` library to parse Terraform HCL syntax
- Extracts resources from the configuration
- Normalizes resource data into a consistent format
- Handles special cases like tag conversions

The main function `extract_terraform_config` takes a Terraform file path and returns a dictionary with a "resources" key containing a list of resource objects. Each resource object includes:
- `id`: The resource name
- `resource_type`: The provider resource type (e.g., aws_instance)
- Various properties from the resource configuration

The module also includes a standalone `main` function that can be used to extract and save configuration to a JSON file when run directly.

### `rules.py`

Handles loading, parsing, and validating rule definitions from YAML files.

Key components:
- `Rule` class: Represents a single rule with properties for ID, resource type, filters, and assertions
- `load_rules` function: Loads rules from a YAML file and validates their structure

The `Rule` class includes a `matches_resource` method that determines if a resource matches the rule's filters. This is used during scanning to determine which rules apply to which resources.

Rule validation ensures that each rule has the required fields:
- `id`: A unique identifier for the rule
- `resource_type`: The type of resource this rule applies to
- `assert`: Conditions that must be true for the resource to pass

Optional fields include:
- `filter`: Criteria to determine which resources the rule applies to

### `scanner.py`

Implements the core scanning logic that checks resources against rules.

Key components:
- `DriftResult` class: Stores the result of checking a resource against a rule
- `scan_resources` function: Scans resources against rules and generates results

The scanning process:
1. For each resource, find applicable rules based on resource type
2. For each applicable rule, check if the resource matches the rule's filters
3. For matching resources, check all assertions defined in the rule
4. Create a `DriftResult` object with the pass/fail status and message

The scanner handles special cases like tag assertions and can work with nested properties. It provides detailed failure messages that explain why a resource failed a particular assertion.

### `reporter.py`

Responsible for formatting and displaying scan results.

Key features:
- Uses the Rich library to create colorful, formatted terminal output
- Creates a table showing results for each rule check
- Provides a summary of passed/failed checks
- Returns an exit code based on whether any checks failed

The `report_results` function takes a list of `DriftResult` objects and:
1. Creates a table with columns for Rule ID, Resource Type, Resource ID, Status, and Message
2. Formats each row with appropriate colors (green for pass, red for fail)
3. Prints a summary showing the number of passed checks out of total checks
4. Returns an exit code (0 for all passed, 1 if any failed)

## Testing

Riveter has a comprehensive test suite covering all components:

### Core Module Tests

- `test_extract_config.py`: Tests Terraform parsing and configuration extraction
- `test_rules.py`: Tests rule loading, validation, and advanced features
- `test_scanner.py`: Tests resource scanning and validation logic
- `test_reporter.py`: Tests result formatting and output generation
- `test_cli.py`: Tests command-line interface functionality

### Advanced Feature Tests

- `test_cloud_parsers.py`: Tests multi-cloud provider support (AWS, Azure, GCP)
- `test_operators.py`: Tests advanced operators (numeric, regex, list operations)
- `test_performance.py`: Tests parallel processing and caching
- `test_rule_distribution.py`: Tests rule packaging and distribution
- `test_formatters.py`: Tests output formatters (JSON, SARIF, JUnit)

### Release Automation Tests

- `test_version_manager.py`: Tests semantic versioning and version management
- `test_changelog_processor.py`: Tests changelog processing and release notes
- `test_error_handling_integration.py`: Tests comprehensive workflow validation
- `test_github_release_integration.py`: Tests GitHub release workflow integration
- `test_package_building_integration.py`: Tests package building and validation
- `test_security_validation.py`: Tests security scanning and validation

### Test Infrastructure

#### Continuous Integration

- **Platforms**: Ubuntu Latest, macOS Latest
- **Python Versions**: 3.12, 3.13
- **Test Types**: Unit, integration, security, performance
- **Coverage**: Minimum 80% code coverage required

#### Test Categories

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: End-to-end workflow testing
- **Security Tests**: Vulnerability scanning and security validation
- **Performance Tests**: Load testing and optimization validation

#### Test Utilities

- **Fixtures**: Reusable test data and mock objects
- **Mocking**: Comprehensive mocking for external dependencies
- **Temporary Environments**: Isolated test environments for git operations
- **Cross-Platform**: Platform-specific test handling

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=riveter --cov-report=html

# Run specific test categories
pytest -m "unit"          # Unit tests only
pytest -m "integration"   # Integration tests only
pytest -m "not slow"      # Skip slow tests

# Run tests for specific modules
pytest tests/test_version_manager.py
pytest tests/test_error_handling_integration.py
```

### Test Configuration

Test configuration is centralized in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--cov=src/riveter",
    "--cov-fail-under=80"
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]
```

## Project Structure

```
riveter/
├── src/riveter/           # Core application code
│   ├── __init__.py
│   ├── cli.py            # Command-line interface
│   ├── extract_config.py # Terraform parsing
│   ├── rules.py          # Rule loading and validation
│   ├── scanner.py        # Core scanning engine
│   ├── reporter.py       # Result formatting
│   ├── version_manager.py # Version management
│   ├── changelog_processor.py # Changelog processing
│   ├── cloud_parsers.py  # Multi-cloud support
│   ├── operators.py      # Advanced operators
│   ├── formatters.py     # Output formatters
│   ├── performance.py    # Performance optimizations
│   ├── rule_*.py         # Rule management modules
│   ├── config.py         # Configuration management
│   ├── logging.py        # Structured logging
│   └── exceptions.py     # Custom exceptions
├── scripts/              # Automation scripts
│   ├── workflow_error_handler.py # Release validation
│   ├── validate_security.py      # Security validation
│   └── debug_ci_environment.py   # CI debugging
├── tests/                # Comprehensive test suite
│   ├── test_*.py         # Unit and integration tests
│   └── fixtures/         # Test data and fixtures
├── docs/                 # Documentation
│   ├── TECHNICAL.md      # This file
│   ├── RELEASE_WORKFLOW.md # Release process documentation
│   ├── CI_TROUBLESHOOTING.md # CI debugging guide
│   └── SECURITY_SETUP.md # Security configuration
├── .github/workflows/    # GitHub Actions workflows
│   ├── release.yml       # Automated release workflow
│   └── test.yml          # Continuous integration
└── .kiro/               # Kiro IDE specifications
    └── specs/           # Feature specifications
```

## Recent Enhancements

### Automated Release Workflow

The project now includes a comprehensive automated release workflow that:

- **Validates** all pre-release conditions (branch, permissions, secrets, project structure)
- **Tests** across multiple platforms and Python versions
- **Scans** for security vulnerabilities and code quality issues
- **Builds** and validates packages
- **Manages** semantic versioning automatically
- **Processes** changelogs and generates release notes
- **Creates** GitHub releases and publishes to PyPI
- **Provides** rollback documentation for failed releases

### Enhanced Testing Infrastructure

- **Multi-platform CI**: Ubuntu and macOS support
- **Comprehensive coverage**: 80% minimum code coverage requirement
- **Integration tests**: End-to-end workflow validation
- **Security testing**: Automated vulnerability scanning
- **Performance testing**: Load testing and optimization validation

### Developer Experience Improvements

- **CI Troubleshooting**: Comprehensive debugging tools and documentation
- **Security Setup**: Detailed security configuration guides
- **Development Tools**: Enhanced pre-commit hooks and code quality checks
- **Documentation**: Updated technical and user documentation

### Architecture Evolution

The project has evolved from a simple CLI tool to a comprehensive infrastructure analysis platform with:

- **Multi-cloud support**: AWS, Azure, GCP resource parsing
- **Advanced operators**: Numeric, regex, and list operations
- **Multiple output formats**: JSON, SARIF, JUnit XML
- **Rule distribution**: Packaging and sharing of rule sets
- **Performance optimization**: Parallel processing and caching
- **Extensible architecture**: Plugin-based rule and formatter system
