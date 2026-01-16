from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import classify_phase, k_EA
from ea_oc_ext.guards.transitions import TransitionContext, guard_transition_or_stop
from ea_oc_ext.synthetic.generate import SyntheticConfig, generate_trajectory


def run_one(spec, cfg: SyntheticConfig, psi_threshold: float, window: int) -> Dict[str, Any]:
    traj = generate_trajectory(spec, cfg)
    market_by_t = {t: fields.market for (t, _s, fields) in traj}

    def ext_psi_at(t: int) -> bool:
        lo = max(0, t - window)
        hi = min(cfg.steps, t + window)
        return any(market_by_t.get(tt, -1e9) > psi_threshold for tt in range(lo, hi + 1))

    prev_phase = "SUCCESS"
    ks: List[float] = []
    phases: List[str] = []
    t_stop = None
    t_success_after_inertia = None
    seen_inertia = False

    for (t, state, _fields) in traj:
        try:
            phase_raw = classify_phase(spec, state)
        except ValueError:
            phases.append("STOP")
            ks.append(0.0)
            t_stop = t
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
            t_stop = t
            break

    if t_stop is None:
        t_stop = cfg.steps
    if t_success_after_inertia is None:
        t_success_after_inertia = cfg.steps

    return {
        "terminated": phases[-1] if phases else "EMPTY",
        "t_stop": t_stop,
        "t_success_after_inertia": t_success_after_inertia,
        "k_mean": (sum(ks) / len(ks)) if ks else 0.0,
    }


def mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def median(xs: List[int]) -> float:
    if not xs:
        return 0.0
    ys = sorted(xs)
    n = len(ys)
    mid = n // 2
    if n % 2 == 1:
        return float(ys[mid])
    return 0.5 * (ys[mid - 1] + ys[mid])


def main() -> None:
    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")

    base = dict(
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

    replicates = 25
    amplitudes = [0.05, 0.10, 0.20, 0.35]
    thresholds = [0.05, 0.10, 0.15, 0.20]
    windows = [0, 1, 2, 5, 10]

    rows_out: List[Dict[str, Any]] = []
    for w in windows:
        for a in amplitudes:
            for th in thresholds:
                terms: List[str] = []
                t_succ: List[int] = []
                t_stop: List[int] = []
                kmeans: List[float] = []

                for r in range(replicates):
                    seed = 700000 + int(w * 1000) + int(a * 10000) + int(th * 1000) + r
                    cfg = SyntheticConfig(seed=seed, single_field_amplitude=a, **base)
                    one = run_one(spec, cfg, psi_threshold=th, window=w)
                    terms.append(one["terminated"])
                    t_succ.append(int(one["t_success_after_inertia"]))
                    t_stop.append(int(one["t_stop"]))
                    kmeans.append(float(one["k_mean"]))

                success_rate = sum(1 for t in terms if t == "SUCCESS") / len(terms)
                stop_rate = sum(1 for t in terms if t == "STOP") / len(terms)

                rows_out.append({
                    "window": w,
                    "amplitude": a,
                    "psi_threshold": th,
                    "replicates": replicates,
                    "success_rate": success_rate,
                    "stop_rate": stop_rate,
                    "t_success_mean": mean([float(x) for x in t_succ]),
                    "t_success_median": median(t_succ),
                    "k_mean_mean": mean(kmeans),
                })

    Path("results").mkdir(exist_ok=True)
    Path("results/sim03c_replicated_grid.json").write_text(
        json.dumps({
            "spec_id": spec.spec_id,
            "spec_sha256": Path("configs/ETS.K_EA.v1.1.sha256").read_text().strip(),
            "note": "SIM-03c: replicated grid (windowed Psi) for stable success-rate estimates (synthetic).",
            "rows": rows_out,
        }, indent=2),
        encoding="utf-8",
    )

    with open("results/sim03c_replicated_grid_summary.csv", "w", newline="", encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["window","amplitude","psi_threshold","replicates","success_rate","stop_rate","t_success_mean","t_success_median","k_mean_mean"])
        for r in rows_out:
            w.writerow([
                r["window"], r["amplitude"], r["psi_threshold"], r["replicates"],
                r["success_rate"], r["stop_rate"], r["t_success_mean"], r["t_success_median"], r["k_mean_mean"]
            ])

    print("Wrote results/sim03c_replicated_grid.json and results/sim03c_replicated_grid_summary.csv")


if __name__ == "__main__":
    main()
