// apps/cockpit/src/ui/ImportDialog.tsx
import React, { useMemo, useRef, useState } from "react";

import { useGraphStore, type RfEdge, type RfNode } from "../store/graph.store";
import type { SourceSnapshot } from "../import/types";
import type { LeanixSnapshot } from "../import/leanix/leanix.types";
import {
  pickDirectory,
  readLeanixCsvSources,
  supportsDirectoryPicker,
} from "../import/leanix/leanix.reader";
import { parseCsv, tableToObjects } from "../import/leanix/leanix.parser";
import { validateLeanixSnapshot } from "../import/leanix/leanix.validate";
import { mapLeanixToCanonical } from "../mapping/leanix_to_canonical";

type Props = {
  open: boolean;
  onClose: () => void;
};

type ImportPhase = "idle" | "reading" | "parsing" | "validating" | "ready" | "error";

function normalizePath(p: string): string {
  return p.replaceAll("\\", "/").replace(/^\/+/, "");
}

function buildLeanixSnapshot(files: Record<string, string>): SourceSnapshot<LeanixSnapshot> {
  const errors: string[] = [];
  const warnings: string[] = [];

  const inv: Record<string, { bytes: number }> = {};
  for (const [k, v] of Object.entries(files)) {
    inv[normalizePath(k)] = { bytes: new Blob([v]).size };
  }

  let manifestVersion = "unknown";
  let manifestRaw: unknown = undefined;
  const manifestText = files["manifest.json"];
  if (typeof manifestText === "string" && manifestText.trim().length) {
    try {
      manifestRaw = JSON.parse(manifestText);
      const v = (manifestRaw as any)?.version ?? (manifestRaw as any)?.fixtureVersion ?? null;
      if (v) manifestVersion = String(v);
    } catch {
      warnings.push("manifest.json is present but not valid JSON (ignored).");
    }
  } else {
    warnings.push("manifest.json not found or empty (version=unknown).");
  }

  function parseFactSheet(path: string): Array<{ id: string; name: string; raw: Record<string, string> }> {
    const txt = files[path];
    if (!txt) return [];
    const t = parseCsv(txt);
    const objs = tableToObjects(t);
    return objs.map((o) => ({
      id: String(o["id"] ?? "").trim(),
      name: String(o["name"] ?? "").trim(),
      raw: o,
    }));
  }

  function parseRelation(path: string): Array<{ fromId: string; toId: string; raw: Record<string, string> }> {
    const txt = files[path];
    if (!txt) return [];
    const t = parseCsv(txt);
    const objs = tableToObjects(t);

    // resolve common from/to variants deterministically
    const resolveFrom = (o: Record<string, string>) =>
      String(
        o["fromid"] ??
          o["from_id"] ??
          o["from"] ??
          o["sourceid"] ??
          o["source_id"] ??
          o["source"] ??
          ""
      ).trim();

    const resolveTo = (o: Record<string, string>) =>
      String(
        o["toid"] ??
          o["to_id"] ??
          o["to"] ??
          o["targetid"] ??
          o["target_id"] ??
          o["target"] ??
          ""
      ).trim();

    return objs.map((o) => ({
      fromId: resolveFrom(o),
      toId: resolveTo(o),
      raw: o,
    }));
  }

  const snapshot: LeanixSnapshot = {
    manifest: { version: manifestVersion, raw: manifestRaw },
    files: inv,
    factSheets: {
      applications: parseFactSheet("fact_sheets/applications.csv"),
      it_components: parseFactSheet("fact_sheets/it_components.csv"),
      business_capabilities: parseFactSheet("fact_sheets/business_capabilities.csv"),
      providers: parseFactSheet("fact_sheets/providers.csv"),
      data_objects: parseFactSheet("fact_sheets/data_objects.csv"),
    },
    relations: {
      app_to_capability: parseRelation("relations/app_to_capability.csv"),
      app_to_it_component: parseRelation("relations/app_to_it_component.csv"),
      app_to_provider: parseRelation("relations/app_to_provider.csv"),
      app_to_data_object: parseRelation("relations/app_to_data_object.csv"),
    },
  };

  const counts: Record<string, number> = {
    "fact_sheets/applications.csv": snapshot.factSheets.applications.length,
    "fact_sheets/it_components.csv": snapshot.factSheets.it_components.length,
    "fact_sheets/business_capabilities.csv": snapshot.factSheets.business_capabilities.length,
    "fact_sheets/providers.csv": snapshot.factSheets.providers.length,
    "fact_sheets/data_objects.csv": snapshot.factSheets.data_objects.length,
    "relations/app_to_capability.csv": snapshot.relations.app_to_capability.length,
    "relations/app_to_it_component.csv": snapshot.relations.app_to_it_component.length,
    "relations/app_to_provider.csv": snapshot.relations.app_to_provider.length,
    "relations/app_to_data_object.csv": snapshot.relations.app_to_data_object.length,
  };

  // validation fills errors/warnings
  validateLeanixSnapshot(files, snapshot, { errors, warnings });

  return {
    kind: "leanix_csv",
    version: manifestVersion,
    counts,
    payload: snapshot,
    diagnostics: { errors, warnings },
  };
}

function canonicalLikeToBaseline(g: { nodes?: any[]; edges?: any[] }): { nodes: RfNode[]; edges: RfEdge[] } {
  const nodes = Array.isArray(g.nodes) ? g.nodes : [];
  const edges = Array.isArray(g.edges) ? g.edges : [];

  const rfNodes: RfNode[] = nodes.map((n) => ({
    id: String(n.id),
    type: "emap0",
    position: { x: n.pos?.x ?? 0, y: n.pos?.y ?? 0 },
    data: {
      id: String(n.id),
      kind: String(n.kind),
      attrs: { ...(n.attrs ?? {}) },
    },
    draggable: true,
  }));

  const rfEdges: RfEdge[] = edges.map((e) => ({
    id: String(e.id),
    source: String(e.from),
    target: String(e.to),
    label: String(e.kind),
    data: { kind: e.kind, attrs: e.attrs ?? {} },
  }));

  return { nodes: rfNodes, edges: rfEdges };
}

export function ImportDialog({ open, onClose }: Props) {
  const setBaselineGraph = useGraphStore((s) => s.setBaselineGraph);

  const [phase, setPhase] = useState<ImportPhase>("idle");
  const [errorText, setErrorText] = useState<string | null>(null);

  const [snapshot, setSnapshot] = useState<SourceSnapshot<LeanixSnapshot> | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const fatalErrors = snapshot?.diagnostics.errors ?? [];
  const warnings = snapshot?.diagnostics.warnings ?? [];

  const canMap = snapshot != null && fatalErrors.length === 0;

  const totals = useMemo(() => {
    if (!snapshot) return null;
    const c = snapshot.counts;
    const totalFact = Object.entries(c)
      .filter(([k]) => k.startsWith("fact_sheets/"))
      .reduce((a, [, v]) => a + (Number.isFinite(v) ? v : 0), 0);
    const totalRel = Object.entries(c)
      .filter(([k]) => k.startsWith("relations/"))
      .reduce((a, [, v]) => a + (Number.isFinite(v) ? v : 0), 0);
    return { totalFact, totalRel };
  }, [snapshot]);

  if (!open) return null;

  // Import is allowed in demo/full (diagnostic-only) — but honest:
  // no persistence/exports/sync. Nothing beyond loading a graph into the current session.

  function fixWrapperFolder(files: Record<string, string>): Record<string, string> {
    // If files are under "<root>/fact_sheets/..." then OK.
    // If files are under "<root>/<wrapper>/fact_sheets/..." we strip first segment.
    const keys = Object.keys(files);
    const hasDirect =
      keys.some((k) => k.startsWith("fact_sheets/")) && keys.some((k) => k.startsWith("relations/"));
    if (hasDirect) return files;

    // detect wrapper by finding first occurrence of "/fact_sheets/"
    const idx = keys.findIndex((k) => k.includes("/fact_sheets/"));
    if (idx < 0) return files;

    const k0 = keys[idx];
    const cut = k0.split("/fact_sheets/")[0]; // wrapper prefix
    const prefix = cut.endsWith("/") ? cut : `${cut}/`;

    const out: Record<string, string> = {};
    for (const [k, v] of Object.entries(files)) {
      if (k.startsWith(prefix)) out[k.slice(prefix.length)] = v;
      else out[k] = v;
    }
    return out;
  }

  async function onPickDirectory() {
    setErrorText(null);
    setSnapshot(null);

    setPhase("reading");
    const dir = await pickDirectory();
    if (!dir) {
      setPhase("idle");
      return;
    }

    try {
      const files = await readLeanixCsvSources({ directoryHandle: dir });

      // normalize keys to expected relative structure
      const normalized: Record<string, string> = {};
      for (const [k, v] of Object.entries(files)) {
        const kk = normalizePath(k);
        normalized[kk] = v;
      }

      setPhase("parsing");
      const fixed = fixWrapperFolder(normalized);

      setPhase("validating");
      const snap = buildLeanixSnapshot(fixed);

      setSnapshot(snap);
      setPhase("ready");
    } catch (e: any) {
      setErrorText(String(e?.message ?? e ?? "Import error."));
      setPhase("error");
    }
  }

  async function onPickFiles(e: React.ChangeEvent<HTMLInputElement>) {
    const list = e.target.files;
    e.target.value = ""; // allow re-pick
    if (!list || list.length === 0) return;

    setErrorText(null);
    setSnapshot(null);

    try {
      setPhase("reading");
      const files = await readLeanixCsvSources({ files: list });

      setPhase("parsing");
      const fixed = fixWrapperFolder(files);

      setPhase("validating");
      const snap = buildLeanixSnapshot(fixed);

      setSnapshot(snap);
      setPhase("ready");
    } catch (err: any) {
      setErrorText(String(err?.message ?? err ?? "Import error."));
      setPhase("error");
    }
  }

  function onMapToGraph() {
    if (!snapshot) return;
    if (snapshot.diagnostics.errors.length > 0) return;

    const canonicalLike = mapLeanixToCanonical(snapshot.payload);
    const baseline = canonicalLikeToBaseline(canonicalLike);

    // load into existing store (session only)
    setBaselineGraph(baseline);
    onClose();
  }

  return (
    <div className="modalOverlay" onClick={onClose} role="presentation">
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div className="modalHeader">
          <div>Import</div>
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>

        <div className="modalBody" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ opacity: 0.9 }}>
            Load a source snapshot, validate it, then map it to the current session graph.
            <div style={{ opacity: 0.75, fontSize: 13, marginTop: 6 }}>
              No persistence / exports / sync are implemented here.
            </div>
          </div>

          <div style={{ border: "1px solid rgba(0,0,0,0.08)", borderRadius: 12, padding: 12 }}>
            <div style={{ fontWeight: 800, marginBottom: 6 }}>Source</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
              <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", opacity: 0.9 }}>
                LeanIX CSV (folder/files)
              </div>

              {supportsDirectoryPicker() ? (
                <button
                  className="btn"
                  onClick={onPickDirectory}
                  disabled={phase === "reading" || phase === "parsing" || phase === "validating"}
                >
                  Pick folder…
                </button>
              ) : (
                <button
                  className="btn"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={phase === "reading" || phase === "parsing" || phase === "validating"}
                >
                  Pick files…
                </button>
              )}

              {/* fallback always available */}
              <button
                className="btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={phase === "reading" || phase === "parsing" || phase === "validating"}
              >
                Pick files…
              </button>

              <input
                ref={fileInputRef}
                type="file"
                multiple
                // directory selection for Chromium/WebKit
                {...({ webkitdirectory: "true" } as any)}
                style={{ display: "none" }}
                onChange={onPickFiles}
              />
            </div>

            <div style={{ marginTop: 8, fontSize: 13, opacity: 0.75 }}>
              Expected structure: <code>fact_sheets/*.csv</code>, <code>relations/*.csv</code>, optional{" "}
              <code>manifest.json</code>.
            </div>
          </div>

          <div style={{ border: "1px solid rgba(0,0,0,0.08)", borderRadius: 12, padding: 12 }}>
            <div style={{ fontWeight: 800, marginBottom: 6 }}>Status</div>

            <div style={{ fontSize: 13, opacity: 0.9 }}>
              phase:{" "}
              <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>{phase}</span>
            </div>

            {errorText ? (
              <div style={{ marginTop: 8, whiteSpace: "pre-wrap", fontSize: 13 }}>{errorText}</div>
            ) : null}

            {snapshot ? (
              <div style={{ marginTop: 10, display: "grid", gap: 6 }}>
                <div style={{ fontSize: 13 }}>
                  kind:{" "}
                  <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                    {snapshot.kind}
                  </span>
                </div>
                <div style={{ fontSize: 13 }}>
                  version:{" "}
                  <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                    {snapshot.version}
                  </span>
                </div>

                {totals ? (
                  <div style={{ fontSize: 13 }}>
                    rows:{" "}
                    <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
                      fact={totals.totalFact}, relations={totals.totalRel}
                    </span>
                  </div>
                ) : null}

                <div style={{ marginTop: 8 }}>
                  <div style={{ fontWeight: 700, marginBottom: 4 }}>Counts</div>
                  <div style={{ display: "grid", gap: 3 }}>
                    {Object.entries(snapshot.counts)
                      .sort((a, b) => a[0].localeCompare(b[0]))
                      .map(([k, v]) => (
                        <div key={k} style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                          <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>{k}</span>
                          <span style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>{v}</span>
                        </div>
                      ))}
                  </div>
                </div>

                <div style={{ marginTop: 8 }}>
                  <div style={{ fontWeight: 700, marginBottom: 4 }}>Diagnostics</div>

                  {fatalErrors.length > 0 ? (
                    <div style={{ fontSize: 13 }}>
                      <div style={{ fontWeight: 700, marginBottom: 4 }}>Errors</div>
                      <ul style={{ margin: 0, paddingLeft: 18 }}>
                        {fatalErrors.map((e, i) => (
                          <li key={i} style={{ marginBottom: 2 }}>
                            {e}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : (
                    <div style={{ fontSize: 13, opacity: 0.85 }}>No fatal errors.</div>
                  )}

                  {warnings.length > 0 ? (
                    <div style={{ fontSize: 13, marginTop: 8 }}>
                      <div style={{ fontWeight: 700, marginBottom: 4 }}>Warnings</div>
                      <ul style={{ margin: 0, paddingLeft: 18 }}>
                        {warnings.map((w, i) => (
                          <li key={i} style={{ marginBottom: 2 }}>
                            {w}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </div>
              </div>
            ) : (
              <div style={{ fontSize: 13, opacity: 0.75, marginTop: 6 }}>No snapshot loaded.</div>
            )}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center" }}>
            <div style={{ fontSize: 13, opacity: 0.75 }}>
              Mapping is blocked if fatal validation errors exist.
            </div>

            <button className="btn" onClick={onMapToGraph} disabled={!canMap}>
              Map to graph
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
