#!/usr/bin/env bash
# Admin Yakari : ouvre une page de cases à cocher accessible depuis le tailnet.
#
# Workflow :
#   ./vps/edit-library.sh     -> lance le serveur, affiche l'URL
#   (cocher les tomes depuis le tél, puis Ctrl-C pour fermer)
#   ./vps/push.sh             -> publie -> le site se redéploie tout seul
#
# Variables surchargeables : HOST (défaut 0.0.0.0), PORT (défaut 8765).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8765}"

cd "$REPO_DIR"
git pull --ff-only 2>/dev/null || echo "ℹ️  git pull ignoré (hors-ligne ou branche divergente)."

# Nom MagicDNS de la machine pour l'URL d'accès (sinon hostname brut)
URL_HOST="$(tailscale status --json 2>/dev/null \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["Self"]["DNSName"].rstrip("."))' 2>/dev/null \
  || hostname)"

echo "────────────────────────────────────────────"
echo "  Admin Yakari en écoute sur ${HOST}:${PORT}"
echo "  Depuis ton tél (tailnet) :  http://${URL_HOST}:${PORT}/"
echo "  Ctrl-C pour fermer, puis ./vps/push.sh pour publier."
echo "────────────────────────────────────────────"

export HOST PORT REPO_DIR
exec python3 "$REPO_DIR/vps/server.py"
