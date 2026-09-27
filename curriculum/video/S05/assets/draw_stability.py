#!/usr/bin/env python3
"""Draw the five animations for "Why a rocket points into the wind", played through `clip` cues:

    vane_side.mp4   a real rooster weather vane (Smithsonian, CC0) on a post, wind flowing past, CG and CP marked
    vane_top.mp4    the vane from above: the wind shifts, the two pushes fall off line, it turns
    forces.mp4      the BR-1 climbing: weight at the CG, drag at the CP, thrust at the tail
    stable.mp4      fins on, a gust tips it, the twist brings it back
    unstable.mp4    fins off, the CP is ahead of the CG, the same gust tips it over

Our own drawings on a sky scene, using render.py's BR-1 side view and the CG and CP from
shared/br1-sim.json. The sequence follows "Rocket Stability" by Angelo State University Engineering
(public domain), redrawn.

    .venv/bin/python curriculum/video/S05/assets/draw_stability.py            # all five
    .venv/bin/python curriculum/video/S05/assets/draw_stability.py stable     # one
    .venv/bin/python curriculum/video/S05/assets/draw_stability.py --stills   # sample frames as PNG, for a look
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, VIDEO)
import render as R

SIZE = (1728, 720)         # the clip box on the plate
FPS = 30

# the sky scene: bright, like the original, so the white BR-1 and the black vane read from the back row
SKY_TOP, SKY_BOT, SKY_FLAT = (118, 160, 214), (176, 205, 238), (140, 176, 224)
FLOW = (52, 84, 150)       # wind arrows
NAVY = "#0e1a33"           # text on the sky
CGC, CPC = "#123a6d", "#c2761f"          # CG and weight  ·  CP and drag
THR, TWIST = "#2f9d5a", "#7b3fa0"        # thrust  ·  the twist
SIL = "#17171c"            # vane silhouette

SIM = json.load(open(os.path.join(VIDEO, "shared", "br1-sim.json")))
G = R.geometry()
CG = next(c for c in SIM["design"]["configurations"] if c["motor"].startswith("G74"))["cgM"]   # G74 loaded
CP = SIM["design"]["cpM"]
CP_NO_FINS = 0.25          # illustrative: ahead of the CG once the fins are gone (CHECK.md)


def font(w, s):
    return R.font(w, s)


# ---------------------------------------------------------------- scene primitives

_sky_cache = {}


def sky(flat=False):
    if flat not in _sky_cache:
        im = Image.new("RGB", SIZE, SKY_FLAT)
        if not flat:
            d = ImageDraw.Draw(im)
            for y in range(SIZE[1]):
                f = y / SIZE[1]
                d.line((0, y, SIZE[0], y), fill=tuple(int(a + (b - a) * f) for a, b in zip(SKY_TOP, SKY_BOT)))
            cl = Image.new("RGBA", SIZE, (0, 0, 0, 0))
            cd = ImageDraw.Draw(cl)
            for (x, y, w, h) in ((160, 110, 260, 70), (300, 90, 200, 60), (1250, 150, 300, 80), (1400, 130, 220, 60),
                                 (700, 560, 320, 70), (900, 540, 220, 60)):
                cd.ellipse((x, y, x + w, y + h), fill=(255, 255, 255, 120))
            cl = cl.filter(ImageFilter.GaussianBlur(18))
            im.paste(cl, (0, 0), cl)
        _sky_cache[flat] = im
    return _sky_cache[flat].copy()


def arrow(d, p0, p1, color, width=10, head=34, outline=None):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 2:
        return
    ux, uy = dx / L, dy / L
    head = min(head, L)
    bx, by = x1 - ux * head, y1 - uy * head
    px, py = -uy, ux
    tri = [(x1, y1), (bx + px * head * 0.55, by + py * head * 0.55), (bx - px * head * 0.55, by - py * head * 0.55)]
    if outline:
        d.line((x0, y0, bx, by), fill=outline, width=width + 8)
        d.polygon(tri, outline=outline, fill=outline, width=4)
    d.line((x0, y0, bx, by), fill=color, width=width)
    d.polygon(tri, fill=color)


def arc_arrow(d, c, r, a0, a1, color, width=10):
    """Arc from a0 to a1 (degrees, clockwise on screen from 3 o'clock) with a head at a1."""
    cx, cy = c
    if abs(a1 - a0) < 3:
        return
    lo, hi = (a0, a1) if a1 > a0 else (a1, a0)
    d.arc((cx - r, cy - r, cx + r, cy + r), lo, hi, fill=color, width=width)
    t = math.radians(a1)
    tip = (cx + r * math.cos(t), cy + r * math.sin(t))
    s = 1 if a1 > a0 else -1
    tx, ty = -math.sin(t) * s, math.cos(t) * s
    head = 34
    base = (tip[0] - tx * head, tip[1] - ty * head)
    px, py = -ty, tx
    d.polygon([tip, (base[0] + px * head * 0.6, base[1] + py * head * 0.6),
               (base[0] - px * head * 0.6, base[1] - py * head * 0.6)], fill=color)


ANCHOR = {(1, 0): "lm", (-1, 0): "rm", (0, -1): "mb", (0, 1): "mt", (1, -1): "lb", (-1, -1): "rb", (1, 1): "lt", (-1, 1): "rt"}


def dot(d, p, color, r=18, label=None, side=(1, 0), size=38):
    x, y = p
    d.ellipse((x - r, y - r, x + r, y + r), fill=color, outline="white", width=5)
    if label:
        d.text((x + side[0] * (r + 12), y + side[1] * (r + 12)), label, font=font("ExtraBold", size), fill=color,
               anchor=ANCHOR[side], stroke_width=3, stroke_fill="white")


def text(d, xy, s, color=NAVY, size=34, weight="SemiBold", anchor="la", stroke=None):
    d.text(xy, s, font=font(weight, size), fill=color, anchor=anchor,
           stroke_width=3 if stroke else 0, stroke_fill=stroke)


def tag(d, s):
    """A small note in the top right corner: the only words on the scene besides the labels."""
    text(d, (SIZE[0] - 48, 56), s, NAVY, 30, "SemiBold", "ra", stroke="white")


def flow(d, angle_deg, phase, sx=150, sy=190, length=110, color=FLOW, width=5, head=22, frame="down"):
    """A field of wind arrows travelling in direction angle_deg (frame "down": 0 points down the
    screen, positive slants toward +x; frame "right": 0 points right, positive turns clockwise).
    phase (0..1) slides every arrow one grid step along the flow, so the field moves."""
    w, h = SIZE
    a = math.radians(angle_deg)
    if frame == "down":
        vx, vy = math.sin(a), math.cos(a)
    else:
        vx, vy = math.cos(a), math.sin(a)
    px, py = vy, -vx
    diag = math.hypot(w, h)
    cx, cy = w / 2, h / 2
    ni, nk = int(diag / sx) + 2, int(diag / sy) + 2
    for i in range(-ni, ni + 1):
        stagger = 0.5 if i % 2 else 0.0
        for k in range(-nk, nk + 1):
            s = (k + phase + stagger) * sy
            mx, my = cx + px * i * sx + vx * s, cy + py * i * sx + vy * s
            if -length < mx < w + length and -length < my < h + length:
                arrow(d, (mx - vx * length / 2, my - vy * length / 2), (mx + vx * length / 2, my + vy * length / 2),
                      color, width=width, head=head)


# ---------------------------------------------------------------- the rocket, nose up, tilted

class Rocket:
    """The BR-1 nose-up with its CG at a chosen point, tilted phi degrees (positive leans the nose to
    the right). map(s) gives the canvas point s metres from the nose tip along the axis."""

    def __init__(self, scale, fins=True, motor=True):
        self.scale, self.fins = scale, fins
        L = int(G["totalLengthM"] * scale * 2.4)
        self.layer = Image.new("RGBA", (L, L), (0, 0, 0, 0))
        d = ImageDraw.Draw(self.layer)
        self.c = (L / 2, L / 2)
        R.draw_rocket(d, self.c[0] - CG * scale, self.c[1], scale, G, fins=fins, motor=motor)

    def place(self, im, pivot, phi, flame=None):
        self.pivot, self.theta = pivot, -90 - phi
        if flame is not None:
            self._flame(im, flame)
        rot = self.layer.rotate(self.theta, resample=Image.BICUBIC, center=self.c)
        im.paste(rot, (int(pivot[0] - self.c[0]), int(pivot[1] - self.c[1])), rot)

    def map(self, s):
        dx = (s - CG) * self.scale
        t = math.radians(self.theta)
        return (self.pivot[0] + dx * math.cos(t), self.pivot[1] - dx * math.sin(t))

    def axis(self):
        n, t = self.map(0), self.map(G["totalLengthM"])
        L = math.hypot(n[0] - t[0], n[1] - t[1])
        return ((n[0] - t[0]) / L, (n[1] - t[1]) / L)

    def _flame(self, im, k):
        """Exhaust behind the tail: two teardrops, flickering with k (seconds)."""
        nx, ny = self.axis()
        px, py = -ny, nx
        tail = self.map(G["totalLengthM"])
        r = G["bodyRadiusM"] * self.scale
        fl = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        d = ImageDraw.Draw(fl)
        for (colour, ln, wd) in (((255, 150, 40, 230), 1.0, 0.75), ((255, 232, 120, 240), 0.55, 0.42)):
            L = r * 4.2 * ln * (1 + 0.12 * math.sin(k * 37) + 0.08 * math.sin(k * 53))
            Wd = r * wd * (1 + 0.1 * math.sin(k * 41))
            pts = []
            for i in range(13):
                u = i / 12; s = math.sin(math.pi * u)
                pts.append((tail[0] - nx * L * u + px * Wd * s, tail[1] - ny * L * u + py * Wd * s))
            for i in range(12, -1, -1):
                u = i / 12; s = math.sin(math.pi * u)
                pts.append((tail[0] - nx * L * u - px * Wd * s, tail[1] - ny * L * u - py * Wd * s))
            d.polygon(pts, fill=colour)
        fl = fl.filter(ImageFilter.GaussianBlur(2))
        im.paste(fl, (0, 0), fl)


def forces(d, rk, phi, drag_len, grow=(1, 1, 1), labels=True, twist=0.0, cp=CP, stable=True):
    """Weight at the CG, drag at the CP, thrust at the tail. grow scales each arrow (weight, drag,
    thrust) from 0 to 1 so they can pop in one at a time. Drag points down the screen, the way the
    air rushes past a climbing rocket, and its length grows with the angle of attack."""
    nx, ny = rk.axis()
    px, py = -ny, nx
    r = G["bodyRadiusM"] * rk.scale
    cg, cpp, tail = rk.map(CG), rk.map(cp), rk.map(G["totalLengthM"])
    off = r + 40
    gw, gd, gt = grow
    if gw > 0:
        w0 = (cg[0] - px * off, cg[1] - py * off)
        d.line((cg[0], cg[1], w0[0], w0[1]), fill=CGC, width=5)
        arrow(d, w0, (w0[0], w0[1] + 130 * gw), CGC, outline="white")
        if labels and gw > 0.9:
            text(d, (w0[0] - 24, w0[1] + 50), "weight", CGC, 34, "ExtraBold", "ra", stroke="white")
    if gd > 0:
        d0 = (cpp[0] + px * off, cpp[1] + py * off)
        d.line((cpp[0], cpp[1], d0[0], d0[1]), fill=CPC, width=5)
        arrow(d, d0, (d0[0], d0[1] + drag_len * gd), CPC, outline="white")
        if labels and gd > 0.9:
            text(d, (d0[0] + 24, d0[1] + 50), "drag", CPC, 34, "ExtraBold", "la", stroke="white")
    if gt > 0:
        t1 = (tail[0] - nx * 130 * gt, tail[1] - ny * 130 * gt)
        arrow(d, t1, (tail[0] - nx * 8, tail[1] - ny * 8), THR, outline="white")
        if labels and gt > 0.9:
            mid = ((t1[0] + tail[0]) / 2, (t1[1] + tail[1]) / 2)
            text(d, (mid[0] + px * 70, mid[1] + py * 70), "thrust", THR, 34, "ExtraBold", "lm" if px >= 0 else "rm", stroke="white")
    if twist > 0.02:
        sweep = min(160, 50 + 110 * twist)
        sign = -1 if (phi > 0) == stable else 1
        a0 = -90 - 30 * sign
        arc_arrow(d, cg, 200, a0, a0 + sign * sweep, TWIST, 11)
        if labels:
            ang = math.radians(a0 + sign * sweep / 2)
            text(d, (cg[0] + 250 * math.cos(ang), cg[1] + 250 * math.sin(ang)), "twist", TWIST, 34, "ExtraBold", "mm", stroke="white")
    dot(d, cg, CGC, label="CG", side=(-1, -1) if px >= 0 else (1, -1))
    dot(d, cpp, CPC, label="CP", side=(1, -1) if px >= 0 else (-1, -1))


# ---------------------------------------------------------------- the rooster vane (a real one)

_rooster = None
ROOSTER_PIVOT, ROOSTER_CP = (603, 531), (1130, 600)     # in rooster.png: the rod on its pin  ·  the tail plate


def rooster_layer():
    """rooster.png: a 19th-century sheet-iron rooster weather vane (Smithsonian American Art Museum,
    1986.65.366, CC0), keyed off its museum background. Pointer to the left, tail plate to the right,
    the rod's pin below. Returns (layer, pivot, cp) in layer pixels."""
    global _rooster
    if _rooster is None:
        _rooster = Image.open(os.path.join(HERE, "rooster.png")).convert("RGBA")
    return _rooster, ROOSTER_PIVOT, ROOSTER_CP


def draw_post(d, x, y):
    """The post under the pin, and the compass cross."""
    d.line((x, y + 120, x, SIZE[1]), fill=SIL, width=14)
    yc = y + 200
    d.line((x - 190, yc, x + 190, yc), fill="#5a4630", width=10)
    for xx, yy in ((x - 190, yc), (x + 190, yc)):
        d.ellipse((xx - 9, yy - 9, xx + 9, yy + 9), fill="#5a4630")
    text(d, (x - 215, yc), "W", SIL, 44, "ExtraBold", "rm")
    text(d, (x + 215, yc), "E", SIL, 44, "ExtraBold", "lm")


# ---------------------------------------------------------------- the vane from above

VANE_L, VANE_PIV, VANE_CP = 620, 250, 500


def vane_top(d, h_deg, c):
    """Top view: pointer, rod and the broad tail, nose pointing in direction h_deg (0 = +x,
    clockwise positive). Returns the local-to-canvas mapping."""
    h = math.radians(h_deg)
    cx, cy = c

    def P(u, v):
        u = VANE_PIV - u
        return (cx + u * math.cos(h) - v * math.sin(h), cy + u * math.sin(h) + v * math.cos(h))
    d.polygon([P(0, 0), P(90, -38), P(90, -10), P(400, -10), P(420, -95), P(VANE_L, -70), P(VANE_L - 34, 0),
               P(VANE_L, 70), P(420, 95), P(400, 10), P(90, 10), P(90, 38)], fill=SIL)
    return P


def vane_pushes(d, P, wind_deg, mag, twist=0.0, labels=True, h_deg=180):
    w = math.radians(wind_deg)
    wx, wy = math.cos(w), math.sin(w)
    piv, cp = P(VANE_PIV, 0), P(VANE_CP, 0)
    arrow(d, cp, (cp[0] + wx * mag, cp[1] + wy * mag), CPC, outline="white")
    arrow(d, piv, (piv[0] - wx * mag, piv[1] - wy * mag), CGC, outline="white")
    if labels:
        text(d, (cp[0] + wx * (mag + 30), cp[1] + wy * (mag + 30)), "air pushes at the CP", CPC, 34, "ExtraBold",
             "lm" if wx >= 0 else "rm", stroke="white")
        text(d, (piv[0] - wx * (mag + 30), piv[1] - wy * (mag + 30)), "rod pushes back at the CG", CGC, 34, "ExtraBold",
             "rm" if wx >= 0 else "lm", stroke="white")
    if twist > 0.02:
        diff = (wind_deg + 180 - h_deg + 540) % 360 - 180
        sign = 1 if diff > 0 else -1
        sweep = min(160, 50 + 110 * twist)
        a0 = 90 - 30 * sign
        arc_arrow(d, piv, 140, a0, a0 + sign * sweep, TWIST, 11)
        if labels:
            text(d, (piv[0], piv[1] + 190), "twist", TWIST, 34, "ExtraBold", "mm", stroke="white")
    dot(d, piv, CGC, label="CG", side=(0, -1))
    dot(d, cp, CPC, label="CP", side=(0, -1))


# ---------------------------------------------------------------- timing helpers

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, t0, t1, a, b):
    return a + (b - a) * smooth((t - t0) / (t1 - t0))


def pop(t, t0, dur=0.45):
    return smooth((t - t0) / dur) if t >= t0 else 0.0


def bump(t, t0, t1, peak):
    if t < t0 or t > t1:
        return 0.0
    return peak * math.sin(math.pi * (t - t0) / (t1 - t0))


def settle(t, t0, start, target, lam=1.1, om=2.4):
    """Damped swing from start to target beginning at t0."""
    if t < t0:
        return start
    u = t - t0
    return target + (start - target) * math.exp(-lam * u) * math.cos(om * u)


def encode(frames, path):
    ff = R.ffmpeg()
    p = subprocess.Popen([ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SIZE[0]}x{SIZE[1]}",
                          "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for im in frames:
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    if p.returncode:
        sys.exit(f"ffmpeg failed on {path}")


# ---------------------------------------------------------------- vane_side.mp4  (about 22 s)

def frame_vane_side(t):
    im = sky()
    d = ImageDraw.Draw(im)
    flow(d, 0, (t * 0.45) % 1.0, frame="right", sx=150, sy=200)
    layer, piv, cp = rooster_layer()
    sc = 0.82                                   # the vane about 1150 px wide on the 1728 px scene
    px, py = SIZE[0] * 0.5, 455
    # a slow wobble in the wind for the first seconds, seen edge-on as a squeeze
    wob = 14 * math.sin(2 * math.pi * t / 5.0) * max(0.0, 1 - t / 9.0)
    k = max(0.25, abs(math.cos(math.radians(wob))))
    lay = layer.resize((int(layer.width * sc * k), int(layer.height * sc)), Image.LANCZOS)
    im.paste(lay, (int(px - piv[0] * sc * k), int(py - piv[1] * sc)), lay)
    d = ImageDraw.Draw(im)
    draw_post(d, px, py)
    cgp = (px, py)
    cpp = (px + (cp[0] - piv[0]) * sc * k, py + (cp[1] - piv[1]) * sc)
    text(d, (48, 56), "wind", NAVY, 38, "ExtraBold", "la", stroke="white")
    if t > 6:
        g = pop(t, 6)
        dot(d, cgp, CGC, r=int(10 + 10 * g))
        if g > 0.9:
            d.line((cgp[0] - 30, cgp[1] + 8, cgp[0] - 130, cgp[1] + 80), fill=CGC, width=5)
            text(d, (cgp[0] - 140, cgp[1] + 62), "CG: the rod, at the balance point", CGC, 40, "ExtraBold", "ra", stroke="white")
            text(d, (cgp[0] - 140, cgp[1] + 108), "the vane turns here", NAVY, 32, "SemiBold", "ra", stroke="white")
    if t > 12:
        g = pop(t, 12)
        dot(d, cpp, CPC, r=int(10 + 10 * g))
        if g > 0.9:
            d.line((cpp[0] + 20, cpp[1] - 22, cpp[0] + 70, cpp[1] - 110), fill=CPC, width=5)
            text(d, (SIZE[0] - 60, cpp[1] - 122), "CP: the tail catches the air", CPC, 40, "ExtraBold", "rb", stroke="white")
            text(d, (SIZE[0] - 60, cpp[1] - 84), "where the wind's push adds up", NAVY, 32, "SemiBold", "rb", stroke="white")
    return im


# ---------------------------------------------------------------- vane_top.mp4  (about 29 s)

def frame_vane_top(t):
    im = sky(flat=True)
    d = ImageDraw.Draw(im)
    c = (SIZE[0] * 0.5, SIZE[1] * 0.46)
    if t < 5:
        wind = 0.0
    elif t < 7:
        wind = ramp(t, 5, 7, 0, -38)
    elif t < 19.5:
        wind = -38.0
    elif t < 21.5:
        wind = ramp(t, 19.5, 21.5, -38, 30)
    else:
        wind = 30.0
    target = wind + 180
    if t < 12:
        h = 180.0
    elif t < 19.5:
        h = settle(t, 12, 180, target)
    elif t < 22.5:
        h = 180 - 38
    else:
        h = settle(t, 22.5, 180 - 38, target)
    flow(d, wind, (t * 0.45) % 1.0, frame="right", sx=150, sy=200)
    P = vane_top(d, h, c)
    misalign = abs((wind + 180 - h + 540) % 360 - 180) / 38.0
    if 8.5 < t < 19.5:
        twist = ramp(t, 8.5, 9.5, 0, 1) * min(1.0, misalign * 1.3)
    elif 22.5 < t < 28:
        twist = min(1.0, misalign * 1.3)
    else:
        twist = 0.0
    if t > 2.0:
        vane_pushes(d, P, wind, 130, twist=twist, labels=not (19.5 < t < 22.5), h_deg=h)
    else:
        dot(d, P(VANE_PIV, 0), CGC, label="CG", side=(0, -1))
        dot(d, P(VANE_CP, 0), CPC, label="CP", side=(0, -1))
    tag(d, "seen from above")
    return im


# ---------------------------------------------------------------- the rocket clips

def rocket_frame(rk, t, phi, gust, drag, grow, twist, cp, stable, note=None):
    im = sky()
    d = ImageDraw.Draw(im)
    flow(d, gust, (t * 0.6) % 1.0, sx=150, sy=190)
    pivot = (SIZE[0] * 0.5, SIZE[1] * 0.5)      # centred: nose, tail and arrows fit at any angle
    rk.place(im, pivot, phi, flame=t)
    d = ImageDraw.Draw(im)
    forces(d, rk, phi, drag, grow=grow, labels=True, twist=twist, cp=cp, stable=stable)
    if gust > 4:
        text(d, (48, 56), "gust", NAVY, 38, "ExtraBold", "la", stroke="white")
        arrow(d, (150, 74), (330, 74 + 60), FLOW, width=8, head=28)
    if note:
        tag(d, note)
    return im


def frame_forces(t):
    rk = _rk(True)
    grow = (pop(t, 4.0), pop(t, 9.0), pop(t, 13.5))
    im = rocket_frame(rk, t, 0.0, 0.0, 100, grow, 0.0, CP, True, note="fins on")
    if t > 17.5:
        d = ImageDraw.Draw(im)
        x = SIZE[0] * 0.5
        for y in range(30, SIZE[1] - 30, 28):
            d.line((x, y, x, y + 14), fill="white", width=3)
    return im


def frame_stable(t):
    rk = _rk(True)
    if t < 5:
        phi = 0.0
    elif t < 7:
        phi = ramp(t, 5, 7, 0, 26)
    elif t < 14:
        phi = 26.0
    elif t < 21:
        phi = settle(t, 14, 26, 0, lam=0.9, om=2.3)
    else:
        phi = 0.0
    gust = bump(t, 5.0, 8.0, 30)
    aoa = abs(phi)
    drag = 100 + 3.2 * aoa
    twist = min(1.0, aoa / 26.0) if t > 8.5 else 0.0
    return rocket_frame(rk, t, phi, gust, drag, (1, 1, 1), twist, CP, True, note="fins on")


def frame_unstable(t):
    rk = _rk(False)
    if t < 4:
        phi = 0.0
    elif t < 6:
        phi = ramp(t, 4, 6, 0, 22)
    elif t < 12:
        phi = 22 + 8 * smooth((t - 6) / 6)
    elif t < 22:
        phi = 30 + 150 * smooth((t - 12) / 10) ** 1.5
    else:
        phi = 180.0
    gust = bump(t, 4.0, 7.0, 30)
    aoa = phi if phi <= 90 else 180 - phi
    drag = 100 + 3.2 * min(aoa, 60)
    twist = min(1.0, aoa / 22.0) if t > 7.5 else 0.0
    grow = (1, 1 if phi < 150 else 0, 1)
    return rocket_frame(rk, t, phi, gust, drag, grow, twist, CP_NO_FINS, False, note="fins off")


_rockets = {}


def _rk(fins):
    if fins not in _rockets:
        _rockets[fins] = Rocket(500 / G["totalLengthM"], fins=fins)
    return _rockets[fins]


CLIPS = {"vane_side": (frame_vane_side, 22.0), "vane_top": (frame_vane_top, 29.0), "forces": (frame_forces, 20.0),
         "stable": (frame_stable, 27.0), "unstable": (frame_unstable, 28.0)}

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(CLIPS)
    for name in names:
        fn, T = CLIPS[name]
        if "--stills" in sys.argv:
            for t in (0.0, T * 0.35, T * 0.7, T - 0.5):
                fn(t).save(os.path.join(HERE, f"_{name}_{t:04.1f}.png"))
            print("stills for", name)
            continue
        encode((fn(i / FPS) for i in range(int(T * FPS))), os.path.join(HERE, f"{name}.mp4"))
        print("wrote", f"{name}.mp4")
