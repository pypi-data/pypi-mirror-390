# Makefile for Riveter development tasks

.PHONY: help install install-dev test test-cov test-fast lint lint-fix format format-check type-check pre-commit setup-hooks clean clean-all dev-setup dev-check all quick-check

# Default target
help:
	@echo "🔧 Riveter Development Commands"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  dev-setup    - Complete development environment setup (recommended for new contributors)"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install development dependencies"
	@echo "  setup-hooks  - Install and configure pre-commit hooks"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test         - Run tests with coverage"
	@echo "  test-fast    - Run tests without coverage (faster)"
	@echo "  test-cov     - Run tests with detailed coverage report"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  format       - Format code (black + isort)"
	@echo "  format-check - Check code formatting without changes"
	@echo "  lint         - Run linting (ruff)"
	@echo "  lint-fix     - Run linting with auto-fix"
	@echo "  type-check   - Run type checking (mypy)"
	@echo ""
	@echo "🚀 Development Workflow:"
	@echo "  quick-check  - Fast code quality checks (format-check + lint + type-check)"
	@echo "  dev-check    - Development checks (format + lint + type-check)"
	@echo "  pre-commit   - Run all pre-commit hooks"
	@echo "  all          - Complete quality pipeline (format + lint + type-check + test)"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  clean        - Clean up cache files"
	@echo "  clean-all    - Deep clean (cache + build artifacts)"

# Setup & Installation
dev-setup: install-dev setup-hooks
	@echo ""
	@echo "🎉 Development environment setup complete!"
	@echo ""
	@echo "💡 Next steps:"
	@echo "  • Run 'make quick-check' to verify everything works"
	@echo "  • Run 'make test' to run the test suite"
	@echo "  • Start coding! Pre-commit hooks will run automatically"

install:
	@echo "📦 Installing Riveter package..."
	pip install -e .

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -e ".[dev]"

# Testing
test:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --tb=short

test-fast:
	@echo "🧪 Running tests (fast mode, no coverage)..."
	pytest tests/ -v --tb=short --no-cov

test-cov:
	@echo "🧪 Running tests with detailed coverage report..."
	pytest tests/ --cov=src/riveter --cov-report=html --cov-report=term-missing

# Code Quality
format:
	@echo "🎨 Formatting code with Black and isort..."
	black src/ tests/
	isort src/ tests/

format-check:
	@echo "🎨 Checking code formatting..."
	black --check src/ tests/
	isort --check-only src/ tests/

lint:
	@echo "🔍 Running linting with Ruff..."
	ruff check src/ tests/

lint-fix:
	@echo "🔍 Running linting with auto-fix..."
	ruff check src/ tests/ --fix

type-check:
	@echo "🔍 Running type checking with MyPy..."
	mypy src/

# Pre-commit
pre-commit:
	@echo "🪝 Running all pre-commit hooks..."
	pre-commit run --all-files

setup-hooks:
	@echo "🔧 Setting up pre-commit hooks..."
	@if ! command -v pre-commit >/dev/null 2>&1; then \
		echo "📦 Installing pre-commit..."; \
		pip install pre-commit; \
	else \
		echo "✅ pre-commit is already installed"; \
	fi
	@echo "🪝 Installing pre-commit hooks..."
	pre-commit install
	@echo "🧪 Running pre-commit on all files to check current state..."
	@if pre-commit run --all-files; then \
		echo "✅ All pre-commit hooks passed!"; \
	else \
		echo "⚠️  Some hooks failed. This is normal for the first run."; \
		echo "   The hooks have automatically fixed what they can."; \
		echo "   Please review the changes and commit them."; \
	fi
	@echo ""
	@echo "🎉 Pre-commit setup complete!"
	@echo ""
	@echo "ℹ️  What happens now:"
	@echo "   • Every time you commit, the hooks will run automatically"
	@echo "   • Code will be formatted with Black and isort"
	@echo "   • Code will be linted with Ruff"
	@echo "   • Type checking will run with MyPy"
	@echo "   • Tests will run on changed files"
	@echo ""
	@echo "💡 Pro tips:"
	@echo "   • Run 'make pre-commit' to check all files manually"
	@echo "   • Use 'git commit --no-verify' to skip hooks (not recommended)"
	@echo "   • Update hooks with 'pre-commit autoupdate'"

# Cleanup
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -f .coverage 2>/dev/null || true
	@echo "✅ Cache cleanup complete"

clean-all: clean
	@echo "🧹 Deep cleaning (build artifacts + cache)..."
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	rm -f coverage.xml 2>/dev/null || true
	@echo "✅ Deep cleanup complete"

# Development Workflow
quick-check: format-check lint type-check
	@echo "✅ Quick code quality checks passed!"

dev-check: format lint type-check
	@echo "✅ Development checks complete!"

# Complete quality pipeline (like CI)
all: format lint type-check test
	@echo "🎉 All quality checks passed!"
