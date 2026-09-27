#!/usr/bin/env python3
"""Draw thrust-to-weight.png: the BR-1's weight against the average thrust of a G40W and a G74W.

Numbers come from ../../shared/br1-sim.json (rocket mass without a motor) and
../../shared/thrustcurves.json (motor total mass and average thrust). Run from anywhere:
    python3 draw_thrust_to_weight.py
"""
import json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(os.path.dirname(HERE))
FONT_DIR = os.path.join(VIDEO, "fonts")
BG, INK, INK2, INK3 = "#14151a", "#e9e8e4", "#adaba4", "#807d76"
ACCENT, WARN, OK, CARD, LINE = "#7fb0ee", "#e0a35a", "#5cc27f", "#1c1e25", "#31353f"
G = 9.81


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"Inter-{weight}.ttf"), size)


sim = json.load(open(os.path.join(VIDEO, "shared", "br1-sim.json")))
tc = json.load(open(os.path.join(VIDEO, "shared", "thrustcurves.json")))
by = {m["designation"]: m for m in tc["motors"]}
s0 = sim["simulations"][0]["series"][0]
dry_kg = s0["massKg"] - s0["motorMassKg"]                 # 0.962 kg, the BR-1 with no motor
loaded_kg = dry_kg + by["G74W"]["totalWeightG"] / 1000     # about 2 lb 5 oz with a G74W
weight_n = loaded_kg * G                                   # about 10.3 N
need_n = 5 * weight_n                                      # about 52 N
low_n = 3 * weight_n                                       # about 31 N
g40, g74 = by["G40W"]["avgThrustN"], by["G74W"]["avgThrustN"]

W, H = 1728, 820
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)

x0, xmax = 560, W - 150           # bar start and the x of 100 N
fmax = 100
X = lambda n: x0 + (xmax - x0) * n / fmax
rows = [
    ("BR-1 weight, G74W in", f"{int(loaded_kg * 35.274 // 16)} lb {loaded_kg * 35.274 % 16:.0f} oz  ·  {weight_n:.0f} N", weight_n, INK3, ""),
    ("G40W average thrust", f"{g40:.0f} N", g40, WARN, f"{g40 / weight_n:.0f}× : marginal"),
    ("G74W average thrust", f"{g74:.0f} N", g74, OK, f"{g74 / weight_n:.0f}× : passes"),
]
y, bh, gap = 110, 96, 60
for label, value, n, col, verdict in rows:
    d.text((60, y + 8), label, font=font("SemiBold", 34), fill=INK)
    d.text((60, y + 54), value, font=font("Regular", 30), fill=INK2)
    d.rounded_rectangle((x0, y + 14, X(n), y + bh - 14), 10, fill=col)
    if verdict:
        d.text((max(X(n), X(need_n)) + 28, y + 26), verdict, font=font("SemiBold", 32), fill=col)
    y += bh + gap

# the three-times and five-times lines
for mult, n_line in ((3, low_n), (5, need_n)):
    xn = X(n_line)
    for yy in range(80, y - 20, 26):
        d.line((xn, yy, xn, yy + 14), fill=ACCENT, width=5)
    lab = f"{mult}× ({int(n_line + 0.5)} N)"
    f = font("ExtraBold", 28); tw = d.textlength(lab, font=f)
    d.text((xn - tw / 2, 30), lab, font=f, fill=ACCENT)

# axis
ya = y - 10
d.line((x0, ya, xmax, ya), fill=INK3, width=3)
for k in range(0, 101, 25):
    d.line((X(k), ya, X(k), ya + 12), fill=INK3, width=3)
    t = f"{k}"; tw = d.textlength(t, font=font("Regular", 26))
    d.text((X(k) - tw / 2, ya + 18), t, font=font("Regular", 26), fill=INK3)
d.text((xmax - 200, ya + 52), "Newtons of push", font=font("SemiBold", 26), fill=INK3)

# rail-exit rule of thumb
d.rounded_rectangle((60, H - 150, W - 60, H - 30), 18, fill=CARD, outline=LINE, width=2)
d.text((90, H - 126), "Second rule of thumb: leave the rail at about 50 ft/s (15 m/s). Short of it? Use a longer rail: the program flies 6 ft rails.",
       font=font("SemiBold", 28), fill=INK)
d.text((90, H - 84), "Fins only steer once air is moving past them.", font=font("Regular", 30), fill=INK2)

im.save(os.path.join(HERE, "thrust-to-weight.png"))
print(f"dry {dry_kg:.3f} kg, loaded {loaded_kg:.3f} kg, weight {weight_n:.1f} N, 5x {need_n:.1f} N, "
      f"G40W {g40:.1f} N ({g40 / weight_n:.1f}:1), G74W {g74:.1f} N ({g74 / weight_n:.1f}:1)")
