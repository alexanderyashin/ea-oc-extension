import type { SimResult } from "../types";

/**
 * MVP rule: DO NOT invent thresholds.
 * We only compute margins if SimulationResult carries numeric threshold fields.
 * Current SIMULATION-0 provides nodeScores in [0..1], but does not expose theta numbers.
 * Therefore: return undefined by default (safe).
 *
 * Extension point: if later nodeScores or nodeStates include numeric thresholds, implement here.
 */
export function thresholdProximity(_sim: SimResult, _nodeId: string): { stopMargin?: number; warnMargin?: number } | undefined {
  return undefined;
}
