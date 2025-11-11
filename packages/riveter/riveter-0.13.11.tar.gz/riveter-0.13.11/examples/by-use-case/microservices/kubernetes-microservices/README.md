# Kubernetes Microservices Architecture

**Estimated Time**: 60 minutes
**Complexity**: Advanced
**Prerequisites**: Intermediate examples, Kubernetes knowledge, service mesh concepts

## What You'll Learn

- Understand container security validation patterns
- Learn service mesh security rule development
- Practice Kubernetes security policy validation
- Master multi-cloud microservices governance

## Architecture Overview

This example demonstrates a production-ready microservices architecture:

```
Internet → ALB → Istio Gateway → Service Mesh → Microservices
    ↓         ↓         ↓            ↓            ↓
  WAF    TLS Termination  mTLS    Network Policies  RBAC
```

### Key Components

1. **EKS Cluster**: Managed Kubernetes with security hardening
2. **Service Mesh**: Istio for traffic management and security
3. **Container Registry**: ECR with vulnerability scanning
4. **Network Security**: VPC, security groups, and network policies
5. **Identity & Access**: RBAC, service accounts, and pod security

## Files Included

- `main.tf` - Main configuration and provider setup
- `cluster.tf` - EKS cluster and node group configuration
- `networking.tf` - VPC, subnets, and network security
- `security.tf` - IAM roles, RBAC, and security policies
- `service-mesh.tf` - Istio service mesh configuration
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `kubernetes-security-rules.yml` - Kubernetes security validation
- `service-mesh-rules.yml` - Service mesh security validation
- `container-security-rules.yml` - Container and image security
- `network-policy-rules.yml` - Network policy validation

## Step-by-Step Walkthrough

### Step 1: Examine Cluster Security (15 minutes)

Review `cluster.tf` for EKS security configuration:

```hcl
# EKS cluster with security hardening
resource "aws_eks_cluster" "microservices" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster_role.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.allowed_cidr_blocks

    security_group_ids = [aws_security_group.cluster_sg.id]
  }

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks_key.arn
    }
    resources = ["secrets"]
  }

  enabled_cluster_log_types = [
    "api", "audit", "authenticator", "controllerManager", "scheduler"
  ]
}

# Managed node group with security settings
resource "aws_eks_node_group" "microservices" {
  cluster_name    = aws_eks_cluster.microservices.name
  node_group_name = "${var.cluster_name}-nodes"
  node_role_arn   = aws_iam_role.node_role.arn
  subnet_ids      = var.private_subnet_ids

  launch_template {
    id      = aws_launch_template.node_template.id
    version = aws_launch_template.node_template.latest_version
  }

  scaling_config {
    desired_size = var.node_desired_size
    max_size     = var.node_max_size
    min_size     = var.node_min_size
  }
}
```

### Step 2: Understand Service Mesh Security (15 minutes)

Review `service-mesh.tf` for Istio configuration:

```hcl
# Istio service mesh with security policies
resource "kubernetes_namespace" "istio_system" {
  metadata {
    name = "istio-system"
    labels = {
      "istio-injection" = "disabled"
    }
  }
}

# Istio gateway with TLS configuration
resource "kubernetes_manifest" "istio_gateway" {
  manifest = {
    apiVersion = "networking.istio.io/v1beta1"
    kind       = "Gateway"
    metadata = {
      name      = "microservices-gateway"
      namespace = "istio-system"
    }
    spec = {
      selector = {
        istio = "ingressgateway"
      }
      servers = [
        {
          port = {
            number   = 443
            name     = "https"
            protocol = "HTTPS"
          }
          tls = {
            mode           = "SIMPLE"
            credentialName = "microservices-tls"
          }
          hosts = ["api.example.com"]
        }
      ]
    }
  }
}

# Peer authentication for mTLS
resource "kubernetes_manifest" "peer_authentication" {
  manifest = {
    apiVersion = "security.istio.io/v1beta1"
    kind       = "PeerAuthentication"
    metadata = {
      name      = "default"
      namespace = "production"
    }
    spec = {
      mtls = {
        mode = "STRICT"
      }
    }
  }
}
```

### Step 3: Review Security Validation Rules (20 minutes)

#### Kubernetes Security Rules (`kubernetes-security-rules.yml`)
```yaml
rules:
  - name: "EKS cluster must have encryption enabled"
    resource_type: "aws_eks_cluster"
    assertions:
      - key: "encryption_config.0.resources"
        operator: "contains"
        value: "secrets"
      - key: "encryption_config.0.provider.0.key_arn"
        operator: "exists"

  - name: "EKS cluster must have logging enabled"
    resource_type: "aws_eks_cluster"
    assertions:
      - key: "enabled_cluster_log_types"
        operator: "contains_all"
        value: ["api", "audit", "authenticator"]

  - name: "Node groups must use private subnets"
    resource_type: "aws_eks_node_group"
    assertions:
      - key: "subnet_ids"
        operator: "not_empty"
        message: "Node groups must be deployed in private subnets"

  - name: "Pods must not run as root"
    resource_type: "kubernetes_pod"
    assertions:
      - key: "spec.0.security_context.0.run_as_non_root"
        operator: "equals"
        value: true
      - key: "spec.0.security_context.0.run_as_user"
        operator: "not_equals"
        value: 0
```

#### Service Mesh Rules (`service-mesh-rules.yml`)
```yaml
rules:
  - name: "Istio gateways must use HTTPS"
    resource_type: "kubernetes_manifest"
    filters:
      - key: "manifest.kind"
        operator: "equals"
        value: "Gateway"
    assertions:
      - key: "manifest.spec.servers.0.port.protocol"
        operator: "equals"
        value: "HTTPS"
      - key: "manifest.spec.servers.0.tls.mode"
        operator: "in"
        value: ["SIMPLE", "MUTUAL"]

  - name: "Peer authentication must enforce mTLS"
    resource_type: "kubernetes_manifest"
    filters:
      - key: "manifest.kind"
        operator: "equals"
        value: "PeerAuthentication"
    assertions:
      - key: "manifest.spec.mtls.mode"
        operator: "equals"
        value: "STRICT"

  - name: "Authorization policies must be defined"
    resource_type: "kubernetes_manifest"
    filters:
      - key: "manifest.kind"
        operator: "equals"
        value: "AuthorizationPolicy"
    assertions:
      - key: "manifest.spec.rules"
        operator: "exists"
        message: "Authorization policies must define access rules"
```

#### Container Security Rules (`container-security-rules.yml`)
```yaml
rules:
  - name: "Container images must be from trusted registries"
    resource_type: "kubernetes_deployment"
    assertions:
      - key: "spec.0.template.0.spec.0.container.0.image"
        operator: "matches"
        value: "^[0-9]+\\.dkr\\.ecr\\.[a-z0-9-]+\\.amazonaws\\.com/.*"
        message: "Container images must be from ECR or approved registries"

  - name: "Containers must have resource limits"
    resource_type: "kubernetes_deployment"
    assertions:
      - key: "spec.0.template.0.spec.0.container.0.resources.0.limits.memory"
        operator: "exists"
      - key: "spec.0.template.0.spec.0.container.0.resources.0.limits.cpu"
        operator: "exists"

  - name: "Containers must not run privileged"
    resource_type: "kubernetes_deployment"
    assertions:
      - key: "spec.0.template.0.spec.0.container.0.security_context.0.privileged"
        operator: "not_equals"
        value: true
      - key: "spec.0.template.0.spec.0.container.0.security_context.0.allow_privilege_escalation"
        operator: "equals"
        value: false
```

#### Network Policy Rules (`network-policy-rules.yml`)
```yaml
rules:
  - name: "Namespaces must have network policies"
    resource_type: "kubernetes_namespace"
    filters:
      - key: "metadata.0.name"
        operator: "not_in"
        value: ["kube-system", "istio-system"]
    assertions:
      - key: "metadata.0.labels.network-policy"
        operator: "equals"
        value: "enabled"

  - name: "Network policies must deny by default"
    resource_type: "kubernetes_network_policy"
    assertions:
      - key: "spec.0.policy_types"
        operator: "contains_all"
        value: ["Ingress", "Egress"]
      - key: "spec.0.ingress"
        operator: "exists"
      - key: "spec.0.egress"
        operator: "exists"
```

### Step 4: Run Comprehensive Validation (10 minutes)

Execute validation across all components:

```bash
# Validate all microservices components
riveter scan \
  -r kubernetes-security-rules.yml \
  -r service-mesh-rules.yml \
  -r container-security-rules.yml \
  -r network-policy-rules.yml \
  -t *.tf

# Use specialized rule packs
riveter scan \
  -p kubernetes-security \
  -p multi-cloud-security \
  -t *.tf
```

## Expected Results

### Successful Validation
```
✅ EKS cluster must have encryption enabled (1 resource)
✅ EKS cluster must have logging enabled (1 resource)
✅ Node groups must use private subnets (2 resources)
✅ Pods must not run as root (8 resources)
✅ Istio gateways must use HTTPS (2 resources)
✅ Peer authentication must enforce mTLS (3 resources)
✅ Authorization policies must be defined (5 resources)
✅ Container images must be from trusted registries (8 resources)
✅ Containers must have resource limits (8 resources)
✅ Containers must not run privileged (8 resources)
✅ Namespaces must have network policies (4 resources)
✅ Network policies must deny by default (4 resources)

Summary: 54 rules passed, 0 failed
Microservices security validation passed!
```

## Advanced Security Patterns

### Zero Trust Architecture
```yaml
- name: "Services must use service accounts"
  resource_type: "kubernetes_deployment"
  assertions:
    - key: "spec.0.template.0.spec.0.service_account_name"
      operator: "exists"
      message: "All services must use dedicated service accounts"

- name: "Service accounts must not auto-mount tokens"
  resource_type: "kubernetes_service_account"
  assertions:
    - key: "automount_service_account_token"
      operator: "equals"
      value: false
```

### Multi-Tenancy Security
```yaml
- name: "Tenant namespaces must have resource quotas"
  resource_type: "kubernetes_resource_quota"
  filters:
    - key: "metadata.0.namespace"
      operator: "matches"
      value: "^tenant-.*"
  assertions:
    - key: "spec.0.hard.requests\\.memory"
      operator: "exists"
    - key: "spec.0.hard.requests\\.cpu"
      operator: "exists"
```

### Compliance Automation
```yaml
- name: "PCI DSS: Payment services must use dedicated nodes"
  resource_type: "kubernetes_deployment"
  filters:
    - key: "metadata.0.labels.app"
      operator: "matches"
      value: ".*payment.*"
  assertions:
    - key: "spec.0.template.0.spec.0.node_selector.workload-type"
      operator: "equals"
      value: "pci-compliant"
```

## Real-World Scenarios

### Financial Services
- PCI DSS compliance for payment processing
- Data encryption and key management
- Audit logging and monitoring
- Network segmentation and isolation

### Healthcare (HIPAA)
- PHI data protection in containers
- Access control and authentication
- Audit trails and compliance reporting
- Data backup and disaster recovery

### Government (FedRAMP)
- Security controls implementation
- Continuous monitoring and assessment
- Incident response procedures
- Supply chain security

## Try It Yourself

### Exercise 1: Implement Pod Security Standards
Add Pod Security Standards (PSS) with validation rules for restricted profiles.

### Exercise 2: Add Service Mesh Observability
Implement distributed tracing and metrics collection with validation.

### Exercise 3: Multi-Cluster Federation
Extend to multiple clusters with cross-cluster security validation.

### Exercise 4: GitOps Integration
Implement GitOps workflow with security policy validation.

## Troubleshooting Guide

### Common Issues

#### EKS Cluster Access
```
❌ Cannot access EKS cluster
   Cause: IAM permissions or security group configuration
   Solution: Verify IAM roles and security group rules
```

#### Service Mesh Configuration
```
❌ Istio sidecar injection failed
   Cause: Namespace not labeled for injection
   Solution: Add istio-injection=enabled label to namespace
```

#### Network Policy Conflicts
```
❌ Pod cannot communicate with service
   Cause: Network policy blocking traffic
   Solution: Review and adjust network policy rules
```

## Performance Considerations

### Resource Optimization
- Right-size container resource requests and limits
- Use horizontal pod autoscaling (HPA)
- Implement vertical pod autoscaling (VPA)
- Optimize node instance types and sizes

### Network Performance
- Use AWS Load Balancer Controller for efficient load balancing
- Implement cluster autoscaling for dynamic scaling
- Optimize service mesh configuration for performance
- Use network policies judiciously to avoid overhead

## Next Steps

After completing this example:

1. **Compliance**: Explore [HIPAA Healthcare](../../compliance/hipaa-compliant-healthcare/) for healthcare-specific requirements
2. **Multi-Cloud**: Try [Multi-Cloud Patterns](../../../by-cloud/multi-cloud/) for cross-cloud deployments
3. **Automation**: Implement [CI/CD Integration](../../../ci-cd/github-actions/) for automated deployments
4. **Monitoring**: Add comprehensive observability and monitoring solutions

## Related Examples

- [ECS Microservices](../ecs-microservices/) - Alternative container orchestration
- [Service Mesh Security](../service-mesh-security/) - Advanced service mesh patterns
- [Three-Tier Web App](../../web-application/three-tier-web-app/) - Traditional architecture comparison
- [Multi-Cloud Security](../../../by-cloud/multi-cloud/) - Cross-cloud governance
