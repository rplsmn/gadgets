#!/usr/bin/env python3
"""Assemble tous les gadgets en un seul site statique (gadgets.raphaelsimon.fr).

Chaque sous-dossier contenant un fichier `gadget.json` est un gadget :
  - clé "build" : la commande est exécutée DANS le dossier du gadget, puis le
    dossier "output" (défaut "dist") est copié vers dist/<slug>/
  - sinon (gadget statique) : le dossier est copié tel quel vers dist/<slug>/

Génère aussi dist/index.html (grille de navigation) à partir des manifestes.
Aucune dépendance externe : stdlib uniquement.

Ajouter un gadget = déposer un dossier avec un gadget.json. Rien d'autre.
"""
import html
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def discover():
    gadgets = []
    for manifest in sorted(ROOT.glob("*/gadget.json")):
        meta = json.loads(manifest.read_text(encoding="utf-8"))
        meta["slug"] = manifest.parent.name
        meta["dir"] = manifest.parent
        gadgets.append(meta)
    return gadgets


def build_gadget(g):
    out = DIST / g["slug"]
    if g.get("build"):
        print(f"  build  {g['slug']}: {g['build']}")
        subprocess.run(g["build"], cwd=g["dir"], shell=True, check=True)
        src = g["dir"] / g.get("output", "dist")
        if not src.is_dir():
            raise SystemExit(f"{g['slug']} : sortie '{src}' introuvable après le build")
        shutil.copytree(src, out, dirs_exist_ok=True)
    else:
        print(f"  static {g['slug']}")
        shutil.copytree(
            g["dir"],
            out,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("gadget.json", "__pycache__", ".git", "dist"),
        )


def build_index(gadgets):
    cards = []
    for g in sorted(gadgets, key=lambda x: x.get("title", x["slug"]).lower()):
        title = html.escape(g.get("title", g["slug"]))
        desc = html.escape(g.get("description", ""))
        cards.append(
            f'      <li><a class="card" href="{g["slug"]}/">\n'
            f"        <h2>{title}</h2>\n"
            f"        <p>{desc}</p>\n"
            f'        <span class="arrow">Ouvrir &rarr;</span>\n'
            f"      </a></li>"
        )
    generated = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")
    page = INDEX_TMPL.replace("__CARDS__", "\n".join(cards)).replace(
        "__GENERATED__", generated
    )
    (DIST / "index.html").write_text(page, encoding="utf-8")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    gadgets = discover()
    if not gadgets:
        print("⚠️  aucun gadget trouvé (cherche */gadget.json).")
    for g in gadgets:
        build_gadget(g)
    build_index(gadgets)
    # Domaine custom : le CNAME doit être présent dans l'artefact déployé.
    cname = ROOT / "CNAME"
    if cname.exists():
        shutil.copy(cname, DIST / "CNAME")
    print(f"✅ {len(gadgets)} gadget(s) assemblé(s) -> {DIST}")


INDEX_TMPL = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gadgets — raphaelsimon.fr</title>
<style>
  :root{--bg:#1b2420;--card:#243029;--card-line:rgba(237,230,216,.14);
    --ink:#ede6d8;--ink-dim:#b9b3a3;--moss:#8faf6e;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  header{padding:2.5rem 1.25rem 1rem;max-width:1000px;margin:0 auto}
  h1{margin:0 0 .25rem;font-size:1.8rem;letter-spacing:.01em}
  .sub{color:var(--ink-dim);margin:0;font-size:.95rem}
  main{max-width:1000px;margin:0 auto;padding:1.25rem 1.25rem 3rem}
  ul.grid{list-style:none;margin:0;padding:0;display:grid;gap:1rem;
    grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
  .card{display:block;background:var(--card);border:1px solid var(--card-line);
    border-radius:12px;padding:1.1rem 1.2rem;text-decoration:none;color:inherit;
    transition:border-color .15s ease,transform .15s ease}
  .card:hover{border-color:var(--moss);transform:translateY(-2px)}
  .card h2{margin:0 0 .35rem;font-size:1.1rem}
  .card p{margin:0;color:var(--ink-dim);font-size:.9rem;line-height:1.45}
  .card .arrow{color:var(--moss);font-size:.85rem;margin-top:.7rem;display:inline-block}
  footer{max-width:1000px;margin:0 auto;padding:0 1.25rem 2.5rem;
    color:var(--ink-dim);font-size:.78rem}
</style>
</head>
<body>
  <header>
    <h1>Gadgets</h1>
    <p class="sub">Petites pages statiques — raphaelsimon.fr</p>
  </header>
  <main>
    <ul class="grid">
__CARDS__
    </ul>
  </main>
  <footer>Généré automatiquement le __GENERATED__.</footer>
</body>
</html>
"""

if __name__ == "__main__":
    main()
