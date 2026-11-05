# Submission report

**Draft 1: Parts I and II.** [`Bhargav_2025102061.pdf`](Bhargav_2025102061.pdf), 17 pages, named as the course asks (Name RollNo.pdf).

The layout follows the reference report in IEEE two-column conference style. It opens with a contents page, then the title, author block and abstract, followed by these numbered sections:

| No. | Section |
|---|---|
| I | Introduction |
| II | Design Proposal |
| III | Design Details |
| IV | NGSPICE Simulation, pre-layout, gate by gate and block by block |
| V | D Flip-Flop Characterization |
| VI | MAGIC Layouts: a screenshot and a post-layout plot for every gate and block |
| VII | NGSPICE Circuit, pre-layout |
| VIII | MAGIC Layout Plan |
| IX | Final MAGIC Layout |
| X | Post-Layout Simulations and Delays |
| XI | Part II: SIMD-Reconfigurable 8-bit Adder |
| XII, XIII | Verilog HDL and FPGA Implementation. **Placeholders**, to be filled when Part III is done |

The report ends with an acknowledgment, the references, and an appendix of netlists.

## Files

| File | What it does |
|---|---|
| `figures.py` | `sims`: pre- and post-layout waveforms for every gate, the flip-flop, the blocks and the full registered circuit, with the course plot titles, and the gate delays in `gate_delays.json`. `shots`: MAGIC screenshots of each gate and block, which needs XQuartz running |
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
python3 build_report.py
```

## Still to add

- **Part III:** Sections XII and XIII, with the Verilog, test vectors, waveforms, FPGA results and oscilloscope captures.
- **Author block:** department and college email are not filled in.
- **Stick diagrams:** the reference has a hand-drawn stick diagram section; this draft has none. The assignment's task list does not ask for one.
