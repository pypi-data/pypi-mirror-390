# Rule Evaluation Flowcharts

This document provides visual flowcharts for understanding how Riveter evaluates rules, selects rule packs, and troubleshoots common validation failures.

## Rule Matching and Evaluation Process

### Core Rule Evaluation Flow

```mermaid
flowchart TD
    START([Start Validation]) --> LOAD_TF[Load Terraform Config]
    LOAD_TF --> LOAD_RULES[Load Rules & Rule Packs]
    LOAD_RULES --> EXTRACT[Extract Resources]

    EXTRACT --> FOR_EACH{For Each Resource}
    FOR_EACH --> CHECK_TYPE{Resource Type Matches Rule?}

    CHECK_TYPE -->|No| NEXT_RULE[Next Rule]
    CHECK_TYPE -->|Yes| CHECK_FILTER{Passes Filters?}

    CHECK_FILTER -->|No| NEXT_RULE
    CHECK_FILTER -->|Yes| EVAL_ASSERT[Evaluate Assertions]

    EVAL_ASSERT --> ASSERT_RESULT{All Assertions Pass?}
    ASSERT_RESULT -->|Yes| PASS[✅ Rule Passes]
    ASSERT_RESULT -->|No| FAIL[❌ Rule Fails]

    PASS --> RECORD_PASS[Record Success]
    FAIL --> RECORD_FAIL[Record Failure]

    RECORD_PASS --> NEXT_RULE
    RECORD_FAIL --> NEXT_RULE

    NEXT_RULE --> MORE_RULES{More Rules?}
    MORE_RULES -->|Yes| CHECK_TYPE
    MORE_RULES -->|No| MORE_RESOURCES{More Resources?}

    MORE_RESOURCES -->|Yes| FOR_EACH
    MORE_RESOURCES -->|No| GENERATE[Generate Report]

    GENERATE --> END([End])

    style START fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style PASS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style FAIL fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style END fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

### Detailed Assertion Evaluation

```mermaid
flowchart TD
    ASSERT_START([Start Assertion Evaluation]) --> GET_PROP[Get Resource Property]
    GET_PROP --> PROP_EXISTS{Property Exists?}

    PROP_EXISTS -->|No| CHECK_REQUIRED{Required Property?}
    CHECK_REQUIRED -->|Yes| FAIL_MISSING[❌ Fail: Missing Required Property]
    CHECK_REQUIRED -->|No| PASS_OPTIONAL[✅ Pass: Optional Property]

    PROP_EXISTS -->|Yes| GET_OPERATOR[Determine Operator]
    GET_OPERATOR --> OPERATOR_TYPE{Operator Type}

    OPERATOR_TYPE -->|eq| EQUAL_CHECK[Check Equality]
    OPERATOR_TYPE -->|ne| NOT_EQUAL_CHECK[Check Not Equal]
    OPERATOR_TYPE -->|regex| REGEX_CHECK[Check Regex Pattern]
    OPERATOR_TYPE -->|gt/gte| GREATER_CHECK[Check Greater Than]
    OPERATOR_TYPE -->|lt/lte| LESS_CHECK[Check Less Than]
    OPERATOR_TYPE -->|contains| CONTAINS_CHECK[Check Contains]
    OPERATOR_TYPE -->|length| LENGTH_CHECK[Check Length]
    OPERATOR_TYPE -->|present| PRESENT_CHECK[Check Present]

    EQUAL_CHECK --> EQUAL_RESULT{Values Equal?}
    NOT_EQUAL_CHECK --> NOT_EQUAL_RESULT{Values Not Equal?}
    REGEX_CHECK --> REGEX_RESULT{Pattern Matches?}
    GREATER_CHECK --> GREATER_RESULT{Value Greater?}
    LESS_CHECK --> LESS_RESULT{Value Less?}
    CONTAINS_CHECK --> CONTAINS_RESULT{Contains Value?}
    LENGTH_CHECK --> LENGTH_RESULT{Length Valid?}
    PRESENT_CHECK --> PRESENT_RESULT{Property Present?}

    EQUAL_RESULT -->|Yes| PASS_ASSERT[✅ Assertion Passes]
    EQUAL_RESULT -->|No| FAIL_ASSERT[❌ Assertion Fails]

    NOT_EQUAL_RESULT -->|Yes| PASS_ASSERT
    NOT_EQUAL_RESULT -->|No| FAIL_ASSERT

    REGEX_RESULT -->|Yes| PASS_ASSERT
    REGEX_RESULT -->|No| FAIL_ASSERT

    GREATER_RESULT -->|Yes| PASS_ASSERT
    GREATER_RESULT -->|No| FAIL_ASSERT

    LESS_RESULT -->|Yes| PASS_ASSERT
    LESS_RESULT -->|No| FAIL_ASSERT

    CONTAINS_RESULT -->|Yes| PASS_ASSERT
    CONTAINS_RESULT -->|No| FAIL_ASSERT

    LENGTH_RESULT -->|Yes| PASS_ASSERT
    LENGTH_RESULT -->|No| FAIL_ASSERT

    PRESENT_RESULT -->|Yes| PASS_ASSERT
    PRESENT_RESULT -->|No| FAIL_ASSERT

    PASS_ASSERT --> MORE_ASSERTIONS{More Assertions?}
    FAIL_ASSERT --> FAIL_RULE[❌ Rule Fails]
    PASS_OPTIONAL --> MORE_ASSERTIONS
    FAIL_MISSING --> FAIL_RULE

    MORE_ASSERTIONS -->|Yes| GET_PROP
    MORE_ASSERTIONS -->|No| PASS_RULE[✅ Rule Passes]

    PASS_RULE --> ASSERT_END([End])
    FAIL_RULE --> ASSERT_END

    style ASSERT_START fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style PASS_ASSERT fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style FAIL_ASSERT fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style PASS_RULE fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style FAIL_RULE fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style ASSERT_END fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

## Rule Pack Selection Decision Tree

### Choosing the Right Rule Pack Combination

```mermaid
flowchart TD
    START([What do you want to validate?]) --> PURPOSE{Primary Purpose}

    PURPOSE -->|Security Best Practices| SECURITY_PATH[Security Focus]
    PURPOSE -->|Compliance Requirements| COMPLIANCE_PATH[Compliance Focus]
    PURPOSE -->|Architecture Quality| ARCHITECTURE_PATH[Architecture Focus]
    PURPOSE -->|Custom Policies| CUSTOM_PATH[Custom Rules Focus]

    SECURITY_PATH --> CLOUD_SEC{Which Cloud Provider?}
    CLOUD_SEC -->|AWS| AWS_SEC[aws-security + multi-cloud-security]
    CLOUD_SEC -->|Azure| AZURE_SEC[azure-security + multi-cloud-security]
    CLOUD_SEC -->|GCP| GCP_SEC[gcp-security + multi-cloud-security]
    CLOUD_SEC -->|Multi-Cloud| MULTI_SEC[multi-cloud-security]
    CLOUD_SEC -->|Kubernetes| K8S_SEC[kubernetes-security]

    COMPLIANCE_PATH --> FRAMEWORK{Compliance Framework}
    FRAMEWORK -->|CIS Benchmarks| CIS_PATH[CIS Focus]
    FRAMEWORK -->|HIPAA| HIPAA_RULES[aws-hipaa + azure-hipaa]
    FRAMEWORK -->|PCI-DSS| PCI_RULES[aws-pci-dss]
    FRAMEWORK -->|SOC 2| SOC2_RULES[soc2-security]
    FRAMEWORK -->|Multiple| MULTI_COMPLIANCE[Multiple Compliance Packs]

    CIS_PATH --> CIS_CLOUD{Which Cloud for CIS?}
    CIS_CLOUD -->|AWS| CIS_AWS[cis-aws]
    CIS_CLOUD -->|Azure| CIS_AZURE[cis-azure]
    CIS_CLOUD -->|GCP| CIS_GCP[cis-gcp]
    CIS_CLOUD -->|All| CIS_ALL[cis-aws + cis-azure + cis-gcp]

    ARCHITECTURE_PATH --> ARCH_CLOUD{Which Cloud Architecture?}
    ARCH_CLOUD -->|AWS| AWS_ARCH[aws-well-architected]
    ARCH_CLOUD -->|Azure| AZURE_ARCH[azure-well-architected]
    ARCH_CLOUD -->|GCP| GCP_ARCH[gcp-well-architected]
    ARCH_CLOUD -->|All| ALL_ARCH[All Well-Architected Packs]

    CUSTOM_PATH --> CUSTOM_COMBO{Combine with Standards?}
    CUSTOM_COMBO -->|Yes| CUSTOM_PLUS[Custom Rules + Rule Packs]
    CUSTOM_COMBO -->|No| CUSTOM_ONLY[Custom Rules Only]

    AWS_SEC --> COMBINE_AWS{Add Compliance?}
    AZURE_SEC --> COMBINE_AZURE{Add Compliance?}
    GCP_SEC --> COMBINE_GCP{Add Compliance?}

    COMBINE_AWS -->|Yes| AWS_FULL[aws-security + cis-aws + aws-well-architected]
    COMBINE_AWS -->|No| AWS_SEC_ONLY[aws-security only]

    COMBINE_AZURE -->|Yes| AZURE_FULL[azure-security + cis-azure + azure-well-architected]
    COMBINE_AZURE -->|No| AZURE_SEC_ONLY[azure-security only]

    COMBINE_GCP -->|Yes| GCP_FULL[gcp-security + cis-gcp + gcp-well-architected]
    COMBINE_GCP -->|No| GCP_SEC_ONLY[gcp-security only]

    style START fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style AWS_FULL fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style AZURE_FULL fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style GCP_FULL fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style MULTI_COMPLIANCE fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

### Rule Pack Recommendation Matrix

```mermaid
flowchart LR
    subgraph "Use Case Categories"
        STARTUP[Startup/Small Team]
        ENTERPRISE[Enterprise]
        HEALTHCARE[Healthcare]
        FINANCE[Financial Services]
        GOVERNMENT[Government]
    end

    subgraph "Recommended Combinations"
        STARTUP_RULES[aws-security + cis-aws]
        ENTERPRISE_RULES[Full Stack: Security + CIS + Well-Architected]
        HEALTHCARE_RULES[HIPAA + Security + CIS]
        FINANCE_RULES[PCI-DSS + SOC2 + Security + CIS]
        GOVERNMENT_RULES[All Compliance + Security + CIS]
    end

    STARTUP --> STARTUP_RULES
    ENTERPRISE --> ENTERPRISE_RULES
    HEALTHCARE --> HEALTHCARE_RULES
    FINANCE --> FINANCE_RULES
    GOVERNMENT --> GOVERNMENT_RULES

    style STARTUP fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style ENTERPRISE fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style HEALTHCARE fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style FINANCE fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style GOVERNMENT fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

## Troubleshooting Flowchart for Common Validation Failures

### General Troubleshooting Process

```mermaid
flowchart TD
    ERROR([Validation Error Occurred]) --> ERROR_TYPE{Error Type}

    ERROR_TYPE -->|Parse Error| PARSE_FLOW[Terraform Parsing Issues]
    ERROR_TYPE -->|Rule Error| RULE_FLOW[Rule Loading Issues]
    ERROR_TYPE -->|Validation Failure| VALIDATION_FLOW[Validation Failures]
    ERROR_TYPE -->|Output Error| OUTPUT_FLOW[Output Generation Issues]

    PARSE_FLOW --> CHECK_SYNTAX{Valid HCL Syntax?}
    CHECK_SYNTAX -->|No| FIX_SYNTAX[Fix Terraform Syntax Errors]
    CHECK_SYNTAX -->|Yes| CHECK_PATH{Correct File Path?}
    CHECK_PATH -->|No| FIX_PATH[Verify File Path and Permissions]
    CHECK_PATH -->|Yes| CHECK_VERSION{Compatible Terraform Version?}
    CHECK_VERSION -->|No| UPDATE_TF[Update Terraform or Use Compatible Syntax]
    CHECK_VERSION -->|Yes| PARSE_SUCCESS[✅ Parsing Fixed]

    RULE_FLOW --> RULE_EXISTS{Rule Pack/File Exists?}
    RULE_EXISTS -->|No| CHECK_RULE_PATH[Verify Rule Pack Name or File Path]
    RULE_EXISTS -->|Yes| RULE_SYNTAX{Valid Rule Syntax?}
    RULE_SYNTAX -->|No| FIX_RULE_SYNTAX[Fix YAML Syntax in Rules]
    RULE_SYNTAX -->|Yes| RULE_LOGIC{Valid Rule Logic?}
    RULE_LOGIC -->|No| FIX_RULE_LOGIC[Fix Rule Assertions and Filters]
    RULE_LOGIC -->|Yes| RULE_SUCCESS[✅ Rules Fixed]

    VALIDATION_FLOW --> EXPECTED_FAIL{Expected Failure?}
    EXPECTED_FAIL -->|Yes| FIX_INFRA[Fix Infrastructure Configuration]
    EXPECTED_FAIL -->|No| CHECK_RULE_MATCH{Rule Matches Resource Type?}
    CHECK_RULE_MATCH -->|No| VERIFY_RESOURCE[Verify Resource Type in Terraform]
    CHECK_RULE_MATCH -->|Yes| CHECK_FILTERS{Filters Applied Correctly?}
    CHECK_FILTERS -->|No| ADJUST_FILTERS[Adjust Rule Filters]
    CHECK_FILTERS -->|Yes| CHECK_ASSERTIONS{Assertions Correct?}
    CHECK_ASSERTIONS -->|No| FIX_ASSERTIONS[Fix Rule Assertions]
    CHECK_ASSERTIONS -->|Yes| VALIDATION_SUCCESS[✅ Validation Fixed]

    OUTPUT_FLOW --> CHECK_FORMAT{Valid Output Format?}
    CHECK_FORMAT -->|No| FIX_FORMAT[Use: table, json, junit, or sarif]
    CHECK_FORMAT -->|Yes| CHECK_PERMISSIONS{Write Permissions?}
    CHECK_PERMISSIONS -->|No| FIX_PERMISSIONS[Fix File/Directory Permissions]
    CHECK_PERMISSIONS -->|Yes| OUTPUT_SUCCESS[✅ Output Fixed]

    style ERROR fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style PARSE_SUCCESS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style RULE_SUCCESS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style VALIDATION_SUCCESS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style OUTPUT_SUCCESS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

### Specific Error Resolution Paths

#### "No Rules Loaded" Error

```mermaid
flowchart TD
    NO_RULES([Error: No rules loaded]) --> CHECK_ARGS{Command Arguments Correct?}

    CHECK_ARGS -->|Missing -r or -p| ADD_ARGS[Add --rules or --rule-pack argument]
    CHECK_ARGS -->|Arguments Present| CHECK_RULE_PACK{Using Rule Pack?}

    CHECK_RULE_PACK -->|Yes| LIST_PACKS[Run: riveter list-rule-packs]
    LIST_PACKS --> PACK_EXISTS{Pack in List?}
    PACK_EXISTS -->|No| USE_CORRECT_NAME[Use correct rule pack name]
    PACK_EXISTS -->|Yes| CHECK_PACK_FILE{Rule pack file exists?}
    CHECK_PACK_FILE -->|No| REINSTALL[Reinstall Riveter]
    CHECK_PACK_FILE -->|Yes| VALIDATE_PACK[Run: riveter validate-rule-pack]

    CHECK_RULE_PACK -->|No| CHECK_CUSTOM{Using Custom Rules?}
    CHECK_CUSTOM -->|Yes| FILE_EXISTS{Rule file exists?}
    FILE_EXISTS -->|No| CREATE_FILE[Create rule file or fix path]
    FILE_EXISTS -->|Yes| VALIDATE_CUSTOM[Validate YAML syntax]
    VALIDATE_CUSTOM --> YAML_VALID{Valid YAML?}
    YAML_VALID -->|No| FIX_YAML[Fix YAML syntax errors]
    YAML_VALID -->|Yes| RULES_VALID{Valid rule structure?}
    RULES_VALID -->|No| FIX_STRUCTURE[Fix rule structure]
    RULES_VALID -->|Yes| SUCCESS[✅ Rules should load]

    style NO_RULES fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style SUCCESS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

#### "Resource Type Not Found" Error

```mermaid
flowchart TD
    NO_RESOURCE([Error: Resource type not found]) --> CHECK_TF{Terraform File Valid?}

    CHECK_TF -->|No| FIX_TF_SYNTAX[Fix Terraform syntax]
    CHECK_TF -->|Yes| CHECK_RESOURCES{Resources Defined?}

    CHECK_RESOURCES -->|No| ADD_RESOURCES[Add resource definitions]
    CHECK_RESOURCES -->|Yes| CHECK_TYPE{Resource Type Matches Rule?}

    CHECK_TYPE -->|No| VERIFY_TYPE[Verify resource type in .tf file]
    VERIFY_TYPE --> TYPE_CORRECT{Type Spelling Correct?}
    TYPE_CORRECT -->|No| FIX_TYPE[Fix resource type spelling]
    TYPE_CORRECT -->|Yes| CHECK_RULE_TYPE{Rule Type Correct?}
    CHECK_RULE_TYPE -->|No| FIX_RULE_TYPE[Fix rule resource_type]
    CHECK_RULE_TYPE -->|Yes| CHECK_CASE{Case Sensitive Match?}
    CHECK_CASE -->|No| MATCH_CASE[Ensure exact case match]
    CHECK_CASE -->|Yes| RESOURCE_SUCCESS[✅ Resource type fixed]

    CHECK_TYPE -->|Yes| CHECK_FILTERS{Filters Excluding Resources?}
    CHECK_FILTERS -->|Yes| ADJUST_FILTERS[Adjust or remove filters]
    CHECK_FILTERS -->|No| RESOURCE_SUCCESS

    style NO_RESOURCE fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style RESOURCE_SUCCESS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

#### Performance Issues Troubleshooting

```mermaid
flowchart TD
    SLOW([Riveter Running Slowly]) --> CHECK_SIZE{Large Terraform Files?}

    CHECK_SIZE -->|Yes| SPLIT_FILES[Split into smaller files]
    CHECK_SIZE -->|No| CHECK_RULES{Many Rules/Rule Packs?}

    CHECK_RULES -->|Yes| REDUCE_RULES[Use fewer rule packs or targeted rules]
    CHECK_RULES -->|No| CHECK_RESOURCES{Many Resources?}

    CHECK_RESOURCES -->|Yes| USE_FILTERS[Add filters to rules to reduce scope]
    CHECK_RESOURCES -->|No| CHECK_INSTALLATION{Installation Method?}

    CHECK_INSTALLATION -->|Python/pip| USE_HOMEBREW[Switch to Homebrew installation]
    CHECK_INSTALLATION -->|Homebrew| CHECK_SYSTEM{System Resources?}

    CHECK_SYSTEM -->|Low Memory| INCREASE_MEMORY[Increase available memory]
    CHECK_SYSTEM -->|Slow Disk| USE_SSD[Use faster storage]
    CHECK_SYSTEM -->|OK| REPORT_ISSUE[Report performance issue]

    USE_HOMEBREW --> PERFORMANCE_IMPROVED[✅ Performance should improve]
    SPLIT_FILES --> PERFORMANCE_IMPROVED
    REDUCE_RULES --> PERFORMANCE_IMPROVED
    USE_FILTERS --> PERFORMANCE_IMPROVED

    style SLOW fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style PERFORMANCE_IMPROVED fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

## Rule Evaluation Examples

### Example: S3 Bucket Encryption Rule

```mermaid
flowchart TD
    START([S3 Bucket Encryption Rule]) --> LOAD_RESOURCE[Load aws_s3_bucket resource]
    LOAD_RESOURCE --> CHECK_TYPE{Resource type = aws_s3_bucket?}

    CHECK_TYPE -->|No| SKIP[Skip this rule]
    CHECK_TYPE -->|Yes| CHECK_FILTER{Environment = production?}

    CHECK_FILTER -->|No| SKIP
    CHECK_FILTER -->|Yes| CHECK_ENCRYPTION{server_side_encryption_configuration exists?}

    CHECK_ENCRYPTION -->|No| FAIL[❌ Fail: No encryption configured]
    CHECK_ENCRYPTION -->|Yes| CHECK_ALGORITHM{Algorithm = AES256 or aws:kms?}

    CHECK_ALGORITHM -->|No| FAIL_ALGORITHM[❌ Fail: Invalid encryption algorithm]
    CHECK_ALGORITHM -->|Yes| PASS[✅ Pass: Encryption properly configured]

    SKIP --> END([End])
    FAIL --> END
    FAIL_ALGORITHM --> END
    PASS --> END

    style START fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style PASS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style FAIL fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style FAIL_ALGORITHM fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style END fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

### Example: Multi-Condition Rule Evaluation

```mermaid
flowchart TD
    START([EC2 Instance Security Rule]) --> LOAD_EC2[Load aws_instance resource]
    LOAD_EC2 --> CHECK_TYPE{Resource type = aws_instance?}

    CHECK_TYPE -->|No| SKIP[Skip this rule]
    CHECK_TYPE -->|Yes| CHECK_ENV{tags.Environment = production?}

    CHECK_ENV -->|No| SKIP
    CHECK_ENV -->|Yes| CONDITION1{instance_type matches approved list?}

    CONDITION1 -->|No| FAIL1[❌ Fail: Invalid instance type]
    CONDITION1 -->|Yes| CONDITION2{associate_public_ip_address = false?}

    CONDITION2 -->|No| FAIL2[❌ Fail: Public IP not allowed]
    CONDITION2 -->|Yes| CONDITION3{monitoring = true?}

    CONDITION3 -->|No| FAIL3[❌ Fail: Monitoring required]
    CONDITION3 -->|Yes| CONDITION4{ebs_block_device.encrypted = true?}

    CONDITION4 -->|No| FAIL4[❌ Fail: EBS encryption required]
    CONDITION4 -->|Yes| PASS[✅ Pass: All security requirements met]

    SKIP --> END([End])
    FAIL1 --> END
    FAIL2 --> END
    FAIL3 --> END
    FAIL4 --> END
    PASS --> END

    style START fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style PASS fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style FAIL1 fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style FAIL2 fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style FAIL3 fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style FAIL4 fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style END fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

---

*These flowcharts provide step-by-step visual guidance for understanding rule evaluation, selecting appropriate rule packs, and troubleshooting common issues with Riveter.*
