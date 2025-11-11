# Rule Packs Guide

Rule packs are collections of pre-built rules that implement common compliance frameworks and security best practices. This guide helps you choose and use the right rule packs for your needs.

## Quick Rule Pack Selection

### By Use Case

| Use Case | Recommended Rule Packs | Command |
|----------|------------------------|---------|
| **Startup/Small Team** | Basic security | `riveter scan -p aws-security -t main.tf` |
| **Enterprise** | Comprehensive | `riveter scan -p aws-security -p cis-aws -p soc2-security -t main.tf` |
| **Healthcare** | HIPAA compliance | `riveter scan -p aws-hipaa -p azure-hipaa -t main.tf` |
| **Financial Services** | PCI-DSS compliance | `riveter scan -p aws-pci-dss -p soc2-security -t main.tf` |
| **Multi-Cloud** | Cross-platform | `riveter scan -p multi-cloud-security -t main.tf` |

### By Cloud Provider

| Provider | Security | CIS Benchmark | Well-Architected | Compliance |
|----------|----------|---------------|-------------------|------------|
| **AWS** | aws-security (26 rules) | cis-aws (22 rules) | aws-well-architected (34 rules) | aws-hipaa, aws-pci-dss |
| **Azure** | azure-security (28 rules) | cis-azure (34 rules) | azure-well-architected (35 rules) | azure-hipaa |
| **GCP** | gcp-security (29 rules) | cis-gcp (43 rules) | gcp-well-architected (30 rules) | Coming soon |

## Available Rule Packs

### Cloud Security Best Practices
- **aws-security** - AWS Security Best Practices (26 rules)
- **azure-security** - Azure Security Best Practices (28 rules)
- **gcp-security** - GCP Security Best Practices (29 rules)
- **multi-cloud-security** - Multi-Cloud Security Patterns (40 rules)

### CIS Benchmarks
- **cis-aws** - CIS AWS Foundations Benchmark v1.4.0 (22 rules)
- **cis-azure** - CIS Azure Foundations Benchmark v1.3.0 (34 rules)
- **cis-gcp** - CIS GCP Foundations Benchmark v1.3.0 (43 rules)

### Well-Architected Frameworks
- **aws-well-architected** - AWS Well-Architected Framework (34 rules)
- **azure-well-architected** - Azure Well-Architected Framework (35 rules)
- **gcp-well-architected** - GCP Architecture Framework (30 rules)

### Compliance Standards
- **aws-hipaa** - AWS HIPAA Compliance (35 rules)
- **azure-hipaa** - Azure HIPAA Compliance (30 rules)
- **aws-pci-dss** - AWS PCI-DSS Compliance (40 rules)
- **soc2-security** - SOC 2 Security Trust Service Criteria (28 rules)

### Container & Kubernetes
- **kubernetes-security** - Kubernetes Security (40 rules)

## Rule Pack Commands

```bash
# List all available rule packs
riveter list-rule-packs

# Use a single rule pack
riveter scan -p aws-security -t main.tf

# Combine multiple rule packs
riveter scan -p aws-security -p cis-aws -p soc2-security -t main.tf

# Combine with custom rules
riveter scan -r custom-rules.yml -p aws-security -t main.tf

# Different output formats
riveter scan -p aws-security -t main.tf --output-format json
riveter scan -p aws-security -t main.tf --output-format sarif
```

## Choosing the Right Combination

### Decision Tree

1. **What's your primary goal?**
   - Security → Use security rule packs (aws-security, azure-security, etc.)
   - Compliance → Use compliance rule packs (cis-aws, aws-hipaa, etc.)
   - Architecture → Use well-architected rule packs

2. **Which cloud provider(s)?**
   - Single cloud → Use provider-specific packs
   - Multi-cloud → Add multi-cloud-security pack

3. **What's your compliance requirement?**
   - Healthcare → Add HIPAA packs
   - Financial → Add PCI-DSS packs
   - General → Add CIS benchmarks

4. **Do you use Kubernetes?**
   - Yes → Add kubernetes-security pack

### Example Combinations

#### Startup AWS Environment
```bash
riveter scan -p aws-security -p cis-aws -t main.tf
```

#### Enterprise Multi-Cloud
```bash
riveter scan -p aws-security -p azure-security -p gcp-security -p multi-cloud-security -p soc2-security -t main.tf
```

#### Healthcare Compliance
```bash
riveter scan -p aws-hipaa -p azure-hipaa -p aws-security -p cis-aws -t main.tf
```

#### Financial Services
```bash
riveter scan -p aws-pci-dss -p soc2-security -p aws-security -p cis-aws -t main.tf
```

## Performance Considerations

| Rule Pack Size | Validation Time | Memory Usage | Best For |
|----------------|-----------------|--------------|----------|
| Single pack (20-30 rules) | 2-3 seconds | ~50MB | Development, quick checks |
| Dual pack (40-50 rules) | 4-5 seconds | ~75MB | Standard validation |
| Triple pack (60-80 rules) | 6-8 seconds | ~100MB | Comprehensive validation |
| Full compliance (100+ rules) | 10-15 seconds | ~150MB | Production, audit |

## Creating Custom Rule Packs

```bash
# Generate a template
riveter create-rule-pack-template company-standards company-rules.yml

# Validate your rule pack
riveter validate-rule-pack company-rules.yml

# Use your custom rule pack
riveter scan -p company-standards -t main.tf
```

## Next Steps

- **[Visual Guides](visual-guides.md)** - See rule pack coverage comparisons
- **[Troubleshooting](troubleshooting.md)** - Fix rule pack issues
- **[CI/CD Integration](../developer/cicd.md)** - Use rule packs in pipelines
