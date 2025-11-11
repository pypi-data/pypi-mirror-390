# Three-Tier Web Application

**Estimated Time**: 45 minutes
**Complexity**: Intermediate
**Prerequisites**: Completed beginner examples, web application architecture knowledge

## What You'll Learn

- Understand multi-tier application architecture validation
- Learn security rule combinations for web applications
- Practice network security and database protection validation
- Understand load balancer and auto-scaling validation

## Architecture Overview

This example demonstrates a classic three-tier web application architecture:

```
Internet → ALB → Auto Scaling Group (EC2) → RDS Database
           ↓
    Public Subnet → Private Subnet → Database Subnet
```

### Components Validated

1. **Presentation Tier**: Application Load Balancer with SSL termination
2. **Application Tier**: Auto Scaling Group with EC2 instances in private subnets
3. **Data Tier**: RDS MySQL database in isolated database subnets

## Files Included

- `main.tf` - Main configuration and provider setup
- `networking.tf` - VPC, subnets, and networking components
- `compute.tf` - Load balancer, auto scaling, and EC2 configuration
- `database.tf` - RDS database configuration
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `web-app-security-rules.yml` - Application-level security rules
- `network-security-rules.yml` - Network security validation
- `database-security-rules.yml` - Database security validation

## Step-by-Step Walkthrough

### Step 1: Examine the Architecture (10 minutes)

Review the Terraform files to understand the complete architecture:

#### Networking (`networking.tf`)
- VPC with public, private, and database subnets
- Internet Gateway and NAT Gateways
- Route tables and security groups

#### Compute (`compute.tf`)
- Application Load Balancer with HTTPS listener
- Launch template with security hardening
- Auto Scaling Group with health checks

#### Database (`database.tf`)
- RDS MySQL instance with encryption
- Database subnet group
- Parameter group with security settings

### Step 2: Understand the Security Rules (15 minutes)

#### Web Application Security (`web-app-security-rules.yml`)
```yaml
rules:
  - name: "ALB must use HTTPS"
    resource_type: "aws_lb_listener"
    assertions:
      - key: "protocol"
        operator: "equals"
        value: "HTTPS"

  - name: "ALB must have SSL policy"
    resource_type: "aws_lb_listener"
    assertions:
      - key: "ssl_policy"
        operator: "matches"
        value: "^ELBSecurityPolicy-TLS-1-2-.*"
```

#### Network Security (`network-security-rules.yml`)
```yaml
rules:
  - name: "Security groups must not allow unrestricted access"
    resource_type: "aws_security_group_rule"
    filters:
      - key: "type"
        operator: "equals"
        value: "ingress"
    assertions:
      - key: "cidr_blocks"
        operator: "not_contains"
        value: "0.0.0.0/0"
        exceptions:
          - key: "from_port"
            operator: "equals"
            value: 443
```

#### Database Security (`database-security-rules.yml`)
```yaml
rules:
  - name: "RDS must have encryption enabled"
    resource_type: "aws_db_instance"
    assertions:
      - key: "storage_encrypted"
        operator: "equals"
        value: true

  - name: "RDS must not be publicly accessible"
    resource_type: "aws_db_instance"
    assertions:
      - key: "publicly_accessible"
        operator: "equals"
        value: false
```

### Step 3: Run Comprehensive Validation (10 minutes)

Execute validation with all rule sets:

```bash
# Validate all components
riveter scan \
  -r web-app-security-rules.yml \
  -r network-security-rules.yml \
  -r database-security-rules.yml \
  -t *.tf

# Or use rule pack combinations
riveter scan \
  -p aws-security \
  -p aws-well-architected \
  -t *.tf
```

### Step 4: Test Security Scenarios (10 minutes)

Experiment with different security configurations:

1. **Test HTTP Listener**: Change ALB listener to HTTP and see validation fail
2. **Test Open Security Group**: Add a rule allowing 0.0.0.0/0 access
3. **Test Unencrypted Database**: Disable RDS encryption
4. **Test Public Database**: Enable public accessibility

## Expected Results

### Successful Validation
```
✅ ALB must use HTTPS (2 resources)
✅ ALB must have SSL policy (2 resources)
✅ Security groups must not allow unrestricted access (8 resources)
✅ RDS must have encryption enabled (1 resource)
✅ RDS must not be publicly accessible (1 resource)
✅ Auto Scaling Group must have health checks (1 resource)
✅ Launch template must use latest AMI (1 resource)

Summary: 16 rules passed, 0 failed
All security validations passed!
```

### Common Failure Scenarios

#### Insecure Load Balancer
```
❌ ALB must use HTTPS
   Resource: aws_lb_listener.web_app_http
   Expected: protocol equals "HTTPS"
   Actual: protocol is "HTTP"
   Fix: Change listener protocol to HTTPS and add SSL certificate
```

#### Open Security Group
```
❌ Security groups must not allow unrestricted access
   Resource: aws_security_group_rule.web_app_ingress
   Expected: cidr_blocks not_contains "0.0.0.0/0"
   Actual: cidr_blocks contains "0.0.0.0/0"
   Fix: Restrict access to specific IP ranges or use ALB security group
```

## Real-World Variations

### High Availability Setup
- Multi-AZ deployment across 3 availability zones
- Cross-zone load balancing enabled
- RDS Multi-AZ for database failover

### Security Hardening
- WAF integration with ALB
- VPC Flow Logs enabled
- CloudTrail for audit logging
- Systems Manager for patch management

### Performance Optimization
- CloudFront CDN integration
- ElastiCache for session storage
- RDS read replicas for read scaling

## Try It Yourself

### Exercise 1: Add WAF Protection
Add AWS WAF resources and rules to validate WAF association with ALB.

### Exercise 2: Implement Blue/Green Deployment
Modify the configuration to support blue/green deployments with validation rules.

### Exercise 3: Add Monitoring and Alerting
Include CloudWatch alarms and SNS topics with appropriate validation rules.

### Exercise 4: Multi-Region Setup
Extend to multiple regions with cross-region replication validation.

## Troubleshooting Guide

### Common Issues

#### "Resource not found" errors
- Ensure all Terraform files are in the same directory
- Check resource dependencies and references
- Verify provider configuration

#### Security group rule validation failures
- Review CIDR block configurations
- Check for conflicting ingress/egress rules
- Validate port ranges and protocols

#### Database connectivity issues
- Verify subnet group configuration
- Check security group associations
- Ensure proper VPC and subnet setup

## Next Steps

After completing this example:

1. **Scale Up**: Try the [Kubernetes Microservices](../../microservices/kubernetes-microservices/) example
2. **Add Compliance**: Explore [HIPAA Compliant Healthcare](../../compliance/hipaa-compliant-healthcare/)
3. **Automate**: Set up [CI/CD Integration](../../../ci-cd/github-actions/)
4. **Monitor**: Add observability with CloudWatch and X-Ray

## Related Examples

- [Simple Static Site](../simple-static-site/) - Simpler web architecture
- [Serverless Web App](../serverless-web-app/) - Serverless alternative
- [ECS Microservices](../../microservices/ecs-microservices/) - Container-based architecture
- [HIPAA Healthcare](../../compliance/hipaa-compliant-healthcare/) - Compliance-focused version
