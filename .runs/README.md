# RUN META LAYER (MANDATORY)

This directory is a MACHINE-READABLE RUN LOG.
It is NOT documentation and NOT part of the scientific content.

Rules:
- Every run MUST create a new subfolder.
- Each run folder MUST contain:
  - run.md
  - status.yaml
  - build.log (optional)
- Every run MUST end with:
  - git commit
  - git push
- GOOD runs SHOULD be tagged.

Statuses allowed:
- GOOD
- FAILED
- INCOMPLETE

Chats MUST read this directory before starting work.
Chats MUST write here before finishing work.
