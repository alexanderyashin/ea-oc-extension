# RUN-20260117-whitepaper-manifest-final-pin-v1

Goal: pin paper/manifest.yml to the commit that contains it (HEAD).

Change:
- paper/manifest.yml: sources.repository.commit -> HEAD

Exit:
- manifest commit equals HEAD
- clean git status
