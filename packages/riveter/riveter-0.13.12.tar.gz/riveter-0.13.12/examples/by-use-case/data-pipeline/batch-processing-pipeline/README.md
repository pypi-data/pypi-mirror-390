# Batch Processing Data Pipeline

**Estimated Time**: 40 minutes
**Complexity**: Intermediate
**Prerequisites**: Completed beginner examples, ETL concepts, AWS data services

## What You'll Learn

- Understand data pipeline security and compliance validation
- Learn data governance rule patterns
- Practice ETL workflow validation strategies
- Understand data encryption and access control validation

## Architecture Overview

This example demonstrates a secure, compliant batch processing pipeline:

```
Raw Data (S3) → Lambda Trigger → Glue ETL Job → Processed Data (S3)
      ↓              ↓              ↓              ↓
   Encrypted    IAM Roles    Job Monitoring   Data Catalog
```

### Pipeline Components

1. **Data Ingestion**: S3 buckets with encryption and lifecycle policies
2. **Processing Trigger**: Lambda function with proper IAM permissions
3. **ETL Processing**: AWS Glue jobs with security configurations
4. **Data Catalog**: Glue Data Catalog with metadata management
5. **Monitoring**: CloudWatch logs and metrics for pipeline observability

## Files Included

- `main.tf` - Main configuration and provider setup
- `storage.tf` - S3 buckets and data storage configuration
- `processing.tf` - Lambda functions and Glue jobs
- `iam.tf` - IAM roles and policies for secure access
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `data-security-rules.yml` - Data encryption and access validation
- `compliance-rules.yml` - Compliance and governance validation
- `pipeline-rules.yml` - Pipeline workflow and monitoring validation

## Step-by-Step Walkthrough

### Step 1: Examine the Data Storage Architecture (10 minutes)

Review `storage.tf` to understand data security:

```hcl
# Raw data bucket with encryption
resource "aws_s3_bucket" "raw_data" {
  bucket = "${var.project_name}-raw-data-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.data_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Lifecycle policy for data retention
resource "aws_s3_bucket_lifecycle_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  rule {
    id     = "data_retention"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}
```

### Step 2: Understand Processing Security (10 minutes)

Review `processing.tf` and `iam.tf` for secure processing:

```hcl
# Lambda function with proper IAM role
resource "aws_lambda_function" "data_processor" {
  filename         = "data_processor.zip"
  function_name    = "${var.project_name}-data-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "python3.9"

  environment {
    variables = {
      GLUE_JOB_NAME = aws_glue_job.etl_job.name
      KMS_KEY_ID    = aws_kms_key.data_key.arn
    }
  }
}

# Glue job with security configuration
resource "aws_glue_job" "etl_job" {
  name         = "${var.project_name}-etl-job"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "3.0"

  command {
    script_location = "s3://${aws_s3_bucket.scripts.bucket}/etl_script.py"
    python_version  = "3"
  }

  default_arguments = {
    "--enable-metrics"                = ""
    "--enable-continuous-cloudwatch-log" = "true"
    "--job-language"                  = "python"
    "--TempDir"                      = "s3://${aws_s3_bucket.temp.bucket}/temp/"
  }

  security_configuration = aws_glue_security_configuration.etl_security.name
}
```

### Step 3: Review Security Validation Rules (15 minutes)

#### Data Security Rules (`data-security-rules.yml`)
```yaml
rules:
  - name: "S3 buckets must use KMS encryption"
    resource_type: "aws_s3_bucket_server_side_encryption_configuration"
    assertions:
      - key: "rule.0.apply_server_side_encryption_by_default.0.sse_algorithm"
        operator: "equals"
        value: "aws:kms"
      - key: "rule.0.apply_server_side_encryption_by_default.0.kms_master_key_id"
        operator: "exists"

  - name: "Data buckets must have lifecycle policies"
    resource_type: "aws_s3_bucket_lifecycle_configuration"
    assertions:
      - key: "rule.0.status"
        operator: "equals"
        value: "Enabled"
      - key: "rule.0.transition"
        operator: "exists"
```

#### Compliance Rules (`compliance-rules.yml`)
```yaml
rules:
  - name: "IAM roles must have least privilege policies"
    resource_type: "aws_iam_role_policy"
    assertions:
      - key: "policy"
        operator: "not_contains"
        value: '"*"'
        message: "IAM policies should not use wildcard permissions"

  - name: "Lambda functions must have CloudWatch logging"
    resource_type: "aws_lambda_function"
    assertions:
      - key: "environment.0.variables.LOG_LEVEL"
        operator: "exists"
        message: "Lambda functions must have logging configured"
```

#### Pipeline Rules (`pipeline-rules.yml`)
```yaml
rules:
  - name: "Glue jobs must have security configuration"
    resource_type: "aws_glue_job"
    assertions:
      - key: "security_configuration"
        operator: "exists"
        message: "Glue jobs must use security configuration for encryption"

  - name: "Glue jobs must enable CloudWatch logging"
    resource_type: "aws_glue_job"
    assertions:
      - key: "default_arguments.--enable-continuous-cloudwatch-log"
        operator: "equals"
        value: "true"
```

### Step 4: Run Pipeline Validation (5 minutes)

Execute comprehensive validation:

```bash
# Validate all pipeline components
riveter scan \
  -r data-security-rules.yml \
  -r compliance-rules.yml \
  -r pipeline-rules.yml \
  -t *.tf

# Use compliance rule packs
riveter scan \
  -p aws-security \
  -p soc2-security \
  -t *.tf
```

## Expected Results

### Successful Validation
```
✅ S3 buckets must use KMS encryption (3 resources)
✅ Data buckets must have lifecycle policies (2 resources)
✅ IAM roles must have least privilege policies (4 resources)
✅ Lambda functions must have CloudWatch logging (2 resources)
✅ Glue jobs must have security configuration (1 resource)
✅ Glue jobs must enable CloudWatch logging (1 resource)
✅ KMS keys must have rotation enabled (2 resources)
✅ S3 buckets must block public access (3 resources)

Summary: 18 rules passed, 0 failed
Data pipeline security validation passed!
```

## Data Governance Patterns

### Data Classification
```yaml
- name: "Sensitive data buckets must have additional encryption"
  resource_type: "aws_s3_bucket"
  filters:
    - key: "tags.DataClassification"
      operator: "equals"
      value: "Sensitive"
  assertions:
    - key: "server_side_encryption_configuration.0.rule.0.bucket_key_enabled"
      operator: "equals"
      value: true
```

### Data Retention Compliance
```yaml
- name: "Financial data must have 7-year retention"
  resource_type: "aws_s3_bucket_lifecycle_configuration"
  filters:
    - key: "bucket"
      operator: "matches"
      value: ".*financial.*"
  assertions:
    - key: "rule.0.expiration.0.days"
      operator: "greater_than_or_equal"
      value: 2555  # 7 years
```

### Access Control Validation
```yaml
- name: "Data processing roles must use specific policies"
  resource_type: "aws_iam_role"
  filters:
    - key: "name"
      operator: "matches"
      value: ".*data-processor.*"
  assertions:
    - key: "assume_role_policy"
      operator: "contains"
      value: "lambda.amazonaws.com"
```

## Real-World Scenarios

### GDPR Compliance
- Data encryption at rest and in transit
- Data retention and deletion policies
- Access logging and audit trails
- Data processing consent tracking

### HIPAA Compliance
- PHI data encryption requirements
- Access control and authentication
- Audit logging and monitoring
- Data backup and recovery

### Financial Services (SOX)
- Data integrity validation
- Change management controls
- Segregation of duties
- Audit trail requirements

## Try It Yourself

### Exercise 1: Add Data Quality Validation
Implement Glue Data Quality rules and validate their configuration.

### Exercise 2: Implement Data Lineage
Add AWS Glue DataBrew for data profiling with validation rules.

### Exercise 3: Add Real-time Processing
Extend with Kinesis Data Streams for real-time data processing.

### Exercise 4: Multi-Region Data Replication
Implement cross-region data replication with validation.

## Troubleshooting Guide

### Common Issues

#### KMS Key Access Errors
```
❌ Glue job cannot access KMS key
   Cause: IAM role lacks KMS permissions
   Solution: Add kms:Decrypt and kms:GenerateDataKey permissions
```

#### S3 Lifecycle Policy Conflicts
```
❌ Lifecycle rule validation failed
   Cause: Conflicting transition rules
   Solution: Ensure transition days are in ascending order
```

#### Glue Job Security Configuration
```
❌ Security configuration not found
   Cause: Security configuration not properly referenced
   Solution: Verify security configuration name and region
```

## Next Steps

After completing this example:

1. **Scale Up**: Try [Data Lake Architecture](../data-lake-architecture/) for enterprise-scale data processing
2. **Real-time**: Explore [Real-time Streaming](../real-time-streaming/) for event-driven processing
3. **Compliance**: Study [SOX Financial Services](../../compliance/sox-financial-services/) for regulatory requirements
4. **Automation**: Implement [CI/CD Integration](../../../ci-cd/github-actions/) for pipeline deployment

## Related Examples

- [Real-time Streaming](../real-time-streaming/) - Event-driven data processing
- [Data Lake Architecture](../data-lake-architecture/) - Enterprise data platform
- [HIPAA Healthcare](../../compliance/hipaa-compliant-healthcare/) - Healthcare data compliance
- [SOX Financial](../../compliance/sox-financial-services/) - Financial data governance
