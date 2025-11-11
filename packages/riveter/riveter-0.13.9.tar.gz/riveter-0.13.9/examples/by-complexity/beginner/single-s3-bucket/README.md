# Single S3 Bucket Validation

**Estimated Time**: 10 minutes
**Complexity**: Beginner
**Prerequisites**: Basic Terraform knowledge, AWS S3 concepts

## What You'll Learn

- Understand basic Riveter validation workflow
- Learn rule syntax for resource properties
- Practice running validations and reading results
- Understand pass/fail validation outcomes

## Overview

This example demonstrates the fundamentals of Riveter validation using a simple S3 bucket configuration. You'll learn how to write basic rules, run validations, and interpret results.

## Files Included

- `main.tf` - Simple S3 bucket configuration
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `s3-security-rules.yml` - Basic security validation rules
- `expected-output.txt` - What successful validation looks like

## Step-by-Step Walkthrough

### Step 1: Examine the Terraform Configuration (2 minutes)

Look at `main.tf` to understand the S3 bucket we're validating:

```hcl
resource "aws_s3_bucket" "example" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "example" {
  bucket = aws_s3_bucket.example.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

### Step 2: Examine the Validation Rules (3 minutes)

Look at `s3-security-rules.yml` to understand what we're validating:

```yaml
rules:
  - name: "S3 bucket must have versioning enabled"
    resource_type: "aws_s3_bucket_versioning"
    assertions:
      - key: "versioning_configuration.0.status"
        operator: "equals"
        value: "Enabled"

  - name: "S3 bucket must have encryption enabled"
    resource_type: "aws_s3_bucket_server_side_encryption_configuration"
    assertions:
      - key: "rule.0.apply_server_side_encryption_by_default.0.sse_algorithm"
        operator: "in"
        value: ["AES256", "aws:kms"]
```

### Step 3: Run the Validation (2 minutes)

Execute Riveter to validate the configuration:

```bash
# Run validation with our custom rules
riveter scan -r s3-security-rules.yml -t main.tf

# Expected output: All validations should pass
```

### Step 4: Experiment with Failures (3 minutes)

Modify the configuration to see validation failures:

1. Comment out the versioning configuration in `main.tf`
2. Run validation again: `riveter scan -r s3-security-rules.yml -t main.tf`
3. Observe the failure message and understand why it failed
4. Restore the configuration to make it pass again

## Expected Results

### Successful Validation
```
✅ S3 bucket must have versioning enabled
✅ S3 bucket must have encryption enabled

Summary: 2 rules passed, 0 failed
```

### Failed Validation (when versioning is disabled)
```
❌ S3 bucket must have versioning enabled
   Resource: aws_s3_bucket_versioning.example
   Expected: versioning_configuration.0.status equals "Enabled"
   Actual: versioning_configuration.0.status is "Suspended"

✅ S3 bucket must have encryption enabled

Summary: 1 rule passed, 1 failed
```

## Try It Yourself

### Experiment 1: Add a New Rule
Add a rule to ensure the bucket name follows a naming convention:

```yaml
- name: "S3 bucket name must follow naming convention"
  resource_type: "aws_s3_bucket"
  assertions:
    - key: "bucket"
      operator: "matches"
      value: "^[a-z0-9][a-z0-9-]*[a-z0-9]$"
```

### Experiment 2: Test Different Encryption Methods
Modify the encryption configuration to use KMS and verify the rule still passes.

### Experiment 3: Add Public Access Blocking
Add resources and rules for S3 public access blocking.

## Common Issues and Solutions

### Issue: "No resources found"
**Cause**: Terraform file path incorrect or file doesn't exist
**Solution**: Verify file paths and ensure you're in the correct directory

### Issue: "Rule validation failed"
**Cause**: Rule syntax error or incorrect key path
**Solution**: Check rule syntax against the schema and verify key paths match Terraform resource structure

## Next Steps

After completing this example:

1. **Continue Learning**: Try the [EC2 Security Group example](../ec2-security-group/) to learn about network security validation
2. **Explore Use Cases**: Check out the [Simple Static Site example](../../by-use-case/web-application/simple-static-site/) for a real-world application
3. **Learn More Rules**: Review the [Rule Writing Guide](../../../docs/user/rule-writing.md) for advanced rule syntax

## Related Examples

- [EC2 Security Group](../ec2-security-group/) - Network security validation
- [Basic Networking](../basic-networking/) - Multi-resource validation
- [Simple Static Site](../../by-use-case/web-application/simple-static-site/) - Real-world S3 usage
