# Azure Infrastructure Example - SECURE VERSION
# This example shows the same infrastructure with security best practices applied
# Run: riveter scan -p azure-security -t secure.tf

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

# Resource Group with proper tags
resource "azurerm_resource_group" "main" {
  name     = "rg-secure-example"
  location = "East US"

  tags = {
    Name        = "secure-example-rg"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# SECURE: Virtual Network with appropriate address space
resource "azurerm_virtual_network" "main" {
  name                = "vnet-secure"
  address_space       = ["10.0.0.0/16"]  # ✅ Appropriately sized
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    Name        = "main-vnet"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# Private subnet for application servers
resource "azurerm_subnet" "private" {
  name                 = "subnet-private"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Public subnet for load balancer only
resource "azurerm_subnet" "public" {
  name                 = "subnet-public"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Database subnet
resource "azurerm_subnet" "database" {
  name                 = "subnet-database"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.3.0/24"]
  
  delegation {
    name = "sql-delegation"
    service_delegation {
      name = "Microsoft.Sql/managedInstances"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action"
      ]
    }
  }
}

# SECURE: Network Security Group for application servers
resource "azurerm_network_security_group" "app" {
  name                = "nsg-app-secure"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # ✅ Only HTTP from load balancer subnet
  security_rule {
    name                       = "AllowHTTPFromLB"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "10.0.2.0/24"  # Only from public subnet
    destination_address_prefix = "*"
  }

  # ✅ SSH only from management subnet
  security_rule {
    name                       = "AllowSSHFromMgmt"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "10.0.0.0/16"  # Only from VNet
    destination_address_prefix = "*"
  }

  # ✅ Deny all other inbound traffic
  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # ✅ Restricted outbound rules
  security_rule {
    name                       = "AllowHTTPSOutbound"
    priority                   = 1001
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "Internet"
  }

  security_rule {
    name                       = "AllowDatabaseOutbound"
    priority                   = 1002
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "1433"
    source_address_prefix      = "*"
    destination_address_prefix = "10.0.3.0/24"  # Database subnet
  }

  tags = {
    Name        = "app-nsg"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# SECURE: Network Security Group for database
resource "azurerm_network_security_group" "database" {
  name                = "nsg-database-secure"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # ✅ Only SQL from application subnet
  security_rule {
    name                       = "AllowSQLFromApp"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "1433"
    source_address_prefix      = "10.0.1.0/24"  # Only from app subnet
    destination_address_prefix = "*"
  }

  # ✅ Deny all other traffic
  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    Name        = "database-nsg"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# Associate NSGs with subnets
resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.private.id
  network_security_group_id = azurerm_network_security_group.app.id
}

resource "azurerm_subnet_network_security_group_association" "database" {
  subnet_id                 = azurerm_subnet.database.id
  network_security_group_id = azurerm_network_security_group.database.id
}

# Network Interface without public IP
resource "azurerm_network_interface" "web" {
  name                = "nic-web-secure"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.private.id  # ✅ Private subnet
    private_ip_address_allocation = "Dynamic"
    # ✅ No public IP assigned
  }

  tags = {
    Name        = "web-nic"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# SECURE: Virtual Machine with encrypted disks and SSH keys
resource "azurerm_linux_virtual_machine" "web" {
  name                = "vm-web-secure"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_B2s"  # ✅ Appropriate size
  admin_username      = "adminuser"

  # ✅ SSH key authentication only
  disable_password_authentication = true

  network_interface_ids = [
    azurerm_network_interface.web.id,
  ]

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("~/.ssh/id_rsa.pub")  # ✅ SSH key authentication
  }

  # ✅ Encrypted OS disk
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    encryption_at_host_enabled = true  # ✅ Host-based encryption
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }

  # ✅ System-assigned managed identity
  identity {
    type = "SystemAssigned"
  }

  tags = {
    Name        = "web-server"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
    Backup      = "daily"
  }
}

# SECURE: Storage Account with private access
resource "azurerm_storage_account" "data" {
  name                     = "stsecure${random_id.suffix.hex}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"  # ✅ Geo-redundant storage

  # ✅ Private access only
  public_network_access_enabled = false
  
  # ✅ Minimum TLS 1.2
  min_tls_version = "TLS1_2"

  # ✅ HTTPS enforced
  enable_https_traffic_only = true

  # ✅ Infrastructure encryption
  infrastructure_encryption_enabled = true

  tags = {
    Name        = "application-storage"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# SECURE: Key Vault for secrets management
resource "azurerm_key_vault" "main" {
  name                = "kv-secure-${random_id.suffix.hex}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "premium"  # ✅ Premium for HSM support

  # ✅ Private access only
  public_network_access_enabled = false

  # ✅ Purge protection enabled
  purge_protection_enabled = true

  # ✅ Soft delete enabled
  soft_delete_retention_days = 90

  tags = {
    Name        = "main-keyvault"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# Key Vault access policy for VM managed identity
resource "azurerm_key_vault_access_policy" "vm" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_linux_virtual_machine.web.identity[0].principal_id

  secret_permissions = [
    "Get",
    "List"
  ]
}

# SECURE: SQL Server with private access and Azure AD authentication
resource "azurerm_mssql_server" "main" {
  name                         = "sqlserver-secure-${random_id.suffix.hex}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = random_password.sql_password.result  # ✅ Generated password

  # ✅ Private access only
  public_network_access_enabled = false

  # ✅ Azure AD authentication
  azuread_administrator {
    login_username = "sqladmin"
    object_id      = data.azurerm_client_config.current.object_id
  }

  tags = {
    Name        = "main-sql-server"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# Store SQL password in Key Vault
resource "random_password" "sql_password" {
  length  = 16
  special = true
}

resource "azurerm_key_vault_secret" "sql_password" {
  name         = "sql-admin-password"
  value        = random_password.sql_password.result
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.vm]
}

# SECURE: SQL Database with encryption
resource "azurerm_mssql_database" "main" {
  name      = "database-secure"
  server_id = azurerm_mssql_server.main.id
  sku_name  = "S1"

  # ✅ Transparent data encryption enabled by default
  # ✅ Threat detection enabled
  threat_detection_policy {
    state           = "Enabled"
    email_addresses = ["security@company.com"]
  }

  tags = {
    Name        = "main-database"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# Private endpoint for SQL Server
resource "azurerm_private_endpoint" "sql" {
  name                = "pe-sql-secure"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.database.id

  private_service_connection {
    name                           = "psc-sql"
    private_connection_resource_id = azurerm_mssql_server.main.id
    subresource_names              = ["sqlServer"]
    is_manual_connection           = false
  }

  tags = {
    Name        = "sql-private-endpoint"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

data "azurerm_client_config" "current" {}

resource "random_id" "suffix" {
  byte_length = 4
}

# Secure outputs (no sensitive information)
output "resource_group_name" {
  value       = azurerm_resource_group.main.name
  description = "Resource group name for reference"
}

output "virtual_network_id" {
  value       = azurerm_virtual_network.main.id
  description = "Virtual network ID for reference"
}

output "key_vault_uri" {
  value       = azurerm_key_vault.main.vault_uri
  description = "Key Vault URI for application configuration"
}