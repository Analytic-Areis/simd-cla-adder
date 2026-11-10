#!/usr/bin/env python3
"""Transistor-level schematic of the whole 4-bit CLA and its flip-flops, for the report.

Drawn from the same cell objects that write the netlist, so drawing and netlist cannot differ.
The circuit is split into its stages, one figure each, and every gate is drawn transistor by
transistor with its sizes. Gates connect by net name: each input and output carries the name
of the net it is on, in blue, so a net can be followed from the gate that drives it to every
gate it feeds. A check at the end confirms every transistor of the netlist was drawn once.

Run:  python3 full_schematic.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "part1" / "cells"))

import json
import re
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cellgen.schematic as sch
from cellgen import config as cfg
from cellgen.cell import GateStage, StagedCell
from dff import tspc
from final_flow import FINAL, build, final_design

FIG = HERE / "figures"
GAP = 0.7
ORIG_TEX = sch.tex
UNIT = 0.5      # inches per drawing unit, the same in every figure


def pretty(net):
    """Net name as printed: g1_0 -> G(1:0), g3_0b -> G-bar(3:0); others as the cell library prints them."""
    m = re.fullmatch(r"([gt])(\d)_(\d)(b?)", net)
    if m:
        base, hi, lo, bar = m.groups()
        body = rf"\overline{{\mathrm{{{base.upper()}}}}}" if bar else rf"\mathrm{{{base.upper()}}}"
        return f"${body}_{{{hi}:{lo}}}$"
    return ORIG_TEX(net)


def panel_size(cell):
    stages = cell.stages if isinstance(cell, StagedCell) else [cell]
    w, h = 0.0, 0.0
    for st in stages:
        c = st.cell if isinstance(st, GateStage) else st
        w += max(sch.extent(c.pun)[0], sch.extent(c.pdn)[0]) + 1.9
        h = max(h, sch.extent(c.pun)[1] + sch.extent(c.pdn)[1] + GAP + 1.0)
    return w, h


def draw_instance(ax, inst, cell, pins, role, local=None):
    """One gate, inputs and output labelled with the nets they connect to.
    pins maps pin -> net; local maps a net inside a multi-stage cell -> its printed label."""
    stages = cell.stages if isinstance(cell, StagedCell) else [cell]
    local = local or {}
    sch.tex = lambda n: local[n] if n in local else pretty(pins.get(n, n))
    w, h = panel_size(cell)
    ax.set_xlim(0, w)
    ax.set_ylim(-0.6, h + 0.75)
    ax.axis("off")
    drawn, x = [], 0.0
    for st in stages:
        c = st.cell if isinstance(st, GateStage) else st
        out = st.out if isinstance(st, GateStage) else c.output
        sw = max(sch.extent(c.pun)[0], sch.extent(c.pdn)[0]) + 1.9
        d, _ = sch._gate_panel(ax, c.pun, c.pdn, x + sw / 2 + 0.1, 0.0, GAP, out, sw / 2 - 0.35)
        drawn += d
        x += sw
    sch.tex = ORIG_TEX
    ax.set_title(f"{inst}: {role}", fontsize=10.5, weight="bold", color=sch.INK, pad=2, loc="left")
    ax.add_patch(plt.Rectangle((0, -0.55), w, h + 1.25, fill=False, ec="#9aa5b1", lw=0.8, ls="--", clip_on=False))
    return drawn


def figure(rows, title, stem, note):
    """rows: lists of (instance, cell, pins, role, local). Panels top-aligned in rows, all at one scale.
    Saved as PDF (vector, for the report, zoomable) and PNG (for a quick look)."""
    row_h = [max(panel_size(it[1])[1] for it in r) + 2.2 for r in rows]
    width = max(sum(panel_size(it[1])[0] + 0.5 for it in r) for r in rows)
    top, bottom = 1.2, 1.4          # units for the title and the note
    total = sum(row_h) + top + bottom
    fig = plt.figure(figsize=(width * UNIT, total * UNIT))
    drawn, y = [], total - top
    for r, rh in zip(rows, row_h):
        x = 0.0
        for inst, cell, pins, role, local in r:
            w, h = panel_size(cell)
            ph = h + 1.35                       # axes height incl. title room, matches draw_instance ylim
            ax = fig.add_axes([x / width, (y - 0.5 - ph) / total, w / width, ph / total])
            drawn += [(inst, d.name) for d in draw_instance(ax, inst, cell, pins, role, local)]
            x += w + 0.5
        y -= rh
    fig.text(0.5, 1 - 0.45 / total, title, ha="center", va="center", fontsize=14, color=sch.INK)
    note = "\n".join(textwrap.wrap(note, int(width * UNIT * 9)))   # about 9 characters an inch at 11 pt
    fig.text(0.5, 0.45 / total, note, ha="center", va="center", fontsize=11, color=sch.INK)
    fig.savefig(FIG / f"{stem}.pdf")
    fig.savefig(FIG / f"{stem}.png", dpi=110)
    plt.close(fig)
    return drawn


ROLE = {"nand": "NAND2, generate-bar", "nor": "NOR2, transmit-bar", "aoi": "AOI21, propagate P", "oai": "OAI21, P-bar",
        "invc0": "inverter, C0-bar", "g10": "OAI21, G(1:0)", "t10": "NOR2, T(1:0)", "g32": "OAI21, G(3:2)",
        "t32": "NOR2, T(3:2)", "ig2": "inverter, g2", "it2": "inverter, t2", "g30": "AOI21, G-bar(3:0)",
        "t30": "NAND2, T-bar(3:0)", "g20": "AOI21, G-bar(2:0)", "t20": "NAND2, T-bar(2:0)", "ig10": "inverter, G-bar(1:0)",
        "it10": "inverter, T-bar(1:0)", "c1": "OAI21, carry C1", "c2": "OAI21, carry C2", "c3": "OAI21, carry C3",
        "c4g": "OAI21, carry C4", "x": "AOI22 XOR with C-bar inverter, sum"}


def role(inst):
    if inst in ROLE:
        return ROLE[inst]
    base, bit = inst.rstrip("0123456789"), inst[len(inst.rstrip("0123456789")):]
    return f"{ROLE[base]} {('S' + bit) if base == 'x' else ''}".strip() + ("" if base == "x" else f", bit {bit}")


def main():
    FIG.mkdir(exist_ok=True)
    label, sizes, flips, _ = final_design()
    adder = build(label, sizes, flips, "cla_final")
    inst = {i[0]: i for i in adder.instances}

    def pick(*rows):
        out = []
        for r in rows:
            row = []
            for n in r:
                local = {}
                if n.startswith("x"):   # the sum cell inverts its carry locally
                    local = {"cb": rf"$\overline{{\mathrm{{c}}}}_{{{n[1]}}}'$"}
                row.append((n, inst[n][1], inst[n][2], role(n), local))
            out.append(row)
        return out

    note = (r"Every transistor of the adder netlist, W/L in $\lambda$. Gates connect by net name: an output label is the same "
            r"net as every input label with that name. Bars mark active-low nets; blue labels are nodes inside a gate.")
    drawn = []
    drawn += figure(pick(*[[f"{g}{b}" for g in ("nand", "nor", "aoi", "oai")] for b in range(4)]),
                    cfg.plot_title("2", "transistor-level-PG-front-end-bits-0-to-3"), "full_tl_1_pg", note)
    drawn += figure(pick(["invc0", "g10", "t10", "ig10", "it10"], ["g32", "t32", "ig2", "it2"],
                         ["g20", "t20", "g30", "t30"]),
                    cfg.plot_title("2", "transistor-level-prefix-carry-tree"), "full_tl_2_tree", note)
    drawn += figure(pick(["c1", "c2", "c3", "c4g"], ["x0", "x1"], ["x2", "x3"]),
                    cfg.plot_title("2", "transistor-level-final-carries-and-sums"), "full_tl_3_carry_sum",
                    note + r" $\overline{\mathrm{c}}_i'$ is the sum cell's own copy of the inverted carry.")
    # the flip-flop, drawn once with generic names
    p = json.loads((FINAL / "dff.json").read_text())["params"]
    ff = tspc(**p)
    ff_note = ("One TSPC flip-flop, used 14 times: 9 register the inputs a0-a3, b0-b3, C0 and 5 register the outputs "
               "S0-S3, C4. All share one clock. X, Y are the internal stage nodes.")
    figure([[("ff", ff, {"d": "D", "clk": "CLK", "q": "Q"}, "TSPC flip-flop (one of 14)",
              {"a": "$X$", "b": "$Y$", "qb": r"$\overline{\mathrm{Q}}$", "d": "$D$", "clk": "CLK", "q": "$Q$"})]],
           cfg.plot_title("2", "transistor-level-TSPC-flip-flop"), "full_tl_4_dff", ff_note)

    # every device of the adder netlist appears exactly once
    want = sorted((i, d.name) for i, c, _ in adder.instances for d in (
        [d for st in c.stages if isinstance(st, GateStage) for d in st.cell.devices] if isinstance(c, StagedCell) else c.devices))
    got = sorted(drawn)
    print("adder transistors in netlist", len(want), "drawn", len(got), "match", want == got)


if __name__ == "__main__":
    main()
