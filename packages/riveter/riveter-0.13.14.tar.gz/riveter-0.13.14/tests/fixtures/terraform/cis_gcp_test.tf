# CIS GCP Benchmark Test Fixtures
# This file contains both passing and failing examples for cis-gcp rule pack

# ============================================================================
# SECTION 1: IDENTITY AND ACCESS MANAGEMENT
# ============================================================================

# PASS: Service account without admin privileges
resource "google_project_iam_binding" "secure_iam_binding" {
  project = "my-project"
  role    = "roles/storage.objectViewer"

  members = [
    "serviceAccount:secure-sa@my-project.iam.gserviceaccount.com",
  ]
}

# FAIL: Service account with owner role (CIS 1.1)
resource "google_project_iam_binding" "owner_role" {
  project = "my-project"
  role    = "roles/owner"

  members = [
    "serviceAccount:admin-sa@my-project.iam.gserviceaccount.com",
  ]
}

# FAIL: Service account with editor role (CIS 1.1)
resource "google_project_iam_binding" "editor_role" {
  project = "my-project"
  role    = "roles/editor"

  members = [
    "serviceAccount:admin-sa@my-project.iam.gserviceaccount.com",
  ]
}

# PASS: Service account with specific role
resource "google_service_account" "cis_compliant_sa" {
  account_id   = "cis-compliant-sa"
  display_name = "CIS Compliant Service Account"
  description  = "Service account with least privilege"
}

# FAIL: Service account keys (CIS 1.4 - should use workload identity)
resource "google_service_account_key" "sa_key" {
  service_account_id = google_service_account.cis_compliant_sa.name
}

# PASS: IAM policy without primitive roles
resource "google_project_iam_member" "specific_role" {
  project = "my-project"
  role    = "roles/compute.instanceAdmin.v1"
  member  = "serviceAccount:${google_service_account.cis_compliant_sa.email}"
}

# FAIL: User with primitive role
resource "google_project_iam_member" "user_editor" {
  project = "my-project"
  role    = "roles/editor"
  member  = "user:admin@example.com"
}

# PASS: Separation of duties
resource "google_project_iam_member" "separation_of_duties_1" {
  project = "my-project"
  role    = "roles/iam.serviceAccountUser"
  member  = "user:developer@example.com"
}

resource "google_project_iam_member" "separation_of_duties_2" {
  project = "my-project"
  role    = "roles/compute.instanceAdmin.v1"
  member  = "user:operator@example.com"
}

# ============================================================================
# SECTION 2: LOGGING AND MONITORING
# ============================================================================

# PASS: Cloud Audit Logging configured (CIS 2.1)
resource "google_project_iam_audit_config" "audit_all_services" {
  project = "my-project"
  service = "allServices"

  audit_log_config {
    log_type = "ADMIN_READ"
  }

  audit_log_config {
    log_type = "DATA_READ"
  }

  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# PASS: Log sink for security logs (CIS 2.2)
resource "google_logging_project_sink" "security_sink" {
  name        = "security-log-sink"
  destination = "storage.googleapis.com/${google_storage_bucket.log_bucket.name}"

  filter = <<-EOT
    logName:"cloudaudit.googleapis.com" OR
    logName:"logs/cloudaudit.googleapis.com"
  EOT

  unique_writer_identity = true
}

# PASS: Log metric for project ownership changes (CIS 2.4)
resource "google_logging_metric" "project_ownership_changes" {
  name   = "project-ownership-changes"
  filter = <<-EOT
    protoPayload.serviceName="cloudresourcemanager.googleapis.com" AND
    protoPayload.methodName="SetIamPolicy" AND
    protoPayload.serviceData.policyDelta.bindingDeltas.role="roles/owner"
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

# PASS: Log metric for audit config changes (CIS 2.5)
resource "google_logging_metric" "audit_config_changes" {
  name   = "audit-config-changes"
  filter = <<-EOT
    protoPayload.serviceName="cloudresourcemanager.googleapis.com" AND
    protoPayload.methodName="SetIamPolicy" AND
    protoPayload.serviceData.policyDelta.auditConfigDeltas:*
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

# PASS: Log metric for custom role changes (CIS 2.6)
resource "google_logging_metric" "custom_role_changes" {
  name   = "custom-role-changes"
  filter = <<-EOT
    resource.type="iam_role" AND
    protoPayload.methodName="google.iam.admin.v1.CreateRole" OR
    protoPayload.methodName="google.iam.admin.v1.DeleteRole" OR
    protoPayload.methodName="google.iam.admin.v1.UpdateRole"
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

# PASS: Log metric for VPC network changes (CIS 2.9)
resource "google_logging_metric" "vpc_network_changes" {
  name   = "vpc-network-changes"
  filter = <<-EOT
    resource.type="gce_network" AND
    protoPayload.methodName:"compute.networks.insert" OR
    protoPayload.methodName:"compute.networks.patch" OR
    protoPayload.methodName:"compute.networks.delete"
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

# PASS: Log bucket for centralized logging
resource "google_storage_bucket" "log_bucket" {
  name     = "cis-log-bucket-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}

# ============================================================================
# SECTION 3: NETWORKING
# ============================================================================

# PASS: VPC with flow logs enabled (CIS 3.8)
resource "google_compute_network" "cis_network" {
  name                    = "cis-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "cis_subnet" {
  name          = "cis-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.cis_network.id

  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# FAIL: Subnet without flow logs (CIS 3.8)
resource "google_compute_subnetwork" "no_flow_logs" {
  name          = "no-flow-logs-subnet"
  ip_cidr_range = "10.1.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.cis_network.id
}

# PASS: Firewall rule with restricted SSH (CIS 3.6)
resource "google_compute_firewall" "restricted_ssh" {
  name    = "restricted-ssh"
  network = google_compute_network.cis_network.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["10.0.0.0/8"]
  target_tags   = ["ssh-allowed"]
}

# FAIL: Firewall rule allowing SSH from anywhere (CIS 3.6)
resource "google_compute_firewall" "open_ssh" {
  name    = "open-ssh"
  network = google_compute_network.cis_network.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}

# FAIL: Firewall rule allowing RDP from anywhere (CIS 3.7)
resource "google_compute_firewall" "open_rdp" {
  name    = "open-rdp"
  network = google_compute_network.cis_network.id

  allow {
    protocol = "tcp"
    ports    = ["3389"]
  }

  source_ranges = ["0.0.0.0/0"]
}

# PASS: Default network deleted (CIS 3.1)
# Note: This would be done via gcloud command, not Terraform
# gcloud compute networks delete default

# PASS: DNSSEC enabled (CIS 3.3)
resource "google_dns_managed_zone" "cis_dns_zone" {
  name        = "cis-dns-zone"
  dns_name    = "example.com."
  description = "CIS compliant DNS zone"

  dnssec_config {
    state = "on"
  }
}

# FAIL: DNSSEC not enabled (CIS 3.3)
resource "google_dns_managed_zone" "no_dnssec" {
  name        = "no-dnssec-zone"
  dns_name    = "insecure.com."
  description = "DNS zone without DNSSEC"
}

# ============================================================================
# SECTION 4: VIRTUAL MACHINES
# ============================================================================

# PASS: Compute instance with OS Login (CIS 4.4)
resource "google_compute_project_metadata" "os_login" {
  metadata = {
    enable-oslogin = "TRUE"
  }
}

# FAIL: Compute instance without OS Login (CIS 4.4)
resource "google_compute_project_metadata" "no_os_login" {
  metadata = {
    enable-oslogin = "FALSE"
  }
}

# PASS: Compute instance with block project-wide SSH keys (CIS 4.3)
resource "google_compute_instance" "block_project_ssh_keys" {
  name         = "block-project-ssh-keys"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.cis_network.id
  }

  metadata = {
    block-project-ssh-keys = "true"
  }
}

# FAIL: Compute instance allowing project-wide SSH keys (CIS 4.3)
resource "google_compute_instance" "allow_project_ssh_keys" {
  name         = "allow-project-ssh-keys"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.cis_network.id
  }

  metadata = {
    block-project-ssh-keys = "false"
  }
}

# PASS: Compute instance with Shielded VM (CIS 4.8)
resource "google_compute_instance" "shielded_vm" {
  name         = "shielded-vm"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.cis_network.id
  }

  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }
}

# FAIL: Compute instance without Shielded VM (CIS 4.8)
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
    network = google_compute_network.cis_network.id
  }
}

# PASS: Compute instance without external IP (CIS 4.9)
resource "google_compute_instance" "no_external_ip" {
  name         = "no-external-ip"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.cis_network.id
    subnetwork = google_compute_subnetwork.cis_subnet.id
    # No access_config block
  }
}

# FAIL: Compute instance with external IP (CIS 4.9)
resource "google_compute_instance" "with_external_ip" {
  name         = "with-external-ip"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.cis_network.id

    access_config {
      # External IP
    }
  }
}

# ============================================================================
# SECTION 5: STORAGE
# ============================================================================

# PASS: Storage bucket with uniform access (CIS 5.1)
resource "google_storage_bucket" "uniform_access" {
  name     = "uniform-access-bucket-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }
}

# FAIL: Storage bucket without uniform access (CIS 5.1)
resource "google_storage_bucket" "no_uniform_access" {
  name     = "no-uniform-access-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = false
  }
}

# PASS: Storage bucket not publicly accessible (CIS 5.2)
resource "google_storage_bucket" "not_public" {
  name     = "not-public-bucket-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }

  public_access_prevention = "enforced"
}

# FAIL: Storage bucket publicly accessible (CIS 5.2)
resource "google_storage_bucket_iam_member" "public_access" {
  bucket = google_storage_bucket.uniform_access.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# ============================================================================
# SECTION 6: CLOUD SQL DATABASE SERVICES
# ============================================================================

# PASS: Cloud SQL with SSL required (CIS 6.4)
resource "google_sql_database_instance" "ssl_required" {
  name             = "ssl-required-db"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      require_ssl  = true
      ipv4_enabled = false
    }

    backup_configuration {
      enabled = true
    }
  }
}

# FAIL: Cloud SQL without SSL required (CIS 6.4)
resource "google_sql_database_instance" "no_ssl" {
  name             = "no-ssl-db"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      require_ssl = false
    }
  }
}

# PASS: Cloud SQL without public IP (CIS 6.5)
resource "google_sql_database_instance" "no_public_ip" {
  name             = "no-public-ip-db"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.cis_network.id
    }
  }
}

# FAIL: Cloud SQL with public IP (CIS 6.5)
resource "google_sql_database_instance" "public_ip" {
  name             = "public-ip-db"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled = true
    }
  }
}

# PASS: Cloud SQL with automated backups (CIS 6.7)
resource "google_sql_database_instance" "automated_backups" {
  name             = "automated-backups-db"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
    }
  }
}

# FAIL: Cloud SQL without automated backups (CIS 6.7)
resource "google_sql_database_instance" "no_backups" {
  name             = "no-backups-db"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled = false
    }
  }
}

# PASS: PostgreSQL with log_checkpoints enabled (CIS 6.2.1)
resource "google_sql_database_instance" "postgres_logging" {
  name             = "postgres-logging-db"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

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

    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
  }
}
