import { EMAP0_NODE_KINDS, type Emap0NodeKind } from "../model/emap0.profile";
import { useGraphStore } from "../store/graph.store";
import { IS_DEMO } from "../gates/tier";

export function Palette() {
  const addNode = useGraphStore((s) => s.addNodeFromPalette);

  return (
    <div className="panel left">
      <div className="panelHeader">Palette</div>

      <div
        className="panelBody"
        style={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
        }}
      >
        {/* node buttons */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {EMAP0_NODE_KINDS.map((k) => (
            <button
              key={k}
              className="btn"
              title={`Add node: ${k}`}
              style={{ textAlign: "left" }}
              onClick={() => addNode(k as Emap0NodeKind)}
            >
              + {k}
            </button>
          ))}
        </div>

        {/* hard spacer: pushes info block to bottom */}
        <div style={{ marginTop: "auto" }} />

        {/* info block (moved from TopBar) */}
        <div
          style={{
            marginTop: 24,
            paddingTop: 12,
            borderTop: "1px solid rgba(255,255,255,0.12)",
            fontSize: 12,
            opacity: 0.88,
            lineHeight: 1.35,
          }}
        >
          <div style={{ fontWeight: 900, opacity: 0.95 }}>Alexander Yashin</div>

          <div style={{ opacity: 0.82 }}>
            Observe continuum state, thresholds Θ, and STOP under deterministic shocks.
          </div>

          <div style={{ fontSize: 11, opacity: 0.7, marginTop: 6 }}>
            No control. No optimization. No output.
          </div>

          <div style={{ fontSize: 11, opacity: 0.6, marginTop: 6 }}>
            Build tier: {IS_DEMO ? "DEMO (public, partial)" : "FULL"}
          </div>
        </div>
      </div>
    </div>
  );
}
