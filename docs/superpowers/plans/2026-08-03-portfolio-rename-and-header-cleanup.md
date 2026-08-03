# Portfolio Rename and Header Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove redundant homepage metadata and migrate the repository, package, Pages base, remote, and local root to the approved `Jiaming Li Portfolio` / `jiaming-li-portfolio` identity.

**Architecture:** `BaseLayout.astro` remains the sole header owner and keeps one Home destination in primary navigation. Project detail metadata remains collection-backed, while the homepage stops rendering Status. Astro continues deriving CI base from `GITHUB_REPOSITORY`, with its local fallback and retained evidence migrated to `/jiaming-li-portfolio`.

**Tech Stack:** Astro 7, Python `unittest`, npm, Git worktrees, GitHub CLI, GitHub Pages.

**Baseline:** `fe10644683bc0b8813116f504c027b3488ada869`, containing Mundus V1.1 and the approved rename design. The remote feature branch was `12ca9a88991c414487f3376c2d4e4757d34ac4d9` when isolation began.

**Compatibility Boundary:** Preserve all project content, the Mundus V1.1 facts/media, OmniPet preservation branch, PR Draft state, `main`, and current Pages deployment. Do not reset, rebase, force-push, merge, mark ready, or deploy.

---

## Task 1: Lock and Implement the Compact Interface

**Files:**
- Modify: `tests/test_site_interface.py`
- Modify: `src/components/BaseLayout.astro`
- Modify: `src/pages/index.astro`

- [ ] **Step 1: Add failing interface tests**

Add tests asserting:

```python
def test_header_has_one_home_destination_without_monogram(self) -> None:
    header = self.layout.split('<header class="site-header">', 1)[1].split(
        "</header>", 1
    )[0]
    self.assertEqual(header.count('<Localized en="Home" zh="主页" />'), 1)
    self.assertNotIn('class="monogram"', header)
    self.assertNotIn(".monogram", self.layout)

def test_home_cards_omit_status_while_project_details_keep_it(self) -> None:
    self.assertNotIn('class="status"', self.home)
    self.assertNotIn(".project-copy .status", self.home)
    self.assertIn('<dt><Localized en="Status" zh="项目状态" /></dt>', self.project)
```

- [ ] **Step 2: Verify RED**

Run:

```bash
python3 -m unittest tests.test_site_interface -v
```

Expected: the two new tests fail because the monogram and homepage Status still
exist.

- [ ] **Step 3: Implement the minimal interface change**

Delete the monogram anchor and all `.monogram` rules from
`BaseLayout.astro`. Keep primary navigation Home, Work, About. Change the
desktop header to right-align navigation and controls. On mobile, use two
columns for locale/theme controls and keep navigation on the second row.

Delete the homepage `<p class="status">` and its two status style rules from
`index.astro`. Change the summary selector from
`.project-copy > p:not(.status)` to `.project-copy > p`.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python3 -m unittest tests.test_site_interface -v
npm test
git diff --check
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_site_interface.py src/components/BaseLayout.astro src/pages/index.astro
git commit -m "fix(portfolio): remove redundant homepage metadata"
```

## Task 2: Migrate the Maintained Project Identity

**Files:**
- Modify: `tests/test_site_interface.py`
- Modify: `tests/test_workflow.py`
- Modify: `package.json`
- Modify: `package-lock.json`
- Modify: `astro.config.mjs`
- Modify: `README.md`
- Modify: `docs/verification/task7-release-verification.md`

- [ ] **Step 1: Add failing identity tests**

Add:

```python
def test_package_and_local_pages_base_use_canonical_repository_name(self) -> None:
    package = json.loads((self.root / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((self.root / "package-lock.json").read_text(encoding="utf-8"))
    config = (self.root / "astro.config.mjs").read_text(encoding="utf-8")
    self.assertEqual(package["name"], "jiaming-li-portfolio")
    self.assertEqual(lock["name"], "jiaming-li-portfolio")
    self.assertEqual(lock["packages"][""]["name"], "jiaming-li-portfolio")
    self.assertIn("const localProjectBase = '/jiaming-li-portfolio';", config)
```

Update the workflow test expectation to:

```python
self.assertIn("const localProjectBase = '/jiaming-li-portfolio';", config)
```

- [ ] **Step 2: Verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_site_interface.TestSiteInterface.test_package_and_local_pages_base_use_canonical_repository_name \
  tests.test_workflow.TestPullRequestWorkflow.test_local_and_ci_builds_share_the_pages_base -v
```

Expected: both tests fail on the old package/base values.

- [ ] **Step 3: Implement canonical identity**

Set the package name in `package.json` and both package-lock locations to
`jiaming-li-portfolio`. Set Astro's local fallback to
`/jiaming-li-portfolio`.

Update maintained README and current release-verification references to the new
repository, Pages URL, and base. Historical design/plan records remain
immutable records unless their commands are active migration instructions.

- [ ] **Step 4: Verify GREEN and build**

Run:

```bash
npm test
npm run build
rg -n "/Oh-My-Portfolio|Oh-My-Portfolio|oh-my-portfolio" \
  package.json package-lock.json astro.config.mjs README.md \
  src tests scripts docs/verification
```

Expected: tests/build pass; the search returns no maintained runtime reference.

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json astro.config.mjs README.md \
  docs/verification/task7-release-verification.md tests/test_site_interface.py \
  tests/test_workflow.py
git commit -m "chore(portfolio): adopt canonical project identity"
```

## Task 3: Rebuild Browser Evidence Under the New Base

**Files:**
- Modify: `docs/verification/evidence/browser-build.json`
- Modify: `docs/verification/evidence/browser-matrix.json`
- Modify: `docs/verification/evidence/browser-network.json`
- Modify: `docs/verification/evidence/browser-console.json` when observed values differ
- Modify: `docs/verification/evidence/browser-reduced-motion.json` when observed values differ
- Modify: `docs/verification/evidence/browser-screenshots.json`
- Modify: `docs/verification/assets/task7-*.webp`

- [ ] **Step 1: Build and serve the new base**

```bash
npm run build
npm run preview -- --host 127.0.0.1 --port 4321
```

Expected preview root:

```text
http://127.0.0.1:4321/jiaming-li-portfolio/
```

- [ ] **Step 2: Recapture the browser matrix**

Re-run the existing eight canonical scenarios at 1440, 1024, 768, and 390,
including English/Chinese, light/dark, reduced motion, keyboard focus, image
decode, overflow, project ordering, console, and network checks.

Additionally verify:

```text
exactly one visible Home navigation entry
no .monogram element
no homepage .status element
project detail Status remains visible
all internal href values begin with /jiaming-li-portfolio/
```

- [ ] **Step 3: Replace screenshots and manifests**

Capture full-page screenshots with existing canonical filenames. Convert to
WebP with `ffmpeg-static`, then update dimensions and SHA-256. Recompute the
six generated HTML SHA-256 values in `browser-build.json`.

- [ ] **Step 4: Verify all retained evidence**

```bash
npm test
npm run verify
git diff --check
```

Expected:

```text
release verification: facts=5/5 browser=pass privacy=pass
```

- [ ] **Step 5: Commit**

```bash
git add docs/verification/evidence docs/verification/assets
git commit -m "test(portfolio): refresh renamed Pages evidence"
```

## Task 4: Rename GitHub, Update the Draft PR, and Move the Local Root

**Files:**
- GitHub repository setting
- Local Git remote
- Local repository/worktree paths

- [ ] **Step 1: Run final pre-migration gates**

```bash
git fetch origin --prune
git status --short --branch
npm ci
npm test
npm run build
npm run verify
npm audit --audit-level=low
git diff --check
```

Stop if the remote feature branch is no longer
`12ca9a88991c414487f3376c2d4e4757d34ac4d9` or if the shared worktree has new
unresolved changes beyond the already observed spec deletion.

- [ ] **Step 2: Rename the GitHub repository**

```bash
gh repo rename -R 0mn1si2i5/Oh-My-Portfolio jiaming-li-portfolio --yes
git remote set-url origin https://github.com/0mn1si2i5/jiaming-li-portfolio.git
```

Verify the old repository resolves to the renamed repository and the canonical
repository reports the new name.

- [ ] **Step 3: Push migration commits to the existing PR branch**

From this isolated branch:

```bash
git push origin HEAD:feat/mundus-omnipet-portfolio
gh pr checks 1 --repo 0mn1si2i5/jiaming-li-portfolio --watch --interval 5
```

Expected: build passes, deploy skips, PR remains Draft/CLEAN/MERGEABLE, and
local/remote/PR SHAs match.

- [ ] **Step 4: Move and repair the local repository**

Only after all processes using the old root have stopped:

```bash
mv "/Users/bytedance/Desktop/Zen/Oh My Portfolio" \
  "/Users/bytedance/Desktop/Zen/Jiaming Li Portfolio"
git -C "/Users/bytedance/Desktop/Zen/Jiaming Li Portfolio" worktree repair \
  "/Users/bytedance/Desktop/Zen/Jiaming Li Portfolio/.worktrees/mundus-omnipet-portfolio" \
  "/Users/bytedance/Desktop/Zen/Jiaming Li Portfolio/.worktrees/portfolio-rename-migration"
```

Update `origin` in the common repository and verify every registered worktree
from its new path. Preserve the shared worktree's uncommitted spec deletion.

- [ ] **Step 5: Final state verification**

Confirm:

```text
repository: 0mn1si2i5/jiaming-li-portfolio
Pages URL: https://0mn1si2i5.github.io/jiaming-li-portfolio/
local root: /Users/bytedance/Desktop/Zen/Jiaming Li Portfolio
PR #1: Draft, CLEAN, MERGEABLE
deploy: skipped
main and public Pages deployment: unchanged
OmniPet preservation branch: unchanged
```

## Risks and Stop Conditions

- GitHub rename changes the Pages URL. No redirect is assumed for the old Pages
  URL.
- The shared feature worktree contains a pre-existing uncommitted deletion of
  the rename spec. Never restore or commit it.
- Local directory movement is blocked while another process actively uses the
  old root. Code/remote migration may complete while the physical move remains
  explicitly deferred.
- Any remote advancement after the recorded baseline stops the rename/push
  sequence for reconciliation; never force-push.

## Self-Review

- The plan covers interface, package/config, evidence, GitHub, PR, remote, and
  local worktree migration.
- No fallback, redirect assumption, history rewrite, merge, or deployment is
  introduced.
- Every source change follows RED/GREEN; external rename and filesystem move
  have explicit preconditions and stop points.
