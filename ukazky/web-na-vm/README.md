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

Postup včetně otevření portů v NSG: [postupy/07-webova-sluzba-na-vm.md](../../postupy/07-webova-sluzba-na-vm.md).

Odebrání: `sudo apt-get remove -y nginx && sudo rm -rf /var/www/acmesoft-demo /etc/nginx/ssl/acmesoft-demo.*`
