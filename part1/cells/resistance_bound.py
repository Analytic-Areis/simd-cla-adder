#!/usr/bin/env python3
"""Upper bound on what layout resistance can add, because MAGIC's extresist crashes on this design.

Poly gate resistance: sheet resistance x longest poly run from a poly contact to the far end of
a transistor gate, in squares of 2 lambda poly. That largest resistance is then placed in series
with EVERY transistor gate in the extracted netlist, and all transitions are simulated again.
Metal and via resistance are compared by estimate; they are far smaller. Usage: resistance_bound.py TAG
"""
import json
import re
import sys
from pathlib import Path

from arcs import all_arcs
from candidates import INPUTS, OUTPUTS
from cellgen import config as cfg
from final_flow import arcs_summary
from postlayout import ExtractedCell

POLY_OHM_SQ = float(sys.argv[2]) if len(sys.argv) > 2 else 7.7
tag = sys.argv[1]
work = cfg.PART1 / "layout" / "integrated" / tag
worst_run, cells = 0, []
for tcl in work.glob("*.tcl"):
    poly, pcs = [], []
    for line in tcl.read_text().splitlines():
        m = re.match(r"box (-?\d+) (-?\d+) (-?\d+) (-?\d+); paint (poly|pc)$", line)
        if m:
            box = tuple(int(v) for v in m.groups()[:4])
            (poly if m.group(5) == "poly" else pcs).append(box)
    for x0, y0, x1, y1 in poly:
        contacts = [p for p in pcs if p[0] <= x0 and p[2] >= x1 and p[1] <= y1 and p[3] >= y0]
        if not contacts:
            continue
        # farthest poly point from its nearest contact
        run = max(min(abs(y0 - c[1]), abs(y0 - c[3])) if not (c[1] <= y0 <= c[3]) else 0 for c in contacts)
        run2 = max(min(abs(y1 - c[1]), abs(y1 - c[3])) if not (c[1] <= y1 <= c[3]) else 0 for c in contacts)
        length = max(run, run2)
        if length > worst_run:
            worst_run, cells = length, tcl.stem
squares = worst_run / 2
r_poly = squares * POLY_OHM_SQ
print(f"longest poly run {worst_run} lambda in {cells}: {squares} squares, {r_poly:.0f} ohm at {POLY_OHM_SQ} ohm/sq")

spice = work / f"top_{tag}.spice"
text = spice.read_text()
count = [0]


def add_resistor(match):
    count[0] += 1
    d, g, s = match.group(2), match.group(3), match.group(4)
    node = f"rg{count[0]}"
    return f"Rg{count[0]} {g} {node} {r_poly:.1f}\n{match.group(1)} {d} {node} {s}"


patched = re.sub(r"(?m)^(M\S+) (\S+) (\S+) (\S+)", add_resistor, text)
out = cfg.PART1 / "results" / "final" / "resistance"
out.mkdir(parents=True, exist_ok=True)
patched_path = out / f"{tag}_gate_r_bound.spice"
patched_path.write_text(patched)
base = json.loads((cfg.PART1 / "results" / "final" / f"{tag}_post.json").read_text())
ext = ExtractedCell(patched_path, f"rb_{tag}", INPUTS, OUTPUTS)
arcs, functional = all_arcs(ext, cfg.PART1 / "simulations" / "timing" / f"rbound_{tag}", workers=6)
s = arcs_summary(arcs)
result = dict(tag=tag, longest_poly_lambda=worst_run, poly_ohm_per_sq=POLY_OHM_SQ, r_gate_ohm=round(r_poly, 1), gates=count[0],
              functional_errors=functional, without_r_ps=base["worst_pin_ps"], with_r_bound_ps=s["worst_pin_ps"],
              increase_ps=round(s["worst_pin_ps"] - base["worst_pin_ps"], 2),
              increase_pct=round(100 * (s["worst_pin_ps"] / base["worst_pin_ps"] - 1), 2),
              worst_arc=s["worst_pin_arc"], note="upper bound: the worst poly resistance is applied to every gate")
(out / f"{tag}_bound.json").write_text(json.dumps(result, indent=1, default=float))
print(result)
