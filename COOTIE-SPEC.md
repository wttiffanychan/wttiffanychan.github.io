# Cootie Catcher Splash — Specification (COOTIE-SPEC.md)

**Supersedes the fold-heavy part of ORIGAMI-SPEC.md.** Direction from
Tiffany: it is LESS important that the name looks like origami folds, and
MORE important that the DYNAMIC MOVEMENT comes together like origami — in
the shape of a cootie catcher (fortune teller).

## Concept

A wide diamond cootie catcher assembles first: four triangular paper flaps
fly in from the four corners and fold flat into the diamond, each catching
light as it lands (a sheen sweep). As the catcher completes, the letters of
**TIFFANY** fold in across its center (paper-flap swing, rotateY + slight
rotateZ), assembling into the name. The catcher dims behind the name; the
role line fades in last. The faceted letters stay as they are — the focus
is the FOLDING MOTION, not the letter texture.

## Timing (orchestrator-controlled, already in global.css)

- Flaps: fold in at 0.05 / 0.18 / 0.31 / 0.44s (0.85s each), sheen sweep
  mid-fold.
- Catcher dims to 0.32 opacity at 1.8s (so the name reads on top).
- Letters: fold in at `0.75s + i*0.16s` (i = 0..6), flap-swing motion.
- Role line: 2.4s. Reduced motion = fully static composed frame.

## Who owns what

| Piece | Owner | File |
|---|---|---|
| Shared choreography: `.cc-*` classes, keyframes, letter motion | orchestrator (done) | `src/styles/global.css` |
| Diamond container + composition | orchestrator (done) | `src/components/origami/catcher.astro` (imports the 4 flaps) + `src/pages/index.astro` |
| Flap **TL** (top-left triangle) | wW | `src/components/origami/flap-tl.astro` |
| Flap **TR** (top-right) | wX | `src/components/origami/flap-tr.astro` |
| Flap **BR** (bottom-right) | wY | `src/components/origami/flap-br.astro` |
| Flap **BL** (bottom-left) + center medallion | wZ | `src/components/origami/flap-bl.astro` (+ tiny center node inside it) |

Agents edit ONLY their own flap file. Never touch global.css, index.astro,
catcher.astro, the letter files, or each other's flaps.

## The shared system (already in global.css — USE IT)

- `.cc-flap` — wrapper span. Set inline `style="--cc-delay: 0.xx s"`.
  Provides fly-in + fold-flat animation and the sheen sweep. Do NOT restyle
  the wrapper; do NOT change `--cc-delay` beyond your assigned value.
- `.cc-flap-svg` — `viewBox="0 0 100 100"`, `preserveAspectRatio="none"`
  (fills the diamond; coordinates map 0-100 across the whole diamond).
- `.cc-paper` — a triangle polygon: mid paper tone + crease stroke.
- `.cc-paper--light` / `--dark` / `--accent` — tone variants (earth tokens,
  dark-mode safe).
- The 4 flaps tile the diamond; your polygon's apex is the center point.

## Flap geometry (exact — vertices in the 100x100 space)

The diamond: left corner (0,50), right (100,50), top (50,17.7), bottom
(50,82.3), center apex (50,50).

- **TL** (wW): triangle `(50,50) (0,50) (50,17.7)` — light source faces it.
- **TR** (wX): triangle `(50,50) (50,17.7) (100,50)`.
- **BR** (wY): triangle `(50,50) (100,50) (50,82.3)` — most shadowed.
- **BL** (wZ): triangle `(50,50) (50,82.3) (0,50)`.

## Per-flap design (the part YOU own)

Split your base triangle into TWO sub-triangles along a crease running from
the center apex to the midpoint of your base edge — like a folded flap. Then
assign tones for coherent top-left lighting:

- **TL:** mostly `--light`, one `--mid` (brightest flap).
- **TR:** `--mid` + one `--light` edge.
- **BR:** mostly `--dark`, one `--mid` (darkest flap).
- **BL:** `--mid` + one `--dark`.
- `--accent` allowed on ONE sub-triangle total across the whole catcher —
  give it to whichever flap you think deserves a quiet terracotta note
  (only ONE of you may use it; if in doubt, skip it).

Base-edge midpoints: TL base from (0,50) to (50,17.7) → midpoint
(25, 33.85). TR: (50,17.7)→(100,50) → (75, 33.85). BR:
(100,50)→(50,82.3) → (75, 66.15). BL: (50,82.3)→(0,50) → (25, 66.15).

So e.g. TL = polygons `(50,50) (0,50) (25,33.85)` and
`(50,50) (25,33.85) (50,17.7)` with your tone classes. Keep both edges
exactly shared with neighbors (no gaps/overlaps).

### Center medallion (wZ only)

Inside your BL flap, add a small diamond node at the center point where the
four flaps meet: a tiny `<polygon class="cc-paper cc-paper--accent"
points="47,50 50,47 53,50 50,53"/>` (or similar ~6-unit accent diamond) so
the catcher has a focal center like a real fortune teller's pin. z-order:
it may sit on top via a scoped style (`position` is not needed — later in
DOM paints over; your flap is rendered last among the four, so it naturally
overlaps).

## Rules

1. Tokens only — never hex. 2. No new animations outside the shared system
   (the sheen/fold/dim are global; your polygon just needs tones). 3. Zero
   deps. 4. No photos/logos. 5. `aria-hidden="true"` on your span + svg.
6. Edit ONLY your file. 7. Keep the skeleton's structure
   (`<span class="cc-flap" style="--cc-delay: ...">` + one svg).

## Done means

`npm run build` exits 0 (ignore other agents' in-flight errors). Your flap
is a two-tone folded triangle matching the geometry above, reads with
coherent top-left lighting, and the diamond closes cleanly. Reply with:
file path, your two polygons + tone classes, whether you used the accent,
assumptions.
