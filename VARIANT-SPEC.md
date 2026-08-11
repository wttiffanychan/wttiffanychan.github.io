# Splash Variants — Specification (VARIANT-SPEC.md)

**Exploratory previews only.** The current splash (`/`) stays untouched.
Four alternative splash designs, each a preview route that renders the same
full-viewport hero with a DIFFERENT lettering treatment for the name and a
different visual language. Tiffany reviews them, picks one, and the winner
gets promoted into `src/pages/index.astro`.

## How to view

Build then visit: `/splash-a`, `/splash-b`, `/splash-c`, `/splash-d`.

## Directional inspiration (NOT to be copied)

Tiffany's taste references: **wabi-sabi, midcentury modern, Issey Miyake,
Miu Miu, Prada**. These are DIRECTION ONLY. Do NOT incorporate any of their
branding — no logos, no marks, no product shapes, no names. You are
translating the *feeling*: restraint, imperfection, geometric optimism,
folded structure, editorial precision.

## Shared rules (all variants — same as SPLASH-SPEC.md)

1. Tokens only — never hardcoded hex. Earth palette from global.css
   (sand / terracotta / olive sage / taupe / umber, auto light+dark).
2. `prefers-reduced-motion`: fully-composed static frame, no animation.
3. Zero dependencies — vanilla CSS/JS/SVG. No canvas libs, no GSAP.
4. Performance: pause rAF on `document.hidden`; cap DPR at 2; animate
   transform/opacity only; calm, not busy.
5. `aria-hidden="true"` on all decorative layers. No photos, no logos.
6. Self-contained: your variant page = markup + `<style>` + optional
   `<script>` in ONE `.astro` file. You may import nothing except
   `BaseLayout`.
7. The side dropdown menu is rendered by BaseLayout automatically — do not
   add another nav, do not hide it.
8. **Name is FIXED: `Tiffany`** (or `tiffany` if the variant is lowercase).
   Role line is FIXED: `Product Marketing Manager`.
9. Every variant is full-viewport (`min-height: 100svh`), calm, expensive.

## Your variant

### A — "Kintsugi" (wabi-sabi) — file `src/pages/splash-a.astro`

**Feeling:** quiet imperfection. A hand-made ceramic piece: asymmetry, rough
texture, generous negative space, nothing shiny.

- **Lettering:** `tiffany` lowercase, **Instrument Serif** light (400),
  italic optional, `clamp(2.5rem, 6vw, 4rem)` — deliberately smaller and
  quieter than the current splash. Letter-spacing slightly positive
  (~0.02em). Place the name off-center (left or right of center, roughly
  60/40), NOT dead center, NOT huge. Maybe one small hand-drawn underline
  stroke beneath a single letter.
- **Font:** add to `<head>` via `<link slot="head" ...>`:
  `https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap`
- **Visual language:** very soft earth-tone blobs (lower opacity than the
  current aurora), one thin irregular hand-drawn line/arc crossing the frame
  (SVG path with slight wobble), a subtle "kintsugi repair" motif — a thin
  jagged crack line with a terracotta glaze fill, abstract, small, near an
  edge. Strong film grain. Rough, organic, quiet.
- **Role line:** eyebrow-style, mono, muted, small — keep `Product Marketing
  Manager` with no industry qualifier.
- **Motion:** almost none. Name fades in slowly (1.2s); the drawn line
  strokes itself ONCE over ~2s (one-shot, not looping); blobs drift on
  a 40s+ loop. The page should feel barely alive.
- **Reduced motion:** everything static, name fully visible.

### B — "Atomic" (midcentury modern) — file `src/pages/splash-b.astro`

**Feeling:** geometric optimism. 1958 brochure energy: sunbursts, arches,
warm earth tones, playful but restrained structure.

- **Lettering:** `TIFFANY` uppercase, **Jost** (Futura-like) weight 500–600,
  letter-spacing ~0.08em, centered or upper-left. Optionally two-tone: a
  span around the first 1–3 letters in terracotta accent, rest in text
  color. NOT the current Fraunces look at all.
- **Font:** `<link slot="head">`:
  `https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600&display=swap`
- **Visual language:** a sunburst/starburst motif behind the name (thin
  radiating lines, low opacity, slow rotation ~60–90s); concentric arcs; a
  horizon line with a small circle "sun"; a few floating geometric shapes
  (circle, arch, dot) at low opacity scattered around the frame. Palette via
  tokens: terracotta + olive sage sing beautifully here.
- **Role line:** small, letterspaced, under or beside the name.
- **Motion:** sunburst rotates very slowly; name letters rise with a slight
  springy ease (`cubic-bezier(0.34, 1.56, 0.64, 1)`); shapes pop in
  staggered. Livelier than A, still calm.
- **Reduced motion:** static composition.

### C — "Pleats" (Issey Miyake) — file `src/pages/splash-c.astro`

**Feeling:** folded structure. Sculptural letterforms, repetition, technical
lightness — a garment folded on a museum pedestal.

- **Lettering:** `TIFFANY` in **Space Grotesk** weight 500, with a PLEAT
  EFFECT on the letters themselves: each letter rendered in vertical strips
  that alternate slightly (fold illusion) — e.g. split each letter into
  3–5 vertical slices via `background-clip: text` on stacked elements with
  tiny horizontal offsets, or a repeating-linear-gradient mask animated
  slowly. Must read as *fabric folds*, elegant — not a glitch effect.
- **Font:** `<link slot="head">`:
  `https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap`
- **Visual language:** angular folded-paper shards (triangles, low opacity),
  parallel fold lines radiating from a corner, an isometric cube or zigzag
  ribbon motif. Mostly monochrome (text color) with ONE terracotta accent.
  Nylon-like fine diagonal hatch texture.
- **Role line:** small mono text, quiet.
- **Motion:** the pleats breathe continuously but very slowly (stripes
  translate, 12–20s loop); on load the name reveals like a fold unfolding
  (clip-path polygon animation, ~1s). Everything else near-static.
- **Reduced motion:** static, fully visible.

### D — "Editorial" (Prada / Miu Miu) — file `src/pages/splash-d.astro`

**Feeling:** architectural minimalism with one off-kilter detail. Garment
label precision, utilitarian texture, runway restraint.

- **Lettering:** `tiffany` small-caps, **Archivo** weight 400–500,
  letter-spacing ~0.2em, SMALL — `clamp(1.75rem, 4vw, 2.5rem)` — like a
  garment label. Stacked or on one line with thin rules above/below.
  Position upper-left or center-left, asymmetric.
- **Font:** `<link slot="head">`:
  `https://fonts.googleapis.com/css2?family=Archivo:wght@400;500&display=swap`
- **Visual language:** thin horizontal rules; a rectangular frame outline at
  low opacity; ONE bold solid accent shape (small terracotta square or
  circle); fine diagonal hatch texture (nylon); an unexpected detail —
  e.g. a small rotated text element ("est. curious", a degree mark, or a
  tiny dot grid) placed like a garment tag. Asymmetric, precise, quiet.
- **Role line:** mono, tiny, muted, with em-dashes:
  `— product marketing manager —`.
- **Motion:** rules draw in (scaleX) with precise timing; text fades in with
  a slight letter-spacing expansion; one element slides. Runway-precision
  timing, total ~1s. Then stillness.
- **Reduced motion:** static.

## Done means

`npm run build` exits 0 (ignore other agents' in-flight file errors). Your
variant matches its direction, uses tokens only, shows a STATIC composed
frame under reduced motion, keeps the name + role line fixed, keeps the side
menu visible, and reads calm and expensive. Reply with: file path, the exact
name treatment you chose, your visual elements, motion summary, assumptions.
