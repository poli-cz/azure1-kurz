# PostgreSQL přes Microsoft Entra ID: VM se do databáze přihlásí identitou, ne heslem

**Cíl:** aplikace na VM se připojí do Azure Database for PostgreSQL (Flexible Server) tokenem své managed identity.
Heslo nikde uložené není.

**Výchozí stav:** VM a Postgres se vidí po síti (stejná VNet nebo peering, viz
[02-vm-a-postgres-v-privatni-siti.md](02-vm-a-postgres-v-privatni-siti.md)), na VM je `psql`. V Postgresu je
přihlášení jen heslem (PostgreSQL authentication only).

| V postupu | Příklad |
|---|---|
| `<vm>` | `vm-acmesoft-dev` (jméno VM = jméno její identity) |
| `<server>` | `psql-acmesoft-dev` |

## 1. Zapnout identitu VM

1. VM `<vm>` > **Security > Identity** > záložka **System assigned**.
2. **Status: On** > **Save** > **Yes**. Pokud je už On, nic neměňte.

## 2. Zapnout Entra ID v Postgresu a nastavit admina

1. Postgres `<server>` > **Security > Authentication**.
2. Authentication method: **PostgreSQL and Microsoft Entra authentication** (heslo funguje dál).
3. **+ Add Microsoft Entra administrators** > vyhledat `<vm>` > označit > **Select**.
   Pokud se VM v hledání neukáže, hledat podle Object (principal) ID z kroku 1.
4. **Save**. Uložení trvá 2 až 3 minuty.
5. Po uložení obnovit stránku a zkontrolovat, že `<vm>` je v seznamu **Microsoft Entra administrators**. Pokud tam
   není (admin přidaný během ukládání změny metody se neuloží), přidat ho znovu a znovu **Save**.

Pro ukázku je adminem přímo identita VM. V produkci je adminem skupina lidí a aplikace dostane vlastní roli
s menšími právy (funkce `pgaadauth_create_principal`).

## 3. Připojit se z VM bez hesla

```
export PGPASSWORD=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fossrdbms-aad.database.windows.net" | jq -r .access_token)
psql "host=<server>.postgres.database.azure.com dbname=postgres user=<vm> sslmode=require"
```

```
select current_user;
```

- Token si VM vyzvedne z lokální adresy 169.254.169.254 (Instance Metadata Service), platí asi hodinu.
- Jméno uživatele musí přesně odpovídat jménu identity, včetně velkých písmen.
- Chybí `jq`: `sudo apt-get install -y jq`.
- Špatný nebo prošlý token: `The access token has invalid format`.

## Úklid

1. Postgres > **Security > Authentication** > u `<vm>` ikona koše (odebrat admina).
2. Authentication method: **PostgreSQL authentication only** > **Save**.

Po odebrání admina se identita VM do databáze nepřihlásí a role v databázi nezůstane.
