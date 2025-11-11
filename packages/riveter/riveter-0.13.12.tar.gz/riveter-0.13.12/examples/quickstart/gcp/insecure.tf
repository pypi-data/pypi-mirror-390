# GCP Infrastructure Example - INSECURE VERSION
# This example contains intentional security violations for learning purposes
# Run: riveter scan -p gcp-security -t insecure.tf

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
  default     = "my-insecure-project"
}

# INSECURE: VPC with default settings
resource "google_compute_network" "main" {
  name                    = "vpc-insecure"
  auto_create_subnetworks = true  # ❌ Should be false for security

  # Missing required labels - will fail validation
}

# INSECURE: Subnet with overly broad range
resource "google_compute_subnetwork" "public" {
  name          = "subnet-public-insecure"
  ip_cidr_range = "10.0.0.0/8"  # ❌ Too broad
  region        = "us-central1"
  network       = google_compute_network.main.id

  # Missing required labels - will fail validation
}

# INSECURE: Firewall rule allowing all traffic
resource "google_compute_firewall" "allow_all" {
  name    = "allow-all-insecure"
  network = google_compute_network.main.name

  # PROBLEM: SSH open to the world
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  # PROBLEM: HTTP open to the world
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  # PROBLEM: All traffic from anywhere
  source_ranges = ["0.0.0.0/0"]  # ❌ Should be restricted

  # Missing required labels - will fail validation
}

# INSECURE: Firewall rule allowing RDP
resource "google_compute_firewall" "allow_rdp" {
  name    = "allow-rdp-insecure"
  network = google_compute_network.main.name

  # PROBLEM: RDP open to the world
  allow {
    protocol = "tcp"
    ports    = ["3389"]
  }

  source_ranges = ["0.0.0.0/0"]  # ❌ Should be restricted

  # Missing required labels - will fail validation
}

# INSECURE: Compute instance with public IP and weak configuration
resource "google_compute_instance" "web" {
  name         = "vm-web-insecure"
  machine_type = "e2-micro"
  zone         = "us-central1-a"

  # PROBLEM: Unencrypted boot disk
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20
      type  = "pd-standard"
      # Missing encryption settings - will fail validation
    }
  }

  # PROBLEM: Public IP assigned
  network_interface {
    network    = google_compute_network.main.name
    subnetwork = google_compute_subnetwork.public.name
    
    access_config {
      # Ephemeral public IP - ❌ Should not have public IP
    }
  }

  # PROBLEM: Full API access
  service_account {
    email  = google_service_account.compute.email
    scopes = ["cloud-platform"]  # ❌ Too broad, should be specific scopes
  }

  # PROBLEM: No OS Login enabled
  metadata = {
    enable-oslogin = "false"  # ❌ Should be true
  }

  # Missing required labels - will fail validation
}

# INSECURE: Service account with excessive permissions
resource "google_service_account" "compute" {
  account_id   = "compute-insecure"
  display_name = "Compute Service Account (Insecure)"

  # Missing required labels - will fail validation
}

# PROBLEM: Overly broad IAM binding
resource "google_project_iam_binding" "compute_admin" {
  project = var.project_id
  role    = "roles/compute.admin"  # ❌ Too broad

  members = [
    "serviceAccount:${google_service_account.compute.email}",
  ]
}

# INSECURE: Cloud Storage bucket with public access
resource "google_storage_bucket" "data" {
  name     = "bucket-insecure-data-${random_id.suffix.hex}"
  location = "US"

  # PROBLEM: Public access allowed
  uniform_bucket_level_access = false  # ❌ Should be true

  # PROBLEM: No versioning
  versioning {
    enabled = false  # ❌ Should be enabled
  }

  # Missing encryption settings - will fail validation
  # Missing required labels - will fail validation
}

# PROBLEM: Public access to bucket
resource "google_storage_bucket_iam_binding" "public_read" {
  bucket = google_storage_bucket.data.name
  role   = "roles/storage.objectViewer"

  members = [
    "allUsers",  # ❌ Should not allow public access
  ]
}

# INSECURE: Cloud SQL instance with public IP
resource "google_sql_database_instance" "main" {
  name             = "db-insecure-${random_id.suffix.hex}"
  database_version = "MYSQL_8_0"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    # PROBLEM: Public IP enabled
    ip_configuration {
      ipv4_enabled = true  # ❌ Should be false
      
      # PROBLEM: Authorized network allows all IPs
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0"  # ❌ Should be restricted
      }
    }

    # PROBLEM: No backup configuration
    backup_configuration {
      enabled = false  # ❌ Should be enabled
    }

    # PROBLEM: No encryption
    # Missing disk_encryption_configuration

    # Missing required labels - will fail validation
  }

  # PROBLEM: Deletion protection disabled
  deletion_protection = false  # ❌ Should be true
}

# INSECURE: Cloud SQL database
resource "google_sql_database" "main" {
  name     = "main-database"
  instance = google_sql_database_instance.main.name

  # Missing required labels - will fail validation
}

# INSECURE: Cloud SQL user with weak password
resource "google_sql_user" "main" {
  name     = "admin"
  instance = google_sql_database_instance.main.name
  password = "password123"  # ❌ Weak hardcoded password

  # Missing required labels - will fail validation
}

# INSECURE: Cloud Function with public access
resource "google_cloudfunctions_function" "api" {
  name        = "api-function-insecure"
  description = "API Function (Insecure)"
  runtime     = "python39"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.data.name
  source_archive_object = "function-source.zip"
  trigger {
    http_trigger {
      url = "https://us-central1-${var.project_id}.cloudfunctions.net/api-function-insecure"
    }
  }
  entry_point = "main"

  # PROBLEM: No authentication required
  # Missing authentication settings

  # Missing required labels - will fail validation
}

# PROBLEM: Public access to Cloud Function
resource "google_cloudfunctions_function_iam_binding" "public_access" {
  project        = var.project_id
  region         = "us-central1"
  cloud_function = google_cloudfunctions_function.api.name
  role           = "roles/cloudfunctions.invoker"

  members = [
    "allUsers",  # ❌ Should not allow public access
  ]
}

# INSECURE: Secret Manager secret with weak access
resource "google_secret_manager_secret" "api_key" {
  secret_id = "api-key-insecure"

  replication {
    automatic = true
  }

  # Missing required labels - will fail validation
}

resource "google_secret_manager_secret_version" "api_key" {
  secret      = google_secret_manager_secret.api_key.id
  secret_data = "super-secret-api-key-123"  # ❌ Hardcoded secret
}

# PROBLEM: Overly broad access to secret
resource "google_secret_manager_secret_iam_binding" "api_key_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"

  members = [
    "serviceAccount:${google_service_account.compute.email}",
    "allUsers",  # ❌ Should not allow public access
  ]
}

resource "random_id" "suffix" {
  byte_length = 4
}

# Insecure outputs exposing sensitive information
output "vm_external_ip" {
  value = google_compute_instance.web.network_interface[0].access_config[0].nat_ip
  description = "External IP of VM (INSECURE - should not exist!)"
}

output "database_ip" {
  value = google_sql_database_instance.main.public_ip_address
  description = "Database public IP (INSECURE - publicly accessible!)"
}

output "api_function_url" {
  value = google_cloudfunctions_function.api.https_trigger_url
  description = "API function URL (INSECURE - publicly accessible!)"
}

output "secret_value" {
  value = google_secret_manager_secret_version.api_key.secret_data
  sensitive = false  # ❌ Should be sensitive
  description = "API key (INSECURE - exposed in output!)"
}