#!/usr/bin/env python3
"""Draw the standard motor diameters as circles to scale, in the renderer's palette.

    .venv/bin/python curriculum/video/S09/assets/draw_diameters.py   # writes diameters.png next to itself
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "..", "fonts")
BG, INK, INK2, INK3 = "#14151a", "#e9e8e4", "#adaba4", "#807d76"
ACCENT, WARN, OK, CARD = "#7fb0ee", "#e0a35a", "#5cc27f", "#1c1e25"

# (diameter mm, label under the size, colour)
SIZES = [(18, "Alpha III", INK2), (24, "", INK2), (29, "BR-1", ACCENT), (38, "", INK2),
         (54, "", INK2), (75, "", INK2), (98, "", INK2)]
SCALE = 3.6          # px per mm
GAP = 30             # px between slots
MIN_SLOT = 168       # px, so the small circles' labels do not collide
W = 1728


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"Inter-{weight}.ttf"), size)


def main():
    h_circ = int(98 * SCALE)
    H = h_circ + 40 + 150
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    slots = [max(int(s[0] * SCALE), MIN_SLOT) for s in SIZES]
    total = sum(slots) + GAP * (len(SIZES) - 1)
    x = (W - total) // 2
    base = 20 + h_circ            # circles sit on a common baseline
    f_big, f_sub = font("ExtraBold", 44), font("SemiBold", 30)
    for (mm, sub, col), slot in zip(SIZES, slots):
        px = int(mm * SCALE)
        cx, cy = x + slot / 2, base - px / 2
        fill = "#1e3a5c" if col == ACCENT else CARD
        d.ellipse((cx - px / 2, cy - px / 2, cx + px / 2, cy + px / 2), fill=fill, outline=col, width=5)
        # a small nozzle throat in the middle, so it reads as the end of a motor
        r = max(4, px * 0.11)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        label = f"{mm} mm"
        tw = d.textlength(label, font=f_big)
        d.text((cx - tw / 2, base + 34), label, font=f_big, fill=INK if col == INK2 else col)
        if sub:
            sw = d.textlength(sub, font=f_sub)
            d.text((cx - sw / 2, base + 96), sub, font=f_sub, fill=col)
        x += slot + GAP
    im.save(os.path.join(HERE, "diameters.png"))
    print("wrote diameters.png", im.size)


if __name__ == "__main__":
    main()
