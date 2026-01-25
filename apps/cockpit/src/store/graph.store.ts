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

function nextId(prefix: string): string {
  return `${prefix}_${Date.now()}_${Math.floor(Math.random() * 1e6)}`;
}

export interface GraphState {
  nodes: RfNode[];
  edges: RfEdge[];

  selected: Selected;

  modal: null | "integrations" | "archimate" | "save" | "report";

  paletteKinds: readonly string[];

  onNodesChange: (changes: NodeChange<RfNode>[]) => void;
  onEdgesChange: (changes: EdgeChange<RfEdge>[]) => void;
  onConnect: (connection: Connection) => void;

  addNodeFromPalette: (kind: Emap0NodeKind) => void;

  selectNode: (id: string) => void;
  selectEdge: (id: string) => void;
  clearSelection: () => void;

  updateSelectedNodeName: (name: string) => void;

  openModal: (m: NonNullable<GraphState["modal"]>) => void;
  closeModal: () => void;
}

export const useGraphStore = create<GraphState>((set, get) => ({
  nodes: toRfNodes(),
  edges: toRfEdges(),

  selected: { type: "none" },

  modal: null,

  paletteKinds: EMAP0_NODE_KINDS,

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
      const id = nextId("e");
      const edge: RfEdge = {
        id,
        source: connection.source ?? "",
        target: connection.target ?? "",
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
        position: { x: 80 + Math.random() * 240, y: 80 + Math.random() * 200 },
        data: {
          id,
          kind,
          attrs: { name: `${kind} ${id.slice(-4)}` },
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
    set((s) => ({
      nodes: s.nodes.map((n) => {
        if (n.id !== sel.id) return n;
        return {
          ...n,
          data: {
            ...n.data,
            attrs: {
              ...n.data.attrs,
              name,
            },
          },
        };
      }),
    }));
  },

  openModal: (m) => set({ modal: m }),
  closeModal: () => set({ modal: null }),
}));
