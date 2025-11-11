# Multi-Cloud Equivalent Patterns

**Estimated Time**: 75 minutes
**Complexity**: Advanced
**Prerequisites**: Experience with multiple cloud providers, intermediate examples completed

## What You'll Learn

- Understand equivalent patterns across cloud providers
- Learn multi-cloud validation strategies
- Practice cross-cloud security rule development
- Master cloud-agnostic governance patterns

## Architecture Overview

This example demonstrates equivalent infrastructure patterns across AWS, Azure, and GCP:

### Pattern: Secure Object Storage with Web Access

```
AWS:     S3 + CloudFront + Route53
Azure:   Blob Storage + CDN + DNS Zone
GCP:     Cloud Storage + Cloud CDN + Cloud DNS
```

### Pattern: Three-Tier Web Application

```
AWS:     ALB + EC2 Auto Scaling + RDS
Azure:   Load Balancer + VM Scale Sets + SQL Database
GCP:     Load Balancer + Managed Instance Groups + Cloud SQL
```

### Pattern: Container Orchestration

```
AWS:     EKS + ECR + ALB Controller
Azure:   AKS + ACR + Application Gateway
GCP:     GKE + Artifact Registry + Cloud Load Balancing
```

## Files Included

- `aws-implementation.tf` - AWS equivalent implementation
- `azure-implementation.tf` - Azure equivalent implementation
- `gcp-implementation.tf` - GCP equivalent implementation
- `variables.tf` - Cloud-agnostic variables
- `outputs.tf` - Standardized outputs across clouds
- `multi-cloud-security-rules.yml` - Cross-cloud security validation
- `equivalent-pattern-rules.yml` - Pattern equivalency validation
- `migration-validation-rules.yml` - Migration readiness validation

## Step-by-Step Walkthrough

### Step 1: Examine Equivalent Object Storage Patterns (20 minutes)

#### AWS Implementation
```hcl
# S3 bucket with security configuration
resource "aws_s3_bucket" "web_content" {
  bucket = "${var.project_name}-content-${var.environment}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "web_content" {
  bucket = aws_s3_bucket.web_content.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "web_content" {
  bucket = aws_s3_bucket.web_content.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "web_content" {
  origin {
    domain_name = aws_s3_bucket.web_content.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.web_content.bucket}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.web_content.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    target_origin_id       = "S3-${aws_s3_bucket.web_content.bucket}"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  enabled = true
}
```

#### Azure Implementation
```hcl
# Storage account with security configuration
resource "azurerm_storage_account" "web_content" {
  name                     = "${var.project_name}content${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  min_tls_version                = "TLS1_2"
  allow_nested_items_to_be_public = false

  blob_properties {
    delete_retention_policy {
      days = 30
    }
  }
}

resource "azurerm_storage_container" "web_content" {
  name                  = "content"
  storage_account_name  = azurerm_storage_account.web_content.name
  container_access_type = "private"
}

# CDN profile and endpoint
resource "azurerm_cdn_profile" "web_content" {
  name                = "${var.project_name}-cdn-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard_Microsoft"
}

resource "azurerm_cdn_endpoint" "web_content" {
  name                = "${var.project_name}-endpoint-${var.environment}"
  profile_name        = azurerm_cdn_profile.web_content.name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  origin {
    name      = "storage"
    host_name = azurerm_storage_account.web_content.primary_blob_host
  }

  delivery_rule {
    name  = "EnforceHTTPS"
    order = 1

    request_scheme_condition {
      operator     = "Equal"
      match_values = ["HTTP"]
    }

    url_redirect_action {
      redirect_type = "Found"
      protocol      = "Https"
    }
  }
}
```

#### GCP Implementation
```hcl
# Cloud Storage bucket with security configuration
resource "google_storage_bucket" "web_content" {
  name     = "${var.project_name}-content-${var.environment}"
  location = var.gcp_region

  uniform_bucket_level_access = true

  encryption {
    default_kms_key_name = google_kms_crypto_key.storage_key.id
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  versioning {
    enabled = true
  }
}

# Cloud CDN with load balancer
resource "google_compute_backend_bucket" "web_content" {
  name        = "${var.project_name}-backend-${var.environment}"
  bucket_name = google_storage_bucket.web_content.name
  enable_cdn  = true

  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    default_ttl       = 3600
    max_ttl           = 86400
    negative_caching  = true

    negative_caching_policy {
      code = 404
      ttl  = 120
    }
  }
}

resource "google_compute_url_map" "web_content" {
  name            = "${var.project_name}-url-map-${var.environment}"
  default_service = google_compute_backend_bucket.web_content.id
}

resource "google_compute_target_https_proxy" "web_content" {
  name    = "${var.project_name}-https-proxy-${var.environment}"
  url_map = google_compute_url_map.web_content.id

  ssl_certificates = [google_compute_managed_ssl_certificate.web_content.id]
}
```

### Step 2: Understand Cross-Cloud Security Rules (25 minutes)

#### Multi-Cloud Security Rules (`multi-cloud-security-rules.yml`)
```yaml
rules:
  # Object Storage Security (AWS S3)
  - name: "AWS S3 buckets must have encryption enabled"
    resource_type: "aws_s3_bucket_server_side_encryption_configuration"
    assertions:
      - key: "rule.0.apply_server_side_encryption_by_default.0.sse_algorithm"
        operator: "in"
        value: ["AES256", "aws:kms"]

  - name: "AWS S3 buckets must block public access"
    resource_type: "aws_s3_bucket_public_access_block"
    assertions:
      - key: "block_public_acls"
        operator: "equals"
        value: true
      - key: "restrict_public_buckets"
        operator: "equals"
        value: true

  # Object Storage Security (Azure Blob)
  - name: "Azure storage accounts must use minimum TLS 1.2"
    resource_type: "azurerm_storage_account"
    assertions:
      - key: "min_tls_version"
        operator: "equals"
        value: "TLS1_2"

  - name: "Azure storage accounts must not allow public blob access"
    resource_type: "azurerm_storage_account"
    assertions:
      - key: "allow_nested_items_to_be_public"
        operator: "equals"
        value: false

  # Object Storage Security (GCP Cloud Storage)
  - name: "GCP storage buckets must use uniform bucket-level access"
    resource_type: "google_storage_bucket"
    assertions:
      - key: "uniform_bucket_level_access"
        operator: "equals"
        value: true

  - name: "GCP storage buckets must have encryption configured"
    resource_type: "google_storage_bucket"
    assertions:
      - key: "encryption.0.default_kms_key_name"
        operator: "exists"

  # CDN Security (Cross-Cloud)
  - name: "CDN distributions must enforce HTTPS"
    resource_type: "aws_cloudfront_distribution"
    assertions:
      - key: "default_cache_behavior.0.viewer_protocol_policy"
        operator: "in"
        value: ["redirect-to-https", "https-only"]

  - name: "Azure CDN endpoints must enforce HTTPS"
    resource_type: "azurerm_cdn_endpoint"
    assertions:
      - key: "delivery_rule.0.url_redirect_action.0.protocol"
        operator: "equals"
        value: "Https"

  - name: "GCP HTTPS proxies must use SSL certificates"
    resource_type: "google_compute_target_https_proxy"
    assertions:
      - key: "ssl_certificates"
        operator: "not_empty"
```

#### Equivalent Pattern Rules (`equivalent-pattern-rules.yml`)
```yaml
rules:
  # Ensure equivalent security across cloud providers
  - name: "Object storage must have equivalent security controls"
    description: "Validates that object storage has consistent security across clouds"
    multi_cloud_pattern: "object_storage"
    assertions:
      aws:
        - resource_type: "aws_s3_bucket_server_side_encryption_configuration"
          key: "rule.0.apply_server_side_encryption_by_default.0.sse_algorithm"
          operator: "exists"
      azure:
        - resource_type: "azurerm_storage_account"
          key: "min_tls_version"
          operator: "equals"
          value: "TLS1_2"
      gcp:
        - resource_type: "google_storage_bucket"
          key: "encryption.0.default_kms_key_name"
          operator: "exists"

  - name: "CDN must have equivalent HTTPS enforcement"
    description: "Validates consistent HTTPS enforcement across cloud CDN services"
    multi_cloud_pattern: "cdn"
    assertions:
      aws:
        - resource_type: "aws_cloudfront_distribution"
          key: "default_cache_behavior.0.viewer_protocol_policy"
          operator: "in"
          value: ["redirect-to-https", "https-only"]
      azure:
        - resource_type: "azurerm_cdn_endpoint"
          key: "delivery_rule.0.url_redirect_action.0.protocol"
          operator: "equals"
          value: "Https"
      gcp:
        - resource_type: "google_compute_target_https_proxy"
          key: "ssl_certificates"
          operator: "not_empty"
```

### Step 3: Validate Multi-Cloud Patterns (15 minutes)

Execute validation across all cloud implementations:

```bash
# Validate AWS implementation
riveter scan \
  -r multi-cloud-security-rules.yml \
  -r equivalent-pattern-rules.yml \
  -t aws-implementation.tf

# Validate Azure implementation
riveter scan \
  -r multi-cloud-security-rules.yml \
  -r equivalent-pattern-rules.yml \
  -t azure-implementation.tf

# Validate GCP implementation
riveter scan \
  -r multi-cloud-security-rules.yml \
  -r equivalent-pattern-rules.yml \
  -t gcp-implementation.tf

# Validate all implementations together
riveter scan \
  -p multi-cloud-security \
  -t *.tf
```

### Step 4: Test Migration Scenarios (15 minutes)

Use migration validation rules to ensure compatibility:

```yaml
# Migration Validation Rules (migration-validation-rules.yml)
rules:
  - name: "Storage encryption compatibility for migration"
    description: "Ensures storage encryption is compatible across cloud migrations"
    migration_pattern: "storage_migration"
    source_cloud: "aws"
    target_cloud: "azure"
    assertions:
      - source_encryption: "aws:kms"
        target_encryption: "customer_managed_key"
        compatibility: "supported"
      - source_encryption: "AES256"
        target_encryption: "microsoft_managed_key"
        compatibility: "supported"

  - name: "CDN configuration migration compatibility"
    description: "Validates CDN settings can be migrated between clouds"
    migration_pattern: "cdn_migration"
    assertions:
      - feature: "https_enforcement"
        aws_equivalent: "viewer_protocol_policy"
        azure_equivalent: "delivery_rule.url_redirect_action"
        gcp_equivalent: "ssl_certificates"
        compatibility: "full"
```

## Expected Results

### Successful Multi-Cloud Validation
```
AWS Implementation:
✅ AWS S3 buckets must have encryption enabled (1 resource)
✅ AWS S3 buckets must block public access (1 resource)
✅ CDN distributions must enforce HTTPS (1 resource)

Azure Implementation:
✅ Azure storage accounts must use minimum TLS 1.2 (1 resource)
✅ Azure storage accounts must not allow public blob access (1 resource)
✅ Azure CDN endpoints must enforce HTTPS (1 resource)

GCP Implementation:
✅ GCP storage buckets must use uniform bucket-level access (1 resource)
✅ GCP storage buckets must have encryption configured (1 resource)
✅ GCP HTTPS proxies must use SSL certificates (1 resource)

Cross-Cloud Pattern Validation:
✅ Object storage must have equivalent security controls (3 clouds)
✅ CDN must have equivalent HTTPS enforcement (3 clouds)

Summary: 11 rules passed, 0 failed across 3 cloud providers
Multi-cloud security validation passed!
```

## Migration Strategies

### Lift and Shift Migration
```yaml
migration_rules:
  - pattern: "compute_migration"
    source: "aws_instance"
    targets:
      azure: "azurerm_virtual_machine"
      gcp: "google_compute_instance"
    validation:
      - security_groups: "network_security_groups"
      - instance_metadata: "custom_metadata"
      - storage_encryption: "disk_encryption"
```

### Refactoring Migration
```yaml
migration_rules:
  - pattern: "serverless_migration"
    source: "aws_lambda_function"
    targets:
      azure: "azurerm_function_app"
      gcp: "google_cloudfunctions_function"
    validation:
      - runtime_compatibility: "supported_runtimes"
      - environment_variables: "app_settings"
      - iam_permissions: "function_permissions"
```

### Hybrid Cloud Integration
```yaml
hybrid_rules:
  - pattern: "cross_cloud_networking"
    components:
      - aws_vpc_peering_connection
      - azurerm_virtual_network_peering
      - google_compute_network_peering
    validation:
      - cidr_compatibility: "non_overlapping"
      - routing_configuration: "symmetric"
      - security_policies: "consistent"
```

## Real-World Multi-Cloud Scenarios

### Disaster Recovery
- Primary: AWS us-east-1
- Secondary: Azure East US 2
- Tertiary: GCP us-central1
- Validation: Cross-cloud backup and replication

### Compliance Requirements
- Data residency: EU data in Azure Europe
- Processing: AWS for ML workloads
- Analytics: GCP for BigQuery
- Validation: Data sovereignty and compliance

### Cost Optimization
- Compute: Spot instances across all clouds
- Storage: Lifecycle policies for cost tiers
- CDN: Multi-CDN for performance and cost
- Validation: Cost governance rules

## Try It Yourself

### Exercise 1: Add Database Migration Patterns
Implement equivalent database patterns across RDS, SQL Database, and Cloud SQL.

### Exercise 2: Container Orchestration Equivalents
Create equivalent Kubernetes patterns across EKS, AKS, and GKE.

### Exercise 3: Serverless Function Migration
Implement serverless patterns across Lambda, Functions, and Cloud Functions.

### Exercise 4: Identity and Access Management
Create equivalent IAM patterns across AWS IAM, Azure AD, and Cloud IAM.

## Troubleshooting Multi-Cloud Issues

### Common Challenges

#### Provider Configuration Conflicts
```
❌ Multiple provider configurations conflict
   Cause: Provider aliases not properly configured
   Solution: Use provider aliases for multi-cloud deployments
```

#### Resource Naming Conflicts
```
❌ Resource names must be globally unique
   Cause: Cloud-specific naming requirements
   Solution: Use cloud-specific naming conventions
```

#### Cross-Cloud Networking
```
❌ VPC peering across clouds failed
   Cause: Different networking models
   Solution: Use VPN or dedicated connections
```

## Best Practices

### Multi-Cloud Governance
- Standardize tagging across all clouds
- Implement consistent security policies
- Use unified monitoring and logging
- Maintain cloud-agnostic documentation

### Cost Management
- Implement cross-cloud cost allocation
- Use reserved instances strategically
- Monitor cross-cloud data transfer costs
- Optimize for cloud-specific pricing models

### Security Consistency
- Maintain equivalent security controls
- Implement unified identity management
- Use consistent encryption strategies
- Monitor compliance across all clouds

## Next Steps

After completing this example:

1. **Migration**: Explore [Cloud Migration Scenarios](../cloud-migration/) for detailed migration strategies
2. **Hybrid**: Try [Hybrid Cloud Integration](../hybrid-cloud/) for on-premises integration
3. **Compliance**: Study [SOC2 Security](../../compliance/soc2-security/) for multi-cloud compliance
4. **Automation**: Implement [CI/CD Integration](../../../ci-cd/github-actions/) for multi-cloud deployments

## Related Examples

- [Cloud Migration](../cloud-migration/) - Migration strategies and validation
- [Hybrid Cloud](../hybrid-cloud/) - On-premises integration patterns
- [SOC2 Security](../../compliance/soc2-security/) - Multi-cloud compliance
- [Kubernetes Microservices](../../by-use-case/microservices/kubernetes-microservices/) - Container orchestration across clouds
