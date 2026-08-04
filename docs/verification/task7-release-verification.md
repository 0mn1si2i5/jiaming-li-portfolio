# Mundus Release Verification

Verified on 2026-08-04 against the exact Mundus-only build on
`feat/mundus-next`.

## Result

The static build emits six pages:

```text
dist/index.html
dist/about/index.html
dist/projects/dialogtree/index.html
dist/projects/mundus/index.html
dist/projects/nbti/index.html
dist/projects/side-b/index.html
```

No deferred project route is generated. Selected Work is DialogTree, Mundus,
NBTI; Side B remains first in Other Work.

## Source Authority

Mundus is pinned to the deployed V1.1 public `main`:

```text
378fe528ca1c8f83f0280f83383b5e785e851285
```

The verifier requires that immutable commit object and reads evidence with
`git show <revision>:<path>`. Four visitor-visible facts bind the bilingual
case and Story to:

- `README.md`: the personal globe, its three current public modes, and the
  Parchment Atlas visual system;
- `tests/e2e/app.spec.ts`: the shared-location experience;
- the bilingual Portfolio case and Story: the same four claims in
  visitor-visible form.

Only capabilities observable on the public Pages deployment are presented as
shipped. Chronorbis is separately identified as an unfinished and unpublished
authorial direction. It is not a Mundus capability or an evidence-backed
product fact.

The source media set contains a globe-only homepage preview, a complete Other
Side interface hero, and three same-size Story mode previews for Other Side,
Development, and Sunline. The Story renders one preview image at a time, so
the project detail page retains two visible images: the hero and the current
Story preview.

## Browser Matrix

The exact GitHub Pages build was served under `/jiaming-li-portfolio/` and
exercised with isolated system Chrome browser sessions driven by
repository-owned Playwright.

| Scenario | Result |
| --- | --- |
| Homepage, English/light, 1440 x 900 | Correct project order; 4/4 images decoded; visible keyboard focus |
| Homepage, English/light, 1024 x 768 | No overflow; 4/4 images decoded; visible keyboard focus |
| Homepage, Chinese/dark/reduced, 768 x 1024 | No active animation or overflow; 4/4 images decoded |
| Homepage, Chinese/dark/reduced, 390 x 844 | No active animation, clipping, overflow, or broken image |
| Mundus, English/light, 1440 x 900 | 2/2 images decoded; one Story visual; visible keyboard focus |
| Mundus, Chinese/dark/reduced, 1440 x 900 | No active animation; 2/2 images decoded |
| Mundus, English/light, 390 x 844 | No overflow or broken image; visible keyboard focus |
| Mundus, Chinese/dark/reduced, 390 x 844 | No active animation; 2/2 images decoded |

Every scenario records its exact route, locale, theme, viewport, motion
preference, image counts, focus result, and overflow result in
`evidence/browser-matrix.json`. Reduced-motion observations are independently
cross-bound in `evidence/browser-reduced-motion.json`.

The Mundus scenarios cover pointer and keyboard switching across Other Side,
Development, and Sunline; synchronized image, alternative text, link, selected
state, and locale; new-tab targets; desktop and mobile selector layouts; and
reduced motion.

The eight isolated browser sessions reported:

- console messages: 0;
- normalized completed network requests: 220;
- statuses: 168 x 200 and 52 x 304;
- failed requests: 0;
- every local document, stylesheet, font, favicon, and image resolved from the
  GitHub Pages project base.

## Retained Screenshots

Eight optimized full-page WebP captures are bound by exact dimensions and
SHA-256 in `evidence/browser-screenshots.json`:

1. `task7-home-en-light-1440x900.webp`
2. `task7-home-en-light-1024x768.webp`
3. `task7-home-zh-dark-reduced-768x1024.webp`
4. `task7-home-zh-dark-reduced-390x844.webp`
5. `task7-mundus-en-light-1440x900.webp`
6. `task7-mundus-zh-dark-reduced-1440x900.webp`
7. `task7-mundus-en-light-390x844.webp`
8. `task7-mundus-zh-dark-reduced-390x844.webp`

The six generated HTML pages are independently SHA-256-bound in
`evidence/browser-build.json`; any rendered-byte change invalidates retained
browser evidence.

## Privacy And CI

The release verifier scans all final files as bytes and applicable text
encodings, recursively decodes HTML entities and URL encoding, and rejects
local paths, internal URLs, credentials, private keys, and high-entropy
secrets. Site-relative project-base asset paths are recognized structurally
rather than misclassified as secret tokens.

The workflow retains the intended Draft, non-deploying pull-request gate with
`contents: read`: portfolio checkout, exact Mundus checkout, `npm ci`, tests,
build, explicit-root verification, and a one-day Pages artifact. Actions use
immutable SHA pins. Only the deploy job receives Pages/id-token permissions,
and it is restricted to non-PR events on `refs/heads/main`.

PR #1 remains closed on its former `feat/mundus-omnipet-portfolio@bbf00b2`
head. The current authority is `feat/mundus-next`. A replacement Draft PR was
explicitly authorized for that branch so its exact head can run the
non-deploying pull-request gate.

## Commands

`MUNDUS_ROOT` points to the locally checked-out Mundus authority repository.

```bash
npm ci
npm audit --audit-level=high
npm test
npm run build
npm run verify -- --mundus-root "$MUNDUS_ROOT"
git diff --check
```

The explicit root keeps verification bound to that local authority checkout.

## Local Gate Result

The Task 8 local gate was rerun from clean HEAD
`8e9f5516179fbd1eed7387cb441c642965f55f38`:

- `npm ci`: 339 packages installed and 340 packages audited;
- `npm audit --audit-level=high`: 0 vulnerabilities;
- `npm test`: 62 of 62 tests passed;
- `npm run build`: 6 static pages built;
- explicit-root release verification:
  `facts=4/4 browser=pass privacy=pass`;
- `git diff --check`: passed with no output.

The scope review found no OmniPet route, media, fact, visitor claim, or source
checkout; no GHSL visitor claim; and no `stop_global_morphology` reference in
`src`, `scripts`, or the deploy workflow. Chronorbis remains explicitly
unfinished, unpublished, and separate from Mundus. The built Mundus detail
page contains exactly two images. Deployment remains restricted to non-PR
events on `refs/heads/main`.

No dependency, source, workflow, browser evidence, screenshot, or unrelated
design file changed while rerunning the local gate. The only working-tree
change is this release record.

The local command evidence is recorded here. Remote exact-head CI is run only
through the authorized replacement Draft PR. This verification does not
reopen PR #1, merge a pull request, or deploy the site.
