# Riveter 5-Minute Quick Start

Welcome to Riveter! This quick start will get you from zero to your first successful infrastructure validation in under 5 minutes.

## What You'll Learn

- How to scan Terraform configurations with Riveter
- How to use pre-built rule packs for security validation
- How to identify and fix common infrastructure issues
- How to integrate Riveter into your workflow

## Prerequisites

- Riveter installed ([Installation Guide](../../README.md#installation))
- Basic familiarity with Terraform (helpful but not required)

## 🚀 5-Step Quick Start (Under 5 Minutes)

### Step 1: Install Riveter ⏱️ *30 seconds*

Choose your preferred installation method:

```bash
# Option A: Homebrew (Recommended - Fastest)
brew install scottryanhoward/homebrew-riveter/riveter

# Option B: Direct download
curl -L https://github.com/scottryanhoward/riveter/releases/latest/download/riveter-darwin-amd64 -o riveter
chmod +x riveter && sudo mv riveter /usr/local/bin/

# Option C: Python pip
pip install riveter
```

**✅ Success Check:** Run `riveter --version` - you should see version information.

**🔧 Troubleshooting:**
- **Command not found?** Check your PATH or try `./riveter --version` if using direct download
- **Permission denied?** Make sure the binary is executable: `chmod +x riveter`

---

### Step 2: Download Examples ⏱️ *30 seconds*

```bash
# Navigate to the quickstart directory (if you cloned the repo)
cd examples/quickstart

# OR download just the examples
curl -L https://github.com/scottryanhoward/riveter/archive/main.zip -o riveter-examples.zip
unzip riveter-examples.zip
cd riveter-main/examples/quickstart
```

**✅ Success Check:** Run `ls` - you should see `aws/`, `azure/`, `gcp/` directories and this README.

**🔧 Troubleshooting:**
- **No directories?** Make sure you're in the right folder: `pwd` should end with `/quickstart`
- **Download failed?** Try the direct GitHub link or clone the full repository

---

### Step 3: Scan Insecure Infrastructure ⏱️ *1 minute*

Let's see what security problems look like:

```bash
# Scan AWS infrastructure with intentional security issues
riveter scan -p aws-security -t aws/insecure.tf
```

**✅ Success Check:** You should see **multiple failures** like:
```
❌ FAIL: ec2_no_public_ip - EC2 instances should not have public IP addresses
❌ FAIL: ebs_encryption_enabled - EBS volumes must be encrypted
❌ FAIL: security_group_ssh_restricted - SSH should not be open to 0.0.0.0/0
❌ FAIL: required_tags - Resources must have required tags
```

**🔧 Troubleshooting:**
- **No output?** Check that the file exists: `ls aws/insecure.tf`
- **"No rules loaded"?** Verify rule pack exists: `riveter list-rule-packs | grep aws-security`
- **Different errors?** That's normal - rule packs may vary by version

---

### Step 4: Fix Issues & See Success ⏱️ *2 minutes*

Now scan the secure version to see what success looks like:

```bash
# Scan the fixed AWS infrastructure
riveter scan -p aws-security -t aws/secure.tf
```

**✅ Success Check:** You should see **all checks passing**:
```
✅ PASS: ec2_no_public_ip - EC2 instances in private subnets
✅ PASS: ebs_encryption_enabled - All volumes encrypted
✅ PASS: security_group_ssh_restricted - SSH restricted to VPC only
✅ PASS: required_tags - All resources properly tagged
```

**Compare the files** to see what changed:
```bash
# See the differences between insecure and secure versions
diff aws/insecure.tf aws/secure.tf | head -20
```

**🔧 Troubleshooting:**
- **Still seeing failures?** Compare your output with the expected results above
- **Want to understand a specific rule?** Use `riveter explain-rule <rule-id>`

---

### Step 5: Try Other Clouds ⏱️ *1 minute*

Test your knowledge with Azure and GCP:

```bash
# Azure - See problems, then solutions
riveter scan -p azure-security -t azure/insecure.tf
riveter scan -p azure-security -t azure/secure.tf

# GCP - See problems, then solutions
riveter scan -p gcp-security -t gcp/insecure.tf
riveter scan -p gcp-security -t gcp/secure.tf
```

**✅ Success Check:** Each cloud should show similar patterns:
- Insecure versions: Multiple failures
- Secure versions: All passes

**🔧 Troubleshooting:**
- **Missing rule packs?** List available packs: `riveter list-rule-packs`
- **Want to try multiple clouds at once?** Use: `riveter scan -p aws-security,azure-security -t */secure.tf`

## 🎉 Success! You Did It!

**Congratulations!** In under 5 minutes, you've:
- ✅ Installed and configured Riveter
- ✅ Scanned infrastructure configurations
- ✅ Identified common security issues
- ✅ Validated secure configurations
- ✅ Tested multiple cloud providers

**You now understand:**
- How Riveter identifies infrastructure security issues
- The difference between secure and insecure configurations
- How to use rule packs for different cloud providers
- What successful validation looks like

## 🚨 Common Issues & Solutions

### "Command not found: riveter"
```bash
# Check if it's in your PATH
echo $PATH | grep -o '/usr/local/bin'

# If using Homebrew, try:
brew doctor
brew reinstall scottryanhoward/homebrew-riveter/riveter
```

### "No rules loaded" or "Rule pack not found"
```bash
# List available rule packs
riveter list-rule-packs

# If empty, reinstall or check your installation
riveter --help
```

### "File not found" errors
```bash
# Make sure you're in the right directory
pwd  # Should end with /quickstart
ls   # Should show aws/, azure/, gcp/ folders
```

### Scan results don't match examples
- Rule packs evolve over time - your results may differ slightly
- Focus on the pattern: insecure = failures, secure = passes
- Use `riveter --version` to check your version

### Want to understand a specific rule?
```bash
# Get detailed information about any rule
riveter explain-rule ec2_no_public_ip
riveter show-rule-pack aws-security
```

## 🎯 What's Next? Choose Your Learning Path

### 📋 Quick Skill Assessment

**Not sure where to start?** Take our [2-minute skill assessment](skill-assessment.md) for personalized recommendations.

**How would you describe your current level?**

<details>
<summary><strong>🟢 Beginner</strong> - "I'm new to infrastructure security and want to learn the basics"</summary>

**Perfect! Start here:**
1. **[Understanding Infrastructure Security](../../docs/tutorial.md)** *(15 min)* - Learn why infrastructure validation matters
2. **[Rule Writing Basics](../rules/beginner/)** *(30 min)* - Write your first custom rule
3. **[Common Security Patterns](../by-use-case/web-application/)** *(20 min)* - See real-world examples

**Your next milestone:** Successfully write and test a custom rule for your infrastructure.
</details>

<details>
<summary><strong>🟡 Intermediate</strong> - "I understand security basics and want to implement Riveter in my workflow"</summary>

**Great! Focus on integration:**
1. **[CI/CD Integration](../ci-cd/)** *(45 min)* - Add Riveter to your pipeline
2. **[Advanced Rule Patterns](../rules/intermediate/)** *(30 min)* - Complex validation logic
3. **[Multi-Environment Setup](../configurations/)** *(25 min)* - Different rules for dev/staging/prod

**Your next milestone:** Have Riveter running in your CI/CD pipeline blocking insecure deployments.
</details>

<details>
<summary><strong>🔴 Advanced</strong> - "I want to customize Riveter for enterprise use and complex scenarios"</summary>

**Excellent! Dive into advanced topics:**
1. **[Custom Rule Packs](../../docs/RULE_PACK_GUIDE.md)** *(60 min)* - Build organization-specific rule sets
2. **[Performance Optimization](../../docs/PERFORMANCE_TESTING.md)** *(30 min)* - Scale for large codebases
3. **[Multi-Cloud Governance](../../docs/MULTI_CLOUD_GUIDE.md)** *(45 min)* - Standardize across cloud providers

**Your next milestone:** Deploy custom rule packs across multiple teams and cloud environments.
</details>

---

### 🎭 Role-Based Learning Paths

#### 👩‍💻 **Developer** - *"I want to integrate security into my development workflow"*

**🚀 Quick Wins (Next 30 minutes):**
- **[Local Development Setup](../configurations/local-dev.md)** - Run Riveter before every commit
- **[VS Code Integration](../ci-cd/vscode-extension.md)** - Get real-time feedback while coding
- **[Pre-commit Hooks](../ci-cd/pre-commit-setup.md)** - Catch issues before they reach CI

**📈 Level Up (Next 2 hours):**
- **[GitHub Actions Integration](../ci-cd/github-actions/)** - Automated security checks on every PR
- **[Custom Rules for Your Stack](../rules/by-technology/)** - Rules specific to your frameworks
- **[Debugging Failed Validations](../../docs/TROUBLESHOOTING.md)** - Quickly fix validation errors

**🎯 Mastery Goals:**
- [ ] Riveter runs automatically on every commit
- [ ] You can write custom rules for your application patterns
- [ ] Your team's deployment pipeline includes security validation
- [ ] You can debug and fix validation failures in under 5 minutes

---

#### 🔒 **Security Engineer** - *"I want to enforce security policies across infrastructure"*

**🚀 Quick Wins (Next 30 minutes):**
- **[Security Rule Pack Overview](../../rule_packs/)** - Understand all available security rules
- **[Compliance Framework Mapping](../../docs/COMPLIANCE_MAPPINGS.md)** - Map rules to SOC2, HIPAA, PCI-DSS
- **[Security Baseline Setup](../configurations/security-baseline.md)** - Minimum security requirements

**📈 Level Up (Next 2 hours):**
- **[Custom Security Rules](../rules/security-patterns/)** - Organization-specific security policies
- **[Threat Modeling Integration](../advanced/threat-modeling.md)** - Rules based on threat analysis
- **[Security Metrics & Reporting](../../docs/MONITORING_GUIDE.md)** - Track security posture over time

**🎯 Mastery Goals:**
- [ ] All infrastructure deployments are validated against security policies
- [ ] You have custom rules for your organization's specific threats
- [ ] Security violations are automatically reported and tracked
- [ ] You can generate compliance reports for audits

---

#### 📋 **Platform/DevOps Engineer** - *"I want to standardize and govern infrastructure across teams"*

**🚀 Quick Wins (Next 30 minutes):**
- **[Multi-Team Rule Distribution](../../docs/RULE_PACK_GUIDE.md)** - Share rules across teams
- **[Environment-Specific Rules](../configurations/multi-environment/)** - Different rules for dev/staging/prod
- **[Rule Pack Versioning](../../docs/VERSION_MANAGEMENT.md)** - Manage rule updates safely

**📈 Level Up (Next 2 hours):**
- **[Multi-Cloud Standardization](../../docs/MULTI_CLOUD_GUIDE.md)** - Consistent policies across AWS/Azure/GCP
- **[Centralized Policy Management](../advanced/policy-management/)** - Enterprise governance patterns
- **[Integration with IaC Tools](../ci-cd/terraform-integration/)** - Terraform, Pulumi, CDK integration

**🎯 Mastery Goals:**
- [ ] Consistent infrastructure standards across all teams and environments
- [ ] Automated rule distribution and updates
- [ ] Multi-cloud governance with unified policies
- [ ] Self-service infrastructure with built-in guardrails

---

#### 📊 **Compliance Officer** - *"I need to ensure regulatory compliance and generate audit reports"*

**🚀 Quick Wins (Next 30 minutes):**
- **[Compliance Framework Overview](../../docs/COMPLIANCE_MAPPINGS.md)** - Understand rule-to-regulation mapping
- **[Audit Report Generation](../../docs/MONITORING_GUIDE.md#audit-reports)** - Automated compliance reporting
- **[Evidence Collection](../advanced/audit-evidence.md)** - Gather proof of compliance

**📈 Level Up (Next 2 hours):**
- **[Continuous Compliance Monitoring](../advanced/continuous-compliance/)** - Real-time compliance tracking
- **[Exception Management](../advanced/exception-handling/)** - Handle approved deviations
- **[Regulatory Change Management](../advanced/regulatory-updates/)** - Adapt to new requirements

**🎯 Mastery Goals:**
- [ ] Automated compliance monitoring for all relevant frameworks
- [ ] Regular audit reports generated without manual effort
- [ ] Clear audit trail for all infrastructure changes
- [ ] Proactive alerts for compliance violations

---

### 🎓 Skill Development Checkpoints

**Complete these challenges to validate your progress:**

#### Checkpoint 1: Basic Validation *(Beginner)*
- [ ] Successfully scan infrastructure with 3 different rule packs
- [ ] Identify and fix 5 common security issues
- [ ] Write a simple custom rule for your environment

#### Checkpoint 2: Integration Mastery *(Intermediate)*
- [ ] Set up Riveter in your CI/CD pipeline
- [ ] Create environment-specific rule configurations
- [ ] Implement automated failure notifications

#### Checkpoint 3: Enterprise Deployment *(Advanced)*
- [ ] Deploy custom rule packs across multiple teams
- [ ] Set up centralized compliance reporting
- [ ] Implement multi-cloud governance policies

**🏆 Achievement Unlocked:** Complete all checkpoints to become a Riveter expert!

## Need Help?

- 📖 [Full Documentation](../../docs/)
- 🐛 [Report Issues](https://github.com/scottryanhoward/riveter/issues)
- 💬 [Community Discussions](https://github.com/scottryanhoward/riveter/discussions)
- 📧 [Contact Support](mailto:support@riveter.dev)

## File Structure

```
quickstart/
├── README.md           # This file
├── aws/
│   ├── insecure.tf    # AWS example with security issues
│   └── secure.tf      # AWS example with issues fixed
├── azure/
│   ├── insecure.tf    # Azure example with security issues
│   └── secure.tf      # Azure example with issues fixed
└── gcp/
    ├── insecure.tf    # GCP example with security issues
    └── secure.tf      # GCP example with issues fixed
```

Each example includes:
- Real-world infrastructure patterns
- Common security misconfigurations
- Clear before/after comparisons
- Detailed comments explaining the issues and fixes
