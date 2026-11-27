# Key Vault: aplikace na VM si bere token z trezoru přes managed identitu

**Cíl:** v konfiguraci aplikace není žádný token. Aplikace na VM se do Key Vaultu přihlásí identitou virtuálky
a falešný bezpečnostní token si načte za běhu.

**Výchozí stav:** běžící Linux VM s veřejnou IP (odchozí přístup do internetu), přihlášení přes SSH.

Ve všech krocích nahraďte názvy svými:

| V postupu | Příklad |
|---|---|
| `<vm>` | `vm-acmesoft-dev` |
| `<trezor>` | `kv-acmesoft-jp` (3 až 24 znaků, písmena, číslice a pomlčky, unikátní v celém Azure) |
| `<rg>` | resource group, ve které je VM |

## 1. Zapnout identitu VM

1. Virtuální počítač `<vm>` > **Security > Identity** > záložka **System assigned**.
2. **Status: On** > **Save** > **Yes**.
3. Zobrazí se **Object (principal) ID**. VM má teď vlastní identitu v Microsoft Entra ID.

Pokud je už **On**, nic neměňte.

## 2. Založit Key Vault

1. Vyhledávání nahoře: **Key vaults** > **+ Create**.
2. Záložka **Basics**:
   - Subscription a Resource group: `<rg>`
   - Key vault name: `<trezor>`
   - Region: stejný jako VM (např. West Europe)
   - Pricing tier: **Standard**
   - Purge protection: **Disable purge protection** (u ukázky jde trezor po smazání hned vyčistit)
3. Záložka **Access configuration**: Permission model **Azure role-based access control (recommended)**.
4. Záložka **Networking**: nechat **Enable public access** a **All networks**.
5. **Review + create** > **Create**. Trvá to asi minutu.

## 3. Dát sobě právo spravovat tajemství

Role Owner na předplatném **nestačí**: s modelem RBAC je čtení a zápis tajemství samostatné oprávnění. Bez tohoto
kroku hlásí Key Vault u tajemství „The operation is not allowed by RBAC“.

1. Trezor `<trezor>` > **Access control (IAM)** > **+ Add** > **Add role assignment**.
2. Role: vyhledat **Key Vault Secrets Officer** > označit > **Next**.
3. Assign access to: **User, group, or service principal** > **+ Select members** > vybrat sebe > **Select**.
4. **Review + assign** (dvakrát).

## 4. Uložit falešný token

Přiřazení role z kroku 3 se propisuje asi minutu. Do té doby hlásí Secrets „not authorized“, stačí chvíli počkat
a stránku obnovit.

1. Trezor > **Objects > Secrets** > **+ Generate/Import**.
2. Upload options: **Manual**
   - Name: `api-token`
   - Secret value: např. `fake-token-acmesoft-1234`
3. **Create**.

## 5. Stáhnout aplikaci na VM a nastavit konfiguraci

Na VM přes SSH:

```
git clone https://github.com/poli-cz/azure1-kurz.git
cd azure1-kurz/ukazky/keyvault-app
nano config.ini        # vault_name = <trezor>
cat config.ini         # ukázat: token tu není, jen kv:api-token
python3 app.py
```

Teď aplikace skončí chybou **403**: VM se do trezoru přihlásila, ale nemá právo tajemství číst. To je správně,
identita sama o sobě nic nesmí.

## 6. Dát identitě VM právo číst tajemství

1. Trezor `<trezor>` > **Access control (IAM)** > **+ Add** > **Add role assignment**.
2. Role: **Key Vault Secrets User** (jen čtení hodnot tajemství) > **Next**.
3. Assign access to: **Managed identity** > **+ Select members**.
4. Managed identity: **Virtual machine** > vybrat `<vm>` > **Select**.
5. **Review + assign** (dvakrát).

## 7. Ověřit

Po 1 až 5 minutách (než se přiřazení role propíše) znovu na VM:

```
python3 app.py
python3 app.py --ukaz    # celá hodnota, jen u falešného tokenu
```

Výstup:

```
Přihlášení do Key Vaultu: managed identita VM (heslo ani klíč v konfiguraci nejsou)

Konfigurace aplikace Acmesoft Demo
------------------------------------------------------------------------
app.name               Acmesoft Demo                  z config.ini
app.environment        dev                            z config.ini
keyvault.vault_name    kv-acmesoft-jp                 z config.ini
secrets.api_token      fake****************1234       z Key Vaultu (kv-acmesoft-jp / api-token)
------------------------------------------------------------------------
```

**Co ukázat navíc:** v trezoru změnit hodnotu tajemství (Secrets > `api-token` > **+ New Version**) a spustit
aplikaci znovu. Načte novou hodnotu bez úpravy konfigurace i kódu, takže rotace tajemství nevyžaduje nasazení.

## Úklid

1. Resource group `<rg>` nebo trezor: Key vaults > `<trezor>` > **Delete**.
2. Smazaný trezor se 90 dní drží v koši a název je obsazený: Key vaults > **Manage deleted vaults** > vybrat >
   **Purge**.
3. Přiřazení rolí na trezoru zmizí s ním.
