"""Memory optimization system for CLI operations."""

import gc
import sys
import weakref
from typing import Any, Dict, List, Optional, Set

from ..logging import debug, warning


class MemoryOptimizer:
    """Optimizes memory usage for CLI operations."""

    def __init__(self):
        self._object_pool: Dict[str, List[Any]] = {}
        self._weak_references: Set[weakref.ref] = set()
        self._memory_threshold = 100 * 1024 * 1024  # 100MB
        self._cleanup_enabled = True

    def get_pooled_object(self, object_type: str, factory_func: callable) -> Any:
        """Get an object from the pool or create a new one."""
        if object_type not in self._object_pool:
            self._object_pool[object_type] = []

        pool = self._object_pool[object_type]

        if pool:
            obj = pool.pop()
            debug(f"Reused pooled object of type {object_type}")
            return obj
        else:
            obj = factory_func()
            debug(f"Created new object of type {object_type}")
            return obj

    def return_to_pool(self, object_type: str, obj: Any) -> None:
        """Return an object to the pool for reuse."""
        if object_type not in self._object_pool:
            self._object_pool[object_type] = []

        # Clean the object if it has a cleanup method
        if hasattr(obj, "cleanup"):
            obj.cleanup()

        self._object_pool[object_type].append(obj)
        debug(f"Returned object of type {object_type} to pool")

    def register_weak_reference(self, obj: Any) -> weakref.ref:
        """Register a weak reference for automatic cleanup."""

        def cleanup_callback(ref):
            self._weak_references.discard(ref)

        weak_ref = weakref.ref(obj, cleanup_callback)
        self._weak_references.add(weak_ref)
        return weak_ref

    def force_garbage_collection(self) -> Dict[str, int]:
        """Force garbage collection and return statistics."""
        # Clear weak references to dead objects
        dead_refs = [ref for ref in self._weak_references if ref() is None]
        for ref in dead_refs:
            self._weak_references.discard(ref)

        # Force garbage collection
        collected = gc.collect()

        # Get memory statistics
        stats = {
            "objects_collected": collected,
            "weak_references": len(self._weak_references),
            "pooled_objects": sum(len(pool) for pool in self._object_pool.values()),
        }

        debug(f"Garbage collection: {collected} objects collected")
        return stats

    def check_memory_usage(self) -> bool:
        """Check if memory usage is above threshold."""
        try:
            import psutil

            process = psutil.Process()
            memory_usage = process.memory_info().rss

            if memory_usage > self._memory_threshold:
                warning(
                    f"Memory usage ({memory_usage / 1024 / 1024:.1f}MB) "
                    f"above threshold ({self._memory_threshold / 1024 / 1024:.1f}MB)"
                )
                return True
        except ImportError:
            # psutil not available, use basic check
            pass

        return False

    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization."""
        if not self._cleanup_enabled:
            return {"status": "disabled"}

        initial_objects = len(gc.get_objects())

        # Clear object pools if memory is high
        if self.check_memory_usage():
            self.clear_object_pools()

        # Force garbage collection
        gc_stats = self.force_garbage_collection()

        final_objects = len(gc.get_objects())

        return {
            "status": "completed",
            "initial_objects": initial_objects,
            "final_objects": final_objects,
            "objects_freed": initial_objects - final_objects,
            "gc_stats": gc_stats,
        }

    def clear_object_pools(self) -> int:
        """Clear all object pools."""
        total_cleared = sum(len(pool) for pool in self._object_pool.values())
        self._object_pool.clear()
        debug(f"Cleared {total_cleared} objects from pools")
        return total_cleared

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        stats = {
            "object_pools": {pool_type: len(pool) for pool_type, pool in self._object_pool.items()},
            "weak_references": len(self._weak_references),
            "gc_objects": len(gc.get_objects()),
        }

        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            stats["memory_usage"] = {
                "rss": memory_info.rss,
                "vms": memory_info.vms,
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
            }
        except ImportError:
            stats["memory_usage"] = {"error": "psutil not available"}

        return stats

    def enable_automatic_cleanup(self, enable: bool = True) -> None:
        """Enable or disable automatic memory cleanup."""
        self._cleanup_enabled = enable
        debug(f"Automatic memory cleanup {'enabled' if enable else 'disabled'}")

    def set_memory_threshold(self, threshold_mb: int) -> None:
        """Set memory usage threshold in MB."""
        self._memory_threshold = threshold_mb * 1024 * 1024
        debug(f"Memory threshold set to {threshold_mb}MB")


class LazyObjectFactory:
    """Factory for creating objects only when needed."""

    def __init__(self):
        self._factories: Dict[str, callable] = {}
        self._instances: Dict[str, Any] = {}
        self._memory_optimizer = MemoryOptimizer()

    def register_factory(self, name: str, factory_func: callable) -> None:
        """Register a factory function for lazy object creation."""
        self._factories[name] = factory_func
        debug(f"Registered lazy factory for {name}")

    def get_instance(self, name: str, *args, **kwargs) -> Any:
        """Get an instance, creating it lazily if needed."""
        if name not in self._instances:
            if name not in self._factories:
                raise ValueError(f"No factory registered for {name}")

            factory_func = self._factories[name]
            instance = factory_func(*args, **kwargs)
            self._instances[name] = instance

            # Register for memory management
            self._memory_optimizer.register_weak_reference(instance)

            debug(f"Created lazy instance of {name}")

        return self._instances[name]

    def clear_instance(self, name: str) -> bool:
        """Clear a specific instance."""
        if name in self._instances:
            del self._instances[name]
            debug(f"Cleared lazy instance of {name}")
            return True
        return False

    def clear_all_instances(self) -> int:
        """Clear all instances."""
        count = len(self._instances)
        self._instances.clear()
        debug(f"Cleared {count} lazy instances")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get factory statistics."""
        return {
            "registered_factories": len(self._factories),
            "active_instances": len(self._instances),
            "factory_names": list(self._factories.keys()),
            "instance_names": list(self._instances.keys()),
        }


class MemoryEfficientDataStructures:
    """Memory-efficient data structures for CLI operations."""

    @staticmethod
    def create_efficient_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a memory-efficient dictionary."""
        # Use __slots__ for better memory efficiency if possible
        if len(data) > 100:  # Only for larger dictionaries
            # Convert to a more memory-efficient structure
            return {k: v for k, v in data.items() if v is not None}
        return data

    @staticmethod
    def create_efficient_list(data: List[Any]) -> List[Any]:
        """Create a memory-efficient list."""
        # Remove None values and duplicates if beneficial
        if len(data) > 100:
            seen = set()
            result = []
            for item in data:
                if item is not None and item not in seen:
                    seen.add(item)
                    result.append(item)
            return result
        return data

    @staticmethod
    def compress_string_data(data: str) -> bytes:
        """Compress string data for memory efficiency."""
        if len(data) > 1024:  # Only compress larger strings
            import gzip

            return gzip.compress(data.encode("utf-8"))
        return data.encode("utf-8")

    @staticmethod
    def decompress_string_data(data: bytes) -> str:
        """Decompress string data."""
        try:
            import gzip

            return gzip.decompress(data).decode("utf-8")
        except:
            return data.decode("utf-8")


# Global instances
_global_memory_optimizer: Optional[MemoryOptimizer] = None
_global_lazy_factory: Optional[LazyObjectFactory] = None


def get_memory_optimizer() -> MemoryOptimizer:
    """Get the global memory optimizer instance."""
    global _global_memory_optimizer
    if _global_memory_optimizer is None:
        _global_memory_optimizer = MemoryOptimizer()
    return _global_memory_optimizer


def get_lazy_factory() -> LazyObjectFactory:
    """Get the global lazy object factory instance."""
    global _global_lazy_factory
    if _global_lazy_factory is None:
        _global_lazy_factory = LazyObjectFactory()
    return _global_lazy_factory


def setup_memory_optimizations():
    """Set up memory optimizations for CLI."""
    optimizer = get_memory_optimizer()
    factory = get_lazy_factory()

    # Register common object factories
    factory.register_factory("scanner", lambda: _create_scanner())
    factory.register_factory("rule_manager", lambda: _create_rule_manager())
    factory.register_factory("config_parser", lambda: _create_config_parser())

    # Enable automatic cleanup
    optimizer.enable_automatic_cleanup(True)

    debug("Memory optimizations set up")
    return optimizer, factory


def _create_scanner():
    """Factory function for scanner."""
    from ..scanner import Scanner

    return Scanner()


def _create_rule_manager():
    """Factory function for rule manager."""
    from ..rule_packs import RulePackManager

    return RulePackManager()


def _create_config_parser():
    """Factory function for config parser."""
    from ..extract_config import ConfigExtractor

    return ConfigExtractor()


def optimize_cli_memory():
    """Optimize CLI memory usage."""
    optimizer = get_memory_optimizer()
    return optimizer.optimize_memory()
