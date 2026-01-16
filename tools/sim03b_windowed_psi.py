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


def run_one(spec, cfg: SyntheticConfig, psi_threshold: float, window: int) -> Dict[str, Any]:
    traj = generate_trajectory(spec, cfg)

    # precompute market(t)
    market_by_t: Dict[int, float] = {t: fields.market for (t, _s, fields) in traj}

    def ext_psi_at(t: int) -> bool:
        lo = max(0, t - window)
        hi = min(cfg.steps, t + window)
        return any(market_by_t.get(tt, -1e9) > psi_threshold for tt in range(lo, hi + 1))

    prev_phase = "SUCCESS"
    ks: List[float] = []
    phases: List[str] = []
    time_to_stop = None
    t_success_after_inertia = None
    seen_inertia = False

    for (t, state, _fields) in traj:
        try:
            phase_raw = classify_phase(spec, state)
        except ValueError:
            phases.append("STOP")
            ks.append(0.0)
            time_to_stop = t
            break

        ctx = TransitionContext(external_psi_restores_potentials=ext_psi_at(t))
        phase_guarded = guard_transition_or_stop(prev_phase, phase_raw, ctx)
        kk = k_EA(spec, state) if phase_guarded != "STOP" else 0.0

        phases.append(phase_guarded)
        ks.append(kk)

        if phase_guarded == "INERTIA":
            seen_inertia = True
        if seen_inertia and phase_guarded == "SUCCESS" and t_success_after_inertia is None:
            t_success_after_inertia = t

        prev_phase = phase_guarded
        if phase_guarded == "STOP":
            time_to_stop = t
            break

    if time_to_stop is None:
        time_to_stop = cfg.steps
    if t_success_after_inertia is None:
        t_success_after_inertia = cfg.steps

    return {
        "cfg": asdict(cfg),
        "psi_threshold": psi_threshold,
        "window": window,
        "terminated": phases[-1] if phases else "EMPTY",
        "t_success_after_inertia": t_success_after_inertia,
        "t_stop": time_to_stop,
        "k_mean": (sum(ks) / len(ks)) if ks else 0.0,
    }


def main() -> None:
    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")

    base = dict(
        seed=400,
        steps=220,
        nodes=40,
        p_edge=0.03,
        shock_scale=0.0,
        tau_EA=25,
        allow_undefined_surface=False,
        force_stop_at=None,
        force_inertia_at=(60, 120),
        force_collapse_at=(),
        force_recover_at=(80, 110, 140, 160),
        single_field="market",
    )

    amplitudes = [0.05, 0.10, 0.20, 0.35]
    thresholds = [0.05, 0.10, 0.15, 0.20]
    windows = [0, 1, 2, 5, 10]

    results: List[Dict[str, Any]] = []
    for a in amplitudes:
        for th in thresholds:
            for w in windows:
                cfg = SyntheticConfig(**{
                    **base,
                    "seed": base["seed"] + int(a * 1000) + int(th * 100) + w,
                    "single_field_amplitude": a,
                })
                results.append(run_one(spec, cfg, psi_threshold=th, window=w))

    Path("results").mkdir(exist_ok=True)
    out = {
        "spec_id": spec.spec_id,
        "spec_sha256": Path("configs/ETS.K_EA.v1.1.sha256").read_text().strip(),
        "note": "SIM-03b: windowed external Psi (market>threshold within +-window). Synthetic synchrony sensitivity.",
        "results": results,
    }
    Path("results/sim03b_windowed_psi.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    with open("results/sim03b_windowed_psi_summary.csv", "w", newline="", encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["amplitude","psi_threshold","window","terminated","t_success_after_inertia","t_stop","k_mean"])
        for r in results:
            cfg = r["cfg"]
            w.writerow([
                cfg["single_field_amplitude"], r["psi_threshold"], r["window"], r["terminated"],
                r["t_success_after_inertia"], r["t_stop"], r["k_mean"]
            ])

    print("Wrote results/sim03b_windowed_psi.json and results/sim03b_windowed_psi_summary.csv")


if __name__ == "__main__":
    main()
