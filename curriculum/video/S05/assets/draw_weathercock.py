#!/usr/bin/env python3
"""Draw weathercock.png: two rockets in the same crosswind. One is far too stable and turns hard into
the wind, flying sideways; one has a sensible margin and flies nearly straight up. Our own drawing.

    python3 curriculum/video/S05/assets/draw_weathercock.py
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(os.path.dirname(HERE))
BG, INK, INK2, INK3, WARN, OK, CARD, LINE = "#14151a", "#e9e8e4", "#adaba4", "#807d76", "#e0a35a", "#5cc27f", "#1c1e25", "#31353f"
def font(w, s): return ImageFont.truetype(os.path.join(VIDEO, "fonts", f"Inter-{w}.ttf"), s)

W, H = 1000, 790
im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
d.rectangle((0, 730, W, H), fill=CARD); d.line((0, 730, W, 730), fill=LINE, width=3)

def sprite(col):
    """A small rocket, nose up, on a transparent canvas."""
    s = Image.new("RGBA", (90, 220), (0, 0, 0, 0)); g = ImageDraw.Draw(s)
    g.polygon([(45, 0), (31, 52), (59, 52)], fill="#ececec", outline=INK3)
    g.rectangle((31, 52, 59, 190), fill="#d9d7d1", outline=INK3)
    g.polygon([(31, 150), (5, 205), (31, 190)], fill=col, outline=INK3)
    g.polygon([(59, 150), (85, 205), (59, 190)], fill=col, outline=INK3)
    g.rectangle((38, 190, 52, 218), fill=WARN)
    return s

def path(fx, fy, n=400):
    return [(fx(i / n), fy(i / n)) for i in range(n + 1)]

def dashed(pts, col, dash=22, gap=14):
    acc, on = 0.0, True; seg = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        acc += math.hypot(x1 - x0, y1 - y0); seg.append((x1, y1))
        if acc >= (dash if on else gap):
            if on: d.line(seg, fill=col, width=6)
            seg, acc, on = [(x1, y1)], 0.0, not on

def place(pts, t, col):
    i = int(t * (len(pts) - 1)); (x0, y0), (x1, y1) = pts[i - 4], pts[i + 4]
    ang = math.degrees(math.atan2(-(x1 - x0), -(y1 - y0)))
    sp = sprite(col).rotate(ang, resample=Image.BICUBIC, expand=True)
    im.paste(sp, (int(pts[i][0] - sp.width / 2), int(pts[i][1] - sp.height / 2)), sp)

for x in (380, 760): d.rectangle((x - 5, 660, x + 5, 730), fill=INK3)
d.line((40, 560, 230, 560), fill=INK2, width=7); d.polygon([(230, 560), (196, 540), (196, 580)], fill=INK2)
d.text((80, 580), "wind", font=font("SemiBold", 36), fill=INK2)

p1 = path(lambda t: 380 - 320 * t * t, lambda t: 730 - 560 * t + 130 * t * t)
dashed(p1, WARN); place(p1, 0.78, WARN)
d.text((40, 36), "Too stable", font=font("ExtraBold", 48), fill=WARN)
d.text((40, 96), "turns into the wind", font=font("Regular", 30), fill=INK2)

p2 = path(lambda t: 760 - 60 * t * t, lambda t: 730 - 500 * t)
dashed(p2, OK); place(p2, 0.72, OK)
d.text((520, 36), "1 to 3 calibers", font=font("ExtraBold", 48), fill=OK)
d.text((520, 96), "flies up", font=font("Regular", 30), fill=INK2)
d.text((40, H - 46), "Same wind, same motor. Only the margin differs.", font=font("SemiBold", 28), fill=INK2)
im.save(os.path.join(HERE, "weathercock.png")); print("wrote weathercock.png")
