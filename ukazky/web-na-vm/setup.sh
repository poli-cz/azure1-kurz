#!/usr/bin/env bash
# Ukázková webová služba na Linux VM (Ubuntu): nginx na portu 80 (HTTP) a 443 (HTTPS, self-signed certifikát).
# Falešný e-shop Acmesoft: stránka ukáže server, protokol a IP návštěvníka, /health a /api/status pro testy.
#
# Použití:  sudo bash setup.sh
set -euo pipefail

[ "$(id -u)" = 0 ] || { echo "Spusťte přes sudo: sudo bash setup.sh" >&2; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
IMDS="http://169.254.169.254/metadata/instance"
meta() { curl -s -m 3 -H Metadata:true "$IMDS/$1?api-version=2021-02-01&format=text" || true; }

echo "Instaluji nginx a openssl ..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx openssl >/dev/null

VM_NAME="$(meta compute/name)";         VM_NAME="${VM_NAME:-$(hostname)}"
REGION="$(meta compute/location)";       REGION="${REGION:-neznámý}"
PRIVATE_IP="$(meta network/interface/0/ipv4/ipAddress/0/privateIpAddress)"
PRIVATE_IP="${PRIVATE_IP:-$(hostname -I | awk '{print $1}')}"
PUBLIC_IP="$(meta network/interface/0/ipv4/ipAddress/0/publicIpAddress)"

echo "Vytvářím self-signed certifikát ..."
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -newkey rsa:2048 -days 30 \
  -keyout /etc/nginx/ssl/acmesoft-demo.key -out /etc/nginx/ssl/acmesoft-demo.crt \
  -subj "/O=Acmesoft demo/CN=${PUBLIC_IP:-acmesoft-demo}" >/dev/null 2>&1
chmod 600 /etc/nginx/ssl/acmesoft-demo.key

echo "Nasazuji stránku ..."
mkdir -p /var/www/acmesoft-demo
sed -e "s|{{VM_NAME}}|$VM_NAME|g" -e "s|{{REGION}}|$REGION|g" -e "s|{{PRIVATE_IP}}|$PRIVATE_IP|g" \
  "$HERE/index.html" > /var/www/acmesoft-demo/index.html
cp "$HERE/nginx-acmesoft-demo.conf" /etc/nginx/sites-available/acmesoft-demo
ln -sf /etc/nginx/sites-available/acmesoft-demo /etc/nginx/sites-enabled/acmesoft-demo
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl enable nginx >/dev/null 2>&1
systemctl restart nginx

echo "Zapínám počítadlo pokusů o útok (každých 30 s) ..."
mkdir -p /opt/acmesoft-demo
cp "$HERE/attack_stats.py" /opt/acmesoft-demo/attack_stats.py
cp "$HERE/acmesoft-stats.service" "$HERE/acmesoft-stats.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now acmesoft-stats.timer >/dev/null 2>&1
python3 /opt/acmesoft-demo/attack_stats.py

echo
echo "Hotovo. Na VM:  curl -s http://localhost/health   curl -sk https://localhost/api/status"
if [ -n "$PUBLIC_IP" ]; then
  echo "V prohlížeči:   http://$PUBLIC_IP   a   https://$PUBLIC_IP"
else
  echo "V prohlížeči:   http://<veřejná IP VM>  a  https://<veřejná IP VM>  (IP najdete v portálu, VM > Overview)"
fi
echo "Z internetu to půjde až po povolení portů 80 a 443 v NSG."
