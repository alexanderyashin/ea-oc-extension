# Whitepaper PDF build & watch (Windows)

Target artifact:
- `paper/whitepaper.pdf`

Preferred source:
- `paper/whitepaper.md`

## Prerequisites (Windows)

You need:
- **Pandoc** (`pandoc` in PATH)
- **LaTeX engine** via MiKTeX or TeX Live (**`xelatex`** in PATH)
- (optional) **Git** (`git` in PATH) for deterministic `SOURCE_DATE_EPOCH` from HEAD commit time

Quick install (one possible route):
- Pandoc: `winget install --id JohnMacFarlane.Pandoc -e`
- MiKTeX: `winget install --id MiKTeX.MiKTeX -e`
- Git: `winget install --id Git.Git -e`

After installs, **restart** VS Code (PATH refresh).

## Build once

From repo root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build_whitepaper_pdf.ps1
