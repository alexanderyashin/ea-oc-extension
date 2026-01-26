import React from "react";

export const StopRupture: React.FC<{ active: boolean }> = ({ active }) => {
  if (!active) return null;

  return (
    <div
      role="presentation"
      aria-label="STOP rupture"
      style={{
        position: "fixed",
        inset: 0,
        background: "#000",
        zIndex: 9999,
        display: "grid",
        placeItems: "center",
      }}
    >
      <div
        style={{
          width: "100%",
          borderTop: "6px solid #ff3b30",
          borderBottom: "6px solid #ff3b30",
          padding: "28px 18px",
          background: "#000",
        }}
      >
        <div
          style={{
            textAlign: "center",
            fontFamily:
              'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            letterSpacing: 6,
            fontSize: 44,
            fontWeight: 800,
            color: "#ff3b30",
          }}
        >
          STOP
        </div>

        <div
          style={{
            marginTop: 10,
            textAlign: "center",
            fontFamily:
              'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            letterSpacing: 2,
            fontSize: 12,
            color: "#b0b0b0",
            lineHeight: 1.6,
          }}
        >
          TERMINAL BOUNDARY / NO RECOVERY / NO CONTROLS
        </div>
      </div>
    </div>
  );
};
