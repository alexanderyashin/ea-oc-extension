import { useMemo } from "react";
import { useGraphStore } from "../store/graph.store";
import type { ShockIntensity, ShockScope, ShockType } from "../compute/types";
import { IS_DEMO } from "../gates/tier";

type Props = {
  onOpenImport?: () => void;
};

export function TopBar({ onOpenImport }: Props) {
  const openModal = useGraphStore((s) => s.openModal);

  const simLocked = useGraphStore((s) => s.simLocked);
  const cfg = useGraphStore((s) => s.simConfig);

  const setShockType = useGraphStore((s) => s.setShockType);
  const setShockScope = useGraphStore((s) => s.setShockScope);
  const setShockIntensity = useGraphStore((s) => s.setShockIntensity);
  const runShock = useGraphStore((s) => s.runShock);
  const resetShock = useGraphStore((s) => s.resetShock);

  const intensityOptions = useMemo(() => {
    // 10..200 step 10 (value in [0.1..2.0])
    return Array.from({ length: 20 }, (_, i) => (i + 1) * 10);
  }, []);

  const selectStyle: React.CSSProperties = {
    width: "100%",
    background: "rgba(0,0,0,0.35)",
    color: "rgba(255,255,255,0.92)",
    border: "1px solid rgba(255,255,255,0.18)",
  };

  return (
    <div className="topbar">
      <div className="title" style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <span style={{ fontWeight: 900 }}>ESTRA Toolkit {IS_DEMO ? "(DEMO)" : ""}</span>

            {IS_DEMO ? (
              <span
                title="Public demo (partial). Full-only capabilities are gated."
                style={{
                  fontSize: 12,
                  fontWeight: 800,
                  padding: "2px 8px",
                  borderRadius: 999,
                  border: "1px solid rgba(255,255,255,0.25)",
                  opacity: 0.9,
                }}
              >
                DEMO
              </span>
            ) : null}
          </div>
        </div>
      </div>

      <div className="actions" style={{ alignItems: "center" }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <select
            className="input"
            style={{ ...selectStyle, width: 190 }}
            disabled={simLocked}
            value={cfg.shockType}
            onChange={(e) => setShockType(e.target.value as ShockType)}
            title="Shock type"
          >
            <option value="infra_capacity_drop">Infra capacity drop</option>
            <option value="node_failure_rate">Node failure rate</option>
          </select>

          <select
            className="input"
            style={{ ...selectStyle, width: 150 }}
            disabled={simLocked}
            value={cfg.scope}
            onChange={(e) => setShockScope(e.target.value as ShockScope)}
            title="Scope"
          >
            <option value="selected">Selected node</option>
            <option value="all_systems">All Systems</option>
          </select>

          <select
            className="input"
            style={{ ...selectStyle, width: 110 }}
            disabled={simLocked}
            value={cfg.intensity}
            onChange={(e) => setShockIntensity(Number(e.target.value) as ShockIntensity)}
            title="Intensity"
          >
            {intensityOptions.map((pct) => (
              <option key={pct} value={pct / 100}>
                {pct}%
              </option>
            ))}
          </select>

          <button className="btn" onClick={runShock} disabled={simLocked} title="Run Shock (deterministic)">
            Run Shock
          </button>

          <button className="btn" onClick={resetShock} title="Reset (clears STOP lock)">
            Reset
          </button>

          <span style={{ opacity: simLocked ? 0.95 : 0.6, fontWeight: 900 }}>{simLocked ? "STOP" : "OK"}</span>
        </div>

        <div style={{ width: 10 }} />

        {/* kernel-neutral import entrypoint (wiring only) */}
        <button
          className="btn"
          onClick={() => onOpenImport?.()}
          disabled={!onOpenImport}
          title="Import source snapshot (session only)"
        >
          Import…
        </button>

        <div style={{ width: 10 }} />

        <button className="btn" onClick={() => openModal("extended")} title="Extended capabilities (Full build only)">
          Extended (Full build)
        </button>
      </div>
    </div>
  );
}
