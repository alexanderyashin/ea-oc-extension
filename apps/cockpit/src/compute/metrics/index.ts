import type { SimConfig, SimResult } from "../types";
import type { MetricSet, NodeMetric } from "./types";
import { buildAdjacency, type RfEdgeLike, type RfNodeLike } from "./adjacency";
import { dependencyDepth } from "./m1_depth";
import { blastRadius } from "./m2_blastRadius";
import { cascadeSusceptibility } from "./m3_susceptibility";
import { structuralCriticalityVector } from "./m4_criticality";
import { thresholdProximity } from "./m5_threshold";
import { sortIds } from "../determinism";

export function computeMetrics(args: {
  cfg: SimConfig;
  nodes: RfNodeLike[];
  edges: RfEdgeLike[];
  selectedNodeId: string | null;
  simResult: SimResult;
}): MetricSet {
  const nodeIds = sortIds(args.nodes.map((n) => n.id));
  const adj = buildAdjacency(args.nodes, args.edges);

  const nodeMetrics: NodeMetric[] = [];
  for (const nodeId of nodeIds) {
    const m1 = dependencyDepth(adj, nodeId);
    const m2 = blastRadius(adj, nodeId);
    const m3 = cascadeSusceptibility(adj, nodeId);
    const m4 = structuralCriticalityVector({
      brOut: m2.out,
      brIn: m2.in,
      depthOut: m1.out,
      depthIn: m1.in,
      inReach: m3.inReach,
      inDegree: m3.inDegree,
    });

    const m5 = thresholdProximity(args.simResult, nodeId);

    const nm: NodeMetric = {
      nodeId,
      m1_dependencyDepth: m1,
      m2_blastRadius: m2,
      m3_cascadeSusceptibility: m3,
      m4_structuralCriticality: m4,
      ...(m5 ? { m5_thresholdProximity: m5 } : {}),
    };

    nodeMetrics.push(nm);
  }

  return {
    version: "metrics-mvp@1",
    nodeMetrics,
  };
}
