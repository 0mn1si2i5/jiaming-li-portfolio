# Site Navigation and Link System Design

## Goal

Simplify the portfolio's information architecture and make link behavior
consistent without rewriting project narratives or changing the established
digital exhibition system.

The result should make internal exploration feel direct, distinguish external
destinations clearly, and remove redundant interface elements.

## Information Architecture

The primary navigation contains:

1. `Home / 主页`
2. `Work / 项目`
3. `About / 关于`

The top-left home link also displays `Home / 主页`. The visitor-facing label
changes, but `Jiaming Li` remains the site name in document titles, metadata,
the homepage introduction, and copyright.

The existing homepage About section moves to a dedicated `/about` route.
The new page contains:

1. the current bilingual About heading and copy;
2. the current bilingual GitHub link;
3. an empty `Notes / 随笔` section reserved for future writing.

The current Notes article is removed. `/notes` is no longer generated, and no
redirect is added because the site is still a draft and the route is not part
of the deployed public `main` baseline.

## Link Semantics

Internal project cards do not show a repeated `Read the exploration /
查看项目详情` call to action. The project image and title remain separate,
semantic links to the same detail route:

- image hover and focus slightly increase brightness and scale;
- title hover and focus add an underline;
- both links retain visible `focus-visible` outlines;
- touch users can activate either link without depending on hover.

Project titles always use the normal text color. In particular, the Side B
title must not inherit the external-link blue.

External text links use the shared blue color and a northeast arrow, `↗`.
This applies to the About GitHub link, RSZ Steam Workshop link, project prose
links, and project-detail Explore links. Explore pills use blue text and border
at rest, then a blue background with readable contrast on hover and focus.

Internal navigation and linked project titles do not use the external blue.
Directional arrows are reserved by destination:

- `↗` for external destinations;
- no arrow for linked project images and titles;
- `↓` remains valid for the homepage in-page Work jump;
- `↑` remains valid for Back to top.

## Footer

The footer contains copyright only. Its redundant GitHub link is removed.
The fixed Back to top control remains available and no longer competes with a
second action at the lower-right edge.

## Ownership and Concurrency

This change may update shared layout, homepage, About route, generic project
route styles, tests, and browser evidence. It must not change:

- Mundus product facts, narrative, screenshots, or source evidence;
- the OmniPet preservation branch or any OmniPet visitor surface;
- project ordering or project-specific content;
- Pages settings, deployment state, or pull-request draft state.

Immediately before implementation and before pushing, fetch the remote and
compare the local branch with Pull Request #1. If the Mundus thread advances
the shared branch, integrate from its new head without resetting, rebasing,
overwriting, or restoring old files.

## Verification

Use test-first changes to lock the intended structure before editing production
files. Automated checks must cover:

- `/about` is included in the generated route manifest;
- `/notes` is absent from the generated route manifest;
- the header labels and targets match the new navigation;
- the footer has no GitHub link;
- repeated internal project CTAs are absent;
- external links retain the blue and `↗` convention;
- internal project titles retain the normal text color;
- the deferred OmniPet route remains absent.

After implementation, regenerate build-bound browser evidence rather than
reusing historical JSON. Validate:

- English and Chinese;
- light and dark themes;
- widths 1440, 1024, 768, and 390;
- keyboard traversal and visible focus;
- reduced motion;
- no horizontal overflow or broken images;
- empty browser console and successful network requests;
- correct external targets and internal routes.

The final tree must pass unit tests, Astro build, fact verification, browser
verification, privacy scan, `npm audit`, and `git diff --check`.

## Acceptance

- The header uses Home, Work, and About in both locales.
- The About content lives at `/about`; Notes has no article content.
- `/notes` is not generated.
- Homepage project details are reached through images and titles, with clear
  hover and keyboard-focus feedback.
- External links are consistently blue and use `↗`.
- Side B and all other linked project titles use the normal text color.
- The footer GitHub link is gone and Back to top remains.
- No Mundus product content or OmniPet preservation state changes.
- Pull Request #1 remains a draft and Pages remains deployed from public
  `main`.

## Out of Scope

- New Notes posts, a Notes content model, or a CMS.
- Project narrative rewrites.
- Mundus V1.1 publication work.
- OmniPet restoration or publication.
- Merge, deployment, Pages changes, or pull-request readiness changes.
