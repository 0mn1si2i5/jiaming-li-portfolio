# Mundus Release Verification

## Release

- Visible-history merge commit:
  `75c937166c17716463b472efd9365d03fa2f41f1`
- Original GitHub merge object:
  `3966ee16d343f402b497d3da146ef68c4a807124`
- Pull request:
  [#2](https://github.com/0mn1si2i5/jiaming-li-portfolio/pull/2)
- GitHub Actions run:
  [30915469732](https://github.com/0mn1si2i5/jiaming-li-portfolio/actions/runs/30915469732)
- GitHub Pages deployment:
  `5744970621`
- Published:
  `2026-08-04`

The original merge object passed the complete build and verification workflow
and was deployed successfully to GitHub Pages. The visible-history commit is
its content-equivalent replacement after repository history normalization.

## Scope

The release presents the current public Mundus product and a separate
Chronorbis concept:

- Mundus remains the shipped, evidence-backed product.
- Chronorbis is explicitly identified as unfinished and unpublished.
- No OmniPet or GHSL product claim is included.

The static build contains exactly six routes:

```text
/
/about/
/projects/dialogtree/
/projects/mundus/
/projects/nbti/
/projects/side-b/
```

## Source Authority

Mundus evidence is pinned to immutable commit:

```text
378fe528ca1c8f83f0280f83383b5e785e851285
```

The verifier requires this commit object and reads source evidence with
`git show <revision>:<path>`. Four visitor-visible fact groups are retained:

1. the public personal globe;
2. the current Other Side, Development, and Sunline modes;
3. the Parchment Atlas visual system;
4. the shared location and reproducible static experience.

The complete fact catalog is stored in
`scripts/verification/facts.json`. Source revision evidence is stored in
`evidence/source-revisions.json`.

## Media

The release contains:

- one globe-only homepage preview;
- one full Other Side interface hero;
- three `1920 x 1080` mode previews for Other Side, Development, and Sunline.

The Mundus project page renders one Story preview at a time. Media dimensions,
roles, source revision, and SHA-256 values are recorded in
`evidence/mundus-media.json`.

## Browser Coverage

Eight isolated browser scenarios cover:

- English and Chinese locales;
- light and dark themes;
- desktop, tablet, and mobile viewports;
- normal and reduced motion;
- keyboard focus visibility;
- image decoding and Pages base-path resolution;
- layout overflow;
- pointer and keyboard switching across all Mundus preview modes;
- synchronized image, alternative text, link, selection, and locale state;
- new-tab destinations.

Observed browser results:

- scenarios: 8;
- completed requests: 220;
- HTTP 200: 168;
- HTTP 304: 52;
- failed requests: 0;
- console messages: 0;
- console errors: 0.

The retained evidence is stored in:

- `evidence/browser-build.json`;
- `evidence/browser-console.json`;
- `evidence/browser-matrix.json`;
- `evidence/browser-network.json`;
- `evidence/browser-reduced-motion.json`;
- `evidence/browser-screenshots.json`.

Eight WebP screenshots under `docs/verification/assets/` are bound to the
screenshot manifest by filename, dimensions, and SHA-256.

## Privacy And Integrity

The release verifier:

- binds retained browser evidence to the exact generated HTML;
- validates screenshot paths, dimensions, and SHA-256;
- checks fact claims against immutable public source revisions;
- scans generated files for local paths, internal URLs, credentials, private
  keys, and high-entropy secrets;
- rejects missing, stale, malformed, or inconsistent evidence.

Any rendered HTML change invalidates `evidence/browser-build.json` and requires
fresh browser evidence.

## Verification Commands

`MUNDUS_ROOT` must point to a local checkout containing the pinned Mundus
commit.

```bash
npm ci
npm audit --audit-level=high
npm test
npm run build
npm run verify -- --mundus-root "$MUNDUS_ROOT"
git diff --check
```

Verified results:

- dependency audit: 0 vulnerabilities;
- Python tests: 62/62 passed;
- Astro build: 6 pages;
- release verifier:
  `facts=4/4 browser=pass privacy=pass`;
- pull-request exact-head build: passed;
- merge-commit build: passed;
- GitHub Pages deployment: passed.

## Deployment Boundary

Pull requests run the complete non-deploying verification workflow. Deployment
is permitted only for non-pull-request events on `refs/heads/main`. The
original release was deployed from GitHub merge object
`3966ee16d343f402b497d3da146ef68c4a807124`. Its normalized visible-history
equivalent is `75c937166c17716463b472efd9365d03fa2f41f1`.
