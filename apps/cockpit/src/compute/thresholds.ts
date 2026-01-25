import type { NodeState } from "./types";

export function stateFromScore(score: number): NodeState {
  if (score >= 0.9) return "STOP";
  if (score >= 0.6) return "RED";
  if (score >= 0.3) return "WARN";
  return "OK";
}

export function isWorse(next: NodeState, prev: NodeState): boolean {
  const order: Record<NodeState, number> = { OK: 0, WARN: 1, RED: 2, STOP: 3 };
  return order[next] > order[prev];
}

export function globalStopFromStates(states: Record<string, NodeState>): { stop: boolean; reason: string } {
  for (const k of Object.keys(states)) {
    if (states[k] === "STOP") return { stop: true, reason: `Node ${k} reached STOP` };
  }

  // Secondary criterion: RED+STOP ratio >= 0.30
  const ids = Object.keys(states);
  if (ids.length === 0) return { stop: false, reason: "" };

  let bad = 0;
  for (const id of ids) {
    const s = states[id];
    if (s === "RED" || s === "STOP") bad++;
  }
  const ratio = bad / ids.length;
  if (ratio >= 0.3) return { stop: true, reason: `Global ratio RED+STOP = ${(ratio * 100).toFixed(0)}%` };

  return { stop: false, reason: "" };
}
