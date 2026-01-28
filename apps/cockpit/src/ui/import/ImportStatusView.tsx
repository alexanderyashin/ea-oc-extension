import React from "react";

type ImportPhase = "idle" | "uploading" | "success" | "error";

export type ImportFacts = {
  rawHash?: string;
  contentHash?: string;
  timestamp?: string; // ISO string
  nodes?: number;
  edges?: number;
  nodeTypeCounts?: Record<string, number>;
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
        <div>Ожидание файла LeanIX export.</div>
      </Box>
    );
  }

  if (phase === "uploading") {
    return (
      <Box title="Import status">
        <div>Загрузка файла…</div>
      </Box>
    );
  }

  if (phase === "error") {
    return (
      <Box title="Import status (error)">
        <div style={{ whiteSpace: "pre-wrap" }}>
          {errorText || "Ошибка импорта."}
        </div>
      </Box>
    );
  }

  // success
  return (
    <Box title="Import status (success)">
      <div>Данные загружены. Модель построена.</div>

      <div style={{ marginTop: 10 }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Hashes</div>
        <div><span style={{ opacity: 0.7 }}>rawHash:</span> {facts?.rawHash ?? "—"}</div>
        <div><span style={{ opacity: 0.7 }}>contentHash:</span> {facts?.contentHash ?? "—"}</div>
        <div><span style={{ opacity: 0.7 }}>timestamp:</span> {facts?.timestamp ?? "—"}</div>
      </div>

      <div style={{ marginTop: 10 }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Graph summary (facts only)</div>
        <div><span style={{ opacity: 0.7 }}>nodes:</span> {facts?.nodes ?? "—"}</div>
        <div><span style={{ opacity: 0.7 }}>edges:</span> {facts?.edges ?? "—"}</div>
      </div>

      <div style={{ marginTop: 10 }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Node types</div>
        {facts?.nodeTypeCounts && Object.keys(facts.nodeTypeCounts).length > 0 ? (
          <div>
            {Object.entries(facts.nodeTypeCounts).map(([k, v]) => (
              <div key={k}>
                <span style={{ opacity: 0.7 }}>{k}:</span> {v}
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
