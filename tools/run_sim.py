from __future__ import annotations

import json
from pathlib import Path

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import classify_phase, k_EA
from ea_oc_ext.guards.transitions import TransitionContext, guard_transition_or_stop
from ea_oc_ext.synthetic.generate import SyntheticConfig, generate_trajectory


def main() -> None:
    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")
    cfg = SyntheticConfig(
        allow_undefined_surface=False,
        force_stop_at=None,   # UNFORCED
    )

    traj = generate_trajectory(spec, cfg)

    prev_phase = "SUCCESS"
    rows = []

    for (t, state, fields) in traj:
        try:
            phase = classify_phase(spec, state)
        except ValueError as e:
            rows.append({
                "t": t,
                "phase_raw": "ETS_UNDEFINED",
                "phase_guarded": "STOP",
                "k": 0.0,
                "error": str(e),
                "f": state.f,
                "closed_cycles": sorted(state.closed_cycles),
                "fields": fields.as_dict(),
            })
            prev_phase = "STOP"
            break

        # driver-only external Ψ: synthetic knob, not theory claim
        ctx = TransitionContext(external_psi_restores_potentials=(fields.market > 0.15))

        phase_guarded = guard_transition_or_stop(prev_phase, phase, ctx)
        kk = k_EA(spec, state) if phase_guarded != "STOP" else 0.0

        rows.append({
            "t": t,
            "phase_raw": phase,
            "phase_guarded": phase_guarded,
            "k": kk,
            "f": state.f,
            "closed_cycles": sorted(state.closed_cycles),
            "fields": fields.as_dict(),
            "external_psi": ctx.external_psi_restores_potentials,
        })
        prev_phase = phase_guarded
        if phase_guarded == "STOP":
            break

    out = {
        "spec_id": spec.spec_id,
        "spec_sha256": Path("configs/ETS.K_EA.v1.1.sha256").read_text().strip(),
        "synthetic_config": cfg.__dict__,
        "rows": rows,
        "note": "Synthetic regime run (UNFORCED STOP). Not an empirical enterprise claim.",
    }

    Path("results").mkdir(exist_ok=True)
    Path("results/sim_run.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote results/sim_run.json with", len(rows), "rows")


if __name__ == "__main__":
    main()
