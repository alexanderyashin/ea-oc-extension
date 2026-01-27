TITLE: D. Determinism
PURPOSE: Formal rules: canonical sorting / serialization / hashing
AUDIENCE: Core dev, Connector dev, Audit
LANGUAGE: EN
EVIDENCE_PROFILE: Design-spec (deterministic rules)
ROLE: Determinism contract
STATUS: ACTIVE

D. Determinism (backend contract)

Principle

The same input snapshot (RawSnapshot), given the same adapter, normalizer, and engine version,
MUST produce bit-for-bit identical CanonicalGraph, SimulationResult, and identical hashes.

Canonical order (normalization)

2.1 Nodes

Sort nodes[] by:

id (lexicographically, Unicode code point order)

if equal — FORBIDDEN (IDs MUST be unique)

2.2 Edges

Sort edges[] by the tuple:

source

target

kind

id

If id values are equal — FORBIDDEN (edge IDs MUST be unique).

Canonical JSON serialization (canonicalJson)

3.1 Definition of canonicalJson

canonicalJson is a JSON string obtained by:

parsing the JSON into an object

serializing it back into a single-line JSON string using compressed mode

This is the normative MVP procedure, because this exact process is used to compute reference fixture hashes.

3.2 Serialization requirements

key order: lexicographic (as produced by the serializer; for MVP this is the source of truth)

dates: ISO8601 strings only (YYYY-MM-DDTHH:mm:ssZ)

runtime-dependent fields are forbidden (random IDs, UI coordinates, now-timestamps, etc.)

numbers: the implementation MUST ensure a stable string representation if it affects hashing

3.3 Prohibition of pretty JSON

In MVP, canonicalJson is ALWAYS computed in compressed, single-line form.
Any formatted or pretty JSON variants are not canonical and MUST NOT be hashed.

Hashing (sha256)

4.1 Algorithm

hash algorithm: sha256

string encoding before hashing: UTF-8

4.2 Formulas

contentHash = sha256(canonicalGraphJson)

resultHash = sha256(canonicalResultJson)

Where:

canonicalGraphJson is canonicalJson for CanonicalGraph

canonicalResultJson is canonicalJson for SimulationResult

4.3 Normative PowerShell reference (MVP)

There exists a normative PowerShell procedure used to compute canonical hashes for:

CanonicalGraph

SimulationResult

This procedure is NOT an example.
It is the normative reference for MVP, and fixture hashes MUST match exactly.

Normalization of unknown or missing values

missing external ID in a source object
→ object is dropped and a record is written to errors[] (RawSnapshot) and or ledger[] (SimulationResult)

missing name while an external ID is present
→ name is set to "<unknown>" and a record is written to errors[] or ledger[]

Prohibitions (non-negotiable)

runtime counters or randomness MUST NOT be used to generate IDs

unstable fields MUST NOT be included in attrs (for example timestamp "now")

sorting or serialization rules MUST NOT be changed without:

updating this document

recomputing fixture hashes

recording the change via a schema or contract version bump
in the corresponding documents A and E