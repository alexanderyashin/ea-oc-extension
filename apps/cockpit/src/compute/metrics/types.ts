export interface MetricSet {
  version: "metrics-mvp@1";
  nodeMetrics: NodeMetric[];
}

export interface NodeMetric {
  nodeId: string;

  // M1
  m1_dependencyDepth: { out: number; in: number };

  // M2
  m2_blastRadius: { out: number; in: number };

  // M3
  m3_cascadeSusceptibility: { inReach: number; inDegree: number };

  // M4
  m4_structuralCriticality: { vector: number[]; note: "lex" };

  // M5 (optional, only if sufficient numeric fields exist in SimResult)
  m5_thresholdProximity?: { stopMargin?: number; warnMargin?: number };
}
