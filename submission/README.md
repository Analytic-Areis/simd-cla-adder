# Submission report

**Draft 1: Parts I and II.** [`Bhargav_2025102061.pdf`](Bhargav_2025102061.pdf), 26 pages, named as the course asks (Name RollNo.pdf).

The layout follows the reference report in IEEE two-column conference style. It opens with a contents page, then the title, author block and abstract, followed by these numbered sections:

| No. | Section |
|---|---|
| I | Introduction |
| II | Design Proposal |
| III | Design Details |
| IV | NGSPICE Simulation, pre-layout, gate by gate and block by block |
| V | D Flip-Flop Characterization |
| VI | Euler Paths and Stick Diagrams: the gate order along each diffusion row, from the generated layouts |
| VII | MAGIC Layouts: a screenshot and a post-layout plot for every gate and block |
| VIII | NGSPICE Circuit, pre-layout |
| IX | MAGIC Layout Plan |
| X | Final MAGIC Layout |
| XI | Post-Layout Simulations and Delays |
| XII | Part II: SIMD-Reconfigurable 8-bit Adder |
| XIII, XIV | Verilog HDL and FPGA Implementation. **Placeholders**, to be filled when Part III is done |

The report ends with an acknowledgment and the references. Netlists are in the project folders, not printed in the report.

## Files

| File | What it does |
|---|---|
| `figures.py` | `sims`: pre- and post-layout waveforms for every gate, the flip-flop, the blocks and the full registered circuit, with the course plot titles, and the gate delays in `gate_delays.json`. `shots`: MAGIC screenshots of each gate and block, which needs XQuartz running |
| `full_schematic.py` | Draws the whole adder at transistor level, all 194 devices with W/L, in three full-page figures (P/G front end, prefix tree, carries and sums) plus the flip-flop, as vector PDF and PNG. Checks every netlist transistor is drawn exactly once |
| `stick_euler.py` | For each gate in the final adder and the flip-flop: regenerates its layout, checks it matches the saved MAGIC layout, and draws the pull-up and pull-down Euler graphs with the row order the layout uses, plus a stick diagram of that layout. Writes `stick_euler.json` |
| `build_report.py` | Writes `report.tex` and builds the PDF. Every number is read from the result files in `part1/results/`, `part2/results/` and `gate_delays.json` |
| `figures/` | All figures used, copied or generated |
| `report.tex` | The LaTeX source, regenerated on each build |
| `work/` | Simulation decks and logs from `figures.py` |

## Rebuild

From this folder:

```bash
python3 figures.py sims
```

```bash
python3 figures.py shots
```

```bash
python3 full_schematic.py
```

```bash
python3 stick_euler.py
```

```bash
python3 build_report.py
```

## Still to add

- **Part III:** Sections XIII and XIV, with the Verilog, test vectors, waveforms, FPGA results and oscilloscope captures.
- **Author block:** department and college email are not filled in.
