# Mundus Portfolio Expansion Design

## Goal

Add Mundus as a concise bilingual product case study while retaining the
portfolio's static Astro architecture and digital research exhibition system.
The published case must describe only the deployed Mundus V1.0.0 surface.

## Public Hierarchy

Selected Work is ordered:

1. DialogTree
2. Mundus
3. NBTI

Side B remains first in Other Work, followed by RSZ Namelist. Grouping and
ordering remain content metadata rather than project-ID conditionals.

## Mundus Narrative

Mundus is an interactive 3D Earth observation product, not a professional GIS
editor or generic mapping platform. The case follows five concise beats:

1. the problem of comparing several ways of understanding one place;
2. a shared WebGL globe and interaction model;
3. three deployed V1 modes: Other Side, Development, Unpacked, and Sunline;
4. a registered mode contract with versioned state and declared data;
5. visible solar, development-data, cartographic, and major-city limits.

The page uses one public hero and one three-mode Story visual. English and
Chinese must agree in meaning. Public links target the V1.0.0 live site and
repository. Parchment Atlas, GeoNames search, bilateral relations, vector-globe
hardening, GHSL work, private review, migration, and performance evidence are
not published.

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
commit `a5ff99bc60fb7cd2e6e14f4d3bc4f54e5abfb4a1`, using `git show` semantics.
The fact catalog covers the three modes, shared globe, versioned mode contract,
validated data registry, and published limits. No other product repository is a
required build input.

Pull requests run checkout, install, tests, build, release verification, and a
bounded Pages artifact upload. Deployment is restricted to non-PR runs on
`refs/heads/main`, with Pages and id-token permissions owned only by the deploy
job.

## Acceptance

- Selected Work is DialogTree, Mundus, NBTI.
- Side B remains in Other Work and its route remains available.
- Generated routes are home, Notes, DialogTree, Mundus, NBTI, and Side B.
- No `/projects/omnipet` route or OmniPet visitor content is generated.
- Mundus works in English and Chinese, light and dark themes, reduced motion,
  and widths 1440, 1024, 768, and 390.
- Keyboard focus is visible; exactly four homepage images and two Mundus-page
  images load without error.
- Browser console and network evidence are failure-free.
- Tests, build, release verification, privacy scan, and `git diff --check`
  pass against the exact final tree.

## Out Of Scope

- Mundus product development or V1.1 publication.
- OmniPet portfolio publication in this release.
- Changes to DialogTree, NBTI, or Side B content.
- Merge, Pages deployment, tags, Releases, repository settings, or history
  rewriting.
