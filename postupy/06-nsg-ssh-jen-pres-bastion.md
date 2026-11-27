# NSG: SSH na VM jen přes Azure Bastion, ne z internetu

**Cíl:** VM má veřejnou IP (kvůli odchozímu přístupu), ale port 22 z internetu je zavřený. Přihlásit se jde jen přes
Azure Bastion v portálu.

**Výchozí stav:** VM vytvořená průvodcem s „Allow selected ports: SSH (22)“. Na síťovém rozhraní je NSG
`<vm>-nsg` s pravidlem **300 SSH** (Allow, zdroj Any, port 22). Ve virtuální síti je Bastion **Developer**
(VM > Connect > Bastion ho založí sám, zdarma, bez vlastního subnetu).

## 1. Ukázat, že SSH z internetu jde

Z notebooku nebo z Cloud Shellu:

```
timeout 5 bash -c '</dev/tcp/<veřejná-IP-VM>/22' && echo OTEVRENO || echo ZAVRENO
```

## 2. Povolit SSH od Bastionu

1. VM `<vm>` > **Networking > Network settings** > **+ Create port rule** > **Inbound port rule**.
2. Nastavit:
   - Source: **IP Addresses**, Source IP addresses: `168.63.129.16`
   - Source port ranges: `*`
   - Destination: **Any**
   - Service: **SSH** (Protocol TCP, port 22)
   - Action: **Allow**
   - Priority: `100`
   - Name: `Allow-SSH-Bastion`
3. **Add**.

### Odkud se Bastion připojuje

- **Bastion Developer** nemá vlastní IP adresu ani subnet, v portálu ji nenajdete. Je to sdílená služba a k VM se
  připojuje z **168.63.129.16**. To je pevná virtuální adresa platformy Azure, stejná ve všech regionech
  a předplatných (přes ni VM dostává i DNS, DHCP a komunikaci s agentem VM).
- **Bastion Basic nebo Standard** má vlastní subnet `AzureBastionSubnet` a spojení chodí z jeho rozsahu:
  virtuální síť > **Subnets** > `AzureBastionSubnet` > Address range. Ten rozsah zadejte jako zdroj pravidla
  (nebo Service Tag **VirtualNetwork**).
- Ověření na VM: připojit se přes Bastion a spustit `echo $SSH_CLIENT`. První údaj je adresa, odkud spojení přišlo.

## 3. Zakázat SSH z internetu

1. **+ Create port rule** > **Inbound port rule**:
   - Source: **Service Tag**, Source service tag: **Internet**
   - Service: **SSH**
   - Action: **Deny**
   - Priority: `200`
   - Name: `Deny-SSH-Internet`
2. **Add**.
3. Původní pravidlo **300 SSH** (Allow z Any): tři tečky na řádku > **Delete**. Po pravidle 200 už stejně
   nemá vliv, ale mrtvá pravidla v NSG matou.

Pravidla se vyhodnocují od nejnižšího čísla priority; první, které sedí, rozhoduje.

## 4. Ověřit

- Z internetu: příkaz z kroku 1 vypíše `ZAVRENO`.
- Rozbor jednoho spojení: **Network Watcher > IP flow verify**: VM `<vm>`, Inbound, TCP, local port 22, remote IP
  např. `8.8.8.8`, remote port `50000` > výsledek **Deny**, pravidlo `Deny-SSH-Internet`.
  (Adresu 168.63.129.16 IP flow verify neotestuje, je vyhrazená.)
- Přehled všech pravidel včetně výchozích: VM > Networking > **Effective security rules**.
- Přes Bastion: VM > **Connect > Connect via Bastion** > uživatel a klíč nebo heslo > **Connect**. Terminál se
  otevře v prohlížeči. V něm `echo $SSH_CLIENT` ukáže adresu Bastionu.

Už otevřené SSH spojení z notebooku se změnou pravidel nemusí hned spadnout, nové se ale nenaváže.

## Vrácení do výchozího stavu

Smazat `Allow-SSH-Bastion` a `Deny-SSH-Internet` a znovu přidat pravidlo **SSH**: Source Any, Service SSH, Allow,
priorita 300.
