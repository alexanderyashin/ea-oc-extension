# RUN-20260117-whitepaper-manifest-pinfix-v1

## Goal
Pin paper/manifest.yml to the current repository commit that contains the manifest itself.

## Change
- paper/manifest.yml: sources.repository.commit -> current HEAD

## Exit criteria
- manifest commit equals HEAD
- clean git status
