"""Modern validation engine for Riveter.

This package provides a modernized validation engine with:
- Type-safe interfaces and protocols
- Dependency injection for extensibility
- Performance optimizations
- Comprehensive error handling
- Parallel processing capabilities
"""

from .engine import ValidationEngine, ValidationEngineConfig
from .evaluator import DefaultRuleEvaluator, RuleEvaluator
from .protocols import RuleEvaluatorProtocol, ValidationEngineProtocol
from .result import AssertionResult, RuleResult, ValidationResult

__all__ = [
    "AssertionResult",
    "DefaultRuleEvaluator",
    "RuleEvaluator",
    "RuleEvaluatorProtocol",
    "RuleResult",
    "ValidationEngine",
    "ValidationEngineConfig",
    "ValidationEngineProtocol",
    "ValidationResult",
]
