import { clamp01, byStableEdge } from "./determinism";
import type { NodeState } from "./types";

export type CascadeInputs = {
  nodeIds: string[];
  edges: Array<{ source: string; target: string; id?: string }>;
  // current states/scores
  states: Record<string, NodeState>;
  scores: Record<string, number>;
  // how many steps to propagate
  steps: number;
};

export type CascadeStep = {
  step: number;
  delta: Record<string, number>; // per node score delta applied at this step
};

function isHighStress(s: NodeState): boolean {
  return s === "RED" || s === "STOP";
}

export function propagateCascades(input: CascadeInputs): CascadeStep[] {
  const edges = [...input.edges].sort(byStableEdge);

  const steps: CascadeStep[] = [];
  for (let t = 1; t <= input.steps; t++) {
    const delta: Record<string, number> = {};
    for (const id of input.nodeIds) delta[id] = 0;

    // Directed propagation: source -> target
    // Rule: if source is RED/STOP, target accumulates stress.
    // Fixed constants (demo-safe, deterministic, no tuning loop).
    for (const e of edges) {
      const src = e.source;
      const dst = e.target;
      const srcState = input.states[src];
      if (!srcState) continue;
      if (!isHighStress(srcState)) continue;

      // stress increment
      delta[dst] = clamp01((delta[dst] ?? 0) + 0.12);
    }

    // Apply deltas deterministically
    for (const id of input.nodeIds) {
      const next = clamp01((input.scores[id] ?? 0) + (delta[id] ?? 0));
      input.scores[id] = next;
    }

    steps.push({ step: t, delta });
  }

  return steps;
}
