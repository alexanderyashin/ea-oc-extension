"use strict";

/*
OPS-CHILD-E — Read-Only Diagnostic Cockpit

BOUNDARIES:
- READ-ONLY (in-memory file reading only)
- NO ENGINE CALLS
- NO WRITES
- NO PERSISTENCE (no localStorage/sessionStorage/IndexedDB/cookies/SW)
- SNAPSHOT-ONLY visualization
*/

const PATHS = {
  trace: "./data/trace.json",
  graphJson: "./data/graph.json",
  graphDot: "./data/graph.dot",
  specYaml: "./data/spec.yaml",
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

function clearDiag() {
  const card = $("diagCard");
  const ul = $("diagList");
  ul.innerHTML = "";
  card.hidden = true;
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

/* ---------------- FILE PICKER / DROP (IN-MEMORY ONLY) ---------------- */

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result || ""));
    r.onerror = () => reject(new Error("FileReader error"));
    r.readAsText(file);
  });
}

function looksLikeTraceJson(obj) {
  return obj && typeof obj === "object" && Array.isArray(obj.steps);
}

function looksLikeGraphJson(obj) {
  return obj && typeof obj === "object" && Array.isArray(obj.nodes) && Array.isArray(obj.edges);
}

async function loadFromFiles(files) {
  clearDiag();
  setLoadState("info", "Reading selected files (in-memory)…");

  let traceObj = null;
  let graphObj = null;
  let graphDot = null;
  let specTxt = null;

  const fileArr = Array.from(files || []);
  if (fileArr.length === 0) {
    setLoadState("warn", "No files selected.");
    return false;
  }

  for (const f of fileArr) {
    const name = (f.name || "").toLowerCase();
    const txt = await readFileAsText(f);

    if (name.endsWith(".dot")) {
      graphDot = txt;
      continue;
    }
    if (name.endsWith(".yaml") || name.endsWith(".yml")) {
      specTxt = txt;
      continue;
    }
    if (name.endsWith(".json")) {
      try {
        const obj = JSON.parse(txt);
        if (!traceObj && looksLikeTraceJson(obj)) { traceObj = obj; continue; }
        if (!graphObj && looksLikeGraphJson(obj)) { graphObj = obj; continue; }

        // name-based fallback
        if (!traceObj && name.includes("trace")) traceObj = obj;
        else if (!graphObj && name.includes("graph")) graphObj = obj;
        else showDiag(`JSON file not recognized (kept ignored): ${f.name}`);
      } catch {
        showDiag(`Invalid JSON: ${f.name}`);
      }
      continue;
    }

    // unknown
    showDiag(`Ignored file type: ${f.name}`);
  }

  if (!traceObj) showDiag("No trace.json detected. Expected JSON with {steps:[...]}.");
  if (!graphObj && !graphDot) showDiag("No graph detected. Provide graph.json ({nodes,edges}) or graph.dot.");

  // render
  if (traceObj) renderTrace(traceObj);

  if (graphObj) {
    renderGraphFromJson(graphObj);
  } else if (graphDot) {
    $("graphRaw").textContent = graphDot;
    // keep SVG empty (no Graphviz execution)
    showDiag("Graph loaded as raw DOT text only (no Graphviz execution).");
  }

  $("specRaw").textContent = specTxt ? specTxt : "—";

  const ok = Boolean(traceObj || graphObj || graphDot || specTxt);
  setLoadState(ok ? "ok" : "stop", ok ? `Loaded ${fileArr.length} file(s).` : "No usable inputs.");
  return ok;
}

/* ---------------- STATIC FALLBACK (OPTIONAL) ---------------- */

async function loadStaticFallbackIfNoUpload() {
  // keep old behavior: try ./data/*
  try {
    const trace = await fetchJson(PATHS.trace);
    renderTrace(trace);
    setLoadState("ok", "Loaded static ./data/trace.json");
    return true;
  } catch (e) {
    showDiag(`Static trace missing: ${e.message}`);
  }

  try {
    const graph = await fetchJson(PATHS.graphJson);
    renderGraphFromJson(graph);
    setLoadState("ok", "Loaded static ./data/graph.json");
    return true;
  } catch (e) {
    // fallback to dot
    try {
      const dot = await fetchText(PATHS.graphDot);
      $("graphRaw").textContent = dot;
      showDiag("Static graph.dot loaded as raw text only (no Graphviz execution).");
      setLoadState("ok", "Loaded static ./data/graph.dot");
      return true;
    } catch (e2) {
      showDiag(`Static graph missing: ${e2.message}`);
    }
  }

  try {
    const spec = await fetchText(PATHS.specYaml);
    $("specRaw").textContent = spec;
  } catch {
    $("specRaw").textContent = "—";
  }

  setLoadState("warn", "No static inputs found. Use file picker / drag & drop.");
  return false;
}

/* ---------------- WIRE UI ---------------- */

function wireUploadUI() {
  const input = $("fileInput");
  const zone = $("dropZone");

  input.addEventListener("change", async () => {
    await loadFromFiles(input.files);
  });

  // drag & drop (in-memory only)
  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("dropActive");
  });
  zone.addEventListener("dragleave", () => zone.classList.remove("dropActive"));
  zone.addEventListener("drop", async (e) => {
    e.preventDefault();
    zone.classList.remove("dropActive");
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length) {
      await loadFromFiles(dt.files);
    }
  });
}

window.addEventListener("DOMContentLoaded", async () => {
  wireUploadUI();
  clearDiag();
  setLoadState("info", "IDLE");
  // optional fallback if someone uses ./data/ mode
  await loadStaticFallbackIfNoUpload();
});
