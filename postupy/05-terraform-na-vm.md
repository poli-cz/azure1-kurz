# Terraform z VM: první infrastruktura jako kód

**Cíl:** z Linux VM vytvořit Terraformem resource group v Azure, ukázat `plan`, `apply`, stavový soubor
a `destroy`.

**Výchozí stav:** Ubuntu VM s přístupem do internetu, přihlášení přes SSH.

## 1. Nainstalovat Azure CLI a Terraform

Příkazy jsou v [instalace-nastroju.md](instalace-nastroju.md) (sekce Azure CLI a Terraform). Ověření:

```
az version
terraform version
```

## 2. Stáhnout ukázku

```
git clone https://github.com/poli-cz/azure1-kurz.git
cd azure1-kurz/ukazky/terraform
cat main.tf
```

## 3. Přihlásit se a vybrat předplatné

```
az login --use-device-code             # kód zadat na https://microsoft.com/devicelogin
az account set --subscription "<název předplatného>"
az account show --query name -o tsv    # ověřit, kam se bude nasazovat
```

## 4. Plan, apply, destroy

```
terraform init        # stáhne provider azurerm
terraform plan        # co se změní, nic nevytváří
terraform apply       # potvrdit: yes
ls                    # terraform.tfstate = co Terraform spravuje
terraform destroy     # potvrdit: yes
```

- První `plan` může trvat jednu až několik minut: azurerm 3.x při prvním běhu v předplatném registruje resource
  providery. Když visí přes 5 minut, Ctrl+C a do bloku `provider "azurerm"` přidat
  `skip_provider_registration = true`.
- Název resource group má náhodnou příponu (`rg-terraform-demo-1234`), takže si účastníci ve sdíleném předplatném
  nepřepíšou skupinu navzájem.
