from __future__ import annotations

import csv
from collections import defaultdict

def main() -> None:
    rows=list(csv.DictReader(open("results/sim03b_windowed_psi_summary.csv","r",encoding="utf-8")))

    windows=sorted({int(r["window"]) for r in rows})
    amps=sorted({float(r["amplitude"]) for r in rows})
    ths=sorted({float(r["psi_threshold"]) for r in rows})

    # window -> (amp, th) -> list terminated
    cell=defaultdict(list)
    for r in rows:
        w=int(r["window"]); a=float(r["amplitude"]); th=float(r["psi_threshold"])
        cell[(w,a,th)].append(r["terminated"])

    for w in windows:
        print("\n=== window", w, "===")
        for a in amps:
            line=[]
            for th in ths:
                vals=cell.get((w,a,th), [])
                if not vals:
                    sr=0.0
                else:
                    sr=sum(1 for v in vals if v=="SUCCESS")/len(vals)
                line.append(f"{sr:0.2f}")
            print("amp", f"{a:0.2f}", "  ", " ".join(line), "  (ths:", ", ".join(f"{t:0.2f}" for t in ths), ")")

if __name__=="__main__":
    main()
