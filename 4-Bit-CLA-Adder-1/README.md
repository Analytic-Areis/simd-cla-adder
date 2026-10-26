# 4-bit Carry Look-Ahead Adder — Course Project Part-I (optimised design)

VLSI Design, Monsoon 2026, IIIT Hyderabad · 180 nm (TSMC BSIM3), VDD = 1.8 V, λ = 0.09 µm, Ln = Lp = 2λ
Author: Bhargav Vemparala (roll no. → edit `.spiceinit`)

## Design in one paragraph
Registered 4-bit CLA: 9 input TSPC flip-flops (a3..a0, b3..b0, c0) → static-CMOS CLA core → 5 output TSPC
flip-flops (s3..s0, c4). Every sum output drives the 20λ/10λ inverter load. The core is built **only from
single-stage inverting gates** (INV, NAND2, NOR2, AOI21, OAI21) plus one sum cell. All group
generate/propagate terms are computed *without* c0, so **c0 reaches every carry through one AOI21 gate and
every sum through one sum cell** (2 gate levels), which is exactly the path the project's worst-case test
(A=1111, B=0000, C0 0→1) exercises. Max depth from any input is 6 gate levels; no stack is deeper than 2.
Full rationale: [`docs/design.md`](docs/design.md). Decision/result log: [`docs/LOG.md`](docs/LOG.md).

## Folder map
| Path | What |
|---|---|
| `tech/` | `TSMC_180nm.txt` (ngspice models) — **put the course-given model file here** (same name), `SCN6M_DEEP.09.tech27` (MAGIC) |
| `.spiceinit` | ngspice start-up: your name/roll for every plot title (`set myname=...`) |
| `spice/common.inc` | supply, λ, L, sizing knobs `UN` (unit NMOS width, λ) and `BETA` (Wp/Wn) |
| `spice/cells/` | `mos.lib` (MOS wrappers w/ diffusion parasitics), `cells.lib` (INV, NAND2, NOR2, AOI21, OAI21, LOADINV), `sum_tg.inc` / `sum_aoi.inc` (2 sum-cell variants), `sumcell.inc` (selected one), `dff_tspc.lib` |
| `spice/blocks/cla4.lib` | the CLA core (P/G, carry look-ahead, sum) with per-block size knobs `SPG SGRP SCAR SSUM SC0` |
| `spice/full/` | full registered circuit (step 4) |
| `spice/tb/` | testbenches (one per question) |
| `scripts/` | `run.sh` (batch runner), result checkers, `logic_check_netlist.py` (boolean check of the netlist, no SPICE needed) |
| `results/logs, plots, tables` | ngspice logs, `.eps` plots (titled `$myname-Qx-...`), result tables |
| `magic/`, `postlayout/` | layouts + extracted netlists (later, Q5/Q7–Q11) |
| `verilog/` | behavioural model / golden reference (Part-III reuse) |
| `report/` | report source + figures |

## How to run (from this folder)
```bash
cd 4-Bit-CLA-Adder-1
./scripts/run.sh step1     # cells + TSPC DFF: function, tcq, setup, hold
./scripts/run.sh step2     # CLA core: worst-case delay/power for both sum cells + 512-vector test
ngspice spice/tb/tb_cla_worst.sp   # interactive: then e.g.  plot v(c0) v(s3) v(c4)
```
Run ngspice **from this folder** (paths in the netlists are relative to it, and `.spiceinit` is read from here).
Needs ngspice ≥ 32 (uses `alterparam`).

## Progress
| Step | Questions | Status |
|---|---|---|
| 0 | architecture, equations, netlists, boolean netlist check | ✅ done (512/512 pass) |
| 1 | Q3 cells, Q4 DFF tcq / setup / hold | ⏳ waiting for ngspice run |
| 2 | Q3 core function, Q9 (pre-layout) worst case, sum-cell choice | ⏳ |
| 3 | sizing optimisation (PDP sweep) | ☐ |
| 4 | Q6 full registered circuit, fmax, power | ☐ |
| 5 | Q5, Q7–Q11 layout + post-layout (MAGIC) | ☐ later |
| 6 | report | ☐ |
