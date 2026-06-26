#!/usr/bin/env python3
"""Génère le site statique de suivi de la collection Yakari.

Source des données :
- data/tomes.csv     -> catalogue statique (numero, titre, annee)
- data/possede.json  -> état "possédé", maintenu via vps/server.py + push.sh

Aucune dépendance externe : uniquement la stdlib Python.
"""
import csv
import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOMES_CSV = ROOT / "data" / "tomes.csv"
POSSEDE_JSON = ROOT / "data" / "possede.json"
COVERS_DIR = ROOT / "covers"
DIST = ROOT / "dist"


def load_tomes():
    with TOMES_CSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_possession():
    if not POSSEDE_JSON.exists():
        print("⚠️  data/possede.json introuvable : génération avec tout en 'manquant'.")
        return {}
    raw = json.loads(POSSEDE_JSON.read_text(encoding="utf-8"))
    return {str(k): bool(v) for k, v in raw.items()}


def find_cover(numero):
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = COVERS_DIR / f"{int(numero):02d}.{ext}"
        if path.exists():
            return path
    return None


def card_html(tome, owned, cover_path):
    numero = tome["numero"]
    titre = html.escape(tome["titre"])
    annee = html.escape(tome.get("annee", ""))
    state_class = "owned" if owned else "missing"

    if cover_path:
        cover_inner = (
            f'<img src="covers/{cover_path.name}" '
            f'alt="Couverture du tome {numero}" loading="lazy">'
        )
    else:
        cover_inner = '<div class="cover-placeholder" aria-hidden="true"></div>'

    stamp = '<span class="stamp">en collection</span>' if owned else ""

    return f"""
      <li class="card {state_class}">
        <div class="cover">{cover_inner}{stamp}</div>
        <div class="meta">
          <span class="tab">N&deg; {numero}</span>
          <h2>{titre}</h2>
          <span class="year">{annee}</span>
        </div>
      </li>"""


def build():
    tomes = load_tomes()
    possede = load_possession()

    # Affichage : tomes possédés d'abord, puis par numéro croissant.
    tomes = sorted(
        tomes, key=lambda t: (not possede.get(t["numero"], False), int(t["numero"]))
    )

    owned_count = 0
    cards = []
    for tome in tomes:
        owned = possede.get(tome["numero"], False)
        owned_count += 1 if owned else 0
        cards.append(card_html(tome, owned, find_cover(tome["numero"])))

    total = len(tomes)
    pct = round(100 * owned_count / total) if total else 0
    generated = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")

    page = (
        TEMPLATE.replace("__OWNED__", str(owned_count))
        .replace("__TOTAL__", str(total))
        .replace("__PCT__", str(pct))
        .replace("__GENERATED__", generated)
        .replace("__CARDS__", "\n".join(cards))
    )

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "index.html").write_text(page, encoding="utf-8")

    if COVERS_DIR.exists():
        shutil.copytree(COVERS_DIR, DIST / "covers", dirs_exist_ok=True)

    print(f"✅ Généré : {owned_count}/{total} tomes possédés.")


TEMPLATE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Collection Yakari</title>
<style>
  :root{
    --bg:#1b2420; --card:#243029; --card-line:rgba(237,230,216,.14);
    --ink:#ede6d8; --ink-dim:#b9b3a3; --moss:#8faf6e;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  header{padding:2rem 1.25rem 1.25rem;max-width:1100px;margin:0 auto}
  h1{margin:0 0 .25rem;font-size:1.6rem;letter-spacing:.01em}
  .sub{color:var(--ink-dim);font-size:.95rem;margin:0 0 1rem}
  .progress-row{display:flex;align-items:center;gap:.75rem;margin-bottom:.75rem}
  .progress-track{flex:1;height:10px;border-radius:99px;
    background:rgba(237,230,216,.12);overflow:hidden}
  .progress-fill{height:100%;background:var(--moss);border-radius:99px;
    transition:width .4s ease}
  .progress-label{font-variant-numeric:tabular-nums;font-size:.9rem;
    color:var(--ink-dim);white-space:nowrap}
  .filter{display:inline-flex;align-items:center;gap:.5rem;
    font-size:.9rem;color:var(--ink-dim);cursor:pointer}
  .filter input{accent-color:var(--moss)}
  main{max-width:1100px;margin:0 auto;padding:0 1.25rem 2rem}
  ul.grid{list-style:none;margin:0;padding:0;display:grid;gap:1rem;
    grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
  .card{background:var(--card);border:1px solid var(--card-line);
    border-radius:10px;overflow:hidden;display:flex;flex-direction:column}
  .cover{position:relative;aspect-ratio:3/4;
    background:repeating-linear-gradient(45deg, rgba(237,230,216,.05) 0 8px, transparent 8px 16px)}
  .card.missing .cover{border-bottom:1px dashed var(--card-line)}
  .cover img{width:100%;height:100%;object-fit:cover;display:block}
  .cover-placeholder{width:100%;height:100%}
  .stamp{position:absolute;left:-16%;right:-16%;bottom:14%;text-align:center;
    white-space:nowrap;background:var(--moss);color:#16210f;font-size:.95rem;
    font-weight:800;letter-spacing:.12em;text-transform:uppercase;padding:.4rem 0;
    transform:rotate(-22deg);box-shadow:0 3px 10px rgba(0,0,0,.55)}
  .meta{padding:.6rem .7rem .8rem;display:flex;flex-direction:column;gap:.15rem}
  .tab{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    font-size:.72rem;color:var(--ink-dim)}
  .meta h2{margin:0;font-size:.88rem;line-height:1.25;font-weight:600;min-height:2.2em}
  .year{font-size:.75rem;color:var(--ink-dim)}
  .card.missing h2, .card.missing .year{color:var(--ink-dim)}
  body.hide-owned .card.owned{display:none}
  footer{max-width:1100px;margin:0 auto;padding:1rem 1.25rem 2.5rem;
    color:var(--ink-dim);font-size:.78rem}
  @media (prefers-reduced-motion: reduce){.progress-fill{transition:none}}
</style>
</head>
<body>
  <header>
    <h1>Collection Yakari</h1>
    <p class="sub">Suivi privé — tomes 1 à 42</p>
    <div class="progress-row">
      <div class="progress-track"><div class="progress-fill" style="width:__PCT__%"></div></div>
      <span class="progress-label">__OWNED__ / __TOTAL__ (__PCT__&nbsp;%)</span>
    </div>
    <label class="filter">
      <input type="checkbox" id="filter-missing">
      Afficher seulement les tomes manquants
    </label>
  </header>
  <main><ul class="grid">
__CARDS__
  </ul></main>
  <footer>Généré automatiquement le __GENERATED__.</footer>
  <script>
    document.getElementById('filter-missing').addEventListener('change', function(e){
      document.body.classList.toggle('hide-owned', e.target.checked);
    });
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
