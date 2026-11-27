# Instalace nástrojů na Ubuntu VM

Ověřeno na Ubuntu Server 24.04 LTS. VM potřebuje odchozí přístup do internetu (veřejná IP nebo NAT Gateway).

## Azure CLI

```
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az version
```

## Klient PostgreSQL (psql)

Verze z Ubuntu (24.04 má psql 16, k serveru 17 nebo 18 se připojí, jen vypíše varování o verzi):

```
sudo apt-get update && sudo apt-get install -y postgresql-client
psql --version
```

Novější verze z repozitáře PostgreSQL:

```
sudo apt update
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
sudo apt update
sudo apt install -y postgresql-client-17
```

## Terraform

```
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y terraform
terraform version
```

## jq (čtení JSON v shellu)

```
sudo apt-get install -y jq
```
