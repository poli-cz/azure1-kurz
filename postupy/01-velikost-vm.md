# Virtuální počítač nejde vytvořit: jakou velikost a nastavení zvolit

**Příznak:** průvodce VM skončí na validaci, často s `NotAvailableForSubscription` nebo
„The requested size is not available“, i když kvóta je volná.

**Příčina:** nová předplatná (zvlášť kreditová a zkušební) mají řadu starších velikostí zablokovanou (B1s, B2s,
B1ms, D2s_v3 ...) a u novějších často jen některé zóny dostupnosti. Kvóta v portálu to neukáže.

## Co vybrat v průvodci (osvědčené 11/2026, West Europe)

1. **Basics > Region:** West Europe.
2. **Availability options:** **No infrastructure redundancy required** (ne Availability zone; průvodce předvyplní
   Zone 1, která bývá zablokovaná).
3. **Size:** **Standard_B2s_v2** (2 vCPU, 8 GiB). Záloha: **Standard_D2ds_v7**.
4. Image: Ubuntu Server 24.04 LTS.
5. **Networking:** nechat **Public IP** (nová), jinak VM nemá přístup do internetu a nejde `apt install`.

## Jak to ověřit předem

Cloud Shell (Bash), velikosti bez omezení v regionu:

```
SUB=$(az account show --query id -o tsv)
az rest --method get \
  --url "https://management.azure.com/subscriptions/$SUB/providers/Microsoft.Compute/skus?api-version=2021-07-01&\$filter=location eq 'westeurope'" \
  --query "value[?resourceType=='virtualMachines' && starts_with(name,'Standard_B2')].[name, join(',', restrictions[].reasonCode)]" -o tsv
```

Prázdný druhý sloupec znamená bez omezení. Kvóta rodiny: Subscriptions > předplatné > **Usage + quotas**
(např. „Standard Bsv2 Family vCPUs“). Nulovou kvótu jde zvýšit tamtéž, u malých hodnot to bývá schválené hned.
