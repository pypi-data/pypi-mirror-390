# Inline Help Components

This document defines standardized help box templates and progressive disclosure patterns for use throughout Riveter documentation.

## Help Box Templates

### 💡 Tips
Use for helpful suggestions and best practices:

```markdown
💡 **Tip**: Use `riveter list-rule-packs` to see all available rule packs before choosing which ones to use.
```

### ⚠️ Warnings
Use for important caveats or potential issues:

```markdown
⚠️ **Warning**: Always activate your Python virtual environment (`source venv/bin/activate`) when using the pip installation method.
```

### 🔧 Troubleshooting
Use for quick fixes to common problems:

```markdown
🔧 **Troubleshooting**: If you see "command not found", check your PATH configuration with `echo $PATH`.
```

### 📋 Prerequisites
Use to highlight required setup or knowledge:

```markdown
📋 **Prerequisites**: Ensure you have Terraform installed and your `.tf` files have valid HCL syntax before running Riveter.
```

### 🚀 Quick Actions
Use for immediate next steps or shortcuts:

```markdown
🚀 **Quick Action**: Test your installation with: `riveter scan -p aws-security -t examples/quickstart/basic-aws.tf`
```

### 🎯 Best Practices
Use for recommended approaches:

```markdown
🎯 **Best Practice**: Start with one rule pack (like `aws-security`) before combining multiple packs to understand the validation results.
```

### 🔍 Deep Dive
Use to link to more detailed information:

```markdown
🔍 **Deep Dive**: For advanced rule writing techniques, see the [Custom Rules Guide](../advanced/custom-rules.md).
```

### ⚡ Performance Tips
Use for optimization suggestions:

```markdown
⚡ **Performance**: Use the Homebrew installation for faster startup times compared to the Python version.
```

## Progressive Disclosure Patterns

### Basic with Advanced Options
```markdown
## Basic Usage
Run Riveter with a pre-built rule pack:
```bash
riveter scan -p aws-security -t main.tf
```

<details>
<summary>🔧 Advanced Options</summary>

### Multiple Rule Packs
```bash
riveter scan -p aws-security -p cis-aws -p soc2-security -t main.tf
```

### Custom Output Formats
```bash
riveter scan -p aws-security -t main.tf --output-format json > results.json
riveter scan -p aws-security -t main.tf --output-format sarif > security.sarif
```

### Combining Custom Rules with Rule Packs
```bash
riveter scan -r custom-rules.yml -p aws-security -t main.tf
```

</details>
```

### Troubleshooting with Solutions
```markdown
## Common Installation Issues

### ❌ "riveter: command not found"

**Quick Fix**: Check if Riveter is in your PATH:
```bash
which riveter
echo $PATH
```

<details>
<summary>🔧 Detailed Troubleshooting Steps</summary>

1. **Verify Installation Method**:
   ```bash
   # For Homebrew installation
   brew list | grep riveter

   # For Python installation
   pip list | grep riveter
   ```

2. **Check Shell Configuration**:
   ```bash
   # Add Homebrew to PATH (if needed)
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Reinstall if Necessary**:
   ```bash
   # Homebrew method
   brew uninstall riveter
   brew install scottryanhoward/homebrew-riveter/riveter

   # Python method
   pip uninstall riveter
   cd riveter && pip install -e .
   ```

</details>
```

### Feature Explanation with Examples
```markdown
## Rule Packs

Rule packs are collections of pre-built validation rules for specific compliance frameworks.

💡 **Tip**: Start with `aws-security` for general AWS best practices.

<details>
<summary>📋 Complete Rule Pack List</summary>

### Cloud Security Best Practices
- `aws-security` (26 rules) - AWS Security Best Practices
- `gcp-security` (29 rules) - GCP Security Best Practices
- `azure-security` (28 rules) - Azure Security Best Practices
- `multi-cloud-security` (40 rules) - Cross-cloud security patterns

### Compliance Frameworks
- `cis-aws` (22 rules) - CIS AWS Foundations Benchmark
- `cis-azure` (34 rules) - CIS Azure Foundations Benchmark
- `cis-gcp` (43 rules) - CIS GCP Foundations Benchmark
- `soc2-security` (28 rules) - SOC 2 Trust Service Criteria

### Industry-Specific Compliance
- `aws-hipaa` (35 rules) - Healthcare compliance
- `azure-hipaa` (30 rules) - Healthcare compliance
- `aws-pci-dss` (40 rules) - Payment card compliance

### Architecture Frameworks
- `aws-well-architected` (34 rules) - AWS 6 pillars
- `azure-well-architected` (35 rules) - Azure 5 pillars
- `gcp-well-architected` (30 rules) - GCP 5 pillars

### Container Security
- `kubernetes-security` (40 rules) - K8s security for EKS/AKS/GKE

</details>
```

## Contextual Links Pattern

### Related Documentation Links
```markdown
🔗 **Related**:
- [Rule Packs Guide](rule-packs.md) - Choose the right rule packs
- [Visual Guides](visual-guides.md) - Understand Riveter workflows
- [Troubleshooting](troubleshooting.md) - Fix common issues
```

### Next Steps Links
```markdown
🚀 **Next Steps**:
- **Developers**: [CI/CD Integration](../developer/cicd.md)
- **Security Engineers**: [Custom Rules](../advanced/custom-rules.md)
- **Compliance Officers**: [Audit Reporting](../compliance/reporting.md)
```

### Cross-Reference Links
```markdown
📖 **See Also**:
- [Installation Guide](installation.md#homebrew) for setup details
- [CLI Reference](../reference/cli.md) for all command options
- [Examples](../../examples/README.md) for real-world configurations
```

## Error Context Pattern

### Error with Solution
```markdown
### ❌ Error: "No rules loaded"

**Cause**: No rule pack or custom rules file specified.

**Solution**: Add either `-p` (rule pack) or `-r` (custom rules):
```bash
riveter scan -p aws-security -t main.tf     # ✅ With rule pack
riveter scan -r rules.yml -t main.tf        # ✅ With custom rules
```

🔗 **Related**: [Rule Packs Guide](rule-packs.md) | [Custom Rules](../advanced/custom-rules.md)
```

### Error with Multiple Solutions
```markdown
### ❌ Error: "Failed to parse Terraform file"

**Possible Causes**:
1. Invalid HCL syntax in your Terraform file
2. File path is incorrect
3. File permissions issue

<details>
<summary>🔧 Step-by-Step Diagnosis</summary>

1. **Check Terraform Syntax**:
   ```bash
   terraform validate
   terraform fmt -check
   ```

2. **Verify File Path**:
   ```bash
   ls -la main.tf
   file main.tf  # Check file type
   ```

3. **Check File Permissions**:
   ```bash
   ls -la main.tf
   chmod 644 main.tf  # Fix if needed
   ```

4. **Test with Simple File**:
   ```bash
   echo 'resource "aws_instance" "test" { instance_type = "t2.micro" }' > test.tf
   riveter scan -p aws-security -t test.tf
   rm test.tf
   ```

</details>
```

## Usage Guidelines

### When to Use Each Component

1. **💡 Tips**: Non-critical helpful information that improves user experience
2. **⚠️ Warnings**: Important information that prevents common mistakes
3. **🔧 Troubleshooting**: Quick fixes for immediate problems
4. **📋 Prerequisites**: Required setup or knowledge before proceeding
5. **🚀 Quick Actions**: Immediate next steps or verification commands
6. **🎯 Best Practices**: Recommended approaches for optimal results
7. **🔍 Deep Dive**: Links to more comprehensive information
8. **⚡ Performance**: Optimization tips for better experience

### Progressive Disclosure Guidelines

1. **Start Simple**: Show the most common use case first
2. **Expand Gradually**: Use `<details>` for advanced options
3. **Clear Labels**: Use descriptive summary text with icons
4. **Logical Grouping**: Group related advanced options together
5. **Maintain Context**: Keep basic and advanced options related

### Contextual Linking Best Practices

1. **Use Descriptive Text**: "Rule Packs Guide" not "click here"
2. **Group Related Links**: Use bullet points for multiple related links
3. **Indicate Link Purpose**: Use prefixes like "See also:", "Next steps:", "Related:"
4. **Keep Links Current**: Verify all links work and point to correct sections
5. **Avoid Link Overload**: Maximum 3-5 links per section

## Implementation Examples

### In Getting Started Guide
```markdown
# Quick Installation

## Homebrew (Recommended)
```bash
brew install scottryanhoward/homebrew-riveter/riveter
```

💡 **Tip**: Homebrew installation provides a single binary with faster startup times.

⚠️ **macOS Users**: If you see "developer cannot be verified", run:
```bash
sudo xattr -rd com.apple.quarantine $(which riveter)
```

<details>
<summary>🔧 Alternative Installation Methods</summary>

### Python/pip Installation
```bash
git clone https://github.com/riveter/riveter.git
cd riveter && python3 -m venv venv && source venv/bin/activate
pip install -e .
```

⚠️ **Remember**: Activate the virtual environment each time: `source venv/bin/activate`

### Docker Installation
```bash
docker run --rm -v $(pwd):/workspace riveter/riveter scan -p aws-security -t /workspace/main.tf
```

</details>

🚀 **Quick Action**: Verify installation with `riveter --version`

🔗 **Next Steps**: [5-Minute Tutorial](tutorial.md) | [Rule Packs Guide](rule-packs.md)
```

### In Troubleshooting Guide
```markdown
# Common Issues

## Installation Problems

### ❌ "riveter: command not found"

🔧 **Quick Fix**: Check if Riveter is in your PATH:
```bash
which riveter
```

<details>
<summary>🔧 Detailed Troubleshooting</summary>

1. **For Homebrew Installation**:
   ```bash
   # Check if Homebrew is in PATH
   echo $PATH | grep brew

   # Add Homebrew to PATH if missing
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **For Python Installation**:
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate

   # Check if riveter is installed
   pip list | grep riveter
   ```

3. **Verify Installation**:
   ```bash
   riveter --version
   riveter list-rule-packs
   ```

</details>

🔗 **Related**: [Installation Guide](installation.md) | [Migration Guide](migration.md)
```
