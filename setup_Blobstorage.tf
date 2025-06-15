provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "billing_rg" {
  name     = "billing-archive-rg"
  location = "East US"
}

resource "azurerm_storage_account" "archive_sa" {
  name                     = "billingarchivestorage"
  resource_group_name      = azurerm_resource_group.billing_rg.name
  location                 = azurerm_resource_group.billing_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  access_tier              = "Hot"

  enable_https_traffic_only = true
}

resource "azurerm_storage_container" "archive_container" {
  name                  = "billing-archive"
  storage_account_name  = azurerm_storage_account.archive_sa.name
  container_access_type = "private"
}

output "blob_connection_string" {
  value     = azurerm_storage_account.archive_sa.primary_connection_string
  sensitive = true
}
