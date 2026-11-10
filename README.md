# VLSI Design course project

IIIT Hyderabad, Monsoon 2026. Bhargav, 2025102061. Assignment: [`Course_project.pdf`](Course_project.pdf).

Due 1 Dec 2026, 18:00. Demo and viva 3 and 4 Dec 2026.

**New to the project? Start in [`explanation/`](explanation/README.md).**

| Folder | What it holds | Status |
|---|---|---|
| [`part1/`](part1/README.md) | 4-bit carry look-ahead adder: cells, simulations, MAGIC layouts, report | Complete. Report: [`part1/documentation/Bhargav_2025102061.pdf`](part1/documentation/Bhargav_2025102061.pdf) |
| [`part2/`](part2/README.md) | SIMD-reconfigurable 8-bit adder: netlists, gating cell, MAGIC layouts, ngspice results | Complete. Report: [`part2/documentation/Bhargav_2025102061_part2.pdf`](part2/documentation/Bhargav_2025102061_part2.pdf) |
| [`fpga/`](fpga/README.md) | Part III: Verilog, testbenches, Boolean Board tops, constraints and Vivado scripts. Self-contained, so it can be copied on its own | Simulation done; Vivado synthesis and hardware test still to do |
| [`submission/`](submission/README.md) | The combined report to hand in, IEEE style. Draft 1 covers Parts I and II: [`submission/Bhargav_2025102061.pdf`](submission/Bhargav_2025102061.pdf) | Draft 1 |
| [`explanation/`](explanation/README.md) | Guides, research log, design decisions, references | |
| [`test_dump/`](test_dump/README.md) | Layouts, post-layout simulations and results of designs tried but not used | Kept for reference, not in any report |
| `technology/` | Provided TSMC 180 nm model and MAGIC tech file, unchanged | |

## Results at a glance, post-layout

| | Part I, 4-bit | Part II baseline, 8-bit | Part II SIMD, mode 0 | Part II SIMD, mode 1 |
|---|---|---|---|---|
| Worst-case delay | 579.88 ps | 1030.86 ps | 1109.77 ps | 570.22 ps |
| Transistors | 194 adder, 348 registered | 388 | 396 | |
| Area | 2937 µm² adder | 7749.0 µm² | 8858.7 µm² | |
| DRC / LVS | 0 / match | 0 / match | 0 / match | |

## Tools

ngspice-46, MAGIC 8.3.668, Python 3 with numpy and matplotlib, Icarus Verilog. Vivado for Part III synthesis on a lab machine.

## Running in the course container

[`docker-compose.yml`](docker-compose.yml) is the course toolchain configuration ("VLSI Design (M26) Toolchain Setup Guide", Step 2): image `hpretl/iic-osic-tools:latest`, container `iiith_vlsid_env`, noVNC on port 6080, password `abc123`, `~/designs` mounted at `/foss/designs`. It adds one volume, which mounts this folder at `/foss/designs/VLSI_CP`.

On Apple Silicon, first turn on "Use Rosetta for x86/amd64 emulation" in Docker Desktop, under Settings → General. Then, from this folder:

```bash
mkdir -p ~/designs
```

```bash
docker compose up -d
```

Open http://localhost:6080 and use a terminal on that desktop:

```bash
cd /foss/designs/VLSI_CP/part1/cells
```

The scripts need no changes inside the container:
- **Paths:** all are relative to the project folder.
- **MAGIC:** runs as `magic -T SCN6M_DEEP.09.tech27`, with the tech file copied from `technology/` into each layout working folder, as the guide's Step 5 does.
- **ngspice and Icarus Verilog:** called by name.
- **MAGIC screenshots** (`magic_shot.py`, `submission/figures.py shots`): use the container's `$DISPLAY` and `xwd`. On the Mac they use XQuartz on `:1`.
- **SKY130:** not used. The project uses the provided TSMC 180 nm files, so `sak-pdk` is not needed.

The results in this folder were produced on the Mac with the tool versions above, not in the container. The container's tool versions may differ.
