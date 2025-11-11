# Azure HIPAA Compliance Test Fixtures
# This file contains both passing and failing examples for azure-hipaa rule pack

# ============================================================================
# RESOURCE GROUP
# ============================================================================

resource "azurerm_resource_group" "hipaa_rg" {
  name     = "hipaa-test-resources"
  location = "East US"

  tags = {
    Environment        = "production"
    DataClassification = "PHI"
    Owner              = "healthcare-team"
    CostCenter         = "healthcare"
  }
}

# ============================================================================
# ENCRYPTION RULES TEST FIXTURES
# ============================================================================

# PASS: Storage account with PHI tag and proper encryption
resource "azurerm_storage_account" "hipaa_compliant_storage" {
  name                     = "hipaacompliant12345"
  resource_group_name      = azurerm_resource_group.hipaa_rg.name
  location                 = azurerm_resource_group.hipaa_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  enable_https_traffic_only = true
  min_tls_version          = "TLS1_2"
  allow_blob_public_access = false

  customer_managed_key {
    key_vault_key_id          = azurerm_key_vault_key.hipaa_key.id
    user_assigned_identity_id = azurerm_user_assigned_identity.storage_identity.id
  }

  blob_properties {
    delete_retention_policy {
      days = 30
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment           = "production"
    DataClassification    = "PHI"
    LoggingEnabled       = "true"
    PrivateEndpointEnabled = "true"
  }
}

# FAIL: Storage account with PHI tag but no HTTPS enforcement
resource "azurerm_storage_account" "hipaa_no_https" {
  name                     = "hipaanohttps12345"
  resource_group_name      = azurerm_resource_group.hipaa_rg.name
  location                 = azurerm_resource_group.hipaa_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = false
  min_tls_version          = "TLS1_0"

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: Storage account with PHI tag but no customer-managed key
resource "azurerm_storage_account" "hipaa_no_cmk" {
  name                     = "hipaanocmk12345"
  resource_group_name      = azurerm_resource_group.hipaa_rg.name
  location                 = azurerm_resource_group.hipaa_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = true
  min_tls_version          = "TLS1_2"

  tags = {
    DataClassification = "PHI"
  }
}

# PASS: SQL Database with TDE enabled
resource "azurerm_mssql_server" "hipaa_sql_server" {
  name                         = "hipaa-sql-server"
  resource_group_name          = azurerm_resource_group.hipaa_rg.name
  location                     = azurerm_resource_group.hipaa_rg.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd1234!"
  minimum_tls_version          = "1.2"
  public_network_access_enabled = false

  extended_auditing_policy {
    enabled                = true
    storage_endpoint       = azurerm_storage_account.audit_storage.primary_blob_endpoint
    storage_account_access_key = azurerm_storage_account.audit_storage.primary_access_key
    retention_in_days      = 365
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment           = "production"
    DataClassification    = "PHI"
    PrivateEndpointEnabled = "true"
  }
}

resource "azurerm_mssql_database" "hipaa_database" {
  name      = "hipaa-database"
  server_id = azurerm_mssql_server.hipaa_sql_server.id
  sku_name  = "S1"

  transparent_data_encryption_enabled = true

  short_term_retention_policy {
    retention_days = 14
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: SQL Database without TDE
resource "azurerm_mssql_database" "hipaa_no_tde" {
  name      = "hipaa-no-tde-db"
  server_id = azurerm_mssql_server.hipaa_sql_server.id
  sku_name  = "S1"

  transparent_data_encryption_enabled = false

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: SQL Server with public network access enabled
resource "azurerm_mssql_server" "hipaa_public_sql" {
  name                         = "hipaa-public-sql"
  resource_group_name          = azurerm_resource_group.hipaa_rg.name
  location                     = azurerm_resource_group.hipaa_rg.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd1234!"
  public_network_access_enabled = true

  tags = {
    DataClassification = "PHI"
  }
}

# PASS: VM with disk encryption enabled
resource "azurerm_linux_virtual_machine" "hipaa_vm" {
  name                = "hipaa-vm"
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  location            = azurerm_resource_group.hipaa_rg.location
  size                = "Standard_D2s_v3"
  admin_username      = "adminuser"

  encryption_at_host_enabled = true

  network_interface_ids = [
    azurerm_network_interface.hipaa_nic.id,
  ]

  admin_ssh_key {
    username   = "adminuser"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_encryption_set_id = azurerm_disk_encryption_set.hipaa_des.id
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment        = "production"
    DataClassification = "PHI"
  }
}

# FAIL: VM without encryption at host
resource "azurerm_linux_virtual_machine" "hipaa_vm_no_encryption" {
  name                = "hipaa-vm-no-encryption"
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  location            = azurerm_resource_group.hipaa_rg.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  encryption_at_host_enabled = false

  network_interface_ids = [
    azurerm_network_interface.hipaa_nic.id,
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
    DataClassification = "PHI"
  }
}

# PASS: Managed disk with encryption
resource "azurerm_managed_disk" "hipaa_disk" {
  name                 = "hipaa-disk"
  location             = azurerm_resource_group.hipaa_rg.location
  resource_group_name  = azurerm_resource_group.hipaa_rg.name
  storage_account_type = "Premium_LRS"
  create_option        = "Empty"
  disk_size_gb         = 100

  encryption_settings {
    enabled = true
    disk_encryption_key {
      secret_url      = azurerm_key_vault_secret.disk_secret.id
      source_vault_id = azurerm_key_vault.hipaa_kv.id
    }
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: Managed disk without encryption
resource "azurerm_managed_disk" "hipaa_disk_no_encryption" {
  name                 = "hipaa-disk-no-encryption"
  location             = azurerm_resource_group.hipaa_rg.location
  resource_group_name  = azurerm_resource_group.hipaa_rg.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = 100

  tags = {
    DataClassification = "PHI"
  }
}

# PASS: Cosmos DB with customer-managed key
resource "azurerm_cosmosdb_account" "hipaa_cosmos" {
  name                = "hipaa-cosmos-db"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  key_vault_key_id             = azurerm_key_vault_key.cosmos_key.id
  public_network_access_enabled = false

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.hipaa_rg.location
    failover_priority = 0
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: Cosmos DB without customer-managed key
resource "azurerm_cosmosdb_account" "hipaa_cosmos_no_cmk" {
  name                = "hipaa-cosmos-no-cmk"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.hipaa_rg.location
    failover_priority = 0
  }

  tags = {
    DataClassification = "PHI"
  }
}

# PASS: App Service with HTTPS only
resource "azurerm_app_service" "hipaa_app" {
  name                = "hipaa-app-service"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  app_service_plan_id = azurerm_app_service_plan.hipaa_plan.id

  https_only = true

  auth_settings {
    enabled = true
    default_provider = "AzureActiveDirectory"
    
    active_directory {
      client_id = "00000000-0000-0000-0000-000000000000"
    }
  }

  site_config {
    vnet_route_all_enabled = true
    min_tls_version        = "1.2"
  }

  logs {
    application_logs {
      file_system {
        level = "Information"
      }
    }
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: App Service without HTTPS only
resource "azurerm_app_service" "hipaa_app_no_https" {
  name                = "hipaa-app-no-https"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  app_service_plan_id = azurerm_app_service_plan.hipaa_plan.id

  https_only = false

  tags = {
    DataClassification = "PHI"
  }
}

# PASS: Function App with HTTPS only
resource "azurerm_function_app" "hipaa_function" {
  name                       = "hipaa-function-app"
  location                   = azurerm_resource_group.hipaa_rg.location
  resource_group_name        = azurerm_resource_group.hipaa_rg.name
  app_service_plan_id        = azurerm_app_service_plan.hipaa_plan.id
  storage_account_name       = azurerm_storage_account.hipaa_compliant_storage.name
  storage_account_access_key = azurerm_storage_account.hipaa_compliant_storage.primary_access_key

  https_only = true

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: Function App without HTTPS only
resource "azurerm_function_app" "hipaa_function_no_https" {
  name                       = "hipaa-function-no-https"
  location                   = azurerm_resource_group.hipaa_rg.location
  resource_group_name        = azurerm_resource_group.hipaa_rg.name
  app_service_plan_id        = azurerm_app_service_plan.hipaa_plan.id
  storage_account_name       = azurerm_storage_account.hipaa_compliant_storage.name
  storage_account_access_key = azurerm_storage_account.hipaa_compliant_storage.primary_access_key

  https_only = false

  tags = {
    DataClassification = "PHI"
  }
}

# ============================================================================
# ACCESS CONTROLS RULES TEST FIXTURES
# ============================================================================

# FAIL: Storage account with public blob access enabled
resource "azurerm_storage_account" "hipaa_public_access" {
  name                     = "hipaapublic12345"
  resource_group_name      = azurerm_resource_group.hipaa_rg.name
  location                 = azurerm_resource_group.hipaa_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = true
  allow_blob_public_access = true

  tags = {
    DataClassification = "PHI"
  }
}

# PASS: Key Vault with network ACLs default deny
resource "azurerm_key_vault" "hipaa_kv" {
  name                       = "hipaa-keyvault-12345"
  location                   = azurerm_resource_group.hipaa_rg.location
  resource_group_name        = azurerm_resource_group.hipaa_rg.name
  tenant_id                  = "00000000-0000-0000-0000-000000000000"
  sku_name                   = "premium"
  soft_delete_retention_days = 90
  purge_protection_enabled   = true

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }

  tags = {
    Environment    = "production"
    LoggingEnabled = "true"
  }
}

# FAIL: Key Vault with network ACLs default allow
resource "azurerm_key_vault" "hipaa_kv_allow" {
  name                       = "hipaa-kv-allow-12345"
  location                   = azurerm_resource_group.hipaa_rg.location
  resource_group_name        = azurerm_resource_group.hipaa_rg.name
  tenant_id                  = "00000000-0000-0000-0000-000000000000"
  sku_name                   = "standard"
  soft_delete_retention_days = 90

  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
  }
}

# FAIL: VM without managed identity
resource "azurerm_linux_virtual_machine" "hipaa_vm_no_identity" {
  name                = "hipaa-vm-no-identity"
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  location            = azurerm_resource_group.hipaa_rg.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.hipaa_nic.id,
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
    DataClassification = "PHI"
  }
}

# FAIL: Role assignment with Owner role (violates least privilege)
resource "azurerm_role_assignment" "hipaa_owner_role" {
  scope                = azurerm_resource_group.hipaa_rg.id
  role_definition_name = "Owner"
  principal_id         = "00000000-0000-0000-0000-000000000000"
}

# PASS: Role assignment with Reader role (follows least privilege)
resource "azurerm_role_assignment" "hipaa_reader_role" {
  scope                = azurerm_resource_group.hipaa_rg.id
  role_definition_name = "Reader"
  principal_id         = "00000000-0000-0000-0000-000000000000"
}

# FAIL: Cosmos DB with public network access enabled
resource "azurerm_cosmosdb_account" "hipaa_cosmos_public" {
  name                = "hipaa-cosmos-public"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  public_network_access_enabled = true

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.hipaa_rg.location
    failover_priority = 0
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: App Service without authentication enabled
resource "azurerm_app_service" "hipaa_app_no_auth" {
  name                = "hipaa-app-no-auth"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  app_service_plan_id = azurerm_app_service_plan.hipaa_plan.id

  https_only = true

  auth_settings {
    enabled = false
  }

  tags = {
    DataClassification = "PHI"
  }
}

# ============================================================================
# AUDIT LOGGING RULES TEST FIXTURES
# ============================================================================

# PASS: Activity log with adequate retention
resource "azurerm_monitor_log_profile" "hipaa_log_profile" {
  name = "hipaa-log-profile"

  categories = [
    "Action",
    "Delete",
    "Write",
  ]

  locations = [
    "eastus",
    "westus",
  ]

  retention_policy {
    enabled = true
    days    = 365
  }

  storage_account_id = azurerm_storage_account.audit_storage.id
}

# FAIL: Activity log with inadequate retention
resource "azurerm_monitor_log_profile" "hipaa_log_profile_short" {
  name = "hipaa-log-profile-short"

  categories = [
    "Action",
  ]

  locations = [
    "eastus",
  ]

  retention_policy {
    enabled = true
    days    = 30
  }

  storage_account_id = azurerm_storage_account.audit_storage.id
}

# FAIL: SQL Server without auditing enabled
resource "azurerm_mssql_server" "hipaa_sql_no_audit" {
  name                         = "hipaa-sql-no-audit"
  resource_group_name          = azurerm_resource_group.hipaa_rg.name
  location                     = azurerm_resource_group.hipaa_rg.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd1234!"

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: Storage account without logging enabled tag
resource "azurerm_storage_account" "hipaa_no_logging" {
  name                     = "hipaanologging12345"
  resource_group_name      = azurerm_resource_group.hipaa_rg.name
  location                 = azurerm_resource_group.hipaa_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = true

  tags = {
    DataClassification = "PHI"
  }
}

# PASS: NSG Flow Logs with proper retention
resource "azurerm_network_watcher_flow_log" "hipaa_flow_log" {
  network_watcher_name = azurerm_network_watcher.hipaa_watcher.name
  resource_group_name  = azurerm_resource_group.hipaa_rg.name

  network_security_group_id = azurerm_network_security_group.hipaa_nsg.id
  storage_account_id        = azurerm_storage_account.audit_storage.id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = 365
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = azurerm_log_analytics_workspace.hipaa_workspace.workspace_id
    workspace_region      = azurerm_log_analytics_workspace.hipaa_workspace.location
    workspace_resource_id = azurerm_log_analytics_workspace.hipaa_workspace.id
  }
}

# FAIL: NSG Flow Logs with inadequate retention
resource "azurerm_network_watcher_flow_log" "hipaa_flow_log_short" {
  network_watcher_name = azurerm_network_watcher.hipaa_watcher.name
  resource_group_name  = azurerm_resource_group.hipaa_rg.name

  network_security_group_id = azurerm_network_security_group.hipaa_nsg.id
  storage_account_id        = azurerm_storage_account.audit_storage.id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = 30
  }
}

# FAIL: App Service without application logging
resource "azurerm_app_service" "hipaa_app_no_logging" {
  name                = "hipaa-app-no-logging"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  app_service_plan_id = azurerm_app_service_plan.hipaa_plan.id

  https_only = true

  tags = {
    DataClassification = "PHI"
  }
}

# ============================================================================
# NETWORK SECURITY RULES TEST FIXTURES
# ============================================================================

# PASS: NSG rule with restricted access
resource "azurerm_network_security_rule" "hipaa_restricted_ssh" {
  name                        = "AllowSSHFromCorporate"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix       = "10.0.0.0/8"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.hipaa_rg.name
  network_security_group_name = azurerm_network_security_group.hipaa_nsg.name
}

# FAIL: NSG rule allowing unrestricted access
resource "azurerm_network_security_rule" "hipaa_unrestricted" {
  name                        = "AllowAllInbound"
  priority                    = 200
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.hipaa_rg.name
  network_security_group_name = azurerm_network_security_group.hipaa_nsg.name
}

# FAIL: Network interface with public IP for PHI VM
resource "azurerm_network_interface" "hipaa_public_nic" {
  name                = "hipaa-public-nic"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.hipaa_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.hipaa_public_ip.id
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: App Service without VNet integration for PHI data
resource "azurerm_app_service" "hipaa_app_no_vnet" {
  name                = "hipaa-app-no-vnet"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  app_service_plan_id = azurerm_app_service_plan.hipaa_plan.id

  https_only = true

  site_config {
    vnet_route_all_enabled = false
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: SQL Server without private endpoint enabled tag
resource "azurerm_mssql_server" "hipaa_sql_no_private_endpoint" {
  name                         = "hipaa-sql-no-pe"
  resource_group_name          = azurerm_resource_group.hipaa_rg.name
  location                     = azurerm_resource_group.hipaa_rg.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd1234!"
  public_network_access_enabled = false

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: Storage account without private endpoint enabled tag
resource "azurerm_storage_account" "hipaa_storage_no_pe" {
  name                     = "hipaastorageno12345"
  resource_group_name      = azurerm_resource_group.hipaa_rg.name
  location                 = azurerm_resource_group.hipaa_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = true
  allow_blob_public_access = false

  tags = {
    DataClassification = "PHI"
  }
}

# ============================================================================
# BACKUP AND RECOVERY RULES TEST FIXTURES
# ============================================================================

# PASS: VM with backup protection
resource "azurerm_backup_protected_vm" "hipaa_vm_backup" {
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  recovery_vault_name = azurerm_recovery_services_vault.hipaa_vault.name
  source_vm_id        = azurerm_linux_virtual_machine.hipaa_vm.id
  backup_policy_id    = azurerm_backup_policy_vm.hipaa_backup_policy.id
}

# FAIL: VM without backup protection (no azurerm_backup_protected_vm resource)

# PASS: SQL Database with adequate backup retention
resource "azurerm_mssql_database" "hipaa_db_good_backup" {
  name      = "hipaa-db-good-backup"
  server_id = azurerm_mssql_server.hipaa_sql_server.id
  sku_name  = "S1"

  transparent_data_encryption_enabled = true

  short_term_retention_policy {
    retention_days = 14
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: SQL Database with inadequate backup retention
resource "azurerm_mssql_database" "hipaa_db_short_backup" {
  name      = "hipaa-db-short-backup"
  server_id = azurerm_mssql_server.hipaa_sql_server.id
  sku_name  = "S1"

  transparent_data_encryption_enabled = true

  short_term_retention_policy {
    retention_days = 3
  }

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: Storage account without soft delete
resource "azurerm_storage_account" "hipaa_no_soft_delete" {
  name                     = "hipaanosoftdel12345"
  resource_group_name      = azurerm_resource_group.hipaa_rg.name
  location                 = azurerm_resource_group.hipaa_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = true

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: Key Vault without purge protection
resource "azurerm_key_vault" "hipaa_kv_no_purge" {
  name                       = "hipaa-kv-no-purge"
  location                   = azurerm_resource_group.hipaa_rg.location
  resource_group_name        = azurerm_resource_group.hipaa_rg.name
  tenant_id                  = "00000000-0000-0000-0000-000000000000"
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  purge_protection_enabled   = false

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }
}

# FAIL: Key Vault with inadequate soft delete retention
resource "azurerm_key_vault" "hipaa_kv_short_retention" {
  name                       = "hipaa-kv-short-ret"
  location                   = azurerm_resource_group.hipaa_rg.location
  resource_group_name        = azurerm_resource_group.hipaa_rg.name
  tenant_id                  = "00000000-0000-0000-0000-000000000000"
  sku_name                   = "standard"
  soft_delete_retention_days = 5
  purge_protection_enabled   = true

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }
}

# ============================================================================
# SUPPORTING RESOURCES
# ============================================================================

resource "azurerm_virtual_network" "hipaa_vnet" {
  name                = "hipaa-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
}

resource "azurerm_subnet" "hipaa_subnet" {
  name                 = "hipaa-subnet"
  resource_group_name  = azurerm_resource_group.hipaa_rg.name
  virtual_network_name = azurerm_virtual_network.hipaa_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_interface" "hipaa_nic" {
  name                = "hipaa-nic"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.hipaa_subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_public_ip" "hipaa_public_ip" {
  name                = "hipaa-public-ip"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  allocation_method   = "Static"
}

resource "azurerm_network_security_group" "hipaa_nsg" {
  name                = "hipaa-nsg"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name

  tags = {
    Environment = "production"
  }
}

resource "azurerm_network_watcher" "hipaa_watcher" {
  name                = "hipaa-network-watcher"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
}

resource "azurerm_log_analytics_workspace" "hipaa_workspace" {
  name                = "hipaa-log-analytics"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 365
}

resource "azurerm_storage_account" "audit_storage" {
  name                     = "hipaaaudit12345"
  resource_group_name      = azurerm_resource_group.hipaa_rg.name
  location                 = azurerm_resource_group.hipaa_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  enable_https_traffic_only = true
  min_tls_version          = "TLS1_2"
}

resource "azurerm_app_service_plan" "hipaa_plan" {
  name                = "hipaa-app-service-plan"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name

  sku {
    tier = "Standard"
    size = "S1"
  }
}

resource "azurerm_user_assigned_identity" "storage_identity" {
  name                = "storage-identity"
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  location            = azurerm_resource_group.hipaa_rg.location
}

resource "azurerm_key_vault_key" "hipaa_key" {
  name         = "hipaa-key"
  key_vault_id = azurerm_key_vault.hipaa_kv.id
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

resource "azurerm_key_vault_key" "cosmos_key" {
  name         = "cosmos-key"
  key_vault_id = azurerm_key_vault.hipaa_kv.id
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

resource "azurerm_key_vault_secret" "disk_secret" {
  name         = "disk-secret"
  value        = "secret-value"
  key_vault_id = azurerm_key_vault.hipaa_kv.id
}

resource "azurerm_disk_encryption_set" "hipaa_des" {
  name                = "hipaa-des"
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  location            = azurerm_resource_group.hipaa_rg.location
  key_vault_key_id    = azurerm_key_vault_key.hipaa_key.id

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_recovery_services_vault" "hipaa_vault" {
  name                = "hipaa-recovery-vault"
  location            = azurerm_resource_group.hipaa_rg.location
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  sku                 = "Standard"

  soft_delete_enabled = true
}

resource "azurerm_backup_policy_vm" "hipaa_backup_policy" {
  name                = "hipaa-backup-policy"
  resource_group_name = azurerm_resource_group.hipaa_rg.name
  recovery_vault_name = azurerm_recovery_services_vault.hipaa_vault.name

  backup {
    frequency = "Daily"
    time      = "23:00"
  }

  retention_daily {
    count = 30
  }

  retention_weekly {
    count    = 12
    weekdays = ["Sunday"]
  }

  retention_monthly {
    count    = 12
    weekdays = ["Sunday"]
    weeks    = ["First"]
  }

  retention_yearly {
    count    = 7
    weekdays = ["Sunday"]
    weeks    = ["First"]
    months   = ["January"]
  }
}