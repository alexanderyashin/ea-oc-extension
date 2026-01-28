import { useMemo } from "react";
import { useGraphStore } from "../store/graph.store";
import { LeanIxImportPanel } from "./import/LeanIxImportPanel";

function fmt(n: unknown): string {
  if (typeof n === "number") return Number.isFinite(n) ? n.toFixed(3) : String(n);
  if (Array.isArray(n)) return `[${n.map((x) => fmt(x)).join(", ")}]`;
  return String(n);
}

type Level = "low" | "medium" | "high" | "critical";

function clamp01(x: number): number {
  if (!Number.isFinite(x)) return 0;
  return Math.max(0, Math.min(1, x));
}

function levelFrom01(x: number): Level {
  const v = clamp01(x);
  if (v >= 0.9) return "critical";
  if (v >= 0.67) return "high";
  if (v >= 0.34) return "medium";
  return "low";
}

function labelForLevel(l: Level): string {
  switch (l) {
    case "low":
      return "Low";
    case "medium":
      return "Medium";
    case "high":
      return "High";
    case "critical":
      return "Critical";
    default: {
      const _x: never = l;
      return String(_x);
    }
  }
}

function hintForMetric(name: "dependency" | "blast" | "criticality", l: Level): string {
  // keep ultra-minimal: readable, non-explanatory, no recommendations
  if (name === "dependency") {
    if (l === "low") return "shallow coupling";
    if (l === "medium") return "moderate coupling";
    if (l === "high") return "deep coupling";
    return "very deep coupling";
  }
  if (name === "blast") {
    if (l === "low") return "local impact";
    if (l === "medium") return "regional impact";
    if (l === "high") return "systemic impact";
    return "system-wide impact";
  }
  // criticality
  if (l === "low") return "non-critical";
  if (l === "medium") return "elevated";
  if (l === "high") return "critical";
  return "stop-prone";
}

function maxNum(xs: number[] | undefined | null): number {
  if (!xs || xs.length === 0) return 0;
  let m = -Infinity;
  for (const v of xs) m = Math.max(m, Number.isFinite(v) ? v : -Infinity);
  return Number.isFinite(m) ? m : 0;
}

export function Inspector() {
  const selected = useGraphStore((s) => s.selected);
  const nodes = useGraphStore((s) => s.nodes);
  const edges = useGraphStore((s) => s.edges);
  const setName = useGraphStore((s) => s.updateSelectedNodeName);
  const metrics = useGraphStore((s) => s.metrics);

  const selectedNode = useMemo(() => {
    if (selected.type !== "node") return null;
    return nodes.find((n) => n.id === selected.id) ?? null;
  }, [selected, nodes]);

  const selectedEdge = useMemo(() => {
    if (selected.type !== "edge") return null;
    return edges.find((e) => e.id === selected.id) ?? null;
  }, [selected, edges]);

  const selectedNodeMetrics = useMemo(() => {
    if (!selectedNode) return null;
    return metrics?.nodeMetrics?.find((x) => x.nodeId === selectedNode.id) ?? null;
  }, [metrics, selectedNode]);

  const projection = useMemo(() => {
    if (!selectedNodeMetrics) return null;

    // Dependency depth: combine in/out (0..1) -> one level
    const dep = Math.max(
      clamp01(selectedNodeMetrics.m1_dependencyDepth?.out ?? 0),
      clamp01(selectedNodeMetrics.m1_dependencyDepth?.in ?? 0)
    );
    const depLevel = levelFrom01(dep);

    // Blast radius: combine in/out (0..1) -> one level
    const blast = Math.max(
      clamp01(selectedNodeMetrics.m2_blastRadius?.out ?? 0),
      clamp01(selectedNodeMetrics.m2_blastRadius?.in ?? 0)
    );
    const blastLevel = levelFrom01(blast);

    // Structural criticality: DO NOT show vector; derive a single level from max component
    const critMax = clamp01(maxNum(selectedNodeMetrics.m4_structuralCriticality?.vector));
    const critLevel = levelFrom01(critMax);

    return {
      dep,
      depLevel,
      blast,
      blastLevel,
      critMax,
      critLevel,
    };
  }, [selectedNodeMetrics]);

  return (
    <div className="panel right">
      <div className="panelHeader">Inspector</div>

      <div className="panelBody">
        {/* Import is a contextual integration tool: keep it inside Inspector panel (no layout changes). */}
        <LeanIxImportPanel />

        <div style={{ height: 12 }} />

        {selected.type === "none" && (
          <div style={{ color: "rgba(255,255,255,0.75)" }}>
            Select a node or edge to view attributes.
          </div>
        )}

        {selectedNode && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ fontWeight: 800 }}>Node: {selectedNode.data.kind}</div>

            <div className="kv">
              <div style={{ opacity: 0.8 }}>id</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                {selectedNode.id}
              </div>

              <div style={{ opacity: 0.8 }}>name</div>
              <input
                className="input"
                value={String(selectedNode.data.attrs?.name ?? "")}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div style={{ marginTop: 6, opacity: 0.85, fontWeight: 800 }}>
              Metrics (post-pass)
            </div>

            {selectedNodeMetrics && projection ? (
              <div
                style={{
                  border: "1px solid rgba(255,255,255,0.10)",
                  borderRadius: 8,
                  padding: 10,
                  background: "rgba(0,0,0,0.20)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                }}
              >
                {/* 3 aggregates only */}
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <div style={{ fontWeight: 800, opacity: 0.92 }}>Dependency depth</div>
                  <div style={{ opacity: 0.9 }}>
                    {labelForLevel(projection.depLevel)}{" "}
                    <span style={{ opacity: 0.65 }}>
                      ({hintForMetric("dependency", projection.depLevel)})
                    </span>
                  </div>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <div style={{ fontWeight: 800, opacity: 0.92 }}>Blast radius</div>
                  <div style={{ opacity: 0.9 }}>
                    {labelForLevel(projection.blastLevel)}{" "}
                    <span style={{ opacity: 0.65 }}>
                      ({hintForMetric("blast", projection.blastLevel)})
                    </span>
                  </div>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <div style={{ fontWeight: 800, opacity: 0.92 }}>Criticality</div>
                  <div style={{ opacity: 0.9 }}>
                    {labelForLevel(projection.critLevel)}{" "}
                    <span style={{ opacity: 0.65 }}>
                      ({hintForMetric("criticality", projection.critLevel)})
                    </span>
                  </div>
                </div>

                {/* M5 only if present */}
                {selectedNodeMetrics.m5_thresholdProximity ? (
                  <div
                    style={{
                      marginTop: 6,
                      paddingTop: 8,
                      borderTop: "1px solid rgba(255,255,255,0.08)",
                      fontFamily:
                        'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                      fontSize: 12,
                      opacity: 0.85,
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {[
                      `thresholdProximity.stopMargin=${fmt(
                        selectedNodeMetrics.m5_thresholdProximity.stopMargin ?? "n/a"
                      )}`,
                      `thresholdProximity.warnMargin=${fmt(
                        selectedNodeMetrics.m5_thresholdProximity.warnMargin ?? "n/a"
                      )}`,
                    ].join("\n")}
                  </div>
                ) : null}
              </div>
            ) : (
              <div style={{ opacity: 0.75 }}>
                No metrics yet. Run Shock to compute a metrics overlay.
              </div>
            )}

            <div style={{ marginTop: 6, opacity: 0.7 }}>
              Tip: connect nodes using the visible handles on the node sides.
            </div>
          </div>
        )}

        {selectedEdge && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ fontWeight: 800 }}>Edge</div>

            <div className="kv">
              <div style={{ opacity: 0.8 }}>id</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                {selectedEdge.id}
              </div>

              <div style={{ opacity: 0.8 }}>kind</div>
              <div>{String(selectedEdge.label ?? selectedEdge.data?.kind ?? "edge")}</div>

              <div style={{ opacity: 0.8 }}>from</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                {selectedEdge.source}
              </div>

              <div style={{ opacity: 0.8 }}>to</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                {selectedEdge.target}
              </div>
            </div>

            <div style={{ marginTop: 6, opacity: 0.7 }}>
              (Edge attribute editing is intentionally minimal in this shell.)
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
