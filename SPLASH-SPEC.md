# Splash System v2 — Specification (SPLASH-SPEC.md)

**Supersedes the Splash section of DESIGN.md.** The splash is the front door
of Tiffany's digital business card (product marketing, life science &
biopharma). It must feel **expensive**: calm, cinematic, quietly alive.
A layered system — each layer is one component owned by one agent.

## Composition — layered, in z-order

`src/pages/index.astro` composes these inside a full-viewport section:

```
z4  GrainOverlay  (film grain, pointer-events none)
z3  HeroText      (eyebrow / name / lede)   +  ScrollCue (bottom edge)
z2  NodeField     (canvas particle network — the "molecular" imagery)
z1  Aurora        (soft animated gradient atmosphere + warm halo)
    ————————————————— .splash (bg from --bg token) —————————————————
```

## File ownership (never touch another agent's file)

| File | Owner | Responsibility |
|---|---|---|
| `src/components/splash/NodeField.astro` | wW | canvas molecular node network (the showpiece) |
| `src/components/splash/Aurora.astro` | wX | gradient atmosphere + warm halo |
| `src/components/splash/HeroText.astro` | wY | typography + entrance reveal (copy is FIXED) |
| `src/components/splash/GrainOverlay.astro` + `src/components/splash/ScrollCue.astro` | wZ | film grain + bottom scroll cue (two small files, both yours) |

`index.astro`, `global.css`, `BaseLayout.astro`, `SideMenu.astro`, other
pages: **DO NOT TOUCH** (orchestrator-owned). Skeleton files already exist
and compile — elevate them, don't restructure.

## Shared rules (all components)

1. **Tokens only — never hardcoded hex.** CSS: `var(--token)`. Canvas/JS:
   read at runtime —
   `getComputedStyle(document.documentElement).getPropertyValue('--accent-decorative')`
   then parse. Dark mode swaps token values automatically; if your script
   keeps a persistent loop, re-read colors on
   `matchMedia('(prefers-color-scheme: dark)')` change (easy win, do it).
2. **prefers-reduced-motion**: render a STATIC, fully-composed frame — no
   loops, no transitions. Check once at init:
   `matchMedia('(prefers-reduced-motion: reduce)')`.
3. **Zero dependencies** — vanilla JS/CSS/SVG only. No canvas libs, no GSAP.
4. **Performance**: pause rAF on `document.hidden`
   (`visibilitychange`); cap `devicePixelRatio` at 2; animate
   transform/opacity only; ≤4 blobs, blur radii ≤ 120px; the whole splash
   must hold 60fps on a normal laptop.
5. **Calm, not busy**: slow speeds, low opacities, muted palette (cream /
   clay / sage family from tokens). No neon, no rainbow, no spinning logos.
   The animation should be felt, not noticed.
6. `aria-hidden="true"` on all decorative layers. No photos, no logos, no
   text inside graphics.
7. Each component is self-contained: markup + `<style>` + optional
   `<script>` in its own `.astro` file. Class names prefixed per component.
8. **Copy (HeroText)** — the name `Tiffany` is FIXED. Eyebrow and lede were
   broadened (Aug 2026) so the splash stops pigeonholing the audience to
   life science: eyebrow must read `Product Marketing Manager` (no industry
   qualifier) or an equally general title line; lede ≤ 12 words, general —
   no "science/health" only framing, no cliché — e.g.
   `Product marketing for the products people depend on.`
   The letter-rise reveal and every layer contract stay unchanged.

## Component contracts

### Aurora.astro (wX) — atmosphere
```
<div class="aurora" aria-hidden="true">
  <div class="aurora-blob aurora-blob--1"></div>
  <div class="aurora-blob aurora-blob--2"></div>
  <div class="aurora-blob aurora-blob--3"></div>
  <div class="aurora-halo"></div>
</div>
```
CSS: `.aurora { position:absolute; inset:0; z-index:1; pointer-events:none; overflow:hidden; }`

- 3–4 large soft blobs: radial-gradients using
  `color-mix(in srgb, var(--accent-decorative) 12%, transparent)`,
  `color-mix(in srgb, var(--accent-secondary) 10%, transparent)`,
  `var(--bg-subtle)`; placed off-center (e.g. 20%/25%, 75%/70%, 50%/10%),
  each ~40–60% of viewport; `filter: blur(70–110px)` or pre-blurred
  gradients.
- Warm halo over the name area: radial ellipse at ~50%/42%,
  accent-decorative ~8%, transparent 70%.
- Animation: slow drift — translate ±3–6% and scale 1.0→1.08 over
  18–45s `ease-in-out infinite alternate`, staggered delays, transform-only.
- Reduced motion: static, no animation.
- Must read as expensive atmospheric light on cream, not a screensaver.

### NodeField.astro (wW) — the showpiece
```
<canvas class="node-field" data-node-field aria-hidden="true"></canvas>
```
CSS: `.node-field { position:absolute; inset:0; z-index:2; width:100%; height:100%; pointer-events:none; }`

- Molecular node network: ~80–120 nodes, tiny circles r 1–2.5px, slow
  independent drift (delta-time based, ~2–6 px/s, gentle wander), lines
  connecting nodes closer than ~110px — stroke alpha fades with distance,
  lineWidth 0.5–1.
- Colors from tokens (read at init): nodes + lines in `--accent-decorative`,
  a few nodes in `--accent-secondary`. Overall low opacity: lines
  ~0.08–0.2 alpha, nodes ~0.25–0.5.
- Subtle mouse influence: nodes within ~160px of cursor get a gentle
  attraction/repulsion, springing back when the cursor leaves. A whisper,
  not a game. Listen on `window` (canvas is pointer-events:none).
- DPR-aware sizing (`min(devicePixelRatio, 2)`), debounced resize
  (~150ms). Pause rAF on `visibilitychange` (hidden); optional
  IntersectionObserver to pause when the splash scrolls out of view.
- Reduced motion: draw ONE static frame (nodes + lines at t=0), no loop,
  no mouse influence.

### HeroText.astro (wY) — typography + reveal
```
<div class="hero">
  <p class="eyebrow hero-eyebrow">Product Marketing Manager · Life Science &amp; Biopharma</p>
  <h1 class="hero-name" aria-label="Tiffany">Tiffany</h1>
  <p class="lede hero-lede">Product marketing for the science that keeps people healthy.</p>
</div>
```
CSS: `.hero { position:relative; z-index:3; text-align:center; max-width:40rem; padding-inline:1.5rem; }`

- Name: Fraunces weight 300, `clamp(3.75rem, 11vw, 7.5rem)`,
  letter-spacing -0.02em, line-height 1.05. Eyebrow: mono small-caps.
  Lede: muted, `text-wrap: balance`.
- Entrance reveal — make it feel expensive. Pick ONE idea:
  a) letter-by-letter rise for the name — each letter in an inline-block
     span inside `overflow:hidden` parents; letters translateY(110%)→0 with
     `cubic-bezier(0.22,1,0.36,1)`, stagger ~35–45ms; eyebrow + lede
     fade/rise 8–12px shortly after.
  b) clip-path wipe across the name + soft blur-to-sharp on the lede.
- If splitting letters, do it in `<script>` (wrap each character); keep
  `aria-label` on the h1 so screen readers read the name once.
- Total animation ≤ 1.4s from load. One idea, not three.
- Reduced motion: everything visible immediately.

### ScrollCue.astro (wZ)
```
<p class="scroll-cue" aria-hidden="true">scroll</p>
```
Bottom-center, JetBrains Mono 0.68rem, letter-spacing 0.18em, uppercase,
`--text-muted`; a 1px line below (gradient to transparent) that slowly
draws downward (scaleY 0→1, transform-origin top, 2.5–3.5s loop) with a
faint opacity pulse on the label (0.5→1, same loop).
Reduced motion: static line, no pulse. `z-index: 3`.

### GrainOverlay.astro (wZ)
```
<div class="grain-overlay" aria-hidden="true"></div>
```
CSS: `.grain-overlay { position:absolute; inset:0; z-index:4; pointer-events:none; opacity:0.05; mix-blend-mode:overlay; background-image:url("data:image/svg+xml,…feTurbulence…"); }`

- Static film grain: inline SVG data-URI with feTurbulence
  (baseFrequency ~0.9, numOctaves 2, small 128–256px tile). Neutral gray
  noise so it works on cream AND dark. NO animation (perf).
- Tune opacity 0.04–0.07: texture, not grit.

## Done means

`npm run build` exits 0 (if it fails on ANOTHER file mid-flight, that's a
parallel agent's in-progress work — your skeleton compiles standalone).
Your component matches its contract: tokens only, static frame under
reduced motion, dark-mode correct, and the splash reads calm and expensive.
