# CI/CD Integration Examples

This directory contains comprehensive CI/CD pipeline examples for integrating Riveter's multi-cloud rule packs into your development workflow.

## Available Examples

### GitHub Actions
- **[github-actions-multi-cloud.yml](github-actions-multi-cloud.yml)**: Complete multi-cloud validation workflow
  - Parallel validation across AWS, Azure, and GCP
  - Kubernetes security validation
  - Compliance validation (HIPAA, PCI-DSS)
  - SARIF integration for security dashboards
  - Artifact management and reporting

### GitLab CI
- **[gitlab-ci-multi-cloud.yml](gitlab-ci-multi-cloud.yml)**: GitLab CI pipeline for multi-cloud infrastructure
  - Environment-specific validation rules
  - Compliance reporting and dashboards
  - Artifact caching and management
  - Security dashboard integration

### Jenkins
- **[jenkins-multi-cloud.groovy](jenkins-multi-cloud.groovy)**: Jenkins pipeline for enterprise environments
  - Parameterized builds for different environments
  - Parallel execution across cloud providers
  - Comprehensive reporting and notifications
  - Integration with Slack and other tools

## Quick Start

### GitHub Actions Setup

1. **Copy the workflow file**:
```bash
mkdir -p .github/workflows
cp examples/cicd/github-actions-multi-cloud.yml .github/workflows/
```

2. **Organize your infrastructure**:
```
infrastructure/
├── aws/
├── gcp/
├── azure/
├── k8s/
├── healthcare/  # For HIPAA compliance
└── payments/    # For PCI-DSS compliance
```

3. **Commit and push** - the workflow will automatically run on changes to infrastructure files.

### GitLab CI Setup

1. **Copy the pipeline file**:
```bash
cp examples/cicd/gitlab-ci-multi-cloud.yml .gitlab-ci.yml
```

2. **Configure GitLab variables** (if needed):
   - `RIVETER_VERSION`: Specific Riveter version (optional)
   - `PYTHON_VERSION`: Python version to use (optional)

3. **Push to GitLab** - the pipeline will run automatically.

### Jenkins Setup

1. **Create a new Pipeline job** in Jenkins
2. **Copy the pipeline script** from `jenkins-multi-cloud.groovy`
3. **Configure parameters**:
   - `ENVIRONMENT`: Target environment
   - `VALIDATE_COMPLIANCE`: Enable compliance validation
   - `VALIDATE_KUBERNETES`: Enable Kubernetes validation
4. **Set up notifications** (Slack, email, etc.)

## Pipeline Features

### Multi-Cloud Validation

All pipelines support validation across:
- **AWS**: Security, CIS compliance, Well-Architected Framework
- **GCP**: Security, CIS compliance, Well-Architected Framework
- **Azure**: Security, CIS compliance, Well-Architected Framework
- **Multi-Cloud**: Common security patterns across all providers

### Compliance Standards

- **SOC 2**: General enterprise compliance
- **HIPAA**: Healthcare data protection (AWS, Azure)
- **PCI-DSS**: Payment card industry compliance (AWS)

### Container Security

- **Kubernetes**: General container security
- **EKS**: AWS-specific Kubernetes security
- **AKS**: Azure-specific Kubernetes security
- **GKE**: GCP-specific Kubernetes security

### Environment-Specific Rules

#### Development
```bash
# Relaxed validation with warnings
riveter scan -p multi-cloud-security -t dev/ --severity warning
```

#### Staging
```bash
# Standard security validation
riveter scan -p multi-cloud-security -p soc2-security -t staging/
```

#### Production
```bash
# Comprehensive validation with all rule packs
riveter scan -p aws-security -p gcp-security -p azure-security \
             -p cis-aws -p cis-gcp -p cis-azure \
             -p aws-well-architected -p gcp-well-architected -p azure-well-architected \
             -t production/
```

## Output Formats

### SARIF (Security Analysis Results Interchange Format)
- **Use case**: Security dashboards, GitHub Security tab
- **Example**: `riveter scan -p aws-security -t main.tf --output-format sarif`
- **Integration**: GitHub Advanced Security, Azure DevOps Security

### JUnit XML
- **Use case**: Test reporting, CI/CD integration
- **Example**: `riveter scan -p cis-aws -t main.tf --output-format junit`
- **Integration**: Jenkins, GitLab CI, GitHub Actions test reporting

### JSON
- **Use case**: Programmatic processing, custom dashboards
- **Example**: `riveter scan -p multi-cloud-security -t main.tf --output-format json`
- **Integration**: Custom reporting tools, metrics collection

### Table (Default)
- **Use case**: Human-readable terminal output
- **Example**: `riveter scan -p aws-security -t main.tf`
- **Integration**: Local development, debugging

## Advanced Configuration

### Conditional Validation

#### Path-Based Triggers
```yaml
# GitHub Actions
on:
  push:
    paths:
      - 'infrastructure/aws/**'
      - 'infrastructure/gcp/**'
      - 'infrastructure/azure/**'
```

```yaml
# GitLab CI
rules:
  - changes:
      - infrastructure/aws/**/*
      - infrastructure/gcp/**/*
```

#### Branch-Based Rules
```yaml
# Production validation only on main branch
- if: '$CI_COMMIT_BRANCH == "main"'
  changes:
    - infrastructure/production/**/*
```

### Parallel Execution

#### GitHub Actions
```yaml
jobs:
  validate-aws:
    # AWS validation
  validate-gcp:
    # GCP validation (runs in parallel)
  validate-azure:
    # Azure validation (runs in parallel)
```

#### GitLab CI
```yaml
validate-aws-security:
  stage: validate-infrastructure
  # Runs in parallel with other jobs in same stage

validate-gcp-security:
  stage: validate-infrastructure
  # Runs in parallel
```

#### Jenkins
```groovy
parallel {
    stage('AWS Validation') {
        // AWS validation steps
    }
    stage('GCP Validation') {
        // GCP validation steps
    }
    stage('Azure Validation') {
        // Azure validation steps
    }
}
```

### Artifact Management

#### Security Results
```yaml
# Store SARIF files for security dashboards
artifacts:
  paths:
    - "*.sarif"
  expire_in: 1 month
```

#### Test Reports
```yaml
# JUnit XML for test reporting
artifacts:
  reports:
    junit: "*.xml"
```

#### Compliance Reports
```yaml
# Long-term storage for compliance audits
artifacts:
  paths:
    - compliance-report.md
    - compliance-summary.json
  expire_in: 1 year
```

## Integration Examples

### Slack Notifications

#### Jenkins
```groovy
post {
    success {
        slackSend(
            channel: '#infrastructure',
            color: 'good',
            message: "✅ Infrastructure validation passed"
        )
    }
    failure {
        slackSend(
            channel: '#infrastructure',
            color: 'danger',
            message: "❌ Infrastructure validation failed"
        )
    }
}
```

#### GitHub Actions
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    channel: '#infrastructure'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Security Dashboard Integration

#### GitHub Security Tab
```yaml
- name: Upload SARIF results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
    category: infrastructure-security
```

#### GitLab Security Dashboard
```yaml
artifacts:
  reports:
    sast: security-results.sarif
```

### Custom Reporting

#### Generate HTML Reports
```bash
# Convert SARIF to HTML
python scripts/sarif-to-html.py results.sarif > security-report.html
```

#### Metrics Collection
```bash
# Extract metrics from JSON results
jq '.summary.total_violations' results.json
```

## Troubleshooting

### Common Issues

#### 1. Rule Pack Not Found
```bash
# Verify rule pack exists
riveter list-rule-packs | grep aws-security

# Check rule pack file
ls riveter/rule_packs/aws-security.yml
```

#### 2. Performance Issues
```bash
# Use targeted scanning
riveter scan -p aws-security -t infrastructure/aws/compute/

# Parallel execution in CI/CD
# Split validation across multiple jobs
```

#### 3. False Positives
```bash
# Use filtering to exclude specific rules
riveter scan -p aws-security -t main.tf --exclude-rules "rule_id_1,rule_id_2"

# Adjust severity levels
riveter scan -p aws-security -t main.tf --severity error
```

### Debugging

#### Verbose Output
```bash
# Enable verbose logging
riveter scan -p aws-security -t main.tf --verbose
```

#### Rule Validation
```bash
# Validate rule pack syntax
riveter validate-rule-pack rule_packs/aws-security.yml
```

#### Dry Run
```bash
# Test without actual validation
riveter scan -p aws-security -t main.tf --dry-run
```

## Best Practices

### 1. Progressive Adoption
- Start with basic security rule packs
- Add compliance frameworks gradually
- Implement environment-specific rules

### 2. Performance Optimization
- Use path-based triggers to limit scope
- Implement parallel execution
- Cache dependencies between runs

### 3. Security Integration
- Upload SARIF results to security dashboards
- Set up automated notifications for failures
- Integrate with vulnerability management tools

### 4. Compliance Management
- Store compliance reports for audit purposes
- Implement approval workflows for production
- Regular review and updates of rule packs

### 5. Team Collaboration
- Clear documentation of validation requirements
- Shared responsibility for infrastructure security
- Regular training on new rule packs and features

## Migration from Existing Pipelines

### From Basic AWS Validation
```yaml
# Before
- run: riveter scan -p aws-security -t main.tf

# After
- run: riveter scan -p aws-security -p cis-aws -p aws-well-architected -t aws/
```

### Adding Multi-Cloud Support
```yaml
# Add parallel validation for multiple clouds
jobs:
  validate-aws:
    run: riveter scan -p aws-security -t aws/
  validate-gcp:
    run: riveter scan -p gcp-security -t gcp/
  validate-azure:
    run: riveter scan -p azure-security -t azure/
```

### Compliance Integration
```yaml
# Add compliance validation
- run: riveter scan -p aws-hipaa -t healthcare/
- run: riveter scan -p aws-pci-dss -t payments/
```

For more detailed examples and customization options, refer to the individual pipeline files and the main Riveter documentation.
