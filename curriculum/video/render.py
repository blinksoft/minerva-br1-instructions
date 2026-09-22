#!/usr/bin/env python3
"""Render a curriculum segment video from its cue list.

    python3 render.py S06            # build videos/S06.mp4 (+ .srt), refresh S06/script.md
    python3 render.py all            # every SNN folder; unchanged segments are skipped
    python3 render.py S06 --force    # rebuild even if nothing changed
    python3 render.py S06 --script   # only regenerate S06/script.md for recording
    python3 render.py S06 --slides   # draw the slides to S06/slides/ only: no narration, no video, no cost

Each cue in SNN/cues.json is one slide plus one line of narration. A segment may add slide types of
its own in SNN/slides.py (a `register(render)` function that adds to render.SLIDES). Shared data the
slides draw from (the BR-1's OpenRocket results, the motors' thrust curves) lives in shared/. Narration audio is looked up in
this order: SNN/voice/NN.wav (a real person reading script.md), then SNN/narration/NN-<hash>.mp3
(synthesized earlier and committed), and only if neither exists is the TTS engine called. The hash
is of the spoken text plus the voice, so a cue is synthesized once per wording and never again.

A segment is skipped when the fingerprint of its inputs (cues.json, assets/, narration/, voice/,
this script) matches videos/SNN.sha from the last render.

Environment (a .env file in the repo root is read too; keep it out of git):
    ELEVEN_LABS_API_KEY   use ElevenLabs for narration. The key needs only the text_to_speech
                          permission. Cached per cue, so unchanged cues cost nothing on re-render.
    ELEVEN_LABS_VOICE     ElevenLabs voice ID or a name from VOICES (default: josh).
    ELEVEN_LABS_MODEL     default eleven_multilingual_v2.
    TTS_ENGINE            "eleven" or "piper"; default eleven when the key is present.
    PIPER_VOICE           path to a Piper .onnx voice, the free local fallback.
    FFMPEG                path to ffmpeg; defaults to the imageio-ffmpeg bundled binary if installed.
"""
import hashlib, json, os, re, shutil, subprocess, sys, wave, urllib.request
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W, H, FPS = 1920, 1080, 30
PAD_AFTER = 0.7          # seconds of silence after each narration line
FONT_DIR = os.path.join(HERE, "fonts")
LOGO = os.path.join(ROOT, "assets", "img", "logo.png")
VIDEOS = os.path.join(ROOT, "videos")

# Palette: the guide's dark theme, so the videos and the page look like one thing.
BG, INK, INK2, INK3 = "#14151a", "#e9e8e4", "#adaba4", "#807d76"
ACCENT, ACCENT_DEEP, WARN, OK = "#7fb0ee", "#123a6d", "#e0a35a", "#5cc27f"
CARD = "#1c1e25"
LINE = "#31353f"

CLASSES = [("A", 2.5), ("B", 5), ("C", 10), ("D", 20), ("E", 40), ("F", 80), ("G", 160),
           ("H", 320), ("I", 640), ("J", 1280), ("K", 2560), ("L", 5120), ("M", 10240),
           ("N", 20480), ("O", 40960)]


def load_env():
    """Read KEY=value lines from ROOT/.env into os.environ without overriding what is already set."""
    p = os.path.join(ROOT, ".env")
    if not os.path.exists(p):
        return
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()
# Voices the program picked from the ElevenLabs library. Segments alternate: odd-numbered segments
# are read by Josh, even-numbered by Nichalia. A segment can override with "voice" in its cues.json
# meta, and ELEVEN_LABS_VOICE overrides everything (useful for samples).
VOICES = {"josh": "nzFihrBIvB34imQBuxub",        # Josh - Teacher for kids
          "nichalia": "XfNU2rGpBa01ckF309OY"}    # Nichalia Schwartz - Bright and Friendly
ELEVEN_DEFAULT_VOICE = VOICES["josh"]
_meta_voice = None


_seg_number = 0


def voice_id():
    v = os.environ.get("ELEVEN_LABS_VOICE") or _meta_voice or ("josh" if _seg_number % 2 else "nichalia")
    return VOICES.get(v.lower(), v)


def engine():
    e = os.environ.get("TTS_ENGINE")
    if e:
        return e
    return "eleven" if os.environ.get("ELEVEN_LABS_API_KEY") else "piper"


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"Inter-{weight}.ttf"), size)


def ffmpeg():
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return shutil.which("ffmpeg") or sys.exit("ffmpeg not found; set FFMPEG or pip install imageio-ffmpeg")


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ---------------------------------------------------------------- drawing helpers

def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, width, gap=1.25, align="left"):
    x, y = xy
    lh = int(fnt.size * gap)
    for ln in wrap(draw, text, fnt, width):
        if align == "center":
            tw = draw.textlength(ln, font=fnt)
            draw.text((x + (width - tw) / 2, y), ln, font=fnt, fill=fill)
        else:
            draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def canvas(bg=BG):
    im = Image.new("RGB", (W, H), bg)
    return im, ImageDraw.Draw(im)


def footer(draw, im, label, dark=True):
    draw.text((96, H - 78), label, font=font("SemiBold", 26), fill=INK3 if dark else "#c7d6ea")
    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA")
        logo.thumbnail((72, 72))
        im.paste(logo, (W - 96 - logo.width, H - 96 - 8), logo)


def heading(draw, text, y=110, size=76, fill=INK):
    draw.text((96, y), text, font=font("ExtraBold", size), fill=fill)
    return y + int(size * 1.35)


# ---------------------------------------------------------------- slide types

def slide_title(c, m):
    im, d = canvas()
    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA"); logo.thumbnail((170, 170))
        im.paste(logo, (96, 150), logo)
    d.text((96, 360), m["eyebrow"], font=font("SemiBold", 34), fill=ACCENT)
    y = text_block(d, (96, 420), c["title"], font("ExtraBold", 112), INK, W - 192, gap=1.08)
    text_block(d, (96, y + 30), c.get("sub", ""), font("Regular", 42), INK2, W - 192)
    footer(d, im, m["footer"])
    return im


def slide_text(c, m):
    im, d = canvas()
    y = heading(d, c["heading"])
    y += 20
    for ln in c.get("lines", []):
        d.rounded_rectangle((96, y + 18, 118, y + 40), 6, fill=ACCENT)
        y = text_block(d, (150, y), ln, font("SemiBold", 52), INK, W - 300) + 28
    if c.get("note"):
        text_block(d, (96, H - 230), c["note"], font("Regular", 34), INK2, W - 192)
    footer(d, im, m["footer"])
    return im


def slide_close(c, m):
    im, d = canvas(ACCENT_DEEP)
    d.text((96, 150), "The one thing to remember", font=font("SemiBold", 36), fill="#c7d6ea")
    y = text_block(d, (96, 260), c["text"], font("ExtraBold", 96), "#ffffff", W - 192, gap=1.12)
    if c.get("sub"):
        text_block(d, (96, y + 40), c["sub"], font("Regular", 40), "#c7d6ea", W - 192)
    footer(d, im, m["footer"], dark=False)
    return im


def slide_pause(c, m, n):
    """Countdown frame n (5..1)."""
    im, d = canvas(ACCENT_DEEP)
    d.text((96, 110), "PAUSE HERE  ·  ASK THE ROOM", font=font("ExtraBold", 40), fill=WARN)
    text_block(d, (96, 230), c["question"], font("ExtraBold", 84), "#ffffff", W - 192 - 320, gap=1.12)
    # countdown ring
    cx, cy, r = W - 96 - 130, H - 96 - 190, 120
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline="#c7d6ea", width=10)
    frac = n / 5
    d.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + int(360 * frac), fill=WARN)
    d.ellipse((cx - r + 22, cy - r + 22, cx + r - 22, cy + r - 22), fill=ACCENT_DEEP)
    f = font("ExtraBold", 120); tw = d.textlength(str(n), font=f)
    d.text((cx - tw / 2, cy - 78), str(n), font=f, fill="#ffffff")
    d.text((96, H - 200), "Take two or three answers, then press play.", font=font("Regular", 36), fill="#c7d6ea")
    footer(d, im, m["footer"], dark=False)
    return im


def slide_answer(c, m):
    """The answer card. "text" alone is one big statement; with "lines" the text is a short lead and
    each line is a bullet, for answers that are a list."""
    im, d = canvas()
    d.text((96, 110), "ANSWER", font=font("ExtraBold", 40), fill=OK)
    if c.get("lines"):
        y = text_block(d, (96, 210), c["text"], font("ExtraBold", 72), INK, W - 192, gap=1.12) + 36
        for ln in c["lines"]:
            d.rounded_rectangle((96, y + 20, 118, y + 42), 6, fill=OK)
            y = text_block(d, (150, y), ln, font("SemiBold", 54), INK, W - 300) + 26
    else:
        text_block(d, (96, 220), c["text"], font("ExtraBold", 80), INK, W - 192, gap=1.12)
    footer(d, im, m["footer"])
    return im


def slide_photo(c, m):
    """Text on the left, a photo in a rounded card on the right, optional badge on the card."""
    im, d = canvas()
    heading(d, c["heading"])
    sdir = c.get("_dir", "")
    photo = Image.open(os.path.join(sdir, c["image"])).convert("RGB")
    box_x, box_y, box_w, box_h = 1040, 250, 784, 620
    photo.thumbnail((box_w, box_h))
    px = box_x + (box_w - photo.width) // 2; py = box_y + (box_h - photo.height) // 2
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, photo.width - 1, photo.height - 1), 28, fill=255)
    im.paste(photo, (px, py), mask)
    if c.get("badge"):
        f = font("ExtraBold", 54); tw = d.textlength(c["badge"], font=f)
        bx2, by2 = px + photo.width - 24, py + photo.height + 26
        d.rounded_rectangle((bx2 - tw - 56, by2 - 92, bx2, by2), 24, fill=ACCENT_DEEP, outline=ACCENT, width=3)
        d.text((bx2 - tw - 28, by2 - 78), c["badge"], font=f, fill="#ffffff")
    text_block(d, (96, 300), c["caption"], font("SemiBold", 52), INK, 880)
    if c.get("lines"):
        y = 600
        for ln in c["lines"]:
            d.rounded_rectangle((96, y + 16, 118, y + 38), 6, fill=ACCENT)
            y = text_block(d, (150, y), ln, font("Regular", 42), INK2, 860) + 22
    if c.get("credit"):
        d.text((box_x, H - 78), c["credit"], font=font("Regular", 22), fill=INK3)
    footer(d, im, m["footer"])
    return im


def slide_clip(c, m):
    """A screen-recording clip. The still is the clip's first frame on the plate; the video build
    overlays the moving clip on the same plate (see encode_clip). Cue keys: "src" (path under the
    segment folder), "heading", optional "crop": [x, y, w, h] in source pixels, optional "fit":
    "hold" (default: the last frame holds if the narration runs longer, the tail is cut if shorter)
    or "stretch" (the clip is slowed or sped so it ends with the narration)."""
    im, d = canvas()
    heading(d, c["heading"], y=56, size=56)
    footer(d, im, m["footer"])
    src = os.path.join(c.get("_dir", ""), c["src"])
    frame = first_frame(src, c.get("crop"))
    x, y, w, h = clip_placement(frame.size)
    im.paste(frame.resize((w, h), Image.LANCZOS), (x, y))
    d.rectangle((x - 2, y - 2, x + w + 1, y + h + 1), outline=LINE, width=2)
    return im


CLIP_BOX = (96, 140, W - 192, 860)      # where the clip sits on the plate, under the heading


def clip_placement(size):
    bx, by, bw, bh = CLIP_BOX
    sw, sh = size
    s = min(bw / sw, bh / sh)
    w, h = int(sw * s) // 2 * 2, int(sh * s) // 2 * 2
    return bx + (bw - w) // 2, by + (bh - h) // 2, w, h


def first_frame(src, crop=None):
    import tempfile
    ff = ffmpeg()
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    vf = [f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}"] if crop else ["null"]
    run(ff, "-y", "-v", "error", "-i", src, "-vf", ",".join(vf), "-frames:v", "1", tmp)
    im = Image.open(tmp).convert("RGB"); im.load(); os.remove(tmp)
    return im


def media_seconds(ff, path):
    out = subprocess.run([ff, "-i", path], capture_output=True, text=True).stderr
    mt = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", out)
    if not mt:
        sys.exit(f"cannot read duration of {path}")
    return int(mt.group(1)) * 3600 + int(mt.group(2)) * 60 + float(mt.group(3))


def slide_curves(c, m):
    """Real thrust curves from thrustcurve.org data, on shared axes, area under each filled."""
    im, d = canvas()
    heading(d, c["heading"])
    text_block(d, (96, 225), c["caption"], font("SemiBold", 44), INK2, W - 192)
    data = json.load(open(os.path.join(c.get("_dir", ""), c["data"])))
    by = {mm["designation"]: mm for mm in data["motors"]}
    motors = [by[k] for k in c["motors"]]          # cue order sets the colour order
    x0, y0, pw, ph = 190, 380, 1300, 470            # plot box
    tmax = max(pt[0] for mm in motors for pt in mm["samples"]) * 1.04
    fmax = max(pt[1] for mm in motors for pt in mm["samples"]) * 1.12
    X = lambda t: x0 + t / tmax * pw
    Y = lambda f: y0 + ph - f / fmax * ph
    # axes and light gridlines
    fs, ts_ = int(max(20, nice_step(fmax))), nice_step(tmax)
    for k in range(0, int(fmax) + 1, fs):
        d.line((x0, Y(k), x0 + pw, Y(k)), fill="#22262f", width=2)
        d.text((x0 - 70, Y(k) - 16), f"{k}", font=font("Regular", 26), fill=INK3)
    k = 0
    while k <= tmax:
        d.text((X(k) - 10, y0 + ph + 12), f"{k:g}", font=font("Regular", 26), fill=INK3); k += ts_
    d.line((x0, y0 + ph, x0 + pw, y0 + ph), fill=INK3, width=4)
    d.line((x0, y0, x0, y0 + ph), fill=INK3, width=4)
    d.text((x0 + pw - 170, y0 + ph + 46), "time, seconds", font=font("SemiBold", 28), fill=INK3)
    d.text((x0 + 12, y0 - 40), "thrust, Newtons", font=font("SemiBold", 28), fill=INK3)
    colors = [ACCENT, WARN, OK]
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(overlay)
    for mm, col in zip(motors, colors):
        pts = [(X(0), Y(0))] + [(X(t), Y(f)) for t, f in mm["samples"]] + [(X(mm["samples"][-1][0]), Y(0))]
        rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
        od.polygon(pts, fill=rgb + (70,))
        d.line(pts[1:-1], fill=col, width=6, joint="curve")
    im.paste(Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB"))
    d = ImageDraw.Draw(im)
    # legend with the numbers that matter
    lx, ly = x0 + pw + 40, y0
    for mm, col in zip(motors, colors):
        d.rounded_rectangle((lx, ly + 8, lx + 28, ly + 36), 6, fill=col)
        d.text((lx + 44, ly), mm["designation"], font=font("ExtraBold", 40), fill=INK)
        d.text((lx, ly + 58), f"{round(mm['avgThrustN'])} N average", font=font("Regular", 30), fill=INK2)
        d.text((lx, ly + 98), f"{mm['burnTimeS']:g} s burn", font=font("Regular", 30), fill=INK2)
        d.text((lx, ly + 138), f"{round(mm['totImpulseNs'])} N·s total", font=font("SemiBold", 30), fill=INK)
        ly += 220
    if c.get("note"):
        d.text((96, H - 165), c["note"], font=font("ExtraBold", 42), fill=INK)
    # acknowledgement, in the legend column where it is readable
    d.text((lx, ly + 10), "Thrust curves courtesy of", font=font("Regular", 26), fill=INK2)
    d.text((lx, ly + 44), "thrustcurve.org", font=font("ExtraBold", 34), fill=ACCENT)
    footer(d, im, m["footer"])
    return im


def slide_ladder(c, m):
    im, d = canvas()
    heading(d, c["heading"])
    show = 7 if c.get("reveal") == "low" else 15
    hi = set(c.get("highlight", []))
    x0, y0, rung_h, gap = 190, 235, 34, 6
    maxw = W - x0 - 420
    for i, (letter, ns) in enumerate(CLASSES):
        y = y0 + i * (rung_h + gap)
        if i >= show:
            continue
        w = int(maxw * (i + 1) / 15)
        col = ACCENT if i < 7 else WARN
        if hi and letter not in hi:
            col = "#3a4657" if i < 7 else "#5e4a2c"
        d.rounded_rectangle((x0, y, x0 + w, y + rung_h), 8, fill=col)
        d.text((96, y - 4), letter, font=font("ExtraBold", 36), fill=INK if (not hi or letter in hi) else INK3)
        label = f"{ns:g} N·s" if ns < 1000 else f"{int(ns):,} N·s"
        d.text((x0 + w + 16, y + 2), label, font=font("SemiBold", 28), fill=INK2 if (not hi or letter in hi) else INK3)
    if show == 15:
        d.line((x0 - 60, y0 + 7 * (rung_h + gap) - gap / 2, W - 96, y0 + 7 * (rung_h + gap) - gap / 2),
               fill=LINE, width=3)
        d.text((W - 96 - 380, y0 + 7 * (rung_h + gap) - 40), "model rocket  ↑", font=font("SemiBold", 30), fill=ACCENT)
        d.text((W - 96 - 380, y0 + 7 * (rung_h + gap) + 6), "high power  ↓", font=font("SemiBold", 30), fill=WARN)
    if c.get("note"):
        text_block(d, (96, H - 180), c["note"], font("SemiBold", 38), INK, W - 192)
    footer(d, im, m["footer"])
    return im


def nice_step(span, target=8):
    for s in (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000):
        if span / s <= target:
            return s
    return 10000


def shared(name):
    return json.load(open(os.path.join(HERE, "shared", name), encoding="utf-8"))


def geometry():
    try:
        return shared("br1-sim.json")["geometry"]
    except (OSError, KeyError):
        return {"noseLengthM": 0.2032, "bodyLengthM": 0.9398, "bodyRadiusM": 0.041656, "finRootM": 0.09,
                "finTipM": 0.06, "finHeightM": 0.09, "finSweepM": 0.015, "finOffsetFromBottomM": 0.02,
                "motorMountLengthM": 0.1905, "totalLengthM": 1.143}


def draw_rocket(d, x0, ya, scale, g, fins=True, motor=False):
    """The BR-1 in side view, nose at x0 pointing left, to scale. Returns (x_nose_tip, x_tail)."""
    r = g["bodyRadiusM"] * scale
    nl, bl = g["noseLengthM"] * scale, g["bodyLengthM"] * scale
    xn, xb, xt = x0, x0 + nl, x0 + nl + bl
    if fins:
        root, tip, h, sw = (g[k] * scale for k in ("finRootM", "finTipM", "finHeightM", "finSweepM"))
        xr = xt - g["finOffsetFromBottomM"] * scale - root
        for sgn in (-1, 1):
            d.polygon([(xr, ya + sgn * r), (xr + sw, ya + sgn * (r + h)), (xr + sw + tip, ya + sgn * (r + h)),
                       (xr + root, ya + sgn * r)], fill="#b9b5ab", outline=INK3)
    d.rectangle((xb, ya - r, xt, ya + r), fill="#d9d7d1", outline=INK3, width=3)
    d.pieslice((xn, ya - r, xn + 2 * nl, ya + r), 90, 270, fill="#ececec", outline=INK3, width=3)
    if motor:
        ml, mr = g["motorMountLengthM"] * scale, 0.0145 * scale
        d.rectangle((xt - ml, ya - mr, xt + 4, ya + mr), fill=WARN)
    for fx in (0.35, 0.92):
        x = xb + bl * fx
        d.rectangle((x - 6, ya + r, x + 6, ya + r + 14), fill=INK3)
    return xn, xt


MARK_COLORS = {"accent": ACCENT, "warn": WARN, "ok": OK, "ink": INK, "dim": INK3}


def slide_rocket(c, m):
    """The BR-1 side view with labelled points along it. Markers: [{"label": "CG", "x": 0.70 (metres
    from the nose tip) or "frac": 0.6, "color": accent|warn|ok, "below": true, "sub": "small text"}].
    Optional "fins": false, "motor": true, "ruler": {"from": m, "to": m, "label": "1.4 calibers"}."""
    im, d = canvas()
    heading(d, c["heading"])
    g = geometry()
    scale = (W - 400) / g["totalLengthM"]
    ya = 520
    xn, xt = draw_rocket(d, 200, ya, scale, g, fins=c.get("fins", True), motor=c.get("motor", False))
    xm = lambda mk: xn + (mk["x"] if "x" in mk else mk.get("frac", 0.5) * g["totalLengthM"]) * scale
    for mk in c.get("markers", []):
        x = xm(mk); col = MARK_COLORS.get(mk.get("color", "accent"), mk.get("color", ACCENT)); rr = 22
        d.ellipse((x - rr, ya - rr, x + rr, ya + rr), fill=col, outline=BG, width=4)
        f = font("ExtraBold", 40); tw = d.textlength(mk["label"], font=f)
        if mk.get("below"):
            d.line((x, ya + rr, x, ya + 140), fill=col, width=4)
            d.text((x - tw / 2, ya + 150), mk["label"], font=f, fill=col)
            if mk.get("sub"):
                sf = font("Regular", 30); sw = d.textlength(mk["sub"], font=sf)
                d.text((x - sw / 2, ya + 205), mk["sub"], font=sf, fill=INK2)
        else:
            d.line((x, ya - rr, x, ya - 140), fill=col, width=4)
            d.text((x - tw / 2, ya - 200), mk["label"], font=f, fill=col)
            if mk.get("sub"):
                sf = font("Regular", 30); sw = d.textlength(mk["sub"], font=sf)
                d.text((x - sw / 2, ya - 245), mk["sub"], font=sf, fill=INK2)
    if c.get("ruler"):
        ru = c["ruler"]; xa, xb2 = xn + ru["from"] * scale, xn + ru["to"] * scale; yr = ya + 275
        d.line((xa, yr, xb2, yr), fill=INK, width=4)
        for x in (xa, xb2):
            d.line((x, yr - 14, x, yr + 14), fill=INK, width=4)
        f = font("SemiBold", 34); tw = d.textlength(ru["label"], font=f)
        d.text(((xa + xb2) / 2 - tw / 2, yr + 20), ru["label"], font=f, fill=INK)
    # caption and note stack up from the footer, so a wrapped line never runs into the next block
    bottom = H - 118
    if c.get("note"):
        f = font("Regular", 34)
        nh = len(wrap(d, c["note"], f, W - 192)) * int(f.size * 1.25)
        text_block(d, (96, bottom - nh), c["note"], f, INK2, W - 192)
        bottom -= nh + 14
    if c.get("caption"):
        f = font("SemiBold", 44)
        if len(wrap(d, c["caption"], f, W - 192)) > 1:
            f = font("SemiBold", 40)
        ch = len(wrap(d, c["caption"], f, W - 192)) * int(f.size * 1.25)
        text_block(d, (96, min(850, bottom - ch)), c["caption"], f, INK, W - 192)
    footer(d, im, m["footer"])
    return im


def slide_table(c, m):
    """Heading, column titles, rows of cells. Optional "widths" (relative), "highlight" (row indexes),
    "size" (cell font size, default 40), "rowHeight" (default 78), "note"."""
    im, d = canvas()
    y = heading(d, c["heading"]) + 10
    cols, rows = c["columns"], c["rows"]
    widths = c.get("widths") or [1] * len(cols)
    avail = W - 192; xs = [96]
    for w in widths:
        xs.append(xs[-1] + avail * w / sum(widths))
    hf, cf = font("SemiBold", 30), font("Regular", c.get("size", 40))
    for i, col in enumerate(cols):
        d.text((xs[i] + 16, y), col, font=hf, fill=ACCENT)
    y += 52; d.line((96, y, W - 96, y), fill=LINE, width=3); y += 16
    hi = set(c.get("highlight", [])); rh = c.get("rowHeight", 78)
    for ri, row in enumerate(rows):
        if ri in hi:
            d.rounded_rectangle((96, y - 10, W - 96, y + rh - 20), 10, fill=CARD, outline=ACCENT, width=2)
        for i, cell in enumerate(row):
            text_block(d, (xs[i] + 16, y), str(cell), cf, INK if (not hi or ri in hi) else INK2,
                       xs[i + 1] - xs[i] - 32, gap=1.1)
        y += rh
    if c.get("note"):
        text_block(d, (96, H - 190), c["note"], font("Regular", 34), INK2, W - 192)
    footer(d, im, m["footer"])
    return im


def slide_figure(c, m):
    """One large image (a diagram or photo from the segment folder) with an optional heading, caption
    and credit."""
    im, d = canvas()
    y = heading(d, c["heading"]) if c.get("heading") else 96
    img = Image.open(os.path.join(c.get("_dir", ""), c["image"])).convert("RGB")
    box_w = W - 192
    box_h = H - y - (270 if c.get("caption") else 150)
    img.thumbnail((box_w, box_h))
    px, py = 96 + (box_w - img.width) // 2, y + 10
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), 28, fill=255)
    im.paste(img, (px, py), mask)
    if c.get("caption"):
        text_block(d, (96, py + img.height + 28), c["caption"], font("SemiBold", 40), INK, W - 192)
    if c.get("credit"):
        d.text((96, H - 118), c["credit"], font=font("Regular", 22), fill=INK3)
    footer(d, im, m["footer"])
    return im


CODE_COLORS = [ACCENT, WARN, OK, "#c48be0", INK2]


def slide_code(c, m):
    """A motor designation broken into its parts. "parts": [{"text": "G", "label": "impulse class",
    "sub": "the letter ladder"}, ...]; a part without a label is drawn dim (the dash, say)."""
    im, d = canvas()
    heading(d, c["heading"])
    parts = c["parts"]; f = font("ExtraBold", 230); yb = 270
    x = (W - sum(d.textlength(p["text"], font=f) for p in parts)) / 2
    placed, k = [], 0
    for p in parts:
        tw = d.textlength(p["text"], font=f)
        col = CODE_COLORS[k % len(CODE_COLORS)] if p.get("label") else INK3
        d.text((x, yb), p["text"], font=f, fill=col)
        if p.get("label"):
            placed.append((x + tw / 2, col, p)); k += 1
        x += tw
    slot = (W - 192) / max(len(placed), 1)
    for i, (cx, col, p) in enumerate(placed):
        lx = 96 + slot * i + slot / 2
        d.ellipse((cx - 9, yb + 284, cx + 9, yb + 302), fill=col)
        d.line((cx, yb + 293, lx, 690), fill=col, width=4)
        lf = font("ExtraBold", 40); tw = d.textlength(p["label"], font=lf)
        d.text((lx - tw / 2, 705), p["label"], font=lf, fill=col)
        if p.get("sub"):
            text_block(d, (lx - slot / 2 + 20, 762), p["sub"], font("Regular", 32), INK2, slot - 40, align="center")
    if c.get("note"):
        text_block(d, (96, H - 190), c["note"], font("Regular", 34), INK2, W - 192)
    footer(d, im, m["footer"])
    return im


FT, MPH, IN = 3.28084, 2.23694, 39.3701          # metres to feet, m/s to mph, metres to inches
US_UNITS = {"altitudeM": (FT, "altitude, feet"), "lateralM": (FT, "distance from the pad, feet"),
            "speedMs": (MPH, "speed, miles per hour"), "accelMs2": (FT, "acceleration, ft/s²"),
            "cgM": (IN, "CG, inches from the nose tip"), "cpM": (IN, "CP, inches from the nose tip"),
            "marginCal": (1.0, "stability margin, calibers"), "stabilityCal": (1.0, "stability, calibers"),
            "thrustN": (1.0, "thrust, Newtons"), "massKg": (35.274, "mass, ounces")}
EVENT_NAMES = {"launchrod": "off the rail", "burnout": "burnout", "ejectioncharge": "ejection",
               "apogee": "apogee", "groundhit": "landing"}


def slide_flight(c, m):
    """A line from the BR-1's stored OpenRocket flight (shared/br1-sim.json): "y" is a series key
    (altitudeM, speedMs, massKg, cgM, cpM, stabilityCal, thrustN), default altitudeM. "sim" picks the
    simulation (default 0). "tmax" clips time. "events" lists which flight events to dot and label.
    "mark": {"t": 14.1, "label": "..."} draws one extra vertical line. "summary": false hides the
    numbers column. "ymin" sets the axis floor (default 0), for a series like marginCal that never nears zero."""
    im, d = canvas()
    heading(d, c["heading"])
    if c.get("caption"):
        text_block(d, (96, 222), c["caption"], font("SemiBold", 36), INK2, W - 192)
    sim = shared("br1-sim.json")["simulations"][c.get("sim", 0)]
    key = c.get("y", "altitudeM")
    apogee = next((e["time"] for e in sim["events"] if e["type"] == "apogee"), 10)
    tmax = c.get("tmax") or apogee * 1.6
    # US units on screen, the way the program's OpenRocket is set: feet, miles per hour, calibers
    conv, ylabel = US_UNITS.get(key, (1.0, key))
    pts = [(r["t"], r[key] * conv) for r in sim["series"] if r["t"] <= tmax and r.get(key) is not None]
    ymin = c.get("ymin", min(0, min(v for _, v in pts))); ymax = max(v for _, v in pts) * 1.12 or 1   # "ymin" lifts the axis floor
    x0, y0, pw, ph = 190, 380, 1300, 470
    X = lambda t: x0 + t / tmax * pw
    Y = lambda v: y0 + ph - (v - ymin) / (ymax - ymin) * ph
    ys, ts = nice_step(ymax - ymin), nice_step(tmax)
    k = ymin
    while k <= ymax:
        d.line((x0, Y(k), x0 + pw, Y(k)), fill="#22262f", width=2)
        d.text((x0 - 90, Y(k) - 16), f"{k:g}", font=font("Regular", 26), fill=INK3); k += ys
    k = 0
    while k <= tmax:
        d.text((X(k) - 10, y0 + ph + 12), f"{k:g}", font=font("Regular", 26), fill=INK3); k += ts
    d.line((x0, Y(0), x0 + pw, Y(0)), fill=INK3, width=4)
    d.line((x0, y0, x0, y0 + ph), fill=INK3, width=4)
    d.text((x0 + pw - 170, y0 + ph + 46), "time, seconds", font=font("SemiBold", 28), fill=INK3)
    d.text((x0 + 12, y0 - 40), c.get("ylabel", ylabel), font=font("SemiBold", 28), fill=INK3)
    d.line([(X(t), Y(v)) for t, v in pts], fill=ACCENT, width=6, joint="curve")
    val = lambda t: min(pts, key=lambda p: abs(p[0] - t))[1]
    placed = []      # (x, y) of labels already drawn, to stagger near-coincident events
    for e in sim["events"]:
        if e["type"] in c.get("events", ["burnout", "apogee", "ejectioncharge"]) and e["time"] <= tmax:
            x, y = X(e["time"]), Y(val(e["time"]))
            d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=WARN, outline=BG, width=3)
            lab = f"{EVENT_NAMES.get(e['type'], e['type'])}  {e['time']:.1f} s"
            lf = font("SemiBold", 30); tw = d.textlength(lab, font=lf)
            ly = y - 48
            while any(abs(px - x) < tw + 30 and abs(py - ly) < 40 for px, py in placed):
                ly += 44           # slide the label down until it is clear
            lx = min(x + 18, x0 + pw - tw)
            d.text((lx, ly), lab, font=lf, fill=WARN); placed.append((lx, ly))
    if c.get("mark"):
        mk = c["mark"]; x = X(mk["t"])
        for yy in range(int(y0), int(y0 + ph), 24):
            d.line((x, yy, x, yy + 12), fill=OK, width=4)
        lf = font("SemiBold", 30); tw = d.textlength(mk["label"], font=lf)
        lx = x + 14 if x + 14 + tw <= x0 + pw else x - 14 - tw
        d.text((lx, y0 + ph - 60), mk["label"], font=lf, fill=OK)
    if c.get("summary", True):
        s = sim["summary"]; lx, ly = x0 + pw + 40, y0
        for lab, v in (("apogee", f"{s['maxaltitude'] * FT:,.0f} ft ({s['maxaltitude']:.0f} m)"), ("top speed", f"{s['maxvelocity'] * MPH:.0f} mph ({s['maxvelocity']:.0f} m/s)"),
                       ("off the rail", f"{s['launchrodvelocity'] * FT:.0f} ft/s ({s['launchrodvelocity']:.1f} m/s)"), ("to apogee", f"{s['timetoapogee']:.1f} s"),
                       ("best delay", f"{s['optimumdelay']:.1f} s")):
            d.text((lx, ly), lab, font=font("Regular", 28), fill=INK2)
            d.text((lx, ly + 34), v, font=font("ExtraBold", 32), fill=INK); ly += 96
        mname = sim['motor'].replace('HP-', '')
        d.text((lx, ly + 10), f"OpenRocket, BR-1 on {'an' if mname[0] in 'AEFHILMNOSX' else 'a'} {mname}", font=font("Regular", 24), fill=INK3)
    if c.get("note"):
        d.text((96, H - 165), c["note"], font=font("ExtraBold", 42), fill=INK)
    footer(d, im, m["footer"])
    return im


def slide_compare(c, m):
    im, d = canvas()
    heading(d, c["heading"])
    sq, g = 52, 10
    # left: one square
    lx, ly = 260, 420
    d.rounded_rectangle((lx, ly, lx + sq, ly + sq), 6, fill=ACCENT)
    text_block(d, (140, ly + 120), c["left"], font("SemiBold", 40), INK, 460)
    # right: 8x8 grid
    rx, ry = 820, 300
    for r in range(8):
        for q in range(8):
            x = rx + q * (sq + g); y = ry + r * (sq + g)
            d.rounded_rectangle((x, y, x + sq, y + sq), 6, fill=WARN)
    text_block(d, (rx, ry + 8 * (sq + g) + 40), c["right"], font("SemiBold", 40), INK, 620)
    d.text((rx + 8 * (sq + g) + 60, ry + 180), "× 64", font=font("ExtraBold", 110), fill=INK)
    if c.get("note"):
        text_block(d, (rx + 8 * (sq + g) + 60, ry + 330), c["note"], font("Regular", 34), INK2, 420)
    footer(d, im, m["footer"])
    return im


SLIDES = {"title": slide_title, "text": slide_text, "close": slide_close, "answer": slide_answer,
          "photo": slide_photo, "curves": slide_curves, "ladder": slide_ladder, "compare": slide_compare,
          "rocket": slide_rocket, "table": slide_table, "figure": slide_figure, "code": slide_code,
          "flight": slide_flight, "clip": slide_clip}
BASE_SLIDES = dict(SLIDES)


def load_plugin(sdir):
    """Reset to the built-in slide types, then let SNN/slides.py add its own."""
    SLIDES.clear(); SLIDES.update(BASE_SLIDES)
    p = os.path.join(sdir, "slides.py")
    if os.path.exists(p):
        import importlib.util
        spec = importlib.util.spec_from_file_location("slides_" + os.path.basename(sdir), p)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        mod.register(sys.modules[__name__])


# ---------------------------------------------------------------- audio

def wav_seconds(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


# Spellings the voices get wrong. Applied to the TTS input only; slide text and the human reading
# script keep the real spelling. Whole tokens only, longest first. A segment adds its own with
# "say_fixes": [["from", "to"], ...] in its cues.json meta; those are applied first.
SAY_FIXES = [("Alpha III", "Alpha Three"), ("BR-1", "B R one"), ("N·s", "Newton-seconds"),
             ("H128W-14", "H one twenty-eight W, fourteen"), ("H115DM-14", "H one fifteen D M, fourteen"),
             ("H135W-8", "H one thirty-five W, eight"), ("G74W-6", "G seventy-four W, six"), ("A8-3", "A eight, three"),
             ("G74W", "G seventy-four W"), ("G12ST", "G twelve S T"), ("G40W", "G forty W"), ("H128W", "H one twenty-eight W"),
             ("H115DM", "H one fifteen D M"), ("H135W", "H one thirty-five W"), ("H180W", "H one eighty W"),
             ("A8", "A eight"), ("G74", "G seventy-four"), ("G12", "G twelve"), ("G40", "G forty"),
             ("H128", "H one twenty-eight"), ("H115", "H one fifteen"), ("H135", "H one thirty-five"), ("H180", "H one eighty"),
             ("APCP", "A P C P"), ("NFPA", "N F P A"), ("RSO", "R S O"), ("LCO", "L C O"), ("NAR", "nar"),
             ("FAA", "F A A"), ("CG", "C G"), ("CP", "C P"), ("L1", "Level one"), ("L2", "Level two"), ("L3", "Level three"),
             (".ork", "dot ork"), ("BR-1.ork", "B R one dot ork")]
_meta_fixes = []


def speakable(text):
    for a, b in list(_meta_fixes) + SAY_FIXES:
        text = re.sub(r"(?<![A-Za-z0-9])" + re.escape(a) + r"(?![A-Za-z0-9])", b, text)
    return text


_voice = None
def tts_piper(text, out):
    global _voice
    if _voice is None:
        from piper import PiperVoice
        vp = os.environ.get("PIPER_VOICE") or sys.exit("PIPER_VOICE not set and no recorded wav for a cue")
        _voice = PiperVoice.load(vp)
    with wave.open(out, "wb") as w:
        _voice.synthesize_wav(speakable(text), w)


def tts_eleven(text, out, ff):
    key = os.environ["ELEVEN_LABS_API_KEY"]
    voice = voice_id()
    model = os.environ.get("ELEVEN_LABS_MODEL", "eleven_multilingual_v2")
    body = json.dumps({"text": speakable(text), "model_id": model,
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0,
                                          "use_speaker_boost": True}}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
        data=body, headers={"xi-api-key": key, "Content-Type": "application/json"})
    for attempt in range(6):
        try:
            mp3 = urllib.request.urlopen(req, timeout=60).read()
            break
        except urllib.error.HTTPError as e:
            sys.exit(f"ElevenLabs error {e.code}: {e.read()[:300]}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            # TLS handshakes time out now and then on some networks; a retry almost always goes through
            if attempt == 5:
                sys.exit(f"ElevenLabs unreachable after 6 tries: {e}")
            print(f"  ElevenLabs: {e}; retrying", file=sys.stderr)
            import time; time.sleep(3 * (attempt + 1))
    tmp = out + ".mp3"
    open(tmp, "wb").write(mp3)
    run(ff, "-y", "-v", "error", "-i", tmp, "-ar", "44100", "-ac", "1", out)
    os.remove(tmp)


def tts(text, out, ff):
    if engine() == "eleven":
        tts_eleven(text, out, ff)
    else:
        tts_piper(text, out)


def tts_cache_key(text):
    if engine() == "eleven":
        tag = "el_" + voice_id()[:6] + "_" + os.environ.get("ELEVEN_LABS_MODEL", "eleven_multilingual_v2")
    else:
        tag = "piper"
    return hashlib.sha1((tag + "|" + speakable(text)).encode()).hexdigest()[:10]


def silence(ff, seconds, out):
    run(ff, "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{seconds}", out)


def chime(ff, out):
    run(ff, "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=880:duration=1.0",
        "-af", "afade=t=in:d=0.02,afade=t=out:st=0.35:d=0.6,volume=0.4", "-ar", "48000", out)


def fingerprint(sdir):
    h = hashlib.sha1()
    files = [os.path.join(sdir, "cues.json"), os.path.abspath(__file__)]
    if os.path.exists(os.path.join(sdir, "slides.py")):
        files.append(os.path.join(sdir, "slides.py"))
    for d in (os.path.join(sdir, "assets"), os.path.join(sdir, "narration"), os.path.join(sdir, "voice"),
              os.path.join(HERE, "shared")):
        if os.path.isdir(d):
            files += sorted(os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))
    for f in files:
        h.update(os.path.relpath(f, ROOT).encode()); h.update(open(f, "rb").read())
    return h.hexdigest()


def to_wav(ff, src, dst):
    if not os.path.exists(dst):
        run(ff, "-y", "-v", "error", "-i", src, "-ar", "44100", "-ac", "1", dst)
    return dst


def narration_for(sdir, work, n, text, ff):
    """Return a wav path for cue n, synthesizing (and saving to narration/) only when needed."""
    rec = os.path.join(sdir, "voice", f"{n:02d}.wav")
    if os.path.exists(rec):
        return rec
    ndir = os.path.join(sdir, "narration"); os.makedirs(ndir, exist_ok=True)
    h = tts_cache_key(text)
    mp3 = os.path.join(ndir, f"{n:02d}-{h}.mp3")
    if not os.path.exists(mp3):
        legacy = os.path.join(work, f"tts_{n:02d}_{h}.wav")
        if os.path.exists(legacy):
            run(ff, "-y", "-v", "error", "-i", legacy, "-b:a", "96k", mp3)
        else:
            tmp = os.path.join(work, f"new_{n:02d}.wav")
            tts(text, tmp, ff)
            run(ff, "-y", "-v", "error", "-i", tmp, "-b:a", "96k", mp3)
        # drop stale narration for this cue (old wording or old voice)
        for f in os.listdir(ndir):
            if f.startswith(f"{n:02d}-") and f != os.path.basename(mp3):
                os.remove(os.path.join(ndir, f))
    return to_wav(ff, mp3, os.path.join(work, f"nar_{n:02d}_{h}.wav"))


GUIDE_URL = "https://blinksoft.github.io/minerva-br1-instructions/"
CHANNEL_URL = "https://www.youtube.com/@GAWingAEO"
REPO_URL = "https://github.com/blinksoft/minerva-br1-instructions"


def upload_kit(seg, meta, cues, sdir, outdir):
    """Everything the YouTube Studio upload form asks for, plus a 1280x720 thumbnail."""
    num = int(re.sub(r"\D", "", seg) or 0)
    title = f"{meta['title']} — BR-1 Build Day, Segment {num}"
    pause = next((c["question"] for c in cues if c["type"] == "pause"), None)
    desc = [meta.get("description", ""), "",
            f"Segment {num} of the \"While the epoxy cures\" series for the Georgia Wing High Power Rocketry "
            f"Minerva BR-1 build day (Civil Air Patrol). Each segment is 3 to 5 minutes and fills an epoxy "
            f"cure wait during the build.", ""]
    if pause:
        desc += ["Pause card: when the countdown appears, instructors pause, ask the room, then press play "
                 f"for the answer. This segment asks: {pause}", ""]
    desc += [f"Assembly guide: {GUIDE_URL}", f"Curriculum and scripts: {REPO_URL}/tree/main/curriculum", "",
             "Narration is synthesized (ElevenLabs) from the program's script. Slides are generated from the "
             "curriculum source in the guide's repository.", ""]
    for c in meta.get("credits", []):
        desc.append(c)
    kit = [f"# YouTube upload kit — {seg}", "",
           f"Channel: GA Wing AeroSpace and STEM Education, {CHANNEL_URL}", "Playlist: BR-1 Build Day (unlisted)", "Visibility: Unlisted",
           "Audience: not made for kids (it is instructional for a mixed-age class; leave 'made for kids' off "
           "so captions, comments and playlists behave normally)",
           f"Video file: videos/{seg}.mp4", f"Captions file: videos/{seg}.srt (Subtitles > Upload file > With timing)",
           f"Thumbnail: videos/{seg}-thumb.jpg", "",
           "## Title", "", title, "", "## Description", ""] + desc + ["", "## Tags", "", ", ".join(meta.get("tags", [])), "",
           "## After uploading", "", f"Paste the video ID into curriculum/production.md, row {seg}."]
    open(os.path.join(outdir, f"{seg}.youtube.md"), "w", encoding="utf-8").write("\n".join(kit) + "\n")
    slide = os.path.join(sdir, "slides", "01-title.png")
    if os.path.exists(slide):
        Image.open(slide).convert("RGB").resize((1280, 720), Image.LANCZOS).save(
            os.path.join(outdir, f"{seg}-thumb.jpg"), quality=88)


# ---------------------------------------------------------------- build

def build(seg, script_only=False, force=False, slides_only=False):
    sdir = os.path.join(HERE, seg)
    spec = json.load(open(os.path.join(sdir, "cues.json"), encoding="utf-8"))
    meta = spec["meta"]
    cues = spec["cues"]
    global _meta_voice, _seg_number, _meta_fixes
    _meta_voice = meta.get("voice")
    _meta_fixes = [tuple(x) for x in meta.get("say_fixes", [])]
    _seg_number = int(re.sub(r"\D", "", seg) or 0)
    load_plugin(sdir)
    work = os.path.join(HERE, "out", "work", seg)
    outdir = VIDEOS
    os.makedirs(work, exist_ok=True); os.makedirs(outdir, exist_ok=True)

    # script.md for whoever records the real voice
    lines = [f"# {seg} — {meta['title']}: narration script", "",
             "Record one file per numbered cue, as `voice/NN.wav` (any sample rate, mono is fine).",
             "Leave a beat of silence at the start and end of each. Re-run render.py and the slides",
             "re-time themselves to your voice.", ""]
    n = 0
    for c in cues:
        if c["type"] == "pause":
            lines += [f"**{n+1:02d} — pause card, no narration.** The card reads: _{c['question']}_", ""]
            n += 1; continue
        n += 1
        lines += [f"**{n:02d}** `voice/{n:02d}.wav`", "", c["say"], ""]
    open(os.path.join(sdir, "script.md"), "w", encoding="utf-8").write("\n".join(lines))
    if script_only:
        print("wrote", os.path.join(sdir, "script.md")); return

    if slides_only:
        slides = os.path.join(sdir, "slides")
        if os.path.isdir(slides):
            for f in os.listdir(slides):
                os.remove(os.path.join(slides, f))
        os.makedirs(slides, exist_ok=True)
        n = 0
        for c in cues:
            n += 1
            if c["type"] == "pause":
                slide_pause(c, meta, 5).save(os.path.join(slides, f"{n:02d}-pause.png")); continue
            c["_dir"] = sdir
            SLIDES[c["type"]](c, meta).save(os.path.join(slides, f"{n:02d}-{c['type']}.png"))
        words = sum(len(c.get("say", "").split()) for c in cues)
        longest = max((len(c.get("say", "").split()) for c in cues), default=0)
        print(f"{seg}: {n} slides written to {os.path.relpath(slides, ROOT)}; {words} narration words "
              f"(about {words / 150 + 5 / 60 + 0.7 * n / 60:.1f} min), longest cue {longest} words")
        return

    ff = ffmpeg()
    # make sure every cue's narration exists (synthesizes only what is missing), then fingerprint
    n = 0
    for c in cues:
        n += 1
        if c["type"] != "pause":
            narration_for(sdir, work, n, c["say"], ff)
    fp = fingerprint(sdir)
    sha_path = os.path.join(outdir, f"{seg}.sha")
    out_mp4 = os.path.join(outdir, f"{seg}.mp4")
    if not force and os.path.exists(out_mp4) and os.path.exists(sha_path) and open(sha_path).read().strip() == fp:
        print(f"{seg}: unchanged, skipped"); return

    slides = os.path.join(sdir, "slides")
    if os.path.isdir(slides):
        for f in os.listdir(slides):
            os.remove(os.path.join(slides, f))
    os.makedirs(slides, exist_ok=True)
    segs, srt, t = [], [], 0.0
    n = 0
    for c in cues:
        n += 1
        if c["type"] == "pause":
            sil = os.path.join(work, "sil1.wav"); ch = os.path.join(work, "chime.wav")
            if not os.path.exists(sil): silence(ff, 1.0, sil)
            if not os.path.exists(ch): chime(ff, ch)
            for k in range(5, 0, -1):
                png = os.path.join(work, f"{n:02d}_{k}.png")
                img = slide_pause(c, meta, k); img.save(png)
                if k == 5:
                    img.save(os.path.join(slides, f"{n:02d}-pause.png"))
                aud = ch if k == 1 else sil
                seg_mp4 = os.path.join(work, f"{n:02d}_{k}.mp4")
                encode(ff, png, aud, 1.0, seg_mp4); segs.append(seg_mp4)
            srt.append((t, t + 5.0, "[Pause card: " + c["question"] + "]")); t += 5.0
            continue
        png = os.path.join(work, f"{n:02d}.png")
        c["_dir"] = sdir
        img = SLIDES[c["type"]](c, meta); img.save(png)
        img.save(os.path.join(slides, f"{n:02d}-{c['type']}.png"))
        aud = narration_for(sdir, work, n, c["say"], ff)
        dur = max(float(c.get("min", 0)), wav_seconds(aud) + PAD_AFTER)
        seg_mp4 = os.path.join(work, f"{n:02d}.mp4")
        if c["type"] == "clip":
            encode_clip(ff, png, os.path.join(sdir, c["src"]), aud, dur, seg_mp4, c)
        else:
            encode(ff, png, aud, dur, seg_mp4)
        segs.append(seg_mp4)
        srt.append((t, t + dur, c["say"])); t += dur

    lst = os.path.join(work, "concat.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
    run(ff, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out_mp4)
    write_srt(srt, os.path.join(outdir, f"{seg}.srt"))
    open(sha_path, "w").write(fp + "\n")
    upload_kit(seg, meta, cues, sdir, outdir)
    print(f"{out_mp4}  {t/60:.1f} min, {len(cues)} cues, narration: {engine()}" + (f" ({[k for k,v in VOICES.items() if v == voice_id()] or [voice_id()]})" if engine() == "eleven" else ""))


def encode(ff, png, aud, dur, out):
    run(ff, "-y", "-v", "error",
        "-loop", "1", "-framerate", str(FPS), "-i", png,
        "-i", aud,
        "-af", "apad,aresample=48000", "-ac", "2",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
        "-t", f"{dur:.3f}", "-r", str(FPS), out)


def encode_clip(ff, plate, src, aud, dur, out, c):
    """Overlay a screen-recording clip on its plate for exactly dur seconds. The narration sets the
    length: with fit "hold" (default) the clip's last frame stays up when the narration runs longer
    and the clip's tail is dropped when it runs shorter; "stretch" retimes the clip to end with the
    narration. The clip's own audio is not used."""
    crop = c.get("crop")
    frame = first_frame(src, crop)
    x, y, w, h = clip_placement(frame.size)
    clip_len = media_seconds(ff, src)
    vf = [f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}"] if crop else []
    if c.get("fit") == "stretch" and clip_len > 0:
        vf.append(f"setpts=PTS*{dur / clip_len:.5f}")
    vf += [f"fps={FPS}", f"scale={w}:{h}:flags=lanczos"]
    graph = f"[1:v]{','.join(vf)}[v];[0:v][v]overlay={x}:{y}:eof_action=repeat:format=auto[out]"
    run(ff, "-y", "-v", "error",
        "-loop", "1", "-framerate", str(FPS), "-i", plate,
        "-i", src,
        "-i", aud,
        "-filter_complex", graph, "-map", "[out]", "-map", "2:a",
        "-af", "apad,aresample=48000", "-ac", "2",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
        "-t", f"{dur:.3f}", "-r", str(FPS), out)


def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"


def write_srt(entries, path):
    out = []
    for i, (a, b, txt) in enumerate(entries, 1):
        out += [str(i), f"{ts(a)} --> {ts(b)}", txt, ""]
    open(path, "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    targets = args
    if args[0] == "all":
        targets = sorted(d for d in os.listdir(HERE) if re.fullmatch(r"S\d+", d) and os.path.exists(os.path.join(HERE, d, "cues.json")))
    for seg in targets:
        build(seg, script_only="--script" in sys.argv, force="--force" in sys.argv, slides_only="--slides" in sys.argv)
