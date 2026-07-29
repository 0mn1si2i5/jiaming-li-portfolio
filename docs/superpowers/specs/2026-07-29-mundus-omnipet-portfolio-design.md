# Mundus and OmniPet Portfolio Expansion Design

## Goal

Add Mundus and OmniPet as concise bilingual product case studies, present both as extensible platforms or engines rather than isolated features, and keep the portfolio focused on what each product enables.

The result must:

- explain Mundus as a shared globe platform whose current modes are extensions of a common rendering, state, data, and validation foundation;
- support Mundus with only the technical detail needed to establish reproducibility, extensibility, and responsible boundaries;
- explain OmniPet as an extensible AI pet production and release engine rather than a one-off sprite generator;
- use only public, approved evidence and assets in visitor-facing pages;
- preserve the current bilingual, static, GitHub Pages-compatible architecture;
- improve the whole site's typography, layout, hierarchy, and responsive behavior without replacing its identity.

## Approved Project Hierarchy

The homepage Selected Work order is:

1. DialogTree
2. Mundus
3. OmniPet
4. NBTI

Side B moves to the first position in Other Work. Its existing detail route and full case study remain available. RSZ Namelist follows it.

Project grouping must be represented in content metadata rather than inferred from IDs or hard-coded exclusion lists. Each project declares whether it is featured and provides a localized project kind. Ordering remains explicit.

## Narrative Strategy

Both new case studies lead with the product problem, platform capability, user value, extensibility, and a concrete result. Technical detail is short supporting evidence, not the exhibition itself. Each project uses roughly one or two core technical paragraphs and one or two visual moments.

### Mundus

Mundus is presented as an extensible globe observation platform. Its three current modes are examples built on a shared system:

- a common WebGL globe and geographic interaction model;
- a versioned mode registry and mode-specific state schemas;
- URL-addressable state for reproducible and shareable observations;
- a validated data registry with sources, licenses, transformations, hashes, caveats, and quality metrics;
- reusable rendering, accessibility, fallback, and performance infrastructure.

The case study follows this compact structure:

1. Product problem and user value: one navigable globe supports several reproducible ways to observe Earth.
2. Platform capability: registered modes share rendering, interaction, addressable state, data provenance, and validation.
3. Result and extensibility: three public modes demonstrate the platform, while a new mode can join without rebuilding the globe.

The public hero and one three-mode Story overview are the only two images on the page. The former six-card algorithm atlas, five-stage data pipeline, and second Story image are removed. English and Chinese each use at most two compact technical-support paragraphs. It must not claim legal-boundary authority, navigation-grade solar accuracy, or globally optimal precision.

### OmniPet

OmniPet is presented as an extensible AI desktop-pet production and release engine. Its value is turning uncertain generated imagery into a reviewable, recoverable, and publishable asset workflow.

The case study follows this compact structure:

1. Product problem and user value: a convincing generated image is not yet a reliable, installable desktop pet.
2. Engine capability and differentiation: resumable state, explicit approvals, repair, packaging, and a separate public release boundary turn uncertain inputs into reviewable output.
3. Extensibility and result: versioned contracts keep generation, validation, and publication separable; SuShi demonstrates the current public outcome while Alpha limitations remain explicit.

The public hero and one SuShi Story outcome are the only two images on the page. The former seven-stage workflow, six-card contract exhibition, and spritesheet image are removed. The case study explicitly names the shipped extension axes and the current one-allowlisted-provider limitation without repeating the publication boundary.

Only the public `OmniPet` engine and public `OmniPets` catalog are linked. Private production and planning repositories may inform accurate high-level writing, but their names, files, paths, prompts, references, provider responses, checkpoints, reviewer evidence, internal URLs, and audit details must not appear in visitor-facing content.

## Visual Direction

The approved direction is a site-wide digital research exhibition.

### Global System

Retain the current paper-and-ink palette and light/dark theme, but strengthen:

- oversized serif display typography;
- numbered chapters and project indices;
- fine rules, restrained grids, and technical annotations;
- alternating wide visual bands and focused reading columns;
- clear project-kind labels;
- more deliberate spacing and bilingual line breaking;
- responsive hierarchy instead of simply stacking desktop blocks.

Use a two-level serif display system:

- Cormorant Garamond for English project names, project heroes, homepage project titles, and the largest exhibition statements;
- Newsreader for longer English section headings, editorial subheads, and quotations where steadier reading matters;
- Instrument Sans for English interface, metadata, labels, and body text;
- Noto Serif SC for Chinese project names, heroes, display text, and section headings;
- Noto Sans SC for Chinese interface, metadata, labels, and body text.

Cormorant Garamond is bundled locally with the site rather than loaded from a remote font service. The homepage project names must no longer inherit the sans-serif heading stack. Font roles are explicit design tokens so the hierarchy remains consistent across pages. Weight, optical size, tracking, line height, measure, and language-specific wrapping are tuned independently.

The homepage stays relatively bright and restrained so all projects remain coherent. Project detail pages may use darker exhibition bands. Notes receives the same typography and spacing system but no project-specific decoration.

### Project Detail Pages

The common detail shell gains:

- a stronger exhibition hero;
- project index and localized kind;
- numbered narrative chapters;
- improved metadata hierarchy;
- wider media moments;
- a narrower, more readable prose measure;
- consistent source and external-link treatment.

Existing DialogTree, Side B, and NBTI content remains valid and does not require a narrative rewrite. Their pages inherit the common visual improvements.

Mundus and OmniPet each receive one distinctive dark exhibition section. These sections must still share the same typography, spacing, color-token, and accessibility rules as the rest of the site.

## Component Design

### Content Schema

Extend project metadata with:

- `featured: boolean`;
- `kind: { en: string; zh: string }`.

`order` continues to define ordering within the featured group. Side B uses `featured: false`; its detail page is still generated because routing continues to use the complete collection.

The homepage reads the collection once, separates featured and non-featured entries, and renders both groups intentionally. RSZ remains a configured non-collection item until there is a reason to migrate it.

### MundusStory

`MundusStory.astro` owns one concise three-mode product overview. Shared
platform and extension text supports that image without introducing another
visual.

Use semantic HTML and inline or component-scoped SVG/CSS. Diagrams require readable text alternatives, meaningful source order, and a static reduced-motion state. They must not require JavaScript to convey core information.

### OmniPetStory

`OmniPetStory.astro` owns one SuShi public-outcome visual plus a compact
text-first engine flow.

The visitor-facing diagram uses only public concepts. It does not expose private filenames, paths, evidence, or repository details.

### Shared Presentation

Avoid expanding the common route into a project-ID switchboard. Project-specific MDX files import their own story components. Shared layout and presentation primitives may be extracted where both components genuinely use the same contract, but no premature generic diagram framework is required.

## Media Strategy

### Mundus

Capture public screenshots from the deployed site for:

- Other Side;
- Development Unpacked;
- Sunline.

Use a composed mode overview for the homepage preview and one representative globe capture in the detail page. Captures must reflect the public site and contain no browser or local-development artifacts.

### OmniPet

Use only public assets from the OmniPets catalog and public repository:

- SuShi preview;
- a compact code-drawn engine-to-release overview.

Do not use private production screenshots. If a public screenshot is not useful, use code-drawn workflow visuals rather than a placeholder or fabricated product UI.

All images require localized alternative text. Image crops must remain legible on mobile, and high-resolution assets should be converted to efficient web formats where appropriate.

Each Story uses localized accessible names through `aria-labelledby`; fixed
English `aria-label` values are not used for bilingual semantic groups.
Multi-column Story layouts collapse to one column at 1024 px and below, and
every grid child remains width-safe.

## Interaction and Motion

Motion is restrained and explanatory:

- subtle section reveals or line drawing may support the exhibition feel;
- no essential content depends on animation;
- `prefers-reduced-motion` removes nonessential transitions;
- no scroll-jacking, parallax that harms reading, or continuously expensive WebGL is added to the portfolio itself.

The diagrams are representations of the projects, not embedded copies of their runtimes.

## Error and Fallback Behavior

- A missing public screenshot falls back to a code-drawn structural visual, never a generic placeholder image.
- Invalid project metadata fails the Astro build through the content schema.
- External links use approved public URLs and safe new-tab attributes.
- Diagram meaning remains available as text when CSS, SVG animation, or motion is unavailable.
- Dark exhibition sections use tokenized colors with sufficient contrast in both site themes.
- Unsupported or unverifiable technical claims are omitted rather than softened into ambiguous marketing language.

## Verification

Implementation is complete only after:

- `npm run build` passes;
- all project collection entries pass the updated schema;
- homepage order is DialogTree, Mundus, OmniPet, NBTI;
- Side B appears first in Other Work and still opens its detail route;
- all five project detail routes render successfully;
- English and Chinese content switch correctly on every affected page;
- light and dark themes preserve contrast and diagram legibility;
- desktop and mobile layouts are checked in a real browser;
- project navigation, public links, and base-path asset URLs work under GitHub Pages;
- images have localized alternatives;
- keyboard navigation and visible focus remain intact;
- reduced-motion behavior is verified;
- browser console and network checks reveal no new errors;
- Mundus technical claims are cross-checked against its public code and documentation;
- OmniPet public claims are cross-checked against the public engine and catalog, with no private material exposed.
- the fact gate contains fewer atomic product assertions, and every assertion
  binds visible English MDX, Chinese MDX, Story text, and reviewed public
  evidence;
- unshown low-level atlas, row-count, solar-threshold, and city-count facts are
  not release gates.

## Out of Scope

- Rebuilding Mundus inside the portfolio.
- Adding a live OmniPet generation service.
- Publishing or linking private OmniPet repositories.
- Rewriting all existing case-study prose.
- Introducing a CMS, client-side framework, remote font service, or generic diagram editor.
- Claiming planned OmniPet community features as already shipped.
- Presenting Mundus approximations as legal, navigational, or engineering authority.
