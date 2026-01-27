import type { Adjacency } from "./adjacency";
import { blastRadius } from "./m2_blastRadius";

export function cascadeSusceptibility(adj: Adjacency, nodeId: string): { inReach: number; inDegree: number } {
  const inDegree = (adj.in[nodeId] ?? []).length;
  const inReach = blastRadius(adj, nodeId).in;
  return { inReach, inDegree };
}
