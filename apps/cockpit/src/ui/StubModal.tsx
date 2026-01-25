import { useGraphStore } from "../store/graph.store";

const TITLES: Record<string, string> = {
  integrations: "Integrations",
  archimate: "ArchiMate Profile",
  save: "Save",
  report: "Report",
};

export function StubModal() {
  const modal = useGraphStore((s) => s.modal);
  const close = useGraphStore((s) => s.closeModal);

  if (!modal) return null;

  const title = TITLES[modal] ?? "Dialog";

  return (
    <div className="modalOverlay" onClick={close} role="presentation">
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div className="modalHeader">
          <div>{title}</div>
          <button className="btn" onClick={close}>
            Close
          </button>
        </div>
        <div className="modalBody">
          <div style={{ fontWeight: 700, marginBottom: 8 }}>
            Available in full version
          </div>
          <div style={{ opacity: 0.85 }}>
            This is a non-claiming UI stub. No persistence, no integrations, no reporting logic in this shell.
          </div>
        </div>
      </div>
    </div>
  );
}
