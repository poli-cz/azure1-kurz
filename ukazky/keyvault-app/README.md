# Key Vault + managed identita: aplikace bez tajemství v konfiguraci

Malá aplikace v Pythonu (jen standardní knihovna, žádný `pip install`). V `config.ini` je místo tokenu jen odkaz
`kv:api-token`. Aplikace si při startu vyžádá token identity virtuálky, načte tajemství z Azure Key Vault a vypíše
konfiguraci.

```
python3 app.py          # tajemství zamaskované: fake************1234
python3 app.py --ukaz   # tajemství celé (jen pro ukázku s falešným tokenem)
```

Mimo Azure (notebook, Cloud Shell) použije místo identity VM přihlášení z `az login`.

Postup krok za krokem: [postupy/04-key-vault.md](../../postupy/04-key-vault.md).

## Co aplikace dělá

1. Přečte `config.ini`. Hodnoty začínající `kv:` jsou odkazy do Key Vaultu.
2. Zavolá lokální adresu `http://169.254.169.254/metadata/identity/oauth2/token` (Instance Metadata Service). Azure
   vrátí token identity VM pro `https://vault.azure.net`. Žádné heslo ani klíč se nikde nezadává.
3. S tokenem zavolá `https://<trezor>.vault.azure.net/secrets/<název>`. Key Vault zkontroluje roli identity
   (Key Vault Secrets User) a vrátí hodnotu.

## Chyby, které uvidíte

| Hláška | Co chybí |
|---|---|
| `doplň [keyvault] vault_name` | Název trezoru v `config.ini` |
| `VM nemá zapnutou managed identitu` | VM > Security > Identity > System assigned > On |
| `Key Vault vrátil 403` | Role Key Vault Secrets User pro identitu VM (po přiřazení 1 až 5 minut počkat) |
| `Key Vault vrátil 404` | Tajemství s tímto názvem v trezoru není |
| `Trezor ... není dostupný` | Překlep v názvu trezoru, nebo trezor nepouští veřejný přístup |
