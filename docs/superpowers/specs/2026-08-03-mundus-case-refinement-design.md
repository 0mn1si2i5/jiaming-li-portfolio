# Mundus Case Refinement Design

## Goal

Refresh the Mundus case study against the public deployment at
`378fe528ca1c8f83f0280f83383b5e785e851285`. The update gives each screenshot
one clear job and rewrites the bilingual narrative in a direct editorial voice.

The case describes the product that a visitor can open today. Unpublished
research and speculative capabilities stay out of the page.

## Image Roles

The portfolio uses three Mundus source images while keeping the project detail
page at two visible images.

### Homepage preview

The homepage receives a dedicated preview asset. It shows only the globe, or a
deliberate crop of the globe, without navigation, controls, result panels, or
small interface text. The crop should remain legible at the card's desktop and
mobile sizes and preserve the Parchment Atlas color and material treatment.

### Project hero

The project page hero shows the complete public desktop interface. Capture it
from a viewport wide enough for the globe, controls, and right result panel to
retain their intended layout. The selected Other Side scene must contain real
results, and every line in the right panel must remain within its container.

The source capture should be at least 1920 CSS pixels wide. A 2x device scale
may be used for sharper type, but layout correctness is judged in CSS pixels.
Before accepting the image, inspect all visible panel elements for horizontal
and vertical overflow.

### Story detail

The Story image focuses on the Other Side interaction: the through-Earth
cross-section, endpoint relationship, and nearby represented cities. It may
crop away global navigation and secondary controls. Labels included in the
crop must be complete and readable at the rendered Story width.

The Story component keeps its existing figure and caption structure. The image
ratio must follow the new source crop rather than stretching a 16:10 screenshot
into the current 4:3 box.

## Narrative

The five-part bilingual structure remains:

1. the question Mundus addresses;
2. the current product flow;
3. the three available observation lenses;
4. the latest public release;
5. the decisions that make continued maintenance practical.

The rewrite uses concrete subjects and actions. It avoids corrective contrasts
such as "not X but Y", "rather than", "不是……而是……", and repeated statements
about what the product does not claim to be. Product boundaries appear as
plain scope statements only when they help a visitor understand current
behavior.

The prose should read as a maintained product case:

- describe what a visitor selects, moves, reads, and shares;
- explain how the globe preserves place and interaction context;
- connect data snapshots, hashes, lazy loading, bilingual copy, accessibility,
  and Pages verification to maintenance decisions;
- present Other Side, Development, Unpacked, and Sunline as the current
  observation lenses without declaring a permanent catalog;
- use natural English and Chinese composition instead of sentence-by-sentence
  literal translation.

Release-administration language belongs in verification documentation, not in
visitor copy. The page should not discuss candidate status, tags, release
objects, internal stop decisions, or unpublished work.

## Current Public Update

The evidence revision moves from
`c6e625fa68879f9771debffebdaf32e295d56769` to
`378fe528ca1c8f83f0280f83383b5e785e851285`.

The revised case may include public behavior introduced by that deployment:

- closer globe inspection;
- stable globe color while dragging the antipode cross-section;
- a clearer Sunline twilight state;
- exact-location sharing with an explicit privacy disclosure.

Every included statement must be supported by the immutable commit and by the
public Pages behavior. The fact catalog should replace unpublished-boundary
assertions with a visitor-visible assertion about the updated interaction and
sharing contract.

## Files and Ownership

Expected maintained changes:

- `src/content/projects/mundus.mdx` for bilingual narrative and media metadata;
- `src/components/MundusStory.astro` for Story copy, alt text, and image ratio;
- `public/media/mundus/` for one homepage crop, one full-interface hero, and one
  Story detail;
- `.github/workflows/deploy.yml` and verification revision files for the new
  immutable Mundus source;
- focused tests and fact rules for the new prose and public behavior;
- current browser evidence and screenshots after the final build changes.

No shared layout change is planned unless the full-resolution hero still
renders too narrowly after the source image is corrected. Any such change must
remain scoped to Mundus media presentation.

## Verification

Source-image checks:

- homepage preview contains no result-panel text;
- hero source dimensions meet the minimum capture width;
- hero result-panel descendants have no measured overflow;
- Story crop contains complete labels and no clipped text;
- all three source images decode successfully and have distinct hashes.

Portfolio browser checks:

- homepage preview remains clear at 1440, 1024, 768, and 390 widths;
- the Mundus page shows exactly two images;
- English and Chinese content render without clipping;
- light and dark themes remain readable;
- keyboard focus and reduced motion still pass;
- all image and route requests stay under `/jiaming-li-portfolio/`;
- console and failed-request counts remain zero;
- `/projects/omnipet` remains absent;
- Selected Work order remains DialogTree, Mundus, NBTI.

Repository gates:

```text
npm ci
npm audit --audit-level=high
npm test
npm run build
npm run verify
git diff --check
```

The existing Draft PR remains Draft. Its deploy job stays skipped, and the
portfolio `main` branch and Pages deployment remain unchanged.

## Acceptance

- The homepage card uses a globe-only crop.
- The project hero shows the complete current interface with no result-panel
  overflow.
- The Story image gives the Other Side relationship enough scale for its
  labels and geometry to read clearly.
- The detail page still displays two images.
- English and Chinese copy contain no formulaic corrective contrasts.
- Visitor copy contains only current public product behavior.
- Fact verification is pinned to `378fe528ca1c8f83f0280f83383b5e785e851285`.
- Local and remote validation pass at the same final PR head.

## Out of Scope

- Mundus product changes.
- Portfolio merge or Pages deployment.
- OmniPet restoration or preservation-branch changes.
- New routes, shared design-system work, or additional case-study sections.
- Tags, Releases, repository settings, or history rewriting.
