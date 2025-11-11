# Test Infrastructure for Comprehensive Cloud Rule Packs

This document describes the test infrastructure created to support the development and validation of new Riveter rule packs.

## Overview

The test infrastructure provides comprehensive Terraform configuration fixtures covering:
- GCP Security Best Practices
- Azure Security Best Practices (expanded)
- CIS GCP Benchmark
- AWS Well-Architected Framework
- Kubernetes Security (EKS, AKS, GKE)
- Multi-Cloud Security Patterns

## Test Fixture Files

### 1. GCP Security Test Fixtures
**File**: `terraform/gcp_security_test.tf`

**Coverage** (25-30 rules):
- Compute Engine: OS Login, external IPs, Shielded VM, disk encryption, labels
- Cloud Storage: Uniform access, encryption, public access prevention, versioning, logging
- Cloud SQL: SSL/TLS, backups, private networking, encryption
- VPC/Networking: Flow logs, firewall rules, Private Google Access, Cloud NAT
- IAM: Service accounts, primitive roles, Workload Identity
- Cloud KMS: Key rotation, key purpose

**Test Scenarios**:
- ✅ 15+ passing examples demonstrating security best practices
- ❌ 15+ failing examples demonstrating security violations

### 2. Azure Security Test Fixtures
**File**: `terraform/azure_security_test.tf`

**Coverage** (25-30 rules):
- Virtual Machines: Disk encryption, public IPs, managed identities, tags, sizing
- Storage Accounts: HTTPS enforcement, TLS version, public access, soft delete, versioning
- SQL Databases: TDE, threat detection, firewall rules, backups
- Network Security Groups: Rule restrictions, descriptions, wide-open rules
- Key Vault: Soft delete, purge protection, network ACLs

**Test Scenarios**:
- ✅ 12+ passing examples with all security features enabled
- ❌ 12+ failing examples with security misconfigurations

### 3. CIS GCP Benchmark Test Fixtures
**File**: `terraform/cis_gcp_test.tf`

**Coverage** (30-40 rules across 6 sections):
- Section 1: IAM (10-12 rules) - Service account privileges, primitive roles, key management
- Section 2: Logging (8-10 rules) - Audit logging, log sinks, log metrics
- Section 3: Networking (6-8 rules) - Flow logs, firewall rules, DNSSEC
- Section 4: VMs (4-5 rules) - OS Login, SSH keys, Shielded VM, external IPs
- Section 5: Storage (4-5 rules) - Uniform access, public access
- Section 6: Cloud SQL (3-4 rules) - SSL, public IP, backups, logging

**Test Scenarios**:
- ✅ 20+ passing examples meeting CIS controls
- ❌ 15+ failing examples violating CIS controls
- Each rule includes CIS control number references

### 4. AWS Well-Architected Framework Test Fixtures
**File**: `terraform/aws_well_architected_test.tf`

**Coverage** (30-40 rules across 6 pillars):
- Operational Excellence (6-8 rules): CloudWatch alarms, Auto Scaling, tagging
- Security (6-8 rules): Encryption, VPC flow logs, access controls
- Reliability (6-8 rules): Multi-AZ, health checks, backups, PITR
- Performance Efficiency (4-6 rules): CloudFront, ElastiCache, EBS types, Lambda
- Cost Optimization (4-6 rules): Cost tags, lifecycle policies, right-sizing
- Sustainability (2-4 rules): Serverless, appropriate sizing

**Test Scenarios**:
- ✅ 18+ passing examples demonstrating well-architected patterns
- ❌ 12+ failing examples showing anti-patterns

### 5. Kubernetes Security Test Fixtures
**File**: `terraform/kubernetes_security_test.tf`

**Coverage** (30-40 rules):
- EKS (AWS): Cluster configuration, node groups, encryption, logging
- AKS (Azure): RBAC, network policies, private clusters, monitoring
- GKE (GCP): Private nodes, Workload Identity, Binary Authorization, Shielded nodes
- Pod Security: Privileged mode, root users, resource limits, read-only filesystem
- Network Policies: Default deny, ingress/egress rules
- RBAC: Service accounts, roles, role bindings, cluster roles
- Secrets Management: External secrets, encryption

**Test Scenarios**:
- ✅ 15+ passing examples across all three providers
- ❌ 15+ failing examples with security misconfigurations
- Provider-agnostic Kubernetes resources

### 6. Multi-Cloud Security Test Fixtures
**File**: `terraform/multi_cloud_test.tf`

**Coverage** (40-50 rules):
- AWS: S3, RDS, EC2, Security Groups, CloudTrail, KMS
- Azure: Storage Accounts, SQL, VMs, NSGs, Activity Logs, Key Vault
- GCP: Cloud Storage, Cloud SQL, Compute, Firewall, Audit Logs, KMS
- Common patterns: Encryption, network security, IAM, logging, monitoring

**Test Scenarios**:
- ✅ 15+ passing examples across all three providers
- ❌ 15+ failing examples demonstrating common security issues
- Tests multi-cloud consistency

## Test Fixture Statistics

| Fixture File | Resources | Passing Examples | Failing Examples | Total Scenarios |
|--------------|-----------|------------------|------------------|-----------------|
| gcp_security_test.tf | 50+ | 15+ | 15+ | 30+ |
| azure_security_test.tf | 45+ | 12+ | 12+ | 24+ |
| cis_gcp_test.tf | 55+ | 20+ | 15+ | 35+ |
| aws_well_architected_test.tf | 60+ | 18+ | 12+ | 30+ |
| kubernetes_security_test.tf | 50+ | 15+ | 15+ | 30+ |
| multi_cloud_test.tf | 70+ | 15+ | 15+ | 30+ |
| **TOTAL** | **330+** | **95+** | **84+** | **179+** |

## Test Fixture Patterns

### Naming Conventions
- **Passing resources**: Prefixed with `secure_`, `compliant_`, or descriptive names
- **Failing resources**: Prefixed with `no_`, `insecure_`, `missing_`, or descriptive names
- **Comments**: Each resource clearly marked with `# PASS:` or `# FAIL:`

### Resource Organization
1. **Sections**: Grouped by service or category
2. **Comments**: Clear explanations of why resources pass or fail
3. **Supporting Resources**: Networks, keys, and dependencies included
4. **Completeness**: All required attributes for valid Terraform

### Testing Approach
```python
# Example test structure
def test_rule_pack(rule_pack_name, fixture_file):
    # Parse Terraform
    resources = parse_terraform(fixture_file)

    # Load rule pack
    rules = load_rule_pack(rule_pack_name)

    # Scan resources
    results = scan_resources(resources, rules)

    # Verify passing resources
    for resource in passing_resources:
        assert resource not in results.failures

    # Verify failing resources
    for resource in failing_resources:
        assert resource in results.failures
```

## Integration with Rule Packs

Each test fixture file corresponds to one or more rule packs:

| Test Fixture | Rule Pack(s) |
|--------------|--------------|
| gcp_security_test.tf | gcp-security.yml |
| azure_security_test.tf | azure-security.yml |
| cis_gcp_test.tf | cis-gcp.yml |
| aws_well_architected_test.tf | aws-well-architected.yml |
| kubernetes_security_test.tf | kubernetes-security.yml |
| multi_cloud_test.tf | multi-cloud-security.yml |

## Usage Examples

### Running Tests Against Fixtures
```bash
# Test GCP security rules
riveter scan -p gcp-security tests/fixtures/terraform/gcp_security_test.tf

# Test CIS GCP benchmark
riveter scan -p cis-gcp tests/fixtures/terraform/cis_gcp_test.tf

# Test AWS Well-Architected
riveter scan -p aws-well-architected tests/fixtures/terraform/aws_well_architected_test.tf

# Test Kubernetes security
riveter scan -p kubernetes-security tests/fixtures/terraform/kubernetes_security_test.tf

# Test multi-cloud patterns
riveter scan -p multi-cloud-security tests/fixtures/terraform/multi_cloud_test.tf
```

### Integration Test Example
```python
def test_gcp_security_compute_rules():
    """Test GCP Compute Engine security rules."""
    results = scan_terraform(
        "tests/fixtures/terraform/gcp_security_test.tf",
        rule_pack="gcp-security"
    )

    # Should pass
    assert_no_violations(results, "google_compute_instance.secure_instance")
    assert_no_violations(results, "google_compute_project_metadata.os_login_enabled")

    # Should fail
    assert_has_violation(results, "google_compute_instance.insecure_external_ip")
    assert_has_violation(results, "google_compute_instance.no_shielded_vm")
    assert_has_violation(results, "google_compute_project_metadata.os_login_disabled")
```

## Maintenance Guidelines

### Adding New Test Scenarios
1. Identify the rule being tested
2. Create a passing example demonstrating compliance
3. Create a failing example demonstrating violation
4. Add clear comments explaining the scenario
5. Update this documentation

### Updating Existing Fixtures
1. Keep Terraform syntax valid and up-to-date
2. Update provider versions as needed
3. Add new resource types as they become available
4. Remove deprecated resources
5. Maintain consistency with rule pack updates

### Best Practices
- Each rule should have at least one passing and one failing example
- Use realistic resource configurations
- Include edge cases and boundary conditions
- Keep fixtures focused and maintainable
- Document any special considerations

## Future Enhancements

### Planned Additions
1. **Azure Well-Architected Framework fixtures** (Phase 2)
2. **GCP Well-Architected Framework fixtures** (Phase 2)
3. **AWS HIPAA compliance fixtures** (Phase 3)
4. **Azure HIPAA compliance fixtures** (Phase 3)
5. **AWS PCI-DSS compliance fixtures** (Phase 3)

### Test Infrastructure Improvements
- Automated fixture validation
- Coverage reporting
- Performance benchmarking fixtures
- Negative test cases (malformed Terraform)
- Cross-provider consistency tests

## Related Documentation

- [Terraform Test Fixtures README](terraform/README.md)
- [Rule Pack Documentation](../../docs/)
- [Testing Guide](../README.md)
- [Contributing Guidelines](../../CONTRIBUTING.md)

## Summary

The test infrastructure provides comprehensive coverage for validating new rule packs with:
- **330+ Terraform resources** across 6 major fixture files
- **179+ test scenarios** covering passing and failing cases
- **Support for 9 new rule packs** across AWS, Azure, and GCP
- **Multi-cloud and Kubernetes** security patterns
- **Well-documented** examples with clear pass/fail indicators

This infrastructure enables thorough testing of rule pack functionality and ensures high-quality rule validation across all cloud providers.
