import { useGraphStore } from "../store/graph.store";

export function StartHereHints() {
  const showHints = useGraphStore((s) => s.showHints);
  const dismiss = useGraphStore((s) => s.dismissHints);
  const nodes = useGraphStore((s) => s.nodes);

  if (!showHints) return null;

  const hasAnyNode = nodes.length > 0;

  return (
    <div className="hintOverlay">
      <div className="hintCard">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
          <div style={{ fontWeight: 800 }}>Start here (30 sec)</div>
          <button className="btn btnSmall" onClick={dismiss} title="Dismiss (session only)">
            Dismiss
          </button>
        </div>

        <div className="hintList" style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 6 }}>
          <div>1) Add a node from <b>Palette</b> (left).</div>
          <div>2) Click the node, rename it in <b>Inspector</b> (right).</div>
          <div>3) Connect nodes using the visible <b>handles</b> (left/right of node).</div>
          <div>4) Run <b>Shock</b> (top), then see events in <b>Ledger</b> (bottom).</div>
          {!hasAnyNode && <div style={{ opacity: 0.8 }}>(Tip: start with any kind — it’s a shell.)</div>}
        </div>

        <div className="hintFoot" style={{ marginTop: 10, opacity: 0.8 }}>
          Pan: drag empty canvas | Zoom: mouse wheel | Select: click node/edge
        </div>
      </div>
    </div>
  );
}
