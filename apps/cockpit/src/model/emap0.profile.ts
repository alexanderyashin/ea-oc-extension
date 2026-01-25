/* apps/cockpit/src/model/emap0.profile.ts
   EMAP-0: Minimal notation/profile (v0).
   Purpose: enable drag & drop modeling now, keep adapter hooks for future ArchiMate mapping.
*/

import type { Edge, EdgeKind, JsonValue, Node, NodeKind } from "./canonical";

export type ProfileId = string;

export type Severity = "INFO" | "WARN" | "ERROR";

export interface ProfileRuleIssue {
  readonly severity: Severity;
  readonly code: string;
  readonly message: string;
}

export type AttributeType =
  | "string"
  | "number"
  | "boolean"
  | "json"; // accept any JsonValue

export interface RequiredAttribute {
  readonly key: string;
  readonly type: AttributeType;
}

/** Endpoint constraints are optional in v0; keep structure for adapter-ready evolution. */
export interface EdgeConstraint {
  readonly kind: EdgeKind;
  readonly fromKinds?: readonly NodeKind[];
  readonly toKinds?: readonly NodeKind[];
  readonly allowSelfLoop?: boolean;
  readonly requiredAttrs?: readonly RequiredAttribute[];
}

export interface NodeConstraint {
  readonly kind: NodeKind;
  readonly requiredAttrs?: readonly RequiredAttribute[];
}

/**
 * Profile definition:
 * - allowed node/edge kinds
 * - required attributes per kind
 * - optional endpoint constraints for edges
 */
export interface Profile {
  readonly id: ProfileId;
  readonly version: "v0";

  readonly allowedNodeKinds: readonly NodeKind[];
  readonly allowedEdgeKinds: readonly EdgeKind[];

  readonly nodeConstraints: readonly NodeConstraint[];
  readonly edgeConstraints: readonly EdgeConstraint[];

  /**
   * Adapter hook: future mapping target (e.g., "ArchiMate") without implementing mapping now.
   * Purely declarative; no logic in this run.
   */
  readonly compatibility?: Readonly<{
    readonly targetNotations?: readonly string[];
    readonly notes?: string;
  }>;
}

/** EMAP-0 kind vocabulary (minimal but extensible). */
export const EMAP0_NODE_KINDS = [
  "Actor",
  "System",
  "Application",
  "Capability",
  "Process",
  "DataObject",
  "External",
] as const satisfies readonly string[];

export const EMAP0_EDGE_KINDS = [
  "depends_on",
  "serves",
  "implements",
  "owns",
  "flows_to",
  "triggers",
] as const satisfies readonly string[];

export type Emap0NodeKind = (typeof EMAP0_NODE_KINDS)[number];
export type Emap0EdgeKind = (typeof EMAP0_EDGE_KINDS)[number];

/**
 * EMAP-0 required attributes:
 * - All nodes require attrs.name (string)
 * - Edges require nothing mandatory in v0, but we keep optional typed hints.
 */
const REQ_NODE_COMMON: readonly RequiredAttribute[] = [
  { key: "name", type: "string" },
];

export const EMAP0_PROFILE: Profile = {
  id: "emap0",
  version: "v0",

  allowedNodeKinds: EMAP0_NODE_KINDS,
  allowedEdgeKinds: EMAP0_EDGE_KINDS,

  nodeConstraints: EMAP0_NODE_KINDS.map((k) => ({
    kind: k,
    requiredAttrs: REQ_NODE_COMMON,
  })),

  edgeConstraints: [
    {
      kind: "depends_on",
      allowSelfLoop: false,
      // optional endpoint shaping (kept minimal)
      requiredAttrs: [{ key: "strength", type: "number" }],
    },
    { kind: "serves", allowSelfLoop: false },
    { kind: "implements", allowSelfLoop: false },
    { kind: "owns", allowSelfLoop: false },
    { kind: "flows_to", allowSelfLoop: false },
    { kind: "triggers", allowSelfLoop: false },
  ],

  compatibility: {
    targetNotations: ["ArchiMate"],
    notes:
      "EMAP-0 is a minimal cockpit profile. Future adapters may map node/edge kinds to ArchiMate elements/relationships.",
  },
};

/** Tiny helpers used by validation (pure). */
export function getNodeConstraint(profile: Profile, kind: NodeKind): NodeConstraint | undefined {
  return profile.nodeConstraints.find((c) => c.kind === kind);
}

export function getEdgeConstraint(profile: Profile, kind: EdgeKind): EdgeConstraint | undefined {
  return profile.edgeConstraints.find((c) => c.kind === kind);
}

/** Attribute runtime type-check (strict, pure) */
export function isAttributeType(value: JsonValue | undefined, t: AttributeType): boolean {
  if (value === undefined) return false;
  switch (t) {
    case "string":
      return typeof value === "string";
    case "number":
      return typeof value === "number" && Number.isFinite(value);
    case "boolean":
      return typeof value === "boolean";
    case "json":
      return true;
    default: {
      // exhaustive guard
      const _exhaustive: never = t;
      return _exhaustive;
    }
  }
}

export function nodeKindAllowed(profile: Profile, node: Node): boolean {
  return profile.allowedNodeKinds.includes(node.kind);
}

export function edgeKindAllowed(profile: Profile, edge: Edge): boolean {
  return profile.allowedEdgeKinds.includes(edge.kind);
}
