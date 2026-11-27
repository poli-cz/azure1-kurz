# AZURE1: Microsoft Azure, základy platformy v praxi

Materiály ke kurzu: zadání labů, postupy krok za krokem a ukázkový kód. Názvy zdrojů v postupech jsou příklady,
nahraďte je svými.

```
git clone https://github.com/poli-cz/azure1-kurz.git
```

## Laby

| | |
|---|---|
| [Lab, část 1](labs/lab1.md) | Struktura Azure, RBAC, výběr compute, Container Apps, síťový pohled |
| [Lab, část 2](labs/lab2.md) | Virtual Network, PostgreSQL jako služba, veřejné a privátní části, tajemství, náklady |

## Postupy krok za krokem

| | |
|---|---|
| [01 Velikost VM](postupy/01-velikost-vm.md) | Co vybrat, když průvodce VM skončí na validaci |
| [02 VM a PostgreSQL v privátní síti](postupy/02-vm-a-postgres-v-privatni-siti.md) | Peering, privátní DNS, `psql` z VM |
| [03 PostgreSQL přes Entra ID](postupy/03-postgres-pres-entra-id.md) | Přihlášení do databáze identitou VM místo hesla |
| [04 Key Vault](postupy/04-key-vault.md) | Aplikace si bere token z trezoru, v konfiguraci žádné tajemství |
| [05 Terraform z VM](postupy/05-terraform-na-vm.md) | `init`, `plan`, `apply`, `destroy` |
| [06 NSG: SSH jen přes Bastion](postupy/06-nsg-ssh-jen-pres-bastion.md) | Zavřít port 22 z internetu, nechat přístup přes Azure Bastion |
| [07 Webová služba na VM](postupy/07-webova-sluzba-na-vm.md) | nginx na HTTP a HTTPS, porty 80 a 443 v NSG, ukázka v prohlížeči |
| [08 WAF před webem](postupy/08-waf-pred-webem.md) | Application Gateway s WAF, Detection a Prevention, blokování SQL injection a XSS |
| [Instalace nástrojů](postupy/instalace-nastroju.md) | Azure CLI, `psql`, Terraform, `jq` na Ubuntu |

## Ukázky

| | |
|---|---|
| [keyvault-app](ukazky/keyvault-app) | Konfigurace s odkazem do Key Vaultu, načtení přes managed identitu (jen standardní knihovna) |
| [web-na-vm](ukazky/web-na-vm) | Falešný e-shop na nginx (HTTP a HTTPS) pro ukázky sítí |
| [terraform](ukazky/terraform) | Resource group z kódu |
| [app-service-python](ukazky/app-service-python) | Webová aplikace pro App Service, nasazení zipem |
| [function-hello](ukazky/function-hello) | Azure Function s HTTP triggerem |
| [function-least-privilege](ukazky/function-least-privilege) | Function čte Blob Storage přes user-assigned identitu a RBAC |
| [vm-blob](ukazky/vm-blob) | Výpis Blob kontejneru z VM přes identitu |
| [zaloha-do-blobu](ukazky/zaloha-do-blobu) | Záloha složky do Blob Storage a obnova |

Lektor: Jan Polišenský
