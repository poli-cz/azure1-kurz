"""Ukázková appka pro Azure App Service (Linux, Python 3.12).

Jen standardní knihovna, žádné balíčky: App Service ji spustí příkazem
`gunicorn app:app`, který si najde sám podle souboru app.py.
"""
import os
import platform
import socket
from datetime import datetime, timezone
from html import escape

PAGE = """<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Azure App Service – Python</title>
<style>
  body {{ font-family: system-ui, sans-serif; background: #f3f6fb; color: #1b1b1b; margin: 0; }}
  main {{ max-width: 640px; margin: 48px auto; padding: 32px; background: #fff;
         border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,.08); }}
  h1 {{ color: #0078d4; margin-top: 0; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td {{ padding: 8px 4px; border-bottom: 1px solid #e5e5e5; }}
  td:first-child {{ color: #666; width: 40%; }}
</style>
</head>
<body>
<main>
<h1>{greeting}</h1>
<table>{rows}</table>
</main>
</body>
</html>
"""


def app(environ, start_response):
    if environ.get("PATH_INFO") == "/health":
        body = b"OK"
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8"),
                                  ("Content-Length", str(len(body)))])
        return [body]

    info = {
        "Python": platform.python_version(),
        "Server": socket.gethostname(),
        "App Service": os.environ.get("WEBSITE_SITE_NAME", "lokálně"),
        "Region": os.environ.get("REGION_NAME", "-"),
        "Instance": os.environ.get("WEBSITE_INSTANCE_ID", "-")[:12],
        "Čas (UTC)": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }
    rows = "".join(f"<tr><td>{escape(k)}</td><td>{escape(v)}</td></tr>" for k, v in info.items())
    greeting = os.environ.get("GREETING", "Ahoj z Azure App Service")
    body = PAGE.format(greeting=escape(greeting), rows=rows).encode("utf-8")
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"),
                              ("Content-Length", str(len(body)))])
    return [body]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    make_server("", 8000, app).serve_forever()
