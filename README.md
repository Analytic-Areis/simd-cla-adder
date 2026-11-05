# VLSI Design course project

IIIT Hyderabad, Monsoon 2026. Bhargav, 2025102061. Assignment: [`Course_project.pdf`](Course_project.pdf).

Due 1 Dec 2026, 18:00. Demo and viva 3 and 4 Dec 2026.

**New to the project? Start in [`explanation/`](explanation/README.md).**

| Folder | What it holds | Status |
|---|---|---|
| [`part1/`](part1/README.md) | 4-bit carry look-ahead adder: cells, simulations, MAGIC layouts, report | Complete. Report: [`part1/documentation/Bhargav_2025102061.pdf`](part1/documentation/Bhargav_2025102061.pdf) |
| [`part2/`](part2/README.md) | SIMD-reconfigurable 8-bit adder: netlists, gating cell, MAGIC layouts, ngspice results | Complete. Report: [`part2/documentation/Bhargav_2025102061_part2.pdf`](part2/documentation/Bhargav_2025102061_part2.pdf) |
| [`part3/`](part3/README.md) | Verilog, testbenches, Boolean Board tops and constraints | Simulation done; Vivado synthesis and hardware test still to do |
| [`submission/`](submission/README.md) | The combined report to hand in, IEEE style. Draft 1 covers Parts I and II: [`submission/Bhargav_2025102061.pdf`](submission/Bhargav_2025102061.pdf) | Draft 1 |
| [`explanation/`](explanation/README.md) | Guides, research log, design decisions, references | |
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
