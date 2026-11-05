#!/usr/bin/env python3
"""Annotated waveform figures from the testbench VCD files, for the report.

Run after scripts/run_sim.sh:  python3 scripts/plot_waves.py
Writes PNG files to fpga/results/. Each directed vector is labelled with the description the
testbench printed for it, so the figure and the log say the same thing.
"""
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

FPGA = Path(__file__).resolve().parents[1]
SIM, OUT = FPGA / "sim", FPGA / "results"
CONFIG = FPGA.parent / "part1" / "project_config.json"


def title(number, what):
    cfg = json.loads(CONFIG.read_text()) if CONFIG.exists() else {"name": "Bhargav", "roll": "2025102061"}
    return f"{cfg['name']}-{cfg['roll']}-{number}-{what}"


def read_vcd(path):
    """Returns {signal name: [(time, value string)]}, names as scope.signal, plus the end time."""
    ids, scope, waves, now = {}, [], {}, 0
    text = path.read_text().split("$enddefinitions", 1)
    unit = re.search(r"\$timescale\s*(\d+)\s*(\w+)", text[0])
    scale = int(unit.group(1)) * {"s": 1e9, "ms": 1e6, "us": 1e3, "ns": 1, "ps": 1e-3, "fs": 1e-6}[unit.group(2)]
    for line in text[0].splitlines():
        tok = line.split()
        if tok[:1] == ["$scope"]:
            scope.append(tok[2])
        elif tok[:1] == ["$upscope"]:
            scope.pop()
        elif tok[:1] == ["$var"]:
            name = ".".join(scope + [tok[4]])
            ids.setdefault(tok[3], []).append(name)
            waves[name] = []
    for line in text[1].split("\n"):
        line = line.strip()
        if not line or line.startswith("$"):
            continue
        if line[0] == "#":
            now = int(line[1:]) * scale
        elif line[0] in "bB":
            value, code = line[1:].split()
            for n in ids.get(code, []):
                waves[n].append((now, value))
        elif line[0] in "01xzXZ":
            for n in ids.get(line[1:], []):
                waves[n].append((now, line[0]))
    return waves, now


def value_at(wave, t):
    v = None
    for time, val in wave:
        if time > t:
            break
        v = val
    return v


def draw(ax, wave, t0, t1, bus, colour):
    pts = [(t, v) for t, v in wave if t0 <= t <= t1]
    start = value_at(wave, t0)
    if start is not None:
        pts = [(t0, start)] + [p for p in pts if p[0] > t0]
    pts.append((t1, pts[-1][1] if pts else "x"))
    # merge repeated values so edges are drawn only where the signal really changes
    merged = [pts[0]]
    for t, v in pts[1:-1]:
        if v != merged[-1][1]:
            merged.append((t, v))
    pts = merged + [pts[-1]]
    for (ta, va), (tb, _) in zip(pts, pts[1:]):
        if tb <= ta:
            continue
        if not bus:
            y = 0.8 if va == "1" else 0.2
            ax.plot([ta, tb], [y, y], color=colour, lw=1.6)
            if tb < t1:
                ax.plot([tb, tb], [0.2, 0.8], color=colour, lw=1.0)
        else:
            ax.fill([ta, ta + 0.3, tb - 0.3, tb, tb - 0.3, ta + 0.3], [0.5, 0.85, 0.85, 0.5, 0.15, 0.15],
                    color=colour, alpha=0.18, lw=0)
            ax.plot([ta, ta + 0.3, tb - 0.3, tb, tb - 0.3, ta + 0.3, ta], [0.5, 0.85, 0.85, 0.5, 0.15, 0.15, 0.5],
                    color=colour, lw=0.8)
            try:
                text = f"{int(va, 2):X}"
            except ValueError:
                text = va
            if tb - ta > (t1 - t0) * 0.012:
                ax.text((ta + tb) / 2, 0.5, text, ha="center", va="center", fontsize=7)


def log_labels(log, marker):
    """Vector descriptions and results, as the testbench printed them."""
    out = []
    for line in log.read_text().splitlines():
        if marker in line and line.startswith("  ") and "FAIL" not in line:
            label, values = line.split("|")[0], line.split("|")[1]
            words = label.split()
            # the first words are the description, the rest are the input values
            desc = re.split(r"\s{2,}", label.strip())[0]
            out.append(f"{desc:42s} {values.strip()}")
    return out


def figure(name, number, what, signals, t0, t1, labels=None, change_on=None, notes=(), relative=False):
    waves, end = read_vcd(SIM / f"{name}.vcd")
    t1 = t1 or end
    rows = len(labels) if labels else 0
    fig = plt.figure(figsize=(13, 0.62 * len(signals) + 1.6 + 0.19 * rows))
    grid = fig.add_gridspec(2, 1, height_ratios=[0.62 * len(signals) + 0.9, 0.19 * rows + 0.2], hspace=0.28)
    sub = grid[0].subgridspec(len(signals), 1, hspace=0.25)
    axes = [fig.add_subplot(sub[i]) for i in range(len(signals))]
    for ax in axes[1:]:
        ax.sharex(axes[0])
    colours = ["#1f5fa8", "#2f7d4f", "#b8362f", "#a0702a", "#6a4c93"]
    for k, (ax, (label, sig, bus)) in enumerate(zip(axes, signals)):
        draw(ax, waves[sig], t0, t1, bus, colours[k % len(colours)])
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_ylabel(label, rotation=0, ha="right", va="center", fontsize=9)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        if ax is not axes[-1]:
            ax.tick_params(labelbottom=False)
    if labels and change_on:
        edges = sorted({t for s in change_on for t, _ in waves[s] if t0 <= t < t1})
        if len(edges) != len(labels):
            raise ValueError(f"{name}: {len(edges)} input changes but {len(labels)} printed vectors")
        bounds = edges + [t1]
        for i, t in enumerate(edges):
            for ax in axes:
                ax.axvline(t, color="#999", lw=0.5, ls=":")
            axes[0].text((t + bounds[i + 1]) / 2, 1.08, str(i + 1), ha="center", va="bottom", fontsize=8,
                         fontweight="bold", transform=axes[0].get_xaxis_transform())
        key = fig.add_subplot(grid[1])
        key.axis("off")
        for i, text in enumerate(labels):
            key.text(0.0, 1 - (i + 0.5) / len(labels), f"{i + 1:2d}.  {text}", fontsize=8, va="center",
                     transform=key.transAxes, family="monospace")
    for t, text in notes:
        axes[-1].annotate(text, xy=(t, 0.15), xytext=(t, -1.3), fontsize=7.5, ha="center",
                          arrowprops=dict(arrowstyle="->", lw=0.7), annotation_clip=False)
    if relative:
        axes[-1].xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x - t0:.0f}"))
        axes[-1].set_xlabel("time from the first directed vector (ns)")
    else:
        axes[-1].set_xlabel("time (ns)")
    axes[-1].set_xlim(t0, t1)
    fig.suptitle(title(number, what), fontsize=10)
    OUT.mkdir(exist_ok=True)
    path = OUT / f"{number}_{what}.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path.relative_to(FPGA))


def main():
    # 4-bit CLA, directed tests (the exhaustive sweep is checked in the log, not dumped)
    waves, end = read_vcd(SIM / "tb_cla4.vcd")
    t0 = min(t for t, _ in waves["tb_cla4.a"] if t > 0)
    figure("tb_cla4", "3.1", "cla4-directed-vectors",
           [("A", "tb_cla4.a", True), ("B", "tb_cla4.b", True), ("Cin", "tb_cla4.cin", False),
            ("S", "tb_cla4.s", True), ("C4", "tb_cla4.cout", False)],
           t0, end, log_labels(SIM / "tb_cla4.log", "| C4="), ["tb_cla4.a", "tb_cla4.b", "tb_cla4.cin"], relative=True)

    # SIMD 8-bit adder, directed tests in both modes
    waves, end = read_vcd(SIM / "tb_simd8.vcd")
    t0 = min(t for t, _ in waves["tb_simd8.a"] if t > 0)
    figure("tb_simd8", "3.2", "simd8-directed-vectors",
           [("SIMD_MODE", "tb_simd8.simd_mode", False), ("A", "tb_simd8.a", True), ("B", "tb_simd8.b", True),
            ("Cin", "tb_simd8.cin", False), ("Cout CLA0", "tb_simd8.cout_lo", False),
            ("Cin CLA1 (gated)", "tb_simd8.cin_hi", False), ("S", "tb_simd8.s", True), ("Cout", "tb_simd8.cout", False)],
           t0, end, log_labels(SIM / "tb_simd8.log", "| CoutLo="),
           ["tb_simd8.a", "tb_simd8.b", "tb_simd8.cin", "tb_simd8.simd_mode"], relative=True)

    # Registered circuits: one-clock latency from input capture to output register
    figure("tb_registered", "3.3", "registered-latency",
           [("clk", "tb_registered.clk", False), ("en", "tb_registered.en", False),
            ("d_a", "tb_registered.d_a", True), ("d_b", "tb_registered.d_b", True),
            ("d_cin", "tb_registered.d_cin", False), ("d_mode", "tb_registered.d_mode", False),
            ("CLA4 q_s", "tb_registered.c_q_s", True), ("SIMD8 q_s", "tb_registered.m_q_s", True),
            ("SIMD8 q_cout", "tb_registered.m_q_cout", False)],
           20, 110, notes=[(45, "edge 1: 0x24, 0x81, Cin 1 captured"), (55, "edge 2: CLA4 S = 4+1+1 = 6 registered")])


if __name__ == "__main__":
    main()
