# 🎯 Riveter Skill Assessment

## Quick Self-Assessment

**Answer these questions to find your ideal learning path:**

### 1. Infrastructure Security Experience

**How familiar are you with infrastructure security concepts?**

- **A)** New to infrastructure security - I want to learn the basics
- **B)** I understand basic security but haven't implemented automated validation
- **C)** I have experience with security tools and want to customize for my organization
- **D)** I'm responsible for compliance and governance across multiple teams

### 2. Current Tool Usage

**Which tools do you currently use for infrastructure validation?**

- **A)** None - I'm just getting started
- **B)** Basic linting tools (terraform validate, etc.)
- **C)** Security scanners like Checkov, TFLint, or similar
- **D)** Enterprise policy engines and compliance platforms

### 3. Your Primary Goal

**What do you want to achieve with Riveter?**

- **A)** Learn infrastructure security best practices
- **B)** Add security validation to my development workflow
- **C)** Implement organization-wide security policies
- **D)** Ensure regulatory compliance and generate audit reports

### 4. Team Size & Scope

**What's your scope of responsibility?**

- **A)** Individual developer or small team (1-5 people)
- **B)** Development team or project (5-20 people)
- **C)** Multiple teams or department (20+ people)
- **D)** Enterprise-wide or regulatory oversight

---

## 📊 Results & Recommendations

### Mostly A's: **🟢 Beginner Path**

**You're just getting started - perfect!**

**Start here:**
1. [Understanding Infrastructure Security](../../docs/tutorial.md) *(15 min)*
2. [Basic Rule Writing](../rules/beginner/) *(30 min)*
3. [Common Security Patterns](../by-use-case/web-application/) *(20 min)*

**Your 30-day goal:** Understand security fundamentals and write your first custom rule.

---

### Mostly B's: **🟡 Developer Path**

**You're ready to integrate security into your workflow!**

**Start here:**
1. [Local Development Setup](../configurations/local-dev.md) *(15 min)*
2. [CI/CD Integration](../ci-cd/github-actions/) *(45 min)*
3. [Custom Rules for Your Stack](../rules/by-technology/) *(30 min)*

**Your 30-day goal:** Have Riveter running in your development pipeline.

---

### Mostly C's: **🔴 Platform Engineer Path**

**You're ready for advanced implementation!**

**Start here:**
1. [Multi-Team Rule Distribution](../../docs/RULE_PACK_GUIDE.md) *(30 min)*
2. [Custom Rule Packs](../advanced/custom-rule-packs/) *(60 min)*
3. [Multi-Cloud Governance](../../docs/MULTI_CLOUD_GUIDE.md) *(45 min)*

**Your 30-day goal:** Deploy standardized policies across multiple teams.

---

### Mostly D's: **🔵 Compliance Officer Path**

**You need enterprise governance and reporting!**

**Start here:**
1. [Compliance Framework Mapping](../../docs/COMPLIANCE_MAPPINGS.md) *(20 min)*
2. [Audit Report Generation](../../docs/MONITORING_GUIDE.md#audit-reports) *(30 min)*
3. [Continuous Compliance Monitoring](../advanced/continuous-compliance/) *(45 min)*

**Your 30-day goal:** Automated compliance monitoring and reporting.

---

## 🚀 Quick Start Commands for Your Path

### Beginner Commands
```bash
# Start with basic security scanning
riveter scan -p aws-security -t examples/basic/
riveter explain-rule ec2_no_public_ip
riveter list-rule-packs
```

### Developer Commands
```bash
# Set up local development
riveter init --local-dev
riveter scan --pre-commit-hook
riveter validate --fix-suggestions
```

### Platform Engineer Commands
```bash
# Multi-team setup
riveter create-rule-pack --template enterprise
riveter distribute-rules --teams all
riveter scan --multi-cloud --report-format json
```

### Compliance Officer Commands
```bash
# Compliance and reporting
riveter scan --compliance-report --framework soc2
riveter audit-trail --date-range 30d
riveter generate-evidence --regulation hipaa
```

---

## 📈 Progress Tracking

**Check off your achievements as you learn:**

### Week 1: Foundation
- [ ] Completed quick start tutorial
- [ ] Successfully scanned first infrastructure
- [ ] Understood the difference between secure and insecure configurations

### Week 2: Integration
- [ ] Set up Riveter in development environment
- [ ] Created first custom rule
- [ ] Integrated with CI/CD pipeline

### Week 3: Customization
- [ ] Built organization-specific rule pack
- [ ] Configured environment-specific rules
- [ ] Set up automated reporting

### Week 4: Mastery
- [ ] Deployed across multiple teams/environments
- [ ] Implemented governance policies
- [ ] Achieved compliance monitoring goals

**🏆 Congratulations!** You're now a Riveter expert ready to help others on their journey.

---

## 🤝 Get Help & Share Progress

- **Questions?** [Join our community discussions](https://github.com/scottryanhoward/riveter/discussions)
- **Stuck?** [Check our troubleshooting guide](../../docs/TROUBLESHOOTING.md)
- **Success story?** [Share it with the community](https://github.com/scottryanhoward/riveter/discussions/categories/show-and-tell)

**Remember:** Everyone starts somewhere. The Riveter community is here to help you succeed!
