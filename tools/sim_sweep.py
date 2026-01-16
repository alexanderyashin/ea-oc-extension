from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import classify_phase, k_EA
from ea_oc_ext.guards.transitions import TransitionContext, guard_transition_or_stop
from ea_oc_ext.synthetic.generate import SyntheticConfig, generate_trajectory


def _summarize(phases: List[str], ks: List[float]) -> Dict[str, Any]:
    if not phases:
        return {"counts": {}, "k_min": 0.0, "k_mean": 0.0, "k_max": 0.0}
    counts: Dict[str, int] = {}
    for p in phases:
        counts[p] = counts.get(p, 0) + 1
    k_min = min(ks) if ks else 0.0
    k_max = max(ks) if ks else 0.0
    k_mean = (sum(ks) / len(ks)) if ks else 0.0
    return {"counts": counts, "k_min": k_min, "k_mean": k_mean, "k_max": k_max}


def run_one(spec, cfg: SyntheticConfig) -> Dict[str, Any]:
    traj = generate_trajectory(spec, cfg)
    prev_phase = "SUCCESS"

    phases_raw: List[str] = []
    phases_guarded: List[str] = []
    ks: List[float] = []
    time_to_stop = None

    for (t, state, fields) in traj:
        try:
            phase_raw = classify_phase(spec, state)
        except ValueError:
            phase_raw = "ETS_UNDEFINED"
            phases_raw.append(phase_raw)
            phases_guarded.append("STOP")
            ks.append(0.0)
            time_to_stop = t
            break

        ctx = TransitionContext(external_psi_restores_potentials=(fields.market > 0.15))
        phase_guarded = guard_transition_or_stop(prev_phase, phase_raw, ctx)
        kk = k_EA(spec, state) if phase_guarded != "STOP" else 0.0

        phases_raw.append(phase_raw)
        phases_guarded.append(phase_guarded)
        ks.append(kk)

        prev_phase = phase_guarded
        if phase_guarded == "STOP":
            time_to_stop = t
            break

    if time_to_stop is None:
        time_to_stop = cfg.steps

    return {
        "cfg": asdict(cfg),
        "time_to_stop": time_to_stop,
        "terminated": phases_guarded[-1] if phases_guarded else "EMPTY",
        "summary_raw": _summarize(phases_raw, ks),
        "summary_guarded": _summarize(phases_guarded, ks),
    }


def main() -> None:
    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")

    sweep: List[SyntheticConfig] = []
    seed0 = 20

    for i, shock in enumerate([0.05, 0.10, 0.20, 0.35]):
        for j, p_edge in enumerate([0.01, 0.03, 0.07]):
            sweep.append(SyntheticConfig(
                seed=seed0 + 10*i + j,
                steps=220,
                nodes=40,
                p_edge=p_edge,
                shock_scale=shock,
                tau_EA=25,
                allow_undefined_surface=False,
                force_stop_at=None,  # UNFORCED
            ))

    results = [run_one(spec, cfg) for cfg in sweep]

    Path("results").mkdir(exist_ok=True)
    out_json = {
        "spec_id": spec.spec_id,
        "spec_sha256": Path("configs/ETS.K_EA.v1.1.sha256").read_text().strip(),
        "note": "SIM-01b synthetic sweep (UNFORCED STOP). Demonstration-only; not an empirical enterprise claim.",
        "results": results,
    }
    Path("results/sim01b_sweep.json").write_text(json.dumps(out_json, indent=2), encoding="utf-8")

    with open("results/sim01b_sweep_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed","shock_scale","p_edge","time_to_stop","terminated","k_mean_guarded","SUCCESS_frac","INERTIA_frac","COLLAPSE_frac","STOP_frac"])
        for r in results:
            cfg = r["cfg"]
            counts = r["summary_guarded"]["counts"]
            total = sum(counts.values()) if counts else 1
            frac = lambda p: (counts.get(p, 0) / total) if total else 0.0
            w.writerow([
                cfg["seed"], cfg["shock_scale"], cfg["p_edge"], r["time_to_stop"], r["terminated"],
                r["summary_guarded"]["k_mean"],
                frac("SUCCESS"), frac("INERTIA"), frac("COLLAPSE"), frac("STOP"),
            ])

    print("Wrote results/sim01b_sweep.json and results/sim01b_sweep_summary.csv")


if __name__ == "__main__":
    main()
