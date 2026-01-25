import type { SimConfig } from "./types";
import { clamp01 } from "./determinism";

export function applyShockBaseScore(cfg: SimConfig): number {
  // Deterministic preset-only intensity already comes as 0.1/0.3/0.5.
  // Interpretation:
  // - infra_capacity_drop: direct score bump (stress due to loss of capacity proxy)
  // - node_failure_rate: direct score bump (risk proxy)
  return clamp01(cfg.intensity);
}
