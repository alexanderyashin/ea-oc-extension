import { useMemo } from "react";
import { useGraphStore } from "../store/graph.store";

function fmt(n: unknown): string {
  if (typeof n === "number") return Number.isFinite(n) ? n.toFixed(3) : String(n);
  if (Array.isArray(n)) return `[${n.map((x) => fmt(x)).join(", ")}]`;
  return String(n);
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
    const nm = metrics?.nodeMetrics?.find((x) => x.nodeId === selectedNode.id) ?? null;
    return nm;
  }, [metrics, selectedNode]);

  return (
    <div className="panel right">
      <div className="panelHeader">Inspector</div>

      <div className="panelBody">
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

            <div style={{ marginTop: 6, opacity: 0.85, fontWeight: 800 }}>Metrics (post-pass)</div>

            {selectedNodeMetrics ? (
              <div
                style={{
                  fontFamily:
                    'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                  fontSize: 12,
                  opacity: 0.95,
                  whiteSpace: "pre-wrap",
                  border: "1px solid rgba(255,255,255,0.10)",
                  borderRadius: 8,
                  padding: 10,
                  background: "rgba(0,0,0,0.20)",
                }}
              >
                {[
                  `m1_dependencyDepth.out=${fmt(selectedNodeMetrics.m1_dependencyDepth?.out)}`,
                  `m1_dependencyDepth.in=${fmt(selectedNodeMetrics.m1_dependencyDepth?.in)}`,
                  `m2_blastRadius.out=${fmt(selectedNodeMetrics.m2_blastRadius?.out)}`,
                  `m2_blastRadius.in=${fmt(selectedNodeMetrics.m2_blastRadius?.in)}`,
                  `m3_inReach=${fmt(selectedNodeMetrics.m3_cascadeSusceptibility?.inReach)}`,
                  `m3_inDegree=${fmt(selectedNodeMetrics.m3_cascadeSusceptibility?.inDegree)}`,
                  `m4_vector=${fmt(selectedNodeMetrics.m4_structuralCriticality?.vector ?? [])}`,
                  `m4_note=${String(selectedNodeMetrics.m4_structuralCriticality?.note ?? "")}`,
                  `m5_thresholdProximity=${
                    selectedNodeMetrics.m5_thresholdProximity ? fmt(selectedNodeMetrics.m5_thresholdProximity) : "n/a"
                  }`,
                ].join("\n")}
              </div>
            ) : (
              <div style={{ opacity: 0.75 }}>No metrics yet. Run Shock to compute a metrics overlay.</div>
            )}

            <div style={{ marginTop: 6, opacity: 0.7 }}>Tip: connect nodes using the visible handles on the node sides.</div>
          </div>
        )}

        {selectedEdge && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ fontWeight: 800 }}>Edge</div>

            <div className="kv">
              <div style={{ opacity: 0.8 }}>id</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>{selectedEdge.id}</div>

              <div style={{ opacity: 0.8 }}>kind</div>
              <div>{String(selectedEdge.label ?? selectedEdge.data?.kind ?? "edge")}</div>

              <div style={{ opacity: 0.8 }}>from</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>{selectedEdge.source}</div>

              <div style={{ opacity: 0.8 }}>to</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>{selectedEdge.target}</div>
            </div>

            <div style={{ marginTop: 6, opacity: 0.7 }}>(Edge attribute editing is intentionally minimal in this shell.)</div>
          </div>
        )}
      </div>
    </div>
  );
}
