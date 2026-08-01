# Site Navigation and Link System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge About and the empty Notes destination at `/about`, simplify internal project entry points, and make external-link styling consistent without changing project narratives.

**Architecture:** `BaseLayout.astro` remains the owner of global navigation, footer, locale/theme behavior, and shared link tokens. `index.astro` remains the owner of homepage project cards, while a focused `about.astro` owns the migrated About copy and empty Notes section. Source-level contract tests protect the static structure, and the existing release verifier remains the owner of generated-route and retained-browser evidence.

**Tech Stack:** Astro 7, TypeScript/Astro components, Python `unittest`, static HTML build, GitHub Pages release verification.

**Baseline/Authority Refs:** `docs/superpowers/specs/2026-08-02-site-navigation-and-links-design.md`; PR #1 head `b201772585b2d7f636231ed8e0ec05d02d701d22` before the design commit; public `main` and Pages at `67918550d5a4a0a2aac218c12cffc4a476327f97`; Mundus facts remain owned by the parallel Mundus thread.

**Compatibility Boundary:** Keep project order, all project routes, bilingual locale switching, themes, reduced motion, `BASE_URL`, Mundus facts/media/copy, the OmniPet preservation branch, Draft PR state, and public Pages unchanged. Remove `/notes` without a redirect because it is absent from public `main`.

**Verification:** Each production slice follows RED/GREEN with focused `unittest` cases. Completion requires the full unit suite, six-page Astro build with `/about` replacing `/notes`, regenerated build-bound browser evidence, facts 5/5, privacy pass, zero audit vulnerabilities, `git diff --check`, multi-viewport browser QA, a clean committed tree, and successful remote PR checks with deploy skipped.

---

## Plan Basis

### Facts

- The feature worktree and remote PR branch matched at `b201772` before the
  approved design document was committed locally as `d03ac7e`.
- The current build generates six pages, including `/notes`.
- `BaseLayout.astro` owns the top-left site-name link, primary navigation,
  footer GitHub link, and Back to top control.
- `index.astro` applies project accent colors to internal CTAs and applies blue
  to every link inside Other Work, including the Side B title.
- `scripts/verification/browser.py` treats the generated route list and
  retained screenshots as release-bound evidence.

### Assumptions

- The empty Notes area means a visible bilingual section heading with no post
  card, date, teaser, or placeholder message.
- The About GitHub link remains useful because the redundant footer copy is
  removed.
- Existing project-specific accent colors remain available for project media
  and detail-page identity; they no longer color homepage internal CTAs because
  those CTAs are removed.

### Unknowns to Recheck at Execution

- Whether the parallel Mundus thread advances PR #1 before either implementation
  or push.
- Whether its changes touch `BaseLayout.astro`, `index.astro`,
  `projects/[...slug].astro`, browser evidence, or tests.

## File Map

- Create `src/pages/about.astro`: dedicated bilingual About content and empty
  Notes section.
- Delete `src/pages/notes.astro`: retire the unshipped Notes article and route.
- Modify `src/components/BaseLayout.astro`: Home label, primary navigation,
  footer cleanup, and shared external-link color token.
- Modify `src/pages/index.astro`: remove About content and repeated internal
  CTAs; scope project-title and external-link styles correctly.
- Modify `src/pages/projects/[...slug].astro`: apply the external-link visual
  contract to project prose and Explore pills.
- Create `tests/test_site_interface.py`: source-level information-architecture
  and link-semantic regression tests.
- Modify `scripts/verification/browser.py`: replace `/notes` with `/about` in
  the exact generated-route contract.
- Modify `docs/verification/evidence/browser-build.json`: bind verification to
  the newly built HTML.
- Modify `docs/verification/evidence/browser-matrix.json`,
  `browser-network.json`, `browser-console.json`,
  `browser-reduced-motion.json`, and `browser-screenshots.json`: record fresh
  browser results rather than retaining stale observations.
- Modify `docs/verification/assets/task7-home-*.webp` only when fresh captures
  differ, preserving the existing scenario filenames and dimensions.

## Architecture Integrity Lens

- **Invariant:** global navigation and footer behavior have one owner,
  `BaseLayout.astro`; generated-route truth has one owner,
  `scripts/verification/browser.py`.
- **Canonical contract:** internal project navigation uses semantic image/title
  anchors; external text links use blue plus `↗`.
- **Responsibility overlap:** the current broad `.other-card a` selector mixes
  project-title and external-link roles. The plan retires that overlap by
  scoping selectors, not by adding a second styling owner.
- **Higher-level simplification:** remove redundant CTA elements instead of
  normalizing their project-specific colors.
- **Retirement/falsifier:** `/notes` and its article are deleted. If remote
  `main` starts publishing `/notes` before execution, stop and reconsider a
  redirect.
- **Verdict:** proceed with existing owners; no new shared component is needed.

## Plan Pressure Test

- **Owner / contract / retirement:** clear owners; `/notes` retirement is
  explicit and bounded to an unshipped route.
- **Architecture integrity / higher-level path:** remove duplicate CTA UI and
  broad selectors at their existing owners.
- **Verification scope:** source contracts, build routes, browser matrix,
  console, network, accessibility, themes, locales, and privacy are covered.
- **Task executability:** each task has exact files, commands, expected failure,
  and commit boundary.
- **Pressure result:** proceed.

## Plan-Time Complexity Check

- **Target files:** `BaseLayout.astro` (about 160 lines), `index.astro` (about
  112 lines), project route (about 100 lines), browser verifier (about 330
  lines).
- **Existing size / shape signals:** compact page-local styles; no 800-line
  owner or new control-flow branch.
- **Owner fit:** all edits fit existing page/layout/verifier responsibilities.
- **Add-in-place risk:** low; the main risk is another overly broad link
  selector.
- **Better file boundary:** a dedicated `about.astro` is warranted; a generic
  Link component is not.
- **Recommendation:** edit in place plus one focused page and one focused test
  file.

## Task 1: Lock the Site Interface Contract

**Files:**
- Create: `tests/test_site_interface.py`

**Why:** Tests must prove the requested information architecture and link
semantics before production files change.

**Impact/Compatibility:** Source-level assertions complement, rather than
replace, generated-browser verification. They deliberately avoid Mundus
narrative content.

**Verification:** `python3 -m unittest tests.test_site_interface -v`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_site_interface.py`:

```python
from __future__ import annotations

import unittest
from pathlib import Path


class TestSiteInterface(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).parents[1]
        self.layout = (self.root / "src/components/BaseLayout.astro").read_text(
            encoding="utf-8"
        )
        self.home = (self.root / "src/pages/index.astro").read_text(
            encoding="utf-8"
        )

    def test_navigation_uses_home_work_and_about(self) -> None:
        self.assertIn('<Localized en="Home" zh="主页" />', self.layout)
        self.assertIn('href={`${base}#work`}', self.layout)
        self.assertIn('href={`${base}about`}', self.layout)
        self.assertNotIn('href={`${base}notes`}', self.layout)

    def test_about_page_owns_about_copy_and_empty_notes_section(self) -> None:
        about = (self.root / "src/pages/about.astro").read_text(encoding="utf-8")
        self.assertIn('id="about-title"', about)
        self.assertIn('id="notes-title"', about)
        self.assertIn('href={site.github}', about)
        self.assertNotIn('class="note"', about)
        self.assertFalse((self.root / "src/pages/notes.astro").exists())
        self.assertNotIn('id="about"', self.home)

    def test_footer_keeps_copyright_without_github(self) -> None:
        footer = self.layout.split('<footer class="site-footer">', 1)[1].split(
            "</footer>", 1
        )[0]
        self.assertIn("site.name", footer)
        self.assertNotIn("site.github", footer)
        self.assertNotIn("GitHub", footer)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test to verify RED**

Run:

```bash
python3 -m unittest tests.test_site_interface -v
```

Expected: three failures/errors because `about.astro` does not exist and the
old navigation and footer remain.

- [ ] **Step 3: Confirm the failure is behavioral**

Check that failures mention missing `src/pages/about.astro`, missing
`Localized en="Home"`, or retained footer GitHub. Do not proceed if the failure
is an import or syntax error.

- [ ] **Step 4: Keep the tests uncommitted until the first GREEN slice**

Run:

```bash
git diff --check
git status --short
```

Expected: only `tests/test_site_interface.py` is untracked and the worktree has
no whitespace errors.

- [ ] **Step 5: Record the RED evidence in the execution checkpoint**

Record the exact failing test count and representative assertions in the task
update. Do not commit a knowingly failing branch.

## Task 2: Implement the About Information Architecture

**Files:**
- Create: `src/pages/about.astro`
- Delete: `src/pages/notes.astro`
- Modify: `src/components/BaseLayout.astro`
- Modify: `src/pages/index.astro`
- Test: `tests/test_site_interface.py`

**Why:** The About content and empty Notes destination need one coherent page,
while global navigation and footer should expose only useful destinations.

**Impact/Compatibility:** Keeps `site.name` in metadata and copyright, preserves
`BASE_URL`, locale switching, theme switching, skip link, and Back to top.

**Repair Track:** Move the About owner from an in-page homepage section to
`about.astro`; update shared navigation at `BaseLayout.astro`.

**Retirement Track:** Delete the unshipped Notes article/route and footer GitHub
copy. No redirect or compatibility carrier is retained.

**Verification:** `python3 -m unittest tests.test_site_interface -v`

- [ ] **Step 1: Re-run the RED test immediately before implementation**

Run:

```bash
python3 -m unittest tests.test_site_interface -v
```

Expected: the same information-architecture failures from Task 1.

- [ ] **Step 2: Create the focused About page**

Create `src/pages/about.astro` with `BaseLayout`, `Localized`, and `site`
imports. Use this structure:

```astro
---
import BaseLayout from '../components/BaseLayout.astro';
import Localized from '../components/Localized.astro';
import { site } from '../config/site';
---

<BaseLayout title="About" description="About Jiaming Li's product and research practice.">
  <section class="about page-width" aria-labelledby="about-title">
    <div>
      <p class="eyebrow"><Localized en="About" zh="关于" /></p>
      <h1 id="about-title"><Localized en="A practice of making things clear." zh="研究、产品与实现。" /></h1>
    </div>
    <div class="about-copy">
      <p><Localized en="I am currently studying Computer Science at the National University of Singapore and exploring human–AI collaboration with AI4SG Lab. My work moves between research questions, product decisions, and working prototypes." zh="我目前在新加坡国立大学计算机系攻读硕士，师从 Yi-Chieh Lee 教授，并在校内 AI4SG Lab 开展人机协作研究。我的工作覆盖研究设计、产品决策与原型实现。" /></p>
      <p><Localized en="I like starting with what feels slightly inconvenient or overlooked: a conversation that is hard to return to, a music link that loses its meaning, a small world that needs better names. Then I try to make the next interaction feel obvious." zh="我通常从具体的问题出发：难以回溯的对话、失去上下文的音乐链接，或不符合中文语境的游戏命名。随后通过产品设计和工程实现，把问题转化为可验证的解决方案。" /></p>
      <a class="external-link" href={site.github} target="_blank" rel="noreferrer">
        <Localized en="Find more on GitHub" zh="在 GitHub 查看更多" />
        <span aria-hidden="true">↗</span>
      </a>
    </div>
  </section>
  <section class="notes page-width" aria-labelledby="notes-title">
    <p class="eyebrow"><Localized en="Notes" zh="随笔" /></p>
    <h2 id="notes-title"><Localized en="Notes" zh="随笔" /></h2>
  </section>
</BaseLayout>

<style>
  .eyebrow {
    margin: 0;
    color: var(--muted);
    font-size: .78rem;
    font-weight: 650;
    letter-spacing: .075em;
    text-transform: uppercase;
  }
  .about {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    padding: var(--space-section) 0;
  }
  h1, h2, p { margin-top: 0; }
  h1, h2 {
    margin-bottom: 0;
    font-size: clamp(2.4rem, 5vw, 4.6rem);
    line-height: .98;
    letter-spacing: var(--display-tracking);
  }
  .about-copy { max-width: 530px; }
  .about-copy p {
    font-size: 1.25rem;
    line-height: 1.45;
  }
  .about-copy p + p { color: var(--muted); }
  .about-copy .external-link {
    display: inline-block;
    margin-top: 1.5rem;
  }
  .notes {
    padding: var(--space-section) 0;
    border-top: 1px solid var(--rule-strong);
  }
  .notes .eyebrow { margin-bottom: 1.5rem; }
  :global(:root[data-locale='zh']) h1,
  :global(:root[data-locale='zh']) h2 {
    font-size: clamp(2.1rem, 4.2vw, 3.75rem);
    line-height: 1.2;
    letter-spacing: -.04em;
  }
  @media (max-width: 760px) {
    .about {
      grid-template-columns: 1fr;
      gap: 2.5rem;
    }
    .about, .notes { padding: 5rem 0; }
  }
  @media (max-width: 560px) {
    :global(:root[data-locale='zh']) h1,
    :global(:root[data-locale='zh']) h2 {
      font-size: clamp(2rem, 8vw, 2.8rem);
    }
  }
</style>
```

Do not add an empty-state sentence.

- [ ] **Step 3: Update shared layout and retire old owners**

In `BaseLayout.astro`:

```astro
<a class="monogram" href={base} aria-label={`${site.name}, home`}>
  <Localized en="Home" zh="主页" />
</a>
<nav aria-label="Primary navigation">
  <a href={base}><Localized en="Home" zh="主页" /></a>
  <a href={`${base}#work`}><Localized en="Work" zh="项目" /></a>
  <a href={`${base}about`}><Localized en="About" zh="关于" /></a>
</nav>
```

Change the footer to:

```astro
<footer class="site-footer">
  <span>© {new Date().getFullYear()} {site.name}</span>
</footer>
```

Set `.site-footer { justify-content: flex-start; ... }`. Delete
`src/pages/notes.astro`. Delete the entire homepage `<section id="about">` and
its page-local About selectors, leaving project content unchanged.

- [ ] **Step 4: Run focused and full tests to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_site_interface -v
npm test
```

Expected: all three About/navigation/footer tests and the complete existing
suite pass.

- [ ] **Step 5: Commit the information-architecture slice**

```bash
git add tests/test_site_interface.py src/pages/about.astro \
  src/pages/notes.astro src/components/BaseLayout.astro src/pages/index.astro
git commit -m "feat(portfolio): merge about and notes navigation"
```

Expected: one commit containing the route move, navigation/footer cleanup, and
contract tests.

## Task 3: Implement the Internal and External Link System

**Files:**
- Modify: `src/components/BaseLayout.astro`
- Modify: `src/pages/index.astro`
- Modify: `src/pages/projects/[...slug].astro`
- Test: `tests/test_site_interface.py`

**Why:** Internal titles should read as content, while external destinations
need one consistent visual and directional convention.

**Impact/Compatibility:** Keeps image and title anchors separate for semantics,
touch input, and keyboard use. No project data or MDX narrative changes.

**Repair Track:** Remove repeated internal CTA markup and broad selectors;
scope interactions by role.

**Retirement Track:** Delete `.project-link`, accent-colored CTA rules, and
`.other-card a { color: ... }`. Project accent variables remain because detail
pages still use them.

**Verification:** `python3 -m unittest tests.test_site_interface -v`

- [ ] **Step 1: Add the link contract tests**

In `setUp`, add:

```python
self.project = (
    self.root / "src/pages/projects/[...slug].astro"
).read_text(encoding="utf-8")
```

Add these methods:

```python
def test_internal_project_ctas_are_removed_but_titles_and_media_link(self) -> None:
    self.assertNotIn("Read the exploration", self.home)
    self.assertNotIn("查看项目详情", self.home)
    self.assertIn('class="media-link"', self.home)
    self.assertIn('<h3><a href={`${base}projects/${project.id}`}>', self.home)
    self.assertIn('class="other-media"', self.home)

def test_external_links_are_blue_and_use_external_arrow(self) -> None:
    about = (self.root / "src/pages/about.astro").read_text(encoding="utf-8")
    self.assertIn('class="external-link"', about)
    self.assertIn('aria-hidden="true">↗</span>', about)
    self.assertIn('class="external-link"', self.home)
    self.assertIn("--external-link: var(--blue);", self.layout)
    self.assertIn("color: var(--external-link);", self.project)

def test_project_titles_do_not_inherit_external_link_color(self) -> None:
    self.assertRegex(
        self.home,
        r"\.other-copy > h3 a\s*\{[^}]*color: var\(--ink\);",
    )
    self.assertNotIn(".other-card a { color: var(--blue);", self.home)
```

- [ ] **Step 2: Run the link tests to verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_site_interface.TestSiteInterface.test_internal_project_ctas_are_removed_but_titles_and_media_link \
  tests.test_site_interface.TestSiteInterface.test_external_links_are_blue_and_use_external_arrow \
  tests.test_site_interface.TestSiteInterface.test_project_titles_do_not_inherit_external_link_color \
  -v
```

Expected: failures for retained CTA markup and missing scoped external/title
rules.

- [ ] **Step 3: Implement the scoped link system**

In `BaseLayout.astro`, add:

```css
:root {
  --external-link: var(--blue);
}
.external-link {
  color: var(--external-link);
  font-weight: 620;
  text-decoration: none;
}
.external-link:hover {
  text-decoration: underline;
}
```

Keep the dark-theme `--blue` value as the source of contrast. Do not duplicate
theme-specific external-link colors.

Delete both `Read the exploration / 查看项目详情` anchors from `index.astro`.
Use these role-specific rules:

```css
.media-link,
.other-media {
  display: block;
  overflow: hidden;
}
.media-link :global(.project-media),
.other-media :global(.project-media) {
  transition: filter 180ms ease, transform 180ms ease;
}
.media-link:hover :global(.project-media),
.media-link:focus-visible :global(.project-media),
.other-media:hover :global(.project-media),
.other-media:focus-visible :global(.project-media) {
  filter: brightness(1.04) saturate(1.05);
  transform: scale(1.015);
}
.project-copy h3 a,
.other-copy > h3 a {
  color: var(--ink);
  text-decoration: none;
}
.project-copy h3 a:hover,
.project-copy h3 a:focus-visible,
.other-copy > h3 a:hover,
.other-copy > h3 a:focus-visible {
  text-decoration: underline;
}
.external-link {
  color: var(--external-link);
}
```

Add `class="external-link"` to the RSZ anchor and keep its `↗`. Preserve the
existing media border/radius rules and focus outline.

In `projects/[...slug].astro`, use:

```css
.prose :global(a) { color: var(--external-link); }
.links a {
  color: var(--external-link);
  border-color: color-mix(in srgb, var(--external-link) 45%, var(--line));
}
.links a:hover,
.links a:focus-visible {
  color: var(--paper);
  background: var(--external-link);
  border-color: var(--external-link);
}
```

- [ ] **Step 4: Run focused and full verification to confirm GREEN**

Run:

```bash
python3 -m unittest tests.test_site_interface -v
npm test
git diff --check
```

Expected: all source contract tests and the complete unit suite pass with no
whitespace errors.

- [ ] **Step 5: Commit the link-system slice**

```bash
git add src/components/BaseLayout.astro src/pages/index.astro \
  'src/pages/projects/[...slug].astro' tests/test_site_interface.py
git commit -m "fix(portfolio): unify internal and external links"
```

Expected: one focused visual/interaction commit with no project-content files.

## Task 4: Update the Generated Route Contract

**Files:**
- Modify: `scripts/verification/browser.py`
- Modify: `tests/test_release_verification.py`

**Why:** The release gate must fail if the build retains `/notes` or omits
`/about`.

**Impact/Compatibility:** Keeps the exact six-page build contract and all
Mundus/OmniPet safeguards.

**Verification:** focused route-manifest unit test plus Astro build.

- [ ] **Step 1: Add a failing exact-route test**

Add to `TestBrowserEvidence` in `tests/test_release_verification.py`:

```python
def test_generated_route_contract_uses_about_not_notes(self) -> None:
    self.assertEqual(
        browser.DIST_HTML_FILES,
        (
            "index.html",
            "about/index.html",
            "projects/dialogtree/index.html",
            "projects/mundus/index.html",
            "projects/nbti/index.html",
            "projects/side-b/index.html",
        ),
    )
    self.assertNotIn("notes/index.html", browser.DIST_HTML_FILES)
```

- [ ] **Step 2: Run the test to verify RED**

```bash
python3 -m unittest \
  tests.test_release_verification.TestBrowserEvidence.test_generated_route_contract_uses_about_not_notes \
  -v
```

Expected: FAIL showing `notes/index.html` where `about/index.html` is expected.

- [ ] **Step 3: Change the canonical generated-route tuple**

In `scripts/verification/browser.py`, replace:

```python
"notes/index.html",
```

with:

```python
"about/index.html",
```

Do not change project order, scenario order, image counts, or OmniPet checks.

- [ ] **Step 4: Verify GREEN and build routes**

```bash
python3 -m unittest \
  tests.test_release_verification.TestBrowserEvidence.test_generated_route_contract_uses_about_not_notes \
  -v
npm test
npm run build
find dist -name index.html -type f | sort
```

Expected: all tests pass and exactly these six HTML files exist: home, About,
DialogTree, Mundus, NBTI, Side B. No `dist/notes/index.html` exists.

- [ ] **Step 5: Commit the route-contract slice**

```bash
git add scripts/verification/browser.py tests/test_release_verification.py
git commit -m "test(portfolio): bind release gate to about route"
```

## Task 5: Regenerate Browser Evidence and Perform UI QA

**Files:**
- Modify: `docs/verification/evidence/browser-build.json`
- Modify: `docs/verification/evidence/browser-matrix.json`
- Modify: `docs/verification/evidence/browser-network.json`
- Modify: `docs/verification/evidence/browser-console.json`
- Modify: `docs/verification/evidence/browser-reduced-motion.json`
- Modify: `docs/verification/evidence/browser-screenshots.json`
- Modify when changed: `docs/verification/assets/task7-home-*.webp`
- Modify when changed: `docs/verification/assets/task7-mundus-*.webp`

**Why:** HTML, navigation, focus order, and homepage visuals changed, so prior
browser JSON and screenshot hashes are no longer valid evidence.

**Impact/Compatibility:** Preserve scenario names and fixed filenames so the
release validator remains stable. Re-observe Mundus without editing its content.

**Verification:** real browser captures plus `npm run verify`.

- [ ] **Step 1: Start the exact built site under the Pages base**

Run:

```bash
npm run build
npm run preview -- --host 127.0.0.1 --port 4321
```

Expected: Astro preview remains running and serves the project under
`/Oh-My-Portfolio/`.

- [ ] **Step 2: Capture the required browser matrix**

Use an isolated `agent-browser` session per scenario against
`http://127.0.0.1:4321/Oh-My-Portfolio/`. The command pattern is:

```bash
SESSION=home-en-light-1440
URL=http://127.0.0.1:4321/Oh-My-Portfolio/
agent-browser --session "$SESSION" open "$URL"
agent-browser --session "$SESSION" set viewport 1440 900
agent-browser --session "$SESSION" set media light
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
    heading => heading.textContent.trim()
  ),
  other: [...document.querySelectorAll('.other-card h3')].map(
    heading => heading.textContent.trim()
  )
})
EVALEOF
agent-browser --session "$SESSION" console --json
agent-browser --session "$SESSION" network requests --json
```

For Chinese scenarios, set state and reload after `open`:

```bash
agent-browser --session "$SESSION" eval \
  'localStorage.setItem("locale","zh");localStorage.setItem("theme","dark")'
agent-browser --session "$SESSION" open "$URL"
agent-browser --session "$SESSION" wait --load networkidle
```

For reduced-motion scenarios, use
`agent-browser --session "$SESSION" set media dark reduced-motion` before
opening. Use the following exact identities from
`browser.SCENARIO_EXPECTATIONS`:

```text
home-en-light-1440
home-en-light-1024
home-zh-dark-768
home-zh-dark-390
mundus-en-light-1440
mundus-zh-dark-desktop
mundus-en-light-390
mundus-zh-dark-mobile
```

For each scenario, record viewport, locale, theme, reduced-motion state,
horizontal overflow, broken/decoded/total images, focusable count, visible
focus, active animations where required, selected/other project order, and
Mundus product visual count. On Mundus pages, additionally evaluate:

```bash
agent-browser --session "$SESSION" eval \
  'JSON.stringify({productVisualCount:document.querySelectorAll(".overview-visual img").length})'
```

Replace the corresponding JSON records with these observed outputs; do not edit
values to satisfy the validator without observing them. Keep each named session
open until its screenshot is captured in Step 3.

- [ ] **Step 3: Perform targeted About and link QA**

At 1440, 1024, 768, and 390 widths, verify:

```text
/about loads in English and Chinese
Home / Work / About targets are correct
About GitHub opens the configured external URL
Notes heading has no article content
project image and title links work by mouse and keyboard
project titles use normal text color
RSZ and project Explore links are blue and display ↗
Back to top remains visible and footer has no GitHub action
light and dark contrast remain readable
console is empty and all requests return 2xx/3xx
```

Capture fresh homepage and Mundus screenshots using the fixed filenames in
`browser.SCREENSHOT_FILES`. For each active scenario session:

```bash
case "$SESSION" in
  home-en-light-1440)
    OUTPUT=task7-home-en-light-1440x900.webp ;;
  home-en-light-1024)
    OUTPUT=task7-home-en-light-1024x768.webp ;;
  home-zh-dark-768)
    OUTPUT=task7-home-zh-dark-reduced-768x1024.webp ;;
  home-zh-dark-390)
    OUTPUT=task7-home-zh-dark-reduced-390x844.webp ;;
  mundus-en-light-1440)
    OUTPUT=task7-mundus-en-light-1440x900.webp ;;
  mundus-zh-dark-desktop)
    OUTPUT=task7-mundus-zh-dark-reduced-1440x900.webp ;;
  mundus-en-light-390)
    OUTPUT=task7-mundus-en-light-390x844.webp ;;
  mundus-zh-dark-mobile)
    OUTPUT=task7-mundus-zh-dark-reduced-390x844.webp ;;
  *)
    printf 'unknown browser scenario: %s\n' "$SESSION" >&2
    exit 1 ;;
esac
agent-browser --session "$SESSION" screenshot /tmp/"$SESSION".png
FFMPEG=$(node -e "console.log(require('ffmpeg-static'))")
"$FFMPEG" -y -i /tmp/"$SESSION".png -c:v libwebp -q:v 80 \
  "docs/verification/assets/$OUTPUT"
agent-browser --session "$SESSION" close
```

Update dimensions and SHA-256 values from the actual WebP files.

- [ ] **Step 4: Rebind the build manifest and verify evidence**

Generate `browser-build.json` entries from the exact six built HTML files in
`browser.DIST_HTML_FILES`, using SHA-256 of each file. Then run:

```bash
npm run verify
```

Expected:

```text
release verification: facts=5/5 browser=pass privacy=pass
```

If verification fails, correct the observation or implementation and recapture;
never weaken the validator or reuse stale hashes.

- [ ] **Step 5: Commit browser evidence**

```bash
git add docs/verification/evidence docs/verification/assets
git commit -m "test(portfolio): refresh navigation browser evidence"
```

Expected: evidence commit contains only fresh browser JSON and screenshot
artifacts.

## Task 6: Final Verification, Concurrency Check, and Draft PR Update

**Files:**
- No planned production edits.
- Update only conflict-affected files if the parallel Mundus thread advanced
  them, preserving both owners' changes.

**Why:** Final evidence must describe the exact pushed tree, and concurrent
Mundus work must not be overwritten.

**Impact/Compatibility:** No merge, deployment, PR-ready transition, Pages
change, force push, rebase, reset, or preservation-branch mutation.

**Verification:** local gates, remote SHA equality, and GitHub PR checks.

- [ ] **Step 1: Fetch and compare before final verification**

```bash
git fetch origin --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/feat/mundus-omnipet-portfolio
gh pr view 1 --repo 0mn1si2i5/Oh-My-Portfolio \
  --json isDraft,headRefOid,mergeable,mergeStateStatus
```

Expected: clean worktree. If the remote advanced, stop the push path, inspect
`git log --left-right` and `git diff --name-status`, then integrate without
rebase/reset/force and rerun Tasks 4-5 for the resulting tree.

- [ ] **Step 2: Run the complete local gate**

```bash
npm ci
npm test
npm run build
npm run verify
npm audit --audit-level=low
git diff --check
git status --short
```

Expected: all tests pass; six pages build; facts 5/5, browser and privacy pass;
zero vulnerabilities; no whitespace errors; clean worktree.

- [ ] **Step 3: Confirm protected boundaries byte-for-byte**

```bash
git diff --exit-code b201772 -- \
  src/content/projects/mundus.mdx \
  src/components/MundusStory.astro \
  public/media/mundus \
  scripts/verification/facts.json \
  docs/verification/evidence/source-revisions.json \
  docs/verification/evidence/task7-fact-assertions.json
git ls-remote origin refs/heads/feat/omnipet-portfolio-deferred
```

Expected: no unauthorized Mundus content/fact differences from the starting
implementation baseline, and preservation branch remains at
`70b2c5ba1a789b97838ca1895600cd6c90eb320d`, unless the parallel Mundus owner
advanced those files and its commit was intentionally integrated.

- [ ] **Step 4: Push normally and watch PR checks**

```bash
git push origin feat/mundus-omnipet-portfolio
gh pr checks 1 --repo 0mn1si2i5/Oh-My-Portfolio --watch --interval 5
```

Expected: normal non-force push; build succeeds; deploy is skipped.

- [ ] **Step 5: Record final remote state**

```bash
LOCAL_SHA=$(git rev-parse HEAD)
REMOTE_SHA=$(git ls-remote origin refs/heads/feat/mundus-omnipet-portfolio | cut -f1)
PR_SHA=$(gh pr view 1 --repo 0mn1si2i5/Oh-My-Portfolio --json headRefOid --jq .headRefOid)
printf 'local=%s\nremote=%s\npr=%s\n' "$LOCAL_SHA" "$REMOTE_SHA" "$PR_SHA"
gh pr view 1 --repo 0mn1si2i5/Oh-My-Portfolio \
  --json isDraft,mergeable,mergeStateStatus,statusCheckRollup
gh api repos/0mn1si2i5/Oh-My-Portfolio/pages --jq '{html_url,source,build_type}'
```

Expected: all three SHAs are identical; PR remains Draft and mergeable; checks
are successful with deploy skipped; Pages still sources public `main`.

## Risks

- A concurrent Mundus push can invalidate browser evidence or create shared-file
  conflicts. Fetch before implementation and before push; recapture evidence
  after integration.
- Source-contract tests can become brittle if they assert incidental whitespace.
  Assertions intentionally target ownership markers and semantic selectors.
- Removing `/notes` would need a redirect if it became public. The pre-push
  Pages/main check is the falsifier.
- Hover feedback alone is insufficient. Real-browser keyboard focus and touch
  activation are required acceptance evidence.

## Retirement

- Delete the old Notes article and route with no fallback.
- Delete repeated internal project CTA markup and its accent-color rules.
- Delete the footer GitHub link while retaining the About GitHub destination.
- Retire broad Other Work link coloring; retain no compatibility selector.
- Do not retire project accent variables, Back to top, locale/theme state,
  Mundus verification, or any preservation branch.

## Self-Review Result

- **Spec coverage:** every information-architecture, link, footer, ownership,
  browser, and release requirement maps to Tasks 1-6.
- **Placeholder scan:** no deferred implementation or unspecified test step
  remains.
- **Type consistency:** all route names, CSS token names, selectors, and Python
  constants are consistent across tasks.
- **Compatibility:** public metadata, project ordering/routes, Mundus facts,
  OmniPet preservation, Draft PR, and Pages boundaries are explicit.
- **Verification:** every major slice has RED/GREEN commands; final evidence is
  bound to the exact built tree.
- **Architecture review:** required and satisfied by the owner/retirement checks
  above; no ADR is needed because no durable architecture decision or public API
  is introduced.
