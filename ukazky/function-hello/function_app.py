"""Ukázková Azure Function (Python 3.12, programovací model v2).

Jedna HTTP funkce: GET /api/hello?name=Jan vrátí pozdrav a pár údajů
o prostředí. Pozdrav jde změnit proměnnou prostředí GREETING.
"""
import json
import logging
import os
import platform
from datetime import datetime, timezone

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="hello", methods=["GET", "POST"])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")
    if not name:
        try:
            name = req.get_json().get("name")
        except ValueError:
            name = None
    name = name or "světe"
    logging.info("hello zavolána pro %s", name)

    body = {
        "message": f"{os.environ.get('GREETING', 'Ahoj')}, {name}!",
        "function_app": os.environ.get("WEBSITE_SITE_NAME", "lokálně"),
        "region": os.environ.get("REGION_NAME", "-"),
        "python": platform.python_version(),
        "time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }
    return func.HttpResponse(
        json.dumps(body, ensure_ascii=False, indent=2),
        mimetype="application/json",
        status_code=200,
    )
