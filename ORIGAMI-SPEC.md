# Origami Splash — Specification (ORIGAMI-SPEC.md)

**The new splash for `/`.** Concept: a dynamic origami visual — folded paper
pieces come together and unfold to form the name **TIFFANY**. Each letter is
a hand-folded paper construction: a bold geometric sans letterform built from
triangular facets, with crease lines between facets and paper shading that
reads as folds. The letters fly in from the sides, unfold (rotate out of the
fold), and their facets settle into place. This REPLACES the current layered
splash (aurora/node-field/herotext) — `index.astro` is being rewritten to
compose the origami system. The old `src/components/splash/` files stay in
the repo but are no longer imported.

## How it is built (who owns what)

| Piece | Owner | File |
|---|---|---|
| Shared choreography: tokens, `.og-*` classes, keyframes | orchestrator (already done) | `src/styles/global.css` |
| Composition: name h1, role line, section | orchestrator (already done) | `src/pages/index.astro` |
| Letters **T** (index 0) + **I** (index 1), both enter from LEFT | wW | `src/components/origami/letters-ti.astro` |
| Letters **F** (2) + **F** (3), enter LEFT / RIGHT | wX | `src/components/origami/letters-ff.astro` |
| Letters **A** (4) + **N** (5), enter RIGHT | wY | `src/components/origami/letters-an.astro` |
| Letter **Y** (6, RIGHT) + ambient **Backdrop** | wZ | `src/components/origami/letter-y.astro` + `src/components/origami/backdrop.astro` |

Agents edit ONLY their own file(s). Never touch global.css, index.astro,
BaseLayout, SideMenu, or any other file.

## The shared system (already in global.css — USE IT, don't redefine)

Classes available to every letter:
- `.og-letter` — wrapper span. Set inline `style="--og-i: N; --og-dir: ±1"`.
  Provides the unfold animation (delay = N*0.16s + 0.2s), direction
  `--og-dir` (-1 = enters from left, +1 = from right), and reduced-motion
  static fallback. Do NOT restyle the wrapper.
- `.og-facet` — a triangle polygon. Default fill = mid fold tone, crease
  stroke = thin dark line.
- `.og-facet--light` — lit paper (facing top-left light source).
- `.og-facet--dark` — shadowed fold (facing down/right).
- `.og-facet--accent` — terracotta (max ONE per letter, zero is fine).
- Facets settle with a small stagger after the letter lands
  (`--og-f: N` optional per facet for micro-delay; skip if you prefer).

Tokens (all derived from the earth palette, dark-mode safe):
`--og-facet-light`, `--og-facet-mid`, `--og-facet-dark`, `--og-crease`,
`--og-accent`.

## Letter geometry rules (HARD, all letters)

- viewBox: `0 0 <W> 140`. Fixed widths: **T=92, I=34, F=82, A=88, N=92,
  Y=86**.
- Cap top at **y=30**, baseline at **y=130** (cap height 100). Letters have
  no descenders; they align via flex-end.
- Letterform = **bold geometric sans** (think Space Grotesk 700 / Futura
  Bold proportions). Stem/bar weight ≈ **16–18 units**.
- The letter is drawn ONLY as triangles (`<polygon class="og-facet ...">`).
  No paths, no rects, no strokes on the silhouette outline — but every
  INTERIOR edge is a crease (the `.og-facet` stroke handles it).
- **Light source: top-left.** Facets angled up/left = `--light`, flat/mid =
  default, angled down/right = `--dark`. Every letter must have at least two
  `--light` and two `--dark` facets or it will read flat.
- Adjacent polygons share vertices exactly — no gaps, no overlaps.
- **The silhouette MUST read as the letter at a glance.** Trace the
  letterform first (stem, bars, diagonals, counter), then triangulate.
  The A needs a visible triangular counter (hole); F needs its mid bar to
  read; Y needs its fork; N needs its diagonal fold.
- Facet counts (guidance): T 7–10, I 3–5, F 8–12, A 9–13, N 9–13, Y 9–12.

## Per-letter anatomy (trace this, then facet it)

- **T (92 wide):** crossbar y≈30–46 full width; stem centered x≈38–54,
  y≈46–130. Crossbar: 2–3 facets (left light, right dark). Stem: 3–4
  vertical bands alternating light/mid/dark.
- **I (34):** single stem x≈9–25, y≈30–130, 3–5 vertical bands.
- **F (82):** stem x≈16–32 full height; top bar y≈30–46 x≈32–78; mid bar
  y≈70–86 x≈32–66. Stem bands + bar facets (top bar left light/right dark,
  mid bar darker on the underside).
- **A (88):** apex at (44,30); left diagonal down to (12,130), right
  diagonal to (76,130); crossbar y≈95–110 connecting diagonals. The counter
  (hole) is a triangle between the diagonals above the crossbar — leave it
  EMPTY. Left diagonal light, right diagonal dark, crossbar mid; one facet
  may be accent.
- **N (92):** left vertical x≈10–27, right vertical x≈65–82, full height;
  diagonal from (27,30) to (65,130). Diagonal is the fold: split into
  light/dark triangles.
- **Y (86):** stem x≈34–52, y≈75–130; two arms from (43,30): left arm down
  to (14,72), right arm to (72,72). Fork = the interesting part: arm facets
  light (left) / dark (right), stem bands.

## Backdrop (wZ, `backdrop.astro`)

A quiet ambient layer behind the name, `aria-hidden="true"`:
- 3–4 floating paper shards (small triangles, some terracotta, some
  paper-dark) drifting very slowly (30–60s loops, low opacity, transform
  only) — like loose scraps of the same paper.
- One soft warm halo behind the name area (radial gradient,
  `color-mix(in srgb, var(--accent-decorative) 8%, transparent)`).
- A fine paper-grain texture (feTurbulence data-URI like GrainOverlay, or a
  repeating gradient hatch) — very low opacity.
- All pointer-events none; z-index below the name (name is z 1).
- Its own `<style>` is fine (Astro scopes it). Tokens only.

## Composition (orchestrator, already in index.astro — do not touch)

```
<section class="origami">          (100svh, centered, bg token)
  <Backdrop />                     z 0
  <div class="og-center">          z 1
    <h1 class="og-name" aria-label="Tiffany">
      <LettersTI /><LettersFF /><LettersAN /><LetterY />   (all aria-hidden)
    </h1>
    <p class="og-role">Product Marketing Manager</p>       (fades in ~1.9s)
  </div>
  <ScrollCue />  <GrainOverlay />  (reused quiet layers)
</section>
```

## Rules

1. Tokens only — never hex. 2. Reduced motion: the shared system already
   renders a static composed frame — just don't add new unguarded
   animations. 3. Zero deps. 4. No photos/logos/branding. 5. Name + role
   line fixed (role: `Product Marketing Manager`, no industry qualifier).
6. Edit ONLY your file(s).

## Done means

`npm run build` exits 0 (ignore other agents' in-flight errors). Your
letters read clearly as their letterforms, use the shared `.og-facet`
classes, follow the geometry rules, and the whole name unfolds left-to-right
with coherent top-left lighting. Reply with: file path, per-letter facet
counts, the tone pattern you used, assumptions.
