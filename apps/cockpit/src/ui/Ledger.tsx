import { useMemo } from "react";
import { useGraphStore } from "../store/graph.store";
import type { LedgerEvent, NodeState } from "../compute/types";

function fmtState(s: NodeState): string {
  return s;
}

function fmtNum(n: number): string {
  // keep readable, stable
  return Number.isFinite(n) ? n.toFixed(3) : String(n);
}

function renderTitle(e: LedgerEvent): string {
  switch (e.type) {
    case "threshold_crossed":
      return `status_change: ${e.nodeLabel}`;
    case "info":
      return "info";
    case "global_stop":
      return "GLOBAL STOP";
    default: {
      const _exhaustive: never = e;
      return String(_exhaustive);
    }
  }
}

function renderBody(e: LedgerEvent): string {
  switch (e.type) {
    case "threshold_crossed":
      return [
        `step: ${e.step}`,
        `nodeId: ${e.nodeId}`,
        `nodeLabel: ${e.nodeLabel}`,
        `state: ${fmtState(e.prev)} → ${fmtState(e.threshold)}`,
        `score: ${fmtNum(e.scorePrev)} → ${fmtNum(e.scoreNext)}`,
      ].join("\n");
    case "info":
      return `step: ${e.step}\n${e.message}`;
    case "global_stop":
      return `step: ${e.step}\nreason: ${e.reason}`;
    default: {
      const _exhaustive: never = e;
      return String(_exhaustive);
    }
  }
}

function eventKey(e: LedgerEvent, idx: number): string {
  // LedgerEvent has no id; construct a stable-ish key from content + index
  // (index makes duplicates safe while keeping React happy)
  switch (e.type) {
    case "threshold_crossed":
      return `tc:${e.step}:${e.nodeId}:${e.prev}:${e.threshold}:${idx}`;
    case "info":
      return `info:${e.step}:${e.message}:${idx}`;
    case "global_stop":
      return `stop:${e.step}:${e.reason}:${idx}`;
    default: {
      const _exhaustive: never = e;
      return `x:${String(_exhaustive)}:${idx}`;
    }
  }
}

export function Ledger() {
  const ledger = useGraphStore((s) => s.ledger);
  const simLocked = useGraphStore((s) => s.simLocked);

  const items = useMemo(() => ledger.slice().reverse(), [ledger]);

  return (
    <div className="panel bottom">
      <div
        className="panelHeader"
        style={{ display: "flex", justifyContent: "space-between", gap: 12 }}
      >
        <div>Ledger (factual)</div>
        <div style={{ opacity: 0.75, fontWeight: 700 }}>
          {simLocked ? "STOP locked" : "OK"}
        </div>
      </div>

      <div className="panelBody" style={{ overflow: "auto" }}>
        {items.length === 0 ? (
          <div style={{ opacity: 0.8 }}>
            No events yet. Add nodes, connect them, then run Shock.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {items.map((e, idx) => (
              <div
                key={eventKey(e, idx)}
                style={{
                  paddingBottom: 6,
                  borderBottom: "1px solid rgba(255,255,255,0.06)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 10,
                  }}
                >
                  <div
                    style={{
                      fontWeight: 800,
                      opacity: e.type === "global_stop" ? 1 : 0.95,
                    }}
                  >
                    {renderTitle(e)}
                  </div>
                  <div style={{ opacity: 0.7, fontSize: 12 }}>step {e.step}</div>
                </div>

                <div
                  style={{
                    opacity: 0.9,
                    marginTop: 2,
                    whiteSpace: "pre-wrap",
                    fontFamily:
                      'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                    fontSize: 12,
                  }}
                >
                  {renderBody(e)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
