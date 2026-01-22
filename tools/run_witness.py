import json
import argparse
from pathlib import Path
from collections import Counter

from ea_oc_ext.engine.spec import load_kea_spec
from ea_oc_ext.engine.model import classify_phase
from ea_oc_ext.synthetic.generate import SyntheticConfig, generate_trajectory


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="witness name (collapse/inertia/stop/success)")
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--force_stop_at", type=str, default="null")          # e.g. "12" or "null"
    ap.add_argument("--force_inertia_at", type=str, default="none")       # e.g. "8,9,10,11" or "none"
    ap.add_argument("--force_collapse_at", type=str, default="none")      # e.g. "10" or "none"
    ap.add_argument("--force_recover_at", type=str, default="none")       # e.g. "80,110" or "none"
    args = ap.parse_args()

    def parse_int_tuple(s: str):
        s = (s or "").strip().lower()
        if s in ("", "none", "null"):
            return ()
        return tuple(int(x.strip()) for x in s.split(",") if x.strip())

    def parse_optional_int(s: str):
        s = (s or "").strip().lower()
        if s in ("null", "none", ""):
            return None
        return int(s)

    spec = load_kea_spec("configs/ETS.K_EA.v1.1.yaml")

    cfg = SyntheticConfig(
        allow_undefined_surface=False,
        seed=args.seed,
        steps=args.steps,
        force_stop_at=parse_optional_int(args.force_stop_at),
        force_inertia_at=parse_int_tuple(args.force_inertia_at),
        force_collapse_at=parse_int_tuple(args.force_collapse_at),
        force_recover_at=parse_int_tuple(args.force_recover_at),
    )

    rows = []
    for (t, state, fields) in generate_trajectory(spec, cfg):
        phase = classify_phase(spec, state)
        rows.append({
            "t": t,
            "phase_raw": phase,
            "f": state.f,
            "fields": fields.as_dict(),
        })
        if phase == "STOP":
            break

    out = {
        "spec_id": spec.spec_id,
        "spec_sha256": Path("configs/ETS.K_EA.v1.1.sha256").read_text().strip(),
        "synthetic_config": cfg.__dict__,
        "rows": rows,
        "note": f"Executable witness run: {args.name} (synthetic; not an empirical claim).",
    }

    outdir = Path("results/pdf3")
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"witness_{args.name}.json"
    outpath.write_text(json.dumps(out, indent=2), encoding="utf-8")

    cnt = Counter(r["phase_raw"] for r in rows)
    print("phase_raw counts:", dict(cnt))
    print("wrote:", str(outpath))


if __name__ == "__main__":
    main()
