import type { Adjacency } from "./adjacency";

function maxDepthFrom(
  start: string,
  nextFn: (id: string) => readonly string[],
  onPath: Set<string>
): number {
  onPath.add(start);
  let best = 0;

  for (const n of nextFn(start)) {
    if (onPath.has(n)) continue; // cycle-safe: simple path
    const d = 1 + maxDepthFrom(n, nextFn, onPath);
    if (d > best) best = d;
  }

  onPath.delete(start);
  return best;
}

export function dependencyDepth(adj: Adjacency, nodeId: string): { out: number; in: number } {
  const out = maxDepthFrom(nodeId, (id) => adj.out[id] ?? [], new Set<string>());
  const _in = maxDepthFrom(nodeId, (id) => adj.in[id] ?? [], new Set<string>());
  return { out, in: _in };
}
