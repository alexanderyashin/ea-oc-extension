import { EMAP0_NODE_KINDS, type Emap0NodeKind } from "../model/emap0.profile";
import { useGraphStore } from "../store/graph.store";

export function Palette() {
  const addNode = useGraphStore((s) => s.addNodeFromPalette);

  return (
    <div className="panel left">
      <div className="panelHeader">Palette</div>
      <div className="panelBody">
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {EMAP0_NODE_KINDS.map((k) => (
            <button
              key={k}
              className="btn"
              onClick={() => addNode(k as Emap0NodeKind)}
              title={`Add node: ${k}`}
              style={{ textAlign: "left" }}
            >
              + {k}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
