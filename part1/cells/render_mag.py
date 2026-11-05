#!/usr/bin/env python3
"""Draw a saved MAGIC .mag file, including its subcells, with matplotlib.

MAGIC's own image plot comes out blank in batch mode with this tech file, so figures are drawn
from the rectangles stored in the .mag files. Nothing is redrawn from the design database.
"""
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Patch, Rectangle

COLORS = {
    "nwell": ("#d8e8c8", 1), "ndiffusion": ("#2ca02c", 2), "pdiffusion": ("#a65628", 2),
    "ntransistor": ("#6b8e23", 3), "ptransistor": ("#b8860b", 3), "polysilicon": ("#d62728", 4),
    "ndcontact": ("#111111", 5), "pdcontact": ("#111111", 5), "polycontact": ("#111111", 5),
    "psubstratepcontact": ("#555555", 5), "nsubstratencontact": ("#555555", 5),
    "metal1": ("#4c78e0", 6), "m2contact": ("#222222", 7), "metal2": ("#b279e8", 8),
    "m3contact": ("#222222", 9), "metal3": ("#17becf", 10), "m4contact": ("#222222", 11), "metal4": ("#e6c229", 12),
    "m345contact": ("#000000", 13), "metal5": ("#e377c2", 14),
}
SKIP = {"checkpaint"}   # MAGIC bookkeeping, not drawn on silicon
ALPHA = {"nwell": 0.55, "metal1": 0.55, "metal2": 0.45, "metal3": 0.45, "metal4": 0.5, "metal5": 0.6}
ALIASES = {"pmc": "polycontact", "pc": "polycontact", "ndc": "ndcontact", "pdc": "pdcontact", "psc": "psubstratepcontact",
           "nsc": "nsubstratencontact", "m2c": "m2contact", "m3c": "m3contact", "m4c": "m4contact",
           "nfet": "ntransistor", "pfet": "ptransistor", "ndiff": "ndiffusion", "pdiff": "pdiffusion", "poly": "polysilicon",
           "m1": "metal1", "m2": "metal2", "m3": "metal3", "m4": "metal4"}
STACKS = {"m123contact": ["m2contact", "metal2", "m3contact"], "m234contact": ["m3contact", "metal3", "m4contact"]}


def read_mag(path, directory, dx=0, dy=0, out=None, cache=None):
    """Return {layer: [(x0, y0, x1, y1)]} for one cell and its children, in parent coordinates."""
    out = {} if out is None else out
    layer = None
    use = None
    lines = (Path(directory) / f"{path}.mag").read_text().splitlines()
    for line in lines:
        if line.startswith("<<"):
            layer = line.strip("<> ").strip()
            continue
        if line.startswith("use "):
            use = line.split()[1]
            continue
        if line.startswith("transform") and use:
            t = [int(v) for v in line.split()[1:]]
            read_mag(use, directory, dx + t[2], dy + t[5], out)
            use = None
            continue
        if line.startswith("rect") and layer:
            x0, y0, x1, y1 = (int(v) for v in line.split()[1:5])
            name = ALIASES.get(layer, layer)
            for item in STACKS.get(name, [name]):
                out.setdefault(item, []).append((x0 + dx, y0 + dy, x1 + dx, y1 + dy))
    return out


def render(cell, directory, png, title="", size=11):
    rects = {k: v for k, v in read_mag(cell, directory).items() if k not in SKIP}
    xs = [r[0] for v in rects.values() for r in v] + [r[2] for v in rects.values() for r in v]
    ys = [r[1] for v in rects.values() for r in v] + [r[3] for v in rects.values() for r in v]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    fig, ax = plt.subplots(figsize=(size, max(3, size * h / w) + 1.0))
    handles = []
    for name in sorted(rects, key=lambda n: COLORS.get(n, ("#999999", 0))[1]):
        colour, z = COLORS.get(name, ("#999999", 0))
        patches = [Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1]) for r in rects[name]]
        ax.add_collection(PatchCollection(patches, facecolor=colour, edgecolor="none", alpha=ALPHA.get(name, 0.9), zorder=z))
        if name in COLORS:
            handles.append(Patch(facecolor=colour, alpha=ALPHA.get(name, 0.9), label=name))
    ax.set_xlim(min(xs) - 5, max(xs) + 5)
    ax.set_ylim(min(ys) - 5, max(ys) + 5)
    ax.set_aspect("equal")
    ax.set_xlabel("x (lambda, 1 lambda = 0.09 um)", fontsize=8)
    ax.set_ylabel("y (lambda)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(handles=handles, ncol=4 if size < 8 else 8, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.09), frameon=False)
    if title:
        ax.set_title(title, fontsize=9)
    fig.savefig(png, dpi=170, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
