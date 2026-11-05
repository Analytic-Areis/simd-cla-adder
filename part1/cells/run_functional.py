#!/usr/bin/env python3
"""Phase 1: run every cell and block through the ngspice truth-table bench."""
from concurrent.futures import ThreadPoolExecutor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cellgen import config as cfg
from cellgen.bench import PERIOD, run_truth_table, write_results
from library import all_blocks, all_cells

OUT = cfg.PART1 / "simulations" / "functional" / "blocks"
INK, GRID = "#1f2933", "#d9dee4"


def plot_waves(cell, t, data, col, path, title):
    """Stacked waveforms of the first vectors, one strip per signal."""
    names = (cell.inputs + cell.outputs)[:14]
    limit = min(32, len(cell.vectors())) * PERIOD
    # ngspice's maximum internal step gives enough points inside each 1 ns vector
    keep = t <= limit
    fig, axes = plt.subplots(len(names), 1, sharex=True, figsize=(9, 0.62 * len(names) + 1.1))
    axes = np.atleast_1d(axes)
    for ax, n in zip(axes, names):
        ax.plot(t[keep] * 1e9, data[keep, col[f"v({n})".lower()]], color=INK, lw=1.1)
        ax.set_ylim(-0.2, 2.0)
        ax.set_yticks([0, 1.8])
        ax.tick_params(labelsize=6, length=2)
        is_out = n in cell.outputs
        ax.set_ylabel(n, rotation=0, ha="right", va="center", fontsize=8, weight="bold" if is_out else "normal")
        ax.grid(axis="x", color=GRID, lw=0.5)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[-1].set_xlabel("time (ns)", fontsize=8)
    fig.suptitle(title, fontsize=9, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def one(cell):
    d = OUT / cell.name
    title = cfg.plot_title("1.3", f"{cell.name}-function")
    # the unit-size 5-high C4 gate needs longer than 1 ns per vector to settle within 10 % of VDD
    res = run_truth_table(cell, d, title, period=3e-9 if cell.name == "c4_x1" else 1e-9)
    if isinstance(res, tuple):
        row, (t, data, col) = res
        plot_waves(cell, t, data, col, d / "waves.png", title)
    else:
        row = res
    print({k: row[k] for k in ("cell", "vectors", "errors", "min_voh", "max_vol", "max_static_ua", "passed")},
          row.get("note", ""), flush=True)
    return row


def main():
    cells = all_cells() + all_blocks()
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(one, cells))
    write_results(rows, cfg.PART1 / "results" / "phase1_block_functional.csv")
    failed = [r["cell"] for r in rows if not r["passed"]]
    print("FAILED:" if failed else "ALL BLOCKS PASS", failed or "")


if __name__ == "__main__":
    main()
