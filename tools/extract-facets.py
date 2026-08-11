"""Pull the finished model's facet map straight out of the official diagram.

The completed-assembly diagram is a flat drawing: yellow paper, black ink for
every crease and edge, white ground. So every facet of the real model is a
connected patch of yellow bounded by ink — segment those patches and you have
the model's actual geometry, not an impression of it.

  1. classify pixels: ink / paper / ground
  2. label connected paper patches (these are the facets)
  3. trace each patch's boundary, simplify it
  4. re-centre and scale into a 400x400 viewBox

The ink lines leave a 2-3px gap between neighbouring facets. That is wanted:
stroked in the final SVG they become the creases.
"""
import json
import math
from collections import deque

import numpy as np
from PIL import Image

SRC = "diagrams/origami-floral-swirls-diagram-assembly-step-completed.png"
VIEW = 400.0          # target viewBox
TARGET_R = 180.0      # star tip radius in the target frame
MIN_AREA = 260        # ignore specks
EPS = 1.15            # Douglas-Peucker tolerance, source pixels

im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(int)
h, w = a.shape[:2]
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

ink = (r + g + b) < 330
ground = (r > 235) & (g > 235) & (b > 235)
paper = ~ink & ~ground
print("ink %.1f%%  paper %.1f%%  ground %.1f%%" %
      (100 * ink.mean(), 100 * paper.mean(), 100 * ground.mean()))

# ---- label connected paper patches ----------------------------------------
label = np.zeros((h, w), dtype=int)
cur = 0
comps = []
for y0 in range(h):
    for x0 in range(w):
        if not paper[y0, x0] or label[y0, x0]:
            continue
        cur += 1
        q = deque([(y0, x0)])
        label[y0, x0] = cur
        n = 0
        while q:
            y, x = q.popleft()
            n += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and paper[yy, xx] and not label[yy, xx]:
                    label[yy, xx] = cur
                    q.append((yy, xx))
        comps.append((cur, n))

comps = [c for c in comps if c[1] >= MIN_AREA]
comps.sort(key=lambda c: -c[1])
print("facets found: %d (of %d patches)" % (len(comps), cur))
for cid, n in comps:
    print("  facet %2d  area %6d" % (cid, n))


# ---- boundary tracing (Moore neighbourhood, Jacob's stopping criterion) ----
NB = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]


def trace(mask):
    ys, xs = np.nonzero(mask)
    sy, sx = ys[0], xs[0]                      # topmost, then leftmost
    for x in range(xs.min(), xs.max() + 1):
        if mask[sy, x]:
            sx = x
            break
    contour = [(sy, sx)]
    b_idx = 6                                   # came from the left
    cy, cx = sy, sx
    for _ in range(200000):
        found = False
        for k in range(8):
            i = (b_idx + 1 + k) % 8
            ny, nx = cy + NB[i][0], cx + NB[i][1]
            if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx]:
                b_idx = (i + 4 + 1) % 8         # back-track direction
                cy, cx = ny, nx
                contour.append((cy, cx))
                found = True
                break
        if not found:
            break
        if (cy, cx) == (sy, sx) and len(contour) > 2:
            break
    return contour[:-1]


def rdp(pts, eps):
    """Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    best, bi = -1.0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs(dy * px - dx * py + x1 * y0 - y1 * x0) / n if n else math.hypot(px - x0, py - y0)
        if d > best:
            best, bi = d, i
    if best > eps:
        return rdp(pts[:bi + 1], eps)[:-1] + rdp(pts[bi:], eps)
    return [pts[0], pts[-1]]


# ---- model centre and scale ------------------------------------------------
ys, xs = np.nonzero(paper | ink)
cx0, cy0 = xs.mean(), ys.mean()
rmax = max(math.hypot(x - cx0, y - cy0) for y, x in zip(*np.nonzero(ink)))
scale = TARGET_R / rmax
print("centre %.1f,%.1f  tip radius %.1f px  scale %.4f" % (cx0, cy0, rmax, scale))

facets = []
for cid, n in comps:
    mask = label == cid
    cont = trace(mask)
    pts = [(float(x), float(y)) for y, x in cont]
    simp = rdp(pts, EPS)
    if len(simp) > 2 and simp[0] != simp[-1]:
        simp.append(simp[0])
    out = [(round((x - cx0) * scale + VIEW / 2, 1), round((y - cy0) * scale + VIEW / 2, 1))
           for x, y in simp]
    ang = math.degrees(math.atan2(sum(p[1] for p in out) / len(out) - VIEW / 2,
                                  sum(p[0] for p in out) / len(out) - VIEW / 2))
    rad = math.hypot(sum(p[0] for p in out) / len(out) - VIEW / 2,
                     sum(p[1] for p in out) / len(out) - VIEW / 2)
    facets.append({"id": cid, "area": n, "pts": out, "ang": round(ang, 1), "r": round(rad, 1)})
    print("  facet %2d -> %3d pts, centroid r=%.0f ang=%.0f" % (cid, len(out), rad, ang))

json.dump(facets, open("facets.json", "w"))
print("wrote facets.json")
