# Webová služba na VM: HTTP a HTTPS z prohlížeče

**Cíl:** na Linux VM spustit malou webovou službu (nginx), otevřít pro ni porty 80 a 443 v NSG a ukázat ji
v prohlížeči. SSH přitom zůstává zavřené (viz [06-nsg-ssh-jen-pres-bastion.md](06-nsg-ssh-jen-pres-bastion.md)).

**Výchozí stav:** Ubuntu VM s veřejnou IP, přihlášení přes Bastion nebo SSH.

## 1. Spustit službu na VM

```
git clone https://github.com/poli-cz/azure1-kurz.git     # kdo už repo má: cd azure1-kurz && git pull
cd azure1-kurz/ukazky/web-na-vm
sudo bash setup.sh
curl -s http://localhost/health          # OK
curl -sk https://localhost/api/status    # JSON, -k = nekontrolovat certifikát
```

## 2. Ukázat, že z internetu to zatím nejde

V prohlížeči otevřít `http://<veřejná IP VM>` (IP: VM > **Overview > Public IP address**). Stránka se nenačte:
služba běží, ale NSG příchozí provoz na port 80 nepustí (výchozí pravidlo DenyAllInBound).

## 3. Otevřít porty 80 a 443 v NSG

1. VM > **Networking > Network settings** > **+ Create port rule** > **Inbound port rule**.
2. Nastavit:
   - Source: **Any** (nebo **My IP address**, pokud má stránku vidět jen lektor)
   - Source port ranges: `*`
   - Destination: **Any**
   - Service: **Custom**, Destination port ranges: `80,443`, Protocol: **TCP**
   - Action: **Allow**
   - Priority: `300`
   - Name: `Allow-HTTP-HTTPS`
3. **Add**. Pravidlo platí do několika sekund.

## 4. Ukázat v prohlížeči

- `http://<veřejná IP VM>`: stránka Acmesoft Shop, protokol **http**, vaše veřejná IP.
- `https://<veřejná IP VM>`: prohlížeč varuje „Vaše připojení není soukromé“. Certifikát je self-signed,
  nepodepsala ho důvěryhodná autorita. **Pokročilé > Pokračovat** a stránka ukáže protokol **https**.
- `/api/status` a `/health`: odpovědi pro aplikace a sondy (load balancer, monitoring).

**K diskuzi:** proč prohlížeč varuje (v praxi certifikát od autority, např. Let's Encrypt nebo App Service
Managed Certificate), proč v praxi přesměrovat HTTP (80) na HTTPS (443), a že **Effective security rules** u VM ukáže
všechna pravidla, která na provoz působí, včetně výchozích.

## 5. Volitelně: zavřít HTTP, nechat jen HTTPS

Pravidlo `Allow-HTTP-HTTPS` > Destination port ranges jen `443` > **Save**. `http://` přestane odpovídat,
`https://` jde dál.

## Úklid

1. NSG: smazat `Allow-HTTP-HTTPS`.
2. Na VM: `sudo apt-get remove -y nginx && sudo rm -rf /var/www/acmesoft-demo /etc/nginx/ssl/acmesoft-demo.*`
