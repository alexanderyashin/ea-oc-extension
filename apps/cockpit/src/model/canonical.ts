/* apps/cockpit/src/model/canonical.ts
   Canonical internal graph model for the cockpit (UI-agnostic, simulation-agnostic).
   Goals: strict typing, profile-attachable, adapter-ready (future ArchiMate mapping).
*/

export type Brand<K, T extends string> = K & { readonly __brand: T };

export type NodeId = Brand<string, "NodeId">;
export type EdgeId = Brand<string, "EdgeId">;

export function asNodeId(value: string): NodeId {
  return value as NodeId;
}
export function asEdgeId(value: string): EdgeId {
  return value as EdgeId;
}

export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonObject | JsonArray;
export type JsonObject = { [k: string]: JsonValue };
export type JsonArray = JsonValue[];

export type Attributes = Readonly<Record<string, JsonValue>>;

export type NodeKind = string;
export type EdgeKind = string;

/** Minimal spatial hint for drag & drop. UI can ignore or override. */
export interface Position2D {
  readonly x: number;
  readonly y: number;
}

export interface Node {
  readonly id: NodeId;
  readonly kind: NodeKind;

  /** Optional human label (UI-friendly). Profile may require a specific attribute like `name`. */
  readonly label?: string;

  /** Free-form attributes; validated against an active profile. */
  readonly attrs: Attributes;

  /** Optional, purely presentational. */
  readonly pos?: Position2D;
}

export interface Edge {
  readonly id: EdgeId;
  readonly kind: EdgeKind;

  /** Directed edge: from -> to */
  readonly from: NodeId;
  readonly to: NodeId;

  readonly attrs: Attributes;
}

export interface GraphMeta {
  /** Used for display only (e.g. "Demo Scenario A"). */
  readonly title?: string;
  readonly description?: string;

  /** Optional tags; profile adapters may map these later. */
  readonly tags?: readonly string[];
}

export interface Graph {
  /** Canonical schema version for internal evolution */
  readonly schemaVersion: "v0";

  /** Active profile id used for validation (e.g. "emap0"). */
  readonly profileId: string;

  /** Graph payload */
  readonly nodes: readonly Node[];
  readonly edges: readonly Edge[];

  /** Optional metadata */
  readonly meta?: GraphMeta;
}

/** Utility: stable lookup maps (pure, derived) */
export type NodeIndex = Readonly<Record<string, Node>>;
export type EdgeIndex = Readonly<Record<string, Edge>>;

export function indexNodes(nodes: readonly Node[]): NodeIndex {
  const m: Record<string, Node> = Object.create(null) as Record<string, Node>;
  for (const n of nodes) m[n.id as unknown as string] = n;
  return m;
}

export function indexEdges(edges: readonly Edge[]): EdgeIndex {
  const m: Record<string, Edge> = Object.create(null) as Record<string, Edge>;
  for (const e of edges) m[e.id as unknown as string] = e;
  return m;
}
