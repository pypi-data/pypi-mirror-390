#!/usr/bin/env python3
"""Benchmark script for new rule packs performance testing."""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from riveter.performance import ParallelProcessor, PerformanceMetrics
from riveter.rule_packs import RulePackManager
from riveter.scanner import validate_resources


class RulePackBenchmark:
    """Benchmark runner for rule pack performance testing."""

    def __init__(self):
        """Initialize benchmark runner."""
        self.rule_pack_manager = RulePackManager()
        self.performance_metrics = PerformanceMetrics()

    def run_full_benchmark(self, output_file: str = None) -> Dict[str, Any]:
        """Run comprehensive benchmark of all new rule packs."""
        print("🚀 Starting Riveter New Rule Packs Performance Benchmark")
        print("=" * 60)

        results = {
            "timestamp": time.time(),
            "individual_packs": self.benchmark_individual_packs(),
            "combined_packs": self.benchmark_combined_packs(),
            "parallel_processing": self.benchmark_parallel_processing(),
            "memory_usage": self.benchmark_memory_usage(),
            "scaling": self.benchmark_scaling(),
            "summary": {},
        }

        # Generate summary
        results["summary"] = self._generate_summary(results)

        # Save results if output file specified
        if output_file:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📊 Results saved to: {output_file}")

        # Print summary
        self._print_summary(results["summary"])

        return results

    def benchmark_individual_packs(self) -> Dict[str, Any]:
        """Benchmark individual rule pack performance."""
        print("\n📋 Benchmarking Individual Rule Packs")
        print("-" * 40)

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

        large_config = self._generate_large_config(500)
        results = {}

        for pack_name in new_rule_packs:
            try:
                # Load and benchmark
                start_time = time.time()
                rule_pack = self.rule_pack_manager.load_rule_pack(pack_name)
                load_time = time.time() - start_time

                start_time = time.time()
                scan_results = validate_resources(rule_pack.rules, large_config["resources"])
                scan_time = time.time() - start_time

                results[pack_name] = {
                    "rule_count": len(rule_pack.rules),
                    "load_time": load_time,
                    "scan_time": scan_time,
                    "result_count": len(scan_results),
                    "throughput": len(scan_results) / scan_time if scan_time > 0 else 0,
                }

                print(f"  ✓ {pack_name:20} | {len(rule_pack.rules):3} rules | {scan_time:6.3f}s")

            except Exception as e:
                results[pack_name] = {"error": str(e)}
                print(f"  ✗ {pack_name:20} | ERROR: {str(e)}")

        return results

    def benchmark_combined_packs(self) -> Dict[str, Any]:
        """Benchmark combined rule pack performance."""
        print("\n🔗 Benchmarking Combined Rule Packs")
        print("-" * 40)

        combinations = [
            ["aws-security", "aws-well-architected"],
            ["azure-security", "azure-well-architected"],
            ["gcp-security", "gcp-well-architected"],
            ["multi-cloud-security", "kubernetes-security"],
        ]

        large_config = self._generate_large_config(300)
        results = {}

        for i, pack_names in enumerate(combinations):
            combo_name = f"combo_{i+1}"
            try:
                # Load all packs
                all_rules = []
                for pack_name in pack_names:
                    rule_pack = self.rule_pack_manager.load_rule_pack(pack_name)
                    all_rules.extend(rule_pack.rules)

                # Benchmark scanning
                start_time = time.time()
                scan_results = validate_resources(all_rules, large_config["resources"])
                scan_time = time.time() - start_time

                results[combo_name] = {
                    "packs": pack_names,
                    "rule_count": len(all_rules),
                    "scan_time": scan_time,
                    "result_count": len(scan_results),
                    "throughput": len(scan_results) / scan_time if scan_time > 0 else 0,
                }

                pack_combo = "+".join(pack_names[:2])
                print(f"  ✓ {pack_combo:25} | {len(all_rules):3} rules | {scan_time:6.3f}s")

            except Exception as e:
                results[combo_name] = {"error": str(e)}
                print(f"  ✗ {combo_name:25} | ERROR: {str(e)}")

        return results

    def benchmark_parallel_processing(self) -> Dict[str, Any]:
        """Benchmark parallel processing performance."""
        print("\n⚡ Benchmarking Parallel Processing")
        print("-" * 40)

        rule_pack = self.rule_pack_manager.load_rule_pack("multi-cloud-security")
        large_config = self._generate_large_config(1000)

        worker_counts = [1, 2, 4, 8]
        results = {}

        for worker_count in worker_counts:
            processor = ParallelProcessor(max_workers=worker_count)

            start_time = time.time()
            parallel_results = processor.validate_resources_parallel(
                rule_pack.rules, large_config["resources"], batch_size=50
            )
            execution_time = time.time() - start_time

            results[f"{worker_count}_workers"] = {
                "worker_count": worker_count,
                "execution_time": execution_time,
                "result_count": len(parallel_results),
                "throughput": len(parallel_results) / execution_time if execution_time > 0 else 0,
            }

            throughput = results[f"{worker_count}_workers"]["throughput"]
            msg = f"  ✓ {worker_count:2} workers | {execution_time:6.3f}s | "
            msg += f"{throughput:8.1f} results/sec"
            print(msg)

        return results

    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage during scanning."""
        print("\n💾 Benchmarking Memory Usage")
        print("-" * 40)

        try:
            import psutil

            process = psutil.Process()
        except ImportError:
            print("  ⚠️  psutil not available, skipping memory benchmark")
            return {"error": "psutil not available"}

        results = {}

        test_packs = ["multi-cloud-security", "kubernetes-security", "aws-well-architected"]
        large_config = self._generate_large_config(500)

        for pack_name in test_packs:
            before_memory = process.memory_info().rss / 1024 / 1024

            rule_pack = self.rule_pack_manager.load_rule_pack(pack_name)
            scan_results = validate_resources(rule_pack.rules, large_config["resources"])

            after_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = after_memory - before_memory

            results[pack_name] = {
                "memory_before": before_memory,
                "memory_after": after_memory,
                "memory_increase": memory_increase,
                "rule_count": len(rule_pack.rules),
                "result_count": len(scan_results),
            }

            print(
                f"  ✓ {pack_name:20} | +{memory_increase:6.1f}MB | {len(rule_pack.rules):3} rules"
            )

        return results

    def benchmark_scaling(self) -> Dict[str, Any]:
        """Benchmark performance scaling with different resource counts."""
        print("\n📈 Benchmarking Performance Scaling")
        print("-" * 40)

        rule_pack = self.rule_pack_manager.load_rule_pack("multi-cloud-security")
        resource_counts = [100, 250, 500, 1000]
        results = {}

        for count in resource_counts:
            config = self._generate_large_config(count)

            start_time = time.time()
            scan_results = validate_resources(rule_pack.rules, config["resources"])
            execution_time = time.time() - start_time

            results[f"{count}_resources"] = {
                "resource_count": count,
                "execution_time": execution_time,
                "result_count": len(scan_results),
                "throughput": len(scan_results) / execution_time if execution_time > 0 else 0,
            }

            throughput = results[f"{count}_resources"]["throughput"]
            print(
                f"  ✓ {count:4} resources | {execution_time:6.3f}s | {throughput:8.1f} results/sec"
            )

        return results

    def _generate_large_config(self, resource_count: int) -> Dict[str, Any]:
        """Generate a large Terraform configuration for testing."""
        resources = []

        resource_templates = [
            {"type": "aws_instance", "props": {"instance_type": "t3.micro", "ami": "ami-12345"}},
            {"type": "aws_s3_bucket", "props": {"bucket": "test-bucket"}},
            {"type": "azurerm_virtual_machine", "props": {"vm_size": "Standard_B1s"}},
            {"type": "google_compute_instance", "props": {"machine_type": "e2-micro"}},
            {"type": "kubernetes_deployment", "props": {"replicas": 3}},
        ]

        for i in range(resource_count):
            template = resource_templates[i % len(resource_templates)]
            resource = {
                "id": f"{template['type']}_{i}",
                "resource_type": template["type"],
                "tags": {"Environment": "production" if i % 2 == 0 else "development"},
                **template["props"],
            }
            resources.append(resource)

        return {"resources": resources, "version": "1.0"}

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary from benchmark results."""
        summary = {}

        # Individual pack summary
        individual = results.get("individual_packs", {})
        if individual:
            successful_packs = [p for p in individual.values() if "scan_time" in p]
            if successful_packs:
                summary["individual_packs"] = {
                    "total_packs": len(individual),
                    "successful_packs": len(successful_packs),
                    "avg_scan_time": sum(p["scan_time"] for p in successful_packs)
                    / len(successful_packs),
                    "total_rules": sum(p["rule_count"] for p in successful_packs),
                    "fastest_pack": min(successful_packs, key=lambda x: x["scan_time"]),
                    "slowest_pack": max(successful_packs, key=lambda x: x["scan_time"]),
                }

        # Parallel processing summary
        parallel = results.get("parallel_processing", {})
        if parallel and "1_workers" in parallel and "4_workers" in parallel:
            single_time = parallel["1_workers"]["execution_time"]
            multi_time = parallel["4_workers"]["execution_time"]
            summary["parallel_processing"] = {
                "single_worker_time": single_time,
                "multi_worker_time": multi_time,
                "speedup": single_time / multi_time if multi_time > 0 else 1,
            }

        # Memory usage summary
        memory = results.get("memory_usage", {})
        if memory and not memory.get("error"):
            memory_increases = [
                m["memory_increase"] for m in memory.values() if isinstance(m, dict)
            ]
            if memory_increases:
                summary["memory_usage"] = {
                    "max_increase": max(memory_increases),
                    "avg_increase": sum(memory_increases) / len(memory_increases),
                    "total_packs_tested": len(memory_increases),
                }

        return summary

    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)

        # Individual packs
        if "individual_packs" in summary:
            ip = summary["individual_packs"]
            print("\n📋 Individual Rule Packs:")
            print(f"  • Tested: {ip['successful_packs']}/{ip['total_packs']} packs")
            print(f"  • Total rules: {ip['total_rules']}")
            print(f"  • Average scan time: {ip['avg_scan_time']:.3f}s")

        # Parallel processing
        if "parallel_processing" in summary:
            pp = summary["parallel_processing"]
            print("\n⚡ Parallel Processing:")
            print(f"  • Single worker: {pp['single_worker_time']:.3f}s")
            print(f"  • Multi worker: {pp['multi_worker_time']:.3f}s")
            print(f"  • Speedup: {pp['speedup']:.1f}x")

        # Memory usage
        if "memory_usage" in summary:
            mu = summary["memory_usage"]
            print("\n💾 Memory Usage:")
            print(f"  • Maximum increase: {mu['max_increase']:.1f}MB")
            print(f"  • Average increase: {mu['avg_increase']:.1f}MB")

        print("\n✅ Benchmark completed successfully!")


def main():
    """Main entry point for benchmark script."""
    parser = argparse.ArgumentParser(description="Benchmark new rule packs performance")
    parser.add_argument("--output", "-o", help="Output file for results (JSON)")
    parser.add_argument(
        "--quick", action="store_true", help="Run quick benchmark (fewer resources)"
    )

    args = parser.parse_args()

    try:
        benchmark = RulePackBenchmark()
        results = benchmark.run_full_benchmark(output_file=args.output)

        # Exit with error code if any critical issues found
        if any("error" in str(v) for v in results.values()):
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Benchmark failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
