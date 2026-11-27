#!/usr/bin/env python3
"""Ukázka: aplikace si bere tajemství z Azure Key Vault přes managed identitu.

V config.ini není žádný token ani heslo, jen odkaz na tajemství v Key Vaultu ve tvaru
kv:<název-tajemství>. Aplikace si při startu vyžádá token své identity, Key Vault ověří,
jestli identita smí tajemství číst (role Key Vault Secrets User), a vrátí hodnotu.

Bez externích knihoven, stačí Python 3.8 nebo novější:
    python3 app.py               spustí aplikaci, tajemství ukáže zamaskované
    python3 app.py --ukaz        ukáže tajemství celé (jen pro ukázku s falešným tokenem)
"""
import configparser
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

IMDS_URL = "http://169.254.169.254/metadata/identity/oauth2/token"
KEY_VAULT_RESOURCE = "https://vault.azure.net"
KEY_VAULT_API = "7.4"
PLACEHOLDER = "DOPLN-NAZEV-TREZORU"


class AppError(Exception):
    pass


def token_from_managed_identity():
    """Token z identity virtuálky (IMDS). Funguje jen uvnitř Azure, heslo ani klíč nepotřebuje."""
    params = {"api-version": "2018-02-01", "resource": KEY_VAULT_RESOURCE}
    client_id = os.environ.get("AZURE_CLIENT_ID")  # jen u user-assigned identity
    if client_id:
        params["client_id"] = client_id
    req = urllib.request.Request(IMDS_URL + "?" + urllib.parse.urlencode(params), headers={"Metadata": "true"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.load(resp)["access_token"]
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")
        if "Identity not found" in detail:
            raise AppError("VM nemá zapnutou managed identitu (VM > Security > Identity > System assigned > On).")
        raise AppError("IMDS vrátil chybu %s: %s" % (err.code, detail[:200]))


def token_from_azure_cli():
    """Záloha mimo Azure: token přihlášeného uživatele z Azure CLI (az login)."""
    if not shutil.which("az"):
        raise AppError("Nejsme na Azure VM a Azure CLI (az) tu není.")
    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", KEY_VAULT_RESOURCE, "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise AppError("Azure CLI token nevydalo, přihlas se: az login")
    return result.stdout.strip()


def get_token():
    try:
        return token_from_managed_identity(), "managed identita VM"
    except urllib.error.URLError:
        return token_from_azure_cli(), "Azure CLI (az login)"


def read_secret(vault_name, secret_name, token):
    url = "https://%s.vault.azure.net/secrets/%s?api-version=%s" % (
        vault_name, urllib.parse.quote(secret_name), KEY_VAULT_API)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.load(resp)["value"]
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")
        try:
            message = json.loads(body)["error"]["message"]
        except (ValueError, KeyError):
            message = body[:300]
        hints = {
            401: "Token nesedí k tomuto tenantu nebo trezoru.",
            403: "Identita nemá oprávnění číst tajemství. V Key Vaultu > Access control (IAM) jí přiřaď "
                 "roli Key Vault Secrets User. Po přiřazení to může pár minut trvat.",
            404: "Tajemství '%s' v trezoru '%s' neexistuje (Objects > Secrets)." % (secret_name, vault_name),
        }
        raise AppError("Key Vault vrátil %s. %s\nDetail: %s" % (err.code, hints.get(err.code, ""), message))
    except urllib.error.URLError as err:
        raise AppError("Trezor %s.vault.azure.net není dostupný (%s). Sedí název v config.ini?" % (vault_name, err.reason))


def mask(value):
    if len(value) <= 8:
        return "*" * len(value)
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


def main():
    show_full = "--ukaz" in sys.argv[1:]
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config = configparser.ConfigParser()
    if not config.read(config_path, encoding="utf-8"):
        raise AppError("Chybí %s" % config_path)

    vault_name = config.get("keyvault", "vault_name", fallback="").strip()
    references = [(s, k, v) for s in config.sections() for k, v in config.items(s) if v.startswith("kv:")]
    if references and (not vault_name or vault_name == PLACEHOLDER):
        raise AppError("V config.ini doplň [keyvault] vault_name = název tvého trezoru.")

    token, token_source = (get_token() if references else (None, None))
    if token_source:
        print("Přihlášení do Key Vaultu: %s (heslo ani klíč v konfiguraci nejsou)\n" % token_source)

    name = config.get("app", "name", fallback="Ukázková aplikace")
    print("Konfigurace aplikace %s" % name)
    print("-" * 72)
    for section in config.sections():
        for key, raw in config.items(section):
            label = "%s.%s" % (section, key)
            if raw.startswith("kv:"):
                secret_name = raw[3:]
                value = read_secret(vault_name, secret_name, token)
                shown = value if show_full else mask(value)
                print("%-22s %-30s z Key Vaultu (%s / %s)" % (label, shown, vault_name, secret_name))
            else:
                print("%-22s %-30s z config.ini" % (label, raw))
    print("-" * 72)
    if references:
        print("Hotovo: tajemství jsou načtená z Key Vaultu, v config.ini je jen odkaz kv:<název>.")


if __name__ == "__main__":
    try:
        main()
    except AppError as err:
        print("CHYBA: %s" % err, file=sys.stderr)
        sys.exit(1)
