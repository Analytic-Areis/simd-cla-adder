#!/usr/bin/env python3
"""Draft diagrams for the planning milestone.

These show PROPOSED topology only, so they carry no W/L values. Final report
schematics will be generated from the same cell descriptions that emit the SPICE
netlists, so that a drawing cannot differ from what was simulated.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

OUT = Path(__file__).resolve().parent
INK, FILL, ACC = "#1f2933", "#eef2f6", "#b42318"


def box(ax, x, y, w, h, title, sub=None):
    ax.add_patch(Rectangle((x, y), w, h, fc=FILL, ec=INK, lw=1.3))
    ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="top", fontsize=10, weight="bold", color=INK)
    if sub:
        ax.text(x + w / 2, y + h - 0.85, sub, ha="center", va="top", fontsize=8, color=INK, linespacing=1.3)


def wire(ax, p, q, label=None, lpos=0.5, dy=0.1, color=INK, lw=1.2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, lw=lw, color=color,
                                 shrinkA=0, shrinkB=0))
    if label:
        ax.text(p[0] + (q[0] - p[0]) * lpos, p[1] + (q[1] - p[1]) * lpos + dy, label,
                ha="center", va="bottom", fontsize=8, color=color)


def block_diagram():
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    ax.set_xlim(0, 17.5)
    ax.set_ylim(0, 8.6)
    ax.axis("off")
    ax.set_title("Proposed 4-bit CLA: block-level signal flow (draft, no sizing)", fontsize=11, color=INK)

    box(ax, 2.2, 3.2, 3.6, 4.5, "P/G block", "per bit i:\nNAND2 gives g̅i\nNOR2 gives t̅i\ncompound gates give Pi, P̅i\n(XOR not in carry path)")
    box(ax, 7.6, 3.2, 3.8, 4.5, "Carry generator", "C1, C2, C3: one complex\ngate each, stack 2/3/4\nC4: mirror gate over C2\nplus output inverter")
    box(ax, 13.0, 3.2, 2.5, 4.5, "Sum block", "Si = Pi xor Ci\nfour XOR stages\nwith output drive")

    ax.text(0.2, 6.5, "A[3:0]", fontsize=9, color=INK)
    ax.text(0.2, 5.3, "B[3:0]", fontsize=9, color=INK)
    wire(ax, (1.2, 6.6), (2.2, 6.6))
    wire(ax, (1.2, 5.4), (2.2, 5.4))
    ax.text(0.2, 1.1, "Cin", fontsize=9, color=ACC, weight="bold")

    wire(ax, (5.8, 6.7), (7.6, 6.7), "g̅[3:0]")
    wire(ax, (5.8, 5.5), (7.6, 5.5), "t̅[3:0]")
    # P rails bypass the carry generator along the top
    ax.plot([5.8, 6.6, 6.6, 12.3, 12.3], [7.2, 7.2, 8.2, 8.2, 7.2], color=INK, lw=1.2)
    wire(ax, (12.3, 7.2), (13.0, 7.2))
    ax.text(9.5, 8.25, "P[3:0], P̅[3:0]", ha="center", va="bottom", fontsize=8, color=INK)
    # raw A[3:2], B[3:2] for the C4 mirror gate
    ax.plot([1.7, 1.7, 7.0, 7.0], [5.4, 2.6, 2.6, 4.2], color=INK, lw=1.2)
    wire(ax, (7.0, 4.2), (7.6, 4.2))
    ax.text(4.3, 2.65, "A[3:2], B[3:2] (mirror gate)", ha="center", va="bottom", fontsize=8, color=INK)

    # Cin
    ax.plot([0.9, 6.3, 6.3], [1.2, 1.2, 3.7], color=ACC, lw=1.5)
    wire(ax, (6.3, 3.7), (7.6, 3.7), color=ACC, lw=1.5)
    ax.text(6.25, 2.05, "C̅0 via\nC0 buffer", ha="right", va="center", fontsize=7.5, color=ACC)
    ax.plot([6.3, 12.6, 12.6], [1.2, 1.2, 3.7], color=ACC, lw=1.5)
    wire(ax, (12.6, 3.7), (13.0, 3.7), color=ACC, lw=1.5)
    ax.text(9.5, 1.25, "C0 = sum input of bit 0", ha="center", va="bottom", fontsize=8, color=ACC)

    wire(ax, (11.4, 6.0), (13.0, 6.0), "C1, C2")
    wire(ax, (11.4, 5.0), (13.0, 5.0), "C3")
    wire(ax, (15.5, 5.45), (16.6, 5.45), "S[3:0]")
    # C4 output
    ax.plot([11.4, 11.9, 11.9, 16.6], [3.9, 3.9, 2.3, 2.3], color=INK, lw=1.2)
    wire(ax, (16.6, 2.3), (17.4, 2.3))
    ax.text(16.4, 2.35, "C4 = Cout", ha="center", va="bottom", fontsize=8, color=INK)

    ax.text(0.2, 0.25, "Standalone test: every output drives the 20L/10L inverter load (Wp 1.8 um, Wn 0.9 um, L 0.18 um). "
                       "Inputs are driven by a realistic finite driver.", fontsize=8, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "proposed_block_diagram.png", dpi=170)
    fig.savefig(OUT / "proposed_block_diagram.svg")
    plt.close(fig)


def fet(ax, x, y, name, kind="n", side="left"):
    """Vertical MOS device centred on (x, y); drain above and source below."""
    ax.plot([x, x], [y + 0.5, y + 0.22], color=INK, lw=1.2)
    ax.plot([x, x], [y - 0.5, y - 0.22], color=INK, lw=1.2)
    ax.plot([x, x - 0.14 if side == "left" else x + 0.14], [y + 0.22, y + 0.22], color=INK, lw=1.2)
    ax.plot([x, x - 0.14 if side == "left" else x + 0.14], [y - 0.22, y - 0.22], color=INK, lw=1.2)
    gx = x - 0.14 if side == "left" else x + 0.14
    ax.plot([gx, gx], [y - 0.22, y + 0.22], color=INK, lw=1.8)
    tip = gx - 0.1 if side == "left" else gx + 0.1
    ax.plot([tip, tip], [y - 0.22, y + 0.22], color=INK, lw=1.2)
    lead = tip - 0.25 if side == "left" else tip + 0.25
    if kind == "p":
        off = 0.05 if side == "left" else -0.05
        ax.add_patch(plt.Circle((tip - off, y), 0.05, fc="white", ec=INK, lw=1.0, zorder=3))
        ax.plot([lead, tip - 2 * off], [y, y], color=INK, lw=1.2)
    else:
        ax.plot([lead, tip], [y, y], color=INK, lw=1.2)
    ax.text(lead - 0.05 if side == "left" else lead + 0.05, y, name, ha="right" if side == "left" else "left",
            va="center", fontsize=8.5, color=ACC if "c" in name else INK)


def dot(ax, x, y):
    ax.add_patch(plt.Circle((x, y), 0.045, fc=INK, ec=INK, zorder=4))


def carry_gate():
    """C2 = NOT[ g1b . ( t1b + g0b . ( t0b + c0b ) ) ]"""
    fig, ax = plt.subplots(figsize=(8.2, 8.2))
    ax.set_xlim(-1.2, 7.8)
    ax.set_ylim(-1.0, 11.0)
    ax.axis("off")
    ax.set_title("Proposed C2 gate: C2 = NOT[ g̅1 ( t̅1 + g̅0 ( t̅0 + c̅0 ) ) ]  (draft, no sizing)", fontsize=10.5, color=INK)

    ax.plot([0, 6], [10.2, 10.2], color=INK, lw=1.6)
    ax.text(6.1, 10.2, "VDD", va="center", fontsize=9)
    ax.plot([0, 6], [-0.4, -0.4], color=INK, lw=1.6)
    ax.text(6.1, -0.4, "GND", va="center", fontsize=9)

    # Pull-up: g1b || ( t1b series ( g0b || ( t0b series c0b ) ) )
    yout = 5.2
    fet(ax, 1, 8.2, "g̅1", "p")
    ax.plot([1, 1], [8.7, 10.2], color=INK, lw=1.2)
    ax.plot([1, 1], [7.7, yout], color=INK, lw=1.2)

    fet(ax, 3, 9.4, "t̅1", "p")
    ax.plot([3, 3], [9.9, 10.2], color=INK, lw=1.2)
    ax.plot([3, 3], [8.9, 8.7], color=INK, lw=1.2)
    dot(ax, 3, 8.7)
    ax.plot([2.2, 5.0], [8.7, 8.7], color=INK, lw=1.2)
    fet(ax, 2.2, 7.5, "g̅0", "p")
    ax.plot([2.2, 2.2], [8.0, 8.7], color=INK, lw=1.2)
    ax.plot([2.2, 2.2], [7.0, 6.2], color=INK, lw=1.2)
    fet(ax, 5.0, 7.9, "t̅0", "p", side="right")
    ax.plot([5.0, 5.0], [8.4, 8.7], color=INK, lw=1.2)
    fet(ax, 5.0, 6.8, "c̅0", "p", side="right")
    ax.plot([5.0, 5.0], [7.4, 7.3], color=INK, lw=1.2)
    ax.plot([5.0, 5.0], [6.3, 6.2], color=INK, lw=1.2)
    ax.plot([2.2, 5.0], [6.2, 6.2], color=INK, lw=1.2)
    dot(ax, 2.2, 6.2)
    ax.plot([3.4, 3.4], [6.2, yout], color=INK, lw=1.2)
    dot(ax, 3.4, 6.2)

    # Output
    ax.plot([1, 7.0], [yout, yout], color=INK, lw=1.6)
    dot(ax, 1, yout)
    dot(ax, 3.4, yout)
    ax.text(7.05, yout, "C2", va="center", fontsize=10, weight="bold")

    # Pull-down: g1b series ( t1b || ( g0b series ( t0b || c0b ) ) )
    fet(ax, 3.4, 4.3, "g̅1")
    ax.plot([3.4, 3.4], [4.8, yout], color=INK, lw=1.2)
    ax.plot([3.4, 3.4], [3.8, 3.5], color=INK, lw=1.2)
    ax.plot([1.2, 5.0], [3.5, 3.5], color=INK, lw=1.2)
    dot(ax, 3.4, 3.5)
    fet(ax, 1.2, 2.0, "t̅1")
    ax.plot([1.2, 1.2], [2.5, 3.5], color=INK, lw=1.2)
    ax.plot([1.2, 1.2], [1.5, 0.3], color=INK, lw=1.2)
    fet(ax, 5.0, 2.9, "g̅0", side="right")
    ax.plot([5.0, 5.0], [3.4, 3.5], color=INK, lw=1.2)
    ax.plot([5.0, 5.0], [2.4, 2.2], color=INK, lw=1.2)
    ax.plot([4.2, 5.8], [2.2, 2.2], color=INK, lw=1.2)
    dot(ax, 5.0, 2.2)
    fet(ax, 4.2, 1.3, "t̅0")
    ax.plot([4.2, 4.2], [1.8, 2.2], color=INK, lw=1.2)
    ax.plot([4.2, 4.2], [0.8, 0.3], color=INK, lw=1.2)
    fet(ax, 5.8, 1.3, "c̅0", side="right")
    ax.plot([5.8, 5.8], [1.8, 2.2], color=INK, lw=1.2)
    ax.plot([5.8, 5.8], [0.8, 0.3], color=INK, lw=1.2)
    ax.plot([1.2, 5.8], [0.3, 0.3], color=INK, lw=1.2)
    ax.plot([3.4, 3.4], [0.3, -0.4], color=INK, lw=1.2)
    dot(ax, 3.4, 0.3)

    ax.text(-1.1, 8.6, "PMOS\nnetwork\n(stack 3:\nt̅1, t̅0, c̅0)", fontsize=8.5, va="center", color=INK)
    ax.text(-1.1, 2.4, "NMOS\nnetwork\n(stack 3:\ng̅1, g̅0, c̅0)", fontsize=8.5, va="center", color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "proposed_c2_gate.png", dpi=170)
    fig.savefig(OUT / "proposed_c2_gate.svg")
    plt.close(fig)


if __name__ == "__main__":
    block_diagram()
    carry_gate()
