// apps/cockpit/src/ui/LockedFeatureDialog.tsx
type Props = {
  title: string;
  featureId: string;
  onClose: () => void;
};

export function LockedFeatureDialog({ title, featureId, onClose }: Props) {
  return (
    <div className="modalOverlay" onClick={onClose} role="presentation">
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div className="modalHeader">
          <div>{title}</div>
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>

        <div className="modalBody">
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Available in full build</div>

          <div style={{ opacity: 0.9, marginBottom: 10 }}>
            This public demo is intentionally partial and diagnostic-only. The feature you clicked is gated and
            requires a full build (audit-gated).
          </div>

          <div style={{ opacity: 0.75, fontSize: 13 }}>
            Feature-id: <code>{featureId}</code>
          </div>

          <div style={{ opacity: 0.75, fontSize: 13, marginTop: 10 }}>
            To unlock: run a full build with <code>VITE_BUILD_TIER=full</code> and provide the full audit / evidence
            context. No hidden exports exist in the demo.
          </div>
        </div>
      </div>
    </div>
  );
}
