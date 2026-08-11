"""Find the real crease each facet folds on, and where it sat before folding.

A fold is a reflection. If a facet's crease is known, the facet's position on
the flat sheet is simply its mirror image across that crease — so animating a
mirror-to-place swing about the crease IS the fold, not an impression of one.

Creases here are not invented: for every facet we look for the edge that runs
alongside a neighbouring facet (the extraction leaves a 2-3px ink gap between
touching facets, so "alongside" means within a few units for most of its
length). The edge with the longest such contact is the crease.

Hinge assignment, so the fold has a base to open from:
  star point -> hinged where it runs longest against a neighbour (its tuck)
  petal      -> hinged on the edge it shares with its own unit's star point
"""
import json
import math

VIEW = 400.0
CX = CY = VIEW / 2

facets = json.load(open("flower_facets.json"))


def segs(pts):
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def pt_seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def poly_dist(p, poly):
    return min(pt_seg_dist(p, a, b) for a, b in segs(poly))


def contact(edge, poly, tol=5.0, n=12):
    """How much of this edge runs alongside that polygon."""
    (ax, ay), (bx, by) = edge
    hits = 0
    for i in range(n + 1):
        t = i / n
        p = (ax + (bx - ax) * t, ay + (by - ay) * t)
        if poly_dist(p, poly) <= tol:
            hits += 1
    return (hits / (n + 1)) * math.hypot(bx - ax, by - ay)


def parse(d):
    body = d[1:].replace("Z", "").strip()
    return [tuple(float(v) for v in tok.strip().lstrip("L").split(",")) for tok in body.split(" L")]


for f in facets:
    f["pts"] = parse(f["d"])

# --- pick each facet's crease ------------------------------------------------
for f in facets:
    if f["kind"] == "petal":
        # the star point of the same unit
        other = next(o for o in facets if o["unit"] == f["unit"] and o["kind"] == "tip")
        best = max(segs(f["pts"]), key=lambda e: contact(e, other["pts"]))
    else:
        # the edge running longest alongside any other facet: this is where
        # the point slides under its neighbour, so it is the real crease
        others = [o for o in facets if o is not f]
        best = max(segs(f["pts"]),
                   key=lambda e: max(contact(e, o["pts"]) for o in others))
    (ax, ay), (bx, by) = best
    f["crease"] = best
    f["ox"], f["oy"] = round((ax + bx) / 2, 1), round((ay + by) / 2, 1)
    f["ang"] = round(math.degrees(math.atan2(by - ay, bx - ax)), 1)
    f["len"] = round(math.hypot(bx - ax, by - ay), 1)


def reflect(p, o, ang):
    a = math.radians(ang)
    dx, dy = p[0] - o[0], p[1] - o[1]
    ca, sa = math.cos(a), math.sin(a)
    # into crease frame, flip y, back out
    u, v = dx * ca + dy * sa, -dx * sa + dy * ca
    v = -v
    return (round(o[0] + u * ca - v * sa, 1), round(o[1] + u * sa + v * ca, 1))


for f in facets:
    o = (f["ox"], f["oy"])
    f["flat"] = "M" + " L".join("%g,%g" % reflect(p, o, f["ang"]) for p in f["pts"]) + " Z"
    print("%-5s u%d  crease at %6.1f,%-6.1f  angle %7.1f  len %5.1f" %
          (f["kind"], f["unit"], f["ox"], f["oy"], f["ang"], f["len"]))

for f in facets:
    del f["pts"], f["crease"]
json.dump(facets, open("flower_facets.json", "w"), indent=1)
print("\nwrote creases + unfolded positions")
