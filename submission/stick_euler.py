#!/usr/bin/env python3
"""Euler graphs and stick diagrams of the gates used in the final adder, for the report.

Both come from the layout generator itself, not drawn by hand:
  * The layout generator orders each gate's transistors along an Euler trail of its pull-up
    and pull-down graphs, so neighbouring transistors share a diffusion node. That chosen
    trail is recorded here, and the graphs are drawn with the trail's edge order numbered.
  * The stick diagram is the same generated layout, with every rectangle reduced to its
    centre line: diffusion, poly, metal 1 and 2 as coloured sticks, contacts as crosses.
The gate layout is regenerated and checked against the saved MAGIC layout script before
drawing, so the drawing is of the layout in the report.

Run:  python3 stick_euler.py
"""
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "part1" / "cells"))

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

import cellgen.layout as L
import cellgen.schematic as sch
from cellgen import config as cfg
from cellgen.layout import devices_from_cell, generate, tcl_for_cell
from dff import tspc
from final_flow import FINAL
from library import aoi21, inv, nand, nor, oai21, xor_aoi22

FIG = HERE / "figures"
BLOCKS = HERE.parent / "part1" / "layout" / "individual_blocks"

# stick-diagram colours, the usual convention
C = {"ndiff": "#2e9e44", "pdiff": "#c8a000", "poly": "#d62728", "m1": "#1f5fbf", "m2": "#8e44ad",
     "contact": "#111111", "nwell": "#c8a000", "rail": "#1f5fbf"}
CONTACTS = {"ndc", "pdc", "pc", "psc", "nsc"}
VIAS = {"m2c", "m3c"}


def gates():
    p = json.loads((FINAL / "dff.json").read_text())["params"]
    return [("Inverter", inv(1.0)), ("NAND2", nand(2, 1.0)), ("NOR2", nor(2, 1.0)), ("AOI21", aoi21(1.0)),
            ("OAI21", oai21(1.0)), ("AOI22 XOR (sum, with its carry inverter)", xor_aoi22(1.0)),
            ("TSPC flip-flop", tspc(p["s1"], p["s2"], p["s3"], p["q"]))]


def layout_with_trail(cell):
    """Regenerate the cell's layout and capture the P and N device orders it used."""
    seen = []
    orig = L._try_layout

    def spy(name, choices, index, *a, **k):
        seen.append([ranked[index[g]] for g, ranked in enumerate(choices)])
        return orig(name, choices, index, *a, **k)

    L._try_layout = spy
    try:
        ports = [p for p in cell.ports if p not in ("vdd", "gnd")]
        lay = generate(cell.name, devices_from_cell(cell), ports)
    finally:
        L._try_layout = orig
    saved = (BLOCKS / cell.name / f"{cell.name}.tcl").read_text()
    same = tcl_for_cell(lay) in saved
    _, _, _, pt, nt = seen[-1][0]
    return lay, pt, nt, same


def label(net):
    return sch.tex(net)


def breaks(trail):
    """Split a trail where neighbours do not share a diffusion node."""
    parts, cur = [], []
    for d, left, right in trail:
        if cur and cur[-1][2] != left:
            parts.append(cur)
            cur = []
        cur.append((d, left, right))
    if cur:
        parts.append(cur)
    return parts


def draw_euler(ax, trail, rail, title, colour):
    """Graph of one network: nodes are diffusion nets, edges are transistors (gate labels).
    Edge numbers give the order along the layout's diffusion row, which is the Euler trail."""
    adj = defaultdict(set)
    for d, a, b in trail:
        adj[a].add(b)
        adj[b].add(a)
    level, frontier = {rail: 0}, [rail]
    while frontier:
        nxt = []
        for n in frontier:
            for m in sorted(adj[n]):
                if m not in level:
                    level[m] = level[n] + 1
                    nxt.append(m)
        frontier = nxt
    for n in adj:                       # nodes not reached from the rail (another stage's island)
        level.setdefault(n, max(level.values()) + 1)
    order = []
    for d, a, b in trail:
        for n in (a, b):
            if n not in order:
                order.append(n)
    by_level = defaultdict(list)
    for n in order:
        by_level[level[n]].append(n)
    depth = max(by_level) or 1
    pos = {}
    for lv, nodes in by_level.items():
        for k, n in enumerate(nodes):
            x = (k + 1) / (len(nodes) + 1)
            y = 1 - lv / depth if rail == "vdd" else lv / depth
            pos[n] = (x, 0.08 + 0.84 * y)
    pair_count = defaultdict(int)
    for k, (d, a, b) in enumerate(trail, 1):
        key = tuple(sorted((a, b)))
        m = pair_count[key]
        pair_count[key] += 1
        rad = [0.0, 0.45, -0.45, 0.8, -0.8][m % 5]
        (x0, y0), (x1, y1) = pos[a], pos[b]
        arr = FancyArrowPatch((x0, y0), (x1, y1), connectionstyle=f"arc3,rad={rad}", arrowstyle="-",
                              lw=2.2, color=colour, shrinkA=9, shrinkB=9)
        ax.add_patch(arr)
        # label at the arc's midpoint
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        lx, ly = mx + rad * dy / 2, my - rad * dx / 2      # midpoint of matplotlib's arc3 curve
        ax.text(lx, ly, f"{label(d.gate)}\n({k})", ha="center", va="center", fontsize=8.5, color=sch.INK,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=colour, lw=0.6))
    for n, (x, y) in pos.items():
        ax.plot(x, y, "o", ms=9, mfc="white", mec=sch.INK, mew=1.2, zorder=5)
        ax.text(x + 0.035, y + 0.035, n.upper() if n in ("vdd", "gnd") else label(n), fontsize=9, color=sch.INK,
                zorder=6, weight="bold" if n in ("vdd", "gnd") else "normal")
    parts = breaks(trail)
    path = "  |  ".join(" → ".join(f"{label(d.gate)}" for d, _, _ in p) for p in parts)
    ax.set_title(title, fontsize=10, color=sch.INK, loc="left")
    ax.text(0.0, -0.06, f"Euler path: {path}" + ("" if len(parts) == 1 else f"   ({len(parts) - 1} diffusion break{'s' if len(parts) > 2 else ''})"),
            fontsize=8.5, color=sch.INK, transform=ax.transAxes, va="top")
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(0, 1)
    ax.axis("off")


def draw_stick(ax, lay):
    """Every rectangle of the generated layout drawn as its centre line, in lambda."""
    polys = [r for r in lay.rects if r.layer == "poly"]
    pcs = [r for r in lay.rects if r.layer == "pc"]
    for r in lay.rects:
        if r.layer == "nwell":
            ax.add_patch(Rectangle((r.x0, r.y0), r.x1 - r.x0, r.y1 - r.y0, fill=False, ls="--", lw=1.0, ec=C["nwell"]))
    # diffusion: one horizontal stick per island, through the middle of the row
    for layer in ("ndiff", "pdiff"):
        spans = sorted((r.x0, r.x1, r.y0, r.y1) for r in lay.rects if r.layer == layer)
        islands = []
        for x0, x1, y0, y1 in spans:
            if islands and x0 <= islands[-1][1]:
                islands[-1] = [islands[-1][0], max(islands[-1][1], x1), min(islands[-1][2], y0), max(islands[-1][3], y1)]
            else:
                islands.append([x0, x1, y0, y1])
        for x0, x1, y0, y1 in islands:
            ax.plot([x0, x1], [(y0 + y1) / 2] * 2, color=C[layer], lw=8, solid_capstyle="butt", zorder=1, alpha=0.6)
    for layer, lw, z in (("poly", 2.4, 3), ("m2", 2.2, 4), ("m1", 2.2, 2)):
        for r in lay.rects:
            if r.layer != layer:
                continue
            w, h = r.x1 - r.x0, r.y1 - r.y0
            rail = layer == "m1" and (r.y0 == lay.y_gnd[0] or r.y0 == lay.y_vdd[0]) and w > 20 and h <= 6
            if w >= h:
                ax.plot([r.x0, r.x1], [(r.y0 + r.y1) / 2] * 2, color=C[layer], lw=4 if rail else lw,
                        solid_capstyle="butt", zorder=z, alpha=0.55 if "diff" in layer else 1)
            else:
                ax.plot([(r.x0 + r.x1) / 2] * 2, [r.y0, r.y1], color=C[layer], lw=lw, solid_capstyle="butt",
                        zorder=z, alpha=0.55 if "diff" in layer else 1)
    for r in lay.rects:
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        if r.layer in CONTACTS:
            ax.plot(cx, cy, "x", ms=6, mew=1.6, color=C["contact"], zorder=6)
        elif r.layer in VIAS:
            ax.plot(cx, cy, "s", ms=5.5, mfc="none", mec=C["contact"], mew=1.0, zorder=6)
            ax.plot(cx, cy, "x", ms=4, mew=1.0, color=C["contact"], zorder=6)
    # gate names on each poly stick, from the net of the poly contact on it
    mid = lay.height / 2
    for p in polys:
        x = (p.x0 + p.x1) / 2
        on = [c for c in pcs if c.x0 <= x <= c.x1 and p.y0 <= c.y0 <= p.y1]
        # the metal 1 track this poly contact lands on; tracks can share a height at different x
        net = next((n for n, (ty, tx0, tx1) in lay.tracks.items() if on and ty == on[0].y0 and tx0 - 6 <= x <= tx1 + 6), None)
        if not net:
            continue
        if p.y0 < mid and p.y1 < mid + 8:         # NMOS-only poly: name it below the GND rail
            ax.text(x, -4, label(net), ha="center", va="top", fontsize=9, color=C["poly"], weight="bold")
            ax.plot([x, x], [-3, p.y0], color=C["poly"], lw=0.6, ls=":", zorder=1)
        else:                                     # PMOS-only or shared poly: above the VDD rail
            ax.text(x, lay.height + 1.5, label(net), ha="center", va="bottom", fontsize=9, color=C["poly"], weight="bold")
            ax.plot([x, x], [p.y1, lay.height + 1], color=C["poly"], lw=0.6, ls=":", zorder=1)
    # pins, where each port leaves the cell on metal 3
    for net, (x, y, _) in lay.pin_stack.items():
        ax.text(x + 3.5, y + 2.5, label(net), fontsize=8.5, color=sch.INK, weight="bold", va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))
    ax.text(-2, (lay.y_vdd[0] + lay.y_vdd[1]) / 2, "VDD", ha="right", va="center", fontsize=8.5, color=sch.INK)
    ax.text(-2, (lay.y_gnd[0] + lay.y_gnd[1]) / 2, "GND", ha="right", va="center", fontsize=8.5, color=sch.INK)
    ax.set_aspect("equal")
    ax.set_xlim(-14, lay.width + 8)
    ax.set_ylim(-12, lay.height + 10)
    ax.axis("off")


def legend(fig):
    from matplotlib.lines import Line2D
    items = [Line2D([], [], color=C["ndiff"], lw=6, alpha=0.55, label="n-diffusion"),
             Line2D([], [], color=C["pdiff"], lw=6, alpha=0.55, label="p-diffusion"),
             Line2D([], [], color=C["poly"], lw=2.4, label="poly"),
             Line2D([], [], color=C["m1"], lw=2.2, label="metal 1"),
             Line2D([], [], color=C["m2"], lw=2.2, label="metal 2"),
             Line2D([], [], color=C["contact"], marker="x", ls="", ms=6, label="contact"),
             Line2D([], [], color=C["contact"], marker="s", mfc="none", ls="", ms=6, label="via (m2, m3 pin)"),
             Line2D([], [], color=C["nwell"], ls="--", lw=1, label="n-well")]
    fig.legend(handles=items, loc="lower center", ncol=8, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, 0.0))


def figure(nice, cell):
    lay, pt, nt, same = layout_with_trail(cell)
    if not same:
        raise RuntimeError(f"{cell.name}: regenerated layout differs from the saved MAGIC layout")
    wide = lay.width > 140
    fig = plt.figure(figsize=(13 if wide else 11, 6.4))
    gl = fig.add_axes([0.02, 0.55, 0.34 if wide else 0.4, 0.36])
    gr = fig.add_axes([0.02, 0.12, 0.34 if wide else 0.4, 0.36])
    st = fig.add_axes([0.40 if wide else 0.46, 0.1, 0.58 if wide else 0.52, 0.82])
    draw_euler(gl, pt, "vdd", "Pull-up network (PMOS) graph", C["pdiff"])
    draw_euler(gr, nt, "gnd", "Pull-down network (NMOS) graph", C["ndiff"])
    draw_stick(st, lay)
    st.set_title(f"Stick diagram of the MAGIC layout ({lay.width} x {lay.height} $\\lambda$)", fontsize=10, color=sch.INK, loc="left")
    fig.suptitle(cfg.plot_title("2", f"Euler-graph-and-stick-diagram-{cell.name}"), fontsize=12, color=sch.INK)
    legend(fig)
    stem = f"stick_{cell.name}"
    fig.savefig(FIG / f"{stem}.pdf")
    fig.savefig(FIG / f"{stem}.png", dpi=120)
    plt.close(fig)
    same_order = [d.gate for d, _, _ in pt] == [d.gate for d, _, _ in nt]
    return dict(cell=cell.name, nice=nice, p_order=[d.gate for d, _, _ in pt], n_order=[d.gate for d, _, _ in nt],
                p_breaks=len(breaks(pt)) - 1, n_breaks=len(breaks(nt)) - 1, same_order=same_order,
                width=lay.width, height=lay.height, stem=stem, matches_saved_layout=same)


def main():
    FIG.mkdir(exist_ok=True)
    rows = [figure(nice, cell) for nice, cell in gates()]
    (HERE / "stick_euler.json").write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(r["cell"], "P", r["p_order"], r["p_breaks"], "N", r["n_order"], r["n_breaks"], "same", r["same_order"],
              "matches saved", r["matches_saved_layout"])


if __name__ == "__main__":
    main()
