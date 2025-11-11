# Azure Security Best Practices Test Fixtures
# This file contains both passing and failing examples for azure-security rule pack

# ============================================================================
# RESOURCE GROUP
# ============================================================================

resource "azurerm_resource_group" "test_rg" {
  name     = "test-resources"
  location = "East US"

  tags = {
    Environment = "production"
    Owner       = "platform-team"
    CostCenter  = "engineering"
  }
}

# ============================================================================
# VIRTUAL MACHINE RESOURCES
# ============================================================================

# PASS: VM with all security best practices
resource "azurerm_linux_virtual_machine" "secure_vm" {
  name                = "secure-vm"
  resource_group_name = azurerm_resource_group.test_rg.name
  location            = azurerm_resource_group.test_rg.location
  size                = "Standard_D2s_v3"
  admin_username      = "adminuser"

  disable_password_authentication = true

  network_interface_ids = [
    azurerm_network_interface.secure_nic.id,
  ]

  admin_ssh_key {
    username   = "adminuser"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"

    disk_encryption_set_id = azurerm_disk_encryption_set.secure_des.id
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
    Environment = "production"
    Owner       = "platform-team"
    CostCenter  = "engineering"
  }
}

# FAIL: VM without disk encryption
resource "azurerm_linux_virtual_machine" "no_encryption" {
  name                = "no-encryption-vm"
  resource_group_name = azurerm_resource_group.test_rg.name
  location            = azurerm_resource_group.test_rg.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.secure_nic.id,
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
  }
}

# FAIL: VM with public IP in production
resource "azurerm_linux_virtual_machine" "public_ip_vm" {
  name                = "public-ip-vm"
  resource_group_name = azurerm_resource_group.test_rg.name
  location            = azurerm_resource_group.test_rg.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.public_nic.id,
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
  }
}

# FAIL: VM without managed identity
resource "azurerm_linux_virtual_machine" "no_managed_identity" {
  name                = "no-identity-vm"
  resource_group_name = azurerm_resource_group.test_rg.name
  location            = azurerm_resource_group.test_rg.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.secure_nic.id,
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
  }
}

# FAIL: VM without required tags
resource "azurerm_linux_virtual_machine" "missing_tags" {
  name                = "missing-tags-vm"
  resource_group_name = azurerm_resource_group.test_rg.name
  location            = azurerm_resource_group.test_rg.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.secure_nic.id,
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
}

# ============================================================================
# STORAGE ACCOUNT RESOURCES
# ============================================================================

# PASS: Storage account with all security best practices
resource "azurerm_storage_account" "secure_storage" {
  name                     = "securestorage12345"
  resource_group_name      = azurerm_resource_group.test_rg.name
  location                 = azurerm_resource_group.test_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  enable_https_traffic_only       = true
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 30
    }

    container_delete_retention_policy {
      days = 30
    }
  }

  network_rules {
    default_action = "Deny"
    bypass         = ["AzureServices"]
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "production"
    Owner       = "platform-team"
  }
}

# FAIL: Storage account without HTTPS enforcement
resource "azurerm_storage_account" "no_https" {
  name                     = "nohttps12345"
  resource_group_name      = azurerm_resource_group.test_rg.name
  location                 = azurerm_resource_group.test_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = false
}

# FAIL: Storage account with public access allowed
resource "azurerm_storage_account" "public_access" {
  name                     = "publicaccess12345"
  resource_group_name      = azurerm_resource_group.test_rg.name
  location                 = azurerm_resource_group.test_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only       = true
  allow_nested_items_to_be_public = true
}

# FAIL: Storage account without soft delete
resource "azurerm_storage_account" "no_soft_delete" {
  name                     = "nosoftdelete12345"
  resource_group_name      = azurerm_resource_group.test_rg.name
  location                 = azurerm_resource_group.test_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = true
}

# FAIL: Storage account without minimum TLS version
resource "azurerm_storage_account" "no_min_tls" {
  name                     = "nomintls12345"
  resource_group_name      = azurerm_resource_group.test_rg.name
  location                 = azurerm_resource_group.test_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  enable_https_traffic_only = true
}

# ============================================================================
# SQL DATABASE RESOURCES
# ============================================================================

# PASS: SQL Server with all security best practices
resource "azurerm_mssql_server" "secure_sql" {
  name                         = "secure-sqlserver"
  resource_group_name          = azurerm_resource_group.test_rg.name
  location                     = azurerm_resource_group.test_rg.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd1234!"
  minimum_tls_version          = "1.2"

  azuread_administrator {
    login_username = "sqladmin"
    object_id      = "00000000-0000-0000-0000-000000000000"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "production"
  }
}

# PASS: SQL Database with TDE and threat detection
resource "azurerm_mssql_database" "secure_db" {
  name      = "secure-database"
  server_id = azurerm_mssql_server.secure_sql.id
  sku_name  = "S1"

  transparent_data_encryption_enabled = true

  tags = {
    Environment = "production"
  }
}

resource "azurerm_mssql_server_security_alert_policy" "secure_threat_detection" {
  resource_group_name = azurerm_resource_group.test_rg.name
  server_name         = azurerm_mssql_server.secure_sql.name
  state               = "Enabled"

  email_account_admins = true
}

# FAIL: SQL Database without TDE
resource "azurerm_mssql_database" "no_tde" {
  name      = "no-tde-database"
  server_id = azurerm_mssql_server.secure_sql.id
  sku_name  = "S1"

  transparent_data_encryption_enabled = false
}

# FAIL: SQL Server without firewall rules configured properly
resource "azurerm_mssql_firewall_rule" "allow_all" {
  name             = "allow-all"
  server_id        = azurerm_mssql_server.secure_sql.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

# FAIL: SQL Server without threat detection
resource "azurerm_mssql_server" "no_threat_detection" {
  name                         = "no-threat-detection-sql"
  resource_group_name          = azurerm_resource_group.test_rg.name
  location                     = azurerm_resource_group.test_rg.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd1234!"
}

# ============================================================================
# NETWORK SECURITY GROUP RESOURCES
# ============================================================================

# PASS: NSG with proper rules
resource "azurerm_network_security_group" "secure_nsg" {
  name                = "secure-nsg"
  location            = azurerm_resource_group.test_rg.location
  resource_group_name = azurerm_resource_group.test_rg.name

  tags = {
    Environment = "production"
  }
}

resource "azurerm_network_security_rule" "secure_ssh" {
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
  resource_group_name         = azurerm_resource_group.test_rg.name
  network_security_group_name = azurerm_network_security_group.secure_nsg.name
}

# FAIL: NSG rule allowing SSH from anywhere
resource "azurerm_network_security_rule" "insecure_ssh" {
  name                        = "AllowSSHFromInternet"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.test_rg.name
  network_security_group_name = azurerm_network_security_group.secure_nsg.name
}

# FAIL: NSG rule without description
resource "azurerm_network_security_rule" "no_description" {
  name                        = "AllowHTTP"
  priority                    = 200
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "80"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.test_rg.name
  network_security_group_name = azurerm_network_security_group.secure_nsg.name
}

# FAIL: NSG rule allowing all protocols from anywhere
resource "azurerm_network_security_rule" "allow_all" {
  name                        = "AllowAll"
  priority                    = 300
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.test_rg.name
  network_security_group_name = azurerm_network_security_group.secure_nsg.name
}

# ============================================================================
# KEY VAULT RESOURCES
# ============================================================================

# PASS: Key Vault with all security best practices
resource "azurerm_key_vault" "secure_kv" {
  name                       = "secure-keyvault-12345"
  location                   = azurerm_resource_group.test_rg.location
  resource_group_name        = azurerm_resource_group.test_rg.name
  tenant_id                  = "00000000-0000-0000-0000-000000000000"
  sku_name                   = "premium"
  soft_delete_retention_days = 90
  purge_protection_enabled   = true

  enabled_for_disk_encryption = true

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }

  tags = {
    Environment = "production"
  }
}

# FAIL: Key Vault without soft delete
resource "azurerm_key_vault" "no_soft_delete" {
  name                = "no-soft-delete-kv"
  location            = azurerm_resource_group.test_rg.location
  resource_group_name = azurerm_resource_group.test_rg.name
  tenant_id           = "00000000-0000-0000-0000-000000000000"
  sku_name            = "standard"

  soft_delete_retention_days = 7
}

# FAIL: Key Vault without purge protection
resource "azurerm_key_vault" "no_purge_protection" {
  name                       = "no-purge-protection-kv"
  location                   = azurerm_resource_group.test_rg.location
  resource_group_name        = azurerm_resource_group.test_rg.name
  tenant_id                  = "00000000-0000-0000-0000-000000000000"
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  purge_protection_enabled   = false
}

# FAIL: Key Vault without network restrictions
resource "azurerm_key_vault" "no_network_acls" {
  name                       = "no-network-acls-kv"
  location                   = azurerm_resource_group.test_rg.location
  resource_group_name        = azurerm_resource_group.test_rg.name
  tenant_id                  = "00000000-0000-0000-0000-000000000000"
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  purge_protection_enabled   = true

  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
  }
}

# ============================================================================
# SUPPORTING RESOURCES
# ============================================================================

resource "azurerm_virtual_network" "test_vnet" {
  name                = "test-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.test_rg.location
  resource_group_name = azurerm_resource_group.test_rg.name
}

resource "azurerm_subnet" "test_subnet" {
  name                 = "test-subnet"
  resource_group_name  = azurerm_resource_group.test_rg.name
  virtual_network_name = azurerm_virtual_network.test_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_network_interface" "secure_nic" {
  name                = "secure-nic"
  location            = azurerm_resource_group.test_rg.location
  resource_group_name = azurerm_resource_group.test_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.test_subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_public_ip" "test_public_ip" {
  name                = "test-public-ip"
  location            = azurerm_resource_group.test_rg.location
  resource_group_name = azurerm_resource_group.test_rg.name
  allocation_method   = "Static"
}

resource "azurerm_network_interface" "public_nic" {
  name                = "public-nic"
  location            = azurerm_resource_group.test_rg.location
  resource_group_name = azurerm_resource_group.test_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.test_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.test_public_ip.id
  }
}

resource "azurerm_disk_encryption_set" "secure_des" {
  name                = "secure-des"
  resource_group_name = azurerm_resource_group.test_rg.name
  location            = azurerm_resource_group.test_rg.location
  key_vault_key_id    = azurerm_key_vault_key.secure_key.id

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_key_vault_key" "secure_key" {
  name         = "secure-key"
  key_vault_id = azurerm_key_vault.secure_kv.id
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
