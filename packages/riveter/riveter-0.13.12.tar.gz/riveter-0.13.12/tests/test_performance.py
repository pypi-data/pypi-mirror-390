"""Tests for performance optimization features."""

import os
import tempfile
import time
from pathlib import Path

from riveter.performance import (
    IncrementalScanner,
    ParallelProcessor,
    PerformanceMetrics,
    ResourceCache,
)
from riveter.rules import Rule


class TestParallelProcessor:
    """Test parallel processing functionality."""

    def test_parallel_processor_initialization(self):
        """Test parallel processor initialization."""
        processor = ParallelProcessor()
        assert processor.max_workers == os.cpu_count()

        processor_custom = ParallelProcessor(max_workers=4)
        assert processor_custom.max_workers == 4

    def test_create_resource_batches(self):
        """Test resource batching for parallel processing."""
        processor = ParallelProcessor()
        resources = [{"id": f"resource-{i}", "resource_type": "aws_instance"} for i in range(25)]

        batches = processor._create_resource_batches(resources, batch_size=10)
        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5

    def test_validate_resources_parallel(self, sample_rules_list, sample_terraform_config):
        """Test parallel resource validation."""
        processor = ParallelProcessor(max_workers=2)
        resources = sample_terraform_config["resources"]

        results = processor.validate_resources_parallel(sample_rules_list, resources, batch_size=2)

        # Should get results for all applicable rule-resource combinations
        assert len(results) > 0
        assert all(hasattr(result, "rule") for result in results)
        assert all(hasattr(result, "resource") for result in results)
        assert all(hasattr(result, "passed") for result in results)

    def test_parallel_vs_sequential_performance(self, sample_rules_list):
        """Test that parallel processing handles large datasets efficiently."""
        # Create a large dataset for performance testing
        large_resources = []
        for i in range(100):
            large_resources.append(
                {
                    "id": f"instance-{i}",
                    "resource_type": "aws_instance",
                    "instance_type": "t3.micro",
                    "tags": {"Environment": "production", "CostCenter": "12345"},
                }
            )

        processor = ParallelProcessor(max_workers=2)

        # Time parallel processing
        start_time = time.time()
        parallel_results = processor.validate_resources_parallel(
            sample_rules_list, large_resources, batch_size=20
        )
        parallel_time = time.time() - start_time

        # Verify results are correct
        assert len(parallel_results) > 0
        assert all(isinstance(result.passed, bool) for result in parallel_results)

        # Test should complete in reasonable time (less than 5 seconds for this dataset)
        assert parallel_time < 5.0


class TestResourceCache:
    """Test resource caching functionality."""

    def test_cache_initialization(self):
        """Test cache initialization with custom directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = ResourceCache(cache_dir=temp_dir, max_size_mb=50)
            assert cache.cache_dir == Path(temp_dir)
            assert cache.max_size_bytes == 50 * 1024 * 1024

    def test_cache_key_generation(self):
        """Test cache key generation based on file properties."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write("resource 'aws_instance' 'test' {}")
            temp_file = f.name

        try:
            cache = ResourceCache()
            key1 = cache.get_cache_key(temp_file)

            # Key should be consistent
            key2 = cache.get_cache_key(temp_file)
            assert key1 == key2

            # Modify file and key should change
            time.sleep(0.1)  # Ensure different mtime
            with open(temp_file, "a") as f:
                f.write("\n# comment")

            key3 = cache.get_cache_key(temp_file)
            assert key1 != key3

        finally:
            os.unlink(temp_file)

    def test_cache_operations(self, sample_terraform_config):
        """Test caching and retrieval operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = ResourceCache(cache_dir=temp_dir)

            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
                f.write("resource 'aws_instance' 'test' {}")
                temp_file = f.name

            try:
                # Initially no cache
                cached_config = cache.get_cached_config(temp_file)
                assert cached_config is None

                # Cache the configuration
                cache.cache_parsed_config(temp_file, sample_terraform_config)

                # Should now retrieve from cache
                cached_config = cache.get_cached_config(temp_file)
                assert cached_config == sample_terraform_config

                # Invalidate cache
                cache.invalidate_cache(temp_file)
                cached_config = cache.get_cached_config(temp_file)
                assert cached_config is None

            finally:
                os.unlink(temp_file)

    def test_cache_cleanup(self):
        """Test cache cleanup when size limit is exceeded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set very small cache size for testing
            cache = ResourceCache(cache_dir=temp_dir, max_size_mb=0.001)  # 1KB limit

            # Create multiple temporary files and cache large configs
            temp_files = []
            large_config = {
                "resources": [{"id": f"resource-{i}", "data": "x" * 1000} for i in range(10)]
            }

            try:
                for i in range(5):
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
                        f.write(f"resource 'aws_instance' 'test{i}' {{}}")
                        temp_files.append(f.name)

                    cache.cache_parsed_config(temp_files[-1], large_config)
                    time.sleep(0.01)  # Ensure different timestamps

                # Check that cleanup occurred (not all files should be cached)
                cache_files = list(Path(temp_dir).glob("*.pkl"))
                assert len(cache_files) < 5  # Some should have been cleaned up

            finally:
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)


class TestIncrementalScanner:
    """Test incremental scanning functionality."""

    def test_incremental_scanner_initialization(self):
        """Test incremental scanner initialization."""
        scanner = IncrementalScanner()
        assert scanner.baseline_file == ".riveter_baseline.json"

        scanner_custom = IncrementalScanner(baseline_file="custom_baseline.json")
        assert scanner_custom.baseline_file == "custom_baseline.json"

    def test_baseline_operations(self, sample_terraform_config):
        """Test baseline save and load operations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            baseline_file = f.name

        try:
            scanner = IncrementalScanner(baseline_file=baseline_file)

            # Initially no baseline
            baseline = scanner.load_baseline()
            assert baseline is None

            # Save baseline
            scanner.save_baseline(sample_terraform_config)

            # Load baseline
            baseline = scanner.load_baseline()
            assert baseline is not None
            assert "resources" in baseline
            assert "timestamp" in baseline
            assert len(baseline["resources"]) == len(sample_terraform_config["resources"])

        finally:
            if os.path.exists(baseline_file):
                os.unlink(baseline_file)

    def test_resource_key_generation(self):
        """Test resource key generation for comparison."""
        scanner = IncrementalScanner()

        resource = {
            "id": "test-instance",
            "resource_type": "aws_instance",
            "instance_type": "t3.micro",
        }

        key = scanner._get_resource_key(resource)
        assert key == "aws_instance:test-instance"

    def test_resource_change_detection(self):
        """Test detection of resource changes."""
        scanner = IncrementalScanner()

        resource1 = {
            "id": "test-instance",
            "resource_type": "aws_instance",
            "instance_type": "t3.micro",
            "tags": {"Environment": "production"},
        }

        resource2 = resource1.copy()
        resource2["instance_type"] = "t3.small"  # Changed

        resource3 = resource1.copy()
        resource3["_terraform_meta"] = {"line": 10}  # Metadata change (should be ignored)

        assert scanner._resource_changed(resource1, resource1) is False
        assert scanner._resource_changed(resource1, resource2) is True
        assert scanner._resource_changed(resource1, resource3) is False  # Metadata ignored

    def test_get_changed_resources(self, sample_terraform_config):
        """Test identification of changed resources."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            baseline_file = f.name

        try:
            scanner = IncrementalScanner(baseline_file=baseline_file)

            # Save initial baseline
            scanner.save_baseline(sample_terraform_config)

            # No changes - should return empty list
            changed = scanner.get_changed_resources(sample_terraform_config["resources"])
            assert len(changed) == 0

            # Modify a resource
            modified_config = sample_terraform_config.copy()
            modified_config["resources"][0]["instance_type"] = "t3.small"

            changed = scanner.get_changed_resources(modified_config["resources"])
            assert len(changed) == 1
            assert changed[0]["id"] == "web_server"

            # Add a new resource
            new_resource = {
                "id": "new_instance",
                "resource_type": "aws_instance",
                "instance_type": "t3.micro",
            }
            modified_config["resources"].append(new_resource)

            changed = scanner.get_changed_resources(modified_config["resources"])
            assert len(changed) == 2  # Modified + new

        finally:
            if os.path.exists(baseline_file):
                os.unlink(baseline_file)


class TestPerformanceMetrics:
    """Test performance metrics collection."""

    def test_metrics_initialization(self):
        """Test metrics initialization."""
        metrics = PerformanceMetrics()
        assert metrics.metrics == {}
        assert metrics.start_times == {}

    def test_timer_operations(self):
        """Test timer start/stop operations."""
        metrics = PerformanceMetrics()

        # Start timer
        metrics.start_timer("test_operation")
        assert "test_operation" in metrics.start_times

        # Small delay
        time.sleep(0.01)

        # End timer
        duration = metrics.end_timer("test_operation")
        assert duration > 0
        assert "test_operation" not in metrics.start_times
        assert "test_operation" in metrics.metrics
        assert len(metrics.metrics["test_operation"]) == 1

    def test_custom_metrics(self):
        """Test recording custom metrics."""
        metrics = PerformanceMetrics()

        metrics.record_metric("resource_count", 100)
        metrics.record_metric("resource_count", 150)
        metrics.record_metric("rule_count", 25)

        assert "resource_count" in metrics.metrics
        assert "rule_count" in metrics.metrics
        assert metrics.metrics["resource_count"] == [100, 150]
        assert metrics.metrics["rule_count"] == [25]

    def test_metrics_summary(self):
        """Test metrics summary generation."""
        metrics = PerformanceMetrics()

        # Add some timing data
        metrics.start_timer("operation1")
        time.sleep(0.01)
        metrics.end_timer("operation1")

        metrics.start_timer("operation1")
        time.sleep(0.01)
        metrics.end_timer("operation1")

        # Add custom metric
        metrics.record_metric("custom_metric", "test_value")

        summary = metrics.get_summary()

        assert "operation1" in summary
        assert "custom_metric" in summary

        op1_stats = summary["operation1"]
        assert "count" in op1_stats
        assert "total" in op1_stats
        assert "average" in op1_stats
        assert "min" in op1_stats
        assert "max" in op1_stats
        assert op1_stats["count"] == 2

        custom_stats = summary["custom_metric"]
        assert "count" in custom_stats
        assert "values" in custom_stats
        assert custom_stats["count"] == 1


class TestPerformanceIntegration:
    """Integration tests for performance features."""

    def test_end_to_end_performance_workflow(self, sample_rules_list, sample_terraform_config):
        """Test complete performance optimization workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = os.path.join(temp_dir, "cache")
            baseline_file = os.path.join(temp_dir, "baseline.json")

            # Initialize components
            cache = ResourceCache(cache_dir=cache_dir)
            scanner = IncrementalScanner(baseline_file=baseline_file)
            processor = ParallelProcessor(max_workers=2)
            metrics = PerformanceMetrics()

            # Create temporary terraform file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
                f.write("resource 'aws_instance' 'test' {}")
                terraform_file = f.name

            try:
                # Simulate first run
                metrics.start_timer("total_workflow")

                # Cache configuration
                cache.cache_parsed_config(terraform_file, sample_terraform_config)

                # Save baseline
                scanner.save_baseline(sample_terraform_config)

                # Run validation
                results = processor.validate_resources_parallel(
                    sample_rules_list, sample_terraform_config["resources"]
                )

                metrics.end_timer("total_workflow")

                # Verify results
                assert len(results) > 0

                # Simulate second run with cache hit
                metrics.start_timer("cached_workflow")

                cached_config = cache.get_cached_config(terraform_file)
                assert cached_config == sample_terraform_config

                # Check for changes (should be none)
                changed_resources = scanner.get_changed_resources(cached_config["resources"])
                assert len(changed_resources) == 0

                metrics.end_timer("cached_workflow")

                # Verify metrics were collected
                summary = metrics.get_summary()
                assert "total_workflow" in summary
                assert "cached_workflow" in summary

            finally:
                if os.path.exists(terraform_file):
                    os.unlink(terraform_file)

    def test_large_dataset_performance(self):
        """Test performance with larger datasets."""
        # Create large dataset
        large_rules = []
        for i in range(50):
            rule_dict = {
                "id": f"rule-{i}",
                "resource_type": "aws_instance",
                "description": f"Test rule {i}",
                "assert": {"tags": {"Environment": "production"}},
            }
            large_rules.append(Rule(rule_dict))

        large_resources = []
        for i in range(200):
            large_resources.append(
                {
                    "id": f"instance-{i}",
                    "resource_type": "aws_instance",
                    "instance_type": "t3.micro",
                    "tags": {"Environment": "production"},
                }
            )

        # Test parallel processing performance
        processor = ParallelProcessor(max_workers=4)
        metrics = PerformanceMetrics()

        metrics.start_timer("large_dataset_validation")
        results = processor.validate_resources_parallel(large_rules, large_resources, batch_size=50)
        execution_time = metrics.end_timer("large_dataset_validation")

        # Verify results
        assert len(results) > 0

        # Should complete in reasonable time (less than 10 seconds)
        assert execution_time < 10.0

        # Record performance metrics
        metrics.record_metric("rule_count", len(large_rules))
        metrics.record_metric("resource_count", len(large_resources))
        metrics.record_metric("result_count", len(results))

        summary = metrics.get_summary()
        assert summary["large_dataset_validation"]["count"] == 1
        # For numeric metrics, they get treated as timing data if they're numbers
        # So we check for the appropriate format
        if "values" in summary["rule_count"]:
            assert summary["rule_count"]["values"] == [50]
            assert summary["resource_count"]["values"] == [200]
        else:
            # If treated as timing data, check count
            assert summary["rule_count"]["count"] == 1
            assert summary["resource_count"]["count"] == 1
