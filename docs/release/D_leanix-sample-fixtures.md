# LeanIX sample fixtures (synthetic)

Location
- fixtures/leanix/sample-v1/

Purpose
- Synthetic dataset for interoperability / import / parsing tests.
- Intended for UI, ingestion, graph, and metric validation.
- Fully synthetic and deterministic. No customer or proprietary data.

Scope
- Fact sheets:
  - Applications (APP)
  - IT Components (ITC)
  - Business Capabilities (BC)
  - Providers (PRV)
  - Data Objects (DO)
- Relations:
  - Application → Business Capability (supports)
  - Application → IT Component (uses)
  - Application → Provider (depends_on)
  - Application → Data Object (reads_writes)

Dataset size (current snapshot)
- Applications: 60
- IT Components: 40
- Business Capabilities: 35
- Providers: 15
- Data Objects: 50
- Relations (approximate):
  - app_to_capability: ~130
  - app_to_it_component: ~217
  - app_to_provider: ~61
  - app_to_data_object: ~148

Determinism
- Generation is fully deterministic via a fixed random seed.
- Output CSV files are sorted and cleaned on each run.
- Re-running the generator produces byte-identical CSV files
  (verifiable via file hashes).

How to (re)generate
- Use Windows Python launcher:
  - py fixtures/leanix/sample-v1/generate.py

How to validate
- Structural validation and integrity checks:
  - py fixtures/leanix/sample-v1/validate.py
- Validator checks:
  - presence of all expected CSV files
  - correct object counts
  - referential integrity of relations
  - basic structural consistency

Notes
- A warning like:
    "Could not find platform independent libraries <prefix>"
  may appear when using the Windows Python launcher.
- This warning does not affect execution or output correctness
  and can be safely ignored for fixture generation.
