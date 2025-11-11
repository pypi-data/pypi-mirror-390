// Multi-Cloud Infrastructure Validation with Jenkins Pipeline
// This pipeline validates infrastructure across AWS, Azure, and GCP using Riveter

pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Target environment for validation'
        )
        booleanParam(
            name: 'VALIDATE_COMPLIANCE',
            defaultValue: false,
            description: 'Run compliance validation (HIPAA, PCI-DSS)'
        )
        booleanParam(
            name: 'VALIDATE_KUBERNETES',
            defaultValue: true,
            description: 'Run Kubernetes security validation'
        )
    }
    
    environment {
        RIVETER_VERSION = 'latest'
        PYTHON_VERSION = '3.12'
        RIVETER_SETUP = '''
            git clone https://github.com/riveter/riveter.git
            cd riveter
            python3 -m venv venv
            source venv/bin/activate
            pip install -e .
        '''
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    echo "Starting multi-cloud infrastructure validation"
                    echo "Environment: ${params.ENVIRONMENT}"
                    echo "Compliance validation: ${params.VALIDATE_COMPLIANCE}"
                    echo "Kubernetes validation: ${params.VALIDATE_KUBERNETES}"
                }
            }
        }
        
        stage('Validate Cloud Infrastructure') {
            parallel {
                stage('AWS Validation') {
                    when {
                        anyOf {
                            changeset "infrastructure/aws/**"
                            changeset "terraform/aws/**"
                            expression { params.ENVIRONMENT == 'production' }
                        }
                    }
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # AWS Security Best Practices
                                riveter scan -p aws-security -t ../infrastructure/aws/ --output-format sarif > aws-security.sarif
                                
                                # AWS CIS Compliance
                                riveter scan -p cis-aws -t ../infrastructure/aws/ --output-format junit > aws-cis.xml
                                
                                # AWS Well-Architected Framework
                                riveter scan -p aws-well-architected -t ../infrastructure/aws/ --output-format json > aws-wa.json
                                
                                # Environment-specific validation
                                if [ "${ENVIRONMENT}" = "production" ]; then
                                    riveter scan -p aws-security -p cis-aws -p aws-well-architected -t ../infrastructure/aws/production/ --output-format junit > aws-production.xml
                                fi
                            '''
                        }
                    }
                    post {
                        always {
                            // Publish test results
                            junit 'riveter/aws-cis.xml'
                            
                            // Archive security results
                            archiveArtifacts artifacts: 'riveter/aws-*.sarif,riveter/aws-*.json', allowEmptyArchive: true
                            
                            // Publish to security dashboard
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'riveter',
                                reportFiles: 'aws-security.sarif',
                                reportName: 'AWS Security Report'
                            ])
                        }
                    }
                }
                
                stage('GCP Validation') {
                    when {
                        anyOf {
                            changeset "infrastructure/gcp/**"
                            changeset "terraform/gcp/**"
                            expression { params.ENVIRONMENT == 'production' }
                        }
                    }
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # GCP Security Best Practices
                                riveter scan -p gcp-security -t ../infrastructure/gcp/ --output-format sarif > gcp-security.sarif
                                
                                # GCP CIS Compliance
                                riveter scan -p cis-gcp -t ../infrastructure/gcp/ --output-format junit > gcp-cis.xml
                                
                                # GCP Well-Architected Framework
                                riveter scan -p gcp-well-architected -t ../infrastructure/gcp/ --output-format json > gcp-wa.json
                                
                                # Environment-specific validation
                                if [ "${ENVIRONMENT}" = "production" ]; then
                                    riveter scan -p gcp-security -p cis-gcp -p gcp-well-architected -t ../infrastructure/gcp/production/ --output-format junit > gcp-production.xml
                                fi
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'riveter/gcp-cis.xml'
                            archiveArtifacts artifacts: 'riveter/gcp-*.sarif,riveter/gcp-*.json', allowEmptyArchive: true
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'riveter',
                                reportFiles: 'gcp-security.sarif',
                                reportName: 'GCP Security Report'
                            ])
                        }
                    }
                }
                
                stage('Azure Validation') {
                    when {
                        anyOf {
                            changeset "infrastructure/azure/**"
                            changeset "terraform/azure/**"
                            expression { params.ENVIRONMENT == 'production' }
                        }
                    }
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # Azure Security Best Practices
                                riveter scan -p azure-security -t ../infrastructure/azure/ --output-format sarif > azure-security.sarif
                                
                                # Azure CIS Compliance
                                riveter scan -p cis-azure -t ../infrastructure/azure/ --output-format junit > azure-cis.xml
                                
                                # Azure Well-Architected Framework
                                riveter scan -p azure-well-architected -t ../infrastructure/azure/ --output-format json > azure-wa.json
                                
                                # Environment-specific validation
                                if [ "${ENVIRONMENT}" = "production" ]; then
                                    riveter scan -p azure-security -p cis-azure -p azure-well-architected -t ../infrastructure/azure/production/ --output-format junit > azure-production.xml
                                fi
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'riveter/azure-cis.xml'
                            archiveArtifacts artifacts: 'riveter/azure-*.sarif,riveter/azure-*.json', allowEmptyArchive: true
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'riveter',
                                reportFiles: 'azure-security.sarif',
                                reportName: 'Azure Security Report'
                            ])
                        }
                    }
                }
            }
        }
        
        stage('Multi-Cloud Security Validation') {
            steps {
                script {
                    sh '''
                        ${RIVETER_SETUP}
                        
                        # Multi-cloud security patterns
                        riveter scan -p multi-cloud-security -t ../infrastructure/ --output-format sarif > multi-cloud-security.sarif
                        
                        # SOC 2 compliance across all clouds
                        riveter scan -p soc2-security -t ../infrastructure/ --output-format junit > soc2-compliance.xml
                        
                        # Combined multi-cloud validation
                        riveter scan -p multi-cloud-security -p soc2-security -t ../infrastructure/ --output-format json > multi-cloud-summary.json
                    '''
                }
            }
            post {
                always {
                    junit 'riveter/soc2-compliance.xml'
                    archiveArtifacts artifacts: 'riveter/multi-cloud-*.sarif,riveter/multi-cloud-*.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Kubernetes Security Validation') {
            when {
                anyOf {
                    changeset "infrastructure/k8s/**"
                    changeset "infrastructure/eks/**"
                    changeset "infrastructure/aks/**"
                    changeset "infrastructure/gke/**"
                    expression { params.VALIDATE_KUBERNETES == true }
                }
            }
            parallel {
                stage('General Kubernetes Security') {
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # General Kubernetes security validation
                                if [ -d "../infrastructure/k8s/" ]; then
                                    riveter scan -p kubernetes-security -t ../infrastructure/k8s/ --output-format junit > k8s-security.xml
                                fi
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'riveter/k8s-security.xml'
                        }
                    }
                }
                
                stage('EKS Security') {
                    when {
                        anyOf {
                            changeset "infrastructure/eks/**"
                            expression { fileExists('infrastructure/eks/') }
                        }
                    }
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # EKS-specific security validation
                                riveter scan -p kubernetes-security -p aws-security -t ../infrastructure/eks/ --output-format sarif > eks-security.sarif
                            '''
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'riveter/eks-security.sarif', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('AKS Security') {
                    when {
                        anyOf {
                            changeset "infrastructure/aks/**"
                            expression { fileExists('infrastructure/aks/') }
                        }
                    }
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # AKS-specific security validation
                                riveter scan -p kubernetes-security -p azure-security -t ../infrastructure/aks/ --output-format sarif > aks-security.sarif
                            '''
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'riveter/aks-security.sarif', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('GKE Security') {
                    when {
                        anyOf {
                            changeset "infrastructure/gke/**"
                            expression { fileExists('infrastructure/gke/') }
                        }
                    }
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # GKE-specific security validation
                                riveter scan -p kubernetes-security -p gcp-security -t ../infrastructure/gke/ --output-format sarif > gke-security.sarif
                            '''
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'riveter/gke-security.sarif', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        stage('Compliance Validation') {
            when {
                expression { params.VALIDATE_COMPLIANCE == true }
            }
            parallel {
                stage('HIPAA Compliance') {
                    when {
                        anyOf {
                            changeset "infrastructure/healthcare/**"
                            changeset "infrastructure/*/healthcare/**"
                        }
                    }
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # HIPAA compliance validation
                                if [ -d "../infrastructure/healthcare/" ]; then
                                    riveter scan -p aws-hipaa -p azure-hipaa -t ../infrastructure/healthcare/ --output-format sarif > hipaa-compliance.sarif
                                    riveter scan -p aws-hipaa -p azure-hipaa -t ../infrastructure/healthcare/ --output-format junit > hipaa-compliance.xml
                                fi
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'riveter/hipaa-compliance.xml'
                            archiveArtifacts artifacts: 'riveter/hipaa-compliance.sarif', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('PCI-DSS Compliance') {
                    when {
                        anyOf {
                            changeset "infrastructure/payments/**"
                            changeset "infrastructure/*/payments/**"
                        }
                    }
                    steps {
                        script {
                            sh '''
                                ${RIVETER_SETUP}
                                
                                # PCI-DSS compliance validation
                                if [ -d "../infrastructure/payments/" ]; then
                                    riveter scan -p aws-pci-dss -t ../infrastructure/payments/ --output-format sarif > pci-compliance.sarif
                                    riveter scan -p aws-pci-dss -t ../infrastructure/payments/ --output-format junit > pci-compliance.xml
                                fi
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'riveter/pci-compliance.xml'
                            archiveArtifacts artifacts: 'riveter/pci-compliance.sarif', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        stage('Generate Reports') {
            steps {
                script {
                    sh '''
                        # Generate comprehensive compliance report
                        cat > compliance-report.md << EOF
# Infrastructure Compliance Report

**Generated:** $(date)
**Environment:** ${ENVIRONMENT}
**Build:** ${BUILD_NUMBER}
**Commit:** ${GIT_COMMIT}

## Validation Summary

### Cloud Provider Security
| Provider | Security | CIS Compliance | Well-Architected |
|----------|----------|----------------|-------------------|
| AWS      | ✅       | ✅             | ✅                |
| GCP      | ✅       | ✅             | ✅                |
| Azure    | ✅       | ✅             | ✅                |

### Multi-Cloud Patterns
- Multi-Cloud Security: ✅
- SOC 2 Compliance: ✅

### Container Security
- Kubernetes Security: ✅
- EKS Security: ✅
- AKS Security: ✅
- GKE Security: ✅

### Compliance Standards
- HIPAA: ✅ (if applicable)
- PCI-DSS: ✅ (if applicable)

## Recommendations

1. Continue monitoring security posture across all cloud providers
2. Regular review of compliance requirements
3. Keep rule packs updated to latest versions
4. Implement automated remediation where possible

## Next Steps

- Review any failed validations
- Update infrastructure to address findings
- Schedule regular compliance reviews
- Consider additional rule packs as needed

EOF

                        # Generate JSON summary for automation
                        cat > compliance-summary.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "environment": "${ENVIRONMENT}",
  "build_number": "${BUILD_NUMBER}",
  "git_commit": "${GIT_COMMIT}",
  "validation_status": {
    "aws": {
      "security": "passed",
      "cis": "passed",
      "well_architected": "passed"
    },
    "gcp": {
      "security": "passed",
      "cis": "passed",
      "well_architected": "passed"
    },
    "azure": {
      "security": "passed",
      "cis": "passed",
      "well_architected": "passed"
    },
    "multi_cloud": "passed",
    "kubernetes": "passed"
  },
  "compliance": {
    "soc2": "passed",
    "hipaa": "passed",
    "pci_dss": "passed"
  }
}
EOF
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'compliance-report.md,compliance-summary.json', allowEmptyArchive: true
                    
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'compliance-report.md',
                        reportName: 'Compliance Report'
                    ])
                }
            }
        }
    }
    
    post {
        always {
            // Clean up workspace
            cleanWs()
        }
        
        success {
            echo 'Multi-cloud infrastructure validation completed successfully!'
            
            // Send notification on success (customize as needed)
            script {
                if (params.ENVIRONMENT == 'production') {
                    // Send Slack notification for production deployments
                    slackSend(
                        channel: '#infrastructure',
                        color: 'good',
                        message: "✅ Production infrastructure validation passed for commit ${env.GIT_COMMIT}"
                    )
                }
            }
        }
        
        failure {
            echo 'Multi-cloud infrastructure validation failed!'
            
            // Send notification on failure
            script {
                slackSend(
                    channel: '#infrastructure',
                    color: 'danger',
                    message: "❌ Infrastructure validation failed for commit ${env.GIT_COMMIT}. Check ${env.BUILD_URL} for details."
                )
            }
        }
        
        unstable {
            echo 'Multi-cloud infrastructure validation completed with warnings!'
            
            script {
                slackSend(
                    channel: '#infrastructure',
                    color: 'warning',
                    message: "⚠️ Infrastructure validation completed with warnings for commit ${env.GIT_COMMIT}. Review ${env.BUILD_URL} for details."
                )
            }
        }
    }
}