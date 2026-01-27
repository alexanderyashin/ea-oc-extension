import type { Adjacency } from "./adjacency";

function reachableCount(start: string, nextFn: (id: string) => readonly string[]): number {
  const visited = new Set<string>();
  const q: string[] = [];

  visited.add(start);
  q.push(start);

  while (q.length) {
    const cur = q.shift() as string;
    for (const n of nextFn(cur)) {
      if (visited.has(n)) continue;
      visited.add(n);
      q.push(n);
    }
  }

  // exclude start itself
  return Math.max(0, visited.size - 1);
}

export function blastRadius(adj: Adjacency, nodeId: string): { out: number; in: number } {
  const out = reachableCount(nodeId, (id) => adj.out[id] ?? []);
  const _in = reachableCount(nodeId, (id) => adj.in[id] ?? []);
  return { out, in: _in };
}
