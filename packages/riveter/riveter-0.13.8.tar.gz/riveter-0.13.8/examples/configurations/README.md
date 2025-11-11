# Riveter Configuration Examples

This directory contains example configuration files for different use cases and environments. These configurations demonstrate various features and can be used as starting points for your own setup.

## Configuration Files

### Basic Configuration
- **File**: `basic-config.yml`
- **Use Case**: Simple setup for getting started with Riveter
- **Features**: Basic rule pack loading, standard output, minimal configuration

### Production Configuration
- **File**: `production-config.yml`
- **Use Case**: Production environments with strict security requirements
- **Features**: Multiple rule packs, JSON output, parallel processing, structured logging

### Development Configuration
- **File**: `development-config.yml`
- **Use Case**: Development environments with detailed feedback
- **Features**: Debug mode, verbose logging, development-specific rules

### CI/CD Configuration
- **File**: `ci-cd-config.yml`
- **Use Case**: Continuous integration and deployment pipelines
- **Features**: JUnit XML output, optimized for automation, fail-fast behavior

### Multi-Cloud Configuration
- **File**: `multi-cloud-config.yml`
- **Use Case**: Organizations using multiple cloud providers (AWS, Azure, GCP)
- **Features**: Multi-cloud rule packs, cloud-specific rule directories

### Security-Focused Configuration
- **File**: `security-focused-config.yml`
- **Use Case**: Security teams and security-focused validation
- **Features**: SARIF output, security rule filtering, compliance frameworks

### Performance-Optimized Configuration
- **File**: `performance-optimized-config.yml`
- **Use Case**: Large Terraform configurations requiring fast processing
- **Features**: Parallel processing, caching, resource limits, performance tuning

### Team Configuration
- **File**: `team-config.yml`
- **Use Case**: Team collaboration with shared standards
- **Features**: Team rule directories, collaboration tools integration, shared baselines

## Using Configuration Files

### Command Line Usage

```bash
# Use a specific configuration file
riveter scan --config examples/configurations/production-config.yml --terraform main.tf

# Override configuration settings
riveter scan --config basic-config.yml --terraform main.tf --output-format json

# Create your own configuration based on an example
cp examples/configurations/basic-config.yml my-config.yml
```

### Configuration Hierarchy

Riveter uses the following configuration hierarchy (highest priority first):

1. Command-line arguments
2. Configuration file (specified with `--config`)
3. Default values

### Environment Variables

Some configurations support environment variable substitution:

```yaml
# In configuration file
integrations:
  slack_webhook: "${SLACK_WEBHOOK_URL}"

# Set environment variable
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

## Configuration Options Reference

### Core Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `rule_packs` | list | Pre-built rule packs to load | `[]` |
| `rule_dirs` | list | Directories to search for custom rules | `[]` |
| `output_format` | string | Output format (table, json, junit, sarif) | `table` |
| `min_severity` | string | Minimum severity level (info, warning, error) | `info` |
| `include_rules` | list | Patterns for rules to include | `[]` |
| `exclude_rules` | list | Patterns for rules to exclude | `[]` |

### Performance Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `debug` | boolean | Enable debug mode | `false` |
| `parallel` | boolean | Enable parallel processing | `false` |
| `cache_dir` | string | Directory for caching | `~/.riveter/cache` |
| `baseline` | string | Baseline file for incremental scanning | `null` |
| `max_workers` | integer | Maximum parallel workers | CPU count |
| `timeout` | integer | Timeout in seconds | `300` |

### Logging Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `log_level` | string | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `log_format` | string | Log format (human, json) | `human` |

## Customizing Configurations

### Creating Your Own Configuration

1. **Start with an Example**: Copy the configuration that best matches your use case
2. **Modify Settings**: Adjust options based on your requirements
3. **Test Configuration**: Validate your configuration works as expected
4. **Document Changes**: Add comments explaining your customizations

### Example Customization

```yaml
# Custom configuration based on production-config.yml
rule_packs:
  - aws-security
  - my-company-rules  # Custom company rule pack

rule_dirs:
  - ./rules
  - /shared/company-rules  # Shared company rules

# Custom output for our monitoring system
output_format: json

# Only show errors in production
min_severity: error

# Custom filtering for our environment
include_rules:
  - "*production*"
  - "*critical*"

exclude_rules:
  - "*dev*"
  - "*test*"

# Performance settings for our infrastructure
parallel: true
max_workers: 4
cache_dir: /var/cache/riveter

# Integration with our logging system
log_level: WARNING
log_format: json
```

## Best Practices

### Configuration Management

1. **Version Control**: Store configuration files in version control
2. **Environment Specific**: Use different configurations for different environments
3. **Documentation**: Document configuration choices and customizations
4. **Testing**: Test configurations with sample Terraform files

### Security Considerations

1. **Sensitive Data**: Don't store secrets in configuration files
2. **Environment Variables**: Use environment variables for sensitive values
3. **File Permissions**: Restrict access to configuration files containing sensitive information
4. **Validation**: Validate configuration files before deployment

### Performance Optimization

1. **Rule Filtering**: Use include/exclude patterns to limit rule processing
2. **Parallel Processing**: Enable parallel processing for large configurations
3. **Caching**: Use caching for repeated scans of the same files
4. **Incremental Scanning**: Use baselines for incremental scanning

## Troubleshooting

### Common Issues

1. **Configuration Not Found**: Ensure the configuration file path is correct
2. **Invalid YAML**: Validate YAML syntax using a YAML validator
3. **Rule Pack Not Found**: Check that rule pack names are correct and available
4. **Permission Errors**: Ensure Riveter has read access to configuration files

### Validation

```bash
# Test configuration file
riveter scan --config my-config.yml --terraform examples/terraform/simple.tf

# Validate rule packs
riveter list-rule-packs

# Debug configuration loading
riveter scan --config my-config.yml --terraform main.tf --debug
```

## Contributing

If you have configuration examples that would be useful for others, please consider contributing them:

1. Create a new configuration file with descriptive naming
2. Add comprehensive comments explaining the use case
3. Test the configuration with sample Terraform files
4. Update this README with information about your configuration
5. Submit a pull request

## Support

For help with configuration:

1. Check the main documentation
2. Review existing configuration examples
3. Ask questions in GitHub Discussions
4. Report issues on GitHub
