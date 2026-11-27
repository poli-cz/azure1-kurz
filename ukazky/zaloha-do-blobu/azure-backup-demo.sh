#!/usr/bin/env bash
# Ukázková záloha složky do Azure Blob Storage (kurz AZURE1).
#
# Použití:
#   ./azure-backup-demo.sh            zálohuje malou ukázkovou složku, kterou si sám vytvoří
#   ./azure-backup-demo.sh ~/projekt  zálohuje zadanou složku
#
# Potřebuje Azure CLI (az). Klíč najdeš v portálu: Storage account > Security + networking > Access keys.
set -euo pipefail

STORAGE_ACCOUNT="mujstorageucet"   # název vašeho storage accountu
CONTAINER="testcontainer"
# Klíč doplň sem, nebo ho předej proměnnou: AZURE_STORAGE_KEY=... ./azure-backup-demo.sh
ACCOUNT_KEY="${AZURE_STORAGE_KEY:-DOPLN_KLIC}"

if [ "$ACCOUNT_KEY" = "DOPLN_KLIC" ]; then
  echo "Chybí klíč: doplň ACCOUNT_KEY ve skriptu, nebo nastav AZURE_STORAGE_KEY." >&2
  exit 1
fi
command -v az >/dev/null || { echo "Chybí Azure CLI (az)." >&2; exit 1; }

# az storage si účet a klíč přečte z těchto proměnných, klíč tak není vidět v seznamu procesů.
export AZURE_STORAGE_ACCOUNT="$STORAGE_ACCOUNT"
export AZURE_STORAGE_KEY="$ACCOUNT_KEY"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

SOURCE_DIR="${1:-}"
if [ -z "$SOURCE_DIR" ]; then
  SOURCE_DIR="$WORK_DIR/demo-data"
  mkdir -p "$SOURCE_DIR"
  echo "Ukázková záloha ze stroje $(hostname)" > "$SOURCE_DIR/readme.txt"
  date > "$SOURCE_DIR/cas-zalohy.txt"
  { uname -a; echo; df -h /; } > "$SOURCE_DIR/system.txt"
fi
[ -d "$SOURCE_DIR" ] || { echo "Složka $SOURCE_DIR neexistuje." >&2; exit 1; }
SOURCE_DIR="$(cd "$SOURCE_DIR" && pwd)"

STAMP="$(date +%Y%m%d-%H%M%S)"
ARCHIVE_NAME="$(basename "$SOURCE_DIR")-$STAMP.tar.gz"
ARCHIVE="$WORK_DIR/$ARCHIVE_NAME"
BLOB_NAME="backups/$(hostname -s)/$ARCHIVE_NAME"

echo "Balím $SOURCE_DIR do $ARCHIVE_NAME"
tar -czf "$ARCHIVE" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"

echo "Nahrávám do $STORAGE_ACCOUNT/$CONTAINER/$BLOB_NAME"
az storage blob upload \
  --container-name "$CONTAINER" \
  --file "$ARCHIVE" \
  --name "$BLOB_NAME" \
  --only-show-errors -o none

echo
echo "Zálohy v kontejneru $CONTAINER:"
az storage blob list \
  --container-name "$CONTAINER" \
  --prefix "backups/" \
  --query "[].{Soubor:name, Bajty:properties.contentLength, Zmeneno:properties.lastModified}" \
  --only-show-errors -o table

echo
echo "Obnova téhle zálohy:"
echo "  az storage blob download --account-name $STORAGE_ACCOUNT --container-name $CONTAINER \\"
echo "    --name \"$BLOB_NAME\" --file obnova.tar.gz --account-key <klíč> && tar -xzf obnova.tar.gz"
