import React from "react";

export type InstrumentState = "S0" | "S1" | "S2" | "S3" | "S4";

export interface ZoneSpec {
  id: string;
  label: string;
  state: InstrumentState;
  manifest?: string;
  facts?: string[];
}

export const ZonesBoard: React.FC<{ zones: ZoneSpec[] }> = ({ zones }) => {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: 14 }}>
      {zones.map((z) => (
        <ZonePanel key={z.id} zone={z} />
      ))}
    </div>
  );
};

const stateStyle = (s: InstrumentState): React.CSSProperties => {
  const base: React.CSSProperties = {
    borderRadius: 999,
    padding: "2px 8px",
    fontSize: 12,
    letterSpacing: 1,
    border: "1px solid #2a2f40",
    background: "#0d1020",
    color: "#e8e8ea",
  };

  switch (s) {
    case "S0":
      return { ...base, borderColor: "#2a2f40", color: "#9aa3b2" };
    case "S1":
      return { ...base, borderColor: "#3a3f55" };
    case "S2":
      return { ...base, borderColor: "#4a5070" };
    case "S3":
      return { ...base, borderColor: "#6b6f90" };
    case "S4":
      return { ...base, borderColor: "#9aa0c0" };
    default:
      return base;
  }
};

const ZonePanel: React.FC<{ zone: ZoneSpec }> = ({ zone }) => {
  return (
    <section
      aria-label={`Zone ${zone.id}`}
      style={{
        gridColumn: "span 6",
        border: "1px solid #1c1f2a",
        background: "#0f1118",
        borderRadius: 10,
        padding: 14,
      }}
    >
      <div style={{ display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap" }}>
        <div style={{ fontSize: 12, letterSpacing: 2, opacity: 0.8 }}>{zone.id}</div>
        <div style={{ fontSize: 14, fontWeight: 650 }}>{zone.label}</div>

        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
          <div style={stateStyle(zone.state)} aria-label={`State ${zone.state}`}>
            {zone.state}
          </div>
        </div>
      </div>

      {zone.manifest && (
        <div
          style={{
            marginTop: 10,
            padding: "8px 10px",
            borderRadius: 8,
            background: "#0b0c12",
            border: "1px solid #1b1e2a",
            fontFamily:
              'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            fontSize: 12,
            letterSpacing: 0.2,
            color: "#cfcfd6",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {zone.manifest}
        </div>
      )}

      {zone.facts && zone.facts.length > 0 && (
        <div style={{ marginTop: 10, borderTop: "1px solid #1c1f2a", paddingTop: 10, display: "grid", gap: 6 }}>
          {zone.facts.map((line, idx) => (
            <div
              key={idx}
              style={{
                fontSize: 12,
                opacity: 0.86,
                lineHeight: 1.35,
                fontFamily:
                  'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
              }}
            >
              {line}
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
