import { create } from "zustand";
import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type Node,
  type NodeChange,
} from "@xyflow/react";

import { SEED_GRAPH_EMAP0 } from "../model/seed.graph";
import { EMAP0_NODE_KINDS, type Emap0NodeKind } from "../model/emap0.profile";
import type { JsonValue } from "../model/canonical";

import { simulateShock } from "../compute/simulate";
import { computeMetrics } from "../compute/metrics";
import type {
  LedgerEvent,
  NodeState,
  ShockIntensity,
  ShockScope,
  ShockType,
  SimConfig,
  MetricSet,
} from "../compute/types";

export type CanonicalData = {
  id: string;
  kind: string;
  attrs: Record<string, JsonValue>;
};

export type RfNode = Node<CanonicalData>;
export type RfEdge = Edge;

type Selected =
  | { type: "node"; id: string }
  | { type: "edge"; id: string }
  | { type: "none" };

function toRfNodes(): RfNode[] {
  return SEED_GRAPH_EMAP0.nodes.map((n) => ({
    id: n.id as unknown as string,
    type: "emap0",
    position: { x: n.pos?.x ?? 0, y: n.pos?.y ?? 0 },
    data: {
      id: n.id as unknown as string,
      kind: n.kind,
      attrs: { ...(n.attrs as Record<string, JsonValue>) },
    },
    draggable: true,
  }));
}

function toRfEdges(): RfEdge[] {
  return SEED_GRAPH_EMAP0.edges.map((e) => ({
    id: e.id as unknown as string,
    source: e.from as unknown as string,
    target: e.to as unknown as string,
    label: e.kind,
    data: { kind: e.kind, attrs: e.attrs },
  }));
}

// Session-deterministic ids (stable within one app session / hot run).
let __idCounter = 0;
function nextId(prefix: string): string {
  __idCounter += 1;
  return `${prefix}_${__idCounter}`;
}

function stateStyle(s: NodeState | undefined): RfNode["style"] | undefined {
  if (!s) return undefined;

  if (s === "OK") {
    return {
      border: "1px solid rgba(0,255,0,0.28)",
      background: "rgba(0,255,0,0.06)",
    };
  }
  if (s === "WARN") {
    return {
      border: "1px solid rgba(255,215,0,0.35)",
      background: "rgba(255,215,0,0.08)",
    };
  }
  if (s === "RED") {
    return {
      border: "1px solid rgba(255,80,80,0.45)",
      background: "rgba(255,80,80,0.10)",
    };
  }
  return {
    border: "2px solid rgba(255,0,0,0.85)",
    background: "rgba(255,0,0,0.14)",
  }; // STOP
}

type BaselineGraph = {
  nodes: RfNode[];
  edges: RfEdge[];
};

export interface GraphState {
  nodes: RfNode[];
  edges: RfEdge[];

  // baseline graph (for reset)
  baseline: BaselineGraph;

  selected: Selected;

  modal: null | "integrations" | "archimate" | "save" | "report" | "extended";
  paletteKinds: readonly string[];

  // Session-only UX hints
  showHints: boolean;
  dismissHints: () => void;

  // Simulation slice (SIMULATION-0)
  simConfig: SimConfig;
  simLocked: boolean; // STOP lock
  nodeStates: Record<string, NodeState>;
  ledger: LedgerEvent[];

  // Metrics overlay (post-pass, does not affect simulation)
  metrics: MetricSet | null;

  onNodesChange: (changes: NodeChange<RfNode>[]) => void;
  onEdgesChange: (changes: EdgeChange<RfEdge>[]) => void;
  onConnect: (connection: Connection) => void;

  addNodeFromPalette: (kind: Emap0NodeKind) => void;

  selectNode: (id: string) => void;
  selectEdge: (id: string) => void;
  clearSelection: () => void;

  updateSelectedNodeName: (name: string) => void;
  updateNodeName: (id: string, name: string) => void;

  openModal: (m: NonNullable<GraphState["modal"]>) => void;
  closeModal: () => void;

  setShockType: (t: ShockType) => void;
  setShockScope: (s: ShockScope) => void;
  setShockIntensity: (i: ShockIntensity) => void;

  runShock: () => void;
  resetShock: () => void;
}

export const useGraphStore = create<GraphState>((set, get) => {
  const seedNodes = toRfNodes();
  const seedEdges = toRfEdges();

  return {
    nodes: seedNodes,
    edges: seedEdges,
    baseline: { nodes: seedNodes, edges: seedEdges },

    selected: { type: "none" },

    modal: null,
    paletteKinds: EMAP0_NODE_KINDS,

    showHints: true,
    dismissHints: () => set({ showHints: false }),

    simConfig: { shockType: "infra_capacity_drop", scope: "all_systems", intensity: 0.3 },
    simLocked: false,
    nodeStates: {},
    ledger: [],
    metrics: null,

    onNodesChange: (changes) =>
      set((s) => ({
        nodes: applyNodeChanges<RfNode>(changes, s.nodes),
      })),

    onEdgesChange: (changes) =>
      set((s) => ({
        edges: applyEdgeChanges<RfEdge>(changes, s.edges),
      })),

    onConnect: (connection) =>
      set((s) => {
        const source = connection.source ?? "";
        const target = connection.target ?? "";
        if (!source || !target) return s;

        const id = nextId("e");
        const edge: RfEdge = {
          id,
          source,
          target,
          label: "connects",
          data: { kind: "connects", attrs: {} },
        };
        return { edges: addEdge(edge, s.edges) };
      }),

    addNodeFromPalette: (kind) =>
      set((s) => {
        const id = nextId("n");
        const node: RfNode = {
          id,
          type: "emap0",
          position: { x: 120 + Math.random() * 420, y: 120 + Math.random() * 280 },
          data: {
            id,
            kind,
            attrs: { name: `${kind} ${id}` },
          },
          draggable: true,
        };
        return { nodes: [...s.nodes, node] };
      }),

    selectNode: (id) => set({ selected: { type: "node", id } }),
    selectEdge: (id) => set({ selected: { type: "edge", id } }),
    clearSelection: () => set({ selected: { type: "none" } }),

    updateSelectedNodeName: (name) => {
      const sel = get().selected;
      if (sel.type !== "node") return;

      const trimmed = name.trim();
      const finalName = trimmed.length ? trimmed : "Unnamed";

      set((s) => ({
        nodes: s.nodes.map((n) => {
          if (n.id !== sel.id) return n;
          return {
            ...n,
            data: {
              ...n.data,
              attrs: {
                ...(n.data.attrs ?? {}),
                name: finalName,
              },
            },
          };
        }),
      }));
    },

    updateNodeName: (id, name) => {
      const trimmed = name.trim();
      const finalName = trimmed.length ? trimmed : "Unnamed";

      set((s) => ({
        nodes: s.nodes.map((n) => {
          if (n.id !== id) return n;
          return {
            ...n,
            data: {
              ...n.data,
              attrs: {
                ...(n.data.attrs ?? {}),
                name: finalName,
              },
            },
          };
        }),
      }));
    },

    openModal: (m) => set({ modal: m }),
    closeModal: () => set({ modal: null }),

    setShockType: (t) => {
      if (get().simLocked) return;
      set((s) => ({ simConfig: { ...s.simConfig, shockType: t } }));
    },
    setShockScope: (sc) => {
      if (get().simLocked) return;
      set((s) => ({ simConfig: { ...s.simConfig, scope: sc } }));
    },
    setShockIntensity: (i) => {
      if (get().simLocked) return;
      set((s) => ({ simConfig: { ...s.simConfig, intensity: i } }));
    },

    runShock: () => {
      if (get().simLocked) return;

      const s = get();
      const selectedNodeId = s.selected.type === "node" ? s.selected.id : null;

      const res = simulateShock(
        s.simConfig,
        s.nodes.map((n) => ({ id: n.id, data: n.data })),
        s.edges.map((e) => ({ id: e.id, source: e.source, target: e.target })),
        selectedNodeId
      );

      // Post-pass metrics (must not affect simulation outcome)
      const metrics = computeMetrics({
        cfg: s.simConfig,
        nodes: s.nodes.map((n) => ({ id: n.id })),
        edges: s.edges.map((e) => ({ source: e.source, target: e.target })),
        selectedNodeId,
        simResult: res,
      });

      const resWithMetrics = { ...res, metrics };

      set((st) => ({
        simLocked: resWithMetrics.stop,
        nodeStates: resWithMetrics.nodeStates,
        ledger: resWithMetrics.ledger,
        metrics: resWithMetrics.metrics ?? null,
        nodes: st.nodes.map((n) => ({
          ...n,
          style: stateStyle(resWithMetrics.nodeStates[n.id]),
        })),
      }));
    },

    resetShock: () => {
      set((st) => ({
        simLocked: false,
        nodeStates: {},
        ledger: [],
        metrics: null,
        selected: { type: "none" },
        nodes: st.baseline.nodes.map((n) => ({ ...n, style: undefined })),
        edges: st.baseline.edges.map((e) => ({ ...e })),
      }));
    },
  };
});
