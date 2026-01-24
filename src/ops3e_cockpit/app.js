/*
OPS-CHILD-E — Read-Only Diagnostic Cockpit

HARD BOUNDARIES:
- READ-ONLY: no writes, no engine calls.
- SNAPSHOT-ONLY: renders existing artefacts only.
- NO STATE: no localStorage/sessionStorage/IndexedDB/cookies.
- STOP TRANSPARENT: STOP is always shown when present.

INPUTS (ONLY):
- ./data/trace.json (default)
- ./data/graph.json (default) OR ./data/graph.dot
- OPTIONAL: ./data/spec.yaml
- OPTIONAL: ./data/manifest.json (discovery only; read-only)
*/

"use strict";

const PATHS = {
  trace: "./data/trace.json",
  graphJson: "./data/graph.json",
  graphDot: "./data/graph.dot",
  specYaml: "./data/spec.yaml",
  manifest: "./data/manifest.json"
};

const $ = (id) => document.getElementById(id);

function setLoadState(kind, note) {
  const pill = $("loadState");
  pill.className = "pill " + (kind || "info");
  pill.textContent = (kind || "info").toUpperCase();
  $("loadNote").textContent = note || "";
}

function showDiag(msg) {
  const card = $("diagCard");
  const ul = $("diagList");
  card.hidden = false;
  const li = document.createElement("li");
  li.textContent = msg;
  ul.appendChild(li);
}

async function fetchText(path) {
  const r = await fetch(path, { cache: "no-store", method: "GET" });
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${path}`);
  return await r.text();
}

async function fetchJson(path) {
  const txt = await fetchText(path);
  return JSON.parse(txt);
}

function safeStr(x, fallback = "—") {
  if (x === null || x === undefined) return fallback;
  const s = String(x);
  return s.length ? s : fallback;
}

function classifyFinal(s) {
  const u = (s || "").toUpperCase();
  if (u === "STOP") return ["stop", "STOP"];
  if (u === "END") return ["ok", "END"];
  return ["info", safeStr(s, "UNKNOWN")];
}

function classifyStepStatus(s) {
  const u = (s || "").toUpperCase();
  if (u === "STOP") return ["stop", "STOP"];
  if (u === "WARN") return ["warn", "WARN"];
  if (u === "OK") return ["ok", "OK"];
  return ["info", safeStr(s, "UNKNOWN")];
}

/* ---------------- TRACE RENDER ---------------- */

function renderTrace(trace) {
  const final = trace?.final || {};
  const [cls, label] = classifyFinal(final.status);

  const finalStatus = $("finalStatus");
  finalStatus.className = "pill " + cls;
  finalStatus.textContent = label;

  const reasonFallback = (label === "STOP") ? "STOP (no reason provided in trace)" : "—";
  $("finalReason").textContent = safeStr(final.reason, reasonFallback);

  const steps = Array.isArray(trace?.steps) ? trace.steps : [];
  if (!Array.isArray(trace?.steps)) showDiag("trace: missing/invalid 'steps' array.");

  // Timeline ticks
  const ticks = $("ticks");
  ticks.innerHTML = "";
  for (let i = 0; i < steps.length; i++) {
    const st = steps[i] || {};
    const [scls] = classifyStepStatus(st.status);
    const d = document.createElement("div");
    d.className = "tick " + scls;
    d.title = `#${safeStr(st.i, i)} ${safeStr(st.status)} op=${safeStr(st.op)}`;
    ticks.appendChild(d);
  }

  // Step list
  const ol = $("steps");
  ol.innerHTML = "";
  steps.forEach((st, idx) => {
    const li = document.createElement("li");
    li.className = "step";

    const head = document.createElement("div");
    head.className = "stepHead";

    const left = document.createElement("div");
    left.className = "stepLeft";

    const [scls, slabel] = classifyStepStatus(st?.status);

    const pill = document.createElement("span");
    pill.className = "pill " + scls;
    pill.textContent = slabel;

    const index = document.createElement("span");
    index.className = "stepIndex";
    index.textContent = `#${safeStr(st?.i, idx)}`;

    const op = document.createElement("span");
    op.className = "stepOp";
    op.textContent = `op=${safeStr(st?.op, "—")}`;

    left.appendChild(pill);
    left.appendChild(index);
    left.appendChild(op);

    const right = document.createElement("span");
    right.className = "muted small";
    right.textContent = safeStr(st?.ts, "");

    head.appendChild(left);
    head.appendChild(right);
    li.appendChild(head);

    const note = safeStr(st?.note, "");
    if (note) {
      const n = document.createElement("div");
      n.className = "stepNote";
      n.textContent = note;
      li.appendChild(n);
    }

    ol.appendChild(li);
  });

  $("traceMeta").textContent = `Steps: ${steps.length}`;
}

/* ---------------- GRAPH RENDER (STATIC SVG) ---------------- */

function topoLayer(nodes, edges) {
  const ids = new Set(nodes.map(n => n.id));
  const indeg = new Map();
  const out = new Map();
  ids.forEach(id => { indeg.set(id, 0); out.set(id, []); });

  edges.forEach(e => {
    if (!ids.has(e.from) || !ids.has(e.to)) return;
    indeg.set(e.to, (indeg.get(e.to) || 0) + 1);
    out.get(e.from).push(e.to);
  });

  let q = Array.from(ids).filter(id => (indeg.get(id) || 0) === 0).sort();
  const layer = new Map();
  ids.forEach(id => layer.set(id, 0));

  while (q.length) {
    const id = q.shift();
    const nexts = (out.get(id) || []).slice().sort();
    nexts.forEach(v => {
      layer.set(v, Math.max(layer.get(v) || 0, (layer.get(id) || 0) + 1));
      indeg.set(v, (indeg.get(v) || 0) - 1);
      if ((indeg.get(v) || 0) === 0) {
        q.push(v);
        q.sort();
      }
    });
  }
  return layer;
}

function renderGraphFromJson(graph) {
  const svg = $("graphSvg");
  $("graphRaw").textContent = JSON.stringify(graph, null, 2);

  const nodes = Array.isArray(graph?.nodes) ? graph.nodes : [];
  const edges = Array.isArray(graph?.edges) ? graph.edges : [];
  if (!Array.isArray(graph?.nodes)) showDiag("graph: missing/invalid 'nodes' array.");
  if (!Array.isArray(graph?.edges)) showDiag("graph: missing/invalid 'edges' array.");

  const stopIds = new Set();
  nodes.forEach(n => {
    const kind = (n.kind || "").toUpperCase();
    const flags = (n.flags || []).map(x => String(x).toUpperCase());
    if (kind === "STOP") stopIds.add(n.id);
    if (flags.includes("STOP")) stopIds.add(n.id);
    if (String(n.id).toUpperCase() === "STOP") stopIds.add(n.id);
  });

  const layer = topoLayer(nodes, edges);
  const byRank = new Map();
  nodes.forEach(n => {
    const r = layer.get(n.id) || 0;
    if (!byRank.has(r)) byRank.set(r, []);
    byRank.get(r).push(n);
  });

  for (const [r, arr] of byRank.entries()) {
    arr.sort((a, b) => String(a.id).localeCompare(String(b.id)));
  }

  const width = svg.clientWidth || 1200;
  const height = 520;
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  while (svg.firstChild) svg.removeChild(svg.firstChild);

  const ns = "http://www.w3.org/2000/svg";
  const mk = (tag) => document.createElementNS(ns, tag);

  const defs = mk("defs");
  const marker = mk("marker");
  marker.setAttribute("id", "arrow");
  marker.setAttribute("markerWidth", "10");
  marker.setAttribute("markerHeight", "8");
  marker.setAttribute("refX", "9");
  marker.setAttribute("refY", "4");
  marker.setAttribute("orient", "auto");
  const tip = mk("path");
  tip.setAttribute("d", "M0,0 L10,4 L0,8 Z");
  tip.setAttribute("fill", "rgba(230,232,239,.75)");
  marker.appendChild(tip);
  defs.appendChild(marker);
  svg.appendChild(defs);

  const ranks = Array.from(byRank.keys()).sort((a, b) => a - b);
  const marginX = 30, marginY = 30;
  const nodeW = 160, nodeH = 40;
  const gapX = 20, gapY = 72;

  const pos = new Map();
  ranks.forEach((r, idxR) => {
    const y = marginY + idxR * gapY;
    const arr = byRank.get(r) || [];
    const totalW = arr.length * nodeW + Math.max(0, arr.length - 1) * gapX;
    let x0 = Math.max(marginX, (width - totalW) / 2);
    arr.forEach((n, j) => {
      pos.set(n.id, { x: x0 + j * (nodeW + gapX), y });
    });
  });

  edges.forEach(e => {
    const a = pos.get(e.from);
    const b = pos.get(e.to);
    if (!a || !b) return;

    const x1 = a.x + nodeW / 2;
    const y1 = a.y + nodeH;
    const x2 = b.x + nodeW / 2;
    const y2 = b.y;

    const midY = (y1 + y2) / 2;
    const d = `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;

    const path = mk("path");
    path.setAttribute("d", d);
    path.setAttribute("fill", "none");

    const flags = (e.flags || []).map(x => String(x).toUpperCase());
    const forbidden = flags.includes("FORBIDDEN");

    path.setAttribute("stroke", forbidden ? "rgba(255,92,119,.85)" : "rgba(230,232,239,.45)");
    path.setAttribute("stroke-width", forbidden ? "2.2" : "1.4");
    path.setAttribute("marker-end", "url(#arrow)");
    svg.appendChild(path);

    if (forbidden) {
      const tx = mk("text");
      tx.textContent = "FORBIDDEN";
      tx.setAttribute("x", String((x1 + x2) / 2 + 6));
      tx.setAttribute("y", String(midY - 6));
      tx.setAttribute("fill", "rgba(255,92,119,.9)");
      tx.setAttribute("font-size", "11");
      tx.setAttribute("font-family", "ui-monospace, monospace");
      svg.appendChild(tx);
    }
  });

  nodes.forEach(n => {
    const p = pos.get(n.id) || { x: marginX, y: marginY };
    const g = mk("g");

    const rect = mk("rect");
    rect.setAttribute("x", String(p.x));
    rect.setAttribute("y", String(p.y));
    rect.setAttribute("rx", "12");
    rect.setAttribute("ry", "12");
    rect.setAttribute("width", String(nodeW));
    rect.setAttribute("height", String(nodeH));

    const flags = (n.flags || []).map(x => String(x).toUpperCase());
    const forbidden = flags.includes("FORBIDDEN");
    const isStop = stopIds.has(n.id);

    const stroke = isStop ? "rgba(255,92,119,.95)"
                : forbidden ? "rgba(255,92,119,.65)"
                : "rgba(230,232,239,.30)";
    rect.setAttribute("stroke", stroke);
    rect.setAttribute("stroke-width", isStop ? "2.6" : "1.4");
    rect.setAttribute("fill", "rgba(0,0,0,.18)");
    g.appendChild(rect);

    const label = mk("text");
    label.setAttribute("x", String(p.x + 10));
    label.setAttribute("y", String(p.y + 25));
    label.setAttribute("fill", "rgba(230,232,239,.90)");
    label.setAttribute("font-size", "12");
    label.setAttribute("font-family", "ui-monospace, monospace");
    label.textContent = safeStr(n.label, n.id);
    g.appendChild(label);

    if (isStop) {
      const tag = mk("text");
      tag.setAttribute("x", String(p.x + nodeW - 52));
      tag.setAttribute("y", String(p.y + 25));
      tag.setAttribute("fill", "rgba(255,92,119,.95)");
      tag.setAttribute("font-size", "12");
      tag.setAttribute("font-family", "ui-monospace, monospace");
      tag.textContent = "STOP";
      g.appendChild(tag);
    } else if (forbidden) {
      const tag = mk("text");
      tag.setAttribute("x", String(p.x + nodeW - 86));
      tag.setAttribute("y", String(p.y + 25));
      tag.setAttribute("fill", "rgba(255,92,119,.85)");
      tag.setAttribute("font-size", "11");
      tag.setAttribute("font-family", "ui-monospace, monospace");
      tag.textContent = "FORBIDDEN";
      g.appendChild(tag);
    }

    svg.appendChild(g);
  });
}

/* ---------------- DISCOVERY (MANIFEST) ---------------- */

function normalizeManifest(m) {
  // expected minimal schema (optional):
  // { "trace": "trace.json", "graph": "graph.json"|"graph.dot", "spec": "spec.yaml" }
  if (!m || typeof m !== "object") return null;
  const trace = (typeof m.trace === "string") ? m.trace : null;
  const graph = (typeof m.graph === "string") ? m.graph : null;
  const spec  = (typeof m.spec === "string")  ? m.spec  : null;
  if (!trace && !graph && !spec) return null;
  return { trace, graph, spec };
}

async function loadOptionalSpec(specPath) {
  try {
    const txt = await fetchText(specPath);
    $("specRaw").textContent = txt;
  } catch {
    $("specRaw").textContent = "—";
  }
}

async function tryLoadArtefacts(tracePath, graphPath, graphFallbackDot) {
  let any = false;

  // TRACE
  try {
    const trace = await fetchJson(tracePath);
    renderTrace(trace);
    any = true;
  } catch (e) {
    showDiag(`Failed to load trace (${tracePath}): ${e.message}`);
  }

  // GRAPH
  try {
    if (graphPath && graphPath.toLowerCase().endsWith(".dot")) {
      const dot = await fetchText(graphPath);
      $("graphRaw").textContent = dot;
      showDiag("Graph loaded as raw DOT text (no Graphviz execution). Prefer JSON for SVG DAG.");
      any = true;
    } else {
      const graph = await fetchJson(graphPath);
      renderGraphFromJson(graph);
      any = true;
    }
  } catch (e) {
    // fallback to dot if provided
    if (graphFallbackDot) {
      try {
        const dot = await fetchText(graphFallbackDot);
        $("graphRaw").textContent = dot;
        showDiag("graph.dot fallback loaded as raw text only (no Graphviz execution).");
        any = true;
      } catch (e2) {
        showDiag(`Failed to load graph (${graphPath}) and fallback (${graphFallbackDot}): ${e2.message}`);
      }
    } else {
      showDiag(`Failed to load graph (${graphPath}): ${e.message}`);
    }
  }

  return any;
}

async function loadAll() {
  $("tracePath").textContent = PATHS.trace;
  $("graphPath").textContent = `${PATHS.graphJson} (preferred) or ${PATHS.graphDot} (fallback)`;
  $("specPath").textContent = `${PATHS.specYaml} (optional), ${PATHS.manifest} (optional)`;

  setLoadState("info", "Fetching artefacts (GET only)…");

  // First: optional manifest discovery
  let manifest = null;
  try {
    const m = await fetchJson(PATHS.manifest);
    manifest = normalizeManifest(m);
    if (manifest) {
      showDiag(`manifest.json loaded (discovery): trace=${manifest.trace || "—"}, graph=${manifest.graph || "—"}, spec=${manifest.spec || "—"}`);
    } else {
      showDiag("manifest.json present but did not match expected schema; using defaults.");
    }
  } catch {
    // normal: no manifest
  }

  // Determine paths
  const tracePath = manifest?.trace ? `./data/${manifest.trace}` : PATHS.trace;
  const graphPath = manifest?.graph ? `./data/${manifest.graph}` : PATHS.graphJson;
  const specPath  = manifest?.spec  ? `./data/${manifest.spec}`  : PATHS.specYaml;

  const any = await tryLoadArtefacts(tracePath, graphPath, PATHS.graphDot);
  await loadOptionalSpec(specPath);

  if (any) {
    setLoadState("ok", "Snapshot loaded. No actions available (read-only).");
  } else {
    setLoadState("stop", "No inputs loaded. Place artefacts into ./data/ and refresh.");
    showDiag("Expected default filenames: data/trace.json and data/graph.json (or data/graph.dot).");
    showDiag("Search in repo returned none → artefacts likely not produced yet, or have different names.");
    showDiag("If OPS-3A outputs different names, drop data/manifest.json to point to them (read-only).");
  }
}

window.addEventListener("DOMContentLoaded", loadAll);
