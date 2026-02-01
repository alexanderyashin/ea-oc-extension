import React, { useMemo, useState } from "react";
import { ImportStatusView } from "./ImportStatusView";
import type { ImportFacts } from "./ImportStatusView";

// IMPORTANT:
// - UI only. Facts-only.
// - No normalization / no interpretation.
// - Preferred path: call store actions (backend ingestion).
// - DEMO fallback: if backend is unavailable (e.g. 404), show file facts + hashes,
//   but DO NOT change the graph.

type ImportPhase = "idle" | "uploading" | "success" | "error";

import { useGraphStore } from "../../store/graph.store";

function countNodeKinds(nodes: any[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const n of nodes) {
    const k = String(n?.data?.kind ?? "unknown");
    counts[k] = (counts[k] ?? 0) + 1;
  }
  return counts;
}

// Best-effort SHA-256 for demo facts.
// If crypto.subtle is unavailable, returns null (still fine: facts-only).
async function sha256Hex(buf: ArrayBuffer): Promise<string | null> {
  try {
    const cryptoObj = (globalThis as any)?.crypto;
    const subtle = cryptoObj?.subtle;
    if (!subtle) return null;

    const hash = await subtle.digest("SHA-256", buf);
    const bytes = new Uint8Array(hash);
    let hex = "";
    for (const b of bytes) hex += b.toString(16).padStart(2, "0");
    return hex;
  } catch {
    return null;
  }
}

function safeIso(ts: number | string | undefined): string {
  if (typeof ts === "number" && Number.isFinite(ts)) return new Date(ts).toISOString();
  if (typeof ts === "string" && ts.trim().length) return ts;
  return new Date().toISOString();
}

export function LeanIxImportPanel() {
  const [phase, setPhase] = useState<ImportPhase>("idle");
  const [errorText, setErrorText] = useState<string | undefined>(undefined);

  const loadRawSnapshot = useGraphStore((s: any) => s.loadRawSnapshot);
  const buildCanonicalGraph = useGraphStore((s: any) => s.buildCanonicalGraph);
  const setBaselineGraph = useGraphStore((s: any) => s.setBaselineGraph);

  const importedFacts = useGraphStore((s: any) => s.importFacts);

  // Subscribe to stable references separately.
  const nodesArr = useGraphStore((s: any) => s.nodes);
  const edgesArr = useGraphStore((s: any) => s.edges);

  // DEMO facts (file-only), used only when backend path is unavailable.
  const [demoFacts, setDemoFacts] = useState<ImportFacts | undefined>(undefined);

  const facts: ImportFacts | undefined = useMemo(() => {
    // Prefer backend facts if present.
    if (importedFacts) {
      const nodes = Array.isArray(nodesArr) ? nodesArr.length : undefined;
      const edges = Array.isArray(edgesArr) ? edgesArr.length : undefined;
      const nodeKindCounts = Array.isArray(nodesArr) ? countNodeKinds(nodesArr) : undefined;

      return {
        rawHash: importedFacts.rawHash,
        contentHash: importedFacts.contentHash,
        timestamp: importedFacts.timestamp,
        nodes,
        edges,
        nodeKindCounts,
      };
    }

    // Else (DEMO fallback) show file-only facts.
    return demoFacts;
  }, [importedFacts, nodesArr, edgesArr, demoFacts]);

  async function onPickFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setErrorText(undefined);
    setPhase("uploading");
    setDemoFacts(undefined);

    try {
      // Preferred path (Tool/FULL): backend ingestion as source of truth.
      await loadRawSnapshot(file);
      const graph = await buildCanonicalGraph();
      setBaselineGraph(graph);

      setPhase("success");
      return;
    } catch (err: any) {
      const msg = err?.message ? String(err.message) : "Ошибка импорта.";

      // DEMO fallback:
      // If backend route is missing/unavailable, keep UI useful:
      // compute file hashes locally and show facts-only (NO graph change).
      const isBackendMissing =
        msg.includes("status=404") ||
        msg.toLowerCase().includes("not found") ||
        msg.toLowerCase().includes("failed to fetch") ||
        msg.toLowerCase().includes("networkerror");

      if (isBackendMissing) {
        try {
          const buf = await file.arrayBuffer();
          const contentHash = await sha256Hex(buf);

          // rawHash is "file envelope" hash surrogate: name+size+mtime
          const rawEnvelope = `${file.name}::${file.size}::${file.lastModified}`;
          const rawHash = await sha256Hex(new TextEncoder().encode(rawEnvelope).buffer);

          setDemoFacts({
            rawHash: rawHash ?? `demo:env:${rawEnvelope}`,
            contentHash: contentHash ?? `demo:sha256:unavailable`,
            timestamp: safeIso(Date.now()),
            nodes: undefined,
            edges: undefined,
            nodeKindCounts: undefined,
          });

          setPhase("success");
          setErrorText(
            "DEMO fallback: Backend ingestion (/api/ingest/leanix) is unavailable. " +
              "Showing file facts + hashes only. No mapping to graph performed."
          );
          return;
        } catch {
          // If even fallback fails, show original error.
        }
      }

      setErrorText(msg);
      setPhase("error");
    } finally {
      // reset file input to allow re-upload same file
      e.target.value = "";
    }
  }

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 16, padding: 14 }}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          gap: 12,
        }}
      >
        <div style={{ fontWeight: 800, fontSize: 16 }}>Import LeanIX</div>
        <div style={{ fontSize: 12, opacity: 0.7 }}>
          Supported format only: LeanIX export file as accepted by backend ingestion (/api/ingest/leanix)
        </div>
      </div>

      <div style={{ marginTop: 10 }}>
        <input
          type="file"
          // CRITICAL (MVP): do not filter in the file picker.
          // Backend is source of truth for validation; UI must allow selecting any file.
          onChange={onPickFile}
          disabled={phase === "uploading"}
        />
      </div>

      <ImportStatusView phase={phase} facts={facts} errorText={errorText} />
    </div>
  );
}
