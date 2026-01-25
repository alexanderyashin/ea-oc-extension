import { useGraphStore } from "../store/graph.store";
import type { ShockIntensity, ShockScope, ShockType } from "../compute/types";

export function TopBar() {
  const openModal = useGraphStore((s) => s.openModal);

  const simLocked = useGraphStore((s) => s.simLocked);
  const cfg = useGraphStore((s) => s.simConfig);

  const setShockType = useGraphStore((s) => s.setShockType);
  const setShockScope = useGraphStore((s) => s.setShockScope);
  const setShockIntensity = useGraphStore((s) => s.setShockIntensity);
  const runShock = useGraphStore((s) => s.runShock);
  const resetShock = useGraphStore((s) => s.resetShock);

  return (
    <div className="topbar">
      <div className="title">EA-OC Cockpit — SIMULATION-0</div>

      <div className="actions" style={{ alignItems: "center" }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <select
            className="input"
            style={{ width: 190 }}
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
            style={{ width: 150 }}
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
            style={{ width: 110 }}
            disabled={simLocked}
            value={cfg.intensity}
            onChange={(e) => setShockIntensity(Number(e.target.value) as ShockIntensity)}
            title="Intensity"
          >
            <option value={0.1}>10%</option>
            <option value={0.3}>30%</option>
            <option value={0.5}>50%</option>
          </select>

          <button className="btn" onClick={runShock} disabled={simLocked} title="Run Shock (deterministic)">
            Run Shock
          </button>

          <button className="btn" onClick={resetShock} title="Reset (clears STOP lock)">
            Reset
          </button>

          {simLocked ? (
            <span style={{ opacity: 0.9, fontWeight: 700 }}>STOP</span>
          ) : (
            <span style={{ opacity: 0.6 }}>OK</span>
          )}
        </div>

        <div style={{ width: 10 }} />

        <button className="btn" onClick={() => openModal("integrations")}>
          Integrations
        </button>
        <button className="btn" onClick={() => openModal("archimate")}>
          Archimate
        </button>
        <button className="btn" onClick={() => openModal("save")}>
          Save
        </button>
        <button className="btn" onClick={() => openModal("report")}>
          Report
        </button>
      </div>
    </div>
  );
}
