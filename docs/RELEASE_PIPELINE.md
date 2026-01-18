# Release Pipeline (Local) — ea-oc-extension

## Entry point
`tools/release.ps1` is the only supported local release entry point.

Git is the source of truth:
- committed state: `git show HEAD:<path>`
- working tree state: `git status`, `git diff`

## Exact behavior of tools/release.ps1

Inputs:
- `-Version <semver>` (required). Tag will be `v<Version>`.
- `-AutoCommit` (optional).

Steps:
1) Validates:
   - inside a Git repo
   - remote `origin` exists
   - fetches tags from `origin`
   - refuses if tag `v<Version>` already exists

2) Deterministic cleanliness:
   - if working tree is dirty:
     - without `-AutoCommit`: abort
     - with `-AutoCommit`: stages everything and creates exactly one commit:
       `chore(release): prepare v<Version>`
       if commit fails: abort

3) HARD GATE (exactly once):
   - runs `tools/check_whitepaper.ps1`
   - any non-zero exit code: abort
   - refuses release if gate changes working tree

4) Release:
   - creates annotated tag `v<Version>`
   - pushes deterministically:
     - `git push origin HEAD`
     - `git push origin v<Version>`

## Canonical usage examples

### 1) Clean working tree (recommended)
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\release.ps1 -Version 1.2.0
