# Getting Started with Riveter

This guide helps you get up and running with Riveter quickly, from installation to your first successful validation.

## What is Riveter?

**Stop infrastructure security issues before they reach production.** Riveter validates your Terraform configurations against security and compliance standards in seconds, not hours.

### Before Riveter 😰
```bash
terraform apply
# ❌ Production incident: S3 bucket publicly accessible
# ❌ Compliance audit failure: Missing encryption
# ❌ Security team escalation: Overprivileged IAM roles
```

### After Riveter ✅
```bash
riveter scan -p aws-security -t main.tf
# ✅ Caught 3 security issues before deployment
# ✅ Fixed in development environment
# ✅ Confident, compliant production deployment
```

## Quick Installation

### Option 1: Homebrew (Recommended)
```bash
brew install scottryanhoward/homebrew-riveter/riveter
```

### Option 2: Python/pip
```bash
git clone https://github.com/riveter/riveter.git
cd riveter && python3 -m venv venv && source venv/bin/activate
pip install -e .
```

## 5-Minute Success Tutorial

### Step 1: Install (30 seconds)
```bash
brew install scottryanhoward/homebrew-riveter/riveter
```

### Step 2: Download Example (30 seconds)
```bash
curl -L https://github.com/riveter/riveter/raw/main/examples/quickstart.zip -o quickstart.zip
unzip quickstart.zip && cd quickstart
```

### Step 3: See It Fail (30 seconds)
```bash
riveter scan -p aws-security -t insecure-example.tf
# Expected: ❌ 3 security issues found
```

### Step 4: Fix and Validate (3 minutes)
```bash
riveter scan -p aws-security -t secure-example.tf
# Expected: ✅ All validations passed!
```

## Common Use Cases

### Security-First Development
```bash
# Check security best practices before deployment
riveter scan -p aws-security -t main.tf      # AWS
riveter scan -p azure-security -t main.tf    # Azure
riveter scan -p gcp-security -t main.tf      # GCP
```

### Compliance Validation
```bash
# HIPAA compliance for healthcare
riveter scan -p aws-hipaa -t healthcare-infrastructure/

# PCI-DSS for payment processing
riveter scan -p aws-pci-dss -t payment-infrastructure/

# CIS benchmarks
riveter scan -p cis-aws -t infrastructure/
```

### Multi-Cloud Environments
```bash
# Validate across multiple cloud providers
riveter scan -p multi-cloud-security -t main.tf
riveter scan -p aws-security -p azure-security -p gcp-security -t main.tf
```

## Next Steps

- **[Rule Packs Guide](rule-packs.md)** - Choose the right rule packs for your needs
- **[Visual Guides](visual-guides.md)** - Understand how Riveter works with diagrams
- **[Troubleshooting](troubleshooting.md)** - Fix common issues
- **[CI/CD Integration](../developer/cicd.md)** - Integrate into your pipeline

## Need Help?

### 🆘 Quick Help Resources
- **[FAQ](faq.md)** - Frequently asked questions and common scenarios
- **[Troubleshooting](troubleshooting.md)** - Step-by-step problem solving
- **[Error Dictionary](error-message-dictionary.md)** - Specific error explanations and solutions

### 📚 Documentation Resources
- **[Rule Packs Guide](rule-packs.md)** - Choose the right rule packs for your needs
- **[Visual Guides](visual-guides.md)** - Understand how Riveter works with diagrams
- **[Inline Help Components](inline-help-components.md)** - Documentation patterns and help templates

### 🤝 Community Support
- 🐛 **[Report Issues](https://github.com/riveter/riveter/issues)** - Bug reports and feature requests
- 💬 **[Ask Questions](https://github.com/riveter/riveter/discussions)** - Community support
- 📖 **[Technical Docs](../TECHNICAL.md)** - Deep technical documentation

💡 **Tip**: Start with the [FAQ](faq.md) for quick answers, then check [Troubleshooting](troubleshooting.md) for detailed problem-solving steps.
