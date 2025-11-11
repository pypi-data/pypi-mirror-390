# Why Riveter?

## The Problem: Infrastructure Validation Gaps

Modern infrastructure teams face a critical challenge: **catching security and compliance issues before they reach production**. While tools exist for various stages of the infrastructure lifecycle, there's often a gap between what developers need during development and what security teams require for compliance.

Common pain points include:

- **Late-stage discovery**: Security issues found after deployment are expensive to fix
- **Complex tool ecosystems**: Multiple tools with overlapping features create confusion
- **Compliance burden**: Manual compliance checks are time-consuming and error-prone
- **Developer friction**: Heavy security tools slow down development velocity
- **Custom policy enforcement**: Organizational standards are hard to codify and enforce

## The Riveter Solution

Riveter is an **Infrastructure Rule Enforcement as Code** tool designed to validate Terraform configurations against security and compliance standards. It bridges the gap between development speed and security requirements by providing:

### 🚀 Shift-Left Security

Catch infrastructure issues **before deployment**, not after. Riveter runs locally or in CI/CD pipelines, giving developers immediate feedback without waiting for cloud deployment or security reviews.

### 📋 Pre-Built Compliance Frameworks

Stop writing rules from scratch. Riveter includes ready-to-use rule packs for:
- **AWS Security Best Practices** (26 rules)
- **CIS AWS Foundations Benchmark** (22 rules)
- **CIS Azure Foundations Benchmark** (34 rules)
- **SOC 2 Security Trust Service Criteria** (28 rules)

### 🔧 Flexible and Extensible

Use pre-built rules, write custom rules, or combine both. Riveter's YAML-based rule format is simple yet powerful, supporting:
- Advanced operators (regex, comparisons, length checks)
- Resource filtering by tags, environment, or any attribute
- Nested property validation
- Multiple severity levels (error, warning, info)

### ⚡ Developer-Friendly

Designed for speed and ease of use:
- Install in under 2 minutes
- Rich terminal output with clear error messages
- Multiple output formats (table, JSON, JUnit, SARIF)
- Integrates seamlessly with existing Terraform workflows

## How Riveter Complements Other Tools

Riveter isn't trying to replace your existing tools—it's designed to **complement** them by filling specific gaps in your infrastructure validation workflow.

### Riveter + Terraform

**Terraform** is your infrastructure provisioning tool. **Riveter** validates that your Terraform configurations meet your security and compliance requirements before you apply them.

- **Terraform**: "Can I create this infrastructure?"
- **Riveter**: "Should I create this infrastructure?"

Use Riveter to catch policy violations before `terraform apply`, saving time and preventing misconfigurations.

### Riveter + Checkov

**Checkov** is a comprehensive static analysis tool with thousands of built-in policies. **Riveter** is focused on custom organizational policies and compliance frameworks.

**When to use Checkov:**
- You want broad coverage with minimal configuration
- You need support for multiple IaC tools (Terraform, CloudFormation, Kubernetes, etc.)
- You want to scan for known CVEs and vulnerabilities

**When to use Riveter:**
- You need to enforce custom organizational policies
- You want lightweight, focused compliance validation
- You prefer simple YAML rules over complex policy languages
- You need to combine standard frameworks with custom rules

**Use both together:**
```bash
# Broad security scanning with Checkov
checkov -d infrastructure/

# Custom policy enforcement with Riveter
riveter scan -p aws-security -r company-policies.yml -t infrastructure/
```

### Riveter + TFLint

**TFLint** focuses on Terraform syntax, best practices, and provider-specific issues. **Riveter** focuses on security and compliance validation.

**TFLint strengths:**
- Terraform syntax validation
- Provider-specific best practices
- Deprecated syntax detection
- Performance optimization suggestions

**Riveter strengths:**
- Security and compliance rule enforcement
- Custom organizational policies
- Multi-framework compliance validation
- Business logic validation

**Use both together:**
```bash
# Validate Terraform syntax and best practices
tflint

# Validate security and compliance
riveter scan -p aws-security -p cis-aws -t main.tf
```

### Riveter + OPA/Conftest

**Open Policy Agent (OPA)** and **Conftest** provide powerful policy-as-code using the Rego language. **Riveter** provides YAML-based rule enforcement with pre-built compliance packs.

**OPA/Conftest strengths:**
- Rego policy language (extremely powerful and flexible)
- Universal policy engine (works with any JSON/YAML data)
- Large ecosystem and community
- Complex policy logic and relationships
- Policy testing framework

**Riveter strengths:**
- Simple YAML rule format (no programming required)
- Pre-built compliance frameworks (CIS, SOC 2)
- Terraform-specific validation
- Immediate productivity (no Rego learning curve)
- Built-in compliance rule packs

**Choose based on your needs:**
- **OPA/Conftest**: If you need maximum flexibility and have complex policy requirements
- **Riveter**: If you want to enforce compliance quickly without learning Rego

**Use both together:**
```bash
# Complex policy logic with OPA/Conftest
conftest test main.tf -p opa-policies/

# Compliance validation with Riveter
riveter scan -p cis-aws -p soc2-security -t main.tf
```

### Riveter + Terrascan

**Terrascan** provides policy-as-code scanning with Rego policies. **Riveter** provides YAML-based rule enforcement with pre-built compliance packs.

**Terrascan strengths:**
- Rego policy language (powerful but complex)
- Built-in policies for multiple clouds
- Kubernetes and Helm support

**Riveter strengths:**
- Simple YAML rule format (easier to write and maintain)
- Pre-built compliance frameworks (CIS, SOC 2)
- Focused on Terraform validation
- Lightweight and fast

**Choose based on your needs:**
- **Terrascan**: If you need Rego's power and multi-tool support
- **Riveter**: If you want simplicity and compliance-focused validation

### Riveter + Sentinel (Terraform Cloud/Enterprise)

**Sentinel** is HashiCorp's policy-as-code framework for Terraform Cloud/Enterprise. **Riveter** is an open-source alternative for teams not using Terraform Cloud.

**Sentinel strengths:**
- Deep integration with Terraform Cloud/Enterprise
- Policy enforcement at the platform level
- Cost estimation integration

**Riveter strengths:**
- Open source and free
- Works with any Terraform workflow (local, CI/CD, etc.)
- No Terraform Cloud subscription required
- Pre-built compliance frameworks

**Use Riveter if:**
- You're not using Terraform Cloud/Enterprise
- You want an open-source solution
- You need local validation during development

## Why Choose Riveter?

### 1. Compliance-First Design

Riveter is built specifically for security and compliance validation. The pre-built rule packs implement real-world compliance frameworks (CIS, SOC 2) that you can use immediately.

### 2. Simple Yet Powerful

YAML-based rules are easy to write and understand. No need to learn complex policy languages like Rego or Sentinel. Yet Riveter supports advanced operators for sophisticated validation logic.

### 3. Developer Experience

Riveter respects developer time:
- Fast installation and setup
- Clear, actionable error messages
- Rich terminal output
- Multiple output formats for different use cases

### 4. Flexible Integration

Use Riveter however you want:
- Locally during development
- In pre-commit hooks
- In CI/CD pipelines
- As part of security reviews

### 5. Open Source and Extensible

Riveter is MIT licensed and designed for extension:
- Create custom rule packs for your organization
- Share rule packs with the community
- Contribute to the core project

## Real-World Use Cases

### Enterprise Compliance Team

**Challenge**: Ensure all infrastructure meets CIS benchmarks and SOC 2 requirements before deployment.

**Solution**:
```bash
# Validate against multiple compliance frameworks
riveter scan -p cis-aws -p soc2-security -t infrastructure/ --output-format junit
```

**Result**: Automated compliance validation in CI/CD, reducing manual review time by 80%.

### Startup Security Team

**Challenge**: Enforce security best practices without slowing down development.

**Solution**:
```bash
# Quick security check before deployment
riveter scan -p aws-security -t main.tf
```

**Result**: Developers get immediate feedback on security issues, preventing misconfigurations before they reach production.

### Platform Engineering Team

**Challenge**: Enforce organizational standards across multiple teams and projects.

**Solution**:
```bash
# Combine company policies with industry standards
riveter scan -r company-policies.yml -p aws-security -t main.tf
```

**Result**: Consistent policy enforcement across all teams with custom rules for organizational requirements.

### DevSecOps Pipeline

**Challenge**: Integrate security validation into existing CI/CD workflows.

**Solution**:
```yaml
# GitHub Actions workflow
- name: Security Validation
  run: |
    riveter scan -p aws-security -t main.tf --output-format sarif > results.sarif
```

**Result**: Automated security scanning with results integrated into GitHub Security tab.

## When to Use Riveter

### ✅ Riveter is Great For:

- **Terraform-focused teams** who need security and compliance validation
- **Organizations with custom policies** that need to be enforced
- **Compliance requirements** (CIS, SOC 2, etc.) that need automation
- **Development teams** who want fast, local validation
- **CI/CD pipelines** that need lightweight security checks
- **Teams without Terraform Cloud** who need policy enforcement

### ⚠️ Consider Other Tools If:

- You need multi-tool support (CloudFormation, Kubernetes, etc.) → **Checkov**
- You need Terraform syntax validation → **TFLint**
- You're heavily invested in Terraform Cloud → **Sentinel**
- You need complex policy logic and relationships → **OPA/Conftest**
- You need universal policy engine for any data format → **OPA**
- You need runtime security monitoring → **Cloud security platforms**

## Getting Started

Ready to try Riveter? Get started in under 2 minutes:

```bash
# 1. Install Riveter
git clone https://github.com/riveter/riveter.git && cd riveter
python3 -m venv venv && source venv/bin/activate
pip install -e .

# 2. See available compliance frameworks
riveter list-rule-packs

# 3. Validate your Terraform
riveter scan -p aws-security -t main.tf
```

## The Bottom Line

**Riveter is a focused, developer-friendly tool for Terraform security and compliance validation.** It doesn't try to do everything—instead, it does one thing well: helping you catch infrastructure issues before they reach production.

Use Riveter alongside your existing tools to create a comprehensive infrastructure validation strategy:

- **TFLint** for syntax and best practices
- **Checkov** for broad security scanning
- **OPA/Conftest** for complex policy logic
- **Riveter** for compliance and custom policies
- **Terraform** for infrastructure provisioning

Together, these tools create a defense-in-depth approach to infrastructure security.

---

**Questions? Want to contribute?**

- 📖 [Read the Documentation](README.md)
- 🐛 [Report Issues](https://github.com/riveter/riveter/issues)
- 💬 [Join Discussions](https://github.com/riveter/riveter/discussions)
- 🤝 [Contributing Guide](CONTRIBUTING.md)

**Made with ❤️ by the Riveter team**

*Riveter helps you build secure, compliant infrastructure from day one.*
