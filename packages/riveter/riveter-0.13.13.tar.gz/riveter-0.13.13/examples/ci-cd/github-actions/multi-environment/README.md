# GitHub Actions Multi-Environment Validation

**Estimated Time**: 35 minutes
**Complexity**: Intermediate
**Prerequisites**: GitHub Actions experience, Terraform workflow knowledge

## What You'll Learn

- Understand CI/CD integration with infrastructure validation
- Learn multi-environment validation strategies
- Practice GitHub Actions workflow development
- Master progressive validation and deployment patterns

## Architecture Overview

This example demonstrates a complete CI/CD pipeline with progressive validation:

```
Pull Request → Development Validation → Staging Validation → Production Validation → Deploy
      ↓              ↓                    ↓                    ↓               ↓
   Basic Rules   Security Rules    Compliance Rules    Final Validation   Monitoring
```

### Validation Strategy

1. **Development**: Fast feedback with basic validation
2. **Staging**: Comprehensive security and compliance validation
3. **Production**: Final validation with strict governance rules
4. **Deployment**: Post-deployment validation and monitoring

## Files Included

- `.github/workflows/infrastructure-validation.yml` - Main workflow file
- `.github/workflows/pull-request-validation.yml` - PR validation workflow
- `environments/dev/main.tf` - Development environment configuration
- `environments/staging/main.tf` - Staging environment configuration
- `environments/prod/main.tf` - Production environment configuration
- `rule-packs/development.yml` - Development validation rules
- `rule-packs/staging.yml` - Staging validation rules (security-focused)
- `rule-packs/production.yml` - Production validation rules (compliance-focused)
- `scripts/validate-environment.sh` - Environment validation script

## Step-by-Step Walkthrough

### Step 1: Examine the Main Workflow (10 minutes)

Review `.github/workflows/infrastructure-validation.yml`:

```yaml
name: Infrastructure Validation and Deployment

on:
  push:
    branches: [main]
    paths: ['environments/**', 'rule-packs/**']
  pull_request:
    branches: [main]
    paths: ['environments/**', 'rule-packs/**']

env:
  TERRAFORM_VERSION: '1.5.0'
  RIVETER_VERSION: 'latest'

jobs:
  # Job 1: Development Environment Validation
  validate-development:
    name: Validate Development Environment
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TERRAFORM_VERSION }}

      - name: Install Riveter
        run: |
          curl -L https://github.com/riveter/riveter/releases/latest/download/riveter-linux-amd64 -o riveter
          chmod +x riveter
          sudo mv riveter /usr/local/bin/

      - name: Terraform Init (Development)
        working-directory: environments/dev
        run: terraform init

      - name: Terraform Plan (Development)
        working-directory: environments/dev
        run: terraform plan -out=tfplan

      - name: Riveter Validation (Development)
        working-directory: environments/dev
        run: |
          riveter scan \
            -r ../../rule-packs/development.yml \
            -t *.tf \
            --output-format json \
            --output-file validation-results.json

      - name: Upload Development Results
        uses: actions/upload-artifact@v3
        with:
          name: dev-validation-results
          path: environments/dev/validation-results.json

  # Job 2: Staging Environment Validation
  validate-staging:
    name: Validate Staging Environment
    runs-on: ubuntu-latest
    needs: validate-development
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TERRAFORM_VERSION }}

      - name: Install Riveter
        run: |
          curl -L https://github.com/riveter/riveter/releases/latest/download/riveter-linux-amd64 -o riveter
          chmod +x riveter
          sudo mv riveter /usr/local/bin/

      - name: Terraform Init (Staging)
        working-directory: environments/staging
        run: terraform init

      - name: Terraform Plan (Staging)
        working-directory: environments/staging
        run: terraform plan -out=tfplan

      - name: Riveter Security Validation (Staging)
        working-directory: environments/staging
        run: |
          riveter scan \
            -r ../../rule-packs/staging.yml \
            -p aws-security \
            -p aws-well-architected \
            -t *.tf \
            --output-format sarif \
            --output-file security-results.sarif

      - name: Upload Security Results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: environments/staging/security-results.sarif

      - name: Deploy to Staging
        working-directory: environments/staging
        run: terraform apply -auto-approve tfplan
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

  # Job 3: Production Environment Validation
  validate-production:
    name: Validate Production Environment
    runs-on: ubuntu-latest
    needs: validate-staging
    environment: production
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TERRAFORM_VERSION }}

      - name: Install Riveter
        run: |
          curl -L https://github.com/riveter/riveter/releases/latest/download/riveter-linux-amd64 -o riveter
          chmod +x riveter
          sudo mv riveter /usr/local/bin/

      - name: Terraform Init (Production)
        working-directory: environments/prod
        run: terraform init

      - name: Terraform Plan (Production)
        working-directory: environments/prod
        run: terraform plan -out=tfplan

      - name: Riveter Compliance Validation (Production)
        working-directory: environments/prod
        run: |
          riveter scan \
            -r ../../rule-packs/production.yml \
            -p aws-security \
            -p soc2-security \
            -p cis-aws \
            -t *.tf \
            --output-format json \
            --output-file compliance-results.json

      - name: Check Compliance Results
        working-directory: environments/prod
        run: |
          # Fail if any critical or high severity issues found
          if jq -e '.results[] | select(.severity == "critical" or .severity == "high")' compliance-results.json > /dev/null; then
            echo "Critical or high severity compliance issues found!"
            jq '.results[] | select(.severity == "critical" or .severity == "high")' compliance-results.json
            exit 1
          fi

      - name: Deploy to Production
        working-directory: environments/prod
        run: terraform apply -auto-approve tfplan
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_PROD_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_PROD_SECRET_ACCESS_KEY }}

      - name: Post-Deployment Validation
        working-directory: environments/prod
        run: |
          # Wait for resources to be ready
          sleep 30

          # Run post-deployment validation
          riveter scan \
            -r ../../rule-packs/production.yml \
            -t *.tf \
            --output-format json \
            --output-file post-deploy-results.json

      - name: Upload Production Results
        uses: actions/upload-artifact@v3
        with:
          name: prod-validation-results
          path: environments/prod/compliance-results.json
```

### Step 2: Understand Environment-Specific Rules (10 minutes)

#### Development Rules (`rule-packs/development.yml`)
```yaml
# Fast feedback rules for development environment
rules:
  - name: "Basic resource naming convention"
    resource_type: "aws_s3_bucket"
    assertions:
      - key: "bucket"
        operator: "matches"
        value: "^dev-.*"

  - name: "Development resources must have environment tag"
    resource_type: "*"
    assertions:
      - key: "tags.Environment"
        operator: "equals"
        value: "development"

  - name: "Cost optimization for development"
    resource_type: "aws_instance"
    assertions:
      - key: "instance_type"
        operator: "in"
        value: ["t3.micro", "t3.small", "t3.medium"]
```

#### Staging Rules (`rule-packs/staging.yml`)
```yaml
# Security-focused rules for staging environment
rules:
  - name: "S3 buckets must have encryption enabled"
    resource_type: "aws_s3_bucket_server_side_encryption_configuration"
    severity: "high"
    assertions:
      - key: "rule.0.apply_server_side_encryption_by_default.0.sse_algorithm"
        operator: "in"
        value: ["AES256", "aws:kms"]

  - name: "Security groups must not allow unrestricted access"
    resource_type: "aws_security_group_rule"
    severity: "critical"
    filters:
      - key: "type"
        operator: "equals"
        value: "ingress"
    assertions:
      - key: "cidr_blocks"
        operator: "not_contains"
        value: "0.0.0.0/0"

  - name: "RDS instances must have encryption enabled"
    resource_type: "aws_db_instance"
    severity: "high"
    assertions:
      - key: "storage_encrypted"
        operator: "equals"
        value: true

  - name: "Load balancers must use HTTPS"
    resource_type: "aws_lb_listener"
    severity: "high"
    assertions:
      - key: "protocol"
        operator: "equals"
        value: "HTTPS"
```

#### Production Rules (`rule-packs/production.yml`)
```yaml
# Comprehensive compliance rules for production
rules:
  - name: "All resources must have required tags"
    resource_type: "*"
    severity: "medium"
    assertions:
      - key: "tags.Environment"
        operator: "exists"
      - key: "tags.Owner"
        operator: "exists"
      - key: "tags.CostCenter"
        operator: "exists"
      - key: "tags.DataClassification"
        operator: "exists"

  - name: "Production S3 buckets must use KMS encryption"
    resource_type: "aws_s3_bucket_server_side_encryption_configuration"
    severity: "critical"
    assertions:
      - key: "rule.0.apply_server_side_encryption_by_default.0.sse_algorithm"
        operator: "equals"
        value: "aws:kms"
      - key: "rule.0.apply_server_side_encryption_by_default.0.kms_master_key_id"
        operator: "exists"

  - name: "Production databases must have backup retention"
    resource_type: "aws_db_instance"
    severity: "high"
    assertions:
      - key: "backup_retention_period"
        operator: "greater_than_or_equal"
        value: 7
      - key: "backup_window"
        operator: "exists"

  - name: "Production instances must use approved AMIs"
    resource_type: "aws_instance"
    severity: "high"
    assertions:
      - key: "ami"
        operator: "matches"
        value: "^ami-[0-9a-f]{8,17}$"
      - key: "tags.AMIApproved"
        operator: "equals"
        value: "true"

  - name: "CloudTrail must be enabled for audit compliance"
    resource_type: "aws_cloudtrail"
    severity: "critical"
    assertions:
      - key: "enable_logging"
        operator: "equals"
        value: true
      - key: "include_global_service_events"
        operator: "equals"
        value: true
      - key: "is_multi_region_trail"
        operator: "equals"
        value: true
```

### Step 3: Examine Pull Request Validation (10 minutes)

Review `.github/workflows/pull-request-validation.yml`:

```yaml
name: Pull Request Validation

on:
  pull_request:
    branches: [main]
    paths: ['environments/**', 'rule-packs/**']

jobs:
  validate-changes:
    name: Validate Infrastructure Changes
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: '1.5.0'

      - name: Install Riveter
        run: |
          curl -L https://github.com/riveter/riveter/releases/latest/download/riveter-linux-amd64 -o riveter
          chmod +x riveter
          sudo mv riveter /usr/local/bin/

      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v39
        with:
          files: |
            environments/**/*.tf
            rule-packs/**/*.yml

      - name: Validate changed environments
        if: steps.changed-files.outputs.any_changed == 'true'
        run: |
          for file in ${{ steps.changed-files.outputs.all_changed_files }}; do
            if [[ $file == environments/*/main.tf ]]; then
              env_dir=$(dirname $file)
              echo "Validating environment: $env_dir"

              cd $env_dir
              terraform init
              terraform validate
              terraform plan -out=tfplan

              # Determine which rule pack to use based on environment
              if [[ $env_dir == *"dev"* ]]; then
                rule_pack="../../rule-packs/development.yml"
              elif [[ $env_dir == *"staging"* ]]; then
                rule_pack="../../rule-packs/staging.yml"
              elif [[ $env_dir == *"prod"* ]]; then
                rule_pack="../../rule-packs/production.yml"
              fi

              # Run Riveter validation
              riveter scan -r $rule_pack -t *.tf --output-format json --output-file validation-results.json

              # Check for failures
              if jq -e '.summary.failed > 0' validation-results.json > /dev/null; then
                echo "Validation failed for $env_dir"
                jq '.results[] | select(.status == "FAIL")' validation-results.json
                exit 1
              fi

              cd - > /dev/null
            fi
          done

      - name: Comment PR with results
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const path = require('path');

            // Find all validation result files
            const findValidationFiles = (dir) => {
              const files = [];
              if (fs.existsSync(dir)) {
                const items = fs.readdirSync(dir, { withFileTypes: true });
                for (const item of items) {
                  if (item.isDirectory()) {
                    files.push(...findValidationFiles(path.join(dir, item.name)));
                  } else if (item.name === 'validation-results.json') {
                    files.push(path.join(dir, item.name));
                  }
                }
              }
              return files;
            };

            const validationFiles = findValidationFiles('environments');
            let comment = '## 🔍 Infrastructure Validation Results\n\n';

            for (const file of validationFiles) {
              const results = JSON.parse(fs.readFileSync(file, 'utf8'));
              const envName = path.dirname(file).split('/').pop();

              comment += `### ${envName.toUpperCase()} Environment\n`;
              comment += `- ✅ Passed: ${results.summary.passed}\n`;
              comment += `- ❌ Failed: ${results.summary.failed}\n`;

              if (results.summary.failed > 0) {
                comment += '\n**Failed Rules:**\n';
                results.results.filter(r => r.status === 'FAIL').forEach(rule => {
                  comment += `- ❌ ${rule.name}: ${rule.message}\n`;
                });
              }
              comment += '\n';
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Step 4: Test the Complete Workflow (5 minutes)

Set up the workflow in your repository:

1. **Create the workflow files** in `.github/workflows/`
2. **Set up repository secrets** for AWS credentials
3. **Configure branch protection rules** to require validation
4. **Create a test PR** to trigger validation

## Expected Results

### Successful Pull Request Validation
```
🔍 Infrastructure Validation Results

### DEV Environment
- ✅ Passed: 5
- ❌ Failed: 0

### STAGING Environment
- ✅ Passed: 12
- ❌ Failed: 0

All validations passed! ✅
```

### Failed Validation Example
```
🔍 Infrastructure Validation Results

### STAGING Environment
- ✅ Passed: 10
- ❌ Failed: 2

**Failed Rules:**
- ❌ S3 buckets must have encryption enabled: Bucket 'staging-data' missing encryption configuration
- ❌ Security groups must not allow unrestricted access: Security group 'web-sg' allows 0.0.0.0/0 on port 22
```

## Advanced Workflow Features

### Conditional Validation
```yaml
- name: Skip validation for documentation changes
  if: |
    !contains(steps.changed-files.outputs.all_changed_files, '.tf') &&
    !contains(steps.changed-files.outputs.all_changed_files, '.yml')
  run: echo "No infrastructure changes detected, skipping validation"
```

### Parallel Environment Validation
```yaml
strategy:
  matrix:
    environment: [dev, staging, prod]
  fail-fast: false

steps:
  - name: Validate ${{ matrix.environment }}
    working-directory: environments/${{ matrix.environment }}
    run: |
      terraform init
      terraform plan -out=tfplan
      riveter scan -r ../../rule-packs/${{ matrix.environment }}.yml -t *.tf
```

### Integration with External Tools
```yaml
- name: Run Checkov for additional validation
  run: |
    pip install checkov
    checkov -d environments/ --framework terraform --output sarif --output-file checkov-results.sarif

- name: Compare Riveter and Checkov results
  run: |
    # Custom script to compare and merge results
    python scripts/merge-validation-results.py \
      --riveter validation-results.json \
      --checkov checkov-results.sarif \
      --output merged-results.json
```

## Troubleshooting Guide

### Common Issues

#### Workflow Permission Errors
```yaml
permissions:
  contents: read
  security-events: write  # For SARIF upload
  pull-requests: write    # For PR comments
```

#### Terraform State Management
```yaml
- name: Configure Terraform Backend
  run: |
    cat > backend.tf << EOF
    terraform {
      backend "s3" {
        bucket = "${{ secrets.TERRAFORM_STATE_BUCKET }}"
        key    = "environments/${{ matrix.environment }}/terraform.tfstate"
        region = "us-east-1"
      }
    }
    EOF
```

#### Riveter Installation Issues
```yaml
- name: Install Riveter with retry
  run: |
    for i in {1..3}; do
      if curl -L https://github.com/riveter/riveter/releases/latest/download/riveter-linux-amd64 -o riveter; then
        chmod +x riveter
        sudo mv riveter /usr/local/bin/
        break
      fi
      sleep 5
    done
```

## Best Practices

### Security
- Use GitHub secrets for sensitive data
- Implement least-privilege access
- Audit workflow execution logs
- Use environment protection rules

### Performance
- Cache Terraform providers and modules
- Use matrix strategies for parallel execution
- Implement smart triggering based on file changes
- Optimize rule pack loading

### Maintainability
- Use reusable workflows for common patterns
- Implement proper error handling and retries
- Document workflow requirements and setup
- Version control rule packs and configurations

## Next Steps

After completing this example:

1. **Security**: Explore [Security Scanning](../security-scanning/) for comprehensive security validation
2. **Enterprise**: Try [Jenkins Enterprise Security](../../jenkins/enterprise-security/) for enterprise patterns
3. **Compliance**: Study [Compliance Automation](../../by-use-case/compliance/) for regulatory requirements
4. **Multi-Cloud**: Implement [Multi-Cloud Deployment](../multi-cloud-deployment/) for cross-cloud validation

## Related Examples

- [Basic Validation](../basic-validation/) - Simple GitHub Actions integration
- [Security Scanning](../security-scanning/) - Comprehensive security validation
- [GitLab CI Pipeline](../../gitlab-ci/pipeline-validation/) - GitLab alternative
- [Jenkins Enterprise](../../jenkins/enterprise-security/) - Enterprise CI/CD patterns
