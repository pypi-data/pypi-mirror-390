# Multi-Cloud Security Test Fixtures
# This file contains resources from AWS, Azure, and GCP to test multi-cloud rule packs

# ============================================================================
# AWS RESOURCES
# ============================================================================

# PASS: AWS S3 bucket with encryption
resource "aws_s3_bucket" "aws_secure_storage" {
  bucket = "aws-secure-storage-12345"

  tags = {
    Environment = "production"
    Provider    = "aws"
    Owner       = "platform-team"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "aws_secure_storage_encryption" {
  bucket = aws_s3_bucket.aws_secure_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.aws_encryption_key.arn
    }
  }
}

# FAIL: AWS S3 bucket without encryption
resource "aws_s3_bucket" "aws_no_encryption" {
  bucket = "aws-no-encryption-12345"

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# PASS: AWS RDS with encryption
resource "aws_db_instance" "aws_secure_database" {
  identifier           = "aws-secure-db"
  engine               = "postgres"
  engine_version       = "14.7"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_encrypted    = true
  kms_key_id           = aws_kms_key.aws_encryption_key.arn
  multi_az             = true
  publicly_accessible  = false
  skip_final_snapshot  = true

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# FAIL: AWS RDS without encryption
resource "aws_db_instance" "aws_no_encryption_db" {
  identifier          = "aws-no-encryption-db"
  engine              = "postgres"
  engine_version      = "14.7"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  storage_encrypted   = false
  skip_final_snapshot = true

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# PASS: AWS EC2 with encrypted EBS
resource "aws_instance" "aws_secure_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  root_block_device {
    encrypted   = true
    kms_key_id  = aws_kms_key.aws_encryption_key.arn
    volume_type = "gp3"
  }

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# FAIL: AWS EC2 without encrypted EBS
resource "aws_instance" "aws_no_encryption_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  root_block_device {
    encrypted = false
  }

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# PASS: AWS Security Group with restricted access
resource "aws_security_group" "aws_secure_sg" {
  name        = "aws-secure-sg"
  description = "Secure security group"
  vpc_id      = "vpc-12345"

  ingress {
    description = "SSH from corporate network"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# FAIL: AWS Security Group allowing SSH from anywhere
resource "aws_security_group" "aws_insecure_sg" {
  name        = "aws-insecure-sg"
  description = "Insecure security group"
  vpc_id      = "vpc-12345"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# PASS: AWS CloudTrail with logging
resource "aws_cloudtrail" "aws_audit_trail" {
  name                          = "aws-audit-trail"
  s3_bucket_name                = aws_s3_bucket.aws_secure_storage.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# PASS: AWS KMS key
resource "aws_kms_key" "aws_encryption_key" {
  description             = "AWS encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Environment = "production"
    Provider    = "aws"
  }
}

# ============================================================================
# AZURE RESOURCES
# ============================================================================

resource "azurerm_resource_group" "multi_cloud_rg" {
  name     = "multi-cloud-resources"
  location = "East US"

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

# PASS: Azure Storage Account with encryption
resource "azurerm_storage_account" "azure_secure_storage" {
  name                     = "azuresecurestorage123"
  resource_group_name      = azurerm_resource_group.multi_cloud_rg.name
  location                 = azurerm_resource_group.multi_cloud_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  enable_https_traffic_only       = true
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false

  # Encryption is enabled by default in Azure

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

# FAIL: Azure Storage Account without HTTPS enforcement
resource "azurerm_storage_account" "azure_no_https" {
  name                     = "azurenohttps123"
  resource_group_name      = azurerm_resource_group.multi_cloud_rg.name
  location                 = azurerm_resource_group.multi_cloud_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = false

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

# PASS: Azure SQL Database with TDE
resource "azurerm_mssql_server" "azure_secure_sql" {
  name                         = "azure-secure-sql"
  resource_group_name          = azurerm_resource_group.multi_cloud_rg.name
  location                     = azurerm_resource_group.multi_cloud_rg.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd1234!"
  minimum_tls_version          = "1.2"

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

resource "azurerm_mssql_database" "azure_secure_db" {
  name      = "azure-secure-database"
  server_id = azurerm_mssql_server.azure_secure_sql.id
  sku_name  = "S1"

  transparent_data_encryption_enabled = true

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

# FAIL: Azure SQL Database without TDE
resource "azurerm_mssql_database" "azure_no_tde" {
  name      = "azure-no-tde-database"
  server_id = azurerm_mssql_server.azure_secure_sql.id
  sku_name  = "S1"

  transparent_data_encryption_enabled = false

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

# PASS: Azure VM with disk encryption
resource "azurerm_linux_virtual_machine" "azure_secure_vm" {
  name                = "azure-secure-vm"
  resource_group_name = azurerm_resource_group.multi_cloud_rg.name
  location            = azurerm_resource_group.multi_cloud_rg.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.azure_nic.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"

    disk_encryption_set_id = azurerm_disk_encryption_set.azure_des.id
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

# FAIL: Azure VM without disk encryption
resource "azurerm_linux_virtual_machine" "azure_no_encryption_vm" {
  name                = "azure-no-encryption-vm"
  resource_group_name = azurerm_resource_group.multi_cloud_rg.name
  location            = azurerm_resource_group.multi_cloud_rg.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.azure_nic.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

# PASS: Azure NSG with restricted access
resource "azurerm_network_security_group" "azure_secure_nsg" {
  name                = "azure-secure-nsg"
  location            = azurerm_resource_group.multi_cloud_rg.location
  resource_group_name = azurerm_resource_group.multi_cloud_rg.name

  tags = {
    Environment = "production"
    Provider    = "azure"
  }
}

resource "azurerm_network_security_rule" "azure_secure_ssh" {
  name                        = "AllowSSHFromCorporate"
  description                 = "Allow SSH from corporate network"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix       = "10.0.0.0/8"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.multi_cloud_rg.name
  network_security_group_name = azurerm_network_security_group.azure_secure_nsg.name
}

# FAIL: Azure NSG allowing SSH from anywhere
resource "azurerm_network_security_rule" "azure_insecure_ssh" {
  name                        = "AllowSSHFromInternet"
  priority                    = 200
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.multi_cloud_rg.name
  network_security_group_name = azurerm_network_security_group.azure_secure_nsg.name
}

# PASS: Azure Activity Log
resource "azurerm_monitor_log_profile" "azure_audit_log" {
  name = "azure-audit-log"

  categories = [
    "Action",
    "Delete",
    "Write",
  ]

  locations = [
    "eastus",
    "westus",
  ]

  storage_account_id = azurerm_storage_account.azure_secure_storage.id

  retention_policy {
    enabled = true
    days    = 365
  }
}

# ============================================================================
# GCP RESOURCES
# ============================================================================

# PASS: GCP Storage Bucket with encryption
resource "google_storage_bucket" "gcp_secure_storage" {
  name     = "gcp-secure-storage-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }

  public_access_prevention = "enforced"

  encryption {
    default_kms_key_name = google_kms_crypto_key.gcp_encryption_key.id
  }

  labels = {
    environment = "production"
    provider    = "gcp"
  }
}

# FAIL: GCP Storage Bucket without encryption
resource "google_storage_bucket" "gcp_no_encryption" {
  name     = "gcp-no-encryption-12345"
  location = "US"

  uniform_bucket_level_access {
    enabled = true
  }

  labels = {
    environment = "production"
    provider    = "gcp"
  }
}

# PASS: GCP Cloud SQL with encryption
resource "google_sql_database_instance" "gcp_secure_database" {
  name             = "gcp-secure-database"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      require_ssl     = true
      ipv4_enabled    = false
      private_network = google_compute_network.gcp_network.id
    }
  }

  encryption_key_name = google_kms_crypto_key.gcp_encryption_key.id
}

# FAIL: GCP Cloud SQL without encryption
resource "google_sql_database_instance" "gcp_no_encryption_db" {
  name             = "gcp-no-encryption-database"
  database_version = "POSTGRES_14"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      require_ssl = true
    }
  }
}

# PASS: GCP Compute Instance with encrypted disk
resource "google_compute_instance" "gcp_secure_instance" {
  name         = "gcp-secure-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
    disk_encryption_key {
      kms_key_self_link = google_kms_crypto_key.gcp_encryption_key.id
    }
  }

  network_interface {
    network = google_compute_network.gcp_network.id
  }

  labels = {
    environment = "production"
    provider    = "gcp"
  }
}

# FAIL: GCP Compute Instance without encrypted disk
resource "google_compute_instance" "gcp_no_encryption_instance" {
  name         = "gcp-no-encryption-instance"
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
    provider    = "gcp"
  }
}

# PASS: GCP Firewall with restricted access
resource "google_compute_firewall" "gcp_secure_firewall" {
  name    = "gcp-secure-firewall"
  network = google_compute_network.gcp_network.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["10.0.0.0/8"]
  target_tags   = ["ssh-allowed"]
}

# FAIL: GCP Firewall allowing SSH from anywhere
resource "google_compute_firewall" "gcp_insecure_firewall" {
  name    = "gcp-insecure-firewall"
  network = google_compute_network.gcp_network.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}

# PASS: GCP Audit Logging
resource "google_project_iam_audit_config" "gcp_audit_config" {
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

# PASS: GCP KMS resources
resource "google_kms_key_ring" "gcp_keyring" {
  name     = "gcp-keyring"
  location = "us-central1"
}

resource "google_kms_crypto_key" "gcp_encryption_key" {
  name            = "gcp-encryption-key"
  key_ring        = google_kms_key_ring.gcp_keyring.id
  rotation_period = "7776000s" # 90 days

  purpose = "ENCRYPT_DECRYPT"
}

resource "google_compute_network" "gcp_network" {
  name                    = "gcp-network"
  auto_create_subnetworks = false
}

# ============================================================================
# SUPPORTING AZURE RESOURCES
# ============================================================================

resource "azurerm_virtual_network" "azure_vnet" {
  name                = "azure-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.multi_cloud_rg.location
  resource_group_name = azurerm_resource_group.multi_cloud_rg.name
}

resource "azurerm_subnet" "azure_subnet" {
  name                 = "azure-subnet"
  resource_group_name  = azurerm_resource_group.multi_cloud_rg.name
  virtual_network_name = azurerm_virtual_network.azure_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_interface" "azure_nic" {
  name                = "azure-nic"
  location            = azurerm_resource_group.multi_cloud_rg.location
  resource_group_name = azurerm_resource_group.multi_cloud_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.azure_subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_key_vault" "azure_kv" {
  name                       = "azure-kv-12345"
  location                   = azurerm_resource_group.multi_cloud_rg.location
  resource_group_name        = azurerm_resource_group.multi_cloud_rg.name
  tenant_id                  = "00000000-0000-0000-0000-000000000000"
  sku_name                   = "premium"
  soft_delete_retention_days = 90
  purge_protection_enabled   = true
}

resource "azurerm_key_vault_key" "azure_key" {
  name         = "azure-key"
  key_vault_id = azurerm_key_vault.azure_kv.id
  key_type     = "RSA"
  key_size     = 2048

  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]
}

resource "azurerm_disk_encryption_set" "azure_des" {
  name                = "azure-des"
  resource_group_name = azurerm_resource_group.multi_cloud_rg.name
  location            = azurerm_resource_group.multi_cloud_rg.location
  key_vault_key_id    = azurerm_key_vault_key.azure_key.id

  identity {
    type = "SystemAssigned"
  }
}
