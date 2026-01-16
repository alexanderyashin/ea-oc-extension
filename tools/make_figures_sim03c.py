from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


def read_rows(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ensure_outdir() -> Path:
    out = Path("figures")
    out.mkdir(parents=True, exist_ok=True)
    return out


def savefig(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=170)
    plt.close()


def heatmap_for_window(rows: List[dict], window: int, out: Path) -> None:
    # Build grid: amplitude x threshold -> success_rate
    amps = sorted({float(r["amplitude"]) for r in rows if int(r["window"]) == window})
    ths = sorted({float(r["psi_threshold"]) for r in rows if int(r["window"]) == window})

    grid = [[None for _ in ths] for _ in amps]
    for r in rows:
        if int(r["window"]) != window:
            continue
        a = float(r["amplitude"])
        th = float(r["psi_threshold"])
        sr = float(r["success_rate"])
        i = amps.index(a)
        j = ths.index(th)
        grid[i][j] = sr

    # Convert None to 0.0 to be safe
    Z = [[(v if v is not None else 0.0) for v in row] for row in grid]

    plt.figure()
    plt.imshow(Z, aspect="auto")  # no explicit colors per your standard
    plt.xticks(range(len(ths)), [f"{x:.2f}" for x in ths])
    plt.yticks(range(len(amps)), [f"{x:.2f}" for x in amps])
    plt.xlabel("psi_threshold")
    plt.ylabel("amplitude")
    plt.title(f"SIM-03c success_rate heatmap (window={window})")
    plt.colorbar()
    savefig(out / f"sim03c_heatmap_window_{window}.png")


def success_rate_vs_window(rows: List[dict], out: Path) -> None:
    by_w: Dict[int, List[float]] = defaultdict(list)
    for r in rows:
        by_w[int(r["window"])].append(float(r["success_rate"]))

    xs = sorted(by_w.keys())
    ys = [sum(by_w[w]) / len(by_w[w]) for w in xs]

    plt.figure()
    plt.plot(xs, ys, marker="o")
    plt.xlabel("window")
    plt.ylabel("mean_success_rate_over_grid")
    plt.title("SIM-03c mean success rate vs window")
    savefig(out / "sim03c_success_rate_vs_window.png")


def t_success_median_vs_threshold(rows: List[dict], out: Path) -> None:
    # Aggregate by threshold (across amps/windows) to show timing behavior
    by_th: Dict[float, List[float]] = defaultdict(list)
    for r in rows:
        th = float(r["psi_threshold"])
        by_th[th].append(float(r["t_success_median"]))

    xs = sorted(by_th.keys())
    ys = [sum(by_th[th]) / len(by_th[th]) for th in xs]

    plt.figure()
    plt.plot(xs, ys, marker="o")
    plt.xlabel("psi_threshold")
    plt.ylabel("mean(t_success_median)")
    plt.title("SIM-03c mean median time-to-success vs threshold")
    savefig(out / "sim03c_tsuccess_median_vs_threshold.png")


def main() -> None:
    rows = read_rows("results/sim03c_replicated_grid_summary.csv")
    out = ensure_outdir()

    windows = sorted({int(r["window"]) for r in rows})
    for w in windows:
        heatmap_for_window(rows, w, out)

    success_rate_vs_window(rows, out)
    t_success_median_vs_threshold(rows, out)

    print("Wrote figures:")
    for p in sorted(out.glob("sim03c_*.png")):
        print(" -", str(p))


if __name__ == "__main__":
    main()
