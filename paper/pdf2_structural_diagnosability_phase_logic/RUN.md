# RUN — paper/pdf2* (PDF-2 / Skeleton)

Purpose:
Create a canonical, buildable folder + file scaffold for:
paper/pdf2_structural_diagnosability_phase_logic/

Scope Locks:
- No edits to PDF-0 / PDF-1 / ETS semantics
- No new primitives, no redefinitions, no prescriptions
- Placeholders only

Build (PowerShell):
Set-Location C:\Users\Megaport\work\ea-oc-extension\paper\pdf2_structural_diagnosability_phase_logic
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

Critique log policy: append-only.
