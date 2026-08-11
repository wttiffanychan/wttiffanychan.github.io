# Tiffany — Personal Website (site-v2) — Design System & Page Briefs

**The single source of truth for this build.** Read this file in full before
writing any code. It is the contract: follow the tokens, the tone, and your
page brief exactly.

## What this site is

A **digital business card** for Tiffany — a **Product Marketing Manager at
Eurofins** applying to marketing roles in the **life science and biopharma
industry**. It should feel high-end, calm, and minimal: expensive, not
decorated. Four pages: **Splash** (/), **Bio** (/bio), **Projects**
(/projects), **Interest** (/interest). Navigation is a small side dropdown
menu (already built — `src/components/SideMenu.astro`, rendered by
`src/layouts/BaseLayout.astro`). You never touch those two files.

## Tech

- Astro 5, static output. Every page is an `.astro` file under `src/pages/`.
- Each page: frontmatter imports `BaseLayout` (already in your stub), markup
  in the template, **page-specific styles in the file's own `<style>` tag**
  (Astro scopes them automatically).
- Verify: `cd /Users/tiffany/Claude/Projects/HerdrProjects/site-v2 && npm run build`
- Do NOT add dependencies, do NOT create new files, do NOT modify
  `src/styles/global.css`, `src/layouts/BaseLayout.astro`,
  `src/components/SideMenu.astro`, or any page other than your own.

## Design tokens (use ONLY these — never hardcode hex)

Defined in `src/styles/global.css`. All pages must work in both light and
dark mode (`prefers-color-scheme: dark` handled automatically by the tokens):

| Token | Light | Role |
|---|---|---|
| `--bg` | #F5F0E6 warm sand | page background |
| `--bg-subtle` | #EAE1CF sand | cards, panels, hover fills |
| `--text` | #2F2A24 warm umber | headings & body |
| `--text-muted` | #6E6455 taupe | secondary text, ledes |
| `--border` | #D9CEB8 sand | hairlines, card borders |
| `--accent-decorative` | #C08A5D terracotta | decorative accents, motifs, selection |
| `--accent-interactive` | #8A5A33 deep terracotta | links, focus |
| `--accent-secondary` | #7C8A6E olive sage | quiet secondary accent |

Palette note (Aug 2026): earth tones — warm sand, terracotta, olive sage,
taupe, umber. Calm and grounding; dark mode swaps to deep warm browns.

Type: **Fraunces** (serif, weight 300–500) for headings, **Inter** (400–600)
for body, **JetBrains Mono** (400) for eyebrows/labels. All three are already
loaded by the layout.

Shared utilities already in global.css: `.container` (max-width 56rem),
`.section` (vertical padding), `.eyebrow` (mono small-caps label),
`.lede` (muted intro line), `.page-head` (+ `h1` inside), `.fade-up`
(subtle entrance animation — respects reduced motion).

## Tone rules (hard)

- Calm, minimal, honest. Short sentences. Few words.
- **Less text, more imagery.** Prefer iconography and abstract SVG motifs over
  paragraphs. A page should be scannable in seconds.
- **Audience is NOT life-science-only.** She is a product marketing manager
  (currently at Eurofins, but that is one data point, not the pitch). Avoid
  phrasing that frames the whole site as life science / biopharma. The site
  works for any marketing role; life science can appear where it's factual
  (bio), not as the splash identity.
- **Banned:** synergy, driving growth, end-to-end, passionate, leveraging,
  robust, best-in-class, "let's talk about how I can help your team",
  exclamation marks, emoji, superlatives, resume-speak.
- No photos, no real imagery, no logos. Decorative imagery is **abstract
  inline SVG only** — molecular dot-clusters, concentric rings, flow-lines,
  contour routes, grain. Use `currentColor` + low opacity
  (`var(--accent-decorative)` reads beautifully). Keep motifs small and calm.
- She is comfortable being identified as **Product Marketing Manager at
  Eurofins** and as a graduate of **Bronx High School of Science (NY)** and
  **Babson College (MA)**. No dates, no metrics, no org-chart language.
- No contact details yet — leave contact blocks commented out.

---

## Page briefs

### Splash — `src/pages/index.astro`

**SUPERSEDED by `SPLASH-SPEC.md`** — the splash is now a layered system of
components under `src/components/splash/` (Aurora, NodeField, HeroText,
ScrollCue, GrainOverlay), composed by `index.astro`. Read SPLASH-SPEC.md for
the current contract. The brief below is historical.

The front door. Must feel expensive. Full-viewport hero:
- Eyebrow: `Product Marketing Manager · Life Science & Biopharma`
- Name **Tiffany** in large Fraunces (weight 300, generous size)
- One honest clause under the name, ≤ 12 words, no clichés. The stub has a
  draft — refine it or replace it. It should read like something a thoughtful
  person would say, not ad copy.
- An abstract SVG motif (the stub has a molecular-cluster one — refine it:
  concentric rings / dot clusters, `currentColor`, subtle, behind or beside
  the text)
- A quiet `scroll` cue. Nothing else — the side menu handles navigation.
- Subtle entrance animation (`.fade-up` or better), respecting reduced motion.

### Bio — `src/pages/bio.astro` (agent wX)

Eyebrow `Bio`, h1 `About`. 2–3 short paragraphs (3–5 sentences each):
1. She is a **product marketing manager at Eurofins**, working in the life
   science and biopharma space — diagnostics, instruments, the science that
   keeps people healthy.
2. What the work looks like day to day: positioning and messaging, product
   launches, market and competitive research, content that scientists
   actually read.
3. How she thinks: plain and direct, comfortable at the intersection of
   marketing and operations, curious by habit.
4. One quiet line on education: Bronx High School of Science (New York), then
   Babson College (Massachusetts).
Optional: a small `Focus areas` list — 4 items max, plain labels (e.g.
Positioning & messaging / Product launches / Market & competitive research /
Content strategy). Keep it understated; no resume-speak, no dates.

### Projects — `src/pages/projects.astro` (agent wY)

Eyebrow `Projects`, h1 `Selected work`. A grid of **4 cards**: title, one-line
description, small tag row (mono, muted). Card style: `--bg-subtle` or `--bg`
with `--border` hairline, subtle hover lift, generous padding, Fraunces title.
- Cards 1–3 are **placeholders Tiffany will replace** — marketing projects
  with bracketed titles like `Product launch — [Name]`. One line each,
  credible and specific: a launch taking a new diagnostic from bench to
  market; a positioning and messaging refresh; a campaign or content program.
  Keep them clearly replaceable (bracketed titles).
- Card 4 is a **real personal project**: an AI-assisted job-search workflow
  she built for herself — how she tracks, tailors, and organizes applications.
  Describe it plainly; it shows initiative.
- No dates, no employer metrics, no logos.

### Interest — `src/pages/interest.astro` (agent wZ)

Eyebrow `Interest`, h1 `Off the clock` (or quieter alternative). A calm list
of short entries, 1–2 sentences each, **no forced lessons** ("this taught me
leadership" is banned). Entries:
1. **Movement** — pilates, weight training, functional cardio
2. **Food & travel** — cooking at home, planning trips around a single meal
3. **Languages** — learning Spanish
4. **Investing** — learning to actually understand markets
5. **AI** — following the AI ecosystem closely
6. **The brain** — keeping it a little surprised: dance, instruments, memory
   exercises (the neuroscience / dementia-risk interest, stated lightly,
   no clinical language)
Each entry may carry a tiny abstract motif (flow-line near movement, contour
route near travel, grain near food) — keep motifs small. Present as a list or
light grid; let a couple of entries be interests without any lesson attached.

---

## Done means

Your page builds cleanly (`npm run build` fails on no file but your own — fix
yours; ignore errors in other agents' in-progress files), matches the tokens,
obeys the tone rules, and reads like a calm, expensive personal site.
