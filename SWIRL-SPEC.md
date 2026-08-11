# Splash — Floral Swirls, folded on screen (current state, Aug 2026)

**This is what `/` actually renders.** It supersedes the *composition* parts
of `SPLASH-SPEC.md`, `ORIGAMI-SPEC.md`, `COOTIE-SPEC.md` and `FOLD-SPEC.md` —
those stay as the record of how the splash got here, but where they disagree
with this file, this file is right.

## The model

**Floral Swirls**, by Madhura Gupta — <https://origami.me/floral-swirls/>.

- **Paper prep** — a circle, creased in half both ways, cut into four
  quarter-disc units.
- **One unit** — the two straight edges are creased in to the chord joining
  the arc's ends, and the corner is rabbit-eared with one flap tucked behind
  the other. That handedness is where the swirl comes from.
- **Assembly** — four units interlock, each slid under the next.

Two things about the finished model that a photograph alone will mislead you
about, and that earlier attempts here got wrong:

1. **Each unit's apex — the centre of the original circle — becomes a STAR
   TIP, and its arc — the circle's rim — becomes the CURVED PETAL at the
   middle.** That is why the model is a four-pointed star with petals
   swirling in the centre, not a round pinwheel.
2. **It is made of hard-edged facets.** Straight crease lines, sharp
   triangular points, distinct petals that visibly tuck under one another.
   Smooth blobs with the right outline do not read as folded paper.

## The geometry is traced, not drawn

Do not draw this by eye. The pipeline reads the model's own diagram:

```bash
cd site-v2
python3 tools/extract-facets.py    # diagram -> facets.json
python3 tools/build-flower.py      # one unit, rotated 4x -> flower_facets.json
python3 tools/find-creases.py      # adds each facet's crease + unfolded position
```

- `tools/extract-facets.py` classifies every pixel of
  `tools/reference/...assembly-step-completed.png` as ink / paper / ground,
  labels the connected paper patches — each patch **is** a facet of the real
  model — traces each boundary and simplifies it, then re-centres and scales
  into the 400x400 viewBox. It finds 9 patches: four star points, four
  petals, and one petal split in two by an extra crease line the diagram
  draws in only one place.
- `tools/build-flower.py` takes **one** unit (a star point plus its petal)
  and rotates it four times. Using one unit gives exact four-fold symmetry
  and sidesteps that split-petal quirk.
- `tools/trace-silhouette.py` samples the same diagram's outline as a
  radius-per-angle profile (tip 1.0, valley 0.58) — useful for checking
  proportions.

The eight resulting paths are pasted into `floral-swirl.astro`. Re-run the
tools and re-paste if the geometry ever needs to change.

## The fold

A fold is a reflection. So a facet's position on the flat sheet is exactly its
mirror image across its crease — and swinging it from there back across that
crease **is** the fold, with the paper passing edge-on through the midpoint.
Nothing is faked and no hinge is invented.

`tools/find-creases.py` finds each crease by measuring, for every edge of a
facet, how much of that edge runs alongside a neighbouring facet (the ink gap
left by the extraction is what "alongside" keys off). The longest such edge is
the crease:

- a **petal** hinges on the edge it shares with its own unit's star point
- a **star point** hinges where it runs longest under its neighbour — its tuck

It then mirrors each facet across its crease to get the unfolded position, and
that is where the animation starts.

Two beats per unit, staggered 0.22s apart:

1. **the paper folds shut on its creases** — `scaleY` runs -1 → 1 in the
   crease's own frame, `transform-origin` on the crease midpoint
2. **the folded unit swings into the assembly** — the `.fs-unit` wrapper goes
   from `rotate(26deg) scale(1.22)` to identity

Assembled by ~2.4s; it holds, then opens back out on a 24s loop.

**To play it once**, change `infinite` to `1` on `.fs-facet` and `.fs-unit`
and drop their closing keyframes.

### What did not work, so nobody retries it

- **Morphing a silhouette** (SMIL `<animate attributeName="d">`, or CSS
  `d: path()`). It requires every keyframe to share one path structure, which
  forces each unit down to a single smooth curve — and that is exactly how
  the model got flattened into four featureless blobs. Fidelity first: build
  the real facets, then move them.
- `path(var(--x))` does not parse; `path()` takes a string literal only, and
  an invalid `d` in a keyframe computes to `none` and blanks the shape.

## Composition (`src/pages/index.astro`)

```
<section class="origami">          100svh, centered, --bg
  <Backdrop />                     z0  warm halo, drifting shards, grain
  <FloralSwirl />                  z0  the flower + the veil under the name
  <div class="og-center">          z1
    <h1 class="og-name" aria-label="Tiffany"> …letters… </h1>
    <p class="og-role">Product Marketing Manager</p>
  </div>
  <ScrollCue />  <GrainOverlay />
</section>
```

The name folds in on top of the flower from 1.5s (`--og-base-delay`), landing
just after the flower assembles; the role line follows at 3.6s. All the name's
timing lives in the `--og-*-delay` / `--og-*-step` tokens in `global.css`.

`OrigamiShapes` (drifting crane / boat / cat silhouettes from an earlier
direction) is no longer composed in. The file still exists.

## Letters

`tools/gen-letters.py --write` regenerates the four letter components: bold
geometric sans on the shared grid (cap top y=30, baseline y=130, stroke
weight 18), each stem/bar/arm/diagonal a quad creased into two facets, 50
facets across the word (Aug 2026 cleanup: every bar/arm is a single fold,
only the longest quads — stems, A legs, N diagonal — split into two bands,
so the word reads as ~25 large folds). Edit the generator, not the vertices.

## Colour

Tokens only, both themes, all derived from `--bg`, `--text` and
`--accent-decorative`:

- `--og-paper-1…4` — the four units' paper tones, lightest to deepest,
  assigned by final position so the light stays top-left.
- `--og-ink` — `--text` warmed with 18% terracotta; the letters mix `--bg`
  with this rather than raw `--text`, keeping the name in the earth palette.
- `--og-facet-light / -mid / -dark` are overridden inside `.origami` to sit
  much closer to the ink than the site-wide defaults (55/70/85% ink), because
  the name sits on patterned paper rather than flat background — the word
  reads as ONE ink surface lifting off the petals, each fold as quiet
  shading. The letters' crease is a whisper (`--og-letter-crease`, 14% ink)
  so 50 facets do not read as 50 lines; the flower keeps its own
  `--og-crease`.

## Rules that still hold

1. Tokens only, never hex. 2. Reduced motion = the finished flower, static.
3. Zero dependencies. 4. Decorative layers `aria-hidden`; the `<h1>` carries
`aria-label="Tiffany"`. 5. Copy is fixed: `Tiffany` /
`Product Marketing Manager`.

## The rose (/splash-rose)

All nine steps of homemadeheather.com "A Rose", played as one continuous
fold of one sheet: crease, three blintz folds (square -> diamond -> square ->
diamond), three petal fold-outs, tips folded behind, hold, unfold in reverse.

Two things made this possible after several failures, both worth keeping:

1. **`tools/simfold.py` is a flat-fold simulation, not drawings.** Cells are
   split by each fold line's preimage under their own transform; blintz folds
   carry every layer beyond the line; a petal fold-out carries exactly the
   thickness of its ring inside its own WEDGE (axis flaps live in
   |cross| <= along — using a half-plane there grabs the neighbouring flaps
   and tears the model). Verified numerically: 4-fold symmetric move counts,
   silhouette extents exact (petal tips at exactly 2x their crease radii).
2. **`tools/export-rose.py` animates folds by NESTING, never by matrix
   interpolation.** One <g> per fold event, outermost = latest; each group
   swings `rotate(a) scaleY(1 -> -1) rotate(-a)` about its own crease, so
   the paper passes edge-on and lands exactly on the reflection. Identical
   keyframe function lists mean CSS interpolates component-wise — the matrix
   decomposition that produced garbage frames in earlier attempts never runs.

Petal proportions are the C5/C6/C7/C8 constants at the top of simfold.py;
re-run it and then export-rose.py after changing them. Current values:
`C5, C6, C7, C8 = 0.33, 0.33, 0.26, 0.42` (C5 lowered 0.38→0.33 in Aug 2026:
the silhouette valley floor is max(C5√2, C6√2) — the mid petal's shoulder
edge runs along x+y = 2·C6 and reaches C6√2 at 45°; with C5 > C6 the inner
petals poked past that shoulder and flattened the valley to 0.814. It now
sits at 0.707, the structural floor; the reference's 0.578 is unreachable
with these fold steps — reaching it would mean narrowing the petal flaps
themselves, which is the step-2–4 blintz geometry, not the C5–C8 constants.)

## Known open items

- ~~`ScrollCue` still says "scroll", but `/` is a single viewport with
  nothing below it. It should become a link into the site or come out.~~
  RESOLVED Aug 2026: it is now a quiet mono "work" link to `/projects` —
  a real `<a>`, no `aria-hidden`, token hover, reduced-motion static.
- The a-unfold sketch has a persisted light/dark toggle; the site itself is
  still OS-driven only.
