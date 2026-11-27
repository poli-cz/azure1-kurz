# Python aplikace pro Azure App Service

Jen standardní knihovna, bez závislostí. App Service (Linux, Python 3.12) ji spustí sám přes `gunicorn app:app`.
Text nadpisu jde změnit v **Settings > Environment variables** proměnnou `GREETING`. Adresa `/health` vrací `OK`.

Nasazení zipem:

1. Zabalit `app.py` a `requirements.txt` do zipu (soubory v kořeni zipu, ne ve složce).
2. Web App > **Deployment > Deployment Center** > **Publish files (new)** > nahrát zip.
3. Otevřít adresu aplikace (Overview > Default domain). Pokud se ukáže výchozí stránka, načíst znovu.

Lokálně: `python3 app.py` a otevřít http://localhost:8000.
