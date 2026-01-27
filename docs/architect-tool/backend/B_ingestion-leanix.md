TITLE: B. Ingestion — SAP LeanIX (MVP)
PURPOSE: Define the MVP adapter LeanIX to CanonicalGraph and the RawSnapshot contract
AUDIENCE: Connector dev, Core dev
LANGUAGE: EN
EVIDENCE_PROFILE: Doc-driven mapping (LeanIX concepts to CanonicalGraph)
ROLE: LeanIX ingestion spec
STATUS: ACTIVE

B. Ingestion — SAP LeanIX (MVP)

Boundary and purpose of ingestion (MVP)

Ingestion performs only:

extraction of facts from the source,

normalization into RawSnapshot,

transformation RawSnapshot to CanonicalGraph (see A),

recording of errors into errors[] (without any smart conclusions).

Ingestion does NOT perform:

recommendations, interpretations, or BI of any kind,

write-back operations to LeanIX (update, patch, import) in MVP,

any UI fields or representations,

any enrichments from external reference data.

RawSnapshot contract (pre-normalization)

RawSnapshot is a reproducibility artifact: what exactly was observed in LeanIX.
It MUST be sufficient to reconstruct the same CanonicalGraph with the same connector version.

1.1 Structure

RawSnapshot consists of:

meta

sourceSystem: leanix

workspace: string

capturedAt: ISO8601

connectorVersion: semver

queries: list of strings

factsheets: list of objects with minimal fields

relations: list of objects with minimal fields

errors: list of objects with code, message, refs

rawHash: sha256 hash

1.2 Minimal fields (MVP)

factsheets minimal fields:

id (externalId in LeanIX)

type (for example Application or Interface)

name (may be missing, see unknown policy)

relations minimal fields:

id (externalId of relation)

type (string, original relation type)

from (factsheet id)

to (factsheet id)

1.3 rawHash (MVP rule)

rawHash is the hash of canonically serialized RawSnapshot after:

removal of explicitly unstable fields (if provided by the source),

sorting of factsheets and relations arrays by a stable key (id),

stable JSON serialization with lexicographic object key ordering.

rawHash is used for tracing that this is the same input.
Determinism of CanonicalGraph is separately fixed by contentHash (see A and D).

Mapping RawSnapshot to CanonicalGraph

2.1 FactSheet to Node

Application FactSheet maps to Node with kind application.

id format:
application:leanix:<workspace>:<factSheetId>

kind: application

attrs (MVP):

name from factsheet.name (if missing, set to <unknown>, see section 3.3)

externalId from factsheet.id

other fields such as lifecycle, criticality, owner, tags are included ONLY if explicitly present in raw facts, without computation

provenance:

sourceSystem: leanix

sourceObjectType: FactSheet

sourceObjectId: factSheetId

ingestedAt: meta.capturedAt

connectorVersion: meta.connectorVersion

Interface FactSheet maps to Node with kind interface.

id format:
interface:leanix:<workspace>:<factSheetId>

kind: interface

attrs (MVP):

name (or <unknown>)

externalId

category and protocol ONLY if explicitly present in raw facts, otherwise omitted

provenance: same as above (FactSheet)

In MVP, no meta-model introspection is performed.
If types or categories are not directly available, they are simply absent.

2.2 Relation to Edge

General Edge form:

id format:
edge:<kind>:leanix:<workspace>:<relationId>

kind: selected by the rules below

source and target: mapped node ids

attrs (MVP):

relationType from raw relation.type

externalId from raw relation.id

other fields ONLY if they are direct facts from the source (for example strength), without computation

provenance:

sourceSystem: leanix

sourceObjectType: Relation

sourceObjectId: relationId

ingestedAt: meta.capturedAt

connectorVersion: meta.connectorVersion

Rules for selecting kind (MVP)

No deep semantic interpretation is performed beyond MVP.
Only node types (Application or Interface) and raw relation.type are used.

Application to Application:

if both endpoints are Application, then kind equals depends_on

Application to Interface:

if from is Application and to is Interface, then kind is exposes_interface or consumes_interface ONLY if raw relation.type is unambiguously distinguishable via a predefined list (see section 2.3)

Otherwise, in case of any ambiguity:

the relation is NOT included in CanonicalGraph (MVP),

but is recorded in RawSnapshot errors[] with code RELATION_DROPPED.

2.3 Mapping table relation.type to kind (MVP)

To avoid magic, the connector MUST have an explicit mapping configuration (in code or config), for example:

dependsTypes equals list of depends, requires, etc.

exposesTypes equals list of exposes, provides, etc.

consumesTypes equals list of consumes, uses, etc.

If relation.type does not belong to any list:

rule applies: drop plus error.

In demo fixtures the following mappings are used:

depends maps to depends_on

exposes maps to exposes_interface

consumes maps to consumes_interface

Determinism and normalization (mandatory rules)

3.1 Stable IDs

IDs MUST NOT be generated using counters or randomness.
In MVP, <kind>:leanix:<workspace>:<externalId> is the only allowed approach.

3.2 Sorting

Before computing CanonicalGraph contentHash:

nodes are sorted by id

edges are sorted by source, target, kind, id

See D. Determinism.

3.3 unknown or missing policy (MVP)

missing factsheet.id
object is dropped and recorded in errors[] with code FACTSHEET_DROPPED_NO_ID

id present but name missing or empty
name is set to <unknown> and recorded in errors[] with code FACTSHEET_UNKNOWN_NAME

relation missing id or from or to
relation is dropped and recorded in errors[] with code RELATION_DROPPED_MISSING_FIELDS

relation endpoints not found in factsheets
relation is dropped and recorded in errors[] with code RELATION_DROPPED_UNKNOWN_ENDPOINT

Fixtures (demo artifacts)

MVP MUST be able to reproduce the following fixtures:

docs/architect-tool/backend/fixtures/rawsnapshot.leanix.sample.json

docs/architect-tool/backend/fixtures/canonicalgraph.sample.json

docs/architect-tool/backend/fixtures/simulationresult.sample.json

Extension points (outside MVP)

Possible extensions (not implemented in MVP, but architecturally allowed):

meta-model introspection (types, subtypes, custom relation types),

extended ontology (capability, process, org),

import and export processors and write-back,

access control and roles,

partial snapshots and diffs.