"""Draw schematics from the same device objects and instances the netlist uses."""
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .cell import Block, GateStage, StagedCell
from .network import D, Pa

INK, NET, FILL = "#1f2933", "#1d4ed8", "#eef2f6"
LEAF_W, LEAF_H = 3.3, 1.75


def tex(name):
    """g0b becomes g-bar with subscript 0."""
    m = re.fullmatch(r"([A-Za-z]+?)(\d*)(b?)", name)
    if not m:
        return name
    base, idx, bar = m.groups()
    body = rf"\overline{{\mathrm{{{base}}}}}" if bar else rf"\mathrm{{{base}}}"
    return f"${body}_{{{idx}}}$" if idx else f"${body}$"


def extent(node):
    if isinstance(node, D):
        return LEAF_W, LEAF_H
    sizes = [extent(c) for c in node.children]
    if isinstance(node, Pa):
        return sum(s[0] for s in sizes), max(s[1] for s in sizes) + 0.5
    return max(s[0] for s in sizes), sum(s[1] for s in sizes)


def draw_fet(ax, x, ytop, ybot, dev):
    y = (ytop + ybot) / 2
    ch, g1, g2 = 0.28, x - 0.2, x - 0.32
    ax.plot([x, x], [ytop, y + ch], color=INK, lw=1.1)
    ax.plot([x, x], [y - ch, ybot], color=INK, lw=1.1)
    ax.plot([x, g1], [y + ch, y + ch], color=INK, lw=1.1)
    ax.plot([x, g1], [y - ch, y - ch], color=INK, lw=1.1)
    ax.plot([g1, g1], [y - ch, y + ch], color=INK, lw=1.8)
    ax.plot([g2, g2], [y - ch, y + ch], color=INK, lw=1.1)
    if dev.kind == "p":
        ax.add_patch(plt.Circle((g2 - 0.06, y), 0.06, fc="white", ec=INK, lw=1.0, zorder=3))
        ax.plot([g2 - 0.42, g2 - 0.12], [y, y], color=INK, lw=1.1)
    else:
        ax.plot([g2 - 0.42, g2], [y, y], color=INK, lw=1.1)
    ax.text(g2 - 0.47, y + 0.09, tex(dev.gate), ha="right", va="center", fontsize=9.5, color=INK)
    wl = f"{dev.w_lam}$\\lambda$/{dev.l_lam}$\\lambda$"
    ax.text(g2 - 0.47, y - 0.19, wl, ha="right", va="center", fontsize=6.3, color=INK)
    upper, lower = ("D", "S") if dev.drain == _terminal_above(dev) else ("S", "D")
    ax.text(x + 0.05, y + 0.40, upper, fontsize=5.5, color=INK, va="center")
    ax.text(x + 0.05, y - 0.40, lower, fontsize=5.5, color=INK, va="center")
    ax.text(x + 0.12, y, dev.name, fontsize=6, color=INK, va="center")


def _terminal_above(dev):
    """Static NMOS and transmission devices draw the drain on top; static PMOS the source."""
    return dev.source if dev.kind == "p" and dev.source == "vdd" or dev.name.endswith("__up") else dev.drain


def draw_node(ax, node, cx, ytop, ybot, drawn):
    if isinstance(node, D):
        draw_fet(ax, cx, ytop, ybot, node.dev)
        drawn.append(node.dev)
        return
    if isinstance(node, Pa):
        total = sum(extent(c)[0] for c in node.children)
        x = cx - total / 2
        bus_t, bus_b = ytop - 0.25, ybot + 0.25
        centres = []
        for child in node.children:
            w = extent(child)[0]
            centres.append(x + w / 2)
            draw_node(ax, child, x + w / 2, bus_t, bus_b, drawn)
            x += w
        for y, end in ((bus_t, ytop), (bus_b, ybot)):
            ax.plot([centres[0], centres[-1]], [y, y], color=INK, lw=1.1)
            ax.plot([cx, cx], [y, end], color=INK, lw=1.1)
            ax.add_patch(plt.Circle((cx, y), 0.04, fc=INK, ec=INK, zorder=4))
        return
    heights = [extent(c)[1] for c in node.children]
    scale = (ytop - ybot) / sum(heights)
    y = ytop
    for i, child in enumerate(node.children):
        lower = y - heights[i] * scale
        draw_node(ax, child, cx, y, lower, drawn)
        if i < len(node.nets):
            # a neighbouring parallel group already marks this junction with its own dot
            if not isinstance(child, Pa) and not isinstance(node.children[i + 1], Pa):
                ax.add_patch(plt.Circle((cx, lower), 0.04, fc=INK, ec=INK, zorder=4))
            ax.text(cx + 0.08, lower, node.nets[i], fontsize=6.5, color=NET, va="bottom")
        y = lower


def _gate_panel(ax, pun, pdn, cx, y_gnd, gap, output, half):
    """Draw one complementary gate centred at cx. Returns the devices drawn."""
    _, h_p = extent(pun)
    _, h_n = extent(pdn)
    y_vdd = y_gnd + 0.25 + h_n + gap + h_p + 0.25
    y_out = y_gnd + 0.25 + h_n + gap / 2
    drawn = []
    draw_node(ax, pun, cx, y_vdd - 0.25, y_out + gap / 2, drawn)
    draw_node(ax, pdn, cx, y_out - gap / 2, y_gnd + 0.25, drawn)
    ax.plot([cx - half, cx + half], [y_vdd, y_vdd], color=INK, lw=1.8)
    ax.plot([cx - half, cx + half], [y_gnd, y_gnd], color=INK, lw=1.8)
    ax.plot([cx, cx], [y_vdd, y_vdd - 0.25], color=INK, lw=1.1)
    ax.plot([cx, cx], [y_gnd, y_gnd + 0.25], color=INK, lw=1.1)
    ax.text(cx - half, y_vdd + 0.08, "VDD", fontsize=8, color=INK, va="bottom")
    ax.text(cx - half, y_gnd - 0.08, "GND", fontsize=8, color=INK, va="top")
    ax.plot([cx, cx], [y_out + gap / 2, y_out - gap / 2], color=INK, lw=1.1)
    ax.plot([cx, cx + half], [y_out, y_out], color=INK, lw=1.5)
    ax.add_patch(plt.Circle((cx, y_out), 0.05, fc=INK, ec=INK, zorder=4))
    ax.text(cx + half + 0.05, y_out, tex(output), fontsize=10.5, weight="bold", color=INK, va="center")
    return drawn, y_vdd


def _save(fig, path_stem):
    if path_stem is not None:
        fig.tight_layout()
        fig.savefig(f"{path_stem}.png", dpi=170)
        fig.savefig(f"{path_stem}.svg")
    plt.close(fig)


def draw_cell(cell, path_stem=None):
    """Draw a static gate. Returns the devices actually drawn, for checking against the netlist."""
    w_p, h_p = extent(cell.pun)
    w_n, h_n = extent(cell.pdn)
    width = max(w_p, w_n) + 2.0
    gap = 0.7
    height = h_p + h_n + gap + 1.6
    fig, ax = plt.subplots(figsize=(max(5.0, width), max(4.5, height * 0.95)))
    ax.set_xlim(-width / 2, width / 2 + 0.3)
    ax.set_ylim(-0.3, height + 0.6)
    ax.axis("off")
    drawn, _ = _gate_panel(ax, cell.pun, cell.pdn, 0, 0.3, gap, cell.output, width / 2 - 0.4)
    ax.set_title(f"{cell.name}: {cell.description}\n{cell.transistor_count} transistors, "
                 f"total width {cell.total_width_lam}$\\lambda$, bodies: NMOS to GND, PMOS to VDD",
                 fontsize=8.5, color=INK)
    _save(fig, path_stem)
    return drawn


def draw_staged(cell, path_stem=None):
    """Draw each stage side by side. Stages connect by the net names shown on them."""
    panels, widths = [], []
    for stage in cell.stages:
        if isinstance(stage, GateStage):
            w = max(extent(stage.cell.pun)[0], extent(stage.cell.pdn)[0]) + 1.6
        else:
            w = extent(stage.tree)[0] + 1.6
        panels.append(stage)
        widths.append(w)
    gap = 0.7
    heights = [extent(s.cell.pun)[1] + extent(s.cell.pdn)[1] + gap + 1.0 if isinstance(s, GateStage)
               else extent(s.tree)[1] + 2.0 for s in panels]
    height, total = max(heights), sum(widths)
    fig, ax = plt.subplots(figsize=(max(6.0, total * 1.0), max(4.5, (height + 1.2) * 0.95)))
    ax.set_xlim(0, total + 0.4)
    ax.set_ylim(-0.3, height + 0.8)
    ax.axis("off")
    drawn, x = [], 0.0
    for stage, w in zip(panels, widths):
        cx = x + w / 2 + 0.2
        if isinstance(stage, GateStage):
            d, _ = _gate_panel(ax, stage.cell.pun, stage.cell.pdn, cx, 0.3, gap, stage.out, w / 2 - 0.45)
            drawn += d
        else:
            ytop, ybot = height / 2 + 1.0, height / 2 - 1.0
            draw_node(ax, stage.tree, cx, ytop, ybot, drawn)
            ax.text(cx, ytop + 0.1, tex(stage.a), ha="center", va="bottom", fontsize=10, weight="bold", color=INK)
            ax.text(cx, ybot - 0.1, tex(stage.b), ha="center", va="top", fontsize=10, weight="bold", color=INK)
            ax.text(cx, ytop + 0.55, "transmission gate", ha="center", fontsize=7.5, color=INK)
        x += w
    ax.set_title(f"{cell.name}: {cell.description}\n{cell.transistor_count} transistors, "
                 f"total width {cell.total_width_lam}$\\lambda$, bodies: NMOS to GND, PMOS to VDD. "
                 "Stages connect by net name.", fontsize=8.5, color=INK)
    _save(fig, path_stem)
    return drawn


def _levels(block):
    """Place each instance in a column after the instances driving its inputs."""
    driver = {}
    for inst, cell, pins in block.instances:
        for out in cell.outputs:
            driver[pins[out]] = inst
    level = {}

    def depth(inst):
        if inst in level:
            return level[inst]
        _, cell, pins = next(i for i in block.instances if i[0] == inst)
        ins = [driver[pins[p]] for p in cell.inputs if pins[p] in driver]
        level[inst] = 0 if not ins else 1 + max(depth(i) for i in ins)
        return level[inst]

    for inst, _, _ in block.instances:
        depth(inst)
    return level


def draw_block(block, path_stem=None):
    """Draw instances as boxes with their pin nets. Returns the instances drawn."""
    level = _levels(block)
    columns = {}
    for item in block.instances:
        columns.setdefault(level[item[0]], []).append(item)
    box_w, col_gap, row_gap = 2.6, 2.2, 0.55

    def box_h(cell):
        return 0.8 + 0.34 * max(len(cell.inputs), len(cell.outputs))

    col_heights = {c: sum(box_h(i[1]) + row_gap for i in items) for c, items in columns.items()}
    height = max(col_heights.values()) + 0.6
    width = len(columns) * (box_w + col_gap) + 0.8
    fig, ax = plt.subplots(figsize=(max(6.5, width * 0.95), max(3.5, height * 0.8)))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height + 0.3)
    ax.axis("off")
    drawn = []
    for col, items in sorted(columns.items()):
        x = 1.3 + col * (box_w + col_gap)
        y = height - 0.2
        for inst, cell, pins in items:
            h = box_h(cell)
            y -= h
            ax.add_patch(Rectangle((x, y), box_w, h, fc=FILL, ec=INK, lw=1.2))
            ax.text(x + box_w / 2, y + h - 0.12, inst, ha="center", va="top", fontsize=8.5, weight="bold", color=INK)
            ax.text(x + box_w / 2, y + h - 0.40, f"{cell.name}, {cell.transistor_count}T", ha="center", va="top",
                    fontsize=6.5, color=INK)
            for side, names, sign in ((x, cell.inputs, -1), (x + box_w, cell.outputs, 1)):
                for k, pin in enumerate(names):
                    py = y + 0.22 + 0.32 * (len(names) - 1 - k)
                    ax.plot([side, side + sign * 0.3], [py, py], color=INK, lw=1.0)
                    ax.text(side + sign * 0.34, py, tex(pins[pin]), ha="right" if sign < 0 else "left", va="center",
                            fontsize=7.5, color=NET)
                    ax.text(side - sign * 0.05, py, pin, ha="left" if sign < 0 else "right", va="center",
                            fontsize=5.5, color=INK)
            drawn.append((inst, cell.name, dict(pins)))
            y -= row_gap
    ax.set_title(f"{block.name}: {block.description}\n{block.transistor_count} transistors, "
                 f"total width {block.total_width_lam}$\\lambda$. Instances connect by the net names in blue.",
                 fontsize=8.5, color=INK)
    _save(fig, path_stem)
    return drawn


def draw(cell, path_stem=None):
    if isinstance(cell, Block):
        return draw_block(cell, path_stem)
    if isinstance(cell, StagedCell):
        return draw_staged(cell, path_stem)
    return draw_cell(cell, path_stem)
