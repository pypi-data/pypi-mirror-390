# Terraform Test Fixtures

This directory contains Terraform configuration files used for testing Riveter rule packs. Each file contains both passing and failing examples to validate rule pack behavior.

## File Structure

### Cloud Provider Security Test Fixtures

- **`gcp_security_test.tf`** - GCP Security Best Practices
  - Compute Engine resources (instances, metadata, OS Login)
  - Cloud Storage buckets (encryption, versioning, access controls)
  - Cloud SQL databases (SSL, backups, private networking)
  - VPC/Networking (flow logs, firewall rules, Cloud NAT)
  - IAM (service accounts, role bindings, primitive roles)
  - Cloud KMS (key rings, crypto keys, rotation)

- **`azure_security_test.tf`** - Azure Security Best Practices
  - Virtual Machines (disk encryption, managed identities, sizing)
  - Storage Accounts (HTTPS, TLS, public access, soft delete)
  - SQL Databases (TDE, threat detection, firewall rules)
  - Network Security Groups (rules, descriptions, restrictions)
  - Key Vault (soft delete, purge protection, network ACLs)

### Compliance Test Fixtures

- **`cis_gcp_test.tf`** - CIS GCP Benchmark
  - Section 1: Identity and Access Management (IAM roles, service accounts)
  - Section 2: Logging and Monitoring (audit logs, log metrics, sinks)
  - Section 3: Networking (VPC flow logs, firewall rules, DNSSEC)
  - Section 4: Virtual Machines (OS Login, SSH keys, Shielded VM)
  - Section 5: Storage (uniform access, public access prevention)
  - Section 6: Cloud SQL (SSL, public IP, backups, logging)

### Well-Architected Framework Test Fixtures

- **`aws_well_architected_test.tf`** - AWS Well-Architected Framework
  - Operational Excellence (CloudWatch alarms, Auto Scaling, tagging)
  - Security (encryption, VPC flow logs, access controls)
  - Reliability (Multi-AZ, health checks, backups, PITR)
  - Performance Efficiency (CloudFront, ElastiCache, EBS types, Lambda)
  - Cost Optimization (cost tags, lifecycle policies, right-sizing)
  - Sustainability (serverless, appropriate sizing, resource utilization)

### Container and Kubernetes Test Fixtures

- **`kubernetes_security_test.tf`** - Kubernetes Security
  - EKS (AWS) clusters and node groups
  - AKS (Azure) clusters with RBAC and network policies
  - GKE (GCP) clusters with private nodes and workload identity
  - Kubernetes pods (security contexts, resource limits, privileged mode)
  - Kubernetes deployments (security best practices)
  - Network policies (default deny, ingress/egress rules)
  - RBAC (service accounts, roles, role bindings, cluster roles)
  - Secrets management

### Multi-Cloud Test Fixtures

- **`multi_cloud_test.tf`** - Multi-Cloud Security Patterns
  - AWS resources (S3, RDS, EC2, Security Groups, CloudTrail, KMS)
  - Azure resources (Storage Accounts, SQL, VMs, NSGs, Activity Logs)
  - GCP resources (Cloud Storage, Cloud SQL, Compute, Firewall, Audit Logs)
  - Common patterns: encryption, network security, IAM, logging, monitoring

### Legacy Test Fixtures

- **`simple.tf`** - Basic AWS resources for simple tests
- **`complex.tf`** - Complex multi-resource scenarios
- **`gcp_example.tf`** - Original GCP examples
- **`azure_example.tf`** - Original Azure examples
- **`malformed.tf`** - Invalid Terraform for error handling tests

## Test Fixture Patterns

### Passing Examples (PASS)
Resources that comply with security best practices and should pass rule validation:
- Proper encryption enabled
- Restricted network access
- Appropriate logging and monitoring
- Required tags and labels
- Security features enabled

### Failing Examples (FAIL)
Resources that violate security best practices and should fail rule validation:
- Missing encryption
- Overly permissive network rules
- Missing logging or monitoring
- Missing required tags
- Security features disabled

## Usage in Tests

These fixtures are used in integration tests to validate that rule packs correctly identify both compliant and non-compliant resources:

```python
def test_gcp_security_rules():
    # Load the test fixture
    terraform_file = "tests/fixtures/terraform/gcp_security_test.tf"

    # Scan with the gcp-security rule pack
    results = scan_terraform(terraform_file, rule_pack="gcp-security")

    # Verify passing resources pass
    assert_resource_passes(results, "google_compute_instance.secure_instance")

    # Verify failing resources fail
    assert_resource_fails(results, "google_compute_instance.insecure_external_ip")
```

## Adding New Test Fixtures

When adding new rule packs, create corresponding test fixtures following these guidelines:

1. **File Naming**: Use `<provider>_<category>_test.tf` format
2. **Comments**: Clearly mark PASS and FAIL examples
3. **Coverage**: Include examples for all major rules in the pack
4. **Organization**: Group resources by logical sections
5. **Completeness**: Include supporting resources (networks, keys, etc.)
6. **Documentation**: Add comments explaining why resources pass or fail

## Test Fixture Maintenance

- Keep fixtures up to date with latest Terraform provider versions
- Add new examples when new rules are added to rule packs
- Remove deprecated resource types
- Update comments to reflect current best practices
- Ensure fixtures remain valid Terraform syntax (even if they represent bad practices)

## Related Documentation

- [Rule Pack Documentation](../../../../docs/)
- [Testing Guide](../../README.md)
- [Contributing Guidelines](../../../../CONTRIBUTING.md)
