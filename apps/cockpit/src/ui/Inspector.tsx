import { useMemo } from "react";
import { useGraphStore } from "../store/graph.store";

export function Inspector() {
  const selected = useGraphStore((s) => s.selected);
  const nodes = useGraphStore((s) => s.nodes);
  const edges = useGraphStore((s) => s.edges);
  const setName = useGraphStore((s) => s.updateSelectedNodeName);

  const selectedNode = useMemo(() => {
    if (selected.type !== "node") return null;
    return nodes.find((n) => n.id === selected.id) ?? null;
  }, [selected, nodes]);

  const selectedEdge = useMemo(() => {
    if (selected.type !== "edge") return null;
    return edges.find((e) => e.id === selected.id) ?? null;
  }, [selected, edges]);

  return (
    <div className="panel right">
      <div className="panelHeader">Inspector</div>
      <div className="panelBody">
        {selected.type === "none" && (
          <div style={{ color: "rgba(255,255,255,0.75)" }}>
            Select a node or edge to edit attributes.
          </div>
        )}

        {selectedNode && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ fontWeight: 700 }}>
              Node: {selectedNode.data.kind}
            </div>

            <div className="kv">
              <div style={{ opacity: 0.8 }}>id</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                {selectedNode.id}
              </div>

              <div style={{ opacity: 0.8 }}>name</div>
              <input
                className="input"
                value={String(selectedNode.data.attrs.name ?? "")}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          </div>
        )}

        {selectedEdge && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ fontWeight: 700 }}>Edge</div>

            <div className="kv">
              <div style={{ opacity: 0.8 }}>id</div>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                {selectedEdge.id}
              </div>

              <div style={{ opacity: 0.8 }}>kind</div>
              <div>{String((selectedEdge.label ?? selectedEdge.data?.kind ?? "edge"))}</div>

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
