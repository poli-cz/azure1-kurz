terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  # Předplatné se bere z: az account set --subscription "<název>"
  # Ve verzi azurerm 4.x je subscription_id povinné, pak sem doplňte:
  # subscription_id = "<ID předplatného z: az account show --query id -o tsv>"
}

# Náhodná přípona, aby si účastníci ve stejném předplatném nepřepsali resource group
resource "random_integer" "suffix" {
  min = 1000
  max = 9999
}

# Jednoduchá ukázková resource group
resource "azurerm_resource_group" "demo" {
  name     = "rg-terraform-demo-${random_integer.suffix.result}"
  location = "westeurope"
}

output "resource_group_name" {
  value = azurerm_resource_group.demo.name
}
