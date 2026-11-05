#!/usr/bin/env python3
"""Report figures. Every number shown comes from a result file or a simulation run here."""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

from arcs import INPUTS, OUTPUTS, build_bench, crossings
from candidates import adder_logic
from cellgen import config as cfg
from cellgen.schematic import draw
from cellgen.sim import ps_to_png, run_ngspice
from dff import tspc
from final_flow import FINAL, build, final_design
from postlayout import ExtractedCell
from render_mag import render

FIG = cfg.PART1 / "documentation" / "figures"
INK, MUTED, GRID, BOX, ACC = "#1f2933", "#6b7280", "#d9dee4", "#eef2f6", "#b42318"
TITLE = cfg.plot_title


def clean(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=7, length=2)


def run_vectors(ext, states, tag, period=2.0e-9):
    work = cfg.PART1 / "simulations" / "timing" / "figures"
    work.mkdir(parents=True, exist_ok=True)
    path = work / f"{tag}.cir"
    build_bench(ext, states, path, period)
    _, res = run_ngspice(path, timeout=600)
    wave = path.with_suffix(".txt")
    if not wave.exists():
        raise RuntimeError(res.stderr[-300:])
    names = wave.read_text().split("\n", 1)[0].split()
    data = np.loadtxt(wave, skiprows=1)
    return data[:, 0], {n.lower(): data[:, i] for i, n in enumerate(names)}


def strips(t, wave, names, title, path, tmin, tmax, marks=None, height=0.72):
    keep = (t >= tmin) & (t <= tmax)
    fig, axes = plt.subplots(len(names), 1, sharex=True, figsize=(9.2, height * len(names) + 1.2))
    for ax, n in zip(axes, names):
        ax.plot(t[keep] * 1e9, wave[f"v({n})"][keep], color=INK, lw=1.2)
        ax.axhline(0.9, color=GRID, lw=0.7, zorder=0)
        ax.set_ylim(-0.25, 2.05)
        ax.set_yticks([0, 1.8])
        ax.set_ylabel(n.upper() if n in OUTPUTS else n, rotation=0, ha="right", va="center", fontsize=8.5)
        clean(ax)
        for (tm, text) in (marks or {}).get(n, []):
            ax.plot([tm * 1e9], [0.9], marker="o", ms=3.5, color=ACC, zorder=5)
            ax.annotate(text, (tm * 1e9, 0.9), xytext=(6, 7), textcoords="offset points", fontsize=7.5, color=ACC)
    axes[-1].set_xlabel("time (ns)", fontsize=8)
    fig.suptitle(title, fontsize=9.5, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def fig_hint(ext):
    hint0, hint1 = 0b1111, 0b1111 | 1 << 8
    period = 2.0e-9
    t, wave = run_vectors(ext, [hint0, hint1, hint0], "hint", period)
    marks = {}
    results = []
    for k, edge in ((1, "rise"), (2, "fall")):
        lo, hi = np.searchsorted(t, [k * period, (k + 1) * period])
        t_in = crossings(t[lo:hi], wave["v(c0)"][lo:hi])[0]
        marks.setdefault("c0", []).append((t_in, f"C0 {edge}"))
        for o in OUTPUTS:
            cr = crossings(t[lo:hi], wave[f"v({o})"][lo:hi])
            if len(cr):
                new = adder_logic({p: ((hint1 if k == 1 else hint0) >> i) & 1 for i, p in enumerate(INPUTS)})[o]
                d = (cr[-1] - t_in) * 1e12
                marks.setdefault(o, []).append((cr[-1], f"{'tpLH' if new else 'tpHL'} {d:.1f} ps"))
                results.append(dict(c0_edge=edge, output=o, kind="tpLH" if new else "tpHL", delay_ps=round(d, 2)))
    strips(t, wave, ["c0"] + OUTPUTS, TITLE("1.9", "hint-vector-A1111-B0000-postlayout"), FIG / "hint_postlayout.png", 1.8e-9, 5.9e-9, marks)
    with open(FINAL / "hint_vector_postlayout.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    return results


def fig_worst(ext, tag):
    rows = list(csv.DictReader(open(cfg.PART1 / "simulations" / "timing" / f"post_{tag}" / "arcs.csv")))
    worst = max(rows, key=lambda r: float(r["tpd_pin_ps"]))
    pin = worst["pin"]
    state = int(worst["state"])
    nxt = state ^ (1 << INPUTS.index(pin))
    period = 2.0e-9
    t, wave = run_vectors(ext, [state, nxt, state], "worst", period)
    lo, hi = np.searchsorted(t, [period, 2 * period])
    t_in = crossings(t[lo:hi], wave[f"v({pin})"][lo:hi])[0]
    out = worst["output"]
    cr = crossings(t[lo:hi], wave[f"v({out})"][lo:hi])
    d = (cr[-1] - t_in) * 1e12
    marks = {pin: [(t_in, f"{pin} {worst['pin_edge']}")], out: [(cr[-1], f"{d:.1f} ps")]}
    strips(t, wave, [pin] + OUTPUTS, TITLE("1.9", f"worst-arc-{pin}-to-{out}-postlayout"), FIG / "worst_arc_postlayout.png",
           1.8e-9, 3.6e-9, marks)
    with open(FINAL / "worst_arc_rerun.json", "w") as fh:
        json.dump(dict(worst_from_all_arcs=worst, rerun_ps=round(d, 2)), fh, indent=1)
    return worst, d


def fig_native_ngspice(ext):
    """One plot exactly as ngspice draws it, showing the course's curplottitle convention."""
    work = cfg.PART1 / "simulations" / "timing" / "figures"
    path = work / "native.cir"
    build_bench(ext, [0b1111, 0b1111 | 1 << 8, 0b1111], path, 2.0e-9)
    title = TITLE("1.9", "hint-vector-ngspice-plot")
    text = path.read_text().replace("wrdata native.txt", f"set curplottitle={title}\nset hcopypscolor=1\nset color0=white\nset color1=black\n"
                                    "hardcopy native.ps v(c0) v(s3)+2 v(c4)+4 xlimit 1.9n 3.2n\nwrdata native.txt")
    path.write_text(text)
    run_ngspice(path, timeout=300)
    png = ps_to_png(work / "native.ps", dpi=110)
    (FIG / "native_ngspice.png").write_bytes(png.read_bytes())


def fig_system():
    system = json.loads((FINAL / "system.json").read_text())
    path = cfg.PART1 / "simulations" / "timing" / "registered" / "postlayout" / "postlayout_at_limit.npz"
    data = np.load(path, allow_pickle=False)
    names = [str(n).lower() for n in data["names"]]
    arr = data["data"]
    wave = {n: arr[:, i] for i, n in enumerate(names)}
    t = wave["time"]
    period = system["postlayout"]["min_period_ps"] * 1e-12
    labels = ["clk", "d_c0", "d_a0", "d_b0", "q_s0", "q_s1", "q_s2", "q_s3", "q_c4"]
    keep = t <= 2 * period + 12 * period
    fig, axes = plt.subplots(len(labels), 1, sharex=True, figsize=(9.2, 0.62 * len(labels) + 1.2))
    for ax, n in zip(axes, labels):
        ax.plot(t[keep] * 1e9, wave[f"v({n})"][keep], color=INK, lw=1.1)
        ax.set_ylim(-0.25, 2.05)
        ax.set_yticks([0, 1.8])
        ax.set_ylabel(n, rotation=0, ha="right", va="center", fontsize=8)
        clean(ax)
    axes[-1].set_xlabel("time (ns)", fontsize=8)
    fig.suptitle(TITLE("1.6", f"registered-system-postlayout-T{system['postlayout']['min_period_ps']:.0f}ps"), fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "system_postlayout.png", dpi=170)
    plt.close(fig)


def fig_dff_sweep(cell_name):
    rows = list(csv.DictReader(open(cfg.PART1 / "simulations" / "timing" / "dff" / cell_name / "setup_sweep.csv")))
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4), sharey=True)
    for ax, value, label in ((axes[0], "1", "D rising (Q rises)"), (axes[1], "0", "D falling (Q falls)")):
        sel = [r for r in rows if r["data"] == value and r["tcq_ps"] not in ("", "None")]
        sel.sort(key=lambda r: float(r["d_to_clk_ps"]))
        x = [float(r["d_to_clk_ps"]) for r in sel]
        keep = [i for i, v in enumerate(x) if v <= 300]
        ax.plot([x[i] for i in keep], [float(sel[i]["tcq_ps"]) for i in keep], color=INK, lw=1.4, marker="o", ms=3)
        ax.plot([x[i] for i in keep], [float(sel[i]["tdq_ps"]) for i in keep], color=MUTED, lw=1.2, marker="s", ms=3)
        ax.annotate("clock to Q", (x[keep[-1]], float(sel[keep[-1]]["tcq_ps"])), xytext=(-52, 8), textcoords="offset points", fontsize=8, color=INK)
        ax.annotate("D to Q", (x[keep[-1]], float(sel[keep[-1]]["tdq_ps"])), xytext=(-38, 6), textcoords="offset points", fontsize=8, color=MUTED)
        ax.set_title(label, fontsize=8.5)
        ax.set_xlabel("D to clock time (ps)", fontsize=8)
        ax.grid(color=GRID, lw=0.5)
        clean(ax)
    axes[0].set_ylabel("delay (ps)", fontsize=8)
    fig.suptitle(TITLE("1.4", "tspc-flipflop-setup-sweep"), fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "dff_sweep.png", dpi=170)
    plt.close(fig)


def box(ax, x, y, w, h, title, sub=""):
    ax.add_patch(Rectangle((x, y), w, h, fc=BOX, ec=INK, lw=1.2))
    ax.text(x + w / 2, y + h - 0.2, title, ha="center", va="top", fontsize=9, weight="bold", color=INK)
    if sub:
        ax.text(x + w / 2, y + h - 0.68, sub, ha="center", va="top", fontsize=7.2, color=INK, linespacing=1.35)


def arrow(ax, p, q, label="", color=INK, dy=0.07):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=8, lw=1.1, color=color, shrinkA=0, shrinkB=0))
    if label:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, label, ha="center", va="bottom", fontsize=7.3, color=color)


def fig_block():
    fig, ax = plt.subplots(figsize=(11.6, 5.0))
    ax.set_xlim(0, 21)
    ax.set_ylim(0, 8.6)
    ax.axis("off")
    ax.set_title(TITLE("1.1", "block-diagram-prefix-CLA"), fontsize=9.5)
    ax.text(0.1, 6.3, "A[3:0]", fontsize=8.5)
    ax.text(0.1, 4.9, "B[3:0]", fontsize=8.5)
    arrow(ax, (1.0, 6.4), (1.6, 6.4))
    arrow(ax, (1.0, 5.0), (1.6, 5.0))
    box(ax, 1.6, 3.0, 3.5, 4.8, "P/G block", "per bit:\nNAND2 gives g-bar\nNOR2 gives t-bar\nAOI21 gives P\nOAI21 gives P-bar")
    box(ax, 6.6, 3.0, 3.3, 4.8, "Prefix level 1", "group (1:0) and (3:2):\nOAI21 gives G\nNOR2 gives T\nbit 2: inverters\ngive g2, t2")
    box(ax, 11.0, 3.0, 3.1, 4.8, "Prefix level 2", "(3:0), (2:0), (1:0):\nAOI21 gives G-bar\nNAND2 gives T-bar\nbit 1 group:\ninverters")
    box(ax, 15.2, 3.0, 2.4, 4.8, "Carry stage", "OAI21 with\nC0-bar:\nC1, C2,\nC3, C4")
    box(ax, 18.3, 3.0, 2.4, 3.5, "Sum block", "dual-rail XOR:\nSi = P xor C")
    arrow(ax, (5.1, 5.6), (6.6, 5.6), "g-bar, t-bar")
    arrow(ax, (9.9, 5.6), (11.0, 5.6), "G, T")
    arrow(ax, (14.1, 5.6), (15.2, 5.6), "G-bar, T-bar")
    arrow(ax, (17.6, 5.0), (18.3, 5.0), "C[3:1]", dy=0.05)
    ax.plot([3.3, 3.3, 19.5, 19.5], [7.8, 8.25, 8.25, 6.5], color=INK, lw=1.1)
    ax.text(11.5, 8.28, "P[3:0], P-bar[3:0]: sum path only, carries use g-bar and t-bar", ha="center", va="bottom", fontsize=7.3)
    # bit 0 goes directly to the carry stage
    ax.plot([5.1, 5.6, 5.6, 16.3, 16.3], [3.5, 3.5, 2.5, 2.5, 3.0], color=INK, lw=1.1)
    ax.text(10.7, 2.53, "g0-bar, t0-bar direct to C1", ha="center", va="bottom", fontsize=7.3)
    ax.text(0.1, 1.15, "Cin", fontsize=8.5, color=ACC, weight="bold")
    ax.plot([0.8, 16.7, 16.7], [1.25, 1.25, 3.0], color=ACC, lw=1.4)
    ax.text(9.0, 1.28, "C0 via inverter: late input, one gate from each carry", ha="center", va="bottom", fontsize=7.3, color=ACC)
    ax.plot([16.7, 19.0, 19.0], [1.25, 1.25, 3.0], color=ACC, lw=1.4)
    ax.text(18.0, 1.0, "C0 to S0", ha="center", va="top", fontsize=7.3, color=ACC)
    arrow(ax, (20.7, 4.7), (21.0, 4.7))
    ax.text(20.75, 4.8, "S[3:0]", fontsize=7.8, ha="left")
    ax.plot([17.6, 17.95, 17.95, 20.7], [3.5, 3.5, 2.5, 2.5], color=INK, lw=1.1)
    arrow(ax, (20.7, 2.5), (21.0, 2.5))
    ax.text(20.0, 2.55, "C4 = Cout", fontsize=7.8, ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(FIG / "block_diagram.png", dpi=170)
    plt.close(fig)


def fig_floorplan():
    system = json.loads((FINAL / "system.json").read_text())
    places = system["placements"]
    x1 = max(p[1] + p[3] for p in places)
    y1 = max(p[2] + p[4] for p in places)
    fig, ax = plt.subplots(figsize=(8.8, 8.8 * y1 / x1 + 0.7))
    for name, x, y, w, h in places:
        kind = "#dfe9f5" if name.startswith("pg") else "#f5ecd9" if name.startswith("carry") else "#e3f1e3" if name.startswith("sum") else "#eee3f3"
        ax.add_patch(Rectangle((x, y), w, h, fc=kind, ec=INK, lw=1))
        ax.text(x + w / 2, y + h / 2, name, ha="center", va="center", fontsize=7.5, color=INK)
    ax.set_xlim(-40, x1 + 10)
    ax.set_ylim(-10, y1 + 10)
    ax.set_aspect("equal")
    ax.set_xlabel("x (lambda)", fontsize=8)
    ax.set_ylabel("y (lambda)", fontsize=8)
    clean(ax)
    ax.set_title(TITLE("1.7", "floor-plan-registered-adder"), fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "floorplan.png", dpi=170)
    plt.close(fig)


def fig_tradeoff():
    path = cfg.PART1 / "results" / "phase4_tradeoff.csv"
    if not path.exists():
        return
    rows = [r for r in csv.DictReader(open(path))]
    rows.sort(key=lambda r: float(r["area_um2"]))
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.3))
    x = [float(r["area_um2"]) for r in rows]
    y = [float(r["post_pin_ps"]) for r in rows]
    adp = [float(r["adp_um2_ns"]) for r in rows]
    axes[0].plot(x, y, color=INK, lw=1.4, marker="o", ms=4)
    for r, xi, yi in zip(rows, x, y):
        axes[0].annotate(f"x{float(r['scale']):g}", (xi, yi), xytext=(5, 4), textcoords="offset points", fontsize=7.5)
    axes[0].set_xlabel("layout area (um2)", fontsize=8)
    axes[0].set_ylabel("post-layout worst delay (ps)", fontsize=8)
    axes[1].plot(x, adp, color=INK, lw=1.4, marker="o", ms=4)
    axes[1].set_xlabel("layout area (um2)", fontsize=8)
    axes[1].set_ylabel("ADP (um2 ns)", fontsize=8)
    for a in axes:
        a.grid(color=GRID, lw=0.5)
        clean(a)
    fig.suptitle(TITLE("1.8", "uniform-scaling-delay-area"), fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "tradeoff.png", dpi=170)
    plt.close(fig)


def fig_convergence(label):
    rows = list(csv.DictReader(open(cfg.PART1 / "simulations" / "optimisation" / label / "log.csv")))
    fig, ax = plt.subplots(figsize=(8.2, 2.9))
    ax.plot([int(r["iteration"]) for r in rows], [float(r["worst_working_ps"]) for r in rows], color=INK, lw=1.4, marker="o", ms=3)
    ax.set_xlabel("accepted iteration", fontsize=8)
    ax.set_ylabel("worst tracked delay from driver input (ps)", fontsize=8)
    ax.grid(color=GRID, lw=0.5)
    clean(ax)
    ax.set_title(TITLE("1.2", f"sizing-convergence-{label.replace('_', '-')}"), fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "convergence.png", dpi=170)
    plt.close(fig)


def schematics(label, sizes, flips):
    adder = build(label, sizes, flips, "cla_final")
    out = cfg.PART1 / "schematics" / "transistor_level" / "final"
    out.mkdir(parents=True, exist_ok=True)
    seen = {}
    for _, cell, _ in adder.instances:
        if cell.name not in seen:
            seen[cell.name] = cell
            draw(cell, out / cell.name)
    dff = json.loads((FINAL / "dff.json").read_text())["params"]
    ff = tspc(dff["s1"], dff["s2"], dff["s3"], dff["q"])
    draw(ff, out / "dff_final")
    (out / "index.txt").write_text("\n".join(sorted(seen)) + "\ndff_final\n")
    return adder, ff


def layouts(tag):
    work = cfg.PART1 / "layout" / "integrated" / tag
    render(f"top_{tag}", work, FIG / "layout_adder.png", TITLE("1.8", "adder-layout-MAGIC-mag-data"), size=9.2)
    reg = cfg.PART1 / "layout" / "integrated" / "registered"
    render("reg_final_top", reg, FIG / "layout_registered.png", TITLE("1.8", "registered-adder-layout-MAGIC-mag-data"), size=9.2)
    render("pg1", reg, FIG / "layout_pg.png", TITLE("1.5", "PG-bit-layout"), size=7)
    render("sum1", reg, FIG / "layout_sum.png", TITLE("1.5", "sum-bit-layout"), size=7)
    render("carry", reg, FIG / "layout_carry.png", TITLE("1.5", "carry-block-layout"), size=9.2)
    render("fia0", reg, FIG / "layout_dff.png", TITLE("1.5", "tspc-flipflop-layout"), size=7)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    label, sizes, flips, tag = final_design()
    ext = ExtractedCell(cfg.PART1 / "layout" / "integrated" / tag / f"top_{tag}.spice", "final_post", INPUTS, OUTPUTS)
    fig_block()
    print("hint", fig_hint(ext))
    print("worst", fig_worst(ext, tag))
    fig_native_ngspice(ext)
    adder, ff = schematics(label, sizes, flips)
    fig_dff_sweep(ff.name)
    fig_system()
    fig_floorplan()
    fig_tradeoff()
    fig_convergence(f"aware_{label}_round1")
    base = cfg.PART1 / "simulations" / "functional" / "blocks"
    (FIG / "wave_pg.png").write_bytes((base / "pg_bit_x1" / "waves.png").read_bytes())
    (FIG / "wave_xor.png").write_bytes((base / "xor_aoi22_x1" / "waves.png").read_bytes())
    layouts(tag)
    print("figures done")


if __name__ == "__main__":
    main()
