# Frequently Asked Questions (FAQ)

This FAQ addresses the most common questions about Riveter installation, usage, integration, and comparisons with other tools.

💡 **Tip**: Use Ctrl+F (Cmd+F on Mac) to quickly find answers to your specific questions.

🚀 **Quick Action**: Can't find your question? Check our [GitHub Discussions](https://github.com/riveter/riveter/discussions) or ask a new question.

## Installation and Setup

### Q: Which installation method should I choose?

**A: Homebrew is recommended for most users.**

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Homebrew** | Most users | ✅ Single binary<br>✅ Fast startup<br>✅ Auto-updates<br>✅ No Python deps | ❌ Requires Homebrew |
| **Python/pip** | Python developers<br>Custom environments | ✅ Full source access<br>✅ Easy customization<br>✅ Works anywhere | ❌ Slower startup<br>❌ Virtual env management |
| **Docker** | Containerized workflows | ✅ Isolated environment<br>✅ Consistent across systems | ❌ Docker overhead<br>❌ Volume mounting needed |

**Quick Installation**:
```bash
# Homebrew (recommended)
brew install scottryanhoward/homebrew-riveter/riveter

# Python alternative
git clone https://github.com/riveter/riveter.git
cd riveter && python3 -m venv venv && source venv/bin/activate && pip install -e .
```

🔗 **Related**: [Installation Guide](README.md#installation) | [Installation Migration Guide](../installation/migration.md)

### Q: Do I need Terraform installed to use Riveter?

**A: No, Terraform is not required for basic Riveter usage.**

Riveter parses Terraform files directly using its built-in HCL parser. However, having Terraform installed is helpful for:

- **Syntax validation**: `terraform validate` before running Riveter
- **File formatting**: `terraform fmt` to clean up your files
- **Plan generation**: `terraform plan` for comprehensive validation

**Recommended workflow**:
```bash
# 1. Write Terraform
vim main.tf

# 2. Format and validate (if Terraform is installed)
terraform fmt main.tf
terraform validate

# 3. Run Riveter validation
riveter scan -p aws-security -t main.tf

# 4. Fix any issues and repeat
```

🔗 **Related**: [Terraform Integration](../terraform/integration.md) | [Workflow Best Practices](../guides/workflow.md)

### Q: Can I use Riveter without internet access?

**A: Yes, once installed, Riveter works completely offline.**

- **Rule packs**: Bundled with installation, no downloads needed
- **Custom rules**: Loaded from local files
- **Terraform parsing**: Done locally
- **No telemetry**: Riveter doesn't send any data externally

**Offline installation options**:
```bash
# 1. Download and install locally
git clone https://github.com/riveter/riveter.git
cd riveter && pip install -e .

# 2. Use pre-built binary (if available)
# Download from GitHub releases page

# 3. Corporate environments
# Use internal package repositories or manual installation
```

🔗 **Related**: [Offline Installation](../installation/offline.md) | [Corporate Networks](../installation/corporate-networks.md)

### Q: I'm getting checksum errors when upgrading Riveter via Homebrew. Is this normal?

**A: Yes, this is a known issue with placeholder checksums in the Homebrew formula. The upgrade still works.**

**Common error messages**:
```
✘ Resource riveter--rule_packs
Warning: Resource reports different checksum: placeholder_source_checksum
SHA-256 checksum of downloaded file: 2f12aad9da840a6bf7c3b00916e42e933979104e9c0cce

✘ Formula riveter (0.12.0)
Warning: Formula reports different checksum: placeholder_checksum_macos_arm64
SHA-256 checksum of downloaded file: a3027dac4f319137805b6355df5df57bce224636bec46b4
```

**Quick solutions**:
```bash
# Option 1: Ignore checksum verification
brew upgrade riveter --ignore-dependencies

# Option 2: Clear cache and retry
brew cleanup riveter
rm -rf "$(brew --cache)/downloads/*riveter*"
brew upgrade riveter

# Option 3: Reinstall if needed
brew uninstall riveter
brew install scottryanhoward/homebrew-riveter/riveter --ignore-dependencies
```

**Why this happens**:
- The Homebrew formula uses placeholder checksums during development
- The actual downloaded files have different checksums than the placeholders
- This is a formula maintenance issue, not a security problem
- Riveter functions normally despite these warnings

**Verification**:
```bash
# Confirm Riveter works after upgrade
riveter --version
riveter list-rule-packs
riveter scan -p aws-security -t examples/quickstart/basic-aws.tf
```

🔗 **Related**: [Homebrew Troubleshooting](troubleshooting.md#checksum-mismatch-errors-during-upgrade) | [Error Dictionary](error-message-dictionary.md#resource-reports-different-checksum)

## Usage and Configuration

### Q: How do I choose the right rule packs?

**A: Start with cloud-specific security packs, then add compliance frameworks as needed.**

**Decision flowchart**:
```
1. What cloud provider(s) do you use?
   ├─ AWS only → Start with `aws-security`
   ├─ Azure only → Start with `azure-security`
   ├─ GCP only → Start with `gcp-security`
   └─ Multi-cloud → Start with `multi-cloud-security`

2. Do you need compliance frameworks?
   ├─ Healthcare → Add `aws-hipaa` or `azure-hipaa`
   ├─ Finance → Add `aws-pci-dss`
   ├─ General compliance → Add `soc2-security`
   └─ Industry benchmarks → Add `cis-aws`, `cis-azure`, or `cis-gcp`

3. Do you follow well-architected principles?
   └─ Add `aws-well-architected`, `azure-well-architected`, or `gcp-well-architected`
```

**Common combinations**:
```bash
# Startup/Small company
riveter scan -p aws-security -t main.tf

# Enterprise AWS
riveter scan -p aws-security -p cis-aws -p aws-well-architected -t main.tf

# Healthcare
riveter scan -p aws-security -p aws-hipaa -p soc2-security -t main.tf

# Multi-cloud enterprise
riveter scan -p aws-security -p azure-security -p gcp-security -p soc2-security -t main.tf
```

🔗 **Related**: [Rule Packs Guide](rule-packs.md) | [Compliance Mapping](../compliance/framework-mapping.md)

### Q: Can I combine custom rules with rule packs?

**A: Yes, you can use both custom rules and rule packs together.**

```bash
# Combine custom rules with rule packs
riveter scan -r my-company-rules.yml -p aws-security -p cis-aws -t main.tf
```

**Rule precedence**:
1. Custom rules are loaded first
2. Rule pack rules are loaded second
3. If rule IDs conflict, custom rules take precedence
4. All rules are evaluated independently

**Example custom rules file**:
```yaml
# my-company-rules.yml
rules:
  - id: company-naming-convention
    description: Resources must follow company naming convention
    resource_type: aws_instance
    assert:
      tags.Name:
        regex: "^(prod|dev|test)-.*"

  - id: company-instance-types
    description: Only approved instance types allowed
    resource_type: aws_instance
    assert:
      instance_type:
        regex: "^(t3|m5|c5)\\.(large|xlarge)$"
```

🔗 **Related**: [Custom Rules Guide](../advanced/custom-rules.md) | [Rule Precedence](../reference/rule-precedence.md)

### Q: How do I handle false positives?

**A: Use rule filters, modify rules, or create exceptions.**

**1. Use rule filters to target specific resources**:
```yaml
rules:
  - id: production-only-rule
    description: Only applies to production resources
    resource_type: aws_instance
    filter:
      tags.Environment: production  # Only check prod resources
    assert:
      instance_type:
        regex: "^(m5|c5)\\.(large|xlarge)$"
```

**2. Modify rule conditions**:
```yaml
# Instead of strict equality
assert:
  instance_type: t3.large

# Use flexible regex
assert:
  instance_type:
    regex: "^(t3|m5)\\.(large|xlarge)$"
```

**3. Create environment-specific rule packs**:
```bash
# Development environment (relaxed rules)
riveter scan -r dev-rules.yml -t main.tf

# Production environment (strict rules)
riveter scan -r prod-rules.yml -p aws-security -p cis-aws -t main.tf
```

**4. Use conditional validation**:
```yaml
rules:
  - id: conditional-encryption
    description: Encryption required for sensitive data
    resource_type: aws_s3_bucket
    filter:
      tags.DataClassification: sensitive
    assert:
      server_side_encryption_configuration: present
```

🔗 **Related**: [Rule Filtering](../reference/rule-filtering.md) | [Environment-Specific Rules](../guides/environment-rules.md)

## Comparisons with Other Tools

### Q: How does Riveter compare to Checkov?

**A: Riveter focuses on simplicity and pre-built compliance, while Checkov offers broader language support.**

| Feature | Riveter | Checkov |
|---------|---------|---------|
| **Installation** | ✅ Single binary (Homebrew) | ⚠️ Python dependencies |
| **Rule Creation** | ✅ Simple YAML | ❌ Python code required |
| **Compliance Packs** | ✅ 15+ ready-to-use frameworks | ❌ Manual setup needed |
| **Terraform Focus** | ✅ Purpose-built for Terraform | ⚠️ Multi-language (broader but complex) |
| **Performance** | ✅ Fast startup | ⚠️ Slower Python startup |
| **Custom Rules** | ✅ YAML-based, easy to write | ❌ Requires Python knowledge |
| **CI/CD Integration** | ✅ Multiple output formats | ✅ Good integration |
| **Community** | 🆕 Growing | ✅ Large, established |

**When to choose Riveter**:
- You primarily use Terraform
- You want ready-to-use compliance frameworks
- You prefer simple YAML rule syntax
- You need fast CI/CD integration

**When to choose Checkov**:
- You use multiple IaC languages (CloudFormation, ARM, etc.)
- You have Python expertise for custom rules
- You need the largest rule library
- You want the most mature ecosystem

🔗 **Related**: [Tool Comparison Guide](../comparisons/checkov-vs-riveter.md) | [Migration from Checkov](../migration/from-checkov.md)

### Q: How does Riveter compare to TFLint?

**A: Riveter focuses on security/compliance, while TFLint focuses on Terraform best practices.**

| Feature | Riveter | TFLint |
|---------|---------|--------|
| **Primary Focus** | 🛡️ Security & Compliance | 🔧 Terraform Best Practices |
| **Rule Types** | Security, compliance frameworks | Syntax, deprecated features, provider-specific |
| **Installation** | ✅ Homebrew or Python | ✅ Single binary |
| **Rule Creation** | ✅ YAML-based | ❌ Go programming required |
| **Compliance** | ✅ 15+ frameworks (CIS, SOC2, HIPAA) | ❌ No compliance frameworks |
| **Cloud Coverage** | ✅ AWS, Azure, GCP security | ⚠️ Provider-specific rules |
| **Performance** | ✅ Fast | ✅ Very fast |

**Complementary usage**:
```bash
# Use both tools together for comprehensive validation
terraform fmt main.tf           # Format code
terraform validate             # Basic syntax check
tflint main.tf                # Terraform best practices
riveter scan -p aws-security -t main.tf  # Security & compliance
```

**When to use Riveter**:
- Security and compliance validation
- Multi-cloud security standards
- Regulatory compliance (HIPAA, PCI-DSS, SOC2)
- Team security policies

**When to use TFLint**:
- Terraform syntax and style checking
- Provider-specific best practices
- Deprecated resource detection
- Code quality enforcement

🔗 **Related**: [TFLint Integration](../integrations/tflint.md) | [Complementary Tools](../guides/tool-combinations.md)

### Q: Can I use Riveter with Terrascan?

**A: Yes, they complement each other well with different focuses.**

| Tool | Focus | Best Used For |
|------|-------|---------------|
| **Riveter** | Terraform-specific security & compliance | Pre-deployment validation, compliance frameworks |
| **Terrascan** | Multi-IaC security scanning | Broader IaC security, policy as code |

**Complementary workflow**:
```bash
# 1. Terraform validation
terraform validate

# 2. Riveter for compliance
riveter scan -p aws-security -p cis-aws -t main.tf

# 3. Terrascan for additional security checks
terrascan scan -t terraform -f main.tf

# 4. Deploy if all pass
terraform apply
```

🔗 **Related**: [Multi-Tool Workflows](../guides/multi-tool-workflows.md) | [Security Tool Comparison](../comparisons/security-tools.md)

## CI/CD Integration

### Q: How do I integrate Riveter into my CI/CD pipeline?

**A: Riveter supports multiple CI/CD platforms with various output formats.**

### GitHub Actions
```yaml
name: Infrastructure Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Riveter
        run: brew install scottryanhoward/homebrew-riveter/riveter
      - name: Validate Infrastructure
        run: |
          riveter scan -p aws-security -p cis-aws -t main.tf --output-format sarif > results.sarif
      - name: Upload Results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

### GitLab CI
```yaml
infrastructure-validation:
  stage: validate
  image: ubuntu:latest
  before_script:
    - apt-get update && apt-get install -y curl git
    - /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    - eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
  script:
    - brew install scottryanhoward/homebrew-riveter/riveter
    - riveter scan -p aws-security -t main.tf --output-format junit > results.xml
  artifacts:
    reports:
      junit: results.xml
```

### Jenkins
```groovy
pipeline {
    agent any
    stages {
        stage('Validate Infrastructure') {
            steps {
                sh '''
                    brew install scottryanhoward/homebrew-riveter/riveter
                    riveter scan -p aws-security -t main.tf --output-format junit > results.xml
                '''
            }
            post {
                always {
                    junit 'results.xml'
                }
            }
        }
    }
}
```

🔗 **Related**: [CI/CD Integration Guide](../cicd/README.md) | [Pipeline Examples](../cicd/examples/)

### Q: What output formats does Riveter support for CI/CD?

**A: Riveter supports 4 output formats optimized for different use cases.**

| Format | Use Case | Example |
|--------|----------|---------|
| **table** | Human-readable terminal output | Local development, debugging |
| **json** | Programmatic processing | Custom dashboards, automation |
| **junit** | CI/CD test reporting | Jenkins, GitLab CI, GitHub Actions |
| **sarif** | Security tool integration | GitHub Security tab, security dashboards |

**Examples**:
```bash
# Terminal output (default)
riveter scan -p aws-security -t main.tf

# JSON for automation
riveter scan -p aws-security -t main.tf --output-format json > results.json

# JUnit for CI/CD
riveter scan -p aws-security -t main.tf --output-format junit > results.xml

# SARIF for security tools
riveter scan -p aws-security -t main.tf --output-format sarif > results.sarif
```

**Processing JSON output**:
```bash
# Count failures
jq '.summary.failed' results.json

# List failed resources
jq '.results[] | select(.status == "FAIL") | .resource' results.json

# Filter by severity
jq '.results[] | select(.severity == "error")' results.json
```

🔗 **Related**: [Output Formats Guide](../reference/output-formats.md) | [JSON Processing Examples](../guides/json-processing.md)

### Q: How do I fail CI/CD builds on validation failures?

**A: Riveter returns appropriate exit codes that CI/CD systems can use.**

**Exit codes**:
- `0`: All validations passed
- `1`: One or more validation failures or errors

**CI/CD configuration**:
```bash
# Basic usage (fails build on any validation failure)
riveter scan -p aws-security -t main.tf

# Custom handling
if ! riveter scan -p aws-security -t main.tf --output-format json > results.json; then
    echo "Validation failed, but continuing..."
    # Custom logic here
fi

# Conditional failure based on severity
riveter scan -p aws-security -t main.tf --output-format json > results.json
ERRORS=$(jq '.results[] | select(.severity == "error") | length' results.json)
if [ "$ERRORS" -gt 0 ]; then
    echo "Found $ERRORS critical errors, failing build"
    exit 1
fi
```

**GitHub Actions example**:
```yaml
- name: Validate Infrastructure
  run: |
    riveter scan -p aws-security -t main.tf --output-format json > results.json

    # Fail on errors, warn on warnings
    ERRORS=$(jq '.summary.failed' results.json)
    if [ "$ERRORS" -gt 0 ]; then
      echo "::error::Found $ERRORS validation failures"
      exit 1
    fi
```

🔗 **Related**: [CI/CD Best Practices](../cicd/best-practices.md) | [Error Handling](../guides/error-handling.md)

## Performance and Scaling

### Q: How fast is Riveter compared to other tools?

**A: Riveter is optimized for speed, especially with Homebrew installation.**

**Performance benchmarks** (approximate, varies by system):

| Tool | Startup Time | Small File (10 resources) | Large File (100 resources) |
|------|-------------|---------------------------|----------------------------|
| **Riveter (Homebrew)** | 0.5s | 1-2s | 3-5s |
| **Riveter (Python)** | 2-3s | 3-4s | 6-8s |
| **Checkov** | 3-5s | 5-8s | 15-25s |
| **TFLint** | 0.3s | 0.5-1s | 2-3s |

**Optimization tips**:
```bash
# Fastest: Homebrew installation
brew install scottryanhoward/homebrew-riveter/riveter

# Faster: Targeted rule packs
riveter scan -p aws-security -t main.tf  # Instead of multiple packs

# Faster: Smaller files
riveter scan -p aws-security -t modules/vpc/main.tf  # Instead of monolithic files
```

🔗 **Related**: [Performance Optimization](../guides/performance.md) | [Benchmarking](../reference/benchmarks.md)

### Q: Can Riveter handle large Terraform files?

**A: Yes, but performance depends on file size and system resources.**

**File size guidelines**:
- **Small** (< 100 lines): Instant validation
- **Medium** (100-1000 lines): 1-5 seconds
- **Large** (1000+ lines): 5-15 seconds
- **Very large** (5000+ lines): Consider splitting

**Optimization strategies**:
```bash
# 1. Use Homebrew for better performance
brew install scottryanhoward/homebrew-riveter/riveter

# 2. Split large files into modules
terraform fmt main.tf  # Clean formatting first
# Then split into logical modules

# 3. Validate modules separately
riveter scan -p aws-security -t modules/vpc/main.tf
riveter scan -p aws-security -t modules/ec2/main.tf
riveter scan -p aws-security -t modules/rds/main.tf

# 4. Use targeted rule packs
riveter scan -p aws-security -t main.tf  # Instead of all rule packs
```

**Memory usage**:
- **Homebrew**: 50-100MB for typical files
- **Python**: 100-200MB for typical files
- **Large files**: Add 50-100MB per 1000 lines

🔗 **Related**: [Large File Handling](../guides/large-files.md) | [Memory Optimization](../reference/memory-optimization.md)

## Troubleshooting

### Q: Why am I getting "command not found" errors?

**A: This usually indicates PATH configuration issues.**

**Quick diagnosis**:
```bash
# Check if Riveter is installed
which riveter

# Check PATH configuration
echo $PATH

# For Homebrew installation
echo $PATH | grep brew
```

**Solutions by installation method**:

**Homebrew**:
```bash
# Add Homebrew to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc  # Apple Silicon
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc    # Intel Mac
source ~/.zshrc

# Verify fix
which riveter && riveter --version
```

**Python**:
```bash
# Activate virtual environment
source venv/bin/activate

# Verify activation
which python  # Should show venv path
which riveter
```

🔗 **Related**: [Installation Troubleshooting](troubleshooting.md#installation-issues) | [PATH Configuration](../reference/path-setup.md)

### Q: Why are my validation results different between runs?

**A: Results should be consistent unless files or rules have changed.**

**Common causes of inconsistent results**:

1. **File changes between runs**:
   ```bash
   # Check if files were modified
   git status
   git diff main.tf
   ```

2. **Different rule packs or versions**:
   ```bash
   # Check Riveter version
   riveter --version

   # List rule packs
   riveter list-rule-packs
   ```

3. **Different installation methods**:
   ```bash
   # Check which installation you're using
   which riveter
   ls -la $(which riveter)
   ```

4. **Environment differences**:
   ```bash
   # Check environment variables
   env | grep -i riveter

   # Check working directory
   pwd
   ls -la main.tf
   ```

**Debugging steps**:
```bash
# 1. Use identical commands
riveter scan -p aws-security -t main.tf --output-format json > run1.json
riveter scan -p aws-security -t main.tf --output-format json > run2.json

# 2. Compare results
diff run1.json run2.json

# 3. Check file timestamps
ls -la main.tf

# 4. Verify rule pack integrity
riveter validate-rule-pack rule_packs/aws-security.yml
```

🔗 **Related**: [Debugging Guide](../guides/debugging.md) | [Reproducible Results](../reference/reproducibility.md)

### Q: How do I report bugs or request features?

**A: Use GitHub Issues with detailed information.**

**Before reporting**:
1. **Search existing issues**: [GitHub Issues](https://github.com/riveter/riveter/issues)
2. **Check documentation**: [Troubleshooting](troubleshooting.md) | [FAQ](faq.md)
3. **Try latest version**: `brew upgrade riveter` or `git pull && pip install -e .`

**Bug report template**:
```bash
# System Information
riveter --version
uname -a
echo $SHELL

# Command that failed
riveter scan -p aws-security -t main.tf

# Full error output
[Paste complete error message]

# File information (if relevant)
ls -la main.tf
head -10 main.tf  # First 10 lines (remove sensitive data)
```

**Feature request template**:
- **Problem**: What problem does this solve?
- **Solution**: What would you like to see?
- **Alternatives**: What workarounds exist?
- **Use case**: How would you use this feature?

**Community channels**:
- 🐛 **[GitHub Issues](https://github.com/riveter/riveter/issues)** - Bug reports and feature requests
- 💬 **[GitHub Discussions](https://github.com/riveter/riveter/discussions)** - Questions and community support
- 📖 **[Documentation](README.md)** - Comprehensive guides and references

🔗 **Related**: [Contributing Guide](../../CONTRIBUTING.md) | [Bug Report Template](../../.github/ISSUE_TEMPLATE/bug_report.md)

## Advanced Usage

### Q: Can I create organization-specific rule packs?

**A: Yes, you can create custom rule packs for your organization's standards.**

**Creating a custom rule pack**:
```bash
# 1. Generate template
riveter create-rule-pack-template company-standards company-rules.yml

# 2. Edit the template
vim company-rules.yml

# 3. Validate your rule pack
riveter validate-rule-pack company-rules.yml

# 4. Use your custom rule pack
riveter scan -r company-rules.yml -p aws-security -t main.tf
```

**Example organization rule pack**:
```yaml
# company-rules.yml
metadata:
  name: company-standards
  version: 1.0.0
  description: Acme Corp infrastructure standards
  author: Platform Team
  tags: [security, compliance, company-policy]

rules:
  - id: company-naming-convention
    description: Resources must follow company naming convention
    resource_type: aws_instance
    assert:
      tags.Name:
        regex: "^(prod|dev|test)-[a-z0-9-]+$"

  - id: company-approved-regions
    description: Resources must be in approved regions
    resource_type: aws_instance
    filter:
      tags.Environment: production
    assert:
      availability_zone:
        regex: "^(us-east-1|us-west-2)"

  - id: company-cost-center-tag
    description: All resources must have cost center tag
    resource_type: aws_instance
    assert:
      tags.CostCenter: present

  - id: company-instance-types
    description: Only approved instance types allowed
    resource_type: aws_instance
    assert:
      instance_type:
        regex: "^(t3|m5|c5)\\.(large|xlarge|2xlarge)$"
```

**Distribution strategies**:
```bash
# 1. Version control
git add company-rules.yml
git commit -m "Add company infrastructure standards"

# 2. Package repository
# Create internal package with rule pack

# 3. Shared network location
# Store on shared drive or internal web server

# 4. CI/CD integration
# Automatically download latest version in pipelines
```

🔗 **Related**: [Custom Rule Packs](../advanced/custom-rule-packs.md) | [Organization Standards](../guides/organization-standards.md)

### Q: How do I validate Terraform modules?

**A: Riveter validates the resources defined in your modules.**

**Module validation approaches**:

1. **Validate module files directly**:
   ```bash
   # Validate individual module files
   riveter scan -p aws-security -t modules/vpc/main.tf
   riveter scan -p aws-security -t modules/ec2/main.tf
   ```

2. **Validate composed infrastructure**:
   ```bash
   # Validate main.tf that uses modules
   riveter scan -p aws-security -t main.tf
   ```

3. **Validate all module files**:
   ```bash
   # Find and validate all .tf files
   find modules/ -name "*.tf" -exec riveter scan -p aws-security -t {} \;
   ```

**Example module structure**:
```
infrastructure/
├── main.tf              # Uses modules
├── modules/
│   ├── vpc/
│   │   ├── main.tf      # VPC resources
│   │   └── variables.tf
│   ├── ec2/
│   │   ├── main.tf      # EC2 resources
│   │   └── variables.tf
│   └── rds/
│       ├── main.tf      # RDS resources
│       └── variables.tf
```

**Validation strategy**:
```bash
# 1. Validate individual modules
riveter scan -p aws-security -t modules/vpc/main.tf
riveter scan -p aws-security -t modules/ec2/main.tf
riveter scan -p aws-security -t modules/rds/main.tf

# 2. Validate composed infrastructure
riveter scan -p aws-security -t main.tf

# 3. Comprehensive validation
find . -name "*.tf" -not -path "./.*" -exec riveter scan -p aws-security -t {} \;
```

**Note**: Riveter validates `resource` blocks, not `module` calls. It sees the actual resources defined in module files.

🔗 **Related**: [Module Validation](../terraform/modules.md) | [Terraform Best Practices](../terraform/best-practices.md)

### Q: Can I use Riveter with Terraform Cloud/Enterprise?

**A: Yes, Riveter integrates well with Terraform Cloud workflows.**

**Integration approaches**:

1. **Pre-commit hooks** (local validation):
   ```bash
   # .pre-commit-config.yaml
   repos:
     - repo: local
       hooks:
         - id: riveter
           name: Riveter Infrastructure Validation
           entry: riveter scan -p aws-security -t
           language: system
           files: \.tf$
   ```

2. **CI/CD pipeline** (before Terraform Cloud):
   ```yaml
   # GitHub Actions
   name: Validate Infrastructure
   on: [push, pull_request]

   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Install Riveter
           run: brew install scottryanhoward/homebrew-riveter/riveter
         - name: Validate Infrastructure
           run: riveter scan -p aws-security -p cis-aws -t main.tf
   ```

3. **Terraform Cloud run tasks** (if supported):
   ```bash
   # Custom run task that calls Riveter
   # (Requires Terraform Cloud Business/Enterprise)
   ```

**Workflow integration**:
```
1. Developer writes Terraform
2. Pre-commit hook runs Riveter locally
3. Push to version control
4. CI/CD runs Riveter validation
5. If validation passes, trigger Terraform Cloud
6. Terraform Cloud runs plan/apply
```

🔗 **Related**: [Terraform Cloud Integration](../integrations/terraform-cloud.md) | [Enterprise Workflows](../enterprise/workflows.md)

## Getting Help and Support

### Q: Where can I get help if I'm stuck?

**A: Multiple support channels are available depending on your needs.**

**Self-Service Resources** (fastest):
1. **[Documentation](README.md)** - Comprehensive guides and references
2. **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions
3. **[Error Message Dictionary](error-message-dictionary.md)** - Specific error explanations
4. **[FAQ](faq.md)** - This document with common questions

**Community Support**:
1. **[GitHub Discussions](https://github.com/riveter/riveter/discussions)** - Ask questions, share ideas
2. **[GitHub Issues](https://github.com/riveter/riveter/issues)** - Bug reports and feature requests

**Before asking for help**:
```bash
# Gather diagnostic information
riveter --version
uname -a
echo $SHELL

# Try the troubleshooting steps
riveter list-rule-packs
riveter scan -p aws-security -t main.tf --output-format json
```

**When asking questions**:
- Include your system information
- Provide the exact command you ran
- Share the complete error message
- Describe what you expected vs. what happened
- Mention any troubleshooting steps you've tried

🔗 **Related**: [Support Guide](../support/README.md) | [Community Guidelines](../../CODE_OF_CONDUCT.md)

### Q: How do I stay updated with new features and releases?

**A: Multiple ways to stay informed about Riveter updates.**

**Automatic updates**:
```bash
# Homebrew (recommended)
brew upgrade riveter  # Updates to latest version

# Check for updates
brew outdated | grep riveter
```

**Release notifications**:
1. **GitHub Releases**: [Watch the repository](https://github.com/riveter/riveter) for release notifications
2. **GitHub Discussions**: Follow announcements in discussions
3. **Changelog**: Check [CHANGELOG.md](../../CHANGELOG.md) for detailed changes

**Version checking**:
```bash
# Check current version
riveter --version

# Check latest available version (Homebrew)
brew info riveter | grep "stable"

# Check GitHub releases
curl -s https://api.github.com/repos/riveter/riveter/releases/latest | jq '.tag_name'
```

**What's included in updates**:
- New rule packs and compliance frameworks
- Performance improvements
- Bug fixes and stability improvements
- New features and CLI enhancements
- Security updates

🔗 **Related**: [Release Notes](../../CHANGELOG.md) | [Update Guide](../maintenance/updates.md)

---

## Still Have Questions?

If you can't find the answer to your question in this FAQ:

1. **Search the documentation**: Use the search function in our docs
2. **Check GitHub Issues**: Someone might have asked the same question
3. **Ask the community**: Start a discussion on GitHub Discussions
4. **Report bugs**: Use GitHub Issues for bug reports

🔗 **Quick Links**:
- 📖 **[Full Documentation](README.md)**
- 🐛 **[Report Issues](https://github.com/riveter/riveter/issues)**
- 💬 **[Ask Questions](https://github.com/riveter/riveter/discussions)**
- 🚀 **[Get Started](README.md#quick-start)**
