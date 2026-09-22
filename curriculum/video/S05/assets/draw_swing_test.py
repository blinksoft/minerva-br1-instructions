"""Draw swing-test.png: the swing test seen from above, plus the two verdicts. Run from anywhere:
    .venv/bin/python curriculum/video/S05/assets/draw_swing_test.py
Renderer palette and Inter fonts, 1728 px wide, no software screenshots, nothing downloaded."""
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "..", "fonts")
BG, INK, INK2, INK3 = "#14151a", "#e9e8e4", "#adaba4", "#807d76"
ACCENT, WARN, OK, CARD, LINE = "#7fb0ee", "#e0a35a", "#5cc27f", "#1c1e25", "#31353f"
W, H = 1728, 600


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"Inter-{weight}.ttf"), size)


def rocket(L, r, cg_dot=True):
    """A small BR-1, nose pointing right, on a transparent layer. Returns (layer, (cg_x, cg_y))."""
    nl, fh, fr = int(L * 0.18), int(r * 1.6), int(L * 0.16)
    pad = fh + 10
    im = Image.new("RGBA", (L + 2 * pad, 2 * (r + pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, ya = pad, r + pad
    xt, xb = x0, x0 + L - nl                      # tail, base of nose
    for sgn in (-1, 1):                           # fins, swept back
        d.polygon([(xt + 6, ya + sgn * r), (xt + 6 + fr, ya + sgn * r), (xt + 6 + fr - int(fr * 0.4), ya + sgn * (r + fh)),
                   (xt - int(fr * 0.2), ya + sgn * (r + fh))], fill="#b9b5ab", outline=INK3)
    d.rectangle((xt, ya - r, xb, ya + r), fill="#d9d7d1", outline=INK3, width=2)
    d.pieslice((xb - nl, ya - r, xb + nl, ya + r), -90, 90, fill="#ececec", outline=INK3, width=2)
    d.rectangle((xt - 4, ya - int(r * 0.45), xt + int(L * 0.16), ya + int(r * 0.45)), fill=WARN)   # motor
    cg = (xt + int((L) * (1 - 0.61)), ya)           # CG is 61 % of the way back from the nose tip
    if cg_dot:
        rr = max(6, r // 2)
        d.ellipse((cg[0] - rr, cg[1] - rr, cg[0] + rr, cg[1] + rr), fill=ACCENT, outline=BG, width=2)
    return im, cg


def arrow(d, p, q, col, w=5, head=18):
    d.line((p, q), fill=col, width=w)
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    for s in (-1, 1):
        a = ang + math.pi + s * 0.5
        d.line((q, (q[0] + head * math.cos(a), q[1] + head * math.sin(a))), fill=col, width=w)


im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)

# ---- left: the swing seen from above
cx, cy, rx, ry = 500, 250, 380, 150
n = 72                                                # dashed ellipse, the path of the rocket
for i in range(0, n, 2):
    a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
    d.line(((cx + rx * math.cos(a0), cy + ry * math.sin(a0)), (cx + rx * math.cos(a1), cy + ry * math.sin(a1))), fill=INK3, width=4)
d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=INK2)             # you, in the middle
f = font("Regular", 26); lab = "you, turning in place"
d.text((cx - 30 - d.textlength(lab, font=f), cy - 14), lab, font=f, fill=INK2)

lay, cg = rocket(340, 24)                                              # rocket on the near side of the path
px, py = cx - cg[0], cy + ry - cg[1]
d.line(((cx, cy), (cx, cy + ry)), fill=INK, width=3)                   # the string, centre to CG
im.paste(lay, (px, py), lay)
d.text((cx + 20, cy + ry - 100), "string tied at the CG", font=font("SemiBold", 28), fill=ACCENT)
tail_x = px + (lay.width - 340) // 2
d.text((tail_x - 60, cy + ry + 74), "motor loaded", font=font("Regular", 26), fill=WARN)
nose_x = tail_x + 340
arrow(d, (nose_x + 24, cy + ry), (nose_x + 150, cy + ry - 22), OK, w=6, head=22)
d.text((nose_x + 40, cy + ry + 8), "nose leads", font=font("SemiBold", 28), fill=OK)
d.text((40, 40), "Swing it in a circle overhead", font=font("SemiBold", 34), fill=INK)
d.text((40, 84), "seen from above", font=font("Regular", 26), fill=INK3)

# ---- right: the two verdicts
def card(y, verdict, col, note, angle):
    x0, x1 = 1060, 1700
    d.rounded_rectangle((x0, y, x1, y + 250), 22, fill=CARD, outline=LINE, width=2)
    d.text((x0 + 36, y + 22), verdict, font=font("ExtraBold", 40), fill=col)
    lay, _ = rocket(150, 12)
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    im.paste(lay, (x0 + 140 - lay.width // 2, y + 160 - lay.height // 2), lay)
    arrow(d, (x0 + 280, y + 100), (x0 + 420, y + 100), INK3, w=4, head=14)
    d.text((x0 + 434, y + 86), "direction of travel", font=font("Regular", 22), fill=INK3)
    yy = y + 132
    for ln in note:
        d.text((x0 + 280, yy), ln, font=font("Regular", 26), fill=INK2); yy += 34

card(40, "GO", OK, ["Nose forward and steady,", "all the way round"], 0)
card(320, "DO NOT LAUNCH", WARN, ["Sideways or backwards:", "the CG is too far back"], 90)

im.save(os.path.join(HERE, "swing-test.png"))
print("wrote swing-test.png", im.size)
