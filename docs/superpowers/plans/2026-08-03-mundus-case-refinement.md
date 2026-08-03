# Mundus Case Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the Mundus case with three purpose-built images and a direct bilingual narrative bound to public deployment `378fe528ca1c8f83f0280f83383b5e785e851285`.

**Architecture:** Astro content metadata remains the owner of the homepage preview and project hero, while `MundusStory.astro` remains the owner of the single Story image. A repository-owned Playwright capture script reads the browser dependency from the Mundus checkout, verifies the live layout before capture, and writes a hash-bound media manifest. The existing immutable fact verifier and browser-evidence gate move to the latest deployed Mundus commit.

**Tech Stack:** Astro 7, MDX, TypeScript/Astro components, Python `unittest`, Playwright Chromium from the Mundus repository, `ffmpeg-static`, GitHub Actions, GitHub Pages.

---

## Execution Boundary

Use:

```text
/Users/bytedance/Desktop/Zen/Oh My Portfolio/.worktrees/portfolio-rename-migration
```

Expected starting identities:

```text
local implementation baseline: a47bef6a19d0a1f05e055c753ba7535c787d3d57
remote Draft PR head:          f777b4fc91540a4693062cd41a68cfc188c16c1a
Mundus public main/Pages:      378fe528ca1c8f83f0280f83383b5e785e851285
Draft PR:                      https://github.com/0mn1si2i5/jiaming-li-portfolio/pull/1
```

Do not use or clean the older
`.worktrees/mundus-omnipet-portfolio` worktree. It contains a user deletion.
Do not merge the PR, deploy the portfolio, restore OmniPet, update the OmniPet
preservation branch, or force-push.

## File Map

- `src/content.config.ts`: localized media schema, including preview-specific
  alternative text.
- `src/components/ProjectMedia.astro`: selects the homepage preview source and
  preview alt without changing shared layout.
- `src/content/projects/mundus.mdx`: visitor-facing bilingual narrative,
  homepage summary, hero/preview metadata, and public links.
- `src/components/MundusStory.astro`: Story copy, detail image, alt text, and
  natural source aspect ratio.
- `scripts/capture-mundus-media.mjs`: reproducible capture and overflow checks
  against the public Mundus deployment.
- `public/media/mundus/globe-preview.webp`: globe-only homepage crop.
- `public/media/mundus/other-side-full.webp`: complete project hero.
- `public/media/mundus/other-side-detail.webp`: focused Story image.
- `docs/verification/evidence/mundus-media.json`: source URL, deployed SHA,
  capture role, dimensions, hashes, and overflow result.
- `scripts/verification/facts.py` and `facts.json`: immutable revision and five
  current public facts.
- `.github/workflows/deploy.yml`: exact Mundus checkout used by PR validation.
- `tests/test_release_verification.py`: prose, media, evidence, and revision
  contracts.
- `tests/test_workflow.py`: CI source revision contract.
- `docs/verification/evidence/*.json` and
  `docs/verification/assets/task7-*.webp`: final build-bound browser evidence.
- `docs/verification/task7-release-verification.md`: final evidence summary.

### Task 1: Lock the new content and media contracts

**Files:**
- Modify: `tests/test_release_verification.py`
- Modify: `tests/test_workflow.py`

- [ ] **Step 1: Add failing prose and scope tests**

Replace `test_mundus_is_a_concise_product_case_study` and
`test_mundus_case_study_keeps_delivered_and_future_scope_distinct` with
assertions for the approved headings and voice:

```python
def test_mundus_case_uses_direct_editorial_voice(self) -> None:
    case = Path("src/content/projects/mundus.mdx").read_text(encoding="utf-8")
    story = Path("src/components/MundusStory.astro").read_text(encoding="utf-8")
    visitor_copy = f"{case}\n{story}"

    for heading in (
        "A globe I can keep extending",
        "One place, several ways to read it",
        "Three lenses in use today",
        "The current release",
        "Built for continued maintenance",
        "一颗持续生长的个人数字地球",
        "同一地点，几种观察方式",
        "目前使用的三个视角",
        "当前公开版本",
        "为长期维护做出的选择",
    ):
        self.assertIn(heading, case)

    for phrase in (
        "not a final",
        "not a candidate",
        "not street navigation",
        "not a plugin",
        "not runtime plugins",
        "rather than",
        "instead of",
        "不是最终",
        "不是候选",
        "不是街道",
        "不是插件",
        "而不是",
        "不代表",
        "GHSL",
        "STOP_GLOBAL_MORPHOLOGY",
    ):
        self.assertNotIn(phrase, visitor_copy)

    self.assertEqual(case.count("\n## "), 10)
    self.assertEqual(story.count("<img"), 1)
```

- [ ] **Step 2: Add a failing three-role media test**

Add to `TestProductCaseStudyFocus`:

```python
def test_mundus_media_has_three_distinct_roles(self) -> None:
    case = Path("src/content/projects/mundus.mdx").read_text(encoding="utf-8")
    story = Path("src/components/MundusStory.astro").read_text(encoding="utf-8")

    self.assertIn("src: /media/mundus/other-side-full.webp", case)
    self.assertIn("preview: /media/mundus/globe-preview.webp", case)
    self.assertIn("previewAlt:", case)
    self.assertIn("/media/mundus/other-side-detail.webp", story)
    self.assertNotIn("/media/mundus/modes-overview.webp", story)
```

- [ ] **Step 3: Update the expected source SHA and fact IDs**

Change the revision assertions to:

```python
EXPECTED_MUNDUS = "378fe528ca1c8f83f0280f83383b5e785e851285"

self.assertEqual(facts.EXPECTED_REVISIONS["Mundus"], EXPECTED_MUNDUS)
self.assertEqual(
    [rule["id"] for rule in rules],
    [
        "mundus-maintained-globe",
        "mundus-current-lenses",
        "mundus-parchment-atlas",
        "mundus-interaction-and-sharing",
        "mundus-maintainable-delivery",
    ],
)
```

Update `tests/test_workflow.py`:

```python
self.assertIn(
    "ref: 378fe528ca1c8f83f0280f83383b5e785e851285",
    self.workflow,
)
```

- [ ] **Step 4: Run the focused tests and confirm RED**

Run:

```bash
python3 -m unittest \
  tests.test_release_verification.TestProductCaseStudyFocus \
  tests.test_release_verification.TestStructuredFacts.test_mundus_uses_live_v11_deployed_revision \
  tests.test_workflow.TestPullRequestWorkflow.test_pull_requests_run_the_complete_non_deploying_gate \
  -v
```

Expected: failures for old headings, missing three-role media, old fact IDs,
old SHA, and old workflow ref.

- [ ] **Step 5: Commit the RED contract**

```bash
git add tests/test_release_verification.py tests/test_workflow.py
git commit -m "test(portfolio): define refined Mundus case contract"
```

### Task 2: Separate homepage and detail media semantics

**Files:**
- Modify: `src/content.config.ts`
- Modify: `src/components/ProjectMedia.astro`
- Modify: `src/content/projects/mundus.mdx`
- Test: `tests/test_release_verification.py`

- [ ] **Step 1: Extend the media schema**

Add `previewAlt` beside `preview`:

```typescript
media: z.object({
  type: z.enum(['video', 'image', 'placeholder']),
  src: z.string().optional(),
  preview: z.string().optional(),
  previewAlt: localized.optional(),
  poster: z.string().optional(),
  walkthrough: z
    .object({ src: z.string(), poster: z.string().optional() })
    .optional(),
  alt: localized,
}),
```

- [ ] **Step 2: Select alt text with the selected image**

In `ProjectMedia.astro`, derive:

```typescript
const imageSource = compact && media.preview ? media.preview : media.src;
const imageAlt =
  compact && media.preview && media.previewAlt ? media.previewAlt : media.alt;
```

Use it on the image:

```astro
<img
  src={asset(imageSource)}
  alt={imageAlt.en}
  data-alt-en={imageAlt.en}
  data-alt-zh={imageAlt.zh}
  loading={compact ? 'lazy' : 'eager'}
/>
```

- [ ] **Step 3: Set the three Mundus media roles**

Update the Mundus frontmatter:

```yaml
media:
  type: image
  src: /media/mundus/other-side-full.webp
  preview: /media/mundus/globe-preview.webp
  previewAlt:
    en: A close crop of the parchment-styled Mundus globe.
    zh: Mundus 羊皮卷质感数字地球的局部画面。
  alt:
    en: The complete Mundus Other Side interface with the globe, controls, and location results.
    zh: Mundus“地球另一端”的完整界面，包含地球、操作控件与地点结果。
```

- [ ] **Step 4: Run the media-role test**

Run:

```bash
python3 -m unittest \
  tests.test_release_verification.TestProductCaseStudyFocus.test_mundus_media_has_three_distinct_roles \
  -v
```

Expected: the metadata assertions pass; the test still fails only because the
Story component has not switched to `other-side-detail.webp`.

- [ ] **Step 5: Commit the metadata change**

```bash
git add src/content.config.ts src/components/ProjectMedia.astro \
  src/content/projects/mundus.mdx
git commit -m "feat(portfolio): separate Mundus media roles"
```

### Task 3: Rewrite the bilingual case and Story

**Files:**
- Modify: `src/content/projects/mundus.mdx`
- Modify: `src/components/MundusStory.astro`
- Test: `tests/test_release_verification.py`

- [ ] **Step 1: Replace the English case copy**

Keep the frontmatter and replace the English narrative with:

```mdx
<section lang="en" data-locale-content="en">

## A globe I can keep extending

Maps, statistical tables, astronomy tools, and data portals each hold a different part of how we understand Earth. Mundus brings those materials into one geographic workspace. I maintain it as a long-running personal globe whose data, methods, and interactions can grow together.

## One place, several ways to read it

A visit begins with a place. The visitor rotates or searches the globe, chooses an observation lens, reads the result with its source and method, and shares the current view. Changing lenses keeps the same geographic context, so the next question starts from somewhere already familiar.

## Three lenses in use today

- **Other Side** follows a point through Earth to its antipode and connects both endpoints with represented major cities from the bundled GeoNames snapshot.
- **Development, Unpacked** places reported HDI beside health, education, and income dimensions, with year, history, source, and missing states.
- **Sunline** turns UTC time into solar position, daylight, twilight, and approximate sunrise and sunset on the shared globe.

</section>
```

- [ ] **Step 2: Replace the Chinese case copy**

Use:

```mdx
<section lang="zh-CN" data-locale-content="zh">

## 一颗持续生长的个人数字地球

地图、统计表、天文工具和数据门户保存着理解地球的不同线索。Mundus 把这些材料放进同一个地理空间。我长期维护这颗个人数字地球，让数据、方法与交互能够沿着同一套产品结构继续生长。

## 同一地点，几种观察方式

一次使用从地点开始。访客旋转地球或搜索城市，选择观察视角，阅读结果及其来源与方法，再分享当前画面。切换视角时，地理上下文会保留下来，下一个问题可以从熟悉的位置继续。

## 目前使用的三个视角

- **地球另一端**沿地心找到对跖点，并用 GeoNames 固定快照中的收录主要城市呈现两端关系。
- **发展的不同侧面**把已发布 HDI 与健康、教育、收入维度放在一起，同时给出年份、历史变化、来源与缺失状态。
- **日照线**把 UTC 时间转换为共享地球上的太阳位置、白昼、曙暮光与近似日出日落。

</section>
```

- [ ] **Step 3: Replace the release and maintenance sections**

English:

```mdx
<section lang="en" data-locale-content="en">

## The current release

Parchment Atlas gives the globe a warmer exhibition surface built from Natural Earth vector geometry. Other Side combines bilingual GeoNames search, endpoint city relationships, and a draggable through-Earth section. The latest update supports closer inspection, preserves the globe's color while that section moves, and gives Sunline a consistent Twilight label and definition.

Sharing creates a URL that restores the selected location and observation mode. The dialog explains that the exact selected location is included before the visitor copies the link; Sunline links also retain the displayed UTC time.

## Built for continued maintenance

One globe kernel carries place, camera behavior, controls, and sharing across every lens. Reviewed data snapshots and hashes keep published results stable. Larger assets load when their lens needs them, while the base experience stays light.

The product ships as a static client with bilingual copy, keyboard access, visible focus, reduced motion, and a WebGL fallback. Pages subpath checks and artifact verification make each public build reproducible.

</section>
```

Chinese:

```mdx
<section lang="zh-CN" data-locale-content="zh">

## 当前公开版本

Parchment Atlas 用 Natural Earth 矢量几何构成更温暖的展览式地球。“地球另一端”整合了 GeoNames 中英文城市搜索、两端城市关系与可拖拽的穿地剖面。最新更新支持更近距离的观察，拖动剖面时地球颜色保持稳定，日照线也统一使用“曙暮光”名称与定义。

分享链接会恢复所选地点与观察视角。复制之前，弹窗会明确说明链接包含精确地点；日照线链接还会保留画面中的 UTC 时间。

## 为长期维护做出的选择

单一地球内核承载所有视角的地点、相机行为、控件与分享方式。经过审核的数据快照和哈希让公开结果保持稳定，较大的资源只在对应视角使用时加载。

产品以静态客户端交付，并提供中英文、键盘操作、可见焦点、reduced motion 与 WebGL fallback。Pages 子路径检查和制品验证让每次公开构建都可以复现。

</section>
```

- [ ] **Step 4: Rewrite `MundusStory.astro`**

Use this visible copy:

```astro
<p class="eyebrow">
  <Localized en="Parchment Atlas · Current product" zh="Parchment Atlas · 当前产品" />
</p>
<h2 id="mundus-story-title">
  <Localized en="One place stays in view." zh="地点始终留在视野中。" />
</h2>
<p>
  <Localized
    en="The current release supports closer globe inspection, a stable through-Earth section, clear Twilight language, and exact-location sharing with an explicit privacy notice."
    zh="当前版本支持更近距离观察地球、稳定拖动穿地剖面、清晰呈现曙暮光，并在分享精确地点前给出隐私提示。"
  />
</p>
```

Change the image to:

```astro
<img
  src={asset('/media/mundus/other-side-detail.webp')}
  alt="A close view of the Other Side cross-section and its endpoint city relationship."
  data-alt-en="A close view of the Other Side cross-section and its endpoint city relationship."
  data-alt-zh="“地球另一端”穿地剖面及两端城市关系的细节画面。"
  loading="lazy"
/>
```

Change the maintenance block to:

```astro
<p class="eyebrow"><Localized en="How it grows" zh="如何继续生长" /></p>
<h3><Localized en="Each lens joins the same globe." zh="每个视角都接入同一颗地球。" /></h3>
<p>
  <Localized
    en="A lens starts with a specific question, pins its data and method, reuses the existing place and controls, and passes the public-build gate."
    zh="每个视角从具体问题出发，固定数据与方法，复用既有地点与控件，并通过公开构建门禁。"
  />
</p>
```

Use these list labels:

```astro
<li><Localized en="Start with one question" zh="从一个问题出发" /></li>
<li><Localized en="Pin data and method" zh="固定数据与方法" /></li>
<li><Localized en="Keep place and controls" zh="保留地点与控件" /></li>
<li><Localized en="Verify the public build" zh="验证公开构建" /></li>
```

Replace the forced ratio:

```css
.overview-visual img {
  display: block;
  width: 100%;
  height: auto;
  object-fit: contain;
  border: 1px solid var(--line);
  background: #090b0a;
}
```

Delete `.overview-visual img { aspect-ratio: 4 / 3; }`.

- [ ] **Step 5: Run focused content tests**

Run:

```bash
python3 -m unittest \
  tests.test_release_verification.TestProductCaseStudyFocus.test_mundus_case_uses_direct_editorial_voice \
  tests.test_release_verification.TestProductCaseStudyFocus.test_mundus_media_has_three_distinct_roles \
  -v
```

Expected: PASS.

- [ ] **Step 6: Commit the narrative**

```bash
git add src/content/projects/mundus.mdx src/components/MundusStory.astro \
  tests/test_release_verification.py
git commit -m "docs(portfolio): rewrite the Mundus product case"
```

### Task 4: Capture and validate the three public product images

**Files:**
- Create: `scripts/capture-mundus-media.mjs`
- Create: `docs/verification/evidence/mundus-media.json`
- Create: `public/media/mundus/globe-preview.webp`
- Create: `public/media/mundus/other-side-full.webp`
- Create: `public/media/mundus/other-side-detail.webp`
- Modify: `tests/test_release_verification.py`
- Delete after references move: `public/media/mundus/other-side.webp`
- Delete after references move: `public/media/mundus/modes-overview.webp`

- [ ] **Step 1: Add a failing manifest and image test**

Add:

```python
def test_mundus_source_media_is_bound_to_current_public_deployment(self) -> None:
    manifest = json.loads(
        Path("docs/verification/evidence/mundus-media.json").read_text(
            encoding="utf-8"
        )
    )
    self.assertEqual(
        manifest["sourceRevision"],
        "378fe528ca1c8f83f0280f83383b5e785e851285",
    )
    self.assertEqual(
        [item["role"] for item in manifest["images"]],
        ["homepage-globe", "project-full-interface", "story-other-side-detail"],
    )
    self.assertEqual(manifest["panelOverflowCount"], 0)
    self.assertGreaterEqual(manifest["images"][1]["width"], 1920)
    self.assertEqual(
        len({item["sha256"] for item in manifest["images"]}),
        3,
    )
    for item in manifest["images"]:
        path = Path("public/media/mundus") / item["path"]
        self.assertTrue(path.is_file())
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            item["sha256"],
        )
        self.assertEqual(
            browser.webp_dimensions(path),
            (item["width"], item["height"]),
        )
```

Run it and expect `FileNotFoundError` for `mundus-media.json`:

```bash
python3 -m unittest \
  tests.test_release_verification.TestProductCaseStudyFocus.test_mundus_source_media_is_bound_to_current_public_deployment \
  -v
```

- [ ] **Step 2: Create the capture script**

Create `scripts/capture-mundus-media.mjs`:

```javascript
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const revision = '378fe528ca1c8f83f0280f83383b5e785e851285';
const liveUrl = 'https://0mn1si2i5.github.io/Mundus/';
const viewport = { width: 2160, height: 1350 };
const mundusRoot = process.env.MUNDUS_ROOT;
assert(mundusRoot, 'MUNDUS_ROOT is required');

const portfolioRequire = createRequire(import.meta.url);
const ffmpeg = portfolioRequire('ffmpeg-static');
assert(ffmpeg, 'ffmpeg-static executable is unavailable');
const mundusRequire = createRequire(
  pathToFileURL(path.join(mundusRoot, 'package.json')),
);
const { chromium } = mundusRequire('@playwright/test');

const portfolioRoot = path.resolve(import.meta.dirname, '..');
const mediaRoot = path.join(portfolioRoot, 'public/media/mundus');
const evidencePath = path.join(
  portfolioRoot,
  'docs/verification/evidence/mundus-media.json',
);
const captures = [
  {
    role: 'homepage-globe',
    png: '/tmp/mundus-globe-preview.png',
    target: 'globe-preview.webp',
  },
  {
    role: 'project-full-interface',
    png: '/tmp/mundus-other-side-full.png',
    target: 'other-side-full.webp',
  },
  {
    role: 'story-other-side-detail',
    png: '/tmp/mundus-other-side-detail.png',
    target: 'other-side-detail.webp',
  },
];

function webpDimensions(data) {
  const marker = data.indexOf(Buffer.from('VP8X'));
  if (marker >= 0) {
    return {
      width: 1 + data.readUIntLE(marker + 12, 3),
      height: 1 + data.readUIntLE(marker + 15, 3),
    };
  }
  const frame = data.indexOf(Buffer.from([0x9d, 0x01, 0x2a]));
  assert(frame >= 0, 'unsupported WebP header');
  return {
    width: data.readUInt16LE(frame + 3) & 0x3fff,
    height: data.readUInt16LE(frame + 5) & 0x3fff,
  };
}

await fs.mkdir(mediaRoot, { recursive: true });
const consoleErrors = [];
const pageErrors = [];
const requestFailures = [];
const browser = await chromium.launch({ headless: true });

try {
  const context = await browser.newContext({
    viewport,
    deviceScaleFactor: 1,
    colorScheme: 'light',
    reducedMotion: 'reduce',
    locale: 'en-US',
  });
  await context.addInitScript(() => {
    localStorage.setItem('locale', 'en');
  });
  const page = await context.newPage();
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('requestfailed', (request) =>
    requestFailures.push({
      url: request.url(),
      reason: request.failure()?.errorText ?? 'unknown',
    }),
  );

  const response = await page.goto(liveUrl, { waitUntil: 'networkidle' });
  assert(response?.ok(), `Mundus returned ${response?.status()}`);
  await page.waitForFunction(() =>
    [...document.images].every((image) => image.complete),
  );
  await page.waitForTimeout(1_000);

  const pageOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > innerWidth,
  );
  assert.equal(pageOverflow, false, 'public page has horizontal overflow');

  const globe = page.getByRole('region', {
    name: 'Interactive three-dimensional globe',
  });
  const result = page.getByRole('complementary', {
    name: 'Location result',
  });
  await globe.waitFor();
  await result.waitFor();

  const panelOverflows = await result.locator('*').evaluateAll((elements) =>
    elements
      .filter((element) => {
        if (!(element instanceof HTMLElement) || element.offsetParent === null) {
          return false;
        }
        return (
          element.scrollWidth > element.clientWidth + 1 ||
          element.scrollHeight > element.clientHeight + 1
        );
      })
      .map((element) => ({
        tag: element.tagName,
        text: element.innerText.slice(0, 120),
        clientWidth: element.clientWidth,
        scrollWidth: element.scrollWidth,
        clientHeight: element.clientHeight,
        scrollHeight: element.scrollHeight,
      })),
  );
  assert.deepEqual(panelOverflows, [], 'result-panel text is clipped');

  await globe.screenshot({
    path: captures[0].png,
    animations: 'disabled',
  });
  await page.screenshot({
    path: captures[1].png,
    fullPage: false,
    animations: 'disabled',
  });

  const globeBox = await globe.boundingBox();
  const resultBox = await result.boundingBox();
  assert(globeBox && resultBox, 'capture regions are unavailable');
  const dragY = globeBox.y + globeBox.height * 0.5;
  await page.mouse.move(globeBox.x + globeBox.width * 0.62, dragY);
  await page.mouse.down();
  await page.mouse.move(globeBox.x + globeBox.width * 0.38, dragY, {
    steps: 16,
  });
  await page.mouse.up();
  await page.waitForTimeout(250);

  const detailLeft = Math.max(0, globeBox.x + globeBox.width * 0.2);
  const detailTop = Math.max(0, Math.min(globeBox.y, resultBox.y));
  const detailRight = Math.min(
    viewport.width,
    Math.max(globeBox.x + globeBox.width, resultBox.x + resultBox.width),
  );
  const detailBottom = Math.min(
    viewport.height,
    Math.max(
      globeBox.y + globeBox.height,
      resultBox.y + resultBox.height,
    ),
  );
  await page.screenshot({
    path: captures[2].png,
    animations: 'disabled',
    clip: {
      x: Math.floor(detailLeft),
      y: Math.floor(detailTop),
      width: Math.floor(detailRight - detailLeft),
      height: Math.floor(detailBottom - detailTop),
    },
  });

  const images = [];
  for (const capture of captures) {
    const target = path.join(mediaRoot, capture.target);
    execFileSync(ffmpeg, [
      '-loglevel',
      'error',
      '-y',
      '-i',
      capture.png,
      '-c:v',
      'libwebp',
      '-q:v',
      '86',
      target,
    ]);
    const data = await fs.readFile(target);
    images.push({
      role: capture.role,
      path: capture.target,
      ...webpDimensions(data),
      sha256: crypto.createHash('sha256').update(data).digest('hex'),
    });
  }

  assert(images[1].width >= 1920, 'hero capture is too narrow');
  assert.equal(new Set(images.map((image) => image.sha256)).size, 3);
  assert.deepEqual(consoleErrors, []);
  assert.deepEqual(pageErrors, []);
  assert.deepEqual(requestFailures, []);

  const manifest = {
    schemaVersion: 1,
    sourceUrl: liveUrl,
    sourceRevision: revision,
    capturedViewport: viewport,
    panelOverflowCount: panelOverflows.length,
    consoleErrorCount: consoleErrors.length,
    failedRequestCount: requestFailures.length,
    images,
  };
  await fs.writeFile(evidencePath, `${JSON.stringify(manifest, null, 2)}\n`);
} finally {
  await browser.close();
}
```

- [ ] **Step 3: Prepare the exact Mundus checkout and capture**

Run:

```bash
git -C "/Users/bytedance/Desktop/Zen/Mundus" fetch origin main
test "$(git -C "/Users/bytedance/Desktop/Zen/Mundus" rev-parse origin/main)" = \
  "378fe528ca1c8f83f0280f83383b5e785e851285"
test "$(gh api 'repos/0mn1si2i5/Mundus/deployments?environment=github-pages&per_page=1' \
  --jq '.[0].sha')" = \
  "378fe528ca1c8f83f0280f83383b5e785e851285"
pnpm --dir "/Users/bytedance/Desktop/Zen/Mundus" install --frozen-lockfile
MUNDUS_ROOT="/Users/bytedance/Desktop/Zen/Mundus" \
  node scripts/capture-mundus-media.mjs
```

Expected: three WebP files, manifest values populated, and the script exits 0.

- [ ] **Step 4: Remove superseded media**

After `rg` confirms no runtime content references:

```bash
rg -n "other-side\\.webp|modes-overview\\.webp" src
git rm public/media/mundus/other-side.webp \
  public/media/mundus/modes-overview.webp
```

Expected: `rg` has no visitor-facing source references before `git rm`.

- [ ] **Step 5: Run the media tests**

```bash
python3 -m unittest \
  tests.test_release_verification.TestProductCaseStudyFocus.test_mundus_source_media_is_bound_to_current_public_deployment \
  tests.test_release_verification.TestProductCaseStudyFocus.test_mundus_media_has_three_distinct_roles \
  -v
```

Expected: PASS.

- [ ] **Step 6: Commit media and capture evidence**

```bash
git add scripts/capture-mundus-media.mjs \
  public/media/mundus \
  docs/verification/evidence/mundus-media.json \
  tests/test_release_verification.py
git commit -m "assets(portfolio): recapture current Mundus views"
```

### Task 5: Rebind immutable facts and CI to the latest public commit

**Files:**
- Modify: `scripts/verification/facts.py`
- Modify: `scripts/verification/facts.json`
- Modify: `.github/workflows/deploy.yml`
- Modify: `docs/verification/evidence/source-revisions.json`
- Modify: `docs/verification/evidence/task7-fact-assertions.json`
- Modify: `tests/test_release_verification.py`
- Modify: `tests/test_workflow.py`

- [ ] **Step 1: Change every immutable revision pin**

Use:

```text
378fe528ca1c8f83f0280f83383b5e785e851285
```

Update:

```python
EXPECTED_REVISIONS = {
    "Mundus": "378fe528ca1c8f83f0280f83383b5e785e851285",
}
```

and:

```yaml
repository: 0mn1si2i5/Mundus
ref: 378fe528ca1c8f83f0280f83383b5e785e851285
path: sources/Mundus
```

- [ ] **Step 2: Replace the five fact assertions**

Replace `scripts/verification/facts.json` with:

```json
{
  "schemaVersion": 2,
  "assertions": [
    {
      "id": "mundus-maintained-globe",
      "description": "Mundus is maintained as one personal globe with a shared geographic context.",
      "claims": [
        {"locale": "en", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["Mundus brings those materials into one geographic workspace", "long-running personal globe"]}]},
        {"locale": "zh", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["Mundus 把这些材料放进同一个地理空间", "长期维护这颗个人数字地球"]}]},
        {"locale": "story", "source": "src/components/MundusStory.astro", "rules": [{"type": "contains_all", "values": ["One place stays in view", "地点始终留在视野中"]}]}
      ],
      "evidence": {
        "repository": "Mundus",
        "source": "README.md",
        "rules": [{"type": "contains_all", "values": ["long-lived personal digital globe", "The current public product begins with three modes"]}]
      }
    },
    {
      "id": "mundus-current-lenses",
      "description": "The public product currently provides Other Side, Development, and Sunline.",
      "claims": [
        {"locale": "en", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["Three lenses in use today", "Other Side", "Development, Unpacked", "Sunline"]}]},
        {"locale": "zh", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["目前使用的三个视角", "地球另一端", "发展的不同侧面", "日照线"]}]},
        {"locale": "story", "source": "src/components/MundusStory.astro", "rules": [{"type": "contains_all", "values": ["Other Side", "Development, Unpacked", "Sunline"]}]}
      ],
      "evidence": {
        "repository": "Mundus",
        "source": "README.md",
        "rules": [{"type": "contains_all", "values": ["Other Side", "Development, Unpacked", "Sunline"]}]
      }
    },
    {
      "id": "mundus-parchment-atlas",
      "description": "Parchment Atlas ships vector geography, bilingual city search, and the Other Side section.",
      "claims": [
        {"locale": "en", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["Parchment Atlas", "Natural Earth vector geometry", "GeoNames search", "draggable through-Earth section"]}]},
        {"locale": "zh", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["Parchment Atlas", "Natural Earth 矢量几何", "GeoNames 中英文城市搜索", "可拖拽的穿地剖面"]}]},
        {"locale": "story", "source": "src/components/MundusStory.astro", "rules": [{"type": "contains_all", "values": ["Parchment Atlas · Current product", "Parchment Atlas · 当前产品", "through-Earth section", "穿地剖面"]}]}
      ],
      "evidence": {
        "repository": "Mundus",
        "source": "README.md",
        "rules": [{"type": "contains_all", "values": ["Parchment Atlas", "draggable Other Side cross-section", "bilingual city search", "Natural Earth vector"]}]
      }
    },
    {
      "id": "mundus-interaction-and-sharing",
      "description": "The current deployment supports closer inspection, clear twilight language, and restorable sharing.",
      "claims": [
        {"locale": "en", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["supports closer inspection", "preserves the globe's color", "consistent Twilight label", "exact selected location"]}]},
        {"locale": "zh", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["支持更近距离的观察", "地球颜色保持稳定", "统一使用“曙暮光”", "链接包含精确地点"]}]},
        {"locale": "story", "source": "src/components/MundusStory.astro", "rules": [{"type": "contains_all", "values": ["closer globe inspection", "clear Twilight language", "exact-location sharing", "更近距离观察地球", "分享精确地点"]}]}
      ],
      "evidence": {
        "repository": "Mundus",
        "source": "tests/e2e/app.spec.ts",
        "rules": [{"type": "contains_all", "values": ["data-camera-distance', '1.55'", "labels and defines civil twilight consistently in both languages", "copiedShareUrl"]}]
      }
    },
    {
      "id": "mundus-maintainable-delivery",
      "description": "Pinned data, static delivery, accessibility, and artifact verification support continued maintenance.",
      "claims": [
        {"locale": "en", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["Reviewed data snapshots and hashes", "static client", "Pages subpath checks and artifact verification"]}]},
        {"locale": "zh", "source": "src/content/projects/mundus.mdx", "rules": [{"type": "contains_all", "values": ["经过审核的数据快照和哈希", "静态客户端", "Pages 子路径检查和制品验证"]}]},
        {"locale": "story", "source": "src/components/MundusStory.astro", "rules": [{"type": "contains_all", "values": ["Pin data and method", "Verify the public build", "固定数据与方法", "验证公开构建"]}]}
      ],
      "evidence": {
        "repository": "Mundus",
        "source": "docs/2026-08-01-v1.1-publication-packet.md",
        "rules": [{"type": "contains_all", "values": ["static, one-Canvas architecture", "SHA-256", "accessible fallbacks", "pages-artifact"]}]
      }
    }
  ]
}
```

The exact deployed revision contains all three phrases in
`tests/e2e/app.spec.ts`; do not switch to working-tree evidence or weaken the
rule.

- [ ] **Step 3: Update retained fact evidence**

Set `source-revisions.json` to the new SHA and replace
`task7-fact-assertions.json` IDs/sources in the same order as `facts.json`.
Keep:

```json
{
  "schemaVersion": 4,
  "total": 5,
  "passed": 5,
  "privateBoundaryHitCount": 0
}
```

- [ ] **Step 4: Run immutable verification tests**

```bash
python3 -m unittest \
  tests.test_release_verification.TestStructuredFacts \
  tests.test_workflow.TestPullRequestWorkflow \
  -v
```

Expected: PASS.

Run fact verification against the exact local repository:

```bash
python3 - <<'PY'
from pathlib import Path
from scripts.verification import facts

errors = facts.verify(
    Path("."),
    {"Mundus": Path("/Users/bytedance/Desktop/Zen/Mundus")},
    Path("scripts/verification/facts.json"),
)
print(errors)
raise SystemExit(bool(errors))
PY
```

Expected: `[]`.

- [ ] **Step 5: Commit the revision migration**

```bash
git add .github/workflows/deploy.yml \
  scripts/verification/facts.py scripts/verification/facts.json \
  docs/verification/evidence/source-revisions.json \
  docs/verification/evidence/task7-fact-assertions.json \
  tests/test_release_verification.py tests/test_workflow.py
git commit -m "fix(verification): bind Mundus case to current deployment"
```

### Task 6: Rebuild and regenerate browser evidence

**Files:**
- Modify: `docs/verification/evidence/browser-build.json`
- Modify: `docs/verification/evidence/browser-matrix.json`
- Modify: `docs/verification/evidence/browser-network.json`
- Modify: `docs/verification/evidence/browser-console.json`
- Modify: `docs/verification/evidence/browser-reduced-motion.json`
- Modify: `docs/verification/evidence/browser-screenshots.json`
- Modify: `docs/verification/assets/task7-home-*.webp`
- Modify: `docs/verification/assets/task7-mundus-*.webp`
- Modify: `docs/verification/task7-release-verification.md`

- [ ] **Step 1: Install and build the exact tree**

```bash
npm ci
npm audit --audit-level=high
npm test
npm run build
```

Expected: 0 vulnerabilities, all tests pass, and six pages build.

- [ ] **Step 2: Start the Pages-base preview**

```bash
npm run preview -- --host 127.0.0.1 --port 4321
```

Expected URL:

```text
http://127.0.0.1:4321/jiaming-li-portfolio/
```

- [ ] **Step 3: Reobserve all eight scenarios**

Use isolated system-Chrome `agent-browser` sessions:

```text
home-en-light-1440      /                 en light 1440×900  motion
home-en-light-1024      /                 en light 1024×768  motion
home-zh-dark-768        /                 zh dark  768×1024  reduced
home-zh-dark-390        /                 zh dark  390×844   reduced
mundus-en-light-1440    /projects/mundus  en light 1440×900  motion
mundus-zh-dark-desktop  /projects/mundus  zh dark  1440×900  reduced
mundus-en-light-390     /projects/mundus  en light 390×844   motion
mundus-zh-dark-mobile   /projects/mundus  zh dark  390×844   reduced
```

For every session:

```bash
agent-browser --session "$SESSION" open "$URL"
agent-browser --session "$SESSION" set viewport "$WIDTH" "$HEIGHT"
agent-browser --session "$SESSION" set media "$THEME" "$MOTION"
agent-browser --session "$SESSION" open "$URL"
agent-browser --session "$SESSION" wait --load networkidle
agent-browser --session "$SESSION" press Tab
agent-browser --session "$SESSION" eval --stdin <<'EVALEOF'
JSON.stringify({
  overflow: document.documentElement.scrollWidth > innerWidth,
  brokenImageCount: [...document.images].filter(
    image => image.complete && image.naturalWidth === 0
  ).length,
  decodedImageCount: [...document.images].filter(
    image => image.complete && image.naturalWidth > 0
  ).length,
  totalImageCount: document.images.length,
  focusableCount: document.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
  ).length,
  focusVisible: document.activeElement.matches(':focus-visible'),
  visibleTextLength: document.body.innerText.trim().length,
  activeAnimationCount: document.getAnimations().filter(
    animation => animation.playState === 'running'
  ).length,
  selected: [...document.querySelectorAll('.project-card h3')].map(
    heading => heading.innerText.trim()
  ),
  other: [...document.querySelectorAll('.other-card h3')].map(
    heading => heading.innerText.trim()
  ),
  productVisualCount: document.querySelectorAll('.overview-visual img').length
})
EVALEOF
agent-browser --session "$SESSION" console --json
agent-browser --session "$SESSION" network requests --json
```

For Chinese sessions, set `locale=zh` and `theme=dark` in local storage before
the second `open`. Record only observed values. Required outcomes:

```text
homepage images: 4
Mundus detail images: 2
Mundus Story images: 1
Selected Work: DialogTree, Mundus, NBTI
Other Work: Side B, RSZ Namelist
overflow: false
broken images: 0
focus visible: true
reduced-motion active animations: 0
console messages: 0
failed requests: 0
```

- [ ] **Step 4: Capture and bind screenshots**

Capture full-page PNGs with the existing eight scenario filenames, convert to
WebP quality 80 using `ffmpeg-static`, then update actual dimensions and
SHA-256 values in `browser-screenshots.json`.

Regenerate `browser-build.json` from:

```text
dist/index.html
dist/about/index.html
dist/projects/dialogtree/index.html
dist/projects/mundus/index.html
dist/projects/nbti/index.html
dist/projects/side-b/index.html
```

Use SHA-256 over exact file bytes.

- [ ] **Step 5: Update the verification narrative**

In `docs/verification/task7-release-verification.md`, record:

```text
Mundus revision: 378fe528ca1c8f83f0280f83383b5e785e851285
source images: globe-only homepage preview, complete Other Side hero,
               focused Other Side Story detail
visitor copy: current public behavior only
browser scenarios: 8
Mundus detail image count: 2
OmniPet route: absent
```

Remove references to the superseded SHA and old two-source-image arrangement.

- [ ] **Step 6: Run the release verifier**

```bash
npm run verify -- --mundus-root "/Users/bytedance/Desktop/Zen/Mundus"
git diff --check
```

Expected:

```text
release verification: facts=5/5 browser=pass privacy=pass
```

- [ ] **Step 7: Commit final browser evidence**

```bash
git add docs/verification/evidence/browser-*.json \
  docs/verification/assets/task7-*.webp \
  docs/verification/task7-release-verification.md
git commit -m "test(portfolio): refresh refined Mundus browser evidence"
```

### Task 7: Final validation and Draft PR update

**Files:**
- Modify only if final evidence finds a scoped defect.

- [ ] **Step 1: Recheck concurrent state**

```bash
git fetch origin feat/mundus-omnipet-portfolio
git rev-parse origin/feat/mundus-omnipet-portfolio
git merge-base --is-ancestor \
  f777b4fc91540a4693062cd41a68cfc188c16c1a \
  HEAD
```

Expected: remote remains `f777b4f...` until this implementation pushes, and
the ancestry check exits 0. Stop if another writer advanced the PR.

- [ ] **Step 2: Run the complete local gate**

```bash
npm ci
npm audit --audit-level=high
npm test
npm run build
npm run verify -- --mundus-root "/Users/bytedance/Desktop/Zen/Mundus"
git diff --check
git status --short
```

Expected: 0 vulnerabilities, all tests pass, six pages build, facts 5/5,
browser/privacy pass, diff check passes, and the tree is clean.

- [ ] **Step 3: Review the final diff**

```bash
git diff --stat f777b4fc91540a4693062cd41a68cfc188c16c1a..HEAD
git diff --name-status f777b4fc91540a4693062cd41a68cfc188c16c1a..HEAD
rg -n "GHSL|STOP_GLOBAL_MORPHOLOGY|not a final|not a plugin|而不是|不是插件" \
  src/content/projects/mundus.mdx src/components/MundusStory.astro
rg -n -i "omnipet|omnipets" \
  .github src scripts/verification docs/verification/evidence/source-revisions.json
```

Expected: the visitor-copy scan returns no matches; no OmniPet route, claim,
source checkout, verifier argument, or workflow input is present.

- [ ] **Step 4: Push normally to the existing Draft PR branch**

```bash
git push origin HEAD:refs/heads/feat/mundus-omnipet-portfolio
git rev-parse HEAD
git ls-remote origin refs/heads/feat/mundus-omnipet-portfolio
```

Expected: local and remote SHAs match. Do not use `--force`.

- [ ] **Step 5: Update and verify Draft PR #1**

Update the PR body with:

```text
- exact Mundus source revision 378fe528...
- three source-image roles and two-image detail-page budget
- rewritten bilingual case boundary
- local audit/test/build/verify results
- eight-scenario browser results
- explicit Draft/no-deploy boundary
```

Then run:

```bash
gh pr view 1 --repo 0mn1si2i5/jiaming-li-portfolio \
  --json url,isDraft,headRefOid,mergeStateStatus,mergeable,statusCheckRollup
gh run list --repo 0mn1si2i5/jiaming-li-portfolio \
  --branch feat/mundus-omnipet-portfolio --limit 3 \
  --json databaseId,headSha,status,conclusion,url
```

Wait for the exact-head run. Required outcome:

```text
build: success
deploy: skipped
PR: Draft, CLEAN, MERGEABLE
```

- [ ] **Step 6: Record the closeout**

Report:

```text
Draft PR URL
final Portfolio SHA
Mundus source/deployment SHA
commit list
diff summary
audit result
test count
build page count
facts count
browser scenario/request/console/failure results
remote run URL
confirmation that Portfolio main and Pages did not change
confirmation that unpublished Mundus work and OmniPet remain absent
```
