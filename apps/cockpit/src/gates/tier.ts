// apps/cockpit/src/gates/tier.ts
export type BuildTier = "demo" | "full";

function normalizeTier(v: unknown): BuildTier {
  const s = String(v ?? "").toLowerCase().trim();
  return s === "full" ? "full" : "demo";
}

/**
 * Single source of truth for demo/full gating.
 * - VITE_BUILD_TIER=demo|full
 * - default: demo (safe by default)
 */
export const BUILD_TIER: BuildTier = normalizeTier(import.meta.env.VITE_BUILD_TIER);
export const IS_DEMO: boolean = BUILD_TIER !== "full";
