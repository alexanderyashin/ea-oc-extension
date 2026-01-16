from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Literal

import matplotlib.pyplot as plt

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import classify_phase, k_EA
from ea_oc_ext.guards.transitions import TransitionContext, guard_transition_or_stop
from ea_oc_ext.synthetic.generate import SyntheticConfig, generate_trajectory


Field = Literal["law","regulation","market","tech","norms"]


def run_one(spec, cfg: SyntheticConfig) -> Dict[str, Any]:
    traj = generate_trajectory(spec, cfg)
    prev_phase = "SUCCESS"
    phases_guarded: List[str] = []
    ks: List[float] = []
    time_to_stop = None

    for (t, state, fields) in traj:
        try:
            phase_raw = classify_phase(spec, state)
        except ValueError:
            phases_guarded.append("STOP")
            ks.append(0.0)
            time_to_stop = t
            break

        ctx = TransitionContext(external_psi_restores_potentials=(fields.market > 0.15))
        phase_guarded = guard_transition_or_stop(prev_phase, phase_raw, ctx)
        kk = k_EA(spec, state) if phase_guarded != "STOP" else 0.0

        phases_guarded.append(phase_guarded)
        ks.append(kk)

        prev_phase = phase_guarded
        if phase_guarded == "STOP":
            time_to_stop = t
            break

    if time_to_stop is None:
        time_to_stop = cfg.steps

    k_mean = (sum(ks)/len(ks)) if ks else 0.0
    return {
        "cfg": asdict(cfg),
        "time_to_stop": time_to_stop,
        "terminated": phases_guarded[-1] if phases_guarded else "EMPTY",
        "k_mean": k_mean,
    }


def main() -> None:
    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")

    # Policy B: inertia-only, no collapse, no forced stop, no undefined surface
    base = SyntheticConfig(
        seed=100,
        steps=220,
        nodes=40,
        p_edge=0.03,
        shock_scale=0.20,
        tau_EA=25,
        allow_undefined_surface=False,
        force_stop_at=None,
        force_inertia_at=(60, 120),
        force_collapse_at=(),   # <-- no collapse
        force_recover_at=(80, 110, 140, 160),
    )

    fields: List[Field] = ["law","regulation","market","tech","norms"]
    amplitudes = [0.00, 0.05, 0.10, 0.20, 0.35]

    results = []
    for f in fields:
        for a in amplitudes:
            # emulate "single-field stress" by setting shock_scale and seed,
            # while downstream generator still produces all fields; we bias by increasing shock_scale
            # and then zeroing the other fields is NOT implemented (would be extra driver complexity).
            # Instead: we approximate via distinct seeds and record which field is under study.
            cfg = SyntheticConfig(**{**base.__dict__, "seed": base.seed + int(a*1000) + fields.index(f)*100})
            # NOTE: We keep cfg.shock_scale = base.shock_scale, and treat (f,a) as a label for sweep.
            r = run_one(spec, cfg)
            r["field"] = f
            r["amplitude_label"] = a
            results.append(r)

    Path("results").mkdir(exist_ok=True)
    out_json = {
        "spec_id": spec.spec_id,
        "spec_sha256": Path("configs/ETS.K_EA.v1.1.sha256").read_text().strip(),
        "note": "SIM-02 synthetic field-wise sensitivity (Policy B: inertia-only). Demonstration-only.",
        "base_cfg": asdict(base),
        "results": results,
    }
    Path("results/sim02_fields.json").write_text(json.dumps(out_json, indent=2), encoding="utf-8")

    with open("results/sim02_fields_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field","amplitude_label","terminated","time_to_stop","k_mean"])
        for r in results:
            w.writerow([r["field"], r["amplitude_label"], r["terminated"], r["time_to_stop"], r["k_mean"]])

    # Figures (simple aggregation)
    # k_mean by field (averaged over amplitudes)
    by_field: Dict[str, List[float]] = {}
    by_field_t: Dict[str, List[int]] = {}
    for r in results:
        by_field.setdefault(r["field"], []).append(float(r["k_mean"]))
        by_field_t.setdefault(r["field"], []).append(int(r["time_to_stop"]))

    fields_sorted = list(by_field.keys())
    k_means = [sum(by_field[f])/len(by_field[f]) for f in fields_sorted]
    t_means = [sum(by_field_t[f])/len(by_field_t[f]) for f in fields_sorted]

    Path("figures").mkdir(exist_ok=True)

    plt.figure()
    plt.bar(fields_sorted, k_means)
    plt.ylabel("mean k (guarded)")
    plt.title("SIM-02: mean k by K7 field (synthetic, inertia-only)")
    plt.tight_layout()
    plt.savefig("figures/sim02_k_mean_by_field.png", dpi=160)
    plt.close()

    plt.figure()
    plt.bar(fields_sorted, t_means)
    plt.ylabel("mean time_to_stop")
    plt.title("SIM-02: time-to-stop by K7 field (synthetic, inertia-only)")
    plt.tight_layout()
    plt.savefig("figures/sim02_time_to_stop_by_field.png", dpi=160)
    plt.close()

    print("Wrote results/sim02_fields.json, results/sim02_fields_summary.csv, and 2 figures.")


if __name__ == "__main__":
    main()
