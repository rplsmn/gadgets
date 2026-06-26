#!/usr/bin/env bash
# Publie l'état de la collection : commit + push de data/possede.json.
# Le push (branche courante, suivie par origin) déclenche le redéploiement Pages.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

git add data/possede.json
if git diff --cached --quiet; then
  echo "Rien à publier (possede.json inchangé)."
  exit 0
fi

git commit -m "Mise à jour collection Yakari ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
git pull --rebase
git push
echo "✅ Publié — le site se redéploie tout seul (~1 min) :"
echo "   https://rplsmn.github.io/yakari-tracker/"
