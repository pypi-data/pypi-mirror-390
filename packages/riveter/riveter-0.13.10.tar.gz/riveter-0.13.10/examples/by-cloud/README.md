# Examples by Cloud Provider

Cloud-specific and multi-cloud infrastructure patterns with equivalent implementations.

## Directory Structure

### Single Cloud Providers
- **aws/**: Amazon Web Services specific examples
- **azure/**: Microsoft Azure specific examples
- **gcp/**: Google Cloud Platform specific examples

### Multi-Cloud Patterns
- **multi-cloud/**: Cross-cloud equivalent implementations
- **hybrid-cloud/**: Hybrid cloud integration patterns
- **cloud-migration/**: Migration scenarios and validation strategies

## Equivalent Patterns

Many infrastructure patterns can be implemented across different cloud providers. This section provides equivalent implementations to help you:

- Compare approaches across cloud providers
- Migrate workloads between clouds
- Implement multi-cloud strategies
- Understand cloud-specific security requirements

## Pattern Equivalencies

| Pattern | AWS | Azure | GCP |
|---------|-----|-------|-----|
| **Object Storage** | S3 | Blob Storage | Cloud Storage |
| **Compute** | EC2 | Virtual Machines | Compute Engine |
| **Container Orchestration** | EKS | AKS | GKE |
| **Serverless Functions** | Lambda | Functions | Cloud Functions |
| **Managed Database** | RDS | SQL Database | Cloud SQL |
| **Load Balancing** | ALB/NLB | Load Balancer | Cloud Load Balancing |
| **Identity & Access** | IAM | Azure AD | Cloud IAM |
| **Key Management** | KMS | Key Vault | Cloud KMS |

## Multi-Cloud Use Cases

### Disaster Recovery
- Cross-cloud backup and replication
- Failover strategies and validation
- Data synchronization patterns

### Compliance Requirements
- Data residency and sovereignty
- Regulatory compliance across regions
- Audit and governance strategies

### Vendor Risk Mitigation
- Avoiding vendor lock-in
- Maintaining operational flexibility
- Cost optimization strategies

### Performance Optimization
- Edge computing and CDN strategies
- Regional deployment patterns
- Latency optimization

## Getting Started

### For Single Cloud
1. Choose your cloud provider directory (aws/, azure/, gcp/)
2. Start with basic patterns and progress to complex scenarios
3. Use cloud-specific rule packs for validation

### For Multi-Cloud
1. Begin with `multi-cloud/equivalent-patterns/`
2. Study cross-cloud security and compliance requirements
3. Implement governance strategies across providers

### For Migration
1. Review `cloud-migration/` scenarios
2. Understand validation strategies for migration
3. Plan phased migration approaches

## Rule Pack Recommendations

### Single Cloud
- **AWS**: Use `aws-security`, `aws-well-architected`, `cis-aws`
- **Azure**: Use `azure-security`, `azure-well-architected`, `cis-azure`
- **GCP**: Use `gcp-security`, `gcp-well-architected`, `cis-gcp`

### Multi-Cloud
- Use `multi-cloud-security` for cross-cloud patterns
- Combine cloud-specific packs for comprehensive validation
- Apply `soc2-security` for compliance across clouds
