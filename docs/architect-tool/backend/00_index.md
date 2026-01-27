TITLE: Architect Tool Backend — Index
PURPOSE: Navigation across the backend core (model, ingestion, MVP boundaries)
AUDIENCE: Core dev, Connector dev, Simulation dev
LANGUAGE: EN
EVIDENCE_PROFILE: Design-spec (no runtime claims)
ROLE: Backend documentation root
STATUS: ACTIVE

Backend core of the Architect Tool — Index

This section fixes the headless backend: the canonical model, ingestion adapters, and the data contract up to simulation.
No UI is assumed here.

Documents

A. Canonical Model

File: A_canonical-model.md

Defines what the Canonical Graph is, which nodes and edges exist, which attributes are allowed, and which determinism invariants apply.

B. Ingestion: SAP LeanIX (MVP)

File: B_ingestion-leanix.md

Describes how LeanIX Fact Sheets and Relations are mapped into the Canonical Graph, how stable IDs and snapshot versioning are ensured, and how errors and omissions are handled.

C. MVP vs Full Product Boundary

File: C_mvp-vs-full-scope.md

Defines what is considered MVP scope (Applications, Interfaces, Dependencies) and what is strictly deferred.

Non-negotiable backend constraints

Headless and embeddable (module or library; no UI assumptions)

No BI: no construction of truth dashboards

No recommendations, advice, or optimizations (the backend never says do this)

Determinism: identical input produces identical output

Compatibility with existing ESTRA and engine principles: ledger plus STOP or LOCK as fact, not as advice

Data flow contract (summary)

Ingestion to Canonical Model to Simulation Input

Ingestion reads an external source (LeanIX) and produces RawSnapshot.

The normalizer transforms RawSnapshot into CanonicalGraph.

Simulation accepts SimulationInput (a projection of CanonicalGraph plus scenario parameters) and produces SimulationResult with ledger.

For details, see A_canonical-model.md and B_ingestion-leanix.md.