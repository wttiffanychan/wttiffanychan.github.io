"""Trace the finished model's silhouette straight off the official diagram.

The completed-assembly diagram is a flat 2-colour drawing: yellow paper,
black outline, white ground. Everything that is not white is the model, so
the silhouette is just the outer boundary of the non-white mask, sampled as
a radius-per-angle profile around the model's centre. Four-fold symmetry
means one 90 degree slice is the whole story.
"""
import math
import sys

import numpy as np
from PIL import Image

path = sys.argv[1] if len(sys.argv) > 1 else "diagrams/origami-floral-swirls-diagram-assembly-step-completed.png"
im = Image.open(path).convert("RGB")
a = np.asarray(im).astype(int)
h, w = a.shape[:2]

# non-white = paper or ink
mask = (a.sum(axis=2) < 720)

ys, xs = np.nonzero(mask)
cx, cy = xs.mean(), ys.mean()
print("image %dx%d  centroid %.1f,%.1f  coverage %.1f%%" % (w, h, cx, cy, 100.0 * mask.mean()))

# radius profile: for each angle, the furthest lit pixel from the centre
N = 720
prof = []
maxr = int(min(cx, cy, w - cx, h - cy)) - 1
for i in range(N):
    ang = 2 * math.pi * i / N          # 0 = +x, counter-clockwise in maths, y flipped below
    dx, dy = math.cos(ang), math.sin(ang)
    last = 0.0
    for r in range(4, maxr):
        x = int(round(cx + dx * r))
        y = int(round(cy + dy * r))
        if 0 <= x < w and 0 <= y < h and mask[y, x]:
            last = r
    prof.append(last)

prof = np.array(prof)
print("radius min %.1f  max %.1f  mean %.1f" % (prof.min(), prof.max(), prof.mean()))

# where are the four tips?
tips = []
for i in range(N):
    seg = prof[(np.arange(i - 18, i + 19)) % N]
    if prof[i] == seg.max() and prof[i] > prof.mean() * 1.25:
        tips.append(i)
# collapse neighbouring indices
grouped, cur = [], [tips[0]] if tips else []
for t in tips[1:]:
    if t - cur[-1] <= 20:
        cur.append(t)
    else:
        grouped.append(cur)
        cur = [t]
if cur:
    grouped.append(cur)
print("tips at angles:", [round(sum(g) / len(g) * 360.0 / N, 1) for g in grouped])

# print the profile normalised to the tip radius, one sample per 2 degrees
step = N // 180
norm = prof / prof.max()
print("\nangle:radius (normalised, every 2 deg)")
out = []
for i in range(0, N, step):
    out.append("%d:%.3f" % (round(i * 360.0 / N), norm[i]))
print(" ".join(out))
