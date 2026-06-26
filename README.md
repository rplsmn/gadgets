# gadgets

Petites pages statiques publiées sous **https://gadgets.raphaelsimon.fr/**.

Un seul repo, un seul site GitHub Pages. Chaque gadget vit dans un dossier à
la racine ; `build_site.py` les assemble tous dans `dist/<slug>/` et génère
la page d'accueil (grille de navigation) automatiquement.

## Ajouter un gadget

1. Créer un dossier `mon-gadget/` à la racine.
2. Y mettre un `gadget.json` :

   ```json
   {
     "title": "Mon gadget",
     "description": "Une phrase de description.",
     "static": true
   }
   ```

   - **Gadget statique** (juste du HTML/CSS/JS) : `"static": true`, et poser
     `index.html` + assets dans le dossier. Tout est copié tel quel.
   - **Gadget avec build** : remplacer `static` par
     `"build": "python3 scripts/build.py"` et `"output": "dist"` (le dossier
     produit par le build, copié vers `dist/<slug>/`).

3. `git push` sur `main` → GitHub Actions reconstruit et redéploie le site.
   Le gadget apparaît à `https://gadgets.raphaelsimon.fr/mon-gadget/` et sur
   l'accueil. **L'index ne s'édite jamais à la main.**

> Les liens internes d'un gadget doivent être **relatifs** (`covers/x.png`,
> pas `/covers/x.png`) puisqu'il est servi sous un sous-chemin.

## Build local

```bash
python3 build_site.py   # produit dist/ (index + chaque gadget)
```

Aucune dépendance : stdlib Python uniquement.

## Gadget « yakari-tracker »

Suivi de collection avec une partie admin tournant sur le VPS (cases à
cocher → `data/possede.json` → push → redéploiement). Usage :

```bash
./yakari-tracker/vps/edit-library.sh   # lance l'admin, affiche l'URL tailnet ; Ctrl-C pour fermer
./yakari-tracker/vps/push.sh           # commit + push -> le site se redéploie
```

(Les scripts détectent seuls leur emplacement ; à lancer depuis n'importe où
dans le repo.)

## Hébergement / DNS (aide-mémoire)

- **Plateforme** : GitHub Pages (repo `rplsmn/gadgets`), source = GitHub Actions.
- **Domaine** : fichier `CNAME` = `gadgets.raphaelsimon.fr`.
- **DNS** (chez **Netim**, `ns*.netim.net`) :
  `CNAME  gadgets  →  rplsmn.github.io.`
- Settings > Pages : custom domain `gadgets.raphaelsimon.fr` + Enforce HTTPS.

C'est la même recette que `www` et `akm`.
