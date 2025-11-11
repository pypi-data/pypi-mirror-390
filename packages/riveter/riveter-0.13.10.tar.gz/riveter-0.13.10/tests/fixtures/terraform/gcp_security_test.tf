# GCP Security Best Practices Test Fixtures
# This file contains both passing and failing examples for gcp-security rule pack

# ============================================================================
# COMPUTE ENGINE RESOURCES
# ============================================================================

# PASS: Compute instance with all security best practices
resource "google_compute_instance" "secure_instance" {
  name         = "secure-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  tags = ["web", "production"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
    disk_encryption_key {
      kms_key_self_link = google_kms_crypto_key.secure_key.id
    }
  }

  network_interface {
    network    = google_compute_network.secure_network.id
    subnetwork = google_compute_subnetwork.secure_subnet.id
    # No access_config block - no external IP
  }

  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }

  labels = {
    environment = "production"
    owner       = "platform-team"
    cost-center = "engineering"
  }
}

# FAIL: Compute instance with external IP (production)
resource "google_compute_instance" "insecure_external_ip" {
  name         = "insecure-external-ip"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
      # External IP assigned
    }
  }

  labels = {
    environment = "production"
  }
}

# FAIL: Compute instance without shielded VM
resource "google_compute_instance" "no_shielded_vm" {
  name         = "no-shielded-vm"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
  }

  labels = {
    environment = "production"
  }
}

# FAIL: Compute instance without required labels
resource "google_compute_instance" "missing_labels" {
  name         = "missing-labels"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
  }
}

# PASS: Compute project metadata with OS Login enabled
resource "google_compute_project_metadata" "os_login_enabled" {
  metadata = {
    enable-oslogin = "TRUE"
  }
}

# FAIL: Compute project metadata without OS Login
resource "google_compute_project_metadata" "os_login_disabled" {
  metadata = {
    enable-oslogin = "FALSE"
  }
}

# ============================================================================
# CLOUD STORAGE RESOURCES
# ============================================================================

# PASS: Storage bucket with all security best practices
resource "google_storage_bucket" "secure_bucket" {
  name     = "secure-bucket-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }

  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.secure_key.id
  }

  logging {
    log_bucket = google_storage_bucket.log_bucket.name
  }

  labels = {
    environment = "production"
    owner       = "platform-team"
  }
}

# FAIL: Storage bucket without uniform bucket-level access
resource "google_storage_bucket" "no_uniform_access" {
  name     = "no-uniform-access-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = false
  }
}

# FAIL: Storage bucket without public access prevention
resource "google_storage_bucket" "public_access_allowed" {
  name     = "public-access-allowed-12345"
  location = "US"

  public_access_prevention = "inherited"
}

# FAIL: Storage bucket without versioning
resource "google_storage_bucket" "no_versioning" {
  name     = "no-versioning-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }
}

# FAIL: Storage bucket without encryption
resource "google_storage_bucket" "no_encryption" {
  name     = "no-encryption-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }
}

# FAIL: Storage bucket without access logging
resource "google_storage_bucket" "no_logging" {
  name     = "no-logging-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }
}

# Log bucket for access logging
resource "google_storage_bucket" "log_bucket" {
  name     = "log-bucket-12345"
  location = "US"
}

# ============================================================================
# CLOUD SQL RESOURCES
# ============================================================================

# PASS: Cloud SQL instance with all security best practices
resource "google_sql_database_instance" "secure_database" {
  name             = "secure-database"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-custom-2-7680"

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
    }

    ip_configuration {
      require_ssl     = true
      ipv4_enabled    = false
      private_network = google_compute_network.secure_network.id
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }
  }

  deletion_protection = true

  encryption_key_name = google_kms_crypto_key.secure_key.id
}

# FAIL: Cloud SQL without SSL/TLS required
resource "google_sql_database_instance" "no_ssl" {
  name             = "no-ssl-database"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      require_ssl = false
    }
  }
}

# FAIL: Cloud SQL without automated backups
resource "google_sql_database_instance" "no_backups" {
  name             = "no-backups-database"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled = false
    }
  }
}

# FAIL: Cloud SQL with public IP
resource "google_sql_database_instance" "public_ip" {
  name             = "public-ip-database"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled = true
      require_ssl  = true
    }
  }
}

# FAIL: Cloud SQL without encryption
resource "google_sql_database_instance" "no_encryption" {
  name             = "no-encryption-database"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      require_ssl = true
    }
  }
}

# ============================================================================
# VPC/NETWORKING RESOURCES
# ============================================================================

# PASS: VPC network with security best practices
resource "google_compute_network" "secure_network" {
  name                    = "secure-network"
  auto_create_subnetworks = false
}

# PASS: Subnet with VPC Flow Logs enabled
resource "google_compute_subnetwork" "secure_subnet" {
  name          = "secure-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.secure_network.id

  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# FAIL: Subnet without VPC Flow Logs
resource "google_compute_subnetwork" "no_flow_logs" {
  name          = "no-flow-logs-subnet"
  ip_cidr_range = "10.1.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.secure_network.id
}

# FAIL: Subnet without Private Google Access
resource "google_compute_subnetwork" "no_private_access" {
  name          = "no-private-access-subnet"
  ip_cidr_range = "10.2.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.secure_network.id

  private_ip_google_access = false

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# PASS: Firewall rule with restricted source ranges
resource "google_compute_firewall" "secure_ssh" {
  name    = "secure-ssh"
  network = google_compute_network.secure_network.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["10.0.0.0/8"]
  target_tags   = ["ssh-allowed"]
}

# FAIL: Firewall rule allowing SSH from anywhere
resource "google_compute_firewall" "insecure_ssh" {
  name    = "insecure-ssh"
  network = google_compute_network.secure_network.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}

# FAIL: Firewall rule allowing all protocols from anywhere
resource "google_compute_firewall" "allow_all" {
  name    = "allow-all"
  network = google_compute_network.secure_network.id

  allow {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]
}

# PASS: Cloud NAT for egress traffic
resource "google_compute_router" "secure_router" {
  name    = "secure-router"
  region  = "us-central1"
  network = google_compute_network.secure_network.id
}

resource "google_compute_router_nat" "secure_nat" {
  name                               = "secure-nat"
  router                             = google_compute_router.secure_router.name
  region                             = google_compute_router.secure_router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# ============================================================================
# IAM RESOURCES
# ============================================================================

# PASS: Service account with proper configuration
resource "google_service_account" "secure_sa" {
  account_id   = "secure-service-account"
  display_name = "Secure Service Account"
  description  = "Service account for secure application"
}

# PASS: IAM binding without primitive roles
resource "google_project_iam_binding" "secure_binding" {
  project = "my-project"
  role    = "roles/storage.objectViewer"

  members = [
    "serviceAccount:${google_service_account.secure_sa.email}",
  ]
}

# FAIL: IAM binding with primitive role (owner)
resource "google_project_iam_binding" "primitive_owner" {
  project = "my-project"
  role    = "roles/owner"

  members = [
    "serviceAccount:${google_service_account.secure_sa.email}",
  ]
}

# FAIL: IAM binding with primitive role (editor)
resource "google_project_iam_binding" "primitive_editor" {
  project = "my-project"
  role    = "roles/editor"

  members = [
    "serviceAccount:${google_service_account.secure_sa.email}",
  ]
}

# ============================================================================
# CLOUD KMS RESOURCES
# ============================================================================

# PASS: KMS key ring
resource "google_kms_key_ring" "secure_keyring" {
  name     = "secure-keyring"
  location = "us-central1"
}

# PASS: KMS crypto key with rotation enabled
resource "google_kms_crypto_key" "secure_key" {
  name     = "secure-key"
  key_ring = google_kms_key_ring.secure_keyring.id

  rotation_period = "7776000s" # 90 days

  purpose = "ENCRYPT_DECRYPT"

  lifecycle {
    prevent_destroy = true
  }
}

# FAIL: KMS crypto key without rotation
resource "google_kms_crypto_key" "no_rotation" {
  name     = "no-rotation-key"
  key_ring = google_kms_key_ring.secure_keyring.id

  purpose = "ENCRYPT_DECRYPT"
}

# FAIL: KMS crypto key without defined purpose
resource "google_kms_crypto_key" "no_purpose" {
  name            = "no-purpose-key"
  key_ring        = google_kms_key_ring.secure_keyring.id
  rotation_period = "7776000s"
}
