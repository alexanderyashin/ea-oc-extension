import { useMemo } from "react";
import { useGraphStore } from "./store/graph.store";
import { InstrumentFormShell, type ZoneSpec } from "./ui/child16/InstrumentFormShell";

export default function Child16App() {
  const simLocked = useGraphStore((s) => s.simLocked);
  const selected = useGraphStore((s) => s.selected);
  const nodes = useGraphStore((s) => s.nodes);
  const edges = useGraphStore((s) => s.edges);
  const nodeStates = useGraphStore((s) => s.nodeStates);
  const ledger = useGraphStore((s) => s.ledger);
  const modal = useGraphStore((s) => s.modal);

  const zones: ZoneSpec[] = useMemo(() => {
    const selectedStr =
      selected.type === "none"
        ? "selected: none"
        : selected.type === "node"
        ? `selected: node:${selected.id}`
        : `selected: edge:${selected.id}`;

    const nTotal = nodes.length;
    const eTotal = edges.length;

    const stopInLedger = ledger.some((e) => e.type === "global_stop");
    const thresholds = ledger.filter((e) => e.type === "threshold_crossed").length;

    const sOk = Object.values(nodeStates).filter((v) => v === "OK").length;
    const sWarn = Object.values(nodeStates).filter((v) => v === "WARN").length;
    const sRed = Object.values(nodeStates).filter((v) => v === "RED").length;
    const sStop = Object.values(nodeStates).filter((v) => v === "STOP").length;

    return [
      {
        id: "Z_CANVAS",
        label: "CANVAS",
        state: simLocked ? "S4" : "S1",
        manifest: `nodes:${nTotal} edges:${eTotal}`,
        facts: [selectedStr],
      },
      {
        id: "Z_SELECTION",
        label: "SELECTION",
        state: selected.type === "none" ? "S0" : "S1",
        manifest: selectedStr,
      },
      {
        id: "Z_NODE_STATES",
        label: "NODE STATES",
        state: simLocked ? "S4" : "S2",
        manifest: `OK:${sOk} WARN:${sWarn} RED:${sRed} STOP:${sStop}`,
      },
      {
        id: "Z_LEDGER",
        label: "LEDGER",
        state: simLocked ? "S4" : ledger.length ? "S2" : "S0",
        manifest: `events:${ledger.length} threshold_crossed:${thresholds} global_stop:${stopInLedger ? 1 : 0}`,
      },
      {
        id: "Z_MODAL_SURFACE",
        label: "MODAL SURFACE",
        state: modal ? "S1" : "S0",
        manifest: modal ? `modal:${modal}` : "modal:none",
      },
      {
        id: "Z_STOP_LOCK",
        label: "STOP LOCK",
        state: simLocked ? "S4" : "S0",
        manifest: simLocked ? "simLocked:true" : "simLocked:false",
      },
    ];
  }, [simLocked, selected, nodes, edges, nodeStates, ledger, modal]);

  return <InstrumentFormShell title="INSTRUMENT FORM" stopActive={simLocked} zones={zones} />;
}
