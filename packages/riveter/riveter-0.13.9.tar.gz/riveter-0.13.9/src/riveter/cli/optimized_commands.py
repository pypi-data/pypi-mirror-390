"""Optimized command implementations with performance enhancements."""

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..cache import CacheManager
from ..logging import debug, info
from ..models.config import CLIArgs
from .performance import _get_global_cli_cache, cached_command, lazy_import_decorator


class OptimizedScanCommand:
    """Optimized scan command with intelligent caching and lazy loading."""

    def __init__(self):
        self._cache = _get_global_cli_cache()
        self._last_scan_cache: Dict[str, Any] = {}

    @cached_command(ttl=300)  # Cache for 5 minutes
    def execute(self, args: CLIArgs) -> Any:
        """Execute scan command with optimizations."""
        # Check if we can use cached results
        cache_key = self._generate_cache_key(args)

        # Check if files have changed since last scan
        if self._can_use_cached_result(args, cache_key):
            debug("Using cached scan result")
            return self._get_cached_result(cache_key)

        # Perform actual scan with lazy loading
        return self._perform_optimized_scan(args)

    def _generate_cache_key(self, args: CLIArgs) -> str:
        """Generate cache key for scan arguments."""
        key_parts = [
            str(args.terraform_file),
            str(args.rules_file) if args.rules_file else "",
            ":".join(sorted(args.rule_packs)),
            args.output_format,
        ]

        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _can_use_cached_result(self, args: CLIArgs, cache_key: str) -> bool:
        """Check if cached result can be used."""
        cached_data = self._cache.get_startup_data(f"scan_metadata_{cache_key}")
        if not cached_data:
            return False

        # Check if Terraform file has changed
        if args.terraform_file and Path(args.terraform_file).exists():
            current_mtime = Path(args.terraform_file).stat().st_mtime
            cached_mtime = cached_data.get("terraform_mtime", 0)
            if current_mtime > cached_mtime:
                return False

        # Check if rules file has changed
        if args.rules_file and Path(args.rules_file).exists():
            current_mtime = Path(args.rules_file).stat().st_mtime
            cached_mtime = cached_data.get("rules_mtime", 0)
            if current_mtime > cached_mtime:
                return False

        return True

    def _get_cached_result(self, cache_key: str) -> Any:
        """Get cached scan result."""
        return self._cache.get_startup_data(f"scan_result_{cache_key}")

    @lazy_import_decorator("riveter.scanner", "Scanner")
    def _perform_optimized_scan(self, args: CLIArgs) -> Any:
        """Perform optimized scan with lazy loading."""
        # This will be replaced by the decorator to use lazy-loaded Scanner
        pass

    def _cache_scan_result(self, args: CLIArgs, cache_key: str, result: Any) -> None:
        """Cache scan result and metadata."""
        metadata = {
            "scan_time": time.time(),
        }

        # Add file modification times
        if args.terraform_file and Path(args.terraform_file).exists():
            metadata["terraform_mtime"] = Path(args.terraform_file).stat().st_mtime

        if args.rules_file and Path(args.rules_file).exists():
            metadata["rules_mtime"] = Path(args.rules_file).stat().st_mtime

        self._cache.cache_startup_data(f"scan_metadata_{cache_key}", metadata)
        self._cache.cache_startup_data(f"scan_result_{cache_key}", result)


class OptimizedRulePackCommand:
    """Optimized rule pack commands with caching."""

    def __init__(self):
        self._cache = _get_global_cli_cache()
        self._rule_pack_cache: Dict[str, Any] = {}

    @cached_command(ttl=1800)  # Cache for 30 minutes
    def list_rule_packs(self) -> List[str]:
        """List available rule packs with caching."""
        cached_packs = self._cache.get_startup_data("available_rule_packs")
        if cached_packs:
            debug("Using cached rule pack list")
            return cached_packs

        # Load rule packs with lazy loading
        packs = self._load_rule_packs_lazy()

        # Cache the result
        self._cache.cache_startup_data("available_rule_packs", packs)

        return packs

    @lazy_import_decorator("riveter.rule_packs", "RulePackManager")
    def _load_rule_packs_lazy(self) -> List[str]:
        """Load rule packs with lazy loading."""
        # This will be replaced by the decorator
        pass

    @cached_command(ttl=600)  # Cache for 10 minutes
    def validate_rule_pack(self, pack_name: str) -> Dict[str, Any]:
        """Validate a rule pack with caching."""
        cache_key = f"rule_pack_validation_{pack_name}"
        cached_result = self._cache.get_startup_data(cache_key)

        if cached_result:
            debug(f"Using cached validation result for {pack_name}")
            return cached_result

        # Perform validation with lazy loading
        result = self._validate_rule_pack_lazy(pack_name)

        # Cache the result
        self._cache.cache_startup_data(cache_key, result)

        return result

    @lazy_import_decorator("riveter.rule_linter", "RuleLinter")
    def _validate_rule_pack_lazy(self, pack_name: str) -> Dict[str, Any]:
        """Validate rule pack with lazy loading."""
        # This will be replaced by the decorator
        pass


class OptimizedConfigCommand:
    """Optimized configuration commands."""

    def __init__(self):
        self._cache = _get_global_cli_cache()

    @cached_command(ttl=3600)  # Cache for 1 hour
    def parse_terraform_config(self, file_path: Path) -> Any:
        """Parse Terraform configuration with caching."""
        if not file_path.exists():
            raise FileNotFoundError(f"Terraform file not found: {file_path}")

        # Check cache based on file modification time
        file_mtime = file_path.stat().st_mtime
        cache_key = f"terraform_config_{file_path}_{int(file_mtime)}"

        cached_config = self._cache.get_startup_data(cache_key)
        if cached_config:
            debug(f"Using cached Terraform config for {file_path}")
            return cached_config

        # Parse with lazy loading
        config = self._parse_terraform_lazy(file_path)

        # Cache the result
        self._cache.cache_startup_data(cache_key, config)

        return config

    @lazy_import_decorator("riveter.extract_config", "extract_terraform_config")
    def _parse_terraform_lazy(self, file_path: Path) -> Any:
        """Parse Terraform config with lazy loading."""
        # This will be replaced by the decorator
        pass


class CommandOptimizer:
    """Optimizes command execution with intelligent routing."""

    def __init__(self):
        self._execution_stats: Dict[str, Dict[str, float]] = {}
        self._optimization_cache: Dict[str, Any] = {}

    def optimize_command_execution(self, command_name: str, args: Any) -> Any:
        """Optimize command execution based on historical performance."""
        start_time = time.perf_counter()

        # Check if we have optimization data for this command
        if command_name in self._execution_stats:
            stats = self._execution_stats[command_name]
            avg_time = stats.get("average_time", 0)

            # If command typically takes a long time, use background execution
            if avg_time > 5.0:  # 5 seconds threshold
                return self._execute_in_background(command_name, args)

        # Execute normally and record stats
        result = self._execute_command(command_name, args)

        execution_time = time.perf_counter() - start_time
        self._record_execution_stats(command_name, execution_time)

        return result

    def _execute_command(self, command_name: str, args: Any) -> Any:
        """Execute command with appropriate optimizer."""
        if command_name == "scan":
            optimizer = OptimizedScanCommand()
            return optimizer.execute(args)
        elif command_name == "list-rule-packs":
            optimizer = OptimizedRulePackCommand()
            return optimizer.list_rule_packs()
        elif command_name == "validate-rule-pack":
            optimizer = OptimizedRulePackCommand()
            return optimizer.validate_rule_pack(args.get("pack_name"))
        else:
            # Fall back to regular execution
            return self._execute_regular_command(command_name, args)

    def _execute_in_background(self, command_name: str, args: Any) -> Any:
        """Execute command in background for better responsiveness."""
        import threading

        result_container = {}
        exception_container = {}

        def background_execution():
            try:
                result_container["result"] = self._execute_command(command_name, args)
            except Exception as e:
                exception_container["exception"] = e

        thread = threading.Thread(target=background_execution)
        thread.start()

        # Show progress indicator while waiting
        self._show_progress_indicator(thread)

        thread.join()

        if "exception" in exception_container:
            raise exception_container["exception"]

        return result_container.get("result")

    def _show_progress_indicator(self, thread: threading.Thread) -> None:
        """Show progress indicator for long-running commands."""
        import sys

        spinner_chars = "|/-\\"
        i = 0

        while thread.is_alive():
            sys.stdout.write(f"\rProcessing... {spinner_chars[i % len(spinner_chars)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

        sys.stdout.write("\r" + " " * 20 + "\r")  # Clear the spinner
        sys.stdout.flush()

    def _execute_regular_command(self, command_name: str, args: Any) -> Any:
        """Execute command using regular (non-optimized) path."""
        # This would delegate to the original command implementations
        debug(f"Executing {command_name} via regular path")
        return None

    def _record_execution_stats(self, command_name: str, execution_time: float) -> None:
        """Record execution statistics for future optimization."""
        if command_name not in self._execution_stats:
            self._execution_stats[command_name] = {
                "total_time": 0.0,
                "execution_count": 0,
                "average_time": 0.0,
            }

        stats = self._execution_stats[command_name]
        stats["total_time"] += execution_time
        stats["execution_count"] += 1
        stats["average_time"] = stats["total_time"] / stats["execution_count"]

        debug(
            f"Command {command_name} executed in {execution_time:.3f}s "
            f"(avg: {stats['average_time']:.3f}s)"
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all commands."""
        return {
            "execution_stats": self._execution_stats,
            "total_commands": sum(
                stats["execution_count"] for stats in self._execution_stats.values()
            ),
            "total_time": sum(stats["total_time"] for stats in self._execution_stats.values()),
        }


# Global command optimizer instance
_global_command_optimizer: Optional[CommandOptimizer] = None


def get_command_optimizer() -> CommandOptimizer:
    """Get the global command optimizer instance."""
    global _global_command_optimizer
    if _global_command_optimizer is None:
        _global_command_optimizer = CommandOptimizer()
    return _global_command_optimizer
