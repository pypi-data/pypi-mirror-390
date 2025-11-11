# Azure Infrastructure Example - INSECURE VERSION
# This example contains intentional security violations for learning purposes
# Run: riveter scan -p azure-security -t insecure.tf

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group without proper tags
resource "azurerm_resource_group" "main" {
  name     = "rg-insecure-example"
  location = "East US"

  # Missing required tags - will fail validation
}

# INSECURE: Virtual Network with overly broad address space
resource "azurerm_virtual_network" "main" {
  name                = "vnet-insecure"
  address_space       = ["10.0.0.0/8"]  # ❌ Too broad
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # Missing required tags - will fail validation
}

# Public subnet with no network security group
resource "azurerm_subnet" "public" {
  name                 = "subnet-public"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# INSECURE: Network Security Group with overly permissive rules
resource "azurerm_network_security_group" "web" {
  name                = "nsg-web-insecure"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # PROBLEM: SSH open to the world
  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"  # ❌ Should be restricted
    destination_address_prefix = "*"
  }

  # PROBLEM: RDP open to the world
  security_rule {
    name                       = "RDP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"  # ❌ Should be restricted
    destination_address_prefix = "*"
  }

  # PROBLEM: All outbound traffic allowed
  security_rule {
    name                       = "AllowAllOutbound"
    priority                   = 1003
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"  # ❌ Should be restricted
  }

  # Missing required tags - will fail validation
}

# Associate NSG with subnet
resource "azurerm_subnet_network_security_group_association" "web" {
  subnet_id                 = azurerm_subnet.public.id
  network_security_group_id = azurerm_network_security_group.web.id
}

# INSECURE: Public IP for VM
resource "azurerm_public_ip" "web" {
  name                = "pip-web-insecure"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                 = "Standard"

  # Missing required tags - will fail validation
}

# Network Interface with public IP
resource "azurerm_network_interface" "web" {
  name                = "nic-web-insecure"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.public.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.web.id  # ❌ Should not have public IP
  }

  # Missing required tags - will fail validation
}

# INSECURE: Virtual Machine with unencrypted disks
resource "azurerm_linux_virtual_machine" "web" {
  name                = "vm-web-insecure"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_B1s"
  admin_username      = "adminuser"

  # PROBLEM: Password authentication enabled
  disable_password_authentication = false  # ❌ Should use SSH keys only

  network_interface_ids = [
    azurerm_network_interface.web.id,
  ]

  admin_password = "P@ssw0rd123!"  # ❌ Hardcoded password

  # PROBLEM: Unencrypted OS disk
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    # Missing encryption settings - will fail validation
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }

  # Missing required tags - will fail validation
}

# INSECURE: Storage Account with public access
resource "azurerm_storage_account" "data" {
  name                     = "stinsecure${random_id.suffix.hex}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # PROBLEM: Public access allowed
  public_network_access_enabled = true  # ❌ Should be false
  
  # PROBLEM: No minimum TLS version set
  min_tls_version = "TLS1_0"  # ❌ Should be TLS1_2

  # PROBLEM: HTTPS not enforced
  enable_https_traffic_only = false  # ❌ Should be true

  # Missing required tags - will fail validation
}

# INSECURE: SQL Server with weak configuration
resource "azurerm_mssql_server" "main" {
  name                         = "sqlserver-insecure-${random_id.suffix.hex}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd123!"  # ❌ Hardcoded password

  # PROBLEM: Public network access enabled
  public_network_access_enabled = true  # ❌ Should be false

  # Missing required tags - will fail validation
}

# INSECURE: SQL Database without encryption
resource "azurerm_mssql_database" "main" {
  name      = "database-insecure"
  server_id = azurerm_mssql_server.main.id

  # PROBLEM: No transparent data encryption
  # Missing encryption configuration

  # Missing required tags - will fail validation
}

# INSECURE: SQL Firewall rule allowing all IPs
resource "azurerm_mssql_firewall_rule" "allow_all" {
  name             = "AllowAll"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"  # ❌ Should be restricted
  end_ip_address   = "255.255.255.255"  # ❌ Should be restricted
}

# INSECURE: Key Vault with public access
resource "azurerm_key_vault" "main" {
  name                = "kv-insecure-${random_id.suffix.hex}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  # PROBLEM: Public network access enabled
  public_network_access_enabled = true  # ❌ Should be false

  # PROBLEM: No access policy restrictions
  # Missing proper access policies

  # Missing required tags - will fail validation
}

data "azurerm_client_config" "current" {}

resource "random_id" "suffix" {
  byte_length = 4
}

# Insecure outputs exposing sensitive information
output "vm_public_ip" {
  value = azurerm_public_ip.web.ip_address
  description = "Public IP of VM (INSECURE - should not exist!)"
}

output "sql_server_fqdn" {
  value = azurerm_mssql_server.main.fully_qualified_domain_name
  description = "SQL Server FQDN (INSECURE - publicly accessible!)"
}

output "storage_account_primary_key" {
  value = azurerm_storage_account.data.primary_access_key
  sensitive = false  # ❌ Should be sensitive
  description = "Storage account key (INSECURE - exposed in output!)"
}