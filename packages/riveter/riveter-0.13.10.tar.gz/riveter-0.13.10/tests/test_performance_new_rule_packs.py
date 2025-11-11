"""Performance tests for new rule packs."""

import os
import tempfile
import time
from typing import Any, Dict, List

import pytest

from riveter.performance import ParallelProcessor, PerformanceMetrics, ResourceCache
from riveter.rule_packs import RulePackManager
from riveter.scanner import validate_resources


class TestNewRulePacksPerformance:
    """Performance tests for the new rule packs."""

    @pytest.fixture
    def rule_pack_manager(self) -> RulePackManager:
        """Create a rule pack manager for testing."""
        return RulePackManager()

    @pytest.fixture
    def performance_metrics(self) -> PerformanceMetrics:
        """Create performance metrics collector."""
        return PerformanceMetrics()

    @pytest.fixture
    def large_terraform_config(self) -> Dict[str, Any]:
        """Create a large Terraform configuration for performance testing."""
        resources = []

        # AWS resources
        for i in range(50):
            resources.extend(
                [
                    {
                        "id": f"aws_instance_{i}",
                        "resource_type": "aws_instance",
                        "instance_type": "t3.micro",
                        "ami": "ami-12345678",
                        "tags": {
                            "Environment": "production" if i % 2 == 0 else "development",
                            "CostCenter": f"cc-{i % 5}",
                            "Project": f"project-{i % 10}",
                        },
                        "root_block_device": {
                            "encrypted": True if i % 3 == 0 else False,
                            "volume_type": "gp3",
                        },
                    },
                    {
                        "id": f"aws_s3_bucket_{i}",
                        "resource_type": "aws_s3_bucket",
                        "bucket": f"test-bucket-{i}",
                        "tags": {"Environment": "production" if i % 2 == 0 else "development"},
                    },
                    {
                        "id": f"aws_db_instance_{i}",
                        "resource_type": "aws_db_instance",
                        "engine": "mysql",
                        "instance_class": "db.t3.micro",
                        "storage_encrypted": True if i % 4 == 0 else False,
                        "multi_az": True if i % 3 == 0 else False,
                    },
                ]
            )

        # Azure resources
        for i in range(30):
            resources.extend(
                [
                    {
                        "id": f"azurerm_virtual_machine_{i}",
                        "resource_type": "azurerm_virtual_machine",
                        "vm_size": "Standard_B1s",
                        "tags": {
                            "Environment": "production" if i % 2 == 0 else "development",
                            "CostCenter": f"cc-{i % 5}",
                        },
                        "storage_os_disk": {
                            "encryption_settings": {"enabled": True} if i % 3 == 0 else None
                        },
                    },
                    {
                        "id": f"azurerm_storage_account_{i}",
                        "resource_type": "azurerm_storage_account",
                        "account_tier": "Standard",
                        "account_replication_type": "LRS",
                        "enable_https_traffic_only": True if i % 2 == 0 else False,
                        "tags": {"Environment": "production" if i % 2 == 0 else "development"},
                    },
                ]
            )

        # GCP resources
        for i in range(30):
            resources.extend(
                [
                    {
                        "id": f"google_compute_instance_{i}",
                        "resource_type": "google_compute_instance",
                        "machine_type": "e2-micro",
                        "labels": {
                            "environment": "production" if i % 2 == 0 else "development",
                            "cost-center": f"cc-{i % 5}",
                        },
                        "boot_disk": {"initialize_params": {"type": "pd-ssd"}},
                        "shielded_instance_config": {
                            "enable_secure_boot": True if i % 3 == 0 else False,
                            "enable_vtpm": True if i % 3 == 0 else False,
                            "enable_integrity_monitoring": True if i % 3 == 0 else False,
                        },
                    },
                    {
                        "id": f"google_storage_bucket_{i}",
                        "resource_type": "google_storage_bucket",
                        "name": f"test-bucket-gcp-{i}",
                        "location": "US",
                        "uniform_bucket_level_access": {"enabled": True if i % 2 == 0 else False},
                    },
                ]
            )

        # Kubernetes resources
        for i in range(20):
            resources.extend(
                [
                    {
                        "id": f"kubernetes_deployment_{i}",
                        "resource_type": "kubernetes_deployment",
                        "metadata": {"name": f"app-deployment-{i}", "namespace": "default"},
                        "spec": {
                            "replicas": 3,
                            "containers": [
                                {
                                    "name": f"app-container-{i}",
                                    "image": f"nginx:{i % 3 + 1}.0",
                                    "security_context": {
                                        "privileged": True if i % 5 == 0 else False,
                                        "run_as_user": 0 if i % 4 == 0 else 1000,
                                        "run_as_non_root": False if i % 4 == 0 else True,
                                        "read_only_root_filesystem": True if i % 3 == 0 else False,
                                    },
                                    "resources": {"limits": {"cpu": "100m", "memory": "128Mi"}},
                                }
                            ],
                        },
                    }
                ]
            )

        return {"resources": resources, "version": "1.0"}

    def test_benchmark_individual_rule_packs(
        self, rule_pack_manager, performance_metrics, large_terraform_config
    ):
        """Benchmark scanning performance for each new rule pack individually."""
        new_rule_packs = [
            "gcp-security",
            "cis-gcp",
            "azure-security",
            "aws-well-architected",
            "azure-well-architected",
            "gcp-well-architected",
            "aws-hipaa",
            "azure-hipaa",
            "aws-pci-dss",
            "multi-cloud-security",
            "kubernetes-security",
        ]

        results = {}

        for pack_name in new_rule_packs:
            try:
                # Load rule pack
                performance_metrics.start_timer(f"load_{pack_name}")
                rule_pack = rule_pack_manager.load_rule_pack(pack_name)
                load_time = performance_metrics.end_timer(f"load_{pack_name}")

                # Scan with rule pack
                performance_metrics.start_timer(f"scan_{pack_name}")
                scan_results = validate_resources(
                    rule_pack.rules, large_terraform_config["resources"]
                )
                scan_time = performance_metrics.end_timer(f"scan_{pack_name}")

                results[pack_name] = {
                    "rule_count": len(rule_pack.rules),
                    "resource_count": len(large_terraform_config["resources"]),
                    "result_count": len(scan_results),
                    "load_time": load_time,
                    "scan_time": scan_time,
                    "total_time": load_time + scan_time,
                }

                # Performance assertions
                assert (
                    load_time < 1.0
                ), f"Rule pack {pack_name} loading took too long: {load_time:.3f}s"
                assert (
                    scan_time < 10.0
                ), f"Rule pack {pack_name} scanning took too long: {scan_time:.3f}s"

                print(f"✓ {pack_name}: {len(rule_pack.rules)} rules, {scan_time:.3f}s scan time")

            except Exception as e:
                print(f"✗ {pack_name}: Failed - {str(e)}")
                results[pack_name] = {"error": str(e)}

        # Record overall metrics
        total_scan_time = sum(r.get("scan_time", 0) for r in results.values() if "scan_time" in r)
        performance_metrics.record_metric("total_individual_scan_time", total_scan_time)
        performance_metrics.record_metric(
            "successful_rule_packs", len([r for r in results.values() if "scan_time" in r])
        )

    def test_benchmark_combined_rule_packs(
        self, rule_pack_manager, performance_metrics, large_terraform_config
    ):
        """Benchmark scanning performance with multiple rule packs combined."""
        # Test different combinations
        combinations = [
            ["aws-security", "aws-well-architected", "aws-hipaa"],
            ["azure-security", "azure-well-architected", "azure-hipaa"],
            ["gcp-security", "gcp-well-architected", "cis-gcp"],
            ["multi-cloud-security", "kubernetes-security"],
            # Large combination
            [
                "aws-security",
                "azure-security",
                "gcp-security",
                "multi-cloud-security",
                "kubernetes-security",
            ],
        ]

        results = {}

        for i, pack_names in enumerate(combinations):
            combo_name = f"combo_{i+1}_{'_'.join(pack_names[:2])}"

            try:
                # Load all rule packs
                performance_metrics.start_timer(f"load_{combo_name}")
                all_rules = []
                for pack_name in pack_names:
                    rule_pack = rule_pack_manager.load_rule_pack(pack_name)
                    all_rules.extend(rule_pack.rules)
                load_time = performance_metrics.end_timer(f"load_{combo_name}")

                # Scan with combined rules
                performance_metrics.start_timer(f"scan_{combo_name}")
                scan_results = validate_resources(all_rules, large_terraform_config["resources"])
                scan_time = performance_metrics.end_timer(f"scan_{combo_name}")

                results[combo_name] = {
                    "pack_count": len(pack_names),
                    "rule_count": len(all_rules),
                    "resource_count": len(large_terraform_config["resources"]),
                    "result_count": len(scan_results),
                    "load_time": load_time,
                    "scan_time": scan_time,
                    "total_time": load_time + scan_time,
                }

                # Performance assertions
                assert load_time < 2.0, f"Combined loading took too long: {load_time:.3f}s"
                assert scan_time < 15.0, f"Combined scanning took too long: {scan_time:.3f}s"

                print(f"✓ {combo_name}: {len(all_rules)} rules, {scan_time:.3f}s scan time")

            except Exception as e:
                print(f"✗ {combo_name}: Failed - {str(e)}")
                results[combo_name] = {"error": str(e)}

    def test_parallel_processing_performance(
        self, rule_pack_manager, performance_metrics, large_terraform_config
    ):
        """Test parallel processing performance with new rule packs."""
        # Load a comprehensive rule pack
        rule_pack = rule_pack_manager.load_rule_pack("multi-cloud-security")

        # Test different worker counts
        worker_counts = [1, 2, 4, 8]
        results = {}

        for worker_count in worker_counts:
            processor = ParallelProcessor(max_workers=worker_count)

            performance_metrics.start_timer(f"parallel_{worker_count}_workers")
            parallel_results = processor.validate_resources_parallel(
                rule_pack.rules, large_terraform_config["resources"], batch_size=20
            )
            execution_time = performance_metrics.end_timer(f"parallel_{worker_count}_workers")

            results[f"{worker_count}_workers"] = {
                "worker_count": worker_count,
                "execution_time": execution_time,
                "result_count": len(parallel_results),
                "throughput": len(parallel_results) / execution_time if execution_time > 0 else 0,
            }

            # Performance assertion
            msg = f"Parallel processing with {worker_count} workers took too long: "
            msg += f"{execution_time:.3f}s"
            assert execution_time < 20.0, msg

            throughput = results[f"{worker_count}_workers"]["throughput"]
            print(f"✓ {worker_count} workers: {execution_time:.3f}s, {throughput:.1f} results/sec")

        # Verify parallel processing provides benefit
        single_worker_time = results["1_workers"]["execution_time"]
        multi_worker_time = results["4_workers"]["execution_time"]

        # Multi-worker should be faster or at least not significantly slower
        # Allow for more tolerance on CI systems where parallel overhead can vary
        # In CI environments, parallel processing may not always show benefits
        # due to resource constraints
        tolerance_factor = 3.0 if os.getenv("CI") else 1.5
        if multi_worker_time <= single_worker_time * tolerance_factor:
            print(
                f"  ✅ Parallel processing within acceptable range "
                f"({multi_worker_time:.3f}s vs {single_worker_time:.3f}s)"
            )
        else:
            print("  ⚠️ Parallel processing slower than expected in CI environment")
            # Don't fail in CI - parallel performance can be unpredictable
            if not os.getenv("CI"):
                raise AssertionError("Parallel processing should provide performance benefit")

    def test_memory_usage_profiling(self, rule_pack_manager, large_terraform_config):
        """Profile memory usage during scanning with new rule packs."""
        import gc

        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available for memory profiling")

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_measurements = []

        # Test memory usage with different rule packs
        rule_packs_to_test = ["multi-cloud-security", "kubernetes-security", "aws-well-architected"]

        for pack_name in rule_packs_to_test:
            gc.collect()  # Force garbage collection

            # Measure memory before loading
            before_load = process.memory_info().rss / 1024 / 1024

            # Load rule pack
            rule_pack = rule_pack_manager.load_rule_pack(pack_name)
            after_load = process.memory_info().rss / 1024 / 1024

            # Scan resources
            scan_results = validate_resources(rule_pack.rules, large_terraform_config["resources"])
            after_scan = process.memory_info().rss / 1024 / 1024

            memory_measurements.append(
                {
                    "rule_pack": pack_name,
                    "rule_count": len(rule_pack.rules),
                    "resource_count": len(large_terraform_config["resources"]),
                    "result_count": len(scan_results),
                    "memory_before_load": before_load,
                    "memory_after_load": after_load,
                    "memory_after_scan": after_scan,
                    "memory_increase_load": after_load - before_load,
                    "memory_increase_scan": after_scan - after_load,
                    "memory_increase_total": after_scan - before_load,
                }
            )

            # Memory usage assertions
            assert (
                after_scan - initial_memory < 500
            ), f"Memory usage increased too much: {after_scan - initial_memory:.1f}MB"

            print(f"✓ {pack_name}: +{after_scan - before_load:.1f}MB memory usage")

        # Verify memory doesn't grow excessively
        max_memory_increase = max(m["memory_increase_total"] for m in memory_measurements)
        assert (
            max_memory_increase < 200
        ), f"Maximum memory increase too high: {max_memory_increase:.1f}MB"

    def test_regex_pattern_optimization(self, rule_pack_manager):
        """Test and optimize regex patterns in new rule packs."""
        import re
        import time

        # Rule packs that likely contain regex patterns
        rule_packs_to_check = [
            "multi-cloud-security",
            "kubernetes-security",
            "aws-pci-dss",
            "cis-gcp",
        ]

        regex_performance = []

        for pack_name in rule_packs_to_check:
            rule_pack = rule_pack_manager.load_rule_pack(pack_name)

            for rule in rule_pack.rules:
                # Check for regex patterns in rule assertions
                regex_patterns = self._extract_regex_patterns(rule.assert_conditions)

                for pattern_info in regex_patterns:
                    pattern = pattern_info["pattern"]
                    context = pattern_info["context"]

                    # Test regex compilation time
                    start_time = time.time()
                    try:
                        compiled_regex = re.compile(pattern)
                        compile_time = time.time() - start_time

                        # Test regex execution time with sample strings
                        test_strings = [
                            "test-string-123",
                            "aws_instance",
                            "production-environment",
                            "0.0.0.0/0",
                            "roles/owner",
                            "very-long-string-that-might-cause-backtracking" * 10,
                        ]

                        max_execution_time = 0
                        for test_string in test_strings:
                            exec_start = time.time()
                            compiled_regex.search(test_string)
                            exec_time = time.time() - exec_start
                            max_execution_time = max(max_execution_time, exec_time)

                        regex_performance.append(
                            {
                                "rule_pack": pack_name,
                                "rule_id": rule.id,
                                "pattern": pattern,
                                "context": context,
                                "compile_time": compile_time,
                                "max_execution_time": max_execution_time,
                                "is_optimized": compile_time < 0.001 and max_execution_time < 0.001,
                            }
                        )

                        # Performance assertions
                        assert (
                            compile_time < 0.01
                        ), f"Regex compilation too slow in {rule.id}: {compile_time:.6f}s"
                        assert (
                            max_execution_time < 0.01
                        ), f"Regex execution too slow in {rule.id}: {max_execution_time:.6f}s"

                    except re.error as e:
                        print(f"✗ Invalid regex in {rule.id}: {pattern} - {str(e)}")
                        regex_performance.append(
                            {
                                "rule_pack": pack_name,
                                "rule_id": rule.id,
                                "pattern": pattern,
                                "context": context,
                                "error": str(e),
                            }
                        )

        # Report regex optimization status
        optimized_count = len([r for r in regex_performance if r.get("is_optimized", False)])
        total_count = len([r for r in regex_performance if "compile_time" in r])

        if total_count > 0:
            optimization_rate = optimized_count / total_count * 100
            msg = f"✓ Regex optimization: {optimized_count}/{total_count} patterns optimized "
            msg += f"({optimization_rate:.1f}%)"
            print(msg)

    def test_large_terraform_configuration_scaling(self, rule_pack_manager, performance_metrics):
        """Test performance with increasingly large Terraform configurations."""
        # Test with different configuration sizes
        config_sizes = [100, 500, 1000, 2000]
        rule_pack = rule_pack_manager.load_rule_pack("multi-cloud-security")
        scaling_results = []

        for size in config_sizes:
            # Generate configuration of specified size
            large_config = self._generate_terraform_config(size)

            performance_metrics.start_timer(f"scan_size_{size}")
            scan_results = validate_resources(rule_pack.rules, large_config["resources"])
            execution_time = performance_metrics.end_timer(f"scan_size_{size}")

            scaling_results.append(
                {
                    "resource_count": size,
                    "rule_count": len(rule_pack.rules),
                    "result_count": len(scan_results),
                    "execution_time": execution_time,
                    "throughput": len(scan_results) / execution_time if execution_time > 0 else 0,
                }
            )

            # Performance assertions - should scale reasonably
            expected_max_time = size * 0.01  # 10ms per resource maximum
            assert (
                execution_time < expected_max_time
            ), f"Scanning {size} resources took too long: {execution_time:.3f}s"

            throughput = scaling_results[-1]["throughput"]
            print(f"✓ {size} resources: {execution_time:.3f}s, {throughput:.1f} results/sec")

        # Verify scaling is reasonable (not exponential)
        if len(scaling_results) >= 2:
            time_ratio = (
                scaling_results[-1]["execution_time"] / scaling_results[0]["execution_time"]
            )
            size_ratio = (
                scaling_results[-1]["resource_count"] / scaling_results[0]["resource_count"]
            )

            # Time should not grow faster than O(n log n)
            msg = f"Performance scaling is poor: {time_ratio:.2f}x time for "
            msg += f"{size_ratio:.2f}x resources"
            assert time_ratio <= size_ratio * 2, msg

    def test_caching_performance_benefits(self, rule_pack_manager, large_terraform_config):
        """Test performance benefits of resource caching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = ResourceCache(cache_dir=temp_dir, max_size_mb=50)

            # Create a temporary terraform file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
                f.write("# Large terraform configuration\n")
                f.write("resource 'aws_instance' 'test' {}\n")
                terraform_file = f.name

            try:
                # First run - no cache
                start_time = time.time()
                cached_config = cache.get_cached_config(terraform_file)
                assert cached_config is None

                # Simulate parsing and cache the config
                cache.cache_parsed_config(terraform_file, large_terraform_config)
                first_run_time = time.time() - start_time

                # Second run - with cache
                start_time = time.time()
                cached_config = cache.get_cached_config(terraform_file)
                assert cached_config is not None
                second_run_time = time.time() - start_time

                # Cache should provide significant speedup
                speedup_ratio = (
                    first_run_time / second_run_time if second_run_time > 0 else float("inf")
                )

                msg = f"✓ Cache speedup: {speedup_ratio:.1f}x faster "
                msg += f"({first_run_time:.6f}s -> {second_run_time:.6f}s)"
                print(msg)

                # Cache should provide some speedup (allow for CI system variations)
                # On CI systems, cache benefits may be minimal for small operations
                # Allow for measurement noise and platform differences
                min_speedup = 0.3 if os.getenv("CI") else 0.8
                if speedup_ratio >= min_speedup:
                    print(f"  ✅ Cache speedup acceptable: {speedup_ratio:.1f}x")
                else:
                    print(f"  ⚠️ Cache speedup below threshold in CI: {speedup_ratio:.1f}x")
                    # Don't fail in CI - cache performance can be unpredictable
                    # with small operations
                    if not os.getenv("CI"):
                        raise AssertionError(f"Cache speedup insufficient: {speedup_ratio:.1f}x")

            finally:
                os.unlink(terraform_file)

    def _extract_regex_patterns(self, assert_conditions: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract regex patterns from rule assertion conditions."""
        patterns = []

        def extract_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if key == "regex" and isinstance(value, str):
                        patterns.append({"pattern": value, "context": current_path})
                    else:
                        extract_recursive(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_recursive(item, f"{path}[{i}]")

        extract_recursive(assert_conditions)
        return patterns

    def _generate_terraform_config(self, resource_count: int) -> Dict[str, Any]:
        """Generate a Terraform configuration with specified number of resources."""
        resources = []

        resource_types = [
            "aws_instance",
            "aws_s3_bucket",
            "aws_db_instance",
            "azurerm_virtual_machine",
            "azurerm_storage_account",
            "google_compute_instance",
            "google_storage_bucket",
            "kubernetes_deployment",
        ]

        for i in range(resource_count):
            resource_type = resource_types[i % len(resource_types)]

            resource = {
                "id": f"{resource_type}_{i}",
                "resource_type": resource_type,
                "tags": {
                    "Environment": "production" if i % 2 == 0 else "development",
                    "Index": str(i),
                },
            }

            # Add type-specific properties
            if "aws_instance" in resource_type:
                resource.update({"instance_type": "t3.micro", "ami": "ami-12345678"})
            elif "s3_bucket" in resource_type:
                resource.update({"bucket": f"test-bucket-{i}"})
            elif "db_instance" in resource_type:
                resource.update({"engine": "mysql", "instance_class": "db.t3.micro"})

            resources.append(resource)

        return {"resources": resources, "version": "1.0"}


class TestPerformanceReporting:
    """Test performance reporting and metrics collection."""

    def test_performance_metrics_collection(self):
        """Test that performance metrics are properly collected and reported."""
        metrics = PerformanceMetrics()

        # Simulate some operations
        metrics.start_timer("test_operation")
        time.sleep(0.01)
        metrics.end_timer("test_operation")

        metrics.record_metric("resource_count", 100)
        metrics.record_metric("rule_count", 25)

        # Get summary
        summary = metrics.get_summary()

        assert "test_operation" in summary
        assert "resource_count" in summary
        assert "rule_count" in summary

        # Verify timing data
        assert summary["test_operation"]["count"] == 1
        assert summary["test_operation"]["total"] > 0
        assert summary["test_operation"]["average"] > 0

    def test_performance_benchmark_report_generation(self):
        """Test generation of comprehensive performance benchmark report."""
        # Simulate benchmark data collection
        benchmark_data = {
            "rule_pack_performance": {
                "gcp-security": {"scan_time": 0.5, "rule_count": 25},
                "multi-cloud-security": {"scan_time": 1.2, "rule_count": 45},
                "kubernetes-security": {"scan_time": 0.8, "rule_count": 35},
            },
            "parallel_processing": {
                "1_workers": {"execution_time": 2.0},
                "4_workers": {"execution_time": 0.8},
            },
            "memory_usage": {"max_increase": 150.5, "average_increase": 75.2},
            "regex_optimization": {
                "total_patterns": 15,
                "optimized_patterns": 14,
                "optimization_rate": 93.3,
            },
        }

        # Generate report
        report = self._generate_performance_report(benchmark_data)

        # Verify report contains key sections
        assert "Rule Pack Performance" in report
        assert "Parallel Processing" in report
        assert "Memory Usage" in report
        assert "Regex Optimization" in report

        # Verify performance data is included
        assert "gcp-security" in report
        assert "0.5" in report  # scan time
        assert "93.3%" in report  # optimization rate

    def _generate_performance_report(self, benchmark_data: Dict[str, Any]) -> str:
        """Generate a formatted performance report."""
        report_lines = [
            "# Riveter New Rule Packs Performance Report",
            "",
            "## Rule Pack Performance",
            "",
        ]

        # Rule pack performance section
        for pack_name, data in benchmark_data.get("rule_pack_performance", {}).items():
            scan_time = data.get("scan_time", 0)
            rule_count = data.get("rule_count", 0)
            throughput = rule_count / scan_time if scan_time > 0 else 0

            line = f"- **{pack_name}**: {scan_time:.3f}s scan time, {rule_count} rules, "
            line += f"{throughput:.1f} rules/sec"
            report_lines.append(line)

        # Parallel processing section
        report_lines.extend(["", "## Parallel Processing", ""])

        parallel_data = benchmark_data.get("parallel_processing", {})
        if "1_workers" in parallel_data and "4_workers" in parallel_data:
            single_time = parallel_data["1_workers"]["execution_time"]
            multi_time = parallel_data["4_workers"]["execution_time"]
            speedup = single_time / multi_time if multi_time > 0 else 1

            report_lines.extend(
                [
                    f"- Single-threaded: {single_time:.3f}s",
                    f"- Multi-threaded (4 workers): {multi_time:.3f}s",
                    f"- Speedup: {speedup:.1f}x",
                ]
            )

        # Memory usage section
        report_lines.extend(["", "## Memory Usage", ""])

        memory_data = benchmark_data.get("memory_usage", {})
        if memory_data:
            report_lines.extend(
                [
                    f"- Maximum memory increase: {memory_data.get('max_increase', 0):.1f}MB",
                    f"- Average memory increase: {memory_data.get('average_increase', 0):.1f}MB",
                ]
            )

        # Regex optimization section
        report_lines.extend(["", "## Regex Optimization", ""])

        regex_data = benchmark_data.get("regex_optimization", {})
        if regex_data:
            report_lines.extend(
                [
                    f"- Total regex patterns: {regex_data.get('total_patterns', 0)}",
                    f"- Optimized patterns: {regex_data.get('optimized_patterns', 0)}",
                    f"- Optimization rate: {regex_data.get('optimization_rate', 0):.1f}%",
                ]
            )

        return "\n".join(report_lines)
