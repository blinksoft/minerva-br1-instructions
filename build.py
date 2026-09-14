#!/usr/bin/env python3
"""Build index.html from content/steps.json.

Edit content/steps.json (and drop new photos in assets/img/), then run:
    python3 build.py
"""
import json, html, os, re, sys, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
D    = json.load(open(os.path.join(ROOT, "content/steps.json"), encoding="utf-8"))
DIMS = {m["file"]: (m["w"], m["h"])
        for m in json.load(open(os.path.join(ROOT, "content/images.json"), encoding="utf-8"))}

e = lambda s: html.escape(str(s), quote=True)

ICON = {"warn": "!", "tip": "i", "time": "⏱", "link": "↗"}


def callout(n):
    kind = n.get("type", "tip")
    if kind == "link":
        inner = f'<a href="{e(n["href"])}" target="_blank" rel="noopener">{e(n["text"])}</a>'
    else:
        inner = e(n["text"])
    return (f'<div class="callout {kind}"><span class="ic" aria-hidden="true">{ICON[kind]}</span>'
            f'<div>{inner}</div></div>')


def body_html(lines):
    """Lines beginning '1.' '2.' ... become a numbered sub-step list; others are paragraphs."""
    out, run = [], []

    def flush():
        if run:
            out.append('<ol class="substeps">' +
                       "".join(f"<li>{e(x)}</li>" for x in run) + "</ol>")
            run.clear()

    for ln in lines:
        m = re.match(r"^\s*\d+\.\s+(.*)$", ln)
        if m:
            run.append(m.group(1))
        else:
            flush()
            out.append(f"<p>{e(ln)}</p>")
    flush()
    return "".join(out)


def figures(imgs):
    if not imgs:
        return ""
    cells = []
    for im in imgs:
        f = im["file"]
        w, h = DIMS.get(f, (1200, 900))
        tag = im.get("tag")
        badge = ""
        cls = ""
        if tag == "ok":
            badge = '<span class="tagbadge ok" title="Correct">✓</span>'; cls = " ok"
        elif tag == "no":
            badge = '<span class="tagbadge no" title="Incorrect">✕</span>'; cls = " no"
        cells.append(
            f'<figure class="fig{cls}"><div class="imgwrap">{badge}'
            f'<img src="assets/img/{e(f)}" width="{w}" height="{h}" loading="lazy" decoding="async" '
            f'alt="{e(im["cap"])}"></div>'
            f'<figcaption>{e(im["cap"])}</figcaption></figure>')
    return f'<div class="figs n{min(len(cells),5)}">' + "".join(cells) + "</div>"


def step_html(st):
    sid = f"step-{st['n']}"
    notes_top = []
    if st.get("epoxy"):
        notes_top.append(callout({"type": "time", "text": st["epoxy"]}))
    notes = "".join(callout(n) for n in st.get("notes", []))
    return f"""
<article class="card step" id="{sid}" data-step="{st['n']}">
  <div class="step-head">
    <div class="step-num" aria-hidden="true">{st['n']}</div>
    <h3 class="step-title">{e(st['title'])}</h3>
    <label class="step-done" title="Mark this step complete">
      <input type="checkbox" class="js-step" data-key="{sid}"><span>Done</span>
    </label>
  </div>
  <div class="step-body">
    {"".join(notes_top)}
    {body_html(st.get('body', []))}
    {notes}
    {figures(st.get('images', []))}
  </div>
</article>"""


def checklist(items, key):
    lis = "".join(
        f'<li><label><input type="checkbox" class="js-chk" data-key="{key}-{i}"><span>{e(x)}</span></label></li>'
        for i, x in enumerate(items))
    return f'<ul class="checklist">{lis}</ul>'


meta = D["meta"]
total = sum(len(s["steps"]) for s in D["stages"])

toc = "".join(
    f'<li><a href="#{e(s["id"])}">{e(s["name"])}</a> '
    f'<span class="cnt">&middot; {len(s["steps"])} step{"s" if len(s["steps"]) != 1 else ""}</span></li>'
    for s in D["stages"])

stages = ""
for i, s in enumerate(D["stages"], 1):
    blurb = f'<p class="secblurb">{e(s["blurb"])}</p>' if s.get("blurb") else ""
    stages += (f'<section id="{e(s["id"])}">'
               f'<h2 class="sec"><span class="idx">{i:02d}</span>{e(s["name"])}</h2>{blurb}'
               + "".join(step_html(st) for st in s["steps"]) + "</section>")

intro = D["intro"]
built = datetime.date.today().isoformat()

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(meta['kit'])} {e(meta['block'])} — Assembly Instructions</title>
<meta name="description" content="{e(meta['subtitle'])}">
<meta name="color-scheme" content="light dark">
<meta property="og:title" content="{e(meta['kit'])} {e(meta['block'])} — Assembly Instructions">
<meta property="og:description" content="{e(meta['subtitle'])}">
<meta property="og:type" content="article">
<link rel="icon" href="assets/img/logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/logo.png">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

<header class="topbar">
  <div class="wrap topbar-in">
    <a class="mark" href="#top"><img src="assets/img/logo.svg" alt=""><span>{e(meta['kit'])} <span class="blk" style="color:var(--ink-3)">{e(meta['block'])}</span></span></a>
    <span class="spacer"></span>
    <span class="iconbtn" id="counter" style="cursor:default">0 / {total}</span>
    <button class="iconbtn resetbtn" id="reset" title="Clear all checkmarks">Reset</button>
    <button class="iconbtn themebtn" id="theme" title="Toggle light / dark" aria-label="Toggle theme"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4"/></svg></button>
  </div>
  <div class="progressbar" id="bar"></div>
</header>

<main class="wrap" id="top">

  <div class="hero">
    <img class="logo" src="assets/img/logo.svg" alt="Georgia Wing High Power Rocketry emblem">
    <p class="eyebrow">{e(meta['program'])}</p>
    <h1>{e(meta['kit'])} {e(meta['block'])}<br>Assembly Instructions</h1>
    <p class="lede">{e(meta['subtitle'])}</p>
    <div class="metastrip">
      <span class="chip">{total} steps</span>
      <span class="chip">{len(D['stages'])} stages</span>
      <span class="chip">Progress saves on this device</span>
    </div>
  </div>

  <section id="start">
    <h2 class="sec">{e(intro['heading'])}</h2>
    {''.join(f'<p class="secblurb">{e(p)}</p>' for p in intro['points'])}
    <div class="card listcard">
      <h3>Safety</h3>
      {''.join(callout({'type':'warn','text':x}) for x in intro['safety'])}
    </div>
  </section>

  <section id="parts">
    <h2 class="sec"><span class="idx">00</span>Parts &amp; Tools</h2>
    <p class="secblurb">Lay everything out and check it off before you start. Tell your instructor now if something is missing.</p>
    {figures([D['partsPhoto']]) if D.get('partsPhoto') else ''}
    <div class="twocol">
      <div class="card listcard"><h3>Kit parts</h3>{checklist(D['parts'],'part')}</div>
      <div class="card listcard"><h3>Tools needed</h3>{checklist(D['tools'],'tool')}</div>
    </div>
    <div class="card toc">
      <h3>Build sequence</h3>
      <ol>{toc}</ol>
    </div>
  </section>

  {stages}

  <footer class="site">
    <p><strong>{e(meta['program'])}</strong> &middot; Civil Air Patrol</p>
    <p>{e(meta['source'])} Built {built}.</p>
    <p>Photos and build content by the Georgia Wing High Power Rocketry program. Knot references link out to Animated Knots.</p>
  </footer>
</main>

<div id="lb" role="dialog" aria-modal="true" aria-label="Enlarged photo">
  <button class="close" id="lbclose" aria-label="Close">&times;</button>
  <div><img id="lbimg" alt=""><div class="cap" id="lbcap"></div></div>
</div>

<script src="assets/js/app.js" defer></script>
</body>
</html>
"""

open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)
print(f"index.html written — {total} steps, {len(D['stages'])} stages, {len(DIMS)} images indexed")
