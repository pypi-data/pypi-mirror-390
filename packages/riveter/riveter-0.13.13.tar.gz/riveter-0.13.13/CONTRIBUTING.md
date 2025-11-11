# Contributing to Riveter

Thank you for your interest in contributing to Riveter! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Code Style Guidelines](#code-style-guidelines)
5. [Testing Requirements](#testing-requirements)
6. [Submitting Changes](#submitting-changes)
7. [Contributing Rule Packs](#contributing-rule-packs)
8. [Documentation](#documentation)
9. [Issue Reporting](#issue-reporting)
10. [Community](#community)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful, inclusive, and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- Basic understanding of Terraform and infrastructure as code
- Familiarity with YAML and Python (for code contributions)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/riveter.git
cd riveter
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/original-org/riveter.git
```

## Development Setup

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Complete Development Setup

```bash
# One command to set up everything
make dev-setup
```

This command:
- Installs Riveter in editable mode with all development dependencies
- Sets up pre-commit hooks automatically
- Verifies the installation

Development dependencies include:
- pytest (testing framework)
- pytest-cov (coverage reporting)
- black (code formatting)
- isort (import sorting)
- ruff (linting)
- mypy (type checking)
- pre-commit (git hooks)

### 3. Verify Installation

```bash
# Run quick quality checks to ensure everything works
make quick-check

# Check that Riveter CLI is available
riveter --version

# Run a sample scan
riveter scan --rule-pack aws-security --terraform examples/terraform/simple.tf
```

## Code Style Guidelines

### Python Code Style

We use several tools to maintain consistent code quality:

#### Code Formatting and Linting

We use Black for code formatting, isort for import sorting, and Ruff for linting. All configurations are centralized in `pyproject.toml`.

```bash
# Format code (Black + isort)
make format

# Check formatting without changes
make format-check

# Run linting
make lint

# Run linting with auto-fix
make lint-fix
```

#### Type Hints

- Use type hints for all function parameters and return values
- Import types from `typing` module when needed
- Use `Optional[T]` for nullable parameters

```python
from typing import Any, Dict, List, Optional

def validate_resources(
    rules: List[Rule],
    resources: List[Dict[str, Any]],
    min_severity: Optional[Severity] = None
) -> List[ValidationResult]:
    """Validate resources against rules."""
    pass
```

#### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.

    Longer description if needed, explaining the purpose,
    behavior, and any important details.

    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter

    Returns:
        Description of the return value

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is negative

    Example:
        result = example_function("test", 42)
        assert result is True
    """
    pass
```

### YAML Style (Rules and Configuration)

- Use 2-space indentation
- Quote strings when they contain special characters
- Use descriptive, kebab-case IDs for rules
- Include meaningful descriptions for all rules

```yaml
rules:
  - id: s3-bucket-encryption-check
    resource_type: aws_s3_bucket
    description: Ensure S3 buckets have encryption enabled
    severity: error
    assert:
      server_side_encryption_configuration: present
```

## Configuration Structure

Riveter uses a modern, consolidated configuration approach with `pyproject.toml` as the central configuration file.

### pyproject.toml Structure

All tool configurations are centralized in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
# Test configuration (replaces pytest.ini)

[tool.coverage.run]
[tool.coverage.report]
# Coverage configuration (replaces .coveragerc)

[tool.black]
# Code formatting configuration

[tool.isort]
# Import sorting configuration

[tool.mypy]
# Type checking configuration

[tool.ruff]
# Linting configuration
```

### Pre-commit Configuration

Pre-commit hooks are configured in `.pre-commit-config.yaml` with tool versions that match `pyproject.toml` dependencies.

### Development Commands

All development commands are available through the `Makefile`:

| Command | Purpose |
|---------|---------|
| `make dev-setup` | Complete development environment setup |
| `make test` | Run tests with coverage |
| `make format` | Format code (Black + isort) |
| `make lint` | Run linting (Ruff) |
| `make type-check` | Run type checking (MyPy) |
| `make quick-check` | Fast quality checks |
| `make all` | Complete quality pipeline |
| `make clean` | Clean up cache files |

## Testi
ng Requirements

### Test Coverage

- Maintain minimum 90% code coverage for all modules
- Write tests for both happy path and error scenarios
- Include integration tests for end-to-end workflows

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests without coverage (faster)
make test-fast

# Run tests with detailed coverage report
make test-cov

# Run specific test file
pytest tests/test_rules.py

# Run tests matching a pattern
pytest -k "test_rule_validation"

# Run tests with verbose output
pytest -v
```

All test configuration is centralized in `pyproject.toml` under `[tool.pytest.ini_options]` and `[tool.coverage.*]` sections.

### Test Structure

Organize tests in the `tests/` directory:

```
tests/
├── unit/                    # Unit tests for individual modules
│   ├── test_rules.py
│   ├── test_scanner.py
│   └── test_operators.py
├── integration/             # End-to-end integration tests
│   ├── test_cli_workflows.py
│   └── test_rule_packs.py
├── fixtures/                # Test data and sample files
│   ├── terraform/
│   ├── rules/
│   └── expected_outputs/
└── conftest.py             # Pytest configuration and fixtures
```

### Writing Tests

#### Unit Tests

```python
import pytest
from riveter.rules import Rule, Severity
from riveter.exceptions import RuleValidationError

class TestRule:
    def test_rule_creation_success(self):
        """Test successful rule creation."""
        rule_dict = {
            "id": "test-rule",
            "resource_type": "aws_instance",
            "assert": {"instance_type": "t3.large"}
        }
        rule = Rule(rule_dict)

        assert rule.id == "test-rule"
        assert rule.resource_type == "aws_instance"
        assert rule.severity == Severity.ERROR  # default

    def test_rule_creation_missing_id(self):
        """Test rule creation fails with missing ID."""
        rule_dict = {
            "resource_type": "aws_instance",
            "assert": {"instance_type": "t3.large"}
        }

        with pytest.raises(RuleValidationError) as exc_info:
            Rule(rule_dict)

        assert "Missing required fields: id" in str(exc_info.value)
```

#### Integration Tests

```python
def test_cli_scan_with_rule_pack(tmp_path):
    """Test CLI scan command with rule pack."""
    # Create test Terraform file
    tf_file = tmp_path / "main.tf"
    tf_file.write_text('''
    resource "aws_instance" "test" {
      instance_type = "t2.micro"
    }
    ''')

    # Run CLI command
    result = runner.invoke(cli.scan, [
        '--rule-pack', 'aws-security',
        '--terraform', str(tf_file)
    ])

    assert result.exit_code == 1  # Should fail validation
    assert "aws_instance" in result.output
```#
## Test Fixtures

Create reusable test data in `tests/fixtures/`:

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_terraform_config():
    """Sample Terraform configuration for testing."""
    return {
        "resources": [
            {
                "resource_type": "aws_instance",
                "id": "web_server",
                "instance_type": "t3.large",
                "tags": {"Environment": "production"}
            }
        ]
    }

@pytest.fixture
def sample_rule():
    """Sample rule for testing."""
    return {
        "id": "test-rule",
        "resource_type": "aws_instance",
        "description": "Test rule",
        "assert": {"instance_type": "t3.large"}
    }
```

## Submitting Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-azure-support`
- `fix/rule-validation-error`
- `docs/update-tutorial`
- `refactor/scanner-performance`

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Longer description if needed, explaining what changed
and why. Wrap at 72 characters.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(operators): add regex pattern matching support

Add support for regex operators in rule assertions to enable
more flexible string validation patterns.

Fixes #45

fix(cli): handle missing rule pack gracefully

Improve error handling when specified rule pack is not found,
providing helpful suggestions to users.

Closes #67
```

### Pull Request Process

1. **Create a Pull Request**
   - Use a descriptive title
   - Fill out the PR template completely
   - Link related issues

2. **PR Requirements**
   - All tests must pass
   - Code coverage must not decrease
   - All pre-commit hooks must pass
   - Documentation must be updated if needed

3. **Review Process**
   - At least one maintainer review required
   - Address all review feedback
   - Keep PR focused and reasonably sized

4. **Merging**
   - Squash commits when merging
   - Delete branch after merge## Cont
ributing Rule Packs

Rule packs are collections of rules for specific use cases or compliance standards.

### Creating a Rule Pack

1. **Create the Rule Pack File**

```yaml
# rule_packs/my-company-security.yml
metadata:
  name: my-company-security
  version: "1.0.0"
  description: Security rules for My Company infrastructure
  author: Your Name <your.email@company.com>
  tags:
    - security
    - aws
    - company-policy

rules:
  - id: ec2-approved-instance-types
    resource_type: aws_instance
    description: Ensure EC2 instances use company-approved types
    severity: error
    assert:
      instance_type:
        regex: "^(t3|m5|c5)\\.(large|xlarge|2xlarge)$"
```

2. **Validate the Rule Pack**

```bash
riveter validate-rule-pack rule_packs/my-company-security.yml
```

3. **Test the Rule Pack**

```bash
riveter scan --rule-pack my-company-security --terraform examples/terraform/
```

### Rule Pack Guidelines

- **Naming**: Use kebab-case for rule pack names
- **Versioning**: Follow semantic versioning (major.minor.patch)
- **Documentation**: Include clear descriptions for all rules
- **Testing**: Provide test cases and example Terraform configurations
- **Metadata**: Include comprehensive metadata

### Built-in Rule Packs

When contributing built-in rule packs:

1. Place files in `rule_packs/` directory
2. Add comprehensive test coverage in `tests/test_rule_packs.py`
3. Update documentation in `docs/rule-packs.md`
4. Include example Terraform configurations in `examples/`

## Documentation

### Types of Documentation

1. **API Documentation**: Docstrings in code (auto-generated)
2. **User Documentation**: Tutorials, guides, and references
3. **Developer Documentation**: Contributing guides and architecture docs

### Writing Documentation

- Use clear, concise language
- Include practical examples
- Keep documentation up-to-date with code changes
- Test all code examples

### Building Documentation

```bash
# Install documentation dependencies
pip install -e .[docs]

# Build documentation (if using Sphinx)
cd docs
make html
```

## Issue Reporting

### Before Reporting

1. Search existing issues to avoid duplicates
2. Try the latest version to see if the issue is already fixed
3. Gather relevant information (versions, error messages, etc.)

### Bug Reports

Include:
- Riveter version (`riveter --version`)
- Python version
- Operating system
- Complete error message and stack trace
- Minimal reproduction case
- Expected vs. actual behavior

### Feature Requests

Include:
- Clear description of the proposed feature
- Use case and motivation
- Possible implementation approach
- Examples of how it would be used## Co
mmunity

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Pull Requests**: Code contributions and reviews

### Getting Help

1. Check the documentation first
2. Search existing issues and discussions
3. Ask questions in GitHub Discussions
4. Join community calls (if available)

## Development Workflow

### Typical Development Cycle

1. **Pick an Issue**
   - Look for issues labeled `good first issue` for beginners
   - Comment on the issue to indicate you're working on it

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Quick checks during development
   make quick-check   # Format-check + lint + type-check (fast)

   # Complete quality pipeline before committing
   make all          # Format + lint + type-check + test

   # Or run individual checks:
   make test         # Run tests with coverage
   make format       # Format code (Black + isort)
   make lint         # Run linting (Ruff)
   make type-check   # Type checking (MyPy)
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

### Release Process

Releases are handled by maintainers:

1. Update version numbers
2. Update CHANGELOG.md
3. Create release tag
4. Build and publish to PyPI
5. Update documentation

## Performance Considerations

When contributing code, consider:

- **Memory Usage**: Avoid loading large files entirely into memory
- **CPU Usage**: Use efficient algorithms and data structures
- **I/O Operations**: Minimize file system operations
- **Parallel Processing**: Support parallel execution where beneficial

### Benchmarking

Include performance tests for significant changes:

```python
def test_large_configuration_performance(benchmark):
    """Test performance with large Terraform configuration."""
    rules = load_rules("rule_packs/aws-security.yml")
    resources = generate_large_resource_list(1000)

    result = benchmark(validate_resources, rules, resources)
    assert len(result) > 0
```

## Security Considerations

- Never commit secrets or sensitive information
- Validate all user inputs
- Use secure defaults
- Follow security best practices for dependencies

## Thank You

Thank you for contributing to Riveter! Your contributions help make infrastructure validation better for everyone. Whether you're fixing bugs, adding features, improving documentation, or helping other users, every contribution is valuable.

If you have questions about contributing, don't hesitate to ask in GitHub Discussions or comment on relevant issues. The maintainers and community are here to help!
