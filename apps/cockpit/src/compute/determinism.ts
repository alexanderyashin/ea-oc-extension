export function sortIds(xs: readonly string[]): string[] {
  return [...xs].sort((a, b) => a.localeCompare(b));
}

export function clamp01(x: number): number {
  if (Number.isNaN(x) || !Number.isFinite(x)) return 0;
  if (x < 0) return 0;
  if (x > 1) return 1;
  return x;
}

export function stableEdgeKey(e: { source: string; target: string; id?: string }): string {
  // Prefer explicit id if present; otherwise deterministic composite.
  return e.id && e.id.length > 0 ? e.id : `${e.source}→${e.target}`;
}

export function byStableEdge(a: any, b: any): number {
  return stableEdgeKey(a).localeCompare(stableEdgeKey(b));
}

export function nodeLabelFromAttrs(attrs: any, fallbackId: string): string {
  const name = attrs?.name;
  if (typeof name === "string" && name.trim().length > 0) return name.trim();
  return fallbackId;
}

export function isSystemKind(kind: unknown): boolean {
  if (typeof kind !== "string") return false;
  return kind.toLowerCase().includes("system");
}
