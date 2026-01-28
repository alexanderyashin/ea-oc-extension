import React, { useMemo, useState } from "react";
import { ImportStatusView } from "./ImportStatusView";
import type { ImportFacts } from "./ImportStatusView";

// IMPORTANT:
// - UI only. No semantics changes.
// - No normalization / no interpretation.
// - Calls store actions only.

type ImportPhase = "idle" | "uploading" | "success" | "error";

// NOTE: path may differ in repo; adjust import to your actual store hook.
import { useGraphStore } from "../../store/graph.store";

function countNodeTypes(graph: any): Record<string, number> {
  // Facts-only count. We do not re-map/clean types, only read what's present.
  const counts: Record<string, number> = {};
  const nodes: any[] = Array.isArray(graph?.nodes) ? graph.nodes : [];
  for (const n of nodes) {
    const t = String(n?.type ?? "unknown");
    counts[t] = (counts[t] ?? 0) + 1;
  }
  return counts;
}

export function LeanIxImportPanel() {
  const [phase, setPhase] = useState<ImportPhase>("idle");
  const [errorText, setErrorText] = useState<string | undefined>(undefined);

  const loadRawSnapshot = useGraphStore((s: any) => s.loadRawSnapshot);
  const buildCanonicalGraph = useGraphStore((s: any) => s.buildCanonicalGraph);
  const setBaselineGraph = useGraphStore((s: any) => s.setBaselineGraph);

  const importedFacts = useGraphStore((s: any) => s.importFacts);
  const currentGraph = useGraphStore((s: any) => ({ nodes: s.nodes, edges: s.edges }));

  const facts: ImportFacts | undefined = useMemo(() => {
    if (!importedFacts) return undefined;
    const nodes = Array.isArray(currentGraph?.nodes) ? currentGraph.nodes.length : undefined;
    const edges = Array.isArray(currentGraph?.edges) ? currentGraph.edges.length : undefined;
    const nodeTypeCounts = currentGraph ? countNodeTypes(currentGraph) : undefined;

    return {
      rawHash: importedFacts.rawHash,
      contentHash: importedFacts.contentHash,
      timestamp: importedFacts.timestamp,
      nodes,
      edges,
      nodeTypeCounts,
    };
  }, [importedFacts, currentGraph]);

  async function onPickFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setErrorText(undefined);
    setPhase("uploading");

    try {
      // 1) load raw snapshot via backend ingestion (store action)
      await loadRawSnapshot(file);

      // 2) build canonical graph (store action; must remain contract-faithful)
      const graph = await buildCanonicalGraph();

      // 3) set baseline (resetShock must return to this)
      setBaselineGraph(graph);

      setPhase("success");
    } catch (err: any) {
      const msg = err?.message ? String(err.message) : "Ошибка импорта.";
      setErrorText(msg);
      setPhase("error");
    } finally {
      // reset file input to allow re-upload same file
      e.target.value = "";
    }
  }

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 16, padding: 14 }}>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12 }}>
        <div style={{ fontWeight: 800, fontSize: 16 }}>Import LeanIX</div>
        <div style={{ fontSize: 12, opacity: 0.7 }}>
          MVP: file-based • формат: как в backend ingestion
        </div>
      </div>

      <div style={{ marginTop: 10 }}>
        <input
          type="file"
          accept=".json,.zip,application/json,application/zip"
          onChange={onPickFile}
          disabled={phase === "uploading"}
        />
      </div>

      <ImportStatusView phase={phase} facts={facts} errorText={errorText} />
    </div>
  );
}
