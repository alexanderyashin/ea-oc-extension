import type { SimConfig, SimResult, NodeState, LedgerEvent } from "./types";
import { nodeLabelFromAttrs, sortIds, isSystemKind, clamp01 } from "./determinism";
import { applyShockBaseScore } from "./shock";
import { stateFromScore, isWorse, globalStopFromStates } from "./thresholds";
import { propagateCascades } from "./cascade";

type RfNodeLike = {
  id: string;
  data?: { kind?: string; attrs?: any };
};

type RfEdgeLike = {
  id?: string;
  source: string;
  target: string;
};

function pickTargetNodeIds(cfg: SimConfig, nodes: RfNodeLike[], selectedNodeId: string | null): string[] {
  const all = nodes.map((n) => n.id);
  if (cfg.scope === "selected") {
    if (!selectedNodeId) return [];
    return all.includes(selectedNodeId) ? [selectedNodeId] : [];
  }

  // all_systems
  const systems = nodes.filter((n) => isSystemKind(n.data?.kind)).map((n) => n.id);
  if (systems.length > 0) return systems;

  // fallback: all nodes
  return all;
}

export function simulateShock(
  cfg: SimConfig,
  nodes: RfNodeLike[],
  edges: RfEdgeLike[],
  selectedNodeId: string | null
): SimResult {
  const ledger: LedgerEvent[] = [];
  const nodeIds = sortIds(nodes.map((n) => n.id));

  const nodeLabel: Record<string, string> = {};
  for (const n of nodes) {
    nodeLabel[n.id] = nodeLabelFromAttrs(n.data?.attrs, n.id);
  }

  const targetIds = sortIds(pickTargetNodeIds(cfg, nodes, selectedNodeId));

  if (targetIds.length === 0) {
    ledger.push({ type: "info", step: 0, message: "No target nodes (scope=selected but nothing selected)." });
    const states0: Record<string, NodeState> = {};
    const scores0: Record<string, number> = {};
    for (const id of nodeIds) {
      states0[id] = "OK";
      scores0[id] = 0;
    }
    return { nodeStates: states0, nodeScores: scores0, ledger, stop: false };
  }

  // Initial scores/states
  const scores: Record<string, number> = {};
  const states: Record<string, NodeState> = {};
  for (const id of nodeIds) {
    scores[id] = 0;
    states[id] = "OK";
  }

  // Step 0: apply base shock to target nodes
  const base = applyShockBaseScore(cfg);
  for (const id of targetIds) {
    scores[id] = clamp01(scores[id] + base);
  }

  // Record initial threshold crossings (step 0)
  for (const id of nodeIds) {
    const prev: NodeState = "OK";
    const next = stateFromScore(scores[id]);
    states[id] = next;
    if (isWorse(next, prev)) {
      ledger.push({
        type: "threshold_crossed",
        step: 0,
        nodeId: id,
        nodeLabel: nodeLabel[id],
        threshold: next,
        prev,
        scorePrev: 0,
        scoreNext: scores[id],
      });
    }
  }

  // Cascade steps
  const cascadeSteps = 5;

  // We want ledger entries to be factual about score deltas.
  // So we snapshot scores before cascade, and per step.
  const scorePrevByStep: Record<string, number>[] = [];
  scorePrevByStep[0] = { ...scores };

  propagateCascades({
    nodeIds,
    edges: edges.map((e) => ({ source: e.source, target: e.target, id: e.id })),
    states,
    scores,
    steps: cascadeSteps,
  });

  // Re-evaluate states after each step deterministically by re-running stateFromScore on updated scores.
  // We emit ledger events only when state worsens, with scorePrev/scoreNext.
  for (let t = 1; t <= cascadeSteps; t++) {
    // snapshot "prev" scores for this step based on last snapshot
    const prevScores = scorePrevByStep[t - 1] ?? { ...scores };
    const nextScores = { ...scores };
    scorePrevByStep[t] = nextScores;

    for (const id of nodeIds) {
      const prev = states[id];
      const next = stateFromScore(scores[id]);
      if (isWorse(next, prev)) {
        ledger.push({
          type: "threshold_crossed",
          step: t,
          nodeId: id,
          nodeLabel: nodeLabel[id],
          threshold: next,
          prev,
          scorePrev: prevScores[id] ?? Number.NaN,
          scoreNext: scores[id],
        });
      }
      states[id] = next;
    }
  }

  const gs = globalStopFromStates(states);
  if (gs.stop) ledger.push({ type: "global_stop", step: cascadeSteps, reason: gs.reason });

  return { nodeStates: states, nodeScores: scores, ledger, stop: gs.stop };
}
