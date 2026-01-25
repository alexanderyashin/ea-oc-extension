import "./App.css";
import "@xyflow/react/dist/style.css";

import { useCallback } from "react";
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

  return (
    <div className="cockpit">
      <TopBar />
      <Palette />

      <div className="panel center">
        <div className="panelHeader">Canvas</div>
        <div className="rfWrap">
          <ReactFlow<RfNode, RfEdge>
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </div>

      <Inspector />
      <Ledger />
      <StubModal />
    </div>
  );
}
