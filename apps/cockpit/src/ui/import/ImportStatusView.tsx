// apps/cockpit/src/ui/import/ImportStatusView.tsx
import React from "react";

type ImportPhase = "idle" | "uploading" | "success" | "error";

export type ImportFacts = {
  rawHash?: string;
  contentHash?: string;
  timestamp?: string; // ISO string
  nodes?: number;
  edges?: number;
  nodeKindCounts?: Record<string, number>;
};

export function ImportStatusView(props: {
  phase: ImportPhase;
  facts?: ImportFacts;
  errorText?: string;
}) {
  const { phase, facts, errorText } = props;

  const Box: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 12, marginTop: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 8 }}>{title}</div>
      <div style={{ fontSize: 13, lineHeight: 1.4 }}>{children}</div>
    </div>
  );

  if (phase === "idle") {
    return (
      <Box title="Import status">
        <div>Waiting for input.</div>
      </Box>
    );
  }

  if (phase === "uploading") {
    return (
      <Box title="Import status">
        <div>Loading…</div>
      </Box>
    );
  }

  if (phase === "error") {
    return (
      <Box title="Import status (error)">
        <div style={{ whiteSpace: "pre-wrap" }}>{errorText || "Import error."}</div>
      </Box>
    );
  }

  // success
  return (
    <Box title="Import status (success)">
      <div>Loaded. Graph baseline updated.</div>

      <div style={{ marginTop: 10 }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Facts: hashes</div>

        <div>
          <span style={{ opacity: 0.7 }}>rawHash:</span>{" "}
          <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
            {facts?.rawHash ?? "—"}
          </span>
        </div>

        <div>
          <span style={{ opacity: 0.7 }}>contentHash:</span>{" "}
          <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
            {facts?.contentHash ?? "—"}
          </span>
        </div>

        <div>
          <span style={{ opacity: 0.7 }}>timestamp:</span>{" "}
          <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
            {facts?.timestamp ?? "—"}
          </span>
        </div>
      </div>

      <div style={{ marginTop: 10 }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Facts: graph counts</div>
        <div>
          <span style={{ opacity: 0.7 }}>nodes:</span> {facts?.nodes ?? "—"}
        </div>
        <div>
          <span style={{ opacity: 0.7 }}>edges:</span> {facts?.edges ?? "—"}
        </div>
      </div>

      <div style={{ marginTop: 10 }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Facts: node kinds</div>
        {facts?.nodeKindCounts && Object.keys(facts.nodeKindCounts).length > 0 ? (
          <div style={{ display: "grid", gap: 4 }}>
            {Object.entries(facts.nodeKindCounts)
              .sort((a, b) => a[0].localeCompare(b[0]))
              .map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>{k}</span>
                  <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>{v}</span>
                </div>
              ))}
          </div>
        ) : (
          <div>—</div>
        )}
      </div>
    </Box>
  );
}
