import { useGraphStore } from "../store/graph.store";

export function TopBar() {
  const openModal = useGraphStore((s) => s.openModal);

  return (
    <div className="topbar">
      <div className="title">EA-OC Cockpit — Canvas UI Shell</div>
      <div className="actions">
        <button className="btn" onClick={() => openModal("integrations")}>
          Integrations
        </button>
        <button className="btn" onClick={() => openModal("archimate")}>
          ArchiMate Profile
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
