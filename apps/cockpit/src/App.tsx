import "./App.css";
import "@xyflow/react/dist/style.css";

import { useCallback, useEffect, useMemo } from "react";
import {
  ReactFlow,
  Background,
  MiniMap,
  type NodeMouseHandler,
  type EdgeMouseHandler,
} from "@xyflow/react";

import { useGraphStore, type RfNode, type RfEdge } from "./store/graph.store";
import { TopBar } from "./ui/TopBar";
import { Palette } from "./ui/Palette";
import { Inspector } from "./ui/Inspector";
import { Ledger } from "./ui/Ledger";
import { StubModal } from "./ui/StubModal";
import { StartHereHints } from "./ui/StartHereHints";
import { Emap0Node } from "./ui/nodes/Emap0Node";

function isTypingTarget(): boolean {
  const el = document.activeElement as HTMLElement | null;
  if (!el) return false;
  const tag = el.tagName?.toLowerCase();
  if (tag === "input" || tag === "textarea" || tag === "select") return true;
  if ((el as any).isContentEditable) return true;
  return false;
}

export default function App() {
  const nodes = useGraphStore((s) => s.nodes);
  const edges = useGraphStore((s) => s.edges);

  const onNodesChange = useGraphStore((s) => s.onNodesChange);
  const onEdgesChange = useGraphStore((s) => s.onEdgesChange);
  const onConnect = useGraphStore((s) => s.onConnect);

  const selected = useGraphStore((s) => s.selected);

  const selectNode = useGraphStore((s) => s.selectNode);
  const selectEdge = useGraphStore((s) => s.selectEdge);
  const clearSelection = useGraphStore((s) => s.clearSelection);

  const removeEdge = useGraphStore((s) => s.removeEdge);

  const openModal = useGraphStore((s) => s.openModal);

  const onPaneClick = useCallback(() => {
    clearSelection();
  }, [clearSelection]);

  const onNodeClick: NodeMouseHandler<RfNode> = (_, n) => selectNode(n.id);
  const onEdgeClick: EdgeMouseHandler<RfEdge> = (_, e) => selectEdge(e.id);

  const onEdgeDoubleClick: EdgeMouseHandler<RfEdge> = (_, e) => {
    removeEdge(e.id);
  };

  // Make store-selection visible in ReactFlow selection styling.
  const rfNodes = useMemo(() => {
    if (selected.type !== "node") return nodes;
    return nodes.map((n) => ({ ...n, selected: n.id === selected.id }));
  }, [nodes, selected]);

  const rfEdges = useMemo(() => {
    if (selected.type !== "edge") return edges;
    return edges.map((e) => ({ ...e, selected: e.id === selected.id }));
  }, [edges, selected]);

  // Delete / Backspace removes selected edge (explicit disconnect).
  useEffect(() => {
    const onKeyDown = (ev: KeyboardEvent) => {
      if (isTypingTarget()) return;

      if (ev.key === "Delete" || ev.key === "Backspace") {
        const sel = selected;
        if (sel.type === "edge") {
          ev.preventDefault();
          removeEdge(sel.id);
        }
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [selected, removeEdge]);

  const nodeTypes = useMemo(() => ({ emap0: Emap0Node }), []);

  return (
    <div className="cockpit">
      {/* TOP: TopBar already has className="topbar" inside */}
      <TopBar onOpenImport={() => openModal("import")} />

      {/* LEFT */}
      <div className="panel left">
        <Palette />
      </div>

      {/* CENTER */}
      <div className="panel center">
        <div className="panelHeader">
          <div>Canvas</div>
          <div style={{ opacity: 0.75, fontWeight: 800 }}>Add → Name → Connect → Shock</div>
        </div>

        <div className="rfWrap">
          <StartHereHints />
          <ReactFlow<RfNode, RfEdge>
            nodes={rfNodes}
            edges={rfEdges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onEdgeDoubleClick={onEdgeDoubleClick}
            onPaneClick={onPaneClick}
            deleteKeyCode={["Backspace", "Delete"]}
            elementsSelectable
            edgesFocusable
            fitView
          >
            <Background />

            {/* ② MiniMap to bottom-right (and styled), ① Controls removed */}
            <MiniMap
              position="bottom-right"
              style={{
                backgroundColor: "#0f1115",
                border: "1px solid rgba(255,255,255,0.15)",
                borderRadius: 8,
                margin: 12,
              }}
            />
          </ReactFlow>
        </div>
      </div>

      {/* RIGHT */}
      <div className="panel right">
        <Inspector />
      </div>
      {/* BOTTOM */}
      <div className="panel bottom">
        <Ledger />
      </div>

      {/* OVERLAY (not part of grid) */}
      <StubModal />
    </div>
  );
}
