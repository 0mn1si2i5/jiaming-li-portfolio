# Mundus Portfolio Expansion Design

## Goal

Add Mundus as a concise bilingual product case study while retaining the
portfolio's static Astro architecture and digital research exhibition system.
The published case must describe only the deployed Mundus V1.1 public surface.

## Public Hierarchy

Selected Work is ordered:

1. DialogTree
2. Mundus
3. NBTI

Side B remains first in Other Work, followed by RSZ Namelist. Grouping and
ordering remain content metadata rather than project-ID conditionals.

## Mundus Narrative

Mundus is a personal digital globe maintained over time, not a professional GIS
editor, street-navigation product, or authoritative scientific service. The
case follows five concise beats:

1. world knowledge is split across maps, tables, astronomy tools, and portals;
2. one user loop preserves a place while changing observation lenses;
3. Other Side, Development, Unpacked, and Sunline are the first shipped lenses,
   not a final catalog;
4. Parchment Atlas delivers the draggable cross-section, bilingual GeoNames
   search, bilateral city relations, and Natural Earth vector globe;
5. static delivery, pinned data, accessibility, and release gates make future
   product additions maintainable.

The page uses one public hero and one three-mode Story visual. English and
Chinese must agree in meaning. Public links target the live V1.1 Pages product
and repository. The page states that Mundus is not a runtime plugin platform.
GHSL Human Morphology remains outside the public product after
`STOP_GLOBAL_MORPHOLOGY`; private review, migration, and candidate-only evidence
are not published.

## Shared Presentation

The generic portfolio expansion retains:

- explicit `featured` and localized `kind` project metadata;
- Cormorant Garamond, Newsreader, Instrument Sans, Noto Serif SC, and Noto Sans
  SC as locally bundled type roles;
- numbered project chapters, wider media moments, readable prose measures, and
  responsive homepage composition;
- semantic HTML, localized alternative text, visible keyboard focus, and
  reduced-motion behavior;
- GitHub Pages `BASE_URL` handling for every local media path.

The common project route renders the complete collection. Project-specific MDX
owns its Story component; the shared route does not become a project switchboard.

## Evidence Boundary

Visitor-visible Mundus claims are verified only against immutable reviewed
and deployed commit `c6e625fa68879f9771debffebdaf32e295d56769`,
using `git show` semantics. The fact catalog covers the maintained personal
globe, observation loop, public V1.1 capabilities, maintainable release
decisions, and explicit GHSL/product boundaries. No other product repository is
a required build input.

Pull requests run checkout, install, tests, build, release verification, and a
bounded Pages artifact upload. Deployment is restricted to non-PR runs on
`refs/heads/main`, with Pages and id-token permissions owned only by the deploy
job.

## Acceptance

- Selected Work is DialogTree, Mundus, NBTI.
- Side B remains in Other Work and its route remains available.
- Generated routes are home, About, DialogTree, Mundus, NBTI, and Side B.
- No `/projects/omnipet` route or OmniPet visitor content is generated.
- Mundus works in English and Chinese, light and dark themes, reduced motion,
  and widths 1440, 1024, 768, and 390.
- Keyboard focus is visible; exactly four homepage images and two Mundus-page
  images load without error.
- Browser console and network evidence are failure-free.
- Tests, build, release verification, privacy scan, and `git diff --check`
  pass against the exact final tree.

## Out Of Scope

- Mundus product development, tag creation, or Release creation.
- OmniPet portfolio publication in this release.
- Changes to DialogTree, NBTI, or Side B content.
- Merge, Pages deployment, tags, Releases, repository settings, or history
  rewriting.
