# WAF před webem: Application Gateway s Web Application Firewall

**Cíl:** před webovou službu na VM ([07-webova-sluzba-na-vm.md](07-webova-sluzba-na-vm.md)) předřadit Azure
Application Gateway s WAF. Útoky typu SQL injection nebo XSS zastaví WAF dřív, než dojdou na server, a VM pak
z internetu na portu 80 vůbec nebude vidět.

```
internet ──> Application Gateway + WAF (veřejná IP) ──> VM 172.16.0.4:80 (jen z virtuální sítě)
```

**Výchozí stav:** VM s webem z postupu 07 ve virtuální síti, např. `vnet-acmesoft` 172.16.0.0/16.

**Cena a čas:** WAF V2 se platí za každou hodinu běhu (pevná částka plus kapacitní jednotky, ověřte v ceníku
Application Gateway). Založení trvá několik minut až čtvrt hodiny. Po ukázce gateway smažte.

## 1. Subnet pro gateway

Application Gateway potřebuje **vlastní subnet**, ve kterém nesmí být nic jiného. Microsoft doporučuje /24.

1. Virtual networks > síť VM > **Settings > Subnets** > **+ Subnet**.
2. Name: `snet-appgw`, Starting address: volný rozsah, např. `172.16.2.0`, Size: **/24** > **Add**.

## 2. Založit Application Gateway s WAF

Vyhledávání: **Application gateways** > **+ Create**.

**Basics**
- Resource group: stejná jako VM, Application gateway name: `agw-acmesoft`
- Region: stejný jako VM
- Tier: **WAF V2**
- Autoscaling: **Yes**, Minimum instance count `0`, Maximum `2` (levnější na ukázku)
- WAF Policy: **Create new** > Name `waf-acmesoft` > **OK**
- Virtual network: síť VM, Subnet: `snet-appgw`

**Frontends**
- Frontend IP address type: **Public**
- Public IP address: **Add new** > `pip-agw-acmesoft` > **OK**

**Backends**
- **Add a backend pool** > Name `pool-vm`, Add backend pool without targets: **No**
- Target type: **IP address or FQDN**, Target: privátní IP VM, např. `172.16.0.4` > **Add**

**Configuration**
- **Add a routing rule** > Rule name `rule-http`, Priority `100`
- Záložka **Listener**: Listener name `listener-http`, Frontend IP **Public IPv4**, Protocol **HTTP**, Port **80**
- Záložka **Backend targets**: Backend target `pool-vm`, Backend settings **Add new** > Name `http-80`,
  Backend protocol **HTTP**, Backend port **80**, ostatní výchozí > **Add**
- **Add**

**Review + create** > **Create**. Než doběhne, vysvětlete architekturu a OWASP Top 10.

## 3. Ověřit, že web jde přes gateway

1. Application gateway > **Overview** > **Frontend public IP address**.
2. Prohlížeč: `http://<IP gateway>` ukáže stránku Acmesoft Shop.
3. Application gateway > **Monitoring > Backend health**: backend `172.16.0.4` je **Healthy**.

Na stránce je teď jako „Vaše IP adresa“ privátní IP gateway (172.16.2.x), ne IP návštěvníka. Server vidí jen
gateway, původní adresu posílá gateway v hlavičce `X-Forwarded-For`.

## 4. Útoky: nejdřív Detection, pak Prevention

Nová WAF politika je ve výchozím stavu v režimu **Detection**: útok jen zaloguje a pustí dál.

Z notebooku nebo Cloud Shellu (`<GW>` = IP gateway):

```
curl -s -o /dev/null -w "%{http_code}\n" "http://<GW>/"                                         # běžný požadavek
curl -s -o /dev/null -w "%{http_code}\n" "http://<GW>/?id=1%27%20OR%20%271%27=%271"            # SQL injection
curl -s -o /dev/null -w "%{http_code}\n" "http://<GW>/?q=%3Cscript%3Ealert(1)%3C/script%3E"     # XSS
curl -s -o /dev/null -w "%{http_code}\n" "http://<GW>/?file=../../../../etc/passwd"            # path traversal
```

V režimu Detection vrátí všechny `200`.

Přepnout na blokování: **Web Application Firewall policies** > `waf-acmesoft` > **Settings > Policy settings** >
Mode **Prevention** > **Save** (nebo na Overview tlačítko pro přepnutí do Prevention). Po minutě znovu stejné
příkazy: běžný požadavek `200`, útoky `403 Forbidden`. V prohlížeči se ukáže stránka 403 od Application Gateway.

Pro srovnání stejný SQL injection přímo na veřejnou IP VM: `200`, nginx útok nepozná.

## 5. Zavřít přímý přístup na VM

Web má být dostupný jen přes WAF.

1. VM > **Networking > Network settings**: smazat pravidla, která pouštějí port 80 a 443 z internetu
   (např. `Allow-HTTP-HTTPS`).
2. Gateway se k VM dostane dál: provoz ze subnetu `snet-appgw` pouští výchozí pravidlo **AllowVnetInBound**.
3. `http://<veřejná IP VM>` přestane odpovídat, `http://<IP gateway>` jde dál.

## Volitelně: logy WAF

Application gateway > **Monitoring > Diagnostic settings** > **+ Add diagnostic setting** > zaškrtnout
**Application Gateway Firewall Log** > Send to Log Analytics workspace > **Save**. Za pár minut jsou zablokované
požadavky v Log Analytics (Logs) i s číslem pravidla, které zasáhlo.

## Úklid

1. Smazat Application Gateway `agw-acmesoft`, pak veřejnou IP `pip-agw-acmesoft` a WAF politiku `waf-acmesoft`.
2. Smazat subnet `snet-appgw`.
3. Pokud má web dál běžet napřímo, vrátit do NSG VM pravidlo pro porty 80 a 443.
