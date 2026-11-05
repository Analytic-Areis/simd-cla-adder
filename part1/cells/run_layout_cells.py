#!/usr/bin/env python3
"""Generate block layouts, run MAGIC DRC and extraction, and compare with the schematic."""
import csv
import os
import re
import shutil
import subprocess
import sys

from cellgen import config as cfg
from cellgen import parse_flat
from cellgen.layout import generate, devices_from_block, devices_from_cell, tcl_for_cell, tcl_labels
from cellgen.lvs import compare, read_extracted, schematic_devices
from library import all_blocks, all_cells, carry, inv, nand, xor_tg

OUT = cfg.PART1 / "layout" / "individual_blocks"
TECH = cfg.ROOT / "technology" / "SCN6M_DEEP.09.tech27"


def magic_run(work, name, body):
    work.mkdir(parents=True, exist_ok=True)
    tech = work / "SCN6M_DEEP.09.tech27"
    if not tech.exists():
        os.symlink(os.path.relpath(TECH, work), tech)
    script = work / f"{name}.tcl"
    script.write_text(body)
    result = subprocess.run(["magic", "-dnull", "-noconsole", "-T", "SCN6M_DEEP.09.tech27", script.name],
                            cwd=work, capture_output=True, text=True, timeout=300)
    (work / f"{name}.magic.log").write_text(result.stdout + result.stderr)
    return result.stdout


def layout_cell(cell, work=OUT):
    if hasattr(cell, "instances"):
        devs = devices_from_block(cell)
    else:
        devs = devices_from_cell(cell)
    ports = [p for p in cell.ports if p not in ("vdd", "gnd")]
    layout = generate(cell.name, devs, ports)
    body = f"""cellname rename (UNNAMED) {cell.name}
{tcl_for_cell(layout)}
{tcl_labels(layout)}
select top cell
drc euclidean on
drc check
drc catchup
set why [drc listall why]
set total 0
foreach {{message boxes}} $why {{
    incr total [llength $boxes]
    puts "DRC_ERR $message : [lrange $boxes 0 3]"
}}
puts "DRC_COUNT $total"
save {cell.name}
extract do local
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice format ngspice
ext2spice subcircuit top on
ext2spice
puts DONE
quit -noprompt
"""
    work_dir = work / cell.name
    out = magic_run(work_dir, cell.name, body)
    count = re.search(r"DRC_COUNT (\d+)", out)
    errors = [l for l in out.splitlines() if l.startswith("DRC_ERR")]
    spice = work_dir / f"{cell.name}.spice"
    message = "extraction missing"
    matched = False
    if spice.exists():
        extracted = read_extracted(spice.read_text())
        if hasattr(cell, "instances"):
            flat = parse_flat(cell.spice(), cell.name)
        else:
            flat = parse_flat(cell.spice(), cell.name)
        matched, message = compare(extracted, schematic_devices(flat), set(ports) | {"vdd", "gnd"})
    return dict(cell=cell.name, width_lambda=layout.width, height_lambda=layout.height,
                area_um2=round(layout.width * layout.height * 0.09 ** 2, 1), tracks=layout.n_tracks,
                drc=int(count.group(1)) if count else -1, lvs=matched, lvs_message=message,
                drc_first="; ".join(errors[:5])[:300])


if __name__ == "__main__":
    want = sys.argv[1:]
    cells = all_cells() + all_blocks()
    rows = []
    for cell in cells:
        if want and cell.name not in want:
            continue
        try:
            row = layout_cell(cell)
        except Exception as exc:
            row = dict(cell=cell.name, drc=-1, lvs=False, lvs_message=str(exc)[:200])
        rows.append(row)
        print(row, flush=True)
