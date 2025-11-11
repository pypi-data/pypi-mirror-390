# Visual Guides

This page consolidates all visual documentation to help you understand how Riveter works, choose the right rule packs, and troubleshoot issues.

## 🏗️ How Riveter Works

### High-Level Flow
```mermaid
graph TD
    A["📄 Terraform<br/>Configuration<br/>Files (.tf)"] --> B["🔍 HCL Parser<br/>(Syntax Analysis<br/>& Parsing)"]
    C["📦 Pre-built<br/>Rule Packs<br/>(AWS, Azure, GCP)"] --> D["⚙️ Rule Engine<br/>(Load & Validate<br/>Rule Definitions)"]
    E["📝 Custom<br/>Organization<br/>Rules"] --> D

    B --> F["🔧 Resource<br/>Extractor<br/>(Extract Resources)"]
    F --> G["✅ Validation<br/>Engine<br/>(Core Logic)"]
    D --> G

    G --> H["📊 Results<br/>Processor<br/>(Format Output)"]
    H --> I["💻 Terminal<br/>Output<br/>(Human Readable)"]
    H --> J["📋 JSON<br/>Export<br/>(Programmatic)"]
    H --> K["🔒 SARIF<br/>Export<br/>(Security Tools)"]
    H --> L["🧪 JUnit<br/>XML<br/>(CI/CD Integration)"]

    style A fill:#ffffff,stroke:#2196f3,stroke-width:3px,color:#000000
    style B fill:#f8f9fa,stroke:#2196f3,stroke-width:2px,color:#000000
    style C fill:#ffffff,stroke:#9c27b0,stroke-width:3px,color:#000000
    style D fill:#ffffff,stroke:#ff9800,stroke-width:3px,color:#000000
    style E fill:#ffffff,stroke:#9c27b0,stroke-width:3px,color:#000000
    style F fill:#f8f9fa,stroke:#2196f3,stroke-width:2px,color:#000000
    style G fill:#ffffff,stroke:#ff9800,stroke-width:3px,color:#000000
    style H fill:#f8f9fa,stroke:#ff9800,stroke-width:2px,color:#000000
    style I fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style J fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style K fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style L fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
```

### Rule Evaluation Process
```mermaid
flowchart TD
    START(["🚀 Start<br/>Validation"]) --> LOAD_TF["📄 Load Terraform<br/>Configuration"]
    LOAD_TF --> LOAD_RULES["📦 Load Rules &<br/>Rule Packs"]
    LOAD_RULES --> EXTRACT["🔧 Extract<br/>Resources"]

    EXTRACT --> FOR_EACH{"🔄 For Each<br/>Resource"}
    FOR_EACH --> CHECK_TYPE{"🎯 Resource Type<br/>Matches Rule?"}

    CHECK_TYPE -->|"❌ No"| NEXT_RULE["➡️ Next Rule"]
    CHECK_TYPE -->|"✅ Yes"| CHECK_FILTER{"🔍 Passes<br/>Filters?"}

    CHECK_FILTER -->|"❌ No"| NEXT_RULE
    CHECK_FILTER -->|"✅ Yes"| EVAL_ASSERT["⚙️ Evaluate<br/>Assertions"]

    EVAL_ASSERT --> ASSERT_RESULT{"✅ All Assertions<br/>Pass?"}
    ASSERT_RESULT -->|"✅ Yes"| PASS["✅ Rule<br/>Passes"]
    ASSERT_RESULT -->|"❌ No"| FAIL["❌ Rule<br/>Fails"]

    PASS --> RECORD_PASS["📝 Record<br/>Success"]
    FAIL --> RECORD_FAIL["📝 Record<br/>Failure"]

    RECORD_PASS --> NEXT_RULE
    RECORD_FAIL --> NEXT_RULE

    NEXT_RULE --> MORE_RULES{"🔄 More<br/>Rules?"}
    MORE_RULES -->|"✅ Yes"| CHECK_TYPE
    MORE_RULES -->|"❌ No"| GENERATE["📊 Generate<br/>Report"]

    GENERATE --> END(["🏁 End"])

    style START fill:#ffffff,stroke:#2196f3,stroke-width:3px,color:#000000
    style PASS fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style FAIL fill:#ffffff,stroke:#f44336,stroke-width:3px,color:#000000
    style END fill:#ffffff,stroke:#9c27b0,stroke-width:3px,color:#000000
    style LOAD_TF fill:#f8f9fa,stroke:#2196f3,stroke-width:2px,color:#000000
    style LOAD_RULES fill:#f8f9fa,stroke:#9c27b0,stroke-width:2px,color:#000000
    style EXTRACT fill:#f8f9fa,stroke:#ff9800,stroke-width:2px,color:#000000
    style GENERATE fill:#f8f9fa,stroke:#9c27b0,stroke-width:2px,color:#000000
```

## 📊 Rule Pack Selection

### Choose by Use Case
```mermaid
graph TD
    START(["🤔 What do you want<br/>to validate?"]) --> PURPOSE{"🎯 Primary<br/>Purpose"}

    PURPOSE -->|"🛡️ Security Best Practices"| SECURITY_PATH["🔒 Security<br/>Focus"]
    PURPOSE -->|"📋 Compliance Requirements"| COMPLIANCE_PATH["📊 Compliance<br/>Focus"]
    PURPOSE -->|"🏗️ Architecture Quality"| ARCHITECTURE_PATH["⚙️ Architecture<br/>Focus"]

    SECURITY_PATH --> CLOUD_SEC{"☁️ Which Cloud<br/>Provider?"}
    CLOUD_SEC -->|"🟠 AWS"| AWS_SEC["aws-security +<br/>multi-cloud-security"]
    CLOUD_SEC -->|"🔵 Azure"| AZURE_SEC["azure-security +<br/>multi-cloud-security"]
    CLOUD_SEC -->|"🟡 GCP"| GCP_SEC["gcp-security +<br/>multi-cloud-security"]
    CLOUD_SEC -->|"🌐 Multi-Cloud"| MULTI_SEC["multi-cloud-security"]

    COMPLIANCE_PATH --> FRAMEWORK{"📋 Compliance<br/>Framework"}
    FRAMEWORK -->|"📊 CIS Benchmarks"| CIS_RULES["cis-aws /<br/>cis-azure /<br/>cis-gcp"]
    FRAMEWORK -->|"🏥 HIPAA"| HIPAA_RULES["aws-hipaa +<br/>azure-hipaa"]
    FRAMEWORK -->|"💳 PCI-DSS"| PCI_RULES["aws-pci-dss"]
    FRAMEWORK -->|"🔐 SOC 2"| SOC2_RULES["soc2-security"]

    ARCHITECTURE_PATH --> ARCH_CLOUD{"🏗️ Which Cloud<br/>Architecture?"}
    ARCH_CLOUD -->|"🟠 AWS"| AWS_ARCH["aws-well-architected"]
    ARCH_CLOUD -->|"🔵 Azure"| AZURE_ARCH["azure-well-architected"]
    ARCH_CLOUD -->|"🟡 GCP"| GCP_ARCH["gcp-well-architected"]

    style START fill:#ffffff,stroke:#2196f3,stroke-width:3px,color:#000000
    style AWS_SEC fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style AZURE_SEC fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style GCP_SEC fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style MULTI_SEC fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style CIS_RULES fill:#ffffff,stroke:#ff9800,stroke-width:3px,color:#000000
    style HIPAA_RULES fill:#ffffff,stroke:#ff9800,stroke-width:3px,color:#000000
    style PCI_RULES fill:#ffffff,stroke:#ff9800,stroke-width:3px,color:#000000
    style SOC2_RULES fill:#ffffff,stroke:#ff9800,stroke-width:3px,color:#000000
    style AWS_ARCH fill:#ffffff,stroke:#9c27b0,stroke-width:3px,color:#000000
    style AZURE_ARCH fill:#ffffff,stroke:#9c27b0,stroke-width:3px,color:#000000
    style GCP_ARCH fill:#ffffff,stroke:#9c27b0,stroke-width:3px,color:#000000
```

### Rule Pack Coverage Matrix

| Service Category | AWS | Azure | GCP | Multi-Cloud | Kubernetes |
|------------------|-----|-------|-----|-------------|------------|
| **Compute** | ✅ EC2, Lambda | ✅ VMs, Functions | ✅ Compute Engine | ✅ Common patterns | ✅ Pods, Deployments |
| **Storage** | ✅ S3, EBS | ✅ Storage Accounts | ✅ Cloud Storage | ✅ Encryption, Access | ✅ Volumes |
| **Database** | ✅ RDS, DynamoDB | ✅ SQL Database | ✅ Cloud SQL | ✅ Encryption, Backup | ✅ StatefulSets |
| **Networking** | ✅ VPC, Security Groups | ✅ VNet, NSGs | ✅ VPC, Firewall | ✅ Network Security | ✅ Network Policies |
| **Identity** | ✅ IAM, Roles | ✅ Azure AD, RBAC | ✅ IAM, Service Accounts | ✅ Access Control | ✅ RBAC |
| **Security** | ✅ KMS, CloudTrail | ✅ Key Vault | ✅ KMS, Logging | ✅ Encryption | ✅ Pod Security |

## 🔧 Troubleshooting Guide

### Common Error Resolution
```mermaid
flowchart TD
    ERROR(["❌ Validation<br/>Error"]) --> ERROR_TYPE{"🔍 Error<br/>Type"}

    ERROR_TYPE -->|"📄 Parse Error"| PARSE_FLOW["🔧 Terraform<br/>Parsing Issues"]
    ERROR_TYPE -->|"📦 Rule Error"| RULE_FLOW["📋 Rule Loading<br/>Issues"]
    ERROR_TYPE -->|"⚠️ Validation Failure"| VALIDATION_FLOW["✅ Expected<br/>Failures"]

    PARSE_FLOW --> CHECK_SYNTAX{"📝 Valid HCL<br/>Syntax?"}
    CHECK_SYNTAX -->|"❌ No"| FIX_SYNTAX["🔧 Fix Terraform<br/>Syntax Errors"]
    CHECK_SYNTAX -->|"✅ Yes"| CHECK_PATH{"📁 Correct<br/>File Path?"}
    CHECK_PATH -->|"❌ No"| FIX_PATH["📂 Verify<br/>File Path"]
    CHECK_PATH -->|"✅ Yes"| PARSE_SUCCESS["✅ Parsing<br/>Fixed"]

    RULE_FLOW --> RULE_EXISTS{"📦 Rule Pack<br/>Exists?"}
    RULE_EXISTS -->|"❌ No"| CHECK_RULE_NAME["🔍 Verify Rule<br/>Pack Name"]
    RULE_EXISTS -->|"✅ Yes"| RULE_SYNTAX{"📝 Valid Rule<br/>Syntax?"}
    RULE_SYNTAX -->|"❌ No"| FIX_RULE_SYNTAX["🔧 Fix YAML<br/>Syntax"]
    RULE_SYNTAX -->|"✅ Yes"| RULE_SUCCESS["✅ Rules<br/>Fixed"]

    VALIDATION_FLOW --> EXPECTED_FAIL{"🤔 Expected<br/>Failure?"}
    EXPECTED_FAIL -->|"✅ Yes"| FIX_INFRA["🔧 Fix Infrastructure<br/>Configuration"]
    EXPECTED_FAIL -->|"❌ No"| CHECK_FILTERS["🔍 Check Rule<br/>Filters"]
    CHECK_FILTERS --> VALIDATION_SUCCESS["✅ Validation<br/>Fixed"]

    style ERROR fill:#ffffff,stroke:#f44336,stroke-width:3px,color:#000000
    style PARSE_SUCCESS fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style RULE_SUCCESS fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style VALIDATION_SUCCESS fill:#ffffff,stroke:#4caf50,stroke-width:3px,color:#000000
    style FIX_SYNTAX fill:#f8f9fa,stroke:#f44336,stroke-width:2px,color:#000000
    style FIX_PATH fill:#f8f9fa,stroke:#f44336,stroke-width:2px,color:#000000
    style CHECK_RULE_NAME fill:#f8f9fa,stroke:#ff9800,stroke-width:2px,color:#000000
    style FIX_RULE_SYNTAX fill:#f8f9fa,stroke:#ff9800,stroke-width:2px,color:#000000
    style FIX_INFRA fill:#f8f9fa,stroke:#2196f3,stroke-width:2px,color:#000000
    style CHECK_FILTERS fill:#f8f9fa,stroke:#2196f3,stroke-width:2px,color:#000000
```

## 📈 Before/After Examples

### S3 Bucket Security Validation

#### Before Fixing Issues
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Riveter Validation Results - aws-security Rule Pack                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ ❌ FAIL │ aws_s3_bucket.documents    │ S3 bucket must have encryption      │
│ ❌ FAIL │ aws_s3_bucket.documents    │ S3 bucket must block public access  │
│ ❌ FAIL │ aws_s3_bucket.documents    │ S3 bucket must have versioning      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Summary: 3 failures, 0 passed                                              │
│ Success Rate: 0%                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### After Fixing Issues
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Riveter Validation Results - aws-security Rule Pack                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✅ PASS │ aws_s3_bucket.documents    │ S3 bucket encryption enabled        │
│ ✅ PASS │ aws_s3_bucket.documents    │ S3 bucket public access blocked     │
│ ✅ PASS │ aws_s3_bucket.documents    │ S3 bucket versioning enabled        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Summary: 0 failures, 3 passed                                              │
│ Success Rate: 100%                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 CI/CD Integration Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Git as Git Repository
    participant CI as CI/CD Pipeline
    participant Riveter as Riveter
    participant Deploy as Deployment

    Dev->>Git: Push Terraform changes
    Git->>CI: Trigger pipeline
    CI->>Riveter: Run validation
    Riveter->>Riveter: Check against rule packs

    alt Validation Passes
        Riveter->>CI: ✅ All checks passed
        CI->>Deploy: Deploy infrastructure
        Deploy->>Dev: ✅ Deployment successful
    else Validation Fails
        Riveter->>CI: ❌ Issues found
        CI->>Dev: ❌ Block deployment + Report
        Dev->>Dev: Fix issues locally
        Dev->>Git: Push fixes
    end
```

## 🎨 Visual Design Standards

All diagrams follow consistent design principles:
- **Blue** (#1976d2): Input/source elements
- **Orange** (#f57c00): Processing/intermediate steps
- **Green** (#388e3c): Success/output states
- **Red** (#d32f2f): Error/failure states
- **Purple** (#7b1fa2): Information/secondary elements

## 📚 More Detailed Visuals

For comprehensive visual documentation including detailed architecture diagrams, advanced troubleshooting flows, and compliance framework mappings, see:

- **[Architecture Diagrams](../ARCHITECTURE_DIAGRAMS.md)** - Detailed system architecture
- **[Rule Evaluation Flowcharts](../RULE_EVALUATION_FLOWCHARTS.md)** - Complete evaluation processes
- **[Rule Pack Comparisons](../RULE_PACK_COMPARISONS.md)** - Comprehensive coverage analysis
- **[Visual Design System](../VISUAL_DESIGN_SYSTEM.md)** - Design standards and templates

---

*These visual guides provide quick understanding of Riveter's core concepts and processes.*
