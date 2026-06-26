#!/usr/bin/env python3
"""Mini-admin pour cocher les tomes Yakari possédés.

N'écoute QUE sur 127.0.0.1. L'exposition au tailnet se fait via
`tailscale serve`, jamais par un bind public. Stdlib uniquement.
"""
import csv
import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

REPO_DIR = Path(os.environ.get("REPO_DIR", ".")).resolve()
TOMES_CSV = REPO_DIR / "data" / "tomes.csv"
POSSEDE_JSON = REPO_DIR / "data" / "possede.json"
PORT = int(os.environ.get("PORT", "8765"))
# Défaut sûr : 127.0.0.1 (n'écoute que en local, exposition via `tailscale serve`).
# Surchargeable via la variable HOST si tu protèges l'accès au niveau réseau :
#   HOST=0.0.0.0        -> toutes interfaces (OK seulement derrière un pare-feu tailnet-only)
#   HOST=<ip-tailscale> -> ne binde que l'interface du tailnet (ex. 100.99.1.30)
HOST = os.environ.get("HOST", "127.0.0.1")


def load_tomes():
    with TOMES_CSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_possede():
    if POSSEDE_JSON.exists():
        return json.loads(POSSEDE_JSON.read_text(encoding="utf-8"))
    return {}


def save_possede(data):
    POSSEDE_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def render_form():
    tomes = load_tomes()
    possede = load_possede()
    rows = []
    for t in tomes:
        n = t["numero"]
        checked = "checked" if possede.get(n) else ""
        rows.append(
            f'<li><label><input type="checkbox" name="t" value="{n}" {checked}>'
            f' N&deg;{n} — {html.escape(t["titre"])} ({html.escape(t.get("annee",""))})'
            f"</label></li>"
        )
    owned = sum(1 for t in tomes if possede.get(t["numero"]))
    return (
        PAGE.replace("__ROWS__", "\n".join(rows))
        .replace("__SUMMARY__", f"{owned} / {len(tomes)} possédés")
    )


PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Yakari — admin</title>
<style>
  body{font-family:-apple-system,sans-serif;background:#1b2420;color:#ede6d8;
       max-width:480px;margin:0 auto;padding:1.25rem}
  h1{font-size:1.3rem}
  ul{list-style:none;padding:0}
  li{padding:.45rem 0;border-bottom:1px solid rgba(237,230,216,.12);font-size:.95rem}
  input[type=checkbox]{transform:scale(1.3);margin-right:.5rem;accent-color:#8faf6e}
  button{margin-top:1.25rem;width:100%;padding:.8rem;font-size:1rem;
         background:#8faf6e;color:#16210f;border:0;border-radius:8px;font-weight:600}
  .summary{color:#b9b3a3;font-size:.9rem}
</style></head>
<body>
  <h1>Collection Yakari</h1>
  <p class="summary">__SUMMARY__</p>
  <form method="POST" action="/save">
    <ul>
__ROWS__
    </ul>
    <button type="submit">Enregistrer</button>
  </form>
</body></html>
"""

CONFIRM_PAGE = '<p>Enregistré. <a href="/">Retour</a></p>'


class Handler(BaseHTTPRequestHandler):
    def _send_html(self, body, status=200):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path != "/":
            self._send_html("<p>Not found</p>", 404)
            return
        self._send_html(render_form())

    def do_POST(self):
        if self.path != "/save":
            self._send_html("<p>Not found</p>", 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        checked_numeros = set(parse_qs(body).get("t", []))
        tomes = load_tomes()
        new_state = {t["numero"]: (t["numero"] in checked_numeros) for t in tomes}
        save_possede(new_state)
        self._send_html(CONFIRM_PAGE)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Écoute sur http://{HOST}:{PORT} (PID {os.getpid()})")
    server.serve_forever()
