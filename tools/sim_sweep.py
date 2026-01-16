from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import classify_phase, k_EA
from ea_oc_ext.guards.transitions import TransitionContext, guard_transition_or_stop
from ea_oc_ext.synthetic.generate import SyntheticConfig, generate_trajectory


def run_one(spec, cfg: SyntheticConfig) -> Dict[str, Any]:
    traj = generate_trajectory(spec, cfg)
    prev_phase = "SUCCESS"
    ctx = TransitionContext(external_psi_restores_potentials=False)

    phases_raw: List[str] = []
    phases_guarded: List[str] = []
    ks: List[float] = []

    for (t, state, fields) in traj:
        # In sweeps we disallow ETS_UNDEFINED by construction; but keep safety.
        try:
            phase = classify_phase(spec, state)
        except ValueError:
            return {
                "cfg": asdict(cfg),
                "terminated": "ETS_UNDEFINED",
                "steps": t,
                "phases_raw": phases_raw,
                "phases_guarded": phases_guarded,
                "k": ks,
            }

        # driver-only external Ψ: present if market shock is positive enough (synthetic rule)
        # This is *not* a theory claim; it's a knob to exercise allowed transition.
        ctx = TransitionContext(external_psi_restores_potentials=(fields.market > 0.15))

        phase_guarded = guard_transition_or_stop(prev_phase, phase, ctx)
        kk = k_EA(spec, state) if phase_guarded != "STOP" else 0.0

        phases_raw.append(phase)
        phases_guarded.append(phase_guarded)
        ks.append(kk)

        prev_phase = phase_guarded
        if phase_guarded == "STOP":
            break

    return {
        "cfg": asdict(cfg),
        "terminated": phases_guarded[-1] if phases_guarded else "EMPTY",
        "steps": len(phases_guarded),
        "phases_raw": phases_raw,
        "phases_guarded": phases_guarded,
        "k": ks,
    }


def main() -> None:
    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")

    sweep: List[SyntheticConfig] = []
    seed0 = 10
    # Grid over shock_scale and p_edge (graph density proxy)
    for i, shock in enumerate([0.05, 0.10, 0.20, 0.35]):
        for j, p_edge in enumerate([0.01, 0.03, 0.07]):
            sweep.append(SyntheticConfig(
                seed=seed0 + 10*i + j,
                steps=220,
                nodes=40,
                p_edge=p_edge,
                shock_scale=shock,
                tau_EA=25,
                allow_undefined_surface=False,  # strict for sweeps
            ))

    results = [run_one(spec, cfg) for cfg in sweep]

    Path("results").mkdir(exist_ok=True)
    out_json = {
        "spec_id": spec.spec_id,
        "spec_sha256": Path("configs/ETS.K_EA.v1.1.sha256").read_text().strip(),
        "note": "SIM-01 synthetic sweep. Demonstration-only; not an empirical enterprise claim.",
        "results": results,
    }
    Path("results/sim01_sweep.json").write_text(json.dumps(out_json, indent=2), encoding="utf-8")

    # CSV summary: one row per cfg
    with open("results/sim01_sweep_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed","shock_scale","p_edge","steps","terminated","k_min","k_mean","k_max"])
        for r in results:
            cfg = r["cfg"]
            ks = r["k"]
            if ks:
                k_min = min(ks); k_max = max(ks); k_mean = sum(ks)/len(ks)
            else:
                k_min = k_max = k_mean = 0.0
            w.writerow([cfg["seed"], cfg["shock_scale"], cfg["p_edge"], r["steps"], r["terminated"], k_min, k_mean, k_max])

    print("Wrote results/sim01_sweep.json and results/sim01_sweep_summary.csv")


if __name__ == "__main__":
    main()
