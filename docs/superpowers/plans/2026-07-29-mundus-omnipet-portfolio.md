# Mundus and OmniPet Portfolio Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Mundus and OmniPet as bilingual, technically substantial platform case studies while upgrading the portfolio into a responsive digital research exhibition.

**Architecture:** Keep Astro Content Collections as the source of truth, add explicit collection metadata for homepage grouping, and let each new MDX entry own a focused project-story component. Shared typography, color, spacing, and detail-page structure remain in the global layout and route; public screenshots and release assets live under project-specific media directories.

**Tech Stack:** Astro 7, MDX, TypeScript, scoped CSS, semantic HTML/SVG, local Fontsource packages, GitHub Pages static output.

---

## File Map

**Create**

- `src/content/projects/mundus.mdx`: bilingual Mundus metadata and narrative.
- `src/content/projects/omnipet.mdx`: bilingual OmniPet metadata and narrative.
- `src/components/MundusStory.astro`: public mode gallery, platform diagram, algorithm cards, and data pipeline.
- `src/components/OmniPetStory.astro`: engine pipeline, approval gates, publication boundary, and SuShi outcome.
- `public/media/mundus/other-side.webp`: public Other Side capture.
- `public/media/mundus/development.webp`: public Development capture.
- `public/media/mundus/sunline.webp`: public Sunline capture.
- `public/media/mundus/modes-overview.webp`: homepage overview composed from public captures.
- `public/media/omnipet/sushi-preview.webp`: copied public release preview.
- `public/media/omnipet/sushi-spritesheet.webp`: copied public release spritesheet.

**Modify**

- `package.json`: add locally bundled Cormorant Garamond.
- `package-lock.json`: lock the font dependency.
- `src/styles/fonts.css`: define Cormorant display faces and explicit font roles.
- `src/content.config.ts`: add `featured` and localized `kind`.
- `src/content/projects/dialogtree.mdx`: mark featured, set kind, preserve order 1.
- `src/content/projects/side-b.mdx`: mark non-featured, set kind, set Other Work order 1.
- `src/content/projects/nbti.mdx`: mark featured, set kind, move to order 4.
- `src/pages/index.astro`: split Featured and Other Work and apply the new exhibition hierarchy.
- `src/pages/projects/[...slug].astro`: add project index/kind, numbered detail structure, and exhibition styling.
- `src/components/BaseLayout.astro`: establish global typography tokens, grid/rule system, and refined header/footer.
- `src/components/ProjectMedia.astro`: support the refined media frames without project-ID branches.
- `src/pages/notes.astro`: inherit the upgraded reading rhythm.
- `src/config/site.ts`: add approved Mundus, OmniPet, and OmniPets links.
- `README.md`: document grouping fields, local font policy, and public-media boundary.

## Task 1: Add Explicit Project Grouping

**Files:**

- Modify: `src/content.config.ts`
- Modify: `src/content/projects/dialogtree.mdx`
- Modify: `src/content/projects/side-b.mdx`
- Modify: `src/content/projects/nbti.mdx`
- Modify: `src/pages/index.astro`

- [ ] **Step 1: Make the schema require grouping metadata**

Add the two fields immediately after `order` in `src/content.config.ts`:

```ts
order: z.number(),
featured: z.boolean(),
kind: localized,
summary: localized,
```

- [ ] **Step 2: Run the build and confirm the content contract fails**

Run:

```bash
npm run build
```

Expected: failure from the `projects` collection because existing entries are missing `featured` and `kind`.

- [ ] **Step 3: Update all existing frontmatter**

Use these exact values:

```yaml
# dialogtree.mdx
order: 1
featured: true
kind: { en: Human–AI research product, zh: 人机协作研究产品 }
```

```yaml
# side-b.mdx
order: 1
featured: false
kind: { en: Mobile product prototype, zh: 移动产品原型 }
```

```yaml
# nbti.mdx
order: 4
featured: true
kind: { en: Cultural interactive product, zh: 文化互动产品 }
```

- [ ] **Step 4: Split the homepage collection**

Replace the single sorted collection with:

```ts
const projects = await getCollection('projects');
const featuredProjects = projects
  .filter((project) => project.data.featured)
  .sort((a, b) => a.data.order - b.data.order);
const otherProjects = projects
  .filter((project) => !project.data.featured)
  .sort((a, b) => a.data.order - b.data.order);
```

Render `featuredProjects` in the existing selected-work list. Add the localized kind to each card metadata:

```astro
<div class="meta">
  <span><Localized {...project.data.year} /></span>
  <span><Localized {...project.data.kind} /></span>
</div>
```

In Other Work, render `otherProjects` before the configured RSZ card. Each collection entry must link to `${base}projects/${project.id}` so Side B keeps its detail route.

- [ ] **Step 5: Run the build and inspect generated routes**

Run:

```bash
npm run build
```

Expected: success; `dist/projects/dialogtree/index.html`, `dist/projects/side-b/index.html`, and `dist/projects/nbti/index.html` exist.

- [ ] **Step 6: Commit the content model**

```bash
git add src/content.config.ts src/content/projects/dialogtree.mdx src/content/projects/side-b.mdx src/content/projects/nbti.mdx src/pages/index.astro
git commit -m "feat(portfolio): add explicit project grouping"
```

## Task 2: Establish the Exhibition Type System

**Files:**

- Modify: `package.json`
- Modify: `package-lock.json`
- Modify: `src/styles/fonts.css`
- Modify: `src/components/BaseLayout.astro`

- [ ] **Step 1: Install the local display font**

Run:

```bash
npm install @fontsource/cormorant-garamond
```

Expected: `package.json` and `package-lock.json` add `@fontsource/cormorant-garamond`; no remote font import is introduced.

- [ ] **Step 2: Add Cormorant faces**

Append Cormorant and the already-installed variable families to `src/styles/fonts.css`:

```css
@font-face {
  font-family: 'Instrument Sans Variable';
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
  src: url('@fontsource-variable/instrument-sans/files/instrument-sans-latin-wght-normal.woff2') format('woff2-variations');
}

@font-face {
  font-family: 'Newsreader Variable';
  font-style: normal;
  font-weight: 400 600;
  font-display: swap;
  src: url('@fontsource-variable/newsreader/files/newsreader-latin-wght-normal.woff2') format('woff2-variations');
}

@font-face {
  font-family: 'Newsreader Variable';
  font-style: italic;
  font-weight: 400 600;
  font-display: swap;
  src: url('@fontsource-variable/newsreader/files/newsreader-latin-wght-italic.woff2') format('woff2-variations');
}

@font-face {
  font-family: 'Cormorant Display';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('@fontsource/cormorant-garamond/files/cormorant-garamond-latin-400-normal.woff2') format('woff2');
}

@font-face {
  font-family: 'Cormorant Display';
  font-style: italic;
  font-weight: 400;
  font-display: swap;
  src: url('@fontsource/cormorant-garamond/files/cormorant-garamond-latin-400-italic.woff2') format('woff2');
}

@font-face {
  font-family: 'Cormorant Display';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('@fontsource/cormorant-garamond/files/cormorant-garamond-latin-500-normal.woff2') format('woff2');
}
```

- [ ] **Step 3: Replace ambiguous global font tokens**

In `BaseLayout.astro`, define:

```css
:root {
  --font-body: "Instrument Sans Variable", "Noto Sans Bilingual", "PingFang SC", sans-serif;
  --font-display: "Cormorant Display", "Newsreader Variable", Georgia, serif;
  --font-editorial: "Newsreader Variable", Georgia, serif;
  --font-display-zh: "Noto Serif Bilingual", "Songti SC", serif;
}

body { font-family: var(--font-body); }
h1, .display-title { font-family: var(--font-display); font-weight: 400; }
h2, .editorial-title { font-family: var(--font-editorial); font-weight: 500; }
h3 { font-family: var(--font-editorial); font-weight: 500; }
:root[data-locale='zh'] h1,
:root[data-locale='zh'] h2,
:root[data-locale='zh'] h3,
:root[data-locale='zh'] .display-title {
  font-family: var(--font-display-zh);
  font-weight: 400;
}
```

Remove the old rule that forces all `h3` elements onto the sans-serif stack. Keep interface labels, metadata, navigation, and body copy sans-serif.

- [ ] **Step 4: Verify local font emission**

Run:

```bash
npm run build
find dist -type f -name "*.woff2" | head
```

Expected: build succeeds and hashed WOFF2 assets are emitted in `dist/_astro`; generated HTML contains no `fonts.googleapis.com` or other remote font host.

- [ ] **Step 5: Commit typography**

```bash
git add package.json package-lock.json src/styles/fonts.css src/components/BaseLayout.astro
git commit -m "style(portfolio): add exhibition typography"
```

## Task 3: Prepare Approved Public Media

**Files:**

- Create: `public/media/mundus/other-side.webp`
- Create: `public/media/mundus/development.webp`
- Create: `public/media/mundus/sunline.webp`
- Create: `public/media/mundus/modes-overview.webp`
- Create: `public/media/omnipet/sushi-preview.webp`
- Create: `public/media/omnipet/sushi-spritesheet.webp`

- [ ] **Step 1: Capture the three public Mundus modes**

Use browser automation against `https://0mn1si2i5.github.io/Mundus/` at a 1440×900 desktop viewport. Capture:

```text
?mode=antipodes&v=1   -> other-side.png
?mode=development&v=1 -> development.png
?mode=sunline&v=1     -> sunline.png
```

Before each capture, wait for the globe canvas and mode controls, then verify the browser console has no errors. Do not include browser chrome.

- [ ] **Step 2: Convert captures to efficient WebP**

Use the repository's existing `ffmpeg-static` binary through Node or system `ffmpeg` if available:

```bash
ffmpeg -i other-side.png -vf "scale=1440:-2" -c:v libwebp -q:v 82 public/media/mundus/other-side.webp
ffmpeg -i development.png -vf "scale=1440:-2" -c:v libwebp -q:v 82 public/media/mundus/development.webp
ffmpeg -i sunline.png -vf "scale=1440:-2" -c:v libwebp -q:v 82 public/media/mundus/sunline.webp
```

Create `modes-overview.webp` as a 4:3 composition with one dominant Other Side frame and two smaller mode frames. Use an image editor or deterministic CSS screenshot; do not use generated placeholder art.

- [ ] **Step 3: Copy only public OmniPets release assets**

Run:

```bash
mkdir -p public/media/omnipet
cp /Users/bytedance/Desktop/Zen/OmniPets/pets/sushi/preview.webp public/media/omnipet/sushi-preview.webp
cp /Users/bytedance/Desktop/Zen/OmniPets/pets/sushi/spritesheet.webp public/media/omnipet/sushi-spritesheet.webp
```

Do not copy any file from `OmniPet-Production`, `.omnipet`, checkpoints, references, or planning repositories.

- [ ] **Step 4: Verify the asset set**

Run:

```bash
find public/media/mundus public/media/omnipet -maxdepth 1 -type f -print
```

Expected: exactly four Mundus WebP files and two OmniPet WebP files.

- [ ] **Step 5: Commit public media**

```bash
git add public/media/mundus public/media/omnipet
git commit -m "assets(portfolio): add public project media"
```

## Task 4: Add the Mundus Platform Case Study

**Files:**

- Create: `src/content/projects/mundus.mdx`
- Create: `src/components/MundusStory.astro`
- Modify: `src/config/site.ts`

- [ ] **Step 1: Add approved links**

Extend `site.links`:

```ts
mundusWebsite: 'https://0mn1si2i5.github.io/Mundus/',
mundusGithub: 'https://github.com/0mn1si2i5/Mundus',
```

- [ ] **Step 2: Create the Mundus content entry**

Use this complete frontmatter:

```yaml
---
title: { en: Mundus, zh: Mundus }
year: { en: 'Jul 2026', zh: '2026 年 7 月' }
status: { en: Live open-source platform, zh: 已上线的开源平台 }
order: 2
featured: true
kind: { en: WebGL observation platform, zh: WebGL 地球观察平台 }
summary: { en: An extensible globe platform that turns antipodes, human development, and sunlight into three reproducible ways of observing Earth., zh: 一个可扩展的三维地球观察平台，以对跖点、人类发展结构和日照线构成三种可复现的观察方式。 }
role: { en: Product concept, interaction and visual design, data pipeline, algorithms, and front-end engineering, zh: 产品概念、交互与视觉设计、数据管线、算法与前端工程 }
accent: blue
media:
  type: image
  src: /media/mundus/other-side.webp
  preview: /media/mundus/modes-overview.webp
  alt: { en: Mundus showing its interactive globe and three observation modes., zh: Mundus 的交互式地球与三种观察模式。 }
links:
  - label: { en: Visit Mundus, zh: 访问 Mundus }
    href: https://0mn1si2i5.github.io/Mundus/
  - label: { en: View source, zh: 查看源代码 }
    href: https://github.com/0mn1si2i5/Mundus
---
```

The English and Chinese sections must cover the approved six-part narrative and import `<MundusStory />` between the platform introduction and the readable algorithm deep dive.

- [ ] **Step 3: Build the semantic Mundus story component**

`MundusStory.astro` must expose no props and contain:

```astro
---
import Localized from './Localized.astro';
const modes = [
  {
    index: '01',
    image: '/media/mundus/other-side.webp',
    title: { en: 'Other Side', zh: '地球另一端' },
    detail: { en: 'Spherical relationships', zh: '球面空间关系' },
  },
  {
    index: '02',
    image: '/media/mundus/development.webp',
    title: { en: 'Development, Unpacked', zh: '发展的不同侧面' },
    detail: { en: 'Human evidence layers', zh: '人类发展证据层' },
  },
  {
    index: '03',
    image: '/media/mundus/sunline.webp',
    title: { en: 'Sunline', zh: '日照线' },
    detail: { en: 'Time and solar geometry', zh: '时间与太阳几何' },
  },
];
const base = import.meta.env.BASE_URL.endsWith('/') ? import.meta.env.BASE_URL : `${import.meta.env.BASE_URL}/`;
const asset = (path: string) => `${base}${path.replace(/^\//, '')}`;
---
```

The rendered structure must include:

- `<section class="mundus-exhibit" aria-labelledby="mundus-platform-title">`;
- a text-first list of the shared layers: globe, mode registry, state, data registry, validation;
- a CSS/SVG orbit graphic marked `aria-hidden="true"`;
- a localized heading referenced by the mode gallery through `aria-labelledby`;
- three `<figure>` mode cards with localized `alt`, captions, and `loading="lazy"`;
- algorithm cards for antipodes, geographic lookup, development comparison, solar model, the shader-rendered solar-altitude field with `0°`/`-6°` twilight thresholds, and vector pipeline;
- an independent semantic data flow: source manifest → hash verification → deterministic transformation → schema/quality gates → versioned public asset;
- a final extension flow: register mode → declare state/data → reuse globe → validate/share.

All key information must exist as HTML text outside decorative SVG.

- [ ] **Step 4: Add scoped exhibition CSS**

Use a dark tokenized band:

```css
.mundus-exhibit {
  --exhibit-paper: #151917;
  --exhibit-ink: #f1eee6;
  --exhibit-muted: #a8b0aa;
  --exhibit-line: #414843;
  margin: 5rem calc(50% - 50vw);
  padding: clamp(4rem, 8vw, 8rem) max(1.5rem, calc((100vw - 1180px) / 2));
  color: var(--exhibit-ink);
  background: var(--exhibit-paper);
}
```

Add responsive single-column layouts below 760px and disable decorative orbit motion under `prefers-reduced-motion`.

- [ ] **Step 5: Build and inspect the route**

Run:

```bash
npm run build
```

Expected: `dist/projects/mundus/index.html` exists and no schema or MDX error is emitted.

Open `/projects/mundus` in English and Chinese. Confirm all diagrams remain understandable without animation and all assets honor `BASE_URL`.

- [ ] **Step 6: Commit Mundus**

```bash
git add src/content/projects/mundus.mdx src/components/MundusStory.astro src/config/site.ts
git commit -m "feat(portfolio): add Mundus platform case study"
```

## Task 5: Add the OmniPet Engine Case Study

**Files:**

- Create: `src/content/projects/omnipet.mdx`
- Create: `src/components/OmniPetStory.astro`
- Modify: `src/config/site.ts`

- [ ] **Step 1: Add public OmniPet links**

Extend `site.links`:

```ts
omnipetGithub: 'https://github.com/0mn1si2i5/OmniPet',
omnipetsGithub: 'https://github.com/0mn1si2i5/OmniPets',
```

- [ ] **Step 2: Create the OmniPet content entry**

Use this complete frontmatter:

```yaml
---
title: { en: OmniPet, zh: OmniPet }
year: { en: 'Jul 2026', zh: '2026 年 7 月' }
status: { en: Open-source Alpha engine, zh: 开源 Alpha 引擎 }
order: 3
featured: true
kind: { en: AI asset production engine, zh: AI 资产生产引擎 }
summary: { en: An extensible engine that turns generated desktop-pet imagery into reviewable, recoverable, and cleanly publishable sprite releases., zh: 一个可扩展的桌宠资产生产引擎，将生成图像转化为可审查、可恢复并可安全发布的精灵资产。 }
role: { en: Product architecture, workflow and safety design, Python CLI, validation, and release engineering, zh: 产品架构、工作流与安全设计、Python CLI、验证与发布工程 }
accent: coral
media:
  type: image
  src: /media/omnipet/sushi-preview.webp
  preview: /media/omnipet/sushi-preview.webp
  alt: { en: SuShi, a public installable desktop pet produced through OmniPet., zh: 通过 OmniPet 生产并公开发布的可安装桌宠 SuShi。 }
links:
  - label: { en: View the engine, zh: 查看引擎 }
    href: https://github.com/0mn1si2i5/OmniPet
  - label: { en: Browse public pets, zh: 浏览公开桌宠 }
    href: https://github.com/0mn1si2i5/OmniPets
---
```

Write paired English and Chinese sections covering the approved seven-part narrative. Explicitly label the current engine as Alpha and distinguish shipped public behavior from planned community contribution features.

- [ ] **Step 3: Build the semantic OmniPet story component**

`OmniPetStory.astro` must define public workflow stages:

```ts
const stages = [
  { index: '01', en: 'Manifest and brief', zh: '清单与创作简报', gate: false },
  { index: '02', en: 'Canonical base', zh: '标准基础形象', gate: true },
  { index: '03', en: 'Actions and directions', zh: '动作与方向', gate: true },
  { index: '04', en: 'Visual QA and repair', zh: '视觉 QA 与修复', gate: true },
  { index: '05', en: 'Atlas and package', zh: '图集与安装包', gate: true },
  { index: '06', en: 'Release export', zh: '发布导出', gate: false },
  { index: '07', en: 'Clean-room verify', zh: '洁净环境验证', gate: false },
];
```

Render:

- a text-first ordered workflow;
- visible approval gates with localized labels;
- a three-zone publication boundary: public engine → private production boundary → public catalog;
- the SuShi preview and public spritesheet with localized alternatives;
- extension contracts: manifests, action definitions, provider adapter boundary, validators, release contract;
- a clear Alpha status note.

Do not mention private repository names, paths, prompts, references, provider responses, checkpoint contents, or reviewer evidence.

- [ ] **Step 4: Add scoped exhibition CSS**

Use the same exhibition tokens as Mundus but a warmer coral signal. Keep the component API independent; share only CSS variables and generic global type tokens, not a generic diagram framework.

The pipeline must become a vertical ordered sequence under 760px and retain visible gate labels without hover.

- [ ] **Step 5: Build and inspect the route**

Run:

```bash
npm run build
```

Expected: `dist/projects/omnipet/index.html` exists.

Open `/projects/omnipet` in both languages. Verify the page contains only the two public GitHub links and no text matching `OmniPet-Production`, `OmniPet-Program`, `.omnipet`, local absolute paths, or credential-like strings.

- [ ] **Step 6: Commit OmniPet**

```bash
git add src/content/projects/omnipet.mdx src/components/OmniPetStory.astro src/config/site.ts
git commit -m "feat(portfolio): add OmniPet engine case study"
```

## Task 6: Apply the Site-Wide Digital Exhibition Layout

**Files:**

- Modify: `src/components/BaseLayout.astro`
- Modify: `src/components/ProjectMedia.astro`
- Modify: `src/pages/index.astro`
- Modify: `src/pages/projects/[...slug].astro`
- Modify: `src/pages/notes.astro`

- [ ] **Step 1: Add global exhibition tokens**

Extend `:root` in `BaseLayout.astro`:

```css
--page-width: 1180px;
--reading-width: 720px;
--space-section: clamp(5rem, 9vw, 9rem);
--display-tracking: -.045em;
--rule-strong: color-mix(in srgb, var(--ink) 22%, var(--line));
```

Refine header/footer with small uppercase labels, thin rules, and a stable mobile layout. Preserve the existing locale/theme scripts and keyboard focus styles.

- [ ] **Step 2: Redesign the homepage hierarchy**

In `index.astro`:

- keep the hero light;
- use Cormorant for English project names and Noto Serif SC for Chinese names;
- display a two-digit project index using `String(index + 1).padStart(2, '0')`;
- display `kind` separately from status;
- use alternating media/copy placement only on desktop;
- render Side B first in Other Work with a compact visual card and detail link;
- render RSZ second as the existing external project.

The selected list must render only:

```text
01 DialogTree
02 Mundus
03 OmniPet
04 NBTI
```

- [ ] **Step 3: Upgrade the common project route**

In `[...slug].astro`, derive the featured project index without project-ID styling branches:

```ts
const projects = (await getCollection('projects'))
  .filter((entry) => entry.data.featured)
  .sort((a, b) => a.data.order - b.data.order);
const projectIndex = projects.findIndex((entry) => entry.id === project.id);
const displayIndex = projectIndex >= 0 ? String(projectIndex + 1).padStart(2, '0') : 'Archive';
```

Show `displayIndex` and localized `kind` in the hero. Restyle prose with:

```css
.prose { max-width: var(--reading-width); }
.prose :global(h2) {
  counter-increment: section;
  font-family: var(--font-editorial);
}
.prose :global(h2)::before {
  content: counter(section, decimal-leading-zero);
  display: block;
  margin-bottom: .75rem;
  color: var(--muted);
  font-family: var(--font-body);
  font-size: .72rem;
  letter-spacing: .12em;
}
```

Reset the counter on `.prose`. Ensure hidden locale sections do not create visible duplicate numbering.

- [ ] **Step 4: Refine media and Notes**

In `ProjectMedia.astro`, retain the existing media contract and add only presentation refinements: subtler borders, exhibition-style radius, background treatment, and responsive aspect ratios. Do not add project-ID conditions.

In `notes.astro`, use the new editorial heading font, reading width, spacing tokens, and rule treatment without adding project diagrams or dark exhibition bands.

- [ ] **Step 5: Run build and manual responsive checks**

Run:

```bash
npm run build
npm run dev
```

At 1440×900, 768×1024, and 390×844, inspect:

- homepage hierarchy and exact grouping;
- all five project routes;
- Notes;
- English and Chinese;
- light and dark themes;
- keyboard focus and skip link;
- no horizontal overflow.

- [ ] **Step 6: Commit the visual system**

```bash
git add src/components/BaseLayout.astro src/components/ProjectMedia.astro src/pages/index.astro src/pages/projects/'[...slug].astro' src/pages/notes.astro
git commit -m "style(portfolio): apply digital exhibition system"
```

## Task 7: Document and Verify the Release

**Files:**

- Modify: `README.md`

- [ ] **Step 1: Update contributor guidance**

Document:

- `featured` and `kind` in project frontmatter;
- featured ordering versus Other Work ordering;
- Cormorant/Newsreader/Noto/Instrument font roles;
- the rule that all visitor-facing project media must be public and approved;
- the rule that private production evidence may inform writing but must never be copied into the portfolio.

- [ ] **Step 2: Run repository checks**

Run:

```bash
npm run build
git diff --check
```

Expected: both commands succeed.

- [ ] **Step 3: Verify generated content and privacy boundaries**

Run:

```bash
find dist/projects -maxdepth 2 -name index.html -print
grep -R "OmniPet-Production\|OmniPet-Program\|/Users/bytedance\|OPENAI_API_KEY" dist || true
grep -R "fonts.googleapis.com\|fonts.gstatic.com" dist || true
```

Expected:

- routes exist for `dialogtree`, `mundus`, `omnipet`, `nbti`, and `side-b`;
- privacy grep prints nothing;
- remote-font grep prints nothing.

- [ ] **Step 4: Run browser acceptance**

Use browser automation against the local preview:

1. Snapshot homepage in English/light.
2. Confirm selected order and Other Work order.
3. Switch to Chinese and confirm localized project kinds and alternatives.
4. Switch to dark and inspect all diagrams.
5. Open Mundus and OmniPet; take desktop and mobile screenshots.
6. Set reduced motion and confirm no essential content disappears.
7. Check console and network requests for errors.
8. Follow all public project links and confirm expected destinations.

Expected: no console errors, broken requests, inaccessible controls, clipped text, or horizontal overflow.

- [ ] **Step 5: Review technical claims**

Cross-check the final Mundus prose against:

```text
/Users/bytedance/Desktop/Zen/Mundus/src/features/modes/modeRegistry.ts
/Users/bytedance/Desktop/Zen/Mundus/src/features/sunline/solar.ts
/Users/bytedance/Desktop/Zen/Mundus/src/data/registry.ts
/Users/bytedance/Desktop/Zen/Mundus/DATA_SOURCES.md
```

Cross-check OmniPet prose only against public sources:

```text
/Users/bytedance/Desktop/Zen/OmniPet/README.md
/Users/bytedance/Desktop/Zen/OmniPet/docs/architecture.md
/Users/bytedance/Desktop/Zen/OmniPet/docs/generation-workflow.md
/Users/bytedance/Desktop/Zen/OmniPet/src/omnipet/public_release.py
/Users/bytedance/Desktop/Zen/OmniPets/README.md
/Users/bytedance/Desktop/Zen/OmniPets/catalog/index.json
```

Remove any claim that is planned, unverifiable, or stronger than these public sources support.

- [ ] **Step 6: Commit documentation and final verification state**

```bash
git add README.md
git commit -m "docs(portfolio): document project publishing rules"
git status --short
```

Expected: clean working tree.
