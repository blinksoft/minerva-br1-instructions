#!/usr/bin/env python3
"""Render a curriculum segment video from its cue list.

    python3 render.py S06            # build videos/S06.mp4 (+ .srt), refresh S06/script.md
    python3 render.py all            # every SNN folder; unchanged segments are skipped
    python3 render.py S06 --force    # rebuild even if nothing changed
    python3 render.py S06 --script   # only regenerate S06/script.md for recording

Each cue in SNN/cues.json is one slide plus one line of narration. Narration audio is looked up in
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
    im, d = canvas()
    d.text((96, 110), "ANSWER", font=font("ExtraBold", 40), fill=OK)
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
    for k in range(0, int(fmax) + 1, 20):
        d.line((x0, Y(k), x0 + pw, Y(k)), fill="#22262f", width=2)
        d.text((x0 - 70, Y(k) - 16), f"{k}", font=font("Regular", 26), fill=INK3)
    for k in range(0, int(tmax) + 1, 2):
        d.text((X(k) - 10, y0 + ph + 12), f"{k}", font=font("Regular", 26), fill=INK3)
    d.line((x0, y0 + ph, x0 + pw, y0 + ph), fill=INK3, width=4)
    d.line((x0, y0, x0, y0 + ph), fill=INK3, width=4)
    d.text((x0 + pw - 170, y0 + ph + 46), "time, seconds", font=font("SemiBold", 28), fill=INK3)
    d.text((x0 + 12, y0 - 40), "thrust, Newtons", font=font("SemiBold", 28), fill=INK3)
    colors = [ACCENT, WARN]
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
          "photo": slide_photo, "curves": slide_curves, "ladder": slide_ladder, "compare": slide_compare}


# ---------------------------------------------------------------- audio

def wav_seconds(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


# Spellings the placeholder voice gets wrong. Applied to the TTS input only; slide text and the
# human reading script keep the real spelling.
SAY_FIXES = [("Alpha III", "Alpha Three"), ("BR-1", "B R one"), ("N·s", "Newton-seconds"),
             ("G74W", "G seventy-four W"), ("G12ST", "G twelve S T"), ("A8", "A eight"), ("G74", "G seventy-four"),
             ("G12", "G twelve")]


def speakable(text):
    for a, b in SAY_FIXES:
        text = text.replace(a, b)
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
    for attempt in range(4):
        try:
            mp3 = urllib.request.urlopen(req, timeout=120).read()
            break
        except urllib.error.HTTPError as e:
            sys.exit(f"ElevenLabs error {e.code}: {e.read()[:300]}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt == 3:
                sys.exit(f"ElevenLabs unreachable after 4 tries: {e}")
            import time; time.sleep(5 * (attempt + 1))
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
    for sub in ("assets", "narration", "voice"):
        d = os.path.join(sdir, sub)
        if os.path.isdir(d):
            files += sorted(os.path.join(d, f) for f in os.listdir(d))
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
           f"Channel: {CHANNEL_URL}", "Playlist: BR-1 Build Day (unlisted)", "Visibility: Unlisted",
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

def build(seg, script_only=False, force=False):
    sdir = os.path.join(HERE, seg)
    spec = json.load(open(os.path.join(sdir, "cues.json"), encoding="utf-8"))
    meta = spec["meta"]
    cues = spec["cues"]
    global _meta_voice, _seg_number
    _meta_voice = meta.get("voice")
    _seg_number = int(re.sub(r"\D", "", seg) or 0)
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

    ff = ffmpeg()
    # make sure every cue's narration exists (synthesizes only what is missing), then fingerprint
    n = 0
    for c in cues:
        n += 1
        if c["type"] != "pause":
            narration_for(sdir, work, n, c["say"], ff)
    fp = fingerprint(sdir)
    upload_kit(seg, meta, cues, sdir, outdir)
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
        encode(ff, png, aud, dur, seg_mp4); segs.append(seg_mp4)
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
        build(seg, script_only="--script" in sys.argv, force="--force" in sys.argv)
