# Azure Function: hello

Python 3.12, programovací model v2. `GET /api/hello?name=Jan` vrátí pozdrav a údaje o prostředí v JSON.
Pozdrav jde změnit proměnnou prostředí `GREETING`.

1. Function App > **+ Create** > hosting **Flex Consumption**, runtime **Python 3.12**.
2. Zabalit `function_app.py`, `host.json` a `requirements.txt` do zipu (soubory v kořeni zipu).
3. Nasadit zip (Deployment Center, nebo `az functionapp deployment source config-zip`).
4. Otevřít `https://<function-app>.azurewebsites.net/api/hello?name=Jan`.

Složitější ukázka s managed identitou a Blob Storage: [../function-least-privilege](../function-least-privilege).
