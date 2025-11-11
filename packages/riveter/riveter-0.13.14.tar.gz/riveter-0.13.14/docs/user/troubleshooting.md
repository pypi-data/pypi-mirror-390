# Troubleshooting Guide

This guide helps you quickly resolve common issues with Riveter installation, configuration, and validation.

💡 **Tip**: Most issues can be resolved in under 2 minutes using the quick fixes below. Use the detailed troubleshooting sections only if quick fixes don't work.

🚀 **Quick Action**: Test your setup anytime with: `riveter --version && riveter list-rule-packs`

## Quick Fixes for Common Issues

### Installation Issues

#### ❌ "riveter: command not found" (Homebrew)

🔧 **Quick Fix**: Add Homebrew to your PATH:
```bash
# macOS (Apple Silicon)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc

# macOS (Intel) or Linux
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Verify installation
which riveter && riveter --version
```

<details>
<summary>🔧 Detailed Diagnosis Steps</summary>

1. **Check if Homebrew is installed**:
   ```bash
   which brew
   brew --version
   ```

2. **Check if Riveter is installed via Homebrew**:
   ```bash
   brew list | grep riveter
   brew info scottryanhoward/homebrew-riveter/riveter
   ```

3. **Reinstall if necessary**:
   ```bash
   brew uninstall riveter 2>/dev/null || true
   brew install scottryanhoward/homebrew-riveter/riveter
   ```

4. **Check shell configuration**:
   ```bash
   echo $SHELL
   cat ~/.zshrc | grep brew  # or ~/.bashrc for bash
   ```

</details>

#### ❌ "No available formula with name 'riveter'"

🔧 **Quick Fix**: Tap the repository first:
```bash
brew tap scottryanhoward/homebrew-riveter
brew install riveter
```

<details>
<summary>🔧 Alternative Solutions</summary>

1. **Use full tap name**:
   ```bash
   brew install scottryanhoward/homebrew-riveter/riveter
   ```

2. **Update Homebrew and retry**:
   ```bash
   brew update
   brew tap scottryanhoward/homebrew-riveter
   brew install riveter
   ```

3. **Check tap status**:
   ```bash
   brew tap | grep riveter
   brew tap-info scottryanhoward/homebrew-riveter
   ```

</details>

#### ❌ Checksum mismatch errors during upgrade

🔧 **Quick Fix**: Ignore checksum verification temporarily:
```bash
# For upgrades with checksum warnings
brew upgrade riveter --ignore-dependencies

# Verify it works
riveter --version
```

<details>
<summary>🔧 Comprehensive Checksum Troubleshooting</summary>

**Error messages you might see**:
- `Resource reports different checksum: placeholder_source_checksum`
- `Formula reports different checksum: placeholder_checksum_macos_arm64`
- `SHA-256 checksum of downloaded file: [hash]`

**Root cause**: The Homebrew formula contains placeholder checksums instead of real ones.

1. **Clear cache and retry**:
   ```bash
   # Clear Homebrew cache
   brew cleanup riveter
   rm -rf "$(brew --cache)/downloads/*riveter*"

   # Update and retry
   brew update
   brew tap --repair
   brew upgrade riveter
   ```

2. **Force reinstall**:
   ```bash
   # Complete reinstall
   brew uninstall riveter
   brew cleanup
   brew install scottryanhoward/homebrew-riveter/riveter --ignore-dependencies
   ```

3. **Check formula status**:
   ```bash
   # Inspect the formula
   brew cat scottryanhoward/homebrew-riveter/riveter

   # Check for updates
   brew tap --repair scottryanhoward/homebrew-riveter
   ```

4. **Alternative: Use Python installation**:
   ```bash
   # If Homebrew issues persist
   brew uninstall riveter  # Remove problematic version

   # Install via Python
   git clone https://github.com/riveter/riveter.git
   cd riveter && python3 -m venv venv && source venv/bin/activate
   pip install -e .
   ```

**Important**: The checksum warnings don't affect functionality - Riveter should work normally despite these messages.

</details>

#### ❌ Virtual environment issues (Python installation)

🔧 **Quick Fix**: Always activate the virtual environment:
```bash
# Linux/Mac
source venv/bin/activate

# Windows
.\venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

⚠️ **Important**: You must activate the virtual environment every time you open a new terminal session when using the Python installation method.

<details>
<summary>🔧 Virtual Environment Troubleshooting</summary>

1. **Check if virtual environment exists**:
   ```bash
   ls -la venv/
   ls -la venv/bin/activate  # Linux/Mac
   ls -la venv/Scripts/activate  # Windows
   ```

2. **Recreate virtual environment if corrupted**:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

3. **Check Python version compatibility**:
   ```bash
   python --version  # Should be 3.12+
   ```

4. **Verify Riveter installation in venv**:
   ```bash
   source venv/bin/activate
   pip list | grep riveter
   which riveter
   ```

</details>

💡 **Tip**: Consider switching to Homebrew installation to avoid virtual environment management. See [Installation Migration Guide](../installation/migration.md).

### Runtime Issues

#### ❌ "Rule pack 'xyz' not found"

🔧 **Quick Fix**: Check available rule packs and use exact names:
```bash
# List all available rule packs
riveter list-rule-packs

# Use exact names (case-sensitive)
riveter scan -p aws-security -t main.tf  # ✅ Correct
```

💡 **Common Mistakes**:
- `AWS-Security` → `aws-security` (lowercase)
- `cis_aws` → `cis-aws` (hyphens, not underscores)
- `soc-2` → `soc2-security` (full name)

<details>
<summary>🔧 Rule Pack Troubleshooting</summary>

1. **Verify rule pack exists**:
   ```bash
   riveter list-rule-packs | grep -i security
   riveter list-rule-packs | grep -i cis
   ```

2. **Check rule pack file directly**:
   ```bash
   ls -la rule_packs/
   cat rule_packs/aws-security.yml | head -10
   ```

3. **Validate rule pack syntax**:
   ```bash
   riveter validate-rule-pack rule_packs/aws-security.yml
   ```

4. **Test with known working rule pack**:
   ```bash
   riveter scan -p aws-security -t main.tf
   ```

</details>

#### ❌ "No rules loaded"

🔧 **Quick Fix**: Specify either rule pack (`-p`) or custom rules (`-r`):
```bash
riveter scan -p aws-security -t main.tf     # ✅ With rule pack
riveter scan -r rules.yml -t main.tf        # ✅ With custom rules
riveter scan -r custom.yml -p aws-security -t main.tf  # ✅ Both
```

⚠️ **Common Mistake**: Running `riveter scan -t main.tf` without any rules specified.

<details>
<summary>🔧 Rules Loading Troubleshooting</summary>

1. **Check command syntax**:
   ```bash
   # Wrong: missing rule specification
   riveter scan -t main.tf

   # Right: with rule pack
   riveter scan -p aws-security -t main.tf

   # Right: with custom rules
   riveter scan -r my-rules.yml -t main.tf
   ```

2. **Verify custom rules file exists**:
   ```bash
   ls -la rules.yml
   file rules.yml  # Should show "ASCII text" or similar
   ```

3. **Validate custom rules syntax**:
   ```bash
   riveter validate-rule-pack rules.yml
   ```

4. **Test with minimal rule file**:
   ```bash
   cat > test-rules.yml << EOF
   rules:
     - id: test-rule
       description: Test rule
       resource_type: aws_instance
       assert:
         instance_type: t2.micro
   EOF

   riveter scan -r test-rules.yml -t main.tf
   ```

</details>

#### ❌ "Failed to parse Terraform file"

🔧 **Quick Fix**: Validate Terraform syntax first:
```bash
# Check Terraform syntax
terraform validate

# Check file exists and is readable
ls -la main.tf && file main.tf
```

<details>
<summary>🔧 Terraform Parsing Troubleshooting</summary>

1. **Validate Terraform syntax**:
   ```bash
   terraform validate
   terraform fmt -check
   terraform plan  # More comprehensive validation
   ```

2. **Check file path and permissions**:
   ```bash
   ls -la main.tf
   file main.tf
   head -5 main.tf  # Check file content
   ```

3. **Test with minimal Terraform file**:
   ```bash
   cat > test.tf << EOF
   resource "aws_instance" "test" {
     instance_type = "t2.micro"
   }
   EOF

   riveter scan -p aws-security -t test.tf
   rm test.tf
   ```

4. **Check for common HCL issues**:
   ```bash
   # Look for syntax errors
   grep -n "resource\|data\|variable\|output" main.tf

   # Check for unclosed braces
   grep -c "{" main.tf && grep -c "}" main.tf
   ```

5. **Verify file encoding**:
   ```bash
   file -i main.tf  # Should show charset=us-ascii or utf-8
   ```

</details>

🔗 **Related**: [Terraform Validation Guide](../terraform/validation.md) | [HCL Syntax Reference](../terraform/hcl-syntax.md)

### Validation Issues

#### ❌ Unexpected validation failures

🎯 **Remember**: Validation failures often indicate real security or compliance issues that should be fixed.

🔧 **Quick Check**: Verify if failures are expected:
```bash
# Review the specific failure messages
riveter scan -p aws-security -t main.tf

# Check if resources match rule expectations
grep -A 5 -B 5 "resource.*aws_s3_bucket" main.tf
```

<details>
<summary>🔧 Validation Failure Analysis</summary>

1. **Understand the failure message**:
   ```
   ❌ FAIL │ aws_s3_bucket.example │ S3 bucket must have encryption enabled
   ```
   - **Resource**: `aws_s3_bucket.example` (what failed)
   - **Rule**: "S3 bucket must have encryption enabled" (what's required)
   - **Action**: Add encryption to your S3 bucket configuration

2. **Check rule filters and conditions**:
   ```bash
   # Some rules only apply to production resources
   grep -i "environment.*production" main.tf

   # Check resource tags
   grep -A 10 "tags.*=" main.tf
   ```

3. **Verify resource configuration**:
   ```bash
   # For S3 encryption failure, check:
   grep -A 20 "aws_s3_bucket" main.tf | grep -i encrypt

   # For EC2 instance type failure, check:
   grep -A 10 "aws_instance" main.tf | grep instance_type
   ```

4. **Test with corrected configuration**:
   ```hcl
   # Example fix for S3 encryption
   resource "aws_s3_bucket" "example" {
     bucket = "my-bucket"

     server_side_encryption_configuration {
       rule {
         apply_server_side_encryption_by_default {
           sse_algorithm = "AES256"
         }
       }
     }
   }
   ```

</details>

💡 **Tip**: Use `--output-format json` to get detailed failure information for programmatic analysis.

#### ❌ No resources found for validation

🔧 **Quick Fix**: Verify your Terraform file contains resource definitions:
```bash
# Check for resource blocks
grep -n "resource " main.tf

# List all resource types
grep "resource " main.tf | awk '{print $2}' | sort | uniq
```

<details>
<summary>🔧 Resource Detection Troubleshooting</summary>

1. **Verify file structure**:
   ```bash
   # Check file size and content
   ls -la main.tf
   wc -l main.tf
   head -10 main.tf
   ```

2. **Look for resource definitions**:
   ```bash
   # Find all resources
   grep -n "resource " main.tf

   # Check for data sources (not validated)
   grep -n "data " main.tf

   # Check for variables and outputs (not validated)
   grep -n "variable\|output" main.tf
   ```

3. **Test with known resource**:
   ```bash
   cat >> main.tf << EOF

   resource "aws_instance" "test" {
     instance_type = "t2.micro"
     ami           = "ami-12345678"
   }
   EOF

   riveter scan -p aws-security -t main.tf
   ```

4. **Check for module-only configurations**:
   ```bash
   # Riveter validates resources, not modules
   grep -n "module " main.tf

   # Look in module files for actual resources
   find . -name "*.tf" -exec grep -l "resource " {} \;
   ```

</details>

⚠️ **Note**: Riveter validates `resource` blocks, not `data` sources, `variable` declarations, or `output` values.

## Detailed Troubleshooting

### Step-by-Step Diagnostic Procedures

When quick fixes don't resolve your issue, follow these comprehensive diagnostic procedures:

#### 1. System Environment Diagnosis

🔧 **Complete Environment Check**:
```bash
# System information
echo "OS: $(uname -s)"
echo "Shell: $SHELL"
echo "PATH: $PATH"

# Riveter installation check
which riveter
riveter --version
ls -la $(which riveter)

# Dependencies check
which terraform && terraform --version
which python3 && python3 --version
which brew && brew --version
```

<details>
<summary>🔧 Environment Troubleshooting Steps</summary>

1. **PATH Configuration**:
   ```bash
   # Check if Riveter directory is in PATH
   echo $PATH | tr ':' '\n' | grep -E "(brew|riveter|venv)"

   # Add missing paths
   # For Homebrew:
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
   # For Python venv:
   echo 'source ~/riveter/venv/bin/activate' >> ~/.zshrc
   ```

2. **Shell Configuration**:
   ```bash
   # Check shell configuration files
   ls -la ~/.zshrc ~/.bashrc ~/.bash_profile

   # Look for Riveter-related configurations
   grep -i riveter ~/.zshrc ~/.bashrc ~/.bash_profile 2>/dev/null
   ```

3. **Permission Issues**:
   ```bash
   # Check executable permissions
   ls -la $(which riveter)

   # Fix permissions if needed
   chmod +x $(which riveter)
   ```

</details>

#### 2. Installation Integrity Check

🔧 **Verify Installation Completeness**:
```bash
# For Homebrew installation
brew list riveter
brew info riveter

# For Python installation
pip list | grep riveter
pip show riveter
```

<details>
<summary>🔧 Installation Verification Steps</summary>

1. **Homebrew Installation Check**:
   ```bash
   # Verify tap is added
   brew tap | grep riveter

   # Check formula information
   brew info scottryanhoward/homebrew-riveter/riveter

   # Verify binary location
   ls -la /opt/homebrew/bin/riveter  # Apple Silicon
   ls -la /usr/local/bin/riveter     # Intel Mac
   ```

2. **Python Installation Check**:
   ```bash
   # Verify virtual environment
   source venv/bin/activate
   which python
   which riveter

   # Check package installation
   pip list | grep -E "(riveter|hcl2|click|rich)"

   # Verify package files
   python -c "import riveter; print(riveter.__file__)"
   ```

3. **Cross-Installation Conflicts**:
   ```bash
   # Check for multiple installations
   which -a riveter

   # Check Python path conflicts
   python -c "import sys; print('\n'.join(sys.path))"
   ```

</details>

#### 3. Rule Pack and Configuration Validation

🔧 **Comprehensive Rule System Check**:
```bash
# List and validate rule packs
riveter list-rule-packs
riveter validate-rule-pack rule_packs/aws-security.yml

# Test with minimal configuration
echo 'resource "aws_instance" "test" { instance_type = "t2.micro" }' > test.tf
riveter scan -p aws-security -t test.tf
rm test.tf
```

<details>
<summary>🔧 Rule System Diagnostic Steps</summary>

1. **Rule Pack Integrity**:
   ```bash
   # Check rule pack files exist
   ls -la rule_packs/

   # Validate each rule pack
   for pack in rule_packs/*.yml; do
     echo "Validating $pack"
     riveter validate-rule-pack "$pack"
   done
   ```

2. **Custom Rules Validation**:
   ```bash
   # Create test rule file
   cat > test-rules.yml << EOF
   rules:
     - id: test-rule
       description: Test rule for diagnosis
       resource_type: aws_instance
       assert:
         instance_type: t2.micro
   EOF

   # Validate custom rules
   riveter validate-rule-pack test-rules.yml

   # Test with custom rules
   riveter scan -r test-rules.yml -t test.tf
   ```

3. **Rule Loading Process**:
   ```bash
   # Test rule loading with verbose output
   riveter scan -p aws-security -t test.tf --output-format json | jq '.rules_loaded'

   # Check for rule conflicts
   riveter scan -r custom.yml -p aws-security -t test.tf --output-format json
   ```

</details>

#### 4. Terraform Configuration Analysis

🔧 **Deep Terraform File Analysis**:
```bash
# Comprehensive Terraform validation
terraform validate
terraform fmt -check
terraform plan -out=plan.out 2>&1 | head -20

# File structure analysis
file main.tf
wc -l main.tf
grep -c "resource\|data\|variable\|output" main.tf
```

<details>
<summary>🔧 Terraform Analysis Steps</summary>

1. **Syntax and Structure Validation**:
   ```bash
   # Check HCL syntax
   terraform validate

   # Check formatting
   terraform fmt -check -diff

   # Parse with terraform show
   terraform plan -out=plan.out
   terraform show -json plan.out | jq '.planned_values.root_module.resources[0]'
   ```

2. **Resource Type Analysis**:
   ```bash
   # List all resource types
   grep "resource " main.tf | awk '{print $2}' | sort | uniq -c

   # Check for supported resource types
   grep "resource " main.tf | grep -E "(aws_|azurerm_|google_)"

   # Verify resource naming
   grep "resource " main.tf | awk '{print $2, $3}'
   ```

3. **Content Analysis**:
   ```bash
   # Check for common issues
   grep -n "TODO\|FIXME\|XXX" main.tf

   # Look for incomplete resources
   grep -A 5 -B 5 "resource.*{$" main.tf

   # Check for variable references
   grep -o "\${[^}]*}" main.tf | sort | uniq
   ```

</details>

#### 5. Network and Connectivity Issues

🔧 **Network-Related Diagnostics**:
```bash
# Test internet connectivity (for rule pack downloads)
curl -I https://github.com/riveter/riveter/raw/main/rule_packs/aws-security.yml

# Check DNS resolution
nslookup github.com
```

<details>
<summary>🔧 Network Troubleshooting Steps</summary>

1. **Connectivity Tests**:
   ```bash
   # Test GitHub connectivity
   curl -s https://api.github.com/repos/riveter/riveter | jq '.name'

   # Test Homebrew tap connectivity
   curl -I https://github.com/scottryanhoward/homebrew-riveter
   ```

2. **Proxy and Firewall Issues**:
   ```bash
   # Check proxy settings
   echo "HTTP_PROXY: $HTTP_PROXY"
   echo "HTTPS_PROXY: $HTTPS_PROXY"

   # Test with proxy bypass
   unset HTTP_PROXY HTTPS_PROXY
   riveter list-rule-packs
   ```

3. **Corporate Network Issues**:
   ```bash
   # Check for corporate certificates
   openssl s_client -connect github.com:443 -servername github.com

   # Test alternative installation methods
   # (Download and install manually if needed)
   ```

</details>

### Performance Issues

#### ❌ Slow validation times

⚡ **Quick Fix**: Use Homebrew installation for 3-5x faster performance:
```bash
# Switch to Homebrew (if using Python)
brew install scottryanhoward/homebrew-riveter/riveter

# Test performance improvement
time riveter scan -p aws-security -t main.tf
```

<details>
<summary>⚡ Performance Optimization Strategies</summary>

1. **Installation Method Comparison**:
   ```bash
   # Homebrew (fastest)
   time riveter scan -p aws-security -t main.tf

   # Python (slower startup)
   time python -m riveter.cli scan -p aws-security -t main.tf
   ```

2. **Rule Pack Optimization**:
   ```bash
   # Faster: Single rule pack
   riveter scan -p aws-security -t main.tf

   # Slower: Multiple rule packs
   riveter scan -p aws-security -p cis-aws -p soc2-security -t main.tf

   # Compromise: Targeted combinations
   riveter scan -p aws-security -p aws-well-architected -t main.tf
   ```

3. **File Size Optimization**:
   ```bash
   # Check file size
   wc -l main.tf
   du -h main.tf

   # Split large files
   terraform fmt main.tf  # Clean formatting first

   # Validate smaller chunks
   riveter scan -p aws-security -t modules/vpc/main.tf
   riveter scan -p aws-security -t modules/ec2/main.tf
   ```

4. **Parallel Validation** (for multiple files):
   ```bash
   # Sequential (slower)
   riveter scan -p aws-security -t file1.tf
   riveter scan -p aws-security -t file2.tf

   # Parallel (faster)
   riveter scan -p aws-security -t file1.tf &
   riveter scan -p aws-security -t file2.tf &
   wait
   ```

</details>

#### ❌ High memory usage

⚡ **Quick Fix**: Switch to Homebrew binary for lower memory footprint:
```bash
# Check current memory usage
ps aux | grep riveter

# Switch to Homebrew
brew install scottryanhoward/homebrew-riveter/riveter
```

<details>
<summary>⚡ Memory Optimization Techniques</summary>

1. **Installation Method Impact**:
   ```bash
   # Homebrew binary (lower memory)
   /opt/homebrew/bin/riveter scan -p aws-security -t main.tf

   # Python version (higher memory due to interpreter)
   python -m riveter.cli scan -p aws-security -t main.tf
   ```

2. **File Size Management**:
   ```bash
   # Check file complexity
   wc -l main.tf
   grep -c "resource " main.tf

   # Split large configurations
   terraform fmt main.tf
   # Consider breaking into modules
   ```

3. **Rule Pack Selection**:
   ```bash
   # Memory-efficient: Targeted rule packs
   riveter scan -p aws-security -t main.tf

   # Memory-intensive: All rule packs
   riveter scan -p aws-security -p cis-aws -p soc2-security -p aws-well-architected -t main.tf
   ```

4. **System Resource Monitoring**:
   ```bash
   # Monitor during validation
   top -p $(pgrep riveter)

   # Check available memory
   free -h  # Linux
   vm_stat  # macOS
   ```

</details>

💡 **Performance Benchmarks**:
- **Homebrew**: ~0.5-2 seconds startup, 50-100MB memory
- **Python**: ~2-5 seconds startup, 100-200MB memory
- **Large files** (1000+ lines): Add 1-3 seconds processing time

### Platform-Specific Issues

#### macOS: "cannot be opened because the developer cannot be verified"
```bash
# Allow the binary to run (one-time setup)
sudo xattr -rd com.apple.quarantine $(which riveter)
```

#### Linux: Permission denied errors
```bash
# Ensure the binary has execute permissions
chmod +x $(which riveter)
```

## Error Messages and Solutions

### Common Error Patterns

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| `command not found` | Installation issue | Follow installation guide |
| `No rules loaded` | Missing rule specification | Add `-p` or `-r` flag |
| `Rule pack not found` | Typo in rule pack name | Check `riveter list-rule-packs` |
| `Failed to parse` | Invalid Terraform syntax | Run `terraform validate` |
| `Permission denied` | File permissions | Check file/directory permissions |
| `No resources found` | Empty or invalid Terraform | Verify resource definitions exist |

### Validation Result Interpretation

#### Understanding Failure Messages
```
❌ FAIL │ aws_s3_bucket.example │ S3 bucket must have encryption enabled
```
- **Resource**: `aws_s3_bucket.example` - The specific resource that failed
- **Rule**: "S3 bucket must have encryption enabled" - What the rule checks
- **Action**: Add encryption configuration to your S3 bucket

#### Expected vs Unexpected Failures
- **Expected**: Riveter finds real security/compliance issues in your infrastructure
- **Unexpected**: Rules fail on correctly configured resources (may indicate rule filter issues)

## Getting Help

### Self-Service Resources
1. **Check this troubleshooting guide** - Most common issues are covered here
2. **Review rule pack documentation** - [Rule Packs Guide](rule-packs.md)
3. **Check visual guides** - [Visual Guides](visual-guides.md) for process understanding

### Community Support
- 🐛 **[GitHub Issues](https://github.com/riveter/riveter/issues)** - Report bugs or request features
- 💬 **[GitHub Discussions](https://github.com/riveter/riveter/discussions)** - Ask questions and get help
- 📖 **[Technical Documentation](../TECHNICAL.md)** - Deep technical details

### When Reporting Issues
Include this information:
```bash
# System information
riveter --version
uname -a  # Linux/macOS
echo $SHELL

# Rule pack information
riveter list-rule-packs

# Command that failed
riveter scan -p aws-security -t main.tf  # Your actual command

# Error output (copy the full error message)
```

## Prevention Tips

### Best Practices
1. **Start simple** - Begin with one rule pack, then add more
2. **Test locally** - Validate before committing to version control
3. **Use consistent naming** - Follow Terraform naming conventions
4. **Keep files manageable** - Split large configurations into modules
5. **Regular updates** - Keep Riveter updated for latest rule packs

### Development Workflow
```bash
# 1. Write Terraform
vim main.tf

# 2. Validate syntax
terraform validate

# 3. Run Riveter validation
riveter scan -p aws-security -t main.tf

# 4. Fix any issues
vim main.tf

# 5. Re-validate
riveter scan -p aws-security -t main.tf

# 6. Commit when clean
git add . && git commit -m "Add secure infrastructure"
```

---

*Most issues can be resolved quickly by following these troubleshooting steps. If you're still stuck, don't hesitate to reach out to the community for help.*
