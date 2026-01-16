from __future__ import annotations

import csv
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple, List

import matplotlib.pyplot as plt


def read_csv(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def savefig(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=170)
    plt.close()


def fig_success_rate_vs_window():
    rows = read_csv("results/sim03b_windowed_psi_summary.csv")
    by = defaultdict(list)
    for r in rows:
        by[int(r["window"])].append(r["terminated"])
    windows = sorted(by.keys())
    rates = [sum(1 for v in by[w] if v == "SUCCESS") / len(by[w]) for w in windows]

    plt.figure()
    plt.plot(windows, rates, marker="o")
    plt.xlabel("window (±steps)")
    plt.ylabel("success_rate")
    plt.title("SIM-03b: success_rate vs windowed external Ψ")
    savefig("figures/sim03b_success_rate_vs_window.png")


def fig_heatmaps_by_window():
    rows = read_csv("results/sim03b_windowed_psi_summary.csv")

    # grid: window -> (amp, th) -> success_rate
    windows = sorted({int(r["window"]) for r in rows})
    amps = sorted({float(r["amplitude"]) for r in rows})
    ths = sorted({float(r["psi_threshold"]) for r in rows})

    for w in windows:
        # counts per cell
        cell = defaultdict(list)
        for r in rows:
            if int(r["window"]) != w:
                continue
            key = (float(r["amplitude"]), float(r["psi_threshold"]))
            cell[key].append(r["terminated"])

        # build matrix [len(amps) x len(ths)]
        mat = []
        for a in amps:
            rowv = []
            for th in ths:
                vals = cell.get((a, th), [])
                if not vals:
                    rowv.append(0.0)
                else:
                    rowv.append(sum(1 for v in vals if v == "SUCCESS") / len(vals))
            mat.append(rowv)

        plt.figure()
        plt.imshow(mat, aspect="auto", origin="lower")
        plt.colorbar(label="success_rate")
        plt.xticks(range(len(ths)), [str(t) for t in ths], rotation=45)
        plt.yticks(range(len(amps)), [str(a) for a in amps])
        plt.xlabel("psi_threshold")
        plt.ylabel("amplitude")
        plt.title(f"SIM-03b: success_rate heatmap (window={w})")
        savefig(f"figures/sim03b_heatmap_window_{w}.png")


def fig_sim02b_mean_k_by_field():
    rows = read_csv("results/sim02b_single_field_summary.csv")
    by = defaultdict(list)
    for r in rows:
        by[r["field"]].append(float(r["k_mean"]))
    fields = sorted(by.keys())
    means = [sum(by[f]) / len(by[f]) for f in fields]

    plt.figure()
    plt.bar(fields, means)
    plt.ylabel("mean k")
    plt.title("SIM-02b: mean k by single K7 field (ψ always)")
    savefig("figures/sim02b_mean_k_by_field.png")


def fig_sim03b_k_vs_tsuccess():
    rows = read_csv("results/sim03b_windowed_psi_summary.csv")
    xs = [int(r["t_success_after_inertia"]) for r in rows]
    ys = [float(r["k_mean"]) for r in rows]
    cs = [1 if r["terminated"] == "SUCCESS" else 0 for r in rows]

    plt.figure()
    plt.scatter(xs, ys, c=cs)
    plt.xlabel("t_success_after_inertia")
    plt.ylabel("k_mean")
    plt.title("SIM-03b: k_mean vs recovery time (color: SUCCESS=1/STOP=0)")
    savefig("figures/sim03b_k_vs_tsuccess.png")


def main():
    Path("figures").mkdir(exist_ok=True)

    fig_success_rate_vs_window()
    fig_heatmaps_by_window()
    fig_sim02b_mean_k_by_field()
    fig_sim03b_k_vs_tsuccess()

    print("Wrote figures:")
    for p in sorted(Path("figures").glob("sim0*.png")):
        print(" -", p.as_posix())


if __name__ == "__main__":
    main()
