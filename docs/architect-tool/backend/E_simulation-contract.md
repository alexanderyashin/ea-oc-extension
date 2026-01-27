TITLE: E. Simulation Contract (MVP)
PURPOSE: Formally define simulation input and output and explicit prohibitions (no BI, no recommendations)
AUDIENCE: Engine dev, Core dev, Audit
LANGUAGE: EN
EVIDENCE_PROFILE: Design-spec (I/O contract and invariants)
ROLE: Simulation interface contract
STATUS: ACTIVE

E. Simulation Contract (MVP)

Principle

The simulation accepts canonical facts (CanonicalGraph) plus scenario parameters
and returns a formal result (states plus ledger plus stop) without recommendations.

The simulation:

is not BI or a dashboard

is not an advisor

does not optimize

does not generate management actions

Contract objects

1.1 SimulationInput

SimulationInput is the only allowed input to the engine.

Composition (MVP):

meta (mandatory)

graphRef (mandatory, reference to CanonicalGraph)

scenario (mandatory)

options (optional)

Important: in MVP the graph is NOT passed inline.
The engine MUST accept a graphRef and resolve it to a CanonicalGraph
(in demo and fixtures via file path).
Inline graph transfer is allowed only later (Full Product) as a separate contract extension.

1.1.1 meta (mandatory)

schemaVersion (for example SI-0.1)

capturedAt (ISO8601; time when the input was formed)

1.1.2 graphRef (mandatory)

graphRef fixes which exact graph is used.

Fields:

path (string; relative path to the CanonicalGraph file, for example ./canonicalgraph.sample.json)

snapshotId (value from CanonicalGraph.meta.snapshotId)

contentHash (value from CanonicalGraph.meta.determinism.contentHash)

Invariants:

contentHash is mandatory and MUST match CanonicalGraph.meta.determinism.contentHash

contentHash is computed as sha256(canonicalGraphJson) according to D_determinism.md

1.1.3 scenario (mandatory)

scenario defines what is being simulated but contains no recommendations.

MVP fields:

shockType (enum)

intensity (number or enum)

targetSelector (enum: all or selected)

targets (string array; mandatory when targetSelector is selected)

seed (string or number; fixes any pseudo-randomness if present)

Recommended MVP shockType set:

capacity_drop

node_failure

dependency_disruption

Important: shockType values and semantics belong to the engine;
the contract only fixes the shape.

1.1.4 options (optional)

strictDeterminism (boolean, default true)

unknownHandling (enum: drop or keep-as-unknown; default drop)

maxLedgerEntries (number; optional guard)

stopOnThreshold (boolean, default true)

1.2 SimulationResult

SimulationResult is the only allowed output of the engine.

Composition:

meta

stop

nodeStates

edgeStates (optional)

ledger array

resultHash

1.2.1 meta (mandatory)

schemaVersion (for example SR-0.1)

producedAt (ISO8601)

graphRef

snapshotId

contentHash

scenarioRef

shockType

intensity

targetSelector

seed (if used)

determinism

hashAlgo (sha256)

resultHash (duplicates the top-level resultHash for audit convenience)

1.2.2 stop (mandatory)

stop: boolean

Meaning:

stop = false — simulation finished without a LOCK or STOP condition

stop = true — STOP or LOCK has been reached (terminal state of the demonstrator)

STOP or LOCK:

does NOT mean what to do

means that within the model a threshold has been reached where further evolution is forbidden or undefined

1.2.3 nodeStates (mandatory)

nodeStates is a map from nodeId to NodeState

NodeState (MVP enum):

OK

WARN

FAIL

STOP (optional, if the engine distinguishes FAIL and STOP)

Requirements:

nodeStates keys MUST be a subset of graph.nodes[].id

key order during result serialization MUST be deterministic (lexicographic by nodeId)

1.2.4 edgeStates (optional)

edgeStates is a map from edgeId to EdgeState (if the engine evaluates edges)

EdgeState (MVP enum):

OK

WARN

FAIL

1.2.5 ledger (mandatory)

ledger is a list of simulation facts.
It is a logbook, not an interpretation.

Entry format (MVP):

ts (ISO8601)

code (string; machine-readable event code)

message (string; human-readable fact description)

refs (string array; references to entities, snapshots, or threshold codes)

Ledger prohibitions:

recommendations are forbidden (for example do X, increase Y)

KPIs or work plans are forbidden

management advice of any kind is forbidden

Allowed content:

recording of events

recording of thresholds or conditions

recording of causal steps in terms of the model

1.2.6 resultHash (mandatory)

resultHash equals sha256(canonicalResultJson)

canonicalResultJson:

deterministically serialized result (see D_determinism.md)

without unstable fields

with fixed key ordering

Determinism and reproducibility

MVP requirement:

the same CanonicalGraph (by contentHash)

the same scenario (including seed)

the same engine version

must produce bit-for-bit identical SimulationResult and resultHash.

Any deviation is considered a determinism defect.

unknown or missing data policy

The simulation MUST NOT infer missing data.

If input is incomplete:

options.unknownHandling is applied:

drop: object or relation is ignored and a fact is written to the ledger

keep-as-unknown: object remains, but states and logic must be strictly defined (not recommended in MVP)

Explicit prohibitions (non-negotiable)

The simulation and its result MUST NOT:

issue recommendations, priorities, or action plans

compute maturity scores or target KPIs

provide portfolio optimization

propose org structure changes, hiring, or budgeting

export reports (PDF or PPT) as part of the engine contract

Only the following is allowed:

recording structure

recording thresholds

recording STOP or LOCK

recording a factual ledger

Relation to fixtures (MVP)

In the repository, fixtures are normative examples:

fixtures/simulationinput.sample.json — SimulationInput example (uses graphRef in MVP)

fixtures/simulationresult.sample.json — SimulationResult example

fixtures/canonicalgraph.sample.json — CanonicalGraph example

Any change to the contract shape requires synchronized updates of the fixtures.