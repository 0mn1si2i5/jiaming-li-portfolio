# Todo Checkpoint Draft

## Authority

- Branch: `feat/mundus-next`
- Current HEAD: `fdbd093`
- Public Mundus SHA:
  `378fe528ca1c8f83f0280f83383b5e785e851285`
- Approved spec commit: `89ab2d8`
- Revised plan commit: `0e2d2c9`
- Previous worktree retired; commits were migrated onto clean `main`
  `d99fcbf`.

## Todo

- [x] Preserve and harden Task 1 RED contract.
- [x] Task 2: accessible three-mode preview.
- [x] Task 3: bilingual Mundus and Chronorbis narrative.
- [x] Task 4: verified three-mode media capture.
- [x] Task 5: narrow immutable facts.
- [x] Task 6: browser evidence contract.
- [ ] Task 7: regenerate browser evidence.
- [ ] Task 8: release record, full gates, push, and Draft PR CI.
- [ ] Final independent review and verification-before-completion.

## Evidence

- Task 1 migrated commits: `38434c3`, `aac4e9d`.
- Task 2 initial migration: `b665b3c`.
- Task 2 semantics/failure-path fix: `7532d9d`.
- Task 2 focused test: pass under Python 3.9.6.
- Astro build: six pages.
- Task 2 specification review: compliant.
- Task 2 quality review: approved.
- Task 3 narrative and Chronorbis commit: `76b0ea6`.
- Task 3 specification review: compliant.
- Task 3 quality review: approved after the prose-column overflow fix.
- Task 4 media capture commit: `98bee4c`.
- Task 4 specification review: compliant.
- Task 4 quality review: approved after adding staged publication rollback.
- Task 4 focused media tests: two passed under Python 3.9.6.
- Task 4 media evidence: three `1920x1080` Story assets, five distinct
  SHA-256 values, and zero error, failed-request, or panel-overflow counts.
- Task 4 `git diff --check`: pass.
- Task 5 fact-contract commit: `d092eab`.
- Task 5 strict TDD: old five-fact catalog produced the expected RED.
- Task 5 structured-fact tests: 22 passed under Python 3.9.6.
- Task 5 immutable evidence verifier: `[]`.
- Task 5 specification review: compliant.
- Task 5 quality review: approved after closing four Astro false-positive
  paths.
- Task 5 plan correction: claim extraction now routes `.astro` sources
  through a bounded rendered-semantics parser instead of treating them as
  MDX. The Story UI and approved fact tokens were not changed.
- Task 6 browser-contract commit: `fdbd093`.
- Task 6 focused validator tests: four passed under Python 3.9.6.
- Task 6 full browser test class: 12 passed and 2 expected stale-evidence
  failures pending Task 7.
- Task 6 specification review: compliant.
- Task 6 quality review: approved after rejecting malformed viewports,
  non-finite measurements, and boolean durations.

## Active Slice

Task 7: rebuild the exact Portfolio output and regenerate all eight browser
evidence scenarios.

## Resume State Hint

Read this checkpoint, then read the approved spec and revised plan with:

```bash
git show 89ab2d8:docs/superpowers/specs/2026-08-04-mundus-chronorbis-case-redesign.md
git show 0e2d2c9:docs/superpowers/plans/2026-08-04-mundus-chronorbis-case-redesign-revised.md
```

Verify current branch, HEAD, and worktree before editing.

## Drift Check Draft

- Original intent served: yes.
- Compatibility boundary intact: yes.
- New owner/fallback introduced: no.
- Authority migration documented: yes.
- Evidence sufficient for Task 6: yes.
- Task 1 RED contract preserved: yes.
- New product owner or fallback introduced: no.
- Unsupported complex Astro syntax remains fail-closed: yes.
- Stale browser evidence is isolated to Task 7: yes.
- Decision: `continue`.
