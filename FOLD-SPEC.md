# Fold-In Splash — Specification (FOLD-SPEC.md)

**Supersedes the animation parts of ORIGAMI-SPEC.md and COOTIE-SPEC.md.**
Tiffany's direction: the splash background shows easy-origami shapes (from
origami.me), and the letters of **TIFFANY** are assembled as the paper
pieces FOLD INTO each letter — the facets fly in from scattered positions
and click together to form the letterform, letter by letter, left to right.

The cootie-catcher diamond is REMOVED from the composition (files stay in
the repo, unused). The `cc-*` CSS stays in global.css but is inert.

## Composition (orchestrator, already done — do not touch)

```
<section class="origami">
  <Backdrop />          (existing: halo, drifting shards, grain)
  <OrigamiShapes />     (NEW — the easy-origami silhouettes, see below)
  <div class="og-center">
    <h1 class="og-name" aria-label="Tiffany">
      <LettersTI /><LettersFF /><LettersAN /><LetterY />
    </h1>
    <p class="og-role">Product Marketing Manager</p>
  </div>
  <ScrollCue />  <GrainOverlay />
</section>
```

## Letter assembly (the shared system, already in global.css)

The `.og-letter` wrapper is now STATIC (just positions the letter; no
wrapper animation). The assembly happens at FACET level:

- Every facet animates `og-facet-in`: from
  `translate(var(--og-fx), var(--og-fy)) rotate(var(--og-fr))
  scale(var(--og-fs))` with `opacity: 0`, to `opacity: 1; transform: none`.
- Delay: `calc(var(--og-i,0)*0.3s + var(--og-f,0)*0.05s + 0.15s)` — letters
  assemble one after another (0.3s apart), facets within a letter click in
  sequentially (50ms apart).
- `transform-box: fill-box; transform-origin: center;` is set so each facet
  rotates around its own center. Do not override these.

## Your job per letter (edit ONLY your file)

For EACH `<polygon class="og-facet ...">` in your letter file, add an inline
`style` with:
- `--og-f: N` — sequential index 0,1,2,3… (already present on some facets;
  make it complete and sequential per letter).
- `--og-fx: Xrem` and `--og-fy: Yrem` — where the paper piece comes FROM,
  in rem (±1 to ±3 is good; think of it as the piece flying in from a
  scattered position).
- `--og-fr: Zdeg` — its starting rotation (±15° to ±50°).
- `--og-fs: 0.5–0.8` — starting scale (smaller = arrives from farther).

Scatter pattern (makes the letter read as pieces folding together):
alternate directions per facet — facet 0 from left, 1 from right, 2 from
below, 3 from above, 4 from left… so the letter visibly assembles from
papers folding in from all sides. Vary magnitudes a little so it feels
organic, not mechanical. Example for one facet:
`style="--og-f: 2; --og-fx: 1.8rem; --og-fy: 2.2rem; --og-fr: 34deg; --og-fs: 0.6"`

Do NOT change: the letterforms/vertices, facet tone classes, viewBox, span
classes, or aria-hidden. Do NOT add or remove facets.

## OrigamiShapes (w12) — file `src/components/origami/origami-shapes.astro`

A background layer of 5–6 recognizable easy-origami silhouettes, drawn as
simple inline SVG paths (clean geometric abstractions of the classic forms —
NOT copied artwork; you are drawing the ESSENCE of the shape):

- **Paper crane** (classic: head, wings, tail silhouette)
- **Paper boat** (hull + sail triangle)
- **Butterfly** (two wing triangles meeting at a body line)
- **Heart** (folded heart: two lobes + bottom point)
- **Paper plane** (dart silhouette)
- Optional 6th: **cat face** or **frog** (simple, geometric)

Each shape:
- One `<svg>` with a single filled `<path>` (or 2-3 paths max), using the
  `--og-facet-mid` / `--og-facet-dark` / `--accent-decorative` tokens at
  LOW opacity (0.08–0.16 — background whisper, not focal).
- Positioned around the edges (corners / mid-edges), sized 3–7rem.
- A slow drift animation (transform-only: translate ±1–2rem, rotate
  ±6–12°, 30–70s ease-in-out infinite alternate, staggered delays).
- `aria-hidden="true"`, `pointer-events: none`, `z-index: 0` (behind the
  name which is z 1; the backdrop is also z 0, order in DOM decides).
- Reduced motion: shapes render static (no animation).

Structure: a single `<div class="og-shapes" aria-hidden="true">` wrapping
all shape svgs; your own `<style>` in the file is fine (Astro scopes it).

## Rules

1. Tokens only — never hex. 2. Zero deps. 3. No photos/logos/branding.
4. `aria-hidden` everywhere decorative. 5. Reduced motion = static composed
   frame. 6. Edit ONLY your file(s).

## Done means

`npm run build` exits 0 (ignore other agents' in-flight errors). Your
letter's facets fly in from scattered directions and assemble into a clear
letterform; your shapes read as quiet origami in the background. Reply
with: file path, per-facet scatter values (or shape list for w12), any
assumptions.
