#!/usr/bin/env python3
"""Draw barrowman.png: the Barrowman equations solved by hand for the BR-1, from shared/br1-sim.json.

    python3 curriculum/video/S04/assets/draw_barrowman.py

The point of the slide is the wall of arithmetic, and that the hand result lands on OpenRocket's number.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(os.path.dirname(HERE))
g = json.load(open(os.path.join(VIDEO, "shared", "br1-sim.json")))["geometry"]
BG, INK, INK2, INK3, ACCENT, WARN, OK, CARD = "#14151a", "#e9e8e4", "#adaba4", "#807d76", "#7fb0ee", "#e0a35a", "#5cc27f", "#1c1e25"
def font(w, s): return ImageFont.truetype(os.path.join(VIDEO, "fonts", f"Inter-{w}.ttf"), s)
IN = 39.3701

# --- the arithmetic (classic Barrowman, three fins, ellipsoid nose treated by its volume)
d = g["bodyDiameterM"]; R = d / 2; LN = g["noseLengthM"]
a, b, m, s, N = g["finRootM"], g["finTipM"], g["finSweepM"], g["finHeightM"], g["finCount"]
XB = g["totalLengthM"] - g["finOffsetFromBottomM"] - a
CN_nose, X_nose = 2.0, LN / 3                       # ellipsoid: X = L - V/(pi R^2) = L/3
l = math.sqrt(s ** 2 + (m + b / 2 - a / 2) ** 2)
CN_fins = (1 + R / (s + R)) * (4 * N * (s / d) ** 2) / (1 + math.sqrt(1 + (2 * l / (a + b)) ** 2))
X_fins = XB + m * (a + 2 * b) / (3 * (a + b)) + (a + b - a * b / (a + b)) / 6
CP = (CN_nose * X_nose + CN_fins * X_fins) / (CN_nose + CN_fins)

W, H = 1728, 720
im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
def T(x, y, t, w="Regular", sz=30, fill=INK):
    dr.text((x, y), t, font=font(w, sz), fill=fill)
def card(x, y, w, h, title, col):
    dr.rounded_rectangle((x, y, x + w, y + h), 18, fill=CARD, outline="#31353f", width=2)
    T(x + 24, y + 14, title, "ExtraBold", 30, col)

fi = lambda v: f"{v * IN:.1f} in"
# top row: nose, body, add them up
card(0, 0, 540, 220, "Nose cone", ACCENT)
T(24, 62, "C_N = 2 for every nose", "SemiBold", 28)
T(24, 104, "X = L − V / (πR²) = L / 3  (ellipsoid)", "Regular", 26, INK2)
T(24, 140, f"= {LN * IN:.1f} in / 3", "Regular", 26, INK2)
T(24, 178, f"C_N = 2.0    X = {fi(X_nose)}", "ExtraBold", 28, OK)
card(570, 0, 540, 220, "Body tube", ACCENT)
T(594, 62, "C_N = 0", "SemiBold", 28)
T(594, 104, "A cylinder at a small angle of attack", "Regular", 26, INK2)
T(594, 140, "makes no normal force in this method.", "Regular", 26, INK2)
T(594, 178, "C_N = 0    X = does not matter", "ExtraBold", 28, OK)
card(1140, 0, 588, 220, "Not in the hand method", INK3)
T(1164, 62, "Rail buttons, paint, fin thickness", "Regular", 26, INK2)
T(1164, 98, "Body taper, speed (Mach) correction", "Regular", 26, INK2)
T(1164, 134, "Every part's exact shape", "Regular", 26, INK2)
T(1164, 178, "OpenRocket handles all of these.", "SemiBold", 26, INK)
# fins
card(0, 250, 1110, 360, f"Fins, {N} trapezoidal", ACCENT)
T(24, 60 + 250, f"root a {fi(a)}  ·  tip b {fi(b)}  ·  span s {fi(s)}  ·  sweep m {fi(m)}  ·  R {fi(R)}  ·  d {fi(d)}", "Regular", 23, INK2)
T(24, 98 + 250, "l = √( s² + (m + b/2 − a/2)² )" + f"  =  {fi(l)}", "Regular", 26)
T(24, 140 + 250, "C_N = [ 1 + R/(s + R) ] · 4N (s/d)² / [ 1 + √( 1 + (2l/(a + b))² ) ]", "SemiBold", 27)
T(24, 180 + 250, f"= {1 + R / (s + R):.3f} · {4 * N * (s / d) ** 2:.2f} / {1 + math.sqrt(1 + (2 * l / (a + b)) ** 2):.3f}", "Regular", 25, INK2)
T(24, 224 + 250, "X = X_B + m (a + 2b) / 3(a + b) + (1/6) [ a + b − ab/(a + b) ]", "SemiBold", 27)
T(24, 264 + 250, f"= {fi(XB)} + {fi(m * (a + 2 * b) / (3 * (a + b)))} + {fi((a + b - a * b / (a + b)) / 6)}", "Regular", 25, INK2)
T(24, 312 + 250, f"C_N = {CN_fins:.2f}    X = {fi(X_fins)}", "ExtraBold", 28, OK)
# combine
card(1140, 250, 588, 360, "Add them up", WARN)
T(1164, 310, "CP = Σ C_N · X  /  Σ C_N", "SemiBold", 28)
T(1164, 354, f"= (2 · {X_nose * IN:.1f} + {CN_fins:.2f} · {X_fins * IN:.1f}) / (2 + {CN_fins:.2f})", "Regular", 24, INK2)
T(1164, 404, f"= {CP * IN:.1f} in ({CP * 100:.0f} cm)", "ExtraBold", 44, WARN)
T(1164, 470, "OpenRocket: 33 3/4 in (86 cm)", "ExtraBold", 30, INK)
T(1164, 520, "By hand, about ten minutes. OpenRocket, a blink,", "Regular", 22, INK3)
T(1164, 548, "every time you change a part.", "Regular", 22, INK3)
T(0, 640, "Classic Barrowman method (1966). Each part gets a normal-force coefficient C_N and a point X, from the nose tip. Numbers from files/BR-1.ork.", "Regular", 23, INK3)
T(0, 676, "Ellipsoid nose: X = L − V/(πR²). The classic tables give 0.466 L for an ogive and 2/3 L for a cone. Sources in the video description.", "Regular", 23, INK3)
im.save(os.path.join(HERE, "barrowman.png"))
print(f"nose C_N 2, X {X_nose:.4f} m; fins C_N {CN_fins:.3f}, X {X_fins:.4f} m; CP {CP:.4f} m = {CP * IN:.2f} in; OpenRocket 0.846 m")
