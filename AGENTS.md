# Repository Instructions

## Source Of Truth

- Product code: `src/`
- Release verification: `scripts/verification/` and `docs/verification/`
- CI and deployment boundary: `.github/workflows/deploy.yml`

## Agent Working Files

- Do not commit agent plans, checkpoints, work logs, resume notes, or task
  scratchpads by default.
- Store temporary agent material under `.agent-work/`; this directory is local
  and ignored by Git.
- A planning or decision document may be committed only when the user
  explicitly requests a persistent artifact.
- User-approved persistent documents belong in exactly one of:
  `docs/specifications/`, `docs/decisions/`, or `docs/verification/`.
- Do not create `docs/aegis/plans/`, `docs/aegis/work/`,
  `docs/superpowers/plans/`, or another tracked agent-work directory.

## Change Discipline

- Keep product changes, verification evidence, and governance documentation in
  separate commits when they are independently reviewable.
- Do not refresh retained browser evidence merely to make a refactor pass.
- Never force-push or rewrite published history without explicit user approval
  for the exact scope.

## Required Checks

```bash
npm run check:hygiene
npm test
npm run build
```

Release-affecting changes also require:

```bash
npm run verify -- --mundus-root "$MUNDUS_ROOT"
```
