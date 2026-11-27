# Webová služba na VM (nginx, HTTP a HTTPS)

Falešný e-shop Acmesoft pro ukázky sítí. `setup.sh` nainstaluje nginx, vytvoří self-signed certifikát a nasadí
stránku, která ukazuje protokol (http nebo https), IP návštěvníka, jméno a privátní IP serveru.

```
sudo bash setup.sh
```

| Adresa | Co vrátí |
|---|---|
| `/` | Stránka e-shopu se spojením |
| `/health` | `OK` (pro sondy load balanceru a monitoring) |
| `/api/status` | JSON se jménem serveru, protokolem a IP klienta |

## Počítadlo útoků

Nahoře na stránce je karta „Kdo se sem od spuštění dobývá“. `attack_stats.py` každých 30 s (systemd timer
`acmesoft-stats.timer`) projde log SSH a access log nginx a zapíše `/stats.json`: pokusy o SSH přihlášení,
zkoušená jména, podezřelé HTTP požadavky podle typu (WordPress, `.env`, admin panely, spouštění příkazů)
a posledních 15 pokusů. IP adresy na stránce jsou bez posledního čísla.

```
sudo python3 /opt/acmesoft-demo/attack_stats.py --vse   # souhrn za celou historii logů
sudo rm /var/lib/acmesoft-demo/start                     # počítat znovu od teď
```

Postup včetně otevření portů v NSG: [postupy/07-webova-sluzba-na-vm.md](../../postupy/07-webova-sluzba-na-vm.md).

Odebrání:

```
sudo systemctl disable --now acmesoft-stats.timer
sudo rm -f /etc/systemd/system/acmesoft-stats.* && sudo rm -rf /opt/acmesoft-demo /var/lib/acmesoft-demo
sudo apt-get remove -y nginx && sudo rm -rf /var/www/acmesoft-demo /etc/nginx/ssl/acmesoft-demo.*
```
