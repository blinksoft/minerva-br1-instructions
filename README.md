# Minerva BR-1 — Block 0 Assembly Instructions

A mobile-friendly, scrolling build guide for the Georgia Wing High Power Rocketry
Minerva BR-1, converted from the Block 0 instruction deck.

Static site — no server, no build dependencies beyond Python 3 (standard library only).

## What's here

```
index.html               generated — do not edit by hand
build.py                 regenerates index.html from content/steps.json
content/steps.json       all text: parts, tools, steps, callouts, captions  <- edit this
content/images.json      image dimensions (generated when photos were extracted)
assets/img/              build photos (WebP) + program emblem
files/BR-1.ork           the program's OpenRocket model, linked from the last step
assets/css/style.css     styles, including print and dark mode
assets/js/app.js         progress checkboxes, theme toggle, photo lightbox
.github/workflows/       GitHub Pages deploy
deploy/                  AWS S3 + CloudFront alternative
```

## Editing content

1. Edit `content/steps.json`.
2. `python3 build.py`
3. Commit both `content/steps.json` and `index.html`.

Step body lines that begin with `1.`, `2.`, … render as a numbered sub-step list.
Callout types are `warn`, `tip`, `time`, and `link` (a `link` note also needs `href`).
A step's `epoxy` field renders as a timing badge at the top of the step.
An image's optional `tag` of `ok` or `no` puts a green check or red X on it.

Adding a photo: drop the file in `assets/img/`, add an entry to `content/images.json`
with its pixel `w`/`h` (used to reserve layout space), then reference it from a step.

## Deploy: GitHub Pages

1. Create the repo and push:
   ```bash
   git remote add origin git@github.com:<you>/minerva-br1-instructions.git
   git push -u origin main
   ```
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Every push to `main` rebuilds and publishes to
   `https://<you>.github.io/minerva-br1-instructions/`.

The site uses only relative paths, so it works from a project subpath without
extra configuration. `.nojekyll` is present so nothing gets filtered.

## Deploy: AWS

See [`deploy/README-aws.md`](deploy/README-aws.md). Short version: this is a static
site, so S3 + CloudFront is the right shape — a few cents a month, free TLS through
ACM, nothing to patch. Lightsail would mean running and updating a server for files
that never change.

## Content notes

* The current kit's body tube is **white**. Some photos show an older kraft-brown
  tube; parts and steps are identical.
* Steps 9 and 10 (the rail buttons) use panels rendered from the original slides
  rather than the bare photos, so the arrows, orange callouts and numbered badges
  showing *where* the glue goes survive the conversion. Regenerating them needs the
  source .pptx; the finished WebP files are committed.
* The knot steps carry the briefing's own annotated diagrams — they mark where the
  eyebolt and the nose cone bar sit in the knot, which the generic knot references
  omit — alongside links to Animated Knots. Diagram sources are credited in the
  captions (wikiHow, 101Knots); swap them for original artwork if the site ever needs
  to be fully self-licensed.
* Progress checkmarks are stored in the visitor's own browser (`localStorage`).
  Nothing is collected or transmitted.

## Credits

Georgia Wing High Power Rocketry, Civil Air Patrol. Photos and build content by the
program.
