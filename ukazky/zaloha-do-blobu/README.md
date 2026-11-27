# Záloha složky do Blob Storage

`azure-backup-demo.sh` zabalí složku do `tar.gz`, nahraje ji do kontejneru jako
`backups/<hostname>/<složka>-<čas>.tar.gz`, vypíše zálohy a příkaz na obnovu.

1. Ve skriptu nastavit `STORAGE_ACCOUNT` a `CONTAINER` (kontejner musí existovat).
2. Klíč: Storage account > **Security + networking > Access keys** > Show > zkopírovat key1.
3. Spustit, klíč předat proměnnou (ne do souboru, ať se nedostane do gitu):

```
AZURE_STORAGE_KEY='<klíč>' ./azure-backup-demo.sh            # záloha ukázkové složky
AZURE_STORAGE_KEY='<klíč>' ./azure-backup-demo.sh ~/projekt  # záloha vlastní složky
```

Potřebuje Azure CLI. Bezpečnější varianta bez klíče: managed identita a role Storage Blob Data Contributor
(viz [../vm-blob](../vm-blob) a [postupy/04-key-vault.md](../../postupy/04-key-vault.md)).
