# Jiaming Li — Explorations & Work

A bilingual (English / 中文) static portfolio built with Astro and deployed through GitHub Pages.

## Local development

```bash
npm install
npm run dev
```

## Content and media

- Project case studies live in `src/content/projects/` as MDX entries. Their frontmatter controls card metadata, media, and approved public links.
- Every project frontmatter entry must declare `featured` and a localized `kind` with paired `en` / `zh` values. `featured: true` places the project in Selected Work; `featured: false` places it in Other Work while preserving its detail route.
- `order` is scoped to a project's group: featured projects are sorted by `order` within Selected Work, and non-featured projects are independently sorted by `order` within Other Work. Configured external entries follow the collection-backed Other Work entries.
- All visitor-facing project metadata uses paired `en` / `zh` fields, and each project MDX keeps English and Chinese narrative sections together. When adding or editing portfolio content, update both languages in the same change unless it is intentionally single-language writing (for example, a future Notes post).
- The header language control stores the reader's choice locally. English is the default; Chinese is available on every portfolio page without a route change.
- Typography is bundled locally: Cormorant Garamond is used for the largest English exhibition and project display text; Newsreader is used for longer English headings, editorial subheads, and quotations; Instrument Sans is used for English interface, metadata, labels, and body text; Noto Serif SC and Noto Sans SC provide the corresponding Chinese display and interface/body roles. Do not replace these fonts with remote imports.
- Public links are centralized in `src/config/site.ts`.
- Add only approved, already-public media to `public/media/`; every visitor-facing project asset must be safe to publish. The DialogTree source video is intentionally not part of this repository; `dialogtree-preview.mp4` is the compressed web derivative.
- Private production evidence may inform accurate high-level writing, but it must never be copied into the portfolio. Do not publish private repository names, files, paths, prompts, references, provider responses, checkpoints, reviewer evidence, internal URLs, audit details, credentials, or other production artifacts.

## Deployment

Push `main` to GitHub. In the repository’s Pages settings, select **GitHub Actions** as the source. The included workflow detects whether the repository is a project site or a user site and builds with the corresponding base path.
