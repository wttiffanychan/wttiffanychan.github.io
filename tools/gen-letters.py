"""Generate the origami letterforms for TIFFANY.

Each letter is drawn as a bold geometric sans built from quads (stems, bars,
diagonals, arms), and every quad is split along a diagonal into two triangular
facets — the fold. Tone follows a single top-left light: the facet on the
up-left side of a fold catches the light, the one on the down-right side falls
into shadow.

Grid: viewBox "0 0 W 140", cap top y=30, baseline y=130, stroke weight 18.
Building the letter from real quads first (instead of free-hand triangles) is
what keeps the silhouette reading as the letter.
"""
import math

TOP, BOT, W = 30.0, 130.0, 18.0


def quad(*pts):
    return list(pts)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def split_v(q, n):
    """Split a quad into n bands along its p0→p3 / p1→p2 direction."""
    (a, b, c, d) = q
    out = []
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        lerp = lambda p, r, t: (p[0] + (r[0] - p[0]) * t, p[1] + (r[1] - p[1]) * t)
        out.append([lerp(a, d, t0), lerp(b, c, t0), lerp(b, c, t1), lerp(a, d, t1)])
    return out


def split_h(q, n):
    """Split a quad into n bands along its p0→p1 / p3→p2 direction."""
    (a, b, c, d) = q
    out = []
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        lerp = lambda p, r, t: (p[0] + (r[0] - p[0]) * t, p[1] + (r[1] - p[1]) * t)
        out.append([lerp(a, b, t0), lerp(a, b, t1), lerp(d, c, t1), lerp(d, c, t0)])
    return out


# ---------------------------------------------------------------- letterforms
# Each entry: (width, [ (quad, n_bands, axis, tone_pair) ... ])
#
# Tone pair = (lit facet, shadowed facet) for every fold in that part. One
# light source, top-left, applied as art direction rather than as a
# simulation: bars face up so they are the lightest, stems face sideways so
# they sit mid-to-dark, a diagonal running down-right catches the light while
# one running down-left falls away from it.
BAR = ("light", "mid")
STEM = ("mid", "dark")
# Band counts are kept LOW on purpose: the name sits on the faceted floral
# swirl, so the letters must read as a few quiet, large folds rather than as
# a second layer of busy paper. Each quad = one crease = one lit/shadow pair;
# only the longest quads (stems, legs, the N diagonal) split into two bands.
LETTERS = {
    "T": (92, [
        (rect(0, TOP, 92, TOP + W), 1, "h", BAR),         # crossbar — one fold
        (rect(37, TOP + W, 55, BOT), 2, "v", STEM),       # stem
    ]),
    "I": (34, [
        (rect(8, TOP, 26, BOT), 2, "v", STEM),
    ]),
    "F": (78, [
        (rect(0, TOP, 18, BOT), 2, "v", STEM),            # stem
        (rect(18, TOP, 74, TOP + W), 1, "h", BAR),        # top bar — one fold
        (rect(18, 72, 62, 90), 1, "h", BAR),              # mid bar — one fold
    ]),
    "A": (92, [
        # Both legs run the full width of the apex (37→55) so their edges stay
        # parallel — they overlap in a triangle at the top, which is exactly
        # how the apex of an A is built, and the counter opens up below it.
        (quad((37, TOP), (55, TOP), (18, BOT), (0, BOT)), 2, "v", BAR),   # left leg
        (quad((37, TOP), (55, TOP), (92, BOT), (74, BOT)), 2, "v", STEM),  # right leg
        (rect(20, 92, 72, 110), 1, "h", BAR),                              # crossbar — one fold
    ]),
    "N": (94, [
        (rect(0, TOP, 18, BOT), 1, "v", STEM),             # left stem — one fold
        (rect(76, TOP, 94, BOT), 1, "v", STEM),            # right stem — one fold
        (quad((18, TOP), (36, TOP), (94, BOT), (76, BOT)), 2, "v", BAR),  # diagonal
    ]),
    "Y": (86, [
        (quad((0, TOP), (18, TOP), (52, 76), (34, 76)), 1, "v", BAR),   # left arm — one fold
        (quad((68, TOP), (86, TOP), (52, 76), (34, 76)), 1, "v", STEM),  # right arm — one fold
        (rect(34, 76, 52, BOT), 1, "v", STEM),                           # stem — one fold
    ]),
}

# no accent facet in the letters — see floral-swirl.astro's hub pin
ACCENT = None


def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def facets(q, i):
    """Split a quad into two triangles; alternate which diagonal is used so
    the creases don't all lean the same way."""
    a, b, c, d = q
    if i % 2 == 0:
        return [(a, b, c), (a, c, d)]
    return [(a, b, d), (b, c, d)]


def lit_score(tri, q):
    """How much of the light a facet catches, within its own quad. On a wide
    quad the fold reads top-vs-bottom, on a tall one left-vs-right; the
    weaker axis still breaks ties so no two facets ever score the same."""
    xs = [p[0] for p in q]
    ys = [p[1] for p in q]
    wide = (max(xs) - min(xs)) >= (max(ys) - min(ys))
    qc, tc = centroid(q), centroid(tri)
    wx, wy = (0.35, 1.0) if wide else (1.0, 0.35)
    return wx * (qc[0] - tc[0]) + wy * (qc[1] - tc[1])


def scatter(n):
    """Deterministic 'thrown on the table' start position for facet n —
    golden-angle spread so consecutive pieces never fly in from the same
    place, distance and spin varied by index."""
    a = math.radians((n * 137.508) % 360)
    dist = 1.5 + 1.4 * (((n * 7) % 5) / 4.0)
    rot = -46 + ((n * 53) % 92)
    scale = 0.5 + (((n * 3) % 4) / 4.0) * 0.28
    return (round(math.cos(a) * dist, 2), round(math.sin(a) * dist, 2), rot, round(scale, 2))


def f(v):
    s = "%.1f" % v
    return s.rstrip("0").rstrip(".") if "." in s else s


def render(letter, index, direction):
    width, parts = LETTERS[letter]
    quads = []
    for q, n, axis, tones in parts:
        for band in (split_v(q, n) if axis == "v" else split_h(q, n)):
            quads.append((band, tones))

    rows, k = [], 0
    for qi, (q, tones) in enumerate(quads):
        tris = facets(q, qi)
        # the facet catching more light gets the lighter tone of the pair
        tris.sort(key=lambda t: lit_score(t, q), reverse=True)
        for tri, t in zip(tris, tones):
            cls = "og-facet" if t == "mid" else "og-facet og-facet--%s" % t
            dx, dy, rot, sc = scatter(k)
            pts = " ".join("%s,%s" % (f(p[0]), f(p[1])) for p in tri)
            rows.append((cls, k, dx, dy, rot, sc, pts))
            k += 1

    out = ['<span class="og-letter" style="--og-i: %d; --og-dir: %d" aria-hidden="true">' % (index, direction),
           '  <svg viewBox="0 0 %d 140">' % width]
    for cls, kk, dx, dy, rot, sc, pts in rows:
        out.append(
            '    <polygon class="%s" style="--og-f: %d; --og-fx: %srem; --og-fy: %srem; '
            '--og-fr: %ddeg; --og-fs: %s" points="%s" />' % (cls, kk, dx, dy, rot, sc, pts)
        )
    out.append("  </svg>")
    out.append("</span>")
    return "\n".join(out), len(rows)


# which letters live in which component, and the index / entry direction each
# one carries (index drives its place in the fold-in order)
FILES = {
    "letters-ti.astro": ("Origami letters T (index 0) and I (index 1).",
                         [("T", 0, -1), ("I", 1, -1)]),
    "letters-ff.astro": ("Origami letters F (index 2, enters from the left) and "
                         "F (index 3, from the right).",
                         [("F", 2, -1), ("F", 3, 1)]),
    "letters-an.astro": ("Origami letters A (index 4) and N (index 5), both "
                         "entering from the right.",
                         [("A", 4, 1), ("N", 5, 1)]),
    "letter-y.astro": ("Origami letter Y (index 6) — the last letter to land.",
                       [("Y", 6, 1)]),
}

HEAD = """---
// %s
//
// Bold geometric sans on the shared grid (cap top y=30, baseline y=130,
// stroke weight 18). Each stem, bar, arm and diagonal is a quad split along
// a crease into two triangular facets; the facet on the lit side of the fold
// takes the lighter tone of its pair. One light source, top-left: bars face
// up and read lightest, stems face sideways and sit mid-to-dark.
//
// Every facet carries its own scatter origin (--og-fx/fy/fr/fs) so the paper
// flies in from a different place and folds into position — see SWIRL-SPEC.md.
// GENERATED by tools/gen-letters.py — edit the letterform definition there and
// re-run `python3 tools/gen-letters.py --write`, don't nudge vertices by hand
// or the silhouette drifts.
---

"""

if __name__ == "__main__":
    import os
    import sys

    write = "--write" in sys.argv
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "src", "components", "origami")

    for fname, (desc, plan) in FILES.items():
        blocks, total = [], 0
        for name, idx, d in plan:
            markup, count = render(name, idx, d)
            blocks.append("<!-- %s — %d facets -->\n%s" % (name, count, markup))
            total += count
        body = HEAD % desc + "\n".join(blocks) + "\n"
        if write:
            with open(os.path.join(dest, fname), "w") as fh:
                fh.write(body)
            print("wrote %s (%d facets)" % (fname, total))
        else:
            print(body)

    if not write:
        print("<!-- pass --write to overwrite the .astro components -->")
