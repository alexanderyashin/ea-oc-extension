from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Literal

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import classify_phase, k_EA
from ea_oc_ext.guards.transitions import TransitionContext, guard_transition_or_stop
from ea_oc_ext.synthetic.generate import SyntheticConfig, generate_trajectory

Field = Literal["law", "regulation", "market", "tech", "norms"]
PsiMode = Literal["none", "market_threshold", "always"]


def run_one(spec, cfg: SyntheticConfig, psi_mode: PsiMode, psi_threshold: float = 0.15) -> Dict[str, Any]:
    traj = generate_trajectory(spec, cfg)
    prev_phase = "SUCCESS"
    ks: List[float] = []
    phases: List[str] = []
    time_to_stop = None

    for (t, state, fields) in traj:
        try:
            phase_raw = classify_phase(spec, state)
        except ValueError:
            phases.append("ETS_UNDEFINED")
            ks.append(0.0)
            time_to_stop = t
            break

        if psi_mode == "always":
            ext = True
        elif psi_mode == "market_threshold":
            ext = (fields.market > psi_threshold)
        else:
            ext = False

        ctx = TransitionContext(external_psi_restores_potentials=ext)
        phase_guarded = guard_transition_or_stop(prev_phase, phase_raw, ctx)
        kk = k_EA(spec, state) if phase_guarded != "STOP" else 0.0

        phases.append(phase_guarded)
        ks.append(kk)

        prev_phase = phase_guarded
        if phase_guarded == "STOP":
            time_to_stop = t
            break

    if time_to_stop is None:
        time_to_stop = cfg.steps

    return {
        "cfg": asdict(cfg),
        "psi_mode": psi_mode,
        "time_to_stop": time_to_stop,
        "terminated": phases[-1] if phases else "EMPTY",
        "k_mean": (sum(ks) / len(ks)) if ks else 0.0,
    }


def main() -> None:
    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")

    # Policy B: inertia-only, no collapse, no forced stop, no undefined surface
    base = dict(
        seed=200,
        steps=220,
        nodes=40,
        p_edge=0.03,
        shock_scale=0.0,  # will be overridden by single_field_amplitude
        tau_EA=25,
        allow_undefined_surface=False,
        force_stop_at=None,
        force_inertia_at=(60, 120),
        force_collapse_at=(),  # no collapse
        force_recover_at=(80, 110, 140, 160),
    )

    fields: List[Field] = ["law", "regulation", "market", "tech", "norms"]
    amplitudes = [0.00, 0.05, 0.10, 0.20, 0.35]

    # Choose psi mode for this experiment:
    # - "always": allows INERTIA->SUCCESS when recover happens (demonstrates survivable regimes)
    # - "market_threshold": ties recovery permission to market only
    psi_mode: PsiMode = "always"

    results: List[Dict[str, Any]] = []
    for f in fields:
        for a in amplitudes:
            cfg = SyntheticConfig(**{
                **base,
                "seed": base["seed"] + int(a * 1000) + fields.index(f) * 100,
                "single_field": f,
                "single_field_amplitude": a,
            })
            results.append(run_one(spec, cfg, psi_mode=psi_mode))

    Path("results").mkdir(exist_ok=True)
    out = {
        "spec_id": spec.spec_id,
        "spec_sha256": Path("configs/ETS.K_EA.v1.1.sha256").read_text().strip(),
        "note": "SIM-02b true single-field sweeps. Synthetic driver only; not an empirical claim.",
        "psi_mode": psi_mode,
        "results": results,
    }
    Path("results/sim02b_single_field.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    with open("results/sim02b_single_field_summary.csv", "w", newline="", encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["field", "amplitude", "psi_mode", "terminated", "time_to_stop", "k_mean"])
        for r in results:
            cfg = r["cfg"]
            w.writerow([cfg["single_field"], cfg["single_field_amplitude"], r["psi_mode"], r["terminated"], r["time_to_stop"], r["k_mean"]])

    print("Wrote results/sim02b_single_field.json and results/sim02b_single_field_summary.csv")


if __name__ == "__main__":
    main()
