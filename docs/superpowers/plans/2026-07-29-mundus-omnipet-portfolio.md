# Mundus Portfolio Expansion Implementation Plan

**Goal:** Bind the bilingual Mundus case study to the verified V1.1 Pages
product without making any deferred product a build input.

**Architecture:** Astro Content Collections remain the source of truth. Mundus
owns one focused Story component and public media directory. Shared typography,
layout, accessibility, privacy, evidence, and Pages safeguards remain generic.

## Completed Foundation

- [x] Add `featured` and localized `kind` metadata.
- [x] Order Selected Work as DialogTree, Mundus, NBTI.
- [x] Keep Side B first in Other Work with its detail route.
- [x] Bundle the exhibition typography locally.
- [x] Apply the responsive homepage and common detail-page system.
- [x] Add the bilingual Mundus product narrative, one Story visual, and public
  screenshots.

## Mundus Evidence

- [x] Pin Mundus to deployed V1.1 public `main`
  `c6e625fa68879f9771debffebdaf32e295d56769`.
- [x] Verify the maintained personal globe and first three lenses.
- [x] Verify the shared observation loop and three delivered modes.
- [x] Verify public Parchment Atlas, cross-section, city-search, bilateral
  relation, and vector-globe behavior.
- [x] Verify static delivery, pinned data, accessibility, and release gates.
- [x] Verify that no runtime plugin platform exists and GHSL Human Morphology
  remains outside the public product.
- [x] Read evidence with `git show <revision>:<path>` so caller checkout state
  cannot alter results.

## Deferred Scope Retirement

- [x] Preserve the combined implementation at remote branch
  `feat/omnipet-portfolio-deferred`.
- [x] Remove the deferred case route, Story, media, links, visitor copy, facts,
  revisions, browser scenarios, source arguments, and CI checkouts.
- [x] Keep no optional private-source bypass or dummy fact.

## Pull Request Gate

- [x] Run on pull requests targeting `main`.
- [x] Check out the portfolio and exact deployed Mundus V1.1 source.
- [x] Run `npm ci`, `npm test`, `npm run build`, and `npm run verify` with an
  explicit isolated Mundus source root.
- [x] Pin all GitHub Actions to immutable SHAs.
- [x] Give build only `contents: read`; give deploy only `pages: write` and
  `id-token: write`.
- [x] Separate PR concurrency from main publication.
- [x] Gate deploy to non-PR events on `refs/heads/main`.

## Final Browser Evidence

- [x] Build the exact final tree and serve it under the GitHub Pages project
  base.
- [x] Capture homepage widths 1440, 1024, 768, and 390.
- [x] Capture Mundus in English/Chinese, light/dark, desktop/mobile, and reduced
  motion.
- [x] Verify keyboard traversal and visible focus.
- [x] Verify exact image counts: homepage 4, Mundus 2.
- [x] Verify no generated deferred route, horizontal overflow, broken image,
  console message, or failed network request.
- [x] Record screenshot dimensions/SHA-256 and bind all generated HTML routes.

## Final Verification

Run from the clean feature worktree:

```bash
npm ci
npm test
npm run build
npm run verify
git diff --check
```

Expected:

- all tests pass;
- six static pages are generated;
- five Mundus facts pass from deployed commit `c6e625f`;
- browser evidence and screenshot hashes match the exact build;
- privacy scanning passes;
- the feature worktree is clean;
- PR build/test/verify passes and deploy is skipped;
- local, remote, and PR heads are identical;
- public main and Pages remain unchanged.
