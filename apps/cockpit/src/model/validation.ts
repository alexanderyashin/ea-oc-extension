/* apps/cockpit/src/model/validation.ts
   Pure validation helpers for canonical Graph + attached Profile.
*/

import type { Edge, Graph, JsonValue, Node } from "./canonical";
import type { Profile, Severity } from "./emap0.profile";
import {
  edgeKindAllowed,
  getEdgeConstraint,
  getNodeConstraint,
  isAttributeType,
  nodeKindAllowed,
} from "./emap0.profile";
import { indexNodes } from "./canonical";

export interface ValidationIssue {
  readonly severity: Severity;
  readonly code: string;
  readonly message: string;

  /** JSON-pointer-ish path, e.g. "/nodes/2/attrs/name" */
  readonly path: string;
}

function issue(severity: Severity, code: string, message: string, path: string): ValidationIssue {
  return { severity, code, message, path };
}

function isNonEmptyString(v: unknown): v is string {
  return typeof v === "string" && v.trim().length > 0;
}

function collectDuplicateIds<T extends { readonly id: unknown }>(
  items: readonly T[],
  pathPrefix: string,
  idName: "nodeId" | "edgeId",
): ValidationIssue[] {
  const seen = new Set<string>();
  const issues: ValidationIssue[] = [];
  for (let i = 0; i < items.length; i++) {
    const raw = items[i]?.id;
    const id = typeof raw === "string" ? raw : String(raw);
    if (!isNonEmptyString(id)) {
      issues.push(
        issue(
          "ERROR",
          `INVALID_${idName.toUpperCase()}`,
          `Invalid ${idName}`,
          `${pathPrefix}/${i}/id`,
        ),
      );
      continue;
    }
    if (seen.has(id)) {
      issues.push(
        issue(
          "ERROR",
          `DUP_${idName.toUpperCase()}`,
          `Duplicate ${idName}: ${id}`,
          `${pathPrefix}/${i}/id`,
        ),
      );
    } else {
      seen.add(id);
    }
  }
  return issues;
}

function validateRequiredAttrs(
  required: readonly { key: string; type: string }[] | undefined,
  attrs: Readonly<Record<string, unknown>>,
  basePath: string,
): ValidationIssue[] {
  if (!required || required.length === 0) return [];
  const out: ValidationIssue[] = [];
  for (const r of required) {
    const val = attrs[r.key];
    const ok =
      r.type === "string"
        ? typeof val === "string" && val.trim().length > 0
        : r.type === "number"
          ? typeof val === "number" && Number.isFinite(val)
          : r.type === "boolean"
            ? typeof val === "boolean"
            : true; // "json"
    if (!ok) {
      out.push(
        issue(
          "ERROR",
          "MISSING_OR_BAD_ATTR",
          `Missing or invalid required attribute '${r.key}' (${r.type})`,
          `${basePath}/attrs/${escapeJsonPointer(r.key)}`,
        ),
      );
    }
  }
  return out;
}

function escapeJsonPointer(s: string): string {
  return s.replace(/~/g, "~0").replace(/\//g, "~1");
}

export function validateNode(node: Node, profile: Profile, idx: number): ValidationIssue[] {
  const path = `/nodes/${idx}`;
  const issues: ValidationIssue[] = [];

  if (!isNonEmptyString(node.id)) {
    issues.push(issue("ERROR", "INVALID_NODE_ID", "Node id must be a non-empty string", `${path}/id`));
  }
  if (!isNonEmptyString(node.kind)) {
    issues.push(issue("ERROR", "INVALID_NODE_KIND", "Node kind must be a non-empty string", `${path}/kind`));
  } else if (!nodeKindAllowed(profile, node)) {
    issues.push(issue("ERROR", "NODE_KIND_NOT_ALLOWED", `Node kind not allowed: '${node.kind}'`, `${path}/kind`));
  }

  const c = getNodeConstraint(profile, node.kind);
  if (c?.requiredAttrs) {
    issues.push(...validateRequiredAttrs(c.requiredAttrs, node.attrs as Record<string, unknown>, path));
  }

  return issues;
}

export function validateEdge(edge: Edge, profile: Profile, idx: number, nodeIds: Set<string>): ValidationIssue[] {
  const path = `/edges/${idx}`;
  const issues: ValidationIssue[] = [];

  if (!isNonEmptyString(edge.id)) {
    issues.push(issue("ERROR", "INVALID_EDGE_ID", "Edge id must be a non-empty string", `${path}/id`));
  }
  if (!isNonEmptyString(edge.kind)) {
    issues.push(issue("ERROR", "INVALID_EDGE_KIND", "Edge kind must be a non-empty string", `${path}/kind`));
  } else if (!edgeKindAllowed(profile, edge)) {
    issues.push(issue("ERROR", "EDGE_KIND_NOT_ALLOWED", `Edge kind not allowed: '${edge.kind}'`, `${path}/kind`));
  }

  const from = edge.from as unknown as string;
  const to = edge.to as unknown as string;

  if (!isNonEmptyString(from)) {
    issues.push(issue("ERROR", "INVALID_EDGE_FROM", "Edge.from must be a non-empty NodeId", `${path}/from`));
  } else if (!nodeIds.has(from)) {
    issues.push(issue("ERROR", "MISSING_FROM_NODE", `Edge.from references missing node: '${from}'`, `${path}/from`));
  }

  if (!isNonEmptyString(to)) {
    issues.push(issue("ERROR", "INVALID_EDGE_TO", "Edge.to must be a non-empty NodeId", `${path}/to`));
  } else if (!nodeIds.has(to)) {
    issues.push(issue("ERROR", "MISSING_TO_NODE", `Edge.to references missing node: '${to}'`, `${path}/to`));
  }

  const c = getEdgeConstraint(profile, edge.kind);
  if (c) {
    if (from === to && c.allowSelfLoop === false) {
      issues.push(issue("ERROR", "SELF_LOOP_NOT_ALLOWED", "Self-loop is not allowed for this edge kind", path));
    }

    if (c.requiredAttrs) {
      issues.push(...validateRequiredAttrs(c.requiredAttrs, edge.attrs as Record<string, unknown>, path));
    }
  }

  return issues;
}

export function validateGraph(graph: Graph, profile: Profile): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  if (graph.schemaVersion !== "v0") {
    issues.push(
      issue("ERROR", "UNSUPPORTED_SCHEMA", `Unsupported schemaVersion: '${String(graph.schemaVersion)}'`, `/schemaVersion`),
    );
  }
  if (!isNonEmptyString(graph.profileId)) {
    issues.push(issue("ERROR", "MISSING_PROFILE_ID", "profileId must be a non-empty string", `/profileId`));
  }

  issues.push(...collectDuplicateIds(graph.nodes, "/nodes", "nodeId"));
  issues.push(...collectDuplicateIds(graph.edges, "/edges", "edgeId"));

  for (let i = 0; i < graph.nodes.length; i++) {
    issues.push(...validateNode(graph.nodes[i], profile, i));
  }

  const nodeIds = new Set<string>(graph.nodes.map((n) => n.id as unknown as string));

  for (let i = 0; i < graph.edges.length; i++) {
    issues.push(...validateEdge(graph.edges[i], profile, i, nodeIds));
  }

  const nodeIndex = indexNodes(graph.nodes);
  for (let i = 0; i < graph.edges.length; i++) {
    const e = graph.edges[i];
    const c = getEdgeConstraint(profile, e.kind);
    if (!c) continue;

    const fromId = e.from as unknown as string;
    const toId = e.to as unknown as string;

    const fromNode = nodeIndex[fromId];
    const toNode = nodeIndex[toId];
    if (!fromNode || !toNode) continue;

    if (c.fromKinds && c.fromKinds.length > 0 && !c.fromKinds.includes(fromNode.kind)) {
      issues.push(
        issue(
          "ERROR",
          "EDGE_FROM_KIND_NOT_ALLOWED",
          `Edge '${e.kind}' from-kind '${fromNode.kind}' not allowed`,
          `/edges/${i}/from`,
        ),
      );
    }
    if (c.toKinds && c.toKinds.length > 0 && !c.toKinds.includes(toNode.kind)) {
      issues.push(
        issue(
          "ERROR",
          "EDGE_TO_KIND_NOT_ALLOWED",
          `Edge '${e.kind}' to-kind '${toNode.kind}' not allowed`,
          `/edges/${i}/to`,
        ),
      );
    }
  }

  return issues;
}

export function isGraphValid(graph: Graph, profile: Profile): boolean {
  return validateGraph(graph, profile).every((x) => x.severity !== "ERROR");
}

export function collectNodeIds(nodes: readonly Node[]): Set<string> {
  return new Set<string>(nodes.map((n) => n.id as unknown as string));
}

/** Optional helper used by future adapters (pure). */
export function assertAttributeType(
  value: JsonValue | undefined,
  t: "string" | "number" | "boolean" | "json",
): boolean {
  return isAttributeType(value, t);
}
