# Kubernetes Security Test Fixtures
# This file contains both passing and failing examples for kubernetes-security rule pack
# Covers EKS (AWS), AKS (Azure), and GKE (GCP)

# ============================================================================
# EKS (AWS) RESOURCES
# ============================================================================

# PASS: EKS cluster with security best practices
resource "aws_eks_cluster" "secure_eks" {
  name     = "secure-eks-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.27"

  vpc_config {
    subnet_ids              = ["subnet-12345", "subnet-67890"]
    endpoint_private_access = true
    endpoint_public_access  = false
    security_group_ids      = ["sg-12345"]
  }

  encryption_config {
    provider {
      key_arn = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    }
    resources = ["secrets"]
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  tags = {
    Environment = "production"
    Owner       = "platform-team"
  }
}

# FAIL: EKS cluster with public endpoint
resource "aws_eks_cluster" "public_endpoint_eks" {
  name     = "public-endpoint-eks"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids              = ["subnet-12345", "subnet-67890"]
    endpoint_private_access = true
    endpoint_public_access  = true
  }
}

# FAIL: EKS cluster without secrets encryption
resource "aws_eks_cluster" "no_encryption_eks" {
  name     = "no-encryption-eks"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = ["subnet-12345", "subnet-67890"]
  }
}

# FAIL: EKS cluster without logging enabled
resource "aws_eks_cluster" "no_logging_eks" {
  name     = "no-logging-eks"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = ["subnet-12345", "subnet-67890"]
  }

  enabled_cluster_log_types = []
}

# PASS: EKS node group with security best practices
resource "aws_eks_node_group" "secure_node_group" {
  cluster_name    = aws_eks_cluster.secure_eks.name
  node_group_name = "secure-node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = ["subnet-12345", "subnet-67890"]

  scaling_config {
    desired_size = 2
    max_size     = 4
    min_size     = 2
  }

  launch_template {
    id      = aws_launch_template.eks_nodes.id
    version = "$Latest"
  }

  tags = {
    Environment = "production"
  }
}

# ============================================================================
# AKS (AZURE) RESOURCES
# ============================================================================

# PASS: AKS cluster with security best practices
resource "azurerm_kubernetes_cluster" "secure_aks" {
  name                = "secure-aks-cluster"
  location            = "East US"
  resource_group_name = "test-resources"
  dns_prefix          = "secure-aks"
  kubernetes_version  = "1.27"

  default_node_pool {
    name                = "default"
    node_count          = 2
    vm_size             = "Standard_D2s_v3"
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 4
    vnet_subnet_id      = "subnet-id"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
  }

  azure_policy_enabled = true

  oms_agent {
    log_analytics_workspace_id = "workspace-id"
  }

  role_based_access_control_enabled = true

  azure_active_directory_role_based_access_control {
    managed                = true
    azure_rbac_enabled     = true
    admin_group_object_ids = ["00000000-0000-0000-0000-000000000000"]
  }

  private_cluster_enabled = true

  tags = {
    Environment = "production"
    Owner       = "platform-team"
  }
}

# FAIL: AKS cluster without network policy
resource "azurerm_kubernetes_cluster" "no_network_policy_aks" {
  name                = "no-network-policy-aks"
  location            = "East US"
  resource_group_name = "test-resources"
  dns_prefix          = "no-network-policy"

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
  }
}

# FAIL: AKS cluster without RBAC enabled
resource "azurerm_kubernetes_cluster" "no_rbac_aks" {
  name                = "no-rbac-aks"
  location            = "East US"
  resource_group_name = "test-resources"
  dns_prefix          = "no-rbac"

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }

  role_based_access_control_enabled = false
}

# FAIL: AKS cluster without private cluster enabled
resource "azurerm_kubernetes_cluster" "public_aks" {
  name                = "public-aks"
  location            = "East US"
  resource_group_name = "test-resources"
  dns_prefix          = "public"

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }

  private_cluster_enabled = false
}

# ============================================================================
# GKE (GCP) RESOURCES
# ============================================================================

# PASS: GKE cluster with security best practices
resource "google_container_cluster" "secure_gke" {
  name     = "secure-gke-cluster"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = "default"
  subnetwork = "default"

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "10.0.0.0/16"
    services_ipv4_cidr_block = "10.1.0.0/16"
  }

  network_policy {
    enabled  = true
    provider = "CALICO"
  }

  addons_config {
    network_policy_config {
      disabled = false
    }
  }

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  workload_identity_config {
    workload_pool = "project-id.svc.id.goog"
  }

  database_encryption {
    state    = "ENCRYPTED"
    key_name = "projects/project-id/locations/us-central1/keyRings/gke/cryptoKeys/gke-key"
  }

  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }

  enable_shielded_nodes = true
  enable_legacy_abac    = false

  resource_labels = {
    environment = "production"
    owner       = "platform-team"
  }
}

# FAIL: GKE cluster without private nodes
resource "google_container_cluster" "public_gke" {
  name     = "public-gke-cluster"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1

  network_policy {
    enabled = true
  }
}

# FAIL: GKE cluster without network policy
resource "google_container_cluster" "no_network_policy_gke" {
  name     = "no-network-policy-gke"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1

  private_cluster_config {
    enable_private_nodes = true
  }

  network_policy {
    enabled = false
  }
}

# FAIL: GKE cluster with legacy ABAC enabled
resource "google_container_cluster" "legacy_abac_gke" {
  name     = "legacy-abac-gke"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1

  enable_legacy_abac = true
}

# FAIL: GKE cluster without workload identity
resource "google_container_cluster" "no_workload_identity_gke" {
  name     = "no-workload-identity-gke"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1

  private_cluster_config {
    enable_private_nodes = true
  }
}

# PASS: GKE node pool with security best practices
resource "google_container_node_pool" "secure_node_pool" {
  name       = "secure-node-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.secure_gke.name
  node_count = 2

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 100
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    service_account = "gke-nodes@project-id.iam.gserviceaccount.com"

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }

    labels = {
      environment = "production"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# ============================================================================
# KUBERNETES RESOURCES (PROVIDER-AGNOSTIC)
# ============================================================================

# PASS: Pod with security best practices
resource "kubernetes_pod" "secure_pod" {
  metadata {
    name      = "secure-pod"
    namespace = "production"

    labels = {
      app = "secure-app"
    }
  }

  spec {
    service_account_name = "app-service-account"

    security_context {
      run_as_non_root = true
      run_as_user     = 1000
      fs_group        = 2000
      seccomp_profile {
        type = "RuntimeDefault"
      }
    }

    container {
      name  = "app"
      image = "myregistry.io/myapp:v1.0.0"

      security_context {
        allow_privilege_escalation = false
        privileged                 = false
        read_only_root_filesystem  = true
        run_as_non_root            = true
        run_as_user                = 1000

        capabilities {
          drop = ["ALL"]
        }
      }

      resources {
        limits = {
          cpu    = "500m"
          memory = "512Mi"
        }
        requests = {
          cpu    = "250m"
          memory = "256Mi"
        }
      }

      volume_mount {
        name       = "tmp"
        mount_path = "/tmp"
      }
    }

    volume {
      name = "tmp"
      empty_dir {}
    }
  }
}

# FAIL: Pod with privileged container
resource "kubernetes_pod" "privileged_pod" {
  metadata {
    name      = "privileged-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:latest"

      security_context {
        privileged = true
      }
    }
  }
}

# FAIL: Pod running as root
resource "kubernetes_pod" "root_pod" {
  metadata {
    name      = "root-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:latest"

      security_context {
        run_as_user = 0
      }
    }
  }
}

# FAIL: Pod without resource limits
resource "kubernetes_pod" "no_limits_pod" {
  metadata {
    name      = "no-limits-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:latest"
    }
  }
}

# FAIL: Pod with writable root filesystem
resource "kubernetes_pod" "writable_root_pod" {
  metadata {
    name      = "writable-root-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:latest"

      security_context {
        read_only_root_filesystem = false
      }
    }
  }
}

# PASS: Deployment with security best practices
resource "kubernetes_deployment" "secure_deployment" {
  metadata {
    name      = "secure-deployment"
    namespace = "production"

    labels = {
      app = "secure-app"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "secure-app"
      }
    }

    template {
      metadata {
        labels = {
          app = "secure-app"
        }
      }

      spec {
        service_account_name = "app-service-account"

        security_context {
          run_as_non_root = true
          run_as_user     = 1000
          fs_group        = 2000
        }

        container {
          name  = "app"
          image = "myregistry.io/myapp:v1.0.0"

          security_context {
            allow_privilege_escalation = false
            privileged                 = false
            read_only_root_filesystem  = true
            run_as_non_root            = true

            capabilities {
              drop = ["ALL"]
            }
          }

          resources {
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "256Mi"
            }
          }
        }
      }
    }
  }
}

# PASS: Network Policy with default deny
resource "kubernetes_network_policy" "default_deny_ingress" {
  metadata {
    name      = "default-deny-ingress"
    namespace = "production"
  }

  spec {
    pod_selector {}

    policy_types = ["Ingress"]
  }
}

# PASS: Network Policy allowing specific traffic
resource "kubernetes_network_policy" "allow_app_traffic" {
  metadata {
    name      = "allow-app-traffic"
    namespace = "production"
  }

  spec {
    pod_selector {
      match_labels = {
        app = "secure-app"
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        pod_selector {
          match_labels = {
            app = "frontend"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "8080"
      }
    }

    egress {
      to {
        pod_selector {
          match_labels = {
            app = "database"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "5432"
      }
    }
  }
}

# PASS: Service Account with limited permissions
resource "kubernetes_service_account" "app_sa" {
  metadata {
    name      = "app-service-account"
    namespace = "production"
  }

  automount_service_account_token = false
}

# PASS: Role with limited permissions
resource "kubernetes_role" "app_role" {
  metadata {
    name      = "app-role"
    namespace = "production"
  }

  rule {
    api_groups = [""]
    resources  = ["configmaps"]
    verbs      = ["get", "list"]
  }
}

# PASS: RoleBinding
resource "kubernetes_role_binding" "app_role_binding" {
  metadata {
    name      = "app-role-binding"
    namespace = "production"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.app_role.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.app_sa.metadata[0].name
    namespace = "production"
  }
}

# FAIL: ClusterRole with wildcard permissions
resource "kubernetes_cluster_role" "wildcard_cluster_role" {
  metadata {
    name = "wildcard-cluster-role"
  }

  rule {
    api_groups = ["*"]
    resources  = ["*"]
    verbs      = ["*"]
  }
}

# PASS: Secret (external secrets preferred)
resource "kubernetes_secret" "app_secret" {
  metadata {
    name      = "app-secret"
    namespace = "production"
  }

  type = "Opaque"

  data = {
    # In production, use external secrets management
    api_key = "base64encodedvalue"
  }
}

# ============================================================================
# SUPPORTING RESOURCES
# ============================================================================

resource "aws_iam_role" "eks_cluster_role" {
  name = "eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role" "eks_node_role" {
  name = "eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_launch_template" "eks_nodes" {
  name_prefix = "eks-nodes-"
  image_id    = "ami-12345678"

  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_size = 20
      volume_type = "gp3"
      encrypted   = true
    }
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
}

# ============================================================================
# ADDITIONAL TEST CASES FOR COMPREHENSIVE COVERAGE
# ============================================================================

# FAIL: Pod with host network
resource "kubernetes_pod" "host_network_pod" {
  metadata {
    name      = "host-network-pod"
    namespace = "production"
  }

  spec {
    host_network = true

    container {
      name  = "app"
      image = "myapp:latest"
    }
  }
}

# FAIL: Pod with host PID
resource "kubernetes_pod" "host_pid_pod" {
  metadata {
    name      = "host-pid-pod"
    namespace = "production"
  }

  spec {
    host_pid = true

    container {
      name  = "app"
      image = "myapp:latest"
    }
  }
}

# FAIL: Pod with host IPC
resource "kubernetes_pod" "host_ipc_pod" {
  metadata {
    name      = "host-ipc-pod"
    namespace = "production"
  }

  spec {
    host_ipc = true

    container {
      name  = "app"
      image = "myapp:latest"
    }
  }
}

# FAIL: Pod with privilege escalation allowed
resource "kubernetes_pod" "privilege_escalation_pod" {
  metadata {
    name      = "privilege-escalation-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:latest"

      security_context {
        allow_privilege_escalation = true
      }
    }
  }
}

# FAIL: Pod without dropping capabilities
resource "kubernetes_pod" "no_drop_capabilities_pod" {
  metadata {
    name      = "no-drop-capabilities-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:latest"

      security_context {
        capabilities {
          add = ["NET_ADMIN"]
        }
      }
    }
  }
}

# FAIL: Deployment with latest tag in production
resource "kubernetes_deployment" "latest_tag_deployment" {
  metadata {
    name      = "latest-tag-deployment"
    namespace = "production"

    labels = {
      app         = "latest-app"
      environment = "production"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "latest-app"
      }
    }

    template {
      metadata {
        labels = {
          app         = "latest-app"
          environment = "production"
        }
      }

      spec {
        container {
          name  = "app"
          image = "myapp:latest"  # FAIL: latest tag in production
        }
      }
    }
  }
}

# FAIL: Deployment with untrusted registry
resource "kubernetes_deployment" "untrusted_registry_deployment" {
  metadata {
    name      = "untrusted-registry-deployment"
    namespace = "production"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "untrusted-app"
      }
    }

    template {
      metadata {
        labels = {
          app = "untrusted-app"
        }
      }

      spec {
        container {
          name  = "app"
          image = "docker.io/untrusted/myapp:v1.0.0"  # FAIL: untrusted registry
        }
      }
    }
  }
}

# FAIL: Role with wildcard verbs
resource "kubernetes_role" "wildcard_verbs_role" {
  metadata {
    name      = "wildcard-verbs-role"
    namespace = "production"
  }

  rule {
    api_groups = [""]
    resources  = ["pods"]
    verbs      = ["*"]  # FAIL: wildcard verbs
  }
}

# FAIL: Role with wildcard resources
resource "kubernetes_role" "wildcard_resources_role" {
  metadata {
    name      = "wildcard-resources-role"
    namespace = "production"
  }

  rule {
    api_groups = [""]
    resources  = ["*"]  # FAIL: wildcard resources
    verbs      = ["get", "list"]
  }
}

# FAIL: ClusterRoleBinding to cluster-admin
resource "kubernetes_cluster_role_binding" "cluster_admin_binding" {
  metadata {
    name = "cluster-admin-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"  # FAIL: binding to cluster-admin
  }

  subject {
    kind      = "User"
    name      = "admin-user"
    api_group = "rbac.authorization.k8s.io"
  }
}

# FAIL: ClusterRoleBinding to system:masters
resource "kubernetes_cluster_role_binding" "system_masters_binding" {
  metadata {
    name = "system-masters-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }

  subject {
    kind      = "Group"
    name      = "system:masters"  # FAIL: binding to system:masters
    api_group = "rbac.authorization.k8s.io"
  }
}

# FAIL: RoleBinding without subjects
resource "kubernetes_role_binding" "no_subjects_binding" {
  metadata {
    name      = "no-subjects-binding"
    namespace = "production"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = "app-role"
  }

  # FAIL: no subjects defined
}

# FAIL: ServiceAccount without explicit token mounting config
resource "kubernetes_service_account" "default_token_sa" {
  metadata {
    name      = "default-token-sa"
    namespace = "production"
  }

  # FAIL: automount_service_account_token not explicitly set
}

# FAIL: ServiceAccount in default namespace
resource "kubernetes_service_account" "default_namespace_sa" {
  metadata {
    name      = "default-namespace-sa"
    namespace = "default"  # FAIL: using default namespace
  }

  automount_service_account_token = false
}

# PASS: RoleBinding with ClusterRole (should prefer Role)
resource "kubernetes_role_binding" "cluster_role_binding" {
  metadata {
    name      = "cluster-role-binding"
    namespace = "production"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"  # INFO: should prefer Role for namespace-scoped
    name      = "view"
  }

  subject {
    kind      = "ServiceAccount"
    name      = "app-service-account"
    namespace = "production"
  }
}

# FAIL: Network Policy without default deny egress
resource "kubernetes_network_policy" "no_default_deny_egress" {
  metadata {
    name      = "no-default-deny-egress"
    namespace = "production"
  }

  spec {
    pod_selector {}

    policy_types = ["Egress"]

    egress {
      to {
        pod_selector {
          match_labels = {
            app = "allowed-app"
          }
        }
      }
    }
  }
}

# FAIL: Network Policy without pod selector
resource "kubernetes_network_policy" "no_pod_selector" {
  metadata {
    name      = "no-pod-selector"
    namespace = "production"
  }

  spec {
    policy_types = ["Ingress"]
  }
}

# FAIL: Service with NodePort in production
resource "kubernetes_service" "nodeport_service" {
  metadata {
    name      = "nodeport-service"
    namespace = "production"

    labels = {
      environment = "production"
    }
  }

  spec {
    type = "NodePort"  # FAIL: NodePort in production

    selector = {
      app = "secure-app"
    }

    port {
      port        = 80
      target_port = 8080
      node_port   = 30080
    }
  }
}

# FAIL: Ingress without TLS
resource "kubernetes_ingress" "no_tls_ingress" {
  metadata {
    name      = "no-tls-ingress"
    namespace = "production"
  }

  spec {
    rule {
      host = "example.com"

      http {
        path {
          path = "/"

          backend {
            service {
              name = "app-service"
              port {
                number = 80
              }
            }
          }
        }
      }
    }

    # FAIL: no TLS configuration
  }
}

# PASS: Ingress with TLS
resource "kubernetes_ingress" "tls_ingress" {
  metadata {
    name      = "tls-ingress"
    namespace = "production"
  }

  spec {
    tls {
      hosts       = ["secure.example.com"]
      secret_name = "tls-secret"
    }

    rule {
      host = "secure.example.com"

      http {
        path {
          path = "/"

          backend {
            service {
              name = "app-service"
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}

# FAIL: Pod with secrets in environment variables
resource "kubernetes_pod" "secrets_in_env_pod" {
  metadata {
    name      = "secrets-in-env-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:v1.0.0"

      env {
        name = "API_KEY"
        value_from {
          secret_key_ref {  # FAIL: secret in environment variable
            name = "app-secret"
            key  = "api_key"
          }
        }
      }
    }
  }
}

# FAIL: Pod with hardcoded secrets
resource "kubernetes_pod" "hardcoded_secrets_pod" {
  metadata {
    name      = "hardcoded-secrets-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:v1.0.0"

      env {
        name  = "DATABASE_PASSWORD"  # FAIL: hardcoded secret
        value = "supersecretpassword123"
      }

      env {
        name  = "API_TOKEN"  # FAIL: hardcoded secret
        value = "abc123token"
      }
    }
  }
}

# PASS: Pod with secrets mounted as volumes
resource "kubernetes_pod" "secrets_volume_pod" {
  metadata {
    name      = "secrets-volume-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "myapp:v1.0.0"

      volume_mount {
        name       = "secret-volume"
        mount_path = "/etc/secrets"
        read_only  = true
      }
    }

    volume {
      name = "secret-volume"
      secret {
        secret_name = "app-secret"
      }
    }
  }
}

# PASS: Secret with encryption annotation
resource "kubernetes_secret" "encrypted_secret" {
  metadata {
    name      = "encrypted-secret"
    namespace = "production"

    annotations = {
      "encryption.alpha.kubernetes.io/encrypted" = "true"
    }
  }

  type = "Opaque"

  data = {
    api_key = "base64encodedvalue"
  }
}

# PASS: Secret with immutable flag
resource "kubernetes_secret" "immutable_secret" {
  metadata {
    name      = "immutable-secret"
    namespace = "production"
  }

  type      = "Opaque"
  immutable = true

  data = {
    config = "base64encodedconfig"
  }
}

# PASS: Secret with external secrets annotation
resource "kubernetes_secret" "external_secret" {
  metadata {
    name      = "external-secret"
    namespace = "production"

    annotations = {
      "external-secrets.io/managed-by" = "external-secrets-operator"
    }
  }

  type = "Opaque"

  data = {
    token = "base64encodedtoken"
  }
}

# PASS: Secret with rotation annotation
resource "kubernetes_secret" "rotated_secret" {
  metadata {
    name      = "rotated-secret"
    namespace = "production"

    annotations = {
      "secret.kubernetes.io/rotation-time" = "2024-01-01T00:00:00Z"
    }
  }

  type = "Opaque"

  data = {
    password = "base64encodedpassword"
  }
}

# PASS: Pod with Always pull policy for latest tag
resource "kubernetes_pod" "always_pull_latest_pod" {
  metadata {
    name      = "always-pull-latest-pod"
    namespace = "development"
  }

  spec {
    container {
      name              = "app"
      image             = "myapp:latest"
      image_pull_policy = "Always"  # PASS: Always pull policy for latest tag
    }
  }
}

# PASS: Pod with trusted registry
resource "kubernetes_pod" "trusted_registry_pod" {
  metadata {
    name      = "trusted-registry-pod"
    namespace = "production"
  }

  spec {
    container {
      name  = "app"
      image = "gcr.io/my-project/myapp:v1.0.0"  # PASS: trusted registry
    }
  }
}

# PASS: Pod with vulnerability scan annotation
resource "kubernetes_pod" "scanned_pod" {
  metadata {
    name      = "scanned-pod"
    namespace = "production"

    annotations = {
      "security.alpha.kubernetes.io/vulnerability-scan" = "passed"
    }
  }

  spec {
    container {
      name  = "app"
      image = "myregistry.io/myapp:v1.0.0"
    }
  }
}

# PASS: Pod with image signature
resource "kubernetes_pod" "signed_image_pod" {
  metadata {
    name      = "signed-image-pod"
    namespace = "production"

    annotations = {
      "cosign.sigstore.dev/signature" = "MEUCIQDxyz..."
    }
  }

  spec {
    container {
      name  = "app"
      image = "myregistry.io/myapp:v1.0.0"
    }
  }
}

# PASS: Pod with runtime security monitoring
resource "kubernetes_pod" "monitored_pod" {
  metadata {
    name      = "monitored-pod"
    namespace = "production"

    annotations = {
      "security.kubernetes.io/runtime-monitoring" = "enabled"
    }
  }

  spec {
    container {
      name  = "app"
      image = "myregistry.io/myapp:v1.0.0"
    }
  }
}

# PASS: ValidatingAdmissionWebhook for image policy
resource "kubernetes_validating_admission_webhook" "image_policy_webhook" {
  metadata {
    name = "image-policy-webhook"
  }

  webhook {
    name = "image-policy.example.com"

    client_config {
      service {
        name      = "image-policy-service"
        namespace = "kube-system"
        path      = "/validate"
      }
    }

    admission_review_versions = ["v1", "v1beta1"]

    rules {
      operations   = ["CREATE", "UPDATE"]
      api_groups   = [""]
      api_versions = ["v1"]
      resources    = ["pods"]
    }
  }
}