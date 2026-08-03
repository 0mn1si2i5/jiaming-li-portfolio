# Mundus Release Verification

Verified on 2026-08-02 against the exact Mundus-only production build on
`feat/mundus-omnipet-portfolio`.

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
c6e625fa68879f9771debffebdaf32e295d56769
```

The verifier requires that immutable commit object and reads evidence with
`git show <revision>:<path>`. Five visitor-visible facts bind the bilingual
case and Story to:

- `README.md`: the maintained personal globe, first three lenses, and public
  Parchment Atlas capabilities;
- `docs/PROJECT_PLAN.md`: the shared observation loop and current modes;
- `docs/2026-08-01-v1.1-publication-packet.md`: static architecture, hashed
  data, accessibility, and release gates;
- `docs/ROADMAP_HANDOFF.md`: product limits, the GHSL stop decision, and the
  frozen follow-on plans.

Only capabilities observable on the public Pages deployment are presented as
shipped. GHSL Human Morphology is explicitly not a public feature. The
`v1.0.0` tag and Release remain unchanged; no V1.1 tag or Release is claimed.
The two case-study media files are direct captures of that deployment: the
Other Side Parchment Atlas is the hero, and its open Mode atlas is the single
Story visual.

## Browser Matrix

The exact GitHub Pages build was served under `/jiaming-li-portfolio/` and exercised
with Playwright Chromium after the `agent-browser` daemon failed to establish a
CDP channel.

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

The eight isolated browser sessions reported:

- console messages: 0;
- normalized completed network requests: 96;
- statuses: 96 x 200;
- failed requests: 0;
- `/projects/omnipet` status: 404;
- the public Mundus site and repository links returned successful responses;
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

Pull requests run the complete non-deploying gate with `contents: read`:
portfolio checkout, exact Mundus checkout, `npm ci`, tests, build, explicit-root
verification, and a one-day Pages artifact. Actions use immutable SHA pins.
Only the deploy job receives Pages/id-token permissions, and it is restricted
to non-PR events on `refs/heads/main`.

## Commands

```bash
npm ci
npm test
npm run build
npm run verify
git diff --check
```

The final command evidence is recorded in the Draft PR and release closeout.
