# Task 7 Release Verification

Verified on 2026-07-29 against branch `feat/mundus-omnipet-portfolio`. The
publishing-rule baseline is `21c919b`; the first retained-evidence baseline is
`942dd12`. The verification used Node.js `v22.23.1`, npm `10.9.8`, Astro
`7.0.7`, and `agent-browser 0.27.0` driving Chrome.

## Result

Task 7 passes. The production build succeeds, all five project detail routes
are emitted, the generated site contains none of the scanned private terms or
remote font hosts, the browser acceptance matrix passes without console errors
or failed requests, every approved public link reaches the expected
destination, and the Mundus and OmniPet claims remain supported by public
sources.

## Repository Checks

Run from the repository root:

```bash
node --version
npm --version
npm run build
git diff --check
find dist/projects -maxdepth 2 -name index.html -print | sort
grep -R -n -E \
  'OmniPet-Production|OmniPet-Program|/Users/bytedance|OPENAI_API_KEY' \
  dist
grep -R -n -E 'fonts\.googleapis\.com|fonts\.gstatic\.com' dist
find dist -type f -name '*.woff2' | sort
```

Observed results:

- `npm run build`: exit `0`; seven static pages generated.
- `git diff --check`: exit `0`.
- Project routes:

  ```text
  dist/projects/dialogtree/index.html
  dist/projects/mundus/index.html
  dist/projects/nbti/index.html
  dist/projects/omnipet/index.html
  dist/projects/side-b/index.html
  ```

- Privacy scan: no matches.
- Remote-font scan: no matches.
- Hashed local WOFF2 output includes Cormorant Garamond, Instrument Sans,
  Newsreader, Noto Sans SC, and Noto Serif SC.

The two `grep` commands intentionally return `1` when they find no matches. The
captured verification wrapper converts that expected empty result into
`[no matches]` and fails only if a match is present:

```bash
if grep -R -n -E \
  'OmniPet-Production|OmniPet-Program|/Users/bytedance|OPENAI_API_KEY' \
  dist; then
  exit 21
else
  echo '[no matches]'
fi

if grep -R -n -E 'fonts\.googleapis\.com|fonts\.gstatic\.com' dist; then
  exit 22
else
  echo '[no matches]'
fi
```

## Browser Setup

Build output was served locally:

```bash
npm run preview -- --host 127.0.0.1 --port 4321
```

The global browser CLI was not installed and the sandbox did not permit writing
to the default home directory. A disposable browser home kept all runtime state
outside the repository:

```bash
mkdir -p /tmp/task7-evidence/browser-home
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --version
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence \
  open http://127.0.0.1:4321/
```

No browser profile, HAR file, dependency, or generated runtime state was added
to the repository.

## Acceptance Matrix

| Viewport | Locale | Theme | Reduced motion | Page | Result |
| --- | --- | --- | --- | --- | --- |
| 1440 x 900 | English | Light | Off | Homepage | Selected Work and Other Work order correct; no overflow or broken images |
| 1440 x 900 | Chinese | Dark | On | Mundus | Product-first narrative and two visuals; no animation, overflow, or broken images |
| 1440 x 900 | Chinese | Dark | On | OmniPet | Product-first narrative, two visuals, and two approved public links; no animation, overflow, or broken images |
| 768 x 1024 | Chinese | Dark | On | Homepage | Correct localized order and alternatives; 27 visible focusable controls; all lazy images decode |
| 390 x 844 | Chinese | Dark | On | Mundus | Product problem precedes overview; no animation, clipped text, overflow, or broken images |
| 390 x 844 | Chinese | Dark | On | OmniPet | Product problem precedes engine overview; no animation, overflow, or broken images |

Theme and locale controls were exercised independently: the session started in
English/light, switched to Chinese, then switched to dark. The resulting state
persisted across project navigation. The locale control changed its accessible
name from `切换至中文` to `Switch to English`; the theme control was localized
from `Switch color theme` to its Chinese alternative.

The homepage state was extracted with:

```bash
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence \
  set viewport 1440 900
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence \
  set media light
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence \
  open http://127.0.0.1:4321/
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence eval \
  'JSON.stringify({
    locale: document.documentElement.dataset.locale,
    theme: document.documentElement.dataset.theme,
    viewport: [innerWidth, innerHeight],
    reducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches,
    overflow: document.documentElement.scrollWidth > innerWidth,
    selected: [...document.querySelectorAll(".project-card h3")]
      .map((element) => element.innerText.trim()),
    other: [...document.querySelectorAll(".other-card h3")]
      .map((element) => element.innerText.trim()),
    kinds: [...document.querySelectorAll(".project-card .kind")]
      .map((element) => element.innerText.trim()),
    brokenImages: [...document.images]
      .filter((image) => image.complete && !image.naturalWidth)
      .map((image) => image.src)
  })'
```

Observed English/light homepage values:

```json
{
  "locale": "en",
  "theme": "light",
  "viewport": [1440, 900],
  "reducedMotion": false,
  "overflow": false,
  "selected": ["DialogTree", "Mundus", "OmniPet", "NBTI"],
  "other": ["Side B", "RSZ Namelist"],
  "brokenImages": []
}
```

Reduced motion and responsive behavior were checked with:

```bash
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence \
  set media dark reduced-motion
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence \
  set viewport 390 844
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence \
  open http://127.0.0.1:4321/projects/mundus
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence eval \
  'JSON.stringify({
    reducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches,
    overflow: document.documentElement.scrollWidth > innerWidth,
    visibleText: document.querySelector("main").innerText.length,
    animated: [...document.querySelectorAll("*")].filter((element) => {
      const style = getComputedStyle(element);
      return style.animationName !== "none" &&
        style.animationDuration !== "0s";
    }).length,
    brokenImages: [...document.images]
      .filter((image) => image.complete && !image.naturalWidth)
      .map((image) => image.src),
    clipped: [...document.querySelectorAll(
      "main h1, main h2, main h3, main p, main li"
    )]
      .filter((element) => element.scrollWidth > element.clientWidth + 1)
      .map((element) => element.innerText.slice(0, 80))
  })'
```

Mundus returned `reducedMotion: true`, `animated: 0`, `overflow: false`,
`brokenImages: []`, and `clipped: []`. OmniPet returned the same reduced-motion,
animation, overflow, and image results at both desktop and mobile widths.

At 768 x 1024, scrolling Other Work into view and waiting one second caused all
five homepage images to report `complete: true` with natural widths of 1600,
1440, 960, 1280, and 1600 pixels. Every image had localized alternative text.
Keyboard traversal reached visible links and applied the shared
`2px solid` focus outline; 27 visible links and buttons were focusable on the
tablet homepage.

## Console and Network

Commands:

```bash
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence console
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-evidence network requests
```

Observed:

- Console output: empty, `0` bytes.
- Recorded requests: `117`.
- Status `200`: `87`.
- Status `304`: `30`.
- Other statuses or failed requests: `0`.
- Documents, CSS, local WOFF2 files, favicon, and project images all loaded
  successfully.

## Machine-Readable Browser Evidence

The following sanitized JSON files retain the direct browser observations used
by this report:

- [Acceptance matrix](evidence/browser-matrix.json): six page, viewport,
  locale, theme, image, focus, and overflow scenarios.
- [Reduced-motion observations](evidence/browser-reduced-motion.json): four
  Mundus and OmniPet desktop/mobile observations.
- [Console observations](evidence/browser-console.json): zero messages, errors,
  or warnings.
- [Network observations](evidence/browser-network.json): 117 normalized
  requests, status and resource-type counts, and an empty failure list.
- [Screenshot manifest](evidence/browser-screenshots.json): five retained
  captures with scenario, dimensions, and SHA-256.

Browser JSON contains only relative routes or resource paths, stable scenario
labels, and aggregate values. It excludes browser profile data, request IDs,
headers, query secrets, filesystem paths, and host-specific user information.
The unified validator checks schema versions, required scenarios, console and
network aggregate consistency, reduced-motion/matrix agreement, screenshot
dimensions, and screenshot hashes. Scenario order and every required success
field are mandatory; all requests must be successful, failure lists must be
empty, and console messages must use structured levels while the retained
release evidence remains warning- and error-free.
Each of the six matrix scenarios is bound to its exact route, locale, theme,
viewport, and reduced-motion value; changing a valid field to another valid
value still fails verification.

## Route and Link Acceptance

Each URL was opened in a separate Chrome session, after which the final URL and
document title were read with:

```bash
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-links open <URL>
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-links get url
HOME=/tmp/task7-evidence/browser-home \
  npx --yes agent-browser --session task7-links get title
```

| Target | Final destination | Observed title |
| --- | --- | --- |
| Homepage | `http://127.0.0.1:4321/` | Jiaming Li |
| DialogTree route | `/projects/dialogtree` | DialogTree - Jiaming Li |
| Mundus route | `/projects/mundus` | Mundus - Jiaming Li |
| OmniPet route | `/projects/omnipet` | OmniPet - Jiaming Li |
| NBTI route | `/projects/nbti` | NBTI - Jiaming Li |
| Side B route | `/projects/side-b` | Side B - Jiaming Li |
| DialogTree demo | `https://chat.golir.top/` | Dialog Tree |
| DialogTree paper | `https://dl.acm.org/doi/10.1145/3772363.3798792` | ACM wait page |
| Mundus site | `https://0mn1si2i5.github.io/Mundus/` | Mundus interactive globe |
| Mundus source | `https://github.com/0mn1si2i5/Mundus` | Expected GitHub repository |
| OmniPet source | `https://github.com/0mn1si2i5/OmniPet` | Expected GitHub repository |
| OmniPets catalog | `https://github.com/0mn1si2i5/OmniPets` | Expected GitHub repository |
| Side B source | `https://github.com/0mn1si2i5/Side-B` | Expected GitHub repository |
| NBTI site | `https://0mn1si2i5.github.io/NBTI/` | NBTI personality test |
| NBTI source | `https://github.com/0mn1si2i5/NBTI` | Expected GitHub repository |
| RSZ Workshop | Steam Workshop item `2804107924` | RSZ Namelist workshop page |
| GitHub profile | `https://github.com/0mn1si2i5` | 0mn1si2i5 (Li Jiaming) |

All `open` commands exited `0`. The DOI redirected to the expected ACM URL.

## Technical Claim Review

The check deliberately uses only the portfolio prose and reviewed public files
named in the implementation plan. Every assertion is bidirectional: the
visitor-facing claim must exist in `mundus.mdx` or `omnipet.mdx`, and its
corresponding evidence must exist in the pinned public source revision.

### Mundus

| Public evidence | Claims checked |
| --- | --- |
| `README.md` | Three-mode public scope; 110m/50m vector quality and raster fallback |
| `src/features/modes/modeRegistry.ts` | Three registered modes; spatial, human, and temporal categories; versioned Zod state; data resources |
| `src/features/sunline/solar.ts` | 2000-2099 range; minute precision; `-0.833` degree sunrise altitude; daylight, civil twilight, polar day, and polar night |
| `src/data/registry.ts` | Manifest validation for source, license, SHA-256, transformations, missing-value and boundary policies, geometry metrics |
| `DATA_SOURCES.md` | 6,944 GeoNames records; UNDP 1990-2023 series; Natural Earth 110m/50m policy; NOAA/Meeus-style approximation and limitations |

### OmniPet

| Public evidence | Claims checked |
| --- | --- |
| `README.md` | Alpha status; Python engine and CLI; resumable state; approval, QA, packaging, export, and verification |
| `docs/architecture.md` | No automatic retry; transactional repair; downstream invalidation; allowlisted provider; clean public boundary |
| `docs/generation-workflow.md` | Nine standard rows plus two look rows; 8 x 11 atlas; exact 1536 x 2288 dimensions; explicit approval gates |
| `src/omnipet/public_release.py` | Closed release file set; canonical release record; SHA-256 binding; extra-file and private-material rejection |
| OmniPets `README.md` and `catalog/index.json` | SuShi v1.0.1; sprite v2; public preview, atlas, manifest, documentation, license, and hashes |

The unified release verifier checks 13 atomic, product-level facts:

```bash
npm run verify
```

The 13 rules live in `scripts/verification/facts.json`. Each item contains
separate claim and evidence sources. The product-focused revision keeps 13
pinned product-evidence checks but binds them to concise, visitor-visible claims about
platform contracts, reproducibility, recoverability, release boundaries, and
public outcomes; low-level source evidence no longer forces an algorithm or
atlas-dimension exhibition into the page. MDX checks remove frontmatter,
imports, HTML/JSX comments; source
checks remove comments and unrelated standalone string assignments; JSON
evidence uses structural `json_path` rules. The latest run returned `13/13`.
Elements hidden with `hidden`, `aria-hidden`, `display: none`, or
`visibility: hidden`, plus multiline exported metadata/functions, are excluded
from visitor-visible claim text.

The facts module pins the following public source revisions. It accepts
explicit source roots and reads evidence with `git show <SHA>:<path>`, so
uncommitted working-tree content cannot influence verification:

| Repository | Revision |
| --- | --- |
| Mundus | `b7b2d0f9e453efd8be83216a43e642f0ee7350ed` |
| OmniPet | `f08e47c7dcee1bf7d89e1c673c73abb6fa90c20d` |
| OmniPets | `081b7c6f651183987c79c4321ff46e1b082e03b7` |

Deployment CI checks out all three repositories at those exact revisions and
passes their paths explicitly. Negative tests cover weakened semantic facts,
inconsistent browser aggregates, screenshot hash drift, absolute paths,
internal URLs, credentials, and high-entropy secrets:

```bash
npm test
```

After `npm run build`, the same entry point scans final `dist/` text for
Unix/macOS/Windows paths, `file://`, loopback/private-network URLs, credential
patterns, private keys, and high-entropy tokens. Known content hashes and
ordinary Astro asset names are narrowly excluded. Every file is also scanned
as raw bytes and through applicable UTF-8/UTF-16 decoding, so image metadata or
payloads appended to binary assets cannot bypass the gate. HTML entities and
URL encoding are recursively decoded to a fixed depth before each scan.

Screenshot paths must match the fixed filename for their scenario, contain no
directory or traversal component, resolve directly inside the assets root, and
must not be symlinks.

## Product-Focused Revalidation

The 2026-07-29 product-feedback pass removed the six-card Mundus algorithm
atlas, five-stage data flow, seven-stage OmniPet workflow, and six-card
extension-contract exhibition. The replacement keeps:

- Mundus: the product problem, shared platform, three-mode user value,
  extension contract, one mode overview, and one representative globe image.
- OmniPet: the product problem, resumable review engine, publication boundary,
  Alpha limitation, compact three-step overview, and SuShi release result.

Both Story components now render exactly two images. In Chinese dark mode with
reduced motion, Mundus reports `924` visible text characters on desktop and
`921` on mobile; OmniPet reports `1066` and `1063`. The previous retained
values were `3609` and `2529`, respectively. All four scenarios report two
product visuals, zero active animations, zero broken images, and no horizontal
overflow. Visual inspection also confirms that the product problem and
platform/engine capability precede the visual overview in both languages.

## Review-Driven Boundary Revalidation

The final review pass limits each project page to two images total: the shared
public hero plus one Story image. Browser inspection at 1440 x 900 and 390 x
844 reported `totalImageCount: 2` and `productVisualCount: 1` for both Mundus
and OmniPet, with zero broken images or horizontal overflow.

At 1024 px, OmniPet's engine flow and outcome each resolved to one CSS grid
column. At 768 px, Mundus's mode overview resolved to one column. The Chinese
semantic group names resolved to `公开发布属性` and `Mundus 扩展契约`; both are
provided by localized `aria-labelledby` targets rather than fixed English
labels.

The fact gate now contains 13 atomic product claims. Every claim binds visible
English MDX, visible Chinese MDX, Story text, and one reviewed public source at
a pinned revision. Unshown atlas dimensions, action-row counts, solar
thresholds, city counts, and other implementation-only details were deleted
from the release gate. OmniPet's remaining claims explicitly cover the shipped
extension axes and the single allowlisted built-in provider boundary.

## Screenshot Evidence

Five optimized full-page WebP captures are retained:

1. [English/light homepage at 1440 x 900](assets/task7-home-en-light-1440x900.webp)
2. [Chinese/dark Mundus at 1440 x 900 with reduced motion](assets/task7-mundus-zh-dark-reduced-1440x900.webp)
3. [Chinese/dark Mundus at 390 x 844 with reduced motion](assets/task7-mundus-zh-dark-reduced-390x844.webp)
4. [Chinese/dark OmniPet at 1440 x 900 with reduced motion](assets/task7-omnipet-zh-dark-reduced-1440x900.webp)
5. [Chinese/dark OmniPet at 390 x 844 with reduced motion](assets/task7-omnipet-zh-dark-reduced-390x844.webp)

The original PNG captures were stored only under `/tmp/task7-evidence`. The
retained WebP files use quality `82`; desktop captures were reduced to 1200
pixels wide and mobile captures remain 390 pixels wide. The two review-gap
captures add approximately 424 KB for Mundus desktop and 320 KB for OmniPet
mobile.

Conversion command:

```bash
node_modules/ffmpeg-static/ffmpeg \
  -y -loglevel error -i <capture.png> \
  -vf scale=<width>:-2 \
  -c:v libwebp -quality 82 -compression_level 6 \
  docs/verification/assets/<capture>.webp
```
