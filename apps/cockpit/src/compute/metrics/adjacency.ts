import { sortIds } from "../determinism";

export type RfNodeLike = { id: string };
export type RfEdgeLike = { source: string; target: string };

export type Adjacency = {
  nodeIds: string[];
  out: Record<string, string[]>;
  in: Record<string, string[]>;
};

export function buildAdjacency(nodes: RfNodeLike[], edges: RfEdgeLike[]): Adjacency {
  const nodeIds = sortIds(nodes.map((n) => n.id));

  const out: Record<string, string[]> = {};
  const _in: Record<string, string[]> = {};
  for (const id of nodeIds) {
    out[id] = [];
    _in[id] = [];
  }

  // Deterministic edge ordering: (source, target)
  const sortedEdges = edges
    .map((e) => ({ source: e.source, target: e.target }))
    .sort((a, b) => {
      if (a.source < b.source) return -1;
      if (a.source > b.source) return 1;
      if (a.target < b.target) return -1;
      if (a.target > b.target) return 1;
      return 0;
    });

  for (const e of sortedEdges) {
    if (!out[e.source] || !_in[e.target]) continue; // ignore edges to/from unknown nodes
    out[e.source].push(e.target);
    _in[e.target].push(e.source);
  }

  // Sort adjacency lists deterministically and de-dup
  for (const id of nodeIds) {
    out[id] = sortIds(Array.from(new Set(out[id])));
    _in[id] = sortIds(Array.from(new Set(_in[id])));
  }

  return { nodeIds, out, in: _in };
}
