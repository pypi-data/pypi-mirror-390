#!/usr/bin/env python3
"""Script to analyze and optimize regex patterns in rule packs."""

import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from riveter.rule_packs import RulePackManager


class RegexOptimizer:
    """Analyzer and optimizer for regex patterns in rule packs."""

    def __init__(self):
        """Initialize regex optimizer."""
        self.rule_pack_manager = RulePackManager()
        self.optimization_suggestions = []

    def analyze_all_rule_packs(self) -> Dict[str, Any]:
        """Analyze regex patterns in all new rule packs."""
        print("🔍 Analyzing Regex Patterns in New Rule Packs")
        print("=" * 50)

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

        analysis_results = {}

        for pack_name in new_rule_packs:
            try:
                print(f"\n📋 Analyzing {pack_name}...")
                pack_results = self.analyze_rule_pack(pack_name)
                analysis_results[pack_name] = pack_results

                # Print summary for this pack
                self._print_pack_summary(pack_name, pack_results)

            except Exception as e:
                print(f"  ❌ Error analyzing {pack_name}: {str(e)}")
                analysis_results[pack_name] = {"error": str(e)}

        # Print overall summary
        self._print_overall_summary(analysis_results)

        return analysis_results

    def analyze_rule_pack(self, pack_name: str) -> Dict[str, Any]:
        """Analyze regex patterns in a specific rule pack."""
        rule_pack = self.rule_pack_manager.load_rule_pack(pack_name)

        pack_results = {
            "total_rules": len(rule_pack.rules),
            "rules_with_regex": 0,
            "total_patterns": 0,
            "performance_issues": [],
            "optimization_suggestions": [],
            "pattern_analysis": [],
        }

        for rule in rule_pack.rules:
            regex_patterns = self._extract_regex_patterns(rule.assert_conditions, rule.id)

            if regex_patterns:
                pack_results["rules_with_regex"] += 1
                pack_results["total_patterns"] += len(regex_patterns)

                for pattern_info in regex_patterns:
                    analysis = self._analyze_pattern(pattern_info, rule.id)
                    pack_results["pattern_analysis"].append(analysis)

                    # Check for performance issues
                    if analysis["performance_risk"] == "high":
                        pack_results["performance_issues"].append(analysis)

                    # Generate optimization suggestions
                    suggestions = self._generate_optimization_suggestions(analysis)
                    if suggestions:
                        pack_results["optimization_suggestions"].extend(suggestions)

        return pack_results

    def _extract_regex_patterns(
        self, assert_conditions: Dict[str, Any], rule_id: str
    ) -> List[Dict[str, Any]]:
        """Extract regex patterns from rule assertion conditions."""
        patterns = []

        def extract_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if key == "regex" and isinstance(value, str):
                        patterns.append(
                            {"pattern": value, "context": current_path, "rule_id": rule_id}
                        )
                    else:
                        extract_recursive(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_recursive(item, f"{path}[{i}]")

        extract_recursive(assert_conditions)
        return patterns

    def _analyze_pattern(self, pattern_info: Dict[str, Any], rule_id: str) -> Dict[str, Any]:
        """Analyze a single regex pattern for performance and correctness."""
        pattern = pattern_info["pattern"]

        analysis = {
            "rule_id": rule_id,
            "pattern": pattern,
            "context": pattern_info["context"],
            "length": len(pattern),
            "complexity_score": 0,
            "performance_risk": "low",
            "compile_time": 0,
            "execution_times": [],
            "issues": [],
            "suggestions": [],
        }

        try:
            # Test compilation time
            start_time = time.time()
            compiled_regex = re.compile(pattern)
            analysis["compile_time"] = time.time() - start_time

            # Test execution time with various inputs
            test_strings = [
                "simple-test",
                "aws_instance",
                "production-environment-very-long-name",
                "0.0.0.0/0",
                "roles/owner",
                "a" * 1000,  # Long string
                "complex.nested.resource.name.with.many.dots",
                "arn:aws:iam::123456789012:role/MyRole",
            ]

            for test_string in test_strings:
                start_time = time.time()
                try:
                    compiled_regex.search(test_string)
                    exec_time = time.time() - start_time
                    analysis["execution_times"].append(exec_time)
                except Exception:
                    # Pattern might not work with this test string
                    pass

            # Calculate complexity score
            analysis["complexity_score"] = self._calculate_complexity_score(pattern)

            # Determine performance risk
            max_exec_time = max(analysis["execution_times"]) if analysis["execution_times"] else 0
            if analysis["compile_time"] > 0.01 or max_exec_time > 0.01:
                analysis["performance_risk"] = "high"
            elif analysis["compile_time"] > 0.001 or max_exec_time > 0.001:
                analysis["performance_risk"] = "medium"

            # Identify specific issues
            analysis["issues"] = self._identify_pattern_issues(pattern)

        except re.error as e:
            analysis["issues"].append(f"Invalid regex: {str(e)}")
            analysis["performance_risk"] = "high"

        return analysis

    def _calculate_complexity_score(self, pattern: str) -> int:
        """Calculate complexity score for a regex pattern."""
        score = 0

        # Basic complexity factors
        score += pattern.count("*") * 2  # Kleene star
        score += pattern.count("+") * 2  # Plus quantifier
        score += pattern.count("?") * 1  # Optional quantifier
        score += pattern.count("(") * 1  # Groups
        score += pattern.count("[") * 1  # Character classes
        score += pattern.count("{") * 1  # Specific quantifiers
        score += pattern.count("|") * 2  # Alternation
        score += pattern.count("\\") * 1  # Escapes

        # Nested quantifiers (high risk)
        if re.search(r"[*+?][*+?]", pattern):
            score += 10

        # Catastrophic backtracking patterns
        if re.search(r"\([^)]*[*+][^)]*\)[*+]", pattern):
            score += 15

        return score

    def _identify_pattern_issues(self, pattern: str) -> List[str]:
        """Identify potential issues in regex patterns."""
        issues = []

        # Check for catastrophic backtracking patterns
        if re.search(r"\([^)]*[*+][^)]*\)[*+]", pattern):
            issues.append("Potential catastrophic backtracking")

        # Check for nested quantifiers
        if re.search(r"[*+?][*+?]", pattern):
            issues.append("Nested quantifiers detected")

        # Check for unescaped dots in contexts where they should be literal
        if "." in pattern and "\\." not in pattern:
            issues.append("Unescaped dots - may match any character")

        # Check for overly broad character classes
        if "[^" in pattern and "]" in pattern:
            issues.append("Negated character class - ensure it's not too broad")

        # Check for anchors
        if not pattern.startswith("^") and not pattern.endswith("$"):
            if "roles/" in pattern or "arn:" in pattern:
                issues.append("Consider adding anchors for exact matching")

        return issues

    def _generate_optimization_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions for a pattern."""
        suggestions = []
        pattern = analysis["pattern"]

        # Suggest atomic groups for performance
        if analysis["complexity_score"] > 5:
            suggestions.append(
                {
                    "type": "performance",
                    "rule_id": analysis["rule_id"],
                    "suggestion": "Consider using atomic groups (?>...) to prevent backtracking",
                    "pattern": pattern,
                }
            )

        # Suggest character class optimizations
        if "[a-zA-Z0-9]" in pattern:
            suggestions.append(
                {
                    "type": "optimization",
                    "rule_id": analysis["rule_id"],
                    "suggestion": "Replace [a-zA-Z0-9] with \\w for better performance",
                    "pattern": pattern,
                    "optimized": pattern.replace("[a-zA-Z0-9]", "\\w"),
                }
            )

        # Suggest anchoring for exact matches
        if any(keyword in pattern for keyword in ["roles/", "arn:", "ami-"]):
            if not pattern.startswith("^") and not pattern.endswith("$"):
                suggestions.append(
                    {
                        "type": "correctness",
                        "rule_id": analysis["rule_id"],
                        "suggestion": "Add anchors for exact matching",
                        "pattern": pattern,
                        "optimized": f"^{pattern}$",
                    }
                )

        return suggestions

    def _print_pack_summary(self, pack_name: str, results: Dict[str, Any]) -> None:
        """Print summary for a single rule pack."""
        if "error" in results:
            print(f"  ❌ Error: {results['error']}")
            return

        print(f"  📊 Rules: {results['total_rules']}")
        print(f"  🔍 Rules with regex: {results['rules_with_regex']}")
        print(f"  📝 Total patterns: {results['total_patterns']}")
        print(f"  ⚠️  Performance issues: {len(results['performance_issues'])}")
        print(f"  💡 Optimization suggestions: {len(results['optimization_suggestions'])}")

    def _print_overall_summary(self, analysis_results: Dict[str, Any]) -> None:
        """Print overall analysis summary."""
        print("\n" + "=" * 50)
        print("📊 OVERALL REGEX ANALYSIS SUMMARY")
        print("=" * 50)

        total_packs = len(analysis_results)
        successful_packs = len([r for r in analysis_results.values() if "error" not in r])

        if successful_packs == 0:
            print("❌ No packs analyzed successfully")
            return

        # Aggregate statistics
        total_rules = sum(
            r.get("total_rules", 0) for r in analysis_results.values() if "error" not in r
        )
        total_regex_rules = sum(
            r.get("rules_with_regex", 0) for r in analysis_results.values() if "error" not in r
        )
        total_patterns = sum(
            r.get("total_patterns", 0) for r in analysis_results.values() if "error" not in r
        )
        total_issues = sum(
            len(r.get("performance_issues", []))
            for r in analysis_results.values()
            if "error" not in r
        )
        total_suggestions = sum(
            len(r.get("optimization_suggestions", []))
            for r in analysis_results.values()
            if "error" not in r
        )

        print(f"\n📋 Analyzed: {successful_packs}/{total_packs} rule packs")
        print(f"📊 Total rules: {total_rules}")
        print(
            f"🔍 Rules with regex: {total_regex_rules} ({total_regex_rules/total_rules*100:.1f}%)"
        )
        print(f"📝 Total regex patterns: {total_patterns}")
        print(f"⚠️  Performance issues: {total_issues}")
        print(f"💡 Optimization suggestions: {total_suggestions}")

        # Performance assessment
        if total_issues == 0:
            print("\n✅ All regex patterns are optimized!")
        elif total_issues <= total_patterns * 0.1:
            print(f"\n🟡 Minor optimization needed ({total_issues}/{total_patterns} patterns)")
        else:
            print(
                f"\n🔴 Significant optimization needed ({total_issues}/{total_patterns} patterns)"
            )

        # Print top suggestions
        if total_suggestions > 0:
            print("\n💡 Top Optimization Opportunities:")
            all_suggestions = []
            for pack_results in analysis_results.values():
                if "optimization_suggestions" in pack_results:
                    all_suggestions.extend(pack_results["optimization_suggestions"])

            # Group by type
            suggestion_types = {}
            for suggestion in all_suggestions[:10]:  # Top 10
                stype = suggestion.get("type", "other")
                if stype not in suggestion_types:
                    suggestion_types[stype] = 0
                suggestion_types[stype] += 1

            for stype, count in suggestion_types.items():
                print(f"  • {stype.title()}: {count} suggestions")

    def generate_optimization_report(
        self, analysis_results: Dict[str, Any], output_file: str = None
    ) -> str:
        """Generate detailed optimization report."""
        report_lines = ["# Regex Pattern Optimization Report", "", "## Summary", ""]

        # Add summary statistics
        successful_results = {k: v for k, v in analysis_results.items() if "error" not in v}

        if successful_results:
            total_patterns = sum(r.get("total_patterns", 0) for r in successful_results.values())
            total_issues = sum(
                len(r.get("performance_issues", [])) for r in successful_results.values()
            )

            optimization_rate = (total_patterns - total_issues) / total_patterns * 100
            report_lines.extend(
                [
                    f"- **Total Rule Packs Analyzed**: {len(successful_results)}",
                    f"- **Total Regex Patterns**: {total_patterns}",
                    f"- **Performance Issues Found**: {total_issues}",
                    f"- **Optimization Rate**: {optimization_rate:.1f}%",
                    "",
                ]
            )

        # Add detailed findings per pack
        report_lines.extend(["## Detailed Findings", ""])

        for pack_name, results in successful_results.items():
            if results.get("total_patterns", 0) > 0:
                report_lines.extend(
                    [
                        f"### {pack_name}",
                        "",
                        f"- Rules with regex: {results.get('rules_with_regex', 0)}",
                        f"- Total patterns: {results.get('total_patterns', 0)}",
                        f"- Performance issues: {len(results.get('performance_issues', []))}",
                        "",
                    ]
                )

                # Add specific issues
                if results.get("performance_issues"):
                    report_lines.extend(["**Performance Issues:**", ""])
                    for issue in results["performance_issues"][:5]:  # Top 5
                        report_lines.append(
                            f"- Rule `{issue['rule_id']}`: {', '.join(issue.get('issues', []))}"
                        )
                    report_lines.append("")

        report_content = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report_content)
            print(f"\n📄 Optimization report saved to: {output_file}")

        return report_content


def main():
    """Main entry point for regex optimization script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze and optimize regex patterns in rule packs"
    )
    parser.add_argument("--report", "-r", help="Generate optimization report file")
    parser.add_argument("--pack", "-p", help="Analyze specific rule pack only")

    args = parser.parse_args()

    try:
        optimizer = RegexOptimizer()

        if args.pack:
            print(f"🔍 Analyzing regex patterns in {args.pack}")
            results = {args.pack: optimizer.analyze_rule_pack(args.pack)}
            optimizer._print_pack_summary(args.pack, results[args.pack])
        else:
            results = optimizer.analyze_all_rule_packs()

        if args.report:
            optimizer.generate_optimization_report(results, args.report)

    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
