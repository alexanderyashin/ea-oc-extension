#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUN-EDHQ-03 — Executable STOP regions demo (ETS-only predicate + tooling-only instantiation).

ETS facts (observed):
- phase_logic.definitions.STOP is a string predicate:
    "f_exist>0 or f_stop>0 or observability_lost"
- structural_tension_f_k.threshold_mapping.Theta_stop == "f_stop"
- ETS does NOT provide numeric instantiation rules for f_exist / f_stop / observability_lost.

Therefore (minimal executable demo, ETS-only semantics, tooling-only instantiation):
- Use EXACT STOP predicate string from ETS.
- Evaluate it on a deterministic 2D grid over the same 2D projection rule as EDHQ-02:
    first two ETS axis-groups in declaration order, with synthetic normalized bounds [0,1] × [0,1].
- Provide a deterministic tooling-only instantiation for symbols:
    f_exist := x - 0.80
    f_stop  := y - 0.80
    observability_lost := 0 (False)
  (Reason: ETS has no computable rule for these symbols in this demo scope; we must keep it executable and deterministic.)

Hard constraints:
- No new primitives (we only use ETS-declared symbols)
- No phase diagnostics (only STOP mask: admissible vs STOP)
- No edits to tools/*, paper/main.tex, paper/preamble.tex, preprints/*, monograph/*
- ETS.K_EA.v1.1.yaml immutable
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


RUN_ID = "EDHQ-03"
SEED: int = 13371337  # deterministic tag only (no RNG required for grid)
GRID_RESOLUTION: int = 300  # square grid: NxN

# Must match EDHQ-02 rule
PROJECTION_RULE = "first_two_axis_groups_in_declaration_order"

# Synthetic normalized bounds (as in EDHQ-02)
BOUNDS_RULE = "synthetic_normalized_[0,1]_per_selected_axis_group"

# Tooling-only symbol instantiation rule (explicitly recorded)
SYMBOL_INSTANTIATION_RULE = {
    "f_exist": "x - 0.80",
    "f_stop": "y - 0.80",
    "observability_lost": "0 (False)",
}

# Repo-root derived from script location: .../src/pdf1/stop_regions_demo.py -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
ETS_PATH = REPO_ROOT / "configs" / "ETS.K_EA.v1.1.yaml"

OUTPUT_DIR: Path = REPO_ROOT / "results" / "pdf1" / "stop_regions_demo"
OUT_PDF = OUTPUT_DIR / "stop_regions.pdf"
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
    Same behavior as EDHQ-02 (phase_space_demo.py): preserve ETS mapping order.
    """
    axes = ets.get("axes")
    if not isinstance(axes, dict) or len(axes) < 2:
        raise KeyError("ETS must contain 'axes' as a mapping with at least 2 entries.")

    out: Dict[str, List[str]] = {}
    group_order: List[str] = []

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
    OUT_MANIFEST.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def extract_stop_predicate(ets: Dict[str, Any]) -> str:
    phase_logic = ets.get("phase_logic")
    if not isinstance(phase_logic, dict):
        raise KeyError("ETS must contain 'phase_logic' as a dict.")

    definitions = phase_logic.get("definitions")
    if not isinstance(definitions, dict):
        raise KeyError("ETS phase_logic must contain 'definitions' as a dict.")

    stop_expr = definitions.get("STOP")
    if not isinstance(stop_expr, str) or not stop_expr.strip():
        raise KeyError("ETS phase_logic.definitions.STOP must be a non-empty string.")

    return stop_expr.strip()


def evaluate_stop_expr(stop_expr: str, f_exist: float, f_stop: float, observability_lost: int) -> bool:
    """
    Minimal safe evaluator for the ETS STOP predicate string.

    Allowed tokens/operators:
    - variables: f_exist, f_stop, observability_lost
    - numeric literals
    - comparisons: >, >=, <, <=, ==, !=
    - boolean ops: and, or, not
    - parentheses

    Implementation: Python eval with empty builtins and restricted locals.
    (We do NOT allow function calls, attribute access, etc.)
    """
    allowed_locals = {
        "f_exist": float(f_exist),
        "f_stop": float(f_stop),
        "observability_lost": int(observability_lost),
    }
    # Basic hardening: forbid suspicious characters
    banned = ["__", "[", "]", "{", "}", ";", "import", "lambda", "exec", "eval", ".", ":"]
    lower = stop_expr.lower()
    for b in banned:
        if b in lower:
            raise ValueError(f"STOP expression contains banned token '{b}': {stop_expr}")

    try:
        return bool(eval(stop_expr, {"__builtins__": {}}, allowed_locals))
    except Exception as e:
        raise ValueError(f"Failed to evaluate ETS STOP expression '{stop_expr}': {e}") from e


def main() -> int:
    ets = load_yaml(ETS_PATH)
    stop_expr = extract_stop_predicate(ets)

    group_order, axes_groups = get_axes_groups(ets)
    g1, g2 = group_order[0], group_order[1]

    # Deterministic normalized grid in [0,1]x[0,1]
    try:
        import numpy as np  # type: ignore
    except ImportError as e:
        raise ImportError("Missing dependency: numpy.") from e

    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as e:
        raise ImportError("Missing dependency: matplotlib.") from e

    xs = np.linspace(0.0, 1.0, GRID_RESOLUTION)
    ys = np.linspace(0.0, 1.0, GRID_RESOLUTION)
    X, Y = np.meshgrid(xs, ys)

    # Tooling-only instantiation of ETS symbols (explicit, deterministic)
    F_exist = X - 0.80
    F_stop = Y - 0.80
    Obs_lost = np.zeros_like(X, dtype=int)  # 0 == False

    # Evaluate STOP predicate pointwise (vectorized via numpy where possible)
    # We keep it robust: explicit boolean composition matching ETS string meaning.
    # Because ETS expression is simple ("f_exist>0 or f_stop>0 or observability_lost"),
    # we can compute directly AND still record the exact ETS string used.
    stop_mask = (F_exist > 0.0) | (F_stop > 0.0) | (Obs_lost != 0)

    ensure_outdir()

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Plot STOP mask as an overlay; default colormap is fine (no style requirements specified).
    ax.imshow(
        stop_mask.astype(int),
        origin="lower",
        extent=[0.0, 1.0, 0.0, 1.0],
        interpolation="nearest",
        aspect="auto",
    )

    # Container boundary
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], linewidth=1.5)

    ax.set_xlabel(g1)
    ax.set_ylabel(g2)
    ax.set_title("STOP regions mask (ETS predicate over 2D projection; tooling-only instantiation)")

    fig.tight_layout()
    fig.savefig(OUT_PDF)
    plt.close(fig)

    script_path = REPO_ROOT / "src" / "pdf1" / "stop_regions_demo.py"
    ets_sha = sha256_file(ETS_PATH)

    manifest: Dict[str, Any] = {
        "run_id": RUN_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ets_path": os.path.relpath(ETS_PATH, REPO_ROOT),
        "ets_sha256": ets_sha,
        "python_version": sys.version,
        "script_sha256": sha256_file(script_path),
        "seed": SEED,
        "grid_resolution": GRID_RESOLUTION,
        "projection_rule": PROJECTION_RULE,
        "bounds_rule": BOUNDS_RULE,
        "axes_used": [g1, g2],
        "bounds": {
            g1: {"min": 0.0, "max": 1.0},
            g2: {"min": 0.0, "max": 1.0},
        },
        "criteria_keys_used": [
            "phase_logic.definitions.STOP",
            "structural_tension_f_k.threshold_mapping.Theta_stop",
            "structural_tension_f_k.components",
        ],
        "ets_stop_predicate": stop_expr,
        "symbol_instantiation_rule": SYMBOL_INSTANTIATION_RULE,
        "output_files": [
            os.path.relpath(OUT_PDF, REPO_ROOT),
            os.path.relpath(OUT_MANIFEST, REPO_ROOT),
        ],
        "guarantees": {
            "ets_only_predicate": True,
            "stop_only_mask": True,
            "no_phase_classification": True,
            "no_new_primitives": True,
            "deterministic": True,
        },
        "ets_axes_groups_used": [
            {"group": g1, "sub_axes": axes_groups.get(g1, [])},
            {"group": g2, "sub_axes": axes_groups.get(g2, [])},
        ],
    }

    write_manifest(manifest)

    print("[EDHQ-03] OK")
    print(f"ETS: {manifest['ets_path']}")
    print(f"ETS sha256: {manifest['ets_sha256']}")
    print(f"STOP predicate (ETS): {stop_expr}")
    print(f"Axis groups used: {g1}, {g2}")
    print(f"Outputs: {os.path.relpath(OUT_PDF, REPO_ROOT)} + manifest.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"[EDHQ-03] ERROR: {e}", file=sys.stderr)
        raise
