#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUN-EDHQ-02 — Minimal executable phase space demo (geometry only).

ETS facts (observed):
- axes is a mapping: group_axis -> list[sub_axes]
  e.g., gov: [decision_latency, rule_enforceability, ...]
- No numeric min/max per axis is provided in ETS.

Demo decision (tooling-only, non-semantic):
- Build a 2D projection over TWO axis-groups (deterministic: first two groups lexicographically).
- For each group, define a synthetic coordinate in [0,1] as the mean of synthetic sub-axis values in [0,1].
  This is purely to produce a reproducible geometric visualization, not a new metric claim.

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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


RUN_ID = "EDHQ-02"
SEED: int = 13371337
SAMPLE_N: int = 20000

# Deterministic group selection rule
PROJECTION_RULE = "lexicographic_first_two_axis_groups"

# Synthetic coordinate rule (explicit, tooling-only)
SYNTHETIC_COORD_RULE = "mean_of_uniform_subaxes_in_[0,1]"

REPO_ROOT = Path.cwd()
ETS_PATH = REPO_ROOT / "configs" / "ETS.K_EA.v1.1.yaml"

OUTPUT_DIR: Path = REPO_ROOT / "results" / "pdf1" / "phase_space_demo"
OUT_PNG = OUTPUT_DIR / "phase_space.png"
OUT_PDF = OUTPUT_DIR / "phase_space.pdf"
OUT_SVG = OUTPUT_DIR / "phase_space.svg"
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

    import yaml  # type: ignore

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("ETS root must be a mapping/dict.")
    return data


def get_axes_groups(ets: Dict[str, Any]) -> Dict[str, List[str]]:
    axes = ets.get("axes")
    if not isinstance(axes, dict) or len(axes) < 2:
        raise KeyError("ETS must contain 'axes' as a mapping with at least 2 entries.")

    out: Dict[str, List[str]] = {}
    for k, v in axes.items():
        if not isinstance(k, str):
            continue
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            raise TypeError(f"ETS axes.{k} must be a list of strings (sub-axes).")
        out[k] = list(v)

    if len(out) < 2:
        raise ValueError("Need at least 2 axis-groups in ETS to build a 2D projection.")
    return out


def ensure_outdir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_manifest(payload: Dict[str, Any]) -> None:
    OUT_MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    ets = load_yaml(ETS_PATH)
    axes_groups = get_axes_groups(ets)

    group_names = sorted(axes_groups.keys())
    g1, g2 = group_names[0], group_names[1]
    sub1, sub2 = axes_groups[g1], axes_groups[g2]

    # Synthetic sample (reproducible)
    import numpy as np
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(SEED)

    # For each sample: draw uniform values for each sub-axis in [0,1], aggregate by mean.
    x_sub = rng.uniform(0.0, 1.0, size=(SAMPLE_N, len(sub1)))
    y_sub = rng.uniform(0.0, 1.0, size=(SAMPLE_N, len(sub2)))
    x = x_sub.mean(axis=1)
    y = y_sub.mean(axis=1)

    ensure_outdir()

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Admissible square for synthetic normalized coordinates
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], linewidth=1.5)

    ax.scatter(x, y, s=1)

    # Axis labels must match A_EA (no new symbols): we use ETS group names.
    ax.set_xlabel(g1)
    ax.set_ylabel(g2)
    ax.set_title("Ω(K_EA): admissible region (2D projection over ETS axis-groups)")

    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=200)
    fig.savefig(OUT_PDF)
    fig.savefig(OUT_SVG)
    plt.close(fig)

    script_path = REPO_ROOT / "src" / "pdf1" / "phase_space_demo.py"

    manifest = {
        "run_id": RUN_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "sample_n": SAMPLE_N,
        "ets_path": os.path.relpath(ETS_PATH, REPO_ROOT),
        "projection_rule": PROJECTION_RULE,
        "synthetic_coordinate_rule": SYNTHETIC_COORD_RULE,
        "axis_groups_used": [
            {"group": g1, "sub_axes": sub1},
            {"group": g2, "sub_axes": sub2},
        ],
        "script_sha256": sha256_file(script_path),
        "outputs": [
            os.path.relpath(OUT_PNG, REPO_ROOT),
            os.path.relpath(OUT_PDF, REPO_ROOT),
            os.path.relpath(OUT_SVG, REPO_ROOT),
            os.path.relpath(OUT_MANIFEST, REPO_ROOT),
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
    print(f"Axis groups used: {g1} (n={len(sub1)}), {g2} (n={len(sub2)})")
    print(f"Outputs: {os.path.relpath(OUT_PDF, REPO_ROOT)} (and .png/.svg), manifest written.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"[EDHQ-02] ERROR: {e}", file=sys.stderr)
        raise
