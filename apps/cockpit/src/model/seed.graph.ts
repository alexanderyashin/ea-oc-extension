/* apps/cockpit/src/model/seed.graph.ts
   One minimal demo seed graph (EMAP-0).
   No UI / no simulation logic; purely data that should validate against EMAP0_PROFILE.
*/

import type { Graph } from "./canonical";
import { asEdgeId, asNodeId } from "./canonical";

export const SEED_GRAPH_EMAP0: Graph = {
  schemaVersion: "v0",
  profileId: "emap0",

  meta: {
    title: "Demo Seed (EMAP-0)",
    description: "Minimal enterprise slice: actor -> capability -> application -> system with a data flow.",
    tags: ["demo", "emap0"],
  },

  nodes: [
    {
      id: asNodeId("n_actor_business"),
      kind: "Actor",
      label: "Business User",
      attrs: {
        name: "Business User",
      },
      pos: { x: 120, y: 120 },
    },
    {
      id: asNodeId("n_cap_order_mgmt"),
      kind: "Capability",
      label: "Order Management",
      attrs: {
        name: "Order Management",
      },
      pos: { x: 340, y: 120 },
    },
    {
      id: asNodeId("n_app_erp"),
      kind: "Application",
      label: "ERP",
      attrs: {
        name: "ERP",
      },
      pos: { x: 560, y: 120 },
    },
    {
      id: asNodeId("n_sys_core"),
      kind: "System",
      label: "Core Platform",
      attrs: {
        name: "Core Platform",
      },
      pos: { x: 780, y: 120 },
    },
    {
      id: asNodeId("n_data_orders"),
      kind: "DataObject",
      label: "Orders",
      attrs: {
        name: "Orders",
      },
      pos: { x: 560, y: 260 },
    },
    {
      id: asNodeId("n_external_payments"),
      kind: "External",
      label: "Payments Provider",
      attrs: {
        name: "Payments Provider",
      },
      pos: { x: 780, y: 260 },
    },
  ],

  edges: [
    {
      id: asEdgeId("e_serves_1"),
      kind: "serves",
      from: asNodeId("n_cap_order_mgmt"),
      to: asNodeId("n_actor_business"),
      attrs: {},
    },
    {
      id: asEdgeId("e_impl_1"),
      kind: "implements",
      from: asNodeId("n_app_erp"),
      to: asNodeId("n_cap_order_mgmt"),
      attrs: {},
    },
    {
      id: asEdgeId("e_dep_1"),
      kind: "depends_on",
      from: asNodeId("n_app_erp"),
      to: asNodeId("n_sys_core"),
      attrs: {
        strength: 0.8,
      },
    },
    {
      id: asEdgeId("e_owns_1"),
      kind: "owns",
      from: asNodeId("n_app_erp"),
      to: asNodeId("n_data_orders"),
      attrs: {},
    },
    {
      id: asEdgeId("e_flow_1"),
      kind: "flows_to",
      from: asNodeId("n_data_orders"),
      to: asNodeId("n_external_payments"),
      attrs: {},
    },
  ],
};
