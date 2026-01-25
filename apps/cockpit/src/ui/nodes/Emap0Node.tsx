import { useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { CanonicalData } from "../../store/graph.store";
import { useGraphStore } from "../../store/graph.store";

type Styles = {
  card: CSSProperties;
  header: CSSProperties;
  body: CSSProperties;
  labelWrap: CSSProperties;
  label: CSSProperties;
  labelInput: CSSProperties;
};

function kindMeta(kind: string): { icon: string; radius: number; headerBg: string; bodyBg: string } {
  const k = kind.toLowerCase();

  if (k.includes("actor") || k.includes("human")) {
    return { icon: "👤", radius: 18, headerBg: "rgba(255,255,255,0.065)", bodyBg: "rgba(255,255,255,0.030)" };
  }
  if (k.includes("service") || k.includes("app") || k.includes("system")) {
    return { icon: "⚙️", radius: 12, headerBg: "rgba(255,255,255,0.075)", bodyBg: "rgba(255,255,255,0.035)" };
  }
  if (k.includes("data") || k.includes("store") || k.includes("db")) {
    return { icon: "🗄️", radius: 8, headerBg: "rgba(255,255,255,0.070)", bodyBg: "rgba(255,255,255,0.032)" };
  }
  return { icon: "⬚", radius: 12, headerBg: "rgba(255,255,255,0.060)", bodyBg: "rgba(255,255,255,0.030)" };
}

export function Emap0Node(props: NodeProps) {
  const data = props.data as CanonicalData | undefined;

  const kind = String(data?.kind ?? "node");
  const name = String((data?.attrs as any)?.name ?? "");

  const updateNodeName = useGraphStore((s) => s.updateNodeName);
  const selectNode = useGraphStore((s) => s.selectNode);

  const meta = useMemo(() => kindMeta(kind), [kind]);

  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(name);

  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    setDraft(name);
  }, [name]);

  useEffect(() => {
    if (!isEditing) return;
    inputRef.current?.focus();
    inputRef.current?.select();
  }, [isEditing]);

  const styles: Styles = {
    card: {
      borderRadius: meta.radius,
      border: "1px solid rgba(255,255,255,0.16)",
      overflow: "hidden",
      minWidth: 180,
      boxShadow: "0 6px 20px rgba(0,0,0,0.30)",
      background: "rgba(20,22,26,0.85)",
      position: "relative",
    },
    header: {
      padding: "6px 8px",
      borderBottom: "1px solid rgba(255,255,255,0.10)",
      fontSize: 12,
      fontWeight: 900,
      letterSpacing: 0.2,
      opacity: 0.92,
      background: meta.headerBg,
      display: "flex",
      alignItems: "center",
      gap: 8,
    },
    body: {
      padding: "8px 8px 8px 8px",
      background: meta.bodyBg,
    },
    labelWrap: {
      marginTop: 6,
      textAlign: "center",
      userSelect: "none",
    },
    label: {
      fontSize: 12,
      fontWeight: 900,
      opacity: 0.92,
      padding: "2px 6px",
      borderRadius: 8,
      display: "inline-block",
      background: "rgba(0,0,0,0.25)",
      border: "1px solid rgba(255,255,255,0.12)",
    },
    labelInput: {
      fontSize: 12,
      fontWeight: 800,
      padding: "4px 8px",
      borderRadius: 8,
      background: "rgba(0,0,0,0.35)",
      color: "rgba(255,255,255,0.92)",
      border: "1px solid rgba(255,255,255,0.18)",
      outline: "none",
      width: 170,
      maxWidth: 200,
    },
  };

  const handleStyle: CSSProperties = {
    width: 12,
    height: 12,
    borderRadius: 999,
    background: "rgba(255,255,255,0.65)",
    border: "2px solid rgba(0,0,0,0.55)",
    boxShadow: "0 0 0 2px rgba(255,255,255,0.12)",
  };

  const commit = () => {
    const trimmed = draft.trim();
    const finalName = trimmed.length ? trimmed : "Unnamed";
    updateNodeName(props.id, finalName);
    setIsEditing(false);
  };

  return (
    <div
      className="emap0Node"
      title="Drag to move. Use handles to connect. Double-click label to rename."
      onClick={() => selectNode(props.id)}
    >
      <div style={styles.card}>
        <Handle
          type="target"
          position={Position.Left}
          className="emapHandle"
          style={handleStyle}
          title="Target handle (drop connection here)"
        />

        <div style={styles.header}>
          <span style={{ opacity: 0.95 }}>{meta.icon}</span>
          <span>{kind}</span>
        </div>

        <div style={styles.body}>
          <div style={{ opacity: 0.75, fontSize: 12 }}>
            {props.selected ? "Selected" : "Click to select"} · Drag from handle to connect
          </div>
        </div>

        <Handle
          type="source"
          position={Position.Right}
          className="emapHandle"
          style={handleStyle}
          title="Source handle (drag from here to connect)"
        />
      </div>

      <div style={styles.labelWrap}>
        {isEditing ? (
          <input
            ref={inputRef}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onBlur={commit}
            onKeyDown={(e) => {
              if (e.key === "Enter") commit();
              if (e.key === "Escape") {
                setDraft(name);
                setIsEditing(false);
              }
            }}
            style={styles.labelInput}
            aria-label="Node name"
          />
        ) : (
          <span
            style={styles.label}
            onDoubleClick={(e) => {
              e.stopPropagation();
              setIsEditing(true);
            }}
            title="Double-click to rename"
          >
            {name?.trim().length ? name : "Unnamed"}
          </span>
        )}
      </div>
    </div>
  );
}
