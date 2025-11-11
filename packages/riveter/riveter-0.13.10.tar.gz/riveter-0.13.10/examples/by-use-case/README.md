# Examples by Use Case

Real-world infrastructure scenarios with complete configurations and validation strategies.

## Available Use Cases

### Web Application
Complete web application infrastructure patterns:
- **simple-static-site/**: Static website with S3 and CloudFront
- **three-tier-web-app/**: Classic web application with load balancer, app servers, and database
- **serverless-web-app/**: Serverless architecture with Lambda, API Gateway, and DynamoDB

### Data Pipeline
Data processing and analytics infrastructure:
- **batch-processing-pipeline/**: ETL pipeline with S3, Lambda, and Glue
- **real-time-streaming/**: Real-time data processing with Kinesis and Lambda
- **data-lake-architecture/**: Comprehensive data lake with governance and security

### Microservices
Container-based microservices patterns:
- **kubernetes-microservices/**: Kubernetes cluster with service mesh
- **ecs-microservices/**: AWS ECS-based microservices architecture
- **service-mesh-security/**: Advanced service mesh with security policies

### Compliance
Compliance-focused infrastructure examples:
- **hipaa-compliant-healthcare/**: Healthcare infrastructure meeting HIPAA requirements
- **pci-dss-payment-processing/**: Payment processing infrastructure for PCI DSS
- **sox-financial-services/**: Financial services infrastructure for SOX compliance

## How to Use These Examples

Each use case includes:
- **Complete Infrastructure**: Full Terraform configurations for production-ready deployments
- **Security Rules**: Comprehensive validation rules covering security, compliance, and best practices
- **Documentation**: Detailed explanations of architecture decisions and trade-offs
- **Variations**: Different implementation approaches and their validation strategies

## Learning Path by Role

### Developers
1. Start with `web-application/simple-static-site/`
2. Progress to `web-application/three-tier-web-app/`
3. Explore `microservices/ecs-microservices/`

### Security Engineers
1. Begin with `compliance/hipaa-compliant-healthcare/`
2. Study `web-application/three-tier-web-app/` for security patterns
3. Advanced: `microservices/service-mesh-security/`

### Data Engineers
1. Start with `data-pipeline/batch-processing-pipeline/`
2. Advance to `data-pipeline/real-time-streaming/`
3. Master `data-pipeline/data-lake-architecture/`

### Platform Engineers
1. Begin with `microservices/kubernetes-microservices/`
2. Study `compliance/` examples for governance patterns
3. Integrate learnings across all use cases
