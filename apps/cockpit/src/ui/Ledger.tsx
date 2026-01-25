import { useGraphStore } from "../store/graph.store";
import type { LedgerEvent } from "../compute/types";

function renderEvent(e: LedgerEvent) {
  if (e.type === "info") {
    return (
      <div>
        <span style={{ opacity: 0.7 }}>t={e.step}</span> — {e.message}
      </div>
    );
  }

  if (e.type === "global_stop") {
    return (
      <div style={{ fontWeight: 700 }}>
        <span style={{ opacity: 0.7 }}>t={e.step}</span> — GLOBAL STOP: {e.reason}
      </div>
    );
  }

  // threshold_crossed
  return (
    <div>
      <span style={{ opacity: 0.7 }}>t={e.step}</span> —{" "}
      <span style={{ fontWeight: 700 }}>{e.threshold}</span>{" "}
      @ <span style={{ opacity: 0.9 }}>{e.nodeLabel}</span>{" "}
      <span style={{ opacity: 0.65 }}>({e.nodeId})</span>
    </div>
  );
}

export function Ledger() {
  const ledger = useGraphStore((s) => s.ledger);
  const simLocked = useGraphStore((s) => s.simLocked);

  return (
    <div className="panel bottom">
      <div className="panelHeader">
        <div>Ledger</div>
        <div style={{ opacity: 0.75, fontWeight: 600 }}>{simLocked ? "STOP (locked)" : "Unlocked"}</div>
      </div>

      <div className="panelBody" style={{ opacity: 0.92 }}>
        {ledger.length === 0 ? (
          <div style={{ opacity: 0.75 }}>Ledger empty. Run Shock to produce factual events.</div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {ledger.map((e, idx) => (
              <div key={idx} style={{ borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: 6 }}>
                {renderEvent(e)}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
