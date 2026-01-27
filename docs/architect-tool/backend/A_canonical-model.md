title: "A. Canonical Model"
purpose: "Define a canonical headless model of the system for ingestion → simulation"
audience: ["Core dev", "Connector dev", "Simulation dev"]
language: "EN"
evidence_profile: "Design-spec (schema + invariants)"
role: "Canonical data model spec"
status: "ACTIVE"

A. Canonical Model (Canonical Graph)

0) Model purpose

The canonical model separates:

external data sources (LeanIX, etc.), which may be unstable,

from the internal deterministic core (CanonicalGraph),
which serves as the single contract for simulation.

The model MUST be:

deterministic (see D_determinism.md),

headless (no UI-related fields),

extensible without breaking the MVP,

free of BI / recommendations / optimizations.

1) Basic concept

The system is represented as a directed multigraph:

Node — an entity,

Edge — a directed relationship.

1.1 Common fields

Each Node and Edge MUST contain:

id — a stable string identifier,

kind — the type of entity / relationship,

attrs — a JSON-compatible attribute map,

provenance — data origin information.

2) CanonicalGraph structure

CanonicalGraph
├─ meta
│ ├─ schemaVersion
│ ├─ sourceSystem
│ ├─ snapshotId
│ ├─ capturedAt
│ └─ determinism
├─ nodes[]
└─ edges[]

2.1 meta (mandatory)

schemaVersion — schema version (e.g. CG-0.1)

sourceSystem — primary source of the snapshot

snapshotId — snapshot identifier

capturedAt — ISO8601 timestamp

determinism:

sortOrder — textual description of canonical sorting

hashAlgo — sha256

contentHash — sha256(canonicalJson)

The source of truth for sorting, serialization, and hashing is D_determinism.md.
Any deviation is considered a contract violation.

3) Canonical serialization and contentHash

3.1 canonicalJson

canonicalJson is a JSON string produced strictly according to the rules defined in D_determinism.md:

deterministic sorting of nodes[] and edges[],

lexicographic ordering of keys,

single-line serialization (compressed JSON),

UTF-8 encoding.

No other forms of serialization are considered canonical.

3.2 contentHash

contentHash = sha256(canonicalJson)

Requirements:

contentHash is mandatory,

used for auditability and reproducibility,

used as a content identifier when passed into simulation,

MUST match recomputation using the procedure defined in D_determinism.md.

4) MVP node ontology (Node.kind)

4.1 application

Meaning: an application system or service.

Mandatory attrs:

name (string)

externalId (string)

Allowed attrs (optional):

lifecycle

criticality

owner

tags

4.2 interface

Meaning: an interaction contract (API / integration object).

Mandatory attrs:

name

externalId

Allowed attrs:

category

protocol

4.3 system (optional)

A neutral container, if provided by the source.

Mandatory attrs:

name

externalId

❗ In MVP, other Node.kind values (capability, process, orgUnit, etc.) are forbidden.

5) MVP edge ontology (Edge.kind)

5.1 Allowed Edge.kind values (MVP)

depends_on  
application → application

exposes_interface  
application → interface

consumes_interface  
application → interface

connects_to (optional)  
interface → interface

5.2 Edge attributes

Mandatory attrs:

externalId

relationType (original type from the source)

Allowed attrs:

strength

The direction of a relationship is defined by the edge itself.
The field direction is forbidden.

6) Identity and ID strategy

6.1 Base rule

The id MUST be stable relative to the source.

Recommended format:

<kind>:<source>:<workspace>:<externalId>

6.2 Fallback (edge case)

If externalId is missing:

<kind>:<source>:<workspace>:hash(<stableKeyFields>)

stableKeyFields MUST be:

explicitly listed,

immutable,

documented.

7) Provenance (mandatory)

Each Node and Edge contains:

sourceSystem

sourceObjectType

sourceObjectId

sourcePath (optional)

ingestedAt

connectorVersion

8) Relation to simulation

CanonicalGraph:

does not contain scenarios,

does not contain states,

does not contain logic.

It is used exclusively by reference from SimulationInput.graphRef
(see E_simulation-contract.md).
