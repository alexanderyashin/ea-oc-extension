import React from "react";
import { ZonesBoard, type ZoneSpec } from "./Zones";
import { StopRupture } from "./StopRupture";

export type InstrumentState = "S0" | "S1" | "S2" | "S3" | "S4";

// Re-export for stable imports from a single surface module.
export type { ZoneSpec };

export interface InstrumentFormShellProps {
  title?: string;
  stopActive: boolean;
  zones: ZoneSpec[];
  globalState?: InstrumentState;
}

export const InstrumentFormShell: React.FC<InstrumentFormShellProps> = ({
  title = "INSTRUMENT FORM",
  stopActive,
  zones,
  globalState,
}) => {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0b0c0f",
        color: "#e8e8ea",
        fontFamily:
          'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"',
      }}
    >
      <header
        style={{
          padding: "18px 20px",
          borderBottom: "1px solid #1c1f2a",
          background: "#090a0d",
        }}
      >
        <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
          <div style={{ letterSpacing: 2, fontWeight: 700, fontSize: 14, color: "#cfcfd6" }}>
            {title}
          </div>

          {globalState && (
            <div
              aria-label={`Global state ${globalState}`}
              style={{
                border: "1px solid #2a2f40",
                background: "#0d1020",
                padding: "2px 8px",
                borderRadius: 999,
                fontSize: 12,
                letterSpacing: 1,
              }}
            >
              {globalState}
            </div>
          )}

          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                fontSize: 12,
                letterSpacing: 2,
                opacity: 0.9,
                color: stopActive ? "#ff3b30" : "#7c839a",
              }}
            >
              STOP
            </div>
            <div
              aria-hidden="true"
              style={{
                width: 10,
                height: 10,
                borderRadius: 2,
                background: stopActive ? "#ff3b30" : "#2a2f40",
              }}
            />
          </div>
        </div>

        <div style={{ marginTop: 6, fontSize: 12, opacity: 0.75, lineHeight: 1.4 }}>
          DIAGNOSTIC SHELL — ZONES FIXED / STATES S0–S4 / STOP IS TERMINAL RUPTURE
        </div>
      </header>

      <main style={{ padding: 20 }}>
        <ZonesBoard zones={zones} />
      </main>

      <StopRupture active={stopActive} />
    </div>
  );
};
