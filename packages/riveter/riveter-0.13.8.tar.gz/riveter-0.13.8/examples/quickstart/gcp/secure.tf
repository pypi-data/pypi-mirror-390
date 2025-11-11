# GCP Infrastructure Example - SECURE VERSION
# This example shows the same infrastructure with security best practices applied
# Run: riveter scan -p gcp-security -t secure.tf

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "my-secure-project"
}

# SECURE: VPC with custom subnets
resource "google_compute_network" "main" {
  name                    = "vpc-secure"
  auto_create_subnetworks = false  # ✅ Custom subnets for better control

  labels = {
    name        = "main-vpc"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# Private subnet for application servers
resource "google_compute_subnetwork" "private" {
  name          = "subnet-private-secure"
  ip_cidr_range = "10.0.1.0/24"  # ✅ Appropriately sized
  region        = "us-central1"
  network       = google_compute_network.main.id

  # ✅ Private Google Access enabled
  private_ip_google_access = true

  labels = {
    name        = "private-subnet"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
    type        = "private"
  }
}

# Public subnet for load balancer only
resource "google_compute_subnetwork" "public" {
  name          = "subnet-public-secure"
  ip_cidr_range = "10.0.2.0/24"
  region        = "us-central1"
  network       = google_compute_network.main.id

  labels = {
    name        = "public-subnet"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
    type        = "public"
  }
}

# SECURE: Restrictive firewall rules
resource "google_compute_firewall" "allow_https_lb" {
  name    = "allow-https-lb"
  network = google_compute_network.main.name

  # ✅ Only HTTPS from internet to load balancer
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["load-balancer"]

  labels = {
    name        = "https-lb-firewall"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

resource "google_compute_firewall" "allow_http_from_lb" {
  name    = "allow-http-from-lb"
  network = google_compute_network.main.name

  # ✅ Only HTTP from load balancer to app servers
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_tags = ["load-balancer"]
  target_tags = ["web-server"]

  labels = {
    name        = "http-internal-firewall"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

resource "google_compute_firewall" "allow_ssh_iap" {
  name    = "allow-ssh-iap"
  network = google_compute_network.main.name

  # ✅ SSH only through Identity-Aware Proxy
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  # IAP source ranges
  source_ranges = ["35.235.240.0/20"]
  target_tags   = ["web-server"]

  labels = {
    name        = "ssh-iap-firewall"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# SECURE: Service account with minimal permissions
resource "google_service_account" "compute" {
  account_id   = "compute-secure"
  display_name = "Compute Service Account (Secure)"

  labels = {
    name        = "compute-service-account"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# ✅ Minimal IAM permissions
resource "google_project_iam_member" "compute_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.compute.email}"
}

resource "google_project_iam_member" "compute_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.compute.email}"
}

# SECURE: Compute instance in private subnet with encryption
resource "google_compute_instance" "web" {
  name         = "vm-web-secure"
  machine_type = "e2-small"  # ✅ Appropriate size
  zone         = "us-central1-a"

  # ✅ Encrypted boot disk
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20
      type  = "pd-ssd"  # ✅ SSD for better performance
    }
    
    # ✅ Customer-managed encryption key
    disk_encryption_key {
      kms_key_self_link = google_kms_crypto_key.vm_key.id
    }
  }

  # ✅ No public IP - private subnet only
  network_interface {
    network    = google_compute_network.main.name
    subnetwork = google_compute_subnetwork.private.name
    # No access_config block = no public IP
  }

  # ✅ Minimal service account permissions
  service_account {
    email  = google_service_account.compute.email
    scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring.write"
    ]
  }

  # ✅ Security features enabled
  metadata = {
    enable-oslogin                = "true"   # ✅ OS Login enabled
    block-project-ssh-keys        = "true"   # ✅ Block project SSH keys
    enable-ip-forwarding          = "false"  # ✅ IP forwarding disabled
    serial-port-enable            = "false"  # ✅ Serial port disabled
  }

  # ✅ Shielded VM features
  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                = true
    enable_integrity_monitoring = true
  }

  tags = ["web-server"]

  labels = {
    name        = "web-server"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
    backup      = "daily"
  }
}

# KMS key for VM encryption
resource "google_kms_key_ring" "vm_keyring" {
  name     = "vm-keyring-secure"
  location = "us-central1"

  labels = {
    name        = "vm-keyring"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

resource "google_kms_crypto_key" "vm_key" {
  name     = "vm-encryption-key"
  key_ring = google_kms_key_ring.vm_keyring.id

  rotation_period = "7776000s"  # 90 days

  labels = {
    name        = "vm-encryption-key"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# SECURE: Cloud Storage bucket with private access
resource "google_storage_bucket" "data" {
  name     = "bucket-secure-data-${random_id.suffix.hex}"
  location = "US"

  # ✅ Uniform bucket-level access
  uniform_bucket_level_access = true

  # ✅ Versioning enabled
  versioning {
    enabled = true
  }

  # ✅ Encryption with customer-managed key
  encryption {
    default_kms_key_name = google_kms_crypto_key.storage_key.id
  }

  # ✅ Lifecycle management
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  # ✅ Public access prevention
  public_access_prevention = "enforced"

  labels = {
    name        = "application-storage"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# KMS key for storage encryption
resource "google_kms_crypto_key" "storage_key" {
  name     = "storage-encryption-key"
  key_ring = google_kms_key_ring.vm_keyring.id

  rotation_period = "7776000s"  # 90 days

  labels = {
    name        = "storage-encryption-key"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# SECURE: Cloud SQL instance with private IP
resource "google_sql_database_instance" "main" {
  name             = "db-secure-${random_id.suffix.hex}"
  database_version = "MYSQL_8_0"
  region           = "us-central1"

  settings {
    tier = "db-n1-standard-1"  # ✅ Appropriate size

    # ✅ Private IP only
    ip_configuration {
      ipv4_enabled    = false  # ✅ No public IP
      private_network = google_compute_network.main.id
      require_ssl     = true   # ✅ SSL required
    }

    # ✅ Automated backups
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 30
      }
    }

    # ✅ Disk encryption
    disk_encryption_configuration {
      kms_key_name = google_kms_crypto_key.sql_key.id
    }

    # ✅ Database flags for security
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }

    user_labels = {
      name        = "main-database"
      environment = "production"
      owner       = "platform-team"
      project     = "web-application"
      cost_center = "engineering"
    }
  }

  # ✅ Deletion protection enabled
  deletion_protection = true
}

# KMS key for SQL encryption
resource "google_kms_crypto_key" "sql_key" {
  name     = "sql-encryption-key"
  key_ring = google_kms_key_ring.vm_keyring.id

  rotation_period = "7776000s"  # 90 days

  labels = {
    name        = "sql-encryption-key"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# Private service connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# SECURE: Cloud SQL database
resource "google_sql_database" "main" {
  name     = "main-database"
  instance = google_sql_database_instance.main.name

  labels = {
    name        = "main-database"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# SECURE: Cloud SQL user with generated password
resource "google_sql_user" "main" {
  name     = "admin"
  instance = google_sql_database_instance.main.name
  password = random_password.sql_password.result  # ✅ Generated password
}

resource "random_password" "sql_password" {
  length  = 16
  special = true
}

# Store SQL password in Secret Manager
resource "google_secret_manager_secret" "sql_password" {
  secret_id = "sql-admin-password"

  replication {
    auto {}
  }

  labels = {
    name        = "sql-admin-password"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

resource "google_secret_manager_secret_version" "sql_password" {
  secret      = google_secret_manager_secret.sql_password.id
  secret_data = random_password.sql_password.result
}

# SECURE: Cloud Function with authentication
resource "google_cloudfunctions2_function" "api" {
  name        = "api-function-secure"
  location    = "us-central1"
  description = "API Function (Secure)"

  build_config {
    runtime     = "python39"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.data.name
        object = "function-source.zip"
      }
    }
  }

  service_config {
    max_instance_count = 10
    available_memory   = "128Mi"
    timeout_seconds    = 60

    # ✅ Custom service account
    service_account_email = google_service_account.function.email

    # ✅ VPC connector for private access
    vpc_connector                 = google_vpc_access_connector.main.id
    vpc_connector_egress_settings = "PRIVATE_RANGES_ONLY"

    # ✅ Environment variables from Secret Manager
    secret_environment_variables {
      key        = "API_KEY"
      project_id = var.project_id
      secret     = google_secret_manager_secret.api_key.secret_id
      version    = "latest"
    }
  }

  labels = {
    name        = "api-function"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# Service account for Cloud Function
resource "google_service_account" "function" {
  account_id   = "function-secure"
  display_name = "Cloud Function Service Account (Secure)"

  labels = {
    name        = "function-service-account"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

# VPC Connector for Cloud Function
resource "google_vpc_access_connector" "main" {
  name          = "vpc-connector-secure"
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.main.name
  region        = "us-central1"
}

# SECURE: Secret Manager secret with restricted access
resource "google_secret_manager_secret" "api_key" {
  secret_id = "api-key-secure"

  replication {
    auto {}
  }

  labels = {
    name        = "api-key"
    environment = "production"
    owner       = "platform-team"
    project     = "web-application"
    cost_center = "engineering"
  }
}

resource "google_secret_manager_secret_version" "api_key" {
  secret      = google_secret_manager_secret.api_key.id
  secret_data = random_password.api_key.result  # ✅ Generated secret
}

resource "random_password" "api_key" {
  length  = 32
  special = false
}

# ✅ Restricted access to secret
resource "google_secret_manager_secret_iam_member" "function_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.function.email}"
}

resource "random_id" "suffix" {
  byte_length = 4
}

# Secure outputs (no sensitive information)
output "vpc_network_id" {
  value       = google_compute_network.main.id
  description = "VPC network ID for reference"
}

output "private_subnet_id" {
  value       = google_compute_subnetwork.private.id
  description = "Private subnet ID where application runs"
}

output "function_uri" {
  value       = google_cloudfunctions2_function.api.service_config[0].uri
  description = "Cloud Function URI (requires authentication)"
}