# Riveter Tutorial: Getting Started Guide

Welcome to Riveter, an infrastructure rule enforcement tool that validates Terraform configurations against custom rules and compliance standards. This tutorial will guide you through installation, basic usage, and advanced features.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Writing Your First Rule](#writing-your-first-rule)
4. [Using Pre-built Rule Packs](#using-pre-built-rule-packs)
5. [Advanced Rule Features](#advanced-rule-features)
6. [Configuration Management](#configuration-management)
7. [Output Formats](#output-formats)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/riveter.git
cd riveter

# Install in development mode
pip install -e .

# Verify installation
riveter --version
```

### Install from PyPI (when available)

```bash
pip install riveter
```

## Quick Start

Let's start with a simple example to validate an AWS EC2 instance configuration.

### Step 1: Create a Sample Terraform File

Create a file called `main.tf`:

```hcl
resource "aws_instance" "web_server" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}
```

### Step 2: Create a Simple Rule

Create a file called `rules.yml`:

```yaml
rules:
  - id: ec2-instance-type-check
    resource_type: aws_instance
    description: Ensure EC2 instances use approved instance types
    severity: error
    assert:
      instance_type:
        regex: "^(t3|m5|c5)\\.(large|xlarge)$"
```### Step 3:
Run Your First Scan

```bash
riveter scan --rules rules.yml --terraform main.tf
```

You should see output indicating that the rule failed because `t2.micro` doesn't match the approved instance types pattern.

### Step 4: Fix the Issue

Update your `main.tf` to use an approved instance type:

```hcl
resource "aws_instance" "web_server" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.large"  # Changed from t2.micro

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}
```

Run the scan again - it should now pass!

## Writing Your First Rule

Rules are the heart of Riveter. Let's explore how to write effective rules.

### Basic Rule Structure

```yaml
rules:
  - id: unique-rule-identifier
    resource_type: terraform_resource_type
    description: Human-readable description
    severity: error|warning|info
    filter:
      # Optional: conditions that determine if rule applies
    assert:
      # Required: conditions that must be true
```

### Example: S3 Bucket Security Rule

```yaml
rules:
  - id: s3-bucket-encryption
    resource_type: aws_s3_bucket
    description: Ensure S3 buckets have encryption enabled
    severity: error
    filter:
      # Only apply to production buckets
      tags.Environment: production
    assert:
      # Check that server_side_encryption_configuration exists
      server_side_encryption_configuration: present
```

### Rule Components Explained

- **id**: Unique identifier for the rule (required)
- **resource_type**: Terraform resource type or "*" for all types (required)
- **description**: Human-readable explanation of what the rule checks
- **severity**: Importance level - `error`, `warning`, or `info`
- **filter**: Conditions that determine if the rule applies to a resource
- **assert**: Conditions that must be true for the rule to pass (required)## Us
ing Pre-built Rule Packs

Riveter comes with pre-built rule packs for common security and compliance standards.

### Available Rule Packs

List all available rule packs:

```bash
riveter list-rule-packs
```

### Using AWS Security Rule Pack

```bash
riveter scan --rule-pack aws-security --terraform main.tf
```

### Using Multiple Rule Packs

```bash
riveter scan --rule-pack aws-security --rule-pack cis-aws --terraform main.tf
```

### Combining Rule Packs with Custom Rules

```bash
riveter scan --rule-pack aws-security --rules custom-rules.yml --terraform main.tf
```

## Advanced Rule Features

### Comparison Operators

Riveter supports advanced operators for sophisticated validation:

```yaml
rules:
  - id: volume-size-check
    resource_type: aws_instance
    description: Ensure root volume is large enough
    assert:
      root_block_device.volume_size:
        gte: 100  # Greater than or equal to 100 GB

  - id: instance-count-limit
    resource_type: aws_autoscaling_group
    description: Limit maximum instance count
    assert:
      max_size:
        lte: 10  # Less than or equal to 10 instances

  - id: naming-convention
    resource_type: aws_instance
    description: Enforce naming convention
    assert:
      tags.Name:
        regex: "^(web|app|db)-[a-z0-9-]+$"
```

### Available Operators

- **Numeric**: `gt`, `lt`, `gte`, `lte`, `ne`, `eq`
- **String**: `regex` (regular expression matching)
- **List**: `contains`, `length`, `subset`
- **Existence**: `present` (check if property exists)

### Nested Property Access

Use dot notation to access nested properties:

```yaml
rules:
  - id: vpc-dns-settings
    resource_type: aws_vpc
    description: Ensure VPC has proper DNS settings
    assert:
      enable_dns_hostnames: true
      enable_dns_support: true
      tags.Environment: present
```### Lis
t Operations

```yaml
rules:
  - id: security-group-rules
    resource_type: aws_security_group
    description: Validate security group configuration
    assert:
      ingress:
        length:
          lte: 5  # No more than 5 ingress rules
      egress:
        contains:
          - protocol: "-1"  # Must have allow-all egress rule

  - id: required-tags
    resource_type: "*"
    description: Ensure required tags are present
    assert:
      tags:
        subset:
          - Environment
          - Owner
          - Project
```

## Configuration Management

### Creating a Configuration File

Generate a sample configuration file:

```bash
riveter create-config
```

This creates `riveter.yml` with default settings:

```yaml
# Riveter Configuration File
rule_packs:
  - aws-security

rule_dirs:
  - ./rules
  - ./custom-rules

output_format: table

min_severity: info

include_rules: []
exclude_rules: []

debug: false
parallel: false
cache_dir: ~/.riveter/cache
```

### Using Configuration Files

```bash
riveter scan --config riveter.yml --terraform main.tf
```

### Environment-Specific Rules

Rules can be filtered based on environment context:

```yaml
rules:
  - id: prod-instance-types
    resource_type: aws_instance
    description: Production instances must use approved types
    severity: error
    filter:
      tags.Environment: production
    assert:
      instance_type:
        regex: "^(m5|c5)\\.(large|xlarge|2xlarge)$"

  - id: dev-instance-types
    resource_type: aws_instance
    description: Development instances can use smaller types
    severity: warning
    filter:
      tags.Environment: development
    assert:
      instance_type:
        regex: "^(t3|t2)\\.(micro|small|medium)$"
```##
 Output Formats

### Table Output (Default)

```bash
riveter scan --rules rules.yml --terraform main.tf
```

### JSON Output

```bash
riveter scan --rules rules.yml --terraform main.tf --output-format json
```

### JUnit XML (for CI/CD)

```bash
riveter scan --rules rules.yml --terraform main.tf --output-format junit
```

### SARIF (for Security Tools)

```bash
riveter scan --rules rules.yml --terraform main.tf --output-format sarif
```

## Performance Optimization

### Parallel Processing

Enable parallel processing for large configurations:

```bash
riveter scan --rules rules.yml --terraform main.tf --parallel
```

### Caching

Use caching to speed up repeated scans:

```bash
riveter scan --rules rules.yml --terraform main.tf --cache-dir ~/.riveter/cache
```

### Incremental Scanning

Only scan changed resources:

```bash
# First scan creates baseline
riveter scan --rules rules.yml --terraform main.tf --baseline .riveter_baseline.json

# Subsequent scans only check changed resources
riveter scan --rules rules.yml --terraform main.tf --baseline .riveter_baseline.json
```

### Performance Benchmarking

Measure performance with benchmarking:

```bash
riveter scan --rules rules.yml --terraform main.tf --benchmark --parallel
```

## Troubleshooting

### Common Issues

#### 1. "No rules loaded" Error

**Problem**: Riveter can't find or load your rules.

**Solutions**:
- Check that the rules file exists and is readable
- Verify YAML syntax with a YAML validator
- Ensure the file contains a `rules:` section
- Check file permissions

#### 2. "Rule validation failed" Error

**Problem**: Rule definition is invalid.

**Solutions**:
- Ensure all required fields are present (`id`, `resource_type`, `assert`)
- Check operator syntax and values
- Validate property paths exist in your resources
- Use `riveter validate-rule-pack rules.yml` to check syntax#
### 3. "No matching resources found" Warning

**Problem**: Rules don't match any resources in your Terraform configuration.

**Solutions**:
- Check that `resource_type` matches your Terraform resources
- Verify filter conditions aren't too restrictive
- Use `resource_type: "*"` for rules that should apply to all resources
- Check that your Terraform file contains the expected resources

#### 4. Performance Issues

**Problem**: Scanning takes too long.

**Solutions**:
- Enable parallel processing with `--parallel`
- Use caching with `--cache-dir`
- Filter rules with `--min-severity` to reduce processing
- Use incremental scanning with `--baseline`

### Debug Mode

Enable debug mode for detailed information:

```bash
riveter scan --rules rules.yml --terraform main.tf --debug
```

### Structured Logging

Use JSON logging for automated processing:

```bash
riveter scan --rules rules.yml --terraform main.tf --log-format json
```

## Real-World Examples

### Example 1: AWS Security Baseline

Create a comprehensive security rule set:

```yaml
rules:
  - id: s3-bucket-public-read
    resource_type: aws_s3_bucket_public_access_block
    description: Prevent S3 buckets from allowing public read access
    severity: error
    assert:
      block_public_acls: true
      block_public_policy: true
      ignore_public_acls: true
      restrict_public_buckets: true

  - id: ec2-security-groups-ssh
    resource_type: aws_security_group
    description: Prevent SSH access from 0.0.0.0/0
    severity: error
    assert:
      ingress:
        contains:
          from_port: 22
          to_port: 22
          cidr_blocks:
            ne: ["0.0.0.0/0"]

  - id: rds-encryption
    resource_type: aws_db_instance
    description: Ensure RDS instances are encrypted
    severity: error
    assert:
      storage_encrypted: true
```

### Example 2: Multi-Cloud Compliance

```yaml
rules:
  - id: aws-instance-tags
    resource_type: aws_instance
    description: AWS instances must have required tags
    severity: warning
    assert:
      tags.Environment: present
      tags.Owner: present
      tags.CostCenter:
        regex: "^\\d{5}$"

  - id: azure-vm-tags
    resource_type: azurerm_virtual_machine
    description: Azure VMs must have required tags
    severity: warning
    assert:
      tags.Environment: present
      tags.Owner: present
```### Examp
le 3: CI/CD Integration

Create a CI/CD pipeline configuration:

```yaml
# .github/workflows/terraform-validation.yml
name: Terraform Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Riveter
        run: pip install riveter

      - name: Validate Terraform
        run: |
          riveter scan \
            --rule-pack aws-security \
            --rule-pack cis-aws \
            --terraform infrastructure/main.tf \
            --output-format junit \
            --min-severity warning > results.xml

      - name: Publish Test Results
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Riveter Results
          path: results.xml
          reporter: java-junit
```

## Next Steps

Now that you've learned the basics of Riveter, here are some next steps:

1. **Explore Rule Packs**: Try different pre-built rule packs for your cloud provider
2. **Create Custom Rules**: Write rules specific to your organization's requirements
3. **Integrate with CI/CD**: Add Riveter to your deployment pipeline
4. **Performance Tuning**: Optimize scanning for large Terraform configurations
5. **Contribute**: Help improve Riveter by contributing rules or features

## Getting Help

- **Documentation**: Check the full documentation in the `docs/` directory
- **Issues**: Report bugs or request features on GitHub
- **Community**: Join discussions and share rule packs with the community

## Conclusion

Riveter provides a powerful and flexible way to enforce infrastructure standards and security policies. By combining custom rules with pre-built rule packs, you can ensure your Terraform configurations meet your organization's requirements while maintaining consistency across environments.

Start with simple rules and gradually build more sophisticated validation logic as you become comfortable with the tool. Remember that good infrastructure governance is an iterative process - your rules will evolve as your infrastructure and requirements change.

Happy validating!
