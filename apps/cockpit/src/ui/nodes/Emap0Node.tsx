import type { CSSProperties } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { CanonicalData } from "../../store/graph.store";

type Styles = {
  root: CSSProperties;
  header: CSSProperties;
  body: CSSProperties;
};

function classifyColors(kind: string): { headerBg: string; bodyBg: string } {
  const k = kind.toLowerCase();

  if (k.includes("actor") || k.includes("human")) {
    return { headerBg: "rgba(255,255,255,0.06)", bodyBg: "rgba(255,255,255,0.03)" };
  }
  if (k.includes("service") || k.includes("app") || k.includes("system")) {
    return { headerBg: "rgba(255,255,255,0.07)", bodyBg: "rgba(255,255,255,0.035)" };
  }
  if (k.includes("data") || k.includes("store") || k.includes("db")) {
    return { headerBg: "rgba(255,255,255,0.065)", bodyBg: "rgba(255,255,255,0.032)" };
  }
  return { headerBg: "rgba(255,255,255,0.055)", bodyBg: "rgba(255,255,255,0.03)" };
}

export function Emap0Node(props: NodeProps) {
  const data = props.data as CanonicalData | undefined;

  const kind = String(data?.kind ?? "node");
  const name = String((data?.attrs as any)?.name ?? "");

  const tint = classifyColors(kind);

  const styles: Styles = {
    root: {
      borderRadius: 12,
      border: "1px solid rgba(255,255,255,0.14)",
      overflow: "hidden",
      minWidth: 180,
      boxShadow: "0 6px 20px rgba(0,0,0,0.30)",
      background: "rgba(20,22,26,0.85)",
    },
    header: {
      padding: "6px 8px",
      borderBottom: "1px solid rgba(255,255,255,0.10)",
      fontSize: 12,
      fontWeight: 900,
      letterSpacing: 0.2,
      opacity: 0.9,
      background: tint.headerBg,
    },
    body: {
      padding: "8px 8px 6px 8px",
      background: tint.bodyBg,
    },
  };

  return (
    <div className="emap0Node" title="Drag to move. Use handles to connect." style={styles.root}>
      <Handle type="target" position={Position.Left} className="emapHandle" />

      <div style={styles.header}>{kind}</div>
      <div style={styles.body}>
        <div className="emapName" style={{ fontWeight: 800 }}>
          {name || "(unnamed)"}
        </div>
        <div className="emapHint" style={{ opacity: 0.75, fontSize: 12, marginTop: 2 }}>
          Click node, edit name in Inspector
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="emapHandle" />
    </div>
  );
}
