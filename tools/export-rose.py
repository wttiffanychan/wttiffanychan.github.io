"""Turn the flat-fold simulation into an animated Astro component.

The trick that makes the animation exact: transforms of nested SVG groups
compose, and a cell's simulated transform is the product of the reflections
of the folds it took part in — latest applied last. So the DOM tree mirrors
the fold history: one <g> per fold EVENT, outermost = latest fold, and each
group animates a single hinge swing about its own crease,

    rotate(theta) scaleY(1 -> -1) rotate(-theta)   about a point on the line

which passes through scaleY(0) — the paper edge-on — and lands exactly on
the reflection. The function lists in the keyframes are identical, so CSS
interpolates component-wise: no matrix decomposition, no garbage frames.
Cells sharing a fold-history suffix share the group chain; a history is
nested reversed (latest event outermost) so left-composition comes out right.

Timing: one shared timeline, no per-element delays — the seven fold steps fire
in sequence and the rose HOLDS. The animation is a one-shot entrance: it runs
once (iteration-count 1, fill-mode forwards) and its 100% frame is exactly the
finished pose the inline styles carry, so the page ends where the static build
began. There is no unfold and no loop: the old 26s cycle folded, held, then
unfolded, which meant a return visit could land mid-unfold and see a different
picture. Now every load plays the same fold and stops on the same rose.

Fill tone steps up a ladder each time a cell's paper is turned over (at the
edge-on moment, so the switch is invisible) and holds the top rung.

Paint order: siblings are sorted by the maximum FINAL stacking order in their
subtree — right for the finished rose and the long hold; brief mid-sequence
tone overlaps are accepted. Step-8 material has negative order (folded
behind) and so paints first.
"""
import json
import math

d = json.load(open("sim2.json"))
CELLS, EVENTS = d["cells"], d["events"]

S = 92.0
C = 200.0

# ---- timeline -------------------------------------------------------------
# The windows below are the ORIGINAL 26s loop's fold percentages, kept as the
# record of the shape of the sequence. The one-shot timeline drops the hold
# and the unfold, so the fold that used to finish at 53% now finishes at 100%:
# every window is rescaled by SCALE.
#
# DURATION is the only wall-clock knob. The keyframes are pure percentages, so
# the seven steps keep their proportions and their rhythm at any duration —
# changing this number stretches or compresses the whole fold evenly and needs
# no other edit. 13.78s reproduced the original loop's fold-in exactly; 9s is
# the same fold about a third quicker, which reads better against the name
# folding in at 1.5s.
FOLD = {2: (4.0, 9.5), 3: (11.5, 17.0), 4: (19.0, 24.5), 5: (26.5, 32.0),
        6: (34.0, 39.5), 7: (41.5, 47.0), 8: (49.0, 53.0)}
FOLD_END = 53.0
SCALE = 100.0 / FOLD_END
DURATION = "9s"
# The old unfold windows, kept only as a record of what was removed:
# UNFOLD = {8: (77.0, 80.0), 7: (80.8, 84.0), 6: (84.8, 87.8), 5: (88.6, 91.2),
#           4: (91.8, 94.0), 3: (94.6, 96.7), 2: (97.2, 99.3)}

# the flat sheet, for the prep creases
LO, HI = C - S, C + S


def f(v):
    s = "%.2f" % v
    return s.rstrip("0").rstrip(".") if "." in s else s


def p(v):
    """original-loop percent -> one-shot percent"""
    return v * SCALE


# ---- per-event hinge parameters -------------------------------------------
for e in EVENTS:
    a, b, c = e["a"], e["b"], e["c"]
    n = math.hypot(a, b)
    nx, ny, cc = a / n, b / n, c / n
    ox, oy = C + S * nx * cc, C + S * ny * cc          # point on the line
    theta = math.degrees(math.atan2(nx, -ny))          # line direction (-ny,nx)
    e["ox"], e["oy"], e["theta"] = round(ox, 2), round(oy, 2), round(theta, 2)

# ---- tree: reversed history, latest event outermost ------------------------
TREE = {"eid": None, "children": {}, "paths": []}
for cell in CELLS:
    node = TREE
    for eid in reversed(cell["hist"]):
        node = node["children"].setdefault(eid, {"eid": eid, "children": {}, "paths": []})
    node["paths"].append(cell)


def max_order(node):
    vals = [c["order"] for c in node["paths"]]
    vals += [max_order(ch) for ch in node["children"].values()]
    return max(vals)


# ---- fill-tone keyframes per distinct fold-step sequence -------------------
SEQS = {}
for cell in CELLS:
    seq = tuple(EVENTS[eid]["step"] for eid in cell["hist"])
    SEQS.setdefault(seq, len(SEQS))


def tone_kf(seq, idx):
    """Tone steps UP at each fold's edge-on moment and holds the top rung.

    The last mark is the cell's final tone, min(len(seq), 4) — the same rung
    the inline fill carries — held to 100%, so the animation ends on exactly
    the static picture."""
    marks = [(0.0, 0)]
    for i, s in enumerate(seq):
        marks.append((p((FOLD[s][0] + FOLD[s][1]) / 2.0), i + 1))
    rows = []
    for j in range(len(marks) - 1):
        t0, k = marks[j]
        t1 = marks[j + 1][0]
        a = f(t0 + (0.12 if j else 0.0))
        b = f(max(t0, t1 - 0.12))
        rows.append("    %s%%, %s%% { fill: var(--rz-p%d); }" % (a, b, min(k, 4)))
    t0, k = marks[-1]
    rows.append("    %s%%, 100%% { fill: var(--rz-p%d); }"
                % (f(min(t0 + 0.12, 100.0)), min(k, 4)))
    return "  @keyframes rt-%d {\n%s\n  }" % (idx, "\n".join(rows))


# ---- keyframes per fold step ----------------------------------------------
def step_kf(s):
    """Flat until the step's window, one hinge swing, then held to 100%.

    The 100% frame is the reflection R — the same transform the group carries
    inline — so fill-mode forwards lands on the finished pose exactly."""
    I = "rotate(var(--a)) scaleY(1) rotate(calc(-1 * var(--a)))"
    R = "rotate(var(--a)) scaleY(-1) rotate(calc(-1 * var(--a)))"
    fs, fe = p(FOLD[s][0]), p(FOLD[s][1])
    hold = ("    100%% { transform: %s; }" % R if fe >= 99.995
            else "    %s%%, 100%% { transform: %s; }" % (f(fe), R))
    return ("  @keyframes rf-s%d {\n"
            "    0%%, %s%% { transform: %s; }\n"
            "%s\n  }" % (s, f(fs), I, hold))


# ---- emit the tree ---------------------------------------------------------
def emit_path(cell, ind):
    pts = " L".join("%s,%s" % (f(C + S * x), f(C + S * y)) for x, y in cell["poly"])
    seq = tuple(EVENTS[eid]["step"] for eid in cell["hist"])
    k = min(len(seq), 4)
    anim = "animation-name: rt-%d; " % SEQS[seq] if seq else ""
    return ('%s<path class="rp" style="fill: var(--rz-p%d); %s" d="M%s Z" />'
            % (ind, k, anim, pts))


def emit_node(node, ind):
    items = [(c["order"], "p", c) for c in node["paths"]]
    items += [(max_order(ch), "g", ch) for ch in node["children"].values()]
    items.sort(key=lambda t: t[0])
    rows = []
    for _, kind, obj in items:
        if kind == "p":
            rows.append(emit_path(obj, ind))
        else:
            e = EVENTS[obj["eid"]]
            folded = ("transform: rotate(%sdeg) scaleY(-1) rotate(%sdeg);"
                      % (f(e["theta"]), f(-e["theta"])))
            rows.append('%s<g class="rf" style="--a: %sdeg; transform-origin: %spx %spx; '
                        'animation-name: rf-s%d; %s">'
                        % (ind, f(e["theta"]), f(e["ox"]), f(e["oy"]), e["step"], folded))
            rows.append(emit_node(obj, ind + "  "))
            rows.append("%s</g>" % ind)
    return "\n".join(rows)


body_svg = emit_node(TREE, "      ")

# ---- the flat sheet's prep creases -----------------------------------------
# The creases a folder puts in before any paper moves: both diagonals, both
# mid-lines, and the blintz square of step 2 (the four lines joining adjacent
# edge midpoints — where the corners fold to the centre). They belong to the
# flat sheet, so they fade out during the first fold and the finished rose has
# none, which is exactly what the static render shows.
prep_d = " ".join([
    "M%s,%s L%s,%s" % (f(LO), f(LO), f(HI), f(HI)),
    "M%s,%s L%s,%s" % (f(HI), f(LO), f(LO), f(HI)),
    "M%s,%s L%s,%s" % (f(C), f(LO), f(C), f(HI)),
    "M%s,%s L%s,%s" % (f(LO), f(C), f(HI), f(C)),
    "M%s,%s L%s,%s L%s,%s L%s,%s Z" % (f(C), f(LO), f(HI), f(C),
                                       f(C), f(HI), f(LO), f(C)),
])
prep_svg = ('      <g class="rz-prep">\n'
            '        <path d="%s" />\n'
            '      </g>' % prep_d)

# ---- the one-shot fold-in --------------------------------------------------
kf = [step_kf(s) for s in sorted(FOLD)]
kf += [tone_kf(seq, idx) for seq, idx in
       sorted(SEQS.items(), key=lambda kv: kv[1]) if seq]
kf.append("  @keyframes rz-lean {\n"
          "    0% { transform: rotate(-8deg) scale(1); }\n"
          "    " + f(p(FOLD[8][0])) + "%, 100% "
          "{ transform: rotate(-6deg) scale(1.58); }\n  }")
kf.append("  @keyframes rz-crease {\n"
          "    0%, " + f(p(FOLD[2][0])) + "% { opacity: 0.55; }\n"
          "    " + f(p(FOLD[3][0])) + "%, 100% { opacity: 0; }\n  }")

anim_css = """<style is:global>
  /* === THE FOLD, ONE SHOT ===
     The sheet folds itself into the rose once and stops. Iteration count 1
     and fill-mode forwards, and every keyframe list ends on the finished
     pose — the same transform, the same tone rung, the same lean that the
     inline styles carry — so the moment the animation ends the page is the
     static rose it used to render immediately. No unfold, no loop, no
     negative delays: there is no phase to arrive in the middle of, and a
     second visit plays the identical fold.

     The seven steps hold the original loop's proportions — the windows are
     the old percentages rescaled so the fold that finished at 53% now
     finishes at 100%. Duration __DUR__ is the whole of the wall-clock: the
     fold is deliberate but does not outstay the name, which folds in at
     1.5s. Set DURATION in tools/export-rose.py to re-time it; nothing else
     changes, the keyframes being percentages.

     Global on purpose: animation-name is written inline on every group and
     path by the exporter, where Astro's scoping cannot follow it, so the
     keyframes have to keep their literal names. Every selector here is
     confined to .rz-wrap.

     Reduced motion: no animation properties are declared at all, so the rose
     renders as the finished still — the behaviour those users already had. */
  @media (prefers-reduced-motion: no-preference) {
    .rz-wrap .rz-sheet,
    .rz-wrap .rz-prep,
    .rz-wrap .rf,
    .rz-wrap .rp {
      animation-duration: __DUR__;
      animation-timing-function: ease-in-out;
      animation-iteration-count: 1;
      animation-fill-mode: forwards;
    }
    .rz-wrap .rz-sheet { animation-name: rz-lean; }
    .rz-wrap .rz-prep { animation-name: rz-crease; }

__KF__
  }
</style>""".replace("__DUR__", DURATION).replace(
    "__KF__", "\n".join("  " + ln if ln.strip() else ln
                        for block in kf for ln in block.split("\n")))

component = """---
// OrigamiRose — a square of paper folded into a rose, all nine steps of the
// reference (homemadeheather.com "A Rose"), simulated and then animated as
// real folds.
//
// GEOMETRY: tools/simfold.py is a flat-fold simulation. The sheet starts as
// one cell; at every fold each cell is split by the preimage of the fold
// line under its own transform, and the pieces on the folding side are
// reflected. Blintz folds (steps 2-4) carry every layer beyond the line;
// petal fold-outs (steps 5-7) carry exactly the thickness of their ring
// inside its own wedge; step 8 folds the diamond's tips behind. The
// simulation is verified numerically (silhouette square -> diamond ->
// square -> diamond; petals to exactly 2x their crease radii; 4-fold
// symmetric move counts) and visually against the reference diagram.
//
// MOTION: the sheet folds itself into the rose ONCE and then holds forever.
// Transforms of nested groups compose, and a cell's simulated position is the
// product of the reflections of the folds that moved it — so the DOM tree
// mirrors the fold history (one <g> per fold event, outermost = latest) and
// each group animates a single hinge swing about its own crease,
// rotate(a) scaleY(1 -> -1) rotate(-a), which passes through the paper
// edge-on and lands exactly on the reflection.
//
// Every element's inline style is the FINISHED rose, and every keyframe list
// ends on that same value: the folded transform, the top rung of the tone
// ladder, the sheet leaned to rotate(-6deg) scale(1.58), the prep creases at
// opacity 0. With iteration-count 1 and fill-mode forwards, the frame the
// animation stops on IS the static picture this file used to render
// immediately — so the guarantee still holds: one fold, always the same one,
// and the same rose afterwards on every return and in any tab. The old loop's
// hold-and-unfold is gone; that was the part that made the picture depend on
// when you arrived.
//
// Reduced motion declares no animation properties at all, so those users get
// the finished still — exactly what they had before.
//
// GENERATED by tools/export-rose.py — edit that and re-run, not this file.
---

<div class="rz-wrap" aria-hidden="true">
  <svg viewBox="0 0 400 400" role="presentation">
    <g class="rz-sheet">
%s
%s
    </g>
  </svg>
  <div class="rz-veil"></div>
</div>

<style>
  .rz-wrap {
    /* the paper's tone ladder: one step per time the paper is turned over */
    --rz-p0: color-mix(in srgb, var(--bg) 84%%, var(--accent-decorative) 16%%);
    --rz-p1: color-mix(in srgb, var(--bg) 72%%, var(--accent-decorative) 28%%);
    --rz-p2: color-mix(in srgb, var(--bg) 62%%, var(--accent-decorative) 38%%);
    --rz-p3: color-mix(in srgb, var(--bg) 52%%, var(--accent-decorative) 48%%);
    --rz-p4: color-mix(in srgb, var(--bg) 42%%, var(--accent-decorative) 58%%);
    position: absolute;
    left: 50%%;
    top: 50%%;
    width: min(108vmin, 56rem);
    aspect-ratio: 1;
    transform: translate(-50%%, -50%%);
    z-index: 0;
    pointer-events: none;
  }
  .rz-wrap svg { display: block; width: 100%%; height: 100%%; overflow: visible; }
  .rz-sheet {
    transform-box: view-box;
    transform-origin: 200px 200px;
    /* where the fold ends, and what a still render shows */
    transform: rotate(-6deg) scale(1.58);
  }

  .rf { transform-box: view-box; }

  /* the flat sheet's own crease pattern — both diagonals, both mid-lines and
     the blintz square of step 2. It belongs to the paper before anything is
     folded, so it is invisible by default: the finished rose has no creases,
     and neither does a still or reduced-motion render. */
  .rz-prep {
    fill: none;
    stroke: var(--og-crease);
    stroke-width: 0.9;
    stroke-dasharray: 5 6;
    stroke-linejoin: round;
    vector-effect: non-scaling-stroke;
    transform-box: view-box;
    opacity: 0;
  }
  .rp {
    stroke: var(--og-crease);
    stroke-width: 0.55;
    stroke-linejoin: round;
    vector-effect: non-scaling-stroke;
  }

  .rz-veil {
    position: absolute;
    inset: 0;
    background: radial-gradient(
      ellipse 54%% 15%% at 50%% 50%%,
      color-mix(in srgb, var(--bg) 50%%, transparent) 0%%,
      color-mix(in srgb, var(--bg) 26%%, transparent) 52%%,
      transparent 80%%
    );
  }

  /* The fold itself lives in the global block below — the keyframes have to
     keep their literal names to match the inline animation-name values. */
</style>

%s

<script>
  // Back/forward-cache restores a frozen DOM snapshot, which can predate the
  // latest design — reload so the page is always current.
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) location.reload();
  });
</script>
""" % (body_svg, prep_svg, anim_css)

out = "/Users/tiffany/Claude/Projects/HerdrProjects/site-v2/src/components/origami/origami-rose.astro"
open(out, "w").write(component)


def count_nodes(node):
    return 1 + sum(count_nodes(ch) for ch in node["children"].values())


print("paths: %d   groups: %d   tone sequences: %d"
      % (len(CELLS), count_nodes(TREE) - 1, len(SEQS)))
print("wrote origami-rose.astro")
