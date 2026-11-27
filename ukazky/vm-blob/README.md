# Výpis Blob kontejneru z VM přes managed identitu

`vm_blob.py` vypíše soubory v kontejneru Blob Storage. Nepoužívá klíč ani connection string: na Azure VM se
`DefaultAzureCredential` přihlásí identitou virtuálky.

1. VM > **Security > Identity** > System assigned > **On** > Save.
2. Storage account > **Access control (IAM)** > + Add > Add role assignment > **Storage Blob Data Reader** >
   Assign access to: **Managed identity** > Virtual machine > vybrat VM > Review + assign.
3. Na VM:

```
sudo apt-get install -y python3-venv
python3 -m venv venv && . venv/bin/activate
pip install azure-identity azure-storage-blob
nano vm_blob.py          # storage_account_name, container_name
python3 vm_blob.py
```

Bez role z kroku 2 skončí skript chybou AuthorizationPermissionMismatch.
