# Changelog

All notable changes to Riveter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 📦 **Rule Pack System**: Pre-built compliance rule collections
- 🔒 **AWS Security Best Practices**: 26 comprehensive security rules
- 📋 **CIS Compliance**: AWS and Azure Foundations Benchmark rules
- 🛡️ **SOC 2 Security**: Trust Service Criteria compliance rules
- 🔧 **Rule Pack Management**: CLI commands for rule pack operations
- ⚡ **Advanced Operators**: regex, comparisons, length, subset validation
- 🎯 **Rule Filtering**: Filter by severity, resource type, and tags
- 🔄 **Rule Pack Merging**: Combine multiple rule packs seamlessly
- 📊 **Multiple Output Formats**: Table, JSON, JUnit XML, and SARIF
- 🧪 **Comprehensive Testing**: 70+ tests with extensive coverage

#### 🌐 **Comprehensive Cloud Rule Packs** (New in this release)
- 🔒 **GCP Security Best Practices**: 29 security rules for Google Cloud Platform
- 📋 **CIS GCP Benchmark**: 43 rules for CIS Google Cloud Platform Foundation Benchmark v1.3.0
- 🔒 **Azure Security Best Practices**: 28 security rules for Microsoft Azure
- 🏗️ **AWS Well-Architected Framework**: 34 rules covering all 6 pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability)
- 🏗️ **Azure Well-Architected Framework**: 35 rules covering all 5 pillars (Cost Optimization, Operational Excellence, Performance Efficiency, Reliability, Security)
- 🏗️ **GCP Well-Architected Framework**: 30 rules covering all 5 pillars (Operational Excellence, Security, Reliability, Performance, Cost Optimization)
- 🏥 **AWS HIPAA Compliance**: 35 rules for healthcare data protection requirements
- 🏥 **Azure HIPAA Compliance**: 30 rules for healthcare data protection requirements
- 💳 **AWS PCI-DSS Compliance**: 40 rules for Payment Card Industry Data Security Standard requirements
- ☁️ **Multi-Cloud Security**: 40 rules for common security patterns across AWS, Azure, and GCP
- 🐳 **Kubernetes Security**: 40 rules for container and Kubernetes security across EKS, AKS, and GKE

### Enhanced
- 🚀 **CLI Interface**: Improved usability and error messages
- 📖 **Documentation**: Complete rewrite with examples and use cases
- 🔍 **Validation Engine**: More robust rule processing and error handling

## [0.1.0] - 2024-01-01

### Added
- 🎯 **Core Validation Engine**: Basic rule parsing and Terraform validation
- 📝 **YAML Rule Format**: Simple, readable rule definitions
- 🖥️ **CLI Interface**: Command-line tool for validation
- 📊 **Basic Reporting**: Terminal output with validation results
- 🔧 **Terraform Parser**: HCL2 configuration parsing
- ✅ **Test Framework**: Initial test suite and CI/CD setup

### Technical
- Python 3.12+ support
- HCL2 parsing with python-hcl2
- Rich terminal output
- Click-based CLI
- Comprehensive type hints
- Pre-commit hooks for code quality

---

## Legend

- 📦 Rule Packs
- 🔒 Security
- 📋 Compliance
- 🛡️ Trust & Safety
- 🔧 Tools & CLI
- ⚡ Performance
- 🎯 Features
- 🔄 Integration
- 📊 Reporting
- 🧪 Testing
- 🚀 User Experience
- 📖 Documentation
- 🔍 Core Engine
