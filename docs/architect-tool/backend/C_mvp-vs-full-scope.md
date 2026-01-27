TITLE: C. MVP vs Full Product Scope
PURPOSE: Fix the boundary between what is done now (MVP) and what is strictly deferred
AUDIENCE: Core dev, Stakeholders, Engine dev
LANGUAGE: EN
EVIDENCE_PROFILE: Scope contract
ROLE: Scope boundary spec
STATUS: ACTIVE

C. MVP vs Full Product Boundary

Principle

The MVP delivers a minimally sufficient layer:

to ingest a real system (LeanIX),

to transform it into CanonicalGraph,

to feed it into an existing deterministic ESTRA-compatible engine.

The MVP does NOT turn the system into BI, a dashboard, or an advisor.

MVP (Phase 1): what is included

1.1 Ingestion (LeanIX to CanonicalGraph)

Application Fact Sheets mapped to application nodes

Interface Fact Sheets mapped to interface nodes (if available)

Relations mapped to edges:

depends_on

exposes_interface

consumes_interface

Provenance on every node and edge

Deterministic normalization (stable sort plus stable hash)

RawSnapshot (optional, but recommended as a reproducibility artifact)

1.2 Simulation contract

SimulationInput equals CanonicalGraph plus scenario parameters (no UI)

SimulationResult equals stop or lock plus ledger plus states (no recommendations)

1.3 Explicit MVP prohibitions

no recommendations

no portfolio optimization

no maturity assessments or KPIs

no export of reports to PDF or PowerPoint (at all)

no write-back to LeanIX

Full Product (Phase 2 and beyond): what comes later

2.1 Model (ontology expansion)

Business Capabilities

Business Processes and Value Streams

Org Units, User Groups, Ownership as first-class structures

Technology Components, Platforms, Data Objects

Environments (prod and non-prod), deployment topology

Events, incidents, changes as separate entities (if needed)

2.2 Ingestion (multi-source)

ServiceNow (CMDB, incidents)

GitHub (repositories, dependencies), CI/CD

Cloud providers (accounts, services, connectivity)

Finance and budgets (facts only)

2.3 Engine and simulation

more complex scenarios (multi-shocks, time windows, heterogeneous thresholds)

parameter calibration based on external data

extended ledger formalization (still without recommendations)

2.4 Access control and security

RBAC at the level of ingestion configurations and artifacts

audit logging

redaction of personal data

Boundary between tool and demonstrator (future)

Even the Full Product does NOT become a BI consulting robot.

Strict line:

allowed: showing structure, thresholds, facts, and consequences in terms of the model

forbidden: statements like reduce X, increase Y, hire people, change org structure

Any wording that resembles a recommendation is out of scope.