import { useGraphStore } from "../store/graph.store";
import { IS_DEMO } from "../gates/tier";
import { LockedFeatureDialog } from "./LockedFeatureDialog";

const TITLES: Record<string, string> = {
  integrations: "Integrations",
  archimate: "ArchiMate Profile",
  save: "Save",
  report: "Report",
};

const FEATURE_IDS: Record<string, string> = {
  integrations: "integrations",
  archimate: "profile.archimate.switch",
  save: "artifact.save",
  report: "artifact.report",
};

export function StubModal() {
  const modal = useGraphStore((s) => s.modal);
  const close = useGraphStore((s) => s.closeModal);

  if (!modal) return null;

  const title = TITLES[modal] ?? "Dialog";
  const featureId = FEATURE_IDS[modal] ?? modal;

  if (IS_DEMO) {
    return <LockedFeatureDialog title={title} featureId={featureId} onClose={close} />;
  }

  // FULL tier: keep honest stub (no fake implementation claims).
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
          <div style={{ opacity: 0.9, marginBottom: 10 }}>
            This shell is diagnostic-only (SIMULATION-0). The UI surface exists, but no persistence / integrations /
            reporting implementation is shipped in this demo artifact.
          </div>

          <div style={{ opacity: 0.75, fontSize: 13 }}>
            Surface-id: <code>{featureId}</code>
          </div>
        </div>
      </div>
    </div>
  );
}
