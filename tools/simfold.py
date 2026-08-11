"""Flat-fold simulation of the origami rose — all 9 reference steps.

Reference: homemadeheather.com "A Rose".

  1  crease the square both ways
  2  fold the four corners to the centre      blintz -> diamond
  3  fold the four corners to the centre      blintz -> square
  4  fold the four corners to the centre      blintz -> diamond
  5  fold the step-4 flaps back OUT           inner petals (diagonals)
  6  fold the step-3 flaps back OUT           mid petals (axes)
  7  fold the step-2 flaps back OUT           outer petals (diagonals)
  8  fold the diamond's tips BEHIND           octagon silhouette
  9  finished

The sheet starts as one cell. At every fold each cell is split by the
PREIMAGE of the fold line under its own transform (so nothing straddles a
crease) and the pieces on the folding side are reflected. Blintz folds move
every layer beyond the line; a petal fold-out moves exactly the cells whose
most recent fold was that ring — the whole thickness of the flap — inside
that flap's own WEDGE. The wedge matters: the step-3 flaps live in the axis
wedges |cross| <= along, and using a half-plane there grabs the neighbouring
flaps and tears the model (that was the bug that sank the last attempt).

Every fold appends an EVENT id to the history of each cell it moves. The
history is what the exporter turns into nested hinge groups.
"""
import json
import math

EPS = 1e-9
C5, C6, C7, C8 = 0.33, 0.33, 0.26, 0.42


def area(p):
    s = 0.0
    for i in range(len(p)):
        x1, y1 = p[i]
        x2, y2 = p[(i + 1) % len(p)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def centroid(p):
    return (sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p))


def split(poly, a, b, c):
    pos, neg = [], []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dp = a * p[0] + b * p[1] - c
        dq = a * q[0] + b * q[1] - c
        if dp >= -EPS:
            pos.append(p)
        if dp <= EPS:
            neg.append(p)
        if (dp > EPS and dq < -EPS) or (dp < -EPS and dq > EPS):
            t = dp / (dp - dq)
            m = (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
            pos.append(m)
            neg.append(m)
    pos = pos if len(pos) >= 3 and area(pos) > 1e-8 else None
    neg = neg if len(neg) >= 3 and area(neg) > 1e-8 else None
    return pos, neg


def mat_mul(m, n):
    a, b, c, d, e, f = m
    A, B, Cc, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * Cc + c * D, b * Cc + d * D,
            a * E + c * F + e, b * E + d * F + f)


def mat_apply(m, p):
    return (m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5])


IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def reflection(a, b, c):
    n = math.hypot(a, b)
    a, b, c = a / n, b / n, c / n
    return (1 - 2 * a * a, -2 * a * b, -2 * a * b, 1 - 2 * b * b, 2 * a * c, 2 * b * c)


def pullback(m, a, b, c):
    return (a * m[0] + b * m[1], a * m[2] + b * m[3], c - a * m[4] - b * m[5])


cells = [{"poly": [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)],
          "m": IDENT, "last": 1, "order": 0, "hist": []}]
EVENTS = []


def do_fold(a, b, c, side, step, only_last=None, exclude_last=(), region=None,
            behind=False):
    eid = len(EVENTS)
    EVENTS.append({"id": eid, "step": step, "a": a, "b": b, "c": c})
    R = reflection(a, b, c)
    out, moved = [], []
    for cell in cells:
        elig = ((only_last is None or cell["last"] == only_last)
                and cell["last"] not in exclude_last)
        if not elig:
            out.append(cell)
            continue
        A, B, Cc = pullback(cell["m"], a, b, c)
        pos, neg = split(cell["poly"], A, B, Cc)
        pieces = [p for p in (pos, neg) if p is not None]
        if not pieces:
            out.append(cell)
            continue
        for piece in pieces:
            new = {"poly": piece, "m": cell["m"], "last": cell["last"],
                   "order": cell["order"], "hist": list(cell["hist"])}
            wc = centroid([mat_apply(cell["m"], q) for q in piece])
            d = a * wc[0] + b * wc[1] - c
            mov = (d > EPS) if side > 0 else (d < -EPS)
            if mov and (region is None or region(*wc)):
                new["m"] = mat_mul(R, cell["m"])
                new["last"] = step
                new["hist"].append(eid)
                moved.append(new)
            out.append(new)
    # folding flips a stack: lifted to the top in reversed order — or dropped
    # below the bottom for a fold-behind
    if moved:
        if behind:
            bot = min(c2["order"] for c2 in out) - 1
            for i, c2 in enumerate(sorted(moved, key=lambda c2: c2["order"])):
                c2["order"] = bot - i
        else:
            top = max(c2["order"] for c2 in out) + 1
            for i, c2 in enumerate(sorted(moved, key=lambda c2: -c2["order"])):
                c2["order"] = top + i
    cells[:] = out
    return len(moved)


STAGES = []


def snapshot():
    STAGES.append([{"poly": c["poly"], "m": c["m"], "order": c["order"],
                    "flips": len(c["hist"])} for c in cells])


DG = ((1, 1), (1, -1), (-1, 1), (-1, -1))
AXV = ((1, 0), (-1, 0), (0, 1), (0, -1))


def quad(sx, sy):
    return lambda x, y: sx * x >= -0.02 and sy * y >= -0.02


def wedge(ax, ay):
    return lambda x, y: (ax * x + ay * y) >= abs(-ay * x + ax * y) - 0.02


snapshot()                                                    # 1 flat
counts = []
for sx, sy in DG:                                             # 2 blintz
    counts.append(do_fold(sx, sy, 1.0, +1, 2))
snapshot()
for a, b in AXV:                                              # 3 blintz
    counts.append(do_fold(a, b, 0.5, +1, 3))
snapshot()
for sx, sy in DG:                                             # 4 blintz
    counts.append(do_fold(sx, sy, 0.5, +1, 4))
snapshot()
for sx, sy in DG:                                             # 5 inner petals
    counts.append(do_fold(sx, sy, C5, -1, 5, only_last=4, region=quad(sx, sy)))
snapshot()
for a, b in AXV:                                              # 6 mid petals
    counts.append(do_fold(a, b, C6, -1, 6, only_last=3, region=wedge(a, b)))
snapshot()
for sx, sy in DG:                                             # 7 outer petals
    counts.append(do_fold(sx, sy, C7, -1, 7, only_last=2, region=quad(sx, sy)))
snapshot()
for a, b in AXV:                                              # 8 tips behind
    counts.append(do_fold(a, b, C8, +1, 8, exclude_last=(5, 6, 7), behind=True))
snapshot()

print("cells: %d   events: %d" % (len(cells), len(EVENTS)))
print("moved per event:", counts)
sym = all(counts[i] == counts[i - i % 4] for i in range(len(counts)))
print("4-fold symmetric:", sym)
for i, st in enumerate(STAGES):
    xs, L1 = [], []
    for cell in st:
        for p in cell["poly"]:
            q = mat_apply(cell["m"], p)
            xs.append(abs(q[0]))
            L1.append(abs(q[0]) + abs(q[1]))
    print("  stage %d  |x|max %.3f  L1max %.3f" % (i + 1, max(xs), max(L1)))

json.dump({"cells": [{"poly": c["poly"], "hist": c["hist"], "order": c["order"]}
                     for c in cells],
           "events": EVENTS,
           "stages": [[{"poly": c["poly"], "m": c["m"], "order": c["order"],
                        "flips": c["flips"]} for c in st] for st in STAGES]},
          open("sim2.json", "w"))
print("wrote sim2.json")
