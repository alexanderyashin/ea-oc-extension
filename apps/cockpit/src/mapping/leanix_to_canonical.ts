// apps/cockpit/src/mapping/leanix_to_canonical.ts
import type { JsonValue } from "../model/canonical";
import type { LeanixSnapshot } from "../import/leanix/leanix.types";

export type ImportedCanonicalGraphLike = {
  nodes?: Array<{
    id: string;
    kind: string;
    attrs?: Record<string, JsonValue>;
    pos?: { x?: number; y?: number };
  }>;
  edges?: Array<{
    id: string;
    from: string;
    to: string;
    kind: string;
    attrs?: Record<string, JsonValue>;
  }>;
};

type NodeKind = "APP" | "ITC" | "BC" | "PRV" | "DO";

function stableSortById<T extends { id: string }>(xs: T[]): T[] {
  return [...xs].sort((a, b) => String(a.id).localeCompare(String(b.id)));
}

function nodeId(kind: NodeKind, sourceId: string): string {
  return `${kind}:${sourceId}`;
}

function edgeId(edgeKind: string, from: string, to: string): string {
  return `${edgeKind}:${from}->${to}`;
}

function layoutPos(index: number): { x: number; y: number } {
  // deterministic simple grid layout (no randomness)
  const col = index % 4;
  const row = Math.floor(index / 4);
  return { x: 80 + col * 260, y: 80 + row * 140 };
}

export function mapLeanixToCanonical(snapshot: LeanixSnapshot): ImportedCanonicalGraphLike {
  const nodes: ImportedCanonicalGraphLike["nodes"] = [];
  const edges: ImportedCanonicalGraphLike["edges"] = [];

  const addNodes = (kind: NodeKind, rows: Array<{ id: string; name: string; raw: Record<string, string> }>) => {
    const sorted = stableSortById(rows);
    for (const r of sorted) {
      const id = nodeId(kind, r.id);
      nodes.push({
        id,
        kind,
        attrs: {
          name: r.name,
          sourceId: r.id,
          sourceKind: "leanix_csv",
          // keep a small raw subset only (facts), deterministic keys
          raw: r.raw as unknown as JsonValue,
        },
      });
    }
  };

  addNodes("APP", snapshot.factSheets.applications);
  addNodes("ITC", snapshot.factSheets.it_components);
  addNodes("BC", snapshot.factSheets.business_capabilities);
  addNodes("PRV", snapshot.factSheets.providers);
  addNodes("DO", snapshot.factSheets.data_objects);

  // deterministic positions by final sorted node id
  nodes.sort((a, b) => String(a.id).localeCompare(String(b.id)));
  nodes.forEach((n, idx) => {
    n.pos = layoutPos(idx);
  });

  const relToEdgeKind: Record<string, string> = {
    app_to_capability: "supports",
    app_to_it_component: "uses",
    app_to_provider: "depends_on",
    app_to_data_object: "reads_writes",
  };

  // Relations: from APP -> target kind
  const rels = [
    ["app_to_capability", "BC"] as const,
    ["app_to_it_component", "ITC"] as const,
    ["app_to_provider", "PRV"] as const,
    ["app_to_data_object", "DO"] as const,
  ];

  for (const [relKind, tgtKind] of rels) {
    const edgeKind = relToEdgeKind[relKind];
    const rows = [...snapshot.relations[relKind]].sort((a, b) => {
      const ka = `${a.fromId}->${a.toId}`;
      const kb = `${b.fromId}->${b.toId}`;
      return ka.localeCompare(kb);
    });

    for (const r of rows) {
      const from = nodeId("APP", r.fromId);
      const to = nodeId(tgtKind, r.toId);

      edges.push({
        id: edgeId(edgeKind, from, to),
        from,
        to,
        kind: edgeKind,
        attrs: {
          sourceKind: "leanix_csv",
          raw: r.raw as unknown as JsonValue,
        },
      });
    }
  }

  // stable edge order
  edges.sort((a, b) => String(a.id).localeCompare(String(b.id)));

  return { nodes, edges };
}
