#!/usr/bin/env python3
"""Figures for the submission report that the part folders do not already have.

  sims   pre- and post-layout waveforms of every gate, the flip-flop and each block, plus the
         full registered circuit, all with the course plot titles. Also measures each gate's delay.
  shots  screenshots of each gate and block in MAGIC's own window (XQuartz must be running)

Run from this folder:  python3 figures.py sims   and   python3 figures.py shots
Everything is written to figures/ and gate_delays.json here.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "part1" / "cells"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arcs import TB_CELLS, crossings, euler_walk
from candidates import INPUTS, OUTPUTS
from cellgen import Block, config as cfg, parse_flat
from cellgen.bench import pwl_lines
from cellgen.sim import run_ngspice
from cellgen.switchlevel import evaluate
from dff import tspc
from final_flow import FINAL, build, final_design
from library import aoi21, inv, nand, nor, oai21, xor_aoi22
from postlayout import ExtractedCell
from registered import REG_INPUTS, REG_OUTPUTS, registered_top, run_system
from top import adder_rows, partition

FIG = HERE / "figures"
WORK = HERE / "work"
BLOCKS = ROOT / "part1" / "layout" / "individual_blocks"
MODEL = ROOT / "part1" / "spice" / "models" / "TSMC_180nm.txt"

# gate name in the report, library cell, free inputs, complement inputs (name -> source), outputs
GATES = [
    ("Inverter", inv(1.0), ["a"], {}, ["y"]),
    ("NAND2", nand(2, 1.0), ["i0", "i1"], {}, ["y"]),
    ("NOR2", nor(2, 1.0), ["i0", "i1"], {}, ["y"]),
    ("AOI21", aoi21(1.0), ["a", "b", "c"], {}, ["y"]),
    ("OAI21", oai21(1.0), ["a", "b", "c"], {}, ["y"]),
    ("AOI22 XOR (sum)", xor_aoi22(1.0), ["p", "c"], {"pb": "p"}, ["s"]),
]


def walk_vectors(free, comp, steps=None):
    """Euler walk over the free inputs: every single-input change from every state."""
    walk = euler_walk(len(free)) if len(free) > 1 else [0, 1, 0, 1, 0]
    if steps:
        walk = walk[:steps + 1]
    out = []
    for s in walk:
        v = {p: (s >> k) & 1 for k, p in enumerate(free)}
        for c, src in comp.items():
            v[c] = 1 - v[src]
        out.append(v)
    return out


def simulate(cell, ins, outs, vectors, tag, period=1.0e-9):
    """Inputs through tb_x1 then tb_x2 drivers, each output into the 20/10 lambda inverter."""
    WORK.mkdir(parents=True, exist_ok=True)
    model = os.path.relpath(MODEL, WORK)
    net = f"* {tag}\n.include {model}\n.options reltol=1e-4\nVDD vdd gnd 1.8\n" + cell.spice() + TB_CELLS
    for p in ins:
        net += pwl_lines(f"V{p}", f"src_{p}", [1 - v[p] for v in vectors], period, 20e-12)
        net += f"Xs_{p} src_{p} drv_{p} vdd gnd tb_x1\nXd_{p} drv_{p} {p} vdd gnd tb_x2\n"
    for o in outs:
        net += f"Xl_{o} {o} lo_{o} vdd gnd tb_x1\n"
    net += f"X0 {' '.join(cell.ports[:-2])} vdd gnd {cell.name}\n"
    total = len(vectors) * period
    net += (f".tran 5p {total:.5e}\n.control\nset wr_singlescale\nset wr_vecnames\nrun\n"
            f"wrdata {tag}.txt {' '.join(f'v({n})' for n in ins + outs)}\nquit\n.endc\n.end\n")
    cir = WORK / f"{tag}.cir"
    cir.write_text(net)
    _, res = run_ngspice(cir, timeout=1200)
    wave = WORK / f"{tag}.txt"
    if not wave.exists():
        raise RuntimeError(f"{tag}: {res.stderr[-300:]}")
    names = wave.read_text().split("\n", 1)[0].split()
    data = np.loadtxt(wave, skiprows=1)
    wave.unlink()
    col = {n.lower(): i for i, n in enumerate(names)}
    return data[:, 0], {n: data[:, col[f"v({n})"]] for n in ins + outs}


def delays(t, waves, free, outs, vectors, devices, period=1.0e-9):
    """Worst tpLH and tpHL over the single-input changes, and output level errors."""
    worst = {"tplh_ps": 0.0, "tphl_ps": 0.0}
    errors = 0
    for k in range(1, len(vectors)):
        changed = [p for p in free if vectors[k][p] != vectors[k - 1][p]]
        lo, hi = np.searchsorted(t, [k * period, (k + 1) * period])
        tw = t[lo:hi + 1]
        old, _ = evaluate(devices, vectors[k - 1])
        new, _ = evaluate(devices, vectors[k])
        for o in outs:
            v = waves[o][lo:hi + 1]
            if (new[o] and v[-1] < 1.62) or (not new[o] and v[-1] > 0.18):
                errors += 1
            if old[o] == new[o] or len(changed) != 1:
                continue
            tin = crossings(tw, waves[changed[0]][lo:hi + 1])
            cr = crossings(tw, v)
            if len(cr) and len(tin):
                key = "tplh_ps" if new[o] else "tphl_ps"
                worst[key] = max(worst[key], (cr[-1] - tin[0]) * 1e12)
    worst["errors"] = errors
    return {k: round(v, 2) if isinstance(v, float) else v for k, v in worst.items()}


def plot_waves(t, waves, ins, outs, title, png):
    sig = ins + outs
    fig, axes = plt.subplots(len(sig), 1, figsize=(9, 0.62 * len(sig) + 1.0), sharex=True)
    axes = np.atleast_1d(axes)
    for ax, n in zip(axes, sig):
        ax.plot(t * 1e9, waves[n], color="#c0392b" if n in outs else "#1f5fa8", lw=1.1)
        ax.set_ylim(-0.2, 2.0)
        ax.set_yticks([0, 1.8])
        ax.tick_params(labelsize=7)
        ax.set_ylabel(n, rotation=0, ha="right", va="center", fontsize=8)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("time (ns)", fontsize=8)
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(png, dpi=150)
    plt.close(fig)


def blocks():
    """The three block types as laid out alone in Part I: P/G bit 0, the carry block, sum bit 0."""
    label, sizes, flips, _ = final_design()
    adder = build(label, sizes, flips, "cla_final")
    tiles = {t.name: t for row in partition(adder, adder_rows(adder), INPUTS + OUTPUTS) for t in row}
    out = []
    for name, nice in (("pg0", "P/G block, bit 0"), ("carry", "Carry block"), ("sum0", "Sum block, bit 0")):
        tile = tiles[name]
        made = {pins[o] for _, cell, pins in tile.instances for o in cell.outputs}
        outs = sorted(n for n in tile.inputs if n in made)
        ins = sorted(n for n in tile.inputs if n not in made)
        out.append((nice, name, Block(f"{name}_b", ins, outs, None, tile.instances, tile.description), ins, outs))
    return out


def free_of(ins):
    return [p for p in ins if not (p.endswith("b") and p[:-1] in ins)]


def stage_sims():
    FIG.mkdir(exist_ok=True)
    table = {}
    # gates
    for nice, cell, free, comp, outs in GATES:
        ins = free + list(comp)
        vecs = walk_vectors(free, comp)
        devs = parse_flat(cell.spice(), cell.name)
        ext = ExtractedCell(BLOCKS / cell.name / f"{cell.name}.spice", f"{cell.name}x", ins, outs)
        row = {}
        for view, c, q in (("schematic", cell, "3"), ("post-layout", ext, "5")):
            t, w = simulate(c, ins, outs, vecs, f"{cell.name}_{view}")
            row[view] = delays(t, w, free, outs, vecs, devs)
            plot_waves(t, w, ins, outs, cfg.plot_title(q, f"{cell.name}-{view}"), FIG / f"gate_{cell.name}_{view}.png")
        table[nice] = dict(cell=cell.name, transistors=cell.transistor_count, **row)
        print(nice, row, flush=True)
    # blocks: plot a short walk, delays are the exhaustive Part I results
    for nice, name, block, ins, outs in blocks():
        free = free_of(ins)
        comp = {p: p[:-1] for p in ins if p not in free}
        vecs = walk_vectors(free, comp, steps=24 if len(free) > 3 else None)
        ext = ExtractedCell(BLOCKS / block.name / f"{block.name}.spice", f"{name}x", ins, outs)
        for view, c, q in (("schematic", block, "3"), ("post-layout", ext, "5")):
            t, w = simulate(c, ins, outs, vecs, f"{name}_{view}")
            plot_waves(t, w, ins, outs, cfg.plot_title(q, f"{name}-block-{view}"), FIG / f"block_{name}_{view}.png")
        print(nice, "plotted", flush=True)
    (HERE / "gate_delays.json").write_text(json.dumps(table, indent=1))
    stage_dff()
    stage_system()


def stage_dff():
    """Flip-flop function: D changes between clock edges, Q follows on each rising edge."""
    p = json.loads((FINAL / "dff.json").read_text())
    cell = tspc(**p["params"])
    ext = ExtractedCell(BLOCKS / cell.name / f"{cell.name}.spice", "dffx", ["d", "clk"], ["q"])
    period = 2e-9
    d_bits = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0]
    for view, c, q in (("schematic", cell, "3"), ("post-layout", ext, "5")):
        WORK.mkdir(parents=True, exist_ok=True)
        model = os.path.relpath(MODEL, WORK)
        net = f"* dff {view}\n.include {model}\n.options reltol=1e-4\nVDD vdd gnd 1.8\n" + c.spice() + TB_CELLS
        # D changes a quarter period after each rising edge, the clock rises every 2 ns
        pts = ["0 1.8"]
        cur = 1.8
        for k, b in enumerate(d_bits):
            lvl = 0.0 if b else 1.8
            tt = k * period + 0.5e-9
            if lvl != cur:
                pts += [f"{tt:.4e} {cur}", f"{tt + 20e-12:.4e} {lvl}"]
                cur = lvl
        clk = " ".join(f"{(k * period + 1e-9):.4e} 1.8 {(k * period + 1e-9 + 20e-12):.4e} 0 {(k * period + 2e-9 - 20e-12):.4e} 0 {(k * period + 2e-9):.4e} 1.8"
                       for k in range(len(d_bits)))
        net += f"Vd sd gnd PWL({' '.join(pts)})\nXd sd d vdd gnd tb_x1\n"
        net += f"Vc sc gnd PWL(0 1.8 {clk})\nXc sc clk vdd gnd tb_x2\n"
        net += f"X0 d clk q vdd gnd {c.name}\nXl q ql vdd gnd tb_x1\nCload q gnd {p['load_ff']}f\n"
        total = len(d_bits) * period
        net += (f".tran 5p {total:.4e}\n.control\nset wr_singlescale\nset wr_vecnames\nrun\nwrdata dff_{view}.txt v(clk) v(d) v(q)\nquit\n.endc\n.end\n")
        cir = WORK / f"dff_{view}.cir"
        cir.write_text(net)
        run_ngspice(cir, timeout=600)
        data = np.loadtxt(WORK / f"dff_{view}.txt", skiprows=1)
        t = data[:, 0]
        plot_waves(t, {"clk": data[:, 1], "D": data[:, 2], "Q": data[:, 3]}, ["clk", "D"], ["Q"],
                   cfg.plot_title(q, f"tspc-dff-{view}"), FIG / f"dff_{view}.png")
    print("dff plotted", flush=True)


def stage_system():
    """Full registered circuit, schematic and extracted, on a few annotated additions."""
    label, sizes, flips, _ = final_design()
    adder = build(label, sizes, flips, "cla_final")
    p = json.loads((FINAL / "dff.json").read_text())["params"]
    sch = registered_top(adder, tspc(**p), "reg_sch")
    post = ExtractedCell(ROOT / "part1" / "extraction" / "registered_extracted.spice", "regpost", REG_INPUTS, REG_OUTPUTS)
    adds = [(7, 1, 0), (15, 0, 1), (5, 10, 0), (12, 9, 1), (3, 6, 0), (15, 15, 1), (0, 0, 0), (9, 7, 0)]
    states = [a | (b << 4) | (c << 8) for a, b, c in adds]
    period = 2e-9
    for view, top, q in (("schematic", sch, "6"), ("post-layout", post, "8")):
        res = run_system(top, period, states, WORK / "system", f"sys_{view}", plot=True)
        z = np.load(WORK / "system" / f"sys_{view}.npz")
        names = [str(n).lower() for n in z["names"]]
        d = z["data"]
        col = {n: i for i, n in enumerate(names)}
        t = d[:, 0] * 1e9
        edges = 2 * period + np.arange(len(states) + 3) * period
        fig, axes = plt.subplots(8, 1, figsize=(10, 6.6), sharex=True)
        rows = [("clk", "v(clk)")] + [(f"q_s{i}", f"v(q_s{i})") for i in range(4)] + [("q_c4", "v(q_c4)")]
        for ax, (lab, key) in zip(axes[:6], rows):
            ax.plot(t, d[:, col[key]], lw=1.0, color="#c0392b" if lab != "clk" else "#555555")
            ax.set_ylabel(lab, rotation=0, ha="right", va="center", fontsize=8)
            ax.set_ylim(-0.2, 2.0)
            ax.set_yticks([])
            ax.grid(alpha=0.3)
        for k, (a, b, c) in enumerate(adds):
            axes[6].text((edges[k] - 0.25 * period) * 1e9, 0.5, f"{a}+{b}+{c}", ha="center", fontsize=7)
            axes[7].text((edges[k + 2] - 0.5 * period) * 1e9, 0.5, f"{a + b + c}", ha="center", fontsize=7, color="#c0392b")
        axes[6].set_ylabel("inputs", rotation=0, ha="right", va="center", fontsize=8)
        axes[7].set_ylabel("expected\nsum", rotation=0, ha="right", va="center", fontsize=8)
        for ax in axes[6:]:
            ax.set_yticks([])
            ax.set_ylim(0, 1)
        axes[-1].set_xlabel("time (ns)", fontsize=8)
        fig.suptitle(cfg.plot_title(q, f"registered-adder-{view}") + f"  ({res['errors']} wrong samples)", fontsize=9)
        fig.tight_layout()
        fig.savefig(FIG / f"system_{view}.png", dpi=150)
        plt.close(fig)
        print("system", view, res["errors"], "errors", flush=True)


def stage_shots():
    from magic_shot import shoot
    jobs = [(BLOCKS / c.name, c.name, FIG / f"magic_gate_{c.name}.png", (900, 880)) for _, c, _, _, _ in GATES]
    p = json.loads((FINAL / "dff.json").read_text())["params"]
    ff = tspc(**p).name
    jobs.append((BLOCKS / ff, ff, FIG / "magic_gate_dff.png", (900, 880)))
    for name in ("pg0_b", "carry_b", "sum0_b"):
        jobs.append((BLOCKS / name, name, FIG / f"magic_block_{name}.png", (1300, 880) if name == "carry_b" else (900, 880)))
    for folder, cell, png, size in jobs:
        for attempt in range(3):
            try:
                shoot(folder, cell, png, size=size, timeout=90)
                print("ok", png.name, flush=True)
                break
            except Exception as exc:
                print("retry", png.name, type(exc).__name__, flush=True)


if __name__ == "__main__":
    globals()[f"stage_{sys.argv[1]}"]()
