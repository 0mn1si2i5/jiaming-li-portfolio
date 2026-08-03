# Portfolio Rename and Header Cleanup Design

## Goal

Remove redundant homepage metadata from the shared interface and rename the
project consistently across GitHub, local storage, package metadata, Pages
paths, tests, and verification evidence.

## Visitor Interface

The shared header has one Home entry only: the Home item in primary navigation.
The left-side Home link is deleted rather than replaced with an icon. This
avoids a duplicate destination and an unexplained symbol.

On mobile, the language and theme controls remain on the first row and the
three navigation items remain on the second row. Removing the left link must
not leave an empty grid column or change keyboard order unexpectedly.

Homepage featured project cards no longer show Status. Status remains in each
project detail hero, where it belongs with the complete project metadata.
Other project content, ordering, titles, summaries, images, and links remain
unchanged.

## Canonical Names

- Local root directory: `Jiaming Li Portfolio`
- GitHub repository: `0mn1si2i5/jiaming-li-portfolio`
- npm package name: `jiaming-li-portfolio`
- Local and deployed Pages base: `/jiaming-li-portfolio`
- GitHub Pages URL: `https://0mn1si2i5.github.io/jiaming-li-portfolio/`

The visitor-facing personal identity remains `Jiaming Li`. This rename changes
the project/repository identity, not the portfolio owner's displayed name.

## Rename Scope

Update maintained repository references that would otherwise become stale:

- `package.json` and `package-lock.json`;
- Astro's local fallback base;
- tests that enforce the local/CI base contract;
- README and active verification documentation;
- retained browser evidence and screenshots generated from the new base;
- Git remote URL after the GitHub repository rename.

Historical design and implementation records may retain old SHAs, but commands,
URLs, and project-base references that are intended to remain executable must
use the new repository name.

## Migration Order

1. Fetch and confirm the feature worktree matches Pull Request #1.
2. Add failing tests for header uniqueness, homepage Status removal, package
   identity, and local Pages base.
3. Implement the smallest source and configuration changes.
4. Build and recapture browser evidence under `/jiaming-li-portfolio`.
5. Run local tests, build, release verification, privacy, and audit gates.
6. Rename the GitHub repository with `gh repo rename`.
7. Update `origin` to the canonical new GitHub URL.
8. Push the feature branch normally and wait for Pull Request checks.
9. Confirm the PR remains Draft, CLEAN, and MERGEABLE, and deployment is
   skipped.
10. Move the local repository root to `Jiaming Li Portfolio`.
11. Run `git worktree repair` from the new root and verify both the main and
    feature worktrees, branches, remotes, and clean status.

The GitHub rename must happen before the migration commit is pushed because CI
derives its Pages base from `GITHUB_REPOSITORY`. Pushing first would build with
the old base and invalidate the new build-bound evidence.

## Concurrency and Safety

Use `12ca9a88991c414487f3376c2d4e4757d34ac4d9` as the initial baseline unless
the remote advances again. Fetch immediately before the GitHub rename and stop
if another thread has pushed.

Do not reset, rebase, force-push, merge the PR, deploy Pages, mark the PR ready,
or alter the OmniPet preservation branch. Preserve the Mundus V1.1 commits and
all user changes.

The local directory move happens last because Git linked-worktree metadata
stores absolute paths. After moving the parent directory, repair the metadata
instead of recreating or deleting worktrees.

## Verification

Automated tests must prove:

- the shared header contains exactly one Home destination;
- no `.monogram` source markup or mobile monogram rule remains;
- homepage project cards contain no Status markup or status styles;
- detail pages still render Status;
- package metadata uses `jiaming-li-portfolio`;
- the local Astro base is `/jiaming-li-portfolio`;
- generated HTML paths and assets use the new base;
- old `/Oh-My-Portfolio` runtime references are absent from maintained source,
  configuration, tests, and current verification evidence.

Real-browser checks cover 1440, 1024, 768, and 390 widths; English and Chinese;
light and dark themes; reduced motion; keyboard focus; console; network;
images; internal routes; external links; and the compacted homepage height.

## Acceptance

- The left header Home entry is deleted with no replacement symbol.
- Primary navigation remains Home, Work, About.
- Homepage cards omit Status; detail pages retain it.
- GitHub repository, local directory, npm package, Astro base, remote URL, and
  current verification evidence use the approved new names.
- Local and remote feature SHAs match after push.
- Pull Request #1 remains Draft, CLEAN, and MERGEABLE.
- PR build passes and deploy remains skipped.
- Both local worktrees remain registered, usable, and clean after the move.
- Mundus content and OmniPet preservation state remain intact.

## Out of Scope

- Merging Pull Request #1.
- Publishing the feature branch to Pages.
- Changing the displayed owner name or portfolio copy.
- Rewriting Git history or renaming feature branches.
- Adding a custom domain.
