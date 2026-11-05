#!/usr/bin/env python3
"""Write every library cell's SPICE module and schematic from its one definition."""
import csv

from cellgen import config as cfg
from cellgen.schematic import draw
from library import all_blocks, all_cells


def main():
    modules = cfg.PART1 / "spice" / "modules"
    drawings = cfg.PART1 / "schematics" / "transistor_level"
    modules.mkdir(parents=True, exist_ok=True)
    drawings.mkdir(parents=True, exist_ok=True)
    rows = []
    for cell in all_cells() + all_blocks():
        (modules / f"{cell.name}.sp").write_text(cell.spice())
        draw(cell, drawings / cell.name)
        rows.append(dict(cell=cell.name, description=cell.description,
                         transistors=cell.transistor_count, total_width_lambda=cell.total_width_lam))
        print(f"{cell.name:22s} {cell.transistor_count:3d} T  width {cell.total_width_lam:5d} lambda")
    with open(modules / "cell_index.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
