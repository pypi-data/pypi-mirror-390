# Error Message Dictionary

This comprehensive dictionary documents all possible error messages from Riveter with explanations, solutions, and links to relevant documentation.

💡 **Tip**: Use Ctrl+F (Cmd+F on Mac) to quickly find your specific error message.

🚀 **Quick Action**: Copy the exact error message from your terminal and search for it below.

## Installation Errors

### Command Not Found Errors

#### `riveter: command not found`

**Cause**: Riveter is not installed or not in your system PATH.

**Solutions**:
1. **For new installations**:
   ```bash
   # Homebrew (recommended)
   brew install scottryanhoward/homebrew-riveter/riveter

   # Python/pip alternative
   git clone https://github.com/riveter/riveter.git
   cd riveter && python3 -m venv venv && source venv/bin/activate
   pip install -e .
   ```

2. **For existing Homebrew installations**:
   ```bash
   # Add Homebrew to PATH
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **For existing Python installations**:
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   ```

🔗 **Related**: [Installation Guide](README.md#installation) | [Troubleshooting](troubleshooting.md#installation-issues)

#### `brew: No available formula with name "riveter"`

**Cause**: The Homebrew tap is not added to your system.

**Solution**:
```bash
# Add the tap first
brew tap scottryanhoward/homebrew-riveter

# Then install
brew install riveter

# Or use the full tap name
brew install scottryanhoward/homebrew-riveter/riveter
```

🔗 **Related**: [Homebrew Installation](README.md#homebrew-recommended)

#### `Resource reports different checksum: placeholder_source_checksum` or `Formula reports different checksum: placeholder_checksum_macos_arm64`

**Cause**: The Homebrew formula contains placeholder checksums that don't match the actual downloaded files. This typically happens during development or when the formula hasn't been properly updated with real checksums.

**Solutions**:

1. **Ignore checksum verification** (temporary workaround):
   ```bash
   # For upgrade
   brew upgrade riveter --ignore-dependencies

   # For fresh install
   brew install scottryanhoward/homebrew-riveter/riveter --ignore-dependencies
   ```

2. **Clear Homebrew cache and retry**:
   ```bash
   # Clear cached downloads
   brew cleanup riveter
   rm -rf "$(brew --cache)/downloads/*riveter*"

   # Update tap and retry
   brew tap --repair
   brew update
   brew upgrade riveter
   ```

3. **Reinstall from scratch**:
   ```bash
   # Uninstall current version
   brew uninstall riveter

   # Clear cache
   brew cleanup

   # Reinstall
   brew install scottryanhoward/homebrew-riveter/riveter
   ```

4. **Use Python installation as alternative**:
   ```bash
   # If Homebrew continues to have issues
   git clone https://github.com/riveter/riveter.git
   cd riveter && python3 -m venv venv && source venv/bin/activate
   pip install -e .
   ```

**Note**: This error indicates the Homebrew formula needs to be updated with proper checksums. The functionality should work despite the warning, but it's recommended to report this issue to the maintainers.

🔗 **Related**: [Homebrew Troubleshooting](troubleshooting.md#homebrew-installation-fails-on-linux) | [Python Installation](README.md#pythonpip-alternative)

#### `python: No module named riveter`

**Cause**: Riveter is not installed in the current Python environment or virtual environment is not activated.

**Solutions**:
1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

2. **Install Riveter in current environment**:
   ```bash
   pip install -e .
   ```

3. **Verify installation**:
   ```bash
   pip list | grep riveter
   ```

🔗 **Related**: [Python Installation](README.md#pythonpip-alternative) | [Virtual Environment Guide](../installation/python-setup.md)

### Permission Errors

#### `Permission denied: '/opt/homebrew/bin/riveter'`

**Cause**: The Riveter binary doesn't have execute permissions.

**Solution**:
```bash
# Fix permissions
chmod +x $(which riveter)

# Verify fix
ls -la $(which riveter)
riveter --version
```

🔗 **Related**: [Platform-Specific Issues](troubleshooting.md#platform-specific-issues)

#### `cannot be opened because the developer cannot be verified` (macOS)

**Cause**: macOS Gatekeeper is blocking the unsigned binary.

**Solution**:
```bash
# Allow the binary to run (one-time setup)
sudo xattr -rd com.apple.quarantine $(which riveter)

# Or install via Homebrew which handles code signing
brew install scottryanhoward/homebrew-riveter/riveter
```

🔗 **Related**: [macOS Installation Issues](troubleshooting.md#macos-cannot-be-opened-because-the-developer-cannot-be-verified)

## Rule Loading Errors

### Rule Pack Errors

#### `Rule pack 'PACK_NAME' not found`

**Cause**: The specified rule pack name doesn't exist or is misspelled.

**Solutions**:
1. **List available rule packs**:
   ```bash
   riveter list-rule-packs
   ```

2. **Use exact rule pack names** (case-sensitive):
   ```bash
   # Correct names
   riveter scan -p aws-security -t main.tf
   riveter scan -p cis-aws -t main.tf
   riveter scan -p soc2-security -t main.tf

   # Common mistakes to avoid
   # ❌ AWS-Security → ✅ aws-security
   # ❌ cis_aws → ✅ cis-aws
   # ❌ soc-2 → ✅ soc2-security
   ```

3. **Verify rule pack file exists**:
   ```bash
   ls -la rule_packs/
   ls -la rule_packs/aws-security.yml
   ```

🔗 **Related**: [Rule Packs Guide](rule-packs.md) | [Available Rule Packs](README.md#available-rule-packs)

#### `No rules loaded`

**Cause**: No rule pack (`-p`) or custom rules file (`-r`) was specified.

**Solution**: Always specify either a rule pack or custom rules:
```bash
# With rule pack
riveter scan -p aws-security -t main.tf

# With custom rules
riveter scan -r rules.yml -t main.tf

# With both
riveter scan -r custom-rules.yml -p aws-security -t main.tf
```

**Common Mistakes**:
```bash
# ❌ Wrong: No rules specified
riveter scan -t main.tf

# ✅ Correct: Rule pack specified
riveter scan -p aws-security -t main.tf
```

🔗 **Related**: [CLI Commands](README.md#cli-commands) | [Quick Start](README.md#quick-start)

#### `Failed to load rule pack: Invalid YAML syntax`

**Cause**: The rule pack file contains invalid YAML syntax.

**Solutions**:
1. **Validate rule pack syntax**:
   ```bash
   riveter validate-rule-pack rule_packs/aws-security.yml
   ```

2. **Check for common YAML issues**:
   ```bash
   # Look for syntax errors
   cat rule_packs/aws-security.yml | head -20

   # Check file encoding
   file -i rule_packs/aws-security.yml
   ```

3. **Restore from backup or re-download**:
   ```bash
   # For built-in rule packs, reinstall Riveter
   brew reinstall riveter

   # For custom rule packs, check version control
   git checkout rule_packs/custom-rules.yml
   ```

🔗 **Related**: [Rule Pack Validation](README.md#rule-pack-commands) | [YAML Syntax Guide](../reference/yaml-syntax.md)

### Custom Rules Errors

#### `Custom rules file 'FILE_PATH' not found`

**Cause**: The specified custom rules file doesn't exist or the path is incorrect.

**Solutions**:
1. **Verify file exists**:
   ```bash
   ls -la rules.yml
   pwd  # Check current directory
   ```

2. **Use correct file path**:
   ```bash
   # Relative path
   riveter scan -r ./rules.yml -t main.tf

   # Absolute path
   riveter scan -r /full/path/to/rules.yml -t main.tf
   ```

3. **Create a basic rules file**:
   ```bash
   cat > rules.yml << EOF
   rules:
     - id: example-rule
       description: Example validation rule
       resource_type: aws_instance
       assert:
         instance_type: t2.micro
   EOF
   ```

🔗 **Related**: [Writing Custom Rules](README.md#writing-custom-rules) | [Rule Syntax Reference](../reference/rule-syntax.md)

#### `Invalid rule syntax in custom rules file`

**Cause**: The custom rules file contains invalid rule definitions.

**Solutions**:
1. **Validate rules file**:
   ```bash
   riveter validate-rule-pack rules.yml
   ```

2. **Check common syntax issues**:
   ```yaml
   # ❌ Wrong: Missing required fields
   rules:
     - description: Missing ID and resource_type

   # ✅ Correct: All required fields
   rules:
     - id: unique-rule-id
       description: Rule description
       resource_type: aws_instance
       assert:
         instance_type: t2.micro
   ```

3. **Start with minimal rule**:
   ```yaml
   rules:
     - id: test-rule
       resource_type: aws_instance
       assert:
         instance_type: present
   ```

🔗 **Related**: [Rule Structure Reference](README.md#rule-structure-reference) | [Custom Rules Examples](../examples/custom-rules/)

## Terraform Parsing Errors

### File Access Errors

#### `Terraform file 'FILE_PATH' not found`

**Cause**: The specified Terraform file doesn't exist or the path is incorrect.

**Solutions**:
1. **Verify file exists**:
   ```bash
   ls -la main.tf
   find . -name "*.tf" -type f
   ```

2. **Use correct file path**:
   ```bash
   # Current directory
   riveter scan -p aws-security -t main.tf

   # Subdirectory
   riveter scan -p aws-security -t terraform/main.tf

   # Different file name
   riveter scan -p aws-security -t infrastructure.tf
   ```

3. **Check file permissions**:
   ```bash
   ls -la main.tf
   chmod 644 main.tf  # Fix permissions if needed
   ```

🔗 **Related**: [CLI Commands](README.md#cli-commands) | [File Path Troubleshooting](troubleshooting.md#terraform-parsing-troubleshooting)

#### `Failed to read Terraform file: Permission denied`

**Cause**: Insufficient permissions to read the Terraform file.

**Solution**:
```bash
# Check current permissions
ls -la main.tf

# Fix permissions
chmod 644 main.tf

# Verify fix
cat main.tf | head -5
```

🔗 **Related**: [File Permissions Guide](../reference/file-permissions.md)

### Syntax Errors

#### `Failed to parse Terraform file: Invalid HCL syntax`

**Cause**: The Terraform file contains invalid HCL (HashiCorp Configuration Language) syntax.

**Solutions**:
1. **Validate Terraform syntax**:
   ```bash
   terraform validate
   terraform fmt -check
   ```

2. **Check for common HCL issues**:
   ```bash
   # Look for unclosed braces
   grep -c "{" main.tf && grep -c "}" main.tf

   # Check for syntax errors around line numbers
   cat -n main.tf | head -20
   ```

3. **Test with minimal file**:
   ```bash
   cat > test.tf << EOF
   resource "aws_instance" "test" {
     instance_type = "t2.micro"
   }
   EOF

   riveter scan -p aws-security -t test.tf
   rm test.tf
   ```

4. **Common syntax fixes**:
   ```hcl
   # ❌ Wrong: Missing quotes
   resource aws_instance test {

   # ✅ Correct: Proper quotes
   resource "aws_instance" "test" {

   # ❌ Wrong: Unclosed brace
   resource "aws_instance" "test" {
     instance_type = "t2.micro"

   # ✅ Correct: Closed brace
   resource "aws_instance" "test" {
     instance_type = "t2.micro"
   }
   ```

🔗 **Related**: [HCL Syntax Guide](../terraform/hcl-syntax.md) | [Terraform Validation](../terraform/validation.md)

#### `Unexpected token at line X, column Y`

**Cause**: Specific syntax error at the indicated location.

**Solutions**:
1. **Check the specific line**:
   ```bash
   # View around the error line (replace X with actual line number)
   sed -n 'X-2,X+2p' main.tf
   ```

2. **Common token issues**:
   ```hcl
   # ❌ Wrong: Missing comma in list
   cidr_blocks = ["10.0.0.0/8" "192.168.0.0/16"]

   # ✅ Correct: Comma between list items
   cidr_blocks = ["10.0.0.0/8", "192.168.0.0/16"]

   # ❌ Wrong: Missing equals sign
   instance_type "t2.micro"

   # ✅ Correct: Equals sign for assignment
   instance_type = "t2.micro"
   ```

3. **Use terraform fmt to fix formatting**:
   ```bash
   terraform fmt main.tf
   ```

🔗 **Related**: [Terraform Formatting](../terraform/formatting.md) | [Common HCL Mistakes](../terraform/common-mistakes.md)

## Validation Errors

### Resource Matching Errors

#### `No resources found for validation`

**Cause**: The Terraform file doesn't contain any `resource` blocks that Riveter can validate.

**Solutions**:
1. **Check for resource definitions**:
   ```bash
   # Look for resource blocks
   grep -n "resource " main.tf

   # Count resources
   grep -c "resource " main.tf
   ```

2. **Verify resource types are supported**:
   ```bash
   # List resource types in your file
   grep "resource " main.tf | awk '{print $2}' | sort | uniq

   # Check for AWS/Azure/GCP resources
   grep "resource " main.tf | grep -E "(aws_|azurerm_|google_)"
   ```

3. **Add a test resource**:
   ```hcl
   resource "aws_instance" "test" {
     instance_type = "t2.micro"
     ami           = "ami-12345678"
   }
   ```

**Note**: Riveter validates `resource` blocks, not `data` sources, `variable` declarations, or `output` values.

🔗 **Related**: [Supported Resources](../reference/supported-resources.md) | [Resource Types Guide](../terraform/resource-types.md)

#### `Resource type 'RESOURCE_TYPE' not supported by any loaded rules`

**Cause**: None of the loaded rules apply to the resource types in your Terraform file.

**Solutions**:
1. **Check resource types in your file**:
   ```bash
   grep "resource " main.tf | awk '{print $2}' | sort | uniq
   ```

2. **Use appropriate rule packs**:
   ```bash
   # For AWS resources
   riveter scan -p aws-security -t main.tf

   # For Azure resources
   riveter scan -p azure-security -t main.tf

   # For GCP resources
   riveter scan -p gcp-security -t main.tf

   # For multi-cloud
   riveter scan -p multi-cloud-security -t main.tf
   ```

3. **Create custom rules for unsupported resources**:
   ```yaml
   rules:
     - id: custom-resource-rule
       resource_type: your_custom_resource_type
       assert:
         property: expected_value
   ```

🔗 **Related**: [Rule Packs Guide](rule-packs.md) | [Custom Rules for New Resources](../advanced/custom-resources.md)

### Rule Evaluation Errors

#### `Rule evaluation failed: Property 'PROPERTY' not found in resource`

**Cause**: A rule is trying to check a property that doesn't exist in the resource configuration.

**Solutions**:
1. **Check the resource configuration**:
   ```bash
   # Find the specific resource
   grep -A 20 "resource.*RESOURCE_NAME" main.tf
   ```

2. **Add the missing property**:
   ```hcl
   # Example: Adding missing encryption property
   resource "aws_s3_bucket" "example" {
     bucket = "my-bucket"

     # Add missing encryption configuration
     server_side_encryption_configuration {
       rule {
         apply_server_side_encryption_by_default {
           sse_algorithm = "AES256"
         }
       }
     }
   }
   ```

3. **Modify rule to handle optional properties**:
   ```yaml
   # Use 'present' assertion for optional properties
   rules:
     - id: check-optional-property
       resource_type: aws_instance
       assert:
         monitoring: present  # Just check if property exists
   ```

🔗 **Related**: [Resource Configuration Guide](../terraform/resource-configuration.md) | [Rule Assertions](../reference/rule-assertions.md)

#### `Assertion failed: Expected 'VALUE1', got 'VALUE2'`

**Cause**: The resource property value doesn't match the rule's expected value.

**Solutions**:
1. **Understand the rule requirement**:
   ```bash
   # Check which rule failed
   riveter scan -p aws-security -t main.tf --output-format json | jq '.results[] | select(.status == "FAIL")'
   ```

2. **Update resource to match rule**:
   ```hcl
   # Example: Fix instance type
   resource "aws_instance" "web" {
     # ❌ Wrong: instance_type = "t2.nano"
     instance_type = "t3.large"  # ✅ Correct: Meets rule requirement
   }
   ```

3. **Modify rule if requirement is too strict**:
   ```yaml
   # Use regex for flexible matching
   rules:
     - id: instance-type-rule
       resource_type: aws_instance
       assert:
         instance_type:
           regex: "^(t3|m5|c5)\\.(large|xlarge)$"
   ```

🔗 **Related**: [Rule Operators](../reference/rule-operators.md) | [Common Validation Fixes](../guides/validation-fixes.md)

## Output and Formatting Errors

### Output Format Errors

#### `Invalid output format 'FORMAT_NAME'`

**Cause**: The specified output format is not supported.

**Solution**: Use one of the supported output formats:
```bash
# Supported formats
riveter scan -p aws-security -t main.tf --output-format table   # Default
riveter scan -p aws-security -t main.tf --output-format json
riveter scan -p aws-security -t main.tf --output-format junit
riveter scan -p aws-security -t main.tf --output-format sarif
```

🔗 **Related**: [Output Formats](README.md#output-formats) | [CLI Reference](../reference/cli.md)

#### `Failed to write output file: Permission denied`

**Cause**: Insufficient permissions to write to the specified output location.

**Solutions**:
1. **Check directory permissions**:
   ```bash
   ls -la $(dirname output-file.json)
   ```

2. **Use writable directory**:
   ```bash
   # Write to current directory
   riveter scan -p aws-security -t main.tf --output-format json > results.json

   # Write to home directory
   riveter scan -p aws-security -t main.tf --output-format json > ~/results.json
   ```

3. **Fix permissions**:
   ```bash
   chmod 755 $(dirname output-file.json)
   ```

🔗 **Related**: [File Permissions](../reference/file-permissions.md)

## Network and Connectivity Errors

### Download Errors

#### `Failed to download rule pack: Connection timeout`

**Cause**: Network connectivity issues or firewall blocking the connection.

**Solutions**:
1. **Test internet connectivity**:
   ```bash
   curl -I https://github.com
   ping github.com
   ```

2. **Check proxy settings**:
   ```bash
   echo "HTTP_PROXY: $HTTP_PROXY"
   echo "HTTPS_PROXY: $HTTPS_PROXY"
   ```

3. **Use local installation**:
   ```bash
   # Install from local source
   git clone https://github.com/riveter/riveter.git
   cd riveter && pip install -e .
   ```

🔗 **Related**: [Network Troubleshooting](troubleshooting.md#network-and-connectivity-issues) | [Offline Installation](../installation/offline.md)

#### `SSL certificate verification failed`

**Cause**: SSL/TLS certificate issues, often in corporate environments.

**Solutions**:
1. **Update certificates**:
   ```bash
   # macOS
   brew install ca-certificates

   # Linux
   sudo apt-get update && sudo apt-get install ca-certificates
   ```

2. **Check corporate proxy/firewall**:
   ```bash
   # Test direct connection
   openssl s_client -connect github.com:443 -servername github.com
   ```

3. **Use alternative installation method**:
   ```bash
   # Download manually and install locally
   wget https://github.com/riveter/riveter/archive/main.zip
   unzip main.zip && cd riveter-main
   pip install -e .
   ```

🔗 **Related**: [Corporate Network Setup](../installation/corporate-networks.md) | [SSL Troubleshooting](../reference/ssl-issues.md)

## Performance and Resource Errors

### Memory Errors

#### `MemoryError: Unable to allocate memory`

**Cause**: Insufficient system memory for processing large Terraform files.

**Solutions**:
1. **Use Homebrew installation** (lower memory usage):
   ```bash
   brew install scottryanhoward/homebrew-riveter/riveter
   ```

2. **Split large Terraform files**:
   ```bash
   # Check file size
   wc -l main.tf

   # Split into smaller files
   terraform fmt main.tf  # Clean formatting first
   # Then manually split into modules
   ```

3. **Increase system memory or use smaller rule packs**:
   ```bash
   # Use targeted rule packs instead of comprehensive ones
   riveter scan -p aws-security -t main.tf  # Instead of multiple packs
   ```

🔗 **Related**: [Performance Optimization](troubleshooting.md#performance-issues) | [Memory Management](../reference/memory-optimization.md)

#### `Process killed (signal 9)`

**Cause**: System killed the process due to excessive memory usage.

**Solutions**:
1. **Monitor memory usage**:
   ```bash
   # Check available memory
   free -h  # Linux
   vm_stat  # macOS
   ```

2. **Use memory-efficient options**:
   ```bash
   # Homebrew binary (more efficient)
   brew install scottryanhoward/homebrew-riveter/riveter

   # Process smaller files
   riveter scan -p aws-security -t module1.tf
   riveter scan -p aws-security -t module2.tf
   ```

🔗 **Related**: [System Requirements](../installation/requirements.md) | [Large File Processing](../guides/large-files.md)

## Getting Additional Help

### When Error Messages Don't Match

If you encounter an error message not listed in this dictionary:

1. **Search the documentation**:
   - [Troubleshooting Guide](troubleshooting.md)
   - [FAQ](faq.md)
   - [GitHub Issues](https://github.com/riveter/riveter/issues)

2. **Report the issue**:
   ```bash
   # Gather diagnostic information
   riveter --version
   uname -a
   echo $SHELL

   # Include the full error message and command used
   ```

3. **Community support**:
   - 🐛 [GitHub Issues](https://github.com/riveter/riveter/issues) - Bug reports
   - 💬 [GitHub Discussions](https://github.com/riveter/riveter/discussions) - Questions
   - 📖 [Technical Documentation](../TECHNICAL.md) - Deep technical details

### Error Reporting Template

When reporting errors, include:

```bash
# System Information
riveter --version
uname -a
echo $SHELL

# Command that failed
riveter scan -p aws-security -t main.tf

# Full error output
[Paste complete error message here]

# File information (if relevant)
ls -la main.tf
head -10 main.tf
```

🔗 **Related**: [Bug Report Template](../.github/ISSUE_TEMPLATE/bug_report.md) | [Contributing Guide](../../CONTRIBUTING.md)
