"""Turn the extracted facet map into the component's geometry.

extract_facets.py segments the official completed-assembly diagram into its
real facets. The model has four-fold symmetry, so one unit is enough: a star
point plus its petal, rotated four times. Taking one unit and rotating it also
sidesteps a quirk of the diagram, where an extra crease line splits one petal
in two but not the other three.

Each facet is hinged on the radius running through it: to fold, the facet is
mirrored across that radius (scaleY -1 in the hinge's frame) and swings open
into place. That is a real fold — the paper passes through edge-on — rather
than a shape morphing into another shape.
"""
import json
import math

VIEW = 400.0
CX = CY = VIEW / 2

facets = json.load(open("facets.json"))
by_id = {f["id"]: f for f in facets}

# one unit: the star point at ~4 deg and the petal at ~55 deg that hangs off it
UNIT = [("tip", 262), ("petal", 300)]


def rot(p, deg):
    a = math.radians(deg)
    x, y = p[0] - CX, p[1] - CY
    return (round(CX + x * math.cos(a) - y * math.sin(a), 1),
            round(CY + x * math.sin(a) + y * math.cos(a), 1))


def d_of(pts):
    return "M" + " L".join("%g,%g" % (x, y) for x, y in pts) + " Z"


def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


# Tone per unit follows one light from the top-left: the unit whose point aims
# up-left is lightest, the one aiming down-right deepest. Within a unit the
# petal is lifted a step off its point so the fold between them reads.
UNIT_TONE = {
    0: ("var(--og-paper-3)", "var(--og-paper-2)"),
    1: ("var(--og-paper-4)", "var(--og-paper-3)"),
    2: ("var(--og-paper-2)", "var(--og-paper-1)"),
    3: ("var(--og-paper-1)", "var(--og-paper-2)"),
}

out = []
for u in range(4):
    turn = 90 * u
    for kind, fid in UNIT:
        pts = [rot(p, turn) for p in by_id[fid]["pts"]]
        cx, cy = centroid(pts)
        hinge = round(math.degrees(math.atan2(cy - CY, cx - CX)), 1)
        tone = UNIT_TONE[u][0 if kind == "tip" else 1]
        # points land first, petals fold over them a beat later
        delay = round(u * 0.17 + (0.0 if kind == "tip" else 0.09), 2)
        out.append({"kind": kind, "unit": u, "d": d_of(pts),
                    "hinge": hinge, "tone": tone, "delay": delay})

json.dump(out, open("flower_facets.json", "w"), indent=1)
for f in out:
    print("%-5s u%d hinge %7.1f  delay %.2f  %s" % (f["kind"], f["unit"], f["hinge"], f["delay"], f["tone"]))
print("\n%d facets written to flower_facets.json" % len(out))
