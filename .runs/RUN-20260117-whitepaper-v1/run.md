# RUN-20260117-whitepaper-v1

## Purpose
Create an ETS-first (executable-closed) whitepaper skeleton for K_EA and a reproducibility manifest.

## Inputs
- Repo: ea-oc-extension (main)
- Commit (start): 27602b3
- ETS: configs/ETS.K_EA.v1.1.yaml
- ETS sha256: c2385be94c79f52c9cbe6ee4437994c8833224cdce50ed8665241c0fdb7ecce6

## Actions
- Created `paper/manifest.yml` (pins repo + ETS hashes; declares non-empirical scope).
- Created `paper/whitepaper.md` as a minimal ETS-projection skeleton (diagnostic-only).
- Initialized `.runs/RUN-20260117-whitepaper-v1/` with run log files.

## Outputs
- paper/manifest.yml
- paper/whitepaper.md
- .runs/RUN-20260117-whitepaper-v1/{run.md,status.yaml,build.log}

## Notes
- No PDF build yet (text-only draft).
- Scope remains executable-closed; no new primitives introduced.
