from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import classify_phase, k_EA
from ea_oc_ext.guards.transitions import TransitionContext, guard_transition_or_stop
from ea_oc_ext.synthetic.generate import SyntheticConfig, generate_trajectory


def main() -> None:
    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")
    cfg = SyntheticConfig(allow_undefined_surface=False)

    traj = generate_trajectory(spec, cfg)

    prev_phase = "SUCCESS"
    ctx = TransitionContext(external_psi_restores_potentials=False)

    rows = []
    for (t, state, fields) in traj:
        # classify phase (may raise ValueError if ETS does not define it for the f-vector)
        try:
            phase = classify_phase(spec, state)
        except ValueError as e:
            phase = "ETS_UNDEFINED"
            rows.append({
                "t": t,
                "phase_raw": phase,
                "phase_guarded": "STOP",
                "k": 0.0,
                "error": str(e),
                "f": state.f,
                "closed_cycles": sorted(state.closed_cycles),
                "fields": fields.as_dict(),
            })
            prev_phase = "STOP"
            break

        # synthetic external Ψ rule: only sometimes present
        # NOTE: this is simulation driver logic, not theory.
        ctx = TransitionContext(external_psi_restores_potentials=(t in (85, 145)))

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
        "note": "Synthetic regime run. Not an empirical enterprise claim.",
    }

    Path("results").mkdir(exist_ok=True)
    Path("results/sim_run.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote results/sim_run.json with", len(rows), "rows")


if __name__ == "__main__":
    main()
