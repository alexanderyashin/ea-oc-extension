# LeanIX Synthetic Sample Dataset (sample-v1)

Purpose
- Synthetic dataset for interoperability / import / parsing tests.
- No customer data. No proprietary exports. Deterministic generation.

Format
- CSV files under:
  - fact_sheets/
  - relations/

Notes
- IDs are stable and deterministic.
- Relations use source_id/target_id.
- Intended as "LeanIX-like" import fixtures (Fact Sheet-style entities + relations).

Size (approx.)
- 60 Applications
- 40 IT Components
- 35 Business Capabilities
- 25 Providers
- 40 Data Objects
- Relations: ~600-800 rows
