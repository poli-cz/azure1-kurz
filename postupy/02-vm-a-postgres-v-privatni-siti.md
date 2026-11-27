# VM a PostgreSQL v privátní síti: připojení bez veřejné IP databáze

**Cíl:** z VM se připojit `psql` do Azure Database for PostgreSQL (Flexible Server) s **Private access**. Databáze
nemá veřejný endpoint, VM ji vidí jen přes virtuální síť.

**Nejjednodušší cesta:** Postgres ve **stejném regionu** jako VM a v jeho průvodci v záložce **Networking** vybrat
**Private access (VNet integration)**, **síť VM** a v ní **samostatný subnet** (Azure ho deleguje jen pro Postgres).
Privátní DNS zóna se pak napojí na síť VM sama a peering není potřeba. Hned na krok 3.

Pokud je Postgres v jiné síti (typicky jiný region, průvodce založil novou VNet), chybí dvě věci: propojení sítí
a DNS. Postup níže.

## 1. Propojit sítě (VNet peering)

1. **Virtual networks** > síť VM > **Settings > Peerings** > **+ Add**.
   (Ne služba „Peerings“ z vyhledávání, ta je pro poskytovatele internetu.)
2. Horní část **Remote virtual network summary**:
   - Peering link name: např. `pg-to-vm`
   - Virtual network: síť Postgresu
3. Dolní část **Local virtual network summary**: Peering link name např. `vm-to-pg`.
4. Volby „Allow ... to access ...“ nechat zapnuté > **Add**.
5. Po chvíli jsou oba směry **Connected**. Průvodce je založí v obou sítích najednou.

Adresní rozsahy obou sítí se nesmí překrývat (např. 172.16.0.0/16 a 10.0.0.0/24 je v pořádku).

## 2. Napojit privátní DNS zónu Postgresu na síť VM

Bez toho VM nepřeloží jméno serveru a připojení selže dřív, než vůbec začne.

1. **Private DNS zones** > `<server>.private.postgres.database.azure.com` > **DNS Management > Virtual Network
   Links** > **+ Add**.
2. Link name: např. `link-vm`, Virtual network: síť VM.
3. **Enable auto registration**: vypnuté > **Create**.

## 3. Ověřit z VM

```
getent hosts <server>.postgres.database.azure.com     # privátní IP, např. 10.0.0.4
timeout 5 bash -c '</dev/tcp/<server>.postgres.database.azure.com/5432' && echo PORT OTEVRENY
psql "host=<server>.postgres.database.azure.com port=5432 dbname=postgres user=<admin> sslmode=require"
```

Instalace `psql`: [instalace-nastroju.md](instalace-nastroju.md).

## Co se pokazí nejčastěji

| Příznak | Příčina |
|---|---|
| `could not translate host name` | DNS zóna není napojená na síť VM (krok 2) |
| `getent` vrátí IP, ale spojení visí | Chybí peering (krok 1), nebo NSG blokuje port 5432 |
| `password authentication failed` | Síť je v pořádku, špatné jméno nebo heslo |
| VM nemá internet a `apt` nejde | Subnet je privátní a VM nemá veřejnou IP ani NAT Gateway |
