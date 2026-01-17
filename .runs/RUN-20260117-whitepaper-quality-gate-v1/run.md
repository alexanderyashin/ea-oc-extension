# RUN-20260117-whitepaper-quality-gate-v1

## Goal
Quality gate for reproducibility anchors:
- pin manifest commit to the current HEAD
- stabilize line endings to reduce cross-platform diffs

## Changes
- paper/manifest.yml: sources.repository.commit -> HEAD
- add .gitattributes (md/yml/yaml -> LF)

## Exit criteria
- git status clean
- manifest shows current commit
- no accidental content changes in paper/whitepaper.md
