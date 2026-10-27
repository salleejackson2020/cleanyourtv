#!/usr/bin/env python3
"""Draws themes/halloween/wallpaper.jpg from code alone: three jack-o'-lanterns on a dark hill under an
orange harvest moon, a dead tree, bats, drifting fog and cobwebs (the top corners, the tree, and one large
web behind the dock band, which shows through the band at dock_opacity 50). No photos, artwork or fonts
are used, so the picture is original and can be redrawn by anyone.

    python3 make_wallpaper.py     # needs Pillow and NumPy; seed 1031 gives the same picture

Dark on purpose (see themes/README.md, Wallpapers): the clock (top left), the pills (top right), the hero
name (left, about 60 % down) and the dock band (72-88 % down) sit on this picture, so those areas stay
near black.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
S = 2                                   # draw at 2x, scale down for clean edges
w, h = W * S, H * S
rng = np.random.default_rng(1031)
OUT = Path(__file__).with_name("wallpaper.jpg")


def gradient(stops, n):
    ys = np.linspace(0, 1, n)
    out = np.zeros((n, 3))
    for c in range(3):
        out[:, c] = np.interp(ys, [p for p, _ in stops], [col[c] for _, col in stops])
    return out


# ---- sky ------------------------------------------------------------------------------------
sky = gradient([(0.0, (7, 3, 14)), (0.35, (18, 8, 34)), (0.62, (34, 12, 44)), (0.72, (44, 16, 40)),
                (1.0, (10, 5, 14))], h)
img = np.zeros((h, w, 3))
img[:] = sky[:, None, :]
yy, xx = np.mgrid[0:h, 0:w]

stars = Image.new("RGB", (w, h), (0, 0, 0))
sd = ImageDraw.Draw(stars)
for _ in range(260):
    x, y = rng.uniform(0, w), rng.uniform(0, h * 0.62)
    r = rng.uniform(0.6, 2.2) * S
    v = int(rng.uniform(90, 210))
    sd.ellipse([x - r, y - r, x + r, y + r], fill=(v, v, int(v * 0.9)))
img += np.asarray(stars, dtype=float)

# harvest moon with a halo, on the right under the pills
MX, MY, MR = w * 0.80, h * 0.40, h * 0.085
halo = np.exp(-(((xx - MX) ** 2 + (yy - MY) ** 2) / (h * 0.16) ** 2))
img += halo[:, :, None] * np.array([70, 36, 10])
moon = Image.new("RGB", (w, h), (0, 0, 0))
md = ImageDraw.Draw(moon)
md.ellipse([MX - MR, MY - MR, MX + MR, MY + MR], fill=(246, 196, 120))
for _ in range(6):
    a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0, MR * 0.7)
    cx, cy, cr = MX + math.cos(a) * d, MY + math.sin(a) * d, rng.uniform(MR * 0.04, MR * 0.11)
    md.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(234, 184, 110))
moon = moon.filter(ImageFilter.GaussianBlur(1.2 * S))
img = np.maximum(img, np.asarray(moon, dtype=float))

# ---- ground ---------------------------------------------------------------------------------
GY = h * 0.705
ground = Image.new("L", (w, h), 0)
gd = ImageDraw.Draw(ground)
pts = [(0, h)]
for i in range(0, w + 1, 40 * S):
    t = i / w
    pts.append((i, GY + math.sin(t * 5.1) * 14 * S + math.sin(t * 13.7) * 6 * S - (t - 0.72) ** 2 * 120 * S))
pts.append((w, h))
gd.polygon(pts, fill=255)
gmask = np.asarray(ground, dtype=float) / 255.0
ground_col = np.array([9, 5, 13])
img = img * (1 - gmask[:, :, None]) + ground_col * gmask[:, :, None]


# ---- jack-o'-lanterns -----------------------------------------------------------------------
def pumpkin(layer, glow, cx, cy, rx, ry):
    d = ImageDraw.Draw(layer)
    body = (236, 118, 28)
    dark = (150, 60, 12)
    rim = (255, 150, 50)
    lobes = [(-0.62, 0.78, dark), (0.62, 0.78, dark), (-0.33, 0.92, body), (0.33, 0.92, body), (0.0, 1.0, rim)]
    for ox, sc, col in lobes:
        d.ellipse([cx + ox * rx - rx * 0.55 * sc, cy - ry * sc, cx + ox * rx + rx * 0.55 * sc, cy + ry * sc],
                  fill=col, outline=(150, 62, 12), width=3 * S)
    sh = Image.new("L", layer.size, 0)
    sdr = ImageDraw.Draw(sh)
    sdr.ellipse([cx - rx * 1.1, cy + ry * 0.25, cx + rx * 1.1, cy + ry * 1.25], fill=140)
    sh = sh.filter(ImageFilter.GaussianBlur(ry * 0.25))
    layer.paste(Image.new("RGB", layer.size, (70, 25, 6)), (0, 0), sh)
    d.polygon([(cx - rx * 0.09, cy - ry * 0.98), (cx + rx * 0.11, cy - ry * 0.98), (cx + rx * 0.16, cy - ry * 1.28),
               (cx - rx * 0.02, cy - ry * 1.3)], fill=(60, 72, 30))
    light = (255, 228, 110)
    face = [
        [(cx - rx * 0.42, cy - ry * 0.10), (cx - rx * 0.16, cy - ry * 0.10), (cx - rx * 0.30, cy - ry * 0.46)],
        [(cx + rx * 0.16, cy - ry * 0.10), (cx + rx * 0.42, cy - ry * 0.10), (cx + rx * 0.30, cy - ry * 0.46)],
        [(cx - rx * 0.08, cy + ry * 0.12), (cx + rx * 0.08, cy + ry * 0.12), (cx, cy - ry * 0.08)],
    ]
    mouth = [(cx - rx * 0.55, cy + ry * 0.22)]
    teeth = 7
    for i in range(1, teeth + 1):
        t = i / teeth
        x = cx - rx * 0.55 + t * rx * 1.1
        y = cy + ry * (0.22 + 0.42 * math.sin(t * math.pi))
        mouth.append((x, y - (ry * 0.11 if i % 2 else 0)))
    mouth += [(cx + rx * 0.55, cy + ry * 0.22), (cx + rx * 0.40, cy + ry * 0.30), (cx + rx * 0.20, cy + ry * 0.34),
              (cx, cy + ry * 0.36), (cx - rx * 0.20, cy + ry * 0.34), (cx - rx * 0.40, cy + ry * 0.30)]
    for poly in face + [mouth]:
        d.polygon(poly, fill=light)
        ImageDraw.Draw(glow).polygon(poly, fill=(255, 170, 60))


pk = Image.new("RGB", (w, h), (0, 0, 0))
pmask = Image.new("L", (w, h), 0)
glow = Image.new("RGB", (w, h), (0, 0, 0))
P = [(w * 0.745, h * 0.635, w * 0.085, h * 0.125), (w * 0.885, h * 0.665, w * 0.055, h * 0.082),
     (w * 0.635, h * 0.672, w * 0.040, h * 0.060)]
for cx, cy, rx, ry in P:
    pumpkin(pk, glow, cx, cy, rx, ry)
    md = ImageDraw.Draw(pmask)
    md.ellipse([cx - rx * 1.06, cy - ry * 1.0, cx + rx * 1.06, cy + ry * 1.0], fill=255)
    md.polygon([(cx - rx * 0.1, cy - ry * 0.98), (cx + rx * 0.12, cy - ry * 0.98), (cx + rx * 0.17, cy - ry * 1.3),
                (cx - rx * 0.03, cy - ry * 1.32)], fill=255)
    gl = ImageDraw.Draw(glow)
    gl.ellipse([cx - rx * 2.2, cy + ry * 0.6, cx + rx * 2.2, cy + ry * 1.5], fill=(120, 60, 14))
glow_big = glow.filter(ImageFilter.GaussianBlur(h * 0.05))
glow_small = glow.filter(ImageFilter.GaussianBlur(h * 0.012))
img += np.asarray(glow_big, dtype=float) * 0.9 + np.asarray(glow_small, dtype=float) * 0.6
pm = np.asarray(pmask, dtype=float)[:, :, None] / 255.0
img = img * (1 - pm) + np.asarray(pk, dtype=float) * pm

# ---- dead tree on the left ------------------------------------------------------------------
tree = Image.new("L", (w, h), 0)
td = ImageDraw.Draw(tree)


def branch(x, y, ang, length, width, depth):
    if depth == 0 or length < 6 * S:
        return
    x2, y2 = x + math.cos(ang) * length, y - math.sin(ang) * length
    td.line([(x, y), (x2, y2)], fill=255, width=max(1, int(width)))
    n = 2 if depth > 2 else int(rng.integers(1, 3))
    for _ in range(n):
        a = ang + rng.uniform(-0.75, 0.75)
        branch(x2, y2, a, length * rng.uniform(0.62, 0.8), width * 0.62, depth - 1)


TX = w * 0.135
branch(TX, GY + 10 * S, math.pi / 2 + 0.05, h * 0.19, 26 * S, 7)
tm = np.asarray(tree, dtype=float)[:, :, None] / 255.0
img = img * (1 - tm) + np.array([6, 3, 9]) * tm

# ---- bats near the moon ---------------------------------------------------------------------
bats = Image.new("L", (w, h), 0)
bd = ImageDraw.Draw(bats)
for (bx, by, bs) in [(0.70, 0.30, 22), (0.735, 0.255, 16), (0.655, 0.36, 13), (0.86, 0.27, 12), (0.60, 0.25, 9)]:
    bx, by, bs = bx * w, by * h, bs * S
    bd.polygon([(bx - bs, by - bs * 0.5), (bx - bs * 0.55, by - bs * 0.15), (bx - bs * 0.2, by - bs * 0.35),
                (bx, by), (bx + bs * 0.2, by - bs * 0.35), (bx + bs * 0.55, by - bs * 0.15), (bx + bs, by - bs * 0.5),
                (bx + bs * 0.6, by + bs * 0.25), (bx + bs * 0.25, by + bs * 0.15), (bx, by + bs * 0.45),
                (bx - bs * 0.25, by + bs * 0.15), (bx - bs * 0.6, by + bs * 0.25)], fill=255)
bm = np.asarray(bats, dtype=float)[:, :, None] / 255.0
img = img * (1 - bm) + np.array([8, 4, 10]) * bm

# ---- fog along the ground -------------------------------------------------------------------
fog = np.exp(-((yy - GY * 1.02) / (h * 0.045)) ** 2) * (0.55 + 0.45 * np.sin(xx / (w * 0.09) + 1.3))
img += fog[:, :, None] * np.array([38, 22, 52])


# ---- cobwebs --------------------------------------------------------------------------------
def web(d, cx, cy, radius, a0, a1, radials=11, rings=9, alpha=255, width=1):
    """A sagging orb web: radial threads from (cx, cy), rings as curves pulled toward the centre."""
    angs = np.linspace(a0, a1, radials)
    col = alpha
    for a in angs:
        d.line([(cx, cy), (cx + math.cos(a) * radius, cy + math.sin(a) * radius)], fill=col, width=width)
    for k in range(1, rings + 1):
        r = radius * (k / rings) ** 1.25
        for i in range(len(angs) - 1):
            p0 = (cx + math.cos(angs[i]) * r, cy + math.sin(angs[i]) * r)
            p1 = (cx + math.cos(angs[i + 1]) * r, cy + math.sin(angs[i + 1]) * r)
            mid_a = (angs[i] + angs[i + 1]) / 2
            sag = r * 0.90
            pm_ = (cx + math.cos(mid_a) * sag, cy + math.sin(mid_a) * sag)
            pts = [(((1 - t) ** 2) * p0[0] + 2 * (1 - t) * t * pm_[0] + t * t * p1[0],
                    ((1 - t) ** 2) * p0[1] + 2 * (1 - t) * t * pm_[1] + t * t * p1[1]) for t in np.linspace(0, 1, 8)]
            d.line(pts, fill=col, width=width)


webs = Image.new("L", (w, h), 0)
wd = ImageDraw.Draw(webs)
web(wd, 0, 0, h * 0.30, 0.02, math.pi / 2 - 0.02, radials=9, rings=8, alpha=120, width=1 * S)            # top left
web(wd, w, 0, h * 0.24, math.pi / 2 + 0.02, math.pi - 0.02, radials=8, rings=7, alpha=80, width=1 * S)    # top right
web(wd, w * 0.5, h * 1.32, h * 0.66, math.pi + 0.35, 2 * math.pi - 0.35, radials=19, rings=10, alpha=150, width=1 * S)  # dock
web(wd, TX + w * 0.06, h * 0.50, h * 0.085, 0, 2 * math.pi, radials=12, rings=6, alpha=135, width=1 * S)  # in the tree
spx, spy = w * 0.455, h * 0.34
wd.line([(spx, 0), (spx, spy)], fill=140, width=1 * S)                                                    # spider thread
webs = webs.filter(ImageFilter.GaussianBlur(0.6 * S))
wm = np.asarray(webs, dtype=float)[:, :, None] / 255.0
web_col = np.array([205, 200, 215])
img = img * (1 - wm * 0.85) + web_col * wm * 0.85

spider = Image.new("L", (w, h), 0)
spd = ImageDraw.Draw(spider)
spd.ellipse([spx - 7 * S, spy - 9 * S, spx + 7 * S, spy + 9 * S], fill=255)
spd.ellipse([spx - 4 * S, spy - 15 * S, spx + 4 * S, spy - 8 * S], fill=255)
for side in (-1, 1):
    for (dx, dy) in [(14, -10), (17, -2), (16, 7), (12, 14)]:
        spd.line([(spx, spy - 2 * S), (spx + side * dx * S, spy + dy * S)], fill=255, width=2 * S)
spm = np.asarray(spider, dtype=float)[:, :, None] / 255.0
img = img * (1 - spm) + np.array([12, 8, 14]) * spm

# ---- vignette, dither, save -----------------------------------------------------------------
vign = 1 - 0.35 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.2
img *= np.clip(vign, 0.45, 1)[:, :, None]
img += rng.normal(0, 1.6, img.shape)          # breaks up banding in the dark sky
out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
out.save(OUT, "JPEG", quality=86, optimize=True)
print(OUT, OUT.stat().st_size, "bytes")
