resource "google_compute_instance" "example" {
  name         = "example-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  tags = ["web", "dev"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
    disk_encryption_key {
      kms_key_self_link = google_kms_crypto_key.example.id
    }
  }

  network_interface {
    network = "default"
    # No access_config block means no external IP
  }

  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }

  labels = {
    environment = "production"
    owner       = "platform-team"
    cost-center = "12345"
  }
}

resource "google_storage_bucket" "example" {
  name     = "example-bucket-12345"
  location = "US"

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.example.id
  }

  labels = {
    environment = "production"
    owner       = "platform-team"
  }
}

resource "google_compute_firewall" "ssh_rule" {
  name    = "allow-ssh-internal"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["10.0.0.0/8"]
  target_tags   = ["ssh-allowed"]
  direction     = "INGRESS"
  priority      = 1000
}

resource "google_compute_firewall" "deny_all" {
  name    = "deny-all-ingress"
  network = "default"

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]
  direction     = "INGRESS"
  priority      = 65534
  action        = "DENY"
}

resource "google_sql_database_instance" "example" {
  name             = "example-database"
  database_version = "POSTGRES_13"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }

    ip_configuration {
      require_ssl = true
      # No authorized_networks means no external access
    }
  }

  deletion_protection = true
}

resource "google_container_cluster" "example" {
  name     = "example-gke-cluster"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1

  private_cluster_config {
    enable_private_nodes   = true
    master_ipv4_cidr_block = "172.16.0.0/28"
  }

  network_policy {
    enabled = true
  }

  master_auth {
    username = ""
    password = ""
  }

  enable_legacy_abac = false
}

resource "google_kms_key_ring" "example" {
  name     = "example-keyring"
  location = "global"
}

resource "google_kms_crypto_key" "example" {
  name     = "example-key"
  key_ring = google_kms_key_ring.example.id

  rotation_period = "7776000s"  # 90 days
}

resource "google_compute_network" "example" {
  name                    = "example-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "example" {
  name          = "example-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region        = "us-central1"
  network       = google_compute_network.example.id

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
    enable               = true
  }
}
