# Architecture Diagrams

This document contains comprehensive visual documentation of Riveter's architecture, workflow, and integration patterns.

## High-Level System Architecture

### Terraform → Riveter → Results Flow

```mermaid
graph TD
    A[Terraform Files] --> B[HCL Parser]
    C[Rule Packs] --> D[Rule Engine]
    E[Custom Rules] --> D

    B --> F[Resource Extractor]
    F --> G[Validation Engine]
    D --> G

    G --> H[Results Processor]
    H --> I[Terminal Output]
    H --> J[JSON Export]
    H --> K[SARIF Export]
    H --> L[JUnit XML]

    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style C fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style G fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style I fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style J fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style K fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style L fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

**Component Descriptions:**
- **Terraform Files**: Infrastructure as Code definitions in HCL format
- **HCL Parser**: Converts Terraform syntax into structured data
- **Rule Packs**: Pre-built compliance and security rule collections
- **Custom Rules**: Organization-specific validation rules
- **Rule Engine**: Loads and processes all rule definitions
- **Resource Extractor**: Identifies and categorizes infrastructure resources
- **Validation Engine**: Core logic that evaluates resources against rules
- **Results Processor**: Formats validation results for different outputs

## Detailed Component Architecture

### Internal Module Interactions

```mermaid
graph TB
    subgraph "CLI Layer"
        CLI[cli.py]
    end

    subgraph "Core Processing"
        CONFIG[extract_config.py]
        RULES[rules.py]
        PACKS[rule_packs.py]
        SCANNER[scanner.py]
        REPORTER[reporter.py]
    end

    subgraph "Data Sources"
        TF[Terraform Files]
        RP[Rule Pack Files]
        CR[Custom Rules]
    end

    subgraph "Output Formats"
        TABLE[Table Output]
        JSON[JSON Output]
        JUNIT[JUnit XML]
        SARIF[SARIF Output]
    end

    CLI --> CONFIG
    CLI --> RULES
    CLI --> PACKS
    CLI --> SCANNER
    CLI --> REPORTER

    TF --> CONFIG
    RP --> PACKS
    CR --> RULES

    CONFIG --> SCANNER
    RULES --> SCANNER
    PACKS --> SCANNER

    SCANNER --> REPORTER
    REPORTER --> TABLE
    REPORTER --> JSON
    REPORTER --> JUNIT
    REPORTER --> SARIF

    style CLI fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style CONFIG fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style RULES fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style PACKS fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style SCANNER fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style REPORTER fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

**Module Responsibilities:**
- **cli.py**: Command-line interface and argument parsing
- **extract_config.py**: Terraform HCL parsing and resource extraction
- **rules.py**: Custom rule loading and validation
- **rule_packs.py**: Pre-built rule pack management
- **scanner.py**: Core validation logic and rule evaluation
- **reporter.py**: Result formatting and output generation

## Deployment Architecture

### CI/CD Integration Patterns

```mermaid
graph TD
    subgraph "Development Environment"
        DEV[Developer Workstation]
        LOCAL[Local Validation]
    end

    subgraph "Version Control"
        GIT[Git Repository]
        PR[Pull Request]
    end

    subgraph "CI/CD Pipeline"
        CI[CI/CD System]
        RIVETER[Riveter Validation]
        GATE[Quality Gate]
    end

    subgraph "Deployment Targets"
        STAGING[Staging Environment]
        PROD[Production Environment]
    end

    subgraph "Monitoring & Compliance"
        DASHBOARD[Security Dashboard]
        AUDIT[Audit Reports]
        ALERTS[Compliance Alerts]
    end

    DEV --> LOCAL
    LOCAL --> GIT
    GIT --> PR
    PR --> CI
    CI --> RIVETER
    RIVETER --> GATE

    GATE -->|Pass| STAGING
    GATE -->|Fail| PR
    STAGING --> PROD

    RIVETER --> DASHBOARD
    RIVETER --> AUDIT
    RIVETER --> ALERTS

    style DEV fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style LOCAL fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style RIVETER fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style GATE fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style STAGING fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style PROD fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

### Multi-Environment Validation Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Local as Local Riveter
    participant Git as Git Repository
    participant CI as CI/CD Pipeline
    participant Riveter as Riveter Service
    participant Deploy as Deployment

    Dev->>Local: riveter scan -p aws-security -t main.tf
    Local->>Dev: ✅ Local validation passed
    Dev->>Git: git push origin feature-branch
    Git->>CI: Trigger pipeline
    CI->>Riveter: Run validation with multiple rule packs

    alt Validation Passes
        Riveter->>CI: ✅ All checks passed
        CI->>Deploy: Deploy to staging
        Deploy->>CI: ✅ Staging deployment successful
        CI->>Deploy: Deploy to production
        Deploy->>Dev: ✅ Production deployment successful
    else Validation Fails
        Riveter->>CI: ❌ Issues found
        CI->>Git: Update PR with failure details
        Git->>Dev: ❌ Deployment blocked - fix required
        Dev->>Local: Fix issues locally
        Dev->>Git: Push fixes
    end
```

## Container and Kubernetes Architecture

### Kubernetes Integration Pattern

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Namespace: riveter-system"
            POD[Riveter Pod]
            CONFIG[ConfigMap]
            SECRET[Secret]
        end

        subgraph "Namespace: applications"
            APP1[Application 1]
            APP2[Application 2]
        end
    end

    subgraph "External Systems"
        REGISTRY[Container Registry]
        TERRAFORM[Terraform Cloud]
        DASHBOARD[Security Dashboard]
    end

    subgraph "Rule Sources"
        BUILTIN[Built-in Rule Packs]
        CUSTOM[Custom Rules]
        COMPLIANCE[Compliance Frameworks]
    end

    REGISTRY --> POD
    TERRAFORM --> POD
    CONFIG --> POD
    SECRET --> POD

    BUILTIN --> CONFIG
    CUSTOM --> CONFIG
    COMPLIANCE --> CONFIG

    POD --> DASHBOARD
    POD --> APP1
    POD --> APP2

    style POD fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style CONFIG fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style SECRET fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style DASHBOARD fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

### Docker Container Architecture

```mermaid
graph LR
    subgraph "Riveter Container"
        BINARY[Riveter Binary]
        RULES[Rule Packs]
        CONFIG[Configuration]
    end

    subgraph "Mounted Volumes"
        WORKSPACE[/workspace]
        RESULTS[/results]
    end

    subgraph "Host System"
        TF_FILES[Terraform Files]
        OUTPUT[Output Files]
    end

    TF_FILES --> WORKSPACE
    WORKSPACE --> BINARY
    RULES --> BINARY
    CONFIG --> BINARY
    BINARY --> RESULTS
    RESULTS --> OUTPUT

    style BINARY fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style WORKSPACE fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style RESULTS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

## Multi-Cloud Architecture Patterns

### Cross-Cloud Validation Strategy

```mermaid
graph TD
    subgraph "Infrastructure Sources"
        AWS_TF[AWS Terraform]
        AZURE_TF[Azure Terraform]
        GCP_TF[GCP Terraform]
        K8S_TF[Kubernetes Terraform]
    end

    subgraph "Riveter Validation Engine"
        PARSER[Multi-Cloud Parser]
        VALIDATOR[Validation Engine]
    end

    subgraph "Rule Pack Matrix"
        AWS_RULES[AWS Rule Packs]
        AZURE_RULES[Azure Rule Packs]
        GCP_RULES[GCP Rule Packs]
        MULTI_RULES[Multi-Cloud Rules]
        COMPLIANCE[Compliance Rules]
    end

    subgraph "Validation Results"
        AWS_RESULTS[AWS Results]
        AZURE_RESULTS[Azure Results]
        GCP_RESULTS[GCP Results]
        UNIFIED[Unified Report]
    end

    AWS_TF --> PARSER
    AZURE_TF --> PARSER
    GCP_TF --> PARSER
    K8S_TF --> PARSER

    PARSER --> VALIDATOR

    AWS_RULES --> VALIDATOR
    AZURE_RULES --> VALIDATOR
    GCP_RULES --> VALIDATOR
    MULTI_RULES --> VALIDATOR
    COMPLIANCE --> VALIDATOR

    VALIDATOR --> AWS_RESULTS
    VALIDATOR --> AZURE_RESULTS
    VALIDATOR --> GCP_RESULTS
    VALIDATOR --> UNIFIED

    style PARSER fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style VALIDATOR fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style UNIFIED fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

## Performance and Scalability Architecture

### Parallel Processing Model

```mermaid
graph TB
    subgraph "Input Processing"
        INPUT[Terraform Files]
        SPLITTER[File Splitter]
    end

    subgraph "Parallel Validation Workers"
        WORKER1[Worker 1]
        WORKER2[Worker 2]
        WORKER3[Worker 3]
        WORKERN[Worker N]
    end

    subgraph "Rule Distribution"
        RULE_CACHE[Rule Cache]
        PACK_LOADER[Pack Loader]
    end

    subgraph "Result Aggregation"
        COLLECTOR[Result Collector]
        FORMATTER[Output Formatter]
        OUTPUT[Final Results]
    end

    INPUT --> SPLITTER
    SPLITTER --> WORKER1
    SPLITTER --> WORKER2
    SPLITTER --> WORKER3
    SPLITTER --> WORKERN

    PACK_LOADER --> RULE_CACHE
    RULE_CACHE --> WORKER1
    RULE_CACHE --> WORKER2
    RULE_CACHE --> WORKER3
    RULE_CACHE --> WORKERN

    WORKER1 --> COLLECTOR
    WORKER2 --> COLLECTOR
    WORKER3 --> COLLECTOR
    WORKERN --> COLLECTOR

    COLLECTOR --> FORMATTER
    FORMATTER --> OUTPUT

    style SPLITTER fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style RULE_CACHE fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style COLLECTOR fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style OUTPUT fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

## Security Architecture

### Security Validation Pipeline

```mermaid
graph LR
    subgraph "Security Layers"
        INPUT_VAL[Input Validation]
        RULE_VAL[Rule Validation]
        EXEC_SEC[Execution Security]
        OUTPUT_SEC[Output Security]
    end

    subgraph "Threat Mitigation"
        SANDBOX[Sandboxed Execution]
        AUDIT[Audit Logging]
        ENCRYPT[Result Encryption]
    end

    subgraph "Compliance Integration"
        SARIF_OUT[SARIF Output]
        SECURITY_HUB[Security Hub]
        COMPLIANCE_DASH[Compliance Dashboard]
    end

    INPUT_VAL --> RULE_VAL
    RULE_VAL --> EXEC_SEC
    EXEC_SEC --> OUTPUT_SEC

    EXEC_SEC --> SANDBOX
    EXEC_SEC --> AUDIT
    OUTPUT_SEC --> ENCRYPT

    OUTPUT_SEC --> SARIF_OUT
    SARIF_OUT --> SECURITY_HUB
    SARIF_OUT --> COMPLIANCE_DASH

    style INPUT_VAL fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style RULE_VAL fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style EXEC_SEC fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style OUTPUT_SEC fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style SANDBOX fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style AUDIT fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

## Integration Architecture Patterns

### Enterprise Integration Model

```mermaid
graph TB
    subgraph "Development Tools"
        IDE[IDE/Editor]
        CLI[Command Line]
        TERRAFORM[Terraform CLI]
    end

    subgraph "CI/CD Platforms"
        GITHUB[GitHub Actions]
        GITLAB[GitLab CI]
        JENKINS[Jenkins]
        AZURE_DEVOPS[Azure DevOps]
    end

    subgraph "Riveter Core"
        ENGINE[Validation Engine]
        RULES[Rule Engine]
        REPORTER[Reporter]
    end

    subgraph "Security Ecosystem"
        SONAR[SonarQube]
        SNYK[Snyk]
        SECURITY_HUB[AWS Security Hub]
        DEFENDER[Azure Defender]
    end

    subgraph "Compliance Tools"
        AUDIT[Audit Systems]
        GRC[GRC Platforms]
        DASHBOARD[Compliance Dashboards]
    end

    IDE --> ENGINE
    CLI --> ENGINE
    TERRAFORM --> ENGINE

    GITHUB --> ENGINE
    GITLAB --> ENGINE
    JENKINS --> ENGINE
    AZURE_DEVOPS --> ENGINE

    ENGINE --> RULES
    ENGINE --> REPORTER

    REPORTER --> SONAR
    REPORTER --> SNYK
    REPORTER --> SECURITY_HUB
    REPORTER --> DEFENDER

    REPORTER --> AUDIT
    REPORTER --> GRC
    REPORTER --> DASHBOARD

    style ENGINE fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style RULES fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style REPORTER fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

---

*These architecture diagrams provide a comprehensive view of how Riveter integrates into modern infrastructure and security workflows.*
