import "./App.css";
import "@xyflow/react/dist/style.css";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
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

export default function App() {
  const nodes = useGraphStore((s) => s.nodes);
  const edges = useGraphStore((s) => s.edges);

  const onNodesChange = useGraphStore((s) => s.onNodesChange);
  const onEdgesChange = useGraphStore((s) => s.onEdgesChange);
  const onConnect = useGraphStore((s) => s.onConnect);

  const selectNode = useGraphStore((s) => s.selectNode);
  const selectEdge = useGraphStore((s) => s.selectEdge);
  const clearSelection = useGraphStore((s) => s.clearSelection);

  const onPaneClick = useCallback(() => {
    clearSelection();
  }, [clearSelection]);

  const onNodeClick: NodeMouseHandler<RfNode> = (_, n) => selectNode(n.id);
  const onEdgeClick: EdgeMouseHandler<RfEdge> = (_, e) => selectEdge(e.id);

  const nodeTypes = useMemo(() => ({ emap0: Emap0Node }), []);

  return (
    <div className="cockpit">
      {/* TOP: TopBar already has className="topbar" inside */}
      <TopBar />

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
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            fitView
          >
            <Background />
            <MiniMap />
            <Controls />
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
