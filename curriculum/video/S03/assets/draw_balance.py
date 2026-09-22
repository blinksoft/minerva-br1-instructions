#!/usr/bin/env python3
"""Draw the two demo diagrams for Segment 3 in the renderer's palette:
    pencil-on-finger.png   a pencil balanced on a fingertip, CG marked
    string-loop.png        a rocket balanced on a finger, then hung level from a string loop: same point
Run from anywhere: python3 draw_balance.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "..", "fonts")
BG, INK, INK2, INK3 = "#14151a", "#e9e8e4", "#adaba4", "#807d76"
ACCENT, WARN, OK, CARD = "#7fb0ee", "#e0a35a", "#5cc27f", "#1c1e25"
W, H = 1728, 590


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Inter-{weight}.ttf"), size)


def centred(d, x, y, s, f, fill):
    d.text((x - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def finger(d, x, y_top, w=70, h=170):
    """A fingertip pointing up, its tip at (x, y_top)."""
    d.rounded_rectangle((x - w / 2, y_top, x + w / 2, y_top + h), w / 2, fill=CARD, outline=INK3, width=4)
    d.arc((x - w / 2 + 14, y_top + 26, x + w / 2 - 14, y_top + 70), 200, 340, fill=INK3, width=3)


def cg_dot(d, x, y, label, sub=None, above=True, r=16):
    d.ellipse((x - r, y - r, x + r, y + r), fill=ACCENT, outline=BG, width=4)
    if above:
        d.line((x, y - r, x, y - 90), fill=ACCENT, width=4)
        centred(d, x, y - 140, label, font("ExtraBold", 40), ACCENT)
        if sub:
            centred(d, x, y - 180, sub, font("Regular", 28), INK2)
    else:
        d.line((x, y + r, x, y + 90), fill=ACCENT, width=4)
        centred(d, x, y + 100, label, font("ExtraBold", 40), ACCENT)
        if sub:
            centred(d, x, y + 150, sub, font("Regular", 28), INK2)


def pencil(d, x0, x1, y, t=40):
    """A pencil lying flat from x0 to x1 at height y, tip on the right."""
    d.rectangle((x0 + 60, y - t / 2, x1 - 90, y + t / 2), fill=WARN, outline=INK3, width=3)
    d.rectangle((x0, y - t / 2, x0 + 60, y + t / 2), fill="#d68b8b", outline=INK3, width=3)   # eraser
    d.rectangle((x0 + 60, y - t / 2, x0 + 80, y + t / 2), fill=INK2, outline=INK3, width=3)   # ferrule
    d.polygon([(x1 - 90, y - t / 2), (x1, y), (x1 - 90, y + t / 2)], fill="#e6d3b3", outline=INK3)
    d.polygon([(x1 - 24, y - 7), (x1, y), (x1 - 24, y + 7)], fill=INK3)


def rocket(d, xn, xt, y, r=22, fins=True):
    """A small model rocket, nose at xn pointing left, tail at xt."""
    nl = 90
    if fins:
        for sgn in (-1, 1):
            d.polygon([(xt - 70, y + sgn * r), (xt - 45, y + sgn * (r + 44)), (xt - 5, y + sgn * (r + 44)),
                       (xt, y + sgn * r)], fill="#b9b5ab", outline=INK3)
    d.rectangle((xn + nl, y - r, xt, y + r), fill="#d9d7d1", outline=INK3, width=3)
    d.pieslice((xn, y - r, xn + 2 * nl, y + r), 90, 270, fill="#ececec", outline=INK3, width=3)


def draw_pencil():
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    y = 300; x0, x1 = 260, 1480; xc = (x0 + x1) / 2 - 50
    finger(d, xc, y + 14)
    pencil(d, x0, x1, y)
    cg_dot(d, xc, y, "CG", "the balance point")
    d.text((96, H - 70), "All the weight acts as if it were at this one point.", font=font("Regular", 30), fill=INK2)
    im.save(os.path.join(HERE, "pencil-on-finger.png"))


def draw_string():
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    # left panel: across a finger
    y = 330; xn, xt = 120, 720; xc = 470
    finger(d, xc, y + 24)
    rocket(d, xn, xt, y)
    d.rectangle((xc - 10, y - 24, xc + 10, y + 24), fill=WARN)        # tape mark
    cg_dot(d, xc, y, "CG", "mark it with tape")
    centred(d, (xn + xt) / 2, H - 70, "Across a finger", font("SemiBold", 34), INK)
    # right panel: hanging from a string loop, level
    xn, xt = 1000, 1600; xc = 1350
    d.line((xc, 0, xc, y - 40), fill=INK2, width=5)
    d.ellipse((xc - 44, y - 44, xc + 44, y + 44), outline=INK2, width=5)
    rocket(d, xn, xt, y)
    d.rectangle((xc - 10, y - 24, xc + 10, y + 24), fill=WARN)
    cg_dot(d, xc, y, "CG", "hangs level here", above=False)
    centred(d, (xn + xt) / 2, H - 70, "From a string loop", font("SemiBold", 34), INK)
    # middle
    centred(d, 860, y - 24, "=", font("ExtraBold", 72), INK3)
    centred(d, 860, H - 70, "Same point", font("SemiBold", 34), ACCENT)
    im.save(os.path.join(HERE, "string-loop.png"))


if __name__ == "__main__":
    draw_pencil(); draw_string()
