# Explanation: read this to understand the project

Everything here is for reading. The working files of each part are in `../part1/`, `../part2/` and `../part3/`.

## Reading order

| Read | What you learn |
|---|---|
| 1. [`guide/part1_build_guide.html`](guide/part1_build_guide.html) | Open in a browser. The whole of Part I with circuit diagrams: carries, gates, the final adder block by block, the flip-flop, layout, 16 problems and their fixes, viva questions, glossary |
| 2. [`part1_explained.md`](part1_explained.md) | Part I in short: phases, results, key decisions |
| 3. [`part2_explained.md`](part2_explained.md) | Part II: the SIMD adder, the gating cell, penalties, problems met |
| 4. [`part3_explained.md`](part3_explained.md) | Part III: Verilog, testbenches, the board, what is left |
| 5. [`research/research_log.md`](research/research_log.md) | Every step in date order, with measured numbers, including dead ends |
| 6. [`research/design_decisions.md`](research/design_decisions.md) | Each design decision, the alternatives and the evidence |

## Folders

| Path | Contents |
|---|---|
| `guide/` | The illustrated Part I guide and its images |
| `research/` | Research log, design decisions, literature review, paper comparison, analysis of earlier submissions |
| `references/` | The provided papers and earlier student submissions, kept unchanged |

## The project in one table

| Part | What | Main result | Status |
|---|---|---|---|
| I | 4-bit CLA in static CMOS, TSMC 180 nm, laid out in MAGIC | 579.88 ps worst single-input delay post-layout; 1.147 GHz working clock | Complete, report written |
| II | SIMD 8-bit adder from two Part I adders and a carry-gating cell | Gating costs +61.7 ps (7.6%) on Cin to S7, +1.5% power | Complete, report written |
| III | Verilog and FPGA | Every input combination checked in simulation, 0 errors | Simulation done; synthesis and hardware test still to do |

## Tools

ngspice-46 for simulation, MAGIC 8.3.668 for layout, Python 3 for the flow, Icarus Verilog for Part III simulation. netgen was not available, so layout-versus-schematic checks use the project's own script, which was tested by planting faults.
