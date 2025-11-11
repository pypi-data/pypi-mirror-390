"""Riveter CLI interface.

This module provides the command-line interface for the Riveter infrastructure
rule enforcement tool. It includes commands for scanning Terraform configurations,
managing rule packs, and configuring output formats.

The CLI supports:
- Scanning Terraform files against custom rules
- Loading pre-built rule packs
- Multiple output formats (table, JSON, JUnit XML, SARIF)
- Performance optimization options
- Configuration file support
- Debug and logging options

Example:
    Basic usage:
        $ riveter scan --rules rules.yml --terraform main.tf

    With rule packs:
        $ riveter scan --rule-pack aws-security --terraform main.tf

    JSON output:
        $ riveter scan --rules rules.yml --terraform main.tf --output-format json
"""

from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.table import Table

from ._version import get_version
from .lazy_imports import lazy_importer

console = Console()


@click.group()
@click.version_option(version=get_version())
def main() -> None:
    """Riveter - Infrastructure Rule Enforcement as Code.

    Riveter is a command-line tool for validating Terraform configurations
    against custom rules and compliance standards. It supports multiple
    cloud providers, advanced rule operators, and various output formats.

    Use 'riveter COMMAND --help' for more information on specific commands.
    """


@main.command()
@click.option(
    "--rules",
    "-r",
    "rules_file",
    type=click.Path(exists=True),
    help="Path to rules YAML file",
)
@click.option(
    "--rule-pack",
    "-p",
    "rule_packs",
    multiple=True,
    help="Rule pack name to load (can be used multiple times)",
)
@click.option(
    "--terraform",
    "-t",
    "terraform_file",
    required=True,
    type=click.Path(exists=True),
    help="Path to Terraform main.tf file",
)
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(["table", "json", "junit", "sarif"], case_sensitive=False),
    help="Output format for validation results",
)
@click.option(
    "--config",
    "-c",
    "config_file",
    type=click.Path(exists=True),
    help="Path to configuration file (YAML or JSON)",
)
@click.option(
    "--include-rules",
    multiple=True,
    help="Include rules matching pattern (can be used multiple times)",
)
@click.option(
    "--exclude-rules",
    multiple=True,
    help="Exclude rules matching pattern (can be used multiple times)",
)
@click.option(
    "--min-severity",
    type=click.Choice(["info", "warning", "error"], case_sensitive=False),
    help="Minimum severity level to report",
)
@click.option(
    "--rule-dirs",
    multiple=True,
    help="Additional rule directories to search (can be used multiple times)",
)
@click.option(
    "--environment",
    "-e",
    help="Environment context for rule filtering (e.g., production, development)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode with verbose output",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help="Set logging level (DEBUG, INFO, WARNING, ERROR)",
)
@click.option(
    "--log-format",
    type=click.Choice(["human", "json"], case_sensitive=False),
    default="human",
    help="Set log output format (human, json)",
)
@click.option(
    "--parallel",
    is_flag=True,
    help="Enable parallel processing for improved performance",
)
@click.option(
    "--cache-dir",
    type=click.Path(),
    help="Directory for caching parsed configurations",
)
@click.option(
    "--baseline",
    type=click.Path(),
    help="Baseline file for incremental scanning",
)
@click.option(
    "--benchmark",
    is_flag=True,
    help="Enable performance measurement and reporting",
)
def scan(
    rules_file: Optional[str],
    rule_packs: tuple[str, ...],
    terraform_file: str,
    output_format: Optional[str],
    config_file: Optional[str],
    include_rules: tuple[str, ...],
    exclude_rules: tuple[str, ...],
    min_severity: Optional[str],
    rule_dirs: tuple[str, ...],
    environment: Optional[str],
    debug: bool,
    log_level: Optional[str],
    log_format: str,
    parallel: bool,
    cache_dir: Optional[str],
    baseline: Optional[str],
    benchmark: bool,
) -> None:
    """Validate Terraform configuration against rules.

    Examples:
        # Validate using a rules file:
        riveter scan -r rules.yml -t main.tf

        # Validate using rule packs:
        riveter scan -p aws-security -t main.tf

        # Validate using configuration file:
        riveter scan -c riveter.yml -t main.tf

        # Filter rules by pattern:
        riveter scan -p aws-security -t main.tf --include-rules "*security*" \\
            --exclude-rules "*test*"

        # Set minimum severity:
        riveter scan -p aws-security -t main.tf --min-severity warning

        # Use environment context:
        riveter scan -p aws-security -t main.tf --environment production

        # Output results in JSON format:
        riveter scan -p aws-security -t main.tf --output-format json

        # Enable debug mode with detailed logging:
        riveter scan -p aws-security -t main.tf --debug --log-level DEBUG

        # Use structured JSON logging:
        riveter scan -p aws-security -t main.tf --log-format json

        # Enable parallel processing for better performance:
        riveter scan -p aws-security -t main.tf --parallel

        # Use caching to speed up repeated scans:
        riveter scan -p aws-security -t main.tf --cache-dir ~/.riveter/cache

        # Incremental scanning with baseline:
        riveter scan -p aws-security -t main.tf --baseline .riveter_baseline.json

        # Performance benchmarking:
        riveter scan -p aws-security -t main.tf --benchmark --parallel
    """
    try:
        # Lazy import heavy dependencies
        configure_logging = lazy_importer.lazy_import("riveter.logging", "configure_logging")
        LogLevel = lazy_importer.lazy_import("riveter.logging", "LogLevel")
        LogFormat = lazy_importer.lazy_import("riveter.logging", "LogFormat")
        ConfigManager = lazy_importer.lazy_import("riveter.config", "ConfigManager")
        get_environment_from_context = lazy_importer.lazy_import(
            "riveter.config", "get_environment_from_context"
        )
        extract_terraform_config = lazy_importer.lazy_import(
            "riveter.extract_config", "extract_terraform_config"
        )
        load_rules = lazy_importer.lazy_import("riveter.rules", "load_rules")
        RulePackManager = lazy_importer.lazy_import("riveter.rule_packs", "RulePackManager")
        RuleFilter = lazy_importer.lazy_import("riveter.rule_filter", "RuleFilter")
        validate_resources = lazy_importer.lazy_import("riveter.scanner", "validate_resources")
        report_results = lazy_importer.lazy_import("riveter.reporter", "report_results")
        PerformanceMetrics = lazy_importer.lazy_import("riveter.performance", "PerformanceMetrics")
        IncrementalScanner = lazy_importer.lazy_import("riveter.performance", "IncrementalScanner")
        ParallelProcessor = lazy_importer.lazy_import("riveter.performance", "ParallelProcessor")
        ResourceCache = lazy_importer.lazy_import("riveter.performance", "ResourceCache")

        # Configure logging based on CLI options
        if debug and not log_level:
            effective_log_level = "DEBUG"
        elif log_level:
            effective_log_level = log_level
        else:
            effective_log_level = "INFO"

        configure_logging(
            level=LogLevel(effective_log_level.upper()), format_type=LogFormat(log_format.lower())
        )

        from .logging import debug as log_debug
        from .logging import info

        info("Starting Riveter scan", terraform_file=terraform_file)

        if debug:
            log_debug("Debug mode enabled", log_level=effective_log_level, log_format=log_format)
        # Load configuration
        config_manager = ConfigManager()

        # Build CLI overrides
        cli_overrides: Dict[str, Any] = {}
        if output_format:
            cli_overrides["output_format"] = output_format
        if min_severity:
            cli_overrides["min_severity"] = min_severity
        if debug:
            cli_overrides["debug"] = debug
        if include_rules:
            cli_overrides["include_rules"] = list(include_rules)
        if exclude_rules:
            cli_overrides["exclude_rules"] = list(exclude_rules)
        if rule_dirs:
            cli_overrides["rule_dirs"] = list(rule_dirs)
        if rule_packs:
            cli_overrides["rule_packs"] = list(rule_packs)
        if parallel:
            cli_overrides["parallel"] = parallel
        if cache_dir:
            cli_overrides["cache_dir"] = cache_dir
        if baseline:
            cli_overrides["baseline"] = baseline
        if benchmark:
            cli_overrides["benchmark"] = benchmark

        # Load configuration with hierarchy
        config = config_manager.load_config(
            config_file=config_file, cli_overrides=cli_overrides, environment=environment
        )

        # Validate configuration
        config_errors = config_manager.validate_config(config)
        if config_errors:
            console.print("[red]Configuration errors:[/red]")
            for error in config_errors:
                console.print(f"  - {error}")
            raise SystemExit(1)

        if debug or config.debug:
            from .logging import debug as log_debug

            log_debug(
                "Configuration loaded",
                rule_directories=config.rule_dirs,
                rule_packs=config.rule_packs,
                include_patterns=config.include_rules,
                exclude_patterns=config.exclude_rules,
                min_severity=config.min_severity,
                output_format=config.output_format,
                environment=environment,
            )

            console.print("[blue]Configuration loaded:[/blue]")
            console.print(f"  - Rule directories: {config.rule_dirs}")
            console.print(f"  - Rule packs: {config.rule_packs}")
            console.print(f"  - Include patterns: {config.include_rules}")
            console.print(f"  - Exclude patterns: {config.exclude_rules}")
            console.print(f"  - Min severity: {config.min_severity}")
            console.print(f"  - Output format: {config.output_format}")
            if environment:
                console.print(f"  - Environment: {environment}")

        # Determine rule sources
        rule_sources = []
        if rules_file:
            rule_sources.append(("file", rules_file))

        # Add rule packs from config and CLI
        all_rule_packs = list(config.rule_packs)
        if rule_packs:
            all_rule_packs.extend(rule_packs)

        for pack_name in all_rule_packs:
            rule_sources.append(("pack", pack_name))

        # Validate that at least one rule source is provided
        if not rule_sources:
            raise click.UsageError(
                "Must specify either --rules, --rule-pack, or configure rule sources in config file"
            )

        all_rules = []

        # Load rules from all sources
        for source_type, source_name in rule_sources:
            if source_type == "file":
                rules = load_rules(source_name)
                all_rules.extend(rules)
                if debug or config.debug:
                    from .logging import debug as log_debug

                    log_debug("Loaded rules file", file_path=source_name, rule_count=len(rules))
                    console.print(
                        f"[green]Loaded rules file:[/green] {source_name} ({len(rules)} rules)"
                    )

            elif source_type == "pack":
                rule_pack_manager = RulePackManager()
                # Add custom rule directories to search path
                for rule_dir in config.rule_dirs:
                    if rule_dir not in rule_pack_manager.rule_pack_dirs:
                        rule_pack_manager.rule_pack_dirs.append(rule_dir)

                try:
                    rule_pack = rule_pack_manager.load_rule_pack(source_name)
                    all_rules.extend(rule_pack.rules)
                    rule_count = len(rule_pack.rules)

                    from .logging import debug as log_debug
                    from .logging import info

                    info("Loaded rule pack", pack_name=source_name, rule_count=rule_count)
                    if debug or config.debug:
                        log_debug(
                            "Rule pack details",
                            pack_name=source_name,
                            version=rule_pack.version,
                            description=rule_pack.description,
                        )

                    console.print(
                        f"[green]Loaded rule pack:[/green] {source_name} ({rule_count} rules)"
                    )
                except FileNotFoundError:
                    from .logging import error as log_error

                    log_error("Rule pack not found", pack_name=source_name)
                    console.print(f"[red]Error:[/red] Rule pack '{source_name}' not found")
                    raise SystemExit(1) from None
                except Exception as e:
                    from .logging import error as log_error

                    log_error("Error loading rule pack", pack_name=source_name, error=str(e))
                    console.print(f"[red]Error loading rule pack '{source_name}':[/red] {str(e)}")
                    raise SystemExit(1) from e

        if not all_rules:
            console.print("[red]Error:[/red] No rules loaded")
            raise SystemExit(1)

        console.print(f"[blue]Total rules loaded:[/blue] {len(all_rules)}")

        # Extract Terraform configuration
        resources = extract_terraform_config(terraform_file)

        # Apply rule filtering
        if (
            config.include_rules
            or config.exclude_rules
            or config.min_severity != "info"
            or environment
        ):
            # Detect environment from resources if not explicitly provided
            detected_environment = environment or get_environment_from_context(
                resources["resources"]
            )

            # Create environment context
            environment_context = {}
            if detected_environment:
                environment_context["environment"] = detected_environment
                if debug or config.debug:
                    console.print(
                        f"[blue]Environment detected/specified:[/blue] {detected_environment}"
                    )

            rule_filter = RuleFilter(
                include_patterns=config.include_rules,
                exclude_patterns=config.exclude_rules,
                min_severity=config.min_severity,
                environment_context=environment_context,
            )

            filtered_rules = rule_filter.filter_rules(all_rules)

            if debug or config.debug:
                from .logging import debug as log_debug

                filtered_count = len(all_rules) - len(filtered_rules)
                log_debug(
                    "Rule filtering completed",
                    original_count=len(all_rules),
                    filtered_count=len(filtered_rules),
                    removed_count=filtered_count,
                )

                console.print(f"[blue]Rules after filtering:[/blue] {len(filtered_rules)}")
                if len(filtered_rules) != len(all_rules):
                    console.print(f"[yellow]Filtered out {filtered_count} rules[/yellow]")

            all_rules = filtered_rules

        if not all_rules:
            console.print("[yellow]Warning:[/yellow] No rules remain after filtering")
            raise SystemExit(0)

        # Initialize performance metrics if benchmarking is enabled
        metrics: Optional[Any] = None
        if benchmark:
            PerformanceMetrics = lazy_importer.lazy_import(
                "riveter.performance", "PerformanceMetrics"
            )
            metrics = PerformanceMetrics()
            metrics.start_timer("total_execution")

        # Initialize caching if cache directory is specified
        cache = None
        if cache_dir:
            cache = ResourceCache(cache_dir=cache_dir)
            if metrics:
                metrics.start_timer("cache_initialization")

            # Try to get cached configuration
            cached_config = cache.get_cached_config(terraform_file)
            if cached_config:
                resources = cached_config
                console.print("[green]Using cached configuration[/green]")
                if debug or config.debug:
                    console.print(f"[blue]Cache hit for:[/blue] {terraform_file}")
            else:
                # Cache the newly extracted configuration
                cache.cache_parsed_config(terraform_file, resources)
                if debug or config.debug:
                    console.print(f"[blue]Configuration cached for:[/blue] {terraform_file}")

            if metrics:
                metrics.end_timer("cache_initialization")

        # Handle incremental scanning if baseline is specified
        resources_to_validate = resources["resources"]
        if baseline:
            if metrics:
                metrics.start_timer("incremental_analysis")

            scanner = IncrementalScanner(baseline_file=baseline)
            changed_resources = scanner.get_changed_resources(resources["resources"])

            if len(changed_resources) < len(resources["resources"]):
                resources_to_validate = changed_resources
                console.print(
                    f"[yellow]Incremental scan:[/yellow] {len(changed_resources)} of "
                    f"{len(resources['resources'])} resources changed"
                )
                if debug or config.debug:
                    console.print(f"[blue]Baseline file:[/blue] {baseline}")
            else:
                console.print(
                    "[blue]All resources will be validated (no baseline or all changed)[/blue]"
                )

            # Save current state as new baseline
            scanner.save_baseline(resources)

            if metrics:
                metrics.end_timer("incremental_analysis")

        # Validate resources
        from .logging import debug as log_debug
        from .logging import info

        info(
            "Starting resource validation",
            rule_count=len(all_rules),
            resource_count=len(resources_to_validate),
            parallel_enabled=parallel,
        )

        if debug or config.debug:
            log_debug(
                "Resource validation details",
                terraform_file=terraform_file,
                resource_types=[r.get("type", "unknown") for r in resources_to_validate],
                parallel_processing=parallel,
                caching_enabled=cache is not None,
                incremental_scanning=baseline is not None,
            )

        if metrics:
            metrics.start_timer("resource_validation")

        # Use parallel processing if enabled
        if parallel:
            processor = ParallelProcessor()
            results = processor.validate_resources_parallel(all_rules, resources_to_validate)
            if debug or config.debug:
                console.print(
                    f"[green]Parallel processing completed[/green] with "
                    f"{processor.max_workers} workers"
                )
        else:
            results = validate_resources(all_rules, resources_to_validate)

        if metrics:
            metrics.end_timer("resource_validation")

        info(
            "Resource validation completed",
            total_results=len(results),
            passed_count=sum(1 for r in results if r.passed),
            failed_count=sum(1 for r in results if not r.passed),
        )

        if metrics:
            metrics.end_timer("total_execution")

        exit_code = report_results(results, output_format=config.output_format)

        # Print performance metrics if benchmarking is enabled
        if benchmark and metrics:
            console.print("\n[bold blue]Performance Metrics:[/bold blue]")
            metrics.print_summary()

        raise SystemExit(exit_code)
    except Exception as e:
        from .logging import exception

        exception("Scan command failed", error=str(e))
        console.print(f"[red]Error:[/red] {str(e)}")
        raise SystemExit(1) from e


@main.command("list-rule-packs")
def list_rule_packs() -> None:
    """List all available rule packs.

    Displays a table of all rule packs found in the configured search
    directories, including their names, versions, rule counts, descriptions,
    and authors.

    Rule packs are searched for in:
    - Built-in rule_packs/ directory
    - User-specified rule directories
    - Current working directory

    Example:
        $ riveter list-rule-packs
    """
    try:
        RulePackManager = lazy_importer.lazy_import("riveter.rule_packs", "RulePackManager")
        rule_pack_manager = RulePackManager()
        packs = rule_pack_manager.list_available_packs()

        if not packs:
            console.print("[yellow]No rule packs found.[/yellow]")
            console.print("\nRule pack search directories:")
            for directory in rule_pack_manager.rule_pack_dirs:
                console.print(f"  - {directory}")
            return

        table = Table(title="Available Rule Packs")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="magenta")
        table.add_column("Rules", justify="right", style="green")
        table.add_column("Description", style="white")
        table.add_column("Author", style="blue")

        for pack in packs:
            description = str(pack["description"])
            table.add_row(
                str(pack["name"]),
                str(pack["version"]),
                str(pack["rule_count"]),
                (description[:50] + "..." if len(description) > 50 else description),
                str(pack["author"]),
            )

        console.print(table)
        console.print(f"\n[blue]Total rule packs:[/blue] {len(packs)}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise SystemExit(1) from e


@main.command("validate-rule-pack")
@click.argument("rule_pack_file", type=click.Path(exists=True))
def validate_rule_pack(rule_pack_file: str) -> None:
    """Validate a rule pack file.

    Checks a rule pack file for:
    - Valid YAML/JSON syntax
    - Required metadata fields
    - Rule definition correctness
    - Operator usage validation
    - Resource type compatibility

    Args:
        rule_pack_file: Path to the rule pack file to validate

    Example:
        $ riveter validate-rule-pack my-custom-rules.yml
    """
    try:
        RulePackManager = lazy_importer.lazy_import("riveter.rule_packs", "RulePackManager")
        rule_pack_manager = RulePackManager()
        result = rule_pack_manager.validate_rule_pack(rule_pack_file)

        if result["valid"]:
            console.print("[green]✓ Rule pack is valid[/green]")
            console.print(f"[blue]Name:[/blue] {result['metadata']['name']}")
            console.print(f"[blue]Version:[/blue] {result['metadata']['version']}")
            console.print(f"[blue]Description:[/blue] {result['metadata']['description']}")
            console.print(f"[blue]Rules:[/blue] {result['rule_count']}")

            if result["warnings"]:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in result["warnings"]:
                    console.print(f"  - {warning}")
        else:
            console.print("[red]✗ Rule pack is invalid[/red]")
            console.print("\n[red]Errors:[/red]")
            for error in result["errors"]:
                console.print(f"  - {error}")

            if result["warnings"]:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in result["warnings"]:
                    console.print(f"  - {warning}")

            raise SystemExit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise SystemExit(1) from e


@main.command("create-rule-pack-template")
@click.argument("pack_name")
@click.argument("output_file", type=click.Path())
def create_rule_pack_template(pack_name: str, output_file: str) -> None:
    """Create a template rule pack file.

    Generates a template rule pack file with proper metadata structure
    and example rules to help users create their own rule packs.

    Args:
        pack_name: Name for the new rule pack
        output_file: Path where the template file will be created

    Example:
        $ riveter create-rule-pack-template my-company-rules rules/my-rules.yml
    """
    try:
        RulePackManager = lazy_importer.lazy_import("riveter.rule_packs", "RulePackManager")
        rule_pack_manager = RulePackManager()
        rule_pack_manager.create_rule_pack_template(pack_name, output_file)
        console.print(f"[green]✓ Created rule pack template:[/green] {output_file}")
        console.print(f"[blue]Pack name:[/blue] {pack_name}")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Edit the template file to add your rules")
        console.print("2. Update the metadata section with your information")
        console.print(f"3. Validate the pack: riveter validate-rule-pack {output_file}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise SystemExit(1) from e


@main.command("create-config")
@click.argument("output_file", type=click.Path(), default="riveter.yml")
@click.option(
    "--format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    help="Configuration file format (default: yaml)",
)
def create_config(output_file: str, format: str) -> None:
    """Create a sample configuration file.

    Generates a sample configuration file with all available options
    and their default values, along with explanatory comments.

    Args:
        output_file: Path where the configuration file will be created
        format: File format (yaml or json)

    Example:
        $ riveter create-config
        $ riveter create-config --format json config.json
    """
    try:
        # Ensure correct file extension
        if format.lower() == "json" and not output_file.endswith(".json"):
            if output_file == "riveter.yml":
                output_file = "riveter.json"
            elif not output_file.endswith(".json"):
                output_file += ".json"
        elif format.lower() == "yaml" and output_file.endswith(".json"):
            output_file = output_file.replace(".json", ".yml")

        ConfigManager = lazy_importer.lazy_import("riveter.config", "ConfigManager")
        config_manager = ConfigManager()
        config_manager.create_sample_config(output_file)

        console.print(f"[green]✓ Created configuration file:[/green] {output_file}")
        console.print(f"[blue]Format:[/blue] {format.upper()}")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Edit the configuration file to match your needs")
        console.print("2. Use the config file: riveter scan -c {} -t main.tf".format(output_file))
        console.print("3. Override settings with CLI options as needed")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise SystemExit(1) from e


@main.command("validate-rules")
@click.argument("rules_file", type=click.Path(exists=True))
@click.option(
    "--format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format for validation results",
)
@click.option(
    "--min-severity",
    type=click.Choice(["error", "warning", "info"], case_sensitive=False),
    default="error",
    help="Minimum severity level to report",
)
def validate_rules(rules_file: str, format: str, min_severity: str) -> None:
    """Validate rule syntax and best practices.

    Performs comprehensive linting of rule files including:
    - YAML syntax validation
    - Required field checking
    - Operator usage validation
    - Best practice recommendations
    - Resource type compatibility

    Args:
        rules_file: Path to the rules file to validate

    Example:
        $ riveter validate-rules rules.yml
        $ riveter validate-rules rules.yml --format json --min-severity warning
    """
    try:
        RuleLinter = lazy_importer.lazy_import("riveter.rule_linter", "RuleLinter")
        LintSeverity = lazy_importer.lazy_import("riveter.rule_linter", "LintSeverity")
        linter = RuleLinter()
        result = linter.lint_file(rules_file)

        # Filter issues by minimum severity
        severity_order = {"info": 0, "warning": 1, "error": 2}
        min_level = severity_order[min_severity]

        filtered_issues = [
            issue for issue in result.issues if severity_order[issue.severity.value] >= min_level
        ]

        if format == "json":
            import json

            output = {
                "file_path": result.file_path,
                "valid": result.valid,
                "rule_count": result.rule_count,
                "issues": [
                    {
                        "rule_id": issue.rule_id,
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "line_number": issue.line_number,
                        "column_number": issue.column_number,
                        "suggestion": issue.suggestion,
                    }
                    for issue in filtered_issues
                ],
                "summary": {
                    "total_issues": len(filtered_issues),
                    "error_count": sum(
                        1 for i in filtered_issues if i.severity == LintSeverity.ERROR
                    ),
                    "warning_count": sum(
                        1 for i in filtered_issues if i.severity == LintSeverity.WARNING
                    ),
                    "info_count": sum(
                        1 for i in filtered_issues if i.severity == LintSeverity.INFO
                    ),
                },
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Table format
            if result.valid and not filtered_issues:
                console.print("[green]✓ Rules file is valid[/green]")
                console.print(f"[blue]File:[/blue] {result.file_path}")
                console.print(f"[blue]Rules:[/blue] {result.rule_count}")
            else:
                if not result.valid:
                    console.print("[red]✗ Rules file has errors[/red]")
                else:
                    console.print("[yellow]⚠ Rules file has warnings[/yellow]")

                console.print(f"[blue]File:[/blue] {result.file_path}")
                console.print(f"[blue]Rules:[/blue] {result.rule_count}")

                if filtered_issues:
                    console.print(f"\n[bold]Issues (showing {min_severity}+ severity):[/bold]")

                    table = Table()
                    table.add_column("Rule ID", style="cyan")
                    table.add_column("Severity", style="magenta")
                    table.add_column("Message", style="white")
                    table.add_column("Suggestion", style="green")

                    for issue in filtered_issues:
                        severity_color = {"error": "red", "warning": "yellow", "info": "blue"}.get(
                            issue.severity.value, "white"
                        )

                        table.add_row(
                            issue.rule_id,
                            f"[{severity_color}]{issue.severity.value.upper()}[/{severity_color}]",
                            issue.message,
                            issue.suggestion or "",
                        )

                    console.print(table)

                    # Summary
                    error_count = sum(
                        1 for i in filtered_issues if i.severity == LintSeverity.ERROR
                    )
                    warning_count = sum(
                        1 for i in filtered_issues if i.severity == LintSeverity.WARNING
                    )
                    info_count = sum(1 for i in filtered_issues if i.severity == LintSeverity.INFO)

                    console.print(f"\n[blue]Summary:[/blue] {len(filtered_issues)} issues")
                    if error_count > 0:
                        console.print(f"  [red]Errors:[/red] {error_count}")
                    if warning_count > 0:
                        console.print(f"  [yellow]Warnings:[/yellow] {warning_count}")
                    if info_count > 0:
                        console.print(f"  [blue]Info:[/blue] {info_count}")

        # Exit with error code if validation failed
        if not result.valid:
            raise SystemExit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise SystemExit(1) from e


@main.command("install-rule-pack")
@click.argument("package_name")
@click.option(
    "--version",
    default="latest",
    help="Package version to install (default: latest)",
)
@click.option(
    "--repository",
    help="Repository to install from (default: search all)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force installation even if package already exists",
)
@click.option(
    "--verify-signature",
    is_flag=True,
    default=True,
    help="Verify package signature (default: true)",
)
def install_rule_pack(
    package_name: str, version: str, repository: Optional[str], force: bool, verify_signature: bool
) -> None:
    """Install a rule pack from a repository.

    Downloads and installs a rule pack from configured repositories.
    Handles dependency resolution and signature verification.

    Args:
        package_name: Name of the package to install

    Example:
        $ riveter install-rule-pack aws-security
        $ riveter install-rule-pack aws-security --version 2.1.0
        $ riveter install-rule-pack custom-rules --repository company-repo
    """
    try:
        RepositoryManager = lazy_importer.lazy_import(
            "riveter.rule_repository", "RepositoryManager"
        )
        RulePackManager = lazy_importer.lazy_import("riveter.rule_packs", "RulePackManager")
        RulePackageValidator = lazy_importer.lazy_import(
            "riveter.rule_distribution", "RulePackageValidator"
        )
        repo_manager = RepositoryManager()

        # Check if package already exists
        rule_pack_manager = RulePackManager()
        try:
            existing_pack = rule_pack_manager.load_rule_pack(package_name, version)
            if existing_pack and not force:
                console.print(
                    f"[yellow]Package {package_name} version {version} already installed[/yellow]"
                )
                console.print("Use --force to reinstall")
                return
        except FileNotFoundError:
            pass  # Package not installed, continue

        # Get package info
        package_info = repo_manager.get_package_info(package_name, version, repository)
        if not package_info:
            console.print(f"[red]Package {package_name} version {version} not found[/red]")
            if repository:
                console.print(f"Repository: {repository}")
            else:
                console.print("Searched all configured repositories")
            raise SystemExit(1)

        console.print(f"[blue]Installing:[/blue] {package_info.name} v{package_info.version}")
        console.print(f"[blue]Description:[/blue] {package_info.description}")
        console.print(f"[blue]Author:[/blue] {package_info.author}")
        console.print(f"[blue]Size:[/blue] {package_info.size_bytes} bytes")

        # Resolve dependencies
        if package_info.dependencies:
            console.print("[blue]Resolving dependencies...[/blue]")
            try:
                dependencies = repo_manager.resolve_dependencies(package_name, version)
                console.print(
                    f"[green]Found {len(dependencies)} packages (including dependencies)[/green]"
                )

                for dep in dependencies:
                    if dep.name != package_name:
                        console.print(f"  - {dep.name} v{dep.version}")
            except Exception as e:
                console.print(f"[red]Dependency resolution failed:[/red] {str(e)}")
                raise SystemExit(1) from e
        else:
            dependencies = [package_info]

        # Download and install packages
        import os
        import tempfile

        install_dir = os.path.expanduser("~/.riveter/rule_packs")
        os.makedirs(install_dir, exist_ok=True)

        for dep_info in dependencies:
            console.print(f"[blue]Downloading:[/blue] {dep_info.name} v{dep_info.version}")

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
                try:
                    # Download package
                    repo_manager.download_package(
                        dep_info.name, dep_info.version, temp_file.name, repository
                    )

                    # Validate package
                    if verify_signature:
                        validator = RulePackageValidator()
                        validation_result = validator.validate_package(
                            temp_file.name, verify_signature=True
                        )

                        if not validation_result["valid"]:
                            console.print(
                                f"[red]Package validation failed for {dep_info.name}:[/red]"
                            )
                            for error in validation_result["errors"]:
                                console.print(f"  - {error}")
                            raise SystemExit(1)

                        if validation_result["warnings"]:
                            console.print(f"[yellow]Warnings for {dep_info.name}:[/yellow]")
                            for warning in validation_result["warnings"]:
                                console.print(f"  - {warning}")

                    # Extract to install directory
                    import tempfile as tf
                    import zipfile

                    with tf.TemporaryDirectory() as extract_dir:
                        with zipfile.ZipFile(temp_file.name, "r") as zip_ref:
                            zip_ref.extractall(extract_dir)

                        # Copy rules.yml to install directory
                        rules_file = os.path.join(extract_dir, "rules.yml")
                        if os.path.exists(rules_file):
                            install_file = os.path.join(install_dir, f"{dep_info.name}.yml")
                            import shutil

                            shutil.copy2(rules_file, install_file)
                            console.print(
                                f"[green]✓ Installed:[/green] {dep_info.name} v{dep_info.version}"
                            )
                        else:
                            console.print(
                                f"[red]Error: rules.yml not found in package {dep_info.name}[/red]"
                            )
                            raise SystemExit(1)

                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_file.name)
                    except OSError:
                        pass

        console.print("\n[green]✓ Installation completed successfully[/green]")
        console.print(f"[blue]Installed packages:[/blue] {len(dependencies)}")
        console.print(f"[blue]Install directory:[/blue] {install_dir}")

    except Exception as e:
        console.print(f"[red]Installation failed:[/red] {str(e)}")
        raise SystemExit(1) from e


@main.command("update-rule-packs")
@click.option(
    "--package",
    multiple=True,
    help="Specific packages to update (default: all)",
)
@click.option(
    "--check-only",
    is_flag=True,
    help="Only check for updates, don't install",
)
def update_rule_packs(package: tuple[str, ...], check_only: bool) -> None:
    """Update installed rule packs to latest versions.

    Checks for updates to installed rule packs and optionally
    updates them to the latest available versions.

    Example:
        $ riveter update-rule-packs
        $ riveter update-rule-packs --package aws-security
        $ riveter update-rule-packs --check-only
    """
    try:
        RulePackManager = lazy_importer.lazy_import("riveter.rule_packs", "RulePackManager")
        RepositoryManager = lazy_importer.lazy_import(
            "riveter.rule_repository", "RepositoryManager"
        )
        rule_pack_manager = RulePackManager()
        repo_manager = RepositoryManager()

        # Get installed packages
        installed_packs = rule_pack_manager.list_available_packs()

        if not installed_packs:
            console.print("[yellow]No rule packs installed[/yellow]")
            return

        # Filter by specified packages if provided
        if package:
            installed_packs = [p for p in installed_packs if p["name"] in package]
            if not installed_packs:
                console.print(
                    f"[yellow]None of the specified packages are installed: "
                    f"{', '.join(package)}[/yellow]"
                )
                return

        console.print(
            f"[blue]Checking {len(installed_packs)} installed packages for updates...[/blue]"
        )

        updates_available = []

        for pack in installed_packs:
            pack_name = str(pack["name"])
            current_version = str(pack["version"])

            try:
                # Get latest version from repositories
                latest_info = repo_manager.get_package_info(pack_name, "latest")

                if latest_info and latest_info.version != current_version:
                    # Simple version comparison (assumes semantic versioning)
                    def version_tuple(v: str) -> tuple[int, ...]:
                        return tuple(map(int, v.split(".")))

                    try:
                        if version_tuple(latest_info.version) > version_tuple(current_version):
                            updates_available.append(
                                {
                                    "name": pack_name,
                                    "current_version": current_version,
                                    "latest_version": latest_info.version,
                                    "description": latest_info.description,
                                }
                            )
                    except ValueError:
                        # Non-semantic versioning, just check if different
                        if latest_info.version != current_version:
                            updates_available.append(
                                {
                                    "name": pack_name,
                                    "current_version": current_version,
                                    "latest_version": latest_info.version,
                                    "description": latest_info.description,
                                }
                            )

            except Exception:
                # Skip packages that can't be found in repositories
                continue

        if not updates_available:
            console.print("[green]✓ All installed packages are up to date[/green]")
            return

        # Display available updates
        console.print(
            f"\n[yellow]Updates available for {len(updates_available)} packages:[/yellow]"
        )

        table = Table()
        table.add_column("Package", style="cyan")
        table.add_column("Current", style="red")
        table.add_column("Latest", style="green")
        table.add_column("Description", style="white")

        for update in updates_available:
            table.add_row(
                update["name"],
                update["current_version"],
                update["latest_version"],
                (
                    update["description"][:50] + "..."
                    if len(update["description"]) > 50
                    else update["description"]
                ),
            )

        console.print(table)

        if check_only:
            console.print("\n[blue]Use 'riveter update-rule-packs' to install updates[/blue]")
            return

        # Install updates
        console.print("\n[blue]Installing updates...[/blue]")

        for update in updates_available:
            try:
                console.print(
                    f"[blue]Updating {update['name']} from {update['current_version']} "
                    f"to {update['latest_version']}...[/blue]"
                )

                # Use the install command logic
                repo_manager = RepositoryManager()
                package_info = repo_manager.get_package_info(
                    update["name"], update["latest_version"]
                )

                if package_info:
                    import os
                    import shutil
                    import tempfile
                    import zipfile

                    install_dir = os.path.expanduser("~/.riveter/rule_packs")

                    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
                        try:
                            repo_manager.download_package(
                                package_info.name, package_info.version, temp_file.name
                            )

                            with tempfile.TemporaryDirectory() as extract_dir:
                                with zipfile.ZipFile(temp_file.name, "r") as zip_ref:
                                    zip_ref.extractall(extract_dir)

                                rules_file = os.path.join(extract_dir, "rules.yml")
                                if os.path.exists(rules_file):
                                    install_file = os.path.join(
                                        install_dir, f"{package_info.name}.yml"
                                    )
                                    shutil.copy2(rules_file, install_file)
                                    console.print(
                                        f"[green]✓ Updated:[/green] {update['name']} "
                                        f"to v{update['latest_version']}"
                                    )
                                else:
                                    console.print(
                                        f"[red]Error: rules.yml not found in package "
                                        f"{update['name']}[/red]"
                                    )
                        finally:
                            try:
                                os.unlink(temp_file.name)
                            except OSError:
                                pass
                else:
                    console.print(f"[red]Failed to get package info for {update['name']}[/red]")

            except Exception as e:
                console.print(f"[red]Failed to update {update['name']}:[/red] {str(e)}")

        console.print("\n[green]✓ Update process completed[/green]")

    except Exception as e:
        console.print(f"[red]Update failed:[/red] {str(e)}")
        raise SystemExit(1) from e


@main.command("list-installed-packs")
@click.option(
    "--format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format",
)
def list_installed_packs(format: str) -> None:
    """List all installed rule packs.

    Shows detailed information about all locally installed rule packs
    including versions, rule counts, and installation paths.

    Example:
        $ riveter list-installed-packs
        $ riveter list-installed-packs --format json
    """
    try:
        RulePackManager = lazy_importer.lazy_import("riveter.rule_packs", "RulePackManager")
        rule_pack_manager = RulePackManager()
        packs = rule_pack_manager.list_available_packs()

        if not packs:
            if format == "json":
                import json

                console.print(json.dumps({"installed_packs": [], "total": 0}, indent=2))
            else:
                console.print("[yellow]No rule packs installed[/yellow]")
                console.print(
                    f"\n[blue]Install directory:[/blue] {rule_pack_manager.rule_pack_dirs}"
                )
            return

        if format == "json":
            import json

            output = {
                "installed_packs": packs,
                "total": len(packs),
                "install_directories": rule_pack_manager.rule_pack_dirs,
            }
            console.print(json.dumps(output, indent=2))
        else:
            table = Table(title="Installed Rule Packs")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Version", style="magenta")
            table.add_column("Rules", justify="right", style="green")
            table.add_column("Description", style="white")
            table.add_column("Author", style="blue")
            table.add_column("File Path", style="dim")

            for pack in packs:
                description = str(pack["description"])
                file_path = str(pack["file_path"])
                table.add_row(
                    str(pack["name"]),
                    str(pack["version"]),
                    str(pack["rule_count"]),
                    (description[:40] + "..." if len(description) > 40 else description),
                    str(pack["author"]),
                    (file_path[-50:] if len(file_path) > 50 else file_path),
                )

            console.print(table)
            console.print(f"\n[blue]Total installed packs:[/blue] {len(packs)}")
            console.print("[blue]Install directories:[/blue]")
            for directory in rule_pack_manager.rule_pack_dirs:
                console.print(f"  - {directory}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
