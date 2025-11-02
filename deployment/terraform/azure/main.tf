# Configuración para proveedor Azure
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
  }

  backend "azurerm" {
    resource_group_name  = "traffic-system-terraform-rg"
    storage_account_name = "trafficsystemtfstate"
    container_name       = "tfstate"
    key                  = "production.terraform.tfstate"
  }
}

# Configuración del proveedor Azure
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Variables
variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "resource_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "traffic-system"
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${var.resource_prefix}-${var.environment}-rg"
  location = var.location

  tags = {
    Environment = var.environment
    Project     = "traffic-system"
    ManagedBy   = "terraform"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${var.resource_prefix}-${var.environment}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    Environment = var.environment
  }
}

# Subnets
resource "azurerm_subnet" "aks" {
  name                 = "${var.resource_prefix}-${var.environment}-aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "database" {
  name                 = "${var.resource_prefix}-${var.environment}-db-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
  
  delegation {
    name = "fs"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

# Network Security Group
resource "azurerm_network_security_group" "database" {
  name                = "${var.resource_prefix}-${var.environment}-db-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "PostgreSQL"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = "10.0.1.0/24"
    destination_address_prefix = "*"
  }

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_subnet_network_security_group_association" "database" {
  subnet_id                 = azurerm_subnet.database.id
  network_security_group_id = azurerm_network_security_group.database.id
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.resource_prefix}-${var.environment}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${var.resource_prefix}-${var.environment}"
  kubernetes_version  = "1.28.3"

  default_node_pool {
    name                = "general"
    node_count          = var.environment == "production" ? 3 : 2
    vm_size             = var.environment == "production" ? "Standard_D4s_v3" : "Standard_D2s_v3"
    vnet_subnet_id      = azurerm_subnet.aks.id
    enable_auto_scaling = true
    min_count           = var.environment == "production" ? 2 : 1
    max_count           = var.environment == "production" ? 10 : 5
    
    upgrade_settings {
      max_surge = "10%"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
    network_policy = "azure"
  }

  # Monitoring
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  tags = {
    Environment = var.environment
  }
}

# Additional Node Pool para ML workloads
resource "azurerm_kubernetes_cluster_node_pool" "ml_workloads" {
  name                  = "mlworkloads"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.environment == "production" ? "Standard_F8s_v2" : "Standard_F4s_v2"
  node_count            = var.environment == "production" ? 2 : 1
  enable_auto_scaling   = true
  min_count             = 0
  max_count             = var.environment == "production" ? 8 : 3
  vnet_subnet_id        = azurerm_subnet.aks.id
  
  node_taints = ["workload-type=ml:NoSchedule"]
  
  node_labels = {
    "workload-type" = "ml"
  }

  tags = {
    Environment = var.environment
    NodePool    = "ml-workloads"
  }
}

# PostgreSQL Flexible Server
resource "azurerm_private_dns_zone" "postgres" {
  name                = "${var.resource_prefix}-${var.environment}-postgres.private.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "${var.resource_prefix}-${var.environment}-postgres-vnet-link"
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = azurerm_virtual_network.main.id
  resource_group_name   = azurerm_resource_group.main.name

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.resource_prefix}-${var.environment}-postgres"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "15"
  delegated_subnet_id    = azurerm_subnet.database.id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres.id
  administrator_login    = "trafficadmin"
  administrator_password = random_password.postgres_password.result
  zone                   = "1"

  storage_mb = var.environment == "production" ? 32768 : 8192
  sku_name   = var.environment == "production" ? "GP_Standard_D4s_v3" : "GP_Standard_D2s_v3"

  backup_retention_days        = var.environment == "production" ? 35 : 7
  geo_redundant_backup_enabled = var.environment == "production"

  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "trafficdb"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

resource "random_password" "postgres_password" {
  length  = 16
  special = true
}

# Redis Cache
resource "azurerm_redis_cache" "main" {
  name                = "${var.resource_prefix}-${var.environment}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = var.environment == "production" ? 2 : 1
  family              = var.environment == "production" ? "P" : "C"
  sku_name            = var.environment == "production" ? "Premium" : "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  redis_configuration {
    enable_authentication = true
  }

  tags = {
    Environment = var.environment
  }
}

# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "${replace(var.resource_prefix, "-", "")}${var.environment}storage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = var.environment == "production" ? "GRS" : "LRS"
  account_kind             = "StorageV2"

  blob_properties {
    versioning_enabled = true
    
    delete_retention_policy {
      days = var.environment == "production" ? 30 : 7
    }
  }

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_storage_container" "images" {
  name                  = "vehicle-images"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "models" {
  name                  = "ml-models"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.resource_prefix}-${var.environment}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.environment == "production" ? 90 : 30

  tags = {
    Environment = var.environment
  }
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "${var.resource_prefix}-${var.environment}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"

  tags = {
    Environment = var.environment
  }
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                = "${var.resource_prefix}-${var.environment}-kv"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get",
    ]

    secret_permissions = [
      "Get",
      "Set",
      "List",
      "Delete",
      "Purge",
      "Recover"
    ]
  }

  # Access policy para AKS
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id

    secret_permissions = [
      "Get",
    ]
  }

  tags = {
    Environment = var.environment
  }
}

data "azurerm_client_config" "current" {}

# Key Vault Secrets
resource "azurerm_key_vault_secret" "postgres_password" {
  name         = "postgres-password"
  value        = random_password.postgres_password.result
  key_vault_id = azurerm_key_vault.main.id

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_key_vault_secret" "redis_password" {
  name         = "redis-password"
  value        = azurerm_redis_cache.main.primary_access_key
  key_vault_id = azurerm_key_vault.main.id

  tags = {
    Environment = var.environment
  }
}

# Outputs
output "cluster_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.main.name
}

output "cluster_endpoint" {
  description = "AKS cluster endpoint"
  value       = azurerm_kubernetes_cluster.main.kube_config.0.host
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "postgres_server_name" {
  description = "PostgreSQL server name"
  value       = azurerm_postgresql_flexible_server.main.name
}

output "postgres_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "redis_hostname" {
  description = "Redis hostname"
  value       = azurerm_redis_cache.main.hostname
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.main.name
}

output "key_vault_name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.main.name
}

output "application_insights_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}