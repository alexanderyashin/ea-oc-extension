#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUN-EDHQ-02 — Minimal executable phase space demo (geometry only).

ETS facts (observed):
- axes is a mapping: group_axis -> list[sub_axes]
  e.g., gov: [decision_latency, rule_enforceability, ...]
- No numeric min/max per axis is provided in ETS.

Demo decision (tooling-only, non-semantic):
- Build a deterministic 2D projection over TWO axis-groups (deterministic: first two groups
  in ETS declaration order).
- For each group, define a synthetic coordinate in [0,1] as the mean of synthetic sub-axis
  values in [0,1]. This is purely to produce a reproducible geometric visualization,
  not a new metric claim.

Hard constraints:
- No STOP
- No diagnostics
- No phase transitions
- No new primitives
- ETS.K_EA.v1.1 is immutable
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


RUN_ID = "EDHQ-02"
SEED: int = 13371337
SAMPLE_N: int = 20000

# Deterministic selection rule (per STEP2 suggestion: declaration order)
PROJECTION_RULE = "first_two_axis_groups_in_declaration_order"

# Synthetic coordinate rule (explicit, tooling-only)
SYNTHETIC_COORD_RULE = "mean_of_uniform_subaxes_in_[0,1]"

# Determinism knobs (manifest-required; not strictly needed for plotting rectangle + scatter)
GRID_RESOLUTION: int = 200

# Repo-root robustly derived from script location: .../src/pdf1/phase_space_demo.py -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
ETS_PATH = REPO_ROOT / "configs" / "ETS.K_EA.v1.1.yaml"

OUTPUT_DIR: Path = REPO_ROOT / "results" / "pdf1" / "phase_space_demo"
OUT_PDF = OUTPUT_DIR / "phase_space.pdf"
OUT_MANIFEST = OUTPUT_DIR / "run_manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"ETS not found at: {path}")

    # STEP2 mandated import-check style
    try:
        import yaml  # type: ignore
    except ImportError as e:
        raise ImportError("Missing dependency: yaml (PyYAML).") from e

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("ETS root must be a mapping/dict.")
    return data


def get_axes_groups(ets: Dict[str, Any]) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Returns (group_names_in_declaration_order, mapping group -> list[sub_axes])
    """
    axes = ets.get("axes")
    if not isinstance(axes, dict) or len(axes) < 2:
        raise KeyError("ETS must contain 'axes' as a mapping with at least 2 entries.")

    out: Dict[str, List[str]] = {}
    group_order: List[str] = []

    # Preserve declaration order (YAML mapping order is preserved in Python 3.7+)
    for k, v in axes.items():
        if not isinstance(k, str):
            continue
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            raise TypeError(f"ETS axes.{k} must be a list of strings (sub-axes).")
        group_order.append(k)
        out[k] = list(v)

    if len(out) < 2 or len(group_order) < 2:
        raise ValueError("Need at least 2 axis-groups in ETS to build a 2D projection.")
    return group_order, out


def ensure_outdir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_manifest(payload: Dict[str, Any]) -> None:
    OUT_MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def synthetic_mean_uniform(rng: random.Random, n_sub: int) -> float:
    if n_sub <= 0:
        # Defensive fallback: if a group had no sub-axes, treat as 0.0 (still within [0,1])
        return 0.0
    s = 0.0
    for _ in range(n_sub):
        s += rng.random()  # uniform in [0,1)
    return s / float(n_sub)


def main() -> int:
    ets = load_yaml(ETS_PATH)
    group_order, axes_groups = get_axes_groups(ets)

    # Deterministic: first two axis groups in ETS declaration order
    g1, g2 = group_order[0], group_order[1]
    sub1, sub2 = axes_groups[g1], axes_groups[g2]

    # STEP2 mandated import-check style for matplotlib
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as e:
        raise ImportError("Missing dependency: matplotlib.") from e

    rng = random.Random(SEED)

    # Synthetic sampling (reproducible, tooling-only)
    xs: List[float] = []
    ys: List[float] = []
    n1 = len(sub1)
    n2 = len(sub2)
    for _ in range(SAMPLE_N):
        xs.append(synthetic_mean_uniform(rng, n1))
        ys.append(synthetic_mean_uniform(rng, n2))

    ensure_outdir()

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Admissible square for synthetic normalized coordinates
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], linewidth=1.5)

    # Scatter of synthetic samples (no semantic meaning; visualization only)
    ax.scatter(xs, ys, s=1)

    # Axis labels must match ETS (no new symbols): we use ETS group names.
    ax.set_xlabel(g1)
    ax.set_ylabel(g2)
    ax.set_title("Ω(K_EA): admissible region (2D projection over ETS axis-groups)")

    fig.tight_layout()
    fig.savefig(OUT_PDF)
    plt.close(fig)

    script_path = REPO_ROOT / "src" / "pdf1" / "phase_space_demo.py"

    # STEP2 requires ETS SHA256 in manifest
    ets_sha = sha256_file(ETS_PATH)

    # STEP2 required manifest fields
    manifest: Dict[str, Any] = {
        "ets_path": os.path.relpath(ETS_PATH, REPO_ROOT),
        "ets_sha256": ets_sha,
        "axes_used": [g1, g2],
        # No numeric min/max provided in ETS; synthetic normalized bounds used for visualization only.
        "bounds": {
            g1: {"min": 0.0, "max": 1.0},
            g2: {"min": 0.0, "max": 1.0},
        },
        "seed": SEED,
        "grid_resolution": GRID_RESOLUTION,
        "python_version": sys.version,
        "script_sha256": sha256_file(script_path),
        "output_files": [
            os.path.relpath(OUT_PDF, REPO_ROOT),
            os.path.relpath(OUT_MANIFEST, REPO_ROOT),
        ],
        # Extra metadata (allowed; still non-semantic)
        "run_id": RUN_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sample_n": SAMPLE_N,
        "projection_rule": PROJECTION_RULE,
        "synthetic_coordinate_rule": SYNTHETIC_COORD_RULE,
        "axis_groups_used": [
            {"group": g1, "sub_axes": sub1},
            {"group": g2, "sub_axes": sub2},
        ],
        "guarantees": {
            "no_stop": True,
            "no_diagnostics": True,
            "no_phase_transitions": True,
            "no_new_primitives": True,
            "geometry_only": True,
        },
    }

    write_manifest(manifest)

    print("[EDHQ-02] OK")
    print(f"ETS: {manifest['ets_path']}")
    print(f"ETS sha256: {manifest['ets_sha256']}")
    print(f"Axis groups used: {g1} (n={len(sub1)}), {g2} (n={len(sub2)})")
    print(f"Outputs: {os.path.relpath(OUT_PDF, REPO_ROOT)}, manifest written.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"[EDHQ-02] ERROR: {e}", file=sys.stderr)
        raise
